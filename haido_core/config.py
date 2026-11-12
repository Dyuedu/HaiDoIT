"""Cấu hình có phiên bản từ `config/rules.toml` (AD-10, DoD dòng 4).

Thiếu khóa hoặc sai kiểu thì báo lỗi tiếng Việt, không tự điền giá trị mặc định.
"""

import re
import tomllib
from dataclasses import dataclass
from itertools import pairwise
from pathlib import Path
from typing import Any

DEFAULT_RULES_PATH = Path(__file__).resolve().parents[1] / "config" / "rules.toml"

ALL_ROLES = "all"
"""Mã dành riêng cho "mọi vai trò"; không được nằm trong danh sách `roles`."""

ALL_LEVELS = "all"
"""Mã dành riêng cho "mọi cấp bậc"; không được là tên nhóm, mã cấp hay phần tử của `level_options`."""

ANY_YEARS = "any"
"""Mã số năm "mọi số năm" (#280): không lọc theo số năm, gồm cả tin không ghi số năm."""


class ConfigError(ValueError):
    """Lỗi cấu hình. Thông báo bằng tiếng Việt."""


@dataclass(frozen=True, slots=True)
class CoverageNoteRule:
    """Một lưu ý độ phủ. `text` của `n_sources` có chỗ `{n}` cho số nguồn đang bật."""

    code: str
    text: str


@dataclass(frozen=True, slots=True)
class RulesConfig:
    config_version: str
    window_days: int
    auto_sources: tuple[str, ...]
    source_priority: tuple[str, ...]
    """Hạng đại diện cụm (#100). Tên đứng trước thắng. Đã chuẩn hóa chữ thường."""
    excluded_sources: tuple[str, ...]
    """Nguồn không bao giờ được đếm và không được liệt kê (#263): tin của nguồn này bị loại khỏi `aggregate`."""
    min_sample: int
    theta_core: float
    theta_common: float
    cv_max_bytes: int
    """Cỡ tối đa của file CV, tính bằng byte (#140). Kiểm trước khi đọc thân request."""
    cv_types: tuple[str, ...]
    """Kiểu MIME được nhận cho file CV (chữ thường, dạng `loại/phụ`)."""
    roles: tuple[str, ...]
    coverage_notes: tuple[CoverageNoteRule, ...]
    city_codes: dict[str, str]
    """Nhãn thành phố của bộ phân loại sang mã snake_case, theo thứ tự hiển thị."""
    role_codes: dict[str, str]
    level_codes: dict[str, str]
    level_options: tuple[str, ...]
    """Mã cấp bậc lọc được của bản đồ, theo thứ tự hiển thị, không gồm `all` (#163, #134). Mỗi mã là một nhóm
    trong `level_groups` hoặc một mã của `level_codes`."""
    level_groups: dict[str, tuple[str, ...]]
    """Nhóm cấp bậc: tên nhóm sang các mã cấp thành viên (`entry` = intern, fresher, junior; #134)."""
    years_options: tuple[int, ...]
    """Mốc "tối đa N năm kinh nghiệm" của bản đồ (#280), tăng dần, không gồm `any`. Mã của mốc là `str(N)`."""


CV_SIGNATURES: dict[str, bytes] = {
    "application/pdf": b"%PDF-",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": b"PK\x03\x04",
}
"""Kiểu MIME CV được hỗ trợ và chữ ký (byte đầu file) của từng kiểu. `cv_types` chỉ được chọn trong bảng này."""

CV_TYPE_NAMES: dict[str, str] = {
    "application/pdf": "PDF",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "DOCX",
}
"""Tên ngắn hiển thị cho người dùng của từng kiểu CV được hỗ trợ."""

CV_MAX_BYTES_LIMIT = 50 * 1024 * 1024
"""Trần tuyệt đối của `cv_max_bytes`, để cấu hình sai không mở cửa cho tệp quá lớn vào bộ nhớ."""

_MIME = re.compile(r"[a-z0-9][a-z0-9.+-]*/[a-z0-9][a-z0-9.+-]*")

CITY_CODES = frozenset({"ha_noi", "ho_chi_minh", "da_nang", "other", "unknown"})
UNKNOWN = "unknown"


