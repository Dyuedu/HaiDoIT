"""#280 — `GET /api/v1/city-shares?years=`: số theo mốc số năm kinh nghiệm, số tin bị bỏ, mẫu nhỏ, nguồn giả.

Số tin bị bỏ vì không ghi số năm là `n` của ô `data.years_unstated_cell_id` trong `meta.cells`, không phải số trần
trong `data` (AD-17: mọi số trong `data` là `Stat` hoặc mã ô).
"""

import json
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

from haido_api.fake_market import FakeMarket
from haido_api.main import app, create_app
from haido_api.market_source import UnknownCell
from haido_api.schemas.market import CitySharesData
from haido_api.stat_market import StatMarket
from haido_core.config import load_rules
from haido_core.domain.envelope import Envelope
from tests.steps.conftest import S

CITIES = ["ha_noi", "ho_chi_minh", "da_nang", "hai_phong", "unknown"]  # #285: "other" thay bằng một tỉnh
RULES = load_rules()
YEARS = ["any", *(str(n) for n in RULES.years_options)]
Counts = dict[str, int]


@pytest.fixture
def client(pg_engine: Engine) -> TestClient:
    stat = StatMarket(engine_factory=lambda: pg_engine, rules=RULES)
    return TestClient(
        create_app({"city_shares": stat, "skill_rates": FakeMarket(), "newcomer_roles": FakeMarket()}),
        raise_server_exceptions=False,
    )


def _seed(
    engine: Engine,
    cells: dict[tuple[str, str, str], tuple[Counts, int]],
    day: str = S,
) -> None:
    """Dựng hàng `stat_*` cho từng (vai trò, cấp, số năm): số tin theo thành phố và số tin không ghi số năm."""
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO haido.snapshots (snapshot_id, status) VALUES (:d, 'published')"), {"d": day})
        conn.execute(text("INSERT INTO haido.stat_sources (snapshot_id, source) VALUES (:d, 'itviec')"), {"d": day})
        for (role, level, years), (counts, unstated) in cells.items():
            total = sum(counts.values())
            for scope in (*CITIES, "vn"):
                n = total if scope == "vn" else counts.get(scope, 0)
                conn.execute(
                    text(
                        "INSERT INTO haido.stat_cells (snapshot_id, role, branch, seniority, years, scope, n,"
                        " seniority_mix, years_unstated, config_version)"
                        " VALUES (:d, :r, 'all', :l, :y, :sc, :n, CAST(:mix AS jsonb), :u, 'v')"
                    ),
                    {
                        "d": day,
                        "r": role,
                        "l": level,
                        "y": years,
                        "sc": scope,
                        "n": n,
                        "mix": json.dumps({"junior": n} if n else {}),
                        "u": unstated,
                    },
                )
                if scope != "vn":
                    share = n / total if total else (1.0 if scope == "unknown" else 0.0)
                    conn.execute(
                        text(
                            "INSERT INTO haido.stat_city_shares (snapshot_id, role, seniority, years, city, share)"
                            " VALUES (:d, :r, :l, :y, :sc, :v)"
                        ),
                        {"d": day, "r": role, "l": level, "y": years, "sc": scope, "v": share},
                    )


SEEDED: dict[tuple[str, str, str], tuple[Counts, int]] = {
    ("backend", "all", "any"): ({"ha_noi": 60, "ho_chi_minh": 40, "da_nang": 30}, 40),
    ("backend", "all", "2"): ({"ha_noi": 40, "ho_chi_minh": 30, "da_nang": 29}, 40),
    ("backend", "entry", "any"): ({"ha_noi": 30, "ho_chi_minh": 20}, 12),
    ("backend", "entry", "1"): ({"ha_noi": 30, "ho_chi_minh": 5}, 12),
    ("backend", "all", "0"): ({}, 40),
}


def _get(client: TestClient, **params: str):
    return client.get("/api/v1/city-shares", params={"role": "backend", **params})


def _ok(client: TestClient, **params: str) -> dict:
    resp = _get(client, **params)
    assert resp.status_code == 200, resp.text
    return resp.json()


def _rows(body: dict) -> dict[str, dict]:
    return {r["city"]: r["share"] for r in body["data"]["rows"]}


# ---------------------------------------------------------------- AC 1, 2: tham số và mã ô


def test_fr33_khong_gui_years_thi_nhu_any_va_ma_o_khong_doi(pg_engine: Engine, client: TestClient) -> None:
    _seed(pg_engine, SEEDED)
    omitted = _ok(client)
    assert omitted == _ok(client, years="any")
    assert omitted["data"]["years"] == "any"
    assert omitted["data"]["years_unstated_cell_id"] is None
    assert omitted["data"]["total_cell_id"] == "vn.backend"


def test_fr33_moc_so_nam_tra_data_years_va_ma_o_co_hau_to_y(pg_engine: Engine, client: TestClient) -> None:
    _seed(pg_engine, SEEDED)
    body = _ok(client, years="2")
    assert body["data"]["years"] == "2"
    assert body["data"]["total_cell_id"] == "vn.backend.y2"
    assert [r["share"]["cell_id"] for r in body["data"]["rows"]] == [f"{c}.backend.y2" for c in CITIES]
    assert body["meta"]["cells"]["vn.backend.y2"]["n"] == 99
    Envelope[CitySharesData].model_validate(body)


