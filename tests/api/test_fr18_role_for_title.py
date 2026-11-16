"""FR-18, AD-2 — `GET /api/v1/role-for-title`: chức danh người dùng gõ thành một vai trò qua phép 6 (#150).

Route chỉ đưa chức danh vào `RuleClassifier` (phép 6) rồi đổi nhãn sang mã vai trò như `aggregate`, để vai trò của màn
hồ sơ kỹ năng trùng vai trò của số liệu. Response không có số nên không dùng Envelope (AD-17).
"""

from typing import Any

import pytest
from fastapi.testclient import TestClient

from haido_api.main import app

PATH = "/api/v1/role-for-title"


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


def _get(client: TestClient, title: str) -> dict[str, Any]:
    resp = client.get(PATH, params={"title": title})
    assert resp.status_code == 200, resp.text
    return resp.json()


@pytest.mark.parametrize(
    ("title", "role"),
    [
        ("Java Backend Developer", "backend"),
        ("Lập trình viên Java", "backend"),
        ("Frontend ReactJS", "frontend"),
        ("Tester", "qa"),
        ("Machine learning engineer", "ai_ml"),
        ("  Senior DevOps  ", "devops"),
    ],
)
def test_fr18_chuc_danh_khop_ra_mot_vai_tro(client: TestClient, title: str, role: str) -> None:
    assert _get(client, title) == {"data": {"status": "matched", "role": role}}


@pytest.mark.parametrize("title", ["Kế toán", "Nhân viên bán hàng"])
def test_fr18_chuc_danh_ngoai_it_la_not_it(client: TestClient, title: str) -> None:
    assert _get(client, title) == {"data": {"status": "not_it", "role": None}}


@pytest.mark.parametrize("title", ["Developer", "Kỹ sư phần mềm"])
def test_fr18_chuc_danh_it_chung_chung_la_generic(client: TestClient, title: str) -> None:
    assert _get(client, title) == {"data": {"status": "generic", "role": None}}


@pytest.mark.parametrize("params", [{}, {"title": ""}, {"title": "   "}, {"title": "a" * 121}])
def test_fr18_chuc_danh_rong_hoac_qua_dai_la_422(client: TestClient, params: dict[str, str]) -> None:
    resp = client.get(PATH, params=params)
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "invalid_query"


def test_fr18_response_khong_lap_lai_chuc_danh(client: TestClient) -> None:
    body = _get(client, "Lập trình viên Java")
    assert "Lập trình viên Java" not in str(body)
