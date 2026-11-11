"""Hình `data` của các route thị trường. Envelope bọc ngoài nằm ở `haido_core.domain.envelope`.

Mã vai trò, cấp bậc, thành phố, nhóm kỹ năng là chuỗi snake_case tạm, chỉ dữ liệu biết;
#16 chốt mã thật. Ở đây không có enum nào cho chúng.
"""

import math
from collections import Counter
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from haido_core.domain.display_policy import DisplayState, MeasureKind
from haido_core.domain.envelope import CellId, Stat

_CONFIG = ConfigDict(extra="forbid", use_attribute_docstrings=True, revalidate_instances="always")


class CityShareRow(BaseModel):
    """Tỷ trọng của một thành phố trong số tin của vai trò, trên toàn quốc (FR-33)."""

    model_config = _CONFIG

    city: str
    """Mã thành phố. `other` gom các thành phố khác, `unknown` là tin không xác định thành phố."""

    share: Stat
    """Tỷ trọng, `kind = composition_share`. Dưới ngưỡng mẫu vẫn có giá trị, kèm `low_sample_shown`."""

    @model_validator(mode="after")
    def _loai_thuoc_do(self) -> Self:
        if self.share.kind is not MeasureKind.COMPOSITION_SHARE:
            raise ValueError(f"share phải là composition_share, nhận {self.share.kind}.")
        return self


class CitySharesData(BaseModel):
    """`data` của `GET /api/v1/city-shares`."""

    model_config = _CONFIG

    role: str
    """Vai trò đã chọn; `all` là mọi vai trò."""

    level: str
    """Cấp bậc lọc đã dùng (#163): `all` là mọi cấp bậc, `entry` là nhóm mới vào nghề, hoặc một cấp như `senior`."""

    total_cell_id: CellId
    """Ô toàn quốc của vai trò ở cấp đã chọn, mẫu số của mọi tỷ trọng. Cỡ mẫu ở `meta.cells[total_cell_id]`."""

    rows: Annotated[list[CityShareRow], Field(min_length=1)]
    """Mỗi thành phố một dòng, cộng dòng `other` và `unknown`. Tổng `share.value` bằng 1."""

    @model_validator(mode="after")
    def _tong_bang_mot(self) -> Self:
        trung = sorted(city for city, k in Counter(r.city for r in self.rows).items() if k > 1)
        if trung:
            raise ValueError(f"Mã thành phố bị trùng: {', '.join(trung)}.")
        thieu = [row.city for row in self.rows if row.share.value is None]
        if thieu:
            raise ValueError(f"Tỷ trọng phải có giá trị, thiếu ở: {', '.join(thieu)}.")
        total = math.fsum(row.share.value for row in self.rows if row.share.value is not None)
        if not math.isclose(total, 1.0, abs_tol=1e-9):
            raise ValueError(f"Tổng tỷ trọng phải bằng 1, nhận {total}.")
        return self


class SkillRateRow(BaseModel):
    """Tỷ lệ xuất hiện của một kỹ năng trong ô đã dùng."""

    model_config = _CONFIG

    skill: str
    """Mã kỹ năng, kebab-case, ví dụ `spring-boot`."""

    rate: Stat
    """Tỷ lệ xuất hiện, `kind = skill_rate`. Dưới ngưỡng mẫu là `null_data`, không có giá trị."""

    group: str | None
    """Nhóm kỹ năng theo θ: `core`, `common`, `company_specific`. `null` khi `rate` bị ẩn (`null_data`)."""

    @model_validator(mode="after")
    def _nhom_theo_hien_thi(self) -> Self:
        if self.rate.kind is not MeasureKind.SKILL_RATE:
            raise ValueError(f"rate phải là skill_rate, nhận {self.rate.kind}.")
        if self.rate.display is DisplayState.NULL_DATA and self.group is not None:
            raise ValueError("rate là null_data thì group phải là null.")
        if self.rate.display is not DisplayState.NULL_DATA and self.group is None:
            raise ValueError("rate có giá trị thì group phải có.")
        return self


class SkillRatesData(BaseModel):
    """`data` của `GET /api/v1/skill-rates`."""

    model_config = _CONFIG

    role: str
    """Vai trò người dùng chọn."""

    level: str
    """Cấp bậc người dùng chọn."""

    cell_id: CellId
    """Ô thật sự dùng để tính. Khác ô đã chọn khi quay về ô rộng hơn; lý do ở `fallback_label`."""

    rows: list[SkillRateRow]
    """Mỗi kỹ năng của ô một dòng."""

    @model_validator(mode="after")
    def _cung_mot_o(self) -> Self:
        lech = sorted({row.rate.cell_id for row in self.rows} - {self.cell_id})
        if lech:
            raise ValueError(f"Mọi rate phải thuộc ô {self.cell_id!r}, có ô lạ: {', '.join(lech)}.")
        return self


class NewcomerRoleRow(BaseModel):
    """Một vai trò trên màn người mới (#110): số tin entry-level, tỷ lệ, và n.

    Hai con số đếm nằm ở `meta.cells`: số tin entry-level là `meta.cells[entry_cell_id].n`,
    n của vai trò là `meta.cells[total_cell_id].n`.
    """

    model_config = _CONFIG

    role: str
    """Mã vai trò."""

    total_cell_id: CellId
    """Ô toàn quốc của vai trò (`vn.<role>`); `n` của ô là số tin của vai trò, mẫu số của `share`."""

    entry_cell_id: CellId
    """Ô entry-level của vai trò (`vn.<role>.entry`); `n` của ô là số tin entry-level."""

    share: Stat
    """Tỷ lệ tin entry-level trong số tin của vai trò, `kind = level_share`, `cell_id = total_cell_id`.
    Vai trò dưới ngưỡng mẫu là `null_data`, không có giá trị."""

    @model_validator(mode="after")
    def _ty_le_cua_vai_tro(self) -> Self:
        if self.share.kind is not MeasureKind.LEVEL_SHARE:
            raise ValueError(f"share phải là level_share, nhận {self.share.kind}.")
        if self.share.cell_id != self.total_cell_id:
            raise ValueError(
                f"share.cell_id phải là total_cell_id {self.total_cell_id!r}, nhận {self.share.cell_id!r}."
            )
        if self.entry_cell_id == self.total_cell_id:
            raise ValueError("entry_cell_id phải khác total_cell_id.")
        return self


class NewcomerRolesData(BaseModel):
    """`data` của `GET /api/v1/newcomer-roles`."""

    model_config = _CONFIG

    levels: Annotated[list[str], Field(min_length=1)]
    """Các cấp bậc được tính là entry-level, ví dụ `["intern", "fresher", "junior"]`."""

    rows: Annotated[list[NewcomerRoleRow], Field(min_length=1)]
    """Mỗi vai trò một dòng, theo thứ tự hiển thị: dòng có tỷ lệ trước, rồi dòng `null_data`;
    trong mỗi nhóm, số tin entry-level giảm dần rồi theo mã vai trò. Web không sắp xếp lại."""

    @model_validator(mode="after")
    def _khong_trung_vai_tro(self) -> Self:
        trung = sorted(role for role, k in Counter(r.role for r in self.rows).items() if k > 1)
        if trung:
            raise ValueError(f"Mã vai trò bị trùng: {', '.join(trung)}.")
        return self
