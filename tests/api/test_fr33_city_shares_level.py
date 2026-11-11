"""#163 — `GET /api/v1/city-shares?level=`: số theo cấp bậc lọc được, mẫu nhỏ theo n của cấp, nguồn giả."""

import json
from collections.abc import Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, event, text

from haido_api.fake_market import FIXTURE, FakeMarket
from haido_api.main import app, create_app
from haido_api.market_source import UnknownCell
from haido_api.schemas.market import CitySharesData
from haido_api.stat_market import StatMarket
from haido_core.config import load_rules
from haido_core.domain.display_policy import DisplayState, suppression_for
from haido_core.domain.envelope import Envelope
from tests.steps.conftest import S

CITIES = ["ha_noi", "ho_chi_minh", "da_nang", "other", "unknown"]
RULES = load_rules()
LEVELS = ["all", *RULES.level_options]
Counts = dict[str, int]


@pytest.fixture
def statements(pg_engine: Engine) -> Iterator[list[str]]:
    seen: list[str] = []

    def record(conn, cursor, statement, parameters, context, executemany) -> None:
        seen.append(statement)

    event.listen(pg_engine, "before_cursor_execute", record)
    yield seen
    event.remove(pg_engine, "before_cursor_execute", record)


@pytest.fixture
def client(pg_engine: Engine) -> TestClient:
    stat = StatMarket(engine_factory=lambda: pg_engine, rules=RULES)
    return TestClient(create_app({"city_shares": stat, "skill_rates": FakeMarket(), "newcomer_roles": FakeMarket(), "learning_path": FakeMarket()}), raise_server_exceptions=False)


def _seed(engine: Engine, cells: dict[tuple[str, str], Counts], day: str = S, status: str = "published") -> None:
    """Dựng thẳng hàng `stat_*` cho từng (vai trò, cấp lọc) với số tin theo thành phố."""
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO haido.snapshots (snapshot_id, status) VALUES (:d, :s)"), {"d": day, "s": status})
        conn.execute(text("INSERT INTO haido.stat_sources (snapshot_id, source) VALUES (:d, 'itviec')"), {"d": day})
        for (role, level), counts in cells.items():
            total = sum(counts.values())
            for scope in (*CITIES, "vn"):
                n = total if scope == "vn" else counts.get(scope, 0)
                mix = {"junior": n} if n else {}
                conn.execute(
                    text(
                        "INSERT INTO haido.stat_cells (snapshot_id, role, branch, seniority, scope, n, seniority_mix,"
                        " config_version) VALUES (:d, :r, 'all', :l, :sc, :n, CAST(:mix AS jsonb), 'v')"
                    ),
                    {"d": day, "r": role, "l": level, "sc": scope, "n": n, "mix": json.dumps(mix)},
                )
                if scope != "vn":
                    share = n / total if total else (1.0 if scope == "unknown" else 0.0)
                    conn.execute(
                        text(
                            "INSERT INTO haido.stat_city_shares (snapshot_id, role, seniority, city, share) "
                            "VALUES (:d, :r, :l, :sc, :v)"
                        ),
                        {"d": day, "r": role, "l": level, "sc": scope, "v": share},
                    )


SEEDED: dict[tuple[str, str], Counts] = {
    ("backend", "all"): {"ha_noi": 60, "ho_chi_minh": 30, "da_nang": 30, "unknown": 5},
    ("backend", "entry"): {"ha_noi": 40, "ho_chi_minh": 29, "da_nang": 30, "other": 1},
    ("backend", "senior"): {"ha_noi": 20},
    ("backend", "lead"): {},
}


def _get(client: TestClient, **params: str):
    return client.get("/api/v1/city-shares", params={"role": "backend", **params})


def _ok(client: TestClient, **params: str) -> dict:
    resp = _get(client, **params)
    assert resp.status_code == 200, resp.text
    return resp.json()


def _error(resp: Any, status: int, code: str) -> dict:
    assert resp.status_code == status, resp.text
    body = resp.json()["error"]
    assert body["code"] == code
    return body


