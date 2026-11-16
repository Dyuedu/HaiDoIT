"""Phép 8: xếp thứ tự lộ trình học, quy tắc bốn tầng của FR-22 (#139, AD-2).

Đầu vào là các khoảng trống, đồ thị tiên quyết và các nút kỹ năng. Kết quả là mã kỹ năng theo thứ
tự học: khoảng trống cộng mọi tổ tiên bắc cầu của chúng (cạnh `before` -> `after`).

Thứ tự là sắp xếp topo theo Kahn, mỗi lần lấy nút sẵn sàng có khóa nhỏ nhất:

1. chặng, nhỏ trước;
2. nhóm: cốt lõi, thường gặp, hiếm;
3. tỷ lệ xuất hiện, lớn trước;
4. mã kỹ năng, A-Z.

Cạnh luôn thắng chặng: nút chỉ vào hàng đợi khi mọi tiên quyết đã ra, kể cả khi chặng khai báo
mâu thuẫn với cạnh. Mã kỹ năng là duy nhất nên khóa là một thứ tự toàn phần; kết quả không phụ thuộc
thứ tự các tuple đầu vào, thứ tự duyệt `set` hay `PYTHONHASHSEED`.

Vòng chỉ bị từ chối khi nằm trong tập được kéo vào (khoảng trống và tổ tiên). Vòng ở phần đồ thị
không ảnh hưởng đầu ra thì bỏ qua.

Module chỉ import thư viện chuẩn và registry.
"""

import heapq

from haido_core.domain.registry import (
    GraphEdge,
    OneOrMany,
    PathRequest,
    PathSkill,
    SkillBand,
    as_batch,
)

_BAND_RANK = {SkillBand.CORE: 0, SkillBand.COMMON: 1, SkillBand.RARE: 2}

type _Key = tuple[int, int, float, str]


class PathOrderError(ValueError):
    """Đầu vào của `order_path` sai: mã lạ, mã lặp, vòng, tỷ lệ hoặc chặng ngoài miền."""


def _key(skill: PathSkill) -> _Key:
    return (skill.stage, _BAND_RANK[skill.band], -skill.rate, skill.skill_id)


def _items(name: str, value: object, kind: type) -> tuple:
    """`value` phải là `tuple` hoặc `list` (không phải `str`) và mỗi phần tử đúng kiểu `kind`."""
    if not isinstance(value, tuple | list):
        raise PathOrderError(f"{name} phải là tuple hoặc list, nhận {type(value).__name__}.")
    for item in value:
        if not isinstance(item, kind):
            raise PathOrderError(f"{name} có phần tử không phải {kind.__name__}: {item!r}.")
    return tuple(value)


def _index_skills(skills: object) -> dict[str, PathSkill]:
    by_id: dict[str, PathSkill] = {}
    for skill in _items("skills", skills, PathSkill):
        if not isinstance(skill.skill_id, str):
            raise PathOrderError(f"skill_id phải là str, nhận {skill.skill_id!r}.")
        if skill.skill_id in by_id:
            raise PathOrderError(f"Mã kỹ năng lặp: {skill.skill_id!r}.")
        if not isinstance(skill.band, SkillBand):
            raise PathOrderError(f"band của {skill.skill_id!r} không phải SkillBand: {skill.band!r}.")
        if isinstance(skill.stage, bool) or not isinstance(skill.stage, int) or skill.stage < 1:
            raise PathOrderError(f"stage của {skill.skill_id!r} phải là số nguyên từ 1, nhận {skill.stage!r}.")
        rate = skill.rate
        # Kiểm miền trước `isfinite`: số nguyên rất lớn làm `isfinite` ném OverflowError.
        if isinstance(rate, bool) or not isinstance(rate, int | float) or not (0 <= rate <= 1):
            raise PathOrderError(f"rate của {skill.skill_id!r} phải nằm trong [0, 1], nhận {rate!r}.")
        by_id[skill.skill_id] = skill
    return by_id


def _one(request: PathRequest) -> tuple[str, ...]:
    if not isinstance(request, PathRequest):
        raise PathOrderError(f"Yêu cầu phải là PathRequest, nhận {type(request).__name__}.")
    skills = _index_skills(request.skills)
    gaps = _items("gaps", request.gaps, str)
    edges = _items("edges", request.edges, GraphEdge)
    for gap in gaps:
        if gap not in skills:
            raise PathOrderError(f"Khoảng trống {gap!r} không có trong skills.")
    before_of: dict[str, set[str]] = {}
    for edge in edges:
        for end in (edge.before, edge.after):
            if not isinstance(end, str) or end not in skills:
                raise PathOrderError(f"Cạnh {edge.before!r} -> {edge.after!r} nhắc mã {end!r} không có trong skills.")
        before_of.setdefault(edge.after, set()).add(edge.before)

    # Kéo tổ tiên bắc cầu vào. Kết quả là tập, không phụ thuộc thứ tự duyệt.
    selected: set[str] = set()
    stack = sorted(set(gaps))
    while stack:
        node = stack.pop()
        if node in selected:
            continue
        selected.add(node)
        stack.extend(before_of.get(node, ()))

    waiting = {node: len(before_of.get(node, ())) for node in selected}
    after_of: dict[str, list[str]] = {node: [] for node in selected}
    for node in selected:
        for parent in before_of.get(node, ()):
            after_of[parent].append(node)

    heap = [(_key(skills[node]), node) for node, count in waiting.items() if count == 0]
    heapq.heapify(heap)
    ordered: list[str] = []
    while heap:
        _, node = heapq.heappop(heap)
        ordered.append(node)
        for child in after_of[node]:
            waiting[child] -= 1
            if waiting[child] == 0:
                heapq.heappush(heap, (_key(skills[child]), child))

    if len(ordered) != len(selected):
        stuck = ", ".join(sorted(selected - set(ordered)))
        raise PathOrderError(f"Đồ thị tiên quyết có vòng giữa các kỹ năng: {stuck}.")
    return tuple(ordered)


class PathOrderer:
    """Thân hàm duy nhất của phép 8."""

    def order_path(self, requests: OneOrMany[PathRequest]) -> OneOrMany[tuple[str, ...]]:
        batch = as_batch(requests)
        if batch is None:
            return _one(requests)
        return tuple(_one(item) for item in batch)

