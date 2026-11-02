"""Phase 2: fetch the full job description for each URL.

Public boards are fetched by scraping the job detail page; LinkedIn is fetched
via its Voyager JSON API (the HTML detail page redirects to a company page).

Resumable: data/full.jsonl is rewritten in batches and doubles as a checkpoint.
"""

import argparse
import json
import time
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from tqdm import tqdm

from crawlers.base import read_jsonl
from crawlers.browser import USER_AGENT, webkit_context

RETRIES = 5
RETRY_DELAY = 2.0
BATCH_SIZE = 200
LINKEDIN_DELAY = 0.3


def site_of(url: str) -> str:
    host = urlparse(url).netloc
    for s in ("itviec", "topdev", "vietnamworks", "topcv", "linkedin"):
        if s in host:
            return s
    return host


# --- public-board extractors -------------------------------------------------


def job_posting_ldjson(soup: BeautifulSoup) -> dict:
    """Parse schema.org JobPosting from application/ld+json (ITviec, VietnamWorks)."""
    for script in soup.select('script[type="application/ld+json"]'):
        raw = script.string or script.get_text() or ""
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if isinstance(item, dict) and item.get("@type") == "JobPosting":
                return item
    return {}


def extract_job_posting(soup: BeautifulSoup) -> dict:
    posting = job_posting_ldjson(soup)
    desc_html = posting.get("description", "")
    description = (
        BeautifulSoup(desc_html, "lxml").get_text("\n", strip=True) if desc_html else ""
    )
    exp = posting.get("experienceRequirements") or {}
    return {
        "description": description,
        "date_posted": posting.get("datePosted"),
        "employment_type": posting.get("employmentType"),
        "experience_months": exp.get("monthsOfExperience")
        if isinstance(exp, dict)
        else None,
    }


def extract_vietnamworks(soup: BeautifulSoup) -> dict:
    """Scrape Mô tả + Yêu cầu (+ phúc lợi). JSON-LD alone omits requirements."""
    parts = []
    for h2 in soup.find_all("h2"):
        label = h2.get_text(" ", strip=True)
        if label not in ("Mô tả công việc", "Yêu cầu công việc"):
            continue
        body_bits = []
        for sib in h2.parent.find_all(recursive=False) if h2.parent else []:
            if sib == h2:
                continue
            t = sib.get_text("\n", strip=True)
            # Match-score teaser above the JD — skip it.
            if "Mức độ phù hợp" in t and len(t) < 160:
                continue
            if t:
                body_bits.append(t)
        if body_bits:
            parts.append(f"{label}\n" + "\n".join(body_bits))

    for node in soup.find_all(
        string=lambda t: t and t.strip() == "Các phúc lợi dành cho bạn"
    ):
        block = node.parent.parent if node.parent else None
        if block:
            t = block.get_text("\n", strip=True)
            if t:
                parts.append(t)
        break

    description = "\n\n".join(parts).strip()
    if not description:
        # Fallback: JSON-LD mô tả only (better than empty).
        return extract_job_posting(soup)

    posting = job_posting_ldjson(soup)
    return {
        "description": description,
        "date_posted": posting.get("datePosted"),
        "employment_type": posting.get("employmentType"),
    }


def extract_generic(soup: BeautifulSoup) -> str:
    for sel in (
        "[class*='job-description']",
        "[class*='job_description']",
        "[class*='jd-description']",
        "article",
        "main",
    ):
        el = soup.select_one(sel)
        if el:
            txt = el.get_text("\n", strip=True)
            if len(txt) > 200:
                return txt
    body = soup.body
    return body.get_text("\n", strip=True) if body else ""


def extract_topdev(soup: BeautifulSoup) -> dict:
    """TopDev/Saramin JD card — avoid whole-page scrape + old 6000-char hard cap."""
    markers = (
        "Your role",
        "Your skills",
        "responsibilities",
        "Benefits",
        "Mô tả",
        "Yêu cầu",
        "Quyền lợi",
    )
    best = ""
    for el in soup.select("div.rounded-xl.border.p-4"):
        txt = el.get_text("\n", strip=True)
        if len(txt) < 400:
            continue
        if not any(m in txt for m in markers):
            continue
        # Prefer the dedicated JD card over "More jobs" side panels.
        if "More jobs for you" in txt or "Other jobs at this company" in txt:
            continue
        if len(txt) > len(best):
            best = txt

    posting = job_posting_ldjson(soup)
    if not best:
        # Fallback: JSON-LD description + benefits (often shorter than the card).
        desc_html = posting.get("description") or ""
        ben_html = posting.get("jobBenefits") or ""
        parts = []
        if desc_html:
            parts.append(BeautifulSoup(desc_html, "lxml").get_text("\n", strip=True))
        if ben_html:
            parts.append(BeautifulSoup(ben_html, "lxml").get_text("\n", strip=True))
        best = "\n\n".join(p for p in parts if p).strip()
    if not best:
        best = extract_generic(soup)
    if not best:
        raise RuntimeError("no description found")

    return {
        "description": best,
        "date_posted": posting.get("datePosted"),
        "employment_type": posting.get("employmentType"),
    }


