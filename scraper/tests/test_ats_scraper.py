"""
Nguồn ATS (Greenhouse / Lever / Workable), trang tuyển dụng công ty (chế độ trang danh sách) và trích kỹ năng
từ văn bản JD. JSON/HTML là bản tối giản tự tạo theo đúng cấu trúc đã khảo sát trên API thật; HTTP qua
`httpx.MockTransport`. Normalizer ở chế độ từ điển dự phòng.
"""
import json
from typing import Dict, List

import httpx
import pytest

from scraper.normalizer import SkillTaxonomyNormalizer
from scraper import ats
from scraper import jobboards as jb
from scraper.polite_http import PoliteClient, build_user_agent
from scraper.skills_text import extract_skill_names, html_to_text, skills_from_text

LEAK = "VAN BAN JD KHONG DUOC LUU"


@pytest.fixture(autouse=True)
def fallback_normalizer():
    SkillTaxonomyNormalizer.use_fallback()
    yield
    SkillTaxonomyNormalizer.use_fallback()


class FakeSite:
    def __init__(self, routes: Dict[str, object]):
        self.routes = routes
        self.requests: List[str] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        self.requests.append(url)
        r = self.routes.get(url)
        if r is None:
            return httpx.Response(404)
        if isinstance(r, httpx.Response):
            return r
        if isinstance(r, (dict, list)):
            return httpx.Response(200, json=r)
        return httpx.Response(200, text=r)


def client_for(site: FakeSite) -> PoliteClient:
    return PoliteClient(
        build_user_agent(), min_delay_s=0, jitter_s=0, transport=httpx.MockTransport(site), sleep=lambda s: None
    )


# ---------------------------------------------------------------- skills_text


def test_html_to_text_handles_double_escaped_greenhouse_content():
    assert html_to_text("&lt;p&gt;Java &amp;amp; Kotlin&lt;/p&gt;") == "Java & Kotlin"
    assert html_to_text(None) == ""


@pytest.mark.parametrize(
    "text, expected",
    [
        ("Experience with Java, Spring Boot and PostgreSQL", ["Java", "Spring Boot", "PostgreSQL"]),
        ("Languages: Java, Scala, Go, C# or similar", ["Java", "Go", "C#"]),
        ("C, C++, Rust, Golang, or Python", ["Golang", "Python"]),
        ("We react quickly and go beyond. Go the extra mile, rest assured.", []),  # động từ, không phải công nghệ
        ("Build REST APIs with Node.js and ReactJS on AWS", ["REST", "Node.js", "ReactJS", "AWS"]),
        ("JavaScript (ES6), .NET Core and ASP.NET", ["JavaScript", "ES6", ".NET Core"]),
        ("CI/CD pipelines, Docker containers, K8s", ["CI/CD", "Docker", "K8s"]),
        ("Spring 2026 internship in our container team", []),
    ],
)
def test_extract_skill_names(text, expected):
    assert extract_skill_names(text) == expected


def test_skills_from_text_returns_only_matched_canonical_skills_once():
    skills = skills_from_text("<p>Golang / Go, ReactJS, React.js and Postgres</p>", "Kubernetes (K8s)")
    assert [s.canonical_name for s in skills] == ["Go", "React", "PostgreSQL", "Kubernetes"]
    assert all(s.matched for s in skills)


# ---------------------------------------------------------------- shared helpers


@pytest.mark.parametrize(
    "args, expected",
    [
        (("Ho Chi Minh City, Vietnam",), "Hồ Chí Minh"),
        (("Hồ Chí Minh",), "Hồ Chí Minh"),
        (("Ho Chi Minh City", "Da Nang City", "Hanoi"), "Hồ Chí Minh, Hà Nội, Đà Nẵng"),
        (("Remote - Vietnam",), "Việt Nam"),
        (("Singapore",), None),
    ],
)
def test_vn_city(args, expected):
    assert ats.vn_city(*args) == expected


def test_parse_location_normalizes_unaccented_city():
    assert jb.parse_location({"address": {"addressRegion": "Ha Noi"}}) == "Hà Nội"


