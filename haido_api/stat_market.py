"""Nguồn số liệu thật cho `GET /api/v1/city-shares` (#93).

Đọc `stat_city_shares` và `stat_cells` của snapshot đã công bố mới nhất, theo khóa. Không cộng
lại từ bảng tin, không đọc bảng của scraper (AD-5, cổng AD-7). Con số trả về là số đã ghi bởi bước
`aggregate`; `display` do `suppression_for` quyết, không tự so với ngưỡng ở đây.

- Snapshot đọc được là `published` hoặc `partial` mới nhất có `stat_city_shares` của cấp đã chọn và ít nhất một hàng
  `stat_sources` (thiếu nguồn thì web coi là không đọc được, nên bỏ qua và lùi về snapshot cũ đầy đủ). Snapshot công bố
  trước migration 0005 chỉ có hàng `all` và không sửa được, nên cấp khác `all` lùi về snapshot có hàng của cấp đó.
- `meta.sources` là `stat_sources` của snapshot đó, A–Z: các nguồn có ít nhất một tin được đếm trong cửa sổ 60 ngày
  (#259, DEC-12), do `aggregate` ghi, không phải các nguồn có lượt chạy ở S. `meta.sources_failed` lấy từ snapshot.
- Ngưỡng và lưu ý độ phủ lấy từ `config/rules.toml`.
- Kết nối mở ở yêu cầu đầu tiên, không mở lúc import hay lúc dựng nguồn.
- Cấp bậc lọc (#163): `level` chọn hàng `seniority = level` của hai bảng; `all` là mọi cấp. Mã ô là `<scope>.<role>` ở
  `all` và `<scope>.<role>.<level>` ở cấp khác. Mẫu nhỏ theo n của ô ở cấp đã chọn.
- Vai trò không có tin nào ở snapshot đã chọn ở cấp đã chọn (n toàn quốc bằng 0) thì `UnknownCell` kèm ngày snapshot;
  không có snapshot nào đọc được cho cấp đó thì `UnknownCell` không có ngày.
- Mốc số năm (#280): `years` chọn hàng `years = years` của hai bảng, cùng cách với cấp. Mã ô thêm đuôi `.y<N>` khi
  `years` khác `any`. Ở một mốc, `data.years_unstated_cell_id` trỏ tới ô `vn.<role>[.<level>].ynone` có `n` là
  `years_unstated` của ô toàn quốc (do `aggregate` ghi, không đếm ở đây).
  Snapshot công bố trước migration 0006 chỉ có hàng `any`, nên mốc khác lùi về snapshot có hàng của mốc đó.
"""

import threading
from collections.abc import Callable
from datetime import date
from typing import Any

import sqlalchemy as sa
from sqlalchemy import Connection, Engine

from haido_api.market_source import UnknownCell
from haido_api.schemas.market import (
    CityShareRow,
    CitySharesData,
    NewcomerRolesData,
    SkillRatesData,
)
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
ANY = "any"


