"""#283 — phép 1 `map_mentions`: lượt nhắc → mã kỹ năng qua từ vựng song ngữ."""

import json
from importlib.resources import files

from haido_core.domain.mapping import VocabularyMapper
from haido_core.domain.posting_text import fold
from haido_core.domain.registry import MappedMention, Mention
from haido_core.vocab.skills import load_seed_skills, load_vocabulary

MAPPER = VocabularyMapper(load_vocabulary())

# 100 mã của seed-2026-11-11: hồ sơ người dùng đã lưu các mã này, không được mất.
OLD_CODES = (
    "agile", "android", "angular", "api_testing", "automation_testing", "autosar", "aws", "azure",
    "business_analysis", "business_intelligence", "c", "ci_cd", "communication", "computer_vision", "cpp",
    "csharp", "css", "cybersecurity", "data_analysis", "data_governance", "data_modeling", "data_warehouse",
    "databricks", "deep_learning", "devsecops", "docker", "dotnet", "english", "etl", "excel", "fastapi",
    "firmware", "gcp", "generative_ai", "git", "gitlab_ci", "golang", "html", "ios", "iot", "japanese", "java",
    "javascript", "jenkins", "jira", "kafka", "kotlin", "kubernetes", "laravel", "linux", "llm",
    "machine_learning", "manual_testing", "microservices", "mlops", "mongodb", "mysql", "nestjs",
    "network_security", "networking", "nextjs", "nlp", "nodejs", "nosql", "oracle_db", "owasp",
    "penetration_testing", "php", "playwright", "postgresql", "postman", "power_bi", "powershell", "python",
    "pytorch", "react", "react_native", "redis", "rest_api", "ruby", "ruby_on_rails", "sap", "scrum",
    "selenium", "siem", "software_architecture", "software_testing", "spring", "spring_boot", "sql",
    "sql_server", "swift", "tableau", "tensorflow", "terraform", "typescript", "unit_testing", "vmware", "vue",
    "windows_server",
)


def _m(text: str) -> Mention:
    return Mention(text, 0, len(text))


def test_gh283_mot_luot_va_mot_lo() -> None:
    assert MAPPER.map_mentions(_m("python")) == MappedMention("python", "python")
    batch = MAPPER.map_mentions([_m("reactjs"), _m("kiem thu tu dong")])
    assert batch == (MappedMention("reactjs", "react"), MappedMention("kiem thu tu dong", "automation_testing"))
    assert MAPPER.map_mentions(()) == ()


def test_gh283_bi_danh_anh_viet_co_dau_khong_dau_ve_mot_ma() -> None:
    for term in ("Học máy", "hoc may", "Machine Learning"):
        assert MAPPER.map_mentions(_m(fold(term))).skill_id == "machine_learning", term


def test_gh283_chuoi_la_khong_doan_ma() -> None:
    assert MAPPER.map_mentions(_m("ky nang bay")).skill_id is None


def test_gh283_100_ma_cu_van_con() -> None:
    codes = {s.code for s in load_seed_skills()}
    assert set(OLD_CODES) <= codes
    assert len(OLD_CODES) == 100


def test_gh283_tu_vung_lon_hon_va_co_phien_ban_moi() -> None:
    skills = load_seed_skills()
    assert len(skills) >= 200
    doc = json.loads(files("haido_core.vocab").joinpath("skills_seed.json").read_text(encoding="utf-8"))
    assert doc["version"] != "seed-2026-11-11"


def test_gh283_khong_co_bi_danh_mo_ho_khi_bo_dau() -> None:
    terms = {fold(t) for s in load_seed_skills() for t in (s.name_en, s.name_vi, *s.aliases)}
    vocab = load_vocabulary()
    scanned = set(vocab.scan_terms)
    for bad in ("sap", "lan", "san", "pic", "soc", "solid", "less", "word", "c", "r", "go"):
        assert bad not in scanned, bad
    assert "sap erp" in terms or "sap fico" in terms


def test_gh283_bi_danh_da_bo_dau_khong_tro_toi_hai_ma() -> None:
    owner: dict[str, str] = {}
    for skill in load_seed_skills():
        for term in (skill.name_en, skill.name_vi, *skill.aliases):
            key = fold(term)
            assert owner.setdefault(key, skill.code) == skill.code, f"{term!r}: {owner[key]} và {skill.code}"
