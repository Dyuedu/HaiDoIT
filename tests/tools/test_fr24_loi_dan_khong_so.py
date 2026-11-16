"""Kiểm thử cổng FR-24: lời dẫn không chứa số (cho phép số trong tên công nghệ)."""

import json
from pathlib import Path
import pytest
import tools.gates.check_gates as check_gates


def test_fr24_no_blurbs_with_valid_ledger_skips(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    gates_dir = tmp_path / "tools" / "gates"
    gates_dir.mkdir(parents=True)
    ledger = {
        "FR-24": {
            "issue": "https://github.com/Dyuedu/HaiDoIT/issues/24",
            # Hạn xa: ca này kiểm sổ hoãn còn hạn, không được tự đỏ khi lịch qua 2026-11-22.
            "due": "2099-12-31"
        }
    }
    (gates_dir / "deferred.json").write_text(json.dumps(ledger), encoding="utf-8")

    status, detail, hits = check_gates.gate_fr24_loi_dan_khong_so()
    assert status == check_gates.SKIP
    assert "deferred" in detail.lower() or "2099-12-31" in detail


def test_fr24_no_blurbs_with_expired_ledger_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    gates_dir = tmp_path / "tools" / "gates"
    gates_dir.mkdir(parents=True)
    ledger = {
        "FR-24": {
            "issue": "https://github.com/Dyuedu/HaiDoIT/issues/24",
            "due": "2020-01-01"
        }
    }
    (gates_dir / "deferred.json").write_text(json.dumps(ledger), encoding="utf-8")

    status, detail, hits = check_gates.gate_fr24_loi_dan_khong_so()
    assert status == check_gates.FAIL
    assert any("quá hạn" in d.lower() or "expired" in d.lower() or "past" in d.lower() for d in [detail] + hits)


def test_fr24_no_blurbs_with_invalid_issue_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    gates_dir = tmp_path / "tools" / "gates"
    gates_dir.mkdir(parents=True)
    ledger = {
        "FR-24": {
            "issue": "not-a-url",
            "due": "2026-11-22"
        }
    }
    (gates_dir / "deferred.json").write_text(json.dumps(ledger), encoding="utf-8")

    status, detail, hits = check_gates.gate_fr24_loi_dan_khong_so()
    assert status == check_gates.FAIL


def test_fr24_no_blurbs_missing_ledger_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    status, detail, hits = check_gates.gate_fr24_loi_dan_khong_so()
    assert status == check_gates.FAIL


def test_fr24_clean_blurbs_passes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    blurbs_dir = tmp_path / "haido_core" / "vocab" / "blurbs"
    blurbs_dir.mkdir(parents=True)
    (blurbs_dir / "java.txt").write_text("Java 17, Spring Boot, Vue 3, HTML5, OAuth2, AWS S3 và EC2\n", encoding="utf-8")

    status, _detail, hits = check_gates.gate_fr24_loi_dan_khong_so()
    assert status == check_gates.PASS
    assert hits == []


def test_fr24_numbers_in_blurbs_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    blurbs_dir = tmp_path / "haido_core" / "vocab" / "blurbs"
    blurbs_dir.mkdir(parents=True)
    (blurbs_dir / "bad.txt").write_text("Kỹ năng này xuất hiện trong 50% tin tuyển dụng\n", encoding="utf-8")

    status, _detail, hits = check_gates.gate_fr24_loi_dan_khong_so()
    assert status == check_gates.FAIL
    assert len(hits) == 1
    assert "bad.txt:1" in hits[0]


def _blurb_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, text: str):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)
    blurbs_dir = tmp_path / "haido_core" / "vocab" / "blurbs"
    blurbs_dir.mkdir(parents=True)
    (blurbs_dir / "t.txt").write_text(text + "\n", encoding="utf-8")


@pytest.mark.parametrize(
    "text",
    [
        "Hơn 30 tin cần Python",
        "Top 5 kỹ năng nên học",
        "Cần 3 năm kinh nghiệm",
        "Kỹ năng này có trong năm mươi phần trăm tin",
        "Phần Trăm tin tuyển dụng",
        "Dùng Java 170 để viết",
        "Mức 100%",
    ],
)
def test_fr24_digits_or_percent_outside_tech_names_fail(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, text: str
):
    _blurb_file(tmp_path, monkeypatch, text)
    status, _detail, hits = check_gates.gate_fr24_loi_dan_khong_so()
    assert status == check_gates.FAIL
    assert len(hits) == 1 and "t.txt:1" in hits[0]


@pytest.mark.parametrize("text", ["Học Java 17 trước", "Viết HTML5 và CSS", "Dùng AWS S3, EC2 và OAuth2"])
def test_fr24_digits_inside_tech_names_pass(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, text: str):
    _blurb_file(tmp_path, monkeypatch, text)
    status, _detail, hits = check_gates.gate_fr24_loi_dan_khong_so()
    assert status == check_gates.PASS
    assert hits == []


