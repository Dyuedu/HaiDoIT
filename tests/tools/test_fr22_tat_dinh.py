"""Kiểm thử cổng FR-22: tính tất định của lộ trình học."""

import json
from pathlib import Path
import pytest
import tools.gates.check_gates as check_gates


def test_fr22_no_order_path_with_valid_ledger_skips(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    gates_dir = tmp_path / "tools" / "gates"
    gates_dir.mkdir(parents=True)
    ledger = {
        "FR-22": {
            "issue": "https://github.com/Dyuedu/HaiDoIT/issues/22",
            "due": "2026-11-22"
        }
    }
    (gates_dir / "deferred.json").write_text(json.dumps(ledger), encoding="utf-8")

    status, detail, hits = check_gates.gate_fr22_tat_dinh()
    assert status == check_gates.SKIP
    assert "deferred" in detail.lower() or "2026-11-22" in detail


def test_fr22_no_order_path_with_expired_ledger_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    gates_dir = tmp_path / "tools" / "gates"
    gates_dir.mkdir(parents=True)
    ledger = {
        "FR-22": {
            "issue": "https://github.com/Dyuedu/HaiDoIT/issues/22",
            "due": "2020-01-01"
        }
    }
    (gates_dir / "deferred.json").write_text(json.dumps(ledger), encoding="utf-8")

    status, detail, hits = check_gates.gate_fr22_tat_dinh()
    assert status == check_gates.FAIL
    assert any("quá hạn" in d.lower() or "expired" in d.lower() for d in [detail] + hits)


def test_fr22_no_order_path_with_invalid_issue_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    gates_dir = tmp_path / "tools" / "gates"
    gates_dir.mkdir(parents=True)
    ledger = {
        "FR-22": {
            "issue": "not-a-valid-url",
            "due": "2026-11-22"
        }
    }
    (gates_dir / "deferred.json").write_text(json.dumps(ledger), encoding="utf-8")

    status, detail, hits = check_gates.gate_fr22_tat_dinh()
    assert status == check_gates.FAIL


def test_fr22_no_order_path_missing_ledger_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    status, detail, hits = check_gates.gate_fr22_tat_dinh()
    assert status == check_gates.FAIL


def test_fr22_with_order_path_function_passes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    dom = tmp_path / "haido_core" / "domain"
    dom.mkdir(parents=True)
    (dom / "path_order.py").write_text(
        "def order_path(requests):\n    return requests\n", encoding="utf-8"
    )

    status, detail, hits = check_gates.gate_fr22_tat_dinh()
    assert status == check_gates.PASS
    assert hits == []


def test_fr22_real_repo_skips():
    status, detail, hits = check_gates.gate_fr22_tat_dinh()
    assert status == check_gates.SKIP
    assert "https://github.com/Dyuedu/HaiDoIT/issues/139" in detail
    assert "2026-11-22" in detail
