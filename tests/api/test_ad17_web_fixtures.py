"""AD-17 — fixture của web khớp đúng response của API giả.

`web/tests/fixtures/city-shares-<role>.json` là response của `GET /api/v1/city-shares?role=<role>&level=all`, và
`city-shares-<role>.entry.json` là response của `...&level=entry` (#163), chép lại để test của web chạy mà không cần
API. Đổi `haido_api/fixtures/fake_market.json` (ví dụ đổi mã thành phố) mà quên sinh lại các file này thì test web
vẫn xanh trong khi `/` hiện "Không đọc được số liệu"; test này bắt chỗ lệch đó.

Sinh lại sau khi đổi bản giả: với mỗi (vai trò, cấp), lấy `TestClient(app).get(...).json()` và ghi đè
file tương ứng bằng `json.dumps(..., ensure_ascii=False, indent=2)` cộng một dòng trống cuối.
"""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from posting_examples import NAMES as READY_EXAMPLES
from posting_examples import ready_example
from posting_samples import (
    BACKEND_TEXT,
    CLOUD_TEXT,
    FEE_TEXT,
    HAVE_16_OF_18,
    NOT_IT_TEXT,
    NOT_POSTING_TEXT,
    POSTING_SKILLS,
    SHORT_TEXT,
    csv,
)

from haido_api.main import app

ROOT = Path(__file__).resolve().parents[2]
WEB_FIXTURES = ROOT / "web" / "tests" / "fixtures"


def _fixture_name(role: str, level: str) -> str:
    return (
        f"city-shares-{role}.json"
        if level == "all"
        else f"city-shares-{role}.{level}.json"
    )


@pytest.mark.parametrize("level", ["all", "entry"])
@pytest.mark.parametrize("role", ["all", "ai_ml", "backend"])
def test_ad17_fixture_web_khop_response_city_shares(role: str, level: str) -> None:
    resp = TestClient(app).get(
        "/api/v1/city-shares", params={"role": role, "level": level}
    )
    assert resp.status_code == 200, resp.text

    fixture = json.loads(
        (WEB_FIXTURES / _fixture_name(role, level)).read_text(encoding="utf-8")
    )
    assert resp.json() == fixture


def test_ad17_fixture_web_khop_response_newcomer_roles() -> None:
    resp = TestClient(app).get("/api/v1/newcomer-roles")
    assert resp.status_code == 200, resp.text

    fixture = json.loads(
        (WEB_FIXTURES / "newcomer-roles.json").read_text(encoding="utf-8")
    )
    assert resp.json() == fixture


@pytest.mark.parametrize(
    ("role", "level", "have"),
    [
        ("backend", "entry", None),
        ("backend", "entry", "java,sql,git"),
        ("backend", "intern", None),  # quay về vai trò × mọi cấp, có số (#217)
        ("data_engineer", "entry", None),  # không ô nào đủ 30: mọi tỷ lệ null_data
        ("data_engineer", "entry", "java,sql,git"),  # ví dụ FR-24
        ("ai_ml", "entry", None),  # not_ready, có hồ sơ kỹ năng để mở (#111)
        ("qa", "entry", None),  # not_ready; từ #149 có hồ sơ kỹ năng
    ],
)
def test_ad17_fixture_web_khop_response_learning_path(
    role: str, level: str, have: str | None
) -> None:
    """#212: `learning-path-<role>[.<cấp>][-have].json` là response của `?role=&level=[&have=java,sql,git]`.

    Cấp `entry` bỏ khỏi tên file (như `city-shares`, mặc định của route); cấp khác thêm `.<cấp>`.
    """
    params = {"role": role, "level": level} | ({"have": have} if have else {})
    resp = TestClient(app).get("/api/v1/learning-path", params=params)
    assert resp.status_code == 200, resp.text

    name = f"learning-path-{role}{'' if level == 'entry' else '.' + level}{'-have' if have else ''}.json"
    fixture = json.loads((WEB_FIXTURES / name).read_text(encoding="utf-8"))
    assert resp.json() == fixture


SKILL_RATES_CASES = [
    ("backend", "entry", None),  # ô đủ mẫu, cả ba nhóm
    ("backend", "entry", "java,sql,git"),  # tick sẵn, đếm core ở API (AD-22)
    ("backend", "intern", None),  # quay về Backend ở mọi cấp, có `fallback_label`
    ("data_engineer", "entry", None),  # không ô nào đủ 30: mọi tỷ lệ null_data
    ("frontend", "entry", None),  # đổi vai trò trên màn (#150)
]


@pytest.mark.parametrize(("role", "level", "have"), SKILL_RATES_CASES)
def test_ad17_fixture_web_khop_response_skill_rates(role: str, level: str, have: str | None) -> None:
    """#149: `skill-rates-<role>.<cấp>[-have].json` là response của `?role=&level=[&have=java,sql,git]`."""
    params = {"role": role, "level": level} | ({"have": have} if have else {})
    resp = TestClient(app).get("/api/v1/skill-rates", params=params)
    assert resp.status_code == 200, resp.text

    name = f"skill-rates-{role}.{level}{'-have' if have else ''}.json"
    fixture = json.loads((WEB_FIXTURES / name).read_text(encoding="utf-8"))
    assert resp.json() == fixture


