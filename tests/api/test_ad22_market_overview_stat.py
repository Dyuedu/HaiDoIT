"""AD-7, AD-17, AD-22 — số thật của toàn cảnh thị trường (#328), đọc từ `stat_cells` của snapshot đã công bố.

Không bảng mới: số tin theo vai trò, cấp, nơi và số năm đều là `n` của các ô `aggregate` đã ghi.
"""

import json

from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

from haido_api.fake_market import FakeMarket
from haido_api.main import create_app
from haido_api.stat_market import StatMarket
from haido_core.config import load_rules
from tests.steps.conftest import S

PATH = "/api/v1/market-overview"
RULES = load_rules()


def _client(engine: Engine) -> TestClient:
    fake = FakeMarket()
    stat = StatMarket(engine_factory=lambda: engine, rules=RULES)
    sources = {"city_shares": fake, "skill_rates": fake, "newcomer_roles": stat, "learning_path": fake,
               "skill_roles": fake, "posting_check": fake}  # fmt: skip
    return TestClient(create_app(sources), raise_server_exceptions=False)


def _cell(conn, role: str, seniority: str, n: int, mix: dict[str, int], *, scope: str = "vn", years: str = "any",
          unstated: int = 0) -> None:  # fmt: skip
    conn.execute(
        text(
            "INSERT INTO haido.stat_cells (snapshot_id, role, branch, seniority, years, scope, n, seniority_mix, "
            "years_unstated, config_version) "
            "VALUES (:d, :r, 'all', :s, :y, :sc, :n, CAST(:mix AS jsonb), :u, 'v')"
        ),
        {"d": S, "r": role, "s": seniority, "y": years, "sc": scope, "n": n, "mix": json.dumps(mix), "u": unstated},
    )


def _seed(engine: Engine) -> None:
    """Hai vai trò có tin: backend 60 (HN 25, HCM 32, Đà Nẵng 3), game 20 (HN 15, HCM 5)."""
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO haido.snapshots (snapshot_id, status, sources_failed) VALUES (:d, 'published', '{}')"),
                     {"d": S})  # fmt: skip
        conn.execute(text("INSERT INTO haido.stat_sources (snapshot_id, source) VALUES (:d, 'itviec')"), {"d": S})
        conn.execute(
            text("INSERT INTO haido.stat_city_shares (snapshot_id, role, seniority, years, city, share) "
                 "VALUES (:d, 'all', 'all', 'any', 'ha_noi', 1.0)"), {"d": S})  # fmt: skip
        _cell(conn, "all", "all", 80, {"intern": 15, "junior": 20, "mid": 35, "senior": 10})
        _cell(conn, "all", "entry", 35, {"intern": 15, "junior": 20})
        _cell(conn, "backend", "all", 60, {"junior": 20, "mid": 30, "senior": 10})
        _cell(conn, "backend", "entry", 20, {"junior": 20})
        _cell(conn, "game", "all", 20, {"intern": 15, "mid": 5})
        _cell(conn, "game", "entry", 15, {"intern": 15})
        for scope, n in {"ha_noi": 40, "ho_chi_minh": 37, "da_nang": 3}.items():
            _cell(conn, "all", "all", n, {}, scope=scope)
        for role, places in {"backend": {"ha_noi": 25, "ho_chi_minh": 32, "da_nang": 3},
                             "game": {"ha_noi": 15, "ho_chi_minh": 5}}.items():  # fmt: skip
            for scope, n in places.items():
                _cell(conn, role, "all", n, {}, scope=scope)
        for years, n in {"0": 5, "1": 20, "2": 35, "3": 50, "5": 60}.items():
            _cell(conn, "all", "all", n, {}, years=years, unstated=12)


def test_ad22_ban_that_doc_o_da_cong_bo(pg_engine: Engine) -> None:
    _seed(pg_engine)
    resp = _client(pg_engine).get(PATH)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    data, cells = body["data"], body["meta"]["cells"]
    assert body["meta"]["snapshot_date"] == S
    assert cells[data["total_cell_id"]]["n"] == 80
    roles = {r["role"]: r for r in data["roles"]}
    assert [r["role"] for r in data["roles"]][:2] == ["backend", "game"]
    assert roles["backend"]["share"]["value"] == 60 / 80
    assert roles["backend"]["entry_share"]["value"] == 20 / 60
    hcm = next(p for p in roles["backend"]["places"] if p["code"] == "ho_chi_minh")
    assert cells[hcm["share"]["cell_id"]]["n"] == 32
    places = {p["code"]: cells[p["share"]["cell_id"]]["n"] for p in data["places"]}
    assert places["ha_noi"] == 40 and places["other_provinces"] == 0
    years = {y["code"]: cells[y["share"]["cell_id"]]["n"] for y in data["years"]}
    assert years == {"0": 5, "1": 15, "2": 15, "3": 15, "4-5": 10, "over_5": 8, "none": 12}
    assert data["big_cities_share"]["value"] == 77 / 80


def test_ad22_chua_co_snapshot_thi_404(pg_engine: Engine) -> None:
    resp = _client(pg_engine).get(PATH)
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "unknown_cell"
