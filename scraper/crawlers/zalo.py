"""Zalo Careers crawler (https://zalo.careers) via its public JSON API.

GET /api/v2/jobs?option=queryJobs&count=N&teams=<slug> returns every open job
of a team with full description and requirements, so one request per team is
enough. Non-tech teams are kept; step-03 filters them out.
"""

import argparse
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

from crawlers.base import write_jsonl
from crawlers.polite import PoliteClient

BASE = "https://zalo.careers"
JOBS_API = f"{BASE}/api/v2/jobs"
TEAMS_API = f"{BASE}/api/v2/teams"


def text_of(html: str | None) -> str:
    return BeautifulSoup(html or "", "lxml").get_text("\n", strip=True)


def iso_date(text: str | None) -> str | None:
    try:
        return datetime.strptime(text or "", "%d %b %Y").date().isoformat()
    except ValueError:
        return None


def parse_job(j: dict, team: str) -> dict:
    description = "\n".join(
        part for part in (text_of(j.get("desc")), text_of(j.get("require"))) if part
    )
    return {
        "site": "zalo",
        "job_url": f"{BASE}/job/{j.get('slug')}",
        "title": (j.get("name") or "").strip(),
        "company": "Zalo (VNG)",
        "team": team,
        "location": j.get("locationName"),
        "summary": text_of(j.get("summary")),
        "description": description,
        "date_posted": iso_date(j.get("createDate")),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl Zalo Careers jobs via API")
    parser.add_argument("--delay", type=float, default=2.0)
    parser.add_argument("--out", type=str, default="data/raw/zalo.jsonl")
    args = parser.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()

    client = PoliteClient(delay=args.delay)
    teams = client.get(TEAMS_API).json().get("data") or []
    total = 0
    for team in teams:
        params = {"option": "queryJobs", "count": 500, "teams": team["slug"]}
        jobs = client.get(JOBS_API, params=params).json().get("data") or []
        rows = [parse_job(j, team["name"]) for j in jobs if j.get("slug")]
        write_jsonl(out, rows)
        total += len(rows)
        print(f"{team['name']}: {len(rows)} jobs (total {total})", flush=True)

    print(f"saved {total} jobs to {out}")


if __name__ == "__main__":
    main()
