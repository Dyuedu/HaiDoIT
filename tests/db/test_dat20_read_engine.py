"""#93 — engine đọc của API: chỉ-đọc ở phía DB, không kết nối khi dựng, lỗi không lộ URL."""

import pytest
from sqlalchemy import Engine, exc, text

from haido_core.db.engine import DatabaseConfigError, make_read_engine

REMOTE = "postgresql+psycopg://admin:CANARYPW@db.supabase.co:5432/postgres"


def test_dat20_thieu_url_thi_bao_loi_tieng_viet(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HAIDO_DATABASE_URL", raising=False)
    with pytest.raises(DatabaseConfigError, match="HAIDO_DATABASE_URL chưa được thiết lập"):
        make_read_engine()


@pytest.mark.parametrize("url", ["mysql://u:CANARYPW@h/d", "sqlite:///x.db", "khong-phai-url"])
def test_dat20_driver_sai_hoac_url_hong_thi_bao_loi_khong_lo_mat_khau(url: str) -> None:
    with pytest.raises(DatabaseConfigError) as err:
        make_read_engine(url)
    assert "CANARYPW" not in str(err.value)


def test_dat20_dung_engine_khong_ket_noi_ngay_va_doc_tu_host_ngoai_khong_can_co_cho_phep_ghi(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("HAIDO_DATABASE_URL", REMOTE)
    monkeypatch.delenv("HAIDO_ALLOW_REMOTE_WRITE", raising=False)
    engine = make_read_engine()  # đọc thì không bị chặn host; không kết nối tới khi có truy vấn đầu tiên
    assert engine.url.host == "db.supabase.co"
    engine.dispose()


def test_dat20_engine_doc_duoc_nhung_khong_ghi_duoc(pg_engine: Engine, pg_url: str) -> None:
    engine = make_read_engine(pg_url)
    try:
        with engine.connect() as conn:
            assert conn.execute(text("SELECT count(*) FROM haido.snapshots")).scalar_one() == 0
        with pytest.raises(exc.DBAPIError), engine.begin() as conn:
            conn.execute(text("INSERT INTO haido.snapshots (snapshot_id) VALUES ('2026-11-03')"))
    finally:
        engine.dispose()
    with pg_engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM haido.snapshots")).scalar_one() == 0
