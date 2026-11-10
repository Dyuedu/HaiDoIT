"""Truy cập schema `haido` cho các bước `ingest` và `lifecycle` (Story 1.4).

Mọi hàm nhận một `Connection` đang trong transaction của bước gọi nó, nên các hàng của một
lần chạy cùng thành công hoặc cùng không có. Quan sát và dữ kiện tin chỉ `INSERT`; DB chặn
`UPDATE`/`DELETE` bằng trigger.
"""

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date

import sqlalchemy as sa
from sqlalchemy import Connection
from sqlalchemy.dialects.postgresql import distinct_on
from sqlalchemy.dialects.postgresql import insert as pg_insert

from haido_core.db.tables import (
    job_observations,
    job_posting_facts,
    job_postings,
    pipeline_runs,
    snapshots,
    stat_cells,
    stat_city_shares,
    stat_job_lifecycle,
)
from haido_core.domain.aggregate import CellRow, ShareRow


@dataclass(frozen=True, slots=True)
class FactVersion:
    """Dữ kiện của tin ở một phiên bản. Không có mô tả JD hay liên hệ người đăng."""

    title: str | None
    company: str | None
    location_text: str | None
    experience_level: str | None
    job_level: str | None


@dataclass(frozen=True, slots=True)
class RunValues:
    source: str
    mode: str
    success: bool
    seen_count: int
    error: str | None


@dataclass(frozen=True, slots=True)
class LifecycleValues:
    posting_id: int
    times_seen: int
    first_seen: date
    last_seen: date
    repost_count: int
    absent: bool
    in_window: bool


# ----------------------------------------------------------------------------- snapshot


def insert_open(conn: Connection, day: date) -> None:
    """Tạo snapshot `open` nếu chưa có. Đây là đường duy nhất tạo hàng `snapshots`."""
    conn.execute(pg_insert(snapshots).values(snapshot_id=day, status="open").on_conflict_do_nothing())


def lock_status(conn: Connection, day: date) -> str | None:
    """Trạng thái của snapshot, khóa hàng tới hết transaction để hai lần chạy không đè nhau."""
    stmt = sa.select(snapshots.c.status).where(snapshots.c.snapshot_id == day).with_for_update()
    return conn.execute(stmt).scalar_one_or_none()


# ----------------------------------------------------------------------------- ingest


def upsert_runs(conn: Connection, day: date, runs: Iterable[RunValues]) -> dict[str, int]:
    """Lượt chạy của S. Chạy lại cho S đang `open` thì cập nhật theo scraper mới nhất."""
    ids: dict[str, int] = {}
    for run in runs:
        stmt = pg_insert(pipeline_runs).values(
            snapshot_id=day,
            source=run.source,
            mode=run.mode,
            success=run.success,
            seen_count=run.seen_count,
            error=run.error,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=[pipeline_runs.c.snapshot_id, pipeline_runs.c.source],
            set_={
                "mode": stmt.excluded.mode,
                "success": stmt.excluded.success,
                "seen_count": stmt.excluded.seen_count,
                "error": stmt.excluded.error,
            },
        ).returning(pipeline_runs.c.id)
        ids[run.source] = conn.execute(stmt).scalar_one()
    return ids


def ensure_postings(conn: Connection, pairs: Sequence[tuple[str, str]]) -> dict[tuple[str, str], int]:
    """Id của từng tin `(source, source_url)`; tạo tin mới nếu chưa có."""
    if not pairs:
        return {}
    conn.execute(
        pg_insert(job_postings).on_conflict_do_nothing(),
        [{"source": s, "source_url": u} for s, u in pairs],
    )
    wanted = set(pairs)
    sources = sorted({s for s, _ in pairs})
    rows = conn.execute(
        sa.select(job_postings.c.id, job_postings.c.source, job_postings.c.source_url).where(
            job_postings.c.source.in_(sources)
        )
    )
    return {(r.source, r.source_url): r.id for r in rows if (r.source, r.source_url) in wanted}


