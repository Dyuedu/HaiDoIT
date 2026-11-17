"""AD-17, AD-7 — #103: response chứa số luôn có `meta`, kể cả khi mọi route đọc nguồn `stat`.

`test_ad17_routes.py` đã duyệt mọi route dưới `/api/v1` với nguồn giả. Ở đây cùng danh sách route đó chạy với nguồn
`stat` trên một snapshot dựng bằng hàng `stat_*`: route có số thật phải trả `{data, meta}`; route chưa có số thật (nguồn
`stat` chưa cài) trả lỗi chuẩn, không có `data` và không có số.
"""

from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

from haido_api.main import create_app
from haido_api.stat_market import StatMarket
from haido_core.config import load_rules
from tests.api.test_ad17_routes import SAMPLE_QUERY
from tests.api.test_fr19_skill_rates_stat import _cell, _snapshot
from tests.steps.conftest import S

RULES = load_rules()
REAL = {"/api/v1/city-shares", "/api/v1/skill-rates", "/api/v1/newcomer-roles"}


def _stat_client(engine: Engine) -> TestClient:
    stat = StatMarket(engine_factory=lambda: engine, rules=RULES)
    app = create_app({op: stat for op in ("city_shares", "skill_rates", "newcomer_roles", "learning_path", "skill_roles")})
    return TestClient(app, raise_server_exceptions=False)


def _seed(engine: Engine) -> None:
    _snapshot(engine)
    _cell(engine, "ai_ml", "entry", 80, 60, {"python": 40, "sql": 10})
    _cell(engine, "ai_ml", "all", 300, 250, {"python": 200, "sql": 60})
    _cell(engine, "ai_ml", "all", 100, 0, {}, scope="ha_noi")
    _cell(engine, "ai_ml", "entry", 30, 0, {}, scope="ha_noi")
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO haido.stat_city_shares (snapshot_id, role, seniority, years, city, share) "
                "VALUES (:d, 'ai_ml', 'all', 'any', 'ha_noi', 1.0), (:d, 'ai_ml', 'entry', 'any', 'ha_noi', 1.0)"
            ),
            {"d": S},
        )


def test_ad17_103_moi_route_co_so_nguon_stat_tra_data_va_meta(pg_engine: Engine) -> None:
    _seed(pg_engine)
    client = _stat_client(pg_engine)
    for path in sorted(REAL):
        resp = client.get(path, params=SAMPLE_QUERY[path])
        assert resp.status_code == 200, (path, resp.text)
        body = resp.json()
        assert set(body) == {"data", "meta"}, path
        assert body["meta"]["snapshot_date"] == S and body["meta"]["cells"], path


def test_ad17_103_route_chua_co_so_that_tra_loi_chuan_khong_co_data(pg_engine: Engine) -> None:
    _seed(pg_engine)
    client = _stat_client(pg_engine)
    for path in sorted(set(SAMPLE_QUERY) - REAL):
        resp = client.get(path, params=SAMPLE_QUERY[path])
        assert resp.status_code == 404, (path, resp.text)
        body = resp.json()
        assert set(body) == {"error"}, path
        assert body["error"]["code"] == "unknown_cell", path
