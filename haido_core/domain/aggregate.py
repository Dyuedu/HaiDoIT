"""Tỷ trọng thành phố của một snapshot (#93, thao tác 3).

Hàm thuần: nhận các tin đã phân loại (mã snake_case) và trả mọi ô cùng mọi tỷ trọng của S. Số
tin của từng ô lấy từ phép 3 (`ClusterPopulation`), nên cửa sổ ngày và quy tắc đếm cụm chỉ có
một chỗ. Thứ tự đầu ra do tham số quyết, không phụ thuộc thứ tự tin đầu vào.

Mỗi vai trò, cộng `all`, có một hàng cho từng thành phố, kể cả khi n = 0. Tổng các tỷ trọng
của một vai trò luôn bằng 1; khi vai trò không có tin nào thì toàn bộ rơi vào `unknown`.

Cấp bậc lọc được (#163, #134): ngoài cấp `all`, mỗi mã trong `level_options` có bộ ô và tỷ trọng riêng,
cùng quy tắc. Mã đó là một cấp thô hoặc một nhóm (`level_groups`, ví dụ `entry`). Một cụm chỉ có một cấp thô và các
nhóm rời nhau, nên n của nhóm là tổng n của các cấp thành viên; hàm không hỏi phép dân số thêm cho nhóm.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date

from haido_core.domain.population import (
    ALL,
    NATIONWIDE,
    ClusterPopulation,
    CountedPosting,
    window_start,
)
from haido_core.domain.registry import CellKey, PopulationRequest

UNKNOWN_CITY = "unknown"
"""Mã thành phố của tin không xác định được thành phố; nhận phần dư khi vai trò không có tin."""

ALL_LEVELS = "all"
"""Mã cấp lọc "mọi cấp bậc". Luôn có, đứng trước các mã của `level_options`."""


@dataclass(frozen=True, slots=True)
class CellRow:
    """Một ô: số cụm và số cụm theo cấp bậc (chỉ cấp có tin; các cấp cộng lại bằng `n`).

    `seniority` là cấp lọc của ô: `all`, một nhóm hoặc một cấp thô. `seniority_mix` chỉ gồm các cấp thô thuộc ô.
    """

    role: str
    scope: str
    n: int
    seniority_mix: dict[str, int]
    seniority: str = ALL_LEVELS


@dataclass(frozen=True, slots=True)
class ShareRow:
    role: str
    city: str
    share: float
    seniority: str = ALL_LEVELS


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
    level_options: Sequence[str] = (),
    level_groups: Mapping[str, Sequence[str]] | None = None,
) -> CityShareAggregate:
    """Ô và tỷ trọng thành phố của S cho `all` cùng từng vai trò trong `roles`, theo `all` và từng cấp lọc.

    `level_options` là các cấp lọc ngoài `all` (một cấp thô trong `levels` hoặc tên một nhóm trong `level_groups`);
    để trống thì chỉ có cấp `all`.

    Raises:
        ValueError: nhóm có thành viên trùng, tin có thành phố hoặc cấp bậc ngoài danh sách, hoặc cấp lọc không biết, vì khi đó các số không
            cộng lại bằng tổng; mã lạ là lỗi của bước gọi, không được đoán.
    """
    groups = {name: tuple(members) for name, members in (level_groups or {}).items()}
    for name, members in groups.items():
        if len(set(members)) != len(members):
            raise ValueError(f"Nhóm cấp bậc {name} có thành viên trùng, sẽ đếm đôi.")
    unknown_city = sorted({p.city for p in postings} - set(cities))
    if unknown_city:
        raise ValueError(f"Mã thành phố ngoài danh sách: {', '.join(unknown_city)}.")
    unknown_level = sorted({p.seniority for p in postings} - set(levels))
    if unknown_level:
        raise ValueError(f"Mã cấp bậc ngoài danh sách: {', '.join(unknown_level)}.")
    stray_members = sorted({m for members in groups.values() for m in members} - set(levels))
    stray_options = sorted(o for o in level_options if o != ALL_LEVELS and o not in groups and o not in levels)
    if stray_members or stray_options or ALL_LEVELS in level_options:
        bad = [*stray_members, *stray_options, *([ALL_LEVELS] if ALL_LEVELS in level_options else [])]
        raise ValueError(f"Mã cấp bậc lọc ngoài danh sách: {', '.join(bad)}.")

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

        n_all = {scope: ask(scope) for scope in scopes}
        if sum(n_all[c] for c in cities) != n_all[NATIONWIDE]:
            raise ValueError(f"Các thành phố của vai trò {role} không cộng lại bằng toàn quốc.")
        n_by_level = {scope: {level: ask(scope, level) for level in levels} for scope in scopes}
        for filter_level in (ALL_LEVELS, *level_options):
            members = levels if filter_level == ALL_LEVELS else groups.get(filter_level, (filter_level,))
            n_by_scope = {
                scope: n_all[scope] if filter_level == ALL_LEVELS else sum(n_by_level[scope][m] for m in members)
                for scope in scopes
            }
            for scope in scopes:
                mix = {level: n_by_level[scope][level] for level in members if n_by_level[scope][level] > 0}
                cells.append(CellRow(role, scope, n_by_scope[scope], mix, filter_level))
            total = n_by_scope[NATIONWIDE]
            for city in cities:
                if total:
                    share = n_by_scope[city] / total
                else:
                    share = 1.0 if city == UNKNOWN_CITY else 0.0
                shares.append(ShareRow(role, city, share, filter_level))
    return CityShareAggregate(tuple(cells), tuple(shares))


def sources_in_window(day: date, rows: Sequence[tuple[str, date]], *, window_days: int) -> tuple[str, ...]:
    """Nguồn có ít nhất một tin được đếm trong cửa sổ của S, A–Z (#259).

    `rows` là `(nguồn, last_seen)` của các tin đã vào phép đếm (đã loại tin ngoài IT và nguồn bị loại).
    Cửa sổ là cửa sổ của phép đếm (`window_start`), nên một nguồn chỉ được liệt kê khi tin của nó góp vào `n`.
    """
    first = window_start(day, window_days)
    return tuple(sorted({source for source, last_seen in rows if first <= last_seen <= day}))
