"""AD-10 — ngưỡng và danh sách nguồn đọc từ config có phiên bản (Story 1.4)."""

import ast
from pathlib import Path

import pytest

from haido_core.config import ConfigError, load_rules

AUTO = ("zalo", "itnavi", "careerlink", "vietnamworks", "momo", "topdev", "itviec")


def _write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "rules.toml"
    path.write_text(body, encoding="utf-8")
    return path


def test_ad10_rules_mac_dinh_co_phien_ban_cua_so_va_bay_nguon() -> None:
    rules = load_rules()
    assert rules.config_version
    assert rules.window_days == 60
    assert rules.auto_sources == AUTO
    assert "topcv" not in rules.auto_sources


def test_ad10_doc_tu_file_chi_dinh(tmp_path: Path) -> None:
    path = _write(tmp_path, 'config_version = "t-1"\nwindow_days = 30\n[sources]\nauto = ["a", "b"]\n')
    rules = load_rules(path)
    assert (rules.config_version, rules.window_days, rules.auto_sources) == ("t-1", 30, ("a", "b"))


@pytest.mark.parametrize(
    ("body", "khoa"),
    [
        ('window_days = 30\n[sources]\nauto = ["a"]\n', "config_version"),
        ('config_version = "t"\n[sources]\nauto = ["a"]\n', "window_days"),
        ('config_version = "t"\nwindow_days = 30\n', "sources.auto"),
    ],
)
def test_ad10_thieu_khoa_thi_bao_loi_tieng_viet(tmp_path: Path, body: str, khoa: str) -> None:
    with pytest.raises(ConfigError, match="thiếu") as exc:
        load_rules(_write(tmp_path, body))
    assert khoa in str(exc.value)


def test_ad10_gia_tri_sai_kieu_thi_bao_loi(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="window_days"):
        load_rules(_write(tmp_path, 'config_version = "t"\nwindow_days = 0\n[sources]\nauto = ["a"]\n'))
    with pytest.raises(ConfigError, match="sources.auto"):
        load_rules(_write(tmp_path, 'config_version = "t"\nwindow_days = 5\n[sources]\nauto = "a"\n'))


def test_ad10_file_khong_ton_tai(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="tìm thấy"):
        load_rules(tmp_path / "khong-co.toml")


def test_ad10_auto_sources_khop_voi_scraper_ingest() -> None:
    tree = ast.parse((Path(__file__).resolve().parents[2] / "scraper" / "ingest.py").read_text(encoding="utf-8"))
    values = [
        ast.literal_eval(node.value)
        for node in tree.body
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "AUTO_SOURCES" for t in node.targets)
    ]
    assert len(values) == 1
    assert load_rules().auto_sources == tuple(values[0])
