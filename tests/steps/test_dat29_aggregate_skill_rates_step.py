"""#101 (DAT.29) — bước `aggregate` ghi `stat_skill_rates`: dày, gắn snapshot và ô, cùng dân số với `stat_cells`."""

from dataclasses import replace
from datetime import date, timedelta

import pytest

from haido_core.steps import aggregate as aggregate_module
from haido_core.steps import ingest as ingest_module
from haido_core.steps.common import SnapshotClosedError, StepError
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


def _edit_facts(env: Env, sql: str) -> None:
    """Sửa dữ kiện đã ghi để dựng dữ kiện cũ: bảng chỉ-thêm có trigger chặn UPDATE, tắt trong lúc dựng."""
    with env.write.begin() as conn:
        conn.exec_driver_sql("ALTER TABLE haido.job_posting_facts DISABLE TRIGGER USER")
        conn.exec_driver_sql(sql)
        conn.exec_driver_sql("ALTER TABLE haido.job_posting_facts ENABLE TRIGGER USER")


def _legacy(env: Env, *urls: str) -> None:
    """Dữ kiện cũ chưa quét kỹ năng: `skills` và `vocab_version` NULL."""
    if not urls:
        return
    _edit_facts(
        env,
        "UPDATE haido.job_posting_facts SET skills = NULL, vocab_version = NULL "
        f"WHERE posting_id IN (SELECT id FROM haido.job_postings WHERE source_url IN ({', '.join(repr(u) for u in urls)}))",
    )


def _build(
    env: Env, scraper_db, jobs: dict[str, dict], source: str = "itviec", day: str = S, legacy: tuple[str, ...] = ()
) -> None:
    for url, cols in jobs.items():
        scraper_db.job(url, source, **cols)
    scraper_db.day(source, day, list(jobs))
    env.ingest(day)
    _legacy(env, *legacy)
    env.lifecycle(day)
    env.aggregate(day)


def _row(env: Env, role: str, seniority: str, skill: str) -> tuple[int, float]:
    [row] = env.query(
        "SELECT n_with, rate FROM haido.stat_skill_rates WHERE snapshot_id = :d AND role = :r "
        "AND seniority = :l AND skill = :k AND scope = 'vn' AND years = 'any' AND branch = 'all'",
        d=S, r=role, l=seniority, k=skill,
    )  # fmt: skip
    return row[0], row[1]


def _scanned(env: Env, role: str, seniority: str) -> int:
    [(n,)] = env.query(
        "SELECT DISTINCT n_scanned FROM haido.stat_skill_rates WHERE snapshot_id = :d AND role = :r "
        "AND seniority = :l AND scope = 'vn' AND years = 'any'",
        d=S, r=role, l=seniority,
    )  # fmt: skip
    return n


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


def test_dat29_d2_ty_le_bang_n_with_chia_n_scanned_va_n_scanned_khong_vuot_n_o_moi_hang(env: Env, scraper_db) -> None:
    _build(env, scraper_db, JOBS, legacy=("c",))
    bad = env.query(
        "SELECT count(*) FROM haido.stat_skill_rates r JOIN haido.stat_cells c "
        "ON (c.snapshot_id, c.role, c.branch, c.seniority, c.years, c.scope) = "
        "(r.snapshot_id, r.role, r.branch, r.seniority, r.years, r.scope) "
        "WHERE r.rate <> CASE WHEN r.n_scanned = 0 THEN 0 ELSE r.n_with::float8 / r.n_scanned END "
        "OR r.n_with > r.n_scanned OR r.n_scanned > c.n"
    )
    assert bad == [(0,)]
    below_n = env.query(
        "SELECT count(DISTINCT (r.role, r.seniority)) FROM haido.stat_skill_rates r JOIN haido.stat_cells c "
        "ON (c.snapshot_id, c.role, c.branch, c.seniority, c.years, c.scope) = "
        "(r.snapshot_id, r.role, r.branch, r.seniority, r.years, r.scope) WHERE r.n_scanned < c.n"
    )
    assert below_n[0][0] > 0  # có ô mà c chưa quét kéo n_scanned xuống dưới n


