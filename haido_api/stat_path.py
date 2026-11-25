"""Nội dung lộ trình học và phép ghép nó với tỷ lệ thật (#216).

`content/learning_path.json` giữ chủ đề, đồ thị, lời dẫn và tài liệu của từng vai trò, kèm dấu rà soát `review`. `null` là
chưa có giảng viên rà soát (#96): `StatMarket` trả `not_ready`. Dấu sai hình hay thiếu là lỗi lúc nạp, không bao giờ thành
"đã rà soát".

Nút trên lộ trình là kỹ năng `core` và `common` của ô cộng mọi tổ tiên của chúng trên đồ thị. Tổ tiên hiếm ghi
`company_specific` và là kỹ năng nền tảng (FR-20); kỹ năng hiếm không ai cần thì bỏ. Chặng là chủ đề của nút; chủ đề không
còn nút nào thì bỏ.
"""

import json
from collections.abc import Collection, Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from haido_api.learning_path import (
    Topic,
    apply_have,
    build_stages,
    topic_stages,
    topics_of,
)
from haido_api.schemas.learning_path import LearningPathData, PathStatus
from haido_api.schemas.market import SkillRatesData
from haido_core.domain.display_policy import DisplayState, MeasureKind
from haido_core.domain.envelope import CoverageNote, Stat

PATH_FILE = Path(__file__).parent / "content" / "learning_path.json"
DRAFT_NOTE = CoverageNote(
    code="draft_path", text="Thứ tự học trên lộ trình này là bản nháp, chưa được giảng viên rà soát."
)
"""Lưu ý kèm mọi lộ trình chưa rà soát được hiện (chỉ app demo)."""

_COMPANY_SPECIFIC = "company_specific"
_REVIEW_KEYS = {"reviewed_on", "record"}


@dataclass(frozen=True)
class Review:
    """Giảng viên đã rà soát: ngày và đường dẫn biên bản trong repo (#96)."""

    reviewed_on: date
    record: str


@dataclass(frozen=True)
class RolePath:
    """Nội dung lộ trình của một vai trò. `review` là `None` khi chưa rà soát."""

    topics: list[Topic]
    nodes: dict[str, dict[str, Any]]
    review: Review | None


def load_paths(file: Path = PATH_FILE) -> dict[str, RolePath]:
    """Nội dung mọi vai trò.

    Raises:
        ValueError: thiếu hoặc sai dấu `review`, hoặc đồ thị trái chủ đề (`PathGraphError`).
    """
    raw = json.loads(file.read_text(encoding="utf-8"))
    out: dict[str, RolePath] = {}
    for role, entry in raw["roles"].items():
        nodes = {node["skill"]: node for node in entry["skills"]}
        topics = topics_of(entry)
        topic_stages(topics, {code: node["requires"] for code, node in nodes.items()})
        out[role] = RolePath(topics, nodes, _review(role, entry))
    return out


def _review(role: str, entry: Mapping[str, Any]) -> Review | None:
    if "review" not in entry:
        raise ValueError(f"Lộ trình {role}: thiếu 'review' (null là chưa rà soát).")
    value = entry["review"]
    if value is None:
        return None
    if not isinstance(value, dict) or set(value) != _REVIEW_KEYS:
        raise ValueError(f"Lộ trình {role}: 'review' phải là null hoặc có đúng {sorted(_REVIEW_KEYS)}.")
    record = value["record"]
    if not isinstance(record, str) or not record.strip():
        raise ValueError(f"Lộ trình {role}: 'review.record' phải là đường dẫn biên bản.")
    try:
        reviewed_on = date.fromisoformat(value["reviewed_on"])
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Lộ trình {role}: 'review.reviewed_on' phải là ngày YYYY-MM-DD.") from exc
    return Review(reviewed_on, record)


def not_ready(*, role: str, level: str, have: Collection[str], entry_cell_id: str) -> LearningPathData:
    return LearningPathData(
        role=role, level=level, status=PathStatus.NOT_READY, cell_id=None, entry_cell_id=entry_cell_id,
        stages=[], current_stage=None, have_on_path=0, path_size=0, have_ignored=sorted(set(have)),
    )  # fmt: skip


def ready(
    *,
    role: str,
    level: str,
    have: Collection[str],
    path: RolePath,
    rates: SkillRatesData,
    raw_rates: Mapping[str, float],
    entry_cell_id: str,
) -> LearningPathData | None:
    """Lộ trình ghép với `rates` (response `skill-rates` cùng vai trò, cấp) và tỷ lệ mọi kỹ năng của cùng ô.

    `None` khi không nút nào của lộ trình có số ở ô này.
    """
    graph, cell_id = path.nodes, rates.cell_id
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
    stages = build_stages(path.topics, nodes, stats, groups)
    out, current, have_on_path, path_size, ignored = apply_have(stages, set(have))
    return LearningPathData(
        role=role, level=level, status=PathStatus.READY, cell_id=cell_id, entry_cell_id=entry_cell_id,
        stages=out, current_stage=current, have_on_path=have_on_path, path_size=path_size, have_ignored=ignored,
    )  # fmt: skip