@pytest.mark.parametrize(
    "title, expected",
    [
        ("UI/UX Designer", True),
        ("Middle Test Engineer", True),
        ("2D UI Artist", False),
        ("AI Video Editor / Motion Graphic", False),
        ("Creative Strategist (Game)", False),
        ("Technology Talent Network", False),
        ("Sales Engineer", False),
        ("Senior Finance Manager", False),
        ("SME-84_Embedded Finance Solution (PO)", True),
        ("Nhân viên kinh doanh phần mềm", False),
    ],
)
def test_non_it_titles_override_it_keywords(title, expected):
    assert jb.is_it_title(title) is expected


# ---------------------------------------------------------------- adapters

GH_BOARD = ats.Board("greenhouse", "acme", "Acme")
LV_BOARD = ats.Board("lever", "acme", "Acme")
WK_BOARD = ats.Board("workable", "acme", "Acme")

GREENHOUSE_JSON = {
    "jobs": [
        {
            "absolute_url": "https://job-boards.greenhouse.io/acme/jobs/1",
            "title": "Senior Backend  Engineer",
            "company_name": "ACME VIETNAM",
            "location": {"name": "Ho Chi Minh City, Vietnam"},
            "first_published": "2026-09-01T01:00:00-05:00",
            "updated_at": "2026-10-01T00:00:00-04:00",
            "content": f"&lt;p&gt;{LEAK}. Java, Kafka &amp;amp; Redis&lt;/p&gt;",
            "departments": [{"name": "Backend Engineering"}],
            "offices": [{"name": "ACME VN (Ho Chi Minh)"}],
        },
        {
            "absolute_url": "https://job-boards.greenhouse.io/acme/jobs/2",
            "title": "Associate Commission Specialist",
            "location": {"name": "Hanoi, Vietnam"},
            "content": "We build Azure backup products",  # boilerplate có kỹ năng nhưng tin không phải IT
            "departments": [{"name": "Finance"}],
        },
        {
            "absolute_url": "https://job-boards.greenhouse.io/acme/jobs/3",
            "title": "Backend Engineer",
            "location": {"name": "Singapore"},
            "content": "Java",
        },
    ]
}

LEVER_JSON = [
    {
        "hostedUrl": "https://jobs.lever.co/acme/a",
        "text": "Platform Product Owner",
        "country": "VN",
        "createdAt": 1790000000000,
        "categories": {"team": "Tech", "location": "Ho Chi Minh City", "allLocations": ["Ho Chi Minh City", "Da Nang"]},
        "descriptionPlain": LEAK,
        "lists": [{"text": "Requirements", "content": "<li>Python, GCP</li>"}],
        "additionalPlain": "",
        "salaryRange": {"min": 24000, "max": 36000, "currency": "USD", "interval": "per-year-salary"},
    },
    {
        "hostedUrl": "https://jobs.lever.co/acme/b",
        "text": "2D UI Artist",
        "country": "VN",
        "categories": {"team": "Product", "location": "Ho Chi Minh City"},
        "descriptionPlain": "Unity, Git",
    },
    {"hostedUrl": "https://jobs.lever.co/acme/c", "text": "Engineer", "country": "SG", "categories": {"location": "Singapore"}},
]

WORKABLE_JSON = {
    "name": "Acme Inc.",
    "jobs": [
        {
            "url": "https://apply.workable.com/j/AAA",
            "title": "DevOps Engineer (Mid-Level)",
            "published_on": "2026-07-02",
            "experience": "Mid-Senior level",
            "function": "Engineering",
            "locations": [{"city": "Ho Chi Minh City", "country": "Vietnam"}],
            "description": f"<p>{LEAK} Docker, Kubernetes, AWS</p>",
        },
        {
            "url": "https://apply.workable.com/j/BBB",
            "title": "QA Tester",
            "experience": "Entry level",
            "locations": [{"city": "Hanoi", "country": "Vietnam"}],
            "description": "",
        },
        {"url": "https://apply.workable.com/j/CCC", "title": "Account Executive", "country": "United States", "city": "Houston"},
    ],
}


def test_parse_greenhouse_vn_only_with_dept_based_it_flag():
    out = list(ats.parse_greenhouse(GH_BOARD, GREENHOUSE_JSON))
    assert [(j.title, it) for j, it in out] == [
        ("Senior Backend Engineer", True),
        ("Associate Commission Specialist", False),
    ]
    job = out[0][0]
    assert job.external_source == "greenhouse" and job.company_name == "ACME VIETNAM"
    assert job.location == "Hồ Chí Minh" and job.published_date == "2026-09-01"
    assert job.level == "Senior" and job.is_salary_negotiable
    assert [s.canonical_name for s in job.skills] == ["Java", "Kafka", "Redis"]
    assert LEAK not in job.model_dump_json()


