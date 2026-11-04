"""Shared helpers for the job-board crawlers."""

import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from bs4 import BeautifulSoup


def write_jsonl(path: Path, rows) -> None:
    """Append rows as JSON lines, creating parent directories."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_jsonl(path) -> list:
    """Read all JSON-line records from a file (empty list if missing)."""
    path = Path(path)
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def today_snapshot() -> str:
    """snapshot_id is YYYY-MM-DD in Asia/Ho_Chi_Minh (AD-15), whatever the host clock says."""
    override = os.environ.get("HAIDO_SNAPSHOT")
    if override:
        return override
    return datetime.now(timezone(timedelta(hours=7))).date().isoformat()


def write_seen(source: str, urls, complete: bool, unresolved: int = 0, error: str | None = None) -> Path:
    """Record what the listing showed in this run, whether or not details were fetched.

    This file, not the raw file, is the source of job_observations. Raw files say
    what we hold; a crawler that skips known jobs writes nothing for a job that
    is still open. `complete` says the whole listing was walked: only then does
    absence from the file mean the job is gone. A second run on the same day merges.
    """
    path = Path("data/seen") / today_snapshot() / f"{source}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    merged = list(dict.fromkeys(u for u in urls if u))
    if path.exists():
        old = json.loads(path.read_text(encoding="utf-8"))
        merged = list(dict.fromkeys(old["job_urls"] + merged))
        complete = complete or old["listing_complete"]
    doc = {
        "source": source,
        "snapshot": today_snapshot(),
        "listing_complete": complete,
        "unresolved": unresolved,
        "error": None if complete else error,
        "job_urls": merged,
    }
    path.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    print(f"seen: {len(merged)} jobs, listing_complete={complete}, unresolved={unresolved}", flush=True)
    return path


def interactive_scrape(page, parse_fn, out_path, *, interval=2.0, label="") -> dict:
    """Continuously scrape a page the user is manually navigating.

    The user logs in / scrolls / clicks "next page" in the visible browser while
    this loop re-reads the DOM every `interval` seconds, dedups by job_url, and
    rewrites `out_path` with everything collected so far. Runs until KeyboardInterrupt.
    """
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    collected = {}
    if out.exists():
        for row in read_jsonl(out):
            if row.get("job_url"):
                collected[row["job_url"]] = row
    try:
        while True:
            try:
                soup = BeautifulSoup(page.content(), "lxml")
                for row in parse_fn(soup):
                    url = row.get("job_url")
                    if url and url not in collected:
                        collected[url] = row
                with out.open("w", encoding="utf-8") as fh:
                    for row in collected.values():
                        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                print(f"[{label}] {len(collected)} unique jobs", flush=True)
            except Exception as exc:  # noqa: BLE001 - navigation in progress, keep scraping
                print(f"[{label}] scrape err: {str(exc)[:60]}", flush=True)
            time.sleep(interval)
    except KeyboardInterrupt:
        pass
    print(f"[{label}] done: {len(collected)} jobs -> {out}")
    return collected
