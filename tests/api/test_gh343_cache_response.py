"""#343 — cache response trong tiến trình, xóa theo snapshot.

Phần không cần Postgres dùng `FakeMarket` bọc một lớp đếm số lần route gọi vào nguồn. Phần cần Postgres kiểm
`StatMarket.version` và việc snapshot mới được phục vụ ngay ở request kế tiếp.
"""

from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pytest
import yaml
from fastapi.testclient import TestClient
from sqlalchemy import Engine

from haido_api.fake_market import FakeMarket
from haido_api.main import create_app
from haido_api.response_cache import CACHE_ENV, CACHE_HEADER
from haido_api.routes.market import SOURCE_ENV, load_sources
from haido_api.stat_market import StatMarket
from haido_core.config import load_rules
from haido_core.db import snapshot_store
from haido_core.db.snapshot_store import RunValues
from haido_core.steps.aggregate import aggregate_snapshot
from haido_core.steps.publish import publish_snapshot
from tools.bench_skill_rates import _build

DEPLOY = Path(__file__).resolve().parents[2] / "deploy"
OVERVIEW = "/api/v1/market-overview"
CITY = "/api/v1/city-shares"


class Counting:
    """Bọc một nguồn: đếm số lần route gọi vào, và cho đổi `version` từ test."""

    def __init__(self, inner: Any) -> None:
        self.inner = inner
        self.calls = 0
        self.ver = "v1"
        self.fail_version = False

    def version(self) -> str:
        if self.fail_version:
            raise RuntimeError("DB down")
        return self.ver

    def __getattr__(self, name: str) -> Any:
        target = getattr(self.inner, name)

        def call(*args: Any, **kwargs: Any) -> Any:
            self.calls += 1
            return target(*args, **kwargs)

        return call


def _client(src: Counting, **kwargs: Any) -> TestClient:
    return TestClient(create_app(dict.fromkeys(SOURCE_ENV, src), **kwargs))


@pytest.fixture
def src() -> Counting:
    return Counting(FakeMarket())


@pytest.fixture
def client(src: Counting) -> TestClient:
    return _client(src, response_cache=True)


def test_gh343_lan_hai_lay_tu_cache_cung_noi_dung(client: TestClient, src: Counting) -> None:
    first = client.get(OVERVIEW)
    second = client.get(OVERVIEW)
    assert (first.status_code, second.status_code) == (200, 200)
    assert first.headers[CACHE_HEADER] == "MISS"
    assert second.headers[CACHE_HEADER] == "HIT"
    assert second.content == first.content
    assert second.headers["content-type"] == first.headers["content-type"]
    assert src.calls == 1


def test_gh343_thu_tu_tham_so_khong_tach_khoa(client: TestClient, src: Counting) -> None:
    assert client.get(f"{CITY}?role=backend&level=all").headers[CACHE_HEADER] == "MISS"
    assert client.get(f"{CITY}?level=all&role=backend").headers[CACHE_HEADER] == "HIT"
    assert src.calls == 1


def test_gh343_tham_so_khac_la_khoa_khac(client: TestClient, src: Counting) -> None:
    client.get(f"{CITY}?role=backend&level=all")
    assert client.get(f"{CITY}?role=fullstack&level=all").headers[CACHE_HEADER] == "MISS"
    assert src.calls == 2


def test_gh343_snapshot_doi_thi_request_ke_tiep_tinh_lai(client: TestClient, src: Counting) -> None:
    client.get(OVERVIEW)
    src.ver = "v2"
    assert client.get(OVERVIEW).headers[CACHE_HEADER] == "MISS"
    assert client.get(OVERVIEW).headers[CACHE_HEADER] == "HIT"
    assert src.calls == 2


def test_gh343_moi_request_deu_hoi_version(client: TestClient, src: Counting) -> None:
    asked = 0
    real = src.version

    def counted() -> str:
        nonlocal asked
        asked += 1
        return real()

    src.version = counted  # type: ignore[method-assign]
    for _ in range(3):
        client.get(OVERVIEW)
    assert asked == 3


@pytest.mark.parametrize(
    "url",
    [
        "/api/v1/skill-rates?role=backend&level=entry&have=python,sql",
        "/api/v1/learning-path?role=backend&have=python",
        "/api/v1/role-for-title?title=L%E1%BA%ADp%20tr%C3%ACnh%20vi%C3%AAn%20Java",
    ],
)
def test_gh343_khong_cache_du_lieu_nguoi_dung_go(client: TestClient, url: str) -> None:
    first, second = client.get(url), client.get(url)
    assert first.status_code == second.status_code == 200
    assert CACHE_HEADER not in first.headers and CACHE_HEADER not in second.headers


def test_gh343_khong_giu_ban_sao_nao_cua_chuc_danh(client: TestClient) -> None:
    client.get("/api/v1/role-for-title?title=Secret%20Title")
    client.get("/api/v1/skill-rates?role=backend&level=entry&have=python")
    cache = client.app.state.response_cache
    assert all(b"Secret" not in repr(k).encode() and "have" not in repr(k) for k in cache)


