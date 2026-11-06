"""Bước `ingest`: mở snapshot S rồi chép lượt chạy, quan sát, dữ kiện tin của S (Story 1.4, AD-4).

Nguồn là bảng của scraper (cầu nối C-11), đọc qua `SourceReader` để test thuần không cần DB.
Đích là schema `haido`. Mọi hàng của một lần chạy ghi trong một transaction; S đã `published`
hoặc `partial` thì từ chối và không ghi gì. Chạy lại cho S đang `open` không sinh hàng trùng.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from typing import Protocol

from sqlalchemy import Connection, Engine

from haido_core.config import RulesConfig
from haido_core.db import snapshot_store
from haido_core.db.scraper_source import SourceSnapshot
from haido_core.db.snapshot_store import FactVersion, RunValues
from haido_core.steps.common import SnapshotClosedError, StepError, parse_snapshot_id


class SourceReader(Protocol):
    def read(self, day: date) -> SourceSnapshot: ...


@dataclass(frozen=True, slots=True)
class PlannedRun:
    source: str
    mode: str
    success: bool
    seen_count: int
    error: str | None


@dataclass(frozen=True, slots=True)
class PlannedObservation:
    source: str
    source_url: str


@dataclass(frozen=True, slots=True)
class PlannedFact:
    source: str
    source_url: str
    title: str | None
    company: str | None
    location_text: str | None
    experience_level: str | None
    job_level: str | None

    def version(self) -> FactVersion:
        return FactVersion(self.title, self.company, self.location_text, self.experience_level, self.job_level)


@dataclass(frozen=True, slots=True)
class IngestPlan:
    snapshot_id: date
    runs: tuple[PlannedRun, ...]
    observations: tuple[PlannedObservation, ...]
    facts: tuple[PlannedFact, ...]


@dataclass(frozen=True, slots=True)
class IngestResult:
    snapshot_id: date
    runs: int
    postings: int
    observations: int
    facts_added: int


def plan_ingest(day: date, data: SourceSnapshot, auto_sources: Sequence[str]) -> IngestPlan:
    """Hàm thuần: từ dữ liệu nguồn dựng kế hoạch ghi. Thứ tự đầu ra không phụ thuộc đầu vào."""
    if not data.runs:
        raise StepError(
            f"Bảng thu thập chưa có lượt chạy nào của ngày {day.isoformat()}; không mở snapshot."
        )
    auto = set(auto_sources)
    runs = tuple(
        PlannedRun(
            source=r.source,
            mode="auto" if r.source in auto else "manual",
            success=r.listing_complete,
            seen_count=r.seen_count,
            error=r.error,
        )
        for r in sorted(data.runs, key=lambda r: r.source)
    )
    run_sources = {r.source for r in runs}
    missing = sorted({o.source for o in data.observations} - run_sources)
    if missing:
        raise StepError(
            f"Quan sát của nguồn {', '.join(missing)} ngày {day.isoformat()} không có lượt chạy tương ứng; "
            "không ghi gì."
        )
    observations = tuple(
        PlannedObservation(o.source, o.job_url)
        for o in sorted(data.observations, key=lambda o: (o.source, o.job_url))
    )
    source_of = {o.job_url: o.source for o in data.observations}
    facts = tuple(
        PlannedFact(source_of[f.job_url], f.job_url, f.title, f.company, f.location, f.experience_level, f.job_level)
        for f in sorted(data.facts, key=lambda f: (source_of.get(f.job_url, ""), f.job_url))
        if f.job_url in source_of
    )
    return IngestPlan(day, runs, observations, facts)


def open_snapshot(conn: Connection, day: date) -> None:
    """Mở snapshot S (trạng thái đầu `open`) hoặc xác nhận S vẫn đang `open`.

    Đây là đường duy nhất tạo snapshot. S đã chốt thì từ chối.
    """
    snapshot_store.insert_open(conn, day)
    status = snapshot_store.lock_status(conn, day)
    if status != "open":
        raise SnapshotClosedError(
            f"Snapshot {day.isoformat()} đã chốt (trạng thái {status}); không ghi thêm. "
            "Tính lại phải sinh snapshot mới."
        )


def ingest_snapshot(snapshot_id: str, *, reader: SourceReader, engine: Engine, rules: RulesConfig) -> IngestResult:
    day = parse_snapshot_id(snapshot_id)
    plan = plan_ingest(day, reader.read(day), rules.auto_sources)
    with engine.begin() as conn:
        open_snapshot(conn, day)
        run_ids = snapshot_store.upsert_runs(
            conn, day, (RunValues(r.source, r.mode, r.success, r.seen_count, r.error) for r in plan.runs)
        )
        posting_ids = snapshot_store.ensure_postings(conn, [(o.source, o.source_url) for o in plan.observations])

        current = snapshot_store.facts_at(conn, day)
        # Tin đã được quan sát ở snapshot sau S (chạy bù/lệch thứ tự): không thêm phiên bản tại S,
        # vì dữ kiện hiện tại của scraper sẽ thành "dữ kiện tại" các snapshot sau và làm sai lịch sử của chúng.
        later = snapshot_store.observed_after(conn, day, [posting_ids[(f.source, f.source_url)] for f in plan.facts])
        new_facts = []
        for fact in plan.facts:
            posting_id = posting_ids[(fact.source, fact.source_url)]
            if posting_id in later:
                continue
            if current.get(posting_id) != fact.version():
                new_facts.append((posting_id, fact.version()))
        facts_added = snapshot_store.insert_facts(conn, day, new_facts)

        snapshot_store.insert_observations(
            conn, day, [(posting_ids[(o.source, o.source_url)], run_ids[o.source]) for o in plan.observations]
        )
    return IngestResult(day, len(plan.runs), len(posting_ids), len(plan.observations), facts_added)
