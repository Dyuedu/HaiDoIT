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
- Tỷ lệ kỹ năng (#151, #103, #106): `stat_skill_rates` của snapshot đọc được mới nhất (`published` hoặc `partial`, có
  nguồn, có hàng tỷ lệ). Chỉ ô toàn quốc, nhánh `all`, số năm `any`. Ô được chọn bằng phép 2 (`CellSelector`, thân hàm ở
  `haido_core/domain/cells.py`) theo `n_scanned` (AD-17), không theo `n` của ô: `meta.cells[...].n` là `n` của
  `stat_cells`, `n_by_measure.skill_count` là `n_scanned`, `fallback_label` là nhãn của phép 2. Nhóm bằng phép 4 với θ của
  `config/rules.toml` (#102 sẽ đóng băng θ). Dòng chỉ gồm `core` và `common`, tỷ lệ giảm dần rồi mã. Không tập nào đủ
  ngưỡng thì dòng là kỹ năng có `n_with > 0` của ô cuối, theo mã, mọi tỷ lệ `null_data` và `group = null`. Chỉ đọc bảng
  `stat_*` theo khóa; không cộng lại từ bảng tin (AD-7).
- Màn người mới (#145, #146): snapshot đọc được mới nhất có hàng cấp `entry`. Số tin entry-level của một vai trò là
  `n` của ô `vn` ở nhóm cấp `entry` (Intern + Fresher + Junior, do `aggregate` ghi); n của vai trò là ô `vn` ở `all`.
  Mọi vai trò của `config/rules.toml` có một dòng; vai trò không có hàng ở snapshot đó là 0 tin. Tỷ lệ là `level_share`,
  dưới ngưỡng thì `null_data` theo `suppression_for`. Thứ tự dòng do máy chủ quyết như bản giả.
- Kỹ năng theo vai trò (#168, #166): cùng snapshot đọc được như tỷ lệ kỹ năng. Mỗi vai trò của `config/rules.toml` một
  dòng: tỷ lệ là `rate` của hàng entry (`n_with / n_scanned`, do `aggregate` ghi, #101). Cỡ mẫu của phép đo là
  `n_scanned`, ở `meta.cells[vn.<role>.entry].n_by_measure.skill_count`; `n` của ô là `n` của `stat_cells`. Dưới ngưỡng
  (theo `n_scanned`) thì `null_data`; vai trò không có ô entry có `n = 0`. `mentioned` là `n_with > 0` của hàng vai trò
  `all` ở cấp `all` (mọi cấp, AC 4 của #113). Kỹ năng không có hàng nào ở snapshot là `UnknownCell` kèm ngày.
  `n_scanned` lớn hơn `n` của ô, hoặc vai trò có `n_with > 0` ở cấp entry khi hàng `all` × `all` có `n_with = 0`, là dữ
  liệu hỏng (`RuntimeError`). Mã kỹ năng ngoài bộ từ vựng là `UnknownSkill`, kiểm trước khi mở kết nối. Chỉ đọc `stat_*` theo khóa (AD-7).
"""

import threading
from collections.abc import Callable, Collection
from datetime import date
from typing import Any

import sqlalchemy as sa
from sqlalchemy import Connection, Engine

from haido_api.market_overview import OverviewCounts, build_market_overview
from haido_api.market_source import UnknownCell, UnknownSkill
from haido_api.schemas.learning_path import LearningPathData
from haido_api.schemas.market import (
    CityShareRow,
    CitySharesData,
    MarketOverviewData,
    NewcomerRoleRow,
    NewcomerRolesData,
    SkillLabel,
    SkillRateRow,
    SkillRatesData,
    SkillRoleRow,
    SkillRolesData,
)
from haido_core.config import RulesConfig, load_rules
from haido_core.db.engine import make_read_engine
from haido_core.db.tables import (
    snapshots,
    stat_cells,
    stat_city_shares,
    stat_skill_rates,
    stat_sources,
)
from haido_core.domain.cells import CellSelector, CellStats
from haido_core.domain.display_policy import DisplayState, MeasureKind, suppression_for
from haido_core.domain.envelope import (
    SKILL_COUNT,
    CellMeta,
    CoverageNote,
    Envelope,
    Meta,
    SnapshotStatus,
    Stat,
    Thresholds,
)
from haido_core.domain.registry import (
    CellChoice,
    CellKey,
    CellQuery,
    SkillBand,
    SkillGroupRequest,
    SkillRate,
)
from haido_core.domain.skill_groups import SkillGrouper
from haido_core.vocab.skills import find_seed_skill

READABLE = ("published", "partial")
NATIONWIDE = "vn"
ALL = "all"
ANY = "any"
ENTRY = "entry"
SKILL_SAMPLE_NOUN = "tin đọc được kỹ năng"  # `n_scanned` không phải `n` của ô: nhãn phải nói đúng con số nào
UNKNOWN_LEVEL = "unknown"


class StatMarket:
    """Bản thật của `MarketReadModel` cho `city_shares`, `newcomer_roles` (#145, #146), `skill_rates` (#151) và `skill_roles` (#168). `learning_path` (#216) chưa có số thật."""

    def __init__(
        self, *, engine_factory: Callable[[], Engine] | None = None, rules: RulesConfig | None = None
    ) -> None:
        self._factory = engine_factory if engine_factory is not None else make_read_engine
        self._rules = rules if rules is not None else load_rules()
        self._engine: Engine | None = None
        self._lock = threading.Lock()
        self._names = _display_names(self._rules)
        self._mid_and_above = _mid_and_above(self._rules)

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

    def skill_rates(
        self, *, role: str, level: str, have: Collection[str] = ()
    ) -> Envelope[SkillRatesData]:
        rules = self._rules
        min_sample = rules.min_sample
        with self._db().connect() as conn:
            latest = _latest_with_skill_rates(conn)
            if latest is None:
                raise UnknownCell("Chưa có snapshot nào đã công bố có tỷ lệ kỹ năng.", snapshot_date=None)
            day: date = latest.snapshot_id
            if role not in rules.roles:
                raise UnknownCell("Không có ô thống kê nào cho vai trò đã chọn.", snapshot_date=day)
            stats = _skill_cell_stats(conn, day, role)
            sources = _sources(conn, day)

            def lookup(cell: CellKey) -> CellStats | None:
                if cell.scope != NATIONWIDE or cell.branch not in (None, ALL):
                    return None
                return stats.get(cell.seniority or ALL)

            selector = CellSelector(
                lookup,
                level_groups=rules.level_groups,
                names=self._names,
                mid_and_above=self._mid_and_above,
                sample_noun=SKILL_SAMPLE_NOUN,
            )
            query = CellQuery(CellKey(day.isoformat(), role, ALL, level, NATIONWIDE), min_sample)
            choice = selector.select_cell(query)
            assert isinstance(choice, CellChoice)
            chosen_level = choice.cell.seniority or ALL
            chosen = stats.get(chosen_level)
            if chosen is None or chosen.n == 0:
                raise UnknownCell("Vai trò đã chọn không có tin nào ở cấp bậc này của snapshot này.", snapshot_date=day)
            rate_rows = _skill_rate_rows(conn, day, role, chosen_level)
            if not rate_rows:
                raise UnknownCell(
                    f"Snapshot {day.isoformat()} có ô thống kê của vai trò đã chọn nhưng chưa có tỷ lệ kỹ năng nào.",
                    snapshot_date=day,
                )

        cell_id = f"{NATIONWIDE}.{role}" + ("" if chosen_level == ALL else f".{chosen_level}")
        scanned = choice.n
        enough = scanned >= min_sample
        display = suppression_for(MeasureKind.SKILL_RATE, scanned, min_sample=min_sample)
        owned = set(have)
        rows: list[SkillRateRow] = []
        if enough:
            grouped = SkillGrouper().group_skills(
                SkillGroupRequest(
                    tuple(SkillRate(skill, rate) for skill, _, rate in rate_rows), rules.theta_core, rules.theta_common
                )
            )
            assert isinstance(grouped, tuple)
            bands = {g.skill_id: g.band for g in grouped}
            shown = [(skill, rate) for skill, _, rate in rate_rows if bands[skill] is not SkillBand.RARE]
            shown.sort(key=lambda item: (-item[1], item[0]))
            for skill, rate in shown:
                stat = Stat(value=rate, kind=MeasureKind.SKILL_RATE, display=display, cell_id=cell_id)
                rows.append(SkillRateRow(skill=skill, rate=stat, group=bands[skill].value, have=skill in owned))
        else:
            # Không tập nào đủ ngưỡng: kỹ năng có nhắc, theo mã. Thứ tự không mang xếp hạng.
            # Không kỹ năng nào được nhắc thì liệt kê mọi mã của ô: web coi `rows` rỗng là response hỏng.
            mentioned = [row for row in rate_rows if row[1] > 0] or rate_rows
            for skill, _, _ in sorted(mentioned):
                stat = Stat(value=None, kind=MeasureKind.SKILL_RATE, display=display, cell_id=cell_id)
                rows.append(SkillRateRow(skill=skill, rate=stat, group=None, have=skill in owned))
        core = [r for r in rows if r.group == SkillBand.CORE.value]
        data = SkillRatesData(
            role=role,
            level=level,
            cell_id=cell_id,
            rows=rows,
            core_size=len(core) if enough else None,
            have_core=sum(r.have for r in core) if enough else None,
        )
        cell = CellMeta(
            n=chosen.n,
            fallback_label=choice.label,
            seniority_mix=dict(chosen.seniority_mix),
            n_by_measure={SKILL_COUNT: scanned},
            insufficient_by_measure={SKILL_COUNT: not enough},
        )
        meta = Meta(
            snapshot_date=day,
            snapshot_status=SnapshotStatus(latest.status),
            sources=sources,
            sources_failed=list(latest.sources_failed),
            thresholds=Thresholds(min_sample=min_sample, theta_core=rules.theta_core, theta_common=rules.theta_common),
            coverage_notes=[
                CoverageNote(code=n.code, text=n.text.replace("{n}", str(len(sources)))) for n in rules.coverage_notes
            ],
            cells={cell_id: cell},
        )
        return Envelope[SkillRatesData](data=data, meta=meta)

    def newcomer_roles(self) -> Envelope[NewcomerRolesData]:
        levels = self._rules.level_groups.get(ENTRY)
        if not levels:
            raise RuntimeError(f"config/rules.toml thiếu nhóm cấp bậc {ENTRY!r} trong level_groups.")
        with self._db().connect() as conn:
            latest = _latest_readable(conn, ENTRY)
            if latest is None:
                raise UnknownCell("Chưa có snapshot nào đã công bố được tính cho nhóm mới vào nghề.", snapshot_date=None)
            day: date = latest.snapshot_id
            totals = _national_cells(conn, day, ALL)
            entries = _national_cells(conn, day, ENTRY)
            sources = _sources(conn, day)

        min_sample = self._rules.min_sample
        cells: dict[str, CellMeta] = {}
        rows: list[NewcomerRoleRow] = []
        for role in self._rules.roles:
            # Vai trò không có hàng ở snapshot này (chưa có tin nào): 0 tin, n = 0.
            total_n, total_mix = totals.get(role, (0, {}))
            entry_n, entry_mix = entries.get(role, (0, {}))
            total_cell_id, entry_cell_id = f"{NATIONWIDE}.{role}", f"{NATIONWIDE}.{role}.{ENTRY}"
            cells[total_cell_id] = _cell_meta(total_n, total_mix)
            cells[entry_cell_id] = _cell_meta(entry_n, entry_mix)
            if entry_n > total_n:
                raise RuntimeError(
                    f"stat_cells của snapshot {day.isoformat()} sai: vai trò {role} có {entry_n} tin entry-level "
                    f"nhiều hơn {total_n} tin của vai trò."
                )
            display = suppression_for(MeasureKind.LEVEL_SHARE, total_n, min_sample=min_sample)
            value = None if display is DisplayState.NULL_DATA else entry_n / total_n
            share = Stat(value=value, kind=MeasureKind.LEVEL_SHARE, display=display, cell_id=total_cell_id)
            rows.append(
                NewcomerRoleRow(role=role, total_cell_id=total_cell_id, entry_cell_id=entry_cell_id, share=share)
            )
        # Thứ tự hiển thị do máy chủ quyết (#144): dòng có tỷ lệ trước, rồi số tin entry-level giảm dần, rồi mã.
        rows.sort(key=lambda r: (r.share.display is DisplayState.NULL_DATA, -cells[r.entry_cell_id].n, r.role))
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
        return Envelope[NewcomerRolesData](data=NewcomerRolesData(levels=list(levels), rows=rows), meta=meta)

    def market_overview(self) -> Envelope[MarketOverviewData]:
        rules = self._rules
        with self._db().connect() as conn:
            latest = _latest_readable(conn, ALL)
            if latest is None:
                raise UnknownCell("Chưa có snapshot nào đã công bố để dựng toàn cảnh thị trường.", snapshot_date=None)
            day: date = latest.snapshot_id
            rows = _overview_rows(conn, day)
            sources = _sources(conn, day)
        national = {(r.role, r.seniority): r for r in rows if r.scope == NATIONWIDE and r.years == ANY}
        total = national.get((ALL, ALL))
        if total is None or total.n == 0:
            raise UnknownCell("Snapshot đã chọn không có tin nào để dựng toàn cảnh.", snapshot_date=day)
        entry = national.get((ALL, ENTRY))
        by_years = {r.years: r for r in rows if r.scope == NATIONWIDE and r.role == ALL and r.seniority == ALL}
        counts = OverviewCounts(
            total_n=total.n,
            total_mix=dict(total.seniority_mix),
            entry_n=entry.n if entry is not None else 0,
            roles={
                role: (national[(role, ALL)].n, dict(national[(role, ALL)].seniority_mix))
                for role in rules.roles
                if (role, ALL) in national
            },
            role_entry={role: national[(role, ENTRY)].n for role in rules.roles if (role, ENTRY) in national},
            places={
                r.scope: r.n
                for r in rows
                if r.role == ALL and r.seniority == ALL and r.years == ANY and r.scope != NATIONWIDE
            },
            role_places=_role_places(rows),
            years_upto={int(y): by_years[str(y)].n for y in rules.years_options if str(y) in by_years},
            # mọi ô mốc số năm của vn.all ghi cùng một số tin không ghi số năm (#280)
            years_unstated=next((r.years_unstated for y, r in by_years.items() if y != ANY), 0),
        )
        data, cells = build_market_overview(counts, rules)
        meta = Meta(
            snapshot_date=day,
            snapshot_status=SnapshotStatus(latest.status),
            sources=sources,
            sources_failed=list(latest.sources_failed),
            thresholds=Thresholds(min_sample=rules.min_sample, theta_core=rules.theta_core, theta_common=rules.theta_common),
            coverage_notes=[
                CoverageNote(code=n.code, text=n.text.replace("{n}", str(len(sources)))) for n in rules.coverage_notes
            ],
            cells=cells,
        )
        return Envelope[MarketOverviewData](data=data, meta=meta)

    def learning_path(self, *, role: str, level: str, have: Collection[str]) -> Envelope[LearningPathData]:
        raise UnknownCell("Lộ trình học chưa có số liệu thật.", snapshot_date=None)

    def skill_roles(self, *, skill: str) -> Envelope[SkillRolesData]:
        rules = self._rules
        levels = rules.level_groups.get(ENTRY)
        if not levels:
            raise RuntimeError(f"config/rules.toml thiếu nhóm cấp bậc {ENTRY!r} trong level_groups.")
        label = find_seed_skill(skill)
        if label is None:
            raise UnknownSkill("Kỹ năng đã chọn không có trong bộ từ vựng.")
        min_sample = rules.min_sample
        with self._db().connect() as conn:
            latest = _latest_with_skill_rates(conn)
            if latest is None:
                raise UnknownCell("Chưa có snapshot nào đã công bố có tỷ lệ kỹ năng.", snapshot_date=None)
            day: date = latest.snapshot_id
            mentioned_n, scanned_by_role, rate_by_role, with_by_role = _skill_role_rows(conn, day, skill)
            if mentioned_n is None:
                raise UnknownCell("Snapshot đã chọn không có số liệu nào của kỹ năng đã chọn.", snapshot_date=day)
            entries = _national_cells(conn, day, ENTRY)
            sources = _sources(conn, day)
        if mentioned_n == 0:
            stray = sorted(role for role, n_with in with_by_role.items() if n_with > 0)
            if stray:
                raise RuntimeError(
                    f"stat_skill_rates của snapshot {day.isoformat()} sai: kỹ năng {skill} có n_with = 0 ở vai trò all "
                    f"và cấp all nhưng vai trò {', '.join(stray)} có n_with > 0 ở cấp entry."
                )

        cells: dict[str, CellMeta] = {}
        rows: list[SkillRoleRow] = []
        for role in rules.roles:
            n, mix = entries.get(role, (0, {}))
            scanned = scanned_by_role.get(role, 0)
            if scanned > n:
                raise RuntimeError(
                    f"stat_skill_rates của snapshot {day.isoformat()} sai: vai trò {role} có n_scanned = {scanned} "
                    f"lớn hơn {n} tin entry-level của ô."
                )
            cell_id = f"{NATIONWIDE}.{role}.{ENTRY}"
            display = suppression_for(MeasureKind.SKILL_RATE, scanned, min_sample=min_sample)
            value = None if display is DisplayState.NULL_DATA else rate_by_role.get(role, 0.0)
            cells[cell_id] = CellMeta(
                n=n,
                fallback_label=None,
                seniority_mix=mix,
                n_by_measure={SKILL_COUNT: scanned},
                insufficient_by_measure={SKILL_COUNT: scanned < min_sample},
            )
            share = Stat(value=value, kind=MeasureKind.SKILL_RATE, display=display, cell_id=cell_id)
            rows.append(SkillRoleRow(role=role, share=share))
        # Thứ tự như bản giả (#166): dòng có tỷ lệ trước (giảm dần rồi mã); dòng `null_data` sau, cỡ mẫu của phép đo
        # giảm dần rồi mã.
        rows.sort(
            key=lambda r: (
                r.share.display is DisplayState.NULL_DATA,
                -(r.share.value or 0.0),
                -cells[r.share.cell_id].n_by_measure[SKILL_COUNT] if r.share.display is DisplayState.NULL_DATA else 0,
                r.role,
            )
        )
        meta = Meta(
            snapshot_date=day,
            snapshot_status=SnapshotStatus(latest.status),
            sources=sources,
            sources_failed=list(latest.sources_failed),
            thresholds=Thresholds(min_sample=min_sample, theta_core=rules.theta_core, theta_common=rules.theta_common),
            coverage_notes=[
                CoverageNote(code=n.code, text=n.text.replace("{n}", str(len(sources)))) for n in rules.coverage_notes
            ],
            cells=cells,
        )
        data = SkillRolesData(
            skill=SkillLabel(code=label.code, name_en=label.name_en, name_vi=label.name_vi),
            level=ENTRY,
            levels=list(levels),
            mentioned=mentioned_n > 0,
            rows=rows,
        )
        return Envelope[SkillRolesData](data=data, meta=meta)


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


def _national_cells(conn: Connection, day: date, level: str) -> dict[str, tuple[int, dict[str, int]]]:
    """`n` và cơ cấu cấp bậc của ô toàn quốc mỗi vai trò ở cấp lọc `level`, mọi số năm (#145).

    Ô `entry` do `aggregate` ghi với `n` = Intern + Fresher + Junior; ở đây chỉ đọc, không cộng lại.
    """
    t = stat_cells
    stmt = sa.select(t.c.role, t.c.n, t.c.seniority_mix).where(
        t.c.snapshot_id == day,
        t.c.scope == NATIONWIDE,
        t.c.branch == ALL,
        t.c.seniority == level,
        t.c.years == ANY,
        t.c.role != ALL,
    )
    return {r.role: (r.n, dict(r.seniority_mix)) for r in conn.execute(stmt)}


def _overview_rows(conn: Connection, day: date) -> list[Any]:
    """Các ô mà toàn cảnh (#328) dùng, mọi ngành (`branch = all`): ô mọi số năm ở cấp `all` và `entry` của mọi vai trò
    và mọi nơi, cộng các ô mốc số năm của `vn.all`. Chỉ đọc `n`, không đếm lại."""
    t = stat_cells
    stmt = sa.select(t.c.role, t.c.scope, t.c.seniority, t.c.years, t.c.n, t.c.seniority_mix, t.c.years_unstated).where(
        t.c.snapshot_id == day,
        t.c.branch == ALL,
        sa.or_(
            sa.and_(t.c.years == ANY, t.c.seniority.in_((ALL, ENTRY))),
            sa.and_(t.c.role == ALL, t.c.seniority == ALL, t.c.scope == NATIONWIDE),
        ),
    )
    return list(conn.execute(stmt))


def _role_places(rows: list[Any]) -> dict[str, dict[str, int]]:
    places: dict[str, dict[str, int]] = {}
    for r in rows:
        if r.role != ALL and r.seniority == ALL and r.years == ANY and r.scope != NATIONWIDE:
            places.setdefault(r.role, {})[r.scope] = r.n
    return places


def _cell_meta(n: int, mix: dict[str, int]) -> CellMeta:
    return CellMeta(n=n, fallback_label=None, seniority_mix=mix, n_by_measure={}, insufficient_by_measure={})


def _sources(conn: Connection, day: date) -> list[str]:
    stmt = sa.select(stat_sources.c.source).where(stat_sources.c.snapshot_id == day).order_by(stat_sources.c.source)
    return list(conn.execute(stmt).scalars())


def _display_names(rules: RulesConfig) -> dict[str, str]:
    """Tên hiển thị của vai trò và cấp bậc cho nhãn của phép 2: nhãn của `[labels.*]`, nhóm cấp viết hoa chữ đầu."""
    names = {code: label for label, code in rules.role_codes.items()}
    names.update({code: label for label, code in rules.level_codes.items()})
    names.update({group: group.capitalize() for group in rules.level_groups})
    names[ALL] = "mọi cấp"
    return names


def _mid_and_above(rules: RulesConfig) -> tuple[str, ...]:
    """Cấp thô không thuộc nhóm nào và không phải `unknown`: Mid, Senior, Lead (FR-19)."""
    grouped = {level for members in rules.level_groups.values() for level in members}
    return tuple(code for code in rules.level_codes.values() if code not in grouped and code != UNKNOWN_LEVEL)


def _latest_with_skill_rates(conn: Connection) -> Any:
    has_rates = sa.exists().where(stat_skill_rates.c.snapshot_id == snapshots.c.snapshot_id)
    has_sources = sa.exists().where(stat_sources.c.snapshot_id == snapshots.c.snapshot_id)
    stmt = (
        sa.select(snapshots.c.snapshot_id, snapshots.c.status, snapshots.c.sources_failed)
        .where(snapshots.c.status.in_(READABLE), has_rates, has_sources)
        .order_by(snapshots.c.snapshot_id.desc())
        .limit(1)
    )
    return conn.execute(stmt).one_or_none()


def _skill_cell_stats(conn: Connection, day: date, role: str) -> dict[str, CellStats]:
    """Mọi ô toàn quốc của một vai trò (nhánh `all`, số năm `any`): `n`, cơ cấu cấp và `n_scanned`, theo cấp lọc."""
    c, r = stat_cells, stat_skill_rates
    cells = sa.select(c.c.seniority, c.c.n, c.c.seniority_mix).where(
        c.c.snapshot_id == day, c.c.role == role, c.c.branch == ALL, c.c.years == ANY, c.c.scope == NATIONWIDE
    )
    # `n_scanned` ghi cùng giá trị ở mọi hàng của ô (#101): đọc giá trị đã ghi, không tính lại, và không chọn ngầm
    # một giá trị khi các hàng khác nhau (dữ liệu hỏng).
    scanned_stmt = (
        sa.select(r.c.seniority, r.c.n_scanned)
        .where(r.c.snapshot_id == day, r.c.role == role, r.c.branch == ALL, r.c.years == ANY, r.c.scope == NATIONWIDE)
        .distinct()
        .order_by(r.c.seniority, r.c.n_scanned)
    )
    scanned: dict[str, list[int]] = {}
    for row in conn.execute(scanned_stmt):
        scanned.setdefault(row.seniority, []).append(row.n_scanned)
    for seniority, values in scanned.items():
        if len(values) > 1:
            raise RuntimeError(
                f"n_scanned không thống nhất ở ô {role}/{seniority} của snapshot {day.isoformat()}: "
                f"{', '.join(map(str, values))} (mọi hàng của một ô phải cùng n_scanned, #101)."
            )
    return {
        row.seniority: CellStats(
            n=row.n, seniority_mix=dict(row.seniority_mix), sample_n=scanned[row.seniority][0] if row.seniority in scanned else 0
        )
        for row in conn.execute(cells)
    }


def _skill_rate_rows(conn: Connection, day: date, role: str, level: str) -> list[tuple[str, int, float]]:
    """`(kỹ năng, n_with, rate)` của một ô, như `aggregate` đã ghi."""
    r = stat_skill_rates
    stmt = sa.select(r.c.skill, r.c.n_with, r.c.rate).where(
        r.c.snapshot_id == day,
        r.c.role == role,
        r.c.branch == ALL,
        r.c.seniority == level,
        r.c.years == ANY,
        r.c.scope == NATIONWIDE,
    )
    return [(row.skill, row.n_with, row.rate) for row in conn.execute(stmt)]


def _skill_role_rows(
    conn: Connection, day: date, skill: str
) -> tuple[int | None, dict[str, int], dict[str, float], dict[str, int]]:
    """Hàng `stat_skill_rates` của một kỹ năng (#168): `(n_with của vai trò all × cấp all, n_scanned, rate và n_with theo vai trò)`.

    Một truy vấn theo khóa `(snapshot_id, skill)`, phạm vi `vn`, nhánh `all`, số năm `any`, cấp `entry` hoặc `all`. Hàng
    `role = all`, `seniority = all` là mọi tin của mọi vai trò và cấp: nguồn của `mentioned` (`None` khi kỹ năng không có
    hàng nào ở snapshot). `n_scanned` và `rate` theo vai trò lấy từ hàng cấp `entry`, như `aggregate` đã ghi.
    """
    r = stat_skill_rates
    stmt = sa.select(r.c.role, r.c.seniority, r.c.n_with, r.c.n_scanned, r.c.rate).where(
        r.c.snapshot_id == day,
        r.c.skill == skill,
        r.c.scope == NATIONWIDE,
        r.c.branch == ALL,
        r.c.years == ANY,
        r.c.seniority.in_((ENTRY, ALL)),
    )
    mentioned: int | None = None
    scanned: dict[str, int] = {}
    rates: dict[str, float] = {}
    with_: dict[str, int] = {}
    for row in conn.execute(stmt):
        if row.role == ALL and row.seniority == ALL:
            mentioned = row.n_with
        elif row.seniority == ENTRY and row.role != ALL:
            scanned[row.role] = row.n_scanned
            rates[row.role] = row.rate
            with_[row.role] = row.n_with
    return mentioned, scanned, rates, with_
