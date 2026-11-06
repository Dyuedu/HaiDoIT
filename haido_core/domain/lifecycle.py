"""Vòng đời tin theo snapshot (Story 1.4, AD-4).

Hàm thuần. Không sửa và không xóa đầu vào. Quan sát vẫn là bảng thêm-một-chiều
ở `scraper/`. Bảng `stat_job_lifecycle` chờ Alembic của #1.

Một lượt thành công của đúng nguồn mới được đếm. Lượt lỗi không làm đứt chuỗi,
không tính là vắng mặt, và không tăng số lần đăng lại.
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

ASIA_HO_CHI_MINH = timezone(timedelta(hours=7))
"""Việt Nam không có giờ mùa. Cùng mốc với `scraper/crawlers/base.py`."""


def snapshot_id_at(moment: datetime) -> str:
    """`YYYY-MM-DD` theo Asia/Ho_Chi_Minh, không theo đồng hồ UTC của máy."""
    if moment.tzinfo is None:
        raise ValueError("Mốc thời gian phải có múi giờ.")
    return moment.astimezone(ASIA_HO_CHI_MINH).date().isoformat()


@dataclass(frozen=True, slots=True)
class SourceRun:
    """Một lượt của một nguồn. `success` là listing đi hết, không phải đêm pipeline lỗi."""

    source: str
    snapshot_id: str
    success: bool


@dataclass(frozen=True, slots=True)
class Observation:
    """Tin có mặt trong listing của nguồn ở snapshot đó."""

    job_id: str
    source: str
    snapshot_id: str


@dataclass(frozen=True, slots=True)
class JobLife:
    """Vòng đời tính tới đúng snapshot được hỏi, không dùng tin của ngày sau."""

    job_id: str
    source: str
    snapshot_id: str
    times_seen: int
    first_seen: str
    last_seen: str
    repost_count: int
    absent: bool
    in_window: bool


def _parse_day(value: str) -> date:
    if len(value) != 10 or value[4] != "-" or value[7] != "-":
        raise ValueError(f"snapshot_id phải là YYYY-MM-DD, nhận {value}.")
    return date.fromisoformat(value)


def job_lifecycle(
    runs: tuple[SourceRun, ...] | list[SourceRun],
    observations: tuple[Observation, ...] | list[Observation],
    snapshot_id: str,
    *,
    window_days: int,
) -> tuple[JobLife, ...]:
    """Vòng đời của mọi tin đã thấy ở một lượt thành công, tính tới `snapshot_id`.

    Vắng dưới ba lượt thành công liên tiếp thì chưa biến mất. Xuất hiện lại sau
    khi đã biến mất thì `repost_count` tăng một. Cửa sổ ngày xét `last_seen`
    của chính snapshot này.
    """
    if window_days < 1:
        raise ValueError(f"Cửa sổ ngày phải từ 1, nhận {window_days}.")
    as_of = _parse_day(snapshot_id)
    seen: dict[tuple[str, str, str], bool] = {}
    for item in observations:
        seen[(item.source, item.snapshot_id, item.job_id)] = True
    by_source: dict[str, list[SourceRun]] = {}
    for run in runs:
        if _parse_day(run.snapshot_id) <= as_of:
            by_source.setdefault(run.source, []).append(run)

    rows: list[JobLife] = []
    for source in sorted(by_source):
        ordered = sorted(by_source[source], key=lambda run: run.snapshot_id)
        jobs: dict[str, dict[str, object]] = {}
        for run in ordered:
            if not run.success:
                continue
            known = set(jobs)
            present = {
                job_id
                for (src, day, job_id), flag in seen.items()
                if flag and src == source and day == run.snapshot_id
            }
            for job_id in present:
                state = jobs.get(job_id)
                if state is None:
                    jobs[job_id] = {
                        "times_seen": 1,
                        "first_seen": run.snapshot_id,
                        "last_seen": run.snapshot_id,
                        "repost_count": 0,
                        "absent_streak": 0,
                        "gone": False,
                    }
                    continue
                if state["gone"]:
                    state["repost_count"] = int(state["repost_count"]) + 1
                    state["gone"] = False
                state["times_seen"] = int(state["times_seen"]) + 1
                state["last_seen"] = run.snapshot_id
                state["absent_streak"] = 0
            for job_id in known - present:
                state = jobs[job_id]
                state["absent_streak"] = int(state["absent_streak"]) + 1
                if int(state["absent_streak"]) >= 3:
                    state["gone"] = True
        for job_id in sorted(jobs):
            state = jobs[job_id]
            last_seen = str(state["last_seen"])
            in_window = 0 <= (as_of - _parse_day(last_seen)).days <= window_days
            rows.append(
                JobLife(
                    job_id=job_id,
                    source=source,
                    snapshot_id=snapshot_id,
                    times_seen=int(state["times_seen"]),
                    first_seen=str(state["first_seen"]),
                    last_seen=last_seen,
                    repost_count=int(state["repost_count"]),
                    absent=bool(state["gone"]),
                    in_window=in_window,
                )
            )
    return tuple(rows)
