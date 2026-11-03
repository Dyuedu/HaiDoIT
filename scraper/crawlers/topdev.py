"""TopDev crawler (https://topdev.vn/jobs/search) — fully automated.

Listing pages are JS-rendered (Playwright). Detail pages carry schema.org
JobPosting JSON-LD with full descriptions. The crawler fetches both listing
and detail in one pass, resuming from the output file.
"""

import argparse
import json
import time
from pathlib import Path

from bs4 import BeautifulSoup

from crawlers.base import read_jsonl, write_jsonl
from crawlers.browser_polite import browser_polite
from crawlers.polite import CAPTCHA_MARKERS

LIST_URL = "https://topdev.vn/jobs/search"


def is_blocked(soup: BeautifulSoup) -> bool:
    title = (soup.title.get_text(" ", strip=True) if soup.title else "").lower()
    if any(t in title for t in ("just a moment", "cloudflare", "attention")):
        return True
    text = soup.get_text(" ", strip=True)[:2000].lower()
    return any(m in text for m in CAPTCHA_MARKERS)


def parse_cards(soup: BeautifulSoup) -> list[dict]:
    rows = []
    seen = set()
    for link in soup.select("a[href*='/detail-jobs/']"):
        href = link["href"].split("?")[0]
        url = "https://topdev.vn" + href if href.startswith("/") else href
        if url in seen:
            continue
        seen.add(url)

        title = link.get_text(strip=True)

        card = link
        for _ in range(7):
            card = card.parent
            if card and "rounded-[16px]" in " ".join(card.get("class", [])):
                break

        company = card.select_one("span.line-clamp-1") if card else None
        skills = [a.get_text(strip=True) for a in card.select("a.line-clamp-1.h-6")] if card else []
        posted_span = card.select_one("span.text-xs.text-text-500") if card else None

        grid = card.select_one("div.mt-2.grid") if card else None
        grid_spans = (
            [s.get_text(strip=True) for s in grid.select("span.line-clamp-1")]
            if grid else []
        )

        rows.append({
            "site": "topdev",
            "job_url": url,
            "title": title,
            "company": company.get_text(strip=True) if company else None,
            "location": grid_spans[0] if grid_spans else None,
            "experience_level": ", ".join(grid_spans[1:]) if len(grid_spans) > 1 else None,
            "posted_at": posted_span.get_text(strip=True) if posted_span else None,
            "skills": skills,
        })
    return rows


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
                parts = []
                for field in ("description", "jobBenefits"):
                    html = item.get(field) or ""
                    txt = BeautifulSoup(html, "lxml").get_text("\n", strip=True)
                    if txt:
                        parts.append(txt)
                return {
                    "description": "\n\n".join(parts),
                    "date_posted": item.get("datePosted"),
                    "employment_type": item.get("employmentType"),
                }

    markers = ("Your role", "Your skills", "responsibilities", "Benefits",
               "Mo ta", "Yeu cau", "Quyen loi")
    best = ""
    for el in soup.select("div.rounded-xl.border.p-4"):
        txt = el.get_text("\n", strip=True)
        if len(txt) < 400:
            continue
        if not any(m.lower() in txt.lower() for m in markers):
            continue
        if "More jobs for you" in txt or "Other jobs at this company" in txt:
            continue
        if len(txt) > len(best):
            best = txt
    if best:
        return {"description": best}
    return {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl TopDev jobs (automated)")
    parser.add_argument("--pages", type=int, default=200)
    parser.add_argument("--limit", type=int, default=0, help="max new jobs to fetch")
    parser.add_argument("--delay", type=float, default=4.0)
    parser.add_argument("--skip-details", action="store_true")
    parser.add_argument("--headless", action="store_true", default=True)
    parser.add_argument("--no-headless", dest="headless", action="store_false")
    parser.add_argument("--out", type=str, default="data/raw/topdev.jsonl")
    args = parser.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    done = {r["job_url"] for r in read_jsonl(out) if r.get("description")}
    done_listing = {r["job_url"] for r in read_jsonl(out)}

    saved = 0
    with browser_polite(headless=args.headless) as ctx:
        page = ctx.new_page()

        for page_num in range(1, args.pages + 1):
            url = LIST_URL if page_num == 1 else f"{LIST_URL}?page={page_num}"
            page.goto(url, wait_until="domcontentloaded", timeout=60_000)
            page.wait_for_timeout(3000)

            soup = BeautifulSoup(page.content(), "lxml")
            if is_blocked(soup):
                print(f"STOP -- blocked on page {page_num}", flush=True)
                break

            cards = parse_cards(soup)
            if not cards:
                print(f"page {page_num}: no cards, stopping", flush=True)
                break

            for card in cards:
                if card["job_url"] in done_listing:
                    continue
                if args.limit and saved >= args.limit:
                    break

                if not args.skip_details:
                    time.sleep(args.delay)
                    page.goto(card["job_url"], wait_until="domcontentloaded", timeout=60_000)
                    page.wait_for_timeout(2000)
                    detail_soup = BeautifulSoup(page.content(), "lxml")
                    if is_blocked(detail_soup):
                        print(f"STOP -- blocked on detail page", flush=True)
                        break
                    detail = extract_detail(detail_soup)
                    card.update(detail)

                write_jsonl(out, [card])
                done_listing.add(card["job_url"])
                if card.get("description"):
                    done.add(card["job_url"])
                saved += 1

            print(f"page {page_num}: {saved} new jobs so far", flush=True)
            if args.limit and saved >= args.limit:
                break
            time.sleep(args.delay)

    print(f"saved {saved} new jobs, {len(done_listing)} total in {out}")


if __name__ == "__main__":
    main()
