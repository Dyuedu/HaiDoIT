"""Upsert pipeline output into Postgres (Supabase) over the shared pooler.

Usage:
    python sync_pg.py                      # auto-pick the richest file in data/
    python sync_pg.py --input data/dedup.jsonl
    python sync_pg.py --dry-run            # parse and report, write nothing

Needs DATABASE_URL in the environment, e.g.
    postgresql://postgres.<ref>:<password>@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres

Which Supabase endpoint to use, measured from this VPS:
  * direct   db.<ref>.supabase.co:5432   AAAA only -- unreachable, the VPS has
             no global IPv6. Needs the IPv4 add-on.
  * session  pooler:5432                 IPv4, prepared statements supported.
             This is the one to use.
  * trans.   pooler:6543                 IPv4, no prepared statements.

On 6543 the connection sets prepare_threshold=None automatically, because the
transaction-mode pooler cannot handle prepared statements:
https://supabase.com/docs/guides/troubleshooting/disabling-prepared-statements-qL8lEL

Writes two tables:
  jobs              one row per job_url, upserted (latest state)
  job_observations  one row per job_url per day — the daily beat. A snapshot is
                    a photo of a day that has passed; it cannot be re-crawled.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

# Richest first: whatever exists furthest down the pipeline wins.
CANDIDATES = [
    "data/extracted.jsonl",
    "data/classified.jsonl",
    "data/step-07-jev-extracted.jsonl",
    "data/consolidated.jsonl",
    "data/dedup.jsonl",
]

COLUMNS = [
    "job_url", "site", "job_id", "title", "company", "location", "salary",
    "experience_level", "job_level", "employment_type", "work_model", "skills",
    "description", "description_consolidated", "date_posted", "valid_through",
    "title_cleaned", "tech_stack", "keywords",
    "title_category", "seniority_category", "location_category", "work_model_category",
    "skills_raw", "years_experience_min", "years_experience_max",
    "is_it_job", "it_confidence", "model_version", "prompt_version",
]
JSONB = {"skills", "tech_stack", "keywords", "skills_raw"}


def pick_input(explicit: str | None) -> Path:
    if explicit:
        p = Path(explicit)
        if not p.exists():
            sys.exit("input not found: %s" % p)
        return p
    for c in CANDIDATES:
        p = Path(c)
        if p.exists() and p.stat().st_size > 0:
            return p
    sys.exit("no pipeline output found; looked for: %s" % ", ".join(CANDIDATES))


def load(path: Path) -> list[dict]:
    rows = []
    bad = 0
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                bad += 1
    if bad:
        print("  skipped %d unparseable lines" % bad, flush=True)
    return rows


def to_record(row: dict) -> dict | None:
    """Flatten one pipeline row. Missing stages simply leave columns NULL."""
    job_url = row.get("job_url")
    if not job_url:
        return None
    extracted = row.get("extracted_info") or {}
    classification = row.get("classification") or {}

    rec = {c: None for c in COLUMNS}
    rec.update({
        "job_url": job_url,
        "site": row.get("site") or "unknown",
        "job_id": row.get("job_id"),
        "title": row.get("title"),
        "company": row.get("company"),
        "location": row.get("location"),
        "salary": row.get("salary"),
        "experience_level": row.get("experience_level"),
        "job_level": row.get("job_level"),
        "employment_type": row.get("employment_type"),
        "work_model": row.get("work_model"),
        "skills": row.get("skills") or [],
        "description": row.get("description"),
        "description_consolidated": row.get("description_consolidated"),
        "date_posted": row.get("date_posted"),
        "valid_through": row.get("valid_through"),
        "title_cleaned": extracted.get("title_cleaned"),
        "tech_stack": extracted.get("tech_stack") or [],
        "keywords": extracted.get("keywords") or [],
        "title_category": classification.get("title_category"),
        "seniority_category": classification.get("seniority_category"),
        "location_category": classification.get("location_category"),
        "work_model_category": classification.get("work_model_category"),
        # Nguyen van, khong dich — xem FR-6 va ghi chu trong extract_gate.py
        "skills_raw": extracted.get("skills_raw") or [],
        "years_experience_min": extracted.get("years_experience_min"),
        "years_experience_max": extracted.get("years_experience_max"),
        "is_it_job": row.get("is_it_job"),
        "it_confidence": row.get("it_confidence"),
        "model_version": row.get("model_version"),
        "prompt_version": row.get("prompt_version"),
    })
    for k in JSONB:
        rec[k] = json.dumps(rec[k], ensure_ascii=False)

    # Mot so nguon nhet nguyen object JSON-LD vao mot truong van ban — careerlink
    # tra experience_level = {"@type": "OccupationalExperienceRequirements",
    # "monthsOfExperience": 12}. Giu lai duoi dang JSON thay vi lam vo ca lo;
    # viec rut ra so nam la cua buoc trich xuat (Story 1.6), khong phai cua sync.
    for k, v in rec.items():
        if k not in JSONB and isinstance(v, (dict, list)):
            rec[k] = json.dumps(v, ensure_ascii=False)
    return rec


UPSERT = """
INSERT INTO jobs ({cols})
VALUES ({ph})
ON CONFLICT (job_url) DO UPDATE SET
  {sets},
  updated_at = now()
