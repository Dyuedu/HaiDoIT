"""Beat one: write what the crawl saw today. No model, no API key, no vocabulary.

    python ingest.py                         # today's snapshot, Asia/Ho_Chi_Minh
    python ingest.py --snapshot 2026-11-05
    python ingest.py --dry-run

Reads data/redacted/*.jsonl and data/seen/<snapshot>/<source>.json. Writes:

  jobs              crawl columns only. Extraction columns belong to extract.py,
                    so neither step can overwrite the other's work.
  job_observations  one row per job listed that day, taken from the seen file. Not
                    from the raw file: a crawler that skips known jobs writes no
                    raw row for a job that is still open.
  job_content_versions  one row per distinct description of a job. Record only, for
                    now: it measures how often JDs change, and nothing is
                    re-extracted because of it. extract.py's cache key is untouched.
  source_runs       one row per source per day. A job missing from a run with
                    listing_complete = false proves nothing; only a complete run
                    can say a job is gone.

An expected source with no seen file crashed before finishing; it is recorded as
an incomplete run, so a dead source never looks like every job was taken down.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from crawlers.base import read_jsonl, today_snapshot
from db import connect

# TopCV is not here: it only opens to a Cloudflare-evading browser, so it stays manual
# (ARCHITECTURE-SPINE.md, AD-16). A manual topcv run still writes a seen file, so if
# you pass --sources topcv by hand, ingest records its observations.
AUTO_SOURCES = ["zalo", "itnavi", "careerlink", "vietnamworks", "momo", "topdev", "itviec"]

CRAWL_COLUMNS = [
    "job_url", "site", "job_id", "title", "company", "location", "salary",
    "experience_level", "job_level", "employment_type", "work_model", "skills",
    "description", "date_posted", "valid_through",
]

UPSERT_JOB = """
INSERT INTO jobs ({cols}) VALUES ({ph})
ON CONFLICT (job_url) DO UPDATE SET
  {sets},
  updated_at = now()
""".format(
    cols=", ".join(CRAWL_COLUMNS),
    ph=", ".join("%({})s".format(c) for c in CRAWL_COLUMNS),
    sets=",\n  ".join("{c} = COALESCE(EXCLUDED.{c}, jobs.{c})".format(c=c)
                      for c in CRAWL_COLUMNS if c != "job_url"),
)

INSERT_OBSERVATION = """
INSERT INTO job_observations (job_url, snapshot_date, site)
VALUES (%s, %s, %s)
ON CONFLICT (job_url, snapshot_date) DO NOTHING
"""

UPSERT_RUN = """
INSERT INTO source_runs (source, snapshot_date, listing_complete, seen_count, unresolved_count, error)
VALUES (%s, %s, %s, %s, %s, %s)
ON CONFLICT (source, snapshot_date) DO UPDATE SET
  listing_complete = source_runs.listing_complete OR EXCLUDED.listing_complete,
  seen_count = GREATEST(source_runs.seen_count, EXCLUDED.seen_count),
  unresolved_count = EXCLUDED.unresolved_count,
  error = CASE WHEN source_runs.listing_complete OR EXCLUDED.listing_complete
               THEN NULL ELSE EXCLUDED.error END,
  finished_at = now()
