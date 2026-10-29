"""
Chuẩn hóa tên kỹ năng (AD-10): nguồn chuẩn là `scraper/taxonomy.json`.
Từ điển hardcode `ALIAS_MAP` chỉ dùng khi không đọc được file đó (kèm WARNING).
"""
import json
import logging
import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

logger = logging.getLogger("skillnexus.normalizer")

TAXONOMY_PATH = Path(__file__).resolve().parent / "taxonomy.json"

UNMATCHED_CATEGORY = "Tool"
TOP_UNMATCHED_LIMIT = 50

# Tiền tố tiếng Việt đứng trước tên kỹ năng ("Lập trình Java", "Kinh nghiệm sử dụng Docker")
_VI_PREFIXES = (
    "lập trình",
    "kinh nghiệm",
    "kiến thức",
    "sử dụng",
    "thành thạo",
    "hiểu biết về",
    "có khả năng",
)
_VI_PREFIX_RE = re.compile(
    r"^(?:(?:" + "|".join(re.escape(unicodedata.normalize("NFC", p)) for p in _VI_PREFIXES) + r")(?:\s+|$))+",
    re.IGNORECASE,
)
_WHITESPACE_RE = re.compile(r"\s+")
_LIST_SEPARATOR_RE = re.compile(r"[,;]")


def _clean(value: Any) -> str:
    """NFC, bỏ khoảng trắng hai đầu, gộp mọi chuỗi khoảng trắng bên trong thành một dấu cách.
    Giá trị không phải chuỗi (None, NaN của dataset...) trả về chuỗi rỗng."""
    if not isinstance(value, str):
        return ""
    return _WHITESPACE_RE.sub(" ", unicodedata.normalize("NFC", value)).strip()


def _key(value: Any) -> str:
    return _clean(value).lower()


def _strip_prefix(cleaned: str) -> str:
    return _VI_PREFIX_RE.sub("", cleaned).strip()


@dataclass(frozen=True)
class NormalizedSkill:
    raw: str
    canonical_name: str
    category: str
    matched: bool


