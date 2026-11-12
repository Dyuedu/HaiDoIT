"""#93 — CLI `aggregate` và `publish` (sau `ingest` và `lifecycle`)."""

from datetime import UTC, datetime

import pytest
from sqlalchemy import Engine, text

from haido_core import cli

S = "2026-11-03"
CANARY = "CANARYPW"


@pytest.fixture
def cli_env(pg_engine: Engine, pg_url: str, monkeypatch: pytest.MonkeyPatch) -> Engine:
    monkeypatch.setenv("HAIDO_DATABASE_URL", pg_url)
    monkeypatch.setenv("HAIDO_SCRAPER_DATABASE_URL", pg_url.replace("postgresql+psycopg://", "postgresql://"))
    monkeypatch.delenv("HAIDO_ALLOW_REMOTE_WRITE", raising=False)
    return pg_engine


def _scalar(engine: Engine, sql: str) -> object:
    with engine.connect() as conn:
        return conn.execute(text(sql)).scalar_one()


def _feed(scraper_db, *, failed: tuple[str, ...] = ()) -> None:
    scraper_db.job("a", "itviec", title="Backend Developer", location="Hà Nội")
    for source in ("zalo", "itnavi", "careerlink", "vietnamworks", "momo", "topdev", "itviec"):
        scraper_db.day(source, S, ["a"] if source == "itviec" else [], complete=source not in failed)


def _chain(*commands: str) -> None:
    for command in commands:
        assert cli.main([command, "--snapshot", S]) == 0


def test_dat20_cli_ingest_lifecycle_aggregate_publish_ma_thoat_0_va_in_tom_tat(
    cli_env: Engine, scraper_db, capsys
) -> None:
    _feed(scraper_db)
    _chain("ingest", "lifecycle")
    capsys.readouterr()

    assert cli.main(["aggregate", "--snapshot", S]) == 0
    out = capsys.readouterr().out
    assert S in out and "6804 ô" in out and "5832 tỷ trọng" in out  # 18 vai trò (#284) × 9 × 6 × (6 nơi luôn có + vn) (#285)
    # #285: 18 vai trò × 9 cấp × 6 mã số năm × (6 nơi luôn có + vn); tin của test chỉ ở các nơi luôn có.
    assert _scalar(cli_env, "SELECT count(*) FROM haido.stat_cells") == 18 * 7 * 9 * 6
    assert _scalar(cli_env, "SELECT count(*) FROM haido.stat_city_shares") == 18 * 6 * 9 * 6

    assert cli.main(["publish", "--snapshot", S]) == 0
    out = capsys.readouterr().out
    assert S in out and "published" in out
    assert _scalar(cli_env, "SELECT status FROM haido.snapshots") == "published"


def test_dat20_cli_publish_partial_in_ra_nguon_loi(cli_env: Engine, scraper_db, capsys) -> None:
    _feed(scraper_db, failed=("zalo", "momo"))
    _chain("ingest", "lifecycle", "aggregate")
    capsys.readouterr()
    assert cli.main(["publish", "--snapshot", S]) == 0
    out = capsys.readouterr().out
    assert "partial" in out and "momo, zalo" in out
    assert _scalar(cli_env, "SELECT status FROM haido.snapshots") == "partial"


def test_dat20_cli_snapshot_da_chot_thi_aggregate_va_publish_ma_thoat_1(cli_env: Engine, scraper_db, capsys) -> None:
    _feed(scraper_db)
    _chain("ingest", "lifecycle", "aggregate", "publish")
    capsys.readouterr()
    for command in ("aggregate", "publish"):
        assert cli.main([command, "--snapshot", S]) == 1
        assert "đã chốt" in capsys.readouterr().err


def test_dat20_cli_snapshot_chua_mo_thi_ma_thoat_1(cli_env: Engine, capsys) -> None:
    for command in ("aggregate", "publish"):
        assert cli.main([command, "--snapshot", S]) == 1
        assert "chưa mở" in capsys.readouterr().err


def test_dat20_cli_ngay_sai_thi_ma_thoat_1_va_khong_ghi(cli_env: Engine, capsys) -> None:
    for command in ("aggregate", "publish"):
        assert cli.main([command, "--snapshot", "2026-13-01"]) == 1
        assert "YYYY-MM-DD" in capsys.readouterr().err
    assert _scalar(cli_env, "SELECT count(*) FROM haido.snapshots") == 0


def test_dat20_cli_mac_dinh_s_la_hom_nay_theo_gio_ho_chi_minh(
    cli_env: Engine, scraper_db, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    monkeypatch.setattr(cli, "_now", lambda: datetime(2026, 11, 3, 17, 30, tzinfo=UTC))
    scraper_db.day("itviec", "2026-11-04", [])
    assert cli.main(["ingest"]) == 0
    assert cli.main(["lifecycle"]) == 0
    assert cli.main(["aggregate"]) == 0
    assert "2026-11-04" in capsys.readouterr().out
    assert cli.main(["publish"]) == 0
    assert _scalar(cli_env, "SELECT snapshot_id::text FROM haido.snapshots WHERE status <> 'open'") == "2026-11-04"


def test_dat20_cli_thieu_url_bao_loi_tieng_viet(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    monkeypatch.delenv("HAIDO_DATABASE_URL", raising=False)
    for command in ("aggregate", "publish"):
        assert cli.main([command, "--snapshot", S]) == 1
        assert "HAIDO_DATABASE_URL chưa được thiết lập" in capsys.readouterr().err


def test_dat20_cli_dich_la_khong_cho_phep_thi_khong_ghi_va_khong_in_mat_khau(
    monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    monkeypatch.setenv("HAIDO_DATABASE_URL", f"postgresql+psycopg://admin:{CANARY}@db.supabase.co:5432/postgres")
    monkeypatch.delenv("HAIDO_ALLOW_REMOTE_WRITE", raising=False)
    for command in ("aggregate", "publish"):
        assert cli.main([command, "--snapshot", S]) == 1
        captured = capsys.readouterr()
        assert "HAIDO_ALLOW_REMOTE_WRITE" in captured.err
        assert CANARY not in captured.out + captured.err


def test_dat20_cli_loi_ket_noi_khong_in_mat_khau(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    monkeypatch.setenv("HAIDO_DATABASE_URL", f"postgresql+psycopg://u:{CANARY}@127.0.0.1:1/d?connect_timeout=2")
    for command in ("aggregate", "publish"):
        assert cli.main([command, "--snapshot", S]) == 1
        captured = capsys.readouterr()
        assert "Lỗi cơ sở dữ liệu" in captured.err
        assert CANARY not in captured.out + captured.err


def test_dat20_cli_tro_giup_liet_ke_du_bon_buoc(capsys) -> None:
    with pytest.raises(SystemExit):
        cli.main(["--help"])
    out = capsys.readouterr().out
    for command in ("ingest", "lifecycle", "aggregate", "publish"):
        assert command in out
