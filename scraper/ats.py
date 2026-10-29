"""
Tin tuyển dụng ở Việt Nam từ API job board CÔNG KHAI của các ATS (Greenhouse, Lever, Workable).

Đây là API mà chính ATS công bố để hiển thị tin ra ngoài, không cần khóa:
- Greenhouse: "Job Board data is publicly available, so authentication is not required for any GET endpoints."
- Lever: tin đã đăng là công khai và "may be scraped by third parties" (README `lever/postings-api`).
- Workable: widget API công khai; robots.txt của apply.workable.com cho phép.
SmartRecruiters KHÔNG dùng: robots.txt của api.smartrecruiters.com chỉ cho LinkedInBot (`User-agent: *` -> `Disallow: /`).

Mỗi bảng tin chỉ tốn một request. Chỉ giữ tin ở Việt Nam và là tin IT. Không có trường `skills`:
kỹ năng được trích từ mô tả bằng `skills_text` rồi bỏ văn bản (AD-7). Lương chỉ lấy khi API trả số
(Lever `salaryRange`); Greenhouse/Workable không trả lương trong API danh sách.
"""
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Iterator, List, Mapping, Optional, Sequence, Tuple

from scraper.jobboards import (
    CrawlState,
    IT_CATEGORY,
    LOCATION_MAX_LENGTH,
    ScrapedJob,
    SitemapEntry,
    compute_source_id,
    derive_web_level,
    is_it_title,
    is_non_it_title,
    cities_in,
)
from scraper.polite_http import BlockedError, DisallowedError, PoliteClient
from scraper.skills_text import skills_from_text

logger = logging.getLogger("skillnexus.scraper")

_VN_RE = re.compile(
    r"viet ?nam|ho chi minh|hcmc|saigon|ha ?noi|da ?nang|can tho|hai phong|hồ chí minh|hà nội|đà nẵng|cần thơ",
    re.IGNORECASE,
)
# Phòng ban / nhóm / chức năng thuộc khối công nghệ
_IT_DEPT_RE = re.compile(
    r"(?<![a-z])(engineering|technology|tech|it|r&d|research and development|data|software|development|product"
    r"|information technology|devops|infrastructure|security|qa|quality assurance)(?![a-z])",
    re.IGNORECASE,
)
_WORKABLE_LEVELS = {"internship": "Intern", "entry level": "Fresher", "associate": "Junior"}
_LEVER_SALARY_PER_MONTH = {"per-month-salary": 1.0, "per-year-salary": 1 / 12}


@dataclass(frozen=True)
class Board:
    ats: str  # greenhouse | lever | workable
    token: str
    company: str


# Công ty có văn phòng / tin ở Việt Nam (khảo sát 2026-10-21; xem README). Thêm công ty = thêm một dòng.
BOARDS: Tuple[Board, ...] = (
    Board("greenhouse", "navervietnam", "NAVER Vietnam"),
    Board("greenhouse", "axon", "Axon"),
    Board("greenhouse", "worldquant", "WorldQuant"),
    Board("greenhouse", "avepoint", "AvePoint"),
    Board("greenhouse", "joblogic", "Joblogic"),
    Board("greenhouse", "thoughtworks", "Thoughtworks"),
    Board("lever", "amanotes", "Amanotes"),
    Board("lever", "gradion", "Gradion"),
    Board("lever", "portcast", "Portcast"),
    Board("lever", "shopback-2", "ShopBack"),
    Board("lever", "ninjavan", "Ninja Van"),
    Board("lever", "keyloop", "Keyloop"),
    Board("workable", "optisigns-inc", "OptiSigns"),
)


def vn_city(*texts: Optional[str]) -> Optional[str]:
    """Các thành phố Việt Nam nhắc tới trong chuỗi địa điểm, viết thống nhất; chỉ có "Vietnam" -> "Việt Nam";
    không ở Việt Nam -> None."""
    joined = " | ".join(t for t in texts if t)
    cities = cities_in(joined)
    if not cities:
        return "Việt Nam" if _VN_RE.search(joined) else None
    return ", ".join(cities)[:LOCATION_MAX_LENGTH]


