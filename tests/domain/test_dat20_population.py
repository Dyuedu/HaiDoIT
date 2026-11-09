"""#93 — phép 3 `population`: dân số của ô, đếm theo cụm trong cửa sổ ngày kết thúc ở S."""

from datetime import date, timedelta

import pytest

from haido_core.domain.population import ClusterPopulation, CountedPosting
from haido_core.domain.registry import CellKey, PopulationRequest

S = date(2026, 11, 3)


def _p(cluster: str, days_back: int, *, role="backend", city="ha_noi", level="junior") -> CountedPosting:
    return CountedPosting(cluster, S - timedelta(days=days_back), role, city, level)


def _ask(pop: ClusterPopulation, *, role="all", branch=None, seniority=None, scope="vn", window=60) -> int:
    key = CellKey(S.isoformat(), role, branch, seniority, scope)
    result = pop.population(PopulationRequest(cell=key, window_days=window))
    assert isinstance(result, int)
    return result


def test_dat20_cua_so_60_ngay_gom_s_tru_59_den_s_khong_phai_61_ngay() -> None:
    pop = ClusterPopulation([_p("a", 0), _p("b", 59), _p("c", 60), _p("d", 61)])
    # S - 59 và S nằm trong; S - 60 (ngày thứ 61) và xa hơn nằm ngoài.
    assert _ask(pop) == 2


def test_dat20_tin_sau_s_khong_duoc_dem() -> None:
    pop = ClusterPopulation([_p("a", 0), _p("b", -1)])
    assert _ask(pop) == 1


def test_dat20_cua_so_la_tham_so_khong_viet_cung() -> None:
    pop = ClusterPopulation([_p("a", 0), _p("b", 1), _p("c", 2)])
    assert _ask(pop, window=1) == 1
    assert _ask(pop, window=2) == 2
    assert _ask(pop, window=3) == 3


@pytest.mark.parametrize("bad", [0, -5])
def test_dat20_cua_so_khong_hop_le_thi_bao_loi(bad: int) -> None:
    with pytest.raises(ValueError, match="window_days"):
        _ask(ClusterPopulation([]), window=bad)


def test_dat20_vai_tro_all_dem_moi_tin_it_vai_tro_cu_the_chi_dem_dung_vai_tro() -> None:
    pop = ClusterPopulation([_p("a", 0, role="backend"), _p("b", 0, role="qa"), _p("c", 0, role="other")])
    assert _ask(pop, role="all") == 3
    assert _ask(pop, role="backend") == 1
    assert _ask(pop, role="other") == 1
    assert _ask(pop, role="mobile") == 0


def test_dat20_pham_vi_vn_dem_moi_thanh_pho_pham_vi_thanh_pho_loc_dung_thanh_pho() -> None:
    pop = ClusterPopulation(
        [_p("a", 0, city="ha_noi"), _p("b", 0, city="da_nang"), _p("c", 0, city="unknown"), _p("d", 0, city="da_nang")]
    )
    assert _ask(pop, scope="vn") == 4
    assert _ask(pop, scope="da_nang") == 2
    assert _ask(pop, scope="ho_chi_minh") == 0


def test_dat20_pham_vi_thanh_pho_khong_bao_gio_tra_ve_so_toan_quoc() -> None:
    pop = ClusterPopulation([_p("a", 0, city="ha_noi")])
    assert _ask(pop, scope="da_nang") == 0  # không "quay về" toàn quốc khi thành phố rỗng


def test_dat20_cap_bac_loc_dung_va_none_hoac_all_la_khong_loc() -> None:
    pop = ClusterPopulation([_p("a", 0, level="junior"), _p("b", 0, level="senior"), _p("c", 0, level="junior")])
    assert _ask(pop, seniority="junior") == 2
    assert _ask(pop, seniority="senior") == 1
    assert _ask(pop, seniority=None) == 3
    assert _ask(pop, seniority="all") == 3


def test_dat20_nhanh_none_hoac_all_la_khong_loc_nhanh_cu_the_thi_tu_choi() -> None:
    pop = ClusterPopulation([_p("a", 0)])
    assert _ask(pop, branch=None) == _ask(pop, branch="all") == 1
    with pytest.raises(ValueError, match="nhánh"):
        _ask(pop, branch="spring")


def test_dat20_moi_tin_la_mot_cum_va_hai_tin_cung_cum_chi_dem_mot_lan() -> None:
    own = ClusterPopulation([_p("a", 0), _p("b", 0)])
    assert _ask(own) == 2
    joined = ClusterPopulation([_p("a", 0), _p("a", 3), _p("b", 0)])
    assert _ask(joined) == 2


def test_dat20_lo_tra_ve_tuple_cung_do_dai_va_mot_yeu_cau_tra_mot_so() -> None:
    pop = ClusterPopulation([_p("a", 0, role="qa"), _p("b", 0, role="backend"), _p("c", 0, role="backend")])
    requests = [
        PopulationRequest(CellKey(S.isoformat(), role, None, None, "vn"), 60) for role in ("all", "backend", "qa", "ai_ml")
    ]
    assert pop.population(requests) == (3, 2, 1, 0)
    assert pop.population(tuple(requests)) == (3, 2, 1, 0)
    assert pop.population([]) == ()


def test_dat20_thu_tu_tin_dau_vao_khong_doi_ket_qua() -> None:
    postings = [_p(str(i), i % 70, role="backend" if i % 2 else "qa", city="ha_noi" if i % 3 else "da_nang") for i in range(200)]
    forward = ClusterPopulation(postings)
    backward = ClusterPopulation(list(reversed(postings)))
    for role in ("all", "backend", "qa"):
        for scope in ("vn", "ha_noi", "da_nang"):
            assert _ask(forward, role=role, scope=scope) == _ask(backward, role=role, scope=scope)
