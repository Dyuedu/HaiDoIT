"""
Bộ cào tin tuyển dụng IT từ job board Việt Nam (ITviec, TopDev).

Cách lấy: robots.txt -> sitemap -> trang chi tiết -> khối JSON-LD schema.org `JobPosting`
(dữ liệu có cấu trúc trang tự công bố cho máy tìm kiếm). Không phụ thuộc DOM, không chạy JavaScript.

Chỉ đọc + biến đổi + ghi JSONL vào `data/scraped/` (đã .gitignore); ghi Postgres/Neo4j thuộc Story 7.4.
Chỉ giữ dữ kiện (tiêu đề, công ty, kỹ năng, lương, địa điểm, level, ngày đăng); `description`,
`jobBenefits`, địa chỉ chi tiết và mọi văn bản JD không bao giờ rời khỏi module này (AD-7 / AR-6).

Nguồn không hỗ trợ và lý do: xem `scraper/README.md`.

Chạy (từ thư mục gốc repo):
    python -m scraper.jobboards --source itviec --limit 20
    python -m scraper.jobboards --source topdev --limit 50 --contact you@example.com
"""
import argparse
import hashlib
import json
import logging
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from html import unescape
from urllib.parse import urljoin
from pathlib import Path
from typing import Any, Dict, Iterator, List, Mapping, Optional, Sequence, Tuple

from pydantic import BaseModel, ConfigDict, Field

from scraper.normalizer import normalizer
from scraper.normalizer import NormalizedSkill
from scraper.skills_text import skills_from_text
from scraper.polite_http import (
    BlockedError,
    DisallowedError,
    PoliteClient,
    ScrapeError,
    build_user_agent,
)

logger = logging.getLogger("skillnexus.scraper")

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "data" / "scraped"
DEFAULT_LIMIT = 50
IT_CATEGORY = "it"
LOCATION_MAX_LENGTH = 100  # job_postings.location VARCHAR(100)
MAX_BARREN_SITEMAPS = 3
ATS_SOURCE = "ats"

_SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
_JSONLD_RE = re.compile(
    r"<script[^>]*type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>", re.IGNORECASE | re.DOTALL
)
# Next.js App Router nhúng dữ liệu trang dưới dạng chuỗi JS trong `self.__next_f.push([1, "..."])`
_NEXT_F_RE = re.compile(r'self\.__next_f\.push\(\[1,\s*("(?:[^"\\]|\\.)*")\]\)')
_NOT_AVAILABLE = {"", "not available", "n/a"}
# Vai trò IT trong tiêu đề (lọc tin TopDev); cố ý không có "kỹ sư"/"engineer" đơn lẻ (kỹ sư xây dựng, QS...)
# "intern" as a token or "internship", not a prefix of internal/international.
_INTERN_RE = re.compile(r"thực tập|(?<![a-z])intern(?:ship)?(?![a-z])", re.IGNORECASE)
_IT_TITLE_RE = re.compile(
    r"(?<![a-z])("
    r"developer|programmer|dev|software|devops|devsecops|sre|tester|automation test|test engineer|ui|ux"
    r"|(qa|qc)[ /]*(engineer|tester|automation|manual)"  # QC đơn lẻ thường là QC sản xuất
    r"|front[- ]?end|back[- ]?end|full[- ]?stack|ios|android|web|game"
    r"|data (engineer|analyst|scientist)|machine learning|ml|ai|llm|computer vision|nlp"
    r"|cloud|(information|cyber|application|network) security|security engineer|pentest"
    r"|network engineer|system admin|sysadmin|it|ict|rpa|erp|sap|blockchain|embedded"
    r"|ui/ux|ux/ui|product owner|scrum master|business analyst|business intelligence|solution architect"
    r"|database|dba"
    r")(?![a-z])"
    r"|lập trình|phần mềm|kiểm thử|an ninh mạng|quản trị (hệ thống|mạng|cơ sở dữ liệu)|công nghệ thông tin"
    r"|phân tích nghiệp vụ",
    re.IGNORECASE,
)
# Vai trò KHÔNG phải IT dù tiêu đề/phòng ban có từ khoá IT ("2D UI Artist", "AI Video Editor", "Game Designer"
# ở phòng Product/Tech...). Thắng mọi tín hiệu IT khác.
_NON_IT_TITLE_RE = re.compile(
    r"(?<![a-z])("
    r"artist|art director|motion|video editor|creative|multimedia|game designer|copywriter|content creator"
    r"|marketing|sales|account executive|account manager|business development|customer success"
    r"|recruiter|recruitment|talent|human resources|hr|legal|accountant|revenue|commission"
    r"|financial analyst|finance (manager|specialist|executive|officer|director)"  # "Embedded Finance (PO)" vẫn là IT
    r")(?![a-z])"
    r"|kế toán|tuyển dụng|nhân sự|kinh doanh",
    re.IGNORECASE,
)
# Tên thành phố (Anh / không dấu / có dấu) -> cách viết thống nhất giữa các nguồn
_CITY_RULES: Tuple[Tuple[re.Pattern, str], ...] = (
    (re.compile(r"ho chi minh|hcmc|saigon|hồ chí minh", re.I), "Hồ Chí Minh"),
    (re.compile(r"ha ?noi|hà nội", re.I), "Hà Nội"),
    (re.compile(r"da ?nang|đà nẵng", re.I), "Đà Nẵng"),
    (re.compile(r"can tho|cần thơ", re.I), "Cần Thơ"),
    (re.compile(r"hai phong|hải phòng", re.I), "Hải Phòng"),
)


