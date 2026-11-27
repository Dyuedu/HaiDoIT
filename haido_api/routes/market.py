"""Các route số liệu thị trường. Route chỉ chuyển tham số cho nguồn; không tính gì (AD-5).

Mỗi phép chọn nguồn riêng qua biến môi trường, mặc định `fake`:

- `HAIDO_MARKET_SOURCE_CITY_SHARES` cho `GET /api/v1/city-shares` (bản thật `stat`: #93, đọc `stat_*`);
- `HAIDO_MARKET_SOURCE_SKILL_RATES` cho `GET /api/v1/skill-rates` (bản thật: #27);
- `HAIDO_MARKET_SOURCE_NEWCOMER_ROLES` cho `GET /api/v1/newcomer-roles` (bản thật: #145, #146);
- `HAIDO_MARKET_SOURCE_LEARNING_PATH` cho `GET /api/v1/learning-path` (bản thật: #216);
- `HAIDO_MARKET_SOURCE_SKILL_ROLES` cho `GET /api/v1/skill-roles` (bản thật: #168);
- `HAIDO_MARKET_SOURCE_POSTING_CHECK` cho `GET /api/v1/posting-check` (bản thật: #234). `stat` ném `CheckUnavailable` (503 `check_unavailable`)
  cho tới đó.

`POST /api/v1/posting-reads` (#230) không phải số liệu thị trường nên có nguồn riêng, `HAIDO_POSTING_READER` (xem `routes/posting.py`).

Thêm bản thật là thêm một mục vào `IMPLEMENTATIONS`; route và schema không đổi.
"""

import os
from collections.abc import Callable, Mapping
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, Query, Request
from fastapi.exceptions import RequestValidationError

from haido_api.advisor_service import build_advisor_roadmap
from haido_api.fake_market import FakeMarket
from haido_api.market_source import MarketReadModel, UnknownSkill
from haido_api.schemas.error import ErrorEnvelope
from haido_api.schemas.learning_path import AdvisorRoadmapData, LearningPathData
from haido_api.schemas.market import (
    CitySharesData,
    MarketOverviewData,
    NewcomerRolesData,
    SkillRatesData,
    SkillRolesData,
)
from haido_api.schemas.posting import (
    MAX_COLLECTED_REPOSTS,
    MAX_COLLECTED_SNAPSHOTS,
    MAX_FEES_PARAM,
    MAX_SALARY,
    MAX_YEARS_MIN,
    ContactChannel,
    PostingCheckData,
    PostingFacts,
    PostingSalary,
    SalaryCurrency,
    SalaryPeriod,
    branch_codes,
    title_level_codes,
)
from haido_api.stat_market import StatMarket
from haido_core.config import ALL_LEVELS, ANY_YEARS, load_rules
from haido_core.domain.envelope import Envelope
from haido_core.vocab.skills import (
    MAX_PROFILE_SKILLS,
    MAX_SKILL_CODE_LEN,
    SKILL_CODE_PATTERN,
    find_seed_skill,
    is_skill_code,
)

LEVEL_CODES: tuple[str, ...] = (ALL_LEVELS, *load_rules().level_options)
"""Cấp bậc lọc được: `all` cộng `level_options` của `config/rules.toml` (#163, #134). Đọc một lần lúc import."""
LevelCode = Literal[LEVEL_CODES]

YEARS_CODES: tuple[str, ...] = (ANY_YEARS, *(str(n) for n in load_rules().years_options))
"""Mốc số năm lọc được: `any` cộng `years_options` của `config/rules.toml` (#280). Đọc một lần lúc import."""
YearsCode = Literal[YEARS_CODES]

