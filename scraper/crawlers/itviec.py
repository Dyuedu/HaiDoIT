"""ITviec crawler (https://itviec.com/it-jobs).

Supports two execution paths:
1. nodriver (undetected Chrome with SQLite queue, anti-bot Cloudflare handling):
   The default mode when invoked as a script or via pipeline.py with --nodriver.
2. Playwright / browser_polite:
   Synchronous main() preserved for observation test suite compatibility.

Listing pages are JS-rendered. Each detail page carries a schema.org JobPosting
JSON-LD with the full description. The crawler fetches both listing and detail
in one pass, resuming from existing descriptions in data/raw/itviec.jsonl and the
SQLite queue.
"""

import argparse
import json
import os
import sqlite3
import time
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from crawlers.base import read_jsonl, write_jsonl, write_seen
from crawlers.browser_polite import (
    MAX_CONSECUTIVE_FAILURES,
    PAGE_RECYCLE_EVERY,
    browser_polite,
    fresh_page,
)
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


# ---------------------------------------------------------------------------
# Sync main — Playwright-based, keeps the API tests expect
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl ITviec jobs (automated)")
    parser.add_argument("--pages", type=int, default=40)
    parser.add_argument("--limit", type=int, default=0, help="max new job details per run, 0 = all")
    parser.add_argument("--delay", type=float, default=4.0, help="seconds between requests")
    parser.add_argument("--skip-details", action="store_true", help="listing only, no descriptions")
    parser.add_argument("--headless", action="store_true", default=True)
    parser.add_argument("--no-headless", dest="headless", action="store_false")
    parser.add_argument("--out", type=str, default="data/raw/itviec.jsonl")
    parser.add_argument("--playwright", action="store_true", help="the switch __main__ reads to pick this path")
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
                        except Exception:  # noqa: BLE001, S110 - no cards: the end, a block, or a slow page
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


# ---------------------------------------------------------------------------
# SQLite queue and JSONL export of the nodriver path. Module level, so tests
# reach them without nodriver installed.
# ---------------------------------------------------------------------------

MAX_RETRIES = 3
# A job that failed MAX_RETRIES times gets a fresh try once this long has passed
# since its last attempt: the page may have been fixed or the job reposted.
RETRY_AFTER_DAYS = 7


def queue_batch(conn: sqlite3.Connection, batch_size: int, now: datetime) -> list[tuple]:
    """Jobs to fetch details for: PENDING first, then FAILED ones still worth a try.

    batch_size <= 0 means no limit. updated_at is stored as datetime.isoformat(),
    so comparing against an isoformat cutoff is a plain string compare.
    """
    cutoff = (now - timedelta(days=RETRY_AFTER_DAYS)).isoformat()
    sql = (
        "SELECT job_url, title, company_name, salary_preview, location, work_model, skills_json "
        "FROM job_queue "
        "WHERE status = 'PENDING' "
        "   OR (status = 'FAILED' AND (retry_count < ? OR updated_at < ?)) "
        "ORDER BY CASE WHEN status = 'PENDING' THEN 0 ELSE 1 END, discovered_at ASC"
    )
    params: list = [MAX_RETRIES, cutoff]
    if batch_size > 0:
        sql += " LIMIT ?"
        params.append(batch_size)
    return conn.execute(sql, params).fetchall()


def _record(row: sqlite3.Row, desc: str) -> dict:
    skills = []
    if row["skills_json"]:
        try:
            skills = json.loads(row["skills_json"])
        except (json.JSONDecodeError, TypeError):
            skills = []
    return {
        "site": "itviec",
        "job_url": row["job_url"],
        "title": row["title"],
        "company": row["company_name"],
        "location": row["location"],
        "work_model": row["work_model"],
        "salary": row["salary"],
        "skills": skills,
        "description": desc,
        "date_posted": row["date_posted"],
        "employment_type": row["employment_type"],
        "experience_months": row["experience_months"],
    }