def cities_in(text: str) -> List[str]:
    """Các thành phố Việt Nam nhắc tới trong chuỗi, viết thống nhất, theo thứ tự `_CITY_RULES`."""
    return [canonical for pattern, canonical in _CITY_RULES if pattern.search(text or "")]


def normalize_city(name: str) -> str:
    """"Ha Noi" / "Hanoi" / "Hà Nội" -> "Hà Nội"; tên không nhận ra giữ nguyên."""
    for pattern, canonical in _CITY_RULES:
        if pattern.search(name):
            return canonical
    return name


# Lọc thô theo slug URL TRƯỚC khi tải trang (nguồn có tỉ lệ IT thấp): cố ý rộng tay — giữ nhầm thì bộ lọc
# sau khi tải loại tiếp, bỏ sót thì mất tin. Đo trên 60 slug TopDev: giữ 19, không sót tin IT nào.
_IT_SLUG_TOKENS = (
    "developer|developers|dev|programmer|software|devops|devsecops|sre|tester|testing|test|automation"
    "|qa|qc|frontend|front-end|backend|back-end|fullstack|full-stack|ios|android|mobile|web|website|game|unity"
    "|data|du-lieu|ai|ml|machine-learning|llm|nlp|computer-vision|cloud|security|bao-mat|an-ninh-mang|cyber"
    "|network|ha-tang|he-thong|system|it|ict|cntt|rpa|erp|sap|crm|blockchain|embedded|nhung|iot|firmware"
    "|ui|ux|designer|product-owner|product-manager|scrum|business-analyst|ba|phan-tich-nghiep-vu|architect"
    "|database|dba|lap-trinh|phan-mem|kiem-thu|cong-nghe|cong-nghe-thong-tin|ung-dung|digital|so-hoa"
    "|analytics|analyst|bi|business-intelligence|helpdesk|it-support|telecom|vien-thong"
    "|java|python|php|net|dotnet|golang|go|react|reactjs|nodejs|node|angular|vue|flutter|kotlin|swift"
    "|c|cpp|c-c|ruby|rust|scala|odoo|salesforce|magento|wordpress|shopify|k8s|kubernetes|linux|engineer|ky-su"
)
_IT_SLUG_RE = re.compile(r"(?:^|-)(?:" + _IT_SLUG_TOKENS + r")(?:-|$)")


