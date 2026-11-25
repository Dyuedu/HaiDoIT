"""Áp `?have=` lên một lộ trình đã xếp (AD-22): cờ `have`, số đếm, chặng hiện tại, mã bị bỏ qua.

Hàm thuần, dùng chung cho bản giả và bản thật (#216). Không đổi chặng, không đổi thứ tự (chặng là thuộc tính của
nút kỹ năng). Web không làm các phép này.

Chặng là chủ đề khai báo sẵn (`topic_stages`); cạnh tiên quyết luôn đi sang chặng sau. Cũng ở đây: độ sâu của đồ thị và `foundation_for` từ đồ thị `requires` (mã -> các mã cần học trước). Đồ thị lỗi (mã không có
nút, chu trình) ra `PathGraphError`, không `KeyError` hay `RecursionError`.
"""

from collections.abc import Collection, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from haido_api.schemas.learning_path import PathResource, PathSkill, PathStage, order_key
from haido_core.domain.envelope import Stat


class PathGraphError(ValueError):
    """Đồ thị học trước - học sau hỏng: `requires` trỏ tới mã không có nút, hoặc có chu trình."""


def _check_graph(requires: Mapping[str, Sequence[str]]) -> None:
    for code, needs in requires.items():
        for need in needs:
            if need not in requires:
                raise PathGraphError(
                    f"{code} cần {need} nhưng {need} không có nút trên đồ thị."
                )


def stage_numbers(requires: Mapping[str, Sequence[str]]) -> dict[str, int]:
    """Chặng của từng nút: 1 + chặng cao nhất của các nút nó cần (nút không cần ai là chặng 1).

    Duyệt không đệ quy (đồ thị sâu không vỡ stack).

    Raises:
        PathGraphError: `requires` trỏ tới mã không có nút, hoặc đồ thị có chu trình.
    """
    _check_graph(requires)
    remaining = {code: len(set(needs)) for code, needs in requires.items()}
    dependents: dict[str, list[str]] = {code: [] for code in requires}
    for code, needs in requires.items():
        for need in set(needs):
            dependents[need].append(code)
    stage = {code: 1 for code, left in remaining.items() if left == 0}
    queue = sorted(stage)
    while queue:
        code = queue.pop()
        for dependent in dependents[code]:
            stage[dependent] = max(stage.get(dependent, 1), stage[code] + 1)
            remaining[dependent] -= 1
            if remaining[dependent] == 0:
                queue.append(dependent)
    stuck = sorted(code for code, left in remaining.items() if left > 0)
    if stuck:
        raise PathGraphError(
            f"Đồ thị có chu trình, gồm hoặc phụ thuộc: {', '.join(stuck)}."
        )
    return {code: stage[code] for code in sorted(requires)}


@dataclass(frozen=True)
class Topic:
    """Một chủ đề của lộ trình, theo thứ tự học khai báo."""

    title: str
    choose_one: bool
    skills: tuple[str, ...]


def topics_of(entry: Mapping[str, Any]) -> list[Topic]:
    """Chủ đề của một vai trò trong file lộ trình (`topics`)."""
    return [Topic(t["title"], t["choose_one"], tuple(t["skills"])) for t in entry["topics"]]


def topic_stages(topics: Sequence[Topic], requires: Mapping[str, Sequence[str]]) -> list[Topic]:
    """Các chặng của những nút trong `requires`: chủ đề theo thứ tự khai báo, bỏ nút không được chọn.

    Chủ đề không còn nút nào thì bỏ; chủ đề chọn một chỉ còn một nút thì thành chủ đề thường (không còn gì để chọn).

    Raises:
        PathGraphError: như `stage_numbers`; nút không thuộc chủ đề nào hoặc thuộc hai chủ đề; hoặc kỹ năng cần học
            trước ở cùng hoặc sau chủ đề của kỹ năng cần nó.
    """
    stage_numbers(requires)
    topic_of: dict[str, int] = {}
    for index, topic in enumerate(topics):
        for code in topic.skills:
            if code in topic_of:
                raise PathGraphError(f"{code} nằm ở hai chủ đề: {topics[topic_of[code]].title} và {topic.title}.")
            topic_of[code] = index
    for code, needs in requires.items():
        if code not in topic_of:
            raise PathGraphError(f"{code} không thuộc chủ đề nào.")
        for need in needs:
            if topic_of.get(need, -1) >= topic_of[code]:
                raise PathGraphError(f"{code} cần {need} nhưng chủ đề của {code} đứng cùng hoặc trước chủ đề của {need}.")
    out = []
    for topic in topics:
        skills = tuple(code for code in topic.skills if code in requires)
        if skills:
            out.append(Topic(topic.title, topic.choose_one and len(skills) > 1, skills))
    return out