def _fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, blurb: str, title: str = "Tài liệu Java 17"):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)
    fx = tmp_path / "haido_api" / "fixtures"
    fx.mkdir(parents=True)
    data = {"roles": {"backend": {"skills": [{"skill": "java", "blurb": blurb, "resource": {"title": title}}]}}}
    (fx / "fake_learning_path.json").write_text(json.dumps(data), encoding="utf-8")


def test_fr24_no_directory_scans_fixture_and_passes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _fixture(tmp_path, monkeypatch, "Ngôn ngữ nền của dịch vụ phía sau, học Java 17 trước")
    status, detail, hits = check_gates.gate_fr24_loi_dan_khong_so()
    assert status == check_gates.PASS
    assert hits == []
    assert "fake_learning_path.json" in detail


@pytest.mark.parametrize("field", ["blurb", "title"])
def test_fr24_no_directory_fixture_with_bad_text_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, field: str):
    if field == "blurb":
        _fixture(tmp_path, monkeypatch, "Cần 3 năm kinh nghiệm")
    else:
        _fixture(tmp_path, monkeypatch, "Ổn", title="Top 5 tài liệu")
    status, _detail, hits = check_gates.gate_fr24_loi_dan_khong_so()
    assert status == check_gates.FAIL
    assert len(hits) == 1
    assert "backend.java" in hits[0]


def test_fr24_directory_and_fixture_are_both_scanned(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _fixture(tmp_path, monkeypatch, "Cần 3 năm kinh nghiệm")
    blurbs_dir = tmp_path / "haido_core" / "vocab" / "blurbs"
    blurbs_dir.mkdir(parents=True)
    (blurbs_dir / "ok.txt").write_text("Sạch\n", encoding="utf-8")
    status, _detail, hits = check_gates.gate_fr24_loi_dan_khong_so()
    assert status == check_gates.FAIL
    assert any("backend.java" in h for h in hits)


def test_fr24_real_repo_scans_todays_blurbs_and_passes():
    status, detail, hits = check_gates.gate_fr24_loi_dan_khong_so()
    assert status == check_gates.PASS, hits
    assert "fake_learning_path.json" in detail


def test_fr24_is_no_longer_in_deferred_ledger():
    ledger = json.loads((check_gates.ROOT / "tools" / "gates" / "deferred.json").read_text(encoding="utf-8"))
    assert "FR-24" not in ledger


# --- Đợt 2 (2026-11-16, review #138) ---


def _node(skill: str, blurb="Sạch", title="Tài liệu Java 17", **extra):
    node = {"skill": skill, "requires": [], "foundation": False, "blurb": blurb, "resource": {"title": title, "url": "https://x"}}
    node.update(extra)
    return node


def _write_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, data):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)
    fx = tmp_path / "haido_api" / "fixtures"
    fx.mkdir(parents=True, exist_ok=True)
    (fx / "fake_learning_path.json").write_text(json.dumps(data), encoding="utf-8")


def _blurbs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)
    d = tmp_path / "haido_core" / "vocab" / "blurbs"
    d.mkdir(parents=True)
    return d


@pytest.mark.parametrize("field", ["blurb", "title"])
def test_fr24_bad_text_in_last_skill_of_last_role_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, field: str):
    bad = {"blurb": "Cần 3 năm"} if field == "blurb" else {"title": "Top 5 tài liệu"}
    data = {
        "roles": {
            "backend": {"skills": [_node("java"), _node("sql")]},
            "frontend": {"skills": [_node("html"), _node("css", **bad)]},
        }
    }
    _write_fixture(tmp_path, monkeypatch, data)
    status, detail, hits = check_gates.gate_fr24_loi_dan_khong_so()
    assert status == check_gates.FAIL
    assert len(hits) == 1 and "frontend.css" in hits[0]


def test_fr24_clean_two_roles_two_skills_passes_and_counts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    data = {"roles": {r: {"skills": [_node("a"), _node("b")]} for r in ("backend", "frontend")}}
    _write_fixture(tmp_path, monkeypatch, data)
    status, detail, hits = check_gates.gate_fr24_loi_dan_khong_so()
    assert (status, hits) == (check_gates.PASS, [])
    assert "scanned 8 texts" in detail


@pytest.mark.parametrize(
    "content",
    ["{not json", "[]", '{"roles": []}', '{"roles": {"b": {"skills": 3}}}', '{"roles": {"b": {"skills": [3]}}}'],
)
def test_fr24_malformed_fixture_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, content: str):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)
    fx = tmp_path / "haido_api" / "fixtures"
    fx.mkdir(parents=True)
    (fx / "fake_learning_path.json").write_text(content, encoding="utf-8")
    status, detail, hits = check_gates.gate_fr24_loi_dan_khong_so()
    assert status == check_gates.FAIL
    assert "crashed" not in detail
    assert hits and "fake_learning_path.json" in hits[0]


def test_fr24_non_utf8_fixture_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)
    fx = tmp_path / "haido_api" / "fixtures"
    fx.mkdir(parents=True)
    (fx / "fake_learning_path.json").write_bytes(b'{"roles": {"a": "\xff"}}')
    status, _detail, hits = check_gates.gate_fr24_loi_dan_khong_so()
    assert status == check_gates.FAIL
    assert hits and "fake_learning_path.json" in hits[0]


