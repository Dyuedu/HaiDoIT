"""Phép 2: chọn ô thống kê và thứ tự quay về (#106, AD-2, AD-6, FR-19).

Thứ tự quay về (đã chốt ở #106), mọi bước giữ nguyên snapshot, vai trò và phạm vi:

1. `(vai trò, cấp được yêu cầu)`;
2. nếu cấp là cấp thô thuộc một nhóm của `level_groups` (ví dụ `fresher` thuộc `entry`): `(vai trò, nhóm)`;
3. `(vai trò, all)`.

Cấp `all` chỉ có một ứng viên. Khi yêu cầu có nhánh thì mỗi bước thử nhánh trước rồi mới tới nhánh `all` của cùng cấp
("giữ cấp bậc trước, giữ nhánh sau", PRD §3); nhánh chưa có dữ liệu thì các bước nhánh chỉ là ô thiếu.

Ô đạt khi cỡ mẫu của nó `>= min_sample`. Cỡ mẫu là `CellStats.sample_n` nếu phép đo có mẫu số riêng (tỷ lệ kỹ năng
dùng `n_scanned`, AD-17), không thì `n`. Ô thiếu coi như cỡ mẫu 0. Không ô nào đạt thì trả ô cuối cùng đã xét kèm
nhãn nói chưa tập nào đủ, để người gọi ẩn số (`null_data`) thay vì đưa số của tập nhỏ.

Phạm vi không phải tham số của phép này: mọi ứng viên mang `scope` của yêu cầu, nên ô thành phố không thể quay về ô
toàn quốc (AD-6). Cùng truy vấn và cùng bảng ô thì cùng kết quả (AD-2): hàm không đọc đồng hồ, config hay DB.

Nhãn gọi tên con số của cỡ mẫu bằng `sample_noun` ("tin" mặc định; tỷ lệ kỹ năng dùng "tin đọc được kỹ năng" vì
`n_scanned` khác `n` của ô). Câu "Mid trở lên" làm tròn nửa lên, mẫu số là mọi tin của `seniority_mix` kể cả `unknown`.

Cỡ mẫu và cơ cấu cấp bậc của từng ô do người gọi đưa qua `lookup` ở constructor; module này không biết DB hay API.
Module chỉ import thư viện chuẩn và registry.
"""

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field

from haido_core.domain.registry import (
    CellChoice,
    CellKey,
    CellQuery,
    OneOrMany,
    as_batch,
)

ALL = "all"
DEFAULT_MID_AND_ABOVE = ("mid", "senior", "lead")


@dataclass(frozen=True, slots=True)
class CellStats:
    """Cỡ mẫu của một ô: `n` của `stat_cells`, cơ cấu cấp bậc và (nếu có) mẫu số riêng của phép đo."""

    n: int
    seniority_mix: Mapping[str, int] = field(default_factory=dict)
    sample_n: int | None = None
    """Mẫu số của phép đo đang hỏi (tỷ lệ kỹ năng: `n_scanned`). `None` thì dùng `n`."""

    @property
    def size(self) -> int:
        return self.n if self.sample_n is None else self.sample_n


class CellSelectionError(ValueError):
    """Đầu vào của `select_cell` sai: không phải `CellQuery` hoặc `min_sample` ngoài miền."""


type CellLookup = Callable[[CellKey], CellStats | None]
"""Tra một ô theo khóa. `None` là ô chưa có."""


