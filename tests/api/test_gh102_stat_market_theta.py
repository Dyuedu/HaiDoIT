"""#102 (DAT.30) — StatMarket nhóm kỹ năng và ghi `meta.thresholds` bằng θ của phiên bản đã ghi trong snapshot.

Snapshot ghi `theta_version` lúc `aggregate`. Đọc lại không dùng θ hiện hành của cấu hình: đổi `theta_version` hiện hành
sau này không làm số của snapshot cũ đổi nhóm. `theta_version` NULL (snapshot trước đóng băng) đọc là `theta-1`; phiên
bản không có trong sổ đăng ký là dữ liệu hỏng, trả 500.
"""

from dataclasses import replace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

from haido_api.fake_market import FakeMarket
from haido_api.main import create_app
from haido_api.stat_market import StatMarket
from haido_core.config import RulesConfig, ThetaVersion, load_rules
from tests.api.test_dat20_stat_market import _seed as seed_city
from tests.api.test_fr09_skill_roles_stat import _all_roles, _entry
from tests.api.test_fr19_skill_rates_stat import _cell, _snapshot
from tests.api.test_fr37_newcomer_roles_stat import _seed as seed_newcomer
from tests.steps.conftest import S

BASE = load_rules()
TEST_VERSION = ThetaVersion("theta-test", 0.5, 0.15, "2026-11-19", "chỉ dùng trong test")
WITH_TEST = replace(BASE, theta_versions=(*BASE.theta_versions, TEST_VERSION))
"""Cấu hình có thêm phiên bản `theta-test` (θ_core 0.5, θ_common 0.15); hiện hành vẫn là `theta-1` (0.3 và 0.1)."""
CURRENT_TEST = replace(WITH_TEST, theta_version="theta-test", theta_core=0.5, theta_common=0.15)
"""Cấu hình mà phiên bản hiện hành là `theta-test`."""

THETA_1 = {"theta_version": "theta-1", "theta_core": 0.3, "theta_common": 0.1}
THETA_TEST = {"theta_version": "theta-test", "theta_core": 0.5, "theta_common": 0.15}


def _client(engine: Engine, rules: RulesConfig = WITH_TEST) -> TestClient:
    stat = StatMarket(engine_factory=lambda: engine, rules=rules)
    app = create_app(
        {"city_shares": stat, "skill_rates": stat, "newcomer_roles": stat, "learning_path": FakeMarket(), "skill_roles": stat}
    )
    return TestClient(app, raise_server_exceptions=False)


def _set_version(engine: Engine, version: str | None, day: str = S) -> None:
    with engine.begin() as conn:
        conn.execute(text("UPDATE haido.snapshots SET theta_version = :v WHERE snapshot_id = :d"), {"v": version, "d": day})


def _rates(engine: Engine) -> None:
    """java 0.6, python 0.4, sql 0.2, git 0.1, docker 0.05: nhóm khác nhau giữa θ 0.3/0.1 và 0.5/0.15."""
    _snapshot(engine)
    _cell(engine, "backend", "entry", 80, 60, {"java": 36, "python": 24, "sql": 12, "git": 6, "docker": 3})
    _cell(engine, "backend", "all", 500, 400, {"java": 300})


def _groups(body: dict) -> list[tuple[str, str]]:
    return [(r["skill"], r["group"]) for r in body["data"]["rows"]]


def _thresholds(body: dict) -> dict:
    t = body["meta"]["thresholds"]
    assert t["min_sample"] == 30
    return {k: v for k, v in t.items() if k != "min_sample"}


def _skill_rates(client: TestClient) -> dict:
    resp = client.get("/api/v1/skill-rates", params={"role": "backend", "level": "entry"})
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_gh102_ac1_snapshot_ghi_theta_test_thi_nhom_theo_theta_do_khong_theo_theta_hien_hanh(pg_engine: Engine) -> None:
    _rates(pg_engine)
    _set_version(pg_engine, "theta-test")
    body = _skill_rates(_client(pg_engine))  # hiện hành là theta-1
    assert _groups(body) == [("java", "core"), ("python", "common"), ("sql", "common")]  # git 0.1 < 0.15: rare, bị ẩn
    assert _thresholds(body) == THETA_TEST
    assert body["data"]["core_size"] == 1


def test_gh102_ac1_snapshot_ghi_theta_1_van_nhom_theo_theta_1_khi_hien_hanh_da_doi(pg_engine: Engine) -> None:
    _rates(pg_engine)
    _set_version(pg_engine, "theta-1")
    body = _skill_rates(_client(pg_engine, CURRENT_TEST))
    assert _groups(body) == [("java", "core"), ("python", "core"), ("sql", "common"), ("git", "common")]
    assert _thresholds(body) == THETA_1
    assert body["data"]["core_size"] == 2


