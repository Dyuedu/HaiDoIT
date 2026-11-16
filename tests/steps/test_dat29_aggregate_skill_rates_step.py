"""#101 (DAT.29) — bước `aggregate` ghi `stat_skill_rates`: dày, gắn snapshot và ô, cùng dân số với `stat_cells`."""

from dataclasses import replace
from datetime import date, timedelta

import pytest

from haido_core.steps.common import SnapshotClosedError
from haido_core.vocab.skills import VOCAB_VERSION, load_seed_skills
from tests.steps.conftest import Env, S

SD = date.fromisoformat(S)
CODES = [s.code for s in load_seed_skills()]
PY_DOCKER = "Yêu cầu\nPython, Docker. Python nâng cao."
PY_SQL = "Yêu cầu\nPython, SQL."
ALL_ROWS = "SELECT * FROM haido.stat_skill_rates ORDER BY snapshot_id, role, branch, seniority, years, scope, skill"


def _day(back: int) -> str:
    return (SD - timedelta(days=back)).isoformat()


def _job(title: str = "Backend Dev", description: str | None = PY_DOCKER, company: str = "A", **cols) -> dict:
    return {"title": title, "company": company, "location": "Hà Nội", "description": description, **cols}


def _build(env: Env, scraper_db, jobs: dict[str, dict], source: str = "itviec", day: str = S) -> None:
    for url, cols in jobs.items():
        scraper_db.job(url, source, **cols)
    scraper_db.day(source, day, list(jobs))
    env.ingest(day)
    env.lifecycle(day)
    env.aggregate(day)


def _row(env: Env, role: str, seniority: str, skill: str) -> tuple[int, float]:
    [row] = env.query(
        "SELECT n_with, rate FROM haido.stat_skill_rates WHERE snapshot_id = :d AND role = :r "
        "AND seniority = :l AND skill = :k AND scope = 'vn' AND years = 'any' AND branch = 'all'",
        d=S, r=role, l=seniority, k=skill,
    )  # fmt: skip
    return row[0], row[1]


def _n(env: Env, role: str, seniority: str) -> int:
    [(n,)] = env.query(
        "SELECT n FROM haido.stat_cells WHERE snapshot_id = :d AND role = :r AND seniority = :l "
        "AND scope = 'vn' AND years = 'any'",
        d=S, r=role, l=seniority,
    )  # fmt: skip
    return n


JOBS = {
    "a": _job(),
    "b": _job(description=PY_SQL, company="B"),
    "c": _job(description=None, company="C", job_level="Senior"),
}


def test_dat29_fr9_moi_o_toan_quoc_co_mot_hang_cho_moi_ky_nang_ke_ca_ty_le_0(env: Env, scraper_db) -> None:
    _build(env, scraper_db, JOBS)
    cells = env.query(
        "SELECT role, seniority FROM haido.stat_cells WHERE scope = 'vn' AND years = 'any' ORDER BY 1, 2"
    )
    assert len(cells) == (1 + len(env.rules.roles)) * (1 + len(env.rules.level_options))
    per_cell = env.query(
        "SELECT role, seniority, count(*), count(DISTINCT skill), count(*) FILTER (WHERE rate = 0) "
        "FROM haido.stat_skill_rates GROUP BY role, seniority ORDER BY 1, 2"
    )
    assert [(r[0], r[1]) for r in per_cell] == [tuple(c) for c in cells]
    assert all(r[2] == r[3] == len(CODES) for r in per_cell)
    assert all(r[4] > 0 for r in per_cell)  # có kỹ năng tỷ lệ 0 trong mỗi ô
    assert {r[0] for r in env.query("SELECT DISTINCT skill FROM haido.stat_skill_rates")} == set(CODES)
    assert env.count("stat_skill_rates") == len(cells) * len(CODES)


def test_dat29_fr9_o_khong_co_tin_van_du_hang_voi_ty_le_0(env: Env, scraper_db) -> None:
    scraper_db.run("itviec", S)
    env.ingest()
    env.lifecycle()
    result = env.aggregate()
    assert result.skill_rates == env.count("stat_skill_rates") == (1 + len(env.rules.roles)) * 9 * len(CODES)
    assert env.query("SELECT count(*) FROM haido.stat_skill_rates WHERE rate <> 0 OR n_with <> 0") == [(0,)]


