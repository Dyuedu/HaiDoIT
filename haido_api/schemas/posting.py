"""Hình response của tin dán "Soi tin" (#230, US-D1/D2/D3).

Hai bước, hai hình:

- `POST /api/v1/posting-reads` đọc chữ dán một lần và trả `{data: PostingReadData}`: các sự kiện đóng đã trích. Không có `meta`:
  không có Stat của thị trường, không có ô thống kê, không có snapshot. Các số trong đó (`mentions`, `years_min`, `salary`,
  `collected`) là sự kiện trích từ chữ người dùng dán hoặc từ tin đã thu thập, nên quy tắc "mọi số là Stat" của AD-17 không áp
  (giống `GET /api/v1/skills` không có số nào).
- `GET /api/v1/posting-check` chỉ nhận mã và số (AD-22), trả `Envelope[PostingCheckData]` với ba mục: `match` (có số), `market`
  (#125) và `warnings` (#126). Hai mục sau luôn `not_ready` ở dữ liệu cho tới #240–#246, nhưng hình `ready` đã chốt đầy đủ ở đây
  để các issue sau chỉ thêm giá trị, không đổi hình: số trong đó là `Stat` (phân vị, ranh giới khoảng tin cậy, P90, P75, P25)
  hoặc `Ordinal` (số đếm và tiền của chính tin dán).
"""

import functools
import math
import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from haido_api.schemas.market import SkillLabel
from haido_api.schemas.skills import SkillCode
from haido_core.config import RulesConfig, load_classify_config, load_rules
from haido_core.domain.display_policy import DisplayState, MeasureKind
from haido_core.domain.envelope import CellId, Meta, Ordinal, OrdinalRef, Stat
from haido_core.vocab.skills import MAX_PROFILE_SKILLS, find_seed_skill

_CONFIG = ConfigDict(extra="forbid", use_attribute_docstrings=True, revalidate_instances="always")

PositiveOrdinal = Annotated[int, OrdinalRef(), Field(ge=1)]
"""`Ordinal` từ 1 (tỷ giá, số trích dẫn): khai báo như `Ordinal` nên không phải bọc trong `Stat`."""


@functools.cache
def _rules() -> RulesConfig:
    """`load_rules()` đọc và kiểm file TOML mỗi lần gọi; bộ kiểm của `PostingReadData` chạy cho mọi response nên đọc một lần."""
    return load_rules()


@functools.cache
def _read_vocab() -> tuple[frozenset[str], frozenset[str], frozenset[str]]:
    """(mã vai trò, mã cấp bậc, mã cấp bậc mà chức danh có thể cho biết: bỏ `unknown`)."""
    rules = _rules()
    levels = frozenset(rules.level_codes.values())
    return frozenset(rules.roles), levels, levels - {"unknown"}


def title_level_codes() -> frozenset[str]:
    """Mã cấp bậc mà chức danh có thể cho biết (`title_level`): mọi mã của `labels.level` trừ `unknown`."""
    return _read_vocab()[2]


def _slug(label: str) -> str:
    plain = unicodedata.normalize("NFKD", label).encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "_", plain).strip("_")


@functools.cache
def branch_codes() -> dict[str, str]:
    """Mã nhánh (FR-27) sang mã vai trò của nhánh đó. Mã nhánh là snake_case của nhãn trong `[[branches]]` của `config/classify.toml`
    (`Cloud` là `cloud`, `LLM / Agent` là `llm_agent`); vai trò đổi từ nhãn của bộ phân loại sang mã của `config/rules.toml`."""
    role_codes = _rules().role_codes
    found: dict[str, str] = {}
    for rule in load_classify_config().branch_rules:
        code = _slug(rule.label)
        if code in found:
            raise ValueError(f"Hai nhánh cùng mã {code!r} trong config/classify.toml.")
        found[code] = role_codes[rule.role]
    return found


# ------------------------------------------------------------------------------------------ bước 1: đọc chữ dán

MAX_TEXT_CHARS = 20_000
"""FR-26: chữ dán dài tối đa 20.000 ký tự. Bằng `posting_read.max_chars` của `config/rules.toml` (test giữ hai chỗ khớp nhau)."""

POSTING_READ_ERRORS: dict[str, int] = {
    "text_too_long": 413,
    "rate_limited": 429,
    "read_failed": 502,
    "read_unavailable": 503,
    "read_timeout": 504,
}
"""Mã lỗi (và HTTP) của `POST /api/v1/posting-reads`, theo hình lỗi chuẩn. `text_too_long` do máy chủ cài từ #230 (trần cỡ, AD-9);
`rate_limited` là trần tốc độ theo IP của #231; `read_*` là cổng model của #232. `invalid_query` (422) là thân sai hình."""

_TOO_LONG_LIMIT = f"{MAX_TEXT_CHARS:,}".replace(",", ".")
POSTING_READ_MESSAGES: dict[str, str] = {
    "text_too_long": f"Tin dán dài hơn giới hạn: tối đa {_TOO_LONG_LIMIT} ký tự. Hãy rút gọn rồi dán lại.",
    "rate_limited": "Bạn đã soi tin quá nhiều lần trong một lúc. Hãy thử lại sau.",
    "read_failed": "Chưa đọc được tin dán này. Hãy thử lại sau.",
    "read_unavailable": "Chưa đọc được tin dán lúc này. Hãy thử lại sau.",
    "read_timeout": "Đọc tin dán quá thời gian chờ. Hãy thử lại.",
}
"""Câu của máy chủ cho từng mã lỗi. Response lỗi của `posting-reads` luôn dùng câu này, không bao giờ thông điệp của nguồn đọc (AD-11)."""

MAX_UNRECOGNISED = 50
MAX_UNRECOGNISED_LEN = 60
MAX_FEE_MENTIONS = 5
MAX_FEE_QUOTE_LEN = 120
MAX_CONTACT_QUOTES = 5
MAX_CONTACT_QUOTE_LEN = 120
MAX_YEARS_MIN = 60
"""Trần số năm kinh nghiệm hợp lý của một tin; số lớn hơn là lỗi đọc, không phải sự kiện."""
MAX_SALARY = 10**10
"""Trần của lương (`min`, `max`) ở bước một và `salary_min`, `salary_max` ở bước hai: một trần chung, để tin đọc hợp lệ ở bước một
không bao giờ bị 422 ở bước hai. Đủ cho VND một tháng; lớn hơn là sai định dạng."""
MAX_COLLECTED_REPOSTS = 100_000
MAX_COLLECTED_SNAPSHOTS = 10_000

