"""#205 — danh sách kỹ năng mồi: định dạng mã, tên song ngữ, bí danh không trùng."""

import re

from haido_core.vocab.skills import (
    MAX_PROFILE_SKILLS,
    MAX_SKILL_CODE_LEN,
    SKILL_CODE_PATTERN,
    VOCAB_VERSION,
    is_skill_code,
    load_seed_skills,
    normalize_term,
)


def test_fr13_dinh_dang_ma_ky_nang() -> None:
    assert SKILL_CODE_PATTERN == r"^[a-z0-9]+(_[a-z0-9]+)*$"
    assert MAX_SKILL_CODE_LEN == 40
    assert MAX_PROFILE_SKILLS == 200
    for good in ("python", "cpp", "ci_cd", "dotnet", "machine_learning", "s3"):
        assert is_skill_code(good), good
    for bad in ("", "Python", "c++", "ci/cd", "_sql", "sql_", "a__b", "node.js", "x" * 41, "a,b"):
        assert not is_skill_code(bad), bad


def test_fr13_danh_sach_moi_du_va_ma_hop_le() -> None:
    skills = load_seed_skills()
    assert 60 <= len(skills) <= 150
    codes = [s.code for s in skills]
    assert len(codes) == len(set(codes))
    assert all(is_skill_code(c) for c in codes)
    assert codes == sorted(codes)
    assert VOCAB_VERSION.startswith("seed-")


def test_fr13_moi_ky_nang_co_ten_anh_viet_va_nguon() -> None:
    for skill in load_seed_skills():
        assert skill.name_en.strip(), skill.code
        assert skill.name_vi.strip(), skill.code
        assert skill.source.strip(), skill.code


def test_fr13_bi_danh_khong_tro_toi_hai_ma() -> None:
    owner: dict[str, str] = {}
    for skill in load_seed_skills():
        for term in (skill.name_en, skill.name_vi, *skill.aliases):
            key = normalize_term(term)
            assert key, skill.code
            assert owner.setdefault(key, skill.code) == skill.code, (
                f"{term!r} thuộc cả {owner[key]} và {skill.code}"
            )


def test_fr13_tim_hoc_may_ra_machine_learning() -> None:
    by_term = {
        normalize_term(t): s.code
        for s in load_seed_skills()
        for t in (s.name_en, s.name_vi, *s.aliases)
    }
    assert by_term[normalize_term("học máy")] == "machine_learning"
    assert by_term[normalize_term("Machine Learning")] == "machine_learning"
    assert by_term[normalize_term("C#")] == "csharp"
    assert by_term[normalize_term("ReactJS")] == "react"


def test_fr13_khong_co_ten_vai_tro_trong_danh_sach() -> None:
    roles = {"tester", "it support", "fullstack", "data engineer", "công nghệ thông tin"}
    terms = {
        normalize_term(t) for s in load_seed_skills() for t in (s.name_en, s.name_vi, *s.aliases)
    }
    assert not {normalize_term(r) for r in roles} & terms


def test_fr13_chuan_hoa_tu_tim() -> None:
    assert normalize_term("  Học   Máy ") == "học máy"
    assert re.fullmatch(r"\S+( \S+)*", normalize_term("Node.js"))
