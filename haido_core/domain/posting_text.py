"""Đọc văn bản JD trong bộ nhớ cho phép 6 (#283): mục yêu cầu, lượt nhắc kỹ năng, số năm tối thiểu.

Không hàm nào ở đây ghi văn bản ra đâu cả. Kết quả là chuỗi đã bỏ dấu (chỉ để quét), lượt nhắc neo vị trí,
mã kỹ năng có số lượt, và số năm. Quy tắc (tiêu đề mục, ngưỡng) đến từ `ClassifyConfig`, không viết trong nhánh if.
Không phải một trong tám phép của REGISTRY.md: đây là bước chuẩn bị đầu vào của phép 1 và phép 6.
"""

from __future__ import annotations

import json
import re
import unicodedata
from functools import cache
from typing import TYPE_CHECKING

from haido_core.domain.registry import Mention

if TYPE_CHECKING:
    from haido_core.domain.classify import ClassifyConfig
    from haido_core.domain.mapping import VocabularyMapper
    from haido_core.vocab.skills import Vocabulary

_WS = re.compile(r"[ \t\f\v ]+")


def fold(text: str | None) -> str:
    """Chữ thường, bỏ dấu tiếng Việt (đ → d), gộp khoảng trắng trên từng dòng. Giữ xuống dòng và ký hiệu (c#, c++)."""
    if not text:
        return ""
    decomposed = unicodedata.normalize("NFD", text.casefold())
    plain = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn").replace("đ", "d")
    lines = (_WS.sub(" ", line).strip() for line in plain.replace("\r", "").split("\n"))
    return "\n".join(line for line in lines if line)


def requirement_text(text: str | None, cfg: ClassifyConfig) -> str:
    """Chuỗi đã bỏ dấu của các mục yêu cầu và nhiệm vụ.

    Gặp tiêu đề mục bỏ (quyền lợi, giới thiệu công ty, địa điểm…) thì ngừng giữ tới tiêu đề mục giữ kế tiếp.
    Văn bản không có tiêu đề nào thì giữ hết. "khoa học máy tính" được che để không thành "học máy".
    """
    rules = cfg.sections
    keep = True
    out: list[str] = []
    for line in fold((text or "")[: cfg.max_text_chars]).split("\n"):
        if len(line) <= rules.max_heading_chars:
            if rules.skip.match(line):
                keep = False
                continue
            if rules.keep.match(line):
                keep = True
        if keep:
            out.append(line)
    body = "\n".join(out)
    for phrase, mask in rules.masks:
        body = body.replace(phrase, mask)
    return body[: cfg.max_text_chars]


def address_text(text: str | None, cfg: ClassifyConfig) -> str:
    """Dòng địa chỉ của JD, đã bỏ dấu (#285): từ chỗ khớp một khóa địa chỉ, `window_chars` ký tự, cộng `next_lines` dòng
    kế (mỗi dòng cũng cắt `window_chars`). Chữ ngoài các dòng đó không được trả về."""
    rules = cfg.address
    lines = fold((text or "")[: cfg.max_text_chars]).split("\n")
    out: list[str] = []
    for i, line in enumerate(lines):
        match = rules.keys.search(line)
        if match is None:
            continue
        out.append(line[match.start() : match.start() + rules.window_chars])
        out.extend(nxt[: rules.window_chars] for nxt in lines[i + 1 : i + 1 + rules.next_lines])
    return "\n".join(out)


@cache
def _scanner(terms: tuple[str, ...]) -> re.Pattern[str]:
    alternation = "|".join(re.escape(t) for t in sorted(terms, key=lambda t: (-len(t), t)))
    return re.compile(r"(?<![a-z0-9])(" + alternation + r")(?![a-z0-9#+])")


