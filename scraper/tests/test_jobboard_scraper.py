"""
Bộ cào job board (ITviec, TopDev): sitemap -> JSON-LD JobPosting -> ScrapedJob.
Toàn bộ HTTP đi qua `httpx.MockTransport` (không gọi mạng); HTML là bản tối giản tự tạo theo đúng
cấu trúc JSON-LD đã khảo sát trên trang thật. Normalizer ở chế độ từ điển dự phòng.
"""
import json
from typing import Callable, Dict, List, Optional, Union

import httpx
import pytest

from scraper.normalizer import SkillTaxonomyNormalizer
from scraper import jobboards as jb
from scraper.polite_http import (
    BlockedError,
    DisallowedError,
    PoliteClient,
    ScrapeError,
    build_user_agent,
)

FREE_TEXT_KEYS = ("description", "jobBenefits", "streetAddress", "qualifications", "responsibilities")


@pytest.fixture(autouse=True)
def fallback_normalizer():
    SkillTaxonomyNormalizer.use_fallback()
    yield
    SkillTaxonomyNormalizer.use_fallback()


# ---------------------------------------------------------------- fake site helpers

Handler = Union[str, httpx.Response, Callable[[httpx.Request], httpx.Response]]


class FakeSite:
    def __init__(self, routes: Dict[str, Handler]):
        self.routes = routes
        self.requests: List[str] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        self.requests.append(url)
        handler = self.routes.get(url)
        if handler is None:
            return httpx.Response(404, text="not found")
        if callable(handler):
            return handler(request)
        if isinstance(handler, httpx.Response):
            return handler
        return httpx.Response(200, text=handler)


def make_client(site: FakeSite, sleeps: Optional[List[float]] = None) -> PoliteClient:
    sleeps = sleeps if sleeps is not None else []
    return PoliteClient(
        build_user_agent("test@example.com"),
        min_delay_s=0,
        jitter_s=0,
        transport=httpx.MockTransport(site),
        sleep=sleeps.append,
    )


def sitemap_index(*locs: str) -> str:
    body = "".join(f"<sitemap><loc>{u}</loc><lastmod>2026-10-21T22:00:00+07:00</lastmod></sitemap>" for u in locs)
    return f'<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</sitemapindex>'


def urlset(*locs: str) -> str:
    body = "".join(f"<url><loc>{u}</loc><lastmod>2026-10-21T22:00:00+07:00</lastmod></url>" for u in locs)
    return f'<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>'


def job_page(posting: dict, extra_blocks: tuple = ()) -> str:
    blocks = [*extra_blocks, posting]
    scripts = "".join(
        f'<script type="application/ld+json">{json.dumps(b, ensure_ascii=False)}</script>' for b in blocks
    )
    return f"<html><head>{scripts}</head><body><h1>{posting.get('title', '')}</h1></body></html>"


ITVIEC_POSTING = {
    "@context": "http://schema.org",
    "@type": "JobPosting",
    "industry": "Information Technology",
    "title": "Backend Developer (Java, Spring Boot)",
    "datePosted": "2026-10-01",
    "validThrough": "2026-11-01",
    "skills": "Java, Spring, MySQL, Docker",
    "description": "TOAN VAN JD KHONG DUOC LUU",
    "jobBenefits": "<p>PHUC LOI KHONG DUOC LUU</p>",
    "hiringOrganization": {"@type": "Organization", "name": "Công ty Mẫu", "logo": "https://x/logo.png"},
    "jobLocation": [
        {
            "@type": "Place",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "SO 1 DUONG KHONG DUOC LUU",
                "addressLocality": "Not Available",
                "addressRegion": "Hà Nội",
            },
        }
    ],
    "baseSalary": {
        "@type": "MonetaryAmount",
        "currency": "USD",
        "value": {"@type": "QuantitativeValue", "minValue": 1000, "maxValue": 2000, "unitText": "MONTH"},
    },
    "experienceRequirements": {"@type": "OccupationalExperienceRequirements", "monthsOfExperience": 24},
}