def _rows(body: dict) -> dict[str, dict]:
    return {r["city"]: r["share"] for r in body["data"]["rows"]}


# ---------------------------------------------------------------- AC 1: mặc định và danh sách cấp


def test_fr33_khong_gui_level_thi_tra_so_cua_moi_cap_nhu_truoc(pg_engine: Engine, client: TestClient) -> None:
    _seed(pg_engine, SEEDED)
    omitted = _ok(client)
    explicit = _ok(client, level="all")
    assert omitted == explicit
    assert omitted["data"]["level"] == "all"
    assert omitted["data"]["total_cell_id"] == "vn.backend"
    assert [r["share"]["cell_id"] for r in omitted["data"]["rows"]] == [f"{c}.backend" for c in CITIES]


def test_fr33_data_level_la_cap_da_dung_va_ma_o_theo_cap(pg_engine: Engine, client: TestClient) -> None:
    _seed(pg_engine, SEEDED)
    body = _ok(client, level="entry")
    assert body["data"]["level"] == "entry"
    assert body["data"]["total_cell_id"] == "vn.backend.entry"
    assert [r["share"]["cell_id"] for r in body["data"]["rows"]] == [f"{c}.backend.entry" for c in CITIES]
    assert set(body["meta"]["cells"]) == {"vn.backend.entry", *(f"{c}.backend.entry" for c in CITIES)}
    Envelope[CitySharesData].model_validate(body)


def test_fr33_moi_cap_trong_config_deu_duoc_nhan_khong_bi_422(pg_engine: Engine, client: TestClient) -> None:
    _seed(pg_engine, SEEDED)
    for level in LEVELS:
        assert _get(client, level=level).status_code in (200, 404), level


@pytest.mark.parametrize("level", ["khong_ton_tai", "Entry", "ALL", "entry,senior", "", "entry-level", "../x"])
def test_fr33_cap_la_tra_422_invalid_query_va_khong_lap_lai_gia_tri(client: TestClient, level: str) -> None:
    error = _error(_get(client, level=level), 422, "invalid_query")
    assert "level" in error["message"]
    assert level == "" or level not in error["message"]


def test_fr33_openapi_liet_ke_cap_hop_le_va_mac_dinh_all() -> None:
    params = {p["name"]: p for p in app.openapi()["paths"]["/api/v1/city-shares"]["get"]["parameters"]}
    assert params["level"]["required"] is False
    assert params["level"]["schema"]["enum"] == LEVELS
    assert params["level"]["schema"]["default"] == "all"
    assert params["role"]["required"] is True


# ---------------------------------------------------------------- AC 2: đổi cấp thì số đổi cùng nhau


def test_fr33_doi_cap_doi_ca_ty_trong_lan_n_cua_o(pg_engine: Engine, client: TestClient) -> None:
    _seed(pg_engine, SEEDED)
    entry, senior, every = (_ok(client, level=level) for level in ("entry", "senior", "all"))
    assert [r["value"] for r in _rows(entry).values()] == pytest.approx([0.4, 0.29, 0.3, 0.01, 0.0])
    assert _rows(senior)["ha_noi"]["value"] == 1.0
    assert entry["meta"]["cells"]["vn.backend.entry"]["n"] == 100
    assert senior["meta"]["cells"]["vn.backend.senior"]["n"] == 20
    assert every["meta"]["cells"]["vn.backend"]["n"] == 125
    for body in (entry, senior, every):
        assert sum(r["value"] for r in _rows(body).values()) == pytest.approx(1.0)
        for row in body["data"]["rows"]:
            assert row["share"]["cell_id"] in body["meta"]["cells"]


def test_fr33_vai_tro_khong_co_tin_o_cap_da_chon_thi_404_unknown_cell_kem_ngay(
    pg_engine: Engine, client: TestClient
) -> None:
    _seed(pg_engine, SEEDED)
    error = _error(_get(client, level="lead"), 404, "unknown_cell")
    assert error["snapshot_date"] == S
    assert "lead" not in error["message"]


