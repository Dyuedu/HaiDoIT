"""Bước `publish`: chốt snapshot S sau `aggregate` (#93, AD-4).

`published` khi mọi nguồn tự động (`sources.auto` trong `config/rules.toml`) có lượt chạy thành
công ở S; ngược lại `partial`, kèm danh sách nguồn lỗi theo A–Z. Nguồn tự động không có lượt chạy
ở S cũng là chưa chạy thành công. Nguồn chạy tay không ảnh hưởng trạng thái.

Sau bước này S không còn nhận `ingest`, `lifecycle` hay `aggregate`: hàng đã công bố không sửa.
"""

from dataclasses import dataclass
from datetime import date

from sqlalchemy import Engine

from haido_core.config import RulesConfig
from haido_core.db import snapshot_store
from haido_core.steps.common import SnapshotClosedError, StepError, parse_snapshot_id


@dataclass(frozen=True, slots=True)
class PublishResult:
    snapshot_id: date
    status: str
    sources_failed: tuple[str, ...]


def publish_snapshot(snapshot_id: str, *, engine: Engine, rules: RulesConfig) -> PublishResult:
    day = parse_snapshot_id(snapshot_id)
    with engine.begin() as conn:
        status = snapshot_store.lock_status(conn, day)
        if status is None:
            raise StepError(f"Snapshot {day.isoformat()} chưa mở; chạy `haido ingest` trước.")
        if status != "open":
            raise SnapshotClosedError(
                f"Snapshot {day.isoformat()} đã chốt (trạng thái {status}); không chốt lại. "
                "Tính lại phải sinh snapshot mới."
            )
        if not snapshot_store.has_city_shares(conn, day):
            raise StepError(f"Snapshot {day.isoformat()} chưa có số liệu tổng hợp; chạy `haido aggregate` trước.")
        runs = snapshot_store.runs_at(conn, day)
        failed = tuple(sorted(source for source in rules.auto_sources if not runs.get(source, False)))
        final = "partial" if failed else "published"
        snapshot_store.close_snapshot(conn, day, final, failed)
    return PublishResult(day, final, failed)
