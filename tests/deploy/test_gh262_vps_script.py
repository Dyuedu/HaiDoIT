"""#262 — script chạy trên VPS nằm trong file riêng, bash đọc được, và đọc URL kho đúng."""

import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "deploy" / "vps-deploy.sh"
DEPLOY = ROOT / ".github" / "workflows" / "deploy.yml"

BASH = shutil.which("bash")
needs_bash = pytest.mark.skipif(BASH is None, reason="không có bash")


def _deploy_step_run() -> str:
    data = yaml.safe_load(DEPLOY.read_text(encoding="utf-8"))
    steps = data["jobs"]["deploy"]["steps"]
    return next(step["run"] for step in steps if step.get("name") == "Deploy")


def _resolve(tmp_path: Path, env_text: str) -> subprocess.CompletedProcess[str]:
    shutil.copy(SCRIPT, tmp_path / "vps-deploy.sh")
    (tmp_path / ".env").write_bytes(env_text.encode("utf-8"))
    assert BASH is not None
    return subprocess.run(
        [BASH, "-c", "HAIDO_DEPLOY_LIB_ONLY=1; . ./vps-deploy.sh; resolve_db_url"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def test_gh262_workflow_gui_file_script_khong_dung_heredoc() -> None:
    run = _deploy_step_run()
    assert "<<EOF" not in run
    assert "cat deploy/vps-deploy.sh" in run
    assert "bash -se" in run
    assert "${GHCR_PULL_TOKEN:-$GITHUB_TOKEN}" in run


@needs_bash
def test_gh262_script_vps_dung_cu_phap_bash() -> None:
    assert BASH is not None
    result = subprocess.run([BASH, "-n", str(SCRIPT)], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr


@needs_bash
@pytest.mark.parametrize(
    ("env_text", "expected"),
    [
        ('HAIDO_DATABASE_URL="postgresql+psycopg://u:p@h/db"\n', "postgresql+psycopg://u:p@h/db"),
        ("HAIDO_DATABASE_URL='postgresql+psycopg://u:p@h/db'\n", "postgresql+psycopg://u:p@h/db"),
        ("HAIDO_DATABASE_URL=postgresql+psycopg://u:p@h/db\r\n", "postgresql+psycopg://u:p@h/db"),
        ('DATABASE_URL="postgresql://u:p@h/db"\n', "postgresql+psycopg://u:p@h/db"),
        ("DATABASE_URL=postgres://u:p@h/db\n", "postgresql+psycopg://u:p@h/db"),
        ("DATABASE_URL=postgresql+psycopg://u:p@h/db\n", "postgresql+psycopg://u:p@h/db"),
    ],
)
def test_gh262_script_vps_doc_url_kho_tu_env(tmp_path: Path, env_text: str, expected: str) -> None:
    result = _resolve(tmp_path, env_text)
    assert result.returncode == 0, result.stderr
    assert result.stdout == expected


@needs_bash
def test_gh262_script_vps_thieu_url_thi_dung(tmp_path: Path) -> None:
    result = _resolve(tmp_path, "OTHER=1\n")
    assert result.returncode != 0
    assert "Không suy ra được URL kho" in result.stderr
    assert result.stdout == ""
