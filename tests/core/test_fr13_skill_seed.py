"""#205 — danh sách kỹ năng mồi: định dạng mã, tên song ngữ, bí danh không trùng."""

import re

from haido_core.domain.posting_text import fold
from haido_core.vocab.skills import (
    MAX_PROFILE_SKILLS,
    MAX_SKILL_CODE_LEN,
    SKILL_CODE_PATTERN,
    VOCAB_VERSION,
    is_skill_code,
    load_seed_skills,
    load_vocabulary,
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
    assert 60 <= len(skills) <= 400  # #283: từ vựng quét JD, khoảng 225 mã
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
    # Quy tắc: tên vai trò không được là tên hay bí danh của kỹ năng nào, trừ `it support` (#278): đó là bí danh tra
    # thẻ của `helpdesk` và nằm trong `scan_skip`, nên không bao giờ khớp tên vai trò trong văn bản JD
    # (xem test_fr13_ten_vai_tro_duoc_giu_lam_bi_danh_phai_nam_trong_scan_skip).
    roles = {"tester", "fullstack", "data engineer", "công nghệ thông tin"}
    terms = {
        normalize_term(t) for s in load_seed_skills() for t in (s.name_en, s.name_vi, *s.aliases)
    }
    assert not {normalize_term(r) for r in roles} & terms


def test_fr13_ten_vai_tro_duoc_giu_lam_bi_danh_phai_nam_trong_scan_skip() -> None:
    kept = {"it support"}
    vocab = load_vocabulary()
    assert kept <= set(vocab.lookup)  # còn là bí danh để tra thẻ
    assert not kept & set(vocab.scan_terms)  # nhưng không được quét trong JD
    terms = {fold(t) for s in load_seed_skills() for t in (s.name_en, s.name_vi, *s.aliases)}
    for role in ("tester", "fullstack", "data engineer", "công nghệ thông tin", "it support"):
        if fold(role) in terms:
            assert fold(role) in kept, role


def test_fr13_chuan_hoa_tu_tim() -> None:
    assert normalize_term("  Học   Máy ") == "học máy"
    assert re.fullmatch(r"\S+( \S+)*", normalize_term("Node.js"))
