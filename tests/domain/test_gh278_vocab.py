"""#278 — mã kỹ năng cho các thẻ hay gặp: mỗi thẻ có mã hoặc nằm trong danh sách loại trừ có lý do (AC1), cách viết
Anh/Việt cùng một mã (AC2), từ vựng đổi phiên bản (AC4) và ánh xạ không cần mạng (AC4, #97).

Nguồn thẻ: `gaps-2026-11-20.json` (kết quả `tools/vocab/skill_gaps.py` trên prod); quyết định đã duyệt:
`quyet-dinh-2026-11-20.json`. Cả hai nằm trong `specs/278-ma-ky-nang-thuong-gap/`.
"""

import json
import socket
from importlib.resources import files
from pathlib import Path

import pytest

from haido_core.domain.mapping import VocabularyMapper
from haido_core.domain.posting_text import find_mentions, fold
from haido_core.domain.registry import Mention
from haido_core.vocab import skills as skills_module
from haido_core.vocab.skills import (
    ExclusionList,
    load_exclusions,
    load_seed_skills,
    load_vocabulary,
    parse_exclusions,
    seed_version,
)

SPEC = Path(__file__).resolve().parents[2] / "specs" / "278-ma-ky-nang-thuong-gap"
PREVIOUS_VERSION = "seed-2026-11-13"
MIN_POSTINGS = 20

# 225 mã của `seed-2026-11-13`: hồ sơ người dùng đã lưu các mã này, không được mất.
OLD_CODES = (
    "ab_testing", "abap", "agile", "ai_agent", "ai_tools", "airflow", "android", "angular", "ansible",
    "api_testing", "appium", "argocd", "automation_testing", "autosar", "aws", "azure", "ba_docs", "backup",
    "bash", "bigquery", "blender_3d", "bootstrap", "bpmn_uml", "business_analysis", "business_intelligence",
    "c", "caching", "cassandra", "chinese", "ci_cd", "cisco", "clean_architecture", "clickhouse", "cocos",
    "communication", "computer_vision", "cpp", "csharp", "css", "cybersecurity", "cypress", "dart",
    "data_analysis", "data_governance", "data_modeling", "data_warehouse", "databricks", "dbt",
    "deep_learning", "design_patterns", "devsecops", "django", "docker", "dotnet", "dsa", "edr",
    "elasticsearch", "elk", "embedded", "english", "entity_framework", "erp", "etl", "excel", "express",
    "fastapi", "feature_engineering", "figma", "fine_tuning", "firebase", "firewall", "firmware", "flask",
    "flink", "flutter", "fpga", "game_design", "gcp", "generative_ai", "git", "github_actions", "gitlab_ci",
    "golang", "graphql", "grpc", "hadoop", "helm", "helpdesk", "hibernate", "html", "huggingface", "iam",
    "incident_response", "ios", "iot", "iso27001", "istqb", "itil", "japanese", "java", "javascript",
    "jenkins", "jest", "jira", "jmeter", "jquery", "kafka", "korean", "kotlin", "kubernetes", "langchain",
    "laravel", "leadership", "linux", "llm", "looker", "lua", "machine_learning", "manual_testing",
    "matlab", "mcu", "message_queue", "microservices", "mlops", "mongodb", "ms_office", "mvvm", "mysql",
    "negotiation", "nestjs", "network_security", "networking", "nextjs", "nginx", "nlp", "nodejs", "nosql",
    "oauth", "objective_c", "observability", "odoo", "oop", "oracle_db", "owasp", "pandas",
    "penetration_testing", "photoshop", "php", "playwright", "plc", "postgresql", "postman", "power_bi",
    "powershell", "problem_solving", "product_management", "project_management", "prometheus",
    "prompt_engineering", "protocols_hw", "python", "pytorch", "query_optimization", "r", "rabbitmq", "rag",
    "react", "react_native", "redis", "redux", "regression", "responsive", "rest_api", "rtos", "ruby",
    "ruby_on_rails", "rust", "sap", "scala", "scikit_learn", "scrum", "sec_certs", "selenium",
    "self_learning", "siem", "snowflake", "software_architecture", "software_testing", "solid", "solidity",
    "spark", "spring", "spring_boot", "sql", "sql_server", "sre", "statistics", "swift", "symfony",
    "system_design", "tableau", "tailwind", "teamwork", "tensorflow", "terraform", "test_design",
    "time_management", "typescript", "uat", "ui_design", "unit_testing", "unity", "unreal", "ux_research",
    "vba", "vector_db", "virtualization", "vmware", "vue", "waf_ips", "waterfall", "webpack", "websocket",
    "windows_server", "zabbix"
)


def _json(name: str) -> dict:
    return json.loads((SPEC / name).read_text(encoding="utf-8"))


