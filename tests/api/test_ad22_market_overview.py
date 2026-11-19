"""AD-17, AD-22 — `GET /api/v1/market-overview` (#327): toàn cảnh thị trường, mọi tỷ trọng tính ở máy chủ.

Hàm thuần `build_market_overview` dựng `data` và `meta.cells` từ số đếm; nguồn giả và nguồn thật (#328) cùng gọi nó.
"""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from haido_api.main import app
from haido_api.market_overview import (
    OverviewCounts,
    build_market_overview,
    year_buckets,
)
from haido_core.config import load_rules
from haido_core.domain.display_policy import DisplayState

RULES = load_rules()
PATH = "/api/v1/market-overview"
WEB_FIXTURE = Path(__file__).resolve().parents[2] / "web" / "tests" / "fixtures" / "market-overview.json"
LEVELS = ["intern", "fresher", "junior", "mid", "senior", "lead", "unknown"]


def _counts(**over) -> OverviewCounts:
    roles = {"backend": (60, {"junior": 20, "mid": 30, "senior": 10}), "game": (20, {"intern": 15, "mid": 5})}
    roles.update({r: (0, {}) for r in RULES.roles if r not in roles})
    base = {
        "total_n": 80,
        "total_mix": {"intern": 15, "junior": 20, "mid": 35, "senior": 10},
        "entry_n": 35,
        "roles": roles,
        "role_entry": {"backend": 20, "game": 15},
        "places": {"ha_noi": 40, "ho_chi_minh": 30, "da_nang": 4, "hai_phong": 2, "can_tho": 1, "remote": 1, "abroad": 0,
                "unknown": 2},
        "role_places": {"backend": {"ha_noi": 25, "ho_chi_minh": 32}, "game": {"ha_noi": 15, "ho_chi_minh": 5}},
        "years_upto": {0: 5, 1: 20, 2: 35, 3: 50, 5: 60},
        "years_unstated": 12,
    }
    base.update(over)
    return OverviewCounts(**base)


def _by(rows: list, key: str = "code") -> dict:
    return {getattr(r, key): r for r in rows}


def test_ad22_cap_bac_va_ty_le_nguoi_moi_tinh_o_may_chu() -> None:
    data, cells = build_market_overview(_counts(), RULES)
    assert data.levels == LEVELS
    assert data.entry_levels == ["intern", "fresher", "junior"]
    mix = _by(data.level_mix)
    assert mix["mid"].share.value == pytest.approx(35 / 80)
    assert mix["lead"].share.value == 0
    assert mix["unknown"].share.value == 0
    assert data.entry_share.value == pytest.approx(35 / 80)
    assert cells[data.total_cell_id].n == 80
    assert cells[data.entry_cell_id].n == 35


def test_ad22_vai_tro_theo_so_tin_giam_dan_other_cuoi() -> None:
    counts = _counts()
    roles = dict(counts.roles) | {"other": (70, {"mid": 70})}
    data, _ = build_market_overview(_counts(roles=roles), RULES)
    order = [r.role for r in data.roles]
    assert order[:2] == ["backend", "game"]
    assert order[-1] == "other"
    assert set(order) == set(RULES.roles)


def test_ad22_ty_trong_va_ty_le_cua_vai_tro() -> None:
    data, cells = build_market_overview(_counts(), RULES)
    backend = _by(data.roles, "role")["backend"]
    assert backend.share.value == pytest.approx(60 / 80)
    assert backend.entry_share.value == pytest.approx(20 / 60)
    assert _by(backend.level_mix)["mid"].share.value == pytest.approx(30 / 60)
    places = _by(backend.places)
    assert places["ha_noi"].share.value == pytest.approx(25 / 60)
    assert places["ho_chi_minh"].share.value == pytest.approx(32 / 60)
    assert cells[places["ho_chi_minh"].share.cell_id].n == 32


