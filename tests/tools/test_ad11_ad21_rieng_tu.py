"""Kiểm thử cổng AD-11 / AD-21: quyền riêng tư, không lưu CV/JD text và không PII trong file dữ liệu."""

import json
from pathlib import Path
import pytest
import tools.gates.check_gates as check_gates


def test_ad11_ad21_cv_text_in_schema_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    db_dir = tmp_path / "haido_core" / "db"
    db_dir.mkdir(parents=True)
    (db_dir / "models.py").write_text("class Job:\n    cv_text: str\n", encoding="utf-8")

    status, _detail, hits = check_gates.gate_ad11_ad21_rieng_tu()
    assert status == check_gates.FAIL
    assert any("cv_text" in h for h in hits)


def test_ad11_ad21_email_in_data_file_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True)
    (data_dir / "records.jsonl").write_text('{"title": "Dev", "contact": "hr_lead@company.vn"}\n', encoding="utf-8")

    status, _detail, hits = check_gates.gate_ad11_ad21_rieng_tu()
    assert status == check_gates.FAIL
    assert len(hits) == 1
    assert "data/records.jsonl:1" in hits[0]


def test_ad11_ad21_vn_phone_in_data_file_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True)
    (data_dir / "jobs.json").write_text('{"phone": "0987654321"}\n', encoding="utf-8")

    status, _detail, hits = check_gates.gate_ad11_ad21_rieng_tu()
    assert status == check_gates.FAIL
    assert len(hits) == 1
    assert "data/jobs.json:1" in hits[0]


def test_ad11_ad21_email_and_phone_in_tests_ignored(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    test_dir = tmp_path / "tests" / "fixtures"
    test_dir.mkdir(parents=True)
    (test_dir / "dummy.json").write_text('{"email": "test@domain.com", "phone": "0987654321"}\n', encoding="utf-8")

    status, _detail, hits = check_gates.gate_ad11_ad21_rieng_tu()
    assert status == check_gates.PASS
    assert hits == []


def test_ad11_ad21_error_does_not_leak_pii(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True)
    secret_email = "super_secret_pii@private.corp.vn"
    secret_phone = "0912345678"
    (data_dir / "pii.jsonl").write_text(f'{{"email": "{secret_email}", "tel": "{secret_phone}"}}\n', encoding="utf-8")

    status, _detail, hits = check_gates.gate_ad11_ad21_rieng_tu()
    assert status == check_gates.FAIL
    for hit in hits:
        assert secret_email not in hit
        assert secret_phone not in hit
        assert "pii.jsonl:1" in hit


def test_ad11_ad21_gate_does_not_skip_on_clean_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    db_dir = tmp_path / "haido_core" / "db"
    db_dir.mkdir(parents=True)
    (db_dir / "schema.py").write_text("class CleanTable:\n    id: int\n", encoding="utf-8")

    status, _detail, hits = check_gates.gate_ad11_ad21_rieng_tu()
    assert status == check_gates.PASS
    assert hits == []


def test_ad11_ad21_deferred_ledger_has_cv_5mb_issue():
    ledger_path = check_gates.ROOT / "tools" / "gates" / "deferred.json"
    assert ledger_path.is_file(), "deferred.json must exist"
    data = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert "AD-11-temp" in data
    entry = data["AD-11-temp"]
    assert entry["due"] == "2026-11-15"
    assert entry["issue"] == "https://github.com/Dyuedu/HaiDoIT/issues/140"


def test_ad11_ad21_real_repo_passes():
    status, _detail, hits = check_gates.gate_ad11_ad21_rieng_tu()
    assert status == check_gates.PASS
    assert hits == []