GAPS = _json("gaps-2026-11-20.json")
DECISION = _json("quyet-dinh-2026-11-20.json")


def _m(text: str) -> Mention:
    return Mention(text, 0, len(text))


# --- AC1 ---------------------------------------------------------------------------------------------------------


def test_gh278_ac1_moi_the_tu_20_tin_co_ma_hoac_nam_trong_danh_sach_loai_tru() -> None:
    vocab = load_vocabulary()
    excluded = {e.key: e for e in load_exclusions().entries}
    keys = [s["key"] for s in GAPS["skills"] if s["postings"] >= MIN_POSTINGS]
    assert len(keys) == 673
    unresolved = []
    for key in keys:
        if key in vocab.lookup or key in vocab.composites:
            continue
        entry = excluded.get(key)
        if entry is None or not entry.reason.strip():
            unresolved.append(key)
    assert unresolved == []


def test_gh278_ac1_the_da_loai_tru_co_ly_do_va_so_tin_bang_chung() -> None:
    exclusions = load_exclusions()
    assert exclusions.snapshot == GAPS["meta"]["snapshot"] == "2026-11-20"
    postings = {s["key"]: s["postings"] for s in GAPS["skills"]}
    assert len(exclusions.entries) == 158
    for entry in exclusions.entries:
        assert entry.reason.strip()
        assert entry.postings == postings[entry.key] >= MIN_POSTINGS, entry.key


def test_gh278_ac1_khoa_loai_tru_khong_dong_thoi_la_khoa_tu_vung() -> None:
    vocab = load_vocabulary()
    assert load_exclusions().keys.isdisjoint(set(vocab.lookup) | set(vocab.composites))


def test_gh278_ac1_bo_kiem_chan_khoa_trung_thieu_ly_do_va_khoa_cua_tu_vung() -> None:
    vocab = load_vocabulary()
    good = {"key": "ha noi", "spelling": "Hà Nội", "reason": "địa điểm", "postings": 30}

    def doc(*entries: dict) -> dict:
        return {"version": "excluded-test", "snapshot": "2026-11-20", "entries": list(entries)}

    assert isinstance(parse_exclusions(doc(good), vocab), ExclusionList)
    with pytest.raises(ValueError, match="thiếu lý do"):
        parse_exclusions(doc({**good, "reason": "  "}), vocab)
    with pytest.raises(ValueError, match="thiếu lý do"):
        parse_exclusions(doc({k: v for k, v in good.items() if k != "reason"}), vocab)
    with pytest.raises(ValueError, match="khóa trùng"):
        parse_exclusions(doc(good, good), vocab)
    with pytest.raises(ValueError, match="vừa bị loại trừ vừa có trong từ vựng"):
        parse_exclusions(doc({**good, "key": "python"}), vocab)
    with pytest.raises(ValueError, match="đã bỏ dấu"):
        parse_exclusions(doc({**good, "key": "Hà Nội"}), vocab)
    with pytest.raises(ValueError, match="số tin"):
        parse_exclusions(doc({**good, "postings": 0}), vocab)
    with pytest.raises(ValueError, match="entries"):
        parse_exclusions({"version": "excluded-test", "snapshot": "2026-11-20", "entries": []}, vocab)


# --- AC2 ---------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("a", "b", "code"),
    [
        ("Cơ sở dữ liệu", "database", "databases"),
        ("Xử lý sự cố", "troubleshooting", "troubleshooting"),
        ("Quản trị hệ thống", "system administration", "system_administration"),
        ("Tích hợp hệ thống", "system integration", "system_integration"),
        ("Kiểm thử tích hợp", "integration testing", "integration_testing"),
        ("Hệ điều hành", "operating systems", "operating_systems"),
        ("Quản lý rủi ro", "risk management", "risk_management"),
        ("Thuyết trình", "presentation", "presentation"),
        ("Quy trình phát triển phần mềm", "SDLC", "sdlc"),
        ("Tư duy phân tích", "analytical skills", "analytical_thinking"),
        ("Tư duy logic", "logical thinking", "analytical_thinking"),
        ("Trí tuệ nhân tạo", "AI", "artificial_intelligence"),
        ("Điện toán đám mây", "cloud", "cloud_computing"),
        ("Khoa học dữ liệu", "data science", "data_science"),
        ("Bảo mật hệ thống", "cybersecurity", "cybersecurity"),
        ("Đọc hiểu tài liệu tiếng Anh", "english", "english"),
        ("CAN", "CAN bus", "can_bus"),
        ("Infrastructure as Code (IaC)", "Hạ tầng dưới dạng mã (IaC)", "infrastructure_as_code"),
        ("SOLID", "solid", "solid"),
    ],
)
def test_gh278_ac2_cach_viet_anh_viet_ve_mot_ma(a: str, b: str, code: str) -> None:
    lookup = load_vocabulary().lookup
    assert lookup[fold(a)] == lookup[fold(b)] == code