def is_cloudflare(soup: BeautifulSoup) -> bool:
    """Detect Cloudflare interstitial pages — avoid loose words like 'challenge'
    that appear in normal job descriptions and cause false positives."""
    title = (soup.title.get_text(" ", strip=True) if soup.title else "").lower()
    if any(t in title for t in ("just a moment", "attention required", "cloudflare")):
        return True

    # Cloudflare-specific DOM hooks (not present on real job pages).
    if soup.select_one(
        "#challenge-form, #cf-challenge-running, .cf-browser-verification, "
        "#challenge-body-text, div.cf-wrapper, script[src*='challenges.cloudflare.com']"
    ):
        return True

    # Narrow text markers on the first chunk of body text only.
    text = soup.get_text(" ", strip=True)[:1500].lower()
    markers = (
        "checking your browser before accessing",
        "cf-browser-verification",
        "enable javascript and cookies to continue",
        "verify you are human",
        "performance & security by cloudflare",
        "needs to review the security of your connection",
    )
    return any(m in text for m in markers)


def extract_topcv(soup: BeautifulSoup) -> dict:
    boilerplate = (
        "Tiếp lợi thế",
        "Hệ sinh thái HR Tech",
        "TopCV hiểu rõ",
        "Định vị bản thân",
    )
    best = ""
    for el in soup.select("div, section"):
        txt = el.get_text("\n", strip=True)
        if len(txt) > 400 and not any(b in txt for b in boilerplate):
            if len(txt) > len(best):
                best = txt
    if not best:
        raise RuntimeError("no description found")
    return {"description": best}


EXTRACTORS = {
    "itviec": extract_job_posting,
    "vietnamworks": extract_vietnamworks,
    "topdev": extract_topdev,
    "topcv": extract_topcv,
}


def description_complete(row: dict) -> bool:
    """True if we already have a usable full description.

    VietnamWorks search API truncates with '...', and JSON-LD-only extracts
    miss the Yêu cầu section — both still need a page scrape.
    TopDev previously hard-capped body text at exactly 6000 chars.
    """
    desc = (row.get("description") or "").strip()
    if not desc:
        return False
    site = site_of(row.get("job_url", ""))
    if site == "vietnamworks":
        if desc.endswith("..."):
            return False
        # Page scrape labels sections; API/JSON-LD dumps do not.
        return "Mô tả công việc" in desc or "Yêu cầu công việc" in desc
    if site == "topdev" and len(desc) == 6000:
        return False
    return True


class CloudflareDetected(Exception):
    pass


