"""Mức khớp của tin dán với hồ sơ (FR-28, FR-29, #230). Chỉ ở API (AD-22): web không đếm, không so mã.

`build_match` nhận tỷ lệ kỹ năng của ô đã dùng (`SkillRatesData`, đã quay về nếu cần) cùng mã kỹ năng của tin và của hồ sơ, và
trả mục `match` của `posting-check`. Bản giả và bản thật (#234) dùng chung hàm này, nên số và nhóm không lệch giữa hai nguồn.

Quy ước về nhóm (FR-29, bản giả, #234 theo cùng hoặc ghi lại khác biệt):

- kỹ năng có dòng trong ô: nhóm của dòng (`company_specific` của θ gọi là `specific`);
- kỹ năng của tin mà ô không có dòng: tỷ lệ 0 và nhóm `specific` ("hiếm ở ô");
- ô không có dòng nào hiện số (dưới ngưỡng mẫu, kể cả sau khi quay về): `not_enough_data`, không nhóm, tỷ lệ `null_data`.
"""

from collections.abc import Collection, Mapping, Sequence

from haido_api.schemas.market import SkillLabel, SkillRatesData
from haido_api.schemas.posting import (
    GROUP_ORDER,
    GroupCode,
    PostingGroupCount,
    PostingMatch,
    PostingMatchedSkill,
    PostingMatchLevel,
    match_percent,
)
from haido_core.domain.display_policy import DisplayState, MeasureKind
from haido_core.domain.envelope import Stat
from haido_core.vocab.skills import find_seed_skill

__all__ = ["build_match", "match_percent"]

_GROUP_OF_THETA: dict[str, GroupCode] = {"core": "core", "common": "common", "company_specific": "specific"}


def build_match(
    rates: SkillRatesData,
    posting_skills: Sequence[str],
    have: Collection[str],
    weights: Mapping[str, int],
    config_version: str,
) -> PostingMatch:
    """Mục `match` của `posting-check`.

    Args:
        rates: tỷ lệ kỹ năng của ô đã dùng (kết quả của `skill_rates`, nguồn nào cũng được).
        posting_skills: mã kỹ năng của tin (đã nằm trong bộ từ vựng, route đã kiểm), có thể trùng.
        have: mã kỹ năng của hồ sơ; rỗng là không có hồ sơ.
        weights: trọng số `core`, `common`, `specific` từ `config/rules.toml` (AD-10).
        config_version: phiên bản cấu hình đã cho `weights`.
    """
    codes = list(dict.fromkeys(posting_skills))
    profile = set(have)
    profiled = bool(profile)
    by_code = {row.skill: row for row in rates.rows}
    ready = any(row.rate.display is not DisplayState.NULL_DATA for row in rates.rows)

    matched: list[PostingMatchedSkill] = []
    for code in codes:
        seed = find_seed_skill(code)
        if seed is None:
            raise ValueError(f"Kỹ năng {code!r} không có trong bộ từ vựng.")
        row = by_code.get(code)
        if not ready:
            rate = row.rate if row is not None else Stat(
                value=None, kind=MeasureKind.SKILL_RATE, display=DisplayState.NULL_DATA, cell_id=rates.cell_id
            )
            group: GroupCode | None = None
        elif row is None:
            rate = Stat(value=0.0, kind=MeasureKind.SKILL_RATE, display=DisplayState.SHOWN, cell_id=rates.cell_id)
            group = "specific"
        else:
            rate = row.rate
            group = _GROUP_OF_THETA[row.group] if row.group is not None else "specific"
        matched.append(
            PostingMatchedSkill(
                skill=SkillLabel(code=seed.code, name_en=seed.name_en, name_vi=seed.name_vi),
                group=group,
                rate=rate,
                have=(code in profile) if profiled else None,
            )
        )
    rank = {g: i for i, g in enumerate(GROUP_ORDER)}
    matched.sort(key=lambda s: (rank[s.group] if s.group else len(rank), -(s.rate.value or 0.0), s.skill.code))
    cv_first = [s.skill.code for s in matched if s.have]

    if not matched:
        return PostingMatch(status="no_skills", skills=[], groups=[], level=None, cv_first=[], config_version=config_version)
    if not ready:
        return PostingMatch(
            status="not_enough_data", skills=matched, groups=[], level=None, cv_first=cv_first, config_version=config_version
        )
    groups = []
    points = max_points = 0
    for group in GROUP_ORDER:
        in_group = [s for s in matched if s.group == group]
        had = sum(bool(s.have) for s in in_group)
        groups.append(PostingGroupCount(group=group, total=len(in_group), had=had if profiled else None))
        max_points += weights[group] * len(in_group)
        points += weights[group] * had
    level = PostingMatchLevel(points=points, max_points=max_points, percent=match_percent(points, max_points)) if profiled else None
    return PostingMatch(status="ready", skills=matched, groups=groups, level=level, cv_first=cv_first, config_version=config_version)
