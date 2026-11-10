"""#93 — migration 0003: `stat_cells` và `stat_city_shares` trong schema `haido`."""

import pytest
from alembic import command
from alembic.script import ScriptDirectory
from sqlalchemy import Engine, exc, text

from haido_core.db import tables
from tests.conftest import alembic_config

S = "2026-11-03"


def _columns(engine: Engine, table: str) -> dict[str, tuple[str, str]]:
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT column_name, data_type, is_nullable FROM information_schema.columns "
                "WHERE table_schema='haido' AND table_name=:t"
            ),
            {"t": table},
        )
        return {r[0]: (r[1], r[2]) for r in rows}


def _primary_key(engine: Engine, table: str) -> list[str]:
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT a.attname FROM pg_index i JOIN pg_attribute a ON a.attrelid = i.indrelid "
                "AND a.attnum = ANY(i.indkey) WHERE i.indisprimary AND i.indrelid = CAST(:t AS regclass) "
                "ORDER BY array_position(i.indkey, a.attnum)"
            ),
            {"t": f"haido.{table}"},
        )
        return [r[0] for r in rows]


def _snapshot(engine: Engine) -> None:
    with engine.begin() as conn:
        conn.execute(text(f"INSERT INTO haido.snapshots (snapshot_id) VALUES ('{S}')"))


def _cell(engine: Engine, **over: object) -> None:
    values = {"s": S, "role": "backend", "scope": "ha_noi", "n": 5, "mix": '{"junior": 5}', "v": "t", **over}
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO haido.stat_cells (snapshot_id, role, branch, seniority, scope, n, seniority_mix, "
                "config_version) VALUES (:s, :role, 'all', 'all', :scope, :n, CAST(:mix AS jsonb), :v)"
            ),
            values,
        )


def test_dat20_migration_0003_noi_tiep_0002() -> None:
    script = ScriptDirectory.from_config(alembic_config())
    revision = script.get_revision("0003_haido_city_share")
    assert revision is not None and revision.down_revision == "0002_haido_snapshot"


def test_dat259_migration_0004_noi_tiep_0003_va_chi_con_mot_head() -> None:
    script = ScriptDirectory.from_config(alembic_config())
    assert script.get_heads() == ["0004_haido_stat_sources"]
    revision = script.get_revision("0004_haido_stat_sources")
    assert revision is not None and revision.down_revision == "0003_haido_city_share"


def test_dat259_stat_sources_co_dung_cot_va_khoa_trong_schema_haido(pg_engine: Engine) -> None:
    cols = _columns(pg_engine, "stat_sources")
    assert set(cols) == {"snapshot_id", "source"}
    assert all(nullable == "NO" for _, nullable in cols.values())
    assert _primary_key(pg_engine, "stat_sources") == ["snapshot_id", "source"]
    assert set(tables.stat_sources.c.keys()) == set(cols)
    assert tables.stat_sources.schema == "haido"


def test_dat259_stat_sources_phai_thuoc_snapshot_co_that_va_khong_trung_khoa(pg_engine: Engine) -> None:
    insert = text("INSERT INTO haido.stat_sources (snapshot_id, source) VALUES (:s, 'itviec')")
    with pytest.raises(exc.IntegrityError), pg_engine.begin() as conn:
        conn.execute(insert, {"s": S})
    _snapshot(pg_engine)
    with pg_engine.begin() as conn:
        conn.execute(insert, {"s": S})
    with pytest.raises(exc.IntegrityError), pg_engine.begin() as conn:
        conn.execute(insert, {"s": S})


def test_dat259_ha_cap_0004_chi_bo_stat_sources_va_nang_cap_lai_duoc(pg_engine: Engine) -> None:
    _snapshot(pg_engine)
    _cell(pg_engine)
    command.downgrade(alembic_config(), "0003_haido_city_share")
    assert _columns(pg_engine, "stat_sources") == {}
    assert _columns(pg_engine, "stat_cells") != {}
    command.upgrade(alembic_config(), "head")
    assert _columns(pg_engine, "stat_sources") != {}


def test_dat20_stat_cells_co_dung_cot_va_khoa(pg_engine: Engine) -> None:
    cols = _columns(pg_engine, "stat_cells")
    assert set(cols) == {"snapshot_id", "role", "branch", "seniority", "scope", "n", "seniority_mix", "config_version"}
    assert cols["seniority_mix"][0] == "jsonb"
    assert cols["n"][0] == "integer"
    assert all(nullable == "NO" for _, nullable in cols.values())
    assert _primary_key(pg_engine, "stat_cells") == ["snapshot_id", "role", "branch", "seniority", "scope"]


def test_dat20_stat_city_shares_co_dung_cot_va_khoa(pg_engine: Engine) -> None:
    cols = _columns(pg_engine, "stat_city_shares")
    assert set(cols) == {"snapshot_id", "role", "city", "share"}
    assert cols["share"][0] == "double precision"
    assert _primary_key(pg_engine, "stat_city_shares") == ["snapshot_id", "role", "city"]


def test_dat20_bang_trong_tables_py_khop_migration(pg_engine: Engine) -> None:
    assert set(tables.stat_cells.c.keys()) == set(_columns(pg_engine, "stat_cells"))
    assert set(tables.stat_city_shares.c.keys()) == set(_columns(pg_engine, "stat_city_shares"))
    assert tables.stat_cells.schema == tables.stat_city_shares.schema == "haido"


def test_dat20_hang_phai_thuoc_snapshot_co_that_va_khong_trung_khoa(pg_engine: Engine) -> None:
    with pytest.raises(exc.IntegrityError):
        _cell(pg_engine)
    _snapshot(pg_engine)
    _cell(pg_engine)
    with pytest.raises(exc.IntegrityError):
        _cell(pg_engine)


def test_dat20_rang_buoc_n_khong_am_va_ty_trong_trong_khoang_0_1(pg_engine: Engine) -> None:
    _snapshot(pg_engine)
    with pytest.raises(exc.IntegrityError):
        _cell(pg_engine, n=-1)
    for bad in (-0.1, 1.1):
        with pytest.raises(exc.IntegrityError), pg_engine.begin() as conn:
            conn.execute(
                text("INSERT INTO haido.stat_city_shares VALUES (:s, 'backend', 'ha_noi', :v)"), {"s": S, "v": bad}
            )


def test_dat20_ha_cap_0003_chi_bo_hai_bang_moi_va_nang_cap_lai_duoc(pg_engine: Engine) -> None:
    _snapshot(pg_engine)
    command.downgrade(alembic_config(), "0002_haido_snapshot")
    assert _columns(pg_engine, "stat_cells") == {}
    assert _columns(pg_engine, "stat_city_shares") == {}
    assert _columns(pg_engine, "stat_job_lifecycle") != {}
    with pg_engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM haido.snapshots")).scalar_one() == 1
    command.upgrade(alembic_config(), "head")
    assert _columns(pg_engine, "stat_cells") != {}
