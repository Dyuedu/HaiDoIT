"""Cấu hình có phiên bản từ `config/rules.toml` (AD-10, DoD dòng 4).

Thiếu khóa hoặc sai kiểu thì báo lỗi tiếng Việt, không tự điền giá trị mặc định.
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_RULES_PATH = Path(__file__).resolve().parents[1] / "config" / "rules.toml"

ALL_ROLES = "all"
"""Mã dành riêng cho "mọi vai trò"; không được nằm trong danh sách `roles`."""


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
    min_sample: int
    theta_core: float
    theta_common: float
    roles: tuple[str, ...]
    coverage_notes: tuple[CoverageNoteRule, ...]
    city_codes: dict[str, str]
    """Nhãn thành phố của bộ phân loại sang mã snake_case, theo thứ tự hiển thị."""
    role_codes: dict[str, str]
    level_codes: dict[str, str]


CITY_CODES = frozenset({"ha_noi", "ho_chi_minh", "da_nang", "other", "unknown"})
UNKNOWN = "unknown"


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

    return RulesConfig(
        config_version=version,
        window_days=window,
        auto_sources=tuple(auto),
        min_sample=min_sample,
        theta_core=thetas["theta_core"],
        theta_common=thetas["theta_common"],
        roles=tuple(roles),
        coverage_notes=notes,
        city_codes=city_codes,
        role_codes=role_codes,
        level_codes=level_codes,
    )
