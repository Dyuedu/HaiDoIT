"""#163 — tỷ trọng thành phố và ô theo cấp bậc lọc được (hàm thuần, chưa đụng DB)."""

import math
from datetime import date, timedelta

import pytest

from haido_core.domain.aggregate import (
    CellRow,
    CityShareAggregate,
    aggregate_city_shares,
)
from haido_core.domain.population import CountedPosting

S = date(2026, 11, 3)
CITIES = ("ha_noi", "ho_chi_minh", "da_nang", "other", "unknown")
LEVELS = ("intern", "fresher", "junior", "mid", "senior", "lead", "unknown")
OPTIONS = ("entry", "intern", "fresher", "junior", "mid", "senior", "lead", "unknown")
GROUPS = {"entry": ("intern", "fresher", "junior")}
ROLES = ("backend", "qa")


def _p(cluster: str, *, role="backend", city="ha_noi", level="junior", back=0) -> CountedPosting:
    return CountedPosting(cluster, S - timedelta(days=back), role, city, level)


def _run(postings, *, options=OPTIONS, groups=GROUPS, window=60) -> CityShareAggregate:
    return aggregate_city_shares(
        S,
        postings,
        roles=ROLES,
        cities=CITIES,
        levels=LEVELS,
        window_days=window,
        level_options=options,
        level_groups=groups,
    )


def _cell(result: CityShareAggregate, role: str, level: str, scope: str) -> CellRow:
    [row] = [c for c in result.cells if (c.role, c.seniority, c.scope) == (role, level, scope)]
    return row


def _shares(result: CityShareAggregate, role: str, level: str) -> dict[str, float]:
    return {s.city: s.share for s in result.shares if (s.role, s.seniority) == (role, level)}


def test_fr33_moi_vai_tro_va_cap_loc_duoc_co_du_nam_dong_va_sau_o_ke_ca_khi_khong_co_tin() -> None:
    result = _run([])
    levels = ("all", *OPTIONS)
    assert len(result.shares) == 3 * len(levels) * 5
    assert len(result.cells) == 3 * len(levels) * 6
    for role in ("all", *ROLES):
        for level in levels:
            shares = _shares(result, role, level)
            assert list(shares) == list(CITIES)
            assert math.isclose(sum(shares.values()), 1.0, abs_tol=1e-12)
            assert [c.scope for c in result.cells if (c.role, c.seniority) == (role, level)] == [*CITIES, "vn"]


def test_fr33_nhom_entry_la_tong_intern_fresher_junior_va_khong_gom_unknown() -> None:
    postings = [
        _p("1", level="intern"), _p("2", level="fresher"), _p("3", level="fresher"), _p("4", level="junior"),
        _p("5", level="mid"), _p("6", level="unknown"), _p("7", level="senior"),
    ]  # fmt: skip
    result = _run(postings)
    assert _cell(result, "all", "entry", "vn").n == 4
    assert _cell(result, "all", "entry", "vn").seniority_mix == {"intern": 1, "fresher": 2, "junior": 1}
    assert _cell(result, "all", "unknown", "vn").n == 1
    assert _cell(result, "all", "all", "vn").n == 7


def test_fr33_o_cua_mot_cap_don_chi_co_cap_do_va_cong_lai_bang_n() -> None:
    postings = [_p("1", level="mid", city="da_nang"), _p("2", level="mid", city="da_nang"), _p("3", level="lead")]
    result = _run(postings)
    cell = _cell(result, "backend", "mid", "da_nang")
    assert (cell.n, cell.seniority_mix) == (2, {"mid": 2})
    assert _cell(result, "backend", "senior", "vn").seniority_mix == {}
    for c in result.cells:
        assert sum(c.seniority_mix.values()) == c.n
        if c.seniority in LEVELS:
            assert set(c.seniority_mix) <= {c.seniority}
        if c.seniority == "entry":
            assert set(c.seniority_mix) <= set(GROUPS["entry"])


