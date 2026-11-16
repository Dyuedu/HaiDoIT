"""#101 (DAT.29) — migration 0009: bảng `stat_skill_rates`, gắn snapshot và khóa ô (AD-4, AD-5)."""

import pytest
from alembic import command
from alembic.script import ScriptDirectory
from sqlalchemy import Engine, exc, text

from haido_core.db import tables
from tests.conftest import alembic_config

S = "2026-11-03"
KEY = ["snapshot_id", "role", "branch", "seniority", "years", "scope", "skill"]


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
                "AND a.attnum = ANY(i.indkey) WHERE i.indisprimary "
                "AND i.indrelid = CAST(:t AS regclass) ORDER BY array_position(i.indkey, a.attnum)"
            ),
            {"t": f"haido.{table}"},
        )
        return [r[0] for r in rows]


def _cell(engine: Engine, role: str = "backend") -> None:
    with engine.begin() as conn:
        conn.execute(text(f"INSERT INTO haido.snapshots (snapshot_id) VALUES ('{S}') ON CONFLICT DO NOTHING"))
        conn.execute(
            text(
                "INSERT INTO haido.stat_cells (snapshot_id, role, branch, seniority, years, scope, n, "
                "seniority_mix, years_unstated, config_version) "
                "VALUES (:s, :r, 'all', 'all', 'any', 'vn', 4, '{}'::jsonb, 0, 'v')"
            ),
            {"s": S, "r": role},
        )


def _rate(
    engine: Engine, role: str = "backend", skill: str = "python", n_with: int = 1, rate: float = 0.25, n_scanned: int = 4
) -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO haido.stat_skill_rates (snapshot_id, role, branch, seniority, years, scope, skill, "
                "n_with, n_scanned, rate, vocab_version) "
                "VALUES (:s, :r, 'all', 'all', 'any', 'vn', :k, :w, :n, :x, 'seed-x')"
            ),
            {"s": S, "r": role, "k": skill, "w": n_with, "n": n_scanned, "x": rate},
        )


def test_dat29_migration_0009_noi_tiep_0008_va_la_head_duy_nhat() -> None:
    script = ScriptDirectory.from_config(alembic_config())
    assert script.get_heads() == ["0009_haido_skill_rates"]
    revision = script.get_revision("0009_haido_skill_rates")
    assert revision is not None and revision.down_revision == "0008_haido_fact_city"


def test_dat29_ad4_cot_va_khoa_gom_snapshot_va_khoa_o(pg_engine: Engine) -> None:
    cols = _columns(pg_engine, "stat_skill_rates")
    assert set(cols) == {*KEY, "n_with", "n_scanned", "rate", "vocab_version"}
    assert cols["n_with"][0] == cols["n_scanned"][0] == "integer"
    assert cols["rate"][0] == "double precision"
    assert all(nullable == "NO" for _, nullable in cols.values())
    assert _primary_key(pg_engine, "stat_skill_rates") == KEY
    assert set(tables.stat_skill_rates.c.keys()) == set(cols)


def test_dat29_ad4_hang_phai_thuoc_o_co_that_khong_trung_khoa(pg_engine: Engine) -> None:
    with pytest.raises(exc.IntegrityError):
        _rate(pg_engine)  # chưa có snapshot, chưa có ô
    _cell(pg_engine)
    with pytest.raises(exc.IntegrityError):
        _rate(pg_engine, role="data")  # có snapshot nhưng ô (data) không có trong stat_cells
    _rate(pg_engine)
    with pytest.raises(exc.IntegrityError):
        _rate(pg_engine)


def test_dat29_fr9_rang_buoc_n_with_khong_am_va_ty_le_trong_khoang_0_1(pg_engine: Engine) -> None:
    _cell(pg_engine)
    with pytest.raises(exc.IntegrityError):
        _rate(pg_engine, n_with=-1)
    for bad in (-0.1, 1.1):
        with pytest.raises(exc.IntegrityError):
            _rate(pg_engine, rate=bad)
    _rate(pg_engine, skill="sql", n_with=0, rate=0.0)
    _rate(pg_engine, skill="docker", n_with=4, rate=1.0)


