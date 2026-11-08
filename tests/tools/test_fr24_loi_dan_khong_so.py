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
            "due": "2026-11-22"
        }
    }
    (gates_dir / "deferred.json").write_text(json.dumps(ledger), encoding="utf-8")

    status, detail, hits = check_gates.gate_fr24_loi_dan_khong_so()
    assert status == check_gates.SKIP
    assert "deferred" in detail.lower() or "2026-11-22" in detail


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


def test_fr24_real_repo_skips():
    status, detail, hits = check_gates.gate_fr24_loi_dan_khong_so()
    assert status == check_gates.SKIP
    assert "https://github.com/Dyuedu/HaiDoIT/issues/138" in detail
    assert "2026-11-22" in detail
