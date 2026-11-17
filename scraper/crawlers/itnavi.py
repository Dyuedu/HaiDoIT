"""ITNavi crawler (https://itnavi.com.vn/job) — IT-only board.

Listing pages (10 jobs each) give job ids via `div.jsl-item[data-id]`; the
detail comes from the JSON endpoint the page itself calls,
/ajax/get-job-by-id/{id}. A run fetches at most --limit new details (default 150)
and skips jobs already in the output file, but always walks the whole listing:
that walk is what proves a known job is still open.

The listing order drifts between requests, so a page can repeat only ids already
seen without being the end (#296). A page with no cards is fetched again up to
EMPTY_PAGE_TRIES times. The walk ends on a page that stays without cards, or after
STALE_PAGES pages in a row with no new id. It counts as complete only if it met
MIN_COVERAGE of the job total the page prints ("485 Việc làm"), as topdev.py does.
"""

import argparse
import re
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from crawlers.base import read_jsonl, write_jsonl, write_seen
from crawlers.polite import BlockedError, PoliteClient

BASE = "https://itnavi.com.vn"
LIST_URL = f"{BASE}/job"
DETAIL_URL = f"{BASE}/ajax/get-job-by-id/{{}}"
STALE_PAGES = 3
MIN_COVERAGE = 0.9
# 17/11 trên VPS trang 42 trả về không có tin, sáng hôm sau listing đủ 49 trang: tải lại rồi mới coi là hết.
EMPTY_PAGE_TRIES = 3


def listed_total(soup: BeautifulSoup) -> int | None:
    """The "N Việc làm" count the listing page shows, None if it is not there."""
    head = soup.select_one("div.js-tab__show h1")
    m = re.search(r"\d[\d.,]*", head.get_text(" ", strip=True)) if head else None
    return int(re.sub(r"\D", "", m.group(0))) if m else None


def iso_date(text: str | None) -> str | None:
    try:
        return datetime.strptime(text or "", "%b %d, %Y").date().isoformat()
    except ValueError:
        return None


def parse_job(d: dict) -> dict:
    lo, hi = d.get("job_salary_min"), d.get("job_salary_max")
    salary = d.get("job_salary")
    if lo or hi:
        salary = f"{lo or ''}-{hi or ''} {d.get('job_salary_currency') or ''}".strip()
    content = d.get("job_content") or ""
    return {
        "site": "itnavi",
        "job_id": d.get("job_id"),
        "job_url": d.get("job_slug"),
        "title": d.get("job_name"),
        "company": d.get("company_name"),
        "company_size": d.get("company_size"),
        "location": d.get("job_addresses"),
        "salary": salary,
        "experience_level": d.get("job_career_level"),
        "employment_type": d.get("job_career_type"),
        "skills": [s.get("name") for s in d.get("skill") or [] if s.get("name")],
        "description": BeautifulSoup(content, "lxml").get_text("\n", strip=True),
        "date_posted": iso_date(d.get("job_published_at_show")),
        "first_published": iso_date(d.get("job_published_at")),
    }


def covered(met: int, total: int | None) -> tuple[bool, str | None]:
    """(complete, error) for a walk that reached the end of the listing."""
    if total is None:
        print("listing total not found on the page; trusting the end of the listing", flush=True)
        return True, None
    if met >= total * MIN_COVERAGE:
        return True, None
    return False, f"met {met} of {total} listed jobs"


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl ITNavi jobs (resumable)")
    parser.add_argument("--limit", type=int, default=150, help="new job details per run")
    parser.add_argument("--pages", type=int, default=80)
    parser.add_argument("--delay", type=float, default=3.0)
    parser.add_argument("--out", type=str, default="data/raw/itnavi.jsonl")
    args = parser.parse_args()

    out = Path(args.out)
    # The listing gives ids only; the URL comes from the detail we already saved.
    known = {r.get("job_id"): r.get("job_url") for r in read_jsonl(out)}
    client = PoliteClient(delay=args.delay)
    seen_ids, saved, unresolved = set(), 0, 0
    complete, error = False, None
    total, stale = None, 0
    try:
        for page in range(1, args.pages + 1):
            for attempt in range(1, EMPTY_PAGE_TRIES + 1):
                soup = BeautifulSoup(client.get(f"{LIST_URL}?page={page}").text, "lxml")
                ids = [int(c["data-id"]) for c in soup.select("div.jsl-item[data-id]")]
                if ids or attempt == EMPTY_PAGE_TRIES:
                    break
                print(f"page {page}: empty, fetching again ({attempt + 1}/{EMPTY_PAGE_TRIES})", flush=True)
            page_total = listed_total(soup)
            if page_total is not None:
                total = max(total or 0, page_total)
            new_ids = [i for i in ids if i not in seen_ids]
            if not ids:
                print(f"end: page {page} is empty", flush=True)
                complete, error = covered(len(seen_ids), total)
                break
            if not new_ids:
                stale += 1
                if stale >= STALE_PAGES:
                    print(f"end: {stale} pages in a row with no new id", flush=True)
                    complete, error = covered(len(seen_ids), total)
                    break
                print(f"page {page}: no new id ({stale}/{STALE_PAGES})", flush=True)
                continue
            stale = 0
            for job_id in new_ids:
                seen_ids.add(job_id)
                if job_id in known:
                    continue
                if saved >= args.limit:  # keep walking the listing, stop fetching details
                    unresolved += 1
                    continue
                try:
                    payload = client.get(DETAIL_URL.format(job_id)).json()
                except requests.RequestException as exc:
                    print(f"detail {job_id}: {exc}", flush=True)
                    unresolved += 1
                    continue
                d = payload.get("data") or {}
                if not payload.get("success") or not d.get("job_content"):
                    unresolved += 1
                    continue
                row = parse_job(d)
                write_jsonl(out, [row])
                known[job_id] = row["job_url"]
                saved += 1
            print(f"page {page}: {len(seen_ids)} listed, {saved} new details", flush=True)
        else:
            error = f"hit --pages {args.pages} before the listing ended"
    except (BlockedError, requests.RequestException) as exc:
        error = str(exc)
        print(f"STOP -- {exc}", flush=True)

    write_seen("itnavi", [known[i] for i in seen_ids if i in known], complete,
               unresolved=unresolved, error=error)
    print(f"saved {saved} new jobs, {len(known)} total in {out}")


if __name__ == "__main__":
    main()
