"""Nguồn số liệu thật cho `GET /api/v1/city-shares` (#93).

Đọc `stat_city_shares` và `stat_cells` của snapshot đã công bố mới nhất, theo khóa. Không cộng
lại từ bảng tin, không đọc bảng của scraper (AD-5, cổng AD-7). Con số trả về là số đã ghi bởi bước
`aggregate`; `display` do `suppression_for` quyết, không tự so với ngưỡng ở đây.

- Snapshot đọc được là `published` hoặc `partial` mới nhất có `stat_city_shares` và ít nhất một hàng `stat_sources`
  (thiếu nguồn thì web coi là không đọc được, nên bỏ qua và lùi về snapshot cũ đầy đủ).
- `meta.sources` là `stat_sources` của snapshot đó, A–Z: các nguồn có ít nhất một tin được đếm trong cửa sổ 60 ngày
  (#259, DEC-12), do `aggregate` ghi, không phải các nguồn có lượt chạy ở S. `meta.sources_failed` lấy từ snapshot.
- Ngưỡng và lưu ý độ phủ lấy từ `config/rules.toml`.
- Kết nối mở ở yêu cầu đầu tiên, không mở lúc import hay lúc dựng nguồn.
- Vai trò không có tin nào ở snapshot (n toàn quốc bằng 0, hoặc không có hàng) thì `UnknownCell`
  kèm ngày snapshot; không có snapshot nào đọc được thì `UnknownCell` không có ngày.
"""

import threading
from collections.abc import Callable
from datetime import date
from typing import Any

import sqlalchemy as sa
from sqlalchemy import Connection, Engine

from haido_api.market_source import UnknownCell
from haido_api.schemas.market import CityShareRow, CitySharesData, SkillRatesData
from haido_core.config import RulesConfig, load_rules
from haido_core.db.engine import make_read_engine
from haido_core.db.tables import snapshots, stat_cells, stat_city_shares, stat_sources
from haido_core.domain.display_policy import MeasureKind, suppression_for
from haido_core.domain.envelope import (
    CellMeta,
    CoverageNote,
    Envelope,
    Meta,
    SnapshotStatus,
    Stat,
    Thresholds,
)

READABLE = ("published", "partial")
NATIONWIDE = "vn"
ALL = "all"


class StatMarket:
    """Bản thật của `MarketReadModel` cho `city_shares`. `skill_rates` chưa có số thật (#101)."""

    def __init__(
        self, *, engine_factory: Callable[[], Engine] | None = None, rules: RulesConfig | None = None
    ) -> None:
        self._factory = engine_factory if engine_factory is not None else make_read_engine
        self._rules = rules if rules is not None else load_rules()
        self._engine: Engine | None = None
        self._lock = threading.Lock()

    def _db(self) -> Engine:
        with self._lock:
            if self._engine is None:
                self._engine = self._factory()
            return self._engine

    def city_shares(self, *, role: str) -> Envelope[CitySharesData]:
        with self._db().connect() as conn:
            latest = _latest_readable(conn)
            if latest is None:
                raise UnknownCell("Chưa có snapshot nào đã công bố để đọc.", snapshot_date=None)
            day: date = latest.snapshot_id
            share_by_city = _shares(conn, day, role)
            cell_rows = _cells(conn, day, role)
            sources = _sources(conn, day)
        total = cell_rows.get(NATIONWIDE)
        if not share_by_city or total is None or total[0] == 0:
            raise UnknownCell("Vai trò đã chọn không có tin nào ở snapshot này.", snapshot_date=day)

        order = {city: i for i, city in enumerate(self._rules.city_codes.values())}
        cities = sorted(share_by_city, key=lambda c: (order.get(c, len(order)), c))
        min_sample = self._rules.min_sample
        rows = []
        for city in cities:
            cell_id = f"{city}.{role}"
            if city not in cell_rows:
                raise RuntimeError(f"stat_cells thiếu ô {cell_id} của snapshot {day.isoformat()}.")
            display = suppression_for(MeasureKind.COMPOSITION_SHARE, cell_rows[city][0], min_sample=min_sample)
            share = Stat(value=share_by_city[city], kind=MeasureKind.COMPOSITION_SHARE, display=display, cell_id=cell_id)
            rows.append(CityShareRow(city=city, share=share))
        total_cell_id = f"{NATIONWIDE}.{role}"
        cells = {
            f"{scope}.{role}": CellMeta(
                n=n,
                fallback_label=None,
                seniority_mix=mix,
                n_by_measure={},
                insufficient_by_measure={},
            )
            for scope, (n, mix) in ((NATIONWIDE, total), *((c, cell_rows[c]) for c in cities))
        }
        meta = Meta(
            snapshot_date=day,
            snapshot_status=SnapshotStatus(latest.status),
            sources=sources,
            sources_failed=list(latest.sources_failed),
            thresholds=Thresholds(
                min_sample=min_sample, theta_core=self._rules.theta_core, theta_common=self._rules.theta_common
            ),
            coverage_notes=[
                CoverageNote(code=n.code, text=n.text.replace("{n}", str(len(sources))))
                for n in self._rules.coverage_notes
            ],
            cells=cells,
        )
        data = CitySharesData(role=role, total_cell_id=total_cell_id, rows=rows)
        return Envelope[CitySharesData](data=data, meta=meta)

    def skill_rates(self, *, role: str, level: str) -> Envelope[SkillRatesData]:
        raise UnknownCell("Tỷ lệ kỹ năng chưa có số liệu thật.", snapshot_date=None)


def _latest_readable(conn: Connection) -> Any:
    has_shares = sa.exists().where(stat_city_shares.c.snapshot_id == snapshots.c.snapshot_id)
    has_sources = sa.exists().where(stat_sources.c.snapshot_id == snapshots.c.snapshot_id)
    stmt = (
        sa.select(snapshots.c.snapshot_id, snapshots.c.status, snapshots.c.sources_failed)
        .where(snapshots.c.status.in_(READABLE), has_shares, has_sources)
        .order_by(snapshots.c.snapshot_id.desc())
        .limit(1)
    )
    return conn.execute(stmt).one_or_none()


def _shares(conn: Connection, day: date, role: str) -> dict[str, float]:
    t = stat_city_shares
    stmt = sa.select(t.c.city, t.c.share).where(t.c.snapshot_id == day, t.c.role == role)
    return {r.city: r.share for r in conn.execute(stmt)}


def _cells(conn: Connection, day: date, role: str) -> dict[str, tuple[int, dict[str, int]]]:
    t = stat_cells
    stmt = sa.select(t.c.scope, t.c.n, t.c.seniority_mix).where(
        t.c.snapshot_id == day, t.c.role == role, t.c.branch == ALL, t.c.seniority == ALL
    )
    return {r.scope: (r.n, dict(r.seniority_mix)) for r in conn.execute(stmt)}


def _sources(conn: Connection, day: date) -> list[str]:
    stmt = sa.select(stat_sources.c.source).where(stat_sources.c.snapshot_id == day).order_by(stat_sources.c.source)
    return list(conn.execute(stmt).scalars())