def facts_at(conn: Connection, day: date) -> dict[int, FactVersion]:
    """Dữ kiện của tin tại S: phiên bản mới nhất có `snapshot_id <= S`."""
    t = job_posting_facts
    stmt = (
        sa.select(t.c.posting_id, t.c.title, t.c.company, t.c.location_text, t.c.experience_level, t.c.job_level)
        .where(t.c.snapshot_id <= day)
        .ext(distinct_on(t.c.posting_id))
        .order_by(t.c.posting_id, t.c.snapshot_id.desc())
    )
    return {r.posting_id: FactVersion(r.title, r.company, r.location_text, r.experience_level, r.job_level)
            for r in conn.execute(stmt)}  # fmt: skip


def observed_after(conn: Connection, day: date, posting_ids: Sequence[int]) -> set[int]:
    """Các tin đã có quan sát ở snapshot sau S."""
    if not posting_ids:
        return set()
    stmt = (
        sa.select(job_observations.c.posting_id)
        .where(job_observations.c.snapshot_id > day, job_observations.c.posting_id.in_(list(posting_ids)))
        .distinct()
    )
    return set(conn.execute(stmt).scalars())


def insert_facts(conn: Connection, day: date, rows: Sequence[tuple[int, FactVersion]]) -> int:
    """Thêm phiên bản dữ kiện tại S; trả về số hàng thật sự được thêm (trùng khóa thì bỏ qua)."""
    if not rows:
        return 0
    inserted = conn.execute(
        pg_insert(job_posting_facts).on_conflict_do_nothing().returning(job_posting_facts.c.posting_id),
        [
            {
                "posting_id": posting_id,
                "snapshot_id": day,
                "title": f.title,
                "company": f.company,
                "location_text": f.location_text,
                "experience_level": f.experience_level,
                "job_level": f.job_level,
            }
            for posting_id, f in rows
        ],
    )
    return len(inserted.all())


def insert_observations(conn: Connection, day: date, rows: Sequence[tuple[int, int]]) -> None:
    """Quan sát `(posting_id, pipeline_run_id)` của S. Trùng thì bỏ qua."""
    if not rows:
        return
    conn.execute(
        pg_insert(job_observations).on_conflict_do_nothing(),
        [{"posting_id": p, "snapshot_id": day, "pipeline_run_id": r} for p, r in rows],
    )


# ----------------------------------------------------------------------------- lifecycle


def runs_up_to(conn: Connection, day: date) -> list[tuple[str, date, bool]]:
    stmt = (
        sa.select(pipeline_runs.c.source, pipeline_runs.c.snapshot_id, pipeline_runs.c.success)
        .where(pipeline_runs.c.snapshot_id <= day)
        .order_by(pipeline_runs.c.snapshot_id, pipeline_runs.c.source)
    )
    return [(r.source, r.snapshot_id, r.success) for r in conn.execute(stmt)]


def observations_up_to(conn: Connection, day: date) -> list[tuple[int, str, date]]:
    """`(posting_id, source của lượt chạy, snapshot)` cho mọi quan sát tới S."""
    stmt = (
        sa.select(job_observations.c.posting_id, pipeline_runs.c.source, job_observations.c.snapshot_id)
        .join(pipeline_runs, pipeline_runs.c.id == job_observations.c.pipeline_run_id)
        .where(job_observations.c.snapshot_id <= day)
        .order_by(job_observations.c.snapshot_id, job_observations.c.posting_id)
    )
    return [(r.posting_id, r.source, r.snapshot_id) for r in conn.execute(stmt)]


def replace_lifecycle(conn: Connection, day: date, config_version: str, rows: Sequence[LifecycleValues]) -> None:
    """Ghi lại `stat_job_lifecycle` của S (bảng dẫn xuất, chỉ ghi khi S còn `open`)."""
    conn.execute(sa.delete(stat_job_lifecycle).where(stat_job_lifecycle.c.snapshot_id == day))
    if not rows:
        return
    conn.execute(
        sa.insert(stat_job_lifecycle),
        [
            {
                "snapshot_id": day,
                "posting_id": r.posting_id,
                "times_seen": r.times_seen,
                "first_seen": r.first_seen,
                "last_seen": r.last_seen,
                "repost_count": r.repost_count,
                "absent": r.absent,
                "in_window": r.in_window,
                "config_version": config_version,
            }
            for r in rows
        ],
    )