def _years_options(raw: dict[str, Any]) -> tuple[int, ...]:
    """`years_options` (#280): số nguyên từ 0, tăng dần, không trùng, không rỗng."""
    options = raw.get("years_options")
    if options is None:
        raise ConfigError("Cấu hình thiếu khóa years_options.")
    if (
        not isinstance(options, list)
        or not options
        or not all(isinstance(n, int) and not isinstance(n, bool) and n >= 0 for n in options)
        or any(a >= b for a, b in pairwise(options))
    ):
        raise ConfigError("years_options phải là danh sách số nguyên từ 0, tăng dần, không trùng và không rỗng.")
    return tuple(options)


def _is_number(value: object) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def _label_table(raw: dict[str, Any], name: str) -> dict[str, str]:
    labels = raw.get("labels")
    table = labels.get(name) if isinstance(labels, dict) else None
    if table is None:
        raise ConfigError(f"Cấu hình thiếu bảng labels.{name}.")
    if (
        not isinstance(table, dict)
        or not table
        or not all(isinstance(k, str) and isinstance(v, str) and k and v for k, v in table.items())
        or len(set(table.values())) != len(table)
    ):
        raise ConfigError(f"labels.{name} phải ánh xạ nhãn sang mã (chuỗi không rỗng), mỗi mã một nhãn.")
    return dict(table)


_CODE_SHAPE = re.compile(r"[a-z0-9_]+")


def _level_filter(
    raw: dict[str, Any], level_codes: dict[str, str]
) -> tuple[tuple[str, ...], dict[str, tuple[str, ...]]]:
    """`level_options` và `level_groups` (#163, #134), kiểm với mã cấp của `labels.level`."""
    options = raw.get("level_options")
    if options is None:
        raise ConfigError("Cấu hình thiếu khóa level_options.")
    groups = raw.get("level_groups")
    if groups is None:
        raise ConfigError("Cấu hình thiếu bảng level_groups.")
    levels = set(level_codes.values())
    if not isinstance(groups, dict):
        raise ConfigError("level_groups phải là bảng ánh xạ tên nhóm sang danh sách mã cấp bậc.")
    seen: set[str] = set()
    for name, members in groups.items():
        if not _CODE_SHAPE.fullmatch(name):
            raise ConfigError(f"level_groups: tên nhóm chỉ gồm a-z0-9_ (chữ thường, số, gạch dưới), gặp {name!r}.")
        if name == ALL_LEVELS or name in levels:
            raise ConfigError(f"level_groups: tên nhóm không được là {ALL_LEVELS!r} hay một mã cấp bậc ({name!r}).")
        if (
            not isinstance(members, list)
            or not members
            or not all(isinstance(m, str) for m in members)
            or len(set(members)) != len(members)
        ):
            raise ConfigError(f"level_groups.{name} phải là danh sách mã cấp bậc không rỗng, không trùng.")
        if not set(members) <= levels or UNKNOWN in members:
            raise ConfigError(
                f"level_groups.{name} chỉ được chứa mã trong labels.level và không chứa {UNKNOWN!r}."
            )
        if seen & set(members):
            raise ConfigError("level_groups: hai nhóm không được chung thành viên.")
        seen |= set(members)
    if (
        not isinstance(options, list)
        or not options
        or not all(isinstance(o, str) and o for o in options)
        or len(set(options)) != len(options)
        or ALL_LEVELS in options
    ):
        raise ConfigError(f"level_options phải là danh sách mã không rỗng, không trùng và không có {ALL_LEVELS!r}.")
    if not all(_CODE_SHAPE.fullmatch(o) for o in options):
        raise ConfigError("level_options: mỗi mã chỉ gồm a-z0-9_ (chữ thường, số, gạch dưới).")
    if set(options) != levels | set(groups):
        raise ConfigError("level_options phải đúng bằng các mã trong labels.level cộng tên các nhóm trong level_groups.")
    return tuple(options), {name: tuple(members) for name, members in groups.items()}


def _coverage_notes(raw: dict[str, Any]) -> tuple[CoverageNoteRule, ...]:
    notes = raw.get("coverage_notes")
    if notes is None:
        raise ConfigError("Cấu hình thiếu khóa coverage_notes.")
    if (
        not isinstance(notes, list)
        or not notes
        or not all(
            isinstance(n, dict)
            and isinstance(n.get("code"), str)
            and n["code"]
            and isinstance(n.get("text"), str)
            and n["text"]
            for n in notes
        )
    ):
        raise ConfigError("coverage_notes phải là danh sách mục có code và text (chuỗi không rỗng).")
    return tuple(CoverageNoteRule(n["code"], n["text"]) for n in notes)


