"""
Trích kỹ năng từ văn bản JD tự do (cho nguồn không có trường `skills`: API ATS, trang tuyển dụng công ty).

Quét văn bản tìm các khóa của `taxonomy.json` (qua `normalizer.alias_keys()`), rồi đưa phần khớp qua
`normalizer.normalize_batch` (AD-6). Văn bản chỉ được đọc trong bộ nhớ và bị bỏ ngay sau khi trích (AD-7);
hàm chỉ trả tên kỹ năng.

Bí danh trùng với từ thông dụng được siết lại để không khớp nhầm:
- `go`, `rest`, `node`, `spring`, `react`, `vue`, `js`, `ts`: chỉ khớp đúng kiểu viết công nghệ
  (`Go`, `REST`, `Node`, `Spring`, `React`, `Vue`, `JS`, `TS`), không khớp chữ thường;
- `Go`, `Spring` còn phải đứng trong ngữ cảnh liệt kê (cạnh `, / ( ) ;` hoặc cuối dòng), vì "Go beyond...",
  "Spring 2026" cũng viết hoa;
- `container` không bao giờ được quét (quá chung chung).
"""
import re
import unicodedata
from html import unescape
from typing import Dict, List, Optional, Pattern, Tuple

from scraper.normalizer import NormalizedSkill, normalizer

# khóa viết thường -> dạng viết hoa duy nhất được chấp nhận trong văn bản
_CASED_ONLY: Dict[str, str] = {
    "go": "Go",
    "rest": "REST",
    "node": "Node",
    "spring": "Spring",
    "react": "React",
    "vue": "Vue",
    "js": "JS",
    "ts": "TS",
}
_LIST_CONTEXT_ONLY = {"go", "spring"}
_NEVER_SCAN = {"container"}
_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")
# ranh giới "từ" cho tên công nghệ có ký tự đặc biệt (.NET, C#, CI/CD, Node.js)
_BEFORE = r"(?<![A-Za-z0-9_+#.])"
_AFTER = r"(?![A-Za-z0-9_+#]|\.[A-Za-z0-9])"

_cache: Tuple[Optional[Tuple[str, ...]], Optional[Pattern], Optional[Pattern]] = (None, None, None)


def html_to_text(html: Optional[str]) -> str:
    """HTML (kể cả HTML đã escape một lần nữa như Greenhouse) -> văn bản thuần một dòng."""
    if not html:
        return ""
    text = unescape(html)
    if "&lt;" in text or "&amp;" in text:
        text = unescape(text)
    text = _TAG_RE.sub(" ", text)
    return _WS_RE.sub(" ", unicodedata.normalize("NFC", text)).strip()


def _patterns() -> Tuple[Pattern, Optional[Pattern]]:
    """(regex không phân biệt hoa thường cho khóa thường, regex phân biệt hoa thường cho khóa nhập nhằng).
    Dựng lại khi bản đồ bí danh đổi (nạp taxonomy.json / fallback)."""
    global _cache
    keys = tuple(sorted(normalizer.alias_keys()))
    if _cache[0] == keys:
        return _cache[1], _cache[2]
    plain = [k for k in keys if k not in _CASED_ONLY and k not in _NEVER_SCAN and len(k) >= 2]
    plain.sort(key=len, reverse=True)  # khóa dài trước: "spring boot" trước "spring"
    plain_re = re.compile(_BEFORE + "(" + "|".join(re.escape(k) for k in plain) + ")" + _AFTER, re.IGNORECASE)
    cased = [re.escape(form) for key, form in _CASED_ONLY.items() if key in keys]
    cased_re = re.compile(_BEFORE + "(" + "|".join(cased) + ")" + _AFTER) if cased else None
    _cache = (keys, plain_re, cased_re)
    return plain_re, cased_re


def _in_list_context(text: str, start: int, end: int) -> bool:
    """Ký tự không trắng liền trước là `, / ( ;` hoặc liền sau là `, / ) ;` / hết văn bản."""
    before = text[:start].rstrip()[-1:]
    after = text[end:].lstrip()[:1]
    return before in (",", "/", "(", ";") or after in (",", "/", ")", ";", "")


def extract_skill_names(text: str) -> List[str]:
    """Tên kỹ năng thô xuất hiện trong văn bản (theo thứ tự xuất hiện, không trùng không phân biệt hoa thường)."""
    if not text:
        return []
    plain_re, cased_re = _patterns()
    plain_hits = [(m.start(), m.end(), m.group(1)) for m in plain_re.finditer(text)]
    hits: List[Tuple[int, str]] = [(start, name) for start, _, name in plain_hits]
    if cased_re is not None:
        for m in cased_re.finditer(text):
            if any(s <= m.start() and m.end() <= e for s, e, _ in plain_hits):
                continue  # "Spring" nằm trong "Spring Boot" đã khớp
            if m.group(1).lower() in _LIST_CONTEXT_ONLY and not _in_list_context(text, m.start(), m.end()):
                continue
            hits.append((m.start(), m.group(1)))
    out, seen = [], set()
    for _, name in sorted(hits):
        if name.lower() not in seen:
            seen.add(name.lower())
            out.append(name)
    return out


def skills_from_text(*parts: Optional[str]) -> List[NormalizedSkill]:
    """Kỹ năng đã chuẩn hóa (chỉ mục khớp taxonomy) từ các đoạn HTML/văn bản; trùng tên chuẩn bị gộp."""
    text = " \n ".join(html_to_text(p) for p in parts if p)
    skills, _ = normalizer.normalize_batch(extract_skill_names(text))
    out, seen = [], set()
    for s in skills:
        if s.matched and s.canonical_name not in seen:
            seen.add(s.canonical_name)
            out.append(s)
    return out
