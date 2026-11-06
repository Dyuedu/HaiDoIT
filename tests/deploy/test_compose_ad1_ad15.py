"""Kiểm thử cấu hình Docker Compose cho AD-1 và AD-15."""

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]


def validate_compose_prod(content: str) -> None:
    data = yaml.safe_load(content)
    assert isinstance(data, dict), "compose.prod phải là dict YAML hợp lệ"
    name = data.get("name", "")
    assert name and name != "scraper", f"Project name phải riêng, không trùng scraper: {name}"

    services = data.get("services", {})
    assert "api" in services, "compose.prod phải có service api"
    assert "web" in services, "compose.prod phải có service web"
    assert "postgres" not in services, "compose.prod không được chứa service postgres (AD-15)"

    for svc_name, svc in services.items():
        assert "build" not in svc, f"Service {svc_name} trong prod không được chứa build: (AD-15)"
        for key in ("command", "entrypoint"):
            val = svc.get(key)
            if isinstance(val, list):
                val = " ".join(str(x) for x in val)
            elif val is None:
                val = ""
            assert "next build" not in str(val), f"Service {svc_name} {key} không được chạy next build (AD-15)"

    assert services["api"].get("image") == "ghcr.io/dyuedu/haidoit-api:${IMAGE_TAG:?}", (
        "API image phải là ghcr.io/dyuedu/haidoit-api:${IMAGE_TAG:?}"
    )
    assert services["web"].get("image") == "ghcr.io/dyuedu/haidoit-web:${IMAGE_TAG:?}", (
        "Web image phải là ghcr.io/dyuedu/haidoit-web:${IMAGE_TAG:?}"
    )

    api_env = services["api"].get("environment", {})
    if isinstance(api_env, dict):
        api_db = api_env.get("HAIDO_DATABASE_URL")
    elif isinstance(api_env, list):
        api_db = next((x.split("=", 1)[1] for x in api_env if x.startswith("HAIDO_DATABASE_URL=")), None)
    else:
        api_db = None
    assert api_db == "${HAIDO_DATABASE_URL:?}", "API HAIDO_DATABASE_URL phải là ${HAIDO_DATABASE_URL:?}"


def validate_web_no_db(content: str) -> None:
    data = yaml.safe_load(content)
    assert isinstance(data, dict)
    services = data.get("services", {})
    assert "web" in services, "Service web phải tồn tại trong compose (AD-1)"
    web = services["web"]
    assert "env_file" not in web, "Service web không được dùng env_file (AD-1)"

    # AD-1: Web không nối DB
    deps = web.get("depends_on", [])
    if isinstance(deps, dict):
        deps = list(deps.keys())
    assert "postgres" not in deps, "Web không được depends_on postgres (AD-1)"

    env = web.get("environment", {})
    env_vars = []
    if isinstance(env, dict):
        env_vars = list(env.keys())
    elif isinstance(env, list):
        env_vars = [item.split("=")[0] for item in env]

    bad_vars = {"DATABASE_URL", "HAIDO_DATABASE_URL", "POSTGRES_PASSWORD", "POSTGRES_DB"}
    assert not any(v in bad_vars for v in env_vars), f"Web không được chứa biến kết nối DB: {env_vars} (AD-1)"