""".format(
    cols=", ".join(COLUMNS),
    ph=", ".join("%({})s".format(c) for c in COLUMNS),
    sets=",\n  ".join(
        "{c} = COALESCE(EXCLUDED.{c}, jobs.{c})".format(c=c)
        for c in COLUMNS if c != "job_url"
    ),
)

OBSERVE = """
INSERT INTO job_observations (job_url, snapshot_date, site)
VALUES (%(job_url)s, %(snapshot_date)s, %(site)s)
ON CONFLICT (job_url, snapshot_date) DO NOTHING
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--batch", type=int, default=500)
    ap.add_argument("--snapshot", default=date.today().isoformat(),
                    help="snapshot date, YYYY-MM-DD (default: today)")
    args = ap.parse_args()

    src = pick_input(args.input)
    raw = load(src)
    records, skipped = [], 0
    seen = set()
    for row in raw:
        rec = to_record(row)
        if rec is None:
            skipped += 1
            continue
        if rec["job_url"] in seen:      # same url twice in one file
            continue
        seen.add(rec["job_url"])
        records.append(rec)

    print("input   : %s" % src, flush=True)
    print("rows    : %d read, %d usable, %d without job_url"
          % (len(raw), len(records), skipped), flush=True)
    print("snapshot: %s" % args.snapshot, flush=True)

    if args.dry_run:
        print("dry run - nothing written", flush=True)
        return 0

    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        sys.exit("DATABASE_URL not set")

    # Port 6543 is the transaction-mode pooler: no prepared statements there.
    # Port 5432 (session pooler or direct) handles them fine, so leave the
    # default and keep the speed-up.
    transaction_pooler = ":6543" in dsn
    opts = {"prepare_threshold": None} if transaction_pooler else {}
    print("endpoint: %s" % ("transaction pooler 6543, prepared statements off"
                            if transaction_pooler else "session 5432, prepared statements on"),
          flush=True)
    with psycopg.connect(dsn, row_factory=dict_row, connect_timeout=30, **opts) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), current_user, version()")
            info = cur.fetchone()
            print("connected: %s as %s" % (info["current_database"], info["current_user"]),
                  flush=True)

        written = 0
        for i in range(0, len(records), args.batch):
            chunk = records[i:i + args.batch]
            with conn.cursor() as cur:
                cur.executemany(UPSERT, chunk)
                cur.executemany(OBSERVE, [
                    {"job_url": r["job_url"], "snapshot_date": args.snapshot, "site": r["site"]}
                    for r in chunk
                ])
            conn.commit()
            written += len(chunk)
            print("  upserted %d/%d" % (written, len(records)), flush=True)

        with conn.cursor() as cur:
            cur.execute("SELECT count(*) AS n FROM jobs")
            total = cur.fetchone()["n"]
            cur.execute("SELECT count(*) AS n FROM job_observations WHERE snapshot_date = %s",
                        (args.snapshot,))
            today = cur.fetchone()["n"]
    print("done: %d rows in jobs, %d observations for %s"
          % (total, today, args.snapshot), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
