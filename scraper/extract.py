"""One extraction gate: filter, extract and classify in a single Claude call.

Replaces step-03-filter-tech (Jev), step-05-extract (Claude) and
step-06-classify (Jev). AD-9: one gate, one place where the operation is
defined, one entry in REGISTRY.md.

    python extract.py                 # Batch API, half price, async
    python extract.py --sync          # immediate, for small runs and dev
    python extract.py --limit 20 --sync
    python extract.py --dry-run       # show what would be sent, call nothing

Needs ANTHROPIC_API_KEY.

Two decisions that look like details and are not:

1. Output shape is declared with `output_config.format`, NOT with a forced
   `tool_choice`. Forced tool use (`tool_choice` any/tool) returns 400 on
   claude-sonnet-5-5, the model the paste path uses — a forced-tool design
   would pass the nightly batch and break Soi tin (FR-12, FR-26).

2. Nothing is translated. The old step-05 prompt ordered "All extracted text
   MUST be in English", which is why 3.464 of 3.469 backfill records hold
   rewritten English and the original Vietnamese is gone. FR-6 wants
   precision/recall reported separately for skills written in Vietnamese, so
   skills come back verbatim as the posting wrote them; mapping to skill codes
   is the bilingual vocabulary's job, not the model's.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from anthropic import Anthropic
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

from crawlers.base import read_jsonl

# Bump when the prompt or the schema changes. Stored on every row (FR-6) and
# part of the cache key, so an old row is never mistaken for a new one.
PROMPT_VERSION = "gate-v3-2026-11-05"
MODEL = "claude-haiku-5-5"

IN_CANDIDATES = ["data/consolidated.jsonl", "data/dedup.jsonl"]
OUT_PATH = Path("data/extracted.jsonl")
NON_IT_PATH = Path("data/non_it.jsonl")
CACHE_PATH = Path("data/extract-cache.jsonl")
# Written before the first poll. A killed run resumes this batch instead of
# paying for the same postings again. custom_id is only unique inside one batch,
# so the cache key has to travel with the id.
PENDING_PATH = Path("data/extract-batch.json")
MAX_TOKENS = 16000

# Taxonomy from step-06 with two changes that Story 1.9 (FR-7) requires:
#   - Data / AI / ML split into three. One bucket hid the difference between a
#     BI analyst and an ML engineer, and the roadmap branches need them apart.
#   - Embedded added. The spine says in so many words that Embedded must not sit
#     in Other; the first 20-row run put a C++ automation engineer there.
TITLE_CATEGORY = [
    "Backend", "Frontend", "Fullstack", "Mobile",
    "Data Analyst / BI", "Data Engineer", "AI / ML Engineer",
    "Embedded",
    "DevOps / SRE / Cloud", "QA / Testing", "Product / BA / Agile",
    "Security / Cyber", "Infrastructure / IT Support", "UI/UX Design",
    "Game Development", "Other",
]
SENIORITY_CATEGORY = [
    "Intern", "Fresher / Entry-level", "Junior", "Mid-level", "Senior",
    "Lead / Principal", "Manager", "Director / Executive", "Unknown",
]
LOCATION_CATEGORY = ["Ho Chi Minh", "Ha Noi", "Da Nang", "Other"]
WORK_MODEL_CATEGORY = ["On-site", "Hybrid", "Remote", "Unknown"]

SCHEMA = {
    "type": "object",
    "properties": {
        "is_it_job": {
            "type": "boolean",
            "description": "See rule 3 of the system prompt.",
        },
        "it_confidence": {
            "type": "number",
            "description": "How sure you are of is_it_job, 0.0 to 1.0.",
        },
        "title_cleaned": {
            "type": ["string", "null"],
            "description": "Core role, seniority and location stripped. English label.",
        },
        "skills_raw": {
            "type": "array",
            "items": {"type": "string"},
            "description": (
                "Every skill the posting requires, VERBATIM as written. Do not "
                "translate: if it says 'kiem thu tu dong', return that, not 'test "
                "automation'. Keep original casing and diacritics."
            ),
        },
        "tech_stack": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Programming languages, frameworks and databases only.",
        },
        "keywords": {
            "type": "array",
            "items": {"type": "string"},
            "description": "3-8 domain concepts, architectures, cloud platforms.",
        },
        "years_experience_min": {
            "type": ["number", "null"],
            "description": "Minimum years required. null if not stated. Never guess.",
        },
        "years_experience_max": {
            "type": ["number", "null"],
            "description": "Maximum years. '2-3 nam' means min 2, max 3. null if open-ended.",
        },
        "title_category": {"type": "string", "enum": TITLE_CATEGORY},
        "seniority_category": {"type": "string", "enum": SENIORITY_CATEGORY},
        "location_category": {"type": "string", "enum": LOCATION_CATEGORY},
        "work_model_category": {"type": "string", "enum": WORK_MODEL_CATEGORY},
    },
    "required": [
        "is_it_job", "it_confidence", "title_cleaned", "skills_raw", "tech_stack",
        "keywords", "years_experience_min", "years_experience_max",
        "title_category", "seniority_category", "location_category",
        "work_model_category",
    ],
    "additionalProperties": False,
}

SYSTEM = (
    "You read job postings, mostly Vietnamese, some of them not IT, and return structured facts.\n\n"
    "Rules that matter more than fluency:\n"
    "1. Do NOT translate skills. Return them exactly as the posting writes them, "
    "Vietnamese included. 'học máy' stays 'học máy'. Mapping to canonical codes "
    "happens later against a bilingual vocabulary.\n"
    "2. Never invent a number. If years of experience are not stated, return null "
    "for both bounds. A range '2-3 năm' is min 2, max 3. 'trên 3 năm' is min 3, max null.\n"
    "3. is_it_job is true when the daily work is mainly building, testing, running or "
    "securing software, data or IT infrastructure, or specifying software: software, "
    "data and AI/ML engineering, embedded and firmware, QA of software, DevOps, system "
    "and network administration, IT support, security, IT business analysis, product "
    "and project management of software, UI/UX for software.\n"
    "It is false for: sales, marketing, account or customer care, even when the product "
    "is software; finance, HR, operations, teaching; QA/QC of physical products; "
    "mechanical, electrical or power engineering; pure hardware design such as PCB "
    "layout; business analysis of a non-software business.\n"
    "Judge from the duties, not the title or the company. it_confidence is how sure you "
    "are of this judgement; near 0.5 when the duties are unclear.\n"
    "4. Pick exactly one value from each category enum. Use 'Other' or 'Unknown' "
    "when the posting does not say — those are real answers, not failures.\n"
    "5. Extract only what the posting states. Do not fill gaps from what is typical."
)

USER_TEMPLATE = "Title: {title}\n\nCompany: {company}\n\nDescription:\n{description}"


def pick_input(explicit: str | None) -> Path:
    if explicit:
        p = Path(explicit)
        if not p.exists():
            sys.exit("input not found: %s" % p)
        return p
    for c in IN_CANDIDATES:
        p = Path(c)
        if p.exists() and p.stat().st_size > 0:
            return p
    sys.exit("no input found; looked for: %s" % ", ".join(IN_CANDIDATES))


def build_user(row: dict) -> str:
    desc = (row.get("description_consolidated") or row.get("description") or "").strip()
    return USER_TEMPLATE.format(
        title=row.get("title") or "",
        company=row.get("company") or "",
        description=desc[:12000],
    )


def cache_key(row: dict) -> str:
    return "%s|%s|%s" % (row.get("job_url"), PROMPT_VERSION, MODEL)


def load_cache() -> dict:
    cache = {}
    for rec in read_jsonl(CACHE_PATH):
        if rec.get("key"):
            cache[rec["key"]] = rec.get("facts")
    return cache


def append_cache(key: str, facts: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CACHE_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"key": key, "facts": facts}, ensure_ascii=False) + "\n")


def params(row: dict, model: str) -> dict:
    return dict(
        model=model,
        max_tokens=MAX_TOKENS,
        system=SYSTEM,
        messages=[{"role": "user", "content": build_user(row)}],
        output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
    )


def first_json(message) -> dict:
    """output_config.format guarantees the first text block is valid JSON."""
    text = next(b.text for b in message.content if b.type == "text")
    return json.loads(text)


def to_output_row(row: dict, facts: dict, model: str) -> dict:
    """Row shape for the JSONL output and for write_db."""
    out = dict(row)
    out["extracted_info"] = {
        "title_cleaned": facts.get("title_cleaned"),
        "tech_stack": facts.get("tech_stack") or [],
        "keywords": facts.get("keywords") or [],
        "skills_raw": facts.get("skills_raw") or [],
        "years_experience_min": facts.get("years_experience_min"),
        "years_experience_max": facts.get("years_experience_max"),
    }
    out["classification"] = {
        "title_category": facts.get("title_category"),
        "seniority_category": facts.get("seniority_category"),
        "location_category": facts.get("location_category"),
        "work_model_category": facts.get("work_model_category"),
    }
    out["is_it_job"] = facts.get("is_it_job")
    out["it_confidence"] = facts.get("it_confidence")
    out["model_version"] = model
    out["prompt_version"] = PROMPT_VERSION
    return out


def remember(cache, key: str, facts: dict) -> None:
    cache[key] = facts
    append_cache(key, facts)


def save_pending(batch_id: str, model: str, items: list[dict]) -> None:
    PENDING_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "batch_id": batch_id,
        "model": model,
        "prompt_version": PROMPT_VERSION,
        "items": items,
    }
    tmp = PENDING_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    tmp.replace(PENDING_PATH)


def load_pending() -> dict | None:
    if not PENDING_PATH.exists():
        return None
    return json.loads(PENDING_PATH.read_text(encoding="utf-8"))


def clear_pending() -> None:
    PENDING_PATH.unlink(missing_ok=True)


def pending_matches(pending: dict, model: str) -> bool:
    return bool(
        pending.get("batch_id")
        and pending.get("items")
        and pending.get("model") == model
        and pending.get("prompt_version") == PROMPT_VERSION
    )


def missing_batch(exc: Exception) -> bool:
    status = getattr(exc, "status_code", None)
    if status is None and getattr(exc, "response", None) is not None:
        status = getattr(exc.response, "status_code", None)
    return status == 404


def poll_until_ended(client, batch_id: str, poll: int):
    """Return the ended batch. None means the id is gone, so the caller may submit again."""
    while True:
        try:
            batch = client.messages.batches.retrieve(batch_id)
        except Exception as exc:
            if missing_batch(exc):
                return None
            raise
        if batch.processing_status == "ended":
            return batch
        counts = batch.request_counts
        print("  %s  processing=%d succeeded=%d errored=%d"
              % (batch.processing_status, counts.processing, counts.succeeded, counts.errored),
              flush=True)
        time.sleep(poll)


def apply_batch_results(client, pending: dict, cache) -> tuple[int, int]:
    by_id = {item["custom_id"]: item["key"] for item in pending["items"]}
    ok = err = 0
    for result in client.messages.batches.results(pending["batch_id"]):
        key = by_id.get(result.custom_id)
        if key is None:
            continue
        if result.result.type != "succeeded":
            err += 1
            print("  %s: %s" % (result.custom_id, result.result.type), flush=True)
            continue
        try:
            facts = first_json(result.result.message)
        except (StopIteration, json.JSONDecodeError) as exc:
            err += 1
            print("  %s: unparseable reply (%s)" % (result.custom_id, exc), flush=True)
            continue
        remember(cache, key, facts)
        ok += 1
    return ok, err


def run_sync(client, todo, model, cache):
    ok = err = 0
    for i, row in enumerate(todo, 1):
        msg = client.messages.create(**params(row, model))
        try:
            facts = first_json(msg)
        except (StopIteration, json.JSONDecodeError) as exc:
            err += 1
            print("  %d/%d unparseable reply (%s)" % (i, len(todo), exc), flush=True)
            continue
        remember(cache, cache_key(row), facts)
        ok += 1
        if i % 10 == 0 or i == len(todo):
            print("  %d/%d" % (i, len(todo)), flush=True)
    print("  results: %d ok, %d failed" % (ok, err), flush=True)


def run_batch(client, todo, model, cache, poll: int):
    pending = load_pending()
    if pending and not pending_matches(pending, model):
        print("  ignoring saved batch %s (prompt or model changed)"
              % pending.get("batch_id"), flush=True)
        clear_pending()
        pending = None
    if pending:
        print("  resuming batch %s" % pending["batch_id"], flush=True)
        ended = poll_until_ended(client, pending["batch_id"], poll)
        if ended is None:
            print("  batch %s is gone; submitting again" % pending["batch_id"], flush=True)
            clear_pending()
        else:
            ok, err = apply_batch_results(client, pending, cache)
            clear_pending()
            print("  results: %d ok, %d failed" % (ok, err), flush=True)
            todo = [row for row in todo if cache_key(row) not in cache]
            if not todo:
                return

    items = []
    requests = []
    for n, row in enumerate(todo):
        cid = "job-%d" % n
        items.append({"custom_id": cid, "key": cache_key(row)})
        requests.append(Request(
            custom_id=cid,
            params=MessageCreateParamsNonStreaming(**params(row, model)),
        ))

    batch = client.messages.batches.create(requests=requests)
    # Persist before polling. The pipeline kills this process after one hour.
    save_pending(batch.id, model, items)
    print("  batch %s submitted, %d requests" % (batch.id, len(requests)), flush=True)
    ended = poll_until_ended(client, batch.id, poll)
    if ended is None:
        print("  batch %s disappeared before it ended" % batch.id, flush=True)
        clear_pending()
        return
    ok, err = apply_batch_results(client, load_pending(), cache)
    clear_pending()
    print("  results: %d ok, %d failed" % (ok, err), flush=True)


UPDATE_JOB = """
UPDATE jobs SET
  description_consolidated = COALESCE(%(description_consolidated)s, description_consolidated),
  title_cleaned = %(title_cleaned)s, tech_stack = %(tech_stack)s, keywords = %(keywords)s,
  skills_raw = %(skills_raw)s,
  years_experience_min = %(years_experience_min)s, years_experience_max = %(years_experience_max)s,
  title_category = %(title_category)s, seniority_category = %(seniority_category)s,
  location_category = %(location_category)s, work_model_category = %(work_model_category)s,
  is_it_job = %(is_it_job)s, it_confidence = %(it_confidence)s,
  model_version = %(model_version)s, prompt_version = %(prompt_version)s,
  updated_at = now()
