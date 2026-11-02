"""MoMo Careers crawler (https://momo.careers/jobs-opening).

The listing is server-rendered 12 at a time; the rest load when the visitor
clicks "Xem thêm", through an API that needs a token the page's own JS signs.
So the listing is read from the DOM of a headless browser (honest UA, no
anti-detection patches) that clicks "Xem thêm" like a visitor would. Each job
page is server-rendered: its __NEXT_DATA__ holds the full job, fetched with a
plain HTTP request. No JSON-LD on this site.
"""

import argparse
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from crawlers.base import write_jsonl
from crawlers.polite import USER_AGENT, BlockedError, PoliteClient

BASE = "https://momo.careers"
LIST_URL = f"{BASE}/jobs-opening"
# DGM.0001 = Trung tâm Công nghệ Thông tin, DGM.0002 = Khối Phát triển Sản phẩm,
# DGM.0003 = Khối Kinh Doanh, DGM.0004 = Khối Vận Hành
DEFAULT_GROUPS = "DGM.0001,DGM.0002"
NEXT_DATA = re.compile(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S)


def list_job_paths(group: str, headless: bool = True) -> list[str]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page(user_agent=USER_AGENT)
        page.goto(f"{LIST_URL}?groups={group}", wait_until="networkidle", timeout=60000)
        more = page.locator("div.mt-6.flex.justify-center button")
        for _ in range(30):
            if not more.count():
                break
            more.first.click()
            page.wait_for_timeout(3000)
        paths = page.eval_on_selector_all(
            "a[href^='/jobs/']", "els => els.map(e => e.getAttribute('href'))"
        )
        browser.close()
    return list(dict.fromkeys(paths))


def text_of(html: str | None) -> str:
    return BeautifulSoup(html or "", "lxml").get_text("\n", strip=True)


def parse_job(url: str, d: dict) -> dict:
    description = "\n".join(
        part
        for part in (text_of(d.get(k)) for k in ("jobDesc", "jobResp", "jobRequire"))
        if part
    )
    return {
        "site": "momo",
        "job_url": url,
        "title": d.get("jobTitle"),
        "company": "MoMo",
        "division": d.get("divisionGroup"),
        "location": d.get("locationPostJob"),
        "employment_type": d.get("jobType"),
        "job_code": d.get("jobCode"),
        "description": description,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl MoMo Careers jobs")
    parser.add_argument("--groups", type=str, default=DEFAULT_GROUPS)
    parser.add_argument("--delay", type=float, default=3.0)
    parser.add_argument("--headless", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--out", type=str, default="data/raw/momo.jsonl")
    args = parser.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()

    client = PoliteClient(delay=args.delay)
    total = 0
    try:
        for group in args.groups.split(","):
            paths = list_job_paths(group, headless=args.headless)
            print(f"{group}: {len(paths)} jobs listed", flush=True)
            for path in paths:
                url = BASE + path
                m = NEXT_DATA.search(client.get(url).text)
                detail = json.loads(m.group(1))["props"]["pageProps"].get("dataJobDetail") if m else None
                if not detail:
                    print(f"  no job data: {url}", flush=True)
                    continue
                write_jsonl(out, [parse_job(url, detail)])
                total += 1
    except BlockedError as exc:
        print(f"STOP — blocked: {exc}", flush=True)

    print(f"saved {total} jobs to {out}")


if __name__ == "__main__":
    main()