def export_jsonl(db_path, out_path) -> int:
    """Write completed jobs with a description from SQLite into the JSONL file.

    Rows that already have a description stay untouched. A row for the same URL
    without a description (e.g. from a --skip-details run) is replaced in place
    rather than duplicated; that case rewrites the file through a temp file and
    os.replace, so a crash never leaves it half written. Otherwise it appends.
    """
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    existing = read_jsonl(out)
    described = {r.get("job_url") for r in existing if r.get("description")}

    db_conn = sqlite3.connect(db_path)
    db_conn.row_factory = sqlite3.Row
    try:
        rows = db_conn.execute("""
            SELECT d.job_url, d.title, d.company_name, d.salary, d.location,
                   d.work_model, d.skills_json, d.description_text,
                   d.date_posted, d.employment_type, d.experience_months
            FROM job_details d
            JOIN job_queue q ON d.job_url = q.job_url
            WHERE q.status = 'COMPLETED'
        """).fetchall()
    finally:
        db_conn.close()

    fresh: dict[str, dict] = {}
    for row in rows:
        desc = (row["description_text"] or "").strip()
        if desc and row["job_url"] not in described:
            fresh[row["job_url"]] = _record(row, desc)

    bare = {r.get("job_url") for r in existing if not r.get("description")}
    if fresh.keys() & bare:
        kept, placed = [], set()
        for r in existing:
            url = r.get("job_url")
            if url in fresh and not r.get("description"):
                if url not in placed:
                    kept.append(fresh[url])
                    placed.add(url)
                continue
            kept.append(r)
        kept.extend(rec for url, rec in fresh.items() if url not in placed)
        tmp = out.with_suffix(out.suffix + ".tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            for r in kept:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        os.replace(tmp, out)
    elif fresh:
        with out.open("a", encoding="utf-8") as fh:
            for rec in fresh.values():
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"[+] Wrote {len(fresh)} jobs to {out} ({len(described) + len(fresh)} with description)")
    return len(fresh)


# ---------------------------------------------------------------------------
# Nodriver-based async main — used on the real VPS where Cloudflare blocks
# Playwright. Run with:  python -m crawlers.itviec --nodriver
# ---------------------------------------------------------------------------

