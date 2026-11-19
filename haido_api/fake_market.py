"""Bản giả của `MarketReadModel`: đọc `fixtures/fake_market.json`.

`learning_path` (#212) đọc thêm `fixtures/fake_learning_path.json` (đồ thị và lời dẫn); tỷ lệ của
từng kỹ năng lấy từ `skill_rates` của `fake_market.json`, nên lộ trình và `/skill-rates` luôn khớp.

Fixture chỉ chứa số thô: `n` của từng ô, giá trị tỷ trọng/tỷ lệ, ngưỡng. Mọi trạng thái hiển
thị (`display`, `insufficient_by_measure`) do `suppression_for` tính từ `n` và
`thresholds.min_sample` của fixture; dưới ngưỡng thì bản giả tự ẩn giá trị.

`city-shares` có hai cấp bậc lọc cho mỗi vai trò: `all` và `entry` (#163); cấp khác là `unknown_cell`. Fixture đặt
`city_shares[vai trò][cấp]`. Mốc số năm (#280) chỉ có `any` ở các khóa đó, cộng khóa `"<cấp>.y<N>"` (bản giả có
`all` / `entry.y1`) mang thêm `years_unstated_cell_id`; mốc khác là `unknown_cell`.

`skill_roles` (#166) đọc `skill_roles[mã kỹ năng]`: `entry[vai trò]` = số tin entry-level của vai trò có nhắc kỹ năng, và
`mentions_all_levels` = số tin ở mọi cấp nhắc kỹ năng (`mentioned` là `mentions_all_levels > 0`, AC 4 của #113). Ô
`vn.<vai trò>.entry` trong `cells` cho `n` (số tin của ô) và `n_by_measure.skill_count` (số tin đã quét kỹ năng, mẫu số
của tỷ lệ); tỷ lệ là số nhắc chia `skill_count`. Mã kỹ năng không có trong mục đó là `unknown_cell`. Fixture lệch `config/rules.toml`
(thiếu hay thừa vai trò, thiếu ô entry) là lỗi khởi tạo `ValueError` nói rõ chỗ lệch, không phải `KeyError`.

Bản giả không chọn ô và không quay về (phép 2 của registry, #3/#17): fixture ánh xạ thẳng
tham số sang ô đã dùng, và `fallback_label` lấy nguyên văn.
"""

import json
from collections.abc import Collection
from datetime import date
from pathlib import Path
from typing import Any