def it_slug(url: str) -> bool:
    """Slug (đoạn cuối URL, bỏ id số) có từ khoá IT."""
    slug = url.rstrip("/").rsplit("/", 1)[-1].lower()
    return bool(_IT_SLUG_RE.search(re.sub(r"-\d+$", "", slug)))
# Level từ tiêu đề khi trang không công bố số tháng kinh nghiệm
_TITLE_LEVEL_RULES: Tuple[Tuple[re.Pattern, str], ...] = (
    (re.compile(r"(?<![a-z])(senior|sr\.?|lead|principal|staff|architect|manager)(?![a-z])", re.I), "Senior"),
    (re.compile(r"(?<![a-z])(middle|mid-level|mid)(?![a-z])", re.I), "Middle"),
    (re.compile(r"(?<![a-z])(junior|jr\.?)(?![a-z])", re.I), "Junior"),
    (re.compile(r"(?<![a-z])fresher(?![a-z])", re.I), "Fresher"),
)


# ---------------------------------------------------------------- sources


@dataclass(frozen=True)
class Source:
    name: str
    home: str
    # sitemap con được đi vào (khớp với `loc` trong sitemapindex)
    child_sitemap_re: re.Pattern
    # URL trang chi tiết job
    job_url_re: re.Pattern
    # True: trang trộn cả job không phải IT -> lọc thô theo slug trước khi tải, rồi `is_it_job` sau khi tải
    needs_it_filter: bool
    # Trang không có sitemap tin (trang tuyển dụng công ty): lấy link tin từ các trang danh sách này
    listing_urls: Tuple[str, ...] = ()


SOURCES: Dict[str, Source] = {
    "itviec": Source(
        name="itviec",
        home="https://itviec.com/",
        child_sitemap_re=re.compile(r"/twinnings_jobs_desc_vn\.xml$"),
        job_url_re=re.compile(r"^https://itviec\.com/viec-lam-it/[^/?#]+$"),
        needs_it_filter=False,
    ),
    "topdev": Source(
        name="topdev",
        home="https://topdev.vn/",
        child_sitemap_re=re.compile(r"/(sitemap-jobs\.xml|sitemap/jobs_desc_vi_page_\d+\.xml)$"),
        # sitemap tiếng Việt dùng /viec-lam/, bản tiếng Anh /detail-jobs/ (cùng một tin)
        job_url_re=re.compile(r"^https://topdev\.vn/(viec-lam|detail-jobs)/[^/?#]+-\d+$"),
        needs_it_filter=True,
    ),
    # Trang tuyển dụng công ty có JSON-LD JobPosting nhưng không có sitemap tin (khảo sát 2026-10-21)
    "coccoc": Source(
        name="coccoc",
        home="https://careers.coccoc.com/",
        child_sitemap_re=re.compile(r"(?!)"),
        job_url_re=re.compile(r"^https://careers\.coccoc\.com/jobs/[a-z0-9-]+$"),
        needs_it_filter=True,
        listing_urls=("https://careers.coccoc.com/", "https://careers.coccoc.com/jobs"),
    ),
}


# ---------------------------------------------------------------- model


class ScrapedJob(BaseModel):
    """Bản ghi tin đã làm sạch. Không có trường văn bản tự do (AD-7)."""

    model_config = ConfigDict(frozen=True)

    source_id: str = Field(..., description="SHA-256 ổn định của định danh nguồn")
    external_source: str
    title: str
    standardized_title: str
    category: str
    level: str = Field(..., description="Intern | Fresher | Junior | Middle | Senior | Unknown")
    company_name: Optional[str] = None
    published_date: Optional[str] = None
    min_salary_vnd: Optional[int] = None
    max_salary_vnd: Optional[int] = None
    is_salary_negotiable: bool
    location: Optional[str] = None
    skills: List[NormalizedSkill] = Field(default_factory=list)
    source_url: str
    min_salary_usd: Optional[float] = None
    max_salary_usd: Optional[float] = None
    valid_through: Optional[str] = None
    months_of_experience: Optional[int] = None
    scraped_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"))


# ---------------------------------------------------------------- sitemap


