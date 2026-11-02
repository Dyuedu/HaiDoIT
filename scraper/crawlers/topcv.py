"""TopCV crawler (https://www.topcv.vn/tim-viec-lam-cong-nghe-thong-tin-cr257)."""

import argparse
from pathlib import Path

from bs4 import BeautifulSoup

from crawlers.base import interactive_scrape
from crawlers.browser import browser

LIST_URL = "https://www.topcv.vn/tim-viec-lam-cong-nghe-thong-tin-cr257"


def parse_cards(soup: BeautifulSoup) -> list[dict]:
    rows = []
    seen = set()
    for card in soup.select("div.job-item-search-result"):
        title_a = card.select_one("h3.title a") or card.select_one(
            "a[href*='/viec-lam/']"
        )
        if not title_a:
            continue
        url = title_a["href"]
        if not url.startswith("http"):
            url = "https://www.topcv.vn" + url
        url = url.split("?")[0]
        if url in seen:
            continue
        seen.add(url)

        company = card.select_one("a.company")
        salary = card.select_one("label.salary")
        location = card.select_one("a.address") or card.select_one("span.city-text")
        exp = card.select_one("label.exp")
        posted = card.select_one("label.label-update")

        rows.append(
            {
                "site": "topcv",
                "job_url": url,
                "title": title_a.get_text(strip=True),
                "company": company.get_text(strip=True) if company else None,
                "location": location.get_text(strip=True) if location else None,
                "salary": salary.get_text(strip=True) if salary else None,
                "experience_level": exp.get_text(strip=True) if exp else None,
                "posted_at": posted.get_text(strip=True) if posted else None,
            }
        )
    return rows


def fetch_page(page, page_num: int) -> list[dict]:
    url = LIST_URL if page_num == 1 else f"{LIST_URL}?page={page_num}"
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(3000)
    soup = BeautifulSoup(page.content(), "lxml")
    return parse_cards(soup)


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl TopCV IT job listings")
    parser.add_argument("--pages", type=int, default=200)
    parser.add_argument("--start-page", type=int, default=1)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--out", type=str, default="data/raw/topcv.jsonl")
    args = parser.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    start_url = (
        LIST_URL if args.start_page <= 1 else f"{LIST_URL}?page={args.start_page}"
    )
    with browser(headless=args.headless) as b:
        page = b.new_page()
        page.goto(start_url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)
        print(
            "Navigate through pages (click next / load more). Scraping continuously — Ctrl+C to finish.",
            flush=True,
        )
        interactive_scrape(page, parse_cards, out, label="topcv")

    print(f"done -> {out}")


if __name__ == "__main__":
    main()
