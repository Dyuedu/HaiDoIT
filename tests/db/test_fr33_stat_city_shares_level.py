"""#163 — migration 0005: `stat_city_shares` có `seniority` trong khóa chính."""

import pytest
from alembic import command
from alembic.script import ScriptDirectory
from sqlalchemy import Engine, exc, text

from haido_core.db import tables
from tests.conftest import alembic_config

S = "2026-11-03"


def _columns(engine: Engine) -> dict[str, tuple[str, str]]:
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT column_name, data_type, is_nullable FROM information_schema.columns "
                "WHERE table_schema='haido' AND table_name='stat_city_shares'"
            )
        )
        return {r[0]: (r[1], r[2]) for r in rows}


def _primary_key(engine: Engine) -> list[str]:
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT a.attname FROM pg_index i JOIN pg_attribute a ON a.attrelid = i.indrelid "
                "AND a.attnum = ANY(i.indkey) WHERE i.indisprimary "
                "AND i.indrelid = CAST('haido.stat_city_shares' AS regclass) "
                "ORDER BY array_position(i.indkey, a.attnum)"
            )
        )
        return [r[0] for r in rows]


def _snapshot(engine: Engine) -> None:
    with engine.begin() as conn:
        conn.execute(text(f"INSERT INTO haido.snapshots (snapshot_id) VALUES ('{S}')"))


def _share(engine: Engine, *, seniority: str | None = "all", city: str = "ha_noi", share: float = 0.5) -> None:
    columns = "snapshot_id, role, years, city, share" + (", seniority" if seniority is not None else "")
    values = ":s, 'backend', 'any', :c, :v" + (", :l" if seniority is not None else "")
    with engine.begin() as conn:
        conn.execute(
            text(f"INSERT INTO haido.stat_city_shares ({columns}) VALUES ({values})"),
            {"s": S, "c": city, "v": share, "l": seniority},
        )


def test_fr33_migration_0005_noi_tiep_0004_va_la_head_duy_nhat() -> None:
    script = ScriptDirectory.from_config(alembic_config())
    assert script.get_heads() == ["0007_haido_classify_at_ingest"]  # #280 nối 0006 sau 0005, #283 nối 0007
    revision = script.get_revision("0005_haido_city_share_level")
    assert revision is not None and revision.down_revision == "0004_haido_stat_sources"


def test_fr33_stat_city_shares_co_cot_seniority_trong_khoa_chinh(pg_engine: Engine) -> None:
    cols = _columns(pg_engine)
    assert set(cols) == {"snapshot_id", "role", "seniority", "years", "city", "share"}  # #280 thêm `years`
    assert cols["seniority"] == ("text", "NO")
    assert _primary_key(pg_engine) == ["snapshot_id", "role", "seniority", "years", "city"]
    assert set(tables.stat_city_shares.c.keys()) == set(cols)


def test_fr33_cung_thanh_pho_khac_cap_khong_trung_khoa_nhung_cung_cap_thi_trung(pg_engine: Engine) -> None:
    _snapshot(pg_engine)
    _share(pg_engine, seniority="all")
    _share(pg_engine, seniority="entry")
    with pytest.raises(exc.IntegrityError):
        _share(pg_engine, seniority="entry")


def test_fr33_cap_bac_khong_duoc_de_trong_va_khong_co_gia_tri_mac_dinh(pg_engine: Engine) -> None:
    _snapshot(pg_engine)
    with pytest.raises(exc.IntegrityError):
        _share(pg_engine, seniority=None)


def _cell(engine: Engine, seniority: str) -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO haido.stat_cells (snapshot_id, role, branch, seniority, years, scope, n, seniority_mix,"
                " years_unstated, config_version) VALUES (:s, 'backend', 'all', :l, 'any', 'vn', 1, '{}'::jsonb, 0, 'v')"
            ),
            {"s": S, "l": seniority},
        )


def test_fr33_ha_cap_0005_giu_hang_all_bo_hang_cap_khac_va_nang_cap_lai_duoc(pg_engine: Engine) -> None:
    _snapshot(pg_engine)
    _share(pg_engine, seniority="all")
    _share(pg_engine, seniority="entry")
    _cell(pg_engine, "all")
    _cell(pg_engine, "entry")
    command.downgrade(alembic_config(), "0004_haido_stat_sources")
    assert set(_columns(pg_engine)) == {"snapshot_id", "role", "city", "share"}
    assert _primary_key(pg_engine) == ["snapshot_id", "role", "city"]
    with pg_engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM haido.stat_city_shares")).scalar_one() == 1
        assert conn.execute(text("SELECT seniority FROM haido.stat_cells")).scalars().all() == ["all"]
    command.upgrade(alembic_config(), "head")
    with pg_engine.connect() as conn:
        assert conn.execute(text("SELECT seniority FROM haido.stat_city_shares")).scalars().all() == ["all"]


def test_fr33_hang_cu_truoc_0005_nhan_cap_all(pg_engine: Engine) -> None:
    command.downgrade(alembic_config(), "0004_haido_stat_sources")
    _snapshot(pg_engine)
    with pg_engine.begin() as conn:
        conn.execute(text(f"INSERT INTO haido.stat_city_shares VALUES ('{S}', 'backend', 'ha_noi', 0.4)"))
    command.upgrade(alembic_config(), "head")
    with pg_engine.connect() as conn:
        rows = conn.execute(text("SELECT role, seniority, city, share FROM haido.stat_city_shares")).all()
    assert [tuple(r) for r in rows] == [("backend", "all", "ha_noi", 0.4)]
