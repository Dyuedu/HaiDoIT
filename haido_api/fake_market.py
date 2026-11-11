"""Bản giả của `MarketReadModel`: đọc `fixtures/fake_market.json`.

Fixture chỉ chứa số thô: `n` của từng ô, giá trị tỷ trọng/tỷ lệ, ngưỡng. Mọi trạng thái hiển
thị (`display`, `insufficient_by_measure`) do `suppression_for` tính từ `n` và
`thresholds.min_sample` của fixture; dưới ngưỡng thì bản giả tự ẩn giá trị.

Bản giả không chọn ô và không quay về (phép 2 của registry, #3/#17): fixture ánh xạ thẳng
tham số sang ô đã dùng, và `fallback_label` lấy nguyên văn.
"""

import json
from datetime import date
from pathlib import Path
from typing import Any

from haido_api.market_source import UnknownCell
from haido_api.schemas.market import (
    CityShareRow,
    CitySharesData,
    NewcomerRoleRow,
    NewcomerRolesData,
    SkillRateRow,
    SkillRatesData,
)
from haido_core.domain.display_policy import DisplayState, MeasureKind, suppression_for
from haido_core.domain.envelope import (
    CellMeta,
    CoverageNote,
    Envelope,
    Meta,
    SnapshotStatus,
    Stat,
    Thresholds,
)

FIXTURE = Path(__file__).parent / "fixtures" / "fake_market.json"


class FakeMarket:
    """Nguồn giả cho mọi phép. Đọc fixture một lần lúc khởi tạo."""

    def __init__(self, fixture: Path = FIXTURE) -> None:
        raw: dict[str, Any] = json.loads(fixture.read_text(encoding="utf-8"))
        snapshot = raw["snapshot"]
        self._snapshot_date = date.fromisoformat(snapshot["snapshot_date"])
        self._snapshot_status = SnapshotStatus(snapshot["snapshot_status"])
        self._sources: list[str] = snapshot["sources"]
        self._sources_failed: list[str] = snapshot["sources_failed"]
        self._thresholds = Thresholds.model_validate(snapshot["thresholds"])
        self._coverage_notes = [CoverageNote.model_validate(c) for c in snapshot["coverage_notes"]]
        self._cells: dict[str, dict[str, Any]] = raw["cells"]
        self._city_shares: dict[str, dict[str, Any]] = raw["city_shares"]
        self._skill_rates: dict[str, dict[str, dict[str, Any]]] = raw["skill_rates"]
        self._newcomer_roles: dict[str, Any] = raw["newcomer_roles"]

    def city_shares(self, *, role: str) -> Envelope[CitySharesData]:
        entry = self._city_shares.get(role)
        if entry is None:
            raise UnknownCell(
                "Không có ô thống kê nào cho vai trò đã chọn.",
                snapshot_date=self._snapshot_date,
            )
        rows = [
            CityShareRow(
                city=row["city"],
                share=self._stat(row["share"], MeasureKind.COMPOSITION_SHARE, row["cell_id"]),
            )
            for row in entry["rows"]
        ]
        data = CitySharesData(role=role, total_cell_id=entry["total_cell_id"], rows=rows)
        cell_ids = [entry["total_cell_id"], *(row["cell_id"] for row in entry["rows"])]
        return Envelope[CitySharesData](data=data, meta=self._meta(cell_ids, {}))

    def skill_rates(self, *, role: str, level: str) -> Envelope[SkillRatesData]:
        entry = self._skill_rates.get(role, {}).get(level)
        if entry is None:
            raise UnknownCell(
                "Không có ô thống kê nào cho vai trò và cấp bậc đã chọn.",
                snapshot_date=self._snapshot_date,
            )
        cell_id: str = entry["cell_id"]
        rows = []
        for row in entry["rows"]:
            rate = self._stat(row["rate"], MeasureKind.SKILL_RATE, cell_id)
            group = None if rate.display is DisplayState.NULL_DATA else row["group"]
            rows.append(SkillRateRow(skill=row["skill"], rate=rate, group=group))
        data = SkillRatesData(role=role, level=level, cell_id=cell_id, rows=rows)
        meta = self._meta([cell_id], {cell_id: entry["fallback_label"]})
        return Envelope[SkillRatesData](data=data, meta=meta)

    def newcomer_roles(self) -> Envelope[NewcomerRolesData]:
        rows = [
            NewcomerRoleRow(
                role=row["role"],
                total_cell_id=row["total_cell_id"],
                entry_cell_id=row["entry_cell_id"],
                share=self._stat(row["share"], MeasureKind.LEVEL_SHARE, row["total_cell_id"]),
            )
            for row in self._newcomer_roles["rows"]
        ]
        # Thứ tự hiển thị do máy chủ quyết: dòng có tỷ lệ trước, rồi số tin entry-level giảm dần,
        # rồi mã vai trò. Bản thật (#146) theo cùng quy tắc.
        rows.sort(
            key=lambda r: (
                r.share.display is DisplayState.NULL_DATA,
                -self._cells[r.entry_cell_id]["n"],
                r.role,
            )
        )
        data = NewcomerRolesData(levels=self._newcomer_roles["levels"], rows=rows)
        cell_ids = [cid for r in rows for cid in (r.total_cell_id, r.entry_cell_id)]
        return Envelope[NewcomerRolesData](data=data, meta=self._meta(cell_ids, {}))

    def _stat(self, value: float | None, kind: MeasureKind, cell_id: str) -> Stat:
        display = suppression_for(
            kind, self._cells[cell_id]["n"], min_sample=self._thresholds.min_sample
        )
        return Stat(
            value=None if display is DisplayState.NULL_DATA else value,
            kind=kind,
            display=display,
            cell_id=cell_id,
        )

    def _meta(self, cell_ids: list[str], fallback_labels: dict[str, str | None]) -> Meta:
        return Meta(
            snapshot_date=self._snapshot_date,
            snapshot_status=self._snapshot_status,
            sources=self._sources,
            sources_failed=self._sources_failed,
            thresholds=self._thresholds,
            coverage_notes=self._coverage_notes,
            cells={cid: self._cell_meta(cid, fallback_labels.get(cid)) for cid in cell_ids},
        )

    def _cell_meta(self, cell_id: str, fallback_label: str | None) -> CellMeta:
        cell = self._cells[cell_id]
        n_by_measure: dict[str, int] = cell["n_by_measure"]
        # Ba thước đo của mục ô (số kỹ năng, số năm, lương) đều là phân vị (FR-30).
        insufficient = {
            measure: suppression_for(
                MeasureKind.PERCENTILE, n, min_sample=self._thresholds.min_sample
            )
            is DisplayState.NULL_DATA
            for measure, n in n_by_measure.items()
        }
        return CellMeta(
            n=cell["n"],
            fallback_label=fallback_label,
            seniority_mix=cell["seniority_mix"],
            n_by_measure=n_by_measure,
            insufficient_by_measure=insufficient,
        )
