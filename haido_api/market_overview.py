"""Toàn cảnh thị trường (#327): từ số đếm của các ô ra `data` và `meta.cells` của `GET /api/v1/market-overview`.

Hàm thuần, không đọc DB. Nguồn giả và nguồn thật (#328) đều gom số đếm vào `OverviewCounts` rồi gọi
`build_market_overview`, nên hai nguồn cùng một cách chia, cùng thứ tự và cùng luật ẩn số. Mọi tỷ trọng tính ở đây,
web chỉ in (AD-22). Hiển thị của từng số theo `suppression_for` với `n` của chính ô mà số đó trỏ tới, đúng như
`Envelope` kiểm: tỷ trọng cấu phần trỏ tới ô của phần (tử số), tỷ lệ cấp bậc trỏ tới ô của cả nhóm (mẫu số).
"""

import itertools
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from haido_api.schemas.market import MarketOverviewData, OverviewRole, OverviewShare
from haido_core.config import RulesConfig
from haido_core.domain.display_policy import DisplayState, MeasureKind, suppression_for
from haido_core.domain.envelope import CellMeta, Stat

NATIONWIDE = "vn"
ALL = "all"
ENTRY = "entry"
BIG_CITIES = ("ha_noi", "ho_chi_minh")
"""Hai nơi của chỉ số "tin ở Hà Nội hoặc TP.HCM" và của biểu đồ hai phía theo vai trò."""
NAMED_PLACES = ("ha_noi", "ho_chi_minh", "da_nang")
TAIL_PLACES = ("remote", "abroad", "unknown")
OTHER_PROVINCES = "other_provinces"
BIG_CITIES_CELL = "big_cities.all"
OTHER_ROLE = "other"


@dataclass(frozen=True)
class OverviewCounts:
    """Số đếm của một snapshot, đọc nguyên từ các ô `aggregate` đã ghi (không đếm lại từ bảng tin)."""

    total_n: int
    """`n` của ô toàn quốc mọi vai trò, mọi cấp, mọi số năm."""
    total_mix: Mapping[str, int]
    """Số tin theo cấp chi tiết của ô đó."""
    entry_n: int
    """`n` của ô toàn quốc cấp `entry`."""
    roles: Mapping[str, tuple[int, Mapping[str, int]]]
    """Mỗi vai trò: `n` và số tin theo cấp của ô toàn quốc."""
    role_entry: Mapping[str, int]
    """Mỗi vai trò: `n` của ô toàn quốc cấp `entry`; thiếu là 0."""
    places: Mapping[str, int]
    """Mỗi nơi (mã của `config/rules.toml`): `n` của ô mọi vai trò; thiếu là 0."""
    role_places: Mapping[str, Mapping[str, int]]
    """Mỗi vai trò: `n` ở Hà Nội và TP.HCM; thiếu là 0."""
    years_upto: Mapping[int, int]
    """Mỗi mốc N của `years_options`: số tin yêu cầu tối thiểu không quá N năm (không gồm tin không ghi)."""
    years_unstated: int
    """Số tin không ghi số năm kinh nghiệm."""


def year_buckets(options: Sequence[int]) -> list[str]:
    """Mã các mốc số năm theo thứ tự: `0`, `1`, …, khoảng `4-5` khi hai mốc liền nhau cách hơn một năm,
    `over_<mốc cuối>`, rồi `none`."""
    marks = sorted(options)
    codes: list[str] = []
    prev: int | None = None
    for mark in marks:
        low = 0 if prev is None else prev + 1
        codes.append(str(mark) if low == mark else f"{low}-{mark}")
        prev = mark
    return [*codes, f"over_{marks[-1]}", "none"]


def _cell(n: int, mix: Mapping[str, int] | None = None) -> CellMeta:
    return CellMeta(
        n=n, fallback_label=None, seniority_mix=dict(mix or {}), n_by_measure={}, insufficient_by_measure={}
    )


def _ratio(part: int, whole: int) -> float:
    return part / whole if whole > 0 else 0.0


def _stat(kind: MeasureKind, part: int, whole: int, cell_id: str, display_n: int, min_sample: int) -> Stat:
    display = suppression_for(kind, display_n, min_sample=min_sample)
    value = None if display is DisplayState.NULL_DATA else _ratio(part, whole)
    return Stat(value=value, kind=kind, display=display, cell_id=cell_id)