@dataclass(frozen=True)
class SitemapEntry:
    loc: str
    lastmod: Optional[str]


def parse_sitemap(xml_text: str) -> Tuple[bool, List[SitemapEntry]]:
    """-> (là sitemapindex?, các mục). XML hỏng -> (False, [])."""
    try:
        root = ET.fromstring(xml_text.encode("utf-8") if isinstance(xml_text, str) else xml_text)
    except ET.ParseError:
        return False, []
    is_index = root.tag == f"{_SITEMAP_NS}sitemapindex"
    entries = []
    for node in root:
        loc = (node.findtext(f"{_SITEMAP_NS}loc") or "").strip()
        if loc:
            lastmod = (node.findtext(f"{_SITEMAP_NS}lastmod") or "").strip() or None
            entries.append(SitemapEntry(loc, lastmod))
    return is_index, entries


def iter_job_urls(client: PoliteClient, source: Source) -> Iterator[SitemapEntry]:
    """URL trang chi tiết job, đi lười qua cây sitemap bắt đầu từ `Sitemap:` trong robots.txt
    (hoặc qua link trong `source.listing_urls` nếu nguồn không có sitemap tin)."""
    if source.listing_urls:
        yield from _iter_listing_links(client, source)
        return
    queue = client.sitemaps(source.home)
    if not queue:
        raise ScrapeError(f"robots.txt của {source.home} không khai báo Sitemap")
    seen_sitemaps = set()
    seen_jobs = set()
    barren = 0  # số sitemap job liên tiếp có URL nhưng không URL nào khớp `job_url_re`
    while queue:
        url = queue.pop(0)
        if url in seen_sitemaps:
            continue
        seen_sitemaps.add(url)
        resp = client.get(url)
        if resp.status_code != 200:
            logger.warning("Bỏ qua sitemap %s (%s)", url, resp.status_code)
            continue
        is_index, entries = parse_sitemap(resp.text)
        if is_index:
            queue.extend(e.loc for e in entries if source.child_sitemap_re.search(e.loc))
            continue
        matched = [e for e in entries if source.job_url_re.match(e.loc)]
        if entries and not matched:
            barren += 1
            if barren >= MAX_BARREN_SITEMAPS:
                raise ScrapeError(
                    f"{barren} sitemap liên tiếp của {source.name} không có URL nào khớp mẫu tin "
                    f"(ví dụ {entries[0].loc}); cấu trúc trang có thể đã đổi"
                )
            continue
        barren = 0
        for e in matched:
            if e.loc not in seen_jobs:
                seen_jobs.add(e.loc)
                yield e


_HREF_RE = re.compile(r"""href=["']([^"'#]+)["']""", re.IGNORECASE)


def _iter_listing_links(client: PoliteClient, source: Source) -> Iterator[SitemapEntry]:
    seen = set()
    for page in source.listing_urls:
        resp = client.get(page)
        if resp.status_code != 200:
            logger.warning("Bỏ qua trang danh sách %s (%s)", page, resp.status_code)
            continue
        for href in _HREF_RE.findall(resp.text):
            url = urljoin(str(resp.url), unescape(href)).split("?", 1)[0].rstrip("/")
            if source.job_url_re.match(url) and url not in seen:
                seen.add(url)
                yield SitemapEntry(url, None)


# ---------------------------------------------------------------- JSON-LD -> ScrapedJob


def _text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(unicodedata.normalize("NFC", unescape(value)).split())


def extract_job_posting(html: str) -> Optional[Dict[str, Any]]:
    """Khối JSON-LD `@type: JobPosting` đầu tiên trong trang (kể cả trong list / `@graph`)."""
    for m in _JSONLD_RE.finditer(html):
        try:
            data = json.loads(m.group(1).strip())
        except ValueError:
            continue
        stack = [data]
        while stack:
            item = stack.pop(0)
            if isinstance(item, list):
                stack.extend(item)
            elif isinstance(item, dict):
                types = item.get("@type")
                types = types if isinstance(types, list) else [types]
                if "JobPosting" in types:
                    return item
                if "@graph" in item:
                    stack.append(item["@graph"])
    return _rsc_job_posting(html)