def test_fr33_snapshot_moi_chi_co_all_thi_cap_entry_lui_ve_snapshot_cu_co_hang_entry(
    pg_engine: Engine, client: TestClient
) -> None:
    older = "2026-10-27"
    _seed(pg_engine, SEEDED, day=older)
    _seed(pg_engine, {("backend", "all"): SEEDED[("backend", "all")]})
    assert _ok(client, level="entry")["meta"]["snapshot_date"] == older
    assert _ok(client, level="all")["meta"]["snapshot_date"] == S
    assert _ok(client)["meta"]["snapshot_date"] == S


def test_fr33_khong_snapshot_nao_co_hang_cua_cap_thi_unknown_cell_khong_ngay_va_noi_ro_ly_do(
    pg_engine: Engine, client: TestClient
) -> None:
    _seed(pg_engine, {("backend", "all"): SEEDED[("backend", "all")]})
    assert _ok(client)["data"]["level"] == "all"
    error = _error(_get(client, level="entry"), 404, "unknown_cell")
    assert error["snapshot_date"] is None
    assert "chưa" in error["message"].lower() and "cấp bậc" in error["message"]
    assert "vai trò" not in error["message"]


def test_fr33_api_doc_theo_khoa_khong_dung_vao_bang_tin(
    pg_engine: Engine, client: TestClient, statements: list[str]
) -> None:
    _seed(pg_engine, SEEDED)
    statements.clear()
    _ok(client, level="entry")
    touched = " ".join(statements)
    assert "stat_city_shares" in touched and "stat_cells" in touched
    assert "job_" not in touched


# ---------------------------------------------------------------- AC 3: mẫu nhỏ theo n của ô (thành phố, vai trò, cấp)


def test_fr33_thanh_pho_duoi_30_o_cap_da_chon_bi_lam_mo_n_bang_30_thi_khong(
    pg_engine: Engine, client: TestClient
) -> None:
    _seed(pg_engine, SEEDED)
    rows = _rows(_ok(client, level="entry"))
    assert rows["ho_chi_minh"]["display"] == DisplayState.LOW_SAMPLE_SHOWN  # n = 29
    assert rows["da_nang"]["display"] == DisplayState.SHOWN  # n = 30
    assert rows["ha_noi"]["display"] == DisplayState.SHOWN
    assert rows["ho_chi_minh"]["value"] == pytest.approx(0.29)  # mờ nhưng vẫn có số


def test_fr33_mo_theo_n_cua_cap_chu_khong_theo_n_cua_moi_cap(pg_engine: Engine, client: TestClient) -> None:
    _seed(pg_engine, SEEDED)
    every = _rows(_ok(client, level="all"))
    senior = _rows(_ok(client, level="senior"))
    assert every["ho_chi_minh"]["display"] == DisplayState.SHOWN  # n = 30 ở mọi cấp
    assert senior["ho_chi_minh"]["display"] == DisplayState.LOW_SAMPLE_SHOWN  # n = 0 ở senior
    assert senior["ha_noi"]["display"] == DisplayState.LOW_SAMPLE_SHOWN  # n = 20 < 30


def test_fr33_display_do_suppression_for_voi_min_sample_cua_config(pg_engine: Engine) -> None:
    from dataclasses import replace

    _seed(pg_engine, SEEDED)
    strict = replace(RULES, min_sample=41)
    stat = StatMarket(engine_factory=lambda: pg_engine, rules=strict)
    body = TestClient(create_app({"city_shares": stat, "skill_rates": FakeMarket(), "newcomer_roles": FakeMarket(), "learning_path": FakeMarket()})).get(
        "/api/v1/city-shares", params={"role": "backend", "level": "entry"}
    ).json()
    meta = body["meta"]
    assert meta["thresholds"]["min_sample"] == 41
    for row in body["data"]["rows"]:
        n = meta["cells"][row["share"]["cell_id"]]["n"]
        assert row["share"]["display"] == suppression_for("composition_share", n, min_sample=41)


