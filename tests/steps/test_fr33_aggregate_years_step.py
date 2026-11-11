"""#280 — bước `aggregate` ghi ô và tỷ trọng thành phố theo số năm kinh nghiệm tối thiểu."""

import math

from tests.steps.conftest import Env, S

CITIES = ["ha_noi", "ho_chi_minh", "da_nang", "other", "unknown"]


def _build(env: Env, scraper_db, jobs: dict[str, dict]) -> None:
    for url, cols in jobs.items():
        scraper_db.job(url, "itviec", **cols)
    scraper_db.day("itviec", S, list(jobs))
    env.ingest()
    env.lifecycle()
    env.aggregate()


def _job(years: str | None, city: str = "Hà Nội", level: str | None = "Junior", title: str = "Backend Dev") -> dict:
    return {"title": title, "location": city, "job_level": level, "years_experience_min": years}


def _cell(env: Env, role: str, level: str, years: str, scope: str) -> tuple[int, int]:
    [row] = env.query(
        "SELECT n, years_unstated FROM haido.stat_cells "
        "WHERE snapshot_id = :d AND role = :r AND seniority = :l AND years = :y AND scope = :s",
        d=S,
        r=role,
        l=level,
        y=years,
        s=scope,
    )
    return tuple(row)


def _shares(env: Env, role: str, level: str, years: str) -> dict[str, float]:
    rows = env.query(
        "SELECT city, share FROM haido.stat_city_shares WHERE role = :r AND seniority = :l AND years = :y",
        r=role,
        l=level,
        y=years,
    )
    return dict(rows)


JOBS = {
    "a": _job("0"),
    "b": _job("1.5", "Hồ Chí Minh"),
    "c": _job("2"),
    "d": _job("3", level="Senior"),
    "e": _job(None),
    "f": _job(None, "Đà Nẵng", level="Senior"),
}


def test_fr33_moi_vai_tro_cap_va_moc_so_nam_co_du_hang(env: Env, scraper_db) -> None:
    scraper_db.run("itviec", S)
    env.ingest()
    env.lifecycle()
    result = env.aggregate()
    roles = 1 + len(env.rules.roles)
    levels = 1 + len(env.rules.level_options)
    years = 1 + len(env.rules.years_options)
    assert (result.cells, result.shares) == (roles * levels * years * 6, roles * levels * years * 5)
    assert {y for (y,) in env.query("SELECT DISTINCT years FROM haido.stat_cells")} == {
        "any",
        *(str(n) for n in env.rules.years_options),
    }


def test_fr33_moc_so_nam_dem_dung_va_years_unstated_dem_tin_khong_ghi(env: Env, scraper_db) -> None:
    _build(env, scraper_db, JOBS)
    assert _cell(env, "backend", "all", "any", "vn") == (6, 2)
    assert _cell(env, "backend", "all", "0", "vn") == (1, 2)
    assert _cell(env, "backend", "all", "1", "vn") == (1, 2)
    assert _cell(env, "backend", "all", "2", "vn") == (3, 2)
    assert _cell(env, "backend", "all", "3", "vn") == (4, 2)
    assert _cell(env, "backend", "entry", "2", "vn") == (3, 1)
    assert _cell(env, "backend", "senior", "3", "vn") == (1, 1)
    assert _cell(env, "backend", "senior", "2", "da_nang") == (0, 1)


def test_fr33_ty_trong_theo_moc_so_nam_cong_lai_bang_1(env: Env, scraper_db) -> None:
    _build(env, scraper_db, JOBS)
    shares = _shares(env, "backend", "all", "2")
    assert sorted(shares) == sorted(CITIES)
    assert math.isclose(sum(shares.values()), 1.0, abs_tol=1e-12)
    assert math.isclose(shares["ha_noi"], 2 / 3) and math.isclose(shares["ho_chi_minh"], 1 / 3)
    assert _shares(env, "backend", "senior", "2")["unknown"] == 1.0