def test_parse_lever_salary_per_month_and_team_flag():
    out = list(ats.parse_lever(LV_BOARD, LEVER_JSON))
    assert [(j.title, it) for j, it in out] == [("Platform Product Owner", True), ("2D UI Artist", False)]
    job = out[0][0]
    assert (job.min_salary_usd, job.max_salary_usd) == (2000.0, 3000.0)
    assert job.is_salary_negotiable is False
    assert job.company_name == "Acme"  # Lever không trả tên công ty -> lấy từ Board
    assert job.location == "Hồ Chí Minh, Đà Nẵng"
    assert job.published_date == "2026-09-21"
    assert [s.canonical_name for s in job.skills] == ["Python", "GCP"]
    assert LEAK not in job.model_dump_json()


@pytest.mark.parametrize(
    "salary, expected",
    [
        ({"min": 1000, "max": 2000, "currency": "USD", "interval": "per-month-salary"}, (1000, 2000, "USD")),
        ({"min": 0, "max": 2000, "currency": "USD", "interval": "per-month-salary"}, (None, 2000, "USD")),
        ({"min": 20, "max": 30, "currency": "USD", "interval": "per-hour-wage"}, (None, None, "USD")),
        (None, (None, None, None)),
    ],
)
def test_lever_salary(salary, expected):
    assert ats._lever_salary(salary) == expected


def test_parse_workable_level_mapping_and_function_flag():
    out = list(ats.parse_workable(WK_BOARD, WORKABLE_JSON))
    assert [(j.title, j.level, it) for j, it in out] == [
        ("DevOps Engineer (Mid-Level)", "Middle", True),
        ("QA Tester", "Fresher", True),
    ]
    assert out[0][0].company_name == "Acme Inc."
    assert out[1][0].location == "Hà Nội"
    assert LEAK not in out[0][0].model_dump_json()


# ---------------------------------------------------------------- crawl_boards


def _ats_site(extra: Dict[str, object] = None) -> FakeSite:
    routes = {
        "https://boards-api.greenhouse.io/robots.txt": "User-agent: *\nDisallow: /embed/\n",
        "https://api.lever.co/robots.txt": "User-agent: *\nAllow: /\nCrawl-delay: 1\n",
        "https://apply.workable.com/robots.txt": "User-agent: *\nDisallow:\n",
        "https://boards-api.greenhouse.io/v1/boards/acme/jobs?content=true": GREENHOUSE_JSON,
        "https://api.lever.co/v0/postings/acme?mode=json": LEVER_JSON,
        "https://apply.workable.com/api/v1/widget/accounts/acme?details=true": WORKABLE_JSON,
    }
    routes.update(extra or {})
    return FakeSite(routes)


def test_crawl_boards_keeps_vn_it_and_dedupes_with_state(tmp_path):
    boards = (GH_BOARD, LV_BOARD, WK_BOARD, ats.Board("lever", "gone", "Gone"))
    state = jb.CrawlState(tmp_path / "ats.state.json")
    stats: dict = {}
    with client_for(_ats_site()) as client:
        kept = list(ats.crawl_boards(client, boards, state, stats))
    assert [j.title for j in kept] == [
        "Senior Backend Engineer",
        "Platform Product Owner",
        "DevOps Engineer (Mid-Level)",
        "QA Tester",
    ]
    assert stats == {"boards_fetched": 3, "boards_failed": 1, "vn_jobs": 6, "skipped_seen": 0, "non_it": 2, "kept": 4}

    stats = {}
    with client_for(_ats_site()) as client:
        assert list(ats.crawl_boards(client, boards, state, stats)) == []
    assert stats["skipped_seen"] == 6


def test_crawl_boards_skips_host_blocked_by_robots_and_bad_json():
    site = _ats_site(
        {
            "https://api.lever.co/robots.txt": "User-agent: *\nDisallow: /\n",
            "https://apply.workable.com/api/v1/widget/accounts/acme?details=true": "<html>not json</html>",
        }
    )
    stats: dict = {}
    with client_for(site) as client:
        kept = list(ats.crawl_boards(client, (LV_BOARD, WK_BOARD, GH_BOARD), stats=stats))
    assert [j.title for j in kept] == ["Senior Backend Engineer"]
    assert stats["boards_failed"] == 2
    assert "https://api.lever.co/v0/postings/acme?mode=json" not in site.requests


