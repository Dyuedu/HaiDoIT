"""#146 — production trả số người mới từ snapshot đã công bố; compose local giữ bản giả cho smoke của CI."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
NEWCOMER_VAR = "HAIDO_MARKET_SOURCE_NEWCOMER_ROLES"


def _api_env(compose: str) -> dict[str, str]:
    env = yaml.safe_load((ROOT / "deploy" / compose).read_text(encoding="utf-8"))["services"]["api"]["environment"]
    assert isinstance(env, dict)
    return {k: str(v) for k, v in env.items()}


def test_gh146_compose_prod_chon_nguon_stat_cho_newcomer_roles() -> None:
    assert _api_env("compose.prod.yml").get(NEWCOMER_VAR) == "stat"


def test_gh146_compose_local_giu_nguon_gia_cho_newcomer_roles() -> None:
    # Smoke của CI chạy compose.local trên DB rỗng; nguồn `stat` sẽ trả 404.
    assert _api_env("compose.local.yml").get(NEWCOMER_VAR, "fake") == "fake"