def test_ad17_fixture_web_khop_response_skills() -> None:
    """#207: `skills.json` là response của `GET /api/v1/skills` (danh sách tìm kỹ năng song ngữ)."""
    resp = TestClient(app).get("/api/v1/skills")
    assert resp.status_code == 200, resp.text
    fixture = json.loads((WEB_FIXTURES / "skills.json").read_text(encoding="utf-8"))
    assert resp.json() == fixture


@pytest.mark.parametrize("skill", ["python", "figma", "abap", "sap", "machine_learning"])
def test_ad17_fixture_web_khop_response_skill_roles(skill: str) -> None:
    """#166: `skill-roles-<mã>.json` là response của `GET /api/v1/skill-roles?skill=<mã>`.

    `python`: đủ trường hợp; `figma`: xếp hạng khác, vai trò cao nhất bị ẩn; `abap`: không tin nào nhắc (`mentioned = false`);
    `sap`: không tin entry-level nào nhắc nhưng có tin ở cấp khác (`mentioned = true`); `machine_learning`: tên tiếng Việt khác tiếng Anh.
    """
    resp = TestClient(app).get("/api/v1/skill-roles", params={"skill": skill})
    assert resp.status_code == 200, resp.text
    fixture = json.loads((WEB_FIXTURES / f"skill-roles-{skill}.json").read_text(encoding="utf-8"))
    assert resp.json() == fixture


@pytest.mark.parametrize(
    ("name", "text"),
    [
        ("backend", BACKEND_TEXT),
        ("fee", FEE_TEXT),
        ("cloud", CLOUD_TEXT),
        ("not-posting", NOT_POSTING_TEXT),
        ("not-it", NOT_IT_TEXT),
        ("too-short", SHORT_TEXT),
    ],
)
def test_ad17_fixture_web_khop_response_posting_read(name: str, text: str) -> None:
    """#230: `posting-read-<tên>.json` là response của `POST /api/v1/posting-reads` với chữ mẫu của `posting_samples.py`.

    `backend`: tin Backend Junior đủ trường; `fee`: tin có đặt cọc, liên hệ Zalo và Telegram, không nêu công ty;
    `cloud`: tin DevOps nhánh Cloud, lương không có số, đã có tin thu thập khớp; `not-posting`: không phải tin; `not-it`: tin tuyển
    dụng không thuộc IT; `too-short`: quá ngắn.
    """
    resp = TestClient(app).post("/api/v1/posting-reads", json={"text": text})
    assert resp.status_code == 200, resp.text
    fixture = json.loads((WEB_FIXTURES / f"posting-read-{name}.json").read_text(encoding="utf-8"))
    assert resp.json() == fixture


_SKILLS = csv(POSTING_SKILLS)
POSTING_CHECK_CASES = [
    ("backend.junior-have", {"role": "backend", "level": "junior", "skills": _SKILLS, "have": csv(HAVE_16_OF_18)}),  # FR-28: 16/18 = 89%
    ("backend.junior", {"role": "backend", "level": "junior", "skills": _SKILLS}),  # chưa có hồ sơ
    ("backend.intern-have", {"role": "backend", "level": "intern", "skills": _SKILLS, "have": "java,sql,docker"}),  # quay về ô rộng
    ("backend.unknown-fee", {"role": "backend", "level": "unknown", "skills": "java", "contacts": "zalo,telegram", "fees": "1"}),  # tin có phí, không ghi cấp
    ("data_engineer.entry-have", {"role": "data_engineer", "level": "entry", "skills": "python,sql,airflow", "have": "python"}),  # không ô nào đủ 30
]


@pytest.mark.parametrize(("name", "params"), POSTING_CHECK_CASES)
def test_ad17_fixture_web_khop_response_posting_check(name: str, params: dict[str, str]) -> None:
    """#230: `posting-check-<tên>.json` là response của `GET /api/v1/posting-check` với tham số của từng ca."""
    resp = TestClient(app).get("/api/v1/posting-check", params=params)
    assert resp.status_code == 200, resp.text
    fixture = json.loads((WEB_FIXTURES / f"posting-check-{name}.json").read_text(encoding="utf-8"))
    assert resp.json() == fixture


@pytest.mark.parametrize("name", READY_EXAMPLES)
def test_ad17_fixture_web_ready_la_vi_du_viet_tay_khop_posting_examples(name: str) -> None:
    """#230 (vòng review): `posting-check-ready-<tên>.json` là ví dụ `ready` của `market` và `warnings` (API giả còn `not_ready`).

    Chúng được dựng bởi `tests/api/posting_examples.py` (phần `match` và `meta` từ API giả) và đã qua `Envelope[PostingCheckData]`.
    """
    fixture = json.loads((WEB_FIXTURES / f"posting-check-ready-{name}.json").read_text(encoding="utf-8"))
    assert ready_example(name) == fixture
