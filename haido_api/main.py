"""App FastAPI của Hải Đồ IT.

Chạy: `uv run uvicorn haido_api.main:app`. Chọn nguồn từng phép qua
`HAIDO_MARKET_SOURCE_CITY_SHARES` và `HAIDO_MARKET_SOURCE_SKILL_RATES` (mặc định `fake`).
"""

import os
from collections.abc import Mapping

from fastapi import FastAPI

from haido_api.errors import install_error_handlers
from haido_api.market_source import MarketReadModel
from haido_api.response_cache import (
    CACHE_ENV,
    DEFAULT_MAX_ENTRIES,
    ResponseCache,
    ResponseStore,
)
from haido_api.routes import market, roles, skills


def create_app(
    sources: Mapping[str, MarketReadModel] | None = None,
    *,
    response_cache: bool | None = None,
    cache_max_entries: int = DEFAULT_MAX_ENTRIES,
) -> FastAPI:
    """Dựng app. `sources` ánh xạ tên phép sang nguồn; bỏ trống thì đọc biến môi trường.

    `response_cache` bỏ trống thì bật khi `HAIDO_RESPONSE_CACHE=on` (#343).
    """
    chosen = dict(sources) if sources is not None else market.load_sources()
    missing = sorted(set(market.SOURCE_ENV) - set(chosen))
    if missing:
        raise ValueError(f"Thiếu nguồn cho phép: {', '.join(missing)}.")

    app = FastAPI(
        title="Hải Đồ IT API",
        version="0.1.0",
        description=(
            "Mọi response chứa số có dạng `{data, meta}` (AD-17); mọi lỗi có dạng "
            "`{error: {code, message, snapshot_date}}`. Xem `docs/api/envelope-meta.md`."
        ),
    )
    app.state.market_sources = chosen
    install_error_handlers(app)
    app.include_router(market.router)
    app.include_router(skills.router)
    app.include_router(roles.router)

    if response_cache is None:
        response_cache = os.environ.get(CACHE_ENV, "").strip().lower() == "on"
    if response_cache:
        store = ResponseStore(cache_max_entries)
        app.state.response_cache = store
        distinct = list({id(src): src for src in chosen.values()}.values())

        def version() -> str:
            return "/".join(src.version() for src in distinct)

        app.add_middleware(ResponseCache, store=store, version=version)
    return app


app = create_app()