TOPDEV_IT_POSTING = {
    "@context": "http://schema.org",
    "@type": "JobPosting",
    "title": "Fresher ReactJS Developer",
    "datePosted": "2026-10-20T08:00:00+07:00",
    "skills": "ReactJS, JavaScript",
    "baseSalary": {
        "@type": "MonetaryAmount",
        "currency": "VND",
        "value": {"@type": "QuantitativeValue", "minValue": 8000000, "maxValue": 12000000, "unitText": "MONTH"},
    },
    "hiringOrganization": {"@type": "Organization", "name": "Công ty Phần mềm"},
    "jobLocation": {"@type": "Place", "address": {"addressRegion": "Hồ Chí Minh"}},
}

TOPDEV_NON_IT_POSTING = {
    "@type": "JobPosting",
    "industry": "Information Technology",  # TopDev gắn nhãn này cho cả tin không phải IT
    "title": "Kế toán thuế",
    "skills": "Kế toán, Thuế",
    "baseSalary": {"@type": "MonetaryAmount", "currency": "VND", "value": {"value": "Negotiable"}},
}

ITVIEC_ROBOTS = "User-Agent: *\nDisallow: /subscriptions/new\nSitemap: https://itviec.com/index.xml\n"


def itviec_site(job_routes: Dict[str, Handler], robots: str = ITVIEC_ROBOTS) -> FakeSite:
    job_urls = list(job_routes)
    return FakeSite(
        {
            "https://itviec.com/robots.txt": robots,
            "https://itviec.com/index.xml": sitemap_index(
                "https://itviec.com/twinnings_companies_vn.xml",
                "https://itviec.com/twinnings_jobs_desc_vn.xml",
            ),
            "https://itviec.com/twinnings_jobs_desc_vn.xml": urlset(
                *job_urls, "https://itviec.com/viec-lam-it/java?city=hn"  # không phải trang chi tiết
            ),
            **job_routes,
        }
    )


# ---------------------------------------------------------------- JSON-LD extraction


def test_extract_job_posting_finds_jobposting_among_other_blocks():
    html = job_page(ITVIEC_POSTING, extra_blocks=({"@type": "BreadcrumbList"}, "<<invalid>>"))
    assert jb.extract_job_posting(html)["title"] == ITVIEC_POSTING["title"]


def test_extract_job_posting_inside_graph_and_list():
    html = (
        '<script type="application/ld+json">{"@graph": [{"@type": "WebPage"}, '
        '[{"@type": ["JobPosting"], "title": "QA"}]]}</script>'
    )
    assert jb.extract_job_posting(html)["title"] == "QA"


def test_extract_job_posting_missing_returns_none():
    assert jb.extract_job_posting("<html><script>var a=1</script></html>") is None


# ---------------------------------------------------------------- field parsing


@pytest.mark.parametrize(
    "value, expected",
    [
        ("Java, Spring Boot ; Docker\nAWS", ["Java", "Spring Boot", "Docker", "AWS"]),
        (["Go", "go", " Kafka "], ["Go", "Kafka"]),
        ([{"name": "Redis"}], ["Redis"]),
        (None, []),
        ("", []),
    ],
)
def test_parse_skills(value, expected):
    assert jb.parse_skills(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ({"currency": "USD", "value": {"minValue": 1120, "maxValue": 2800, "unitText": "MONTH"}}, (1120, 2800, "USD")),
        ({"currency": "VND", "value": {"minValue": "20,000,000", "maxValue": 15000000}}, (15000000, 20000000, "VND")),
        ({"currency": "USD", "value": {"value": 3000, "unitText": "MONTH"}}, (3000, 3000, "USD")),
        ({"currency": "USD", "value": {"minValue": 24000, "maxValue": 36000, "unitText": "YEAR"}}, (2000, 3000, "USD")),
        ({"currency": "USD", "value": {"minValue": 10, "unitText": "HOUR"}}, (None, None, "USD")),
        ({"currency": "VND", "value": {"value": "Negotiable", "unitText": "MONTH"}}, (None, None, "VND")),
        ({"currency": "VND", "value": 0}, (None, None, "VND")),
        (None, (None, None, None)),
    ],
)
def test_parse_base_salary(value, expected):
    low, high, currency = jb.parse_base_salary(value)
    assert (low and int(low), high and int(high), currency) == expected


