"""Định dạng mã kỹ năng và danh sách kỹ năng mồi (#205).

Mã kỹ năng là snake_case ASCII, tối đa 40 ký tự: an toàn không cần mã hóa trong `?have=a,b,c`
của link chia sẻ và của AD-22. `web/lib/haido-keys.ts` giữ cùng mẫu này.

Danh sách mồi nằm ở `skills_seed.json`, lấy từ các tag kỹ năng hay gặp nhất của bộ tin nền.
Bộ từ vựng v1 (#96) sẽ thay file đó; mã giữ nguyên định dạng.
"""

import json
import re
from dataclasses import dataclass
from functools import cache
from importlib.resources import files

SKILL_CODE_PATTERN = r"^[a-z0-9]+(_[a-z0-9]+)*$"
MAX_SKILL_CODE_LEN = 40
MAX_PROFILE_SKILLS = 200
"""Trần số mã trong một hồ sơ, cùng trần với `have=` của AD-22."""

_SKILL_CODE_RE = re.compile(SKILL_CODE_PATTERN)
_SEED_FILE = "skills_seed.json"


@dataclass(frozen=True, slots=True)
class SeedSkill:
    """Một kỹ năng của danh sách mồi."""

    code: str
    name_en: str
    name_vi: str
    aliases: tuple[str, ...]
    """Cách viết khác trong tin tuyển dụng, cả tiếng Anh và tiếng Việt. Ô tìm kiếm (#207) dò ở đây."""
    source: str


def is_skill_code(value: str) -> bool:
    """Đúng định dạng mã kỹ năng hay không."""
    return len(value) <= MAX_SKILL_CODE_LEN and _SKILL_CODE_RE.fullmatch(value) is not None


def normalize_term(term: str) -> str:
    """Khóa so khớp một tên hay bí danh: chữ thường, gộp khoảng trắng. Giữ dấu và ký hiệu (C#, C++)."""
    return " ".join(term.casefold().split())


def _load_document() -> dict[str, object]:
    raw = files("haido_core.vocab").joinpath(_SEED_FILE).read_text(encoding="utf-8")
    doc = json.loads(raw)
    if not isinstance(doc, dict):
        raise TypeError(f"{_SEED_FILE}: gốc phải là object.")
    return doc


def _parse(entry: object) -> SeedSkill:
    if not isinstance(entry, dict):
        raise TypeError(f"{_SEED_FILE}: mỗi kỹ năng phải là object, nhận {entry!r}.")
    code = entry.get("code")
    if not isinstance(code, str) or not is_skill_code(code):
        raise ValueError(f"{_SEED_FILE}: mã {code!r} sai định dạng {SKILL_CODE_PATTERN}.")
    texts = {k: entry.get(k) for k in ("name_en", "name_vi", "source")}
    empty = sorted(k for k, v in texts.items() if not isinstance(v, str) or not v.strip())
    if empty:
        raise ValueError(f"{_SEED_FILE}: {code} thiếu {', '.join(empty)}.")
    aliases = entry.get("aliases", [])
    if not isinstance(aliases, list) or not all(isinstance(a, str) and a.strip() for a in aliases):
        raise ValueError(f"{_SEED_FILE}: {code} có bí danh rỗng hoặc sai kiểu.")
    return SeedSkill(
        code=code,
        name_en=str(texts["name_en"]),
        name_vi=str(texts["name_vi"]),
        aliases=tuple(aliases),
        source=str(texts["source"]),
    )


@cache
def _seed() -> tuple[str, tuple[SeedSkill, ...]]:
    doc = _load_document()
    version = doc.get("version")
    if not isinstance(version, str) or not version.startswith("seed-"):
        raise ValueError(f"{_SEED_FILE}: version phải bắt đầu bằng 'seed-', nhận {version!r}.")
    entries = doc.get("skills")
    if not isinstance(entries, list) or not entries:
        raise ValueError(f"{_SEED_FILE}: thiếu danh sách skills.")
    skills = tuple(_parse(e) for e in entries)

    codes = [s.code for s in skills]
    if codes != sorted(set(codes)):
        raise ValueError(f"{_SEED_FILE}: mã phải không trùng và xếp theo thứ tự chữ cái.")
    owner: dict[str, str] = {}
    for skill in skills:
        for term in (skill.name_en, skill.name_vi, *skill.aliases):
            key = normalize_term(term)
            if owner.setdefault(key, skill.code) != skill.code:
                raise ValueError(f"{_SEED_FILE}: {term!r} thuộc cả {owner[key]} và {skill.code}.")
    return version, skills


def load_seed_skills() -> tuple[SeedSkill, ...]:
    """Danh sách mồi đã kiểm, theo thứ tự mã. File sai thì ném `ValueError` hoặc `TypeError`, không bỏ qua dòng hỏng."""
    return _seed()[1]


def seed_version() -> str:
    """Phiên bản của danh sách mồi, ví dụ `seed-2026-11-11`."""
    return _seed()[0]


VOCAB_VERSION = seed_version()


@dataclass(frozen=True, slots=True)
class Vocabulary:
    """Từ vựng để quét JD (#283). Mọi khóa đã bỏ dấu (`posting_text.fold`)."""

    version: str
    lookup: dict[str, str]
    """Tên và bí danh đã bỏ dấu → mã. Gồm cả từ không được quét riêng (`c`, `r`): phần của mã ghép tra ở đây."""
    scan_terms: tuple[str, ...]
    """Từ được tìm trong văn bản: `lookup` trừ `scan_skip` (mơ hồ khi đứng riêng), cộng mã ghép."""
    composites: dict[str, tuple[str, ...]]
    """Cụm ghép như `c/c++` → các phần (`c`, `c++`), mỗi phần là một lượt nhắc."""


@cache
def load_vocabulary() -> Vocabulary:
    """Từ vựng đã kiểm. Hai tên/bí danh trùng nhau sau khi bỏ dấu mà thuộc hai mã thì ném `ValueError`."""
    from haido_core.domain.posting_text import fold

    doc = _load_document()
    version, skills = _seed()
    lookup: dict[str, str] = {}
    for skill in skills:
        for term in (skill.name_en, skill.name_vi, *skill.aliases):
            key = fold(term)
            if lookup.setdefault(key, skill.code) != skill.code:
                raise ValueError(f"{_SEED_FILE}: {term!r} (bỏ dấu: {key!r}) thuộc cả {lookup[key]} và {skill.code}.")
    raw_composites = doc.get("composites", {})
    raw_skip = doc.get("scan_skip", [])
    if not isinstance(raw_composites, dict) or not isinstance(raw_skip, list):
        raise TypeError(f"{_SEED_FILE}: composites phải là object, scan_skip phải là danh sách.")
    composites: dict[str, tuple[str, ...]] = {}
    for term, parts in raw_composites.items():
        folded_parts = tuple(fold(p) for p in parts) if isinstance(parts, list) else ()
        if len(folded_parts) < 2 or any(p not in lookup for p in folded_parts):
            raise ValueError(f"{_SEED_FILE}: mã ghép {term!r} phải có từ hai phần, mỗi phần là tên hoặc bí danh.")
        composites[fold(term)] = folded_parts
    skip = {fold(t) for t in raw_skip if isinstance(t, str)}
    scan_terms = tuple(sorted((set(lookup) - skip) | set(composites)))
    return Vocabulary(version=version, lookup=lookup, scan_terms=scan_terms, composites=composites)