from haido_api.learning_path import apply_have, foundation_targets, stage_numbers
from haido_api.market_overview import BIG_CITIES, OverviewCounts, build_market_overview
from haido_api.market_source import UnknownCell
from haido_api.schemas.learning_path import (
    LearningPathData,
    PathResource,
    PathSkill,
    PathStatus,
    order_key,
)
from haido_api.schemas.market import (
    SKILL_ROLES_LEVEL_GROUP,
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
from haido_core.config import load_rules
from haido_core.domain.display_policy import DisplayState, MeasureKind, suppression_for
from haido_core.domain.envelope import (
    CellMeta,
    CoverageNote,
    Envelope,
    Meta,
    SnapshotStatus,
    Stat,
    Thresholds,
    sample_n,
)
from haido_core.vocab.skills import find_seed_skill

FIXTURE = Path(__file__).parent / "fixtures" / "fake_market.json"
LEARNING_PATH_FIXTURE = Path(__file__).parent / "fixtures" / "fake_learning_path.json"


class FakeMarket:
    """Nguồn giả cho mọi phép. Đọc fixture một lần lúc khởi tạo."""

    def __init__(
        self,
        fixture: Path = FIXTURE,
        learning_path_fixture: Path = LEARNING_PATH_FIXTURE,
    ) -> None:
        raw: dict[str, Any] = json.loads(fixture.read_text(encoding="utf-8"))
        snapshot = raw["snapshot"]
        self._snapshot_date = date.fromisoformat(snapshot["snapshot_date"])
        self._snapshot_status = SnapshotStatus(snapshot["snapshot_status"])
        self._sources: list[str] = snapshot["sources"]
        self._sources_failed: list[str] = snapshot["sources_failed"]
        self._thresholds = Thresholds.model_validate(snapshot["thresholds"])
        self._coverage_notes = [
            CoverageNote.model_validate(c) for c in snapshot["coverage_notes"]
        ]
        self._cells: dict[str, dict[str, Any]] = raw["cells"]
        # city_shares[vai trò][cấp bậc lọc]: bản giả chỉ có `all` và `entry` (#163); cấp khác là `unknown_cell`.
        self._city_shares: dict[str, dict[str, dict[str, Any]]] = raw["city_shares"]
        self._skill_rates: dict[str, dict[str, dict[str, Any]]] = raw["skill_rates"]
        self._newcomer_roles: dict[str, Any] = raw["newcomer_roles"]
        self._skill_roles: dict[str, dict[str, Any]] = raw["skill_roles"]
        # Toàn cảnh (#327): số đếm bổ sung mà `cells` chưa có (Hà Nội/TP.HCM của vài vai trò, mốc số năm).
        self._overview: dict[str, Any] = raw["market_overview"]
        # Lộ trình học (#212): đồ thị, lời dẫn, tài nguyên. Tỷ lệ lấy từ `skill_rates` ở trên, không chép số.
        path_raw: dict[str, Any] = json.loads(
            learning_path_fixture.read_text(encoding="utf-8")
        )
        self._paths: dict[str, list[dict[str, Any]]] = {
            role: entry["skills"] for role, entry in path_raw["roles"].items()
        }
        self._roles: tuple[str, ...] = tuple(load_rules().roles)
        self._check_skill_roles()

    def _check_skill_roles(self) -> None:
        """Fixture `skill_roles` phải đủ và chỉ đủ vai trò của `config/rules.toml`, mỗi vai trò có ô entry (#166).

        Lệch là lỗi khởi tạo nói rõ chỗ lệch, để đổi config mà quên fixture không thành `KeyError` ở một request.
        """
        roles = set(self._roles)
        missing_cells = sorted(
            f"vn.{role}.{SKILL_ROLES_LEVEL_GROUP}"
            for role in roles
            if f"vn.{role}.{SKILL_ROLES_LEVEL_GROUP}" not in self._cells
        )
        if missing_cells:
            raise ValueError(
                f"fake_market.json: thiếu ô entry cho vai trò của config/rules.toml: {', '.join(missing_cells)}."
            )
        for skill, entry in self._skill_roles.items():
            counts = entry.get("entry", {})
            missing, extra = sorted(roles - set(counts)), sorted(set(counts) - roles)
            if missing or extra or "mentions_all_levels" not in entry:
                raise ValueError(
                    f"fake_market.json: skill_roles[{skill}] lệch config/rules.toml: thiếu vai trò {missing}, "
                    f"thừa vai trò {extra}, cần có mentions_all_levels."
                )

    def city_shares(self, *, role: str, level: str = "all", years: str = "any") -> Envelope[CitySharesData]:
        key = level if years == "any" else f"{level}.y{years}"
        entry = self._city_shares.get(role, {}).get(key)
        if entry is None:
            raise UnknownCell(
                "Không có ô thống kê nào cho vai trò, cấp bậc và số năm đã chọn.",
                snapshot_date=self._snapshot_date,
            )
        rows = [
            CityShareRow(
                city=row["city"],
                share=self._stat(
                    row["share"], MeasureKind.COMPOSITION_SHARE, row["cell_id"]
                ),
            )
            for row in entry["rows"]
        ]
        data = CitySharesData(
            role=role,
            level=level,
            years=years,
            years_unstated_cell_id=None if years == "any" else entry["years_unstated_cell_id"],
            total_cell_id=entry["total_cell_id"],
            rows=rows,
        )
        cell_ids = [entry["total_cell_id"], *(row["cell_id"] for row in entry["rows"])]
        if data.years_unstated_cell_id is not None:
            cell_ids.append(data.years_unstated_cell_id)
        return Envelope[CitySharesData](data=data, meta=self._meta(cell_ids, {}))

    def skill_rates(
        self, *, role: str, level: str, have: Collection[str] = ()
    ) -> Envelope[SkillRatesData]:
        entry = self._skill_rates.get(role, {}).get(level)
        if entry is None:
            raise UnknownCell(
                "Không có ô thống kê nào cho vai trò và cấp bậc đã chọn.",
                snapshot_date=self._snapshot_date,
            )
        cell_id: str = entry["cell_id"]
        owned = set(have)
        rows = []
        for row in entry["rows"]:
            rate = self._stat(row["rate"], MeasureKind.SKILL_RATE, cell_id)
            group = None if rate.display is DisplayState.NULL_DATA else row["group"]
            rows.append(
                SkillRateRow(skill=row["skill"], rate=rate, group=group, have=row["skill"] in owned)
            )
        # Thứ tự hiển thị do máy chủ quyết (#149): dòng có tỷ lệ trước, tỷ lệ giảm dần, rồi mã. Bản thật theo cùng quy tắc.
        rows.sort(key=lambda r: (r.rate.value is None, -(r.rate.value or 0.0), r.skill))
        core = [r for r in rows if r.group == "core"]
        shown = any(r.rate.value is not None for r in rows)
        data = SkillRatesData(
            role=role,
            level=level,
            cell_id=cell_id,
            rows=rows,
            core_size=len(core) if shown else None,
            have_core=sum(r.have for r in core) if shown else None,
        )
        meta = self._meta([cell_id], {cell_id: entry["fallback_label"]})
        return Envelope[SkillRatesData](data=data, meta=meta)

    def newcomer_roles(self) -> Envelope[NewcomerRolesData]:
        rows = [
            NewcomerRoleRow(
                role=row["role"],
                total_cell_id=row["total_cell_id"],
                entry_cell_id=row["entry_cell_id"],
                share=self._stat(
                    row["share"], MeasureKind.LEVEL_SHARE, row["total_cell_id"]
                ),
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

    def market_overview(self) -> Envelope[MarketOverviewData]:
        cells = self._cells
        extra = self._overview
        role_places: dict[str, dict[str, int]] = {}
        for role in self._roles:
            found = {city: cells[f"{city}.{role}"]["n"] for city in BIG_CITIES if f"{city}.{role}" in cells}
            role_places[role] = found if len(found) == len(BIG_CITIES) else dict(extra["role_places"][role])
        counts = OverviewCounts(
            total_n=cells["vn.all"]["n"],
            total_mix=cells["vn.all"]["seniority_mix"],
            entry_n=cells["vn.all.entry"]["n"],
            roles={r: (cells[f"vn.{r}"]["n"], cells[f"vn.{r}"]["seniority_mix"]) for r in self._roles},
            role_entry={r: cells[f"vn.{r}.entry"]["n"] for r in self._roles if f"vn.{r}.entry" in cells},
            places={
                cid.split(".")[0]: cell["n"]
                for cid, cell in cells.items()
                if cid.endswith(".all") and not cid.startswith("vn.")
            },
            role_places=role_places,
            years_upto={int(k): v for k, v in extra["years_upto"].items()},
            years_unstated=extra["years_unstated"],
        )
        data, overview_cells = build_market_overview(counts, load_rules())
        meta = Meta(
            snapshot_date=self._snapshot_date,
            snapshot_status=self._snapshot_status,
            sources=self._sources,
            sources_failed=self._sources_failed,
            thresholds=self._thresholds,
            coverage_notes=self._coverage_notes,
            cells=overview_cells,
        )
        return Envelope[MarketOverviewData](data=data, meta=meta)

    def learning_path(
        self, *, role: str, level: str, have: Collection[str]
    ) -> Envelope[LearningPathData]:
        if role not in self._roles:
            raise UnknownCell(
                "Không có ô thống kê nào cho vai trò đã chọn.",
                snapshot_date=self._snapshot_date,
            )
        entry_cell_id = f"vn.{role}.entry"
        if role not in self._paths:
            empty = LearningPathData(
                role=role, level=level, status=PathStatus.NOT_READY, cell_id=None,
                entry_cell_id=entry_cell_id, stages=[], current_stage=None,
                have_on_path=0, path_size=0, have_ignored=sorted(set(have)),
            )  # fmt: skip
            return Envelope[LearningPathData](
                data=empty, meta=self._meta([entry_cell_id], {})
            )

        rates = self._skill_rates.get(role, {}).get(level)
        no_cell = UnknownCell(
            "Không có ô thống kê nào cho vai trò và cấp bậc đã chọn.",
            snapshot_date=self._snapshot_date,
        )
        if rates is None:
            raise no_cell
        cell_id: str = rates["cell_id"]
        by_skill = {row["skill"]: row for row in rates["rows"]}
        nodes = {node["skill"]: node for node in self._paths[role]}
        # Bản giả chỉ ném `UnknownCell` với yêu cầu hợp lệ: ô tỷ lệ không phủ hết nút của lộ trình thì không có lộ trình
        # cho (vai trò, cấp) này, thay vì để `KeyError` thành 500.
        if not set(nodes) <= set(by_skill):
            raise no_cell
        requires = {code: node["requires"] for code, node in nodes.items()}
        stage_of = stage_numbers(requires)
        stats = {
            code: self._stat(by_skill[code]["rate"], MeasureKind.SKILL_RATE, cell_id)
            for code in nodes
        }
        groups = {
            code: None
            if stats[code].display is DisplayState.NULL_DATA
            else by_skill[code]["group"]
            for code in nodes
        }
        targets = foundation_targets(requires, groups)
        needed_by: dict[str, list[str]] = {code: [] for code in nodes}
        for code, needs in requires.items():
            for required in needs:
                needed_by[required].append(code)
        foundation_for = {
            code: targets[code] if nodes[code]["foundation"] else [] for code in nodes
        }
        if any(
            groups[c] == "company_specific" and not foundation_for[c] for c in nodes
        ):
            raise no_cell  # riêng công ty mà không phải nền tảng không được vào lộ trình (FR-20)
        by_stage: dict[int, list[PathSkill]] = {}
        for code, node in nodes.items():
            by_stage.setdefault(stage_of[code], []).append(
                PathSkill(
                    skill=code,
                    rate=stats[code],
                    group=groups[code],
                    foundation_for=foundation_for[code],
                    prerequisite_for=sorted(needed_by[code]),
                    have=False,
                    blurb=node["blurb"],
                    resource=PathResource(**node["resource"]),
                )
            )
        stages = [(n, sorted(by_stage[n], key=order_key)) for n in sorted(by_stage)]
        out, current, have_on_path, path_size, ignored = apply_have(stages, set(have))
        data = LearningPathData(
            role=role, level=level, status=PathStatus.READY, cell_id=cell_id,
            entry_cell_id=entry_cell_id, stages=out, current_stage=current,
            have_on_path=have_on_path, path_size=path_size, have_ignored=ignored,
        )  # fmt: skip
        cells = list(dict.fromkeys([cell_id, entry_cell_id]))
        meta = self._meta(cells, {cell_id: rates["fallback_label"]})
        return Envelope[LearningPathData](data=data, meta=meta)

    def skill_roles(self, *, skill: str) -> Envelope[SkillRolesData]:
        entry = self._skill_roles.get(skill)
        seed = find_seed_skill(skill)
        if entry is None or seed is None:
            raise UnknownCell(
                "Không có ô thống kê nào cho kỹ năng đã chọn.", snapshot_date=self._snapshot_date
            )
        counts: dict[str, int] = entry["entry"]
        group = SKILL_ROLES_LEVEL_GROUP
        rows = []
        for role in self._roles:
            cell_id = f"vn.{role}.{group}"
            scanned = self._sample(cell_id)
            share = self._stat(counts[role] / scanned if scanned else 0.0, MeasureKind.SKILL_RATE, cell_id)
            rows.append(SkillRoleRow(role=role, share=share))
        # Thứ tự hiển thị do máy chủ quyết (#166): dòng có tỷ lệ trước, tỷ lệ giảm dần rồi mã vai trò; dòng `null_data`
        # sau, cỡ mẫu của phép đo giảm dần rồi mã. Bản thật (#168) theo cùng quy tắc.
        rows.sort(
            key=lambda r: (
                r.share.display is DisplayState.NULL_DATA,
                -(r.share.value or 0.0),
                -self._sample(r.share.cell_id) if r.share.value is None else 0,
                r.role,
            )
        )
        data = SkillRolesData(
            skill=SkillLabel(code=seed.code, name_en=seed.name_en, name_vi=seed.name_vi),
            level=group,
            levels=list(load_rules().level_groups[group]),
            mentioned=entry["mentions_all_levels"] > 0,  # mọi cấp, không chỉ entry-level (AC 4 của #113)
            rows=rows,
        )
        return Envelope[SkillRolesData](data=data, meta=self._meta([r.share.cell_id for r in rows], {}))

    def _sample(self, cell_id: str) -> int:
        """Cỡ mẫu của tỷ lệ kỹ năng của ô: `n_by_measure.skill_count`, thiếu thì `n`."""
        cell = self._cells[cell_id]
        return sample_n(MeasureKind.SKILL_RATE, cell["n"], cell["n_by_measure"])

    def _stat(self, value: float | None, kind: MeasureKind, cell_id: str) -> Stat:
        cell = self._cells[cell_id]
        display = suppression_for(
            kind, sample_n(kind, cell["n"], cell["n_by_measure"]), min_sample=self._thresholds.min_sample
        )
        return Stat(
            value=None if display is DisplayState.NULL_DATA else value,
            kind=kind,
            display=display,
            cell_id=cell_id,
        )

    def _meta(
        self, cell_ids: list[str], fallback_labels: dict[str, str | None]
    ) -> Meta:
        return Meta(
            snapshot_date=self._snapshot_date,
            snapshot_status=self._snapshot_status,
            sources=self._sources,
            sources_failed=self._sources_failed,
            thresholds=self._thresholds,
            coverage_notes=self._coverage_notes,
            cells={
                cid: self._cell_meta(cid, fallback_labels.get(cid)) for cid in cell_ids
            },
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
