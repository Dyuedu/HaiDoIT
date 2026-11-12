"""#284 — tin của bảy vai trò mới vào ô của mã riêng, không vào `other`; API đọc được như vai trò cũ."""

from fastapi.testclient import TestClient

from haido_api.fake_market import FakeMarket
from haido_api.main import create_app
from haido_api.stat_market import StatMarket
from tests.steps.conftest import Env, S

JOBS = {
    "ds": ("Data Scientist", "data_scientist"),
    "fs": ("Senior Fullstack Developer", "fullstack"),
    "ba": ("Business Analyst", "ba_po_pm"),
    "sec": ("Penetration Tester", "security"),
    "inf": ("Nhân viên IT Helpdesk", "it_infra"),
    "ux": ("UI/UX Designer", "ui_ux"),
    "gm": ("Unity Game Developer", "game"),
    "gen": ("Software Engineer", "other"),
}


def _n(env: Env, role: str) -> int:
    rows = env.query(
        "SELECT n FROM haido.stat_cells WHERE snapshot_id = :d AND role = :r AND seniority = 'all' "
        "AND years = 'any' AND scope = 'vn'",
        d=S,
        r=role,
    )
    return rows[0][0] if rows else -1


def _build(env: Env, scraper_db) -> None:
    for url, (title, _) in JOBS.items():
        scraper_db.job(url, "itviec", title=title, location="Hà Nội", job_level="Junior")
    for source in env.rules.auto_sources:
        scraper_db.day(source, S, list(JOBS) if source == "itviec" else [])
    env.ingest()
    env.lifecycle()
    env.aggregate()


def test_gh284_moi_vai_tro_moi_co_o_rieng_va_other_chi_con_chuc_danh_chung(env: Env, scraper_db) -> None:
    _build(env, scraper_db)
    for title, code in JOBS.values():
        assert _n(env, code) == 1, (title, code)
    assert _n(env, "all") == len(JOBS)


def test_gh284_vai_tro_moi_co_du_hang_theo_cap_so_nam_pham_vi(env: Env, scraper_db) -> None:
    _build(env, scraper_db)
    per_role = len(env.rules.level_options) + 1  # cộng `all`
    per_role *= len(env.rules.years_options) + 1  # cộng `any`
    per_role *= len(env.rules.always_cities) + 1  # #285: nơi luôn có, cộng `vn` (tin chỉ ở Hà Nội)
    [(count,)] = env.query("SELECT count(*) FROM haido.stat_cells WHERE snapshot_id = :d AND role = 'fullstack'", d=S)
    assert count == per_role


def test_gh284_api_doc_vai_tro_moi_nhu_vai_tro_cu(env: Env, scraper_db) -> None:
    _build(env, scraper_db)
    env.publish()
    app = create_app(
        {
            "city_shares": StatMarket(engine_factory=lambda: env.write, rules=env.rules),
            "skill_rates": FakeMarket(),
            "newcomer_roles": FakeMarket(),
        }
    )
    resp = TestClient(app).get("/api/v1/city-shares", params={"role": "fullstack", "level": "entry", "years": "any"})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["data"]["role"] == "fullstack"
    shares = {r["city"]: r["share"] for r in body["data"]["rows"]}
    assert shares["ha_noi"]["display"] != "shown"  # n = 1 < 30: làm mờ như vai trò cũ