WHERE job_url = %(job_url)s
"""


def to_update(row: dict) -> dict:
    info, cls = row["extracted_info"], row["classification"]
    return {
        "job_url": row.get("job_url"),
        "description_consolidated": row.get("description_consolidated"),
        "title_cleaned": info["title_cleaned"],
        "tech_stack": json.dumps(info["tech_stack"], ensure_ascii=False),
        "keywords": json.dumps(info["keywords"], ensure_ascii=False),
        "skills_raw": json.dumps(info["skills_raw"], ensure_ascii=False),
        "years_experience_min": info["years_experience_min"],
        "years_experience_max": info["years_experience_max"],
        **cls,
        "is_it_job": row["is_it_job"],
        "it_confidence": row["it_confidence"],
        "model_version": row["model_version"],
        "prompt_version": row["prompt_version"],
    }


def write_db(rows: list[dict], conn=None, batch: int = 500) -> None:
    """UPDATE, never upsert: ingest.py creates the row and owns the crawl columns."""
    from db import connect

    own = conn is None
    conn = conn or connect()
    updates = [to_update(r) for r in rows]
    for i in range(0, len(updates), batch):
        with conn.cursor() as cur:
            cur.executemany(UPDATE_JOB, updates[i:i + batch])
        conn.commit()
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM jobs WHERE job_url = ANY(%s)", ([u["job_url"] for u in updates],))
        found = cur.fetchone()["n"]
    print("db      : %d rows updated, %d had no row in jobs" % (found, len(updates) - found), flush=True)
    if own:
        conn.close()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-db", action="store_true", help="write the JSONL files only")
    ap.add_argument("--input")
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--sync", action="store_true",
                    help="call the Messages API directly instead of the Batch API")
    ap.add_argument("--poll", type=int, default=60, help="batch poll interval, seconds")
    ap.add_argument("--drop-threshold", type=float, default=0.7,
                    help="drop a posting only when is_it_job is false at or above this confidence")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    src = pick_input(args.input)
    rows = read_jsonl(src)
    if args.limit:
        rows = rows[:args.limit]

    cache = load_cache()
    todo = [r for r in rows if cache_key(r) not in cache]

    print("input   : %s" % src, flush=True)
    print("rows    : %d, %d already cached, %d to call"
          % (len(rows), len(rows) - len(todo), len(todo)), flush=True)
    print("model   : %s   prompt: %s" % (args.model, PROMPT_VERSION), flush=True)
    print("mode    : %s" % ("sync" if args.sync else "batch (half price)"), flush=True)

    if args.dry_run:
        if todo:
            print("\n--- first request would be:\n%s\n" % build_user(todo[0])[:600], flush=True)
        print("dry run - nothing called", flush=True)
        return 0

    if todo:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            sys.exit("ANTHROPIC_API_KEY not set")
        client = Anthropic()
        if args.sync:
            run_sync(client, todo, args.model, cache)
        else:
            run_batch(client, todo, args.model, cache, args.poll)

    kept, dropped, missing = [], [], 0
    for row in rows:
        facts = cache.get(cache_key(row))
        if facts is None:
            missing += 1
            continue
        out = to_output_row(row, facts, args.model)
        if facts.get("is_it_job") is False and (facts.get("it_confidence") or 0) >= args.drop_threshold:
            dropped.append(out)
        else:
            kept.append(out)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    for path, data in ((OUT_PATH, kept), (NON_IT_PATH, dropped)):
        with path.open("w", encoding="utf-8") as fh:
            for r in data:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    print("\nkept    : %d -> %s" % (len(kept), OUT_PATH), flush=True)
    print("non-IT  : %d -> %s (dropped at confidence >= %.2f)"
          % (len(dropped), NON_IT_PATH, args.drop_threshold), flush=True)
    if not args.no_db:
        write_db(kept + dropped)
    if missing:
        print("missing : %d rows had no result — rerun to pick them up" % missing, flush=True)
    return 1 if missing and not kept else 0


if __name__ == "__main__":
    sys.exit(main())
