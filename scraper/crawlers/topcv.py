import argparse
import asyncio
import os
import sqlite3
import json
import math
import random
import re
import shutil
import time
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import nodriver as uc

from crawlers.base import write_seen

DB_PATH = os.environ.get("TOPCV_DB", "data/state/topcv_jobs.db")
CHROME_PATH = os.environ.get("CHROME_PATH")  # nodriver auto-detects when unset
# Ca profile lan hang doi nam duoi data/state: trong container la volume scraper_data, giu qua cac dem.
PROFILE_DIR = os.environ.get(
    "TOPCV_PROFILE_DIR",
    str(Path("data/state/chrome_topcv_profile").resolve()),
)
BASE_SEARCH_URL = "https://www.topcv.vn/tim-viec-lam-cong-nghe-thong-tin-cr257?page={page}"

# 18/11: trang 24 đọc được 22/50 thẻ vì fetch() đọc HTML ngay khi thẻ đầu tiên hiện.
# Trang listing chỉ được đọc khi số thẻ đứng yên CARD_STABLE_POLLS lần đếm liền và DOM đã parse xong.
LISTING_WAIT = 20  # giây tối đa chờ thẻ tin
CARD_POLL = 0.5  # giây giữa hai lần đếm
CARD_STABLE_POLLS = 3
CARD_COUNT_JS = (
    "document.querySelectorAll('div.job-item-search-result').length + '|' + document.readyState"
)
# Trang rỗng hoặc thiếu thẻ được lưu lại để biết là trang chậm hay trang chặn.
DEBUG_DIR = os.environ.get("TOPCV_DEBUG_DIR", "data/state/topcv_debug")
DEBUG_MAX_FILES = 40  # mỗi lượt
DEBUG_KEEP_DAYS = 7


async def wait_for_cards(
    page,
    timeout: float = LISTING_WAIT,
    poll: float = CARD_POLL,
    stable_polls: int = CARD_STABLE_POLLS,
    sleep=asyncio.sleep,
    clock=time.monotonic,
) -> tuple[int, str]:
    """Wait until the listing's job cards stop growing and the DOM is parsed.

    Returns (card count, document.readyState) at the end; gives up after `timeout`.
    """
    deadline = clock() + timeout
    last, same = -1, 0
    count, state = 0, ""
    while True:
        try:
            raw = str(await page.evaluate(CARD_COUNT_JS))
            head, _, state = raw.partition("|")
            count = int(head)
        except Exception:
            count, state = 0, ""
        same = same + 1 if count == last else 1
        last = count
        if count > 0 and state in ("interactive", "complete") and same >= stable_polls:
            return count, state
        if clock() >= deadline:
            return count, state
        await sleep(poll)


