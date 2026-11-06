"""Hạ tầng kiểm thử dùng chung (Story 1.4).

Test có marker `postgres` cần Postgres thật. URL lấy từ `HAIDO_TEST_DATABASE_URL`, chỉ
chấp nhận host local (cùng luật với Alembic). Mỗi test dựng lại schema `haido` bằng
`alembic upgrade head` và nạp lại bảng của scraper từ `scraper/schema.sql`.
"""

import os
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine import make_url

from haido_core.db.migrations.env import validate_migration_target

ROOT = Path(__file__).resolve().parents[1]
TEST_URL_ENV = "HAIDO_TEST_DATABASE_URL"
SCRAPER_TABLES = ("jobs", "job_observations", "source_runs", "job_content_versions")


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        if "pg_engine" in getattr(item, "fixturenames", ()):
            item.add_marker(pytest.mark.postgres)


@pytest.fixture
def pg_url() -> str:
    url = os.environ.get(TEST_URL_ENV, "").strip()
    if not url:
        if os.environ.get("CI", "").strip().lower() in ("1", "true", "yes"):
            pytest.fail(f"{TEST_URL_ENV} chưa đặt: trong CI test postgres phải chạy thật, không skip.")
        pytest.skip(f"{TEST_URL_ENV} chưa đặt")
    checked = validate_migration_target(url, allow_remote=False)
    db_name = make_url(checked).database or ""
    if not db_name.endswith("_test"):
        pytest.fail(
            f"{TEST_URL_ENV} phải trỏ tới DB có tên kết thúc bằng _test (test sẽ xóa schema haido và bảng scraper); "
            "từ chối chạy."
        )
    return checked


def alembic_config() -> Config:
    cfg = Config()
    cfg.set_main_option("script_location", str(ROOT / "haido_core" / "db" / "migrations"))
    return cfg


@pytest.fixture
def pg_engine(pg_url: str, monkeypatch: pytest.MonkeyPatch) -> Iterator[Engine]:
    engine = create_engine(pg_url)
    scraper_sql = (ROOT / "scraper" / "schema.sql").read_text(encoding="utf-8")
    with engine.begin() as conn:
        conn.exec_driver_sql("DROP SCHEMA IF EXISTS haido CASCADE; DROP TABLE IF EXISTS public.alembic_version")
        conn.exec_driver_sql("DROP TABLE IF EXISTS " + ", ".join(f"public.{t}" for t in SCRAPER_TABLES))
        conn.exec_driver_sql(scraper_sql)
    monkeypatch.setenv("HAIDO_DATABASE_URL", pg_url)
    monkeypatch.delenv("HAIDO_ALLOW_REMOTE_MIGRATION", raising=False)
    command.upgrade(alembic_config(), "head")
    yield engine
    engine.dispose()


@dataclass
class ScraperDb:
    """Nạp dữ liệu giả vào bảng của scraper (nguồn của `ingest`)."""

    engine: Engine

    def run(self, source: str, day: str, *, complete: bool = True, seen: int = 0, error: str | None = None) -> None:
        with self.engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO public.source_runs (source, snapshot_date, listing_complete, seen_count, error) "
                    "VALUES (:s, :d, :c, :n, :e) ON CONFLICT (source, snapshot_date) DO UPDATE SET "
                    "listing_complete = EXCLUDED.listing_complete, seen_count = EXCLUDED.seen_count, "
                    "error = EXCLUDED.error"
                ),
                {"s": source, "d": day, "c": complete, "n": seen, "e": error},
            )

    def observe(self, source: str, day: str, *urls: str) -> None:
        with self.engine.begin() as conn:
            for url in urls:
                conn.execute(
                    text(
                        "INSERT INTO public.job_observations (job_url, snapshot_date, site) VALUES (:u, :d, :s) "
                        "ON CONFLICT DO NOTHING"
                    ),
                    {"u": url, "d": day, "s": source},
                )

    def job(self, url: str, source: str, **cols: str | None) -> None:
        """Ghi đè hàng `jobs` như scraper làm (UPSERT)."""
        values = {"job_url": url, "site": source, **cols}
        names = ", ".join(values)
        marks = ", ".join(f":{k}" for k in values)
        sets = ", ".join(f"{k} = EXCLUDED.{k}" for k in values if k != "job_url")
        with self.engine.begin() as conn:
            conn.execute(
                text(f"INSERT INTO public.jobs ({names}) VALUES ({marks}) ON CONFLICT (job_url) DO UPDATE SET {sets}"),
                values,
            )

    def day(self, source: str, day: str, urls: list[str], *, complete: bool = True) -> None:
        self.run(source, day, complete=complete, seen=len(urls), error=None if complete else "bị chặn")
        self.observe(source, day, *urls)


@pytest.fixture
def scraper_db(pg_engine: Engine) -> ScraperDb:
    return ScraperDb(pg_engine)