def fetch_public(page, row: dict) -> dict:
    site = site_of(row["job_url"])
    page.goto(row["job_url"], wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(1500)
    if site == "vietnamworks":
        btn = page.locator("button:has-text('Xem đầy đủ')")
        if btn.count():
            try:
                btn.first.click(timeout=2000)
                page.wait_for_timeout(800)
            except Exception:
                pass
    soup = BeautifulSoup(page.content(), "lxml")
    if is_cloudflare(soup):
        raise CloudflareDetected()
    detail = EXTRACTORS[site](soup)
    if not (detail.get("description") or "").strip():
        raise RuntimeError("empty description")
    return {**row, **detail}


# --- LinkedIn via Voyager API -------------------------------------------------


def linkedin_job_id(url: str) -> str:
    return url.rstrip("/").split("/")[-1]


def linkedin_csrf(ctx) -> str:
    for c in ctx.cookies():
        if c["name"] == "JSESSIONID":
            return c["value"].replace('"', "")
    return ""


def fetch_linkedin(ctx, row: dict) -> dict:
    job_id = linkedin_job_id(row["job_url"])
    resp = ctx.request.get(
        f"https://www.linkedin.com/voyager/api/jobs/jobPostings/{job_id}",
        headers={
            "x-restli-protocol-version": "2.0.0",
            "csrf-token": linkedin_csrf(ctx),
        },
        timeout=30000,
    )
    if resp.status != 200:
        raise RuntimeError(f"voyager HTTP {resp.status}")

    d = resp.json()
    desc = (d.get("description") or {}).get("text", "")
    if not desc:
        raise RuntimeError("empty description")

    company = None
    cd = d.get("companyDetails") or {}
    if isinstance(cd, dict):
        for v in cd.values():
            if isinstance(v, dict) and v.get("name"):
                company = v["name"]
                break

    return {
        **row,
        "description": desc,
        "title": d.get("title") or row.get("title"),
        "company": company or row.get("company"),
        "location": d.get("formattedLocation") or row.get("location"),
        "date_posted": d.get("createdAt"),
    }


def with_retry(fn, *args, delay=LINKEDIN_DELAY):
    last_err = None
    for attempt in range(1, RETRIES + 1):
        try:
            return fn(*args), None
        except Exception as exc:  # noqa: BLE001 - retry transient failures
            last_err = f"{type(exc).__name__}: {str(exc)[:200]}"
            time.sleep(RETRY_DELAY * attempt)
    return args[-1], last_err


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch full job bodies (Phase 2, resumable)"
    )
    parser.add_argument("--in", dest="src", type=str, default="data/dedup.jsonl")
    parser.add_argument("--out", type=str, default="data/full.jsonl")
    parser.add_argument("--errors", type=str, default="data/details-errors.jsonl")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument(
        "--site",
        type=str,
        default="",
        help="only fetch this site (linkedin/itviec/topdev/topcv/vietnamworks)",
    )
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args()

    rows = read_jsonl(args.src)
    out = Path(args.out)
    err_path = Path(args.errors)
    out.parent.mkdir(parents=True, exist_ok=True)
    err_path.parent.mkdir(parents=True, exist_ok=True)

    # Keep any existing description in the checkpoint — including incomplete
    # ones (TopDev 6000-cap, VW truncated) — so a partial run cannot wipe them.
    results = {}
    if out.exists():
        for r in read_jsonl(out):
            if r.get("job_url") and (r.get("description") or "").strip():
                results[r["job_url"]] = r

    todo = [
        r
        for r in rows
        if r.get("job_url") and not description_complete(results.get(r["job_url"], r))
    ]
    if args.site:
        todo = [r for r in todo if site_of(r["job_url"]) == args.site]
    if args.limit:
        todo = todo[: args.limit]
    print(
        f"{len(rows)} total, {len(results)} already fetched, {len(todo)} to fetch",
        flush=True,
    )

    by_site = {}
    for r in todo:
        by_site.setdefault(site_of(r["job_url"]), []).append(r)

    errors = []

    def flush():
        with out.open("w", encoding="utf-8") as fh:
            for row in rows:
                merged = results.get(row["job_url"], row)
                fh.write(json.dumps(merged, ensure_ascii=False) + "\n")

    def run_linkedin(ctx, subset):
        with tqdm(total=len(subset), desc="linkedin", unit="job") as pbar:
            for i, row in enumerate(subset, 1):
                merged, err = with_retry(fetch_linkedin, ctx, row, delay=LINKEDIN_DELAY)
                if err:
                    errors.append(
                        {
                            "job_url": row["job_url"],
                            "site": row.get("site"),
                            "error": err,
                        }
                    )
                else:
                    results[row["job_url"]] = merged
                if i % BATCH_SIZE == 0:
                    flush()
                pbar.update(1)
                time.sleep(LINKEDIN_DELAY)
        flush()

    def run_public(subset, desc, headless):
        from playwright.sync_api import sync_playwright

        pw = sync_playwright().start()
        browser_obj = ctx = page = None

        def open_browser():
            nonlocal browser_obj, ctx, page
            browser_obj = pw.chromium.launch(
                channel="chrome",
                headless=headless,
                args=["--disable-blink-features=AutomationControlled"],
            )
            ctx = browser_obj.new_context(user_agent=USER_AGENT)
            ctx.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            page = ctx.new_page()

        def close_browser():
            nonlocal browser_obj, ctx, page
            for obj in (ctx, browser_obj):
                if obj:
                    try:
                        obj.close()
                    except Exception:
                        pass
            browser_obj = ctx = page = None

        open_browser()
        try:
            with tqdm(total=len(subset), desc=desc, unit="job") as pbar:
                for i, row in enumerate(subset, 1):
                    merged = None
                    err = None
                    for attempt in range(RETRIES):
                        try:
                            merged = fetch_public(page, row)
                            break
                        except CloudflareDetected:
                            print(
                                f"[cloudflare] reopening browser for {row['job_url']}",
                                flush=True,
                            )
                            close_browser()
                            time.sleep(2)
                            open_browser()
                            err = f"cloudflare (attempt {attempt + 1})"
                        except Exception as exc:
                            err = f"{type(exc).__name__}: {str(exc)[:200]}"
                            time.sleep(RETRY_DELAY * (attempt + 1))
                    if merged is not None:
                        results[row["job_url"]] = merged
                    else:
                        errors.append(
                            {
                                "job_url": row["job_url"],
                                "site": row.get("site"),
                                "error": err,
                            }
                        )
                    if i % BATCH_SIZE == 0:
                        flush()
                    pbar.update(1)
            flush()
        finally:
            close_browser()
            pw.stop()

    # Site-by-site: LinkedIn first, then public boards.
    if by_site.get("linkedin"):
        with webkit_context(
            "data/linkedin-profile-webkit", headless=args.headless
        ) as ctx:
            run_linkedin(ctx, by_site["linkedin"])

    for site in ("itviec", "topdev", "topcv", "vietnamworks"):
        if by_site.get(site):
            run_public(by_site[site], site, args.headless)

    if err_path.exists():
        err_path.unlink()
    if errors:
        with err_path.open("w", encoding="utf-8") as fh:
            for e in errors:
                fh.write(json.dumps(e, ensure_ascii=False) + "\n")

    print(
        f"fetched {len(results)} descriptions total, {len(errors)} errors", flush=True
    )
    print(f"full -> {out}, errors -> {err_path}")


if __name__ == "__main__":
    main()