PostingReason = Literal["not_posting", "too_short", "not_it"]
SalaryCurrency = Literal["vnd", "usd"]
SalaryPeriod = Literal["month", "year"]


class ContactChannel(StrEnum):
    """Kênh liên hệ tìm thấy trong tin (tập đóng, #245)."""

    COMPANY_EMAIL = "company_email"
    COMPANY_SITE = "company_site"
    PHONE = "phone"
    ZALO = "zalo"
    TELEGRAM = "telegram"
    PERSONAL_EMAIL = "personal_email"


PERSONAL_CHANNELS: frozenset[ContactChannel] = frozenset(
    {ContactChannel.ZALO, ContactChannel.TELEGRAM, ContactChannel.PERSONAL_EMAIL}
)
"""Kênh của dấu hiệu D5 (FR-31): ứng dụng chat hoặc email cá nhân, không phải kênh của công ty."""


class PostingSkillMention(BaseModel):
    """Một kỹ năng của bộ từ vựng mà tin nhắc."""

    model_config = _CONFIG

    code: SkillCode
    """Mã kỹ năng trong bộ từ vựng, snake_case."""

    mentions: Annotated[int, Field(ge=1)]
    """Số lần tin nhắc kỹ năng. Chỉ để hiện trên màn; không đi vào query của `posting-check`."""


class PostingSalary(BaseModel):
    """Lương tin công bố dạng số."""

    model_config = _CONFIG

    min: Annotated[int, Field(ge=0, le=MAX_SALARY)] | None
    """Cận dưới; `null` khi tin chỉ nêu cận trên."""

    max: Annotated[int, Field(ge=0, le=MAX_SALARY)] | None
    """Cận trên; `null` khi tin chỉ nêu cận dưới."""

    currency: SalaryCurrency
    period: SalaryPeriod

    @model_validator(mode="after")
    def _khoang_hop_le(self) -> Self:
        if self.min is None and self.max is None:
            raise ValueError("salary phải có min hoặc max.")
        if self.min is not None and self.max is not None and self.min > self.max:
            raise ValueError("salary.min không được lớn hơn salary.max.")
        return self


class PostingContactQuote(BaseModel):
    """Một trích dẫn ngắn về kênh liên hệ (#245): dấu hiệu phải trích nguyên văn điều đã tìm thấy."""

    model_config = _CONFIG

    channel: ContactChannel
    """Kênh mà trích dẫn nói tới; phải nằm trong `contacts`."""

    quote: Annotated[str, Field(min_length=1, max_length=MAX_CONTACT_QUOTE_LEN)]
    """Nguyên văn, tối đa 120 ký tự. Chỉ hiện trên màn từ response bước một; không bao giờ vào query."""


class PostingCollected(BaseModel):
    """Tin đã thu thập khớp với tin dán (FR-32, #246): bước một đã tìm nên có link; bước hai chỉ nhận hai số."""

    model_config = _CONFIG

    site: Annotated[str, Field(min_length=1, max_length=100)]
    """Nguồn đã thu thập tin."""

    first_seen: date
    """Ngày thấy tin lần đầu."""

    repost_count: Annotated[int, Field(ge=0, le=MAX_COLLECTED_REPOSTS)]
    """Số lần đăng lại. Đi vào bước hai qua `collected_reposts` cho D4."""

    snapshots_seen: Annotated[int, Field(ge=1, le=MAX_COLLECTED_SNAPSHOTS)]
    """Số snapshot mà tin xuất hiện. Đi vào bước hai qua `collected_snapshots` cho D4."""

    url: Annotated[str, Field(min_length=9, max_length=2048, pattern=r"^https?://\S+$")]
    """Link về tin gốc. Bắt buộc khi có tin khớp (FR-32); chỉ hiện trên màn, không vào query."""


