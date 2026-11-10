"""Hình response của `GET /api/v1/skills`.

Danh sách kỹ năng không chứa con số nào, nên không dùng Envelope của AD-17 (Envelope dành cho
response chứa số). Response là `{data: {vocab_version, skills}}`.
"""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from haido_core.vocab.skills import MAX_SKILL_CODE_LEN, SKILL_CODE_PATTERN

_CONFIG = ConfigDict(extra="forbid", use_attribute_docstrings=True)

SkillCode = Annotated[str, Field(pattern=SKILL_CODE_PATTERN, max_length=MAX_SKILL_CODE_LEN)]


class SkillRow(BaseModel):
    """Một kỹ năng web hiển thị và cho tìm."""

    model_config = _CONFIG

    code: SkillCode
    """Mã kỹ năng, snake_case ASCII. Đây là thứ lưu trong hồ sơ trình duyệt và trong link chia sẻ."""
    name_en: Annotated[str, Field(min_length=1)]
    """Tên tiếng Anh."""
    name_vi: Annotated[str, Field(min_length=1)]
    """Tên tiếng Việt."""
    aliases: list[str]
    """Cách viết khác trong tin tuyển dụng, cả hai ngôn ngữ. Ô tìm kiếm dò cả ở đây."""


class SkillsData(BaseModel):
    """Danh sách kỹ năng của bộ từ vựng đang dùng."""

    model_config = _CONFIG

    vocab_version: Annotated[str, Field(min_length=1)]
    """Phiên bản bộ từ vựng, ví dụ `seed-2026-11-11`."""
    skills: list[SkillRow]
    """Mọi kỹ năng, theo thứ tự mã."""


class SkillsResponse(BaseModel):
    """`{data}`. Không có `meta` vì không có con số nào cần ngữ cảnh snapshot."""

    model_config = _CONFIG

    data: SkillsData