_EXCLUDED_ERROR = (
    "sources.excluded phải là danh sách tên nguồn (chuỗi không rỗng, không trùng sau khi chuẩn hóa) "
    "và không chứa nguồn trong sources.auto."
)


def load_rules(path: Path | str | None = None) -> RulesConfig:
    target = Path(path) if path is not None else DEFAULT_RULES_PATH
    try:
        raw = tomllib.loads(target.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigError(f"Không tìm thấy file cấu hình {target.name}.") from exc
    except (OSError, UnicodeDecodeError) as exc:
        raise ConfigError(f"Không đọc được file cấu hình {target.name} ({type(exc).__name__}).") from exc
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"File cấu hình {target.name} không đúng cú pháp TOML: {exc}") from exc

    version = raw.get("config_version")
    if version is None:
        raise ConfigError("Cấu hình thiếu khóa config_version.")
    if not isinstance(version, str) or not version.strip():
        raise ConfigError("config_version phải là chuỗi không rỗng.")

    window = raw.get("window_days")
    if window is None:
        raise ConfigError("Cấu hình thiếu khóa window_days.")
    if isinstance(window, bool) or not isinstance(window, int) or window < 1:
        raise ConfigError("window_days phải là số nguyên từ 1 trở lên.")

    sources = raw.get("sources")
    auto = sources.get("auto") if isinstance(sources, dict) else None
    if auto is None:
        raise ConfigError("Cấu hình thiếu khóa sources.auto.")
    if not isinstance(auto, list) or not auto or not all(isinstance(s, str) and s for s in auto):
        raise ConfigError("sources.auto phải là danh sách tên nguồn (chuỗi), không rỗng.")

    excluded = sources.get("excluded") if isinstance(sources, dict) else None
    if excluded is None:
        raise ConfigError("Cấu hình thiếu khóa sources.excluded.")
    if not isinstance(excluded, list) or not all(isinstance(s, str) for s in excluded):
        raise ConfigError(_EXCLUDED_ERROR)
    excluded = [s.strip().lower() for s in excluded]  # so khớp không phân biệt hoa thường và khoảng trắng đầu cuối
    if not all(excluded) or len(set(excluded)) != len(excluded) or set(excluded) & {s.strip().lower() for s in auto}:
        raise ConfigError(_EXCLUDED_ERROR)

    priority = sources.get("priority")
    if priority is None:
        raise ConfigError("Cấu hình thiếu khóa sources.priority.")
    if not isinstance(priority, list) or not priority or not all(isinstance(item, str) for item in priority):
        raise ConfigError("sources.priority phải là danh sách tên nguồn (chuỗi), không rỗng.")
    priority_norm = [item.strip().casefold() for item in priority]
    if not all(priority_norm) or len(set(priority_norm)) != len(priority_norm):
        raise ConfigError("sources.priority phải là danh sách tên nguồn không rỗng, không trùng.")
    if set(priority_norm) & set(excluded):
        raise ConfigError("sources.priority không được chứa nguồn trong sources.excluded.")
    if not {item.strip().casefold() for item in auto} <= set(priority_norm):
        raise ConfigError("sources.priority phải chứa mọi nguồn trong sources.auto.")

    min_sample = raw.get("min_sample")
    if min_sample is None:
        raise ConfigError("Cấu hình thiếu khóa min_sample.")
    if isinstance(min_sample, bool) or not isinstance(min_sample, int) or min_sample < 1:
        raise ConfigError("min_sample phải là số nguyên từ 1 trở lên.")

    thetas: dict[str, float] = {}
    for key in ("theta_core", "theta_common"):
        value = raw.get(key)
        if value is None:
            raise ConfigError(f"Cấu hình thiếu khóa {key}.")
        if not _is_number(value) or not 0 <= value <= 1:
            raise ConfigError(f"{key} phải là số từ 0 đến 1.")
        thetas[key] = float(value)
    if thetas["theta_common"] > thetas["theta_core"]:
        raise ConfigError("theta_common không được lớn hơn theta_core.")

    cv_max_bytes = raw.get("cv_max_bytes")
    if cv_max_bytes is None:
        raise ConfigError("Cấu hình thiếu khóa cv_max_bytes.")
    if isinstance(cv_max_bytes, bool) or not isinstance(cv_max_bytes, int) or not 1 <= cv_max_bytes <= CV_MAX_BYTES_LIMIT:
        raise ConfigError(f"cv_max_bytes phải là số nguyên byte từ 1 đến {CV_MAX_BYTES_LIMIT}.")

    cv_types = raw.get("cv_types")
    if cv_types is None:
        raise ConfigError("Cấu hình thiếu khóa cv_types.")
    if (
        not isinstance(cv_types, list)
        or not cv_types
        or not all(isinstance(t, str) and _MIME.fullmatch(t) for t in cv_types)
        or len(set(cv_types)) != len(cv_types)
    ):
        raise ConfigError("cv_types phải là danh sách kiểu MIME chữ thường dạng loại/phụ, không rỗng và không trùng.")
    if not set(cv_types) <= CV_SIGNATURES.keys():
        raise ConfigError(f"cv_types chỉ được chọn trong các kiểu hỗ trợ: {', '.join(CV_SIGNATURES)}.")

    roles = raw.get("roles")
    if roles is None:
        raise ConfigError("Cấu hình thiếu khóa roles.")
    if (
        not isinstance(roles, list)
        or not roles
        or not all(isinstance(r, str) and r for r in roles)
        or len(set(roles)) != len(roles)
        or ALL_ROLES in roles
    ):
        raise ConfigError(f"roles phải là danh sách mã vai trò không rỗng, không trùng và không có {ALL_ROLES!r}.")

    notes = _coverage_notes(raw)
    city_codes = _label_table(raw, "city")
    role_codes = _label_table(raw, "role")
    level_codes = _label_table(raw, "level")
    if set(city_codes.values()) != CITY_CODES:
        raise ConfigError(f"labels.city phải có đúng các mã {', '.join(sorted(CITY_CODES))}.")
    if UNKNOWN not in level_codes.values():
        raise ConfigError(f"labels.level phải có mã {UNKNOWN!r}.")
    if set(role_codes.values()) != set(roles):
        raise ConfigError("roles phải đúng bằng tập mã trong labels.role.")
    level_options, level_groups = _level_filter(raw, level_codes)
    years_options = _years_options(raw)

    return RulesConfig(
        config_version=version,
        window_days=window,
        auto_sources=tuple(auto),
        source_priority=tuple(priority_norm),
        excluded_sources=tuple(excluded),
        min_sample=min_sample,
        theta_core=thetas["theta_core"],
        theta_common=thetas["theta_common"],
        cv_max_bytes=cv_max_bytes,
        cv_types=tuple(cv_types),
        roles=tuple(roles),
        coverage_notes=notes,
        city_codes=city_codes,
        role_codes=role_codes,
        level_codes=level_codes,
        level_options=level_options,
        level_groups=level_groups,
        years_options=years_options,
    )