def _rsc_rows(html: str) -> Iterator[Any]:
    """Payload Next.js App Router: nối các chuỗi trong `self.__next_f.push([1, "..."])` rồi tách thành dòng
    `ID:JSON` (cách đọc giống njsparser). Dòng không phải JSON (module `I`, văn bản `T`...) bị bỏ qua."""
    chunks = []
    for m in _NEXT_F_RE.finditer(html):
        try:
            chunks.append(json.loads(m.group(1)))
        except ValueError:
            continue
    for line in "".join(c for c in chunks if isinstance(c, str)).split("\n"):
        _, sep, body = line.partition(":")
        if not sep:
            continue
        try:
            yield json.loads(body)
        except ValueError:
            continue


def _rsc_job_posting(html: str) -> Optional[Dict[str, Any]]:
    """Trang Next.js không có JSON-LD: object đầu tiên có `jobTitle` trong payload RSC -> dạng JobPosting.
    Lương chỉ lấy khi payload ghi rõ tiền tệ (không đoán VND/USD)."""
    if "self.__next_f" not in html:
        return None
    for row in _rsc_rows(html):
        stack = [row]
        while stack:
            item = stack.pop(0)
            if isinstance(item, list):
                stack.extend(item)
            elif isinstance(item, dict):
                if isinstance(item.get("jobTitle"), str):
                    return _rsc_to_posting(item)
                stack.extend(item.values())
    return None


def _rsc_to_posting(raw: Mapping[str, Any]) -> Dict[str, Any]:
    currency = raw.get("salaryCurrency") or raw.get("currency")
    sal_min, sal_max = raw.get("salaryMin"), raw.get("salaryMax")
    base_salary = None
    if isinstance(currency, str) and (sal_min is not None or sal_max is not None):
        base_salary = {"currency": currency, "value": {"minValue": sal_min, "maxValue": sal_max, "unitText": "MONTH"}}
    city = next((raw.get(k) for k in ("city", "location") if isinstance(raw.get(k), str)), None)
    return {
        "@type": "JobPosting",
        "title": raw["jobTitle"],
        "hiringOrganization": {"name": raw.get("companyName")},
        "datePosted": raw.get("createdOn") or raw.get("approvedOn"),
        "validThrough": raw.get("expiredOn"),
        "baseSalary": base_salary,
        "jobLocation": {"address": {"addressLocality": city}} if city else None,
        "description": raw.get("jobDescription") or "",
        "skills": raw.get("skills") or [],
    }


def parse_skills(value: Any) -> List[str]:
    """`skills` là chuỗi "A, B, C" hoặc list chuỗi."""
    items = value if isinstance(value, list) else re.split(r"[,;\n]", value) if isinstance(value, str) else []
    out, seen = [], set()
    for raw in items:
        s = _text(raw) if isinstance(raw, str) else _text(raw.get("name")) if isinstance(raw, dict) else ""
        if s and s.lower() not in seen:
            seen.add(s.lower())
            out.append(s)
    return out


def _amount(value: Any) -> Optional[Decimal]:
    if isinstance(value, bool) or value is None:
        return None
    try:
        amount = Decimal(str(value).replace(",", "").strip())
    except InvalidOperation:
        return None
    return amount if amount > 0 else None


def parse_base_salary(value: Any) -> Tuple[Optional[Decimal], Optional[Decimal], Optional[str]]:
    """schema.org `baseSalary` -> (min, max, currency) theo THÁNG.
    Không công bố / "Negotiable" / đơn vị không quy được về tháng -> (None, None, currency)."""
    if not isinstance(value, dict):
        return None, None, None
    currency = _text(value.get("currency")).upper() or None
    qv = value.get("value")
    if isinstance(qv, dict):
        low, high = _amount(qv.get("minValue")), _amount(qv.get("maxValue"))
        if low is None and high is None:
            low = high = _amount(qv.get("value"))
        unit = _text(qv.get("unitText")).upper()
    else:
        low = high = _amount(qv)
        unit = ""
    per_month = {"": Decimal(1), "MONTH": Decimal(1), "YEAR": Decimal(1) / 12}.get(unit)
    if per_month is None or (low is None and high is None):
        return None, None, currency
    low = low * per_month if low is not None else None
    high = high * per_month if high is not None else None
    if low is not None and high is not None and low > high:
        low, high = high, low
    return low, high, currency


