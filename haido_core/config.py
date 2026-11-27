"""Cấu hình có phiên bản từ `config/rules.toml` (AD-10, DoD dòng 4).

Thiếu khóa hoặc sai kiểu thì báo lỗi tiếng Việt, không tự điền giá trị mặc định.
"""

import re
import tomllib
from dataclasses import dataclass
from datetime import date
from itertools import pairwise
from pathlib import Path
from typing import Any

DEFAULT_RULES_PATH = Path(__file__).resolve().parents[1] / "config" / "rules.toml"
DEFAULT_THETA_PATH = Path(__file__).resolve().parents[1] / "config" / "theta.toml"
"""Sổ đăng ký θ (#102): các phiên bản đã đóng băng, chỉ thêm."""
PRE_FREEZE_THETA_VERSION = "theta-1"
"""Phiên bản θ của snapshot có `snapshots.theta_version` NULL (tính trước khi đóng băng, #102). Bắt buộc là mục ĐẦU TIÊN
của `config/theta.toml`: NULL không phụ thuộc vào thứ tự hay vào phiên bản được thêm sau."""

_THETA_ENTRY_KEYS = ("id", "theta_core", "theta_common", "calibrated_on", "note")
_ISO_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")

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
class ThetaVersion:
    """Một phiên bản θ đã đóng băng trong `config/theta.toml` (#102)."""

    id: str
    theta_core: float
    theta_common: float
    calibrated_on: str
    """Ngày hiệu chỉnh, `YYYY-MM-DD`."""
    note: str


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
    theta_version: str
    """Phiên bản θ hiện hành (#102): phiên bản mà `aggregate` ghi vào snapshot mới."""
    theta_core: float
    """θ_core của `theta_version` hiện hành. Snapshot đã tính đọc θ của chính nó qua `theta(version)`."""
    theta_common: float
    theta_versions: tuple[ThetaVersion, ...]
    """Mọi phiên bản trong sổ đăng ký, theo thứ tự thêm. Phiên bản đầu là phiên bản của snapshot chưa ghi phiên bản."""
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
    posting_match_weights: dict[str, int]
    """Trọng số mức khớp tin dán (FR-28, #230), khóa `core`, `common`, `specific`; số nguyên dương, giảm dần theo thứ tự đó."""
    posting_max_chars: int
    """Số ký tự tối đa của chữ dán (FR-26: 20.000). `POST /api/v1/posting-reads` từ chối chữ dài hơn bằng 413 `text_too_long`."""
    posting_max_body_bytes: int
    """Số byte tối đa của thân `POST /api/v1/posting-reads` (AD-9). Kiểm bằng `Content-Length` rồi đếm lúc đọc, trước khi phân tích JSON."""
    posting_ci_below_n: int
    """Cỡ mẫu `n` mà từ đó phân vị của tin dán không còn kèm khoảng tin cậy 95% (FR-30, AD-26): có khoảng khi `min_sample <= n < ci_below_n`."""
    always_cities: tuple[str, ...] = ()
    """Nơi luôn có hàng trong `stat_*` (#285); nơi khác chỉ có hàng khi có tin."""
    """Mốc "tối đa N năm kinh nghiệm" của bản đồ (#280), tăng dần, không gồm `any`. Mã của mốc là `str(N)`."""

    def theta(self, version: str) -> ThetaVersion:
        """θ của một phiên bản trong sổ đăng ký (#102).

        Raises:
            KeyError: phiên bản không có trong sổ đăng ký.
        """
        for entry in self.theta_versions:
            if entry.id == version:
                return entry
        raise KeyError(version)


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

UNKNOWN = "unknown"

POSTING_WEIGHT_GROUPS: tuple[str, ...] = ("core", "common", "specific")
"""Ba nhóm của mức khớp tin dán, theo thứ tự trọng số giảm dần (`specific` là nhóm `company_specific` của θ)."""


def _posting_match_weights(raw: dict[str, Any]) -> dict[str, int]:
    """`[posting_match]` (#230): `weight_core`, `weight_common`, `weight_specific` là số nguyên dương, không tăng dần."""
    table = raw.get("posting_match")
    if table is None:
        raise ConfigError("Cấu hình thiếu bảng posting_match.")
    keys = {f"weight_{group}" for group in POSTING_WEIGHT_GROUPS}
    if not isinstance(table, dict) or set(table) != keys:
        raise ConfigError(f"posting_match phải có đúng các khóa {', '.join(sorted(keys))}.")
    weights: dict[str, int] = {}
    for group in POSTING_WEIGHT_GROUPS:
        value = table[f"weight_{group}"]
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ConfigError(f"posting_match.weight_{group} phải là số nguyên từ 1 trở lên.")
        weights[group] = value
    if any(a < b for a, b in pairwise(weights.values())):
        raise ConfigError("posting_match: trọng số phải giảm dần từ core, common đến specific (không tăng).")
    return weights


