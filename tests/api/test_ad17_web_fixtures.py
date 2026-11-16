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
        ("qa", "entry", None),  # not_ready, không có hồ sơ kỹ năng
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
