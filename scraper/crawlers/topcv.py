import asyncio
import os
import sqlite3
import json
import random
import re
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import nodriver as uc

from crawlers.base import write_seen

DB_PATH = os.environ.get("TOPCV_DB", "data/state/topcv_jobs.db")
CHROME_PATH = os.environ.get("CHROME_PATH")  # nodriver auto-detects when unset
PROFILE_DIR = os.path.abspath("./chrome_topcv_profile")
BASE_SEARCH_URL = "https://www.topcv.vn/tim-viec-lam-cong-nghe-thong-tin-cr257?page={page}"

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

    async def start(self):
        print(f"[*] Đang khởi động trình duyệt với Profile cố định tại: {PROFILE_DIR}")
        os.makedirs(PROFILE_DIR, exist_ok=True)
        
        # Tinh chỉnh 1: Lưu giữ cf_clearance cookie và session trong user_data_dir
        start_kwargs = dict(
            headless=True,
            user_data_dir=PROFILE_DIR,
            browser_args=[
                "--disable-blink-features=AutomationControlled",
                "--blink-settings=imagesEnabled=false",  # Chặn tải ảnh giúp trang nhẹ và nhanh gấp 3 lần
            ],
        )
        if CHROME_PATH:
            start_kwargs["browser_executable_path"] = CHROME_PATH
        self.browser = await uc.start(**start_kwargs)
        self.page = await self.browser.get("https://www.topcv.vn/")
        await self._wait_for_cloudflare()

    async def _wait_for_cloudflare(self):
        for _ in range(15):
            try:
                title = await self.page.evaluate("document.title")
                if "Just a moment" in title or "Attention Required" in title:
                    print("  [~] Đang đợi vượt Cloudflare Challenge...")
                    await asyncio.sleep(3)
                else:
                    break
            except Exception:
                await asyncio.sleep(1)

    async def fetch(self, url: str, is_listing: bool = False) -> str | None:
        try:
            await asyncio.sleep(random.uniform(2.2, 4.0))
            self.page = await self.browser.get(url)
            await self._wait_for_cloudflare()

            # Tinh chỉnh 2: Chờ thông minh đến khi selector mục tiêu xuất hiện thay vì sleep cứng
            target_selector = "div.job-item-search-result" if is_listing else "div.job-description__item, script[type='application/ld+json']"
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
            self.browser.stop()


# 3. PHASE 1: QUÉT DANH SÁCH & LỌC TRÙNG
def extract_job_id_from_url(url: str) -> str | None:
    match = re.search(r'(?:/|-j)(\d+)\.html', url)
    return match.group(1) if match else None

async def crawl_listing_pages(conn: sqlite3.Connection, client: TopCVBrowserClient, start_page: int = 1, max_pages: int = 10):
    """Walk the listing. Returns (absolute URLs seen, reached_the_end)."""
    cursor = conn.cursor()
    seen: list[str] = []
    reached_end = False
    for page_num in range(start_page, start_page + max_pages):
        url = BASE_SEARCH_URL.format(page=page_num)
        print(f"\n[*] Đang quét trang danh sách {page_num}: {url}")
        
        html = await client.fetch(url, is_listing=True)
        if html == "NOT_FOUND":
            reached_end = True
            break
        if not html:
            break  # a block or a load error: listing stays incomplete

        soup = BeautifulSoup(html, "lxml")
        job_cards = soup.select("div.job-item-search-result")
        
        if not job_cards:
            reached_end = True  # an empty page is the only proof we reached the end
            print("[!] Không tìm thấy danh sách job trên trang này. Dừng phân trang.")
            break

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

            cursor.execute("""
                INSERT OR IGNORE INTO job_queue (job_id, url, title, company_name, salary_preview)
                VALUES (?, ?, ?, ?, ?)
            """, (str(job_id), raw_url, title, company, salary))
            
            abs_url = raw_url if raw_url.startswith("http") else "https://www.topcv.vn" + raw_url
            if abs_url not in seen:
                seen.append(abs_url)
            if cursor.rowcount > 0:
                new_jobs_count += 1

        conn.commit()
        print(f"[+] Trang {page_num}: Tìm thấy {len(job_cards)} jobs -> Thêm mới {new_jobs_count} jobs.")
    else:
        reached_end = True  # walked every page up to max_pages
    return seen, reached_end


