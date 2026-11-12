"""Tám chữ ký phép dùng chung (AD-2, SPEC-REG-03).

Chưa có thân hàm. Story sau cài đúng một class trong file ghi ở REGISTRY.md.
Module chỉ import thư viện chuẩn, cùng kiểu display_policy.py.
"""

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

type OneOrMany[T] = T | list[T] | tuple[T, ...]


def as_batch[T](value: OneOrMany[T]) -> tuple[T, ...] | None:
    """Tách lô khỏi một đối tượng.

    `list` và `tuple` là lô, kể cả lô rỗng. Mọi thứ khác, gồm `str`, là một đối tượng.
    Không phải một trong tám phép.
    """
    if isinstance(value, list | tuple):
        return tuple(value)
    return None


@dataclass(frozen=True, slots=True)
class Mention:
    """Lượt nhắc nguyên văn, neo bằng vị trí trong đoạn đã trích."""

    text: str
    start: int
    end: int


@dataclass(frozen=True, slots=True)
class MappedMention:
    """Mã kỹ năng của một lượt nhắc. `None` nghĩa là chưa khớp, không đoán mã."""

    text: str
    skill_id: str | None


@dataclass(frozen=True, slots=True)
class CellKey:
    """Khóa ô: snapshot, vai trò, nhánh, cấp bậc, phạm vi. Nhánh và cấp có thể trống."""

    snapshot_id: str
    role: str
    branch: str | None
    seniority: str | None
    scope: str


@dataclass(frozen=True, slots=True)
class CellQuery:
    """Ô được yêu cầu. Không có cờ cho phép đổi phạm vi."""

    requested: CellKey
    min_sample: int


@dataclass(frozen=True, slots=True)
class CellChoice:
    """Ô đã chọn, cỡ mẫu và nhãn. Ba thứ này không tách rời."""

    cell: CellKey
    n: int
    label: str


@dataclass(frozen=True, slots=True)
class PopulationRequest:
    """Đếm cụm của một ô. Cửa sổ ngày là tham số, không viết cứng."""

    cell: CellKey
    window_days: int


@dataclass(frozen=True, slots=True)
class SkillRate:
    """Tỷ lệ một kỹ năng trong ô. Tỷ lệ 0 vẫn là một phần tử."""

    skill_id: str
    rate: float


@dataclass(frozen=True, slots=True)
class SkillGroupRequest:
    """θ truyền vào từng lần gọi."""

    rates: tuple[SkillRate, ...]
    theta_core: float
    theta_common: float


class SkillBand(StrEnum):
    """Nhóm kỹ năng sau khi so với θ."""

    CORE = "core"
    COMMON = "common"
    RARE = "rare"


@dataclass(frozen=True, slots=True)
class SkillGroup:
    """Một kỹ năng và nhóm của nó."""

    skill_id: str
    band: SkillBand


@dataclass(frozen=True, slots=True)
class PercentileRequest:
    """Seed do người gọi đưa. Hàm không đọc đồng hồ."""

    values: tuple[float, ...]
    percentile: float
    seed: str
    draws: int


@dataclass(frozen=True, slots=True)
class PercentileResult:
    """Giá trị phân vị và hai đầu khoảng. `None` khi người gọi chưa muốn một số."""

    value: float | None
    low: float | None
    high: float | None


@dataclass(frozen=True, slots=True)
class PostingFacts:
    """Đầu vào phân loại. Được phép mang văn bản JD đầy đủ (REGISTRY.md); văn bản đó không được ghi xuống bảng hay log."""

    title: str
    source: str
    source_category: str | None
    seniority_text: str | None
    location_text: str | None
    text: str | None = None
    """Mục yêu cầu và nhiệm vụ của JD, đã bỏ dấu (#283). Chỉ trong bộ nhớ."""
    skills: tuple[tuple[str, int], ...] = ()
    """Mã kỹ năng → số lượt nhắc, đã ánh xạ bằng phép 1."""
    years_min: float | None = None
    """Số năm tối thiểu đã giải (nguồn → bước trích → luật)."""