def test_crawl_boards_cloudflare_on_one_ats_host_skips_only_that_host():
    challenge = httpx.Response(403, text="<title>Just a moment...</title> challenges.cloudflare.com")
    site = _ats_site({"https://api.lever.co/v0/postings/acme?mode=json": challenge})
    stats: dict = {}
    boards = (LV_BOARD, ats.Board("lever", "other", "Other"), GH_BOARD)
    with client_for(site) as client:
        kept = list(ats.crawl_boards(client, boards, stats=stats))
    assert [j.title for j in kept] == ["Senior Backend Engineer"]
    assert "https://api.lever.co/v0/postings/other?mode=json" not in site.requests


def test_boards_config_has_no_smartrecruiters():
    assert {b.ats for b in ats.BOARDS} <= set(ats.ADAPTERS) == {"greenhouse", "lever", "workable"}


# ---------------------------------------------------------------- career page (listing mode) + text skills


def _coccoc_job(title: str, description: str) -> str:
    posting = {
        "@type": "JobPosting",
        "title": title,
        "datePosted": "2026-10-14T11:14:38+00:00",
        "description": description,
        "baseSalary": {"currency": "USD", "value": {"value": "Up to 22,000,000"}},
        "experienceRequirements": "Middle",
        "hiringOrganization": {"name": "Công ty TNHH Cốc Cốc"},
        "jobLocation": {"address": {"addressRegion": "Ha Noi"}},
    }
    return f'<script type="application/ld+json">{json.dumps(posting, ensure_ascii=False)}</script>'


def test_listing_source_crawl_with_text_skills_and_title_it_filter():
    site = FakeSite(
        {
            "https://careers.coccoc.com/robots.txt": "User-agent: *\nAllow: /\n",
            "https://careers.coccoc.com/": (
                '<a href="/jobs/middle-test-engineer-2">a</a> <a href="/jobs/chuyen-vien-telesales">b</a>'
                ' <a href="https://careers.coccoc.com/jobs/software-engineer-intern-3?utm=x">c</a>'
                ' <a href="/jobs/digital-marketing-executive-4">d</a> <a href="/blog/post">e</a>'
            ),
            "https://careers.coccoc.com/jobs": '<a href="/jobs/middle-test-engineer-2">dup</a>',
            "https://careers.coccoc.com/jobs/middle-test-engineer-2": _coccoc_job(
                "Middle Test Engineer", f"<p>{LEAK} Selenium, Python, Git</p>"
            ),
            "https://careers.coccoc.com/jobs/software-engineer-intern-3": _coccoc_job(
                "Software Engineer Intern, Search", "C++ and Java"
            ),
            "https://careers.coccoc.com/jobs/digital-marketing-executive-4": _coccoc_job(
                "Digital Marketing Executive", "Our browser is built with C++, Python and Go, Rust"
            ),
        }
    )
    stats: dict = {}
    with client_for(site) as client:
        kept = list(jb.crawl(client, jb.SOURCES["coccoc"], limit=10, stats=stats))
    assert [j.title for j in kept] == ["Middle Test Engineer", "Software Engineer Intern, Search"]
    assert stats["skipped_slug"] == 1  # telesales: không tải
    assert stats["non_it"] == 1  # digital-marketing: qua lọc slug ("digital") nhưng tiêu đề không IT
    first = kept[0]
    assert [s.canonical_name for s in first.skills] == ["Python", "Git"]
    assert first.location == "Hà Nội" and first.level == "Middle"
    assert first.is_salary_negotiable  # "Up to 22,000,000" không phải số -> không đoán
    assert LEAK not in first.model_dump_json()


def test_cli_accepts_ats_source(tmp_path, monkeypatch, capsys):
    calls = []

    def fake_crawl_boards(client, state=None, stats=None):
        calls.append(state)
        stats.update({"boards_fetched": 0, "kept": 0})
        return iter(())

    monkeypatch.setattr(ats, "crawl_boards", fake_crawl_boards)
    monkeypatch.setattr(jb, "_load_normalizer", lambda: None)
    assert jb.main(["--source", "ats", "--out", str(tmp_path / "ats.jsonl")]) == 0
    assert calls and "=== ats: 0 tin IT" in capsys.readouterr().out