def test_gh278_ac2_moi_the_da_duyet_tra_ve_dung_ma_da_duyet() -> None:
    lookup = load_vocabulary().lookup
    composites = load_vocabulary().composites
    wrong = []
    for row in DECISION["rows"]:
        action, target, key = row["action"], row["target"], row["key"]
        if action in ("new", "alias"):
            if lookup.get(key) != target:
                wrong.append((key, lookup.get(key), target))
        elif action == "composite":
            parts = tuple(lookup[p] for p in composites[key])
            if parts != tuple(lookup[fold(p)] for p in target.split("+")):
                wrong.append((key, parts, target))
        else:
            assert key not in lookup
            assert key not in composites
    assert wrong == []


def test_gh278_ac2_mot_ma_khong_bi_tach_thanh_hai_ma() -> None:
    """Mọi khóa mà quyết định đưa vào một mã mới đều tra ra đúng mã đó, cả tên Anh lẫn tên Việt."""
    lookup = load_vocabulary().lookup
    for code, spec in DECISION["new"].items():
        terms = {fold(spec["name_en"]), fold(spec["name_vi"]), *spec["keys"]}
        assert {lookup[t] for t in terms} == {code}, code


def test_gh278_ac2_hai_ma_khong_giu_chung_mot_khoa_sau_khi_bo_dau() -> None:
    owner: dict[str, str] = {}
    for skill in load_seed_skills():
        for term in (skill.name_en, skill.name_vi, *skill.aliases):
            assert owner.setdefault(fold(term), skill.code) == skill.code, term


def test_gh278_ac2_ba_khoa_trung_duoc_chuyen_ve_ma_moi_va_solid_het_dau_phay() -> None:
    by_code = {s.code: s for s in load_seed_skills()}
    assert "tu duy phan tich" not in by_code["problem_solving"].aliases
    assert "tu duy logic" not in by_code["problem_solving"].aliases
    assert "can bus" not in by_code["protocols_hw"].aliases
    assert "infrastructure as code" not in by_code["terraform"].aliases
    assert "solid" in by_code["solid"].aliases
    assert "solid, " not in by_code["solid"].aliases
    assert load_vocabulary().lookup["terraform"] == "terraform"


def test_gh278_ac2_ma_ghep_tach_thanh_hai_ky_nang() -> None:
    vocab = load_vocabulary()
    mapper = VocabularyMapper(vocab)
    mentions = find_mentions("kinh nghiem agile/scrum va html/css, javascript/typescript", vocab)
    ids = [m.skill_id for m in mapper.map_mentions(list(mentions))]
    assert ids == ["agile", "scrum", "html", "css", "javascript", "typescript"]


# --- scan_skip ---------------------------------------------------------------------------------------------------


def test_gh278_scan_skip_khong_nam_trong_tu_duoc_quet_nhung_van_tra_duoc() -> None:
    vocab = load_vocabulary()
    scanned = set(vocab.scan_terms)
    assert len(DECISION["scan_skip"]) == 31
    for term in DECISION["scan_skip"]:
        assert term not in scanned, term
        assert term in vocab.lookup, term
    text = "cloud api database windows monitoring rest router solid security word"
    assert find_mentions(text, vocab) == ()


def test_gh278_the_khong_nam_trong_scan_skip_van_duoc_quet_trong_jd() -> None:
    vocab = load_vocabulary()
    mapper = VocabularyMapper(vocab)
    mentions = find_mentions("kinh nghiem troubleshooting, debugging va code review", vocab)
    assert [m.skill_id for m in mapper.map_mentions(list(mentions))] == ["troubleshooting", "debugging", "code_review"]


# --- phiên bản và mã cũ ------------------------------------------------------------------------------------------


def test_gh278_ac4_them_ma_thi_phien_ban_tu_vung_doi() -> None:
    doc = json.loads(files("haido_core.vocab").joinpath("skills_seed.json").read_text(encoding="utf-8"))
    assert doc["version"] != PREVIOUS_VERSION
    assert seed_version() == load_vocabulary().version == doc["version"]
    assert doc["version"].startswith("seed-")


def test_gh278_225_ma_cu_van_con() -> None:
    codes = {s.code for s in load_seed_skills()}
    assert len(OLD_CODES) == len(set(OLD_CODES)) == 225
    assert set(OLD_CODES) <= codes


def test_gh278_40_ma_moi_co_ten_anh_viet_va_nguon() -> None:
    by_code = {s.code: s for s in load_seed_skills()}
    assert len(DECISION["new"]) == 40
    assert len(by_code) == 225 + 40
    for code in DECISION["new"]:
        skill = by_code[code]
        assert skill.name_en.strip()
        assert skill.name_vi.strip()
        assert skill.source.startswith("gh-278")