class PostingReadData(BaseModel):
    """`data` của `POST /api/v1/posting-reads`: sự kiện đóng đã trích từ chữ dán."""

    model_config = _CONFIG

    is_posting: bool
    """`false` với chữ không phải tin tuyển dụng IT hoặc quá ngắn: không có gì để khớp."""

    reason: PostingReason | None
    """Lý do khi `is_posting = false`: `not_posting` (không phải tin tuyển dụng), `too_short` (dưới 200 ký tự) hoặc `not_it` (tin
    tuyển dụng mà không thuộc lĩnh vực IT, UX-DR44: "Tin này có vẻ không thuộc lĩnh vực IT"). `null` khi là tin."""

    role: str | None
    """Mã vai trò của `config/rules.toml` (`roles`); `null` khi không phải tin."""

    branch: str | None
    """Mã nhánh của vai trò (FR-27), lấy từ `[[branches]]` của `config/classify.toml` (ví dụ `cloud` của `devops`); `null` khi tin
    không thuộc nhánh nào hoặc không phải tin."""

    level: str | None
    """Mã cấp bậc của `config/rules.toml` (`labels.level`: `intern`, `fresher`, ..., `unknown`); `null` khi không phải tin.
    Tin không ghi cấp là `unknown`."""

    skills: Annotated[list[PostingSkillMention], Field(max_length=MAX_PROFILE_SKILLS)]
    """Kỹ năng của bộ từ vựng mà tin nhắc, không trùng mã. Đây là thứ đi vào `skills=` của `posting-check`."""

    unrecognised: Annotated[list[Annotated[str, Field(min_length=1, max_length=MAX_UNRECOGNISED_LEN)]], Field(max_length=MAX_UNRECOGNISED)]
    """Cụm chữ chưa nhận diện, nguyên văn, chỉ hiện trên màn ("không tính vào mức khớp"). Không bao giờ vào query."""

    years_min: Annotated[int, Field(ge=0, le=MAX_YEARS_MIN)] | None
    """Số năm kinh nghiệm tối thiểu tin yêu cầu; `null` khi tin không ghi."""

    salary: PostingSalary | None
    """Lương dạng số; `null` khi tin không công bố số."""

    salary_non_numeric: bool
    """Tin có nói về lương nhưng không có số ("thỏa thuận", "cạnh tranh"). `false` khi có `salary`, và khi tin không nói gì về lương."""

    company_named: bool
    """Tin có nêu tên công ty."""

    duties_described: bool
    """Tin có mô tả công việc (danh sách "chi tiết thường có", #244)."""

    title_level: str | None
    """Cấp bậc mà chức danh của tin cho biết (mã của `labels.level`, không gồm `unknown`); `null` khi chức danh không nêu cấp. Đủ để
    kiểm "chức danh khớp cấp bậc" (#244) mà không phải đưa chữ của tin lên bước hai."""

    contacts: list[ContactChannel]
    """Kênh liên hệ tìm thấy, không trùng."""

    contact_quotes: Annotated[list[PostingContactQuote], Field(max_length=MAX_CONTACT_QUOTES)]
    """Trích dẫn nguyên văn về kênh liên hệ (tối đa 5, mỗi cái tối đa 120 ký tự), cho #245 ("trích điều đã tìm thấy"). Chỉ hiện trên
    màn từ response này; bước hai chỉ nhận enum `contacts`."""

    fee_mentions: Annotated[list[Annotated[str, Field(min_length=1, max_length=MAX_FEE_QUOTE_LEN)]], Field(max_length=MAX_FEE_MENTIONS)]
    """Trích dẫn ngắn về phí hoặc đặt cọc (tối đa 5, mỗi cái tối đa 120 ký tự), cho #245. Chỉ hiện trên màn."""

    collected: PostingCollected | None
    """Tin đã thu thập khớp với tin dán (FR-32); `null` là không khớp. Bước một tra, vì chỉ bước này thấy chữ."""

    model_id: Annotated[str, Field(min_length=1)]
    """Mô hình đã đọc (AD-9 truy vết)."""

    prompt_version: Annotated[str, Field(min_length=1)]
    """Phiên bản prompt của cổng đọc."""

    vocab_version: Annotated[str, Field(min_length=1)]
    """Phiên bản bộ từ vựng kỹ năng đã dùng."""

    @model_validator(mode="after")
    def _nhat_quan(self) -> Self:
        if self.is_posting != (self.reason is None):
            raise ValueError("reason phải là null khi is_posting = true và có giá trị khi is_posting = false.")
        if not self.is_posting:
            leftover = [
                name
                for name, empty in (
                    ("role", self.role is None),
                    ("branch", self.branch is None),
                    ("level", self.level is None),
                    ("skills", not self.skills),
                    ("unrecognised", not self.unrecognised),
                    ("years_min", self.years_min is None),
                    ("salary", self.salary is None),
                    ("salary_non_numeric", not self.salary_non_numeric),
                    ("company_named", not self.company_named),
                    ("duties_described", not self.duties_described),
                    ("title_level", self.title_level is None),
                    ("contacts", not self.contacts),
                    ("contact_quotes", not self.contact_quotes),
                    ("fee_mentions", not self.fee_mentions),
                    ("collected", self.collected is None),
                )
                if not empty
            ]
            if leftover:
                raise ValueError(f"Không phải tin thì các trường này phải rỗng: {', '.join(leftover)}.")
            return self
        roles, levels, title_levels = _read_vocab()
        if self.role not in roles:
            raise ValueError("role phải là mã vai trò của config/rules.toml.")
        if self.level not in levels:
            raise ValueError("level phải là mã cấp bậc của config/rules.toml.")
        if self.branch is not None and branch_codes().get(self.branch) != self.role:
            raise ValueError("branch phải là mã nhánh của chính role (config/classify.toml).")
        if self.title_level is not None and self.title_level not in title_levels:
            raise ValueError("title_level phải là mã cấp bậc của config/rules.toml, không gồm unknown.")
        if self.salary_non_numeric and self.salary is not None:
            raise ValueError("salary_non_numeric chỉ đúng khi tin không có lương dạng số.")
        codes = [s.code for s in self.skills]
        if len(set(codes)) != len(codes):
            raise ValueError("skills không được trùng mã.")
        if any(find_seed_skill(c) is None for c in codes):
            raise ValueError("skills phải là mã trong bộ từ vựng.")
        if len(set(self.contacts)) != len(self.contacts):
            raise ValueError("contacts không được trùng.")
        if not {q.channel for q in self.contact_quotes} <= set(self.contacts):
            raise ValueError("contact_quotes chỉ được trích kênh có trong contacts.")
        return self


class PostingReadRequest(BaseModel):
    """Thân của `POST /api/v1/posting-reads`. Trần cỡ ở đây và ở `posting_read` của `config/rules.toml` (AD-9); trần tốc độ là của #231."""

    model_config = ConfigDict(extra="forbid", use_attribute_docstrings=True)

    text: Annotated[str, Field(max_length=MAX_TEXT_CHARS)]
    """Chữ của tin dán, tối đa 20.000 ký tự (dài hơn là 413 `text_too_long`). Chỉ đi qua cổng đọc một lần, không lưu và không ghi log (AD-11)."""


class PostingReadResponse(BaseModel):
    """`{data}`. Không có `meta`: xem docstring của module."""

    model_config = _CONFIG

    data: PostingReadData


# ------------------------------------------------------------------------------------ bước 2: GET posting-check

GroupCode = Literal["core", "common", "specific"]
GROUP_ORDER: tuple[GroupCode, ...] = ("core", "common", "specific")
"""Thứ tự hiển thị và thứ tự trọng số của ba nhóm."""

CHECKLIST_CODES: tuple[str, ...] = ("company_named", "salary_stated", "duties_described", "title_matches_level")
"""Bốn mục của danh sách "chi tiết thường có" (#244), theo thứ tự hiển thị."""

MAX_FEES_PARAM = MAX_FEE_MENTIONS
MAX_PERCENTILE = 100


@dataclass(frozen=True, slots=True)
class PostingFacts:
    """Sự kiện đóng của bước 1 mà `posting-check` nhận (đã kiểm định dạng): chỉ mã và số. #240–#246 đọc chúng; #230 chỉ chuyển qua."""

    branch: str | None = None
    years_min: int | None = None
    salary: PostingSalary | None = None
    salary_non_numeric: bool = False
    company_named: bool | None = None
    contacts: tuple[ContactChannel, ...] = ()
    fees: int | None = None
    duties_described: bool | None = None
    title_level: str | None = None
    collected_reposts: int | None = None
    collected_snapshots: int | None = None


def match_percent(points: int, max_points: int) -> int:
    """Phần trăm làm tròn nửa lên, bằng số nguyên: 16/18 là 89, 5/8 là 63."""
    return (200 * points + max_points) // (2 * max_points)


