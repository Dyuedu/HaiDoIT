"""AD-17 — fixture của web khớp đúng response của API giả.

`web/tests/fixtures/city-shares-<role>.json` là response của `GET /api/v1/city-shares?role=<role>`,
chép lại để test của web chạy mà không cần API. Đổi `haido_api/fixtures/fake_market.json` (ví dụ
đổi mã thành phố) mà quên sinh lại các file này thì test web vẫn xanh trong khi `/` hiện
"Không đọc được số liệu"; test này bắt chỗ lệch đó.

Sinh lại sau khi đổi bản giả: với mỗi vai trò, lấy `TestClient(app).get(...).json()` và ghi đè
file tương ứng bằng `json.dumps(..., ensure_ascii=False, indent=2)` cộng một dòng trống cuối.
"""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from haido_api.main import app

ROOT = Path(__file__).resolve().parents[2]
WEB_FIXTURES = ROOT / "web" / "tests" / "fixtures"


@pytest.mark.parametrize("role", ["all", "ai_ml", "backend"])
def test_ad17_fixture_web_khop_response_city_shares(role: str) -> None:
    resp = TestClient(app).get("/api/v1/city-shares", params={"role": role})
    assert resp.status_code == 200, resp.text

    fixture = json.loads((WEB_FIXTURES / f"city-shares-{role}.json").read_text(encoding="utf-8"))
    assert resp.json() == fixture


def test_ad17_fixture_web_khop_response_newcomer_roles() -> None:
    resp = TestClient(app).get("/api/v1/newcomer-roles")
    assert resp.status_code == 200, resp.text

    fixture = json.loads((WEB_FIXTURES / "newcomer-roles.json").read_text(encoding="utf-8"))
    assert resp.json() == fixture