def _iso_date(value: Any) -> Optional[str]:
    if isinstance(value, (int, float)) and not isinstance(value, bool):  # Lever: mili giây epoch
        return datetime.fromtimestamp(value / 1000, tz=timezone.utc).date().isoformat()
    if isinstance(value, str) and len(value) >= 10:
        try:
            return datetime.fromisoformat(value[:10]).date().isoformat()
        except ValueError:
            return None
    return None


def _job(
    board: Board,
    url: str,
    title: str,
    company: Optional[str],
    location: Optional[str],
    published: Optional[str],
    texts: Sequence[Optional[str]],
    level: Optional[str] = None,
    salary: Tuple[Optional[float], Optional[float], Optional[str]] = (None, None, None),
) -> ScrapedJob:
    low, high, currency = salary
    vnd = (low, high) if currency == "VND" else (None, None)
    usd = (low, high) if currency == "USD" else (None, None)
    return ScrapedJob(
        source_id=compute_source_id(board.ats, url),
        external_source=board.ats,
        source_url=url,
        title=title,
        standardized_title=title,
        category=IT_CATEGORY,
        level=level or derive_web_level(title, None),
        company_name=company or board.company,
        published_date=published,
        min_salary_vnd=int(vnd[0]) if vnd[0] is not None else None,
        max_salary_vnd=int(vnd[1]) if vnd[1] is not None else None,
        min_salary_usd=round(usd[0], 2) if usd[0] is not None else None,
        max_salary_usd=round(usd[1], 2) if usd[1] is not None else None,
        is_salary_negotiable=low is None and high is None,
        location=location,
        skills=skills_from_text(title, *texts),
    )


# ---------------------------------------------------------------- adapters: JSON -> ScrapedJob (chỉ tin VN)


def parse_greenhouse(board: Board, data: Mapping[str, Any]) -> Iterator[Tuple[ScrapedJob, bool]]:
    for j in data.get("jobs") or []:
        offices = " | ".join(o.get("name") or "" for o in j.get("offices") or [] if isinstance(o, dict))
        loc_name = (j.get("location") or {}).get("name") or ""
        if not _VN_RE.search(f"{loc_name} | {offices}") or not j.get("title") or not j.get("absolute_url"):
            continue
        title = " ".join(j["title"].split())
        departments = " | ".join(d.get("name") or "" for d in j.get("departments") or [] if isinstance(d, dict))
        job = _job(
            board,
            j["absolute_url"],
            title,
            j.get("company_name"),
            vn_city(loc_name, offices),
            _iso_date(j.get("first_published") or j.get("updated_at")),
            [j.get("content")],
        )
        yield job, is_it_posting(title, departments)


def _lever_salary(value: Any) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    if not isinstance(value, dict):
        return None, None, None
    factor = _LEVER_SALARY_PER_MONTH.get(value.get("interval") or "")
    currency = (value.get("currency") or "").upper() or None
    low, high = value.get("min"), value.get("max")
    if factor is None or not isinstance(low, (int, float)) or not isinstance(high, (int, float)) or high <= 0:
        return None, None, currency
    low, high = sorted((max(low, 0) * factor, high * factor))
    return (low or None), high, currency


def parse_lever(board: Board, data: Sequence[Mapping[str, Any]]) -> Iterator[Tuple[ScrapedJob, bool]]:
    for j in data or []:
        cat = j.get("categories") or {}
        locs = [cat.get("location") or ""] + list(cat.get("allLocations") or [])
        if not (j.get("country") == "VN" or _VN_RE.search(" | ".join(locs))) or not j.get("text") or not j.get("hostedUrl"):
            continue
        lists = [f"{x.get('text', '')} {x.get('content', '')}" for x in j.get("lists") or [] if isinstance(x, dict)]
        title = " ".join(j["text"].split())
        job = _job(
            board,
            j["hostedUrl"],
            title,
            None,
            vn_city(*locs) or "Việt Nam",
            _iso_date(j.get("createdAt")),
            [j.get("descriptionPlain") or j.get("description"), *lists, j.get("additionalPlain") or j.get("additional")],
            salary=_lever_salary(j.get("salaryRange")),
        )
        yield job, is_it_posting(title, f"{cat.get('team') or ''} | {cat.get('department') or ''}")


