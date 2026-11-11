"""FR-19, FR-20, FR-22, FR-24, AD-22 — các điều kiện thêm sau review của #212 (đợt 2 của `specs/212-*/tdd.md`).

Quét mọi vai trò × cấp (không 500), `cell_id` ở trong vai trò, nhóm và lộ trình, `foundation_for` bắc cầu, trần 200 mã
đếm trước khi loại trùng, ví dụ FR-24, toàn vẹn fixture đồ thị.
"""

import json
from collections import defaultdict
from collections.abc import Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from test_fr22_learning_path import (  # type: ignore[import-not-found]
    FIXTURES,
    PATH,
    _assert_invariants,
    _codes,
    _get,
    _get_rates,
    _skills,
)

from haido_api.fake_market import FakeMarket
from haido_api.main import app
from haido_api.market_source import UnknownCell
from haido_api.routes.market import LEVEL_CODES
from haido_core.config import load_rules

SWEEP_ROLES = tuple(load_rules().roles)
SWEEP_LEVELS = tuple(LEVEL_CODES)


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


# ---------------------------------------------------------------- quét mọi vai trò × cấp (F1)


@pytest.mark.parametrize("have", [None, "java,sql,linux,khong_co"])
def test_fr22_quet_moi_vai_tro_va_cap_chi_tra_200_hoac_404_khong_bao_gio_500(
    client: TestClient, have: str | None
) -> None:
    seen = {200: 0, 404: 0}
    for role in SWEEP_ROLES:
        for level in SWEEP_LEVELS:
            params = {"role": role, "level": level} | ({"have": have} if have else {})
            resp = client.get(PATH, params=params)
            assert resp.status_code in (200, 404), (
                f"{role}/{level}: {resp.status_code} {resp.text[:200]}"
            )
            seen[resp.status_code] += 1
            if resp.status_code == 200:
                _assert_invariants(resp.json(), role)
            else:
                assert resp.json()["error"]["code"] == "unknown_cell"
    assert seen[200] and seen[404]


def test_fr22_data_engineer_senior_la_404_khong_phai_500(client: TestClient) -> None:
    """Trước đây `skill_rates[data_engineer][senior]` thiếu `git` nên `KeyError` thành 500."""
    resp = client.get(PATH, params={"role": "data_engineer", "level": "senior"})
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "unknown_cell"


def test_fr22_fake_chi_nem_unknown_cell_voi_yeu_cau_hop_le() -> None:
    fake = FakeMarket()
    for role in SWEEP_ROLES:
        for level in SWEEP_LEVELS:
            try:
                fake.learning_path(role=role, level=level, have=())
            except UnknownCell:
                pass


# ---------------------------------------------------------------- FR-19: ô ở trong vai trò


def test_fr19_cell_id_luon_thuoc_vai_tro_da_chon(client: TestClient) -> None:
    for role in SWEEP_ROLES:
        for level in SWEEP_LEVELS:
            resp = client.get(PATH, params={"role": role, "level": level})
            if resp.status_code != 200:
                continue
            data = resp.json()["data"]
            for cell_id in (data["cell_id"], data["entry_cell_id"]):
                if cell_id is not None:
                    assert cell_id.split(".")[1] == role, f"{role}/{level}: {cell_id}"


def test_fr19_skill_rates_gia_khong_tro_sang_vai_tro_khac() -> None:
    raw = json.loads((FIXTURES / "fake_market.json").read_text(encoding="utf-8"))
    for role, levels in raw["skill_rates"].items():
        if role == "java_backend":  # nhánh: dùng ô của vai trò cha (FR-19 bước 2)
            continue
        for entry in levels.values():
            assert entry["cell_id"].split(".")[1] == role, (role, entry["cell_id"])


# ---------------------------------------------------------------- F4: nhóm và lộ trình


def _ready_cells(client: TestClient) -> Iterator[tuple[str, str, dict[str, Any]]]:
    for role in SWEEP_ROLES:
        for level in SWEEP_LEVELS:
            resp = client.get(PATH, params={"role": role, "level": level})
            if resp.status_code == 200 and resp.json()["data"]["status"] == "ready":
                yield role, level, resp.json()


def test_fr22_moi_ky_nang_cot_loi_va_thuong_gap_cua_o_deu_co_tren_lo_trinh(
    client: TestClient,
) -> None:
    count = 0
    for role, level, body in _ready_cells(client):
        count += 1
        rates = _get_rates(client, role, level)
        on_path = set(_codes(body))
        for row in rates["data"]["rows"]:
            if row["group"] in ("core", "common"):
                assert row["skill"] in on_path, (
                    f"{role}/{level}: {row['skill']} ({row['group']}) thiếu trên lộ trình"
                )
    assert count >= 3