# ---------------------------------------------------------------- #283: luật phân loại

DEFAULT_CLASSIFY_PATH = Path(__file__).resolve().parents[1] / "config" / "classify.toml"


def _read_toml(target: Path) -> dict[str, Any]:
    try:
        return tomllib.loads(target.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigError(f"Không tìm thấy file cấu hình {target.name}.") from exc
    except (OSError, UnicodeDecodeError) as exc:
        raise ConfigError(f"Không đọc được file cấu hình {target.name} ({type(exc).__name__}).") from exc
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"File cấu hình {target.name} không đúng cú pháp TOML: {exc}") from exc


def _need(raw: dict[str, Any], key: str) -> Any:
    if key not in raw:
        raise ConfigError(f"classify.toml thiếu khóa {key}.")
    return raw[key]


def _phrases(value: Any, where: str) -> tuple[str, ...]:
    from haido_core.domain.posting_text import fold

    if not isinstance(value, list) or not value or not all(isinstance(p, str) and p.strip() for p in value):
        raise ConfigError(f"{where} phải là danh sách cụm chữ không rỗng.")
    out: list[str] = []
    for p in value:
        lead = " " if p.startswith(" ") else ""
        tail = " " if p.endswith(" ") else ""
        out.append(lead + fold(p) + tail)
    return tuple(out)


def _str_list(raw: dict[str, Any], key: str) -> tuple[str, ...]:
    value = _need(raw, key)
    if not isinstance(value, list) or not all(isinstance(v, str) and v for v in value):
        raise ConfigError(f"{key} phải là danh sách chuỗi không rỗng.")
    return tuple(value)


def _regex(value: Any, where: str) -> re.Pattern[str]:
    if not isinstance(value, str) or not value:
        raise ConfigError(f"{where} phải là biểu thức chính quy không rỗng.")
    try:
        return re.compile(value)
    except re.error as exc:
        raise ConfigError(f"{where} không phải biểu thức chính quy hợp lệ: {exc}") from exc


