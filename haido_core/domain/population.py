"""Phép 3: dân số của ô, đếm theo cụm (#93, AD-2).

Một ô là `(snapshot, vai trò, nhánh, cấp bậc, phạm vi)`. Dân số là số cụm có tin rơi vào ô, trong
`window_days` ngày kết thúc ở S, gồm cả S: `S - (window_days - 1) <= last_seen <= S`. Với 60 thì
đúng 60 ngày, không phải 61 như cột `in_window` của vòng đời.

Đối tượng nhận tin lúc dựng. `cluster_id` là cụm đã gộp (#100); hai tin cùng `cluster_id` chỉ đếm một lần.

Giá trị đặc biệt của khóa ô: vai trò `all` là mọi tin IT, phạm vi `vn` là toàn quốc, nhánh và
cấp bậc `None` hoặc `all` là không lọc. Phạm vi thành phố không bao giờ trả số toàn quốc.

Module chỉ import thư viện chuẩn và registry.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, timedelta

from haido_core.domain.registry import CellKey, OneOrMany, PopulationRequest, as_batch

ALL = "all"
"""Vai trò "mọi vai trò", cũng là nhánh và cấp bậc "không lọc"."""

NATIONWIDE = "vn"
"""Phạm vi toàn quốc. Mọi giá trị khác của phạm vi là mã thành phố."""


@dataclass(frozen=True, slots=True)
class CountedPosting:
    """Một tin đã phân loại, đã nằm trong dữ liệu IT. Nhãn là mã snake_case, không phải nhãn tiếng Việt."""

    cluster_id: str
    last_seen: date
    role: str
    city: str
    seniority: str
    years_min: float | None = None
    """Số năm kinh nghiệm tối thiểu tin yêu cầu (#280); `None` là tin không ghi. Phép đếm không đọc trường này:
    bước tổng hợp lọc tin theo mốc số năm trước khi dựng `ClusterPopulation`."""


def window_start(day: date, window_days: int) -> date:
    """Ngày đầu của cửa sổ đếm: cửa sổ gồm `window_days` ngày kết thúc ở `day`, gồm cả `day`."""
    return day - timedelta(days=window_days - 1)


def _matches(posting: CountedPosting, cell: CellKey) -> bool:
    return (
        (cell.role == ALL or posting.role == cell.role)
        and (cell.scope == NATIONWIDE or posting.city == cell.scope)
        and (cell.seniority in (None, ALL) or posting.seniority == cell.seniority)
    )


class ClusterPopulation:
    """Thân hàm duy nhất của phép 3."""

    def __init__(self, postings: Sequence[CountedPosting]) -> None:
        self._postings = tuple(postings)
        self._in_window: dict[tuple[date, int], tuple[CountedPosting, ...]] = {}

    def population(self, requests: OneOrMany[PopulationRequest]) -> OneOrMany[int]:
        batch = as_batch(requests)
        if batch is None:
            return self._one(requests)
        return tuple(self._one(item) for item in batch)

    def _one(self, request: PopulationRequest) -> int:
        cell = request.cell
        if request.window_days < 1:
            raise ValueError(f"window_days phải từ 1 trở lên, nhận {request.window_days}.")
        if cell.branch not in (None, ALL):
            raise ValueError(f"Chưa hỗ trợ nhánh {cell.branch!r}; nhánh là phạm vi của story sau.")
        window = self._window(date.fromisoformat(cell.snapshot_id), request.window_days)
        return len({p.cluster_id for p in window if _matches(p, cell)})

    def _window(self, day: date, window_days: int) -> tuple[CountedPosting, ...]:
        key = (day, window_days)
        if key not in self._in_window:
            first = window_start(day, window_days)
            self._in_window[key] = tuple(p for p in self._postings if first <= p.last_seen <= day)
        return self._in_window[key]
