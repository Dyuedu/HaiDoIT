"""Các route số liệu thị trường. Route chỉ chuyển tham số cho nguồn; không tính gì (AD-5).

Mỗi phép chọn nguồn riêng qua biến môi trường, mặc định `fake`:

- `HAIDO_MARKET_SOURCE_CITY_SHARES` cho `GET /api/v1/city-shares` (bản thật `stat`: #93, đọc `stat_*`);
- `HAIDO_MARKET_SOURCE_SKILL_RATES` cho `GET /api/v1/skill-rates` (bản thật: #27);
- `HAIDO_MARKET_SOURCE_NEWCOMER_ROLES` cho `GET /api/v1/newcomer-roles` (bản thật: #145, #146).

Thêm bản thật là thêm một mục vào `IMPLEMENTATIONS`; route và schema không đổi.
"""

import os
from collections.abc import Callable, Mapping
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, Query, Request

from haido_api.fake_market import FakeMarket
from haido_api.market_source import MarketReadModel
from haido_api.schemas.error import ErrorEnvelope
from haido_api.schemas.market import CitySharesData, NewcomerRolesData, SkillRatesData
from haido_api.stat_market import StatMarket
from haido_core.config import ALL_LEVELS, load_rules
from haido_core.domain.envelope import Envelope

LEVEL_CODES: tuple[str, ...] = (ALL_LEVELS, *load_rules().level_options)
"""Cấp bậc lọc được: `all` cộng `level_options` của `config/rules.toml` (#163, #134). Đọc một lần lúc import."""
LevelCode = Literal[LEVEL_CODES]

SOURCE_ENV: dict[str, str] = {
    "city_shares": "HAIDO_MARKET_SOURCE_CITY_SHARES",
    "skill_rates": "HAIDO_MARKET_SOURCE_SKILL_RATES",
    "newcomer_roles": "HAIDO_MARKET_SOURCE_NEWCOMER_ROLES",
}
DEFAULT_SOURCE = "fake"
IMPLEMENTATIONS: dict[str, Callable[[], MarketReadModel]] = {
    "fake": FakeMarket,
    "stat": StatMarket,
}


def load_sources(environ: Mapping[str, str] = os.environ) -> dict[str, MarketReadModel]:
    """Dựng nguồn cho từng phép theo biến môi trường. Hai phép cùng tên nguồn dùng chung một bản."""
    built: dict[str, MarketReadModel] = {}
    sources: dict[str, MarketReadModel] = {}
    for op, var in SOURCE_ENV.items():
        name = environ.get(var, "").strip() or DEFAULT_SOURCE
        if name not in IMPLEMENTATIONS:
            known = ", ".join(sorted(IMPLEMENTATIONS))
            raise ValueError(f"{var}={name!r} không phải nguồn đã biết. Chọn một trong: {known}.")
        if name not in built:
            built[name] = IMPLEMENTATIONS[name]()
        sources[op] = built[name]
    return sources


def _source_for(op: str) -> Callable[[Request], MarketReadModel]:
    def dependency(request: Request) -> MarketReadModel:
        return request.app.state.market_sources[op]

    dependency.__name__ = f"{op}_source"
    return dependency


def _code(description: str) -> Any:
    """Tham số mã: snake_case, chỉ chữ thường, số và gạch dưới."""
    return Query(min_length=1, max_length=64, pattern=r"^[a-z0-9_]+$", description=description)


router = APIRouter(
    prefix="/api/v1",
    tags=["market"],
    responses={
        404: {"model": ErrorEnvelope, "description": "Không có ô thống kê cho tham số đã chọn (`unknown_cell`)."},
        422: {"model": ErrorEnvelope, "description": "Tham số truy vấn thiếu hoặc sai (`invalid_query`)."},
        500: {"model": ErrorEnvelope, "description": "Lỗi máy chủ (`internal_error`, `invalid_response`)."},
    },
)


@router.get(
    "/city-shares",
    response_model=Envelope[CitySharesData],
    summary="Tỷ trọng thành phố của một vai trò",
)
def get_city_shares(
    role: Annotated[str, _code("Mã vai trò, snake_case; `all` là mọi vai trò.")],
    source: Annotated[MarketReadModel, Depends(_source_for("city_shares"))],
    level: Annotated[
        LevelCode,
        Query(
            description=(
                "Cấp bậc lọc: `all` (mặc định, mọi cấp), `entry` (Intern, Fresher, Junior gộp một), "
                "từng cấp, hoặc `unknown` (chưa ghi cấp bậc). Danh sách lấy từ `config/rules.toml`."
            )
        ),
    ] = ALL_LEVELS,
) -> Envelope[CitySharesData]:
    """Tỷ trọng từng thành phố trong số tin của vai trò ở cấp bậc đã chọn, trên toàn quốc (FR-33).

    Thành phố dưới ngưỡng mẫu của cấp đã chọn vẫn có giá trị, kèm `display = low_sample_shown`.
    """
    return source.city_shares(role=role, level=level)


@router.get(
    "/skill-rates",
    response_model=Envelope[SkillRatesData],
    summary="Tỷ lệ xuất hiện kỹ năng của một ô",
)
def get_skill_rates(
    role: Annotated[str, _code("Mã vai trò, snake_case.")],
    level: Annotated[str, _code("Mã cấp bậc, snake_case.")],
    source: Annotated[MarketReadModel, Depends(_source_for("skill_rates"))],
) -> Envelope[SkillRatesData]:
    """Tỷ lệ xuất hiện của từng kỹ năng trong ô của vai trò × cấp bậc.

    Khi ô đã chọn không đủ mẫu, số lấy từ ô rộng hơn; `data.cell_id` là ô đã dùng và
    `meta.cells[data.cell_id].fallback_label` giải thích. Dưới ngưỡng thì `rate` là
    `null_data` và `group` là `null`.
    """
    return source.skill_rates(role=role, level=level)


@router.get(
    "/newcomer-roles",
    response_model=Envelope[NewcomerRolesData],
    summary="Số tin entry-level của từng vai trò",
)
def get_newcomer_roles(
    source: Annotated[MarketReadModel, Depends(_source_for("newcomer_roles"))],
) -> Envelope[NewcomerRolesData]:
    """Mỗi vai trò một dòng: số tin Intern/Fresher/Junior, tỷ lệ trong số tin của vai trò, và n (#110).

    Số tin entry-level là `meta.cells[entry_cell_id].n`, n là `meta.cells[total_cell_id].n`.
    Vai trò dưới ngưỡng mẫu có `share.display = null_data`. Dòng đã theo thứ tự hiển thị.
    """
    return source.newcomer_roles()
