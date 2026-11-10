"""#262 — bật deploy: migration trước API, compose.prod lên VPS, rebuild khi đổi khóa phụ thuộc."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DEPLOY = ROOT / ".github" / "workflows" / "deploy.yml"
VPS_SCRIPT = ROOT / "deploy" / "vps-deploy.sh"


def _workflow() -> tuple[str, dict]:
    text = DEPLOY.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    assert isinstance(data, dict)
    return text, data


def _vps_script() -> str:
    return VPS_SCRIPT.read_text(encoding="utf-8")


def _on(data: dict) -> dict:
    trigger = data.get("on", data.get(True))
    assert isinstance(trigger, dict)
    return trigger


def _deploy_steps(data: dict) -> list[dict]:
    steps = data["jobs"]["deploy"]["steps"]
    assert isinstance(steps, list)
    return steps


def test_gh262_doi_khoa_phu_thuoc_va_dockerignore_thi_build_lai() -> None:
    _, data = _workflow()
    paths = _on(data)["push"]["paths"]
    for item in ("pyproject.toml", "uv.lock", "alembic.ini", ".dockerignore"):
        assert item in paths


def test_gh262_job_deploy_checkout_va_chep_compose_prod() -> None:
    text, data = _workflow()
    steps = _deploy_steps(data)
    assert any(str(step.get("uses", "")).startswith("actions/checkout@") for step in steps)
    assert 'scp deploy/compose.prod.yml "$USER@$HOST:$VPS_PATH/compose.prod.yml"' in text


def test_gh262_alembic_truoc_up_khong_an_stdin() -> None:
    text = _vps_script()
    migrate = text.index("alembic upgrade head")
    up = text.index("up -d --remove-orphans")
    assert migrate < up
    line = text[text.rfind("\n", 0, migrate) + 1 : text.find("\n", migrate)]
    assert "--no-deps" in line
    assert "HAIDO_ALLOW_REMOTE_MIGRATION=1" in line
    assert "alembic upgrade head < /dev/null" in line


def test_gh262_project_prod_khac_scraper() -> None:
    prod = yaml.safe_load((ROOT / "deploy" / "compose.prod.yml").read_text(encoding="utf-8"))
    scraper = yaml.safe_load((ROOT / "deploy" / "compose.scraper.yml").read_text(encoding="utf-8"))
    assert prod["name"] == "haido-prod"
    assert scraper.get("name") != "haido-prod"
    assert "scraper" not in prod["services"]
    assert "warehouse" not in prod["services"]
    assert "scraper-browser" not in prod["services"]


def test_gh262_suc_khoe_api_va_web_tren_may_chu_sau_up() -> None:
    text = _vps_script()
    up = text.index("up -d --remove-orphans")
    api = text.index("http://127.0.0.1:8000/openapi.json")
    web = text.index("http://127.0.0.1:3000")
    assert up < api < web or up < web < api


def test_gh262_khoa_deploy_enabled_va_token_keo_image() -> None:
    text, data = _workflow()
    assert "vars.DEPLOY_ENABLED == 'true'" in text
    deploy_runs = "\n".join(step.get("run", "") for step in _deploy_steps(data) if step.get("run"))
    assert "${GHCR_PULL_TOKEN:-$GITHUB_TOKEN}" in deploy_runs
    deploy_runs += "\n" + _vps_script()
    assert "docker login ghcr.io" in deploy_runs
    assert "Không suy ra được URL kho" in deploy_runs
    assert "postgresql+psycopg://" in deploy_runs
    assert "export HAIDO_DATABASE_URL" in deploy_runs
    assert 'echo "$HAIDO_DATABASE_URL"' not in deploy_runs
    assert 'echo "$DATABASE_URL"' not in deploy_runs