def validate_compose_local_no_leak(content: str) -> None:
    data = yaml.safe_load(content)
    assert isinstance(data, dict)

    # Không dùng env_file (tránh rò deploy/.env chứa Supabase thật)
    assert "env_file" not in data, "compose.local không được khai env_file ở gốc"
    for name, svc in data.get("services", {}).items():
        assert "env_file" not in svc, f"Service {name} không được dùng env_file"

    # Không nhận biến kết nối từ môi trường ngoài, kể cả dạng $VAR hay ${VAR:-x}
    raw = content
    assert not re.search(r"\$\{?(HAIDO_)?DATABASE_URL\b", raw), (
        "Không được dùng $DATABASE_URL hoặc $HAIDO_DATABASE_URL"
    )
    assert "supabase.co" not in raw and "supabase.com" not in raw, (
        "Không được chứa host Supabase thật trong compose.local"
    )

    # API connection string host phải là chính xác 'postgres'
    api = data.get("services", {}).get("api", {})
    api_env = api.get("environment", {})
    if isinstance(api_env, dict):
        api_url = str(api_env.get("HAIDO_DATABASE_URL", ""))
    elif isinstance(api_env, list):
        api_url = next((x.split("=", 1)[1] for x in api_env if x.startswith("HAIDO_DATABASE_URL=")), "")
    else:
        api_url = ""
    assert "@postgres:" in api_url or "@postgres/" in api_url, (
        f"API HAIDO_DATABASE_URL host phải là 'postgres', nhận được: {api_url}"
    )

    # Khai báo biến kết nối không có giá trị
    conn_vars = {"DATABASE_URL", "HAIDO_DATABASE_URL"}
    for name, svc in data.get("services", {}).items():
        env = svc.get("environment", {})
        if isinstance(env, dict):
            for var_name, var_val in env.items():
                if var_name in conn_vars:
                    assert var_val is not None and str(var_val).strip() != "", (
                        f"Service {name} khai biến kết nối {var_name} không có giá trị (dict form)"
                    )
        elif isinstance(env, list):
            for item in env:
                if item in conn_vars:
                    raise AssertionError(
                        f"Service {name} khai biến kết nối {item} không có giá trị (list form)"
                    )
                for cv in conn_vars:
                    if item.startswith(f"{cv}="):
                        val = item.split("=", 1)[1].strip()
                        assert val != "", (
                            f"Service {name} khai biến kết nối {cv} rỗng (list form)"
                        )

    # Postgres local chỉ bind 127.0.0.1
    pg = data.get("services", {}).get("postgres", {})
    ports = pg.get("ports", [])
    assert ports, "Postgres local phải khai báo cổng"
    for p in ports:
        port_str = str(p)
        assert port_str.startswith("127.0.0.1:"), f"Postgres local chỉ được bind 127.0.0.1: {port_str}"

    # Tên project riêng
    name = data.get("name", "")
    assert name and name != "scraper", f"Project name phải riêng, không trùng scraper: {name}"


def test_ad15_compose_prod_rules():
    prod_file = REPO_ROOT / "deploy" / "compose.prod.yml"
    assert prod_file.is_file(), "deploy/compose.prod.yml phải tồn tại"
    validate_compose_prod(prod_file.read_text(encoding="utf-8"))

    # Vi phạm: build
    bad_prod_build = """
    name: haido-prod
    services:
      web:
        build: ./web
        image: ghcr.io/dyuedu/haidoit-web:${IMAGE_TAG:?}
      api:
        image: ghcr.io/dyuedu/haidoit-api:${IMAGE_TAG:?}
        environment:
          HAIDO_DATABASE_URL: ${HAIDO_DATABASE_URL:?}
    """
    with pytest.raises(AssertionError):
        validate_compose_prod(bad_prod_build)

    # Vi phạm: list-form command next build
    bad_prod_list_cmd = """
    name: haido-prod
    services:
      web:
        image: ghcr.io/dyuedu/haidoit-web:${IMAGE_TAG:?}
        command: ["next", "build"]
      api:
        image: ghcr.io/dyuedu/haidoit-api:${IMAGE_TAG:?}
        environment:
          HAIDO_DATABASE_URL: ${HAIDO_DATABASE_URL:?}
    """
    with pytest.raises(AssertionError):
        validate_compose_prod(bad_prod_list_cmd)

    # Vi phạm: entrypoint next build
    bad_prod_entrypoint = """
    name: haido-prod
    services:
      web:
        image: ghcr.io/dyuedu/haidoit-web:${IMAGE_TAG:?}
        entrypoint: "next build"
      api:
        image: ghcr.io/dyuedu/haidoit-api:${IMAGE_TAG:?}
        environment:
          HAIDO_DATABASE_URL: ${HAIDO_DATABASE_URL:?}
    """
    with pytest.raises(AssertionError):
        validate_compose_prod(bad_prod_entrypoint)

    # Vi phạm: thiếu biến HAIDO_DATABASE_URL trên API
    bad_prod_no_api_db = """
    name: haido-prod
    services:
      web:
        image: ghcr.io/dyuedu/haidoit-web:${IMAGE_TAG:?}
      api:
        image: ghcr.io/dyuedu/haidoit-api:${IMAGE_TAG:?}
    """
    with pytest.raises(AssertionError):
        validate_compose_prod(bad_prod_no_api_db)


