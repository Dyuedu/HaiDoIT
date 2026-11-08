"""Kiểm thử cổng AD-7: haido_api không tổng hợp trên bảng job_*."""

from pathlib import Path
import pytest
import tools.gates.check_gates as check_gates


def test_ad7_table_name_mention_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    api_dir = tmp_path / "haido_api"
    api_dir.mkdir(parents=True)
    (api_dir / "routes.py").write_text(
        "from db import job_postings\n", encoding="utf-8"
    )

    status, _detail, hits = check_gates.gate_ad7_khong_tong_hop_tren_job()
    assert status == check_gates.FAIL
    assert len(hits) == 1
    assert "routes.py:1" in hits[0]


@pytest.mark.parametrize("agg_keyword", ["GROUP BY", "AVG(", "COUNT(", "percentile"])
def test_ad7_sql_aggregation_with_job_prefix_fails(agg_keyword: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    api_dir = tmp_path / "haido_api"
    api_dir.mkdir(parents=True)
    (api_dir / "query.py").write_text(
        f'query = "SELECT {agg_keyword} FROM job_records"\n', encoding="utf-8"
    )

    status, _detail, hits = check_gates.gate_ad7_khong_tong_hop_tren_job()
    assert status == check_gates.FAIL
    assert len(hits) == 1
    assert "query.py:1" in hits[0]


def test_ad7_error_only_prints_path_no_leak(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    api_dir = tmp_path / "haido_api"
    api_dir.mkdir(parents=True)
    (api_dir / "secret_query.py").write_text(
        'query = "SELECT COUNT(*) FROM job_data WHERE secret=\'SECRET_PASSWORD_123\'"\n',
        encoding="utf-8"
    )

    status, _detail, hits = check_gates.gate_ad7_khong_tong_hop_tren_job()
    assert status == check_gates.FAIL
    assert not any("SECRET_PASSWORD_123" in h for h in hits)
    assert any("secret_query.py:1" in h for h in hits)


def test_ad7_clean_haido_api_passes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    api_dir = tmp_path / "haido_api"
    api_dir.mkdir(parents=True)
    (api_dir / "routes.py").write_text(
        "query = 'SELECT * FROM stat_cells WHERE id = :id'\n", encoding="utf-8"
    )

    status, _detail, hits = check_gates.gate_ad7_khong_tong_hop_tren_job()
    assert status == check_gates.PASS
    assert hits == []


def test_ad7_missing_haido_api_skips(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    status, detail, hits = check_gates.gate_ad7_khong_tong_hop_tren_job()
    assert status == check_gates.SKIP
    assert hits == []


def test_ad7_real_repo_passes():
    status, _detail, hits = check_gates.gate_ad7_khong_tong_hop_tren_job()
    assert status == check_gates.PASS
    assert hits == []
