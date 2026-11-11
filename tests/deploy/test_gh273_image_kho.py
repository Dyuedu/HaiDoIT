"""#273 — image kho build cùng commit với API và web, lịch đêm chạy đúng image đã deploy."""

import shutil
import stat
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
DEPLOY = ROOT / ".github" / "workflows" / "deploy.yml"
VPS_SCRIPT = ROOT / "deploy" / "vps-deploy.sh"
DAILY = ROOT / "deploy" / "daily.sh"
SCRAPER_COMPOSE = ROOT / "deploy" / "compose.scraper.yml"
WAREHOUSE_IMAGE = "ghcr.io/dyuedu/haidoit-warehouse"

BASH = shutil.which("bash")
needs_bash = pytest.mark.skipif(BASH is None, reason="không có bash")


def _workflow() -> dict:
    data = yaml.safe_load(DEPLOY.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _deploy_runs() -> str:
    steps = _workflow()["jobs"]["deploy"]["steps"]
    return "\n".join(step.get("run", "") for step in steps if step.get("run"))


def test_gh273_workflow_build_image_kho() -> None:
    matrix = _workflow()["jobs"]["build"]["strategy"]["matrix"]["include"]
    apps = {item["app"]: item["dockerfile"] for item in matrix}
    assert apps.get("warehouse") == "deploy/warehouse.Dockerfile"
    assert apps.get("api") == "deploy/api.Dockerfile"
    assert apps.get("web") == "deploy/web.Dockerfile"


def test_gh273_doi_config_thi_build_lai() -> None:
    data = _workflow()
    trigger = data.get("on", data.get(True))
    assert "config/**" in trigger["push"]["paths"]


def test_gh273_deploy_chep_compose_scraper_va_daily() -> None:
    runs = _deploy_runs()
    assert 'scp -p deploy/compose.scraper.yml deploy/daily.sh "$USER@$HOST:$VPS_PATH/"' in runs


def test_gh273_compose_scraper_dung_image_da_deploy() -> None:
    services = yaml.safe_load(SCRAPER_COMPOSE.read_text(encoding="utf-8"))["services"]
    warehouse = services["warehouse"]
    assert warehouse["image"] == f"{WAREHOUSE_IMAGE}:${{HAIDO_WAREHOUSE_TAG:-none}}"
    assert "build" not in warehouse
    assert warehouse["pull_policy"] == "never"
    assert "ports" not in warehouse
    # Nhịp một không phụ thuộc image kho: scraper vẫn build trên VPS như cũ.
    assert "build" in services["scraper"]
    assert "build" in services["scraper-browser"]


def test_gh273_daily_doc_tag_truoc_khi_chay_kho() -> None:
    text = DAILY.read_text(encoding="utf-8")
    tag = text.index(".warehouse-tag")
    run = text.index("HAIDO_WAREHOUSE_TAG=")
    compose = text.index("run --rm warehouse")
    assert tag < run < compose


def test_gh273_daily_la_file_thuc_thi_trong_git() -> None:
    out = subprocess.run(
        ["git", "ls-files", "-s", "deploy/daily.sh"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert out.startswith("100755 "), out


def _stub(path: Path, body: str) -> None:
    path.write_text("#!/usr/bin/env bash\n" + body, encoding="utf-8", newline="\n")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _run_deploy(tmp_path: Path, *, healthy: bool) -> tuple[subprocess.CompletedProcess[str], Path, str]:
    vps = tmp_path / "vps"
    vps.mkdir()
    (vps / ".env").write_text("DATABASE_URL=postgres://u:p@h/db\n", encoding="utf-8", newline="\n")
    (vps / ".warehouse-tag").write_text("sha-old\n", encoding="utf-8", newline="\n")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _stub(bin_dir / "docker", 'echo "docker $*" >> "$LOG"\n[ "$1" = login ] && cat > /dev/null\nexit 0\n')
    _stub(bin_dir / "curl", 'echo "curl $*" >> "$LOG"\n[ "$HEALTHY" = 1 ]\n')
    _stub(bin_dir / "sleep", "exit 0\n")
    shutil.copy(VPS_SCRIPT, tmp_path / "vps-deploy.sh")
    assert BASH is not None
    result = subprocess.run(
        [
            BASH,
            "-c",
            'export PATH="$(pwd)/bin:$PATH" LOG="$(pwd)/log" VPS_PATH="$(pwd)/vps"; bash ./vps-deploy.sh',
        ],
        cwd=tmp_path,
        env={
            "SHA": "abc123",
            "ACTOR": "bot",
            "PULL_TOKEN": "t",
            "HEALTHY": "1" if healthy else "0",
            "PATH": str(Path(BASH).parent),
        },
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    log = (tmp_path / "log").read_text(encoding="utf-8") if (tmp_path / "log").exists() else ""
    return result, vps, log


@needs_bash
def test_gh273_deploy_keo_image_kho_va_ghi_tag_khi_khoe(tmp_path: Path) -> None:
    result, vps, log = _run_deploy(tmp_path, healthy=True)
    assert result.returncode == 0, result.stderr + result.stdout
    pull = log.index(f"docker pull {WAREHOUSE_IMAGE}:sha-abc123")
    assert pull < log.index("docker logout ghcr.io")
    assert (vps / ".warehouse-tag").read_text(encoding="utf-8").strip() == "sha-abc123"


@needs_bash
def test_gh273_deploy_hong_thi_giu_tag_cu(tmp_path: Path) -> None:
    result, vps, _ = _run_deploy(tmp_path, healthy=False)
    assert result.returncode != 0
    assert (vps / ".warehouse-tag").read_text(encoding="utf-8").strip() == "sha-old"