def test_ad22_vai_tro_duoi_nguong_an_ty_le_cap_bac_nhung_van_hien_ty_trong() -> None:
    data, _ = build_market_overview(_counts(), RULES)
    game = _by(data.roles, "role")["game"]
    assert game.entry_share.display is DisplayState.NULL_DATA
    assert game.entry_share.value is None
    assert all(s.share.display is DisplayState.NULL_DATA for s in game.level_mix)
    assert game.share.display is DisplayState.LOW_SAMPLE_SHOWN
    assert game.share.value == pytest.approx(20 / 80)
    empty = _by(data.roles, "role")["mobile"]
    assert empty.share.value == 0
    assert empty.places == [] or all(s.share.value == 0 for s in empty.places)


def test_ad22_noi_lam_viec_gop_tinh_khac() -> None:
    data, cells = build_market_overview(_counts(), RULES)
    assert [p.code for p in data.places] == [
        "ha_noi", "ho_chi_minh", "da_nang", "other_provinces", "remote", "abroad", "unknown",
    ]
    other = _by(data.places)["other_provinces"]
    assert cells[other.share.cell_id].n == 3
    assert other.share.value == pytest.approx(3 / 80)
    assert data.big_cities_share.value == pytest.approx(70 / 80)
    assert cells[data.big_cities_share.cell_id].n == 70


def test_ad22_so_nam_kinh_nghiem_chia_moc_va_cong_lai_bang_tong() -> None:
    assert year_buckets((0, 1, 2, 3, 5)) == ["0", "1", "2", "3", "4-5", "over_5", "none"]
    data, cells = build_market_overview(_counts(), RULES)
    assert [y.code for y in data.years] == ["0", "1", "2", "3", "4-5", "over_5", "none"]
    ns = {y.code: cells[y.share.cell_id].n for y in data.years}
    assert ns == {"0": 5, "1": 15, "2": 15, "3": 15, "4-5": 10, "over_5": 8, "none": 12}
    assert sum(ns.values()) == 80


def test_ad22_so_dem_lech_thi_bao_loi() -> None:
    with pytest.raises(RuntimeError, match="số năm"):
        build_market_overview(_counts(years_upto={0: 5, 1: 3, 2: 35, 3: 50, 5: 60}), RULES)
    with pytest.raises(RuntimeError, match="entry"):
        build_market_overview(_counts(role_entry={"backend": 61, "game": 15}), RULES)


def test_ad22_route_gia_tra_envelope_hop_le() -> None:
    resp = TestClient(app).get(PATH)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    data, meta = body["data"], body["meta"]
    assert data["levels"] == LEVELS
    assert [r["role"] for r in data["roles"]][-1] == "other"
    assert meta["snapshot_date"]
    total = meta["cells"][data["total_cell_id"]]["n"]
    assert sum(meta["cells"][y["share"]["cell_id"]]["n"] for y in data["years"]) == total


def test_ad17_fixture_web_khop_response_market_overview() -> None:
    resp = TestClient(app).get(PATH)
    assert resp.status_code == 200, resp.text
    assert resp.json() == json.loads(WEB_FIXTURE.read_text(encoding="utf-8"))


def test_ad22_thu_hang_do_may_chu_xep() -> None:
    counts = _counts()
    roles = dict(counts.roles) | {"other": (70, {"mid": 70})}
    data, _ = build_market_overview(_counts(roles=roles), RULES)
    # cấp có nhiều tin trước, không gồm "chưa ghi cấp"
    assert data.levels_by_size == ["mid", "junior", "intern", "senior", "fresher", "lead"]
    by_level = {r.level: r.roles for r in data.roles_by_level}
    assert list(by_level) == LEVELS
    assert by_level["intern"][0] == "game"
    assert by_level["mid"][0] == "backend"
    assert by_level["mid"][-1] == "other"
    assert all(set(v) == set(RULES.roles) for v in by_level.values())
    # chỉ vai trò có tỷ lệ người mới hiện được, tỷ lệ cao trước; không gồm "Vai trò khác"
    assert data.roles_by_entry_share == ["backend"]