class PostingMatchedSkill(BaseModel):
    """Một kỹ năng của tin trong mục khớp."""

    model_config = _CONFIG

    skill: SkillLabel
    """Kỹ năng, kèm tên song ngữ."""

    group: GroupCode | None
    """`core`, `common` hoặc `specific` (hiếm ở ô: nhóm `company_specific` của θ, hoặc không có dòng nào trong ô). `null` khi ô
    không đủ mẫu để chia nhóm."""

    rate: Stat
    """Tỷ lệ của kỹ năng trong ô đã dùng, `kind = skill_rate`. Kỹ năng không có dòng trong ô đủ mẫu là 0. Ô không đủ mẫu là
    `null_data`."""

    have: bool | None
    """Hồ sơ có kỹ năng này (AD-22: máy chủ so, web không tự so). `null` khi không có hồ sơ."""

    @model_validator(mode="after")
    def _nhom_theo_hien_thi(self) -> Self:
        if self.rate.kind is not MeasureKind.SKILL_RATE:
            raise ValueError(f"rate phải là skill_rate, nhận {self.rate.kind}.")
        if (self.group is None) != (self.rate.display is DisplayState.NULL_DATA):
            raise ValueError("group là null khi và chỉ khi rate là null_data.")
        return self


class PostingGroupCount(BaseModel):
    """Một dòng đếm thô theo nhóm: "có `had` trên `total`"."""

    model_config = _CONFIG

    group: GroupCode
    total: Ordinal
    """Số kỹ năng của tin thuộc nhóm."""

    had: Ordinal | None
    """Số kỹ năng trong đó hồ sơ có. `null` khi không có hồ sơ."""

    @model_validator(mode="after")
    def _khong_vuot(self) -> Self:
        if self.had is not None and self.had > self.total:
            raise ValueError("had không được lớn hơn total.")
        return self


class PostingMatchLevel(BaseModel):
    """Mức khớp theo trọng số thị trường (FR-28): `points / max_points`."""

    model_config = _CONFIG

    points: Ordinal
    """Tổng trọng số kỹ năng của tin mà hồ sơ có."""

    max_points: Ordinal
    """Tổng trọng số mọi kỹ năng đã nhận diện của tin."""

    percent: Ordinal
    """`points / max_points` làm tròn nửa lên, 0 đến 100."""

    @model_validator(mode="after")
    def _hop_le(self) -> Self:
        if self.max_points < 1 or self.points > self.max_points:
            raise ValueError("points phải nằm trong 0 đến max_points và max_points phải từ 1.")
        if self.percent != match_percent(self.points, self.max_points):
            raise ValueError("percent phải là points / max_points làm tròn nửa lên.")
        return self


class PostingMatch(BaseModel):
    """Mục khớp kỹ năng (FR-28, FR-29): có số từ #230."""

    model_config = _CONFIG

    status: Literal["ready", "not_enough_data", "no_skills"]
    """`ready`; `not_enough_data` khi ô đã dùng (kể cả sau khi quay về) dưới ngưỡng mẫu nên không chia nhóm được; `no_skills`
    khi tin không có kỹ năng nhận diện."""

    skills: list[PostingMatchedSkill]
    """Kỹ năng của tin, theo thứ tự do máy chủ quyết: core, common, specific (rồi chưa chia nhóm), mỗi nhóm tỷ lệ giảm dần rồi
    mã. Web không sắp xếp lại."""

    groups: list[PostingGroupCount]
    """Đủ ba dòng `core`, `common`, `specific` khi `status = ready`; rỗng nếu không."""

    level: PostingMatchLevel | None
    """Mức khớp. `null` khi không có hồ sơ hoặc `status` khác `ready`."""

    cv_first: list[SkillCode]
    """Kỹ năng hồ sơ có và tin nêu, theo thứ tự của `skills`: danh sách "nên đặt đầu CV" (#235). Rỗng khi không có hồ sơ."""

    config_version: Annotated[str, Field(min_length=1)]
    """Phiên bản `config/rules.toml` đã cho trọng số (AD-10)."""

    @model_validator(mode="after")
    def _nhat_quan(self) -> Self:
        codes = [s.skill.code for s in self.skills]
        if len(set(codes)) != len(codes):
            raise ValueError("skills không được trùng mã.")
        have_known = {s.have is not None for s in self.skills}
        if len(have_known) > 1:
            raise ValueError("have phải cùng null hoặc cùng có giá trị ở mọi kỹ năng.")
        rank = {g: i for i, g in enumerate(GROUP_ORDER)}
        keys = [(rank.get(s.group, len(rank)) if s.group else len(rank), -(s.rate.value or 0.0), s.skill.code) for s in self.skills]
        if keys != sorted(keys):
            raise ValueError("Sai thứ tự: core, common, specific, rồi tỷ lệ giảm dần, rồi mã.")
        if self.cv_first != [s.skill.code for s in self.skills if s.have]:
            raise ValueError("cv_first phải đúng là các kỹ năng có cờ have, theo thứ tự của skills.")
        profiled = True in have_known
        if self.status == "no_skills":
            if self.skills:
                raise ValueError("no_skills thì skills phải rỗng.")
        elif not self.skills:
            raise ValueError(f"{self.status} thì skills không được rỗng.")
        if self.status != "ready":
            if self.groups or self.level is not None or any(s.group for s in self.skills):
                raise ValueError(f"{self.status} thì groups rỗng, level là null và không kỹ năng nào có nhóm.")
            return self
        if [g.group for g in self.groups] != list(GROUP_ORDER):
            raise ValueError("ready thì groups phải đủ core, common, specific theo thứ tự.")
        for g in self.groups:
            in_group = [s for s in self.skills if s.group == g.group]
            if g.total != len(in_group) or g.had != (sum(bool(s.have) for s in in_group) if profiled else None):
                raise ValueError(f"groups[{g.group}] phải khớp các kỹ năng của nhóm và cờ have.")
        if profiled != (self.level is not None):
            raise ValueError("level có giá trị khi và chỉ khi có hồ sơ.")
        return self


MARKET_MEASURE_OF: dict[str, str] = {"years": "experience_years", "skill_count": "skill_count", "salary": "salary"}
"""Trường của `market` sang thước đo trong `meta.cells[market.cell_id].n_by_measure` (FR-30): cỡ mẫu "X/30" của mỗi trường là số tin
có đúng trường đó (có số năm, có số kỹ năng, có lương), không phải `n` của ô."""

NO_SALARY_NOTE = "salary_not_stated"
"""Mã câu trung tính khi tin không ghi lương (#125, FR-31): "Tin không công bố khoảng lương. Bạn có thể tham khảo phân vị lương của vai
trò này (nếu đủ mẫu) khi đàm phán." Không phải cảnh báo."""
SalaryNote = Literal["salary_not_stated"]

Disclaimer = Literal["signs_are_hints"]
DISCLAIMER = "signs_are_hints"
"""Mã câu cố định của FR-31, luôn có khi `warnings.status = ready`: "Dấu hiệu là gợi ý để bạn tự kiểm tra. Đa số tin bị gắn dấu hiệu vẫn
là tin thật." """