def parse_location(value: Any) -> Optional[str]:
    """Tỉnh/thành từ `jobLocation` (một hoặc nhiều Place). Không giữ địa chỉ chi tiết."""
    places = value if isinstance(value, list) else [value]
    regions: List[str] = []
    for place in places:
        address = place.get("address") if isinstance(place, dict) else None
        if not isinstance(address, dict):
            continue
        for key in ("addressRegion", "addressLocality"):
            region = normalize_city(_text(address.get(key)))
            if region.lower() not in _NOT_AVAILABLE:
                if region not in regions:
                    regions.append(region)
                break
    joined = ", ".join(regions)
    return joined[:LOCATION_MAX_LENGTH].rstrip(", ") or None


def _months_of_experience(value: Any) -> Optional[int]:
    if isinstance(value, dict):
        value = value.get("monthsOfExperience")
    if isinstance(value, bool):
        return None
    try:
        months = int(float(value))
    except (TypeError, ValueError):
        return None
    return months if months >= 0 else None


def derive_web_level(title: str, months: Optional[int]) -> str:
    """Thực tập theo tiêu đề; rồi theo số tháng kinh nghiệm; thiếu số tháng -> suy từ tiêu đề."""
    if _INTERN_RE.search(_text(title)):
        return "Intern"
    if months is not None:
        if months < 12:
            return "Fresher"
        if months < 36:
            return "Junior"
        if months < 60:
            return "Middle"
        return "Senior"
    for pattern, title_level in _TITLE_LEVEL_RULES:
        if pattern.search(title):
            return title_level
    return "Unknown"


def _iso_date(value: Any) -> Optional[str]:
    text = _text(value)
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10]).isoformat()
    except ValueError:
        return None


def compute_source_id(source: str, url: str) -> str:
    return hashlib.sha256(f"{source}\x1f{url}".encode("utf-8")).hexdigest()


def transform_posting(source: Source, url: str, posting: Mapping[str, Any]) -> Optional[ScrapedJob]:
    """JSON-LD JobPosting -> ScrapedJob. Chỉ đọc title, hiringOrganization.name, skills, baseSalary,
    jobLocation (tỉnh/thành), experienceRequirements, datePosted, validThrough.
    Thiếu tiêu đề -> None."""
    title = _text(posting.get("title"))
    if not title:
        return None
    org = posting.get("hiringOrganization")
    company = _text(org.get("name")) if isinstance(org, dict) else _text(org)
    listed = parse_skills(posting.get("skills"))
    if listed:
        skills, _ = normalizer.normalize_batch(listed)
    else:  # không có trường skills: trích từ mô tả rồi bỏ văn bản (AD-7)
        skills = skills_from_text(
            title, *(posting.get(k) for k in ("description", "qualifications", "responsibilities", "skills"))
        )
    low, high, currency = parse_base_salary(posting.get("baseSalary"))
    vnd = (low, high) if currency == "VND" else (None, None)
    usd = (low, high) if currency == "USD" else (None, None)
    months = _months_of_experience(posting.get("experienceRequirements"))
    return ScrapedJob(
        source_id=compute_source_id(source.name, url),
        external_source=source.name,
        source_url=url,
        title=title,
        standardized_title=title,
        category=IT_CATEGORY,
        level=derive_web_level(title, months),
        company_name=company or None,
        published_date=_iso_date(posting.get("datePosted")),
        valid_through=_iso_date(posting.get("validThrough")),
        min_salary_vnd=int(vnd[0]) if vnd[0] is not None else None,
        max_salary_vnd=int(vnd[1]) if vnd[1] is not None else None,
        min_salary_usd=float(round(usd[0], 2)) if usd[0] is not None else None,
        max_salary_usd=float(round(usd[1], 2)) if usd[1] is not None else None,
        is_salary_negotiable=low is None and high is None,
        location=parse_location(posting.get("jobLocation")),
        months_of_experience=months,
        skills=skills,
    )


