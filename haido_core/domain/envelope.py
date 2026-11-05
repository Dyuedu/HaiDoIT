"""Envelope `{data, meta}` dùng chung cho mọi response chứa số (AD-17).

Validator ở đây là một phần của quy tắc ẩn số liệu khi mẫu nhỏ, nên nằm cạnh `display_policy`.
Module chỉ import thư viện chuẩn, `pydantic` và `display_policy`; không biết gì về tầng HTTP.
Hình `data` của từng route nằm ở `haido_api/schemas/`.

Ba quy tắc của hợp đồng:

- mọi con số trong `data` là một `Stat`, không có số nào đứng riêng ngoài `Stat`;
- `Stat.display` khớp với `value` và `kind` (`null_data` thì không có giá trị; chỉ tỷ trọng
  cấu phần được `low_sample_shown`), và với `suppression_for` trên `n` của ô;
- mọi `cell_id` trong `data` có mục tương ứng trong `meta.cells`.
"""

import numbers
from collections.abc import Iterator, Mapping
from datetime import date
from enum import StrEnum
from typing import Annotated, Self, get_args

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    NonNegativeInt,
    PositiveInt,
    model_validator,
)

from haido_core.domain.display_policy import DisplayState, MeasureKind, suppression_for


class CellRef:
    """Dấu đặt trong `Annotated[...]`: trường mang một `cell_id` phải có trong `meta.cells`.

    Dùng qua bí danh `CellId`. Route nào có trường trỏ tới một ô ngoài `Stat.cell_id`
    (ví dụ ô toàn quốc làm mẫu số) thì khai trường đó là `CellId` để `Envelope` kiểm.
    """

    __slots__ = ()

    def __repr__(self) -> str:
        return "CellRef()"


CellId = Annotated[str, CellRef(), Field(min_length=1)]
"""Mã ô thống kê. Chuỗi opaque: giao diện chỉ dùng nó để tra `meta.cells`."""

Fraction = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]

# revalidate_instances: một instance sửa bằng `model_copy(update=...)` vẫn qua validator khi
# lồng vào model khác hoặc khi FastAPI kiểm response.
_CONFIG = ConfigDict(extra="forbid", use_attribute_docstrings=True, revalidate_instances="always")
_RATIO_KINDS = frozenset({MeasureKind.COMPOSITION_SHARE, MeasureKind.SKILL_RATE})


class Stat(BaseModel):
    """Một con số kèm trạng thái hiển thị và ô đã sinh ra nó."""

    model_config = _CONFIG

    value: Annotated[float, Field(allow_inf_nan=False)] | None
    """Giá trị chưa làm tròn. Tỷ lệ và tỷ trọng là số thực 0–1. `null` khi `display = null_data`."""

    kind: MeasureKind
    """Loại thước đo."""

    display: DisplayState
    """Trạng thái hiển thị, do `suppression_for` quyết. Giao diện chỉ đọc, không tự suy."""

    cell_id: CellId
    """Ô đã sinh ra con số; tra cỡ mẫu và nhãn ở `meta.cells[cell_id]`."""

    @model_validator(mode="after")
    def _luat_hien_thi(self) -> Self:
        if self.display is DisplayState.NULL_DATA:
            if self.value is not None:
                raise ValueError("display = null_data thì value phải là null.")
        elif self.value is None:
            raise ValueError(f"display = {self.display} thì value phải có giá trị.")
        if (
            self.display is DisplayState.LOW_SAMPLE_SHOWN
            and self.kind is not MeasureKind.COMPOSITION_SHARE
        ):
            raise ValueError(
                f"Chỉ composition_share được low_sample_shown, nhận kind = {self.kind}."
            )
        if self.value is not None and self.kind in _RATIO_KINDS and not 0 <= self.value <= 1:
            raise ValueError(f"{self.kind} phải nằm trong 0–1, nhận {self.value}.")
        return self