def test_parse_location_keeps_region_only_and_dedupes():
    loc = [
        {"address": {"streetAddress": "X", "addressRegion": "Hà Nội"}},
        {"address": {"addressRegion": "Hà Nội"}},
        {"address": {"addressRegion": "Not Available", "addressLocality": "Đà Nẵng"}},
    ]
    assert jb.parse_location(loc) == "Hà Nội, Đà Nẵng"
    assert jb.parse_location(None) is None


@pytest.mark.parametrize(
    "title, months, level",
    [
        ("Thực tập sinh Java", 24, "Intern"),
        ("Backend Developer", 0, "Fresher"),
        ("Backend Developer", 24, "Junior"),
        ("Backend Developer", 40, "Middle"),
        ("Backend Developer", 72, "Senior"),
        ("Senior Backend Developer", None, "Senior"),
        ("Junior QA", None, "Junior"),
        ("Fresher Tester", None, "Fresher"),
        ("Backend Developer", None, "Unknown"),
        ("International Sales Engineer", None, "Unknown"),
    ],
)
def test_derive_web_level(title, months, level):
    assert jb.derive_web_level(title, months) == level


def test_transform_posting_keeps_only_facts():
    job = jb.transform_posting(jb.SOURCES["itviec"], "https://itviec.com/viec-lam-it/a-1", ITVIEC_POSTING)
    assert job.title == "Backend Developer (Java, Spring Boot)"
    assert job.company_name == "Công ty Mẫu"
    assert job.external_source == "itviec"
    assert job.published_date == "2026-10-01" and job.valid_through == "2026-11-01"
    assert (job.min_salary_usd, job.max_salary_usd) == (1000.0, 2000.0)
    assert (job.min_salary_vnd, job.max_salary_vnd) == (None, None)
    assert job.is_salary_negotiable is False
    assert job.location == "Hà Nội"
    assert job.level == "Junior" and job.months_of_experience == 24
    assert {s.canonical_name for s in job.skills} >= {"Java", "Spring Boot", "MySQL", "Docker"}
    assert job.source_id == jb.compute_source_id("itviec", "https://itviec.com/viec-lam-it/a-1")

    # AD-7: không một mẩu văn bản JD / địa chỉ chi tiết nào trong bản ghi
    dumped = job.model_dump_json()
    for key in FREE_TEXT_KEYS:
        assert key not in dumped
    for leaked in ("KHONG DUOC LUU",):
        assert leaked not in dumped


def test_transform_posting_vnd_salary_and_datetime_date():
    job = jb.transform_posting(jb.SOURCES["topdev"], "https://topdev.vn/detail-jobs/x-1", TOPDEV_IT_POSTING)
    assert (job.min_salary_vnd, job.max_salary_vnd) == (8_000_000, 12_000_000)
    assert job.min_salary_usd is None
    assert job.published_date == "2026-10-20"
    assert job.level == "Fresher"
    assert jb.is_it_job(job)


def test_transform_posting_negotiable_and_non_it():
    job = jb.transform_posting(jb.SOURCES["topdev"], "https://topdev.vn/detail-jobs/y-2", TOPDEV_NON_IT_POSTING)
    assert job.is_salary_negotiable is True
    assert not jb.is_it_job(job)


