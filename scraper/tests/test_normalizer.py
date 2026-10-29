from scraper.normalizer import normalizer

def test_skill_normalization_aliases():
    """Kiểm tra các biến thể viết khác nhau của cùng 1 kỹ năng ánh xạ về tên chuẩn"""
    cases = [
        ("ReactJS", "React", "Framework"),
        ("react.js", "React", "Framework"),
        ("SpringBoot", "Spring Boot", "Framework"),
        ("spring framework", "Spring Boot", "Framework"),
        ("golang", "Go", "Language"),
        ("postgres", "PostgreSQL", "Database"),
        ("k8s", "Kubernetes", "Cloud"),
        ("docker compose", "Docker", "Tool"),
    ]
    for raw, expected_name, expected_category in cases:
        canonical, category = normalizer.normalize(raw)
        assert canonical == expected_name, f"Failed for {raw}: expected {expected_name}, got {canonical}"
        assert category == expected_category, f"Category mismatch for {raw}: expected {expected_category}, got {category}"

def test_skill_normalization_fallback():
    """Kỹ năng mới lạ chưa có trong từ điển giữ nguyên tên và gán danh mục mặc định Tool"""
    canonical, category = normalizer.normalize("SomeObscureLibrary")
    assert canonical == "SomeObscureLibrary"
    assert category == "Tool"


# ---------------------------------------------------------------------------
# Story 7.2 — taxonomy.json, normalize_batch, fallback
# ---------------------------------------------------------------------------
import json
import logging
import unicodedata

import pytest

from scraper.normalizer import TAXONOMY_PATH, SkillTaxonomyNormalizer, NormalizedSkill


@pytest.fixture(autouse=True)
def _restore_fallback_state():
    SkillTaxonomyNormalizer.use_fallback()
    yield
    SkillTaxonomyNormalizer.use_fallback()


def _taxonomy_rows():
    """Mục taxonomy.json giả lập dựng từ ALIAS_MAP + một kỹ năng/bí danh chỉ có trong file."""
    groups = {}
    for alias, (canon, cat) in SkillTaxonomyNormalizer.ALIAS_MAP.items():
        groups.setdefault(canon, (cat, []))[1].append(alias)
    rows = [{"canonical_name": c, "category": cat, "aliases": a} for c, (cat, a) in sorted(groups.items())]
    rows.append({"canonical_name": "Selenium", "category": "Tool", "aliases": ["selenium webdriver"]})
    return rows


def _write(tmp_path, rows):
    path = tmp_path / "taxonomy.json"
    path.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    return path


def _warnings(caplog):
    return [r for r in caplog.records if r.name == "skillnexus.normalizer" and r.levelno == logging.WARNING]


def _names(items):
    return [(it.canonical_name, it.category, it.matched) for it in items]


# --- I/O matrix -----------------------------------------------------------------

def test_batch_alias_hit():
    items, report = normalizer.normalize_batch(["ReactJS"])
    assert _names(items) == [("React", "Framework", True)]
    assert report["total"] == 1 and report["matched"] == 1


def test_batch_slash_inside_known_skill_stays_whole():
    items, _ = normalizer.normalize_batch(["CI/CD"])
    assert _names(items) == [("CI/CD", "Methodology", True)]


def test_batch_multi_skill_string():
    items, _ = normalizer.normalize_batch(["java/spring; Docker"])
    assert _names(items) == [
        ("Java", "Language", True),
        ("Spring Boot", "Framework", True),
        ("Docker", "Tool", True),
    ]


def test_batch_vietnamese_prefix():
    items, _ = normalizer.normalize_batch(["Lập trình Java", "Kinh nghiệm sử dụng Docker"])
    assert _names(items) == [("Java", "Language", True), ("Docker", "Tool", True)]


def test_normalize_follows_prefix_rule():
    assert normalizer.normalize("Lập trình Java") == ("Java", "Language")
    assert normalizer.normalize("THÀNH THẠO   React.js") == ("React", "Framework")
    assert normalizer.normalize("Lập trình Rust") == ("Rust", "Tool")


def test_batch_unknown_skill():
    items, report = normalizer.normalize_batch(["Selenium"])
    assert _names(items) == [("Selenium", "Tool", False)]
    assert report["top_unmatched"] == [{"name": "Selenium", "count": 1}]


def test_batch_prefixed_unknown_uses_stripped_name():
    items, report = normalizer.normalize_batch(["Lập trình Rust", "Rust"])
    assert _names(items) == [("Rust", "Tool", False), ("Rust", "Tool", False)]
    assert report["top_unmatched"] == [{"name": "Rust", "count": 2}]


def test_batch_prefix_only_token_yields_nothing():
    items, report = normalizer.normalize_batch(["Lập trình", "Kinh nghiệm, Java"])
    assert _names(items) == [("Java", "Language", True)]
    assert report["total"] == 1


@pytest.mark.parametrize("raw", ["TCP/IP", "UI/UX", "PL/SQL"])
def test_batch_unknown_slash_skill_kept_whole(raw):
    items, _ = normalizer.normalize_batch([raw])
    assert _names(items) == [(raw, "Tool", False)]


def test_batch_comma_list_of_unknowns_gives_two_items():
    items, report = normalizer.normalize_batch(["Selenium, Jira"])
    assert _names(items) == [("Selenium", "Tool", False), ("Jira", "Tool", False)]
    assert report["matched"] == 0 and report["total"] == 2


