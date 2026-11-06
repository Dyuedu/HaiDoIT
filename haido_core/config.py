"""Cấu hình có phiên bản từ `config/rules.toml` (AD-10, DoD dòng 4).

Thiếu khóa hoặc sai kiểu thì báo lỗi tiếng Việt, không tự điền giá trị mặc định.
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path

DEFAULT_RULES_PATH = Path(__file__).resolve().parents[1] / "config" / "rules.toml"


class ConfigError(ValueError):
    """Lỗi cấu hình. Thông báo bằng tiếng Việt."""


@dataclass(frozen=True, slots=True)
class RulesConfig:
    config_version: str
    window_days: int
    auto_sources: tuple[str, ...]


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

    return RulesConfig(config_version=version, window_days=window, auto_sources=tuple(auto))
