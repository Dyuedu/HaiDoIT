"""Kiểm thử AD-25: Alembic một head và an toàn môi trường."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from haido_core.db.migrations.env import get_url, validate_migration_target
from tools.gates import check_gates


def test_ad25_rejects_remote_host_without_flag():
    url = "postgresql+psycopg://admin:super_secret_pw123@db.supabase.co:5432/haido"
    with pytest.raises(ValueError) as exc_info:
        validate_migration_target(url, allow_remote=False)

    msg = str(exc_info.value)
    # Lỗi phải bằng tiếng Việt
    assert "từ chối" in msg.lower() or "chưa đặt cờ" in msg.lower() or "không được phép" in msg.lower()
    # Tuyệt đối không in mật khẩu
    assert "super_secret_pw123" not in msg


def test_ad25_rejects_password_with_at_without_leaking():
    url = "postgresql+psycopg://admin:Pa@ssw0rd@db.supabase.co/d"
    with pytest.raises(ValueError) as exc_info:
        validate_migration_target(url, allow_remote=False)

    msg = str(exc_info.value)
    assert "ssw0rd" not in msg
    assert "db.supabase.co" not in msg


def test_ad25_rejects_wrong_driver():
    url = "postgresql://u:p@localhost/d"
    with pytest.raises(ValueError) as exc_info:
        validate_migration_target(url, allow_remote=False)

    msg = str(exc_info.value)
    assert "postgresql+psycopg" in msg


def test_ad25_get_url_unset_raises_error(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("HAIDO_DATABASE_URL", raising=False)
    with pytest.raises(ValueError) as exc_info:
        get_url()
    assert "chưa được thiết lập" in str(exc_info.value)


def test_ad25_rejects_url_without_host():
    url = "postgresql+psycopg:///d"
    with pytest.raises(ValueError) as exc_info:
        validate_migration_target(url, allow_remote=False)
    assert "không thể xác định host" in str(exc_info.value).lower()


def test_ad25_alembic_cli_rejects_remote_host(monkeypatch: pytest.MonkeyPatch):
    env = os.environ.copy()
    env["HAIDO_DATABASE_URL"] = "postgresql+psycopg://u:CANARYPW@remote.invalid/d"
    env.pop("HAIDO_ALLOW_REMOTE_MIGRATION", None)
    env["PYTHONUTF8"] = "1"
    res = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
        encoding="utf-8",
    )
    assert res.returncode != 0
    assert "từ chối" in res.stderr.lower()
    assert "CANARYPW" not in res.stdout
    assert "CANARYPW" not in res.stderr


def test_ad25_rejects_query_param_host_without_flag():
    url = "postgresql+psycopg://u:secret_in_query@localhost:5432/d?host=evil.example.com"
    with pytest.raises(ValueError) as exc_info:
        validate_migration_target(url, allow_remote=False)

    msg = str(exc_info.value)
    assert "từ chối" in msg.lower() or "chưa đặt cờ" in msg.lower()
    assert "secret_in_query" not in msg


def test_ad25_rejects_query_param_hostaddr_without_flag():
    url = "postgresql+psycopg://u:secret_in_query2@localhost:5432/d?hostaddr=10.0.0.99"
    with pytest.raises(ValueError) as exc_info:
        validate_migration_target(url, allow_remote=False)

    msg = str(exc_info.value)
    assert "từ chối" in msg.lower() or "chưa đặt cờ" in msg.lower()
    assert "secret_in_query2" not in msg


def test_ad25_allow_flag_strictly_one(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("HAIDO_DATABASE_URL", "postgresql+psycopg://admin:secret123@remote.supabase.co:5432/haido")

    # "true" không được chấp nhận
    monkeypatch.setenv("HAIDO_ALLOW_REMOTE_MIGRATION", "true")
    with pytest.raises(ValueError) as exc_info:
        get_url()
    assert "secret123" not in str(exc_info.value)

    # Chỉ "1" được chấp nhận
    monkeypatch.setenv("HAIDO_ALLOW_REMOTE_MIGRATION", "1")
    url = get_url()
    assert url is not None
    assert "remote.supabase.co" in url


def test_ad25_allows_remote_host_with_flag():
    url = "postgresql+psycopg://admin:super_secret_pw123@db.supabase.co:5432/haido"
    # Khi có cờ cho phép thì không ném lỗi
    target = validate_migration_target(url, allow_remote=True)
    assert target is not None


def test_ad25_allows_local_hosts():
    for host in ("localhost", "127.0.0.1", "postgres"):
        url = f"postgresql+psycopg://haido:localpass@{host}:5433/haido"
        target = validate_migration_target(url, allow_remote=False)
        assert target is not None


def test_ad25_single_head_gate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    vers_dir = tmp_path / "haido_core" / "db" / "migrations" / "versions"
    vers_dir.mkdir(parents=True)

    # 1 migration rỗng ban đầu -> 1 head
    (vers_dir / "0001_initial.py").write_text(
        '"""initial\n"""\nrevision = "0001"\ndown_revision = None\n',
        encoding="utf-8",
    )
    status, _detail, heads = check_gates.gate_ad25_mot_head_alembic()
    assert status == check_gates.PASS

    # Thêm migration thứ 2 cùng down_revision -> 2 heads -> đỏ
    (vers_dir / "0002_conflict.py").write_text(
        '"""conflict\n"""\nrevision = "0002"\ndown_revision = None\n',
        encoding="utf-8",
    )
    status, _detail, heads = check_gates.gate_ad25_mot_head_alembic()
    assert status == check_gates.FAIL
    assert len(heads) == 2
