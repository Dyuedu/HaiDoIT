"""#285 — migration 0008: cột `city` của `job_posting_facts`."""

from alembic import command
from alembic.script import ScriptDirectory
from sqlalchemy import Engine, text

from tests.conftest import alembic_config


def _columns(engine: Engine) -> dict[str, tuple[str, str]]:
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT column_name, data_type, is_nullable FROM information_schema.columns "
                "WHERE table_schema = 'haido' AND table_name = 'job_posting_facts'"
            )
        )
        return {r[0]: (r[1], r[2]) for r in rows}


def test_gh285_migration_0008_noi_tiep_0007_va_la_head_duy_nhat() -> None:
    script = ScriptDirectory.from_config(alembic_config())
    assert script.get_heads() == ["0008_haido_fact_city"]
    revision = script.get_revision("0008_haido_fact_city")
    assert revision is not None and revision.down_revision == "0007_haido_classify_at_ingest"


def test_gh285_cot_city_va_ha_cap(pg_engine: Engine) -> None:
    assert _columns(pg_engine)["city"] == ("text", "YES")
    command.downgrade(alembic_config(), "0007_haido_classify_at_ingest")
    try:
        assert "city" not in _columns(pg_engine)
    finally:
        command.upgrade(alembic_config(), "head")
    assert "city" in _columns(pg_engine)