@pytest.mark.parametrize(
    "title, expected",
    [
        ("RPA Developer (Middle)", True),
        ("Lập trình viên PHP", True),
        ("Kỹ sư phần mềm nhúng", True),
        ("QC Engineer (Manual Tester)", True),
        ("Information Security Specialist", True),
        ("IT Helpdesk", True),
        ("Chuyên viên phân tích nghiệp vụ (BA)", True),
        ("Business Intelligence Analytics", True),
        ("Phiên dịch viên tiếng Hàn", False),
        ("Kỹ sư QS phòng kiểm soát", False),
        ("Nhân viên QC sản xuất", False),
        ("Nhân viên kinh doanh tour du lịch inbound", False),
        ("Security Guard", False),
        ("Nhân viên quản lý website bán hàng", False),
    ],
)
def test_is_it_job_by_title_when_no_skill_matches(title, expected):
    posting = {"@type": "JobPosting", "title": title, "skills": "Giao tiếp, Kỹ năng mềm"}
    job = jb.transform_posting(jb.SOURCES["topdev"], "https://topdev.vn/viec-lam/x-1", posting)
    assert jb.is_it_job(job) is expected


def test_transform_posting_without_title_is_none():
    assert jb.transform_posting(jb.SOURCES["itviec"], "u", {"@type": "JobPosting"}) is None


# ---------------------------------------------------------------- sitemap


def test_parse_sitemap_index_and_urlset_and_garbage():
    assert jb.parse_sitemap(sitemap_index("https://a/1.xml")) == (
        True,
        [jb.SitemapEntry("https://a/1.xml", "2026-10-21T22:00:00+07:00")],
    )
    is_index, entries = jb.parse_sitemap(urlset("https://a/job-1"))
    assert not is_index and entries[0].loc == "https://a/job-1"
    assert jb.parse_sitemap("<html>Just a moment...</html") == (False, [])


def test_iter_job_urls_follows_only_job_sitemaps_and_filters_urls():
    job = "https://itviec.com/viec-lam-it/java-dev-1"
    site = itviec_site({job: job_page(ITVIEC_POSTING)})
    with make_client(site) as client:
        urls = [e.loc for e in jb.iter_job_urls(client, jb.SOURCES["itviec"])]
    assert urls == [job]
    assert "https://itviec.com/twinnings_companies_vn.xml" not in site.requests


def test_iter_job_urls_stops_when_url_pattern_no_longer_matches():
    pages = [f"https://topdev.vn/sitemap/jobs_desc_vi_page_{i}.xml" for i in range(1, 6)]
    routes: Dict[str, Handler] = {
        "https://topdev.vn/robots.txt": "User-Agent: *\nSitemap: https://topdev.vn/sitemap-jobs.xml\n",
        "https://topdev.vn/sitemap-jobs.xml": sitemap_index(*pages),
    }
    routes.update({p: urlset(f"https://topdev.vn/tin-moi/job-{i}") for i, p in enumerate(pages)})
    site = FakeSite(routes)
    with make_client(site) as client, pytest.raises(ScrapeError, match="cấu trúc trang"):
        list(jb.iter_job_urls(client, jb.SOURCES["topdev"]))
    assert pages[3] not in site.requests  # dừng sau MAX_BARREN_SITEMAPS, không đi hết cây


def test_iter_job_urls_requires_sitemap_in_robots():
    site = FakeSite({"https://itviec.com/robots.txt": "User-Agent: *\nAllow: /\n"})
    with make_client(site) as client, pytest.raises(ScrapeError):
        list(jb.iter_job_urls(client, jb.SOURCES["itviec"]))


# ---------------------------------------------------------------- crawl


def test_crawl_end_to_end_with_limit_and_state(tmp_path):
    jobs = {f"https://itviec.com/viec-lam-it/dev-{i}": job_page({**ITVIEC_POSTING, "title": f"Dev {i}"}) for i in range(3)}
    jobs["https://itviec.com/viec-lam-it/no-jsonld-9"] = "<html>no data</html>"
    site = itviec_site(jobs)
    state = jb.CrawlState(tmp_path / "itviec.state.json")
    stats: dict = {}
    with make_client(site) as client:
        first = list(jb.crawl(client, jb.SOURCES["itviec"], limit=2, state=state, stats=stats))
    assert [j.title for j in first] == ["Dev 0", "Dev 1"]
    assert stats["pages_fetched"] == 2
    state.save()

    state = jb.CrawlState(tmp_path / "itviec.state.json")
    stats = {}
    with make_client(site) as client:
        second = list(jb.crawl(client, jb.SOURCES["itviec"], limit=10, state=state, stats=stats))
    assert [j.title for j in second] == ["Dev 2"]
    assert stats["skipped_seen"] == 2 and stats["no_jsonld"] == 1


