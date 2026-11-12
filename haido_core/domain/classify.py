"""Phép 6: gán vai trò, chức danh con, cấp bậc, thành phố bằng luật (Story 1.20, AD-2; #283).

Luật đọc chức danh, nguồn, danh mục nguồn, chữ cấp bậc, chữ địa điểm, và từ #283 thêm văn bản JD (chỉ trong
bộ nhớ), mã kỹ năng đã ánh xạ và số năm tối thiểu. Không gọi mô hình. Cùng đầu vào và cùng cấu hình thì cùng nhãn.
Danh sách cụm và ngưỡng nằm trong `ClassifyConfig` (đọc từ `config/classify.toml`), không viết trong nhánh if.

Thứ tự vai trò: cụm vai trò cụ thể khớp sớm nhất trong chức danh thắng; không có thì cụm chung (Other); cụm việc không
thuộc IT thắng trừ khi vai trò cụ thể đứng trước nó. Chức danh chung hoặc trống dựa vào bằng chứng kỹ năng.
Tin không có văn bản (dữ kiện cũ) đi đúng đường của luật v1: chức danh, nguồn, chữ cấp.
"""

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

from haido_core.domain.posting_text import fold
from haido_core.domain.registry import Classification, OneOrMany, PostingFacts, as_batch

NON_IT = "không thuộc IT"
UNKNOWN = "không xác định"
OTHER_CITY = "Khác"
"""Nhãn "Khác" của luật cũ; từ #285 không còn được gán (mọi nơi biết được có tỉnh riêng)."""
REMOTE_CITY = "Remote"
ABROAD_CITY = "Nước ngoài"
OTHER_ROLE = "Other"
FULLSTACK = "Fullstack"
FRONTEND = "Frontend"
BACKEND = "Backend"
BA_ROLE = "BA/PO/PM"
QA_ROLE = "QA/Tester"
INTERN = "Intern"
LEAD = "Lead"


@dataclass(frozen=True, slots=True)
class PhraseRule:
    """Cụm khớp trước thì thắng. Cụm so khớp trên chữ đã bỏ dấu, theo biên chữ/số."""

    label: str
    phrases: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class BranchRule:
    """Chức danh con của một vai trò."""

    role: str
    label: str
    phrases: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SkillHint:
    """Mã kỹ năng gợi ý vai trò nào, nặng bao nhiêu."""

    role: str
    weight: float


@dataclass(frozen=True, slots=True)
class EvidenceRules:
    min_tech_skills_without_title: int = 4
    min_tech_skills_generic_title: int = 2
    min_tech_skills_override_non_it: int = 5
    min_score: float = 4.0
    win_ratio: float = 1.3
    fullstack_min_each: float = 6.0
    fullstack_balance: float = 0.5
    max_mentions_per_skill: int = 3


@dataclass(frozen=True, slots=True)
class SectionRules:
    """Tiêu đề mục của JD: `skip` ngừng giữ, `keep` giữ lại; `masks` che cụm trước khi quét."""

    max_heading_chars: int
    skip: re.Pattern[str]
    keep: re.Pattern[str]
    masks: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True, slots=True)
class YearsRules:
    """Số năm từ mục yêu cầu: ngữ cảnh kinh nghiệm quanh con số, chữ loại, câu "không yêu cầu"."""

    window_chars: int
    max_years: float
    context: re.Pattern[str]
    reject: re.Pattern[str]
    zero: re.Pattern[str]


@dataclass(frozen=True, slots=True)
class YearsToLevel:
    """Một dòng của bảng #134: số năm nhỏ hơn `below` thì ra `label`. Dòng cuối `below = None`."""

    below: float | None
    label: str


_NEVER = re.compile(r"(?!x)x")


@dataclass(frozen=True, slots=True)
class AddressRules:
    """Dòng địa chỉ của JD (#285): dòng có `keys`, đọc `window_chars` ký tự từ chỗ khớp, cộng `next_lines` dòng kế."""

    keys: re.Pattern[str]
    window_chars: int = 160
    next_lines: int = 1