@pytest.mark.parametrize(
    ("url", "status"),
    [
        (f"{CITY}?role=khong_co&level=all", 404),  # unknown_cell
        ("/api/v1/skill-roles?skill=khong_co_ma", 404),  # unknown_skill
        (f"{CITY}?role=Backend&level=all", 422),  # sai định dạng mã
    ],
)
def test_gh343_khong_cache_loi(client: TestClient, src: Counting, url: str, status: int) -> None:
    responses = [client.get(url) for _ in range(3)]
    assert [r.status_code for r in responses] == [status] * 3
    assert all(r.headers.get(CACHE_HEADER) != "HIT" for r in responses)


def test_gh343_hoi_version_hong_thi_di_thang_vao_route(client: TestClient, src: Counting) -> None:
    src.fail_version = True
    first, second = client.get(OVERVIEW), client.get(OVERVIEW)
    assert first.status_code == second.status_code == 200
    assert CACHE_HEADER not in second.headers
    assert src.calls == 2


def test_gh343_chi_cache_duong_dan_api_v1_va_get(client: TestClient) -> None:
    assert CACHE_HEADER not in client.get("/openapi.json").headers
    assert client.head(OVERVIEW).headers.get(CACHE_HEADER) != "HIT"


def test_gh343_so_muc_co_tran(src: Counting) -> None:
    client = _client(src, response_cache=True, cache_max_entries=2)
    for role in ("backend", "fullstack", "security"):  # vai trò có số trong fixture giả: response 200
        assert client.get(f"{CITY}?role={role}&level=all").status_code == 200
    assert client.get(f"{CITY}?role=backend&level=all").headers[CACHE_HEADER] == "MISS"
    assert client.get(f"{CITY}?role=security&level=all").headers[CACHE_HEADER] == "HIT"
    assert len(client.app.state.response_cache) <= 2


def test_gh343_mac_dinh_tat(src: Counting, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(CACHE_ENV, raising=False)
    client = _client(src)
    assert CACHE_HEADER not in client.get(OVERVIEW).headers
    assert CACHE_HEADER not in client.get(OVERVIEW).headers
    assert src.calls == 2


def test_gh343_bat_bang_bien_moi_truong(src: Counting, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(CACHE_ENV, "on")
    client = _client(src)
    client.get(OVERVIEW)
    assert client.get(OVERVIEW).headers[CACHE_HEADER] == "HIT"


def test_gh343_fake_market_co_version_khong_doi() -> None:
    market = FakeMarket()
    assert market.version() == market.version()


def _api_env(name: str) -> dict:
    return yaml.safe_load((DEPLOY / name).read_text(encoding="utf-8"))["services"]["api"]["environment"]


def test_gh343_prod_bat_cache() -> None:
    assert str(_api_env("compose.prod.yml").get(CACHE_ENV)) == "on"


def test_gh343_local_cua_ci_giu_mac_dinh() -> None:
    assert CACHE_ENV not in _api_env("compose.local.yml")


def test_gh343_compose_do_mac_dinh_giong_prod_va_tat_duoc() -> None:
    assert _api_env("compose.loadtest.yml").get(CACHE_ENV) == "${HAIDO_RESPONSE_CACHE:-on}"


# --- Cần Postgres ---------------------------------------------------------------------------------------------

DAY = date(2026, 11, 10)


def _publish(engine: Engine, day: date) -> None:
    rules = load_rules()
    with engine.begin() as conn:
        snapshot_store.upsert_runs(conn, day, (RunValues(s, "auto", True, 0, None) for s in rules.auto_sources))
    aggregate_snapshot(day.isoformat(), engine=engine, rules=rules)
    publish_snapshot(day.isoformat(), engine=engine, rules=rules)


def test_gh343_version_chi_doi_khi_snapshot_duoc_chot(pg_engine: Engine, pg_url: str) -> None:
    _build(pg_url, 300, 343, DAY)  # mở ba snapshot DAY-2..DAY, chưa chốt cái nào
    market = StatMarket()
    empty = market.version()
    with pg_engine.begin() as conn:
        snapshot_store.insert_open(conn, DAY + timedelta(days=1))
    assert market.version() == empty, "mở snapshot mới chưa đổi số đọc được"
    _publish(pg_engine, DAY - timedelta(days=1))
    after = market.version()
    assert after != empty
    assert market.version() == after


def test_gh343_snapshot_moi_duoc_phuc_vu_ngay_request_ke_tiep(pg_engine: Engine, pg_url: str) -> None:
    _build(pg_url, 600, 343, DAY)
    older = DAY - timedelta(days=1)
    _publish(pg_engine, older)
    env = {var: "stat" for var in SOURCE_ENV.values()}
    client = TestClient(create_app(load_sources(env), response_cache=True))

    first = client.get(OVERVIEW)
    assert first.status_code == 200
    assert first.json()["meta"]["snapshot_date"] == older.isoformat()
    assert client.get(OVERVIEW).headers[CACHE_HEADER] == "HIT"

    _publish(pg_engine, DAY)
    nxt = client.get(OVERVIEW)
    assert nxt.headers[CACHE_HEADER] == "MISS"
    assert nxt.json()["meta"]["snapshot_date"] == DAY.isoformat()