def test_crawl_topdev_drops_non_it():
    site = FakeSite(
        {
            "https://topdev.vn/robots.txt": "User-Agent: *\nAllow: /\nSitemap: https://topdev.vn/sitemap.xml\n",
            "https://topdev.vn/sitemap.xml": sitemap_index(
                "https://topdev.vn/sitemap-companies.xml", "https://topdev.vn/sitemap-jobs.xml"
            ),
            "https://topdev.vn/sitemap-jobs.xml": sitemap_index(
                "https://topdev.vn/sitemap/jobs_desc_en_page_1.xml", "https://topdev.vn/sitemap/jobs_desc_vi_page_1.xml"
            ),
            "https://topdev.vn/sitemap/jobs_desc_vi_page_1.xml": urlset(
                "https://topdev.vn/viec-lam/react-dev-1",
                "https://topdev.vn/viec-lam/ke-toan-2",
                "https://topdev.vn/viec-lam/nhan-vien-qc-nha-may-nhua-3",
            ),
            "https://topdev.vn/viec-lam/react-dev-1": job_page(TOPDEV_IT_POSTING),
            "https://topdev.vn/viec-lam/ke-toan-2": job_page(TOPDEV_NON_IT_POSTING),
            "https://topdev.vn/viec-lam/nhan-vien-qc-nha-may-nhua-3": job_page(
                {**TOPDEV_NON_IT_POSTING, "title": "Nhân viên QC nhà máy nhựa"}
            ),
        }
    )
    stats: dict = {}
    with make_client(site) as client:
        kept = list(jb.crawl(client, jb.SOURCES["topdev"], limit=10, stats=stats))
    assert [j.title for j in kept] == ["Fresher ReactJS Developer"]
    assert stats["skipped_slug"] == 1  # ke-toan: không tải
    assert stats["non_it"] == 1  # qc: qua lọc slug, bị loại sau khi tải
    assert stats["pages_fetched"] == 2
    assert "https://topdev.vn/viec-lam/ke-toan-2" not in site.requests
    assert "https://topdev.vn/sitemap/jobs_desc_en_page_1.xml" not in site.requests  # chỉ bản tiếng Việt


def test_itviec_has_no_slug_prefilter():
    jobs = {"https://itviec.com/viec-lam-it/ke-toan-noi-bo-cong-ty-x-1": job_page(ITVIEC_POSTING)}
    with make_client(itviec_site(jobs)) as client:
        assert len(list(jb.crawl(client, jb.SOURCES["itviec"], limit=5))) == 1


@pytest.mark.parametrize(
    "url, expected",
    [
        ("https://topdev.vn/viec-lam/rpa-developer-middle-cyberlogitec-vietnam-co-ltd-2133547", True),
        ("https://topdev.vn/viec-lam/chuyen-vien-phan-tich-nghiep-vu-ba-cong-ty-dich-vu-so-2133550", True),
        ("https://topdev.vn/viec-lam/c-c-software-developer-telecom-all-levels-remotepeople-2133561", True),
        ("https://topdev.vn/viec-lam/ky-su-du-lieu-data-engineer-vnpt-net-2133562", True),
        ("https://topdev.vn/viec-lam/chuyen-gia-van-hanh-ung-dung-ha-noi-pgbank-2133555", True),
        ("https://topdev.vn/viec-lam/ui-ux-designer-cong-ty-tnhh-rontech-2133559", True),
        ("https://topdev.vn/viec-lam/dieu-duong-benh-vien-mat-cong-ty-co-phan-2133570", False),
        ("https://topdev.vn/viec-lam/thuc-tap-sinh-thu-mua-cong-ty-co-phan-cafe-katinat-2133566", False),
        ("https://topdev.vn/viec-lam/ke-toan-doanh-thu-cong-ty-co-phan-2133580", False),
    ],
)
def test_it_slug(url, expected):
    assert jb.it_slug(url) is expected