def test_fr33_cap_bac_khong_doi_nguong_theta_va_ghi_chu_pham_vi(pg_engine: Engine, client: TestClient) -> None:
    _seed(pg_engine, SEEDED)
    meta = _ok(client, level="entry")["meta"]
    assert meta["thresholds"] == {"min_sample": 30, "theta_core": 0.3, "theta_common": 0.1}
    assert [n["code"] for n in meta["coverage_notes"]] == [n.code for n in RULES.coverage_notes]
    assert meta["sources"] == ["itviec"]


# ---------------------------------------------------------------- nguồn giả và route


def test_fr33_ban_gia_phuc_vu_entry_va_all_cho_cac_vai_tro_cua_no() -> None:
    fake = FakeMarket()
    for role in ("all", "ai_ml", "backend"):
        for level in ("all", "entry"):
            env = fake.city_shares(role=role, level=level)
            assert env.data.level == level
            assert [r.city for r in env.data.rows] == CITIES
            Envelope[CitySharesData].model_validate(env.model_dump(mode="json"))


def test_fr33_ban_gia_cap_khac_entry_va_all_tra_unknown_cell() -> None:
    fake = FakeMarket()
    for level in ("senior", "unknown", "mid"):
        with pytest.raises(UnknownCell) as exc:
            fake.city_shares(role="backend", level=level)
        assert exc.value.snapshot_date is not None
    with pytest.raises(UnknownCell):
        fake.city_shares(role="khong_co", level="entry")


def test_fr33_ban_gia_entry_co_thanh_pho_mau_nho_va_mau_du_va_o_toan_quoc_khop_cap_entry() -> None:
    fake = FakeMarket()
    env = fake.city_shares(role="ai_ml", level="entry")
    rows = {r.city: r.share for r in env.data.rows}
    assert env.meta.cells["vn.ai_ml.entry"].n == 501
    assert rows["da_nang"].display is DisplayState.LOW_SAMPLE_SHOWN
    assert rows["ha_noi"].display is DisplayState.SHOWN
    for city, stat in rows.items():
        assert stat.cell_id == f"{city}.ai_ml.entry"
        assert stat.value == pytest.approx(env.meta.cells[stat.cell_id].n / 501)
    mix = env.meta.cells["vn.ai_ml.entry"].seniority_mix
    assert set(mix) == {"intern", "fresher", "junior"}


def test_fr33_ban_gia_so_tong_cac_thanh_pho_o_entry_bang_n_toan_quoc() -> None:
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    for role, levels in raw["city_shares"].items():
        for level, entry in levels.items():
            cells = raw["cells"]
            total = cells[entry["total_cell_id"]]["n"]
            assert sum(cells[r["cell_id"]]["n"] for r in entry["rows"]) == total, (role, level)
            assert sum(r["share"] for r in entry["rows"]) == pytest.approx(1.0)
            if level == "entry":
                for r in entry["rows"]:
                    mix = cells[r["cell_id"]]["seniority_mix"]
                    assert set(mix) <= {"intern", "fresher", "junior"}
                    assert sum(mix.values()) == cells[r["cell_id"]]["n"]


def test_fr33_route_chuyen_level_cho_nguon_va_mac_dinh_la_all() -> None:
    seen: list[tuple[str, str]] = []

    class _Records:
        def city_shares(self, *, role: str, level: str) -> Any:
            seen.append((role, level))
            raise UnknownCell("thử", snapshot_date=None)

        def skill_rates(self, *, role: str, level: str) -> Any:
            raise AssertionError("không gọi tới")

    source = _Records()
    test_client = TestClient(create_app({"city_shares": source, "skill_rates": source, "newcomer_roles": FakeMarket(), "learning_path": FakeMarket()}))
    test_client.get("/api/v1/city-shares", params={"role": "ai_ml"})
    test_client.get("/api/v1/city-shares", params={"role": "ai_ml", "level": "entry"})
    assert seen == [("ai_ml", "all"), ("ai_ml", "entry")]


def test_fr33_nguon_giu_nguyen_cho_skill_rates_va_ve_cap_bac_cua_city_shares_khong_lan_sang() -> None:
    client = TestClient(app)
    resp = client.get("/api/v1/skill-rates", params={"role": "backend", "level": "entry"})
    assert resp.status_code == 200
    assert resp.json()["data"]["level"] == "entry"