class StatMarket:
    """Bản thật của `MarketReadModel` cho `city_shares`. `skill_rates` (#101) và `newcomer_roles` (#145, #146) chưa có số thật."""

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

    def city_shares(self, *, role: str, level: str = ALL, years: str = ANY) -> Envelope[CitySharesData]:
        with self._db().connect() as conn:
            latest = _latest_readable(conn, level, years)
            if latest is None:
                raise UnknownCell(
                    "Chưa có snapshot nào đã công bố được tính cho cấp bậc và bộ lọc số năm này.", snapshot_date=None
                )
            day: date = latest.snapshot_id
            share_by_city = _shares(conn, day, role, level, years)
            cell_rows = _cells(conn, day, role, level, years)
            sources = _sources(conn, day)
        total = cell_rows.get(NATIONWIDE)
        if not share_by_city or total is None or total[0] == 0:
            raise UnknownCell("Vai trò đã chọn không có tin nào ở cấp bậc này của snapshot này.", snapshot_date=day)

        order = {city: i for i, city in enumerate(self._rules.city_codes.values())}
        cities = sorted(share_by_city, key=lambda c: (order.get(c, len(order)), c))
        min_sample = self._rules.min_sample
        # mã ô của mọi cấp và mọi số năm giữ nguyên `<scope>.<role>`
        suffix = ("" if level == ALL else f".{level}") + ("" if years == ANY else f".y{years}")
        rows = []
        for city in cities:
            cell_id = f"{city}.{role}{suffix}"
            if city not in cell_rows:
                raise RuntimeError(f"stat_cells thiếu ô {cell_id} của snapshot {day.isoformat()}.")
            display = suppression_for(MeasureKind.COMPOSITION_SHARE, cell_rows[city][0], min_sample=min_sample)
            share = Stat(value=share_by_city[city], kind=MeasureKind.COMPOSITION_SHARE, display=display, cell_id=cell_id)
            rows.append(CityShareRow(city=city, share=share))
        total_cell_id = f"{NATIONWIDE}.{role}{suffix}"
        cells = {
            f"{scope}.{role}{suffix}": CellMeta(
                n=n,
                fallback_label=None,
                seniority_mix=mix,
                n_by_measure={},
                insufficient_by_measure={},
            )
            for scope, (n, mix, _) in ((NATIONWIDE, total), *((c, cell_rows[c]) for c in cities))
        }
        unstated_cell_id = None
        if years != ANY:
            level_part = "" if level == ALL else f".{level}"
            unstated_cell_id = f"{NATIONWIDE}.{role}{level_part}.ynone"
            cells[unstated_cell_id] = CellMeta(
                n=total[2], fallback_label=None, seniority_mix={}, n_by_measure={}, insufficient_by_measure={}
            )
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
        data = CitySharesData(
            role=role,
            level=level,
            years=years,
            years_unstated_cell_id=unstated_cell_id,
            total_cell_id=total_cell_id,
            rows=rows,
        )
        return Envelope[CitySharesData](data=data, meta=meta)

    def skill_rates(self, *, role: str, level: str) -> Envelope[SkillRatesData]:
        raise UnknownCell("Tỷ lệ kỹ năng chưa có số liệu thật.", snapshot_date=None)

    def newcomer_roles(self) -> Envelope[NewcomerRolesData]:
        raise UnknownCell("Số tin cho người mới chưa có số liệu thật.", snapshot_date=None)


def _latest_readable(conn: Connection, level: str, years: str = ANY) -> Any:
    has_shares = sa.exists().where(
        stat_city_shares.c.snapshot_id == snapshots.c.snapshot_id,
        stat_city_shares.c.seniority == level,
        stat_city_shares.c.years == years,
    )
    has_sources = sa.exists().where(stat_sources.c.snapshot_id == snapshots.c.snapshot_id)
    stmt = (
        sa.select(snapshots.c.snapshot_id, snapshots.c.status, snapshots.c.sources_failed)
        .where(snapshots.c.status.in_(READABLE), has_shares, has_sources)
        .order_by(snapshots.c.snapshot_id.desc())
        .limit(1)
    )
    return conn.execute(stmt).one_or_none()


def _shares(conn: Connection, day: date, role: str, level: str, years: str) -> dict[str, float]:
    t = stat_city_shares
    stmt = sa.select(t.c.city, t.c.share).where(
        t.c.snapshot_id == day, t.c.role == role, t.c.seniority == level, t.c.years == years
    )
    return {r.city: r.share for r in conn.execute(stmt)}


def _cells(
    conn: Connection, day: date, role: str, level: str, years: str
) -> dict[str, tuple[int, dict[str, int], int]]:
    t = stat_cells
    stmt = sa.select(t.c.scope, t.c.n, t.c.seniority_mix, t.c.years_unstated).where(
        t.c.snapshot_id == day, t.c.role == role, t.c.branch == ALL, t.c.seniority == level, t.c.years == years
    )
    return {r.scope: (r.n, dict(r.seniority_mix), r.years_unstated) for r in conn.execute(stmt)}


def _sources(conn: Connection, day: date) -> list[str]:
    stmt = sa.select(stat_sources.c.source).where(stat_sources.c.snapshot_id == day).order_by(stat_sources.c.source)
    return list(conn.execute(stmt).scalars())
