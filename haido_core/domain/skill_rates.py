"""Tỷ lệ kỹ năng của từng ô, dày (#101, AD-5, FR-9).

Hàm thuần. Nhận các tin đã phân loại cùng tập mã kỹ năng của chúng (`CountedPosting.skills`) và các ô của
`aggregate_city_shares`, trả một hàng cho MỌI (ô, kỹ năng trong từ vựng), kể cả tỷ lệ 0.

Dân số là dân số của ô: cùng cửa sổ (`postings_in_window`), cùng cụm (`cluster_id`), cùng cách khớp ô (`matches_cell`)
của phép 3, với bộ lọc vai trò và cấp (`all`, một nhóm của `level_groups`, hoặc một cấp thô).

Quy tắc hợp (D1): một cụm nhắc kỹ năng X khi BẤT KỲ tin nào của cụm khớp ô và đã quét mà nhắc X; cụm vẫn đếm một lần.
Nhãn vai trò, cấp, thành phố, số năm của cụm vẫn là của tin đại diện (không đổi). Bước tổng hợp đưa mỗi cụm một tin
mang hợp kỹ năng của mọi thành viên.

Mẫu số (D2): chỉ các cụm đã quét. Cụm đã quét khi có ít nhất một tin khớp ô mà `skills` khác `None` (kể cả `frozenset()`,
nghĩa là quét mà không thấy gì). Cụm chưa quét (mọi tin `None`) không vào tử số lẫn mẫu số. Số cụm đã quét của ô là
`n_scanned`, cùng giá trị ở mọi hàng của ô; `rate = n_with / n_scanned`, 0 khi `n_scanned = 0`. `n_scanned` là cỡ mẫu của
chính phép đo này (AD-17 `n_with_value`), không phải `n` của ô; `n_scanned <= n`. Số lượt nhắc không vào đây.

Hàm kiểm lại `n` bằng cách đếm cụm và từ chối nếu lệch `n` của ô.

Chỉ ô toàn quốc, số năm `any`; ô khác bị bỏ qua. Mã kỹ năng ngoài `skills` bị bỏ, không tạo hàng.
"""

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date

from haido_core.domain.aggregate import ALL_LEVELS, ANY_YEARS, CellRow
from haido_core.domain.population import (
    ALL,
    NATIONWIDE,
    CountedPosting,
    matches_cell,
    postings_in_window,
)
from haido_core.domain.registry import CellKey


@dataclass(frozen=True, slots=True)
class SkillRateRow:
    """Một kỹ năng trong một ô. Khóa ô cùng `snapshot_id` của bước gọi."""

    role: str
    seniority: str
    skill: str
    n_with: int
    n_scanned: int
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
    groups = {name: tuple(members) for name, members in (level_groups or {}).items()}
    clusters: dict[str, list[CountedPosting]] = {}
    for posting in postings_in_window(postings, snapshot_id, window_days):
        clusters.setdefault(posting.cluster_id, []).append(posting)
    vocab = frozenset(skills)
    ordered = tuple(skills)
    day = snapshot_id.isoformat()
    rows: list[SkillRateRow] = []
    for cell in cells:
        if cell.scope != NATIONWIDE or cell.years != ANY_YEARS:
            continue
        levels = (ALL,) if cell.seniority == ALL_LEVELS else groups.get(cell.seniority, (cell.seniority,))
        keys = tuple(CellKey(day, cell.role, None, level, NATIONWIDE) for level in levels)
        n = 0
        scanned = 0
        counts: Counter[str] = Counter()
        for group in clusters.values():
            hit = [p for p in group if any(matches_cell(p, key) for key in keys)]
            if not hit:
                continue
            n += 1
            known = [p.skills for p in hit if p.skills is not None]
            if not known:
                continue
            scanned += 1
            counts.update(frozenset().union(*known) & vocab)
        if n != cell.n:
            raise ValueError(f"n của ô ({cell.role}, {cell.seniority}) là {cell.n}, đếm lại được {n}: không khớp.")
        for skill in ordered:
            n_with = counts[skill]
            rate = n_with / scanned if scanned else 0.0
            rows.append(SkillRateRow(cell.role, cell.seniority, skill, n_with, scanned, rate, vocab_version))
    return tuple(rows)
