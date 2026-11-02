"""LinkedIn crawler (https://www.linkedin.com/jobs/search). Requires one manual login.

Run it, log in once in the Chrome window that opens, then leave it. The session
is saved under data/linkedin-profile so later runs stay logged in.
"""

import argparse
from pathlib import Path

from bs4 import BeautifulSoup

from crawlers.base import interactive_scrape
from crawlers.browser import webkit_context

PROFILE_DIR = "data/linkedin-profile-webkit"
SEARCH_URL = (
    "https://www.linkedin.com/jobs/search/"
    "?keywords=software%20engineer%20OR%20developer%20OR%20engineer"
    "&location=Vietnam&f_TPR=r2592000"
)
JOBS_SELECTOR = "a[href*='/jobs/view/']"


def parse_jobs(soup: BeautifulSoup) -> list[dict]:
    rows = []
    seen = set()
    for card in soup.select(
        "div.job-search-card, div.job-card-container, li.jobs-search-results__list-item"
    ):
        link = card.select_one("a.base-card__full-link, a[href*='/jobs/view/']")
        if not link:
            continue
        href = link["href"]
        path = href.split("?")[0].rstrip("/")
        if path.startswith("/jobs/view/"):
            job_id = path.split("/jobs/view/")[-1].split("/")[0]
            url = f"https://www.linkedin.com/jobs/view/{job_id}"
        elif path.startswith("http"):
            url = path
        else:
            url = "https://www.linkedin.com" + path
        if url in seen:
            continue
        seen.add(url)

        title_el = card.select_one("span.sr-only") or link
        title = title_el.get_text(strip=True)

        company = card.select_one("[class*='company-name'], [class*='companyName']")
        location = card.select_one("[class*='metadata-item'], [class*='location']")
        salary = card.select_one("[class*='salary']")

        rows.append(
            {
                "site": "linkedin",
                "job_url": url,
                "title": title,
                "company": company.get_text(strip=True) if company else None,
                "location": location.get_text(strip=True) if location else None,
                "salary": salary.get_text(strip=True) if salary else None,
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl LinkedIn jobs (manual login)")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--scrolls", type=int, default=40)
    parser.add_argument("--out", type=str, default="data/raw/linkedin.jsonl")
    args = parser.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    with webkit_context(PROFILE_DIR, headless=args.headless) as ctx:
        page = ctx.new_page()
        page.goto(SEARCH_URL, wait_until="domcontentloaded", timeout=60000)
        print(f"page title: {page.title()}", flush=True)
        print(
            "Log in (if asked) and scroll through pages. Scraping continuously — Ctrl+C to finish.",
            flush=True,
        )
        interactive_scrape(page, parse_jobs, out, label="linkedin")

    print(f"done -> {out}")


if __name__ == "__main__":
    main()