def find_mentions(text: str, vocab: Vocabulary) -> tuple[Mention, ...]:
    """Lượt nhắc trong chuỗi đã bỏ dấu: cụm dài trước, không chồng lấn. Mã ghép ("c/c++") tách thành từng phần."""
    out: list[Mention] = []
    for match in _scanner(vocab.scan_terms).finditer(text):
        term = match.group(1)
        parts = vocab.composites.get(term)
        if parts is None:
            out.append(Mention(term, match.start(), match.end()))
            continue
        offset = match.start()
        for part in parts:
            at = text.find(part, offset, match.end())
            out.append(Mention(part, at, at + len(part)))
            offset = at + len(part)
    return tuple(out)


def skill_counts(text: str, vocab: Vocabulary, mapper: VocabularyMapper) -> dict[str, int]:
    """Mã kỹ năng → số lượt nhắc (kể cả lặp lại). Lượt nhắc không khớp mã thì bỏ, không đoán."""
    mentions = find_mentions(text, vocab)
    mapped = mapper.map_mentions(list(mentions))
    counts: dict[str, int] = {}
    for item in mapped:
        if item.skill_id is not None:
            counts[item.skill_id] = counts.get(item.skill_id, 0) + 1
    return counts


_NUM = r"(\d{1,2}(?:[.,]5)?)"
_UNIT = r"(?:nam|years?|yrs?)"
_RANGE = re.compile(_NUM + r"\s*\+?\s*(?:-|–|~|den|to)\s*" + _NUM + r"\s*\+?\s*" + _UNIT + r"(?![a-z])")
_SINGLE = re.compile(_NUM + r"\s*\+?\s*" + _UNIT + r"(?![a-z])")
_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "ten": 10}
_WORD = re.compile(r"\b(" + "|".join(_WORDS) + r")\s*\+?\s*(?:continuous\s+)?" + _UNIT + r"(?![a-z])")


def _source_years(source_experience: str | None) -> float | None:
    """Số năm từ trường có cấu trúc của nguồn: JSON `monthsOfExperience` (CareerLink) hoặc "no requirements"."""
    if not source_experience:
        return None
    raw = source_experience.strip()
    if raw.startswith("{"):
        try:
            months = json.loads(raw).get("monthsOfExperience")
        except (ValueError, AttributeError):
            return None
        if isinstance(months, int | float) and not isinstance(months, bool) and months >= 0:
            return round(months / 12, 1)
        return None
    if fold(raw) in {"no requirements", "khong yeu cau", "khong yeu cau kinh nghiem"}:
        return 0.0
    return None


def _text_years(text: str, cfg: ClassifyConfig) -> float | None:
    rules = cfg.years
    found: list[float] = []
    ranges: list[tuple[int, int]] = []
    for pattern in (_RANGE, _SINGLE, _WORD):
        for match in pattern.finditer(text):
            if pattern is _RANGE:
                ranges.append(match.span())
            elif any(start <= match.start() < end for start, end in ranges):
                continue  # "5 năm" trong "3–5 năm": khoảng lấy đầu dưới
            window = text[max(0, match.start() - rules.window_chars) : match.end() + rules.window_chars]
            if not rules.context.search(window) or rules.reject.search(window):
                continue
            raw = match.group(1)
            value = float(_WORDS[raw]) if raw in _WORDS else float(raw.replace(",", "."))
            if value <= rules.max_years:
                found.append(value)
    if found:
        # Yêu cầu chính: câu phụ kiểu "trong đó 2 năm quản lý" luôn nhỏ hơn yêu cầu chung.
        return max(found)
    if rules.zero.search(text):
        return 0.0
    return None


def resolve_years(source_experience: str | None, extracted: float | None, text: str, cfg: ClassifyConfig) -> float | None:
    """Số năm tối thiểu: số tháng có cấu trúc của nguồn → giá trị bước trích → luật đọc mục yêu cầu.

    Bước trích để trống mà mục yêu cầu nói "không yêu cầu kinh nghiệm" thì 0.
    """
    from_source = _source_years(source_experience)
    if from_source is not None:
        return from_source
    if extracted is not None:
        return float(extracted)
    return _text_years(text, cfg)
