"""#93 — phép tính tỷ trọng thành phố của một snapshot (hàm thuần, chưa đụng DB)."""

import math
from datetime import date, timedelta

import pytest

from haido_core.domain.aggregate import CellRow, aggregate_city_shares
from haido_core.domain.population import CountedPosting

S = date(2026, 11, 3)
CITIES = ("ha_noi", "ho_chi_minh", "da_nang", "other", "unknown")
LEVELS = ("intern", "fresher", "junior", "mid", "senior", "lead", "unknown")
ROLES = ("backend", "qa", "other")


def _p(cluster: str, *, role="backend", city="ha_noi", level="junior", back=0) -> CountedPosting:
    return CountedPosting(cluster, S - timedelta(days=back), role, city, level)


def _run(postings, *, roles=ROLES, window=60):
    return aggregate_city_shares(S, postings, roles=roles, cities=CITIES, levels=LEVELS, window_days=window)


def _cell(result, role: str, scope: str) -> CellRow:
    [row] = [c for c in result.cells if (c.role, c.scope) == (role, scope)]
    return row


def _shares(result, role: str) -> dict[str, float]:
    return {s.city: s.share for s in result.shares if s.role == role}


def test_dat20_moi_vai_tro_va_all_co_dung_nam_dong_ke_ca_khi_khong_co_tin() -> None:
    result = _run([])
    assert len(result.shares) == 4 * 5
    for role in ("all", *ROLES):
        assert list(_shares(result, role)) == list(CITIES)
        assert math.isclose(sum(_shares(result, role).values()), 1.0, abs_tol=1e-12)
    # sáu ô mỗi vai trò: năm thành phố cộng toàn quốc, n = 0 vẫn có hàng
    assert len(result.cells) == 4 * 6
    assert all(c.n == 0 and c.seniority_mix == {} for c in result.cells)


def test_dat20_n_bang_0_thi_tong_van_bang_1_voi_dong_unknown_la_1() -> None:
    shares = _shares(_run([]), "qa")
    assert shares["unknown"] == 1.0
    assert all(v == 0.0 for k, v in shares.items() if k != "unknown")


def test_dat20_ty_trong_la_so_tin_cua_thanh_pho_chia_so_tin_toan_quoc_cua_vai_tro() -> None:
    postings = [
        _p("1", city="ha_noi"), _p("2", city="ha_noi"), _p("3", city="da_nang"), _p("4", city="unknown"),
        _p("5", role="qa", city="ho_chi_minh"),
    ]  # fmt: skip
    result = _run(postings)
    assert _shares(result, "backend") == {
        "ha_noi": 0.5, "ho_chi_minh": 0.0, "da_nang": 0.25, "other": 0.0, "unknown": 0.25,
    }  # fmt: skip
    assert _shares(result, "qa")["ho_chi_minh"] == 1.0
    assert _shares(result, "all")["ha_noi"] == 0.4
    assert _shares(result, "all")["ho_chi_minh"] == 0.2


def test_dat20_da_nang_luon_co_dong_va_mau_nho_van_co_so() -> None:
    result = _run([_p(str(i)) for i in range(50)] + [_p("dn", city="da_nang")])
    assert _cell(result, "backend", "da_nang").n == 1
    assert _shares(result, "backend")["da_nang"] == pytest.approx(1 / 51)
    assert _cell(_run([]), "backend", "da_nang").n == 0


def test_dat20_all_dem_moi_tin_it_va_moi_o_luu_n_va_pha_cap_bac() -> None:
    postings = [
        _p("1", level="junior"), _p("2", level="junior"), _p("3", level="senior", role="qa"),
        _p("4", level="unknown", city="da_nang", role="other"),
    ]  # fmt: skip
    result = _run(postings)
    assert _cell(result, "all", "vn").n == 4
    assert _cell(result, "all", "vn").seniority_mix == {"junior": 2, "senior": 1, "unknown": 1}
    assert _cell(result, "backend", "ha_noi").seniority_mix == {"junior": 2}
    assert _cell(result, "all", "da_nang").seniority_mix == {"unknown": 1}
    for cell in result.cells:
        assert sum(cell.seniority_mix.values()) == cell.n


def test_dat20_tin_dem_mot_lan_trong_o_vn_bang_tong_cac_thanh_pho() -> None:
    postings = [_p(str(i), city=CITIES[i % 5], role=ROLES[i % 3]) for i in range(40)]
    result = _run(postings)
    for role in ("all", *ROLES):
        assert _cell(result, role, "vn").n == sum(_cell(result, role, c).n for c in CITIES)
    assert _cell(result, "all", "vn").n == 40


def test_dat20_cua_so_60_ngay_ket_thuc_o_s_gom_ca_s() -> None:
    postings = [_p("a", back=0), _p("b", back=59), _p("c", back=60), _p("d", back=200)]
    assert _cell(_run(postings), "all", "vn").n == 2
    assert _cell(_run(postings, window=61), "all", "vn").n == 3


def test_dat20_ma_la_thanh_pho_hoac_cap_bac_ngoai_danh_sach_thi_bao_loi_khong_doan() -> None:
    with pytest.raises(ValueError, match="thành phố"):
        _run([_p("a", city="hue")])
    with pytest.raises(ValueError, match="cấp bậc"):
        _run([_p("a", level="principal")])


def test_dat20_vai_tro_la_all_hoac_ngoai_danh_sach_vai_tro_thi_khong_vao_o_rieng() -> None:
    # tin có vai trò ngoài danh sách vẫn nằm trong `all`, nhưng khi đó tổng các vai trò nhỏ hơn all
    result = _run([_p("a", role="mobile")])
    assert _cell(result, "all", "vn").n == 1
    assert all(_cell(result, r, "vn").n == 0 for r in ROLES)


@pytest.mark.determinism
def test_dat20_determinism_thu_tu_tin_va_hai_lan_chay_ra_cung_ket_qua() -> None:
    postings = [
        _p(str(i), role=ROLES[i % 3], city=CITIES[i % 5], level=LEVELS[i % 7], back=i % 75) for i in range(300)
    ]
    first = _run(postings)
    assert _run(postings) == first
    assert _run(list(reversed(postings))) == first
    assert [(c.role, c.scope) for c in first.cells][:6] == [("all", c) for c in (*CITIES, "vn")]
