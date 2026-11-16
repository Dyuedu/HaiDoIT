"""#101 (DAT.29): tỷ lệ kỹ năng của từng ô, dày, đếm theo cụm (AD-5, FR-9)."""

from datetime import date, timedelta

import pytest

from haido_core.domain.aggregate import CellRow
from haido_core.domain.population import CountedPosting
from haido_core.domain.skill_rates import SkillRateRow, aggregate_skill_rates

S = date(2026, 11, 3)
SKILLS = ("docker", "python", "sql")
GROUPS = {"entry": ("intern", "fresher", "junior")}


def _p(cid: str, role: str = "backend", seniority: str = "junior", skills: tuple[str, ...] = (), back: int = 0,
       city: str = "ha_noi") -> CountedPosting:
    return CountedPosting(cid, S - timedelta(days=back), role, city, seniority, None, frozenset(skills))


def _cell(role: str, seniority: str, n: int, scope: str = "vn", years: str = "any") -> CellRow:
    return CellRow(role, scope, n, {}, seniority, years)


def _run(postings, cells) -> tuple[SkillRateRow, ...]:
    return aggregate_skill_rates(S, postings, cells, skills=SKILLS, window_days=60, level_groups=GROUPS,
                                 vocab_version="seed-test")


def _rates(postings, cells) -> dict[tuple[str, str, str], SkillRateRow]:
    return {(r.role, r.seniority, r.skill): r for r in _run(postings, cells)}


def test_dat29_fr9_moi_ky_nang_co_mot_hang_ke_ca_ty_le_0() -> None:
    rows = _rates([_p("a", skills=("python",)), _p("b")], [_cell("backend", "all", 2)])
    assert {k[2] for k in rows} == set(SKILLS)
    assert (rows["backend", "all", "python"].n_with, rows["backend", "all", "python"].rate) == (1, 0.5)
    assert (rows["backend", "all", "docker"].n_with, rows["backend", "all", "docker"].rate) == (0, 0.0)


def test_dat29_fr9_o_n_bang_0_van_du_hang_voi_ty_le_0_khong_chia_cho_0() -> None:
    rows = _rates([], [_cell("backend", "all", 0)])
    assert len(rows) == len(SKILLS)
    assert all(r.n_with == 0 and r.rate == 0.0 for r in rows.values())


def test_dat29_fr9_hai_tin_cung_cum_chi_dem_mot_lan() -> None:
    rows = _rates([_p("a", skills=("python",)), _p("a", skills=("python",))], [_cell("backend", "all", 1)])
    assert rows["backend", "all", "python"].n_with == 1
    assert rows["backend", "all", "python"].rate == 1.0


def test_dat29_dat28_cum_co_tin_nao_nhac_ky_nang_thi_tinh_mot_lan() -> None:
    postings = [_p("a", skills=("python",)), _p("a", skills=("sql",)), _p("b", skills=("python",))]
    rows = _rates(postings, [_cell("backend", "all", 2)])
    assert rows["backend", "all", "python"].n_with == 2
    assert rows["backend", "all", "sql"].n_with == 1


def test_dat29_fr9_cua_so_60_ngay_59_trong_60_ngoai() -> None:
    postings = [_p("in", skills=("python",), back=59), _p("out", skills=("python",), back=60)]
    rows = _rates(postings, [_cell("backend", "all", 1)])
    assert rows["backend", "all", "python"].n_with == 1


def test_dat29_fr9_vai_tro_all_gom_moi_vai_tro_va_vai_tro_khac_khong_lan() -> None:
    postings = [_p("a", "backend", skills=("python",)), _p("b", "data_analyst", skills=("python", "sql"))]
    cells = [_cell("all", "all", 2), _cell("backend", "all", 1), _cell("data_analyst", "all", 1)]
    rows = _rates(postings, cells)
    assert rows["all", "all", "python"].n_with == 2
    assert rows["backend", "all", "sql"].n_with == 0
    assert rows["data_analyst", "all", "sql"].n_with == 1


def test_dat29_fr9_cap_loc_la_cap_tho_nhom_va_all() -> None:
    postings = [
        _p("a", seniority="fresher", skills=("python",)),
        _p("b", seniority="junior", skills=("sql",)),
        _p("c", seniority="senior", skills=("python",)),
    ]
    cells = [_cell("backend", "all", 3), _cell("backend", "entry", 2), _cell("backend", "senior", 1),
             _cell("backend", "fresher", 1)]
    rows = _rates(postings, cells)
    assert rows["backend", "all", "python"].n_with == 2
    assert rows["backend", "entry", "python"].n_with == 1
    assert rows["backend", "entry", "sql"].n_with == 1
    assert rows["backend", "senior", "python"].n_with == 1
    assert rows["backend", "fresher", "sql"].n_with == 0


def test_dat29_fr9_chi_o_toan_quoc_va_so_nam_any() -> None:
    cells = [_cell("backend", "all", 1), _cell("backend", "all", 1, scope="ha_noi"),
             _cell("backend", "all", 1, years="2")]
    rows = _run([_p("a", skills=("python",))], cells)
    assert {(r.scope, r.years) for r in rows} == {("vn", "any")}
    assert len(rows) == len(SKILLS)


def test_dat29_fr9_ma_ngoai_tu_vung_bi_bo_khong_tao_hang() -> None:
    rows = _rates([_p("a", skills=("python", "cobol"))], [_cell("backend", "all", 1)])
    assert {k[2] for k in rows} == set(SKILLS)


def test_dat29_fr9_n_cua_o_khong_khop_dan_so_thi_la_loi() -> None:
    with pytest.raises(ValueError, match="không khớp"):
        _run([_p("a")], [_cell("backend", "all", 5)])


def test_dat29_fr9_hang_mang_vocab_version_thu_tu_on_dinh_va_rate_bang_n_with_chia_n() -> None:
    postings = [_p("a", skills=("sql", "python")), _p("b", skills=("docker",))]
    cells = [_cell("all", "all", 2), _cell("backend", "all", 2)]
    first = _run(postings, cells)
    assert first == _run(list(reversed(postings)), cells)
    assert [(r.role, r.skill) for r in first] == [(r, s) for r in ("all", "backend") for s in SKILLS]
    assert {r.vocab_version for r in first} == {"seed-test"}
    assert all(r.rate == r.n_with / 2 for r in first)