"""


# A listing cannot honestly lose over half its jobs overnight (FR-1 alarms at the
# same 50%). A crawler that thought it finished after a slow page would otherwise
# mark everything past that page as taken down.
MIN_LISTING_RATIO = 0.5


INSERT_VERSION = """
INSERT INTO job_content_versions (job_url, content_hash, site, first_seen_date)
VALUES (%s, %s, %s, %s)
ON CONFLICT (job_url, content_hash) DO NOTHING
"""


def content_hash(description: str | None) -> str | None:
    """Hash of the text with whitespace collapsed, so reflowing alone is not a change."""
    text = " ".join((description or "").split())
    return hashlib.sha256(text.encode("utf-8")).hexdigest() if text else None


def changed_jobs(cur, snapshot: str) -> dict[str, int]:
    """Per site, jobs whose description first took a new form on this snapshot."""
    cur.execute("""SELECT n.site, count(*) AS n
                   FROM job_content_versions n
                   WHERE n.first_seen_date = %s AND EXISTS (
                     SELECT 1 FROM job_content_versions o
                     WHERE o.job_url = n.job_url AND o.first_seen_date < n.first_seen_date)
                   GROUP BY 1""", (snapshot,))
    return {r["site"]: r["n"] for r in cur.fetchall()}


def to_record(row: dict) -> dict | None:
    if not row.get("job_url"):
        return None
    rec = {c: row.get(c) for c in CRAWL_COLUMNS}
    rec["site"] = row.get("site") or "unknown"
    rec["skills"] = json.dumps(row["skills"], ensure_ascii=False) if row.get("skills") else None
    for k, v in rec.items():
        # careerlink sends experience_level as a JSON-LD object; keep it as text.
        if k != "skills" and isinstance(v, (dict, list)):
            rec[k] = json.dumps(v, ensure_ascii=False)
    return rec


def load_records(redacted_dir: Path) -> list[dict]:
    records: dict[str, dict] = {}
    for path in sorted(redacted_dir.glob("*.jsonl")):
        for row in read_jsonl(path):
            rec = to_record(row)
            if rec:
                records[rec["job_url"]] = rec
    return list(records.values())


def load_seen(seen_root: Path, snapshot: str, sources: list[str]) -> dict[str, dict]:
    seen = {}
    day = seen_root / snapshot
    for source in sources:
        path = day / f"{source}.json"
        if path.exists():
            seen[source] = json.loads(path.read_text(encoding="utf-8"))
        else:
            seen[source] = {"job_urls": [], "listing_complete": False, "unresolved": 0,
                            "error": "no seen file: crawler did not finish"}
    return seen


def gone_jobs(cur, site: str, snapshot: str) -> list[str]:
    """Jobs listed at the previous complete run of a source, absent from this one.

    Empty unless this run is complete: an incomplete run proves nothing.
    """
    cur.execute("SELECT listing_complete FROM source_runs WHERE source = %s AND snapshot_date = %s",
                (site, snapshot))
    row = cur.fetchone()
    if not row or not row["listing_complete"]:
        return []
    cur.execute("""SELECT max(snapshot_date) AS d FROM source_runs
                   WHERE source = %s AND listing_complete AND snapshot_date < %s""", (site, snapshot))
    prev = cur.fetchone()["d"]
    if prev is None:
        return []
    cur.execute("""SELECT job_url FROM job_observations WHERE site = %s AND snapshot_date = %s
                   EXCEPT
                   SELECT job_url FROM job_observations WHERE site = %s AND snapshot_date = %s
                   ORDER BY 1""", (site, prev, site, snapshot))
    return [r["job_url"] for r in cur.fetchall()]


def ingest_snapshot(conn, snapshot: str, records: list[dict], seen: dict[str, dict], batch: int = 500) -> None:
    for i in range(0, len(records), batch):
        with conn.cursor() as cur:
            chunk = records[i:i + batch]
            cur.executemany(UPSERT_JOB, chunk)
            versions = [(r["job_url"], h, r["site"], snapshot) for r in chunk
                        if (h := content_hash(r.get("description")))]
            if versions:
                cur.executemany(INSERT_VERSION, versions)
        conn.commit()
    for source, doc in seen.items():
        with conn.cursor() as cur:
            urls = doc["job_urls"]
            complete, error = doc["listing_complete"], doc.get("error")
            cur.execute("""SELECT seen_count FROM source_runs
                           WHERE source = %s AND listing_complete AND snapshot_date < %s
                           ORDER BY snapshot_date DESC LIMIT 1""", (source, snapshot))
            prev = cur.fetchone()
            if complete and prev and len(urls) < prev["seen_count"] * MIN_LISTING_RATIO:
                complete = False
                error = "listing shrank from %d to %d, not trusted as complete" % (prev["seen_count"], len(urls))
            if urls:
                cur.executemany(INSERT_OBSERVATION, [(u, snapshot, source) for u in urls])
            cur.execute(UPSERT_RUN, (source, snapshot, complete, len(urls), doc.get("unresolved") or 0, error))
        conn.commit()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", default=today_snapshot())
    ap.add_argument("--sources", default=",".join(AUTO_SOURCES))
    ap.add_argument("--redacted", default="data/redacted")
    ap.add_argument("--seen", default="data/seen")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    sources = [s.strip() for s in args.sources.split(",") if s.strip()]
    records = load_records(Path(args.redacted))
    seen = load_seen(Path(args.seen), args.snapshot, sources)

    print("snapshot: %s" % args.snapshot, flush=True)
    print("jobs    : %d rows from %s" % (len(records), args.redacted), flush=True)
    for source, doc in seen.items():
        print("  %-14s listed=%-5d complete=%-5s unresolved=%d%s"
              % (source, len(doc["job_urls"]), doc["listing_complete"], doc.get("unresolved") or 0,
                 "  error: " + str(doc["error"])[:100] if doc.get("error") else ""), flush=True)
    if args.dry_run:
        print("dry run - nothing written", flush=True)
        return 0

    with connect() as conn:
        ingest_snapshot(conn, args.snapshot, records, seen)
        with conn.cursor() as cur:
            for source in sources:
                print("  %-14s gone since last complete run: %d"
                      % (source, len(gone_jobs(cur, source, args.snapshot))), flush=True)
            print("  jobs with a changed description: %s" % (changed_jobs(cur, args.snapshot) or "none"), flush=True)
            cur.execute("SELECT count(*) AS n FROM job_observations WHERE snapshot_date = %s", (args.snapshot,))
            print("done: %d observations for %s" % (cur.fetchone()["n"], args.snapshot), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