def test_ad1_compose_web_no_db_rules():
    for compose_name in ("compose.local.yml", "compose.prod.yml"):
        f = REPO_ROOT / "deploy" / compose_name
        assert f.is_file(), f"deploy/{compose_name} phải tồn tại"
        validate_web_no_db(f.read_text(encoding="utf-8"))

    # Vi phạm: depends_on postgres
    bad_web_dep = """
    services:
      web:
        depends_on:
          - postgres
    """
    with pytest.raises(AssertionError):
        validate_web_no_db(bad_web_dep)

    # Vi phạm: thiếu service web
    bad_web_missing = """
    services:
      api:
        image: api
    """
    with pytest.raises(AssertionError):
        validate_web_no_db(bad_web_missing)

    # Vi phạm: service web có env_file
    bad_web_env_file = """
    services:
      web:
        env_file: .env
    """
    with pytest.raises(AssertionError):
        validate_web_no_db(bad_web_env_file)


def test_ad1_compose_local_no_supabase_leak():
    local_file = REPO_ROOT / "deploy" / "compose.local.yml"
    assert local_file.is_file(), "deploy/compose.local.yml phải tồn tại"
    validate_compose_local_no_leak(local_file.read_text(encoding="utf-8"))

    # Vi phạm: env_file ở gốc
    bad_local_env_file = """
    name: haido-local
    env_file: .env
    services:
      postgres:
        image: postgres:18.6
        ports:
          - "127.0.0.1:5433:5432"
    """
    with pytest.raises(AssertionError):
        validate_compose_local_no_leak(bad_local_env_file)

    # Vi phạm: env_file dưới một service
    bad_local_svc_env_file = """
    name: haido-local
    services:
      api:
        image: api
        env_file: .env
      postgres:
        image: postgres:18.6
        ports:
          - "127.0.0.1:5433:5432"
    """
    with pytest.raises(AssertionError):
        validate_compose_local_no_leak(bad_local_svc_env_file)

    # Vi phạm: $HAIDO_DATABASE_URL
    bad_local_bare_var = """
    name: haido-local
    services:
      api:
        image: api
        environment:
          HAIDO_DATABASE_URL: $HAIDO_DATABASE_URL
      postgres:
        image: postgres:18.6
        ports:
          - "127.0.0.1:5433:5432"
    """
    with pytest.raises(AssertionError):
        validate_compose_local_no_leak(bad_local_bare_var)

    # Vi phạm: literal Supabase host
    bad_local_supabase = """
    name: haido-local
    services:
      api:
        image: api
        environment:
          HAIDO_DATABASE_URL: postgresql+psycopg://u:p@db.supabase.co:5432/d
      postgres:
        image: postgres:18.6
        ports:
          - "127.0.0.1:5433:5432"
    """
    with pytest.raises(AssertionError):
        validate_compose_local_no_leak(bad_local_supabase)

    # Vi phạm: API DB host khác 'postgres'
    bad_local_api_host = """
    name: haido-local
    services:
      api:
        image: api
        environment:
          HAIDO_DATABASE_URL: postgresql+psycopg://u:p@localhost:5432/d
      postgres:
        image: postgres:18.6
        ports:
          - "127.0.0.1:5433:5432"
    """
    with pytest.raises(AssertionError):
        validate_compose_local_no_leak(bad_local_api_host)
