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

from crawlers.base import read_jsonl, write_jsonl, write_seen
from crawlers.browser_polite import MAX_CONSECUTIVE_FAILURES, PAGE_RECYCLE_EVERY, browser_polite, fresh_page
from crawlers.polite import CAPTCHA_MARKERS, BlockedError

BASE = "https://itviec.com"
LIST_URL = "https://itviec.com/it-jobs"
EMPTY_PAGE_TRIES = 3


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


def fetch_detail(page, url: str, delay: float, settle_ms: int) -> dict | None:
    """One detail page. None means it failed to load: keep the job for the next run."""
    time.sleep(delay)
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=60_000)
        page.wait_for_timeout(settle_ms)
    except Exception as exc:  # noqa: BLE001 - playwright raises its own error types
        print(f"detail {url}: {str(exc)[:120]}", flush=True)
        return None
    soup = BeautifulSoup(page.content(), "lxml")
    if is_blocked(soup):
        raise BlockedError(f"blocked on {url}")
    return extract_detail(soup)


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl ITviec jobs (automated)")
    parser.add_argument("--pages", type=int, default=40)
    parser.add_argument("--limit", type=int, default=0, help="max new job details per run, 0 = all")
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
    cards: dict[str, dict] = {}
    complete, error = False, None
    try:
        with browser_polite(headless=args.headless) as ctx:
            page = ctx.new_page()
            try:
                for page_num in range(1, args.pages + 1):
                    url = LIST_URL if page_num == 1 else f"{LIST_URL}?page={page_num}"
                    if page_num % PAGE_RECYCLE_EVERY == 0:
                        page = fresh_page(ctx, page)
                    new = []
                    for _ in range(EMPTY_PAGE_TRIES):  # a slow page must not look like the end
                        page.goto(url, wait_until="domcontentloaded", timeout=60_000)
                        try:
                            page.wait_for_selector("div.job-card", timeout=15_000)
                        except Exception:  # noqa: BLE001 - no cards: the end, a block, or a slow page
                            pass

                        soup = BeautifulSoup(page.content(), "lxml")
                        if is_blocked(soup):
                            raise BlockedError(f"blocked on page {page_num}")

                        found = [row for c in soup.select("div.job-card") if (row := parse_card(c))]
                        new = [c for c in found if c["job_url"] not in cards]
                        if new:
                            break
                        time.sleep(args.delay)
                    if not new:  # past the end, or the site repeating its last page
                        if page_num == 1:
                            raise BlockedError("no job cards on page 1")
                        complete = True
                        break
                    cards.update((c["job_url"], c) for c in new)
                    print(f"page {page_num}: {len(cards)} listed", flush=True)
                    time.sleep(args.delay)
                else:
                    error = f"hit --pages {args.pages} before the listing ended"
            except Exception as exc:  # noqa: BLE001 - whatever stopped the walk, keep what it saw
                error = str(exc)[:300]
                print(f"listing incomplete: {error}", flush=True)

            # Written before the details: with no limit they can run for hours, and
            # a timeout or a block there must not lose today's observations.
            write_seen("itviec", list(cards), complete, error=error)

            if error and "blocked" in error:
                return
            todo = [c for u, c in cards.items() if u not in done]
            print(f"{len(todo)} details to fetch", flush=True)
            page = fresh_page(ctx, page)
            failures = 0
            for card in todo:
                if args.limit and saved >= args.limit:
                    break
                if not args.skip_details:
                    if saved and saved % PAGE_RECYCLE_EVERY == 0:
                        page = fresh_page(ctx, page)
                    detail = fetch_detail(page, card["job_url"], args.delay, 1500)
                    if detail is None:
                        failures += 1
                        if failures >= MAX_CONSECUTIVE_FAILURES:
                            print(f"STOP -- {failures} details failed in a row", flush=True)
                            break
                        page = fresh_page(ctx, page)
                        continue
                    failures = 0
                    card.update(detail)
                    if not card.get("description"):  # no empty rows: the next run retries it
                        continue
                write_jsonl(out, [card])
                done.add(card["job_url"])
                saved += 1
                if saved % 25 == 0:
                    print(f"{saved}/{len(todo)} details", flush=True)
    except Exception as exc:  # noqa: BLE001 - browser died or a detail was blocked; next run resumes
        print(f"STOP -- {str(exc)[:300]}", flush=True)

    print(f"saved {saved} new jobs, {len(done)} total in {out}")


if __name__ == "__main__":
    main()