@dataclass(frozen=True, slots=True)
class Classification:
    """Một tin, một vai trò, một cấp bậc, một thành phố. Nhánh trống cho tới Story 1.9."""

    role: str
    branch: str | None
    seniority: str
    city: str


class MatchScope(StrEnum):
    """Phạm vi so khớp. Một phép cho cả hai, không tách hai hàm."""

    IN_SOURCE = "in_source"
    CROSS_SOURCE = "cross_source"


@dataclass(frozen=True, slots=True)
class PostingPair:
    """Một cặp là một đối tượng. Danh sách cặp là một lô."""

    left_id: str
    right_id: str
    scope: MatchScope


@dataclass(frozen=True, slots=True)
class MatchDecision:
    """Khớp hay không. Phép không xóa tin."""

    left_id: str
    right_id: str
    matched: bool


@dataclass(frozen=True, slots=True)
class GraphEdge:
    """Cạnh học trước → học sau."""

    before: str
    after: str


@dataclass(frozen=True, slots=True)
class PathSkill:
    """Nút trên đồ thị lộ trình, kèm chặng, nhóm và tỷ lệ để phá hòa."""

    skill_id: str
    stage: int
    band: SkillBand
    rate: float


@dataclass(frozen=True, slots=True)
class PathRequest:
    """Khoảng trống, đồ thị và nút. Thứ tự trả về không phụ thuộc thứ tự các tuple này."""

    gaps: tuple[str, ...]
    edges: tuple[GraphEdge, ...]
    skills: tuple[PathSkill, ...]


class MapMentions(Protocol):
    """Phép 1. Lượt nhắc thành mã kỹ năng."""

    def map_mentions(self, mentions: OneOrMany[Mention]) -> OneOrMany[MappedMention]:
        """Một lượt nhắc hoặc một lô. Chưa khớp thì `skill_id` là `None`."""
        ...


class SelectCell(Protocol):
    """Phép 2. Chọn ô và nhãn quay về trong cùng phạm vi."""

    def select_cell(self, queries: OneOrMany[CellQuery]) -> OneOrMany[CellChoice]:
        """Ô thành phố không được trả về dưới dạng ô toàn quốc."""
        ...


class Population(Protocol):
    """Phép 3. Dân số ô, đếm theo cụm."""

    def population(self, requests: OneOrMany[PopulationRequest]) -> OneOrMany[int]:
        """Một yêu cầu trả một số nguyên. Một lô trả một tuple số nguyên."""
        ...


class GroupSkills(Protocol):
    """Phép 4. Nhóm kỹ năng theo θ của lần gọi."""

    def group_skills(
        self, requests: OneOrMany[SkillGroupRequest]
    ) -> OneOrMany[tuple[SkillGroup, ...]]:
        """Mỗi yêu cầu trả một tuple nhóm, gồm cả kỹ năng tỷ lệ 0 nếu người gọi đưa vào."""
        ...


class Percentiles(Protocol):
    """Phép 5. Phân vị, mốc và khoảng tin cậy."""

    def percentiles(self, requests: OneOrMany[PercentileRequest]) -> OneOrMany[PercentileResult]:
        """Cùng seed và cùng đầu vào thì story cài thân hàm phải ra cùng số."""
        ...


class Classify(Protocol):
    """Phép 6. Vai trò, nhánh, cấp bậc, thành phố."""

    def classify(self, postings: OneOrMany[PostingFacts]) -> OneOrMany[Classification]:
        """Hàm thuần. Không gọi mô hình. Cùng đầu vào thì cùng nhãn."""
        ...


class MatchPostings(Protocol):
    """Phép 7. So khớp một cặp tin."""

    def match_postings(self, pairs: OneOrMany[PostingPair]) -> OneOrMany[MatchDecision]:
        """Phạm vi nằm trên cặp. Không có hàm riêng cho trong nguồn và chéo nguồn."""
        ...


class OrderPath(Protocol):
    """Phép 8. Xếp thứ tự lộ trình bốn tầng."""

    def order_path(self, requests: OneOrMany[PathRequest]) -> OneOrMany[tuple[str, ...]]:
        """Một yêu cầu trả một tuple mã kỹ năng. Không sắp ở `web/`."""
        ...