def test_dat29_d2_n_with_khong_vuot_n_scanned_va_n_scanned_khong_am(pg_engine: Engine) -> None:
    _cell(pg_engine)
    with pytest.raises(exc.IntegrityError):
        _rate(pg_engine, n_with=3, n_scanned=2, rate=0.5)
    with pytest.raises(exc.IntegrityError):
        _rate(pg_engine, n_with=0, n_scanned=-1, rate=0.0)
    _rate(pg_engine, skill="sql", n_with=2, n_scanned=2, rate=1.0)
    _rate(pg_engine, skill="docker", n_with=0, n_scanned=0, rate=0.0)  # chưa cụm nào quét: rate 0


def test_dat29_r1_co_chi_muc_snapshot_skill_cho_doc_mot_ky_nang_qua_cac_vai_tro(pg_engine: Engine) -> None:
    with pg_engine.connect() as conn:
        rows = conn.execute(
            text("SELECT indexname, indexdef FROM pg_indexes WHERE schemaname='haido' AND tablename='stat_skill_rates'")
        ).all()
    secondary = {name: definition for name, definition in rows if not name.endswith("_pkey")}
    assert list(secondary) == ["ix_stat_skill_rates_snapshot_skill"]
    assert "(snapshot_id, skill)" in secondary["ix_stat_skill_rates_snapshot_skill"]
    assert [i.name for i in tables.stat_skill_rates.indexes] == ["ix_stat_skill_rates_snapshot_skill"]


def test_dat29_d3_job_posting_facts_co_cot_vocab_version_cho_phep_null(pg_engine: Engine) -> None:
    assert _columns(pg_engine, "job_posting_facts")["vocab_version"] == ("text", "YES")
    assert "vocab_version" in tables.job_posting_facts.c


def test_dat29_ad4_ha_cap_0009_bo_bang_moi_va_cot_vocab_version_roi_nang_cap_lai_duoc(pg_engine: Engine) -> None:
    _cell(pg_engine)
    _rate(pg_engine)
    command.downgrade(alembic_config(), "0008_haido_fact_city")
    try:
        assert _columns(pg_engine, "stat_skill_rates") == {}
        assert _columns(pg_engine, "stat_cells") != {}
        assert "vocab_version" not in _columns(pg_engine, "job_posting_facts")
        assert "role" in _columns(pg_engine, "job_posting_facts")  # cột của các migration trước còn nguyên
    finally:
        command.upgrade(alembic_config(), "head")
    assert _columns(pg_engine, "stat_skill_rates") != {}
    assert "vocab_version" in _columns(pg_engine, "job_posting_facts")
    with pg_engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM haido.stat_skill_rates")).scalar_one() == 0


def test_dat29_r4_replace_stats_bat_buoc_phai_truyen_ty_le_ky_nang() -> None:
    import inspect

    from haido_core.db import snapshot_store

    parameter = inspect.signature(snapshot_store.replace_stats).parameters["skill_rates"]
    assert parameter.default is inspect.Parameter.empty


def test_dat29_d2_replace_stats_tu_choi_hang_co_n_scanned_vuot_n_cua_o(pg_engine: Engine) -> None:
    from datetime import date

    from haido_core.db import snapshot_store
    from haido_core.domain.aggregate import CellRow
    from haido_core.domain.skill_rates import SkillRateRow

    day = date.fromisoformat(S)
    cell = CellRow("backend", "vn", 2, {})
    ok = SkillRateRow("backend", "all", "python", 1, 2, 0.5, "seed-x")
    too_big = SkillRateRow("backend", "all", "python", 1, 3, 1 / 3, "seed-x")
    with pg_engine.begin() as conn:
        snapshot_store.insert_open(conn, day)
    with pytest.raises(ValueError, match="n_scanned"), pg_engine.begin() as conn:
        snapshot_store.replace_stats(conn, day, "v", [cell], [], [], [too_big])
    with pg_engine.begin() as conn:
        snapshot_store.replace_stats(conn, day, "v", [cell], [], [], [ok])
        assert conn.execute(text("SELECT count(*) FROM haido.stat_skill_rates")).scalar_one() == 1
