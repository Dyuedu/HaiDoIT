"""#280 — tỷ trọng thành phố và ô theo số năm kinh nghiệm tối thiểu (hàm thuần, chưa đụng DB)."""

import math
from datetime import date, timedelta

from haido_core.domain.aggregate import (
    CellRow,
    CityShareAggregate,
    aggregate_city_shares,
)
from haido_core.domain.population import CountedPosting

S = date(2026, 11, 12)
CITIES = ("ha_noi", "ho_chi_minh", "da_nang", "other", "unknown")
LEVELS = ("intern", "fresher", "junior", "mid", "senior", "lead", "unknown")
OPTIONS = ("entry", "intern", "fresher", "junior", "mid", "senior", "lead", "unknown")
GROUPS = {"entry": ("intern", "fresher", "junior")}
ROLES = ("backend", "qa")
YEARS = (0, 1, 2, 3, 5)


def _p(cluster: str, years: float | None, *, role="backend", city="ha_noi", level="junior", back=0) -> CountedPosting:
    return CountedPosting(cluster, S - timedelta(days=back), role, city, level, years)


def _run(postings, *, years=YEARS, window=60) -> CityShareAggregate:
    return aggregate_city_shares(
        S,
        postings,
        roles=ROLES,
        cities=CITIES,
        levels=LEVELS,
        window_days=window,
        level_options=OPTIONS,
        level_groups=GROUPS,
        years_options=years,
    )


def _cell(result: CityShareAggregate, role: str, level: str, years: str, scope: str) -> CellRow:
    [row] = [c for c in result.cells if (c.role, c.seniority, c.years, c.scope) == (role, level, years, scope)]
    return row


def _shares(result: CityShareAggregate, role: str, level: str, years: str) -> dict[str, float]:
    return {s.city: s.share for s in result.shares if (s.role, s.seniority, s.years) == (role, level, years)}


SAMPLE = [
    _p("a", 0),
    _p("b", 1.5, city="ho_chi_minh"),
    _p("c", 2),
    _p("d", 3, level="senior"),
    _p("e", None),
    _p("f", None, level="senior", city="da_nang"),
]


def test_fr33_moc_n_chi_dem_tin_co_so_nam_toi_thieu_khong_qua_n() -> None:
    result = _run(SAMPLE)
    assert _cell(result, "backend", "all", "2", "vn").n == 3
    assert _cell(result, "backend", "all", "1", "vn").n == 1
    assert _cell(result, "backend", "all", "3", "vn").n == 4
    assert _cell(result, "backend", "all", "5", "vn").n == 4


def test_fr33_moc_0_chi_dem_tin_khong_can_kinh_nghiem() -> None:
    result = _run(SAMPLE)
    assert _cell(result, "backend", "all", "0", "vn").n == 1
    assert _cell(result, "backend", "all", "0", "ha_noi").n == 1


def test_fr33_any_ra_dung_so_nhu_khi_chua_co_bo_loc_so_nam() -> None:
    with_years = _run(SAMPLE)
    without = _run(SAMPLE, years=())
    old = {(c.role, c.seniority, c.scope): c.n for c in without.cells}
    new = {(c.role, c.seniority, c.scope): c.n for c in with_years.cells if c.years == "any"}
    assert new == old
    assert {(s.role, s.seniority, s.city): s.share for s in with_years.shares if s.years == "any"} == {
        (s.role, s.seniority, s.city): s.share for s in without.shares
    }
    assert {c.years for c in without.cells} == {"any"}


def test_fr33_tin_khong_ghi_so_nam_chi_nam_trong_any() -> None:
    result = _run([_p("x", None)])
    assert _cell(result, "backend", "all", "any", "vn").n == 1
    for code in ("0", "1", "2", "3", "5"):
        assert _cell(result, "backend", "all", code, "vn").n == 0


def test_fr33_years_unstated_dem_cum_khong_ghi_so_nam_cua_vai_tro_va_cap() -> None:
    result = _run(SAMPLE)
    for code in ("any", "0", "2", "5"):
        assert _cell(result, "backend", "all", code, "vn").years_unstated == 2
        assert _cell(result, "backend", "entry", code, "vn").years_unstated == 1
        assert _cell(result, "backend", "senior", code, "vn").years_unstated == 1
        assert _cell(result, "backend", "senior", code, "da_nang").years_unstated == 1
        assert _cell(result, "qa", "all", code, "vn").years_unstated == 0


def test_fr33_cap_va_so_nam_loc_cung_nhau() -> None:
    result = _run(SAMPLE)
    assert _cell(result, "backend", "entry", "2", "vn").n == 3
    assert _cell(result, "backend", "senior", "2", "vn").n == 0
    assert _cell(result, "backend", "senior", "3", "vn").n == 1
    assert _cell(result, "backend", "entry", "2", "vn").seniority_mix == {"junior": 3}


def test_fr33_moi_bo_ba_co_du_nam_dong_tong_bang_1_va_n_bang_0_roi_vao_unknown() -> None:
    result = _run(SAMPLE)
    codes = ("any", "0", "1", "2", "3", "5")
    levels = ("all", *OPTIONS)
    assert len(result.shares) == 3 * len(levels) * len(codes) * 5
    assert len(result.cells) == 3 * len(levels) * len(codes) * 6
    for role in ("all", *ROLES):
        for level in levels:
            for code in codes:
                shares = _shares(result, role, level, code)
                assert list(shares) == list(CITIES)
                assert math.isclose(sum(shares.values()), 1.0, abs_tol=1e-12)
    assert _shares(result, "backend", "senior", "2") == {
        "ha_noi": 0.0,
        "ho_chi_minh": 0.0,
        "da_nang": 0.0,
        "other": 0.0,
        "unknown": 1.0,
    }
    assert _shares(result, "backend", "all", "2") == {
        "ha_noi": 2 / 3,
        "ho_chi_minh": 1 / 3,
        "da_nang": 0.0,
        "other": 0.0,
        "unknown": 0.0,
    }


def test_fr33_tin_ngoai_cua_so_khong_vao_moc_so_nam() -> None:
    result = _run([_p("old", 0, back=60), _p("new", 0, back=59)])
    assert _cell(result, "backend", "all", "0", "vn").n == 1


def test_fr33_thu_tu_dau_vao_khong_doi_ket_qua_so_nam() -> None:
    assert _run(SAMPLE) == _run(list(reversed(SAMPLE)))