# --- AC4: ánh xạ không gọi mô hình, không cần mạng (#97) -------------------------------------------------------


def _no_network(*_args, **_kwargs):
    raise AssertionError("ánh xạ kỹ năng không được mở kết nối mạng")


def _clear_caches() -> None:
    for cached in (load_vocabulary, skills_module._seed, skills_module._by_code):
        cached.cache_clear()


def test_gh278_ac4_anh_xa_chay_khi_chan_mang(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_caches()
    monkeypatch.setattr(socket, "socket", _no_network)
    monkeypatch.setattr(socket, "create_connection", _no_network)
    monkeypatch.setattr(socket, "getaddrinfo", _no_network)
    try:
        vocab = load_vocabulary()
        mapper = VocabularyMapper(vocab)
        keys = sorted(vocab.lookup)
        mapped = mapper.map_mentions([_m(k) for k in keys])
        assert len(mapped) == len(keys) > 1000
        assert all(m.skill_id == vocab.lookup[m.text] for m in mapped)
        text = "yeu cau: python, docker, troubleshooting, code review, agile/scrum, quan tri he thong, co so du lieu"
        found = [m.skill_id for m in mapper.map_mentions(list(find_mentions(text, vocab)))]
        assert found == ["python", "docker", "troubleshooting", "code_review", "agile", "scrum", "system_administration", "databases"]
    finally:
        monkeypatch.undo()
        _clear_caches()


# --- review 2026-11-23: ai/ml, scan_skip mới ----------------------------------------------------------------------


def test_gh278_ma_ghep_ai_ml_neo_tung_phan_trong_cum() -> None:
    vocab = load_vocabulary()
    text = "dung ai/ml cho nlp"
    mentions = find_mentions(text, vocab)
    assert [(m.text, m.start, m.end) for m in mentions] == [("ai", 5, 7), ("ml", 8, 10), ("nlp", 15, 18)]
    ids = [m.skill_id for m in VocabularyMapper(vocab).map_mentions(list(mentions))]
    assert ids == ["artificial_intelligence", "machine_learning", "nlp"]


def test_gh278_moi_phan_cua_ma_ghep_nam_trong_cum_da_bo_dau() -> None:
    vocab = load_vocabulary()
    for term, parts in vocab.composites.items():
        for part in parts:
            assert part in term, (term, part)
        for m in find_mentions(f"x {term} y", vocab):
            assert m.start >= 0 and m.end > m.start, (term, m)


def test_gh278_tai_tu_vung_tu_choi_ma_ghep_co_phan_khong_nam_trong_cum(monkeypatch: pytest.MonkeyPatch) -> None:
    doc = dict(skills_module._load_document())
    doc["composites"] = {"ai/ml": ["artificial intelligence", "machine learning"]}
    monkeypatch.setattr(skills_module, "_load_document", lambda: doc)
    with pytest.raises(ValueError, match="không nằm trong"):
        skills_module.load_vocabulary.__wrapped__()


def test_gh278_chuyen_nganh_khong_sinh_ma_data_science_hay_ai() -> None:
    vocab = load_vocabulary()
    mapper = VocabularyMapper(vocab)
    text = fold("Tốt nghiệp chuyên ngành Khoa học dữ liệu, Trí tuệ nhân tạo, Khoa học máy tính")
    ids = {m.skill_id for m in mapper.map_mentions(list(find_mentions(text, vocab)))}
    assert not ids & {"data_science", "artificial_intelligence"}
    assert vocab.lookup["khoa hoc du lieu"] == "data_science"  # tra thẻ vẫn ra mã
    assert vocab.lookup["tri tue nhan tao"] == "artificial_intelligence"


def test_gh278_cum_chung_chung_trong_jd_khong_sinh_ma_moi() -> None:
    vocab = load_vocabulary()
    mapper = VocabularyMapper(vocab)
    jd = fold("Cam kết bảo mật thông tin khách hàng, có wifi, lập kế hoạch công việc")
    new_terms = {"bao mat", "wifi", "lap ke hoach"}
    assert not {m.text for m in find_mentions(jd, vocab)} & new_terms
    boiler = fold("Bảo mật dữ liệu, wifi, wi-fi, lập kế hoạch, phân quyền, IT infrastructure, IT operations, IT support, presentation")
    assert find_mentions(boiler, vocab) == ()
    for term in ("bao mat", "lap ke hoach", "phan quyen", "wifi", "wi-fi", "it infrastructure", "it operations",
                 "it support", "presentation"):
        assert term in vocab.lookup and term not in vocab.scan_terms, term
    assert mapper.map_mentions([_m("it support")])[0].skill_id == "helpdesk"