class CellSelector:
    """Thân hàm duy nhất của phép 2."""

    def __init__(
        self,
        lookup: CellLookup,
        *,
        level_groups: Mapping[str, Sequence[str]],
        names: Mapping[str, str] | None = None,
        mid_and_above: Sequence[str] = DEFAULT_MID_AND_ABOVE,
        sample_noun: str = "tin",
    ) -> None:
        self._noun = sample_noun
        self._lookup = lookup
        self._groups = {group: tuple(members) for group, members in level_groups.items()}
        self._names = dict(names or {})
        self._mid = frozenset(mid_and_above)

    def select_cell(self, queries: OneOrMany[CellQuery]) -> OneOrMany[CellChoice]:
        batch = as_batch(queries)
        if batch is None:
            return self._one(queries)  # type: ignore[arg-type]
        return tuple(self._one(item) for item in batch)

    # ------------------------------------------------------------------ một truy vấn

    def _one(self, query: CellQuery) -> CellChoice:
        if not isinstance(query, CellQuery):
            raise CellSelectionError(f"Yêu cầu phải là CellQuery, nhận {type(query).__name__}.")
        if isinstance(query.min_sample, bool) or not isinstance(query.min_sample, int) or query.min_sample < 1:
            raise CellSelectionError(f"min_sample phải là số nguyên từ 1, nhận {query.min_sample!r}.")
        order = self._order(query.requested)
        tried: list[tuple[CellKey, int, CellStats | None]] = []
        for cell in order:
            stats = self._lookup(cell)
            size = 0 if stats is None else stats.size
            tried.append((cell, size, stats))
            if size >= query.min_sample:
                return self._choice(query, order, tried, qualified=True)
        return self._choice(query, order, tried, qualified=False)

    def _order(self, requested: CellKey) -> tuple[CellKey, ...]:
        level = requested.seniority
        steps: list[str | None] = [level]
        if level is not None and level != ALL:
            group = next((g for g, members in self._groups.items() if level in members), None)
            if group is not None:
                steps.append(group)
            steps.append(ALL)
        cells: list[CellKey] = []
        for step in steps:
            for branch in self._branches(requested.branch):
                cell = CellKey(requested.snapshot_id, requested.role, branch, step, requested.scope)
                if cell not in cells:
                    cells.append(cell)
        return tuple(cells)

    @staticmethod
    def _branches(branch: str | None) -> tuple[str | None, ...]:
        if branch is None or branch == ALL:
            return (branch,)
        return (branch, ALL)

    # ------------------------------------------------------------------ nhãn

    def _choice(
        self,
        query: CellQuery,
        order: tuple[CellKey, ...],
        tried: list[tuple[CellKey, int, CellStats | None]],
        *,
        qualified: bool,
    ) -> CellChoice:
        chosen, size, stats = tried[-1]
        requested_size = tried[0][1]
        label: str | None = None
        if not qualified:
            where = "; ".join(f"{self._name(cell)} có {n} {self._noun}" for cell, n, _ in tried)
            label = f"Chưa có tập nào đủ {query.min_sample} {self._noun} ({where}), nên chưa đủ dữ liệu để hiện số."
        elif chosen != query.requested:
            label = (
                f"{self._name(query.requested)} chỉ có {requested_size} {self._noun} (dưới {query.min_sample}), "
                f"chưa đủ để tính riêng, nên số dưới đây lấy từ {self._name(chosen)} ({size} {self._noun})."
            )
        if label is not None and self._is_last_step(query.requested, chosen) and self._is_entry_type(query.requested):
            share = self._mid_share(stats)
            if share is not None:
                label += f" Trong tập này {share}% tin là Mid trở lên."
        return CellChoice(cell=chosen, n=size, label=label, order=order)

    def _is_last_step(self, requested: CellKey, chosen: CellKey) -> bool:
        return chosen.seniority == ALL and requested.seniority != ALL

    def _is_entry_type(self, requested: CellKey) -> bool:
        level = requested.seniority
        if level is None or level == ALL:
            return False
        return level in self._groups or any(level in members for members in self._groups.values())

    def _mid_share(self, stats: CellStats | None) -> int | None:
        if stats is None:
            return None
        total = sum(stats.seniority_mix.values())  # mẫu số là mọi tin của ô, kể cả `unknown`
        if total <= 0:
            return None
        mid = sum(count for level, count in stats.seniority_mix.items() if level in self._mid)
        # Làm tròn nửa lên bằng số nguyên (round() của Python làm tròn nửa về chẵn: 12,5 thành 12).
        return (200 * mid + total) // (2 * total)

    def _name(self, cell: CellKey) -> str:
        role = self._names.get(cell.role, cell.role)
        level = cell.seniority if cell.seniority is not None else ALL
        text = f"{role} · {self._names.get(level, level)}"
        if cell.branch not in (None, ALL):
            text = f"nhánh {self._names.get(cell.branch, cell.branch)} · {text}"
        if cell.scope != "vn":
            text += f" tại {self._names.get(cell.scope, cell.scope)}"
        return text