# ----------------------------------------------------------------------------- aggregate

ALL = "all"
"""Giá trị của `branch` và `seniority` trong `stat_cells` cho tới khi có nhánh và cấp bậc riêng."""


def lifecycle_postings(conn: Connection, day: date) -> list[tuple[int, str, date]]:
    """`(posting_id, source, last_seen)` của mọi tin có dòng vòng đời tại S, theo `posting_id`.

    Tin không có dòng vòng đời (chỉ thấy ở lượt chạy lỗi, AD-4) không nằm ở đây, nên không được đếm.
    """
    stmt = (
        sa.select(stat_job_lifecycle.c.posting_id, job_postings.c.source, stat_job_lifecycle.c.last_seen)
        .join(job_postings, job_postings.c.id == stat_job_lifecycle.c.posting_id)
        .where(stat_job_lifecycle.c.snapshot_id == day)
        .order_by(stat_job_lifecycle.c.posting_id)
    )
    return [(r.posting_id, r.source, r.last_seen) for r in conn.execute(stmt)]


def unaccounted_postings(conn: Connection, day: date) -> int:
    """Số tin thấy tại S ở lượt chạy thành công nhưng chưa có dòng vòng đời tại S với `last_seen = S`."""
    life = sa.exists().where(
        stat_job_lifecycle.c.snapshot_id == day,
        stat_job_lifecycle.c.posting_id == job_observations.c.posting_id,
        stat_job_lifecycle.c.last_seen == day,
    )
    stmt = (
        sa.select(sa.func.count())
        .select_from(job_observations)
        .join(pipeline_runs, pipeline_runs.c.id == job_observations.c.pipeline_run_id)
        .where(job_observations.c.snapshot_id == day, pipeline_runs.c.success.is_(True), ~life)
    )
    return conn.execute(stmt).scalar_one()


def has_city_shares(conn: Connection, day: date) -> bool:
    stmt = sa.select(sa.literal(1)).where(stat_city_shares.c.snapshot_id == day).limit(1)
    return conn.execute(stmt).first() is not None


def replace_stats(
    conn: Connection, day: date, config_version: str, cells: Sequence[CellRow], shares: Sequence[ShareRow]
) -> None:
    """Ghi lại `stat_cells` và `stat_city_shares` của S (bảng dẫn xuất, chỉ ghi khi S còn `open`)."""
    conn.execute(sa.delete(stat_cells).where(stat_cells.c.snapshot_id == day))
    conn.execute(sa.delete(stat_city_shares).where(stat_city_shares.c.snapshot_id == day))
    if cells:
        conn.execute(
            sa.insert(stat_cells),
            [
                {
                    "snapshot_id": day,
                    "role": c.role,
                    "branch": ALL,
                    "seniority": ALL,
                    "scope": c.scope,
                    "n": c.n,
                    "seniority_mix": c.seniority_mix,
                    "config_version": config_version,
                }
                for c in cells
            ],
        )
    if shares:
        conn.execute(
            sa.insert(stat_city_shares),
            [{"snapshot_id": day, "role": r.role, "city": r.city, "share": r.share} for r in shares],
        )


# ----------------------------------------------------------------------------- publish


def runs_at(conn: Connection, day: date) -> dict[str, bool]:
    """`{source: success}` của các lượt chạy ghi cho đúng S."""
    stmt = sa.select(pipeline_runs.c.source, pipeline_runs.c.success).where(pipeline_runs.c.snapshot_id == day)
    return {r.source: r.success for r in conn.execute(stmt)}


def close_snapshot(conn: Connection, day: date, status: str, sources_failed: Sequence[str]) -> None:
    """Chốt S thành `published` hoặc `partial`, kèm các nguồn lỗi. Chỉ gọi khi S đang `open` và đã khóa."""
    conn.execute(
        sa.update(snapshots)
        .where(snapshots.c.snapshot_id == day)
        .values(status=status, sources_failed=list(sources_failed), closed_at=sa.func.now())
    )