def test_gh102_ac1_theta_version_null_doc_la_theta_1_du_hien_hanh_da_doi(pg_engine: Engine) -> None:
    _rates(pg_engine)
    _set_version(pg_engine, None)
    body = _skill_rates(_client(pg_engine, CURRENT_TEST))
    assert _groups(body) == [("java", "core"), ("python", "core"), ("sql", "common"), ("git", "common")]
    assert _thresholds(body) == THETA_1


def test_gh102_ac1_theta_version_la_tra_500_chung_khong_co_du_lieu_nhom_va_khong_lo_phien_ban(pg_engine: Engine) -> None:
    _rates(pg_engine)
    _set_version(pg_engine, "theta-ma")
    resp = _client(pg_engine).get("/api/v1/skill-rates", params={"role": "backend", "level": "entry"})
    assert resp.status_code == 500
    body = resp.json()
    assert set(body) == {"error"}  # không có `data` hay `meta`: không dòng nào được nhóm bằng θ khác
    assert body["error"]["code"] == "internal_error"
    for leaked in ("theta-ma", "theta-1", "core", "common"):
        assert leaked not in resp.text  # 500 trả thông báo chung; tên phiên bản chỉ nằm ở RuntimeError (log)


def test_gh102_ac1_theta_version_khong_co_trong_so_dang_ky_nem_runtime_error_nem_ten_phien_ban(pg_engine: Engine) -> None:
    _rates(pg_engine)
    _set_version(pg_engine, "theta-ma")
    stat = StatMarket(engine_factory=lambda: pg_engine, rules=WITH_TEST)
    with pytest.raises(RuntimeError, match="theta-ma"):
        stat.skill_rates(role="backend", level="entry")


def _seed_skill_roles(engine: Engine) -> None:
    _snapshot(engine)
    _entry(engine, "backend", 80, 60, 30)
    _all_roles(engine)


ROUTES = {
    "city_shares": ("/api/v1/city-shares", {"role": "backend"}, lambda e: seed_city(e)),
    "newcomer_roles": ("/api/v1/newcomer-roles", {}, lambda e: seed_newcomer(e, {"backend": {"junior": 40, "mid": 20}})),
    "skill_rates": ("/api/v1/skill-rates", {"role": "backend", "level": "entry"}, _rates),
    "skill_roles": ("/api/v1/skill-roles", {"skill": "python"}, _seed_skill_roles),
}


@pytest.mark.parametrize("route", list(ROUTES))
def test_gh102_ac1_moi_route_stat_ghi_theta_cua_snapshot_vao_meta(pg_engine: Engine, route: str) -> None:
    path, params, seed = ROUTES[route]
    seed(pg_engine)
    client = _client(pg_engine)
    _set_version(pg_engine, None)
    resp = client.get(path, params=params)
    assert resp.status_code == 200, resp.text
    assert _thresholds(resp.json()) == THETA_1  # NULL đọc là theta-1
    _set_version(pg_engine, "theta-test")
    resp = client.get(path, params=params)
    assert resp.status_code == 200, resp.text
    assert _thresholds(resp.json()) == THETA_TEST


@pytest.mark.parametrize("route", list(ROUTES))
def test_gh102_ac1_moi_route_stat_doc_null_la_theta_1_du_hien_hanh_da_doi(pg_engine: Engine, route: str) -> None:
    path, params, seed = ROUTES[route]
    seed(pg_engine)
    client = _client(pg_engine, CURRENT_TEST)  # hiện hành là theta-test (0.5/0.15)
    _set_version(pg_engine, None)
    resp = client.get(path, params=params)
    assert resp.status_code == 200, resp.text
    assert _thresholds(resp.json()) == THETA_1  # NULL là snapshot trước đóng băng, không theo hiện hành
    _set_version(pg_engine, "theta-test")
    resp = client.get(path, params=params)
    assert resp.status_code == 200, resp.text
    assert _thresholds(resp.json()) == THETA_TEST


@pytest.mark.parametrize("route", list(ROUTES))
def test_gh102_ac1_moi_route_stat_tra_500_khi_snapshot_ghi_phien_ban_la(pg_engine: Engine, route: str) -> None:
    path, params, seed = ROUTES[route]
    seed(pg_engine)
    _set_version(pg_engine, "theta-ma")
    resp = _client(pg_engine).get(path, params=params)
    assert resp.status_code == 500
    assert resp.json()["error"]["code"] == "internal_error"