class CellMeta(BaseModel):
    """Mục của một ô thống kê mà response dùng."""

    model_config = _CONFIG

    n: NonNegativeInt
    """Số tin (đếm theo cụm) của ô."""

    fallback_label: str | None
    """Nhãn giải thích khi ô này được dùng thay cho ô người dùng chọn; `null` nếu không quay về."""

    seniority_mix: dict[str, NonNegativeInt]
    """Số tin theo cấp bậc chi tiết, ví dụ `{"intern": 13, "fresher": 7, "junior": 32}`."""

    n_by_measure: dict[str, NonNegativeInt]
    """Số tin có giá trị của từng thước đo (`n_with_value`): số kỹ năng, số năm kinh nghiệm, lương."""

    insufficient_by_measure: dict[str, bool]
    """`true` khi thước đo đó dưới ngưỡng mẫu. Cùng tập khóa với `n_by_measure`."""

    @model_validator(mode="after")
    def _khop_thuoc_do(self) -> Self:
        if set(self.n_by_measure) != set(self.insufficient_by_measure):
            raise ValueError(
                "n_by_measure và insufficient_by_measure phải có cùng tập thước đo, nhận "
                f"{sorted(self.n_by_measure)} và {sorted(self.insufficient_by_measure)}."
            )
        vuot = sorted(m for m, n in self.n_by_measure.items() if n > self.n)
        if vuot:
            raise ValueError(f"n_by_measure vượt n của ô ({self.n}) ở: {', '.join(vuot)}.")
        return self


class Thresholds(BaseModel):
    """Các ngưỡng đã dùng cho response, lấy từ cấu hình có phiên bản (AD-10)."""

    model_config = _CONFIG

    min_sample: PositiveInt
    """Ngưỡng mẫu: ô có ít tin hơn mức này thì `suppression_for` ẩn số liệu (riêng tỷ trọng thì hiện mờ)."""

    theta_core: Fraction
    """Ngưỡng tỷ lệ của nhóm cốt lõi."""

    theta_common: Fraction
    """Ngưỡng tỷ lệ của nhóm thường gặp."""

    @model_validator(mode="after")
    def _thu_tu_theta(self) -> Self:
        if self.theta_common > self.theta_core:
            raise ValueError("theta_common không được lớn hơn theta_core.")
        return self


class CoverageNote(BaseModel):
    """Một lưu ý về độ phủ dữ liệu (ba lưu ý chuẩn của FR-36 và lưu ý số nguồn của §5)."""

    model_config = _CONFIG

    code: Annotated[str, Field(min_length=1)]
    """Mã ổn định của lưu ý, snake_case."""

    text: Annotated[str, Field(min_length=1)]
    """Câu hiển thị, tiếng Việt."""


class SnapshotStatus(StrEnum):
    """Trạng thái kết thúc của snapshot (AD-4). Cả hai đều đọc được."""

    PUBLISHED = "published"
    PARTIAL = "partial"


class Meta(BaseModel):
    """Ngữ cảnh của mọi con số trong `data`."""

    model_config = _CONFIG

    snapshot_date: date
    """Ngày snapshot, `YYYY-MM-DD` theo `Asia/Ho_Chi_Minh`."""

    snapshot_status: SnapshotStatus
    """`published` khi mọi nguồn tự động đang bật đều chạy thành công, ngược lại `partial`."""

    sources: list[str]
    """Các nguồn đang bật."""

    sources_failed: list[str]
    """Các nguồn lỗi ở lượt chạy của snapshot. Rỗng khi `published`."""

    thresholds: Thresholds
    """Ngưỡng đã dùng."""

    coverage_notes: Annotated[list[CoverageNote], Field(min_length=1)]
    """Lưu ý độ phủ, hiển thị trên mọi màn hình có số. Ít nhất một lưu ý."""

    cells: dict[str, CellMeta]
    """Một mục cho mỗi ô mà response dùng, khóa theo `cell_id`."""

    @model_validator(mode="after")
    def _trang_thai_va_nguon_loi(self) -> Self:
        if self.snapshot_status is SnapshotStatus.PUBLISHED and self.sources_failed:
            raise ValueError("Snapshot published thì sources_failed phải rỗng.")
        return self