SOURCE_ENV: dict[str, str] = {
    "city_shares": "HAIDO_MARKET_SOURCE_CITY_SHARES",
    "skill_rates": "HAIDO_MARKET_SOURCE_SKILL_RATES",
    "newcomer_roles": "HAIDO_MARKET_SOURCE_NEWCOMER_ROLES",
    "learning_path": "HAIDO_MARKET_SOURCE_LEARNING_PATH",
    "skill_roles": "HAIDO_MARKET_SOURCE_SKILL_ROLES",
    "posting_check": "HAIDO_MARKET_SOURCE_POSTING_CHECK",
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
            raise ValueError(
                f"{var}={name!r} không phải nguồn đã biết. Chọn một trong: {known}."
            )
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
    return Query(
        min_length=1, max_length=64, pattern=r"^[a-z0-9_]+$", description=description
    )


DEFAULT_PATH_LEVEL = "entry"
"""Cấp mặc định của lộ trình: nhóm mới vào nghề (DEC-8, #134)."""


def _invalid_param(name: str) -> RequestValidationError:
    """Lỗi 422 chỉ nêu tên tham số, không lặp lại giá trị đã gửi."""
    return RequestValidationError([{"type": "value_error", "loc": ("query", name), "msg": f"{name} không hợp lệ", "input": None}])


def parse_code_list(raw: str | None, name: str) -> tuple[str, ...]:
    """`?<name>=a,b,c` thành tuple mã kỹ năng đã loại trùng, giữ thứ tự gặp đầu. Rỗng là không có mã nào.

    Raises:
        RequestValidationError: có phần tử rỗng hoặc sai định dạng mã kỹ năng, hoặc quá `MAX_PROFILE_SKILLS`
            phần tử (AD-22; đếm trước khi loại trùng).
    """
    if not raw:
        return ()
    parts = raw.split(",")
    if len(parts) > MAX_PROFILE_SKILLS or not all(is_skill_code(p) for p in parts):
        raise _invalid_param(name)
    return tuple(dict.fromkeys(parts))


def parse_have(raw: str | None) -> tuple[str, ...]:
    """`?have=a,b,c`: hồ sơ của người dùng (AD-22). Xem `parse_code_list`."""
    return parse_code_list(raw, "have")


POSTING_CHECK_PARAMS: tuple[str, ...] = (
    "role", "level", "branch", "have", "skills", "years_min", "salary_min", "salary_max", "salary_currency", "salary_period",
    "salary_non_numeric", "company_named", "contacts", "fees", "duties_described", "title_level", "collected_reposts",
    "collected_snapshots",
)  # fmt: skip
"""Mọi tham số của `posting-check`. Tham số khác (kể cả chữ tự do như `text`, `quote`, `url`) bị 422: chỉ mã và số đi lên máy chủ (AD-22).
`MAX_SALARY` (trần của `salary_min`, `salary_max`) là của schema, cùng trần với `PostingSalary` ở bước một."""


def _only_known_params(request: Request) -> None:
    """Từ chối tham số lạ của `posting-check`, không nêu tên tham số đã gửi."""
    if not set(request.query_params) <= set(POSTING_CHECK_PARAMS):
        raise _invalid_param("unknown_param")


def _posting_skills(raw: str | None) -> tuple[str, ...]:
    """`skills=`: mã của tin, mọi mã phải có trong bộ từ vựng. Cụm chưa nhận diện không thể lọt vào query dù viết snake_case."""
    codes = parse_code_list(raw, "skills")
    if any(find_seed_skill(c) is None for c in codes):
        raise _invalid_param("skills")
    return codes


def _posting_facts(
    *,
    role: str,
    branch: str | None,
    years_min: int | None,
    salary_min: int | None,
    salary_max: int | None,
    salary_currency: SalaryCurrency | None,
    salary_period: SalaryPeriod | None,
    salary_non_numeric: bool | None,
    company_named: bool | None,
    contacts: str | None,
    fees: int | None,
    duties_described: bool | None,
    title_level: str | None,
    collected_reposts: int | None,
    collected_snapshots: int | None,
) -> PostingFacts:
    """Gộp sự kiện đóng của bước 1 thành `PostingFacts`; ghép lương, nhánh hay tin thu thập sai là 422."""
    if branch is not None and branch_codes().get(branch) != role:
        raise _invalid_param("branch")  # nhánh phải thuộc vai trò đang chọn: đổi vai trò thì bỏ nhánh
    if title_level is not None and title_level not in title_level_codes():
        raise _invalid_param("title_level")
    if (collected_reposts is None) != (collected_snapshots is None):
        raise _invalid_param("collected_reposts")  # hai số của một tin khớp đi cặp
    salary: PostingSalary | None = None
    has_amount = salary_min is not None or salary_max is not None
    has_unit = salary_currency is not None or salary_period is not None
    if has_amount != has_unit or (has_amount and (salary_currency is None or salary_period is None)):
        raise _invalid_param("salary_currency")
    if salary_non_numeric and has_amount:
        raise _invalid_param("salary_non_numeric")  # có số thì không thể "lương không có số"
    if has_amount and salary_currency is not None and salary_period is not None:
        if salary_min is not None and salary_max is not None and salary_min > salary_max:
            raise _invalid_param("salary_min")
        salary = PostingSalary(min=salary_min, max=salary_max, currency=salary_currency, period=salary_period)
    channels: list[ContactChannel] = []
    if contacts:
        known = {c.value for c in ContactChannel}
        parts = contacts.split(",")
        if len(set(parts)) != len(parts) or not set(parts) <= known:
            raise _invalid_param("contacts")
        channels = [ContactChannel(p) for p in parts]
    return PostingFacts(
        branch=branch,
        years_min=years_min,
        salary=salary,
        salary_non_numeric=bool(salary_non_numeric),
        company_named=company_named,
        contacts=tuple(channels),
        fees=fees,
        duties_described=duties_described,
        title_level=title_level,
        collected_reposts=collected_reposts,
        collected_snapshots=collected_snapshots,
    )


router = APIRouter(
    prefix="/api/v1",
    tags=["market"],
    responses={
        404: {
            "model": ErrorEnvelope,
            "description": (
                "Không có ô thống kê cho tham số đã chọn (`unknown_cell`), hoặc mã kỹ năng không có trong bộ từ vựng "
                "(`unknown_skill`, chỉ ở `skill-roles`)."
            ),
        },
        422: {
            "model": ErrorEnvelope,
            "description": "Tham số truy vấn thiếu hoặc sai (`invalid_query`).",
        },
        500: {
            "model": ErrorEnvelope,
            "description": "Lỗi máy chủ (`internal_error`, `invalid_response`).",
        },
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
    years: Annotated[
        YearsCode,
        Query(
            description=(
                "Mốc số năm kinh nghiệm: `any` (mặc định, mọi tin, gồm cả tin không ghi số năm) hoặc `N`: chỉ tin yêu "
                "cầu tối thiểu không quá N năm. Danh sách lấy từ `config/rules.toml`."
            )
        ),
    ] = ANY_YEARS,
) -> Envelope[CitySharesData]:
    """Tỷ trọng từng thành phố trong số tin của vai trò ở cấp bậc và mốc số năm đã chọn, trên toàn quốc (FR-33).

    Thành phố dưới ngưỡng mẫu của bộ lọc đã chọn vẫn có giá trị, kèm `display = low_sample_shown`. Ở một mốc số năm,
    `data.years_unstated` là số tin của vai trò ở cấp đó không ghi số năm (#280).
    """
    return source.city_shares(role=role, level=level, years=years)


@router.get(
    "/skill-rates",
    response_model=Envelope[SkillRatesData],
    summary="Tỷ lệ xuất hiện kỹ năng của một ô",
)
def get_skill_rates(
    role: Annotated[str, _code("Mã vai trò, snake_case.")],
    level: Annotated[
        LevelCode,
        Query(description="Cấp bậc lọc, như `city-shares`. Màn hồ sơ kỹ năng mặc định gửi `entry` (#134)."),
    ],
    source: Annotated[MarketReadModel, Depends(_source_for("skill_rates"))],
    have: Annotated[
        str | None,
        Query(
            description=(
                "Mã kỹ năng người dùng đã có, như `learning-path` (AD-22): ngăn bằng dấu phẩy, tối đa 200 mã. "
                "Đặt cờ `have` từng dòng và đếm `data.have_core`; không đổi thứ tự dòng."
            ),
        ),
    ] = None,
) -> Envelope[SkillRatesData]:
    """Tỷ lệ xuất hiện của từng kỹ năng trong ô của vai trò × cấp bậc.

    Khi ô đã chọn không đủ mẫu, số lấy từ ô rộng hơn; `data.cell_id` là ô đã dùng và
    `meta.cells[data.cell_id].fallback_label` giải thích. Dưới ngưỡng thì `rate` là
    `null_data`, `group` là `null`, `core_size` và `have_core` là `null`. Dòng đã theo thứ tự hiển thị.
    """
    return source.skill_rates(role=role, level=level, have=parse_have(have))


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


@router.get(
    "/market-overview",
    response_model=Envelope[MarketOverviewData],
    summary="Toàn cảnh thị trường: cấp bậc, vai trò, nơi làm việc, số năm kinh nghiệm",
)
def get_market_overview(
    source: Annotated[MarketReadModel, Depends(_source_for("newcomer_roles"))],
) -> Envelope[MarketOverviewData]:
    """Toàn cảnh của snapshot mới nhất (#327, #326). Mọi tỷ trọng đã tính và đã ẩn theo ngưỡng ở máy chủ; web chỉ in
    (AD-22). Số tin của từng phần ở `meta.cells[share.cell_id].n`. Dòng đã theo thứ tự hiển thị.

    Đọc cùng nguồn với `newcomer-roles` (biến `HAIDO_MARKET_SOURCE_NEWCOMER_ROLES`): hai phép cùng đọc ô toàn quốc.
    """
    return source.market_overview()


@router.get(
    "/learning-path",
    response_model=Envelope[LearningPathData],
    summary="Lộ trình học của một vai trò",
)
def get_learning_path(
    role: Annotated[str, _code("Mã vai trò, snake_case.")],
    source: Annotated[MarketReadModel, Depends(_source_for("learning_path"))],
    level: Annotated[
        LevelCode,
        Query(
            description="Cấp bậc lọc, như `city-shares`. Mặc định `entry` (Intern, Fresher, Junior gộp một)."
        ),
    ] = DEFAULT_PATH_LEVEL,
    have: Annotated[
        str | None,
        Query(
            description=(
                "Mã kỹ năng người dùng đã có, ngăn bằng dấu phẩy, tối đa 200 mã, mỗi mã snake_case tối đa 40 ký tự (AD-22). "
                "Mã trùng chỉ tính một lần (trần 200 đếm trên số mã gửi lên, trước khi loại trùng); mã không có trên lộ "
                "trình vào `data.have_ignored`. Chỉ đọc một tham số `have`: lặp lại `have` thì lấy cái cuối. "
                "Hồ sơ 200 mã dài có thể làm URL khoảng 8 KB."
            ),
        ),
    ] = None,
) -> Envelope[LearningPathData]:
    """Lộ trình học đã xếp theo chặng, mỗi kỹ năng có tỷ lệ xuất hiện (FR-22).

    Chặng là thuộc tính của kỹ năng: `have` không đổi thứ tự, chỉ đổi cờ `have` và `have_on_path`, `current_stage`,
    `have_ignored`. Vai trò chưa có lộ trình đã rà soát trả 200 với `status = not_ready`. Số tin entry-level của vai
    trò là `meta.cells[data.entry_cell_id].n`, có cả khi `data.cell_id` đã quay về ô rộng hơn.
    """
    return source.learning_path(role=role, level=level, have=parse_have(have))


@router.get(
    "/posting-check",
    response_model=Envelope[PostingCheckData],
    summary="Soi một tin dán: mức khớp kỹ năng, so thị trường, dấu hiệu cần kiểm",
    responses={
        503: {
            "model": ErrorEnvelope,
            "description": (
                "Chưa có số thật để soi tin (`check_unavailable`, tới #234): lỗi tạm thời, thử lại được, khác 404 `unknown_cell` "
                "(vai trò và cấp không có ô). Production trả mã này cho tới khi nối số thật, không bao giờ số giả."
            ),
        },
    },
)
def get_posting_check(
    role: Annotated[str, _code("Mã vai trò, snake_case: vai trò nhận diện được ở `POST /api/v1/posting-reads`, hoặc người dùng đổi.")],
    level: Annotated[
        LevelCode,
        Query(description="Cấp bậc, như `skill-rates`: cấp nhận diện được ở bước một, hoặc người dùng đổi."),
    ],
    source: Annotated[MarketReadModel, Depends(_source_for("posting_check"))],
    _known: Annotated[None, Depends(_only_known_params)],
    branch: Annotated[
        str | None,
        _code("Mã nhánh của vai trò (FR-27, `branch` của bước một), phải thuộc `role` (`config/classify.toml`); được lặp lại ở `data.branch`."),
    ] = None,
    have: Annotated[
        str | None,
        Query(
            description=(
                "Hồ sơ: mã kỹ năng người dùng đã có, ngăn bằng dấu phẩy, tối đa 200 mã (AD-22), cùng bộ đọc với `skill-rates`. "
                "Rỗng là không có hồ sơ: không có cờ `have`, mức khớp hay đếm theo nhóm."
            ),
        ),
    ] = None,
    skills: Annotated[
        str | None,
        Query(
            description=(
                "Mã kỹ năng của tin (`skills[].code` của bước một), ngăn bằng dấu phẩy, tối đa 200 mã. Mọi mã phải có trong bộ "
                "từ vựng (`GET /api/v1/skills`); cụm chưa nhận diện không bao giờ đi vào query."
            ),
        ),
    ] = None,
    years_min: Annotated[
        int | None, Query(ge=0, le=MAX_YEARS_MIN, description="`years_min` của bước một, cho #125. #230 chỉ kiểm định dạng.")
    ] = None,
    salary_min: Annotated[
        int | None, Query(ge=0, le=MAX_SALARY, description="`salary.min` của bước một, cho #125. Cần cả tiền tệ và kỳ.")
    ] = None,
    salary_max: Annotated[
        int | None, Query(ge=0, le=MAX_SALARY, description="`salary.max` của bước một, cho #125. Cần cả tiền tệ và kỳ.")
    ] = None,
    salary_currency: Annotated[SalaryCurrency | None, Query(description="`salary.currency` của bước một.")] = None,
    salary_period: Annotated[SalaryPeriod | None, Query(description="`salary.period` của bước một.")] = None,
    salary_non_numeric: Annotated[
        bool | None,
        Query(description="`salary_non_numeric` của bước một: tin có nói về lương mà không có số. Không đi cùng `salary_min` hay `salary_max`."),
    ] = None,
    company_named: Annotated[bool | None, Query(description="`company_named` của bước một, cho #126.")] = None,
    contacts: Annotated[
        str | None,
        Query(description="`contacts` của bước một, ngăn bằng dấu phẩy, mỗi mã là một kênh trong tập đóng, cho #126."),
    ] = None,
    fees: Annotated[
        int | None,
        Query(ge=0, le=MAX_FEES_PARAM, description="Số trích dẫn phí hoặc đặt cọc của bước một (không phải chính chữ), cho #126."),
    ] = None,
    duties_described: Annotated[bool | None, Query(description="`duties_described` của bước một: tin có mô tả công việc, cho #244.")] = None,
    title_level: Annotated[
        str | None,
        _code("`title_level` của bước một: mã cấp bậc mà chức danh cho biết (không gồm `unknown`), cho #244. Không bao giờ là chữ của chức danh."),
    ] = None,
    collected_reposts: Annotated[
        int | None,
        Query(
            ge=0,
            le=MAX_COLLECTED_REPOSTS,
            description="`collected.repost_count` của bước một: số lần đăng lại của tin thu thập khớp, cho D4 (#246). Vắng mặt là không khớp; đi cặp với `collected_snapshots`.",
        ),
    ] = None,
    collected_snapshots: Annotated[
        int | None,
        Query(
            ge=1,
            le=MAX_COLLECTED_SNAPSHOTS,
            description="`collected.snapshots_seen` của bước một: số snapshot mà tin khớp xuất hiện, cho D4 (#246). Đi cặp với `collected_reposts`.",
        ),
    ] = None,
) -> Envelope[PostingCheckData]:
    """Bước hai của tin dán: chỉ mã và số, không bao giờ có chữ của tin (AD-22, AD-11).

    `data.match` có số: từng kỹ năng của tin kèm nhóm, tỷ lệ trong ô và cờ `have`; mức khớp theo trọng số thị trường (FR-28); đếm
    theo nhóm; kỹ năng nên đặt đầu CV. Ô dưới ngưỡng quay về ô rộng hơn như `skill-rates` (`data.cell_id`, nhãn ở
    `meta.cells[data.cell_id].fallback_label`); cấp `unknown` (tin không ghi cấp) và cấp không có ô quay về ô mọi cấp của vai trò.
    `data.market` (#125, FR-30) và `data.warnings` (#126, FR-31) có `status = not_ready` và rỗng cho tới khi #240–#246 xong; hình
    khi `ready` đã chốt đầy đủ trong schema (phân vị kèm khoảng tin cậy, lương đã quy đổi, bảy dấu hiệu D1 đến D7). Tham số lạ,
    nhánh không thuộc vai trò hoặc mã kỹ năng ngoài bộ từ vựng: 422. Chưa có số thật: 503 `check_unavailable`.
    """
    facts = _posting_facts(
        role=role,
        branch=branch,
        years_min=years_min,
        salary_min=salary_min,
        salary_max=salary_max,
        salary_currency=salary_currency,
        salary_period=salary_period,
        salary_non_numeric=salary_non_numeric,
        company_named=company_named,
        contacts=contacts,
        fees=fees,
        duties_described=duties_described,
        title_level=title_level,
        collected_reposts=collected_reposts,
        collected_snapshots=collected_snapshots,
    )
    return source.posting_check(
        role=role, level=level, have=parse_have(have), skills=_posting_skills(skills), facts=facts
    )


@router.get(
    "/skill-roles",
    response_model=Envelope[SkillRolesData],
    summary="Một kỹ năng qua các vai trò",
)
def get_skill_roles(
    skill: Annotated[
        str,
        Query(
            min_length=1,
            max_length=MAX_SKILL_CODE_LEN,
            pattern=SKILL_CODE_PATTERN,
            description="Mã kỹ năng trong bộ từ vựng (`GET /api/v1/skills`), snake_case, tối đa 40 ký tự.",
        ),
    ],
    source: Annotated[MarketReadModel, Depends(_source_for("skill_roles"))],
) -> Envelope[SkillRolesData]:
    """Mỗi vai trò một dòng: tỷ lệ tin entry-level (Intern/Fresher/Junior) của vai trò có nhắc kỹ năng (FR-9, #113).

    Cấp bậc cố định là nhóm `entry` (`data.level`). Cỡ mẫu của tỷ lệ là
    `meta.cells[row.share.cell_id].n_by_measure.skill_count` (số tin đã quét kỹ năng; `n` của ô là số tin của ô); dưới
    ngưỡng mẫu thì `share.display = null_data` (ghi "not enough data (skill_count/min_sample)"). `data.mentioned = false`
    khi không tin nào, ở cấp nào, nhắc kỹ năng. Dòng đã theo thứ tự hiển thị. Mã không có trong bộ từ vựng: 404 `unknown_skill`.
    """
    if find_seed_skill(skill) is None:
        raise UnknownSkill("Kỹ năng đã chọn không có trong bộ từ vựng.")
    return source.skill_roles(skill=skill)


@router.post(
    "/advisor/roadmap",
    response_model=Envelope[AdvisorRoadmapData],
    summary="Phân tích CV theo vai trò & cấp bậc để tạo lộ trình roadmap.sh",
)
async def post_advisor_roadmap(
    request: Request,
    source: Annotated[MarketReadModel, Depends(_source_for("skill_rates"))],
) -> Envelope[AdvisorRoadmapData]:
    """Nhận file CV (PDF/DOCX trong bộ nhớ, không lưu), `role`, `level`, `consent` và sinh lộ trình học từ yêu cầu JD thật."""
    return await build_advisor_roadmap(request, skill_rates_source=source)
