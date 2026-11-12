"""#280 — migration 0006: số năm tối thiểu của tin và cột `years` trong khóa của hai bảng stat."""

import pytest
from alembic import command
from alembic.script import ScriptDirectory
from sqlalchemy import Engine, exc, text

from haido_core.db import tables
from tests.conftest import alembic_config

S = "2026-11-12"


def _columns(engine: Engine, table: str) -> dict[str, tuple[str, str]]:
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT column_name, data_type, is_nullable FROM information_schema.columns "
                "WHERE table_schema = 'haido' AND table_name = :t"
            ),
            {"t": table},
        )
        return {r[0]: (r[1], r[2]) for r in rows}


def _primary_key(engine: Engine, table: str) -> list[str]:
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT a.attname FROM pg_index i JOIN pg_attribute a ON a.attrelid = i.indrelid "
                "AND a.attnum = ANY(i.indkey) WHERE i.indisprimary "
                "AND i.indrelid = CAST(:t AS regclass) ORDER BY array_position(i.indkey, a.attnum)"
            ),
            {"t": f"haido.{table}"},
        )
        return [r[0] for r in rows]


def _snapshot(engine: Engine) -> None:
    with engine.begin() as conn:
        conn.execute(text(f"INSERT INTO haido.snapshots (snapshot_id) VALUES ('{S}')"))


def _cell(engine: Engine, years: str | None, unstated: int | None = 0) -> None:
    columns = ["snapshot_id", "role", "branch", "seniority", "scope", "n", "seniority_mix", "config_version"]
    values = [":s", "'backend'", "'all'", "'all'", "'vn'", "1", "'{}'::jsonb", "'v'"]
    if years is not None:
        columns.append("years")
        values.append(":y")
    if unstated is not None:
        columns.append("years_unstated")
        values.append(":u")
    with engine.begin() as conn:
        conn.execute(
            text(f"INSERT INTO haido.stat_cells ({', '.join(columns)}) VALUES ({', '.join(values)})"),
            {"s": S, "y": years, "u": unstated},
        )


def _share(engine: Engine, years: str) -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO haido.stat_city_shares (snapshot_id, role, seniority, years, city, share) "
                "VALUES (:s, 'backend', 'all', :y, 'ha_noi', 0.5)"
            ),
            {"s": S, "y": years},
        )


def test_fr33_migration_0006_noi_tiep_0005_va_la_head_duy_nhat() -> None:
    script = ScriptDirectory.from_config(alembic_config())
    assert script.get_heads() == ["0007_haido_classify_at_ingest"]  # #283 nối 0007 sau 0006
    revision = script.get_revision("0006_haido_years_filter")
    assert revision is not None and revision.down_revision == "0005_haido_city_share_level"


def test_fr33_cot_moi_va_khoa_chinh_co_years(pg_engine: Engine) -> None:
    facts = _columns(pg_engine, "job_posting_facts")
    assert facts["years_min"] == ("double precision", "YES")
    cells = _columns(pg_engine, "stat_cells")
    assert cells["years"] == ("text", "NO") and cells["years_unstated"] == ("integer", "NO")
    assert _primary_key(pg_engine, "stat_cells") == ["snapshot_id", "role", "branch", "seniority", "years", "scope"]
    assert _primary_key(pg_engine, "stat_city_shares") == ["snapshot_id", "role", "seniority", "years", "city"]
    for name in ("job_posting_facts", "stat_cells", "stat_city_shares"):
        assert set(getattr(tables, name).c.keys()) == set(_columns(pg_engine, name))


def test_fr33_years_va_years_unstated_khong_co_gia_tri_mac_dinh(pg_engine: Engine) -> None:
    _snapshot(pg_engine)
    with pytest.raises(exc.IntegrityError):
        _cell(pg_engine, years=None)
    with pytest.raises(exc.IntegrityError):
        _cell(pg_engine, years="any", unstated=None)


def test_fr33_cung_o_khac_moc_so_nam_khong_trung_khoa(pg_engine: Engine) -> None:
    _snapshot(pg_engine)
    _cell(pg_engine, "any")
    _cell(pg_engine, "2")
    _share(pg_engine, "any")
    _share(pg_engine, "2")
    with pytest.raises(exc.IntegrityError):
        _share(pg_engine, "2")


def test_fr33_ha_cap_0006_giu_hang_any_bo_hang_moc_khac_va_nang_cap_lai_duoc(pg_engine: Engine) -> None:
    _snapshot(pg_engine)
    _cell(pg_engine, "any")
    _cell(pg_engine, "2")
    _share(pg_engine, "any")
    _share(pg_engine, "2")
    command.downgrade(alembic_config(), "0005_haido_city_share_level")
    assert "years" not in _columns(pg_engine, "stat_cells")
    assert "years_unstated" not in _columns(pg_engine, "stat_cells")
    assert "years_min" not in _columns(pg_engine, "job_posting_facts")
    assert _primary_key(pg_engine, "stat_cells") == ["snapshot_id", "role", "branch", "seniority", "scope"]
    assert _primary_key(pg_engine, "stat_city_shares") == ["snapshot_id", "role", "seniority", "city"]
    with pg_engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM haido.stat_cells")).scalar_one() == 1
        assert conn.execute(text("SELECT count(*) FROM haido.stat_city_shares")).scalar_one() == 1
    command.upgrade(alembic_config(), "head")
    with pg_engine.connect() as conn:
        assert conn.execute(text("SELECT years, years_unstated FROM haido.stat_cells")).all() == [("any", 0)]
        assert conn.execute(text("SELECT years FROM haido.stat_city_shares")).scalars().all() == ["any"]
