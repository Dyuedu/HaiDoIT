"""CareerLink crawler (https://www.careerlink.vn) — IT software + hardware/network.

Listing pages give job URLs; each detail page carries a schema.org JobPosting
(JSON-LD) with description, salary (VND), locations and dates.

CareerLink shows hCaptcha after ~100 requests/hour, so a run is capped at
--max-requests (default 40) and refuses to start within an hour of the
previous run. Each run walks the whole listing first, because that is what
proves a job is still open, then spends what is left of the budget on details
of jobs listed today. Skipped URLs live in data/state/careerlink.json.
"""

import argparse
import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from crawlers.base import read_jsonl, write_jsonl, write_seen
from crawlers.polite import BlockedError, BudgetExhausted, PoliteClient

BASE = "https://www.careerlink.vn"
CATEGORIES = ["/viec-lam/cntt-phan-mem/19", "/viec-lam/cntt-phan-cung-mang/130"]
JOB_LINK = re.compile(r"^/tim-viec-lam/[^/]+/\d+$")
MIN_GAP_SECONDS = 3600
MAX_LISTING_PAGES = 100


def load_state(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"skipped": [], "last_run": 0}


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")


def job_links(html: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    links = []
    for a in soup.select("a[href^='/tim-viec-lam/']"):
        href = a["href"].split("?")[0]
        if JOB_LINK.match(href):
            url = urljoin(BASE, href)
            if url not in links:
                links.append(url)
    return links


def job_posting(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    for script in soup.select('script[type="application/ld+json"]'):
        try:
            data = json.loads(script.string or script.get_text() or "")
        except (json.JSONDecodeError, TypeError):
            continue
        for item in data if isinstance(data, list) else [data]:
            if isinstance(item, dict) and item.get("@type") == "JobPosting":
                return item
    return {}


def format_salary(base_salary: dict) -> str | None:
    value = (base_salary or {}).get("value")
    if not isinstance(value, dict):
        return None
    currency = base_salary.get("currency") or ""
    lo, hi = value.get("minValue"), value.get("maxValue")
    if lo or hi:
        return f"{lo or ''}-{hi or ''} {currency}".strip()
    return value.get("value")


def parse_job(url: str, posting: dict) -> dict:
    desc_html = posting.get("description") or ""
    description = BeautifulSoup(desc_html, "lxml").get_text("\n", strip=True)
    places = posting.get("jobLocation") or []
    if isinstance(places, dict):
        places = [places]
    regions = []
    for place in places:
        region = ((place or {}).get("address") or {}).get("addressRegion")
        if region and region not in regions:
            regions.append(region)
    return {
        "site": "careerlink",
        "job_url": url,
        "title": posting.get("title"),
        "company": (posting.get("hiringOrganization") or {}).get("name"),
        "location": ", ".join(regions) or None,
        "salary": format_salary(posting.get("baseSalary")),
        "experience_level": posting.get("experienceRequirements"),
        "employment_type": posting.get("employmentType"),
        "industries": posting.get("industry"),
        "description": description,
        "date_posted": posting.get("datePosted"),
        "valid_through": posting.get("validThrough"),
    }


def crawl_listing(client: PoliteClient, seen: list) -> None:
    """Walk every page of every category, appending to `seen` as it goes.

    Stops a category on a page with no link this walk has not met yet; comparing
    against yesterday's queue instead would stop at page 1 once nothing is new.
    """
    for cat in CATEGORIES:
        met = set()
        for page in range(1, MAX_LISTING_PAGES + 1):
            url = f"{BASE}{cat}" + (f"?page={page}" if page > 1 else "")
            try:
                links = job_links(client.get(url).text)
            except requests.HTTPError as exc:
                if exc.response is not None and exc.response.status_code == 404:
                    break  # past the last page
                raise
            new = [u for u in links if u not in met]
            if not new:
                break
            met.update(new)
            seen.extend(u for u in new if u not in seen)
            print(f"{cat} page {page}: +{len(new)} (listed {len(seen)})", flush=True)
        else:
            raise RuntimeError(f"{cat}: hit {MAX_LISTING_PAGES} pages before the listing ended")


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl CareerLink IT jobs (resumable)")
    parser.add_argument("--max-requests", type=int, default=40)
    parser.add_argument("--delay", type=float, default=15.0)
    parser.add_argument("--out", type=str, default="data/raw/careerlink.jsonl")
    parser.add_argument("--state", type=str, default="data/state/careerlink.json")
    parser.add_argument("--force", action="store_true", help="ignore the 1-hour gap")
    args = parser.parse_args()

    out, state_path = Path(args.out), Path(args.state)
    state = load_state(state_path)
    since = time.time() - state["last_run"]
    if since < MIN_GAP_SECONDS and not args.force:
        print(f"last run {since / 60:.0f} min ago, wait {(MIN_GAP_SECONDS - since) / 60:.0f} min")
        return

    done = {r["job_url"] for r in read_jsonl(out)}
    client = PoliteClient(delay=args.delay, max_requests=args.max_requests)
    seen, saved = [], 0
    complete, error = False, None
    try:
        crawl_listing(client, seen)
        complete = True
    except (BudgetExhausted, BlockedError, RuntimeError, requests.RequestException) as exc:
        error = str(exc)
        print(f"listing incomplete: {exc}", flush=True)
    # Written before the details, so a block during details cannot lose the observation.
    write_seen("careerlink", seen, complete, error=error)

    try:
        for url in seen:  # only jobs listed today: an old queue entry may be long gone
            if url in done or url in state["skipped"]:
                continue
            try:
                posting = job_posting(client.get(url).text)
            except requests.HTTPError as exc:
                print(f"skip {url}: {exc}", flush=True)
                state["skipped"].append(url)
                continue
            if not posting.get("description"):
                state["skipped"].append(url)
                continue
            write_jsonl(out, [parse_job(url, posting)])
            done.add(url)
            saved += 1
    except BudgetExhausted:
        print(f"request budget used ({client.count})", flush=True)
    except (BlockedError, requests.RequestException) as exc:
        print(f"STOP -- {exc}", flush=True)
    finally:
        state["last_run"] = time.time()
        save_state(state_path, state)

    left = len([u for u in seen if u not in done and u not in state["skipped"]])
    print(f"saved {saved} jobs this run, {len(done)} total in {out}, {left} listed without detail")


if __name__ == "__main__":
    main()