def test_fr33_ty_trong_cua_mot_cap_la_n_thanh_pho_chia_n_toan_quoc_cua_cap_do() -> None:
    postings = [
        _p("1", city="ha_noi", level="junior"), _p("2", city="ha_noi", level="intern"),
        _p("3", city="da_nang", level="fresher"), _p("4", city="unknown", level="junior"),
        _p("5", city="ho_chi_minh", level="senior"), _p("6", city="ho_chi_minh", level="senior"),
        _p("7", city="ho_chi_minh", level="mid", role="qa"),
    ]  # fmt: skip
    result = _run(postings)
    assert _shares(result, "backend", "entry") == {
        "ha_noi": 0.5, "ho_chi_minh": 0.0, "da_nang": 0.25, "other": 0.0, "unknown": 0.25,
    }  # fmt: skip
    assert _shares(result, "backend", "senior")["ho_chi_minh"] == 1.0
    assert _shares(result, "all", "entry")["ha_noi"] == 0.5
    assert _shares(result, "backend", "all")["ho_chi_minh"] == pytest.approx(2 / 6)  # sáu tin backend, hai ở TP.HCM
    assert _shares(result, "all", "mid")["ho_chi_minh"] == 1.0


def test_fr33_cap_khong_co_tin_thi_toan_bo_ty_trong_roi_vao_unknown() -> None:
    result = _run([_p("1", level="junior")])
    shares = _shares(result, "backend", "lead")
    assert shares["unknown"] == 1.0
    assert all(v == 0.0 for k, v in shares.items() if k != "unknown")
    assert _cell(result, "backend", "lead", "vn").n == 0


def test_fr33_cap_all_giong_het_khi_khong_khai_cap_loc_duoc() -> None:
    postings = [_p(str(i), city=CITIES[i % 5], level=LEVELS[i % 7], role=ROLES[i % 2]) for i in range(60)]
    plain = aggregate_city_shares(S, postings, roles=ROLES, cities=CITIES, levels=LEVELS, window_days=60)
    both = _run(postings)
    assert tuple(c for c in both.cells if c.seniority == "all") == plain.cells
    assert tuple(s for s in both.shares if s.seniority == "all") == plain.shares
    assert {c.seniority for c in plain.cells} == {"all"}


def test_fr33_cac_cap_don_cong_lai_bang_all_o_moi_o() -> None:
    postings = [_p(str(i), city=CITIES[i % 5], level=LEVELS[i % 7], role=ROLES[i % 2]) for i in range(90)]
    result = _run(postings)
    for role in ("all", *ROLES):
        for scope in (*CITIES, "vn"):
            by_level = sum(_cell(result, role, level, scope).n for level in LEVELS)
            assert by_level == _cell(result, role, "all", scope).n
            entry = sum(_cell(result, role, level, scope).n for level in GROUPS["entry"])
            assert entry == _cell(result, role, "entry", scope).n


def test_fr33_cua_so_60_ngay_ap_cho_ca_o_theo_cap() -> None:
    postings = [_p("a", back=0), _p("b", back=59), _p("c", back=60), _p("d", back=200)]
    assert _cell(_run(postings), "all", "entry", "vn").n == 2
    assert _cell(_run(postings, window=61), "all", "entry", "vn").n == 3


def test_fr33_cap_loc_duoc_la_ma_la_thi_bao_loi_khong_doan() -> None:
    with pytest.raises(ValueError, match="cấp bậc"):
        _run([], options=(*OPTIONS, "principal"))
    with pytest.raises(ValueError, match="cấp bậc"):
        _run([], groups={"entry": ("intern", "principal")})
    with pytest.raises(ValueError, match="cấp bậc"):
        _run([], options=("all", *OPTIONS))


def test_fr33_thanh_vien_trung_trong_nhom_thi_bao_loi_khong_cong_doi() -> None:
    with pytest.raises(ValueError, match="trùng"):
        _run([_p("c1")], groups={"entry": ("intern", "junior", "junior")})


@pytest.mark.determinism
def test_fr33_determinism_thu_tu_tin_va_hai_lan_chay_ra_cung_ket_qua() -> None:
    postings = [
        _p(str(i), role=ROLES[i % 2], city=CITIES[i % 5], level=LEVELS[i % 7], back=i % 75) for i in range(300)
    ]
    first = _run(postings)
    assert _run(postings) == first
    assert _run(list(reversed(postings))) == first
    scopes = (*CITIES, "vn")
    head = [(c.role, c.seniority, c.scope) for c in first.cells][:12]
    assert head == [("all", "all", s) for s in scopes] + [("all", "entry", s) for s in scopes]
