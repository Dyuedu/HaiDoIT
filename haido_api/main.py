"""App FastAPI của Hải Đồ IT.

Chạy: `uv run uvicorn haido_api.main:app`. Chọn nguồn từng phép qua
`HAIDO_MARKET_SOURCE_CITY_SHARES` và `HAIDO_MARKET_SOURCE_SKILL_RATES` (mặc định `fake`).
"""

from collections.abc import Mapping

from fastapi import FastAPI

from haido_api.errors import install_error_handlers
from haido_api.market_source import MarketReadModel
from haido_api.routes import market


def create_app(sources: Mapping[str, MarketReadModel] | None = None) -> FastAPI:
    """Dựng app. `sources` ánh xạ tên phép sang nguồn; bỏ trống thì đọc biến môi trường."""
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
    return app


app = create_app()
