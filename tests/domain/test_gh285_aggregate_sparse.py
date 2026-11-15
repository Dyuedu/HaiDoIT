"""#285 — tổng hợp chỉ ghi hàng của nơi có tin, cộng nhóm luôn có; tỷ trọng vẫn cộng bằng 1."""

import math
from collections import defaultdict
from datetime import date

from haido_core.domain.aggregate import aggregate_city_shares
from haido_core.domain.population import CountedPosting

S = date(2026, 11, 12)
CITIES = ("ha_noi", "ho_chi_minh", "da_nang", "hai_phong", "ca_mau", "remote", "abroad", "unknown")
ALWAYS = ("ha_noi", "ho_chi_minh", "da_nang", "remote", "abroad", "unknown")


def _post(i: int, city: str, role: str = "backend") -> CountedPosting:
    return CountedPosting(f"c{i}", S, role, city, "junior")


def _run(postings):
    return aggregate_city_shares(
        S, postings, roles=("backend", "qa"), cities=CITIES, levels=("junior", "unknown"), window_days=60,
        always_cities=ALWAYS,
    )


def test_gh285_noi_khong_co_tin_khong_co_hang_nhom_luon_co_thi_co() -> None:
    result = _run([_post(1, "ha_noi"), _post(2, "hai_phong"), _post(3, "remote")])
    backend = {(r.city) for r in result.shares if r.role == "backend" and r.seniority == "all"}
    assert backend == {*ALWAYS, "hai_phong"}
    assert "ca_mau" not in {r.city for r in result.shares}
    scopes = {c.scope for c in result.cells if c.role == "backend" and c.seniority == "all"}
    assert scopes == {*ALWAYS, "hai_phong", "vn"}


def test_gh285_ty_trong_moi_bo_loc_cong_bang_1() -> None:
    result = _run([_post(1, "ha_noi"), _post(2, "hai_phong"), _post(3, "remote"), _post(4, "ca_mau", "qa")])
    sums: dict[tuple, float] = defaultdict(float)
    for r in result.shares:
        sums[(r.role, r.seniority, r.years)] += r.share
    assert all(math.isclose(v, 1.0) for v in sums.values())


def test_gh285_tinh_chi_co_tin_ghi_so_nam_van_tong_hop_duoc_theo_moc() -> None:
    # Lỗi thấy khi chạy bản sao: tỉnh có tin ghi số năm mà không có tin nào không ghi thì không có ô "không ghi số
    # năm" để tra, aggregate ném KeyError.
    with_years = CountedPosting("c1", S, "backend", "hai_phong", "junior", 2.0)
    unstated = CountedPosting("c2", S, "backend", "ha_noi", "junior", None)
    result = aggregate_city_shares(
        S, [with_years, unstated], roles=("backend",), cities=CITIES, levels=("junior", "unknown"), window_days=60,
        years_options=(1, 3), always_cities=ALWAYS,
    )
    hai_phong = {(c.years, c.n, c.years_unstated) for c in result.cells
                 if c.role == "backend" and c.seniority == "all" and c.scope == "hai_phong"}
    assert hai_phong == {("any", 1, 0), ("3", 1, 0)}


def test_gh285_vai_tro_khong_co_tin_chi_co_nhom_luon_co() -> None:
    result = _run([_post(1, "ha_noi")])
    qa = {r.city: r.share for r in result.shares if r.role == "qa" and r.seniority == "all"}
    assert set(qa) == set(ALWAYS)
    assert qa["unknown"] == 1.0