def _shown_percentile(stat: Stat | None, *, upper: float | None) -> bool:
    return (
        stat is not None
        and stat.kind is MeasureKind.PERCENTILE
        and stat.display is DisplayState.SHOWN
        and stat.value is not None
        and 0 <= stat.value <= (math.inf if upper is None else upper)
    )


def _hidden_percentile(stat: Stat | None) -> bool:
    return stat is not None and stat.kind is MeasureKind.PERCENTILE and stat.display is DisplayState.NULL_DATA


class PostingPercentile(BaseModel):
    """Vị trí của tin theo một thước (số năm, số kỹ năng) so với ô, dạng phân vị (#125, FR-30)."""

    model_config = _CONFIG

    state: Literal["compared", "not_enough_data", "not_stated"]
    """`compared`: có phân vị. `not_enough_data`: ô chưa đủ mẫu của thước này, màn ghi "chưa đủ dữ liệu (X/30 ...)" với X là
    `meta.cells[market.cell_id].n_by_measure` của thước (`experience_years`, `skill_count`). `not_stated`: tin không ghi (ví dụ không
    ghi số năm)."""

    percentile: Stat | None
    """`kind = percentile`, giá trị 0 đến 100. `null_data` khi `not_enough_data`; `null` khi `not_stated`."""

    ci_low: Stat | None
    """Cận dưới khoảng tin cậy 95% của phân vị (AD-26), `kind = percentile`. Chỉ có khi `compared` và `min_sample <= n < ci_below_n`
    (30 đến 99 tin có đúng trường đó, `config/rules.toml`); `null` khi n từ 100, và khi không `compared`."""

    ci_high: Stat | None
    """Cận trên của khoảng tin cậy; đi cặp với `ci_low`."""

    @model_validator(mode="after")
    def _theo_trang_thai(self) -> Self:
        if self.state == "compared":
            if not _shown_percentile(self.percentile, upper=MAX_PERCENTILE):
                raise ValueError("compared thì percentile phải là Stat percentile hiện số từ 0 đến 100.")
            if (self.ci_low is None) != (self.ci_high is None):
                raise ValueError("ci_low và ci_high đi cặp.")
            if self.ci_low is not None and self.ci_high is not None and self.percentile is not None:
                if not (_shown_percentile(self.ci_low, upper=MAX_PERCENTILE) and _shown_percentile(self.ci_high, upper=MAX_PERCENTILE)):
                    raise ValueError("Ranh giới khoảng tin cậy phải là Stat percentile hiện số từ 0 đến 100.")
                if not (self.ci_low.value <= self.percentile.value <= self.ci_high.value):  # type: ignore[operator]
                    raise ValueError("Khoảng tin cậy phải bao phân vị: ci_low <= percentile <= ci_high.")
        elif self.state == "not_enough_data":
            if not _hidden_percentile(self.percentile) or self.ci_low is not None or self.ci_high is not None:
                raise ValueError("not_enough_data thì percentile là null_data và không có khoảng tin cậy.")
        elif self.percentile is not None or self.ci_low is not None or self.ci_high is not None:
            raise ValueError("not_stated thì không có Stat.")
        return self


class PostingFxRate(BaseModel):
    """Tỷ giá đã dùng để quy USD sang VND (AD-10): tỷ giá cố định của snapshot đang dùng, số nguyên VND cho một USD."""

    model_config = _CONFIG

    rate: PositiveOrdinal
    """Số VND cho một USD."""

    unit: Literal["vnd_per_usd"]
    fx_version: Annotated[str, Field(min_length=1)]
    """Phiên bản tỷ giá của snapshot (truy vết)."""


class PostingSalaryConversion(BaseModel):
    """Lương của tin sau khi quy về VND một tháng gross (AD-10): USD theo tỷ giá, theo năm chia 12."""

    model_config = _CONFIG

    min_vnd_month: Ordinal | None
    """Cận dưới đã quy đổi; `null` khi tin chỉ nêu cận trên."""

    max_vnd_month: Ordinal | None
    """Cận trên đã quy đổi; `null` khi tin chỉ nêu cận dưới."""

    fx: PostingFxRate | None
    """Tỷ giá đã dùng; `null` khi tin đã ghi bằng VND (không cần đổi tiền tệ)."""

    @model_validator(mode="after")
    def _hop_le(self) -> Self:
        low, high = self.min_vnd_month, self.max_vnd_month
        if low is None and high is None:
            raise ValueError("Lương quy đổi phải có min hoặc max.")
        if low is not None and high is not None and low > high:
            raise ValueError("min_vnd_month không được lớn hơn max_vnd_month.")
        return self


class PostingSalaryComparison(BaseModel):
    """Lương tin công bố so với khoảng giữa P25 đến P75 của ô (#125, DEC-10), sau khi quy về VND một tháng (AD-10)."""

    model_config = _CONFIG

    state: Literal["compared", "not_enough_data", "not_stated", "not_numeric"]
    """`compared`: có vị trí so với khoảng giữa. `not_enough_data`: tin có lương dạng số nhưng ô chưa đủ 30 tin có lương (X/30 ở
    `meta.cells[market.cell_id].n_by_measure.salary`). `not_stated`: tin không công bố lương (sự thật trung tính, không phải cảnh
    báo; `note`). `not_numeric`: tin có nói về lương nhưng không có số ("thỏa thuận"). Lương ngoại tệ hay theo năm không còn là một
    trạng thái riêng: quy đổi lo cả hai."""

    position: Literal["below", "within", "above"] | None
    """Vị trí so với `[low, high]`; chỉ có khi `compared`."""

    low: Stat | None
    """P25 của lương trong ô, `kind = percentile`, VND một tháng. `null_data` khi `not_enough_data`; `null` khi không có lương dạng số."""

    high: Stat | None
    """P75 của lương trong ô, `kind = percentile`, VND một tháng."""

    converted: PostingSalaryConversion | None
    """Lương của tin đã quy đổi, kèm tỷ giá và đơn vị đã dùng. Có khi `compared` và `not_enough_data` (tin có lương dạng số)."""

    note: SalaryNote | None
    """`salary_not_stated` khi `not_stated`: dòng trung tính của #125; `null` ở các trạng thái khác."""

    @model_validator(mode="after")
    def _theo_trang_thai(self) -> Self:
        if self.state in ("compared", "not_enough_data"):
            if self.converted is None or self.note is not None:
                raise ValueError(f"{self.state} thì có lương quy đổi và không có câu trung tính.")
            if (self.position is not None) != (self.state == "compared"):
                raise ValueError("position có giá trị khi và chỉ khi state = compared.")
            if self.state == "compared":
                if not (_shown_percentile(self.low, upper=None) and _shown_percentile(self.high, upper=None)):
                    raise ValueError("compared thì low và high là Stat percentile hiện số.")
                if self.low.value > self.high.value:  # type: ignore[union-attr, operator]
                    raise ValueError("P25 không được lớn hơn P75.")
            elif not (_hidden_percentile(self.low) and _hidden_percentile(self.high)):
                raise ValueError("not_enough_data thì low và high là null_data.")
            return self
        if any(x is not None for x in (self.position, self.low, self.high, self.converted)):
            raise ValueError(f"{self.state} thì không có vị trí, Stat hay lương quy đổi.")
        if (self.note is not None) != (self.state == "not_stated"):
            raise ValueError("note là salary_not_stated khi và chỉ khi state = not_stated.")
        return self


