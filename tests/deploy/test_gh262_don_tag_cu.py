"""#262 đợt 5 — deploy xóa tag sha cũ của image api, web, kho, chỉ giữ vài bản mới nhất.

`docker image prune` chỉ xóa image dangling, nên mỗi lần deploy để lại khoảng 1,5 GB
image có tag. Ngày 2026-11-19 đĩa VPS lên 94%.
"""

import shutil
import stat
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "deploy" / "vps-deploy.sh"
BASH = shutil.which("bash")
needs_bash = pytest.mark.skipif(BASH is None, reason="không có bash")

REPOS = ("ghcr.io/dyuedu/haidoit-api", "ghcr.io/dyuedu/haidoit-web", "ghcr.io/dyuedu/haidoit-warehouse")


def _stale(tmp_path: Path, tags: list[str], *args: str) -> list[str]:
    shutil.copy(SCRIPT, tmp_path / "vps-deploy.sh")
    assert BASH is not None
    quoted = " ".join(f"'{a}'" for a in args)
    result = subprocess.run(
        [BASH, "-c", f"HAIDO_DEPLOY_LIB_ONLY=1; . ./vps-deploy.sh; stale_tags {quoted}"],
        cwd=tmp_path,
        input="".join(t + "\n" for t in tags),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.split()


@needs_bash
def test_giu_hai_tag_sha_moi_nhat(tmp_path: Path) -> None:
    tags = ["sha-e", "sha-d", "sha-c", "sha-b", "sha-a"]
    assert _stale(tmp_path, tags, "2", "sha-e") == ["sha-c", "sha-b", "sha-a"]


@needs_bash
def test_khong_xoa_tag_dang_deploy_du_cu(tmp_path: Path) -> None:
    # Rollback bằng workflow_dispatch: tag đang deploy có thể cũ hơn hai tag mới nhất.
    tags = ["sha-e", "sha-d", "sha-c", "sha-b", "sha-a"]
    assert _stale(tmp_path, tags, "2", "sha-b") == ["sha-c", "sha-a"]


@needs_bash
def test_bo_qua_tag_khong_phai_sha(tmp_path: Path) -> None:
    tags = ["local", "sha-c", "<none>", "sha-b", "main", "sha-a"]
    assert _stale(tmp_path, tags, "2", "sha-c") == ["sha-a"]


@needs_bash
def test_it_tag_thi_khong_xoa_gi(tmp_path: Path) -> None:
    assert _stale(tmp_path, ["sha-b", "sha-a"], "2", "sha-b") == []


def _stub(path: Path, body: str) -> None:
    path.write_text("#!/usr/bin/env bash\n" + body, encoding="utf-8", newline="\n")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _deploy(tmp_path: Path, *, healthy: bool, rmi_fails: bool = False) -> tuple[int, str]:
    vps = tmp_path / "vps"
    vps.mkdir()
    (vps / ".env").write_text("DATABASE_URL=postgres://u:p@h/db\n", encoding="utf-8", newline="\n")
    (tmp_path / "tags").write_text("sha-new\nsha-prev\nsha-old1\nsha-old2\n", encoding="utf-8", newline="\n")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _stub(
        bin_dir / "docker",
        'echo "docker $*" >> "$LOG"\n'
        '[ "$1" = login ] && cat > /dev/null\n'
        '[ "$1" = images ] && cat "$TAGS"\n'
        '[ "$1" = rmi ] && [ "$RMI_FAILS" = 1 ] && exit 1\n'
        "exit 0\n",
    )
    _stub(bin_dir / "curl", '[ "$HEALTHY" = 1 ]\n')
    _stub(bin_dir / "sleep", "exit 0\n")
    shutil.copy(SCRIPT, tmp_path / "vps-deploy.sh")
    assert BASH is not None
    result = subprocess.run(
        [
            BASH,
            "-c",
            'export PATH="$(pwd)/bin:$PATH" LOG="$(pwd)/log" TAGS="$(pwd)/tags" VPS_PATH="$(pwd)/vps";'
            " bash ./vps-deploy.sh",
        ],
        cwd=tmp_path,
        env={
            "SHA": "new",
            "ACTOR": "bot",
            "PULL_TOKEN": "t",
            "HEALTHY": "1" if healthy else "0",
            "RMI_FAILS": "1" if rmi_fails else "0",
            "PATH": str(Path(BASH).parent),
        },
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    log = (tmp_path / "log").read_text(encoding="utf-8")
    return result.returncode, log


@needs_bash
def test_deploy_khoe_xoa_tag_cu_cua_ba_image(tmp_path: Path) -> None:
    code, log = _deploy(tmp_path, healthy=True)
    assert code == 0, log
    removed = {line.split()[2] for line in log.splitlines() if line.startswith("docker rmi ")}
    assert removed == {f"{r}:{t}" for r in REPOS for t in ("sha-old1", "sha-old2")}


@needs_bash
def test_deploy_hong_thi_khong_xoa_tag(tmp_path: Path) -> None:
    code, log = _deploy(tmp_path, healthy=False)
    assert code != 0
    assert "docker rmi " not in log


@needs_bash
def test_xoa_tag_loi_khong_lam_hong_deploy(tmp_path: Path) -> None:
    # Image đang được container dùng (vd lượt đêm) thì rmi từ chối; deploy vẫn coi là xong.
    code, log = _deploy(tmp_path, healthy=True, rmi_fails=True)
    assert code == 0, log
    assert "docker rmi " in log
