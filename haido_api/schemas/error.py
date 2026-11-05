"""Hình lỗi chuẩn: `{"error": {"code", "message", "snapshot_date"}}`."""

from datetime import date
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

_CONFIG = ConfigDict(extra="forbid", use_attribute_docstrings=True)


class ErrorBody(BaseModel):
    """Nội dung lỗi."""

    model_config = _CONFIG

    code: Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*$")]
    """Mã lỗi snake_case, ổn định để giao diện rẽ nhánh."""

    message: str
    """Câu giải thích tiếng Việt."""

    snapshot_date: date | None
    """Ngày snapshot mà lỗi liên quan; `null` khi lỗi xảy ra trước khi đọc snapshot nào."""


class ErrorEnvelope(BaseModel):
    """Thân của mọi response lỗi. Không bao giờ đi cùng `data`."""

    model_config = _CONFIG

    error: ErrorBody