def test_dat29_d2_so_dem_theo_vai_tro_cap_cum_chua_quet_khong_vao_mau_so(env: Env, scraper_db) -> None:
    _build(env, scraper_db, JOBS, legacy=("c",))  # c: dữ kiện cũ, chưa quét
    assert _n(env, "backend", "all") == 3
    assert _scanned(env, "backend", "all") == 2
    assert _row(env, "backend", "all", "python") == (2, pytest.approx(1.0))  # a nhắc Python hai lần vẫn một; 2/2
    assert _row(env, "backend", "all", "docker") == (1, pytest.approx(1 / 2))
    assert _row(env, "backend", "all", "sql") == (1, pytest.approx(1 / 2))
    assert _row(env, "all", "all", "python")[0] == 2
    assert _n(env, "backend", "senior") == 1 and _scanned(env, "backend", "senior") == 0
    assert _row(env, "backend", "senior", "python") == (0, 0.0)  # cụm duy nhất chưa quét: rate 0, không chia cho 0
    assert _scanned(env, "backend", "unknown") == _n(env, "backend", "unknown") == 2
    assert _row(env, "backend", "unknown", "python") == (2, pytest.approx(1.0))
    assert _row(env, "frontend", "all", "python") == (0, 0.0) and _scanned(env, "frontend", "all") == 0


def test_dat29_d2_quet_khong_thay_gi_van_la_da_quet_nen_nam_trong_mau_so(env: Env, scraper_db) -> None:
    _build(env, scraper_db, JOBS)  # c không có mô tả: ingest ghi skills = {}, đã quét
    assert _n(env, "backend", "all") == _scanned(env, "backend", "all") == 3
    assert _row(env, "backend", "all", "python") == (2, pytest.approx(2 / 3))
    assert _row(env, "backend", "all", "docker") == (1, pytest.approx(1 / 3))
    assert _row(env, "backend", "senior", "python") == (0, 0.0)  # đã quét, không thấy: n_scanned = 1
    assert _scanned(env, "backend", "senior") == 1


def test_dat29_fr9_nhom_entry_dem_cac_cap_thanh_vien(env: Env, scraper_db) -> None:
    jobs = {
        "a": _job(job_level="Fresher"),
        "b": _job(description=PY_SQL, company="B", job_level="Junior"),
        "c": _job(company="C", job_level="Senior"),
    }
    _build(env, scraper_db, jobs)
    assert _n(env, "backend", "entry") == _scanned(env, "backend", "entry") == 2
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


ITVIEC = "https://itviec.test/b"
TOPCV = "https://topcv.test/b"


def _two_sources(env: Env, scraper_db, itviec: str | None, topcv: str | None, legacy: tuple[str, ...] = ()) -> None:
    scraper_db.job(ITVIEC, "itviec", **_job(company="FPT", description=itviec))
    scraper_db.job(TOPCV, "topcv", **_job(company="Công ty TNHH FPT", description=topcv))
    scraper_db.day("itviec", S, [ITVIEC])
    scraper_db.day("topcv", S, [TOPCV])
    env.ingest()
    _legacy(env, *legacy)
    env.lifecycle()
    env.aggregate()


def test_dat29_dat28_hai_nguon_cung_cum_dem_mot_lan(env: Env, scraper_db) -> None:
    _two_sources(env, scraper_db, PY_DOCKER, PY_DOCKER)
    assert _n(env, "backend", "all") == 1
    assert _row(env, "backend", "all", "python") == (1, 1.0)
    assert _row(env, "backend", "all", "docker") == (1, 1.0)


def test_dat29_d1_cum_hai_nguon_tin_dai_dien_khong_co_mo_ta_van_tinh_ky_nang_cua_tin_kia(env: Env, scraper_db) -> None:
    # itviec được ưu tiên làm đại diện; skills của nó là NULL, topcv nhắc Python.
    _two_sources(env, scraper_db, None, "Yêu cầu\nPython.", legacy=(ITVIEC,))
    assert env.query("SELECT count(*) FROM haido.job_posting_facts WHERE skills IS NULL") == [(1,)]
    assert _n(env, "backend", "all") == _scanned(env, "backend", "all") == 1
    assert _row(env, "backend", "all", "python") == (1, 1.0)
    assert _row(env, "backend", "all", "docker") == (0, 0.0)


def test_dat29_d1_ca_hai_nguon_cung_nhac_python_van_la_mot_cum(env: Env, scraper_db) -> None:
    _two_sources(env, scraper_db, "Yêu cầu\nPython, Docker.", "Yêu cầu\nPython, SQL.")
    assert _n(env, "backend", "all") == _scanned(env, "backend", "all") == 1
    assert _row(env, "backend", "all", "python") == (1, 1.0)  # không phải 2
    assert _row(env, "backend", "all", "docker") == (1, 1.0)  # hợp: Docker chỉ ở một nguồn
    assert _row(env, "backend", "all", "sql") == (1, 1.0)


def test_dat29_d1_ca_hai_nguon_chua_quet_thi_cum_khong_vao_mau_so(env: Env, scraper_db) -> None:
    _two_sources(env, scraper_db, PY_DOCKER, PY_DOCKER, legacy=(ITVIEC, TOPCV))
    assert _n(env, "backend", "all") == 1 and _scanned(env, "backend", "all") == 0
    assert _row(env, "backend", "all", "python") == (0, 0.0)


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


