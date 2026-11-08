"""Kiểm thử cổng AD-17: hình dạng Envelope meta."""

from pathlib import Path
import pytest
import tools.gates.check_gates as check_gates


def test_ad17_missing_snapshot_date_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    domain_dir = tmp_path / "haido_core" / "domain"
    domain_dir.mkdir(parents=True)

    # Viết Envelope thiếu snapshot_date
    envelope_code = """
class Envelope:
    snapshot_status: str
    sources: list[str]
    sources_failed: list[str]
    thresholds: dict
    coverage_notes: list[str]
    n_by_measure: dict
    insufficient_by_measure: dict
"""
    (domain_dir / "envelope.py").write_text(envelope_code, encoding="utf-8")

    status, detail, hits = check_gates.gate_ad17_hinh_dang_meta()
    assert status == check_gates.FAIL
    assert any("snapshot_date" in h for h in hits)


def test_ad17_missing_envelope_class_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    domain_dir = tmp_path / "haido_core" / "domain"
    domain_dir.mkdir(parents=True)
    (domain_dir / "models.py").write_text("class OtherModel:\n    pass\n", encoding="utf-8")

    status, detail, hits = check_gates.gate_ad17_hinh_dang_meta()
    assert status == check_gates.FAIL
    assert "no Envelope model found" in detail


def test_ad17_missing_domain_dir_skips(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    status, detail, hits = check_gates.gate_ad17_hinh_dang_meta()
    assert status == check_gates.SKIP
    assert hits == []


def test_ad17_real_repo_passes():
    status, detail, hits = check_gates.gate_ad17_hinh_dang_meta()
    assert status == check_gates.PASS
    assert hits == []