class PostingMarket(BaseModel):
    """Mục so với thị trường (#125, FR-30). `not_ready` ở dữ liệu tới #240–#241: mọi trường là `null`, không phải số 0."""

    model_config = _CONFIG

    status: Literal["not_ready", "ready"]
    """`not_ready`: chưa tính (#240, #241). Khác với `not_enough_data` của từng thước, vốn là kết quả đã tính."""

    cell_id: CellId | None
    """Ô mà ba so sánh dùng. Có thể khác `data.cell_id` của mục `match` (mỗi mục quay về theo thước của mình). Cỡ mẫu "X/30" tra ở
    `meta.cells[cell_id].n_by_measure[<thước của trường>]` (`MARKET_MEASURE_OF`), không phải ô của `match`. `null` khi `not_ready`."""

    years: PostingPercentile | None
    """Số năm kinh nghiệm yêu cầu so với ô."""

    skill_count: PostingPercentile | None
    """Số kỹ năng nhận diện so với ô (FR-30: luôn hiện khi ô đủ mẫu)."""

    salary: PostingSalaryComparison | None
    """Lương công bố so với khoảng giữa của ô."""

    note: Literal["comparisons_not_verdict"] | None
    """Mã câu "đây là so sánh với thị trường, không phải phán quyết về tin" (#125 AC5, #242). Có khi `ready`, `null` khi `not_ready`.
    Chữ do web dựng từ mã."""

    @model_validator(mode="after")
    def _theo_trang_thai(self) -> Self:
        parts = (self.years, self.skill_count, self.salary)
        if self.status == "not_ready":
            if self.cell_id is not None or self.note is not None or any(x is not None for x in parts):
                raise ValueError("not_ready thì cell_id, note và cả ba mục là null.")
            return self
        if self.note is None:
            raise ValueError("ready thì có note (câu so sánh không phải phán quyết).")
        if self.cell_id is None or any(x is None for x in parts):
            raise ValueError("ready thì có cell_id và đủ years, skill_count, salary.")
        if self.skill_count is not None and self.skill_count.state == "not_stated":
            raise ValueError("skill_count luôn có số (FR-30): không có not_stated.")
        wrong = sorted({s.cell_id for s in _market_stats(self)} - {self.cell_id})
        if wrong:
            raise ValueError(f"Mọi Stat của market phải thuộc ô {self.cell_id!r}, có ô lạ: {', '.join(wrong)}.")
        return self


def _market_stats(market: PostingMarket) -> list[Stat]:
    stats: list[Stat | None] = []
    for part in (market.years, market.skill_count):
        if part is not None:
            stats += [part.percentile, part.ci_low, part.ci_high]
    if market.salary is not None:
        stats += [market.salary.low, market.salary.high]
    return [s for s in stats if s is not None]


class PostingChecklistItem(BaseModel):
    """Một mục "chi tiết thường có" của tin (#244)."""

    model_config = _CONFIG

    code: Literal["company_named", "salary_stated", "duties_described", "title_matches_level"]
    present: bool | None
    """`null` là không biết (ví dụ `title_matches_level` khi tin không có `title_level` hoặc cấp là `unknown`), khác với `false`."""


SignCode = Literal[
    "d1_wide_skills",
    "d2_specific_heavy",
    "d3_high_req_low_pay",
    "d4_reposted",
    "d5_unusual_contact",
    "d6_fee_first",
    "d7_no_company",
]
SIGN_CODES: tuple[str, ...] = (
    "d1_wide_skills",
    "d2_specific_heavy",
    "d3_high_req_low_pay",
    "d4_reposted",
    "d5_unusual_contact",
    "d6_fee_first",
    "d7_no_company",
)
"""Bảy dấu hiệu D1 đến D7 của FR-31, theo thứ tự. Khi `warnings.status = ready` luôn có đủ bảy, mỗi cái một trạng thái."""

ActionCode = Literal[
    "ask_daily_stack",
    "check_company_stack",
    "compare_pay_before_applying",
    "check_original_posting",
    "verify_company_channel",
    "no_payment_before_verifying",
    "look_up_company",
]
SIGN_ACTION: dict[str, str] = dict(
    zip(
        SIGN_CODES,
        (
            "ask_daily_stack",  # D1: hỏi rõ 2-3 công nghệ nhóm thực sự dùng hằng ngày (FR-31)
            "check_company_stack",  # D2
            "compare_pay_before_applying",  # D3
            "check_original_posting",  # D4
            "verify_company_channel",  # D5
            "no_payment_before_verifying",  # D6
            "look_up_company",  # D7
        ),
        strict=True,
    )
)
"""Mã câu gợi ý hành động của từng dấu hiệu (`action`). Câu chữ ở web; mã là một-một với dấu hiệu."""

SIGN_SOURCE_FIELD: dict[str, str | None] = {code: None for code in SIGN_CODES} | {
    "d5_unusual_contact": "contacts",
    "d6_fee_first": "fee_mentions",
}
"""Trường của `PostingReadData` mà màn trích nguyên văn cho dấu hiệu; `null` khi dấu hiệu không có trích dẫn."""

