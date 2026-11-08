"""Kiểm thử cổng AD-25: Alembic một head hỗ trợ down_revision dạng tuple."""

from pathlib import Path
import pytest
import tools.gates.check_gates as check_gates


def test_ad25_tuple_down_revision_single_head_passes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    vers = tmp_path / "migrations" / "versions"
    vers.mkdir(parents=True)

    (vers / "0001_base1.py").write_text(
        '"""base1"""\nrevision = "0001"\ndown_revision = None\n', encoding="utf-8"
    )
    (vers / "0002_base2.py").write_text(
        '"""base2"""\nrevision = "0002"\ndown_revision = None\n', encoding="utf-8"
    )
    (vers / "0003_merge.py").write_text(
        '"""merge"""\nrevision = "0003"\ndown_revision = ("0001", "0002")\n', encoding="utf-8"
    )

    status, detail, heads = check_gates.gate_ad25_mot_head_alembic()
    assert status == check_gates.PASS
    assert heads == []
    assert "1 head" in detail


def test_ad25_tuple_with_type_annotation_passes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    vers = tmp_path / "alembic" / "versions"
    vers.mkdir(parents=True)

    (vers / "rev1.py").write_text(
        'revision: str = "rev1"\ndown_revision = None\n', encoding="utf-8"
    )
    (vers / "rev2.py").write_text(
        'revision: str = "rev2"\ndown_revision = None\n', encoding="utf-8"
    )
    (vers / "rev3.py").write_text(
        'revision: str = "rev3"\ndown_revision: tuple[str, ...] = ("rev1", "rev2")\n', encoding="utf-8"
    )

    status, detail, heads = check_gates.gate_ad25_mot_head_alembic()
    assert status == check_gates.PASS
    assert heads == []


def test_ad25_two_branches_no_parent_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    vers = tmp_path / "haido_core" / "db" / "migrations" / "versions"
    vers.mkdir(parents=True)

    (vers / "0001_branch1.py").write_text(
        'revision = "0001"\ndown_revision = None\n', encoding="utf-8"
    )
    (vers / "0002_branch2.py").write_text(
        'revision = "0002"\ndown_revision = None\n', encoding="utf-8"
    )

    status, detail, heads = check_gates.gate_ad25_mot_head_alembic()
    assert status == check_gates.FAIL
    assert len(heads) == 2
    assert "0001" in heads
    assert "0002" in heads
    assert "2 heads found" in detail


def test_ad25_real_repo_passes():
    status, detail, heads = check_gates.gate_ad25_mot_head_alembic()
    assert status == check_gates.PASS
    assert heads == []
    assert "1 head" in detail
