"""Định dạng mã kỹ năng và danh sách kỹ năng mồi (#205).

Mã kỹ năng là snake_case ASCII, tối đa 40 ký tự: an toàn không cần mã hóa trong `?have=a,b,c`
của link chia sẻ và của AD-22. `web/lib/haido-keys.ts` giữ cùng mẫu này.

Danh sách mồi nằm ở `skills_seed.json`, lấy từ các tag kỹ năng hay gặp nhất của bộ tin nền.
Thẻ hay gặp mà cố ý không gán mã nằm ở `skills_excluded.json`, kèm lý do (#278).
Bộ từ vựng v1 (#96) sẽ thay các file đó; mã giữ nguyên định dạng.
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
_EXCLUDED_FILE = "skills_excluded.json"


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


@cache
def _by_code() -> dict[str, SeedSkill]:
    return {s.code: s for s in _seed()[1]}


def find_seed_skill(code: str) -> SeedSkill | None:
    """Kỹ năng của danh sách mồi theo mã, hoặc `None` khi mã không có trong bộ từ vựng (#166)."""
    return _by_code().get(code)


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
        key = fold(term)
        outside = [p for p in folded_parts if p not in key]
        if outside:
            raise ValueError(f"{_SEED_FILE}: phần {outside} của mã ghép {term!r} không nằm trong cụm, không neo được vị trí.")
        composites[key] = folded_parts
    skip = {fold(t) for t in raw_skip if isinstance(t, str)}
    scan_terms = tuple(sorted((set(lookup) - skip) | set(composites)))
    return Vocabulary(version=version, lookup=lookup, scan_terms=scan_terms, composites=composites)


@dataclass(frozen=True, slots=True)
class ExcludedSkill:
    """Một thẻ hay gặp mà cố ý không có mã kỹ năng (#278)."""

    key: str
    """Dạng đã bỏ dấu (`posting_text.fold`), cùng dạng với khóa của `Vocabulary.lookup`."""
    spelling: str
    reason: str
    postings: int
    """Số tin nhắc thẻ ở snapshot nguồn: bằng chứng rằng thẻ đủ hay gặp để phải có lý do."""


@dataclass(frozen=True, slots=True)
class ExclusionList:
    version: str
    snapshot: str
    entries: tuple[ExcludedSkill, ...]

    @property
    def keys(self) -> frozenset[str]:
        return frozenset(e.key for e in self.entries)


def _parse_excluded(entry: object) -> ExcludedSkill:
    from haido_core.domain.posting_text import fold

    if not isinstance(entry, dict):
        raise TypeError(f"{_EXCLUDED_FILE}: mỗi dòng phải là object, nhận {entry!r}.")
    key, spelling, reason, postings = (entry.get(k) for k in ("key", "spelling", "reason", "postings"))
    if not isinstance(key, str) or not key.strip() or fold(key) != key:
        raise ValueError(f"{_EXCLUDED_FILE}: khóa {key!r} phải không rỗng và đã bỏ dấu.")
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError(f"{_EXCLUDED_FILE}: {key!r} thiếu lý do loại trừ.")
    if not isinstance(spelling, str) or not spelling.strip():
        raise ValueError(f"{_EXCLUDED_FILE}: {key!r} thiếu cách viết gốc.")
    if isinstance(postings, bool) or not isinstance(postings, int) or postings < 1:
        raise ValueError(f"{_EXCLUDED_FILE}: {key!r} thiếu số tin làm bằng chứng.")
    return ExcludedSkill(key=key, spelling=spelling, reason=reason, postings=postings)


def parse_exclusions(doc: object, vocab: Vocabulary) -> ExclusionList:
    """Kiểm một danh sách loại trừ đã đọc từ JSON với từ vựng `vocab`; sai thì ném `ValueError` hoặc `TypeError`."""
    if not isinstance(doc, dict):
        raise TypeError(f"{_EXCLUDED_FILE}: gốc phải là object.")
    version, snapshot, entries = doc.get("version"), doc.get("snapshot"), doc.get("entries")
    if not isinstance(version, str) or not version.startswith("excluded-"):
        raise ValueError(f"{_EXCLUDED_FILE}: version phải bắt đầu bằng 'excluded-', nhận {version!r}.")
    if not isinstance(snapshot, str) or not snapshot:
        raise ValueError(f"{_EXCLUDED_FILE}: thiếu snapshot nguồn.")
    if not isinstance(entries, list) or not entries:
        raise ValueError(f"{_EXCLUDED_FILE}: thiếu danh sách entries.")
    parsed = tuple(_parse_excluded(e) for e in entries)
    keys = [e.key for e in parsed]
    if len(keys) != len(set(keys)):
        dup = sorted({k for k in keys if keys.count(k) > 1})
        raise ValueError(f"{_EXCLUDED_FILE}: khóa trùng {dup}.")
    clash = sorted(set(keys) & (set(vocab.lookup) | set(vocab.composites)))
    if clash:
        raise ValueError(f"{_EXCLUDED_FILE}: {clash} vừa bị loại trừ vừa có trong từ vựng.")
    return ExclusionList(version=version, snapshot=snapshot, entries=parsed)


@cache
def load_exclusions() -> ExclusionList:
    """Danh sách loại trừ đã kiểm (xem `parse_exclusions`)."""
    raw = files("haido_core.vocab").joinpath(_EXCLUDED_FILE).read_text(encoding="utf-8")
    return parse_exclusions(json.loads(raw), load_vocabulary())
