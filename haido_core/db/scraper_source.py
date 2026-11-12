"""Đọc bảng của scraper (cầu nối C-11) bằng `SELECT`, qua engine chỉ-đọc.

Lấy lượt chạy, quan sát và các cột dữ kiện của tin. Từ #283 đọc thêm mô tả JD để bước `ingest` phân loại
trong bộ nhớ; mô tả không được ghi xuống schema `haido` (DoD dòng 9).
Tên bảng ghi rõ schema `public`: user trùng tên schema `haido` sẽ tìm schema đó trước.
Khi Story 1.2 và 1.3 chuyển crawl vào `haido_core`, chỉ file này đổi.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date

from sqlalchemy import Engine, text

SCRAPER_SCHEMA = "public"


@dataclass(frozen=True, slots=True)
class SourceRunRow:
    source: str
    listing_complete: bool
    seen_count: int
    error: str | None


@dataclass(frozen=True, slots=True)
class SourceObservationRow:
    job_url: str
    source: str


@dataclass(frozen=True, slots=True)
class SourceFactsRow:
    job_url: str
    title: str | None
    company: str | None
    location: str | None
    experience_level: str | None
    job_level: str | None
    years_min: float | None = None
    """Số năm kinh nghiệm tối thiểu (`jobs.years_experience_min`, #280); `None` là tin không ghi."""
    text: str | None = None
    """Mô tả JD (`description_consolidated`, rỗng thì `description`), #283. Chỉ dùng trong bộ nhớ."""


@dataclass(frozen=True, slots=True)
class SourceSnapshot:
    runs: tuple[SourceRunRow, ...]
    observations: tuple[SourceObservationRow, ...]
    facts: tuple[SourceFactsRow, ...]


class ScraperPostgresReader:
    """Đọc một ngày của scraper trong một transaction chỉ-đọc, nhất quán."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def read(self, day: date) -> SourceSnapshot:
        schema = SCRAPER_SCHEMA
        params = {"d": day}
        with self.engine.connect() as conn:
            runs = conn.execute(
                text(
                    f"SELECT source, listing_complete, seen_count, error FROM {schema}.source_runs "
                    "WHERE snapshot_date = :d ORDER BY source"
                ),
                params,
            ).all()
            observed = conn.execute(
                text(
                    f"SELECT job_url, site FROM {schema}.job_observations "
                    "WHERE snapshot_date = :d ORDER BY job_url"
                ),
                params,
            ).all()
            facts = conn.execute(
                text(
                    f"SELECT {_FACT_COLUMNS} "
                    f"FROM {schema}.jobs j JOIN {schema}.job_observations o ON o.job_url = j.job_url "
                    "WHERE o.snapshot_date = :d ORDER BY j.job_url"
                ),
                params,
            ).all()
        return SourceSnapshot(
            runs=tuple(SourceRunRow(r[0], bool(r[1]), int(r[2]), r[3]) for r in runs),
            observations=tuple(SourceObservationRow(r[0], r[1]) for r in observed),
            facts=tuple(_fact(r) for r in facts),
        )

    def read_facts(self, urls: Sequence[str]) -> tuple[SourceFactsRow, ...]:
        """Dữ kiện hiện tại của các tin theo URL (để làm mới nhãn của tin không quan sát ở S, #283)."""
        if not urls:
            return ()
        with self.engine.connect() as conn:
            rows = conn.execute(
                text(f"SELECT {_FACT_COLUMNS} FROM {SCRAPER_SCHEMA}.jobs j WHERE j.job_url = ANY(:u) ORDER BY j.job_url"),
                {"u": list(urls)},
            ).all()
        return tuple(_fact(r) for r in rows)


_FACT_COLUMNS = (
    "j.job_url, j.title, j.company, j.location, j.experience_level, j.job_level, j.years_experience_min, "
    "coalesce(nullif(j.description_consolidated, ''), j.description)"
)


def _fact(r: Sequence[object]) -> SourceFactsRow:
    years = r[6]
    return SourceFactsRow(*r[:6], None if years is None else float(years), r[7])  # type: ignore[arg-type]