SignStatus = Literal["triggered", "not_triggered", "not_evaluable"]
NotEvaluableReason = Literal["not_in_data", "not_enough_data", "no_numeric_salary"]
NOT_EVALUABLE_REASONS: dict[str, frozenset[str]] = {
    "d1_wide_skills": frozenset({"not_enough_data"}),  # ô chưa đủ mẫu để có P90
    "d2_specific_heavy": frozenset({"not_enough_data"}),  # nhóm kỹ năng chỉ có khi ô khớp đủ n ≥ 30
    "d3_high_req_low_pay": frozenset({"not_enough_data", "no_numeric_salary"}),  # ô chưa đủ 30 tin có lương, hoặc tin không có lương số
    "d4_reposted": frozenset({"not_in_data"}),  # "không đánh giá được: tin chưa có trong dữ liệu"
}
"""Dấu hiệu nào có thể `not_evaluable` và vì lý do gì. D5, D6, D7 luôn đánh giá được từ chính tin; D2 chỉ không đánh giá được khi ô khớp chưa đủ mẫu để có nhóm kỹ năng."""


class WideSkillsFact(BaseModel):
    """D1 (yêu cầu kỹ năng dàn trải): số kỹ năng đã nhận diện của tin so với P90 của ô."""

    model_config = _CONFIG

    kind: Literal["d1_wide_skills"]
    skill_count: Ordinal
    """Số kỹ năng đã nhận diện của tin."""

    p90: Stat
    """P90 của số kỹ năng trong ô, `kind = percentile`."""

    @model_validator(mode="after")
    def _p90_hien_so(self) -> Self:
        if not _shown_percentile(self.p90, upper=None):
            raise ValueError("p90 phải là Stat percentile hiện số.")
        return self


class SpecificHeavyFact(BaseModel):
    """D2 (tỷ lệ kỹ năng riêng cao): số kỹ năng đã nhận diện và số trong đó thuộc nhóm riêng của công ty (không tính chưa nhận diện)."""

    model_config = _CONFIG

    kind: Literal["d2_specific_heavy"]
    recognised_count: Ordinal
    specific_count: Ordinal

    @model_validator(mode="after")
    def _khong_vuot(self) -> Self:
        if self.specific_count > self.recognised_count:
            raise ValueError("specific_count không được lớn hơn recognised_count.")
        return self


class HighReqLowPayFact(BaseModel):
    """D3 (yêu cầu cao, lương thấp): số kỹ năng so với P75 và lương trần (đã quy VND một tháng) so với P25 của lương trong ô."""

    model_config = _CONFIG

    kind: Literal["d3_high_req_low_pay"]
    skill_count: Ordinal
    p75_skill_count: Stat
    """P75 của số kỹ năng trong ô, `kind = percentile`."""

    salary_ceiling_vnd_month: Ordinal
    """Lương trần của tin, VND một tháng gross."""

    p25_salary: Stat
    """P25 của lương trong ô, VND một tháng, `kind = percentile`."""

    @model_validator(mode="after")
    def _phan_vi_hien_so(self) -> Self:
        if not (_shown_percentile(self.p75_skill_count, upper=None) and _shown_percentile(self.p25_salary, upper=None)):
            raise ValueError("p75_skill_count và p25_salary phải là Stat percentile hiện số.")
        return self


class RepostedFact(BaseModel):
    """D4 (tin đăng lại nhiều lần): vòng đời của tin thu thập khớp."""

    model_config = _CONFIG

    kind: Literal["d4_reposted"]
    reposts: Ordinal
    snapshots_seen: Ordinal


class UnusualContactFact(BaseModel):
    """D5 (kênh liên hệ bất thường): các kênh đã tìm thấy, chỉ có kênh cá nhân. Màn trích `contact_quotes` của bước một theo kênh."""

    model_config = _CONFIG

    kind: Literal["d5_unusual_contact"]
    channels: Annotated[list[ContactChannel], Field(min_length=1)]

    @model_validator(mode="after")
    def _chi_kenh_ca_nhan(self) -> Self:
        if len(set(self.channels)) != len(self.channels) or not set(self.channels) <= PERSONAL_CHANNELS:
            raise ValueError("channels không trùng và chỉ gồm zalo, telegram, personal_email.")
        return self


class FeeFirstFact(BaseModel):
    """D6 (đòi tiền trước): số trích dẫn về phí hoặc đặt cọc. Màn trích `fee_mentions[0 : quote_count]` của bước một."""

    model_config = _CONFIG

    kind: Literal["d6_fee_first"]
    quote_count: Annotated[int, OrdinalRef(), Field(ge=1, le=MAX_FEE_MENTIONS)]


class NoCompanyFact(BaseModel):
    """D7 (không rõ công ty): tin không nêu tên công ty. Không có số."""

    model_config = _CONFIG

    kind: Literal["d7_no_company"]


SignFact = Annotated[
    WideSkillsFact | SpecificHeavyFact | HighReqLowPayFact | RepostedFact | UnusualContactFact | FeeFirstFact | NoCompanyFact,
    Field(discriminator="kind"),
]


class PostingWarningSign(BaseModel):
    """Một dấu hiệu cần tự kiểm tra (FR-31, #245). Máy chủ không nhận chữ của tin: màn trích nguyên văn từ kết quả bước một."""

    model_config = _CONFIG

    code: SignCode
    status: SignStatus
    """`triggered`: kích hoạt, kèm `fact` và `action`. `not_triggered`: đánh giá được và không kích hoạt. `not_evaluable`: không có
    đủ dữ liệu để đánh giá (`reason`), không phải "không kích hoạt"."""

    reason: NotEvaluableReason | None
    """Chỉ có khi `not_evaluable`: `not_in_data` (D4: tin chưa có trong dữ liệu), `not_enough_data` (D1, D3: ô chưa đủ mẫu),
    `no_numeric_salary` (D3: tin không có lương dạng số)."""

    fact: SignFact | None
    """Dữ kiện đã kích hoạt dấu hiệu, kiểu theo `code`; chỉ có khi `triggered`."""

    action: ActionCode | None
    """Mã câu gợi ý hành động (`SIGN_ACTION`); chỉ có khi `triggered`."""

    source_field: Literal["fee_mentions", "contacts"] | None
    """Trường của `PostingReadData` mà màn trích nguyên văn: D5 `contacts`, D6 `fee_mentions`; `null` ở mọi trường hợp khác."""

    @model_validator(mode="after")
    def _theo_trang_thai(self) -> Self:
        if self.status == "triggered":
            if self.fact is None or self.fact.kind != self.code:
                raise ValueError("triggered thì fact có kiểu đúng mã dấu hiệu.")
            if self.action != SIGN_ACTION[self.code] or self.reason is not None:
                raise ValueError("triggered thì action là gợi ý của dấu hiệu và không có reason.")
            if self.source_field != SIGN_SOURCE_FIELD[self.code]:
                raise ValueError(f"{self.code} có source_field là {SIGN_SOURCE_FIELD[self.code]!r}.")
            return self
        if self.fact is not None or self.action is not None or self.source_field is not None:
            raise ValueError(f"{self.status} thì không có fact, action và source_field.")
        if self.status == "not_triggered":
            if self.reason is not None:
                raise ValueError("not_triggered thì không có reason.")
        elif self.reason not in NOT_EVALUABLE_REASONS.get(self.code, frozenset()):
            raise ValueError(f"{self.code} không thể not_evaluable với reason {self.reason!r}.")
        return self