POSTING_READ_BYTES_LIMIT = 1024 * 1024
"""Trần tuyệt đối của `posting_read.max_body_bytes`, để cấu hình sai không mở cửa cho thân lớn vào bộ nhớ."""


def _plain_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _posting_read(raw: dict[str, Any]) -> tuple[int, int]:
    """`[posting_read]` (#230, FR-26, AD-9): `max_chars` và `max_body_bytes`, số nguyên dương; byte không ít hơn ký tự, không quá 1 MiB."""
    table = raw.get("posting_read")
    if table is None:
        raise ConfigError("Cấu hình thiếu bảng posting_read.")
    if not isinstance(table, dict) or set(table) != {"max_chars", "max_body_bytes"}:
        raise ConfigError("posting_read phải có đúng các khóa max_body_bytes, max_chars.")
    chars, size = table["max_chars"], table["max_body_bytes"]
    if not _plain_int(chars) or chars < 1:
        raise ConfigError("posting_read.max_chars phải là số nguyên từ 1 trở lên.")
    if not _plain_int(size) or not chars <= size <= POSTING_READ_BYTES_LIMIT:
        raise ConfigError(
            f"posting_read.max_body_bytes phải là số nguyên byte từ max_chars ({chars}) đến {POSTING_READ_BYTES_LIMIT}."
        )
    return chars, size


def _posting_ci_below_n(raw: dict[str, Any], min_sample: int) -> int:
    """`[posting_market]` (#230, FR-30, AD-26): `ci_below_n` là số nguyên lớn hơn `min_sample`."""
    table = raw.get("posting_market")
    if table is None:
        raise ConfigError("Cấu hình thiếu bảng posting_market.")
    if not isinstance(table, dict) or set(table) != {"ci_below_n"}:
        raise ConfigError("posting_market phải có đúng khóa ci_below_n.")
    value = table["ci_below_n"]
    if not _plain_int(value) or value <= min_sample:
        raise ConfigError(f"posting_market.ci_below_n phải là số nguyên lớn hơn min_sample ({min_sample}).")
    return value


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


def _theta_entry(entry: Any, position: int) -> ThetaVersion:
    where = f"theta.toml, versions[{position}]"
    if not isinstance(entry, dict):
        raise ConfigError(f"{where} phải là một bảng.")
    for key in ("id", "theta_core", "theta_common", "calibrated_on", "note"):
        if key not in entry:
            raise ConfigError(f"{where} thiếu khóa {key}.")
    unknown = sorted(str(k) for k in entry if k not in _THETA_ENTRY_KEYS)
    if unknown:
        raise ConfigError(f"{where} có khóa lạ: {', '.join(unknown)}.")
    for key in ("id", "calibrated_on", "note"):
        if not isinstance(entry[key], str) or not entry[key].strip():
            raise ConfigError(f"{where}: {key} phải là chuỗi không rỗng.")
    if entry["id"] != entry["id"].strip():
        raise ConfigError(f"{where}: id không được có khoảng trắng ở hai đầu ({entry['id']!r}).")
    try:
        if not _ISO_DATE.fullmatch(entry["calibrated_on"]):
            raise ValueError(entry["calibrated_on"])
        date.fromisoformat(entry["calibrated_on"])
    except ValueError:
        raise ConfigError(
            f"{where}: calibrated_on phải là ngày dạng YYYY-MM-DD (theta {entry['id']}), nhận {entry['calibrated_on']!r}."
        ) from None
    values: dict[str, float] = {}
    for key in ("theta_core", "theta_common"):
        value = entry[key]
        if not _is_number(value) or not 0 <= value <= 1:
            raise ConfigError(f"{where}: {key} phải là số từ 0 đến 1 (theta {entry['id']}).")
        values[key] = float(value)
    if values["theta_common"] > values["theta_core"]:
        raise ConfigError(f"{where}: theta_common không được lớn hơn theta_core (theta {entry['id']}).")
    return ThetaVersion(entry["id"], values["theta_core"], values["theta_common"], entry["calibrated_on"], entry["note"])


