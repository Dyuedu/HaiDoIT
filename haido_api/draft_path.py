"""Lộ trình nháp cho demo (#216, một phần): tỷ lệ thật của snapshot ghép với đồ thị chưa rà soát.

Tỷ lệ, nhóm và ô là của `StatMarket.skill_rates`, nên bằng `/skill-rates` cùng (vai trò, cấp). Đồ thị, chủ đề, lời dẫn
và tài liệu là `fixtures/draft_learning_path.json`, chưa có giảng viên rà soát (#96), nên bản này chỉ được dựng ở
`haido_api.demo`, không có trong `IMPLEMENTATIONS` và không chạy trên prod. Mỗi lộ trình trả ra mang lưu ý `draft_path`.

Nút trên lộ trình là kỹ năng `core` và `common` của ô cộng mọi tổ tiên của chúng trên đồ thị. Tổ tiên hiếm ghi
`company_specific` và là kỹ năng nền tảng (FR-20); kỹ năng hiếm không ai cần thì bỏ. Chặng là
chủ đề của nút; chủ đề không còn nút nào thì bỏ.
"""

import json
from collections.abc import Callable, Collection
from pathlib import Path
from typing import Any

from sqlalchemy import Engine

from haido_api.learning_path import Topic, apply_have, build_stages, topics_of
from haido_api.market_source import UnknownCell
from haido_api.schemas.learning_path import (
    LearningPathData,
    PathStatus,
)
from haido_api.schemas.market import SkillRatesData
from haido_api.stat_market import (
    ALL,
    ENTRY,
    NATIONWIDE,
    StatMarket,
    _cell_meta,
    _national_cells,
    _skill_rate_rows,
)
from haido_core.config import RulesConfig
from haido_core.domain.display_policy import DisplayState, MeasureKind
from haido_core.domain.envelope import CoverageNote, Envelope, Stat

DRAFT_FIXTURE = Path(__file__).parent / "fixtures" / "draft_learning_path.json"
DRAFT_NOTE_CODE = "draft_path"
_DRAFT_NOTE = CoverageNote(
    code=DRAFT_NOTE_CODE, text="Thứ tự học trên lộ trình này là bản nháp, chưa được giảng viên rà soát."
)
_COMPANY_SPECIFIC = "company_specific"


class DraftPathMarket(StatMarket):
    """`StatMarket` có thêm `learning_path` nháp. Các phép khác không đổi."""

    def __init__(
        self, *, engine_factory: Callable[[], Engine] | None = None, rules: RulesConfig | None = None
    ) -> None:
        super().__init__(engine_factory=engine_factory, rules=rules)
        raw = json.loads(DRAFT_FIXTURE.read_text(encoding="utf-8"))
        self._topics = {role: topics_of(entry) for role, entry in raw["roles"].items()}
        self._graphs: dict[str, dict[str, dict[str, Any]]] = {
            role: {node["skill"]: node for node in entry["skills"]} for role, entry in raw["roles"].items()
        }

    def learning_path(self, *, role: str, level: str, have: Collection[str]) -> Envelope[LearningPathData]:
        rates = self.skill_rates(role=role, level=level)
        day = rates.meta.snapshot_date
        chosen_level = rates.data.cell_id.removeprefix(f"{NATIONWIDE}.{role}").removeprefix(".") or ALL
        with self._db().connect() as conn:
            entry_n, entry_mix = _national_cells(conn, day, ENTRY).get(role, (0, {}))
            raw_rates = {skill: rate for skill, _, rate in _skill_rate_rows(conn, day, role, chosen_level)}
        entry_cell_id = f"{NATIONWIDE}.{role}.{ENTRY}"
        cells = {entry_cell_id: _cell_meta(entry_n, entry_mix)}
        notes = list(rates.meta.coverage_notes)
        graph = self._graphs.get(role)
        if graph is None:
            data = LearningPathData(
                role=role, level=level, status=PathStatus.NOT_READY, cell_id=None, entry_cell_id=entry_cell_id,
                stages=[], current_stage=None, have_on_path=0, path_size=0, have_ignored=sorted(set(have)),
            )  # fmt: skip
        else:
            data = _ready(role, level, have, self._topics[role], graph, rates.data, raw_rates, entry_cell_id)
            if data is None:
                raise UnknownCell("Lộ trình của vai trò đã chọn chưa có số liệu ở cấp bậc này.", snapshot_date=day)
            cells |= rates.meta.cells
            notes.append(_DRAFT_NOTE)
        meta = rates.meta.model_copy(update={"cells": cells, "coverage_notes": notes})
        return Envelope[LearningPathData](data=data, meta=meta)


def _ready(
    role: str,
    level: str,
    have: Collection[str],
    topics: list[Topic],
    graph: dict[str, dict[str, Any]],
    rates: SkillRatesData,
    raw_rates: dict[str, float],
    entry_cell_id: str,
) -> LearningPathData | None:
    """Lộ trình của một vai trò có đồ thị; `None` khi không nút nào của đồ thị có số ở ô này."""
    cell_id = rates.cell_id
    hidden = rates.core_size is None  # không tập nào đủ mẫu: mọi tỷ lệ bị ẩn
    shown = {row.skill: row for row in rates.rows}
    selected: set[str] = set()
    todo = list(graph) if hidden else [code for code in graph if code in shown]
    while todo:
        code = todo.pop()
        if code not in selected:
            selected.add(code)
            todo.extend(graph[code]["requires"])
    if not selected or not (hidden or selected <= set(raw_rates)):
        return None
    stats: dict[str, Stat] = {}
    groups: dict[str, str | None] = {}
    for code in selected:
        if hidden:
            stats[code] = Stat(
                value=None, kind=MeasureKind.SKILL_RATE, display=DisplayState.NULL_DATA, cell_id=cell_id
            )
            groups[code] = None
        elif code in shown:
            stats[code], groups[code] = shown[code].rate, shown[code].group
        else:
            stats[code] = Stat(
                value=raw_rates[code], kind=MeasureKind.SKILL_RATE, display=rates.rows[0].rate.display, cell_id=cell_id
            )
            groups[code] = _COMPANY_SPECIFIC
    nodes = {code: node for code, node in graph.items() if code in selected}
    stages = build_stages(topics, nodes, stats, groups)
    out, current, have_on_path, path_size, ignored = apply_have(stages, set(have))
    return LearningPathData(
        role=role, level=level, status=PathStatus.READY, cell_id=cell_id, entry_cell_id=entry_cell_id,
        stages=out, current_stage=current, have_on_path=have_on_path, path_size=path_size, have_ignored=ignored,
    )  # fmt: skip
