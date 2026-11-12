"""#93 — từ bước thật tới API: ingest, lifecycle, aggregate, publish rồi đọc `GET /api/v1/city-shares`."""

from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from haido_api.fake_market import FakeMarket
from haido_api.main import create_app
from haido_api.stat_market import StatMarket
from tests.steps.conftest import Env, S


def test_dat20_so_tren_api_la_so_aggregate_da_ghi_tu_buoc_that(env: Env, scraper_db) -> None:
    for i, (title, loc) in enumerate(
        [("Backend Dev", "Hà Nội"), ("Java Dev", "Hà Nội"), ("Golang Dev", "Đà Nẵng"), ("QA Tester", "Hồ Chí Minh")]
    ):
        scraper_db.job(f"u{i}", "itviec", title=title, location=loc, job_level="Junior")
    for source in env.rules.auto_sources:
        scraper_db.day(source, S, [f"u{i}" for i in range(4)] if source == "itviec" else [])
    env.ingest()
    env.lifecycle()
    env.aggregate()
    env.publish()
    app = create_app({"city_shares": StatMarket(engine_factory=lambda: env.write, rules=env.rules), "skill_rates": FakeMarket(), "newcomer_roles": FakeMarket()})
    body = TestClient(app).get("/api/v1/city-shares", params={"role": "backend"}).json()
    rows = {r["city"]: r["share"]["value"] for r in body["data"]["rows"]}
    assert rows == {"ha_noi": pytest.approx(2 / 3), "ho_chi_minh": 0.0, "da_nang": pytest.approx(1 / 3), "remote": 0.0, "abroad": 0.0, "unknown": 0.0}
    assert body["meta"]["snapshot_date"] == S and body["meta"]["snapshot_status"] == "published"
    # Sáu nguồn tự động khác chạy ở S nhưng không có tin nào được đếm nên không được liệt kê (#259).
    assert body["meta"]["sources"] == ["itviec"]
    assert body["meta"]["cells"]["vn.backend"]["seniority_mix"] == {"junior": 3}
    all_body = TestClient(app).get("/api/v1/city-shares", params={"role": "all"}).json()
    assert all_body["meta"]["cells"]["vn.all"]["n"] == 4


def test_dat259_dat263_api_liet_ke_nguon_chay_tay_va_khong_dem_linkedin(env: Env, scraper_db) -> None:
    ten_days_ago = (date.fromisoformat(S) - timedelta(days=10)).isoformat()
    scraper_db.job("tc", "topcv", title="Backend Dev", location="Hà Nội")
    scraper_db.job("li", "linkedin", title="Backend Dev", location="Hà Nội")
    scraper_db.job("iv", "itviec", title="Backend Dev", location="Hà Nội")
    scraper_db.day("topcv", ten_days_ago, ["tc"])
    scraper_db.day("linkedin", ten_days_ago, ["li"])
    env.ingest(ten_days_ago)
    for source in env.rules.auto_sources:
        scraper_db.day(source, S, ["iv"] if source == "itviec" else [])
    env.ingest()
    env.lifecycle()
    env.aggregate()
    env.publish()
    app = create_app({"city_shares": StatMarket(engine_factory=lambda: env.write, rules=env.rules), "skill_rates": FakeMarket(), "newcomer_roles": FakeMarket()})
    body = TestClient(app).get("/api/v1/city-shares", params={"role": "all"}).json()
    assert body["meta"]["sources"] == ["itviec", "topcv"]
    assert body["meta"]["cells"]["vn.all"]["n"] == 2  # linkedin không được đếm
    notes = {n["code"]: n["text"] for n in body["meta"]["coverage_notes"]}
    assert notes["n_sources"] == "Dữ liệu chỉ gồm tin tuyển dụng IT đăng online trên 2 nguồn."
