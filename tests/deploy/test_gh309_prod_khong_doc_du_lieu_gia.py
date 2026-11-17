"""#309 — production không bao giờ phục vụ fixture giả của thị trường.

Mã mặc định chọn `fake` cho mọi nguồn (`haido_api.routes.market.DEFAULT_SOURCE`), nên mỗi nguồn trong `SOURCE_ENV`
phải được đặt `stat` trong `deploy/compose.prod.yml`. Thêm một nguồn mới mà quên dòng này thì test đỏ, thay vì số giả
lặng lẽ lên prod mang meta `published` và tên nguồn thật. compose.local giữ `fake` cho smoke của CI trên DB rỗng.
"""

from pathlib import Path

import pytest
import yaml

from haido_api.routes.market import DEFAULT_SOURCE, SOURCE_ENV, load_sources
from haido_api.stat_market import StatMarket

ROOT = Path(__file__).resolve().parents[2]


def _api_env(compose: str) -> dict[str, str]:
    env = yaml.safe_load((ROOT / "deploy" / compose).read_text(encoding="utf-8"))["services"]["api"]["environment"]
    assert isinstance(env, dict)
    return {k: str(v) for k, v in env.items()}


@pytest.mark.parametrize("op", sorted(SOURCE_ENV))
def test_gh309_compose_prod_dat_stat_cho_moi_nguon(op: str) -> None:
    assert _api_env("compose.prod.yml").get(SOURCE_ENV[op]) == "stat", (
        f"{SOURCE_ENV[op]} chưa đặt `stat` trong compose.prod.yml: prod sẽ phục vụ số giả của `{DEFAULT_SOURCE}`."
    )


def test_gh309_moi_nguon_cua_prod_dung_ban_that() -> None:
    env = {k: v for k, v in _api_env("compose.prod.yml").items() if k in SOURCE_ENV.values()}
    sources = load_sources(env)
    fake = sorted(op for op, src in sources.items() if not isinstance(src, StatMarket))
    assert fake == [], f"prod vẫn dựng nguồn giả cho: {', '.join(fake)}"


@pytest.mark.parametrize("op", sorted(SOURCE_ENV))
def test_gh309_compose_local_giu_nguon_gia(op: str) -> None:
    # Smoke của CI chạy compose.local trên DB rỗng; nguồn `stat` sẽ trả 404.
    assert _api_env("compose.local.yml").get(SOURCE_ENV[op], DEFAULT_SOURCE) == DEFAULT_SOURCE
