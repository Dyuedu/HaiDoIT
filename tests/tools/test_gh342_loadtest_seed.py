"""#342 — `tools/loadtest_seed.py`: DB đo có một snapshot đã công bố, sinh qua các bước thật, và API `stat` trả 200
cho mọi URL mà kịch bản k6 gọi.

Phần kiểm URL không cần Postgres; phần seed cần `HAIDO_TEST_DATABASE_URL` như các test Postgres khác.
"""

import json
from datetime import date
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

from haido_api.main import create_app
from haido_api.routes.market import SOURCE_ENV, load_sources
from tools.loadtest_seed import check_target, seed

PARAMS = json.loads((Path(__file__).resolve().parents[2] / "loadtest" / "k6" / "params.json").read_text(encoding="utf-8"))
DAY = date(2026, 11, 10)


@pytest.mark.parametrize(
    "url",
    [
        "postgresql+psycopg://u:p@db.example.com:5432/haido_test",
        "postgresql+psycopg://u:p@127.0.0.1:5432/haido",
        "postgresql+psycopg://u:p@127.0.0.1:5432/haido_test_backup",
    ],
)
def test_gh342_tu_choi_host_ngoai_hoac_db_khong_ten_test(url: str) -> None:
    with pytest.raises(ValueError):
        check_target(url)


def test_gh342_nhan_db_local_ten_test() -> None:
    url = "postgresql+psycopg://u:p@127.0.0.1:5434/haido_load_test"
    assert check_target(url) == url


def _journey_urls() -> list[str]:
    urls = ["/api/v1/market-overview", "/api/v1/newcomer-roles", "/api/v1/skills"]
    for role in PARAMS["roles"]:
        urls.append(f"/api/v1/skill-rates?role={role}&level=entry")
        urls += [f"/api/v1/city-shares?role={role}&level={level}" for level in PARAMS["levels"]]
    urls += [f"/api/v1/skill-roles?skill={skill}" for skill in PARAMS["skills"]]
    return urls


def test_gh342_seed_cong_bo_mot_snapshot_va_api_stat_tra_200_cho_moi_url(pg_engine: Engine, pg_url: str) -> None:
    result = seed(pg_url, facts=1500, rng_seed=342, day=DAY)
    assert result.snapshot_id == DAY
    assert result.status == "published"
    with pg_engine.connect() as conn:
        rows = conn.execute(text("SELECT snapshot_id, status FROM haido.snapshots WHERE status <> 'open'")).all()
    assert [(r.snapshot_id, r.status) for r in rows] == [(DAY, "published")]

    client = TestClient(create_app(load_sources({env: "stat" for env in SOURCE_ENV.values()})))
    failed = [(url, r.status_code) for url in _journey_urls() if (r := client.get(url)).status_code != 200]
    assert failed == []
