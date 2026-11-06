"""Phần dùng chung của các bước CLI (Story 1.4)."""

import re
from datetime import date

_DAY = re.compile(r"\d{4}-\d{2}-\d{2}")


class StepError(Exception):
    """Lỗi nghiệp vụ của một bước. Thông báo bằng tiếng Việt, không chứa URL hay mật khẩu."""


class SnapshotClosedError(StepError):
    """Snapshot đã `published` hoặc `partial`: hàng đã công bố không sửa, không xóa."""


def parse_snapshot_id(value: str) -> date:
    """`snapshot_id` là `YYYY-MM-DD` chặt chẽ (không nhận `20261103` hay `2026-1-3`)."""
    if isinstance(value, str) and _DAY.fullmatch(value):
        try:
            return date.fromisoformat(value)
        except ValueError:
            pass
    raise StepError(f"Snapshot phải có dạng YYYY-MM-DD và là ngày có thật (nhận: {value!r}).")
