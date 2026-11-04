"""TopDev crawler (https://topdev.vn/jobs/search), plain HTTP, IT jobs only.

The board lists 4,000+ jobs and most are not IT (bank branches, garment factories).
A job is kept when TopDev files it under its IT category OR its title or skills
match IT_KEYWORDS. Measured on 315 classified jobs: the category alone caught 80%
of IT jobs and missed real ones ("Chuyen vien lap trinh Back-end (Java)"); together
they caught 97%. extract.py still labels what slips through.

So every run walks the IT category and the whole listing, and only kept jobs get
details and observations. The end of a listing is `last_page` from the page data,
never an empty page: past the end the site keeps returning jobs. A walk counts as
complete only if it also met nearly all of the `total` the site reports.
"""

import argparse
import json
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from crawlers.base import read_jsonl, write_jsonl, write_seen
from crawlers.polite import BlockedError, PoliteClient

LIST_URL = "https://topdev.vn/jobs/search"
IT_CATEGORY_URL = f"{LIST_URL}?job_categories_ids=1"
MIN_COVERAGE = 0.9
MAX_PAGES = 1000
MAX_CONSECUTIVE_FAILURES = 10
ZERO_RESULT_TRIES = 3
ZERO_RESULT_WAIT = 30
IT_KEYWORDS = re.compile(
    r"(?i)\b(developer|engineer|lập trình|phần mềm|software|backend|back-end|frontend|front-end"
    r"|fullstack|full-stack|devops|data|an ninh mạng|security|cntt|công nghệ thông tin|it|tester"
    r"|qa|qc|kỹ sư|business analyst|phân tích nghiệp vụ|ba|ai|machine learning|cloud|hệ thống"
    r"|mạng|erp|sap|game|ui/ux|mobile|android|ios)\b"
)


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
            if card.parent is None:
                break
            card = card.parent
            if "rounded-[16px]" in " ".join(card.get("class", [])):
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


def page_meta(html: str) -> tuple[int | None, int | None]:
    """(last_page, total) from the data embedded in the page."""
    text = html.replace('\\"', '"')
    last = re.search(r'"last_page":(\d+)', text)
    total = re.search(r'"total":(\d+)', text)
    return (int(last.group(1)) if last else None, int(total.group(1)) if total else None)


def fetch_results_page(client, url: str) -> tuple[str, int, int]:
    """A page that really has results. The site now and then answers "0 positions",
    last_page 0, with unrelated suggested jobs; that is a hiccup, not the end."""
    for attempt in range(ZERO_RESULT_TRIES):
        html = client.get(url).text
        last, total = page_meta(html)
        if last and total:
            return html, last, total
        if attempt + 1 < ZERO_RESULT_TRIES:
            print(f"{url}: reported no results, retrying", flush=True)
            time.sleep(ZERO_RESULT_WAIT)
    raise RuntimeError(f"{url}: reported no results {ZERO_RESULT_TRIES} times")


def walk_listing(client, base_url: str, cards: dict) -> int:
    """Fetch pages 1..last_page into `cards`, keeping what it met if it stops.

    Returns the largest total the site reported during the walk.
    """
    sep = "&" if "?" in base_url else "?"
    page, last, total = 1, 0, 0
    while page <= MAX_PAGES:
        html, page_last, page_total = fetch_results_page(client, f"{base_url}{sep}page={page}")
        last, total = max(last, page_last), max(total, page_total)
        for card in parse_cards(BeautifulSoup(html, "lxml")):
            cards.setdefault(card["job_url"], card)
        if page % 25 == 0 or page >= last:
            print(f"{base_url} page {page}/{last}: {len(cards)} listed", flush=True)
        if page >= last:
            return total
        page += 1
    raise RuntimeError(f"{base_url}: hit {MAX_PAGES} pages")


def is_kept(card: dict, it_urls) -> bool:
    if card["job_url"] in it_urls:
        return True
    return bool(IT_KEYWORDS.search(" ".join([card.get("title") or ""] + (card.get("skills") or []))))


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl TopDev IT jobs")
    parser.add_argument("--limit", type=int, default=0, help="max new job details per run, 0 = all")
    parser.add_argument("--delay", type=float, default=4.0)
    parser.add_argument("--skip-details", action="store_true")
    parser.add_argument("--out", type=str, default="data/raw/topdev.jsonl")
    args = parser.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    done = {r["job_url"] for r in read_jsonl(out) if r.get("description")}

    client = PoliteClient(delay=args.delay)
    it_cards, all_cards = {}, {}
    complete, error = False, None
    try:
        walk_listing(client, IT_CATEGORY_URL, it_cards)
        total = walk_listing(client, LIST_URL, all_cards)
        complete = len(all_cards) >= total * MIN_COVERAGE
        if not complete:
            error = f"met {len(all_cards)} of {total} listed jobs"
    except (BlockedError, RuntimeError, requests.RequestException) as exc:
        error = str(exc)[:300]
        print(f"listing incomplete: {error}", flush=True)

    kept = dict(it_cards)
    for url, card in all_cards.items():
        if url not in kept and is_kept(card, it_cards):
            kept[url] = card
    print(f"kept {len(kept)} of {len(all_cards)} listed ({len(it_cards)} in the IT category)", flush=True)
    # Written before the details: a timeout or a block there must not lose today's observations.
    write_seen("topdev", list(kept), complete, error=error)

    saved = failures = 0
    todo = [c for u, c in kept.items() if u not in done]
    print(f"{len(todo)} details to fetch", flush=True)
    try:
        for card in todo:
            if args.limit and saved >= args.limit:
                break
            if not args.skip_details:
                try:
                    card.update(extract_detail(BeautifulSoup(client.get(card["job_url"]).text, "lxml")))
                except requests.RequestException as exc:
                    print(f"detail {card['job_url']}: {str(exc)[:120]}", flush=True)
                    failures += 1
                    if failures >= MAX_CONSECUTIVE_FAILURES:
                        print(f"STOP -- {failures} details failed in a row", flush=True)
                        break
                    continue
                failures = 0
                if not card.get("description"):  # no empty rows: the next run retries it
                    continue
            write_jsonl(out, [card])
            saved += 1
            if saved % 25 == 0:
                print(f"{saved}/{len(todo)} details", flush=True)
    except BlockedError as exc:
        print(f"STOP -- {exc}", flush=True)

    print(f"saved {saved} new jobs to {out}")


if __name__ == "__main__":
    main()
