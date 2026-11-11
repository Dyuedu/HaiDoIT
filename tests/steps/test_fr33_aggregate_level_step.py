"""#163 — bước `aggregate` ghi ô và tỷ trọng thành phố theo từng cấp bậc lọc được."""

import math
from dataclasses import replace
from datetime import date, timedelta

import pytest

from haido_core.db import snapshot_store
from tests.steps.conftest import Env, S

SD = date.fromisoformat(S)
CITIES = ["ha_noi", "ho_chi_minh", "da_nang", "other", "unknown"]


def _day(back: int) -> str:
    return (SD - timedelta(days=back)).isoformat()


def _build(env: Env, scraper_db, jobs: dict[str, dict], source: str = "itviec", day: str = S) -> None:
    for url, cols in jobs.items():
        scraper_db.job(url, source, **cols)
    scraper_db.day(source, day, list(jobs))
    env.ingest(day)
    env.lifecycle(day)
    env.aggregate(day)


def _job(level: str | None, city: str = "Hà Nội", title: str = "Backend Dev", **extra: str) -> dict:
    return {"title": title, "location": city, "job_level": level, **extra}


def _n(env: Env, role: str, level: str, scope: str, day: str = S) -> int:
    [(n,)] = env.query(
        "SELECT n FROM haido.stat_cells WHERE snapshot_id = :d AND role = :r AND seniority = :l AND scope = :s"
        " AND years = 'any'",
        d=day,
        r=role,
        l=level,
        s=scope,
    )
    return n


def _mix(env: Env, role: str, level: str, scope: str) -> dict[str, int]:
    [(mix,)] = env.query(
        "SELECT seniority_mix FROM haido.stat_cells WHERE role = :r AND seniority = :l AND scope = :s"
        " AND years = 'any'",
        r=role,
        l=level,
        s=scope,
    )
    return mix


def _shares(env: Env, role: str, level: str) -> dict[str, float]:
    rows = env.query(
        "SELECT city, share FROM haido.stat_city_shares WHERE role = :r AND seniority = :l AND years = 'any'",
        r=role,
        l=level,
    )
    return dict(rows)


MIXED = {
    "a": _job("Intern", "Hà Nội"),
    "b": _job("Fresher", "Hà Nội"),
    "c": _job("Junior", "Đà Nẵng"),
    "d": _job("Junior", "Hồ Chí Minh"),
    "e": _job("Mid", "Hà Nội"),
    "f": _job("Senior", "Hồ Chí Minh"),
    "g": _job("Lead", "Hồ Chí Minh"),
    "h": _job(None, "Hà Nội"),
}


def test_fr33_moi_vai_tro_va_cap_loc_duoc_co_du_hang_ke_ca_khi_khong_co_tin(env: Env, scraper_db) -> None:
    scraper_db.run("itviec", S)
    env.ingest()
    env.lifecycle()
    result = env.aggregate()
    roles = ["all", *env.rules.roles]
    levels = ["all", *env.rules.level_options]
    years = 1 + len(env.rules.years_options)  # #280: mỗi cấp có `any` và từng mốc số năm
    assert (result.cells, result.shares) == (
        len(roles) * len(levels) * years * 6,
        len(roles) * len(levels) * years * 5,
    )
    assert env.count("stat_cells") == result.cells
    assert env.count("stat_city_shares") == result.shares
    for role in roles:
        for level in levels:
            shares = _shares(env, role, level)
            assert sorted(shares) == sorted(CITIES)
            assert math.isclose(sum(shares.values()), 1.0, abs_tol=1e-12)


def test_fr33_nhom_entry_la_tong_intern_fresher_junior_va_khong_gom_unknown(env: Env, scraper_db) -> None:
    _build(env, scraper_db, MIXED)
    assert _n(env, "backend", "all", "vn") == 8
    assert _n(env, "backend", "entry", "vn") == 4
    assert _mix(env, "backend", "entry", "vn") == {"intern": 1, "fresher": 1, "junior": 2}
    assert _n(env, "backend", "unknown", "vn") == 1
    assert _n(env, "backend", "intern", "vn") + _n(env, "backend", "fresher", "vn") + _n(
        env, "backend", "junior", "vn"
    ) == _n(env, "backend", "entry", "vn")


def test_fr33_o_cap_don_va_ty_trong_cua_cap_do_chi_dem_tin_cua_cap_do(env: Env, scraper_db) -> None:
    _build(env, scraper_db, MIXED)
    assert _n(env, "backend", "junior", "da_nang") == 1
    assert _mix(env, "backend", "junior", "vn") == {"junior": 2}
    assert _shares(env, "backend", "junior") == {
        "ha_noi": 0.0, "ho_chi_minh": 0.5, "da_nang": 0.5, "other": 0.0, "unknown": 0.0,
    }  # fmt: skip
    assert _shares(env, "backend", "entry") == {
        "ha_noi": 0.5, "ho_chi_minh": 0.25, "da_nang": 0.25, "other": 0.0, "unknown": 0.0,
    }  # fmt: skip
    assert _shares(env, "all", "senior")["ho_chi_minh"] == 1.0
    assert _shares(env, "backend", "all")["ha_noi"] == pytest.approx(4 / 8)


def test_fr33_cap_khong_co_tin_thi_n_bang_0_va_ty_trong_roi_vao_unknown(env: Env, scraper_db) -> None:
    _build(env, scraper_db, {"a": _job("Junior")})
    assert _n(env, "backend", "lead", "vn") == 0
    shares = _shares(env, "backend", "lead")
    assert shares["unknown"] == 1.0 and sum(shares.values()) == 1.0


