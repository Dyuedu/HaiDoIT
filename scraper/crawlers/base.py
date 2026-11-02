"""Shared helpers for the job-board crawlers."""

import json
import time
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