def build_stages(
    topics: Sequence[Topic],
    nodes: Mapping[str, Mapping[str, Any]],
    stats: Mapping[str, Stat],
    groups: Mapping[str, str | None],
) -> list[PathStage]:
    """Các chặng đã xếp của những nút trong `nodes` (mã -> nút của file lộ trình), mọi `have` là `False`.

    Nút `foundation` và nút riêng công ty ghi `foundation_for` (FR-20). Dùng chung cho bản giả và bản nháp.
    """
    requires = {code: node["requires"] for code, node in nodes.items()}
    stages = topic_stages(topics, requires)
    targets = foundation_targets(requires, groups)
    needed_by: dict[str, list[str]] = {code: [] for code in nodes}
    for code, needs in requires.items():
        for need in needs:
            needed_by[need].append(code)

    def skill(code: str) -> PathSkill:
        node = nodes[code]
        return PathSkill(
            skill=code,
            rate=stats[code],
            group=groups[code],
            foundation_for=targets[code] if node["foundation"] or groups[code] == "company_specific" else [],
            prerequisite_for=sorted(needed_by[code]),
            have=False,
            blurb=node["blurb"],
            resource=PathResource(**node["resource"]),
        )

    return [
        PathStage(
            stage=number,
            title=topic.title,
            choose_one=topic.choose_one,
            skills=sorted((skill(code) for code in topic.skills), key=order_key),
        )
        for number, topic in enumerate(stages, start=1)
    ]


def foundation_targets(
    requires: Mapping[str, Sequence[str]], groups: Mapping[str, str | None]
) -> dict[str, list[str]]:
    """`foundation_for` của từng nút: các nút `core` hoặc `common` có nút này là tổ tiên (bắc cầu), xếp A–Z.

    Nhóm bị ẩn (`None`) không phải `core` hay `common`, nên không bao giờ là đích.

    Raises:
        PathGraphError: như `stage_numbers`.
    """
    stage_numbers(requires)  # kiểm đồ thị trước khi duyệt
    children: dict[str, list[str]] = {code: [] for code in requires}
    for code, needs in requires.items():
        for need in needs:
            children[need].append(code)
    out: dict[str, list[str]] = {}
    for code in requires:
        seen: set[str] = set()
        todo = list(children[code])
        while todo:
            nxt = todo.pop()
            if nxt not in seen:
                seen.add(nxt)
                todo.extend(children[nxt])
        out[code] = sorted(c for c in seen if groups.get(c) in ("core", "common"))
    return out


def apply_have(
    stages: Sequence[PathStage], have: Collection[str]
) -> tuple[list[PathStage], int | None, int, int, list[str]]:
    """Trả `(stages, current_stage, have_on_path, path_size, have_ignored)`.

    `have` là tập mã đã loại trùng hoặc chuỗi có thể trùng; trùng chỉ tính một lần.
    """
    wanted = set(have)
    on_path = {s.skill for st in stages for s in st.skills}
    out = [
        st.model_copy(
            update={"skills": [s.model_copy(update={"have": s.skill in wanted}) for s in st.skills]}
        )
        for st in stages
    ]
    flat = [s for st in out for s in st.skills]
    current = next((st.stage for st in out if not st.is_done()), None)
    return (
        out,
        current,
        sum(1 for s in flat if s.have),
        len(flat),
        sorted(wanted - on_path),
    )
