"""AD-4 — engine ghi chặn host lạ, engine nguồn chỉ-đọc (Story 1.4)."""

import pytest
from sqlalchemy import Engine, exc, text

from haido_core.db.engine import (
    DatabaseConfigError,
    make_source_engine,
    make_write_engine,
    normalize_source_url,
)

REMOTE = "postgresql+psycopg://admin:CANARYPW@db.supabase.co:5432/postgres"


def test_ad4_ghi_vao_host_la_bi_tu_choi_va_khong_lo_mat_khau(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HAIDO_DATABASE_URL", REMOTE)
    monkeypatch.delenv("HAIDO_ALLOW_REMOTE_WRITE", raising=False)
    with pytest.raises(DatabaseConfigError) as err:
        make_write_engine()
    assert "HAIDO_ALLOW_REMOTE_WRITE" in str(err.value)
    assert "CANARYPW" not in str(err.value)
    assert "supabase" not in str(err.value)


@pytest.mark.parametrize("query", ["host=db.supabase.co", "hostaddr=10.0.0.99"])
def test_ad4_host_la_qua_query_string_cung_bi_tu_choi(monkeypatch: pytest.MonkeyPatch, query: str) -> None:
    monkeypatch.delenv("HAIDO_ALLOW_REMOTE_WRITE", raising=False)
    with pytest.raises(DatabaseConfigError):
        make_write_engine(f"postgresql+psycopg://u:p@localhost:5432/d?{query}")


def test_ad4_co_cho_phep_host_tu_xa_chi_khi_dat_dung_1(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HAIDO_DATABASE_URL", REMOTE)
    monkeypatch.setenv("HAIDO_ALLOW_REMOTE_WRITE", "true")
    with pytest.raises(DatabaseConfigError):
        make_write_engine()
    monkeypatch.setenv("HAIDO_ALLOW_REMOTE_WRITE", "1")
    engine = make_write_engine()  # không kết nối ngay
    assert engine.url.host == "db.supabase.co"
    engine.dispose()


def test_ad4_thieu_url_dich_thi_bao_loi_tieng_viet(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HAIDO_DATABASE_URL", raising=False)
    with pytest.raises(DatabaseConfigError, match="HAIDO_DATABASE_URL chưa được thiết lập"):
        make_write_engine()


def test_ad4_thieu_url_nguon_thi_bao_loi_tieng_viet(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HAIDO_SCRAPER_DATABASE_URL", raising=False)
    with pytest.raises(DatabaseConfigError, match="HAIDO_SCRAPER_DATABASE_URL chưa được thiết lập"):
        make_source_engine()


def test_ad4_url_nguon_kieu_scraper_duoc_doi_sang_psycopg() -> None:
    assert normalize_source_url("postgresql://u:p@h/d") == "postgresql+psycopg://u:p@h/d"
    assert normalize_source_url("postgres://u:p@h/d") == "postgresql+psycopg://u:p@h/d"
    assert normalize_source_url("postgresql+psycopg://u:p@h/d") == "postgresql+psycopg://u:p@h/d"


def test_ad4_url_nguon_sai_khong_lo_mat_khau() -> None:
    with pytest.raises(DatabaseConfigError) as err:
        normalize_source_url("mysql://u:CANARYPW@h/d")
    assert "CANARYPW" not in str(err.value)


def test_ad4_ket_noi_nguon_chi_doc_o_phia_db(pg_engine: Engine, pg_url: str) -> None:
    source = make_source_engine(pg_url)
    try:
        with source.connect() as conn:
            assert conn.execute(text("SELECT count(*) FROM source_runs")).scalar_one() == 0
        with source.connect() as conn:
            assert conn.execute(text("SHOW transaction_isolation")).scalar_one() == "repeatable read"
            assert conn.execute(text("SHOW transaction_read_only")).scalar_one() == "on"
        with pytest.raises(exc.DBAPIError) as err1, source.begin() as conn:
            conn.execute(text("INSERT INTO source_runs VALUES ('x', '2026-11-01', true, 0, 0, null, now())"))
        assert err1.value.orig.sqlstate == "25006"
        with pytest.raises(exc.DBAPIError) as err2, source.begin() as conn:
            conn.execute(text("DELETE FROM jobs"))
        assert err2.value.orig.sqlstate == "25006"
    finally:
        source.dispose()
