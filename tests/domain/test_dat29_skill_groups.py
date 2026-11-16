"""#101 (DAT.29), phép 4 `group_skills`: nhóm kỹ năng theo θ truyền vào từng lần gọi (FR-9, AD-2)."""

import pytest

from haido_core.domain.registry import (
    SkillBand,
    SkillGroup,
    SkillGroupRequest,
    SkillRate,
)
from haido_core.domain.skill_groups import SkillGrouper

CORE, COMMON = 0.3, 0.1
group_skills = SkillGrouper().group_skills


def _request(*rates: tuple[str, float], core: float = CORE, common: float = COMMON) -> SkillGroupRequest:
    return SkillGroupRequest(tuple(SkillRate(s, r) for s, r in rates), core, common)


def test_dat29_fr9_dung_theta_la_core_va_common_duoi_common_la_rare() -> None:
    result = group_skills(_request(("a", 0.3), ("b", 0.2999), ("c", 0.1), ("d", 0.0999), ("e", 0.0)))
    assert result == (
        SkillGroup("a", SkillBand.CORE),
        SkillGroup("b", SkillBand.COMMON),
        SkillGroup("c", SkillBand.COMMON),
        SkillGroup("d", SkillBand.RARE),
        SkillGroup("e", SkillBand.RARE),
    )


def test_dat29_fr9_ty_le_0_va_1_van_la_mot_phan_tu() -> None:
    result = group_skills(_request(("x", 1.0), ("y", 0.0)))
    assert [(g.skill_id, g.band) for g in result] == [("x", SkillBand.CORE), ("y", SkillBand.RARE)]


def test_dat29_fr9_dau_vao_rong_ra_tuple_rong() -> None:
    assert group_skills(_request()) == ()


def test_dat29_fr9_theta_di_theo_tung_lan_goi_doi_theta_doi_nhom() -> None:
    rates = (("a", 0.25),)
    assert group_skills(_request(*rates))[0].band is SkillBand.COMMON
    assert group_skills(_request(*rates, core=0.2, common=0.05))[0].band is SkillBand.CORE
    assert group_skills(_request(*rates, core=0.9, common=0.5))[0].band is SkillBand.RARE


def test_dat29_ad2_mot_yeu_cau_tra_mot_tuple_mot_lo_tra_tuple_cung_do_dai() -> None:
    one = _request(("a", 0.5))
    other = _request(("a", 0.5), ("b", 0.05), core=0.4, common=0.2)
    single = group_skills(one)
    batch = group_skills([one, other])
    assert isinstance(single, tuple) and all(isinstance(g, SkillGroup) for g in single)
    assert isinstance(batch, tuple) and len(batch) == 2
    assert batch[0] == single
    assert batch[1] == group_skills(other)
    assert group_skills([]) == ()
    assert group_skills((one,)) == (single,)


def test_dat29_ad2_giu_thu_tu_dau_vao() -> None:
    request = _request(("z", 0.5), ("a", 0.5), ("m", 0.0))
    assert [g.skill_id for g in group_skills(request)] == ["z", "a", "m"]


@pytest.mark.parametrize("bad", [-0.01, 1.01, float("nan")])
def test_dat29_fr9_ty_le_ngoai_0_den_1_la_loi_khong_doan(bad: float) -> None:
    with pytest.raises(ValueError, match="Tỷ lệ"):
        group_skills(_request(("a", bad)))


def test_dat29_fr9_theta_common_lon_hon_theta_core_la_loi() -> None:
    with pytest.raises(ValueError, match="theta_common"):
        group_skills(_request(("a", 0.5), core=0.1, common=0.3))


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf"), -0.01, 1.01])
@pytest.mark.parametrize("which", ["core", "common"])
def test_dat29_fr9_theta_khong_huu_han_hoac_ngoai_0_den_1_la_loi(which: str, bad: float) -> None:
    kwargs = {"core": 0.3, "common": 0.1} | {which: bad}
    with pytest.raises(ValueError, match="theta_"):
        group_skills(_request(("a", 0.5), **kwargs))


@pytest.mark.parametrize("bad", [float("inf"), float("-inf")])
def test_dat29_fr9_ty_le_vo_han_la_loi(bad: float) -> None:
    with pytest.raises(ValueError, match="Tỷ lệ"):
        group_skills(_request(("a", bad)))


def test_dat29_fr9_theta_o_hai_dau_khoang_la_hop_le() -> None:
    assert group_skills(_request(("a", 1.0), ("b", 0.0), core=1.0, common=0.0)) == (
        SkillGroup("a", SkillBand.CORE),
        SkillGroup("b", SkillBand.COMMON),
    )
    assert group_skills(_request(("a", 0.0), core=0.0, common=0.0))[0].band is SkillBand.CORE


def test_dat29_fr9_skill_id_trung_trong_mot_yeu_cau_la_loi_nhung_khac_yeu_cau_thi_duoc() -> None:
    with pytest.raises(ValueError, match="trùng"):
        group_skills(_request(("a", 0.5), ("b", 0.2), ("a", 0.1)))
    first, second = group_skills([_request(("a", 0.5)), _request(("a", 0.1))])
    assert first[0].band is SkillBand.CORE and second[0].band is SkillBand.COMMON
