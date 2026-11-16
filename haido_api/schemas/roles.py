"""Hình response của `GET /api/v1/role-for-title` (#150).

Response không chứa số nên không dùng Envelope của AD-17 (như `GET /api/v1/skills`). Response là `{data: {status, role}}`.
"""

from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator

_CONFIG = ConfigDict(extra="forbid", use_attribute_docstrings=True)


class TitleMatch(StrEnum):
    """Kết quả phân loại một chức danh."""

    MATCHED = "matched"
    """Phép 6 ra một vai trò cụ thể."""
    GENERIC = "generic"
    """Chức danh IT chung chung (phép 6 ra `Other`): không chỉ một vai trò."""
    NOT_IT = "not_it"
    """Chức danh không thuộc IT."""


class RoleForTitleData(BaseModel):
    """Vai trò Hải Đồ dùng cho chức danh người dùng gõ."""

    model_config = _CONFIG

    status: TitleMatch
    """`matched`, `generic` hoặc `not_it`."""
    role: str | None
    """Mã vai trò của `config/rules.toml` khi `matched`; `null` khi không."""

    @model_validator(mode="after")
    def _vai_tro_theo_trang_thai(self) -> Self:
        if (self.status is TitleMatch.MATCHED) != (self.role is not None):
            raise ValueError("role có giá trị khi và chỉ khi status = matched.")
        return self


class RoleForTitleResponse(BaseModel):
    """`{data}`. Không có `meta` vì không có con số nào."""

    model_config = _CONFIG

    data: RoleForTitleData
