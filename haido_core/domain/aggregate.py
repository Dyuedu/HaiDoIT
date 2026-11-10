"""Tỷ trọng thành phố của một snapshot (#93, thao tác 3).

Hàm thuần: nhận các tin đã phân loại (mã snake_case) và trả mọi ô cùng mọi tỷ trọng của S. Số
tin của từng ô lấy từ phép 3 (`ClusterPopulation`), nên cửa sổ ngày và quy tắc đếm cụm chỉ có
một chỗ. Thứ tự đầu ra do tham số quyết, không phụ thuộc thứ tự tin đầu vào.

Mỗi vai trò, cộng `all`, có một hàng cho từng thành phố, kể cả khi n = 0. Tổng các tỷ trọng
của một vai trò luôn bằng 1; khi vai trò không có tin nào thì toàn bộ rơi vào `unknown`.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date

from haido_core.domain.population import (
    ALL,
    NATIONWIDE,
    ClusterPopulation,
    CountedPosting,
)
from haido_core.domain.registry import CellKey, PopulationRequest

UNKNOWN_CITY = "unknown"
"""Mã thành phố của tin không xác định được thành phố; nhận phần dư khi vai trò không có tin."""


@dataclass(frozen=True, slots=True)
class CellRow:
    """Một ô: số cụm và số cụm theo cấp bậc (chỉ cấp có tin; các cấp cộng lại bằng `n`)."""

    role: str
    scope: str
    n: int
    seniority_mix: dict[str, int]


@dataclass(frozen=True, slots=True)
class ShareRow:
    role: str
    city: str
    share: float


@dataclass(frozen=True, slots=True)
class CityShareAggregate:
    cells: tuple[CellRow, ...]
    shares: tuple[ShareRow, ...]


def aggregate_city_shares(
    snapshot_id: date,
    postings: Sequence[CountedPosting],
    *,
    roles: Sequence[str],
    cities: Sequence[str],
    levels: Sequence[str],
    window_days: int,
) -> CityShareAggregate:
    """Ô và tỷ trọng thành phố của S cho `all` cùng từng vai trò trong `roles`.

    Raises:
        ValueError: tin có thành phố hoặc cấp bậc ngoài danh sách, vì khi đó các số không cộng
            lại bằng tổng; mã lạ là lỗi của bước gọi, không được đoán.
    """
    unknown_city = sorted({p.city for p in postings} - set(cities))
    if unknown_city:
        raise ValueError(f"Mã thành phố ngoài danh sách: {', '.join(unknown_city)}.")
    unknown_level = sorted({p.seniority for p in postings} - set(levels))
    if unknown_level:
        raise ValueError(f"Mã cấp bậc ngoài danh sách: {', '.join(unknown_level)}.")

    population = ClusterPopulation(postings)
    day = snapshot_id.isoformat()
    scopes = (*cities, NATIONWIDE)
    cells: list[CellRow] = []
    shares: list[ShareRow] = []
    for role in (ALL, *roles):

        def ask(scope: str, level: str | None = None, role: str = role) -> int:
            key = CellKey(day, role, None, level, scope)
            count = population.population(PopulationRequest(cell=key, window_days=window_days))
            assert isinstance(count, int)
            return count

        n_by_scope = {scope: ask(scope) for scope in scopes}
        if sum(n_by_scope[c] for c in cities) != n_by_scope[NATIONWIDE]:
            raise ValueError(f"Các thành phố của vai trò {role} không cộng lại bằng toàn quốc.")
        for scope in scopes:
            mix = {level: count for level in levels if (count := ask(scope, level)) > 0}
            cells.append(CellRow(role, scope, n_by_scope[scope], mix))
        total = n_by_scope[NATIONWIDE]
        for city in cities:
            if total:
                share = n_by_scope[city] / total
            else:
                share = 1.0 if city == UNKNOWN_CITY else 0.0
            shares.append(ShareRow(role, city, share))
    return CityShareAggregate(tuple(cells), tuple(shares))
