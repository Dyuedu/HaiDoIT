"""Bước `lifecycle`: tính vòng đời tin tới snapshot S rồi ghi `stat_job_lifecycle` (Story 1.4, AD-4).

Phép tính nằm ở `domain.lifecycle.job_lifecycle` (hàm thuần). Bước này chỉ đọc lượt chạy và
quan sát đã `ingest`, gọi hàm, ghi kết quả kèm `config_version`. Cùng dữ liệu và cùng cấu hình
thì ra cùng hàng. S đã `published` hoặc `partial` thì từ chối.
"""

from dataclasses import dataclass
from datetime import date

from sqlalchemy import Engine

from haido_core.config import RulesConfig
from haido_core.db import snapshot_store
from haido_core.db.snapshot_store import LifecycleValues
from haido_core.domain.lifecycle import Observation, SourceRun, job_lifecycle
from haido_core.steps.common import SnapshotClosedError, StepError, parse_snapshot_id


@dataclass(frozen=True, slots=True)
class LifecycleResult:
    snapshot_id: date
    rows: int
    config_version: str


def lifecycle_snapshot(snapshot_id: str, *, engine: Engine, rules: RulesConfig) -> LifecycleResult:
    day = parse_snapshot_id(snapshot_id)
    with engine.begin() as conn:
        status = snapshot_store.lock_status(conn, day)
        if status is None:
            raise StepError(f"Snapshot {day.isoformat()} chưa mở; chạy `haido ingest` trước.")
        if status != "open":
            raise SnapshotClosedError(
                f"Snapshot {day.isoformat()} đã chốt (trạng thái {status}); không ghi thêm. "
                "Tính lại phải sinh snapshot mới."
            )
        runs = [SourceRun(source, d.isoformat(), ok) for source, d, ok in snapshot_store.runs_up_to(conn, day)]
        seen = [
            Observation(str(posting_id), source, d.isoformat())
            for posting_id, source, d in snapshot_store.observations_up_to(conn, day)
        ]
        lives = job_lifecycle(runs, seen, day.isoformat(), window_days=rules.window_days)
        values = sorted(
            (
                LifecycleValues(
                    posting_id=int(life.job_id),
                    times_seen=life.times_seen,
                    first_seen=date.fromisoformat(life.first_seen),
                    last_seen=date.fromisoformat(life.last_seen),
                    repost_count=life.repost_count,
                    absent=life.absent,
                    in_window=life.in_window,
                )
                for life in lives
            ),
            key=lambda v: v.posting_id,
        )
        snapshot_store.replace_lifecycle(conn, day, rules.config_version, values)
    return LifecycleResult(day, len(values), rules.config_version)