class SkillTaxonomyNormalizer:
    """
    Chuẩn hóa các tên kỹ năng phong phú từ CV và JD về thực thể duy nhất (Canonical Skill).
    Ngăn chặn việc sinh siêu nút hoặc các node rác bị phân mảnh trên đồ thị Neo4j.
    """

    # Từ điển dự phòng (fallback) khi không đọc được taxonomy.json.
    # Nguồn chuẩn là taxonomy.json (đã chứa toàn bộ bí danh này).
    ALIAS_MAP: Dict[str, Tuple[str, str]] = {
        # Languages
        "java": ("Java", "Language"),
        "core java": ("Java", "Language"),
        "java 8": ("Java", "Language"),
        "java 11": ("Java", "Language"),
        "java 17": ("Java", "Language"),
        "java 21": ("Java", "Language"),
        "python": ("Python", "Language"),
        "python3": ("Python", "Language"),
        "python 3": ("Python", "Language"),
        "js": ("JavaScript", "Language"),
        "javascript": ("JavaScript", "Language"),
        "es6": ("JavaScript", "Language"),
        "ts": ("TypeScript", "Language"),
        "typescript": ("TypeScript", "Language"),
        "golang": ("Go", "Language"),
        "go": ("Go", "Language"),
        "csharp": ("C#", "Language"),
        "c#": ("C#", "Language"),
        "c sharp": ("C#", "Language"),
        "php": ("PHP", "Language"),
        "php 8": ("PHP", "Language"),

        # Frameworks
        "react": ("React", "Framework"),
        "reactjs": ("React", "Framework"),
        "react.js": ("React", "Framework"),
        "spring": ("Spring Boot", "Framework"),
        "springboot": ("Spring Boot", "Framework"),
        "spring boot": ("Spring Boot", "Framework"),
        "spring boot rest api": ("Spring Boot", "Framework"),
        "spring framework": ("Spring Boot", "Framework"),
        "nodejs": ("Node.js", "Framework"),
        "node.js": ("Node.js", "Framework"),
        "node": ("Node.js", "Framework"),
        "nextjs": ("Next.js", "Framework"),
        "next.js": ("Next.js", "Framework"),
        "vue": ("Vue.js", "Framework"),
        "vuejs": ("Vue.js", "Framework"),
        "vue.js": ("Vue.js", "Framework"),
        "laravel": ("Laravel", "Framework"),
        ".net": (".NET", "Framework"),
        "dotnet": (".NET", "Framework"),
        ".net core": (".NET", "Framework"),

        # Databases
        "postgres": ("PostgreSQL", "Database"),
        "postgresql": ("PostgreSQL", "Database"),
        "mysql": ("MySQL", "Database"),
        "mariadb": ("MySQL", "Database"),
        "redis": ("Redis", "Database"),
        "redis cache": ("Redis", "Database"),
        "mongodb": ("MongoDB", "Database"),
        "mongo": ("MongoDB", "Database"),

        # Tools & Cloud
        "docker": ("Docker", "Tool"),
        "docker compose": ("Docker", "Tool"),
        "k8s": ("Kubernetes", "Cloud"),
        "kubernetes": ("Kubernetes", "Cloud"),
        "aws": ("AWS", "Cloud"),
        "amazon web services": ("AWS", "Cloud"),
        "azure": ("Azure", "Cloud"),
        "gcp": ("GCP", "Cloud"),
        "google cloud": ("GCP", "Cloud"),
        "git": ("Git", "Tool"),
        "github": ("Git", "Tool"),
        "gitlab": ("Git", "Tool"),
        "kafka": ("Kafka", "Tool"),
        "apache kafka": ("Kafka", "Tool"),
        "rabbitmq": ("RabbitMQ", "Tool"),

        # Core Concepts
        "rest": ("REST API", "CoreConcept"),
        "restful": ("REST API", "CoreConcept"),
        "rest api": ("REST API", "CoreConcept"),
        "restful api": ("REST API", "CoreConcept"),
        "microservices": ("Microservices", "CoreConcept"),
        "microservice": ("Microservices", "CoreConcept"),
        "oop": ("OOP", "CoreConcept"),
        "ci/cd": ("CI/CD", "Methodology"),
        "cicd": ("CI/CD", "Methodology"),
    }

    # Bản đồ đang dùng: khóa = bí danh/tên chuẩn đã làm sạch + viết thường
    _alias_map: Dict[str, Tuple[str, str]] = dict(ALIAS_MAP)
    source: str = "fallback"

    # ------------------------------------------------------------------ loading

    @classmethod
    def use_fallback(cls) -> None:
        """Dùng từ điển hardcode (không log); là trạng thái mặc định khi chưa nạp taxonomy.json."""
        cls._alias_map = dict(cls.ALIAS_MAP)
        cls.source = "fallback"

    @classmethod
    def _fallback(cls, reason: str) -> str:
        cls.use_fallback()
        logger.warning(
            "Không nạp được taxonomy.json (%s); dùng từ điển hardcode %d bí danh",
            reason,
            len(cls.ALIAS_MAP),
        )
        return cls.source

    @classmethod
    def load_from_file(cls, path: Path = TAXONOMY_PATH) -> str:
        """Nạp bản đồ bí danh từ taxonomy.json (mảng {canonical_name, category, aliases}).
        Không bao giờ ném lỗi: file thiếu, JSON hỏng hoặc mảng rỗng -> từ điển hardcode
        kèm đúng một WARNING. Trả về `source` ("file" | "fallback")."""
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            rows = [(r["canonical_name"], r["category"], r.get("aliases")) for r in data]
        except (OSError, ValueError, TypeError, KeyError) as e:
            return cls._fallback(f"{type(e).__name__}: {e}")

        if not rows:
            return cls._fallback("taxonomy.json rỗng")

        new_map: Dict[str, Tuple[str, str]] = {}
        # Tên chuẩn được ưu tiên hơn bí danh khi trùng khóa; thứ tự trong file làm kết quả ổn định
        for canonical_name, category, _aliases in rows:
            k = _key(canonical_name)
            if k:
                new_map.setdefault(k, (canonical_name, category))
        for canonical_name, category, aliases in rows:
            if aliases is None:
                continue
            if not isinstance(aliases, list):
                logger.warning(
                    "taxonomy.json '%s': aliases không phải mảng; chỉ dùng tên chuẩn",
                    canonical_name,
                )
                continue
            for alias in aliases:
                k = _key(alias)
                if k:
                    new_map.setdefault(k, (canonical_name, category))

        differing = sorted(k for k, v in cls.ALIAS_MAP.items() if new_map.get(k) != v)
        if differing:
            logger.warning(
                "taxonomy.json không cho cùng kết quả với %d bí danh của từ điển hardcode: %s",
                len(differing),
                ", ".join(differing[:10]),
            )

        cls._alias_map = new_map
        cls.source = "file"
        logger.info("Đã nạp taxonomy.json: %d kỹ năng, %d khóa tra cứu", len(rows), len(new_map))
        return cls.source

    # ------------------------------------------------------------------ lookup

    @classmethod
    def _lookup(cls, value: Any) -> Optional[Tuple[str, str, bool]]:
        """Tra một token: cả chuỗi, rồi sau khi bỏ tiền tố tiếng Việt.
        Trả về (tên, danh mục, matched), hoặc None nếu token rỗng / chỉ gồm tiền tố.
        Tên chưa khớp là phần còn lại sau khi bỏ tiền tố, danh mục `Tool`."""
        cleaned = _clean(value)
        if not cleaned:
            return None
        hit = cls._alias_map.get(cleaned.lower())
        if hit:
            return (hit[0], hit[1], True)
        stripped = _strip_prefix(cleaned)
        if not stripped:
            return None
        hit = cls._alias_map.get(stripped.lower())
        if hit:
            return (hit[0], hit[1], True)
        return (stripped, UNMATCHED_CATEGORY, False)

    @classmethod
    def alias_keys(cls) -> List[str]:
        """Mọi khóa tra cứu đang dùng (tên chuẩn + bí danh, viết thường) — để quét kỹ năng trong văn bản."""
        return list(cls._alias_map)

    @classmethod
    def normalize(cls, raw_skill_name: str) -> Tuple[str, str]:
        """
        Nhận vào tên kỹ năng thô (ví dụ: 'ReactJS', 'SpringBoot', 'K8s', 'Lập trình Java').
        Trả về Tuple (canonical_name, category).
        Nếu không có trong taxonomy, giữ tên (đã bỏ tiền tố tiếng Việt) và gán danh mục mặc định.
        """
        found = cls._lookup(raw_skill_name)
        if found is None:
            return ("Unknown", UNMATCHED_CATEGORY)
        return (found[0], found[1])

    @classmethod
    def _split_one(cls, raw: Any) -> List[NormalizedSkill]:
        """Một chuỗi thô -> các kỹ năng. Cả chuỗi khớp thì giữ nguyên (`CI/CD`); nếu không,
        tách theo `,` `;`; phần nào vẫn không khớp chỉ tách theo `/` khi có ít nhất một mảnh khớp
        (`java/spring` -> Java, Spring Boot; `TCP/IP` giữ nguyên)."""
        cleaned = _clean(raw)
        if not cleaned:
            return []
        whole = cls._lookup(cleaned)
        if whole is not None and whole[2]:
            return [NormalizedSkill(cleaned, *whole)]

        items: List[NormalizedSkill] = []
        for part in _LIST_SEPARATOR_RE.split(cleaned):
            part = _clean(part)
            if not part:
                continue
            found = cls._lookup(part)
            if found is not None and not found[2] and "/" in part:
                pieces = [(p, cls._lookup(p)) for p in (_clean(x) for x in part.split("/")) if p]
                if any(r is not None and r[2] for _, r in pieces):
                    items.extend(NormalizedSkill(p, *r) for p, r in pieces if r is not None)
                    continue
            if found is not None:
                items.append(NormalizedSkill(part, *found))
        return items

    @classmethod
    def normalize_batch(cls, raws: Iterable[Any]) -> Tuple[List[NormalizedSkill], Dict[str, Any]]:
        """Chuẩn hóa danh sách chuỗi kỹ năng thô (có thể chứa nhiều kỹ năng, tiền tố tiếng Việt).
        Trả về (items, report), report = {total, matched, coverage_pct, top_unmatched}
        với top_unmatched = [{name, count}] (tối đa 50, giảm dần theo tần suất)."""
        items: List[NormalizedSkill] = []
        for raw in raws:
            if isinstance(raw, float) and math.isnan(raw):
                continue
            items.extend(cls._split_one(raw))

        total = len(items)
        matched = sum(1 for it in items if it.matched)
        counts: Counter = Counter()
        display: Dict[str, str] = {}
        for it in items:
            if not it.matched:
                k = it.canonical_name.lower()
                display.setdefault(k, it.canonical_name)
                counts[k] += 1
        top = sorted(
            ({"name": display[k], "count": c} for k, c in counts.items()),
            key=lambda e: (-e["count"], e["name"]),
        )[:TOP_UNMATCHED_LIMIT]
        report = {
            "total": total,
            "matched": matched,
            "coverage_pct": (matched / total * 100) if total else 0.0,
            "top_unmatched": top,
        }
        return items, report

normalizer = SkillTaxonomyNormalizer()
