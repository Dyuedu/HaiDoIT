"""Dịch vụ tầng API cho cố vấn lộ trình roadmap.sh từ CV + vị trí + cấp bậc + dữ liệu JD."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError

from haido_api.errors import MissingConsentError
from haido_api.learning_path import apply_have, order_key
from haido_api.market_source import MarketReadModel, UnknownCell
from haido_api.schemas.learning_path import (
    AdvisorRoadmapData,
    LearningPathData,
    PathResource,
    PathSkill,
    PathStage,
    PathStatus,
)
from haido_api.schemas.market import SkillRatesData
from haido_api.stat_path import RolePath, load_paths
from haido_api.uploads import read_cv_upload
from haido_core.config import ALL_LEVELS, RulesConfig, load_rules
from haido_core.domain.envelope import CellMeta, Envelope, Meta
from haido_core.extract import (
    AdvisorInput,
    AdvisorLlmConfig,
    MarketSkillContext,
    extract_document_chars,
    generate_advisor_roadmap,
    load_advisor_config,
)
from haido_core.vocab.skills import (
    MAX_PROFILE_SKILLS,
    find_seed_skill,
    is_skill_code,
    load_seed_skills,
)

_CONSENT_TRUE = frozenset({"true", "1", "yes", "on"})

_ROLE_LABELS: dict[str, str] = {
    "embedded": "Nhúng",
    "ai_ml": "AI/ML",
    "data_scientist": "Khoa học dữ liệu",
    "data_engineer": "Kỹ sư dữ liệu",
    "data_analyst": "Phân tích dữ liệu",
    "qa": "Kiểm thử (QA)",
    "devops": "DevOps",
    "security": "Bảo mật",
    "it_infra": "Hạ tầng & IT support",
    "mobile": "Mobile",
    "frontend": "Frontend",
    "backend": "Backend",
    "fullstack": "Fullstack",
    "ba_po_pm": "BA / PO / PM",
    "ui_ux": "UI/UX",
    "game": "Phát triển game",
    "other": "Vai trò khác",
}

_LEVEL_LABELS: dict[str, str] = {
    "entry": "Mới vào nghề",
    "intern": "Intern",
    "fresher": "Fresher",
    "junior": "Junior",
    "mid": "Mid",
    "senior": "Senior",
    "lead": "Lead",
    "unknown": "Chưa ghi cấp bậc",
    "all": "Mọi cấp bậc",
}


@lru_cache(maxsize=1)
def _reference_paths() -> dict[str, RolePath]:
    try:
        return load_paths()
    except (OSError, ValueError):
        return {}


def _default_llm_caller(cfg: AdvisorLlmConfig) -> Any:
    """Hook để test inject LLM caller giả lập; runtime dùng `_call_llm_http` bên trong `haido_core`."""
    _ = cfg
    return None


def _validation_error(loc_name: str, msg: str) -> RequestValidationError:
    return RequestValidationError(
        [{"type": "value_error", "loc": ("form", loc_name), "msg": msg, "input": None}]
    )


def _parse_have_field(raw: str | None) -> tuple[str, ...]:
    if not raw:
        return ()
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    if len(parts) > MAX_PROFILE_SKILLS or not all(is_skill_code(p) for p in parts):
        raise _validation_error("have", "have không hợp lệ")
    return tuple(dict.fromkeys(parts))


def _load_rates_with_level_fallback(
    source: MarketReadModel,
    *,
    role: str,
    level: str,
) -> tuple[Envelope[SkillRatesData], str, dict[str, CellMeta]]:
    """Đọc tỷ lệ kỹ năng JD cho `(role, level)`. Khi ô cấp cụ thể chưa có trong nguồn giả, quay về `all`."""
    try:
        rates_env = source.skill_rates(role=role, level=level, have=())
    except UnknownCell:
        if level == ALL_LEVELS:
            raise
        rates_env = source.skill_rates(role=role, level=ALL_LEVELS, have=())

    cells: dict[str, CellMeta] = dict(rates_env.meta.cells)
    entry_cell_id = f"vn.{role}.entry"
    if entry_cell_id not in cells:
        try:
            entry_env = source.skill_rates(role=role, level="entry", have=())
            if entry_cell_id in entry_env.meta.cells:
                cells[entry_cell_id] = entry_env.meta.cells[entry_cell_id]
            elif entry_env.data.cell_id in entry_env.meta.cells:
                entry_cell_id = entry_env.data.cell_id
                cells[entry_cell_id] = entry_env.meta.cells[entry_cell_id]
        except UnknownCell:
            entry_cell_id = rates_env.data.cell_id
    return rates_env, entry_cell_id, cells


async def build_advisor_roadmap(
    request: Request,
    *,
    skill_rates_source: MarketReadModel,
    rules: RulesConfig | None = None,
) -> Envelope[AdvisorRoadmapData]:
    """Nhận multipart CV + role + level + consent trong RAM và trả về lộ trình `roadmap.sh` gắn số liệu JD."""
    cfg_rules = rules if rules is not None else load_rules()
    cv = await read_cv_upload(
        request,
        rules=cfg_rules,
        capture_fields=("role", "level", "consent", "have"),
    )

    consent_raw = cv.fields.get("consent", "").strip().lower()
    if consent_raw not in _CONSENT_TRUE:
        raise MissingConsentError()

    role = cv.fields.get("role", "").strip()
    if not role:
        raise _validation_error("role", "thiếu tham số role")
    if role not in cfg_rules.roles:
        raise _validation_error("role", "role không hợp lệ")

    allowed_levels = {ALL_LEVELS, *cfg_rules.level_options}
    level = cv.fields.get("level", "entry").strip() or "entry"
    if level not in allowed_levels:
        raise _validation_error("level", "level không hợp lệ")

    extra_have = _parse_have_field(cv.fields.get("have"))
    document_chars = extract_document_chars(cv.content, cv.content_type)

    rates_env, entry_cell_id, cells = _load_rates_with_level_fallback(
        skill_rates_source,
        role=role,
        level=level,
    )
    rates_by_code = {row.skill: row for row in rates_env.data.rows}
    vocab = load_seed_skills()

    market_skills = tuple(
        MarketSkillContext(
            code=row.skill,
            name_en=skill.name_en if (skill := find_seed_skill(row.skill)) else row.skill,
            name_vi=skill.name_vi if skill else row.skill,
            rate=row.rate.value,
            group=row.group,
        )
        for row in rates_env.data.rows
    )

    ref_paths = _reference_paths()
    ref_entry = ref_paths.get(role)
    ref_topics = (
        tuple(
            {"title": t.title, "choose_one": t.choose_one, "skills": t.skills}
            for t in ref_entry.topics
        )
        if ref_entry
        else ()
    )
    ref_nodes = ref_entry.nodes if ref_entry else {}

    advisor_input = AdvisorInput(
        document_chars=document_chars,
        role=role,
        role_label=_ROLE_LABELS.get(role, role),
        level=level,
        level_label=_LEVEL_LABELS.get(level, level),
        market_skills=market_skills,
        vocab=vocab,
        known_have=extra_have,
        reference_topics=ref_topics,
        reference_nodes=ref_nodes,
    )
    llm_cfg = load_advisor_config()
    plan = generate_advisor_roadmap(
        advisor_input,
        config=llm_cfg,
        llm_caller=_default_llm_caller(llm_cfg),
    )

    combined_have = tuple(dict.fromkeys([*plan.cv_skills, *extra_have]))[:MAX_PROFILE_SKILLS]
    owned_set = set(combined_have)

    candidate_stages: list[tuple[str, bool, list[Any]]] = []
    for raw_stage in plan.stages:
        items = [raw_node for raw_node in raw_stage.skills if raw_node.skill in rates_by_code]
        if items:
            candidate_stages.append((raw_stage.title, raw_stage.choose_one, items))

    def _reachable(edges: dict[str, list[str]], start: str) -> set[str]:
        seen: set[str] = set()
        stack = list(edges.get(start, ()))
        while stack:
            cur = stack.pop()
            if cur not in seen:
                seen.add(cur)
                stack.extend(edges.get(cur, ()))
        return seen

    # Lọc điểm bất biến FR-20: kỹ năng company_specific chỉ giữ nếu dẫn tới ít nhất một kỹ năng core/common
    pruned_edges: dict[str, list[str]] = {}
    foundations: dict[str, list[str]] = {}
    while candidate_stages:
        stage_num_by_skill = {
            item.skill: idx
            for idx, (_t, _c, items) in enumerate(candidate_stages, start=1)
            for item in items
        }
        pruned_edges = {}
        for idx, (_t, _c, items) in enumerate(candidate_stages, start=1):
            for item in items:
                pruned_edges[item.skill] = sorted(
                    t for t in item.prerequisite_for if stage_num_by_skill.get(t, 0) > idx
                )
        foundations = {}
        drop: set[str] = set()
        for _t, _c, items in candidate_stages:
            for item in items:
                grp = rates_by_code[item.skill].group
                if grp is None:
                    foundations[item.skill] = []
                    continue
                ff = sorted(
                    t
                    for t in _reachable(pruned_edges, item.skill)
                    if rates_by_code[t].group in ("core", "common")
                )
                if grp == "company_specific" and not ff:
                    drop.add(item.skill)
                else:
                    foundations[item.skill] = ff
        if not drop:
            break
        candidate_stages = [
            (t, c, [it for it in items if it.skill not in drop])
            for t, c, items in candidate_stages
        ]
        candidate_stages = [(t, c, items) for t, c, items in candidate_stages if items]

    built_stages: list[PathStage] = []
    for stage_idx, (title, choose_one, items) in enumerate(candidate_stages, start=1):
        stage_nodes = [
            PathSkill(
                skill=raw_node.skill,
                rate=rates_by_code[raw_node.skill].rate,
                group=rates_by_code[raw_node.skill].group,
                foundation_for=foundations[raw_node.skill],
                prerequisite_for=pruned_edges[raw_node.skill],
                have=False,
                blurb=raw_node.blurb,
                resource=PathResource(
                    title=raw_node.resource_title,
                    url=raw_node.resource_url,
                ),
            )
            for raw_node in items
        ]
        stage_nodes.sort(key=order_key)
        built_stages.append(
            PathStage(
                stage=stage_idx,
                title=title,
                choose_one=choose_one and len(stage_nodes) >= 2,
                skills=stage_nodes,
            )
        )

    if built_stages:
        final_stages, current_stage, have_on_path, path_size, have_ignored = apply_have(
            built_stages, combined_have
        )
        path_data = LearningPathData(
            role=role,
            level=level,
            status=PathStatus.READY,
            cell_id=rates_env.data.cell_id,
            entry_cell_id=entry_cell_id,
            stages=final_stages,
            current_stage=current_stage,
            have_on_path=have_on_path,
            path_size=path_size,
            have_ignored=have_ignored,
        )
    else:
        path_data = LearningPathData(
            role=role,
            level=level,
            status=PathStatus.NOT_READY,
            cell_id=None,
            entry_cell_id=entry_cell_id,
            stages=[],
            current_stage=None,
            have_on_path=0,
            path_size=0,
            have_ignored=sorted(owned_set),
        )

    missing_core = [
        row.skill
        for row in rates_env.data.rows
        if row.group == "core" and row.skill not in owned_set
    ]
    missing_common = [
        row.skill
        for row in rates_env.data.rows
        if row.group == "common" and row.skill not in owned_set
    ]

    meta_out = Meta(
        snapshot_date=rates_env.meta.snapshot_date,
        snapshot_status=rates_env.meta.snapshot_status,
        sources=rates_env.meta.sources,
        sources_failed=rates_env.meta.sources_failed,
        thresholds=rates_env.meta.thresholds,
        coverage_notes=rates_env.meta.coverage_notes,
        cells=cells,
    )
    return Envelope(
        data=AdvisorRoadmapData(
            path=path_data,
            cv_skills=plan.cv_skills,
            missing_core_skills=missing_core,
            missing_common_skills=missing_common,
            advisor_summary=plan.advisor_summary,
            generation_mode=plan.generation_mode,
        ),
        meta=meta_out,
    )
