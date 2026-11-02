"""ITNavi crawler (https://itnavi.com.vn/job) — IT-only board.

Listing pages (10 jobs each) give job ids via `div.jsl-item[data-id]`; the
detail comes from the JSON endpoint the page itself calls,
/ajax/get-job-by-id/{id}. A run saves at most --limit new jobs (default 150);
jobs already in the output file are skipped, so re-running continues.
"""

import argparse
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

from crawlers.base import read_jsonl, write_jsonl
from crawlers.polite import BlockedError, PoliteClient

BASE = "https://itnavi.com.vn"
LIST_URL = f"{BASE}/job"
DETAIL_URL = f"{BASE}/ajax/get-job-by-id/{{}}"


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


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl ITNavi jobs (resumable)")
    parser.add_argument("--limit", type=int, default=150, help="new jobs per run")
    parser.add_argument("--pages", type=int, default=80)
    parser.add_argument("--delay", type=float, default=3.0)
    parser.add_argument("--out", type=str, default="data/raw/itnavi.jsonl")
    args = parser.parse_args()

    out = Path(args.out)
    done = {r.get("job_id") for r in read_jsonl(out)}
    client = PoliteClient(delay=args.delay)
    saved = 0
    try:
        for page in range(1, args.pages + 1):
            soup = BeautifulSoup(client.get(f"{LIST_URL}?page={page}").text, "lxml")
            ids = [int(c["data-id"]) for c in soup.select("div.jsl-item[data-id]")]
            if not ids:
                break
            for job_id in ids:
                if job_id in done:
                    continue
                payload = client.get(DETAIL_URL.format(job_id)).json()
                d = payload.get("data") or {}
                if not payload.get("success") or not d.get("job_content"):
                    continue
                write_jsonl(out, [parse_job(d)])
                done.add(job_id)
                saved += 1
                if saved >= args.limit:
                    break
            print(f"page {page}: {saved} new jobs so far", flush=True)
            if saved >= args.limit:
                break
    except BlockedError as exc:
        print(f"STOP — blocked: {exc}", flush=True)

    print(f"saved {saved} new jobs, {len(done)} total in {out}")


if __name__ == "__main__":
    main()
