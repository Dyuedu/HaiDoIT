"""VietnamWorks crawler via the ms.vietnamworks.com job-search API.

The site's frontend calls POST https://ms.vietnamworks.com/job-search/v1.0/search
with jobFunction parentId=5 (IT). Returns 756 IT jobs across 16 pages of 50,
including full description, skills, level, salary, and locations.
"""

import argparse
import json
from pathlib import Path

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from crawlers.base import write_jsonl

ENDPOINT = "https://ms.vietnamworks.com/job-search/v1.0/search"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

BODY = {
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
        "address",
        "benefits",
        "jobTitle",
        "salaryMax",
        "isSalaryVisible",
        "jobLevelVI",
        "isShowLogo",
        "salaryMin",
        "companyLogo",
        "userId",
        "jobLevel",
        "jobLevelId",
        "jobId",
        "jobUrl",
        "companyId",
        "approvedOn",
        "isAnonymous",
        "alias",
        "expiredOn",
        "industries",
        "industriesV3",
        "workingLocations",
        "services",
        "companyName",
        "salary",
        "onlineOn",
        "onlineOnText",
        "simpleServices",
        "visibilityDisplay",
        "isShowLogoInSearch",
        "priorityOrder",
        "skills",
        "profilePublishedSiteMask",
        "jobDescription",
        "jobRequirement",
        "prettySalary",
        "requiredCoverLetter",
        "languageSelectedVI",
        "languageSelected",
        "languageSelectedId",
        "typeWorkingId",
        "createdOn",
        "isAdrLiteJob",
        "applicantSignal",
        "numOfApplications",
        "numberOfRecruits",
        "exposureStatus",
        "isTopPriorityV4",
        "topPriorityType",
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
        [
            clean_html(j.get("jobDescription")),
            clean_html(j.get("jobRequirement")),
        ]
    ).strip()

    return {
        "site": "vietnamworks",
        "job_url": job_url,
        "title": j.get("jobTitle"),
        "company": j.get("companyName"),
        "location": location,
        "salary": salary,
        "experience_level": j.get("jobLevel"),
        "posted_at": j.get("approvedOnText"),
        "skills": skills,
        "description": description,
        "date_posted": j.get("createdOn"),
        "industries": industries,
    }


def fetch_page(ctx, page_num: int) -> list[dict]:
    body = {**BODY, "page": page_num}
    resp = ctx.post(
        ENDPOINT,
        data=json.dumps(body),
        headers={"Content-Type": "application/json"},
    )
    payload = resp.json()
    return [parse_job(j) for j in payload.get("data", [])]


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl VietnamWorks IT jobs via API")
    parser.add_argument("--pages", type=int, default=16)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--out", type=str, default="data/raw/vietnamworks.jsonl")
    args = parser.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()

    seen = set()
    total = 0
    with sync_playwright() as p:
        ctx = p.request.new_context(user_agent=USER_AGENT)
        for page_num in range(args.pages):
            rows = fetch_page(ctx, page_num)
            if not rows:
                break
            rows = [r for r in rows if r["job_url"] and r["job_url"] not in seen]
            for r in rows:
                seen.add(r["job_url"])
            if args.limit and total + len(rows) > args.limit:
                rows = rows[: args.limit - total]
            write_jsonl(out, rows)
            total += len(rows)
            print(f"page {page_num + 1}: {len(rows)} jobs (total {total})", flush=True)
            if args.limit and total >= args.limit:
                break
        ctx.dispose()

    print(f"saved {total} jobs to {out}")


if __name__ == "__main__":
    main()