def test_dat29_ad4_moi_hang_mang_snapshot_va_khoa_o_khop_stat_cells(env: Env, scraper_db) -> None:
    _build(env, scraper_db, JOBS)
    assert env.query(
        "SELECT count(*) FROM haido.stat_skill_rates r LEFT JOIN haido.stat_cells c "
        "ON (c.snapshot_id, c.role, c.branch, c.seniority, c.years, c.scope) = "
        "(r.snapshot_id, r.role, r.branch, r.seniority, r.years, r.scope) WHERE c.snapshot_id IS NULL"
    ) == [(0,)]
    assert {str(d) for (d,) in env.query("SELECT DISTINCT snapshot_id FROM haido.stat_skill_rates")} == {S}
    assert env.query("SELECT DISTINCT branch, years, scope FROM haido.stat_skill_rates") == [("all", "any", "vn")]
    assert {v for (v,) in env.query("SELECT DISTINCT vocab_version FROM haido.stat_skill_rates")} == {VOCAB_VERSION}


def test_dat29_fr9_ty_le_bang_n_with_chia_n_cua_stat_cells_o_moi_hang(env: Env, scraper_db) -> None:
    _build(env, scraper_db, JOBS)
    bad = env.query(
        "SELECT count(*) FROM haido.stat_skill_rates r JOIN haido.stat_cells c "
        "ON (c.snapshot_id, c.role, c.branch, c.seniority, c.years, c.scope) = "
        "(r.snapshot_id, r.role, r.branch, r.seniority, r.years, r.scope) "
        "WHERE r.rate <> CASE WHEN c.n = 0 THEN 0 ELSE r.n_with::float8 / c.n END OR r.n_with > c.n"
    )
    assert bad == [(0,)]


def test_dat29_fr9_so_dem_theo_vai_tro_cap_va_luot_nhac_nhieu_lan_tinh_mot(env: Env, scraper_db) -> None:
    _build(env, scraper_db, JOBS)
    assert _n(env, "backend", "all") == 3
    assert _row(env, "backend", "all", "python") == (2, pytest.approx(2 / 3))  # a nhắc Python hai lần vẫn một
    assert _row(env, "backend", "all", "docker") == (1, pytest.approx(1 / 3))
    assert _row(env, "backend", "all", "sql") == (1, pytest.approx(1 / 3))
    assert _row(env, "all", "all", "python")[0] == 2
    assert _row(env, "backend", "senior", "python") == (0, 0.0)  # c không ghi kỹ năng nào
    assert _row(env, "backend", "unknown", "python") == (2, pytest.approx(1.0))
    assert _row(env, "frontend", "all", "python") == (0, 0.0)


def test_dat29_fr9_nhom_entry_dem_cac_cap_thanh_vien(env: Env, scraper_db) -> None:
    jobs = {
        "a": _job(job_level="Fresher"),
        "b": _job(description=PY_SQL, company="B", job_level="Junior"),
        "c": _job(company="C", job_level="Senior"),
    }
    _build(env, scraper_db, jobs)
    assert _n(env, "backend", "entry") == 2
    assert _row(env, "backend", "entry", "python") == (2, 1.0)
    assert _row(env, "backend", "entry", "docker") == (1, 0.5)
    assert _row(env, "backend", "senior", "docker") == (1, 1.0)


def test_dat29_fr9_cua_so_60_ngay_cung_cua_so_cua_n(env: Env, scraper_db) -> None:
    for back, url, company in ((59, "in59", "A"), (60, "out60", "B")):
        _build(env, scraper_db, {url: _job(company=company)}, day=_day(back))
    _build(env, scraper_db, {"today": _job(description=PY_SQL, company="C")})
    assert _n(env, "backend", "all") == 2
    assert _row(env, "backend", "all", "python") == (2, 1.0)
    assert _row(env, "backend", "all", "docker") == (1, 0.5)  # out60 nhắc Docker nhưng ngoài cửa sổ


def test_dat29_dat28_hai_nguon_cung_cum_dem_mot_lan(env: Env, scraper_db) -> None:
    scraper_db.job("https://itviec.test/b", "itviec", **_job(company="FPT"))
    scraper_db.job("https://topcv.test/b", "topcv", **_job(company="Công ty TNHH FPT"))
    scraper_db.day("itviec", S, ["https://itviec.test/b"])
    scraper_db.day("topcv", S, ["https://topcv.test/b"])
    env.ingest()
    env.lifecycle()
    env.aggregate()
    assert _n(env, "backend", "all") == 1
    assert _row(env, "backend", "all", "python") == (1, 1.0)
    assert _row(env, "backend", "all", "docker") == (1, 1.0)


