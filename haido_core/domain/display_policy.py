"""Quy tắc ẩn số liệu khi mẫu nhỏ — bản cài đặt duy nhất (AD-17, DoD dòng 3).

Mọi quyết định "con số này có được hiện không" đi qua `suppression_for`. Không nơi nào
khác so `n` với ngưỡng. Ngưỡng là tham số có phiên bản (AD-10), nên hàm nhận nó qua
`min_sample` thay vì tự đọc hay viết cứng.

Module này chỉ import thư viện chuẩn.
"""

from enum import StrEnum


class MeasureKind(StrEnum):
    """Loại thước đo của một con số."""

    COMPOSITION_SHARE = "composition_share"
    """Tỷ trọng cấu phần, ví dụ tỷ trọng một thành phố trong số tin của một vai trò (FR-33)."""

    SKILL_RATE = "skill_rate"
    """Tỷ lệ xuất hiện của một kỹ năng trong ô thống kê."""

    PERCENTILE = "percentile"
    """Phân vị: lương, số kỹ năng yêu cầu, số năm kinh nghiệm (FR-30)."""

    LEVEL_SHARE = "level_share"
    """Tỷ lệ tin của một nhóm cấp bậc trong số tin của vai trò, ví dụ tỷ lệ tin entry-level (#144)."""


class DisplayState(StrEnum):
    """Trạng thái hiển thị của một con số, do `suppression_for` quyết."""

    SHOWN = "shown"
    """Đủ mẫu, hiện bình thường."""

    LOW_SAMPLE_SHOWN = "low_sample_shown"
    """Dưới ngưỡng nhưng vẫn hiện, ở trạng thái mờ kèm nhãn cỡ mẫu nhỏ. Chỉ tỷ trọng cấu phần."""

    NULL_DATA = "null_data"
    """Dưới ngưỡng: không có giá trị, giao diện ghi "chưa đủ dữ liệu"."""


def suppression_for(measure_kind: MeasureKind, n: int, *, min_sample: int) -> DisplayState:
    """Quyết trạng thái hiển thị của một con số tính trên `n` tin.

    `n` là cỡ mẫu của chính thước đo đó (`n_with_value`), không phải `n` của ô khi hai
    số khác nhau (AD-17). `n >= min_sample` thì hiện. Dưới ngưỡng, chỉ tỷ trọng cấu phần
    được `low_sample_shown`; mọi loại khác luôn `null_data`. `n = 0` xử lý như
    mọi `n` dưới ngưỡng.

    Raises:
        ValueError: `n` âm, `min_sample` nhỏ hơn 1, hoặc `measure_kind` không phải một
            loại thước đo đã khai.
    """
    kind = MeasureKind(measure_kind)
    if n < 0:
        raise ValueError(f"Cỡ mẫu n không được âm, nhận {n}.")
    if min_sample < 1:
        raise ValueError(f"Ngưỡng mẫu min_sample phải từ 1 trở lên, nhận {min_sample}.")
    if n >= min_sample:
        return DisplayState.SHOWN
    if kind is MeasureKind.COMPOSITION_SHARE:
        return DisplayState.LOW_SAMPLE_SHOWN
    return DisplayState.NULL_DATA