def test_fr33_cap_all_khong_doi_so_voi_truoc_khi_co_bo_loc(env: Env, scraper_db) -> None:
    _build(env, scraper_db, MIXED)
    assert _mix(env, "all", "all", "vn") == {
        "intern": 1, "fresher": 1, "junior": 2, "mid": 1, "senior": 1, "lead": 1, "unknown": 1,
    }  # fmt: skip
    [(branch,)] = env.query("SELECT DISTINCT branch FROM haido.stat_cells")
    assert branch == "all"


def test_fr33_chay_lai_khi_s_van_open_ghi_de_khong_nhan_doi_hang_theo_cap(env: Env, scraper_db) -> None:
    _build(env, scraper_db, MIXED)
    before = (env.count("stat_cells"), env.count("stat_city_shares"))
    env.aggregate()
    assert (env.count("stat_cells"), env.count("stat_city_shares")) == before


def test_fr33_cum_cheo_nguon_dem_mot_lan_o_cap_cua_tin_dai_dien(env: Env, scraper_db) -> None:
    scraper_db.job("https://itviec.test/b", "itviec", **_job("Junior", company="FPT"))
    scraper_db.job("https://topcv.test/b", "topcv", **_job("Senior", company="Công ty TNHH FPT"))
    scraper_db.day("itviec", S, ["https://itviec.test/b"])
    scraper_db.day("topcv", S, ["https://topcv.test/b"])
    env.ingest()
    env.lifecycle()
    env.aggregate()
    assert _n(env, "all", "all", "vn") == 1
    assert _n(env, "all", "entry", "vn") == 1  # đại diện là ITviec: Junior
    assert _n(env, "all", "senior", "vn") == 0


def test_fr33_cua_so_60_ngay_ap_cho_ca_cap_loc_duoc_va_nguon_bi_loai_van_bi_loai(env: Env, scraper_db) -> None:
    for back, url in ((59, "in59"), (60, "out60")):
        scraper_db.job(url, "itviec", **_job("Junior"))
        scraper_db.day("itviec", _day(back), [url])
        env.ingest(_day(back))
    scraper_db.job("li", "linkedin", **_job("Junior"))
    scraper_db.day("linkedin", S, ["li"])
    scraper_db.job("today", "itviec", **_job("Junior"))
    scraper_db.day("itviec", S, ["today"])
    env.ingest()
    env.lifecycle()
    env.aggregate()
    assert _n(env, "all", "entry", "vn") == 2  # in59 và today; out60 ngoài cửa sổ; linkedin bị loại
    assert _n(env, "all", "junior", "vn") == 2


def test_fr33_nhom_lay_tu_config_khong_viet_cung_trong_ma(env: Env, scraper_db) -> None:
    _build(env, scraper_db, MIXED)
    assert _n(env, "backend", "entry", "vn") == 4
    env.aggregate(rules=replace(env.rules, level_groups={"entry": ("junior",)}))
    assert _n(env, "backend", "entry", "vn") == 2
    assert _mix(env, "backend", "entry", "vn") == {"junior": 2}


def test_fr33_loi_giua_chung_thi_giu_nguyen_hang_theo_cap_cu(env: Env, scraper_db, monkeypatch) -> None:
    _build(env, scraper_db, MIXED)
    cells = "SELECT * FROM haido.stat_cells ORDER BY role, seniority, years, scope"
    shares = "SELECT * FROM haido.stat_city_shares ORDER BY role, seniority, years, city"
    before = env.query(cells), env.query(shares)
    real = snapshot_store.replace_stats

    def after_write(*args, **kwargs):
        real(*args, **kwargs)
        raise RuntimeError("giả lập lỗi sau khi ghi")

    monkeypatch.setattr(snapshot_store, "replace_stats", after_write)
    with pytest.raises(RuntimeError):
        env.aggregate(rules=replace(env.rules, level_groups={"entry": ("junior",)}))
    assert (env.query(cells), env.query(shares)) == before


def test_fr33_danh_sach_nguon_cua_snapshot_giu_nguyen(env: Env, scraper_db) -> None:
    _build(env, scraper_db, MIXED)
    assert env.query("SELECT source FROM haido.stat_sources ORDER BY source") == [("itviec",)]


@pytest.mark.determinism
def test_fr33_determinism_hai_lan_aggregate_ra_cung_hang_theo_cap(env: Env, scraper_db) -> None:
    _build(
        env,
        scraper_db,
        {
            f"u{i}": _job(
                ("Junior", "Senior", None, "Intern", "Lead")[i % 5],
                ("Hà Nội", "Hồ Chí Minh", "Đà Nẵng", "Cần Thơ", None)[i % 5],
                ("Backend Dev", "QA Tester", "Mobile Android", "DevOps Engineer")[i % 4],
            )
            for i in range(41)
        },
    )
    cells = "SELECT * FROM haido.stat_cells ORDER BY snapshot_id, role, branch, seniority, years, scope"
    shares = "SELECT * FROM haido.stat_city_shares ORDER BY snapshot_id, role, seniority, years, city"
    first = env.query(cells), env.query(shares)
    env.aggregate()
    assert (env.query(cells), env.query(shares)) == first
    roles = len(env.rules.roles) + 1
    levels = len(env.rules.level_options) + 1
    levels *= len(env.rules.years_options) + 1  # #280: mỗi cấp có `any` và từng mốc số năm
    assert len(first[0]) == roles * levels * 6 and len(first[1]) == roles * levels * 5
