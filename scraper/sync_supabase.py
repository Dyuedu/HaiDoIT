"""Sync classified.jsonl → Supabase Postgres (upsert).

Reads the final pipeline output and upserts each job into the `jobs` table.
Skips rows that haven't changed (based on updated_at).

Needs SUPABASE_URL and SUPABASE_SERVICE_KEY in the environment.
"""

import json
import os
import sys
from pathlib import Path

from supabase import create_client


INPUT_PATH = "data/classified.jsonl"
TABLE = "jobs"
BATCH_SIZE = 500


def load_rows(path: str) -> list[dict]:
    rows = []
    p = Path(path)
    if not p.exists():
        print(f"  {path} not found", flush=True)
        return rows
    with p.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def to_record(row: dict) -> dict | None:
    job_url = row.get("job_url")
    if not job_url:
        return None

    extracted = row.get("extracted_info") or {}
    classification = row.get("classification") or {}

    return {
        "job_url": job_url,
        "site": row.get("site"),
        "job_id": row.get("job_id"),
        "title": row.get("title"),
        "company": row.get("company"),
        "location": row.get("location"),
        "salary": row.get("salary"),
        "experience_level": row.get("experience_level"),
        "job_level": row.get("job_level"),
        "employment_type": row.get("employment_type"),
        "work_model": row.get("work_model"),
        "skills": json.dumps(row.get("skills") or [], ensure_ascii=False),
        "description": row.get("description"),
        "description_consolidated": row.get("description_consolidated"),
        "date_posted": row.get("date_posted"),
        "valid_through": row.get("valid_through"),
        "title_cleaned": extracted.get("title_cleaned"),
        "tech_stack": json.dumps(extracted.get("tech_stack") or [], ensure_ascii=False),
        "keywords": json.dumps(extracted.get("keywords") or [], ensure_ascii=False),
        "title_category": classification.get("title_category"),
        "seniority_category": classification.get("seniority_category"),
        "location_category": classification.get("location_category"),
        "work_model_category": classification.get("work_model_category"),
    }


def main() -> None:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not url or not key:
        print("Set SUPABASE_URL and SUPABASE_SERVICE_KEY", file=sys.stderr)
        sys.exit(1)

    client = create_client(url, key)

    rows = load_rows(INPUT_PATH)
    if not rows:
        print("No rows to sync")
        return

    records = [r for r in (to_record(row) for row in rows) if r]
    print(f"{len(records)} records to upsert", flush=True)

    upserted = 0
    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i : i + BATCH_SIZE]
        client.table(TABLE).upsert(
            batch,
            on_conflict="job_url",
            default_to_null=False,
        ).execute()
        upserted += len(batch)
        print(f"  upserted {upserted}/{len(records)}", flush=True)

    print(f"Sync done: {upserted} jobs → Supabase", flush=True)


if __name__ == "__main__":
    main()
