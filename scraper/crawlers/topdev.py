"""TopDev crawler (https://topdev.vn/jobs/search)."""

import argparse
from pathlib import Path

from bs4 import BeautifulSoup

from crawlers.base import write_jsonl
from crawlers.browser import browser

LIST_URL = "https://topdev.vn/jobs/search"


def parse_cards(soup: BeautifulSoup) -> list[dict]:
    """Parse all job cards from a rendered TopDev search page."""
    rows = []
    seen = set()
    for link in soup.select("a[href*='/detail-jobs/']"):
        url = "https://topdev.vn" + link["href"].split("?")[0]
        if url in seen:
            continue
        seen.add(url)

        title = link.get_text(strip=True)

        card = link
        for _ in range(7):
            card = card.parent
            if "rounded-[16px]" in " ".join(card.get("class", [])):
                break

        company = card.select_one("span.line-clamp-1")
        salary_span = card.find("span", string=lambda t: t and "salary" in t.lower())
        grid = card.select_one("div.mt-2.grid")
        grid_spans = (
            [s.get_text(strip=True) for s in grid.select("span.line-clamp-1")]
            if grid
            else []
        )
        skills = [a.get_text(strip=True) for a in card.select("a.line-clamp-1.h-6")]
        posted_span = card.select_one("span.text-xs.text-text-500")

        rows.append(
            {
                "site": "topdev",
                "job_url": url,
                "title": title,
                "company": company.get_text(strip=True) if company else None,
                "location": grid_spans[0] if grid_spans else None,
                "experience_level": ", ".join(grid_spans[1:])
                if len(grid_spans) > 1
                else None,
                "salary": salary_span.get_text(strip=True) if salary_span else None,
                "posted_at": posted_span.get_text(strip=True) if posted_span else None,
                "skills": skills,
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
    parser = argparse.ArgumentParser(description="Crawl TopDev job listings")
    parser.add_argument("--pages", type=int, default=194)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--out", type=str, default="data/raw/topdev.jsonl")
    args = parser.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()

    total = 0
    with browser(headless=args.headless) as b:
        page = b.new_page()
        for page_num in range(1, args.pages + 1):
            rows = fetch_page(page, page_num)
            if not rows:
                break
            if args.limit and total + len(rows) > args.limit:
                rows = rows[: args.limit - total]
            write_jsonl(out, rows)
            total += len(rows)
            print(f"page {page_num}: {len(rows)} jobs (total {total})", flush=True)
            if args.limit and total >= args.limit:
                break

    print(f"saved {total} jobs to {out}")


if __name__ == "__main__":
    main()