def parse_workable(board: Board, data: Mapping[str, Any]) -> Iterator[Tuple[ScrapedJob, bool]]:
    for j in data.get("jobs") or []:
        locs = [f"{x.get('city', '')} {x.get('country', '')}" for x in j.get("locations") or [] if isinstance(x, dict)]
        locs.append(f"{j.get('city') or ''} {j.get('country') or ''}")
        if not _VN_RE.search(" | ".join(locs)) or not j.get("title") or not j.get("url"):
            continue
        title = " ".join(j["title"].split())
        job = _job(
            board,
            j["url"],
            title,
            data.get("name"),
            vn_city(*locs),
            _iso_date(j.get("published_on") or j.get("created_at")),
            [j.get("description")],
            level=_WORKABLE_LEVELS.get((j.get("experience") or "").strip().lower()),
        )
        yield job, is_it_posting(title, f"{j.get('function') or ''} | {j.get('department') or ''}")


def is_it_posting(title: str, department: str) -> bool:
    """IT theo tiêu đề hoặc phòng ban — KHÔNG theo kỹ năng trích từ mô tả, vì đoạn giới thiệu công ty
    lặp ở mọi tin (vd. AvePoint nhắc Azure trong cả tin Commission Specialist)."""
    if is_non_it_title(title):
        return False
    return is_it_title(title) or bool(_IT_DEPT_RE.search(department or ""))


ADAPTERS: Dict[str, Tuple[Callable[[Board], str], Callable[[Board, Any], Iterator[Tuple[ScrapedJob, bool]]]]] = {
    "greenhouse": (lambda b: f"https://boards-api.greenhouse.io/v1/boards/{b.token}/jobs?content=true", parse_greenhouse),
    "lever": (lambda b: f"https://api.lever.co/v0/postings/{b.token}?mode=json", parse_lever),
    "workable": (lambda b: f"https://apply.workable.com/api/v1/widget/accounts/{b.token}?details=true", parse_workable),
}


# ---------------------------------------------------------------- crawl


def crawl_boards(
    client: PoliteClient,
    boards: Sequence[Board] = BOARDS,
    state: Optional[CrawlState] = None,
    stats: Optional[Dict[str, int]] = None,
) -> Iterator[ScrapedJob]:
    """Tin IT ở Việt Nam, chưa có trong `state`. Bảng tin lỗi/404/JSON hỏng -> bỏ qua bảng đó, chạy tiếp."""
    stats = stats if stats is not None else {}
    for key in ("boards_fetched", "boards_failed", "vn_jobs", "skipped_seen", "non_it", "kept"):
        stats.setdefault(key, 0)
    blocked_ats = set()
    for board in boards:
        api_url, parse = ADAPTERS[board.ats]
        if board.ats in blocked_ats:
            stats["boards_failed"] += 1
            continue
        try:
            resp = client.get(api_url(board))
        except BlockedError as e:  # host ATS chặn bot: bỏ mọi bảng tin trên host đó, không vượt chặn
            blocked_ats.add(board.ats)
            stats["boards_failed"] += 1
            logger.warning("%s; bỏ qua mọi bảng tin %s", e, board.ats)
            continue
        except DisallowedError:
            stats["boards_failed"] += 1
            logger.warning("robots.txt cấm %s; bỏ qua %s", api_url(board), board.token)
            continue
        if resp.status_code != 200:
            stats["boards_failed"] += 1
            logger.warning("Bỏ qua bảng tin %s/%s (%s)", board.ats, board.token, resp.status_code)
            continue
        try:
            data = resp.json()
        except ValueError:
            stats["boards_failed"] += 1
            logger.warning("JSON hỏng từ %s/%s", board.ats, board.token)
            continue
        stats["boards_fetched"] += 1
        for job, it in parse(board, data):
            stats["vn_jobs"] += 1
            entry = SitemapEntry(job.source_url, None)
            if state is not None and state.is_fresh(entry):
                stats["skipped_seen"] += 1
                continue
            if state is not None:
                state.mark(entry)
            if not it:
                stats["non_it"] += 1
                continue
            stats["kept"] += 1
            yield job


def boards_from(names: Optional[List[str]]) -> Sequence[Board]:
    return BOARDS if not names else tuple(b for b in BOARDS if b.token in names)
