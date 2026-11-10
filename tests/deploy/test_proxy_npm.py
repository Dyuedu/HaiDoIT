"""Proxy công khai: Nginx Proxy Manager đứng project riêng, web vào mạng edge."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def _load(name: str) -> dict:
    data = yaml.safe_load((ROOT / "deploy" / name).read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_proxy_project_rieng_va_cong_quan_tri_chi_localhost() -> None:
    data = _load("compose.proxy.yml")
    assert data["name"] == "haido-proxy"
    assert data["name"] != "haido-prod"
    service = data["services"]["npm"]
    assert service["environment"]["INITIAL_ADMIN_EMAIL"] == "${NPM_ADMIN_EMAIL:?}"
    assert service["environment"]["INITIAL_ADMIN_PASSWORD"] == "${NPM_ADMIN_PASSWORD:?}"
    ports = [str(item) for item in service["ports"]]
    assert "80:80" in ports
    assert "443:443" in ports
    assert "127.0.0.1:81:81" in ports
    assert not any(item.endswith(":81") and not item.startswith("127.0.0.1:") for item in ports)
    edge = data["networks"]["edge"]
    assert edge["name"] == "haido-edge"
    assert edge["external"] is True


def test_web_vao_mang_edge_api_khong() -> None:
    data = _load("compose.prod.yml")
    web_networks = data["services"]["web"]["networks"]
    assert "default" in web_networks
    assert "edge" in web_networks
    api_networks = data["services"]["api"].get("networks", ["default"])
    assert "edge" not in api_networks
    edge = data["networks"]["edge"]
    assert edge["name"] == "haido-edge"
    assert edge["external"] is True


def test_deploy_tao_mang_edge_truoc_khi_up() -> None:
    text = (ROOT / ".github" / "workflows" / "deploy.yml").read_text(encoding="utf-8")
    create = text.index("docker network create haido-edge")
    up = text.index("up -d --remove-orphans")
    assert create < up