def build_market_overview(counts: OverviewCounts, rules: RulesConfig) -> tuple[MarketOverviewData, dict[str, CellMeta]]:
    """`data` và các ô `meta.cells` mà `data` trỏ tới.

    Raises:
        RuntimeError: số đếm tự mâu thuẫn (ô entry nhiều hơn ô cả nhóm, mốc số năm giảm, hay tổng các mốc vượt `n`
            toàn quốc). Đó là lỗi của bước `aggregate`, không phải dữ liệu để hiện.
    """
    min_sample = rules.min_sample
    entry_levels = list(rules.level_groups.get(ENTRY, ()))
    if not entry_levels:
        raise RuntimeError(f"config/rules.toml thiếu nhóm cấp bậc {ENTRY!r} trong level_groups.")
    levels = [lv for lv in rules.level_options if lv not in rules.level_groups]
    total, total_id, entry_id = counts.total_n, f"{NATIONWIDE}.{ALL}", f"{NATIONWIDE}.{ALL}.{ENTRY}"
    if counts.entry_n > total:
        raise RuntimeError(f"Ô {entry_id} có {counts.entry_n} tin entry, nhiều hơn {total} tin của {total_id}.")
    cells: dict[str, CellMeta] = {
        total_id: _cell(total, counts.total_mix),
        entry_id: _cell(counts.entry_n, {lv: k for lv, k in counts.total_mix.items() if lv in entry_levels}),
    }

    def level_mix(mix: Mapping[str, int], n: int, cell_id: str) -> list[OverviewShare]:
        return [
            OverviewShare(code=lv, share=_stat(MeasureKind.LEVEL_SHARE, mix.get(lv, 0), n, cell_id, n, min_sample))
            for lv in levels
        ]

    rows: list[OverviewRole] = []
    for role in rules.roles:
        n, mix = counts.roles.get(role, (0, {}))
        entry_n = counts.role_entry.get(role, 0)
        if entry_n > n:
            raise RuntimeError(f"Vai trò {role} có {entry_n} tin entry nhiều hơn {n} tin của vai trò.")
        cell_id, role_entry_id = f"{NATIONWIDE}.{role}", f"{NATIONWIDE}.{role}.{ENTRY}"
        cells[cell_id] = _cell(n, mix)
        cells[role_entry_id] = _cell(entry_n, {lv: k for lv, k in mix.items() if lv in entry_levels})
        places: list[OverviewShare] = []
        for city in BIG_CITIES:
            city_n = counts.role_places.get(role, {}).get(city, 0)
            city_id = f"{city}.{role}"
            cells[city_id] = _cell(city_n)
            places.append(
                OverviewShare(
                    code=city, share=_stat(MeasureKind.COMPOSITION_SHARE, city_n, n, city_id, city_n, min_sample)
                )
            )
        rows.append(
            OverviewRole(
                role=role,
                cell_id=cell_id,
                entry_cell_id=role_entry_id,
                share=_stat(MeasureKind.COMPOSITION_SHARE, n, total, cell_id, n, min_sample),
                entry_share=_stat(MeasureKind.LEVEL_SHARE, entry_n, n, cell_id, n, min_sample),
                level_mix=level_mix(mix, n, cell_id),
                places=places,
            )
        )
    # Thứ tự hiển thị do máy chủ quyết: nhiều tin trước, cùng số tin thì theo mã; "Vai trò khác" luôn ở cuối.
    rows.sort(key=lambda r: (r.role == OTHER_ROLE, -cells[r.cell_id].n, r.role))

    def place_share(code: str, n: int) -> OverviewShare:
        cell_id = f"{code}.{ALL}"
        cells[cell_id] = _cell(n)
        return OverviewShare(code=code, share=_stat(MeasureKind.COMPOSITION_SHARE, n, total, cell_id, n, min_sample))

    provinces = [c for c in rules.city_codes.values() if c not in NAMED_PLACES and c not in TAIL_PLACES]
    places = [
        *(place_share(c, counts.places.get(c, 0)) for c in NAMED_PLACES),
        place_share(OTHER_PROVINCES, sum(counts.places.get(c, 0) for c in provinces)),
        *(place_share(c, counts.places.get(c, 0)) for c in TAIL_PLACES),
    ]
    big_n = sum(counts.places.get(c, 0) for c in BIG_CITIES)
    cells[BIG_CITIES_CELL] = _cell(big_n)

    marks = sorted(rules.years_options)
    upto = [counts.years_upto.get(m, 0) for m in marks]
    if any(b < a for a, b in itertools.pairwise(upto)):
        raise RuntimeError(f"Số tin theo mốc số năm phải tăng dần, nhận {dict(zip(marks, upto, strict=True))}.")
    over = total - upto[-1] - counts.years_unstated
    if over < 0:
        raise RuntimeError(f"Tổng các mốc số năm ({upto[-1]} + {counts.years_unstated} không ghi) vượt {total} tin.")
    parts = [upto[0], *(b - a for a, b in itertools.pairwise(upto)), over, counts.years_unstated]
    years: list[OverviewShare] = []
    for code, n in zip(year_buckets(marks), parts, strict=True):
        cell_id = f"{NATIONWIDE}.{ALL}.years_{code}"
        cells[cell_id] = _cell(n)
        years.append(
            OverviewShare(code=code, share=_stat(MeasureKind.COMPOSITION_SHARE, n, total, cell_id, n, min_sample))
        )

    data = MarketOverviewData(
        total_cell_id=total_id,
        entry_cell_id=entry_id,
        levels=levels,
        entry_levels=entry_levels,
        level_mix=level_mix(counts.total_mix, total, total_id),
        entry_share=_stat(MeasureKind.LEVEL_SHARE, counts.entry_n, total, total_id, total, min_sample),
        big_cities_share=_stat(MeasureKind.COMPOSITION_SHARE, big_n, total, BIG_CITIES_CELL, big_n, min_sample),
        roles=rows,
        places=places,
        years=years,
    )
    return data, cells
