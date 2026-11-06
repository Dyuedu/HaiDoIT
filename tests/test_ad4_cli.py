"""AD-4 — CLI `haido ingest|lifecycle --snapshot S` (Story 1.4)."""

import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest
from sqlalchemy import Engine, text

from haido_core import cli

ROOT = Path(__file__).resolve().parents[1]
S = "2026-11-03"
CANARY = "CANARYPW"


@pytest.fixture
def cli_env(pg_engine: Engine, pg_url: str, monkeypatch: pytest.MonkeyPatch) -> Engine:
    monkeypatch.setenv("HAIDO_DATABASE_URL", pg_url)
    monkeypatch.setenv("HAIDO_SCRAPER_DATABASE_URL", pg_url.replace("postgresql+psycopg://", "postgresql://"))
    monkeypatch.delenv("HAIDO_ALLOW_REMOTE_WRITE", raising=False)
    return pg_engine


def _count(engine: Engine, table: str) -> int:
    with engine.connect() as conn:
        return conn.execute(text(f"SELECT count(*) FROM haido.{table}")).scalar_one()


def test_ad4_cli_ingest_roi_lifecycle_ma_thoat_0_va_in_tom_tat(cli_env: Engine, scraper_db, capsys) -> None:
    scraper_db.day("itviec", S, ["a", "b"])
    assert cli.main(["ingest", "--snapshot", S]) == 0
    out = capsys.readouterr().out
    assert S in out and "2 quan sát" in out
    assert cli.main(["lifecycle", "--snapshot", S]) == 0
    assert "2 tin" in capsys.readouterr().out
    assert _count(cli_env, "stat_job_lifecycle") == 2


def test_ad4_cli_ngay_sai_thi_khong_ghi_ma_thoat_khac_0(cli_env: Engine, scraper_db, capsys) -> None:
    scraper_db.day("itviec", S, ["a"])
    assert cli.main(["ingest", "--snapshot", "2026-13-01"]) != 0
    assert "YYYY-MM-DD" in capsys.readouterr().err
    assert _count(cli_env, "snapshots") == 0


def test_ad4_cli_chua_co_du_lieu_ngay_s(cli_env: Engine, capsys) -> None:
    assert cli.main(["ingest", "--snapshot", S]) == 1
    assert "chưa có lượt chạy" in capsys.readouterr().err
    assert _count(cli_env, "snapshots") == 0


def test_ad4_cli_snapshot_da_chot_ma_thoat_khac_0(cli_env: Engine, scraper_db, capsys) -> None:
    scraper_db.day("itviec", S, ["a"])
    assert cli.main(["ingest", "--snapshot", S]) == 0
    with cli_env.begin() as conn:
        conn.execute(text("UPDATE haido.snapshots SET status='published'"))
    capsys.readouterr()
    assert cli.main(["ingest", "--snapshot", S]) == 1
    assert "đã chốt" in capsys.readouterr().err
    assert cli.main(["lifecycle", "--snapshot", S]) == 1
    assert "đã chốt" in capsys.readouterr().err


def test_ad4_cli_mac_dinh_s_la_hom_nay_theo_gio_ho_chi_minh(
    cli_env: Engine, scraper_db, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    # 17:30 UTC ngày 03 đã là ngày 04 ở Việt Nam
    monkeypatch.setattr(cli, "_now", lambda: datetime(2026, 11, 3, 17, 30, tzinfo=UTC))
    scraper_db.day("itviec", "2026-11-04", ["a"])
    assert cli.main(["ingest"]) == 0
    assert "2026-11-04" in capsys.readouterr().out


def test_ad4_cli_thieu_url_bao_loi_tieng_viet(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    monkeypatch.delenv("HAIDO_DATABASE_URL", raising=False)
    monkeypatch.delenv("HAIDO_SCRAPER_DATABASE_URL", raising=False)
    assert cli.main(["ingest", "--snapshot", S]) == 1
    assert "chưa được thiết lập" in capsys.readouterr().err
    assert cli.main(["lifecycle", "--snapshot", S]) == 1
    assert "HAIDO_DATABASE_URL chưa được thiết lập" in capsys.readouterr().err


def test_ad4_cli_dich_la_khong_cho_phep_thi_khong_ghi_va_khong_in_mat_khau(
    monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    monkeypatch.setenv("HAIDO_DATABASE_URL", f"postgresql+psycopg://admin:{CANARY}@db.supabase.co:5432/postgres")
    monkeypatch.setenv("HAIDO_SCRAPER_DATABASE_URL", f"postgresql://admin:{CANARY}@db.supabase.co:5432/postgres")
    monkeypatch.delenv("HAIDO_ALLOW_REMOTE_WRITE", raising=False)
    for command in ("ingest", "lifecycle"):
        assert cli.main([command, "--snapshot", S]) == 1
        captured = capsys.readouterr()
        assert "HAIDO_ALLOW_REMOTE_WRITE" in captured.err
        assert CANARY not in captured.out + captured.err


def test_ad4_cli_loi_ket_noi_khong_in_mat_khau(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    monkeypatch.setenv("HAIDO_DATABASE_URL", f"postgresql+psycopg://u:{CANARY}@127.0.0.1:1/d?connect_timeout=2")
    monkeypatch.setenv("HAIDO_SCRAPER_DATABASE_URL", f"postgresql://u:{CANARY}@127.0.0.1:1/d?connect_timeout=2")
    for command in ("ingest", "lifecycle"):
        assert cli.main([command, "--snapshot", S]) == 1
        captured = capsys.readouterr()
        assert "Lỗi cơ sở dữ liệu" in captured.err
        assert CANARY not in captured.out + captured.err


def test_ad4_cli_thieu_lenh_thi_ma_thoat_khac_0() -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main([])
    assert exc.value.code != 0


def test_ad4_cli_chay_duoc_nhu_module_va_ma_thoat_truyen_ra_ngoai() -> None:
    res = subprocess.run(
        [sys.executable, "-m", "haido_core.cli", "ingest", "--snapshot", "2026-13-01"],
        capture_output=True,
        env={**{k: v for k, v in os.environ.items() if not k.startswith("HAIDO_")}, "PYTHONUTF8": "1"},
        cwd=ROOT,
        check=False,
    )
    assert res.returncode != 0
    assert b"YYYY-MM-DD" in res.stderr