def _table(raw: dict[str, Any], key: str) -> dict[str, Any]:
    value = _need(raw, key)
    if not isinstance(value, dict):
        raise ConfigError(f"{key} phải là bảng.")
    return value


def _rules_list(raw: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = _need(raw, key)
    if not isinstance(value, list) or not value or not all(isinstance(v, dict) for v in value):
        raise ConfigError(f"{key} phải là danh sách bảng [[{key}]].")
    return value


def _number(table: dict[str, Any], key: str, where: str) -> float:
    value = table.get(key)
    if not _is_number(value) or value < 0:
        raise ConfigError(f"{where}.{key} phải là số không âm.")
    return float(value)


def _int(raw: dict[str, Any], key: str, minimum: int) -> int:
    value = _need(raw, key)
    if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
        raise ConfigError(f"{key} phải là số nguyên từ {minimum}.")
    return value


def _phrase_rules(raw: dict[str, Any], key: str) -> list[Any]:
    from haido_core.domain.classify import PhraseRule

    out = []
    for item in _rules_list(raw, key):
        label = item.get("label")
        if not isinstance(label, str) or not label:
            raise ConfigError(f"{key}: mỗi dòng phải có label.")
        out.append(PhraseRule(label, _phrases(item.get("phrases"), f"{key}.{label}.phrases")))
    return out


def _years_steps(raw: dict[str, Any], level_labels: set[str]) -> tuple[Any, ...]:
    from haido_core.domain.classify import YearsToLevel

    steps = []
    last = -1.0
    rows = _rules_list(raw, "years_to_level")
    for i, item in enumerate(rows):
        label, below = item.get("label"), item.get("below")
        if label not in level_labels or (below is None) != (i == len(rows) - 1):
            raise ConfigError("years_to_level: mỗi dòng có label trong levels; chỉ dòng cuối không có below.")
        if below is not None:
            if not _is_number(below) or below <= last:
                raise ConfigError("years_to_level: below phải tăng dần.")
            last = float(below)
        steps.append(YearsToLevel(None if below is None else float(below), label))
    return tuple(steps)


def _build_classify(raw: dict[str, Any]) -> Any:
    from haido_core.domain.classify import (
        OTHER_ROLE,
        BranchRule,
        ClassifyConfig,
        EvidenceRules,
        SectionRules,
        SkillHint,
        YearsRules,
    )
    from haido_core.domain.posting_text import fold
    from haido_core.vocab.skills import load_vocabulary

    version = _need(raw, "classify_version")
    if not isinstance(version, str) or not version.startswith("classify-"):
        raise ConfigError("classify_version phải là chuỗi bắt đầu bằng 'classify-'.")

    roles = _phrase_rules(raw, "roles")
    labels = [r.label for r in roles]
    if len(set(labels)) != len(labels) or labels[-1] != OTHER_ROLE:
        raise ConfigError(f"roles: nhãn không trùng và {OTHER_ROLE!r} đứng cuối, đúng một lần.")

    branches = []
    raw_branches = _need(raw, "branches")
    if not isinstance(raw_branches, list) or not all(isinstance(b, dict) for b in raw_branches):
        raise ConfigError("branches phải là danh sách bảng [[branches]].")
    for item in raw_branches:
        role, label = item.get("role"), item.get("label")
        if role not in labels or not isinstance(label, str) or not label:
            raise ConfigError(f"branches: vai trò {role!r} không có trong roles, hoặc thiếu label.")
        branches.append(BranchRule(role, label, _phrases(item.get("phrases"), f"branches.{label}.phrases")))

    levels = _phrase_rules(raw, "levels")
    steps = _years_steps(raw, {r.label for r in levels})

    known = set(load_vocabulary().lookup.values())
    hints = {}
    for code, item in _table(raw, "skill_hints").items():
        if code not in known:
            raise ConfigError(f"skill_hints: mã {code} không có trong từ vựng kỹ năng.")
        if not isinstance(item, dict) or item.get("role") not in labels:
            raise ConfigError(f"skill_hints.{code}: role phải là một nhãn trong roles.")
        hints[code] = SkillHint(item["role"], _number(item, "weight", f"skill_hints.{code}"))
    non_tech = frozenset(_str_list(raw, "non_technical_skills"))
    qa_skills = frozenset(_str_list(raw, "qa_software_skills"))
    unknown = sorted((non_tech | qa_skills) - known)
    if unknown:
        raise ConfigError(f"non_technical_skills/qa_software_skills: mã {', '.join(unknown)} không có trong từ vựng.")

    ev = _table(raw, "evidence")
    evidence = EvidenceRules(
        min_tech_skills_without_title=int(_number(ev, "min_tech_skills_without_title", "evidence")),
        min_tech_skills_generic_title=int(_number(ev, "min_tech_skills_generic_title", "evidence")),
        min_tech_skills_override_non_it=int(_number(ev, "min_tech_skills_override_non_it", "evidence")),
        min_score=_number(ev, "min_score", "evidence"),
        win_ratio=_number(ev, "win_ratio", "evidence"),
        fullstack_min_each=_number(ev, "fullstack_min_each", "evidence"),
        fullstack_balance=_number(ev, "fullstack_balance", "evidence"),
        max_mentions_per_skill=int(_number(ev, "max_mentions_per_skill", "evidence")),
    )

    report_as = _table(raw, "report_as")
    for src, dst in report_as.items():
        if src not in labels or dst not in labels:
            raise ConfigError(f"report_as: {src!r} → {dst!r} phải là hai nhãn trong roles.")

    sec = _table(raw, "sections")
    masks = sec.get("masks", [])
    if not isinstance(masks, list) or not all(
        isinstance(m, list) and len(m) == 2 and all(isinstance(x, str) and x for x in m) for m in masks
    ):
        raise ConfigError("sections.masks phải là danh sách cặp [cụm, thay bằng].")
    sections = SectionRules(
        max_heading_chars=int(_number(sec, "max_heading_chars", "sections")),
        skip=_regex(sec.get("skip"), "sections.skip"),
        keep=_regex(sec.get("keep"), "sections.keep"),
        masks=tuple((fold(a), b) for a, b in masks),
    )
    yr = _table(raw, "years")
    years = YearsRules(
        window_chars=int(_number(yr, "window_chars", "years")),
        max_years=_number(yr, "max_years", "years"),
        context=_regex(yr.get("context"), "years.context"),
        reject=_regex(yr.get("reject"), "years.reject"),
        zero=_regex(yr.get("zero"), "years.zero"),
    )

    return ClassifyConfig(
        version=version,
        role_rules=tuple(roles),
        non_it_phrases=_phrases(_need(raw, "non_it_phrases"), "non_it_phrases"),
        non_it_categories=_str_list(raw, "non_it_categories"),
        it_only_sources=_str_list(raw, "it_only_sources"),
        seniority_rules=tuple(levels),
        city_rules=tuple(_phrase_rules(raw, "cities")),
        other_city_phrases=_phrases(_need(raw, "other_city_phrases"), "other_city_phrases"),
        multi_city=str(_need(raw, "multi_city")),
        art_phrases=_phrases(_need(raw, "art_phrases"), "art_phrases"),
        art_exceptions=_phrases(_need(raw, "art_exceptions"), "art_exceptions"),
        qa_hardware_phrases=_phrases(_need(raw, "qa_hardware_phrases"), "qa_hardware_phrases"),
        qa_software_phrases=_phrases(_need(raw, "qa_software_phrases"), "qa_software_phrases"),
        qa_software_skills=qa_skills,
        qa_min_tech_skills=_int(raw, "qa_min_tech_skills", 0),
        generic_it_titles=_phrases(_need(raw, "generic_it_titles"), "generic_it_titles"),
        branch_rules=tuple(branches),
        role_manager_phrases=_phrases(_need(raw, "role_manager_phrases"), "role_manager_phrases"),
        role_manager_keep=_phrases(_need(raw, "role_manager_keep"), "role_manager_keep"),
        ignore_source_levels=tuple(fold(v) for v in _str_list(raw, "ignore_source_levels")),
        years_to_level=steps,
        skill_hints=hints,
        non_technical_skills=non_tech,
        evidence=evidence,
        report_as=dict(report_as),
        max_text_chars=_int(raw, "max_text_chars", 1000),
        sections=sections,
        years=years,
    )


_classify_cache: dict[Path, Any] = {}


def load_classify_config(path: Path | str | None = None) -> Any:
    """Luật phân loại đã kiểm (`haido_core.domain.classify.ClassifyConfig`). File mặc định đọc một lần mỗi tiến trình."""
    target = Path(path) if path is not None else DEFAULT_CLASSIFY_PATH
    if path is None and target in _classify_cache:
        return _classify_cache[target]
    cfg = _build_classify(_read_toml(target))
    if path is None:
        _classify_cache[target] = cfg
    return cfg
