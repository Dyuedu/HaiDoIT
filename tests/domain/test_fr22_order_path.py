"""FR-22: phép 8 `order_path`, luật bốn tầng và tính tất định (#139)."""

import math
import os
import random
import subprocess
import sys
from pathlib import Path

import pytest

from haido_core.domain.path_order import PathOrderer, PathOrderError
from haido_core.domain.registry import GraphEdge, PathRequest, PathSkill, SkillBand

ROOT = Path(__file__).resolve().parents[2]
C, M, R = SkillBand.CORE, SkillBand.COMMON, SkillBand.RARE

# (mã, chặng, nhóm, tỷ lệ). Có hòa chặng, nhóm, tỷ lệ để tầng 4 quyết định.
SKILLS = (
    ("git", 1, C, 0.90),
    ("linux", 1, C, 0.90),
    ("python", 1, C, 0.95),
    ("sql", 1, M, 0.70),
    ("http", 2, C, 0.80),
    ("rest", 2, C, 0.80),
    ("ci", 2, M, 0.85),
    ("docker", 2, M, 0.85),
    ("postgres", 3, C, 0.75),
    ("kubernetes", 3, R, 0.20),
    ("helm", 1, R, 0.10),  # chặng khai báo 1 nhưng cạnh kubernetes -> helm bắt nó đứng sau
    ("unused", 1, C, 0.99),
)
EDGES = (
    ("git", "ci"),
    ("linux", "docker"),
    ("docker", "kubernetes"),
    ("ci", "kubernetes"),
    ("sql", "postgres"),
    ("python", "http"),
    ("http", "rest"),
    ("kubernetes", "helm"),
)
GAPS = ("kubernetes", "postgres", "rest", "helm")
EXPECTED = ("python", "git", "linux", "sql", "http", "rest", "ci", "docker", "postgres", "kubernetes", "helm")


def req(gaps=GAPS, edges=EDGES, skills=SKILLS) -> PathRequest:
    return PathRequest(
        gaps=tuple(gaps),
        edges=tuple(GraphEdge(a, b) for a, b in edges),
        skills=tuple(PathSkill(s, st, b, r) for s, st, b, r in skills),
    )


def simple(skills, edges=(), gaps=None) -> tuple[str, ...]:
    gaps = gaps if gaps is not None else [s[0] for s in skills]
    return PathOrderer().order_path(req(gaps, edges, skills))


def test_fr22_order_path_fixture_matches_hand_computed_order() -> None:
    assert PathOrderer().order_path(req()) == EXPECTED


def test_fr22_order_path_ignores_input_order_of_gaps_edges_and_skills() -> None:
    for seed in range(25):
        rng = random.Random(seed)
        gaps, edges, skills = list(GAPS), list(EDGES), list(SKILLS)
        rng.shuffle(gaps)
        rng.shuffle(edges)
        rng.shuffle(skills)
        assert PathOrderer().order_path(req(gaps, edges, skills)) == EXPECTED
    assert PathOrderer().order_path(req(GAPS[::-1], EDGES[::-1], SKILLS[::-1])) == EXPECTED


def test_fr22_order_path_pulls_in_transitive_ancestors_only() -> None:
    assert PathOrderer().order_path(req(gaps=("rest",))) == ("python", "http", "rest")
    assert "unused" not in PathOrderer().order_path(req())


def test_fr22_order_path_gap_without_ancestors_and_empty_gaps() -> None:
    assert PathOrderer().order_path(req(gaps=("git",))) == ("git",)
    assert PathOrderer().order_path(req(gaps=())) == ()


def test_fr22_order_path_duplicate_gaps_change_nothing() -> None:
    assert PathOrderer().order_path(req(gaps=GAPS + GAPS)) == EXPECTED


def test_fr22_order_path_edge_beats_declared_stage() -> None:
    assert simple([("a", 3, C, 0.9), ("b", 1, C, 0.9)], edges=[("a", "b")]) == ("a", "b")


def test_fr22_order_path_tier1_stage_first() -> None:
    assert simple([("a", 2, C, 0.99), ("b", 1, R, 0.01)]) == ("b", "a")


def test_fr22_order_path_tier2_band_core_common_rare() -> None:
    assert simple([("r", 1, R, 0.99), ("m", 1, M, 0.50), ("c", 1, C, 0.10)]) == ("c", "m", "r")


def test_fr22_order_path_tier3_higher_rate_first() -> None:
    assert simple([("a", 1, C, 0.10), ("b", 1, C, 0.60), ("c", 1, C, 0.30)]) == ("b", "c", "a")


def test_fr22_order_path_tier4_skill_id_breaks_full_tie() -> None:
    assert simple([("b", 1, C, 0.5), ("c", 1, C, 0.5), ("a", 1, C, 0.5)]) == ("a", "b", "c")


def test_fr22_order_path_cycle_outside_the_pulled_in_set_is_ignored() -> None:
    skills = [("a", 1, C, 0.5), ("x", 1, C, 0.5), ("y", 1, C, 0.5)]
    assert simple(skills, edges=[("x", "y"), ("y", "x")], gaps=["a"]) == ("a",)


def test_fr22_order_path_single_request_returns_tuple_of_ids() -> None:
    result = PathOrderer().order_path(req())
    assert isinstance(result, tuple)
    assert all(isinstance(x, str) for x in result)


def test_fr22_order_path_batch_returns_tuple_of_tuples_same_length() -> None:
    other = req(gaps=("rest",))
    for batch in ([req(), other], (req(), other)):
        result = PathOrderer().order_path(batch)
        assert result == (EXPECTED, ("python", "http", "rest"))
        assert isinstance(result, tuple)
    assert PathOrderer().order_path([]) == ()