def is_non_it_title(text: str) -> bool:
    return bool(_NON_IT_TITLE_RE.search(text or ""))


def is_it_title(text: str) -> bool:
    return not is_non_it_title(text) and bool(_IT_TITLE_RE.search(text or ""))


def is_it_posting_jsonld(job: ScrapedJob, posting: Mapping[str, Any]) -> bool:
    """Có trường `skills` -> `is_it_job`. Không có (kỹ năng trích từ mô tả, dễ dính đoạn giới thiệu công ty)
    -> chỉ tin tiêu đề / `occupationalCategory`."""
    if parse_skills(posting.get("skills")):
        return is_it_job(job)
    return is_it_title(f"{job.title} | {_text(posting.get('occupationalCategory'))}")


def is_it_job(job: ScrapedJob) -> bool:
    """Có kỹ năng khớp taxonomy, hoặc tiêu đề là vai trò IT (taxonomy còn nhỏ nên không đủ một mình:
    "RPA Developer" với kỹ năng ERP/SAP/RPA không khớp kỹ năng nào)."""
    if is_non_it_title(job.title):
        return False
    return any(s.matched for s in job.skills) or is_it_title(job.title)


# ---------------------------------------------------------------- crawl


class CrawlState:
    """URL đã cào (kèm `lastmod` lúc cào) -> chạy lại chỉ lấy tin mới. Lưu cạnh file JSONL.
    Không so `lastmod`: ITviec/TopDev ghi giờ sinh sitemap cho mọi URL, nên nó đổi ở mỗi lần sinh
    dù tin không đổi. URL chứa id tin; muốn tải lại thì dùng `--refresh`."""

    def __init__(self, path: Path):
        self.path = path
        try:
            self.lastmod: Dict[str, Optional[str]] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self.lastmod = {}

    def is_fresh(self, entry: SitemapEntry) -> bool:
        return entry.loc in self.lastmod

    def mark(self, entry: SitemapEntry) -> None:
        self.lastmod[entry.loc] = entry.lastmod

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_name(self.path.name + ".part")
        tmp.write_text(json.dumps(self.lastmod, ensure_ascii=False, indent=0), encoding="utf-8")
        tmp.replace(self.path)


def crawl(
    client: PoliteClient,
    source: Source,
    limit: int = DEFAULT_LIMIT,
    state: Optional[CrawlState] = None,
    stats: Optional[Dict[str, int]] = None,
) -> Iterator[ScrapedJob]:
    """Tối đa `limit` trang chi tiết được tải (không tính sitemap). `BlockedError` lan ra ngoài:
    nguồn chặn bot thì dừng hẳn."""
    stats = stats if stats is not None else {}
    for key in ("pages_fetched", "skipped_seen", "skipped_slug", "skipped_disallowed", "no_jsonld", "non_it", "kept"):
        stats.setdefault(key, 0)
    for entry in iter_job_urls(client, source):
        if stats["pages_fetched"] >= limit:
            break
        if state is not None and state.is_fresh(entry):
            stats["skipped_seen"] += 1
            continue
        if source.needs_it_filter and not it_slug(entry.loc):
            stats["skipped_slug"] += 1
            continue
        try:
            resp = client.get(entry.loc)
        except DisallowedError:
            stats["skipped_disallowed"] += 1
            continue
        stats["pages_fetched"] += 1
        if resp.status_code != 200:
            logger.warning("Bỏ qua %s (%s)", entry.loc, resp.status_code)
            continue
        posting = extract_job_posting(resp.text)
        job = transform_posting(source, entry.loc, posting) if posting else None
        if state is not None:
            state.mark(entry)
        if job is None:
            stats["no_jsonld"] += 1
            continue
        if source.needs_it_filter and not is_it_posting_jsonld(job, posting):
            stats["non_it"] += 1
            continue
        stats["kept"] += 1
        yield job


