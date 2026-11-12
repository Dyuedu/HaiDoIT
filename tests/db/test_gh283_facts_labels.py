"""#283 — migration 0007: nhãn và mã của tin trong `job_posting_facts`; văn bản JD không xuống bảng nào."""

from alembic import command
from alembic.script import ScriptDirectory
from sqlalchemy import Engine, text

from haido_core.config import load_rules
from haido_core.db.engine import make_source_engine
from haido_core.db.scraper_source import ScraperPostgresReader
from haido_core.steps.ingest import ingest_snapshot
from tests.conftest import alembic_config

S = "2026-11-03"
MARKER = "ZZDAUVET283"


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


def test_gh283_migration_0007_noi_tiep_0006_va_la_head_duy_nhat() -> None:
    script = ScriptDirectory.from_config(alembic_config())
    assert script.get_heads() == ["0008_haido_fact_city"]  # #285 nối 0008
    revision = script.get_revision("0007_haido_classify_at_ingest")
    assert revision is not None and revision.down_revision == "0006_haido_years_filter"


def test_gh283_cot_nhan_moi(pg_engine: Engine) -> None:
    cols = _columns(pg_engine, "job_posting_facts")
    assert cols["role"] == ("text", "YES")
    assert cols["branch"] == ("text", "YES")
    assert cols["seniority"] == ("text", "YES")
    assert cols["skills"] == ("jsonb", "YES")
    assert cols["classify_version"] == ("text", "YES")


def test_gh283_ha_cap_0007_bo_cot_nhan_va_nang_cap_lai_duoc(pg_engine: Engine) -> None:
    command.downgrade(alembic_config(), "0006_haido_years_filter")
    try:
        cols = _columns(pg_engine, "job_posting_facts")
        assert not {"role", "branch", "seniority", "skills", "classify_version"} & cols.keys()
        assert "years_min" in cols
    finally:
        command.upgrade(alembic_config(), "head")
    assert "classify_version" in _columns(pg_engine, "job_posting_facts")


def test_gh283_van_ban_jd_khong_xuong_bang_nao(pg_engine: Engine, pg_url: str, scraper_db) -> None:
    jd = f"Yêu cầu\nPython {MARKER}, Docker, Kubernetes.\nQuyền lợi\n{MARKER} lương tháng 13."
    scraper_db.job("u1", "topcv", title="DevOps Engineer", location="Hà Nội", description=jd,
                   description_consolidated=jd)
    scraper_db.day("topcv", S, ["u1"])
    source = make_source_engine(pg_url)
    try:
        ingest_snapshot(S, reader=ScraperPostgresReader(source), engine=pg_engine, rules=load_rules())
    finally:
        source.dispose()
    with pg_engine.connect() as conn:
        cols = conn.execute(
            text(
                "SELECT table_name, column_name FROM information_schema.columns WHERE table_schema = 'haido' "
                "AND data_type IN ('text', 'jsonb', 'character varying', 'json')"
            )
        ).all()
        assert cols
        hits = []
        for table, column in cols:
            found = conn.execute(
                text(f'SELECT count(*) FROM haido."{table}" WHERE CAST("{column}" AS text) LIKE :m'),
                {"m": f"%{MARKER.lower()}%"},
            ).scalar_one()
            found += conn.execute(
                text(f'SELECT count(*) FROM haido."{table}" WHERE CAST("{column}" AS text) LIKE :m'),
                {"m": f"%{MARKER}%"},
            ).scalar_one()
            if found:
                hits.append(f"{table}.{column}")
        assert hits == []
        assert conn.execute(text("SELECT count(*) FROM haido.job_posting_facts")).scalar_one() == 1