# 1. KHỞI TẠO DATABASE SQLITE LOCAL
def init_db():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_queue (
            job_id TEXT PRIMARY KEY,
            url TEXT NOT NULL,
            title TEXT,
            company_name TEXT,
            salary_preview TEXT,
            status TEXT DEFAULT 'PENDING', -- PENDING, COMPLETED, FAILED, NOT_FOUND
            discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_details (
            job_id TEXT PRIMARY KEY,
            title TEXT,
            company_name TEXT,
            salary TEXT,
            experience TEXT,
            job_level TEXT,
            employment_type TEXT,
            location TEXT,
            date_posted TEXT,
            valid_through TEXT,
            description_text TEXT,
            requirements_text TEXT,
            benefits_text TEXT,
            skills_json TEXT,
            raw_json_ld TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            synced_to_pg INTEGER DEFAULT 0
        )
    """)
    # migrate: thêm cột synced_to_pg nếu DB cũ chưa có
    try:
        cursor.execute("SELECT synced_to_pg FROM job_details LIMIT 0")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE job_details ADD COLUMN synced_to_pg INTEGER DEFAULT 0")

    conn.commit()
    return conn


# 2. BROWSER CLIENT VỚI CHROME PROFILE CỐ ĐỊNH & SMART DOM WAIT
class TopCVBrowserClient:
    def __init__(self):
        self.browser = None
        self.page = None
        self.last_fetch: dict = {}  # thời gian, readyState, số thẻ của lần tải listing gần nhất

    async def start(self):
        print(f"[*] Đang khởi động trình duyệt với Profile cố định tại: {PROFILE_DIR}", flush=True)
        os.makedirs(PROFILE_DIR, exist_ok=True)
        # Container lần trước bị kill thì Chrome để lại file khóa, lần sau không mở được profile
        for lock_name in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
            lock_file = Path(PROFILE_DIR) / lock_name
            if lock_file.exists() or lock_file.is_symlink():
                lock_file.unlink(missing_ok=True)

        # headless=False: trên VPS chạy dưới Xvfb (pipeline.py bọc xvfb-run), trên máy local là cửa sổ thật
        start_kwargs = dict(
            headless=False,
            user_data_dir=PROFILE_DIR,
            browser_args=[
                "--disable-blink-features=AutomationControlled",
                # Chrome chạy dưới user runner trong container
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--window-size=1920,1080",
            ],
        )
        if CHROME_PATH:
            start_kwargs["browser_executable_path"] = CHROME_PATH
        self.browser = await uc.start(**start_kwargs)
        self.page = await self.browser.get("https://www.topcv.vn/")
        await self._wait_for_cloudflare()

    async def _wait_for_cloudflare(self):
        for i in range(20):
            try:
                title = await self.page.evaluate("document.title")
                if "Just a moment" in title or "Attention Required" in title:
                    if i == 0:
                        print("  [~] Đang đợi vượt Cloudflare Challenge (hãy click ô xác thực trên Chrome nếu có)...")
                    else:
                        print("  [~] Đang đợi vượt Cloudflare Challenge...")
                    await asyncio.sleep(3)
                else:
                    return
            except Exception:
                await asyncio.sleep(1)
        raise RuntimeError("Cloudflare challenge timeout sau 60s")

    async def fetch(self, url: str, is_listing: bool = False) -> str | None:
        try:
            await asyncio.sleep(random.uniform(2.2, 4.0))
            started = time.monotonic()
            self.page = await self.browser.get(url)
            await self._wait_for_cloudflare()

            if is_listing:
                count, state = await wait_for_cards(self.page)
                self.last_fetch = {
                    "seconds": round(time.monotonic() - started, 1),
                    "ready_state": state,
                    "cards": count,
                }
            else:
                # Chờ thông minh đến khi selector mục tiêu xuất hiện thay vì sleep cứng
                target_selector = "div.job-description__item, script[type='application/ld+json']"
                try:
                    await self.page.select(target_selector, timeout=6)
                except Exception:
                    # Fallback cho các trang Brand thiết kế riêng
                    await asyncio.sleep(1.5)

            html = await self.page.get_content()
            if "Không tìm thấy trang" in html or "Trang bạn tìm kiếm không tồn tại" in html:
                return "NOT_FOUND"
            return html
        except Exception as e:
            print(f"[!] Lỗi khi tải trang {url}: {e}")
            return None

    def close(self):
        if self.browser:
            try:
                self.browser.stop()
            except Exception:
                pass


# 3. PHASE 1: QUÉT DANH SÁCH & LỌC TRÙNG
def is_challenge(html: str) -> bool:
    return any(m in html[:5000] for m in ("Just a moment", "Attention Required", "cf-challenge"))


# Trang tải chậm có thể chưa hiện thẻ tin khi đọc HTML (16/11 trên VPS: trang 16 rỗng, tải lại thì đủ 50 tin).
EMPTY_PAGE_TRIES = 3
# Thấy ít hơn tỷ lệ này so với tổng TopCV ghi trên tiêu đề thì lượt chưa đủ.
MIN_COVERAGE = 0.9
# 18/11 trên VPS: trang 18-45 rỗng ngày càng dày, trang 45 rỗng cả 3 lần nên lượt dừng ở 2169/2502.
# Trang vẫn rỗng sau EMPTY_PAGE_TRIES lần thì để lại, đi tiếp, rồi thử lại sau khi nghỉ.
DEFERRED_ROUNDS = 2
DEFERRED_PAUSE = (120, 240)  # giây, mỗi vòng thử lại
# Tiêu đề không có tổng thì không biết trang cuối: chừng này trang rỗng liền nhau là hết listing.
EMPTY_PAGES_IN_A_ROW = 3


def listed_total(soup) -> int | None:
    """Tổng số việc làm TopCV ghi trên tiêu đề: "Tuyển dụng 2.293 việc làm ..."."""
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    match = re.search(r"([\d.,]+)\s*việc làm", title)
    if not match:
        return None
    digits = re.sub(r"[.,]", "", match.group(1))
    return int(digits) if digits else None


def extract_job_id_from_url(url: str) -> str | None:
    match = re.search(r"(?:/|-j)(\d+)\.html", url)
    return match.group(1) if match else None


_debug_saved = {"count": 0}


def prune_debug_dir(keep_days: int = DEBUG_KEEP_DAYS) -> None:
    """Drop debug folders older than `keep_days`, so the volume does not fill up."""
    root = Path(DEBUG_DIR)
    if not root.is_dir():
        return
    cutoff = time.time() - keep_days * 86400
    for folder in root.iterdir():
        try:
            if folder.is_dir() and folder.stat().st_mtime < cutoff:
                shutil.rmtree(folder, ignore_errors=True)
        except OSError:
            pass


def note_odd_page(client, label: str, page_num: int, attempt: int, html: str, soup, cards, expected) -> None:
    """Log what an empty or short listing page looked like and keep its HTML for diagnosis."""
    info = getattr(client, "last_fetch", None) or {}
    title = soup.title.get_text(" ", strip=True)[:80] if soup is not None and soup.title else ""
    want = f"/{expected}" if expected else ""
    print(
        f"[?] {datetime.now():%H:%M:%S} Trang {page_num} lần {attempt}: {len(cards)}{want} thẻ, "
        f"tải {info.get('seconds', '?')}s, readyState={info.get('ready_state', '?')}, "
        f"{len(html)} ký tự HTML, tiêu đề {title!r}",
        flush=True,
    )
    if _debug_saved["count"] >= DEBUG_MAX_FILES:
        return
    try:
        folder = Path(DEBUG_DIR) / datetime.now().strftime("%Y-%m-%d")
        folder.mkdir(parents=True, exist_ok=True)
        (folder / f"{label}-try-{attempt}.html").write_text(html, encoding="utf-8")
        _debug_saved["count"] += 1
    except OSError as exc:
        print(f"[!] Không lưu được HTML chẩn đoán: {exc}", flush=True)


async def fetch_listing_cards(client, url: str, page_num: int, expected: int | None = None, label: str | None = None):
    """Fetch a listing page; fetch again up to EMPTY_PAGE_TRIES times while it has no job
    cards, or fewer than `expected`. Returns (html, soup, cards) of the fetch with the most cards.

    A blocked or missing page comes back at once with no cards. Every empty or short
    fetch is logged and its HTML kept under DEBUG_DIR.
    """
    label = label or f"page-{page_num}"

    def too_few(found) -> bool:
        return not found or (expected is not None and len(found) < expected)

    best = None
    for attempt in range(1, EMPTY_PAGE_TRIES + 1):
        if attempt > 1:
            reason = "không có tin" if not best[2] else f"chỉ có {len(best[2])}/{expected} tin"
            print(f"[~] Trang {page_num} {reason}, tải lại ({attempt}/{EMPTY_PAGE_TRIES})", flush=True)
        html = await client.fetch(url, is_listing=True)
        if not html or html == "NOT_FOUND" or is_challenge(html):
            return html, best[1] if best else None, []
        soup = BeautifulSoup(html, "lxml")
        cards = soup.select("div.job-item-search-result")
        if too_few(cards):
            note_odd_page(client, label, page_num, attempt, html, soup, cards, expected)
        if best is None or len(cards) > len(best[2]):
            best = (html, soup, cards)
        if not too_few(cards):
            break
    return best


def store_listing_cards(cursor, job_cards, seen: list[str]) -> int:
    """Queue the cards' jobs and add their URLs to `seen`. Returns how many jobs were new to the queue."""
    new_jobs_count = 0
    for card in job_cards:
        job_id = card.get("data-job-id")
        title_tag = card.select_one("h3.title a")
        if not title_tag:
            continue

        raw_url = title_tag.get("href", "").split("?")[0]
        if not job_id:
            job_id = extract_job_id_from_url(raw_url)
        if not job_id:
            continue

        title = title_tag.get_text(strip=True)
        company_tag = card.select_one("a.company")
        company = company_tag.get_text(strip=True) if company_tag else ""
        salary_tag = card.select_one("label.title-salary")
        salary = salary_tag.get_text(strip=True) if salary_tag else ""

        cursor.execute(
            """
            INSERT OR IGNORE INTO job_queue (job_id, url, title, company_name, salary_preview)
            VALUES (?, ?, ?, ?, ?)
            """,
            (str(job_id), raw_url, title, company, salary),
        )

        abs_url = raw_url if raw_url.startswith("http") else "https://www.topcv.vn" + raw_url
        if abs_url not in seen:
            seen.append(abs_url)
        if cursor.rowcount > 0:
            new_jobs_count += 1
    return new_jobs_count


async def crawl_listing_pages(
    conn: sqlite3.Connection,
    client: TopCVBrowserClient,
    start_page: int = 1,
    seen: list[str] | None = None,
    problems: list[str] | None = None,
):
    """Walk the listing until it ends. Returns (absolute URLs seen, reached_the_end).

    A page without job cards is fetched again up to EMPTY_PAGE_TRIES times. If it is
    still empty it is set aside and the walk goes on, up to the last page the title's
    total implies (without a total: until EMPTY_PAGES_IN_A_ROW empty pages in a row).
    When an empty page sits between full pages, or the walk is short of MIN_COVERAGE
    of the total, the pages set aside are fetched again after DEFERRED_PAUSE, for at
    most DEFERRED_ROUNDS rounds. An empty page left between full pages, or a walk
    short of the total, makes the run incomplete; the reason goes into `problems`.
    A page with fewer cards than the first page, before the last page, is fetched
    again the same way; if it stays short its cards are kept and it is fetched again
    in the rounds too. A blocked page ends the walk as incomplete at once.

    Passing `seen` in place ensures that if the user presses Ctrl+C mid-walk,
    all URLs collected up to that point are preserved for `write_seen`.
    """
    cursor = conn.cursor()
    if seen is None:
        seen = []
    if problems is None:
        problems = []
    total = None
    per_page = None
    full_pages: set[int] = set()
    empty_pages: list[int] = []
    short_pages: list[int] = []
    page_num = start_page - 1
    prune_debug_dir()
    _debug_saved["count"] = 0

    def last_page() -> int | None:
        return math.ceil(total / per_page) if total and per_page else None

    def expected_cards(page: int) -> int | None:
        """Cards a page must have: as many as the first page, except the last page."""
        last = last_page()
        return per_page if last is not None and page < last else None

    def gaps() -> list[int]:
        top = max(full_pages, default=0)
        return [p for p in empty_pages if p < top]

    def short_of_total() -> bool:
        return bool(total) and len(seen) < MIN_COVERAGE * total

    async def walk() -> str:
        """Walk forward from page_num + 1. Returns 'blocked', 'end', 'repeat' or 'empty'."""
        nonlocal page_num, total, per_page
        in_a_row = 0
        while True:
            page_num += 1
            url = BASE_SEARCH_URL.format(page=page_num)
            print(f"\n[*] {datetime.now():%H:%M:%S} Đang quét trang danh sách {page_num}: {url}")

            expected = expected_cards(page_num)
            html, soup, job_cards = await fetch_listing_cards(client, url, page_num, expected)
            if html == "NOT_FOUND":
                return "end"
            if not html or is_challenge(html):
                print(f"[!] Trang {page_num}: bị chặn hoặc lỗi tải. Listing chưa hoàn chỉnh.")
                return "blocked"
            if total is None:
                total = listed_total(soup)

            if not job_cards:
                empty_pages.append(page_num)
                in_a_row += 1
                last = last_page()
                if (last is not None and page_num > last) or (
                    last is None and in_a_row >= EMPTY_PAGES_IN_A_ROW
                ):
                    print("[!] Không tìm thấy danh sách job trên trang này. Dừng phân trang.")
                    return "empty"
                print(f"[~] Trang {page_num} vẫn không có tin: để lại thử sau, đi tiếp.", flush=True)
                continue

            in_a_row = 0
            if per_page is None:
                per_page = len(job_cards)
            seen_before_page = len(seen)
            new_jobs_count = store_listing_cards(cursor, job_cards, seen)
            conn.commit()
            full_pages.add(page_num)
            print(f"[+] Trang {page_num}: Tìm thấy {len(job_cards)} jobs -> Thêm mới {new_jobs_count} jobs.")
            if expected is not None and len(job_cards) < expected:
                short_pages.append(page_num)
                print(f"[~] Trang {page_num} vẫn thiếu tin ({len(job_cards)}/{expected}): giữ tin, thử lại sau.")
            if len(seen) == seen_before_page:  # the site is repeating a page: nothing further
                return "repeat"

    ended = await walk()
    rounds = 0
    while (
        ended != "blocked"
        and ((empty_pages and (gaps() or short_of_total())) or short_pages)
        and rounds < DEFERRED_ROUNDS
    ):
        rounds += 1
        pause = random.uniform(*DEFERRED_PAUSE)
        listed = ", ".join(map(str, sorted(empty_pages + short_pages)))
        print(
            f"\n[~] Vòng thử lại {rounds}/{DEFERRED_ROUNDS}: nghỉ {pause:.0f}s rồi tải lại trang {listed}",
            flush=True,
        )
        await asyncio.sleep(pause)
        for p in sorted(empty_pages + short_pages):
            url = BASE_SEARCH_URL.format(page=p)
            expected = expected_cards(p)
            label = f"page-{p}-round-{rounds}"
            html, soup, job_cards = await fetch_listing_cards(client, url, p, expected, label)
            if not job_cards:
                continue
            new_jobs_count = store_listing_cards(cursor, job_cards, seen)
            conn.commit()
            full_pages.add(p)
            if p in empty_pages:
                empty_pages.remove(p)
            if expected is None or len(job_cards) >= expected:
                if p in short_pages:
                    short_pages.remove(p)
            elif p not in short_pages:
                short_pages.append(p)
            print(f"[+] Trang {p} (thử lại): Tìm thấy {len(job_cards)} jobs -> Thêm mới {new_jobs_count} jobs.")
        if ended == "empty" and page_num in full_pages:
            ended = await walk()  # the page that ended the walk has jobs now: the listing goes on

    if ended == "blocked" or not full_pages:
        reached_end = False
    elif gaps():
        reached_end = False
        missing = ", ".join(map(str, gaps()))
        problems.append(f"pages still empty: {missing}")
        print(f"[!] Trang {missing} vẫn không có tin sau {rounds} vòng thử lại. Listing chưa hoàn chỉnh.", flush=True)
    else:
        reached_end = True
    if short_pages:
        missing = ", ".join(map(str, short_pages))
        print(f"[~] Trang {missing} vẫn thiếu tin sau {rounds} vòng thử lại.", flush=True)

    if reached_end and short_of_total():
        reached_end = False
        problems.append(f"met {len(seen)} of {total} listed jobs")
        print(f"[!] Listing dừng ở trang {page_num} với {len(seen)}/{total} tin: chưa đủ.", flush=True)

    return seen, reached_end


# 4. PHASE 2: BÓC TÁCH CHI TIẾT JD THEO BATCH AN TOÀN
def parse_jd_html(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    result = {
        "title": None,
        "company_name": None,
        "salary": None,
        "experience": None,
        "job_level": None,
        "employment_type": None,
        "location": None,
        "date_posted": None,
        "valid_through": None,
        "description_text": "",
        "requirements_text": "",
        "benefits_text": "",
        "skills": [],
        "raw_json_ld": "{}",
    }

    for script in soup.find_all("script", type="application/ld+json"):
        try:
            if not script.string:
                continue
            data = json.loads(script.string, strict=False)
            if data.get("@type") == "JobPosting":
                result["raw_json_ld"] = json.dumps(data, ensure_ascii=False)
                result["title"] = data.get("title")
                result["company_name"] = data.get("hiringOrganization", {}).get("name")
                result["date_posted"] = data.get("datePosted")
                result["valid_through"] = data.get("validThrough")
                result["employment_type"] = data.get("employmentType")

                loc = data.get("jobLocation")
                if isinstance(loc, list) and loc:
                    loc = loc[0]
                if isinstance(loc, dict):
                    addr = loc.get("address", {})
                    result["location"] = f"{addr.get('addressLocality', '')}, {addr.get('addressRegion', '')}".strip(", ")

                desc_html = data.get("description", "")
                if desc_html:
                    desc_soup = BeautifulSoup(desc_html, "lxml")
                    result["description_text"] = desc_soup.get_text(separator="\n", strip=True)
                break
        except Exception:
            continue

    for item in soup.select("div.job-description__item"):
        h3 = item.find("h3")
        content_div = item.select_one("div.job-description__item--content")
        if not h3 or not content_div:
            continue
        header_text = h3.get_text(strip=True).lower()
        clean_text = content_div.get_text(separator="\n", strip=True)

        if "mô tả" in header_text:
            result["description_text"] = clean_text
        elif "yêu cầu" in header_text:
            result["requirements_text"] = clean_text
        elif "quyền lợi" in header_text or "chế độ" in header_text:
            result["benefits_text"] = clean_text

    for box in soup.select("div.job-detail__info--section, div.box-general-group-info"):
        label = box.select_one("div.job-detail__info--section-content-title, div.box-general-group-info-title")
        val = box.select_one("div.job-detail__info--section-content-value, div.box-general-group-info-value")
        if label and val:
            l_text = label.get_text(strip=True).lower()
            v_text = val.get_text(strip=True)
            if "mức lương" in l_text or "thu nhập" in l_text:
                result["salary"] = v_text
            elif "kinh nghiệm" in l_text:
                result["experience"] = v_text
            elif "cấp bậc" in l_text:
                result["job_level"] = v_text

    skills = [
        tag.get_text(strip=True)
        for tag in soup.select("div.box-category-tags a, a.item-tag, div.skill-tag a")
        if tag.get_text(strip=True)
    ]
    result["skills"] = list(dict.fromkeys(skills))
    return result


async def process_job_queue(
    conn: sqlite3.Connection,
    client: TopCVBrowserClient,
    batch_size: int = 100,
    cooldown_every: int = 40,
):
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT job_id, url, title, company_name, salary_preview 
        FROM job_queue 
        WHERE status = 'PENDING' 
        LIMIT ?
        """,
        (batch_size,),
    )

    pending_jobs = cursor.fetchall()
    print(f"\n[*] Bắt đầu cào chi tiết {len(pending_jobs)} jobs đang chờ...")

    for idx, (job_id, url, q_title, q_company, q_salary) in enumerate(pending_jobs, 1):
        print(f"  [{idx}/{len(pending_jobs)}] Job ID {job_id}: {(q_title or '')[:48]}...")

        html = await client.fetch(url, is_listing=False)
        now = datetime.now().isoformat()

        if html == "NOT_FOUND":
            cursor.execute("UPDATE job_queue SET status = 'NOT_FOUND', updated_at = ? WHERE job_id = ?", (now, job_id))
            conn.commit()
            continue
        elif not html or is_challenge(html):
            cursor.execute("UPDATE job_queue SET status = 'FAILED', updated_at = ? WHERE job_id = ?", (now, job_id))
            conn.commit()
            continue

        parsed = parse_jd_html(html)
        final_title = parsed["title"] or q_title
        final_company = parsed["company_name"] or q_company
        final_salary = parsed["salary"] or q_salary

        cursor.execute(
            """
            INSERT OR REPLACE INTO job_details (
                job_id, title, company_name, salary, experience, job_level,
                employment_type, location, date_posted, valid_through,
                description_text, requirements_text, benefits_text,
                skills_json, raw_json_ld, synced_to_pg
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (
                job_id,
                final_title,
                final_company,
                final_salary,
                parsed["experience"],
                parsed["job_level"],
                parsed["employment_type"],
                parsed["location"],
                parsed["date_posted"],
                parsed["valid_through"],
                parsed["description_text"],
                parsed["requirements_text"],
                parsed["benefits_text"],
                json.dumps(parsed["skills"], ensure_ascii=False),
                parsed["raw_json_ld"],
            ),
        )

        cursor.execute("UPDATE job_queue SET status = 'COMPLETED', updated_at = ? WHERE job_id = ?", (now, job_id))
        conn.commit()

        # Nghỉ giải lao giữa các cụm request để tránh Cloudflare Rate Limit theo IP
        if idx % cooldown_every == 0 and idx < len(pending_jobs):
            rest_sec = random.uniform(45, 75)
            print(f"  [☕] Đã cào {idx} trang liên tiếp. Tạm nghỉ {rest_sec:.0f}s làm mát IP...")
            await asyncio.sleep(rest_sec)


def export_jsonl(db_path: str = DB_PATH, out_path: str = "data/raw/topcv.jsonl"):
    """Export job_details from SQLite to JSONL matching the pipeline schema."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.job_id, q.url, d.title, d.company_name, d.salary,
               d.experience, d.job_level, d.employment_type, d.location,
               d.date_posted, d.valid_through,
               d.description_text, d.requirements_text, d.benefits_text,
               d.skills_json
        FROM job_details d
        JOIN job_queue q ON d.job_id = q.job_id
        WHERE q.status = 'COMPLETED'
    """)

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with out.open("w", encoding="utf-8") as fh:
        for row in cursor:
            desc_parts = [
                row["description_text"] or "",
                row["requirements_text"] or "",
                row["benefits_text"] or "",
            ]
            description = "\n\n".join(p for p in desc_parts if p).strip()

            skills = []
            if row["skills_json"]:
                try:
                    skills = json.loads(row["skills_json"])
                except Exception:
                    pass

            job_url = row["url"]
            if job_url and not job_url.startswith("http"):
                job_url = "https://www.topcv.vn" + job_url

            record = {
                "site": "topcv",
                "job_id": row["job_id"],
                "job_url": job_url,
                "title": row["title"],
                "company": row["company_name"],
                "location": row["location"],
                "salary": row["salary"],
                "experience_level": row["experience"],
                "job_level": row["job_level"],
                "employment_type": row["employment_type"],
                "skills": skills,
                "description": description,
                "date_posted": row["date_posted"],
                "valid_through": row["valid_through"],
            }
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1

    conn.close()
    print(f"[+] Exported {count} jobs to {out}")
    return count


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="TopCV nodriver crawler")
    parser.add_argument("--skip-details", action="store_true", help="chỉ quét trang danh sách")
    parser.add_argument("--limit", type=int, default=0, help="giới hạn số trang chi tiết (0 = không giới hạn)")
    return parser.parse_args(argv)