@dataclass(frozen=True, slots=True)
class ClassifyConfig:
    """Bảng luật có phiên bản. Đổi luật là đổi file cấu hình, không đổi hàm."""

    version: str
    role_rules: tuple[PhraseRule, ...]
    non_it_phrases: tuple[str, ...]
    non_it_categories: tuple[str, ...]
    it_only_sources: tuple[str, ...]
    seniority_rules: tuple[PhraseRule, ...]
    city_rules: tuple[PhraseRule, ...]
    other_city_phrases: tuple[str, ...] = ()
    multi_city: str = "first_phrase"
    abroad_phrases: tuple[str, ...] = ()
    abroad_location_phrases: tuple[str, ...] = ()
    remote_phrases: tuple[str, ...] = ()
    address: AddressRules = AddressRules(_NEVER)
    art_phrases: tuple[str, ...] = ()
    art_exceptions: tuple[str, ...] = ()
    qa_hardware_phrases: tuple[str, ...] = ()
    qa_software_phrases: tuple[str, ...] = ()
    qa_software_skills: frozenset[str] = frozenset()
    qa_min_tech_skills: int = 3
    generic_it_titles: tuple[str, ...] = ()
    """Chức danh lãnh đạo/kiến trúc IT (CTO, Solution Architect): luôn là Other, không cần bằng chứng kỹ năng."""
    branch_rules: tuple[BranchRule, ...] = ()
    role_manager_phrases: tuple[str, ...] = ()
    role_manager_keep: tuple[str, ...] = ()
    ignore_source_levels: tuple[str, ...] = ()
    years_to_level: tuple[YearsToLevel, ...] = ()
    skill_hints: Mapping[str, SkillHint] = field(default_factory=dict)
    non_technical_skills: frozenset[str] = frozenset()
    evidence: EvidenceRules = EvidenceRules()
    report_as: Mapping[str, str] = field(default_factory=dict)
    max_text_chars: int = 50000
    sections: SectionRules = SectionRules(70, _NEVER, _NEVER)
    years: YearsRules = YearsRules(70, 15, _NEVER, _NEVER, _NEVER)

    def __hash__(self) -> int:  # dict không băm được; phiên bản là danh tính của bảng luật
        return hash(self.version)


def _phrase_at(text: str, phrase: str) -> int | None:
    """Vị trí cụm trong chữ đã bỏ dấu, hoặc None.

    Cụm có khoảng trắng đầu/cuối được so nguyên văn trên " text "; cụm khác thì hai đầu không được là chữ hoặc số.
    """
    if not phrase:
        return None
    if phrase != phrase.strip():
        found = f" {text} ".find(phrase)
        return None if found < 0 else max(found - 1, 0)
    start = 0
    while True:
        found = text.find(phrase, start)
        if found < 0:
            return None
        before = found == 0 or not text[found - 1].isalnum()
        end = found + len(phrase)
        after = end == len(text) or not text[end].isalnum()
        if before and after:
            return found
        start = found + 1


def _first_rule(text: str, rules: Sequence[PhraseRule]) -> tuple[str, int] | None:
    winner: tuple[int, int, str] | None = None
    for order, rule in enumerate(rules):
        for phrase in rule.phrases:
            at = _phrase_at(text, phrase)
            if at is None:
                continue
            candidate = (at, order, rule.label)
            if winner is None or candidate < winner:
                winner = candidate
    return None if winner is None else (winner[2], winner[0])


def _first_at(text: str, phrases: Sequence[str]) -> int | None:
    hits = [at for at in (_phrase_at(text, p) for p in phrases) if at is not None]
    return min(hits) if hits else None


def default_classify_config() -> ClassifyConfig:
    """Luật đang dùng: `config/classify.toml`, đã kiểm (ném `ConfigError` nếu file sai)."""
    from haido_core.config import load_classify_config

    return load_classify_config()


@dataclass(frozen=True, slots=True)
class SourceExclusion:
    """Tỷ lệ tin không thuộc IT của một nguồn. Mẫu số là mọi tin của nguồn đó."""

    source: str
    excluded: int
    total: int


_BA_ABBREVIATION = re.compile(r"(?<![A-Za-z])BA(?![A-Za-z])")