class Envelope[T: BaseModel](BaseModel):
    """Thân của mọi response chứa số: `data` cùng `meta` mô tả từng ô mà `data` dùng."""

    model_config = _CONFIG

    data: T
    """Phần riêng của route. Mọi con số trong đây là một `Stat`."""

    meta: Meta
    """Ngữ cảnh của con số: snapshot, nguồn, ngưỡng, lưu ý độ phủ, và từng ô."""

    @model_validator(mode="after")
    def _hop_dong(self) -> Self:
        cells = self.meta.cells
        min_sample = self.meta.thresholds.min_sample
        loi: list[str] = []
        for path, found in _walk(self.data, "data"):
            if found is None:
                loi.append(f"{path} là số đứng riêng ngoài Stat, phải bọc trong Stat")
                continue
            if isinstance(found, Stat):
                cell_id, ref_path = found.cell_id, f"{path}.cell_id"
            else:
                cell_id, ref_path = found, path
            cell = cells.get(cell_id)
            if cell is None:
                loi.append(f"{ref_path} = {cell_id!r} không có mục trong meta.cells")
            elif isinstance(found, Stat) and found.kind in _RATIO_KINDS:
                # percentile chưa có tham chiếu tới thước đo của nó, nên chưa kiểm được ở đây.
                expected = suppression_for(found.kind, cell.n, min_sample=min_sample)
                if found.display is not expected:
                    loi.append(
                        f"{path}.display = {found.display}, nhưng suppression_for cho "
                        f"{expected} với n = {cell.n}"
                    )
        for cell_id, cell in cells.items():
            for measure, n in cell.n_by_measure.items():
                hidden = suppression_for(MeasureKind.PERCENTILE, n, min_sample=min_sample)
                expected = hidden is DisplayState.NULL_DATA
                if cell.insufficient_by_measure[measure] is not expected:
                    loi.append(
                        f"meta.cells[{cell_id!r}].insufficient_by_measure[{measure!r}] phải là "
                        f"{str(expected).lower()} với n = {n}"
                    )
        if loi:
            raise ValueError("Hợp đồng envelope bị vỡ: " + "; ".join(loi) + ".")
        return self


def _has_cell_ref(annotation: object) -> bool:
    """`CellRef` nằm ở bất kỳ đâu trong kiểu, kể cả `CellId | None`, `list[CellId]`."""
    if isinstance(annotation, CellRef):
        return True
    return any(_has_cell_ref(arg) for arg in get_args(annotation))


def _strings(value: object, path: str) -> Iterator[tuple[str, str]]:
    """Mọi chuỗi dưới một trường mang `CellRef`. Khóa của dict không phải mã ô nên bỏ qua."""
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, Mapping):
        for key, item in value.items():
            yield from _strings(item, f"{path}[{key!r}]")
    elif isinstance(value, list | tuple | set | frozenset):
        for i, item in enumerate(value):
            yield from _strings(item, f"{path}[{i}]")


def _walk(value: object, path: str) -> Iterator[tuple[str, Stat | str | None]]:
    """Duyệt `data`: trả `(đường dẫn, Stat)` cho mỗi `Stat`, `(đường dẫn, cell_id)` cho mỗi
    trường mang `CellRef`, `(đường dẫn, None)` cho mỗi số đứng riêng ngoài `Stat`."""
    if isinstance(value, Stat):
        yield path, value
    elif isinstance(value, BaseModel):
        for name, info in type(value).model_fields.items():
            field_value = getattr(value, name)
            field_path = f"{path}.{name}"
            if any(isinstance(m, CellRef) for m in info.metadata) or _has_cell_ref(info.annotation):
                yield from _strings(field_value, field_path)
            else:
                yield from _walk(field_value, field_path)
    elif isinstance(value, Mapping):
        for key, item in value.items():
            yield from _walk(item, f"{path}[{key!r}]")
    elif isinstance(value, list | tuple | set | frozenset):
        for i, item in enumerate(value):
            yield from _walk(item, f"{path}[{i}]")
    elif isinstance(value, numbers.Number) and not isinstance(value, bool):
        yield path, None
