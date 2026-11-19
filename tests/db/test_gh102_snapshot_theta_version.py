"""#102 (DAT.30) — migration 0010: cột `haido.snapshots.theta_version` (text, nullable), hạ cấp bỏ cột."""

import pytest
from sqlalchemy import Engine, text

from haido_core.db.tables import snapshots


def _column(engine: Engine) -> tuple[str, str] | None:
    with engine.connect() as conn:
        row = conn.execute(
            text(
                "SELECT data_type, is_nullable FROM information_schema.columns "
                "WHERE table_schema = 'haido' AND table_name = 'snapshots' AND column_name = 'theta_version'"
            )
        ).one_or_none()
    return None if row is None else (row[0], row[1])


def test_gh102_cot_theta_version_la_text_cho_phep_null(pg_engine: Engine) -> None:
    assert _column(pg_engine) == ("text", "YES")


def test_gh102_snapshot_cu_khong_co_phien_ban_theta_la_null(pg_engine: Engine) -> None:
    with pg_engine.begin() as conn:
        conn.execute(text("INSERT INTO haido.snapshots (snapshot_id, status) VALUES ('2026-11-01', 'published')"))
        version = conn.execute(text("SELECT theta_version FROM haido.snapshots")).scalar_one()
    assert version is None


def test_gh102_bang_trong_code_co_cot_theta_version() -> None:
    column = snapshots.c.theta_version
    assert column.nullable and str(column.type) == "TEXT"


# ---------------------------------------------------------------- replace_stats chỉ ghi vào snapshot đang open (đợt review)


def _replace(conn, day: str) -> None:
    from datetime import date

    from haido_core.db import snapshot_store

    snapshot_store.replace_stats(conn, date.fromisoformat(day), "v", [], [], [], [], theta_version="theta-1")


def test_gh102_replace_stats_ghi_phien_ban_vao_snapshot_open(pg_engine: Engine) -> None:
    with pg_engine.begin() as conn:
        conn.execute(text("INSERT INTO haido.snapshots (snapshot_id, status) VALUES ('2026-11-01', 'open')"))
        _replace(conn, "2026-11-01")
        assert conn.execute(text("SELECT theta_version FROM haido.snapshots")).scalar_one() == "theta-1"


@pytest.mark.parametrize("status", ["published", "partial"])
def test_gh102_replace_stats_tu_choi_snapshot_da_chot_va_khong_doi_phien_ban(pg_engine: Engine, status: str) -> None:
    with pg_engine.begin() as conn:
        conn.execute(
            text("INSERT INTO haido.snapshots (snapshot_id, status, theta_version) VALUES ('2026-11-01', :s, 'theta-0')"),
            {"s": status},
        )
    with pytest.raises(ValueError, match="không có hoặc không còn open"), pg_engine.begin() as conn:
        _replace(conn, "2026-11-01")
    with pg_engine.connect() as conn:
        assert conn.execute(text("SELECT theta_version FROM haido.snapshots")).scalar_one() == "theta-0"


def test_gh102_replace_stats_tu_choi_snapshot_khong_ton_tai(pg_engine: Engine) -> None:
    with pytest.raises(ValueError, match="không có hoặc không còn open"), pg_engine.begin() as conn:
        _replace(conn, "2026-11-01")
