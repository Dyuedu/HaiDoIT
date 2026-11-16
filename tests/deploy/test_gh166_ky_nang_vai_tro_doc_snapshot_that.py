"""#166 — production chọn nguồn `stat` cho skill-roles (404 `unknown_cell` đến khi #168 có số thật, không bao giờ số giả);
compose local giữ bản giả cho smoke của CI. Cùng khuôn với #146 và #162."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SKILL_ROLES_VAR = "HAIDO_MARKET_SOURCE_SKILL_ROLES"


def _api_env(compose: str) -> dict[str, str]:
    env = yaml.safe_load((ROOT / "deploy" / compose).read_text(encoding="utf-8"))["services"]["api"]["environment"]
    assert isinstance(env, dict)
    return {k: str(v) for k, v in env.items()}


def test_gh166_compose_prod_chon_nguon_stat_cho_skill_roles() -> None:
    assert _api_env("compose.prod.yml").get(SKILL_ROLES_VAR) == "stat"


def test_gh166_compose_local_giu_nguon_gia_cho_skill_roles() -> None:
    # Smoke của CI chạy compose.local trên DB rỗng; nguồn `stat` sẽ trả 404.
    assert _api_env("compose.local.yml").get(SKILL_ROLES_VAR, "fake") == "fake"