def _nodriver_main() -> None:
    """Async entry-point using nodriver. Import is lazy so CI (which has no
    nodriver in requirements-vps.txt) never hits the import."""
    import asyncio
    import math
    import random
    import re
    import shutil

    import nodriver as uc  # lazy: only imported when nodriver path is executed

    DB_PATH = os.environ.get("ITVIEC_DB", "data/state/itviec_jobs.db")
    CHROME_PATH = os.environ.get("CHROME_PATH")
    PROFILE_DIR = os.environ.get(
        "ITVIEC_PROFILE_DIR",
        str(Path("data/state/chrome_itviec_profile").resolve()),
    )
    OUT_PATH = "data/raw/itviec.jsonl"

    # Smart DOM wait
    LISTING_WAIT = 20
    CARD_POLL = 0.5
    CARD_STABLE_POLLS = 3
    CARD_COUNT_JS = (
        "document.querySelectorAll('div.job-card').length + '|' + document.readyState"
    )
    DEFERRED_ROUNDS = 2
    DEFERRED_PAUSE = (120, 240)
    EMPTY_PAGES_IN_A_ROW = 3
    MIN_COVERAGE = 0.9
    DEBUG_DIR = os.environ.get("ITVIEC_DEBUG_DIR", "data/state/itviec_debug")
    DEBUG_MAX_FILES = 40
    DEBUG_KEEP_DAYS = 7

    _debug_saved = {"count": 0}

    # ---- helpers ----

    async def wait_for_cards(nd_page, timeout=LISTING_WAIT, poll=CARD_POLL,
                             stable_polls=CARD_STABLE_POLLS):
        deadline = time.monotonic() + timeout
        last, same = -1, 0
        count, state = 0, ""
        while True:
            try:
                raw = str(await nd_page.evaluate(CARD_COUNT_JS))
                head, _, state = raw.partition("|")
                count = int(head)
            except (ValueError, TypeError, AttributeError):
                count, state = 0, ""
            same = same + 1 if count == last else 1
            last = count
            if count > 0 and state in ("interactive", "complete") and same >= stable_polls:
                return count, state
            if time.monotonic() >= deadline:
                return count, state
            await asyncio.sleep(poll)

    def is_challenge(html: str) -> bool:
        return any(m in html[:5000] for m in ("Just a moment", "Attention Required", "cf-challenge"))

    # ---- DB ----

    def init_db():
        Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS job_queue (
                job_url TEXT PRIMARY KEY,
                title TEXT, company_name TEXT, salary_preview TEXT,
                location TEXT, work_model TEXT, skills_json TEXT,
                status TEXT DEFAULT 'PENDING',
                retry_count INTEGER DEFAULT 0,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS job_details (
                job_url TEXT PRIMARY KEY,
                title TEXT, company_name TEXT, salary TEXT,
                location TEXT, work_model TEXT, skills_json TEXT,
                description_text TEXT, date_posted TEXT,
                employment_type TEXT, experience_months INTEGER,
                raw_json_ld TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                synced_to_pg INTEGER DEFAULT 0
            )
        """)
        try:
            c.execute("SELECT synced_to_pg FROM job_details LIMIT 0")
        except sqlite3.OperationalError:
            c.execute("ALTER TABLE job_details ADD COLUMN synced_to_pg INTEGER DEFAULT 0")
        try:
            c.execute("SELECT retry_count FROM job_queue LIMIT 0")
        except sqlite3.OperationalError:
            c.execute("ALTER TABLE job_queue ADD COLUMN retry_count INTEGER DEFAULT 0")
        conn.commit()
        return conn

    # ---- Browser client ----

    class ITviecBrowserClient:
        def __init__(self):
            self.browser = None
            self.page = None
            self.last_fetch: dict = {}

        async def start(self):
            print(f"[*] Khởi động trình duyệt với Profile tại: {PROFILE_DIR}", flush=True)
            os.makedirs(PROFILE_DIR, exist_ok=True)
            for lock in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
                p = Path(PROFILE_DIR) / lock
                if p.exists() or p.is_symlink():
                    p.unlink(missing_ok=True)

            kw = {
                "headless": False,
                "user_data_dir": PROFILE_DIR,
                "browser_args": [
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--window-size=1920,1080",
                ],
            }
            if CHROME_PATH:
                kw["browser_executable_path"] = CHROME_PATH
            self.browser = await uc.start(**kw)
            self.page = await self.browser.get("https://itviec.com/")
            await self._wait_cf()

        async def _wait_cf(self):
            for _ in range(20):
                try:
                    title = await self.page.evaluate("document.title")
                    if "Just a moment" in title or "Attention Required" in title:
                        print("  [~] Đang đợi vượt Cloudflare Challenge...", flush=True)
                        await asyncio.sleep(3)
                    else:
                        return
                except Exception:  # noqa: BLE001 - evaluation error during page navigation
                    await asyncio.sleep(1)
            raise RuntimeError("Cloudflare challenge timeout sau 60s")

        async def fetch(self, url, is_listing=False):
            try:
                await asyncio.sleep(random.uniform(2.5, 5.0))
                started = time.monotonic()
                self.page = await self.browser.get(url)
                await self._wait_cf()
                if is_listing:
                    count, state = await wait_for_cards(self.page)
                    self.last_fetch = {
                        "seconds": round(time.monotonic() - started, 1),
                        "ready_state": state, "cards": count,
                    }
                else:
                    try:
                        await self.page.select(
                            "script[type='application/ld+json'], div.job-content", timeout=8)
                    except Exception:  # noqa: BLE001 - selector timeout on slow connection
                        await asyncio.sleep(2.0)
                return await self.page.get_content()
            except Exception as e:  # noqa: BLE001 - page load or network failure
                print(f"[!] Lỗi khi tải {url}: {e}", flush=True)
                return None

        def close(self):
            if self.browser:
                try:
                    self.browser.stop()
                except Exception:  # noqa: BLE001, S110 - browser might already be closed
                    pass

    # ---- Debug ----

    def prune_debug_dir():
        root = Path(DEBUG_DIR)
        if not root.is_dir():
            return
        cutoff = time.time() - DEBUG_KEEP_DAYS * 86400
        for f in root.iterdir():
            try:
                if f.is_dir() and f.stat().st_mtime < cutoff:
                    shutil.rmtree(f, ignore_errors=True)
            except OSError:
                pass

    def note_odd_page(client, label, pg, attempt, html, soup, found_cards, expected):
        info = getattr(client, "last_fetch", None) or {}
        title = soup.title.get_text(" ", strip=True)[:80] if soup and soup.title else ""
        want = f"/{expected}" if expected else ""
        print(
            f"[?] {datetime.now():%H:%M:%S} Trang {pg} lần {attempt}: {len(found_cards)}{want} thẻ, "
            f"tải {info.get('seconds', '?')}s, {len(html)} ký tự HTML, tiêu đề {title!r}",
            flush=True,
        )
        if _debug_saved["count"] >= DEBUG_MAX_FILES:
            return
        try:
            folder = Path(DEBUG_DIR) / datetime.now().strftime("%Y-%m-%d")
            folder.mkdir(parents=True, exist_ok=True)
            (folder / f"{label}-try-{attempt}.html").write_text(html, encoding="utf-8")
            _debug_saved["count"] += 1
        except OSError:
            pass

    # ---- Listing ----

    async def fetch_listing_cards(client, url, pg, expected=None, label=None):
        label = label or f"page-{pg}"

        def too_few(cards):
            return not cards or (expected is not None and len(cards) < expected)

        best = None
        for attempt in range(1, EMPTY_PAGE_TRIES + 1):
            if attempt > 1:
                reason = "không có tin" if not best[2] else f"chỉ có {len(best[2])}/{expected} tin"
                print(f"[~] Trang {pg} {reason}, tải lại ({attempt}/{EMPTY_PAGE_TRIES})", flush=True)
            html = await client.fetch(url, is_listing=True)
            if not html or is_challenge(html):
                return html, best[1] if best else None, []
            soup = BeautifulSoup(html, "lxml")
            found = soup.select("div.job-card")
            if too_few(found):
                note_odd_page(client, label, pg, attempt, html, soup, found, expected)
            if best is None or len(found) > len(best[2]):
                best = (html, soup, found)
            if not too_few(found):
                break
        return best

    def store_listing_cards(cursor, job_cards, seen_list, done_urls=None):
        new_count = 0
        for card_soup in job_cards:
            parsed = parse_card(card_soup)
            if not parsed or not parsed["job_url"]:
                continue
            ju = parsed["job_url"]
            if ju not in seen_list:
                seen_list.append(ju)

            # Nếu tin đã có mô tả trong file JSONL, đánh dấu COMPLETED để không cào lại
            if done_urls and ju in done_urls:
                cursor.execute(
                    "INSERT OR IGNORE INTO job_queue (job_url, title, company_name, salary_preview, "
                    "location, work_model, skills_json, status) VALUES (?,?,?,?,?,?,?,'COMPLETED')",
                    (ju, parsed["title"], parsed["company"], parsed["salary"],
                     parsed["location"], parsed["work_model"],
                     json.dumps(parsed["skills"], ensure_ascii=False)),
                )
            else:
                cursor.execute(
                    "INSERT OR IGNORE INTO job_queue (job_url, title, company_name, salary_preview, "
                    "location, work_model, skills_json, status) VALUES (?,?,?,?,?,?,?,'PENDING')",
                    (ju, parsed["title"], parsed["company"], parsed["salary"],
                     parsed["location"], parsed["work_model"],
                     json.dumps(parsed["skills"], ensure_ascii=False)),
                )
                if cursor.rowcount > 0:
                    new_count += 1
        return new_count

    async def crawl_listing_pages(conn, client, max_pages=60, seen_list=None, problems=None, done_urls=None):
        cursor = conn.cursor()
        if seen_list is None:
            seen_list = []
        if problems is None:
            problems = []
        total = per_page = None
        full_pages: set[int] = set()
        empty_pages: list[int] = []
        short_pages: list[int] = []
        pg = 0
        prune_debug_dir()
        _debug_saved["count"] = 0

        def listed_total_from(soup):
            h = soup.select_one("h1, div.search-page__title")
            if h:
                m = re.search(r"([\d.,]+)\s*(?:IT\s+)?(?:jobs|việc)", h.get_text(), re.IGNORECASE)
                if m:
                    d = re.sub(r"[.,]", "", m.group(1))
                    return int(d) if d else None
            return None

        def last_page():
            return math.ceil(total / per_page) if total and per_page else None

        def expected_cards(p):
            lp = last_page()
            return per_page if lp is not None and p < lp else None

        def gaps():
            top = max(full_pages, default=0)
            return [p for p in empty_pages if p < top]

        def short_of_total():
            return bool(total) and len(seen_list) < MIN_COVERAGE * total

        async def walk():
            nonlocal pg, total, per_page
            in_a_row = 0
            while pg < max_pages:
                pg += 1
                url = LIST_URL if pg == 1 else f"{LIST_URL}?page={pg}"
                print(f"\n[*] {datetime.now():%H:%M:%S} Quét trang {pg}: {url}", flush=True)
                exp = expected_cards(pg)
                html, soup, job_cards = await fetch_listing_cards(client, url, pg, exp)
                if not html or is_challenge(html or ""):
                    print(f"[!] Trang {pg}: bị chặn hoặc lỗi.", flush=True)
                    return "blocked"
                if total is None and soup:
                    total = listed_total_from(soup)
                if not job_cards:
                    empty_pages.append(pg)
                    in_a_row += 1
                    lp = last_page()
                    if (lp is not None and pg > lp) or (lp is None and in_a_row >= EMPTY_PAGES_IN_A_ROW):
                        return "empty"
                    continue
                in_a_row = 0
                if per_page is None:
                    per_page = len(job_cards)
                before = len(seen_list)
                n = store_listing_cards(cursor, job_cards, seen_list, done_urls=done_urls)
                conn.commit()
                full_pages.add(pg)
                print(f"[+] Trang {pg}: {len(job_cards)} jobs -> {n} mới vào queue.", flush=True)
                if exp is not None and len(job_cards) < exp:
                    short_pages.append(pg)
                if len(seen_list) == before:
                    return "repeat"
            return "maxpages"

        ended = await walk()
        rounds = 0
        while (
            ended != "blocked"
            and ((empty_pages and (gaps() or short_of_total())) or short_pages)
            and rounds < DEFERRED_ROUNDS
        ):
            rounds += 1
            pause = random.uniform(*DEFERRED_PAUSE)
            print(f"\n[~] Vòng thử lại {rounds}/{DEFERRED_ROUNDS}: nghỉ {pause:.0f}s", flush=True)
            await asyncio.sleep(pause)
            for p in sorted(empty_pages + short_pages):
                url = LIST_URL if p == 1 else f"{LIST_URL}?page={p}"
                exp = expected_cards(p)
                _html, _soup, job_cards = await fetch_listing_cards(client, url, p, exp, f"page-{p}-r{rounds}")
                if not job_cards:
                    continue
                store_listing_cards(cursor, job_cards, seen_list, done_urls=done_urls)
                conn.commit()
                full_pages.add(p)
                if p in empty_pages:
                    empty_pages.remove(p)
                if exp is None or len(job_cards) >= exp:
                    if p in short_pages:
                        short_pages.remove(p)
                elif p not in short_pages:
                    short_pages.append(p)
            if ended == "empty" and pg in full_pages:
                ended = await walk()

        if ended == "blocked" or not full_pages:
            reached_end = False
        elif gaps():
            reached_end = False
            problems.append(f"pages still empty: {', '.join(map(str, gaps()))}")
        else:
            reached_end = True

        if reached_end and short_of_total():
            reached_end = False
            problems.append(f"met {len(seen_list)} of {total} listed jobs")

        return seen_list, reached_end

    # ---- Detail parse ----

    def parse_detail_html(html):
        soup = BeautifulSoup(html, "lxml")
        result = {
            "title": None, "company_name": None, "salary": None, "location": None,
            "work_model": None, "skills": [], "description_text": "",
            "date_posted": None, "employment_type": None, "experience_months": None,
            "raw_json_ld": "{}",
        }
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                if not script.string:
                    continue
                data = json.loads(script.string, strict=False)
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if isinstance(item, dict) and item.get("@type") == "JobPosting":
                        result["raw_json_ld"] = json.dumps(item, ensure_ascii=False)
                        result["title"] = item.get("title")
                        org = item.get("hiringOrganization", {})
                        if isinstance(org, dict):
                            result["company_name"] = org.get("name")
                        result["date_posted"] = item.get("datePosted")
                        result["employment_type"] = item.get("employmentType")
                        exp = item.get("experienceRequirements") or {}
                        if isinstance(exp, dict):
                            result["experience_months"] = exp.get("monthsOfExperience")
                        loc = item.get("jobLocation")
                        if isinstance(loc, list) and loc:
                            loc = loc[0]
                        if isinstance(loc, dict):
                            addr = loc.get("address", {})
                            if isinstance(addr, dict):
                                result["location"] = f"{addr.get('addressLocality', '')}, {addr.get('addressRegion', '')}".strip(", ")
                        desc_html = item.get("description", "")
                        if desc_html:
                            result["description_text"] = BeautifulSoup(desc_html, "lxml").get_text("\n", strip=True)
                        jd_skills = item.get("skills") or []
                        if isinstance(jd_skills, list):
                            result["skills"] = [s for s in jd_skills if isinstance(s, str)]
                        break
            except (json.JSONDecodeError, TypeError, KeyError, AttributeError):
                continue
        if not result["skills"]:
            skills = [t.get_text(strip=True) for t in soup.select(
                "a[data-responsive-tag-list-target='tag'], div.tag-list a, a.tag") if t.get_text(strip=True)]
            result["skills"] = list(dict.fromkeys(skills))
        return result

    # ---- Detail queue ----

    async def process_job_queue(conn, client, batch_size=100, cooldown_every=30):
        cursor = conn.cursor()
        pending = queue_batch(conn, batch_size, datetime.now())
        print(f"\n[*] Cào chi tiết {len(pending)} jobs...", flush=True)
        for idx, (ju, qt, qc, qs, ql, qwm, qsk) in enumerate(pending, 1):
            print(f"  [{idx}/{len(pending)}] {(qt or '')[:48]}...", flush=True)
            html = await client.fetch(ju, is_listing=False)
            now = datetime.now().isoformat()
            if not html or is_challenge(html):
                cursor.execute(
                    "UPDATE job_queue SET status='FAILED', retry_count = retry_count + 1, updated_at=? WHERE job_url=?",
                    (now, ju),
                )
                conn.commit()
                continue
            p = parse_detail_html(html)
            desc = (p.get("description_text") or "").strip()
            # Không đánh dấu COMPLETED nếu không có mô tả; chuyển FAILED để thử lại lượt sau
            if not desc:
                print(f"  [!] Job {ju}: mô tả rỗng, đánh dấu FAILED để thử lại lượt sau", flush=True)
                cursor.execute(
                    "UPDATE job_queue SET status='FAILED', retry_count = retry_count + 1, updated_at=? WHERE job_url=?",
                    (now, ju),
                )
                conn.commit()
                continue

            q_skills = json.loads(qsk) if qsk else []
            cursor.execute(
                "INSERT OR REPLACE INTO job_details "
                "(job_url, title, company_name, salary, location, work_model, skills_json, "
                "description_text, date_posted, employment_type, experience_months, raw_json_ld, synced_to_pg) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,0)",
                (ju, p["title"] or qt, p["company_name"] or qc, p["salary"] or qs,
                 p["location"] or ql, p["work_model"] or qwm,
                 json.dumps(p["skills"] or q_skills, ensure_ascii=False),
                 desc, p["date_posted"], p["employment_type"],
                 p["experience_months"], p["raw_json_ld"]),
            )
            cursor.execute("UPDATE job_queue SET status='COMPLETED', updated_at=? WHERE job_url=?", (now, ju))
            conn.commit()
            if cooldown_every > 0 and idx % cooldown_every == 0 and idx < len(pending):
                rest = random.uniform(45, 75)
                print(f"  [☕] Nghỉ {rest:.0f}s...", flush=True)
                await asyncio.sleep(rest)

    # ---- Async main ----

    parser = argparse.ArgumentParser(description="ITviec nodriver crawler")
    parser.add_argument("--pages", type=int, default=60)
    parser.add_argument("--skip-details", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--nodriver", action="store_true")
    args = parser.parse_args()

    async def _run():
        db_conn = init_db()
        client = ITviecBrowserClient()
        seen_list: list[str] = []
        complete = False
        error = None
        problems: list[str] = []
        seen_written = False

        # Đọc danh sách URL đã có mô tả trong itviec.jsonl để bỏ qua khi xếp hàng
        done_urls = {r["job_url"] for r in read_jsonl(OUT_PATH) if r.get("description")}
        print(f"[*] Tìm thấy {len(done_urls)} tin đã có mô tả trong {OUT_PATH}", flush=True)

        # Cập nhật status COMPLETED cho các URL đã có sẵn trong file
        if done_urls:
            c = db_conn.cursor()
            for ju in done_urls:
                c.execute("UPDATE job_queue SET status = 'COMPLETED' WHERE job_url = ? AND status != 'COMPLETED'", (ju,))
            db_conn.commit()

        try:
            await client.start()
            try:
                seen_list, complete = await crawl_listing_pages(
                    db_conn, client, max_pages=args.pages,
                    seen_list=seen_list, problems=problems, done_urls=done_urls)
            except (Exception, KeyboardInterrupt, asyncio.CancelledError) as exc:  # noqa: BLE001
                error = f"Listing interrupted ({type(exc).__name__}): {exc}"[:300]
                print(f"\n[!] Listing dừng sớm: {error}", flush=True)

            write_seen("itviec", seen_list, complete,
                       error=error or "; ".join(problems) or None)
            seen_written = True

            if not args.skip_details and seen_list and error is None:
                batch = args.limit if args.limit > 0 else -1
                await process_job_queue(db_conn, client, batch_size=batch, cooldown_every=30)

        except (Exception, KeyboardInterrupt, asyncio.CancelledError) as exc:  # noqa: BLE001
            error = f"{type(exc).__name__}: {exc}"[:300]
            print(f"\n[!] Dừng phiên cào: {error}", flush=True)
        finally:
            if not seen_written:
                write_seen("itviec", seen_list, complete, error=error)
            client.close()
            db_conn.close()
            print("\n[+] Hoàn tất phiên cào ITviec!", flush=True)

        export_jsonl(db_path=DB_PATH, out_path=OUT_PATH)

    uc.loop().run_until_complete(_run())


if __name__ == "__main__":
    import sys
    if "--playwright" in sys.argv:
        main()
    else:
        _nodriver_main()