def test_cli_rejects_out_with_several_sources(tmp_path, capsys):
    assert jb.main(["--source", "all", "--out", str(tmp_path / "x.jsonl")]) == 2
    assert "--out" in capsys.readouterr().err


def test_write_jsonl_round_trip(tmp_path):
    job = jb.transform_posting(jb.SOURCES["itviec"], "https://itviec.com/viec-lam-it/a-1", ITVIEC_POSTING)
    out = tmp_path / "out.jsonl"
    assert jb.write_jsonl(iter([job, job]), out) == 2
    rows = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]
    assert rows[0]["source_url"] == "https://itviec.com/viec-lam-it/a-1"
    assert "description" not in rows[0]


# ---------------------------------------------------------------- politeness


def test_robots_disallow_is_respected():
    site = FakeSite({"https://itviec.com/robots.txt": "User-Agent: *\nDisallow: /private/\n"})
    with make_client(site) as client:
        with pytest.raises(DisallowedError):
            client.get("https://itviec.com/private/x")
    assert "https://itviec.com/private/x" not in site.requests


def test_robots_server_error_means_disallow_all_and_404_means_allow():
    site = FakeSite(
        {
            "https://a.vn/robots.txt": httpx.Response(500),
            "https://b.vn/robots.txt": httpx.Response(404),
            "https://b.vn/page": "ok",
        }
    )
    with make_client(site) as client:
        client.max_retries = 0
        assert client.can_fetch("https://a.vn/page") is False
        assert client.get("https://b.vn/page").text == "ok"


def test_cloudflare_challenge_stops_crawl():
    challenge = httpx.Response(
        403, text="<html><head><title>Just a moment...</title></head>challenges.cloudflare.com</html>"
    )
    site = FakeSite({"https://www.topcv.vn/robots.txt": "User-agent: *\n", "https://www.topcv.vn/job": challenge})
    with make_client(site) as client, pytest.raises(BlockedError):
        client.get("https://www.topcv.vn/job")
    assert site.requests.count("https://www.topcv.vn/job") == 1  # không thử lại


def test_cf_mitigated_header_is_a_challenge_even_with_200():
    site = FakeSite(
        {
            "https://x.vn/robots.txt": "",
            "https://x.vn/a": httpx.Response(200, headers={"cf-mitigated": "challenge"}, text="ok"),
        }
    )
    with make_client(site) as client, pytest.raises(BlockedError):
        client.get("https://x.vn/a")


def test_429_retries_after_retry_after_then_succeeds():
    calls = {"n": 0}

    def flaky(_request):
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(429, headers={"Retry-After": "7"})
        return httpx.Response(200, text="ok")

    sleeps: List[float] = []
    site = FakeSite({"https://x.vn/robots.txt": "", "https://x.vn/a": flaky})
    with make_client(site, sleeps) as client:
        assert client.get("https://x.vn/a").text == "ok"
    assert 7 in sleeps


def test_retry_after_is_capped_and_retries_are_bounded():
    sleeps: List[float] = []
    site = FakeSite({"https://x.vn/robots.txt": "", "https://x.vn/a": httpx.Response(503, headers={"Retry-After": "99999"})})
    with make_client(site, sleeps) as client:
        resp = client.get("https://x.vn/a")
    assert resp.status_code == 503
    assert site.requests.count("https://x.vn/a") == client.max_retries + 1
    assert max(sleeps) <= 300


