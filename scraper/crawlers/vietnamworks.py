"""VietnamWorks crawler via the ms.vietnamworks.com job-search API.

POST https://ms.vietnamworks.com/job-search/v1.0/search with jobFunction
parentId=5 (IT). Returns up to 50 jobs per page with full descriptions.

Rewritten to use PoliteClient (honest UA, robots check, delay) instead of
Playwright request context with a fake Chrome UA.
"""

import argparse
import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from crawlers.base import write_jsonl, write_seen
from crawlers.polite import BlockedError, PoliteClient

ENDPOINT = "https://ms.vietnamworks.com/job-search/v1.0/search"

BODY_TEMPLATE = {
    "userId": 0,
    "query": "",
    "filter": [
        {"field": "jobFunction", "value": '[{"parentId":5,"childrenIds":[-1]}]'}
    ],
    "ranges": [],
    "order": [],
    "hitsPerPage": 50,
    "page": 0,
    "retrieveFields": [
        "address", "benefits", "jobTitle", "salaryMax", "isSalaryVisible",
        "jobLevelVI", "salaryMin", "companyLogo", "userId", "jobLevel",
        "jobLevelId", "jobId", "jobUrl", "companyId", "approvedOn",
        "isAnonymous", "alias", "expiredOn", "industries", "industriesV3",
        "workingLocations", "services", "companyName", "salary", "onlineOn",
        "skills", "jobDescription", "jobRequirement", "prettySalary",
        "languageSelectedVI", "languageSelected", "typeWorkingId", "createdOn",
        "numOfApplications", "numberOfRecruits",
    ],
    "summaryVersion": "",
    "variants": "test",
}


def clean_html(html: str) -> str:
    if not html:
        return ""
    return BeautifulSoup(html, "lxml").get_text("\n", strip=True)


def parse_job(j: dict) -> dict:
    job_url = j.get("jobUrl")
    if not job_url and j.get("alias") and j.get("jobId"):
        job_url = f"https://www.vietnamworks.com/{j['alias']}-{j['jobId']}-jv"

    locs = j.get("workingLocations") or []
    location = locs[0].get("cityNameVI") or locs[0].get("address") if locs else None

    salary = j.get("prettySalary")
    if not salary and j.get("isSalaryVisible") and j.get("salaryMax"):
        salary = f"{j.get('salaryMin') or ''}-{j.get('salaryMax')}".strip("-")

    skills = [s.get("skillName") for s in (j.get("skills") or []) if s.get("skillName")]
    industries = [
        i.get("industryV3NameVI")
        for i in (j.get("industriesV3") or [])
        if i.get("industryV3NameVI")
    ]

    description = "\n".join(
        [clean_html(j.get("jobDescription")), clean_html(j.get("jobRequirement"))]
    ).strip()

    return {
        "site": "vietnamworks",
        "job_url": job_url,
        "title": j.get("jobTitle"),
        "company": j.get("companyName"),
        "location": location,
        "salary": salary,
        "experience_level": j.get("jobLevel"),
        "skills": skills,
        "description": description,
        "date_posted": j.get("createdOn"),
        "industries": industries,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl VietnamWorks IT jobs via API")
    parser.add_argument("--pages", type=int, default=20)
    parser.add_argument("--delay", type=float, default=3.0)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--out", type=str, default="data/raw/vietnamworks.jsonl")
    args = parser.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()

    client = PoliteClient(delay=args.delay)
    seen = set()
    total = 0
    complete, error = False, None
    try:
        for page_num in range(args.pages):
            body = {**BODY_TEMPLATE, "page": page_num}
            resp = client.post(ENDPOINT, json=body)
            jobs = resp.json().get("data") or []
            if not jobs:
                complete = True  # an empty page is the only proof we reached the end
                break
            rows = [parse_job(j) for j in jobs]
            rows = [r for r in rows if r["job_url"] and r["job_url"] not in seen]
            for r in rows:
                seen.add(r["job_url"])
            if args.limit and total + len(rows) > args.limit:
                rows = rows[: args.limit - total]
            write_jsonl(out, rows)
            total += len(rows)
            print(f"page {page_num + 1}: {len(rows)} jobs (total {total})", flush=True)
            if args.limit and total >= args.limit:
                error = f"stopped at --limit {args.limit}"
                break
        else:
            error = f"hit --pages {args.pages} before the listing ended"
    except (BlockedError, requests.RequestException) as exc:
        error = str(exc)
        print(f"STOP -- {exc}", flush=True)

    write_seen("vietnamworks", seen, complete, error=error)
    print(f"saved {total} jobs to {out}")


if __name__ == "__main__":
    main()
