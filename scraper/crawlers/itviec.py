"""ITviec crawler (https://itviec.com/it-jobs) — fully automated.

Listing pages are JS-rendered (Playwright). Each detail page carries a
schema.org JobPosting JSON-LD with the full description. The crawler fetches
both listing and detail in one pass, resuming from the output file.
"""

import argparse
import json
import time
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from crawlers.base import read_jsonl, write_jsonl
from crawlers.browser_polite import browser_polite
from crawlers.polite import CAPTCHA_MARKERS

BASE = "https://itviec.com"
LIST_URL = "https://itviec.com/it-jobs"


def is_blocked(soup: BeautifulSoup) -> bool:
    title = (soup.title.get_text(" ", strip=True) if soup.title else "").lower()
    if any(t in title for t in ("just a moment", "cloudflare", "attention")):
        return True
    text = soup.get_text(" ", strip=True)[:2000].lower()
    return any(m in text for m in CAPTCHA_MARKERS)


def parse_card(card: BeautifulSoup) -> dict | None:
    title_a = card.select_one("h3 a")
    if not title_a:
        return None
    job_url = urljoin(BASE, title_a.get("href", "").split("?")[0])
    title = title_a.get_text(strip=True)

    company = None
    company_a = card.select_one("span.ims-2 a.text-rich-grey")
    if company_a:
        company = company_a.get_text(strip=True)

    salary = None
    salary_a = card.select_one("div.salary a")
    if salary_a:
        salary = salary_a.get_text(strip=True)

    location = None
    loc_div = card.select_one("div.text-rich-grey.text-truncate.text-nowrap")
    if loc_div:
        location = loc_div.get("title")

    work_model = None
    wm_div = card.select_one("div.text-rich-grey.flex-shrink-0")
    if wm_div:
        work_model = wm_div.get_text(strip=True)

    skills = [
        a.get_text(strip=True)
        for a in card.select("a[data-responsive-tag-list-target='tag']")
    ]

    return {
        "site": "itviec",
        "job_url": job_url,
        "title": title,
        "company": company,
        "location": location,
        "work_model": work_model,
        "salary": salary,
        "skills": skills,
    }


def extract_detail(soup: BeautifulSoup) -> dict:
    """Extract description from detail page JSON-LD or DOM."""
    for script in soup.select('script[type="application/ld+json"]'):
        try:
            data = json.loads(script.string or script.get_text() or "")
        except (json.JSONDecodeError, TypeError):
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if isinstance(item, dict) and item.get("@type") == "JobPosting":
                desc_html = item.get("description") or ""
                description = BeautifulSoup(desc_html, "lxml").get_text("\n", strip=True)
                exp = item.get("experienceRequirements") or {}
                return {
                    "description": description,
                    "date_posted": item.get("datePosted"),
                    "employment_type": item.get("employmentType"),
                    "experience_months": exp.get("monthsOfExperience")
                    if isinstance(exp, dict) else None,
                }
    return {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl ITviec jobs (automated)")
    parser.add_argument("--pages", type=int, default=40)
    parser.add_argument("--limit", type=int, default=0, help="max new jobs to fetch")
    parser.add_argument("--delay", type=float, default=4.0, help="seconds between requests")
    parser.add_argument("--skip-details", action="store_true", help="listing only, no descriptions")
    parser.add_argument("--headless", action="store_true", default=True)
    parser.add_argument("--no-headless", dest="headless", action="store_false")
    parser.add_argument("--out", type=str, default="data/raw/itviec.jsonl")
    args = parser.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    done = {r["job_url"] for r in read_jsonl(out) if r.get("description")}

    saved = 0
    with browser_polite(headless=args.headless) as ctx:
        page = ctx.new_page()

        for page_num in range(1, args.pages + 1):
            url = LIST_URL if page_num == 1 else f"{LIST_URL}?page={page_num}"
            page.goto(url, wait_until="domcontentloaded", timeout=60_000)
            try:
                page.wait_for_selector("div.job-card", timeout=15_000)
            except Exception:
                print(f"page {page_num}: no job cards found, stopping", flush=True)
                break

            soup = BeautifulSoup(page.content(), "lxml")
            if is_blocked(soup):
                print(f"STOP -- blocked on page {page_num}", flush=True)
                break

            cards = [row for c in soup.select("div.job-card") if (row := parse_card(c))]
            if not cards:
                break

            for card in cards:
                if card["job_url"] in done:
                    continue
                if args.limit and saved >= args.limit:
                    break

                if not args.skip_details:
                    time.sleep(args.delay)
                    page.goto(card["job_url"], wait_until="domcontentloaded", timeout=60_000)
                    page.wait_for_timeout(1500)
                    detail_soup = BeautifulSoup(page.content(), "lxml")
                    if is_blocked(detail_soup):
                        print(f"STOP -- blocked on detail page", flush=True)
                        break
                    detail = extract_detail(detail_soup)
                    card.update(detail)

                write_jsonl(out, [card])
                done.add(card["job_url"])
                saved += 1

            print(f"page {page_num}: {saved} new jobs so far", flush=True)
            if args.limit and saved >= args.limit:
                break
            time.sleep(args.delay)

    print(f"saved {saved} new jobs, {len(done)} total in {out}")


if __name__ == "__main__":
    main()
