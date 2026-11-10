"""AD-4 — schema `haido`: snapshot, lượt chạy, tin, dữ kiện, quan sát, vòng đời (Story 1.4)."""

import pytest
from alembic import command
from alembic.script import ScriptDirectory
from sqlalchemy import Engine, exc, text

from haido_core.db import tables
from tests.conftest import alembic_config

TABLES = {
    "snapshots",
    "pipeline_runs",
    "job_postings",
    "job_posting_facts",
    "job_observations",
    "stat_job_lifecycle",
    "stat_cells",
    "stat_city_shares",
    "stat_sources",
}


def _columns(engine: Engine, table: str) -> set[str]:
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT column_name FROM information_schema.columns WHERE table_schema='haido' AND table_name=:t"),
            {"t": table},
        )
        return {r[0] for r in rows}


def _seed(engine: Engine) -> None:
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO haido.snapshots (snapshot_id) VALUES ('2026-11-01')"))
        conn.execute(
            text(
                "INSERT INTO haido.pipeline_runs (snapshot_id, source, mode, success, seen_count) "
                "VALUES ('2026-11-01', 'itviec', 'auto', true, 1)"
            )
        )
        conn.execute(text("INSERT INTO haido.job_postings (source, source_url) VALUES ('itviec', 'u1')"))
        conn.execute(
            text(
                "INSERT INTO haido.job_posting_facts (posting_id, snapshot_id, title) "
                "SELECT id, '2026-11-01', 'Dev' FROM haido.job_postings"
            )
        )
        conn.execute(
            text(
                "INSERT INTO haido.job_observations (posting_id, snapshot_id, pipeline_run_id) "
                "SELECT p.id, '2026-11-01', r.id FROM haido.job_postings p, haido.pipeline_runs r"
            )
        )


def test_ad4_upgrade_downgrade_mot_head_va_xoa_sach_schema(pg_engine: Engine) -> None:
    assert len(ScriptDirectory.from_config(alembic_config()).get_heads()) == 1
    with pg_engine.connect() as conn:
        found = {
            r[0]
            for r in conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='haido'"))
        }
    assert found == TABLES

    command.downgrade(alembic_config(), "base")
    with pg_engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM pg_namespace WHERE nspname='haido'")).scalar_one() == 0
    command.upgrade(alembic_config(), "head")


def test_ad4_cot_dung_thiet_ke_va_khong_co_cot_van_ban_jd(pg_engine: Engine) -> None:
    assert _columns(pg_engine, "snapshots") == {"snapshot_id", "status", "opened_at", "closed_at", "sources_failed"}
    assert _columns(pg_engine, "pipeline_runs") == {
        "id", "snapshot_id", "source", "mode", "success", "seen_count", "error",
    }  # fmt: skip
    assert _columns(pg_engine, "job_postings") == {"id", "source", "source_url"}
    assert _columns(pg_engine, "job_posting_facts") == {
        "posting_id", "snapshot_id", "title", "company", "location_text", "experience_level", "job_level",
    }  # fmt: skip
    assert _columns(pg_engine, "job_observations") == {"posting_id", "snapshot_id", "pipeline_run_id"}
    assert _columns(pg_engine, "stat_job_lifecycle") == {
        "snapshot_id", "posting_id", "times_seen", "first_seen", "last_seen",
        "repost_count", "absent", "in_window", "config_version",
    }  # fmt: skip


def test_ad4_tables_py_khop_voi_schema_that(pg_engine: Engine) -> None:
    assert {t.name for t in tables.metadata.tables.values()} == TABLES
    for table in tables.metadata.tables.values():
        assert table.schema == "haido"
        assert {c.name for c in table.columns} == _columns(pg_engine, table.name)


def test_ad4_trang_thai_snapshot_chi_open_published_partial(pg_engine: Engine) -> None:
    with pg_engine.begin() as conn:
        conn.execute(text("INSERT INTO haido.snapshots (snapshot_id) VALUES ('2026-11-01')"))
        assert conn.execute(text("SELECT status FROM haido.snapshots")).scalar_one() == "open"
    for status in ("published", "partial"):
        with pg_engine.begin() as conn:
            conn.execute(text("UPDATE haido.snapshots SET status=:s"), {"s": status})
    with pytest.raises(exc.IntegrityError), pg_engine.begin() as conn:
        conn.execute(text("UPDATE haido.snapshots SET status='closed'"))


def test_ad4_mode_cua_luot_chay_chi_auto_hoac_manual(pg_engine: Engine) -> None:
    with pg_engine.begin() as conn:
        conn.execute(text("INSERT INTO haido.snapshots (snapshot_id) VALUES ('2026-11-01')"))
    with pytest.raises(exc.IntegrityError), pg_engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO haido.pipeline_runs (snapshot_id, source, mode, success, seen_count) "
                "VALUES ('2026-11-01', 'x', 'semi', true, 0)"
            )
        )


@pytest.mark.parametrize("table", ["job_observations", "job_posting_facts"])
def test_ad4_db_chan_update_va_delete_tren_bang_chi_them(pg_engine: Engine, table: str) -> None:
    _seed(pg_engine)
    update_col = "snapshot_id" if table == "job_observations" else "title"
    update_val = "'2026-11-01'" if table == "job_observations" else "'Khác'"
    with pytest.raises(exc.DBAPIError, match="chỉ được thêm"), pg_engine.begin() as conn:
        conn.execute(text(f"UPDATE haido.{table} SET {update_col} = {update_val}"))
    with pytest.raises(exc.DBAPIError, match="chỉ được thêm"), pg_engine.begin() as conn:
        conn.execute(text(f"DELETE FROM haido.{table}"))
    with pytest.raises(exc.DBAPIError, match="chỉ được thêm"), pg_engine.begin() as conn:
        conn.execute(text(f"TRUNCATE haido.{table}"))
    with pg_engine.connect() as conn:
        assert conn.execute(text(f"SELECT count(*) FROM haido.{table}")).scalar_one() == 1


def test_ad4_tin_va_luot_chay_khong_trung(pg_engine: Engine) -> None:
    _seed(pg_engine)
    with pytest.raises(exc.IntegrityError), pg_engine.begin() as conn:
        conn.execute(text("INSERT INTO haido.job_postings (source, source_url) VALUES ('itviec', 'u1')"))
    with pytest.raises(exc.IntegrityError), pg_engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO haido.pipeline_runs (snapshot_id, source, mode, success, seen_count) "
                "VALUES ('2026-11-01', 'itviec', 'auto', true, 0)"
            )
        )
