"""Coarse filter: classify each job as tech vs non-tech using Jev (TypeSafe).

Reads data/full.jsonl and asks Jev one `choice` question `is_tech`, using only
title / company / skills / location / experience (NOT description).

Conservative drop rule: drop only when Jev says `non_tech` with confidence >= 0.7.
Everything else is kept and flagged.

Outputs:
- data/tech_filtered.jsonl   kept (tech + ambiguous) jobs
- data/non_tech.jsonl        confidently non-tech jobs
- data/jev-cache.jsonl       resumable cache with is_tech + tech_confidence

Needs TYPESAFE_API_KEY in the environment (or .env.local).
"""

import argparse
import concurrent.futures
import json
import os
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

from tqdm import tqdm

from crawlers.base import read_jsonl

ENDPOINT = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-latest"
DROP_CONFIDENCE = 0.7
MAX_WORKERS = 32

CACHE_LOCK = threading.Lock()


def load_key() -> str:
    key = os.environ.get("TYPESAFE_API_KEY")
    if key:
        return key
    envfile = Path(".env.local")
    if envfile.exists():
        for line in envfile.read_text(encoding="utf-8").splitlines():
            name, _, value = line.strip().partition("=")
            if name == "TYPESAFE_API_KEY" and value:
                return value
    sys.exit("Chưa có TYPESAFE_API_KEY (environment hoặc .env.local)")


def ask_jev(state: str, questions: dict) -> dict:
    body = json.dumps({"model": MODEL, "state": state, "questions": questions}).encode(
        "utf-8"
    )
    req = urllib.request.Request(
        ENDPOINT,
        data=body,
        headers={
            "Authorization": f"Bearer {load_key()}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        # Return a safe fallback or re-raise; for a threaded script, returning a dict helps avoid crashing everything.
        print(
            f"\nAPI Error: {e.code} {e.reason}: {e.read().decode('utf-8', 'replace')[:400]}",
            file=sys.stderr,
        )
        raise


QUESTION = {
    "is_tech": {
        "type": "choice",
        "instructions": "Is this a hands-on technical (tech) job?",
        "criteria": {
            "tech": (
                "Technical role: developer/engineer (backend, frontend, fullstack, mobile, "
                "embedded, game), data engineer, data scientist, data analyst, ML/AI engineer, "
                "DevOps/SRE/Cloud/Platform, QA/automation tester, security engineer, "
                "solution architect, system/network admin, IT support/helpdesk."
            ),
            "non_tech": (
                "Non-technical role: product owner/manager, project manager, scrum master, "
                "business analyst, UI/UX designer, graphic designer, and any non-IT role "
                "(sales, marketing, accounting, HR, admin, driver, retail, manufacturing, "
                "hospitality, etc.)."
            ),
        },
    }
}


def build_state(row: dict) -> str:
    return (
        f"Title: {row.get('title') or ''}\n"
        f"Company: {row.get('company') or ''}\n"
        f"Location: {row.get('location') or ''}\n"
        f"Experience: {row.get('experience_level') or ''}\n"
        f"Skills: {', '.join(row.get('skills') or [])}"
    )


def overwrite(path: Path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_outputs(cache: dict, args) -> None:
    all_rows = list(cache.values())
    tech = []
    nontech = []
    for r in all_rows:
        is_tech = r.get("is_tech")
        conf = float(r.get("tech_confidence") or 0)
        if is_tech == "non_tech" and conf >= DROP_CONFIDENCE:
            nontech.append(r)
        else:
            tech.append(r)
    overwrite(Path(args.tech_out), tech)
    overwrite(Path(args.nontech_out), nontech)
    print(f"\ntech (kept): {len(tech)}, non-tech (dropped): {len(nontech)}", flush=True)


def process_job(row: dict, cache: dict, cache_path: Path) -> None:
    """Worker function to process a single job listing."""
    try:
        res = ask_jev(build_state(row), QUESTION)
        ans = res["answers"]["is_tech"]
        merged = {
            **row,
            "is_tech": ans.get("choice"),
            "tech_confidence": ans.get("confidence"),
        }

        # Thread-safe dictionary update and file write
        with CACHE_LOCK:
            cache[row["job_url"]] = merged
            with cache_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(merged, ensure_ascii=False) + "\n")

    except Exception as e:
        print(f"\nFailed to process job {row.get('job_url')}: {e}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description="Coarse tech/non-tech filter with Jev")
    parser.add_argument("--in", dest="src", type=str, default="data/full.jsonl")
    parser.add_argument("--tech-out", type=str, default="data/tech_filtered.jsonl")
    parser.add_argument("--nontech-out", type=str, default="data/non_tech.jsonl")
    parser.add_argument("--cache", type=str, default="data/jev-cache.jsonl")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    rows = read_jsonl(args.src)
    dedup = {}
    for r in rows:
        dedup.setdefault(r.get("job_url"), r)
    rows = list(dedup.values())
    print(f"{len(rows)} unique listings", flush=True)

    cache = {r["job_url"]: r for r in read_jsonl(args.cache) if "job_url" in r}
    todo = [r for r in rows if r.get("job_url") not in cache]

    if args.limit:
        todo = todo[: args.limit]

    if not todo:
        print("all cached")
        write_outputs(cache, args)
        return

    print(
        f"Will call Jev {len(todo)} times (~${len(todo) * 0.000022:.4f} total).",
        flush=True,
    )

    cache_path = Path(args.cache)
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    # Use ThreadPoolExecutor to run tasks concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all tasks to the executor
        futures = [executor.submit(process_job, row, cache, cache_path) for row in todo]

        # Use as_completed to update the progress bar as soon as a thread finishes
        for _ in tqdm(
            concurrent.futures.as_completed(futures),
            total=len(todo),
            desc="Classifying jobs",
            unit="job",
        ):
            pass

    write_outputs(cache, args)


if __name__ == "__main__":
    main()
