"""FR-20, FR-22 — đồ thị học trước – học sau và `foundation_for` bắc cầu (#212, đợt 2 của tdd.md).

Hàm thuần ở `haido_api/learning_path.py`: tính chặng từ `requires` và `foundation_for` từ các cạnh bắc cầu. Đồ thị lỗi
(mã không có nút, chu trình) phải ra `PathGraphError` rõ ràng, không `KeyError` hay `RecursionError`.
"""

import copy
from typing import Any

import pytest
from pydantic import ValidationError

from haido_api.learning_path import PathGraphError, foundation_targets, stage_numbers
from haido_api.schemas.learning_path import LearningPathData

CELL = "vn.x"


def test_fr22_chang_la_1_cong_chang_cao_nhat_cua_requires() -> None:
    requires = {"a": [], "b": ["a"], "c": ["a", "b"], "d": []}
    assert stage_numbers(requires) == {"a": 1, "b": 2, "c": 3, "d": 1}


def test_fr22_requires_tro_toi_ma_khong_co_nut_la_loi_ro_rang() -> None:
    with pytest.raises(PathGraphError, match="ghost"):
        stage_numbers({"a": ["ghost"]})


def test_fr22_chu_trinh_la_loi_ro_rang_khong_recursion_error() -> None:
    with pytest.raises(PathGraphError, match="chu trình"):
        stage_numbers({"a": ["b"], "b": ["c"], "c": ["a"]})
    with pytest.raises(PathGraphError, match="chu trình"):
        stage_numbers({"a": ["a"]})


def test_fr22_do_thi_rat_sau_khong_vo_stack() -> None:
    requires = {f"n{i}": ([f"n{i - 1}"] if i else []) for i in range(3000)}
    assert stage_numbers(requires)["n2999"] == 3000


def test_fr20_foundation_for_bac_cau_hai_buoc() -> None:
    """A (nền tảng) -> B (không phải core/common) -> C (core): `foundation_for` của A chứa C, không chứa B."""
    requires = {"a": [], "b": ["a"], "c": ["b"]}
    groups = {"a": "company_specific", "b": "company_specific", "c": "core"}
    targets = foundation_targets(requires, groups)
    assert targets["a"] == ["c"]
    assert targets["b"] == ["c"]
    assert targets["c"] == []


def test_fr20_foundation_for_gom_ca_core_va_common_xep_a_z() -> None:
    requires = {"a": [], "z": ["a"], "m": ["a"], "x": ["m"]}
    groups = {"a": "company_specific", "z": "core", "m": "common", "x": "common"}
    assert foundation_targets(requires, groups)["a"] == ["m", "x", "z"]


def test_fr20_nhom_an_thi_khong_co_foundation_for() -> None:
    requires = {"a": [], "b": ["a"]}
    assert foundation_targets(requires, {"a": None, "b": None}) == {"a": [], "b": []}


def test_fr20_foundation_targets_bao_loi_khi_do_thi_hong() -> None:
    with pytest.raises(PathGraphError):
        foundation_targets({"a": ["ghost"]}, {"a": "core"})


# ---------------------------------------------------------------- validator của schema (F5)


def _stat(value: float | None, cell_id: str = CELL) -> dict[str, Any]:
    return {
        "value": value,
        "kind": "skill_rate",
        "display": "null_data" if value is None else "shown",
        "cell_id": cell_id,
    }


def _skill(
    code: str,
    value: float | None,
    group: str | None,
    *,
    prereq: tuple[str, ...] = (),
    foundation: tuple[str, ...] = (),
) -> dict[str, Any]:
    return {
        "skill": code,
        "rate": _stat(value),
        "group": group,
        "foundation_for": list(foundation),
        "prerequisite_for": list(prereq),
        "have": False,
        "blurb": "Một câu.",
        "resource": {"title": "Tài liệu", "url": "https://example.org/x"},
    }


def _path(*stages: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "role": "backend",
        "level": "entry",
        "status": "ready",
        "cell_id": CELL,
        "entry_cell_id": CELL,
        "stages": [{"stage": i, "skills": s} for i, s in enumerate(stages, start=1)],
        "current_stage": 1,
        "have_on_path": 0,
        "path_size": sum(len(s) for s in stages),
        "have_ignored": [],
    }


def _two_hop() -> dict[str, Any]:
    return _path(
        [
            _skill(
                "linux",
                0.05,
                "company_specific",
                prereq=("docker",),
                foundation=("java",),
            )
        ],
        [
            _skill(
                "docker",
                0.04,
                "company_specific",
                prereq=("java",),
                foundation=("java",),
            )
        ],
        [_skill("java", 0.7, "core")],
    )


def test_fr20_validator_nhan_foundation_for_la_chau_khong_la_con_truc_tiep() -> None:
    parsed = LearningPathData.model_validate(_two_hop())
    assert parsed.stages[0].skills[0].foundation_for == ["java"]
    assert parsed.stages[0].skills[0].prerequisite_for == ["docker"]


def test_fr20_validator_tu_choi_foundation_for_khong_di_toi_duoc_qua_prerequisite_for() -> (
    None
):
    data = _path(
        [
            _skill(
                "linux",
                0.05,
                "company_specific",
                prereq=("docker",),
                foundation=("java",),
            )
        ],
        [_skill("java", 0.7, "core"), _skill("docker", 0.2, "common")],
    )
    with pytest.raises(ValidationError, match="java"):
        LearningPathData.model_validate(data)


def test_fr20_validator_tu_choi_foundation_for_tro_toi_nhom_khong_phai_core_hoac_common() -> (
    None
):
    data = copy.deepcopy(_two_hop())
    data["stages"][2]["skills"][0] = _skill(
        "java", 0.05, "company_specific", foundation=("java",)
    )
    with pytest.raises(ValidationError):
        LearningPathData.model_validate(data)
    data = _path(
        [
            _skill(
                "linux",
                0.05,
                "company_specific",
                prereq=("docker",),
                foundation=("docker",),
            )
        ],
        [
            _skill(
                "docker",
                0.04,
                "company_specific",
                prereq=("java",),
                foundation=("java",),
            )
        ],
        [_skill("java", 0.7, "core")],
    )
    with pytest.raises(ValidationError, match="core hoặc common"):
        LearningPathData.model_validate(data)


def test_fr20_validator_tu_choi_foundation_for_tro_toi_nhom_an() -> None:
    data = _path(
        [
            _skill(
                "linux",
                0.05,
                "company_specific",
                prereq=("docker",),
                foundation=("docker",),
            )
        ],
        [_skill("docker", None, None)],
    )
    with pytest.raises(ValidationError, match="core hoặc common"):
        LearningPathData.model_validate(data)