def test_dat29_dat263_tin_nguon_bi_loai_khong_vao_ty_le(env: Env, scraper_db) -> None:
    scraper_db.job("li", "linkedin", **_job(description="Yêu cầu\nPython, Docker, SQL, Linux.", company="L"))
    scraper_db.day("linkedin", S, ["li"])
    _build(env, scraper_db, {"a": _job(description=PY_SQL)})
    assert _n(env, "backend", "all") == 1
    assert _row(env, "backend", "all", "linux") == (0, 0.0)
    assert _row(env, "backend", "all", "docker") == (0, 0.0)
    assert _row(env, "backend", "all", "python") == (1, 1.0)


def test_dat29_fr9_tin_ngoai_it_khong_vao_n_va_khong_vao_ty_le(env: Env, scraper_db) -> None:
    _build(env, scraper_db, {"a": _job(), "x": _job(title="Kế toán tổng hợp", company="X")})
    assert _n(env, "all", "all") == 1
    assert _row(env, "all", "all", "python") == (1, 1.0)


def test_dat29_fr9_chay_lai_khi_s_van_open_ra_cung_hang_khong_nhan_doi(env: Env, scraper_db) -> None:
    _build(env, scraper_db, JOBS)
    first = env.query(ALL_ROWS)
    result = env.aggregate()
    assert env.query(ALL_ROWS) == first
    assert result.skill_rates == len(first)


@pytest.mark.determinism
def test_dat29_fr9_determinism_hai_lan_aggregate_ra_cung_hang(env: Env, scraper_db) -> None:
    _build(env, scraper_db, JOBS)
    first = env.query(ALL_ROWS)
    env.aggregate()
    second = env.query(ALL_ROWS)
    assert first == second and len(first) > 0


@pytest.mark.parametrize("status", ["published", "partial"])
def test_dat29_ad4_snapshot_da_chot_thi_tu_choi_va_khong_ghi(env: Env, scraper_db, status: str) -> None:
    _build(env, scraper_db, JOBS)
    before = env.query(ALL_ROWS)
    with env.write.begin() as conn:
        conn.exec_driver_sql(f"UPDATE haido.snapshots SET status = '{status}'")
    with pytest.raises(SnapshotClosedError, match="đã chốt"):
        env.aggregate(rules=replace(env.rules, config_version="moi"))
    assert env.query(ALL_ROWS) == before


def test_dat29_ad4_loi_sau_khi_ghi_thi_giu_nguyen_hang_cu(env: Env, scraper_db, monkeypatch) -> None:
    from haido_core.db import snapshot_store

    _build(env, scraper_db, JOBS)
    before = env.query(ALL_ROWS)
    real = snapshot_store.replace_stats

    def after_write(*args, **kwargs):
        real(*args, **kwargs)
        raise RuntimeError("giả lập lỗi sau khi ghi")

    monkeypatch.setattr(snapshot_store, "replace_stats", after_write)
    scraper_db.job("d", "itviec", **_job(description="Yêu cầu\nLinux.", company="D"))
    scraper_db.day("itviec", S, [*JOBS, "d"])
    env.ingest()
    env.lifecycle()
    with pytest.raises(RuntimeError):
        env.aggregate()
    assert env.query(ALL_ROWS) == before


def test_dat29_fr9_snapshot_moi_khong_dong_vao_hang_cua_snapshot_da_chot(env: Env, scraper_db) -> None:
    _build(env, scraper_db, {"a": _job()}, day=_day(1))
    with env.write.begin() as conn:
        conn.exec_driver_sql(f"UPDATE haido.snapshots SET status = 'published' WHERE snapshot_id = '{_day(1)}'")
    before = env.query("SELECT * FROM haido.stat_skill_rates WHERE snapshot_id = :d ORDER BY 2,3,4,5,6,7", d=_day(1))
    _build(env, scraper_db, {"b": _job(company="B")})
    assert env.query("SELECT * FROM haido.stat_skill_rates WHERE snapshot_id = :d ORDER BY 2,3,4,5,6,7", d=_day(1)) == before
    assert env.query("SELECT count(*) FROM haido.stat_skill_rates WHERE snapshot_id = :d", d=S) != [(0,)]


def test_dat29_fr9_dung_du_kien_cu_chua_co_ma_ky_nang_thi_ty_le_0_khong_loi(env: Env, scraper_db) -> None:
    _build(env, scraper_db, {"a": _job(description=None)})
    assert _n(env, "backend", "all") == 1
    assert _row(env, "backend", "all", "python") == (0, 0.0)