# 4. PHASE 2: BÓC TÁCH CHI TIẾT JD THEO BATCH AN TOÀN
def parse_jd_html(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    result = {
        "title": None, "company_name": None, "salary": None,
        "experience": None, "job_level": None, "employment_type": None,
        "location": None, "date_posted": None, "valid_through": None,
        "description_text": "", "requirements_text": "", "benefits_text": "",
        "skills": [], "raw_json_ld": "{}"
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


async def process_job_queue(conn: sqlite3.Connection, client: TopCVBrowserClient, batch_size: int = 100, cooldown_every: int = 40):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT job_id, url, title, company_name, salary_preview 
        FROM job_queue 
        WHERE status = 'PENDING' 
        LIMIT ?
    """, (batch_size,))
    
    pending_jobs = cursor.fetchall()
    print(f"\n[*] Bắt đầu cào chi tiết {len(pending_jobs)} jobs đang chờ...")

    for idx, (job_id, url, q_title, q_company, q_salary) in enumerate(pending_jobs, 1):
        print(f"  [{idx}/{len(pending_jobs)}] Job ID {job_id}: {q_title[:48]}...")
        
        html = await client.fetch(url, is_listing=False)
        now = datetime.now().isoformat()

        if html == "NOT_FOUND":
            cursor.execute("UPDATE job_queue SET status = 'NOT_FOUND', updated_at = ? WHERE job_id = ?", (now, job_id))
            conn.commit()
            continue
        elif not html:
            cursor.execute("UPDATE job_queue SET status = 'FAILED', updated_at = ? WHERE job_id = ?", (now, job_id))
            conn.commit()
            continue

        parsed = parse_jd_html(html)
        final_title = parsed["title"] or q_title
        final_company = parsed["company_name"] or q_company
        final_salary = parsed["salary"] or q_salary

        cursor.execute("""
            INSERT OR REPLACE INTO job_details (
                job_id, title, company_name, salary, experience, job_level,
                employment_type, location, date_posted, valid_through,
                description_text, requirements_text, benefits_text,
                skills_json, raw_json_ld, synced_to_pg
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, (
            job_id, final_title, final_company, final_salary,
            parsed["experience"], parsed["job_level"], parsed["employment_type"],
            parsed["location"], parsed["date_posted"], parsed["valid_through"],
            parsed["description_text"], parsed["requirements_text"], parsed["benefits_text"],
            json.dumps(parsed["skills"], ensure_ascii=False), parsed["raw_json_ld"]
        ))

        cursor.execute("UPDATE job_queue SET status = 'COMPLETED', updated_at = ? WHERE job_id = ?", (now, job_id))
        conn.commit()

        # Tinh chỉnh 3: Nghỉ giải lao giữa các cụm request để tránh Cloudflare Rate Limit theo IP
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

    from pathlib import Path
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


async def main():
    db_conn = init_db()
    client = TopCVBrowserClient()
    seen, complete, error = [], False, None
    try:
        await client.start()
        try:
            seen, complete = await crawl_listing_pages(db_conn, client, start_page=1, max_pages=200)
        except Exception as exc:  # noqa: BLE001 - a block mid-walk keeps what it saw
            error = str(exc)[:300]
            print(f"[!] listing incomplete: {error}")
        # Written before details, so a block during details cannot lose the observation.
        write_seen("topcv", seen, complete, error=error)
        if complete or seen:
            await process_job_queue(db_conn, client, batch_size=5000, cooldown_every=30)
    except Exception as exc:  # noqa: BLE001 - Cloudflare never cleared, or the browser died
        error = str(exc)[:300]
        print(f"[!] STOP -- {error}")
        write_seen("topcv", seen, complete, error=error)
    finally:
        client.close()
        db_conn.close()
        print("\n[+] Hoàn tat phien cao du lieu TopCV!")

    export_jsonl(out_path="data/raw/topcv.jsonl")


if __name__ == "__main__":
    uc.loop().run_until_complete(main())