class RuleClassifier:
    """Một thân hàm của phép 6."""

    def __init__(self, config: ClassifyConfig) -> None:
        if config.multi_city != "first_phrase":
            raise ValueError(f"Quy tắc nhiều thành phố chưa hỗ trợ: {config.multi_city}")
        self.config = config
        self._specific = tuple(r for r in config.role_rules if r.label != OTHER_ROLE)
        self._generic = tuple(r for r in config.role_rules if r.label == OTHER_ROLE)
        self._strong = frozenset(r.label for r in self._specific) - {BA_ROLE}

    def classify(self, postings: OneOrMany[PostingFacts]) -> OneOrMany[Classification]:
        batch = as_batch(postings)
        if batch is None:
            return self._one(postings)  # type: ignore[arg-type]
        return tuple(self._one(item) for item in batch)

    # ----------------------------------------------------------------- vai trò
    def _title_role(self, title: str) -> tuple[str | None, int]:
        specific = _first_rule(title, self._specific)
        if specific is not None:
            return specific
        generic = _first_rule(title, self._generic)
        return generic if generic is not None else (None, -1)

    def _tech_breadth(self, skills: Mapping[str, int]) -> int:
        return sum(1 for code in skills if code not in self.config.non_technical_skills)

    def _evidence_role(self, skills: Mapping[str, int]) -> str:
        cfg, rules = self.config, self.config.evidence
        scores: dict[str, float] = {}
        for code, count in skills.items():
            hint = cfg.skill_hints.get(code)
            if hint is None or code in cfg.non_technical_skills:
                continue
            scores[hint.role] = scores.get(hint.role, 0.0) + hint.weight * min(count, rules.max_mentions_per_skill)
        if not scores:
            return OTHER_ROLE
        fe, be = scores.get(FRONTEND, 0.0), scores.get(BACKEND, 0.0)
        if fe >= rules.fullstack_min_each and be >= rules.fullstack_min_each and min(fe, be) / max(fe, be) >= rules.fullstack_balance:
            return FULLSTACK
        ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
        top_role, top = ranked[0]
        second = ranked[1][1] if len(ranked) > 1 else 0.0
        if top >= rules.min_score and top >= rules.win_ratio * second:
            return top_role
        return OTHER_ROLE

    def _role(self, posting: PostingFacts, skills: Mapping[str, int]) -> str:
        cfg, rules = self.config, self.config.evidence
        raw_title = posting.title or ""
        title = fold(raw_title)
        has_text = bool(posting.text)
        breadth = self._tech_breadth(skills)
        role, at = self._title_role(title)
        if role in (None, OTHER_ROLE):
            ba = _BA_ABBREVIATION.search(raw_title)
            if ba is not None:
                role, at = BA_ROLE, ba.start()
        art_at = _first_at(title, cfg.art_phrases)
        if art_at is not None and _first_at(title, cfg.art_exceptions) is None:
            return NON_IT
        non_it_at = _first_at(title, cfg.non_it_phrases)
        if non_it_at is not None:
            if role in self._strong and at < non_it_at:
                pass  # "DevOps Engineer - Ngân hàng": vai trò đứng trước
            elif role in (OTHER_ROLE, BA_ROLE) and breadth >= rules.min_tech_skills_override_non_it:
                pass  # "Phát triển hệ thống quản trị tài chính - K.CNTT" với mục yêu cầu đầy kỹ năng
            else:
                return NON_IT
        if role is None:
            category = (posting.source_category or "").casefold()
            if category in {c.casefold() for c in cfg.non_it_categories}:
                return NON_IT
            if has_text and breadth >= rules.min_tech_skills_without_title:
                return self._evidence_role(skills)
            if (posting.source or "").casefold() in {s.casefold() for s in cfg.it_only_sources}:
                return OTHER_ROLE
            return NON_IT
        if role == OTHER_ROLE:
            if not has_text or _first_at(title, cfg.generic_it_titles) is not None:
                return OTHER_ROLE
            if breadth < rules.min_tech_skills_generic_title:
                return NON_IT
            return self._evidence_role(skills)
        if role == QA_ROLE and has_text and self._hardware_qa(title, skills, breadth):
            return NON_IT
        return role

    def _hardware_qa(self, title: str, skills: Mapping[str, int], breadth: int) -> bool:
        cfg = self.config
        return (
            _first_at(title, cfg.qa_hardware_phrases) is not None
            and _first_at(title, cfg.qa_software_phrases) is None
            and not (set(skills) & cfg.qa_software_skills)
            and breadth < cfg.qa_min_tech_skills
        )

    def _branch(self, role: str, title: str) -> str | None:
        rules = tuple(PhraseRule(b.label, b.phrases) for b in self.config.branch_rules if b.role == role)
        found = _first_rule(title, rules)
        return None if found is None else found[0]

    # ----------------------------------------------------------------- cấp
    def _level(self, posting: PostingFacts) -> str:
        cfg = self.config
        source_text = fold(posting.seniority_text)
        if source_text and source_text not in cfg.ignore_source_levels:
            found = _first_rule(source_text, cfg.seniority_rules)
            if found is not None:
                return found[0]
        title = fold(posting.title)
        found = _first_rule(title, cfg.seniority_rules)
        if found is not None and not (found[0] == LEAD and self._manager_is_role(title)):
            return found[0]
        if found is not None:
            rest = tuple(r for r in cfg.seniority_rules if r.label != LEAD)
            other = _first_rule(title, rest)
            if other is not None:
                return other[0]
        if posting.years_min is not None:
            for row in cfg.years_to_level:
                if row.below is None or posting.years_min < row.below:
                    return row.label
        return UNKNOWN

    def _manager_is_role(self, title: str) -> bool:
        cfg = self.config
        return _first_at(title, cfg.role_manager_phrases) is not None and _first_at(title, cfg.role_manager_keep) is None

    # ----------------------------------------------------------------- một tin
    def _one(self, posting: PostingFacts) -> Classification:
        skills = dict(posting.skills)
        role = self._role(posting, skills)
        branch = self._branch(role, fold(posting.title)) if role not in (NON_IT, OTHER_ROLE) else None
        return Classification(role=role, branch=branch, seniority=self._level(posting), city=self._city(posting))

    def _city(self, posting: PostingFacts) -> str:
        """Tỉnh ở location → nước ngoài ở location → tỉnh ở dòng địa chỉ → nước ngoài ở dòng địa chỉ → remote (#285)."""
        cfg = self.config
        location = fold(posting.location_text)
        address = posting.address_text or ""
        named = _first_rule(location, cfg.city_rules)
        if named is not None:
            return named[0]
        if _first_at(location, (*cfg.abroad_phrases, *cfg.abroad_location_phrases)) is not None:
            return ABROAD_CITY
        named = _first_rule(address, cfg.city_rules)
        if named is not None:
            return named[0]
        if _first_at(address, cfg.abroad_phrases) is not None:
            return ABROAD_CITY
        if _first_at(location, cfg.remote_phrases) is not None or _first_at(address, cfg.remote_phrases) is not None:
            return REMOTE_CITY
        if _first_at(location, cfg.other_city_phrases) is not None:
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
