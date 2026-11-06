"""Phép 6: gán vai trò, cấp bậc, thành phố bằng luật (Story 1.20, AD-2).

Luật chỉ đọc chức danh, nguồn, danh mục nguồn, chữ cấp bậc và chữ địa điểm.
Không gọi mô hình. Cùng đầu vào và cùng cấu hình thì cùng nhãn.
Danh sách từ khóa nằm trong `ClassifyConfig`, không viết trong nhánh if.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from haido_core.domain.registry import Classification, OneOrMany, PostingFacts, as_batch

NON_IT = "không thuộc IT"
UNKNOWN = "không xác định"
OTHER_CITY = "Khác"
OTHER_ROLE = "Other"


@dataclass(frozen=True, slots=True)
class PhraseRule:
    """Cụm khớp trước thì thắng. Cụm so khớp theo biên từ, không nuốt chữ bên trong."""

    label: str
    phrases: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ClassifyConfig:
    """Bảng luật có phiên bản. Đổi luật là đổi object này, không đổi hàm."""

    version: str
    role_rules: tuple[PhraseRule, ...]
    non_it_phrases: tuple[str, ...]
    non_it_categories: tuple[str, ...]
    it_only_sources: tuple[str, ...]
    seniority_rules: tuple[PhraseRule, ...]
    city_rules: tuple[PhraseRule, ...]
    other_city_phrases: tuple[str, ...]
    multi_city: str = "first_phrase"


def _fold(text: str) -> str:
    return text.casefold()


def _phrase_at(text: str, phrase: str) -> int | None:
    """Vị trí cụm, hoặc None. Hai đầu cụm không được là chữ hoặc số."""
    haystack = _fold(text)
    needle = _fold(phrase)
    if not needle:
        return None
    start = 0
    while True:
        found = haystack.find(needle, start)
        if found < 0:
            return None
        before = found == 0 or not haystack[found - 1].isalnum()
        end = found + len(needle)
        after = end == len(haystack) or not haystack[end].isalnum()
        if before and after:
            return found
        start = found + 1


def _first_rule(text: str, rules: tuple[PhraseRule, ...]) -> str | None:
    winner: tuple[int, int, str] | None = None
    for order, rule in enumerate(rules):
        for phrase in rule.phrases:
            at = _phrase_at(text, phrase)
            if at is None:
                continue
            candidate = (at, order, rule.label)
            if winner is None or candidate < winner:
                winner = candidate
    return None if winner is None else winner[2]


def _any_phrase(text: str, phrases: tuple[str, ...]) -> bool:
    return any(_phrase_at(text, phrase) is not None for phrase in phrases)


def default_classify_config() -> ClassifyConfig:
    """Luật v1. Embedded và ba nhánh Data đứng trước Other. Nhánh thuộc Story 1.9."""
    return ClassifyConfig(
        version="classify-v1",
        role_rules=(
            PhraseRule("Embedded", ("embedded", "firmware", "rtos", "lập trình nhúng", "vi điều khiển")),
            PhraseRule(
                "AI/ML Engineer",
                ("machine learning", "deep learning", "ai/ml", "ai engineer", "học máy", "nlp", "computer vision"),
            ),
            PhraseRule("Data Engineer", ("data engineer", "kỹ sư dữ liệu", "etl", "airflow")),
            PhraseRule(
                "Data Analyst/BI",
                ("data analyst", "business intelligence", "power bi", "phân tích dữ liệu"),
            ),
            PhraseRule("QA/Tester", ("quality assurance", "kiểm thử", "tester", "qa")),
            PhraseRule("DevOps", ("devops", "site reliability", "sre")),
            PhraseRule("Mobile", ("react native", "flutter", "android", "ios")),
            PhraseRule("Frontend", ("frontend", "front-end", "reactjs", "react.js", "vue")),
            PhraseRule("Backend", ("backend", "back-end", "java", "golang", "spring", ".net")),
        ),
        non_it_phrases=(
            "kế toán",
            "nhân sự",
            "tuyển dụng",
            "pháp chế",
            "sales",
            "marketing",
        ),
        non_it_categories=("finance", "hr", "human resources", "legal", "accounting", "sales"),
        it_only_sources=("itviec", "topdev", "itnavi"),
        seniority_rules=(
            PhraseRule("Intern", ("intern", "thực tập")),
            PhraseRule("Fresher", ("fresher",)),
            PhraseRule("Junior", ("junior",)),
            PhraseRule("Mid", ("middle", "mid-level", "mid level", "mid")),
            PhraseRule("Senior", ("senior",)),
            PhraseRule("Lead", ("principal", "staff engineer", "tech lead", "lead")),
        ),
        city_rules=(
            PhraseRule("Hà Nội", ("hà nội", "ha noi", "hanoi")),
            PhraseRule("TP.HCM", ("hồ chí minh", "ho chi minh", "tp.hcm", "tp hcm", "sài gòn", "saigon", "hcm")),
            PhraseRule("Đà Nẵng", ("đà nẵng", "da nang", "danang")),
        ),
        other_city_phrases=(
            "hải phòng",
            "hai phong",
            "cần thơ",
            "can tho",
            "huế",
            "hue",
            "biên hòa",
            "bien hoa",
        ),
        multi_city="first_phrase",
    )


@dataclass(frozen=True, slots=True)
class SourceExclusion:
    """Tỷ lệ tin không thuộc IT của một nguồn. Mẫu số là mọi tin của nguồn đó."""

    source: str
    excluded: int
    total: int


class RuleClassifier:
    """Một thân hàm của phép 6. Nhánh để trống cho tới Story 1.9."""

    def __init__(self, config: ClassifyConfig) -> None:
        if config.multi_city != "first_phrase":
            raise ValueError(f"Quy tắc nhiều thành phố chưa hỗ trợ: {config.multi_city}")
        self.config = config

    def classify(self, postings: OneOrMany[PostingFacts]) -> OneOrMany[Classification]:
        batch = as_batch(postings)
        if batch is None:
            return self._one(postings)
        return tuple(self._one(item) for item in batch)

    def _one(self, posting: PostingFacts) -> Classification:
        title = posting.title or ""
        role = _first_rule(title, self.config.role_rules)
        category = (posting.source_category or "").casefold()
        non_it_category = category in {item.casefold() for item in self.config.non_it_categories}
        non_it_title = _any_phrase(title, self.config.non_it_phrases)
        if role is None and (non_it_category or non_it_title):
            role = NON_IT
        elif role is None and (posting.source or "").casefold() in {
            item.casefold() for item in self.config.it_only_sources
        }:
            role = OTHER_ROLE
        elif role is None:
            role = NON_IT
        seniority_text = posting.seniority_text or ""
        seniority = _first_rule(seniority_text, self.config.seniority_rules) or _first_rule(
            title, self.config.seniority_rules
        )
        return Classification(
            role=role,
            branch=None,
            seniority=seniority or UNKNOWN,
            city=self._city(posting.location_text or ""),
        )

    def _city(self, location: str) -> str:
        named = _first_rule(location, self.config.city_rules)
        if named is not None:
            return named
        if _any_phrase(location, self.config.other_city_phrases):
            return OTHER_CITY
        return UNKNOWN


def counts_in_aggregate(result: Classification) -> bool:
    """Tin không thuộc IT không vào bảng tổng hợp."""
    return result.role != NON_IT


def exclusion_by_source(rows: Sequence[tuple[str, Classification]]) -> tuple[SourceExclusion, ...]:
    """Tỷ lệ loại theo nguồn. Thứ tự nguồn là A–Z, không phụ thuộc thứ tự đầu vào."""
    totals: dict[str, list[int]] = {}
    for source, result in rows:
        bucket = totals.setdefault(source, [0, 0])
        bucket[1] += 1
        if not counts_in_aggregate(result):
            bucket[0] += 1
    return tuple(
        SourceExclusion(source=source, excluded=totals[source][0], total=totals[source][1])
        for source in sorted(totals)
    )
