"""Tỷ lệ kỹ năng của từng ô, dày (#101, AD-5, FR-9).

Hàm thuần. Nhận các tin đã phân loại cùng tập mã kỹ năng của chúng (`CountedPosting.skills`) và các ô của
`aggregate_city_shares`, trả một hàng cho MỌI (ô, kỹ năng trong từ vựng), kể cả tỷ lệ 0.

Dân số là dân số của ô: cùng cửa sổ (`window_start`), cùng cụm (`cluster_id`), cùng bộ lọc vai trò và cấp (`all`, một
nhóm của `level_groups`, hoặc một cấp thô). Một cụm có kỹ năng khi tin nào của cụm khớp ô cũng nhắc nó; bước tổng hợp
chỉ đưa tin đại diện của cụm nên là kỹ năng của tin đại diện. Số lượt nhắc không vào đây: một tập mã đã là "nhắc ít
nhất một lần". `rate = n_with / n` với `n` là số của ô; hàm kiểm lại `n` bằng cách đếm cụm và từ chối nếu lệch.

Chỉ ô toàn quốc, số năm `any`; ô khác bị bỏ qua. Mã kỹ năng ngoài `skills` bị bỏ, không tạo hàng.
"""

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date

from haido_core.domain.aggregate import ALL_LEVELS, ANY_YEARS, CellRow
from haido_core.domain.population import ALL, NATIONWIDE, CountedPosting, window_start


@dataclass(frozen=True, slots=True)
class SkillRateRow:
    """Một kỹ năng trong một ô. Khóa ô cùng `snapshot_id` của bước gọi."""

    role: str
    seniority: str
    skill: str
    n_with: int
    rate: float
    vocab_version: str
    years: str = ANY_YEARS
    scope: str = NATIONWIDE


def aggregate_skill_rates(
    snapshot_id: date,
    postings: Sequence[CountedPosting],
    cells: Sequence[CellRow],
    *,
    skills: Sequence[str],
    window_days: int,
    level_groups: Mapping[str, Sequence[str]] | None = None,
    vocab_version: str,
) -> tuple[SkillRateRow, ...]:
    """Hàng tỷ lệ của mọi ô toàn quốc, số năm `any` trong `cells`, theo thứ tự ô rồi kỹ năng.

    Raises:
        ValueError: `n` của một ô không bằng số cụm đếm lại; hai số phải từ cùng một dân số.
    """
    groups = {name: frozenset(members) for name, members in (level_groups or {}).items()}
    first = window_start(snapshot_id, window_days)
    clusters: dict[str, list[CountedPosting]] = {}
    for posting in postings:
        if first <= posting.last_seen <= snapshot_id:
            clusters.setdefault(posting.cluster_id, []).append(posting)
    vocab = frozenset(skills)
    ordered = tuple(skills)
    rows: list[SkillRateRow] = []
    for cell in cells:
        if cell.scope != NATIONWIDE or cell.years != ANY_YEARS:
            continue
        members = groups.get(cell.seniority)

        def matches(p: CountedPosting, cell: CellRow = cell, members: frozenset[str] | None = members) -> bool:
            if cell.role != ALL and p.role != cell.role:
                return False
            if cell.seniority == ALL_LEVELS:
                return True
            return p.seniority in members if members is not None else p.seniority == cell.seniority

        n = 0
        counts: Counter[str] = Counter()
        for group in clusters.values():
            hit = [p for p in group if matches(p)]
            if not hit:
                continue
            n += 1
            counts.update(set().union(*(p.skills for p in hit)) & vocab)
        if n != cell.n:
            raise ValueError(f"n của ô ({cell.role}, {cell.seniority}) là {cell.n}, đếm lại được {n}: không khớp.")
        for skill in ordered:
            n_with = counts[skill]
            rows.append(
                SkillRateRow(cell.role, cell.seniority, skill, n_with, n_with / n if n else 0.0, vocab_version)
            )
    return tuple(rows)