async def main():
    args = parse_args()
    db_conn = init_db()
    client = TopCVBrowserClient()
    seen: list[str] = []
    complete = False
    error = None
    problems: list[str] = []
    seen_written = False

    try:
        await client.start()
        try:
            seen, complete = await crawl_listing_pages(
                db_conn, client, start_page=1, seen=seen, problems=problems
            )
        except (Exception, KeyboardInterrupt, asyncio.CancelledError) as exc:
            error = f"Listing interrupted ({type(exc).__name__}): {exc}"[:300]
            print(f"\n[!] Listing dừng sớm: {error}", flush=True)

        # Chỉ ghi những URL listing hôm nay thật sự hiện ra. Không lấy URL cũ trong job_queue:
        # job_observations sẽ hiểu là tin đó hôm nay vẫn còn.
        write_seen("topcv", seen, complete, error=error or "; ".join(problems) or None)
        seen_written = True

        if not args.skip_details and seen and error is None:
            batch_size = args.limit if args.limit > 0 else -1
            await process_job_queue(db_conn, client, batch_size=batch_size, cooldown_every=30)

    except (Exception, KeyboardInterrupt, asyncio.CancelledError) as exc:
        error = f"{type(exc).__name__}: {exc}"[:300]
        print(f"\n[!] Dừng phiên cào: {error}", flush=True)
    finally:
        if not seen_written:
            write_seen("topcv", seen, complete, error=error)
        client.close()
        db_conn.close()
        print("\n[+] Hoàn tất phiên cào dữ liệu TopCV!", flush=True)

    export_jsonl(db_path=DB_PATH, out_path="data/raw/topcv.jsonl")


if __name__ == "__main__":
    try:
        uc.loop().run_until_complete(main())
    except KeyboardInterrupt:
        pass