def load_theta_versions(path: Path | str | None = None) -> tuple[ThetaVersion, ...]:
    """Đọc sổ đăng ký θ (`config/theta.toml`, #102). Id trùng, giá trị sai hay thiếu file đều là `ConfigError`."""
    target = Path(path) if path is not None else DEFAULT_THETA_PATH
    raw = _read_toml(target)
    unknown = sorted(str(k) for k in raw if k != "versions")
    if unknown:
        raise ConfigError(f"theta.toml có khóa lạ ở cấp cao nhất: {', '.join(unknown)}; chỉ có các mục [[versions]].")
    entries = raw.get("versions")
    if not isinstance(entries, list) or not entries:
        raise ConfigError("theta.toml phải có ít nhất một mục [[versions]] (versions là danh sách bảng).")
    versions = tuple(_theta_entry(entry, i) for i, entry in enumerate(entries))
    ids = [v.id for v in versions]
    duplicated = sorted({i for i in ids if ids.count(i) > 1})
    if duplicated:
        raise ConfigError(f"theta.toml có id trùng: {', '.join(duplicated)}.")
    if versions[0].id != PRE_FREEZE_THETA_VERSION:
        raise ConfigError(
            f"theta.toml: mục [[versions]] đầu tiên phải là {PRE_FREEZE_THETA_VERSION!r} (phiên bản của snapshot chưa ghi "
            f"theta_version), nhận {versions[0].id!r}."
        )
    return versions


def load_rules(path: Path | str | None = None, *, theta_path: Path | str | None = None) -> RulesConfig:
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

    legacy = [key for key in ("theta_core", "theta_common") if key in raw]
    if legacy:
        raise ConfigError(
            f"rules.toml còn khóa {', '.join(legacy)}: θ nay nằm ở config/theta.toml và rules.toml chỉ chọn phiên bản "
            "hiện hành bằng khóa theta_version."
        )
    theta_version = raw.get("theta_version")
    if theta_version is None:
        raise ConfigError("Cấu hình thiếu khóa theta_version.")
    if not isinstance(theta_version, str) or not theta_version.strip():
        raise ConfigError("theta_version phải là chuỗi không rỗng.")
    theta_versions = load_theta_versions(theta_path)
    current = next((v for v in theta_versions if v.id == theta_version), None)
    if current is None:
        known = ", ".join(v.id for v in theta_versions)
        raise ConfigError(f"theta_version {theta_version!r} không có trong sổ đăng ký θ (có: {known}).")

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
    if UNKNOWN not in city_codes.values() or not all(_CODE_SHAPE.fullmatch(c) for c in city_codes.values()):
        raise ConfigError(f"labels.city phải có mã {UNKNOWN!r} và mọi mã dạng snake_case không dấu.")
    always = raw.get("always_cities")
    if always is None:
        raise ConfigError("Cấu hình thiếu khóa always_cities.")
    if (
        not isinstance(always, list)
        or not all(isinstance(c, str) for c in always)
        or len(set(always)) != len(always)
        or not set(always) <= set(city_codes.values())
        or UNKNOWN not in always
    ):
        raise ConfigError("always_cities phải là danh sách mã trong labels.city, không trùng, có 'unknown'.")
    if UNKNOWN not in level_codes.values():
        raise ConfigError(f"labels.level phải có mã {UNKNOWN!r}.")
    if set(role_codes.values()) != set(roles):
        raise ConfigError("roles phải đúng bằng tập mã trong labels.role.")
    level_options, level_groups = _level_filter(raw, level_codes)
    years_options = _years_options(raw)
    posting_match_weights = _posting_match_weights(raw)
    posting_max_chars, posting_max_body_bytes = _posting_read(raw)

    return RulesConfig(
        config_version=version,
        window_days=window,
        auto_sources=tuple(auto),
        source_priority=tuple(priority_norm),
        excluded_sources=tuple(excluded),
        min_sample=min_sample,
        theta_version=current.id,
        theta_core=current.theta_core,
        theta_common=current.theta_common,
        theta_versions=theta_versions,
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
        posting_match_weights=posting_match_weights,
        posting_max_chars=posting_max_chars,
        posting_max_body_bytes=posting_max_body_bytes,
        posting_ci_below_n=_posting_ci_below_n(raw, min_sample),
        always_cities=tuple(always),
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


def _address_rules(raw: dict[str, Any]) -> Any:
    from haido_core.domain.classify import AddressRules

    table = _table(raw, "address")
    return AddressRules(
        keys=_regex(table.get("keys"), "address.keys"),
        window_chars=int(_number(table, "window_chars", "address")),
        next_lines=int(_number(table, "next_lines", "address")),
    )


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
        abroad_phrases=_phrases(_need(raw, "abroad_phrases"), "abroad_phrases"),
        abroad_location_phrases=_phrases(_need(raw, "abroad_location_phrases"), "abroad_location_phrases"),
        remote_phrases=_phrases(_need(raw, "remote_phrases"), "remote_phrases"),
        address=_address_rules(raw),
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
