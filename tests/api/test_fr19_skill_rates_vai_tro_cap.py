"""FR-19, FR-18, AD-22 — `GET /api/v1/skill-rates` giả theo vai trò và cấp (#149).

Màn hồ sơ kỹ năng (#152) đọc route này cho mọi vai trò mà danh sách người mới dẫn tới, ở cấp mặc định `entry` (#134)
và `all`. Ô dưới 30 tin thì số lấy từ ô rộng hơn và `fallback_label` gọi tên ô đó. Số kỹ năng core người dùng đã có
do API đếm từ `have=` (AD-22), web không đếm.
"""

from typing import Any

import pytest
from fastapi.testclient import TestClient

from haido_api.main import app
from haido_core.config import load_rules
from haido_core.vocab.skills import MAX_PROFILE_SKILLS

PATH = "/api/v1/skill-rates"
ROLES = tuple(load_rules().roles)


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


def _get(client: TestClient, **params: str) -> dict[str, Any]:
    resp = client.get(PATH, params=params)
    assert resp.status_code == 200, resp.text
    return resp.json()


def _cell(body: dict[str, Any]) -> dict[str, Any]:
    return body["meta"]["cells"][body["data"]["cell_id"]]


@pytest.mark.parametrize("level", ["entry", "all"])
@pytest.mark.parametrize("role", ROLES)
def test_fr19_moi_vai_tro_co_so_o_entry_va_all(client: TestClient, role: str, level: str) -> None:
    body = _get(client, role=role, level=level)
    assert body["data"]["role"] == role
    assert body["data"]["level"] == level
    assert body["data"]["rows"], "ô phải có ít nhất một kỹ năng"


def test_fr18_cap_la_tra_422(client: TestClient) -> None:
    resp = client.get(PATH, params={"role": "backend", "level": "khong_co"})
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "invalid_query"


def test_fr18_cap_hop_le_ma_khong_co_o_van_404(client: TestClient) -> None:
    resp = client.get(PATH, params={"role": "backend", "level": "lead"})
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "unknown_cell"


@pytest.mark.parametrize(
    ("role", "level", "wider"),
    [("backend", "intern", "vn.backend"), ("ui_ux", "entry", "vn.ui_ux"), ("devops", "entry", "vn.devops")],
)
def test_fr19_o_duoi_30_goi_ten_o_rong_hon_va_n_cua_no(
    client: TestClient, role: str, level: str, wider: str
) -> None:
    body = _get(client, role=role, level=level)
    min_sample = body["meta"]["thresholds"]["min_sample"]
    assert body["data"]["cell_id"] == wider
    cell = _cell(body)
    assert cell["fallback_label"], "ô quay về phải có câu gọi tên ô đã dùng"
    assert cell["n"] >= min_sample
    assert all(row["rate"]["display"] != "null_data" for row in body["data"]["rows"])


@pytest.mark.parametrize("role", ["data_engineer", "data_scientist", "embedded", "other"])
def test_fr19_khong_o_nao_du_30_thi_chua_du_du_lieu(client: TestClient, role: str) -> None:
    body = _get(client, role=role, level="entry")
    assert _cell(body)["fallback_label"], "phải nói không ô nào đủ mẫu"
    assert _cell(body)["n"] < body["meta"]["thresholds"]["min_sample"]
    for row in body["data"]["rows"]:
        assert row["rate"]["display"] == "null_data"
        assert row["rate"]["value"] is None
        assert row["group"] is None
    assert body["data"]["core_size"] is None
    assert body["data"]["have_core"] is None


@pytest.mark.parametrize("role", ROLES)
def test_fr19_thu_tu_dong_va_nhom_theo_theta(client: TestClient, role: str) -> None:
    body = _get(client, role=role, level="all")
    thresholds = body["meta"]["thresholds"]
    rows = body["data"]["rows"]
    key = [(r["rate"]["value"] is None, -(r["rate"]["value"] or 0.0), r["skill"]) for r in rows]
    assert key == sorted(key), f"{role}: máy chủ phải sắp dòng, web không sắp lại"
    for row in rows:
        value = row["rate"]["value"]
        if value is None:
            continue
        expected = (
            "core"
            if value >= thresholds["theta_core"]
            else "common"
            if value >= thresholds["theta_common"]
            else "company_specific"
        )
        assert row["group"] == expected, f"{role}/{row['skill']}"


def test_ad22_have_dat_co_va_dem_core(client: TestClient) -> None:
    body = _get(client, role="backend", level="entry", have="java,sql,git,khong_co_trong_o")
    rows = body["data"]["rows"]
    flags = {r["skill"]: r["have"] for r in rows}
    assert {code for code, on in flags.items() if on} == {"java", "sql", "git"} & set(flags)
    core = [r for r in rows if r["group"] == "core"]
    assert body["data"]["core_size"] == len(core)
    assert body["data"]["have_core"] == sum(1 for r in core if r["have"])
    assert body["data"]["have_core"] >= 1


def test_ad22_khong_gui_have_thi_khong_co_ky_nang_nao(client: TestClient) -> None:
    body = _get(client, role="backend", level="entry")
    assert not any(r["have"] for r in body["data"]["rows"])
    assert body["data"]["have_core"] == 0
    assert body["data"]["core_size"] >= 1


@pytest.mark.parametrize(
    "have",
    ["Java", "java,,sql", "java;sql", ",".join(f"k{i}" for i in range(MAX_PROFILE_SKILLS + 1))],
)
def test_ad22_have_sai_tra_422(client: TestClient, have: str) -> None:
    resp = client.get(PATH, params={"role": "backend", "level": "entry", "have": have})
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "invalid_query"