def test_fr33_cap_va_so_nam_cung_nhau_ma_o_co_ca_hai(pg_engine: Engine, client: TestClient) -> None:
    _seed(pg_engine, SEEDED)
    body = _ok(client, level="entry", years="1")
    assert (body["data"]["level"], body["data"]["years"]) == ("entry", "1")
    assert body["data"]["total_cell_id"] == "vn.backend.entry.y1"
    assert set(body["meta"]["cells"]) == {
        "vn.backend.entry.y1",
        "vn.backend.entry.ynone",
        *(f"{c}.backend.entry.y1" for c in CITIES),
    }
    assert _rows(body)["ha_noi"]["value"] == pytest.approx(30 / 35)


@pytest.mark.parametrize("years", ["4", "-1", "1.5", "ANY", "all", "", "1,2", "y1"])
def test_fr33_years_la_tra_422_invalid_query(client: TestClient, years: str) -> None:
    resp = _get(client, years=years)
    assert resp.status_code == 422, resp.text
    assert resp.json()["error"]["code"] == "invalid_query"
    assert "years" in resp.json()["error"]["message"]


def test_fr33_openapi_liet_ke_moc_so_nam_va_mac_dinh_any() -> None:
    params = {p["name"]: p for p in app.openapi()["paths"]["/api/v1/city-shares"]["get"]["parameters"]}
    assert params["years"]["required"] is False
    assert params["years"]["schema"]["enum"] == YEARS
    assert params["years"]["schema"]["default"] == "any"


# ---------------------------------------------------------------- AC 3: số tin bị bỏ


def _unstated(body: dict) -> tuple[str, int]:
    cell_id = body["data"]["years_unstated_cell_id"]
    return cell_id, body["meta"]["cells"][cell_id]["n"]


def test_fr33_years_unstated_la_so_tin_khong_ghi_so_nam_cua_vai_tro_va_cap(pg_engine: Engine, client: TestClient) -> None:
    _seed(pg_engine, SEEDED)
    assert _unstated(_ok(client, years="2")) == ("vn.backend.ynone", 40)
    assert _unstated(_ok(client, level="entry", years="1")) == ("vn.backend.entry.ynone", 12)
    assert _ok(client, level="entry")["data"]["years_unstated_cell_id"] is None


def test_fr33_so_tin_bi_bo_nam_trong_meta_cells_khong_la_so_tran_trong_data(pg_engine: Engine, client: TestClient) -> None:
    _seed(pg_engine, SEEDED)
    body = _ok(client, years="2")
    assert "years_unstated" not in body["data"]
    Envelope[CitySharesData].model_validate(body)


# ---------------------------------------------------------------- AC 4, 5: snapshot và mẫu nhỏ


def test_fr33_thanh_pho_duoi_30_o_moc_so_nam_bi_lam_mo(pg_engine: Engine, client: TestClient) -> None:
    _seed(pg_engine, SEEDED)
    rows = _rows(_ok(client, years="2"))
    assert rows["da_nang"]["display"] == "low_sample_shown"
    assert rows["ho_chi_minh"]["display"] == "shown"
    assert _rows(_ok(client))["da_nang"]["display"] == "shown"


def test_fr33_moc_so_nam_khong_co_tin_thi_unknown_cell_kem_ngay(pg_engine: Engine, client: TestClient) -> None:
    _seed(pg_engine, SEEDED)
    resp = _get(client, years="0")
    assert resp.status_code == 404
    assert resp.json()["error"]["snapshot_date"] == S


def test_fr33_snapshot_moi_chua_co_hang_so_nam_thi_lui_ve_snapshot_co_hang(pg_engine: Engine, client: TestClient) -> None:
    older = "2026-10-27"
    _seed(pg_engine, SEEDED, day=older)
    _seed(pg_engine, {("backend", "all", "any"): SEEDED[("backend", "all", "any")]})
    assert _ok(client, years="2")["meta"]["snapshot_date"] == older
    assert _ok(client)["meta"]["snapshot_date"] == S


def test_fr33_khong_snapshot_nao_co_hang_so_nam_thi_unknown_cell_khong_ngay(pg_engine: Engine, client: TestClient) -> None:
    _seed(pg_engine, {("backend", "all", "any"): SEEDED[("backend", "all", "any")]})
    resp = _get(client, years="3")
    assert resp.status_code == 404
    body = resp.json()["error"]
    assert body["snapshot_date"] is None
    assert "bộ lọc" in body["message"]


# ---------------------------------------------------------------- route và nguồn giả


def test_fr33_route_chuyen_years_cho_nguon_va_mac_dinh_la_any() -> None:
    seen: list[tuple[str, str, str]] = []

    class _Records:
        def city_shares(self, *, role: str, level: str, years: str) -> Any:
            seen.append((role, level, years))
            raise UnknownCell("thử", snapshot_date=None)

    source = _Records()
    test_client = TestClient(create_app({"city_shares": source, "skill_rates": source, "newcomer_roles": FakeMarket()}))
    test_client.get("/api/v1/city-shares", params={"role": "ai_ml"})
    test_client.get("/api/v1/city-shares", params={"role": "ai_ml", "level": "entry", "years": "1"})
    assert seen == [("ai_ml", "all", "any"), ("ai_ml", "entry", "1")]


def test_fr33_ban_gia_co_moc_1_cho_all_entry_va_so_tin_bi_bo() -> None:
    fake = FakeMarket()
    body = fake.city_shares(role="all", level="entry", years="1")
    assert body.data.years == "1"
    assert body.data.total_cell_id == "vn.all.entry.y1"
    assert body.data.years_unstated_cell_id == "vn.all.entry.ynone"
    assert body.meta.cells["vn.all.entry.ynone"].n > 0
    assert fake.city_shares(role="all", level="entry").data.years_unstated_cell_id is None
    with pytest.raises(UnknownCell):
        fake.city_shares(role="backend", level="senior", years="1")