def write_jsonl(jobs: Iterator[ScrapedJob], path: Path) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with open(path, "a", encoding="utf-8") as f:
        for job in jobs:
            f.write(job.model_dump_json() + "\n")
            f.flush()
            n += 1
    return n


# ---------------------------------------------------------------- CLI


def _load_normalizer() -> None:
    normalizer.load_from_file()


def main(argv: Optional[Sequence[str]] = None) -> int:
    for stream in (sys.stdout, sys.stderr):  # console Windows (cp125x) không in được tiếng Việt
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    parser = argparse.ArgumentParser(
        prog="python -m scraper.jobboards",
        description="Cào tin IT từ job board (sitemap + JSON-LD), ghi JSONL; chưa ghi DB (Story 7.4).",
    )
    parser.add_argument(
        "--source",
        action="append",
        choices=sorted(SOURCES) + [ATS_SOURCE, "all"],
        required=True,
        help=f"nguồn (lặp được); '{ATS_SOURCE}' = API công khai Greenhouse/Lever/Workable; 'all' = mọi nguồn",
    )
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="số trang chi tiết tối đa mỗi nguồn mỗi lần chạy")
    parser.add_argument(
        "--out", type=Path, default=None, help="file JSONL khi chạy một nguồn (mặc định data/scraped/<source>.jsonl)"
    )
    parser.add_argument("--contact", default=None, help="email/URL liên hệ đưa vào User-Agent")
    parser.add_argument("--min-delay", type=float, default=3.0, help="giây tối thiểu giữa hai request cùng host")
    parser.add_argument("--refresh", action="store_true", help="bỏ qua state, tải lại cả tin chưa đổi")
    args = parser.parse_args(argv)

    names = sorted(SOURCES) + [ATS_SOURCE] if "all" in args.source else list(dict.fromkeys(args.source))
    if args.limit < 1 or args.min_delay < 1.0:
        print("LỖI: --limit phải >= 1 và --min-delay phải >= 1 giây", file=sys.stderr)
        return 2
    if args.out is not None and len(names) > 1:
        print("LỖI: --out chỉ dùng được khi chạy một nguồn", file=sys.stderr)
        return 2

    _load_normalizer()
    code = 0
    with PoliteClient(build_user_agent(args.contact), min_delay_s=args.min_delay) as client:
        for name in names:  # nguồn lỗi/bị chặn không làm dừng nguồn khác
            out = args.out or DEFAULT_OUT_DIR / f"{name}.jsonl"
            code = max(code, run_source(client, name, out, args.limit, args.refresh))
    return code


def run_source(client: PoliteClient, name: str, out: Path, limit: int, refresh: bool) -> int:
    state = CrawlState(out.with_suffix(".state.json"))
    if refresh:
        state.lastmod = {}
    stats: Dict[str, int] = {}
    code = 0
    try:
        if name == ATS_SOURCE:  # một request mỗi bảng tin, `limit` không áp dụng
            from scraper.ats import crawl_boards

            jobs = crawl_boards(client, state=state, stats=stats)
        else:
            jobs = crawl(client, SOURCES[name], limit, state, stats)
        written = write_jsonl(jobs, out)
    except BlockedError as e:
        print(f"DỪNG {name}: {e}. Không cố vượt chặn; xem scraper/README.md.", file=sys.stderr)
        written, code = stats.get("kept", 0), 3
    except ScrapeError as e:
        print(f"LỖI {name}: {e}", file=sys.stderr)
        written, code = stats.get("kept", 0), 1
    finally:
        state.save()

    print(f"=== {name}: {written} tin IT -> {out}")
    for key, value in stats.items():
        print(f"  {key:<20}: {value}")
    return code


if __name__ == "__main__":
    sys.exit(main())