def test_dat29_d2_dung_du_kien_cu_chua_quet_thi_khong_vao_mau_so_ty_le_0_khong_loi(env: Env, scraper_db) -> None:
    _build(env, scraper_db, {"a": _job(description=None)}, legacy=("a",))
    assert _n(env, "backend", "all") == 1
    assert _scanned(env, "backend", "all") == 0
    assert _row(env, "backend", "all", "python") == (0, 0.0)


def _vocab_of_facts(env: Env) -> set[str | None]:
    return {v for (v,) in env.query("SELECT DISTINCT vocab_version FROM haido.job_posting_facts")}


def _vocab_of_rates(env: Env) -> set[str]:
    return {v for (v,) in env.query("SELECT DISTINCT vocab_version FROM haido.stat_skill_rates")}


def _ingest_only(env: Env, scraper_db) -> None:
    for url, cols in JOBS.items():
        scraper_db.job(url, "itviec", **cols)
    scraper_db.day("itviec", S, list(JOBS))
    env.ingest()
    env.lifecycle()


def test_dat29_d3_hang_duoc_dong_dau_bang_phien_ban_tu_vung_cua_du_kien(env: Env, scraper_db, monkeypatch) -> None:
    new = replace(ingest_module.load_vocabulary(), version="seed-2099-01-01")
    monkeypatch.setattr(ingest_module, "load_vocabulary", lambda: new)
    monkeypatch.setattr(aggregate_module, "seed_version", lambda: "seed-2099-01-01")
    _ingest_only(env, scraper_db)
    env.aggregate()
    assert _vocab_of_facts(env) == {"seed-2099-01-01"}
    assert _vocab_of_rates(env) == _vocab_of_facts(env)


def test_dat29_d3_phien_ban_dong_dau_la_phien_ban_hien_hanh_khi_khong_doi(env: Env, scraper_db) -> None:
    _build(env, scraper_db, JOBS)
    assert _vocab_of_facts(env) == {VOCAB_VERSION}
    assert _vocab_of_rates(env) == {VOCAB_VERSION}


def test_dat29_d3_tu_choi_khi_du_kien_dem_duoc_mang_hai_phien_ban(env: Env, scraper_db) -> None:
    _build(env, scraper_db, JOBS)
    before = env.query(ALL_ROWS)
    _edit_facts(
        env,
        "UPDATE haido.job_posting_facts SET vocab_version = 'seed-cu' "
        "WHERE posting_id = (SELECT min(id) FROM haido.job_postings)",
    )
    with pytest.raises(StepError, match="Chạy lại `haido ingest`"):
        env.aggregate()
    assert env.query(ALL_ROWS) == before  # không ghi gì


def test_dat29_d3_tu_choi_khi_moi_du_kien_deu_cu_hon_tu_vung_hien_hanh(env: Env, scraper_db) -> None:
    _build(env, scraper_db, JOBS)
    _edit_facts(env, "UPDATE haido.job_posting_facts SET vocab_version = 'seed-cu'")
    with pytest.raises(StepError, match="seed-cu"):
        env.aggregate()


def test_dat29_d3_du_kien_da_quet_ma_khong_ghi_phien_ban_cung_bi_tu_choi(env: Env, scraper_db) -> None:
    _build(env, scraper_db, JOBS)
    _edit_facts(env, "UPDATE haido.job_posting_facts SET vocab_version = NULL")
    with pytest.raises(StepError, match="None"):
        env.aggregate()


def test_dat29_d3_du_kien_chua_quet_khong_chan_viec_dong_dau(env: Env, scraper_db) -> None:
    _build(env, scraper_db, JOBS, legacy=("c",))  # c: skills và vocab_version NULL, các tin khác cùng phiên bản
    assert _vocab_of_facts(env) == {VOCAB_VERSION, None}
    assert _vocab_of_rates(env) == {VOCAB_VERSION}


def test_dat29_d3_du_kien_ngoai_cua_so_hay_ngoai_cum_dem_khong_chan(env: Env, scraper_db) -> None:
    _build(env, scraper_db, {"old": _job(company="Z")}, day=_day(90))
    _build(env, scraper_db, {"x": _job(title="Kế toán tổng hợp", company="X")})
    _edit_facts(env, "UPDATE haido.job_posting_facts SET vocab_version = 'seed-cu'")
    env.aggregate()  # tin 90 ngày trước ngoài cửa sổ, tin ngoài IT không được đếm: không chặn