def test_min_delay_between_requests_to_same_host():
    sleeps: List[float] = []
    now = {"t": 0.0}
    site = FakeSite({"https://x.vn/robots.txt": "User-agent: *\nCrawl-delay: 5\n", "https://x.vn/a": "a", "https://x.vn/b": "b"})
    client = PoliteClient(
        "SkillNexusBot/0.1",
        min_delay_s=2,
        jitter_s=0,
        transport=httpx.MockTransport(site),
        sleep=lambda s: (sleeps.append(s), now.__setitem__("t", now["t"] + s)),
        clock=lambda: now["t"],
    )
    with client:
        client.get("https://x.vn/a")
        client.get("https://x.vn/b")
    assert sleeps and all(s == pytest.approx(5) for s in sleeps)  # Crawl-delay lớn hơn min_delay


def test_user_agent_is_honest():
    ua = build_user_agent("me@example.com")
    assert ua.startswith("SkillNexusBot/") and "me@example.com" in ua and "Mozilla" not in ua


# ---------------------------------------------------------------- Next.js RSC (không có JSON-LD)


def _next_f_page(*rows) -> str:
    """Trang Next.js App Router: các dòng `ID:JSON` chia thành nhiều chuỗi JS trong `self.__next_f.push`."""
    flight = "".join(f"{i}:{json.dumps(r, ensure_ascii=False)}\n" for i, r in enumerate(rows))
    half = len(flight) // 2
    pushes = "".join(
        f"<script>self.__next_f.push([1,{json.dumps(part, ensure_ascii=False)}])</script>"
        for part in (flight[:half], flight[half:])
    )
    return f'<html><body><script>(self.__next_f=self.__next_f||[]).push([0])</script>{pushes}</body></html>'


RSC_JOB = {
    "jobId": 2124572,
    "jobTitle": "Senior Python Engineer",
    "companyName": "VinAI",
    "company": {"id": 7, "logo": {"url": "x.png"}},  # object lồng nhau sau jobTitle
    "salaryMin": 25000000,
    "salaryMax": 40000000,
    "salaryCurrency": "VND",
    "city": "Hà Nội",
    "createdOn": "2026-10-25",
    "jobDescription": "FastAPI, PostgreSQL, PyTorch",
}


def test_rsc_fallback_reads_job_split_across_pushes():
    html = _next_f_page(["$", "div", None, {"children": "x"}], {"props": {"job": RSC_JOB}})
    posting = jb.extract_job_posting(html)
    assert posting["@type"] == "JobPosting" and posting["title"] == "Senior Python Engineer"
    assert posting["hiringOrganization"]["name"] == "VinAI"
    assert posting["baseSalary"] == {
        "currency": "VND",
        "value": {"minValue": 25000000, "maxValue": 40000000, "unitText": "MONTH"},
    }
    job = jb.transform_posting(jb.SOURCES["topdev"], "https://topdev.vn/viec-lam/python-1", posting)
    assert job.location == "Hà Nội"
    assert {"Python", "PostgreSQL"} <= {s.canonical_name for s in job.skills}
    assert "FastAPI, PostgreSQL, PyTorch" not in job.model_dump_json()  # AD-7


def test_rsc_fallback_no_currency_means_no_salary():
    raw = {k: v for k, v in RSC_JOB.items() if k != "salaryCurrency"}
    posting = jb.extract_job_posting(_next_f_page({"job": raw}))
    assert posting["baseSalary"] is None


def test_rsc_fallback_ignores_pages_without_job():
    assert jb.extract_job_posting(_next_f_page(["$", "div", None, {"jobTitleLabel": 1}])) is None
    assert jb.extract_job_posting('<script>self.__next_f.push([1,"not json\\n"])</script>') is None
    assert jb.extract_job_posting("<html>jobTitle</html>") is None


def test_jsonld_wins_over_rsc():
    html = _next_f_page({"job": RSC_JOB}) + (
        '<script type="application/ld+json">{"@type": "JobPosting", "title": "From JSON-LD"}</script>'
    )
    assert jb.extract_job_posting(html)["title"] == "From JSON-LD"
