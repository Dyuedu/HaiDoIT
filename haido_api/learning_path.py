"""Áp `?have=` lên một lộ trình đã xếp (AD-22): cờ `have`, số đếm, chặng hiện tại, mã bị bỏ qua.

Hàm thuần, dùng chung cho bản giả và bản thật (#216). Không đổi chặng, không đổi thứ tự (chặng là thuộc tính của
nút kỹ năng). Web không làm các phép này.

Cũng ở đây: tính chặng và `foundation_for` từ đồ thị `requires` (mã -> các mã cần học trước). Đồ thị lỗi (mã không có
nút, chu trình) ra `PathGraphError`, không `KeyError` hay `RecursionError`.
"""

from collections.abc import Collection, Mapping, Sequence

from haido_api.schemas.learning_path import PathSkill, PathStage


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
    stages: list[tuple[int, list[PathSkill]]], have: Collection[str]
) -> tuple[list[PathStage], int | None, int, int, list[str]]:
    """Trả `(stages, current_stage, have_on_path, path_size, have_ignored)`.

    `have` là tập mã đã loại trùng hoặc chuỗi có thể trùng; trùng chỉ tính một lần.
    """
    wanted = set(have)
    on_path = {s.skill for _, skills in stages for s in skills}
    out = [
        PathStage(
            stage=number,
            skills=[s.model_copy(update={"have": s.skill in wanted}) for s in skills],
        )
        for number, skills in stages
    ]
    flat = [s for st in out for s in st.skills]
    current = next((st.stage for st in out if any(not s.have for s in st.skills)), None)
    return (
        out,
        current,
        sum(1 for s in flat if s.have),
        len(flat),
        sorted(wanted - on_path),
    )