@pytest.mark.parametrize("raw", ["", "   ", " , ; ", ";;", "\t\n"])
def test_batch_empty_or_separators_only(raw):
    items, report = normalizer.normalize_batch([raw])
    assert items == []
    assert report == {"total": 0, "matched": 0, "coverage_pct": 0.0, "top_unmatched": []}


def test_batch_ignores_non_string_inputs():
    items, report = normalizer.normalize_batch([None, float("nan"), 42, ["Java"], "Go"])
    assert _names(items) == [("Go", "Language", True)]
    assert report["total"] == 1


def test_cleaning_collapses_internal_whitespace_and_applies_nfc():
    nfd = unicodedata.normalize("NFD", "Lập trình\t\n  Java")
    assert normalizer.normalize(nfd) == ("Java", "Language")
    assert normalizer.normalize("  spring \t  boot ") == ("Spring Boot", "Framework")
    assert normalizer.normalize("Apache   Airflow") == ("Apache Airflow", "Tool")


def test_normalize_non_string_and_empty():
    assert normalizer.normalize("") == ("Unknown", "Tool")
    assert normalizer.normalize(None) == ("Unknown", "Tool")


def test_items_carry_raw_token():
    items, _ = normalizer.normalize_batch(["java/spring"])
    assert items[0] == NormalizedSkill(raw="java", canonical_name="Java", category="Language", matched=True)


# --- report ---------------------------------------------------------------------

def test_report_numbers_and_ordering():
    raws = ["Java", "Selenium", "selenium", "Jira", "Selenium", "Jira", "Ansible", "Docker; Ansible", "Zeplin"]
    items, report = normalizer.normalize_batch(raws)
    assert report["total"] == len(items) == 10
    assert report["matched"] == 2
    assert report["coverage_pct"] == report["matched"] / report["total"] * 100
    assert report["top_unmatched"] == [
        {"name": "Selenium", "count": 3},
        {"name": "Ansible", "count": 2},
        {"name": "Jira", "count": 2},
        {"name": "Zeplin", "count": 1},
    ]


def test_report_top_unmatched_capped_at_50():
    raws = [f"UnknownLib{i:03d}" for i in range(80)] + ["UnknownLib079"] * 3
    _, report = normalizer.normalize_batch(raws)
    top = report["top_unmatched"]
    assert len(top) == 50
    assert top[0] == {"name": "UnknownLib079", "count": 4}
    counts = [e["count"] for e in top]
    assert counts == sorted(counts, reverse=True)


def test_existing_73_aliases_unchanged_in_fallback():
    assert len(SkillTaxonomyNormalizer.ALIAS_MAP) == 73
    for alias, expected in SkillTaxonomyNormalizer.ALIAS_MAP.items():
        assert normalizer.normalize(alias) == expected
        assert normalizer.normalize(alias.upper()) == expected


# --- loading / fallback ---------------------------------------------------------

def test_load_from_file_builds_map_from_rows(tmp_path, caplog):
    caplog.set_level(logging.INFO, logger="skillnexus.normalizer")
    assert normalizer.load_from_file(_write(tmp_path, _taxonomy_rows())) == "file"
    assert SkillTaxonomyNormalizer.source == "file"
    for alias, expected in SkillTaxonomyNormalizer.ALIAS_MAP.items():
        assert normalizer.normalize(alias) == expected
    assert normalizer.normalize("Selenium WebDriver") == ("Selenium", "Tool")
    assert _warnings(caplog) == []


def test_load_from_file_falls_back_when_missing(tmp_path, caplog):
    assert normalizer.load_from_file(tmp_path / "missing.json") == "fallback"
    assert SkillTaxonomyNormalizer.source == "fallback"
    assert len(_warnings(caplog)) == 1
    assert normalizer.normalize("ReactJS") == ("React", "Framework")


def test_load_from_file_falls_back_on_bad_json(tmp_path, caplog):
    path = tmp_path / "taxonomy.json"
    path.write_text("[{", encoding="utf-8")
    assert normalizer.load_from_file(path) == "fallback"
    assert len(_warnings(caplog)) == 1


def test_load_from_file_zero_rows_falls_back(tmp_path, caplog):
    assert normalizer.load_from_file(_write(tmp_path, [])) == "fallback"
    assert SkillTaxonomyNormalizer.source == "fallback"
    assert len(_warnings(caplog)) == 1


def test_load_from_file_non_array_aliases_uses_canonical_only(tmp_path, caplog):
    rows = _taxonomy_rows() + [{"canonical_name": "Jira", "category": "Tool", "aliases": {"oops": "object"}}]
    assert normalizer.load_from_file(_write(tmp_path, rows)) == "file"
    assert normalizer.normalize("jira") == ("Jira", "Tool")
    assert normalizer.normalize("oops") == ("oops", "Tool")
    assert len(_warnings(caplog)) == 1


def test_load_from_file_warns_when_alias_resolves_differently(tmp_path, caplog):
    rows = [r for r in _taxonomy_rows() if r["canonical_name"] != "OOP"]
    assert normalizer.load_from_file(_write(tmp_path, rows)) == "file"
    warnings = _warnings(caplog)
    assert len(warnings) == 1 and "oop" in warnings[0].getMessage()


def test_shipped_taxonomy_covers_fallback(caplog):
    """taxonomy.json trong repo = trạng thái Postgres lúc cào ảnh 2026-10-21 (31 kỹ năng, 92 khóa)."""
    assert normalizer.load_from_file(TAXONOMY_PATH) == "file"
    assert len(json.loads(TAXONOMY_PATH.read_text(encoding="utf-8"))) == 31
    assert len(normalizer.alias_keys()) == 92
    assert _warnings(caplog) == []
