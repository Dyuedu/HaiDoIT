"""#283 — luật phân loại là dữ liệu có phiên bản trong `config/classify.toml`."""

import tomllib
from pathlib import Path

import pytest

from haido_core.config import (
    DEFAULT_CLASSIFY_PATH,
    ConfigError,
    load_classify_config,
    load_rules,
)

RAW = DEFAULT_CLASSIFY_PATH.read_text(encoding="utf-8")


def _write(tmp_path: Path, text: str) -> Path:
    p = tmp_path / "classify.toml"
    p.write_text(text, encoding="utf-8")
    return p


def test_gh283_doc_duoc_file_that_va_co_phien_ban() -> None:
    cfg = load_classify_config()
    assert cfg.version.startswith("classify-")
    labels = [r.label for r in cfg.role_rules]
    for expected in ("Data Scientist", "Fullstack", "BA/PO/PM", "Security", "Hạ tầng/IT support", "UI/UX", "Game"):
        assert expected in labels
    assert labels[-1] == "Other"
    assert cfg.max_text_chars == 50000


def test_gh283_moi_nhan_vai_tro_co_ma_trong_rules_sau_report_as() -> None:
    cfg = load_classify_config()
    table = load_rules().role_codes
    for r in cfg.role_rules:
        reported = cfg.report_as.get(r.label, r.label)
        assert reported in table, r.label
    # #284: mọi nhãn có mã riêng, report_as rỗng (xem tests/deploy/test_gh284_vai_tro_moi.py).
    assert table["Data Scientist"] == "data_scientist"
    assert table["Fullstack"] == "fullstack"
    assert set(cfg.report_as.values()) <= set(table)


def test_gh283_moi_nhan_cap_co_ma_trong_rules() -> None:
    table = load_rules().level_codes
    for r in load_classify_config().seniority_rules:
        assert r.label in table, r.label


def test_gh283_thieu_khoa_thi_configerror_neu_khoa(tmp_path: Path) -> None:
    raw = tomllib.loads(RAW)
    assert "classify_version" in raw
    broken = RAW.replace('classify_version = "', 'classify_versio = "', 1)
    with pytest.raises(ConfigError, match="classify_version"):
        load_classify_config(_write(tmp_path, broken))


def test_gh283_cum_rong_thi_configerror(tmp_path: Path) -> None:
    broken = RAW + '\n[[roles]]\nlabel = "Rỗng"\nphrases = []\n'
    with pytest.raises(ConfigError, match="phrases"):
        load_classify_config(_write(tmp_path, broken))


def test_gh283_chuc_danh_con_tro_toi_vai_tro_khong_co_thi_configerror(tmp_path: Path) -> None:
    broken = RAW + '\n[[branches]]\nrole = "Không có"\nlabel = "X"\nphrases = ["x"]\n'
    with pytest.raises(ConfigError, match="branches"):
        load_classify_config(_write(tmp_path, broken))


def test_gh283_bang_so_nam_phai_tang(tmp_path: Path) -> None:
    broken = RAW + '\n[[years_to_level]]\nbelow = 1.0\nlabel = "Junior"\n'
    with pytest.raises(ConfigError, match="years_to_level"):
        load_classify_config(_write(tmp_path, broken))


def test_gh283_ma_ky_nang_trong_bang_bang_chung_phai_co_trong_tu_vung(tmp_path: Path) -> None:
    broken = RAW + '\n[skill_hints.khong_co_ma_nay]\nrole = "Backend"\nweight = 1.0\n'
    with pytest.raises(ConfigError, match="khong_co_ma_nay"):
        load_classify_config(_write(tmp_path, broken))
