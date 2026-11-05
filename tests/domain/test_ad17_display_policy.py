"""AD-17 — `suppression_for` là chỗ duy nhất quyết số liệu nào được hiện. Dòng "Biên ngưỡng" của I/O Matrix."""

import pytest

from haido_core.domain.display_policy import DisplayState, MeasureKind, suppression_for

MIN_SAMPLE = 30

DUOI_NGUONG = {
    MeasureKind.COMPOSITION_SHARE: DisplayState.LOW_SAMPLE_SHOWN,
    MeasureKind.SKILL_RATE: DisplayState.NULL_DATA,
    MeasureKind.PERCENTILE: DisplayState.NULL_DATA,
}


@pytest.mark.parametrize("kind", list(MeasureKind))
def test_ad17_dung_nguong_thi_hien(kind: MeasureKind) -> None:
    assert suppression_for(kind, 30, min_sample=MIN_SAMPLE) is DisplayState.SHOWN


@pytest.mark.parametrize("n", [29, 0])
@pytest.mark.parametrize("kind", list(MeasureKind))
def test_ad17_duoi_nguong_chi_ty_trong_duoc_hien_mo(kind: MeasureKind, n: int) -> None:
    assert suppression_for(kind, n, min_sample=MIN_SAMPLE) is DUOI_NGUONG[kind]


def test_ad17_n_bang_0_xu_ly_nhu_n_bang_29() -> None:
    for kind in MeasureKind:
        assert suppression_for(kind, 0, min_sample=MIN_SAMPLE) is suppression_for(
            kind, 29, min_sample=MIN_SAMPLE
        )


def test_ad17_n_am_la_loi() -> None:
    with pytest.raises(ValueError, match="không được âm"):
        suppression_for(MeasureKind.SKILL_RATE, -1, min_sample=MIN_SAMPLE)


@pytest.mark.parametrize("min_sample", [0, -5])
def test_ad17_nguong_nho_hon_1_la_loi(min_sample: int) -> None:
    with pytest.raises(ValueError, match="min_sample"):
        suppression_for(MeasureKind.SKILL_RATE, 10, min_sample=min_sample)


def test_ad17_nguong_la_tham_so_khong_viet_cung() -> None:
    assert suppression_for(MeasureKind.SKILL_RATE, 30, min_sample=50) is DisplayState.NULL_DATA
    assert suppression_for(MeasureKind.SKILL_RATE, 12, min_sample=10) is DisplayState.SHOWN


def test_ad17_nhan_ma_chuoi_cua_thuoc_do() -> None:
    assert suppression_for("composition_share", 3, min_sample=MIN_SAMPLE) is (  # type: ignore[arg-type]
        DisplayState.LOW_SAMPLE_SHOWN
    )
    with pytest.raises(ValueError):
        suppression_for("khong_co", 3, min_sample=MIN_SAMPLE)  # type: ignore[arg-type]