def test_fr24_non_utf8_blurb_file_fails_naming_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    d = _blurbs(tmp_path, monkeypatch)
    (d / "ok.txt").write_text("Sạch\n", encoding="utf-8")
    (d / "bad.txt").write_bytes("Cần 3 năm\n".encode("utf-16"))
    status, _detail, hits = check_gates.gate_fr24_loi_dan_khong_so()
    assert status == check_gates.FAIL
    assert any("bad.txt" in h and "UTF-8" in h for h in hits)


def test_fr24_empty_blurbs_dir_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _blurbs(tmp_path, monkeypatch)
    status, detail, hits = check_gates.gate_fr24_loi_dan_khong_so()
    assert status == check_gates.FAIL
    assert "scanned 0 texts" in " ".join([detail, *hits])


def test_fr24_fixture_with_zero_skills_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _write_fixture(tmp_path, monkeypatch, {"roles": {"backend": {"skills": []}}})
    status, detail, hits = check_gates.gate_fr24_loi_dan_khong_so()
    assert status == check_gates.FAIL
    assert "scanned 0 texts" in " ".join([detail, *hits])


def test_fr24_fixture_with_no_roles_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _write_fixture(tmp_path, monkeypatch, {"roles": {}})
    status, _detail, _hits = check_gates.gate_fr24_loi_dan_khong_so()
    assert status == check_gates.FAIL


@pytest.mark.parametrize(
    ("data", "key"),
    [
        ({"roles": {"b": {"skills": [_node("java", summary="Có 3 mục")]}}}, "summary"),
        ({"roles": {"b": {"skills": [_node("java")], "intro": "x"}}}, "intro"),
        ({"roles": {"b": {"skills": [_node("java")]}}, "extra": 1}, "extra"),
    ],
)
def test_fr24_unknown_key_fails_naming_key(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, data, key: str):
    _write_fixture(tmp_path, monkeypatch, data)
    status, _detail, hits = check_gates.gate_fr24_loi_dan_khong_so()
    assert status == check_gates.FAIL
    assert any(key in h for h in hits)


def test_fr24_unknown_resource_key_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    node = _node("java")
    node["resource"]["note"] = "Có 3 mục"
    _write_fixture(tmp_path, monkeypatch, {"roles": {"b": {"skills": [node]}}})
    status, _detail, hits = check_gates.gate_fr24_loi_dan_khong_so()
    assert status == check_gates.FAIL
    assert any("note" in h for h in hits)


@pytest.mark.parametrize("field", ["blurb", "title"])
@pytest.mark.parametrize("value", [None, 5, ["x"]])
def test_fr24_non_string_text_fails_clearly(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, field: str, value):
    _write_fixture(tmp_path, monkeypatch, {"roles": {"b": {"skills": [_node("java", **{field: value})]}}})
    status, detail, hits = check_gates.gate_fr24_loi_dan_khong_so()
    assert status == check_gates.FAIL
    assert "crashed" not in detail
    assert any("b.java" in h and "string" in h for h in hits)


def test_fr24_missing_blurb_fails_clearly(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    node = _node("java")
    del node["blurb"]
    _write_fixture(tmp_path, monkeypatch, {"roles": {"b": {"skills": [node]}}})
    status, detail, hits = check_gates.gate_fr24_loi_dan_khong_so()
    assert status == check_gates.FAIL
    assert "crashed" not in detail
    assert any("b.java" in h and "blurb" in h for h in hits)


def test_fr24_phrase_split_across_lines_fails_with_file_and_line(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    d = _blurbs(tmp_path, monkeypatch)
    (d / "t.txt").write_text("Dòng một sạch\nChiếm phần\ntrăm lớn\n", encoding="utf-8")
    status, _detail, hits = check_gates.gate_fr24_loi_dan_khong_so()
    assert status == check_gates.FAIL
    assert len(hits) == 1 and "t.txt:2" in hits[0]


@pytest.mark.parametrize(
    "text", ["Tăng 5％", "Bước ²", "Mục ①", "Có １２ tin", "Chiếm PHẦN TRĂM", "Chiếm phần trăm"]
)
def test_fr24_normalised_forms_fail(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, text: str):
    _blurb_file(tmp_path, monkeypatch, text)
    status, _detail, hits = check_gates.gate_fr24_loi_dan_khong_so()
    assert status == check_gates.FAIL
    assert len(hits) == 1 and "t.txt:1" in hits[0]


@pytest.mark.parametrize("text", ["Java 17, rồi framework", "Viết (HTML5) trước"])
def test_fr24_tech_names_with_punctuation_still_pass(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, text: str):
    _blurb_file(tmp_path, monkeypatch, text)
    status, _detail, hits = check_gates.gate_fr24_loi_dan_khong_so()
    assert (status, hits) == (check_gates.PASS, [])


def test_fr24_real_fixture_has_only_known_keys_and_scans_texts():
    status, detail, hits = check_gates.gate_fr24_loi_dan_khong_so()
    assert (status, hits) == (check_gates.PASS, [])
    assert "scanned " in detail and "scanned 0 texts" not in detail