class PostingCollectedCounts(BaseModel):
    """Vòng đời của tin thu thập khớp (FR-32), phần số mà bước hai nhận. Site, ngày thấy đầu và link ở `PostingReadData.collected`."""

    model_config = _CONFIG

    repost_count: Ordinal
    """Số lần đăng lại."""

    snapshots_seen: Ordinal
    """Số snapshot mà tin xuất hiện."""


class PostingWarnings(BaseModel):
    """Mục dấu hiệu cần kiểm (#126, FR-31). `not_ready` ở dữ liệu tới #244–#246: rỗng, không phải "không có dấu hiệu"."""

    model_config = _CONFIG

    status: Literal["not_ready", "ready"]

    checklist: list[PostingChecklistItem]
    """Đủ bốn mục của `CHECKLIST_CODES` theo thứ tự khi `ready`; rỗng khi `not_ready`."""

    signs: list[PostingWarningSign]
    """Khi `ready`: đủ bảy dấu hiệu `SIGN_CODES` theo thứ tự, mỗi cái một trạng thái. Rỗng khi `not_ready`."""

    collected_match: PostingCollectedCounts | None
    """Vòng đời của tin thu thập khớp (hai số mà bước hai nhận); `null` là không khớp, và D4 là `not_evaluable`. Site, ngày thấy đầu
    và link của tin khớp ở `PostingReadData.collected` (bước một)."""

    salary_note: SalaryNote | None
    """`salary_not_stated` khi tin không ghi lương: dòng trung tính của FR-31, không phải dấu hiệu. `null` khi tin có lương hoặc `not_ready`."""

    disclaimer: Disclaimer | None
    """`signs_are_hints`: mã câu cố định FR-31 đặt ngay dưới các dấu hiệu. Có khi và chỉ khi `ready`."""

    @model_validator(mode="after")
    def _theo_trang_thai(self) -> Self:
        if self.status == "not_ready":
            if self.checklist or self.signs or any(x is not None for x in (self.collected_match, self.salary_note, self.disclaimer)):
                raise ValueError("not_ready thì checklist, signs rỗng và collected_match, salary_note, disclaimer là null.")
            return self
        if [c.code for c in self.checklist] != list(CHECKLIST_CODES):
            raise ValueError("ready thì checklist phải đủ bốn mục theo thứ tự.")
        if [s.code for s in self.signs] != list(SIGN_CODES):
            raise ValueError("ready thì signs phải đủ bảy dấu hiệu D1 đến D7, theo thứ tự, không trùng.")
        if self.disclaimer != DISCLAIMER:
            raise ValueError("ready thì disclaimer là signs_are_hints.")
        d4 = self.signs[3]
        if self.collected_match is None:
            if d4.status != "not_evaluable":
                raise ValueError("Không có tin thu thập khớp thì D4 là not_evaluable.")
        elif d4.status == "not_evaluable":
            raise ValueError("Có tin thu thập khớp thì D4 đánh giá được.")
        elif isinstance(d4.fact, RepostedFact) and (
            (d4.fact.reposts, d4.fact.snapshots_seen) != (self.collected_match.repost_count, self.collected_match.snapshots_seen)
        ):
            raise ValueError("fact của D4 phải đúng với collected_match.")
        return self


class PostingCheckData(BaseModel):
    """`data` của `GET /api/v1/posting-check`."""

    model_config = _CONFIG

    role: str
    """Vai trò đã chọn (mã)."""

    branch: str | None
    """Nhánh của vai trò (mã, FR-27) mà người gọi gửi lên; lặp lại nguyên mã. `null` khi không gửi."""

    level: str
    """Cấp bậc đã chọn (mã)."""

    cell_id: CellId
    """Ô đã dùng cho `match`, sau khi quay về như `skill-rates`; `meta.cells[cell_id].fallback_label` giải thích. Mục `market` có
    `market.cell_id` riêng."""

    has_profile: bool
    """`false` khi `have` rỗng: không có cờ `have`, mức khớp và đếm theo nhóm; nhóm và tỷ lệ vẫn có."""

    match: PostingMatch
    market: PostingMarket
    warnings: PostingWarnings

    @model_validator(mode="after")
    def _nhat_quan(self) -> Self:
        lech = sorted({s.rate.cell_id for s in self.match.skills} - {self.cell_id})
        if lech:
            raise ValueError(f"Mọi rate phải thuộc ô {self.cell_id!r}, có ô lạ: {', '.join(lech)}.")
        flags = {s.have is not None for s in self.match.skills}
        if flags and flags != {self.has_profile}:
            raise ValueError("has_profile phải khớp cờ have của các kỹ năng.")
        if not self.has_profile and (self.match.level is not None or self.match.cv_first):
            raise ValueError("Không có hồ sơ thì level là null và cv_first rỗng.")
        return self

    def check_against_meta(self, meta: Meta) -> list[str]:
        """Luật cần cả `data` lẫn `meta` (hợp đồng `Envelope`): trạng thái và khoảng tin cậy của `market` khớp cỡ mẫu từng thước."""
        market = self.market
        if market.status != "ready" or market.cell_id is None or market.cell_id not in meta.cells:
            return []  # ô lạ đã bị `Envelope` báo
        cell = meta.cells[market.cell_id]
        min_sample, ci_below_n = meta.thresholds.min_sample, _rules().posting_ci_below_n
        errors: list[str] = []
        for name, measure in MARKET_MEASURE_OF.items():
            part = getattr(market, name)
            if part.state in ("not_stated", "not_numeric"):
                continue
            n = cell.n_by_measure.get(measure)
            if n is None:
                errors.append(f"meta.cells[{market.cell_id!r}].n_by_measure thiếu thước {measure!r}")
                continue
            if (part.state == "compared") != (n >= min_sample):
                errors.append(f"data.market.{name}.state = {part.state}, nhưng {measure} có n = {n} (ngưỡng {min_sample})")
            if name != "salary" and (part.ci_low is not None) != (part.state == "compared" and n < ci_below_n):
                errors.append(f"data.market.{name} có khoảng tin cậy khi và chỉ khi {min_sample} <= n < {ci_below_n}, nhận n = {n}")
        return errors