def test_fr22_order_path_does_not_mutate_the_request() -> None:
    request = req()
    before = (request.gaps, request.edges, request.skills)
    PathOrderer().order_path(request)
    assert (request.gaps, request.edges, request.skills) == before


def _one(skills, gaps=("a",), edges=()) -> PathRequest:
    return req(gaps=gaps, edges=edges, skills=skills)


@pytest.mark.parametrize(
    ("request_", "fragment"),
    [
        (req(gaps=("nope",)), "nope"),
        (req(edges=EDGES + (("ghost", "git"),)), "ghost"),
        (req(edges=EDGES + (("git", "ghost"),)), "ghost"),
        (req(skills=SKILLS + (("git", 1, C, 0.5),)), "git"),
        (req(edges=EDGES + (("helm", "git"),)), "vòng"),
        (req(edges=EDGES + (("git", "git"),)), "vòng"),
        (_one((("a", 1, C, math.nan),)), "rate"),
        (_one((("a", 1, C, math.inf),)), "rate"),
        (_one((("a", 1, C, -0.1),)), "rate"),
        (_one((("a", 1, C, 1.1),)), "rate"),
        (_one((("a", 0, C, 0.5),)), "stage"),
        (_one((("a", -3, C, 0.5),)), "stage"),
        (_one((("a", 1, "core", 0.5),)), "band"),
    ],
)
def test_fr22_order_path_rejects_bad_input_with_a_clear_error(request_: PathRequest, fragment: str) -> None:
    with pytest.raises(PathOrderError, match=fragment):
        PathOrderer().order_path(request_)


def _raw(gaps=("a",), edges=(), skills=(("a", 1, C, 0.5),)) -> PathRequest:
    """Dựng PathRequest bằng tay, cho phép nhét kiểu sai vào các trường (dataclass không kiểm kiểu)."""
    return PathRequest(gaps=gaps, edges=edges, skills=tuple(PathSkill(*s) for s in skills))  # type: ignore[arg-type]


def _skill_with(**fields) -> PathRequest:
    base = {"skill_id": "a", "stage": 1, "band": C, "rate": 0.5}
    base.update(fields)
    return PathRequest(gaps=("a",), edges=(), skills=(PathSkill(**base),))  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("request_", "fragment"),
    [
        (_skill_with(stage=True), "stage"),
        (_skill_with(rate=True), "rate"),
        (_skill_with(rate=10**400), "rate"),
        (_skill_with(rate="0.5"), "rate"),
        (_skill_with(skill_id=None), "skill_id"),
        (_skill_with(skill_id=1), "skill_id"),
        (_skill_with(skill_id=[]), "skill_id"),
        (_raw(gaps="a"), "gaps"),
        (_raw(gaps=None), "gaps"),
        (_raw(gaps=([],)), "gaps"),
        (_raw(gaps=(1,)), "gaps"),
        (_raw(edges="ab"), "edges"),
        (_raw(edges=None), "edges"),
        (_raw(edges=(("a", "a"),)), "edges"),
        (_raw(edges=(GraphEdge([], "a"),)), "Cạnh"),
        (_raw(edges=(GraphEdge("a", None),)), "Cạnh"),
        (PathRequest(gaps=("a",), edges=(), skills="a"), "skills"),  # type: ignore[arg-type]
        (PathRequest(gaps=("a",), edges=(), skills=None), "skills"),  # type: ignore[arg-type]
        (PathRequest(gaps=("a",), edges=(), skills=("a",)), "skills"),  # type: ignore[arg-type]
        (None, "PathRequest"),
        ("git", "PathRequest"),
    ],
)
def test_fr22_order_path_wraps_wrong_types_into_path_order_error(request_: object, fragment: str) -> None:
    with pytest.raises(PathOrderError, match=fragment):
        PathOrderer().order_path(request_)  # type: ignore[arg-type]


def test_fr22_order_path_batch_item_that_is_not_a_request_raises() -> None:
    with pytest.raises(PathOrderError, match="PathRequest"):
        PathOrderer().order_path([req(), None])  # type: ignore[list-item]


def test_fr22_order_path_negative_zero_rate_is_valid_and_ties_with_zero() -> None:
    skills = [("b", 1, C, -0.0), ("a", 1, C, 0.0), ("c", 1, C, -0.0)]
    assert simple(skills) == ("a", "b", "c")
    assert simple(skills[::-1]) == ("a", "b", "c")


def test_fr22_order_path_duplicate_edges_change_nothing() -> None:
    assert PathOrderer().order_path(req(edges=EDGES + EDGES)) == EXPECTED


def test_fr22_order_path_error_is_a_value_error() -> None:
    assert issubclass(PathOrderError, ValueError)


def test_fr22_order_path_one_bad_request_in_a_batch_raises() -> None:
    with pytest.raises(PathOrderError):
        PathOrderer().order_path([req(), req(gaps=("nope",))])


@pytest.mark.determinism
def test_fr22_order_path_same_result_under_different_hash_seeds() -> None:
    code = (
        "import sys; sys.path.insert(0, sys.argv[1]); "
        "from tests.domain.test_fr22_order_path import req; "
        "from haido_core.domain.path_order import PathOrderer; "
        "print(PathOrderer().order_path(req()))"
    )
    outputs = []
    for seed in ("0", "1", "2"):
        env = {**os.environ, "PYTHONHASHSEED": seed, "PYTHONDONTWRITEBYTECODE": "1"}
        done = subprocess.run(
            [sys.executable, "-c", code, str(ROOT)], capture_output=True, text=True, env=env, cwd=ROOT, check=True
        )
        outputs.append(done.stdout)
    assert outputs[0] == outputs[1] == outputs[2]
    assert str(EXPECTED) in outputs[0]