def test_fr20_ky_nang_rieng_cong_ty_tren_lo_trinh_phai_la_nen_tang(
    client: TestClient,
) -> None:
    for role, level, body in _ready_cells(client):
        for _, skill in _skills(body):
            if skill["group"] is not None and skill["group"] not in ("core", "common"):
                assert skill["foundation_for"], (
                    f"{role}/{level}: {skill['skill']} ({skill['group']})"
                )


def test_fr20_foundation_for_la_to_tien_bac_cau_trong_cac_nut_core_hoac_common(
    client: TestClient,
) -> None:
    body = _get(client, role="backend", level="entry")
    by_code = {s["skill"]: s for _, s in _skills(body)}
    linux = by_code["linux"]
    assert linux["group"] == "company_specific"
    assert linux["prerequisite_for"] == ["docker"]
    assert set(linux["foundation_for"]) == {"docker", "ci_cd", "microservices"}, (
        "cả cháu, không chỉ con trực tiếp"
    )
    assert all(
        by_code[c]["group"] in ("core", "common") for c in linux["foundation_for"]
    )
    for code, skill in by_code.items():
        if code != "linux":
            assert skill["foundation_for"] == [], code


# ---------------------------------------------------------------- not_ready có hồ sơ kỹ năng (F6)


def test_fr22_ai_ml_entry_not_ready_nhung_co_skill_rates_de_mo_ho_so(
    client: TestClient,
) -> None:
    body = _get(client, role="ai_ml", level="entry")
    assert body["data"]["status"] == "not_ready"
    assert _get_rates(client, "ai_ml", "entry")["data"]["rows"]
    qa = client.get("/api/v1/skill-rates", params={"role": "qa", "level": "entry"})
    assert qa.status_code == 404


# ---------------------------------------------------------------- trần 200 mã đếm trước khi loại trùng (F9)


def test_ad22_201_ma_tho_la_422_du_chi_co_150_ma_duy_nhat(client: TestClient) -> None:
    unique = [f"skill_{i}" for i in range(150)]
    raw = [*unique, *unique[:51]]
    assert len(raw) == 201 and len(set(raw)) == 150
    resp = client.get(
        PATH, params={"role": "backend", "level": "entry", "have": ",".join(raw)}
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "invalid_query"
    ok = client.get(
        PATH,
        params={
            "role": "backend",
            "level": "entry",
            "have": ",".join([*unique, *unique[:50]]),
        },
    )
    assert ok.status_code == 200


def test_ad22_have_lap_lai_chi_doc_cai_cuoi(client: TestClient) -> None:
    resp = client.get(f"{PATH}?role=backend&level=entry&have=java&have=sql")
    assert resp.status_code == 200
    flagged = [s["skill"] for _, s in _skills(resp.json()) if s["have"]]
    assert flagged == ["sql"]


def test_ad22_openapi_ghi_ro_have_lap_lai_va_url_dai(client: TestClient) -> None:
    spec = client.get("/openapi.json").json()
    params = {p["name"]: p for p in spec["paths"][PATH]["get"]["parameters"]}
    text = params["have"]["description"]
    assert "cái cuối" in text
    assert "8 KB" in text


# ---------------------------------------------------------------- FR-24: Backend → Data Engineer với {java, sql, git} (F10)


def test_fr24_doi_tu_backend_sang_data_engineer_giao_cua_ho_so_voi_lo_trinh(
    client: TestClient,
) -> None:
    body = _get(client, role="data_engineer", level="entry", have="java,sql,git")
    data = body["data"]
    flagged = sorted(s["skill"] for _, s in _skills(body) if s["have"])
    assert flagged == ["git", "sql"]
    assert data["have_on_path"] == 2
    assert data["path_size"] == 11
    assert data["have_ignored"] == ["java"]
    assert data["current_stage"] == 1
    assert data["status"] == "ready"


# ---------------------------------------------------------------- F11: toàn vẹn fixture đồ thị


def test_fr22_moi_requires_cua_fixture_la_nut_co_that_va_do_thi_khong_chu_trinh() -> (
    None
):
    raw = json.loads((FIXTURES / "fake_learning_path.json").read_text(encoding="utf-8"))
    for role, entry in raw["roles"].items():
        nodes = entry["skills"]
        codes = [n["skill"] for n in nodes]
        assert len(codes) == len(set(codes)), f"{role}: nút lặp"
        requires = {n["skill"]: n["requires"] for n in nodes}
        for code, needs in requires.items():
            for need in needs:
                assert need in requires, f"{role}.{code} cần {need} nhưng không có nút"
        indegree = {c: len(r) for c, r in requires.items()}
        children: dict[str, list[str]] = defaultdict(list)
        for code, needs in requires.items():
            for need in needs:
                children[need].append(code)
        ready = [c for c, d in indegree.items() if d == 0]
        done = 0
        while ready:
            code = ready.pop()
            done += 1
            for child in children[code]:
                indegree[child] -= 1
                if indegree[child] == 0:
                    ready.append(child)
        assert done == len(requires), f"{role}: đồ thị có chu trình"
