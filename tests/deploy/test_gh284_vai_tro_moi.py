"""#284 — bảy vai trò mới có mã riêng ở config, bản giả và web (cùng thứ tự)."""

import json
import re
from pathlib import Path

from haido_core.config import ALL_ROLES, load_classify_config, load_rules

ROOT = Path(__file__).resolve().parents[2]
FAKE = json.loads((ROOT / "haido_api" / "fixtures" / "fake_market.json").read_text(encoding="utf-8"))
LABELS_TS = (ROOT / "web" / "lib" / "labels.ts").read_text(encoding="utf-8")

ROLES = [
    "embedded", "ai_ml", "data_scientist", "data_engineer", "data_analyst", "qa", "devops", "security", "it_infra",
    "mobile", "frontend", "backend", "fullstack", "ba_po_pm", "ui_ux", "game", "other",
]  # fmt: skip
NEW = {
    "Data Scientist": "data_scientist",
    "Security": "security",
    "Hạ tầng/IT support": "it_infra",
    "Fullstack": "fullstack",
    "BA/PO/PM": "ba_po_pm",
    "UI/UX": "ui_ux",
    "Game": "game",
}


def test_gh284_roles_cua_config_co_17_ma_dung_thu_tu() -> None:
    assert list(load_rules().roles) == ROLES


def test_gh284_moi_nhan_cua_bo_phan_loai_co_ma_rieng_va_report_as_rong() -> None:
    codes = load_rules().role_codes
    for label, code in NEW.items():
        assert codes[label] == code
    cfg = load_classify_config()
    assert dict(cfg.report_as) == {}
    for rule in cfg.role_rules:
        assert rule.label in codes, rule.label


def test_gh284_chip_web_co_nhan_tieng_viet_cho_ma_moi() -> None:
    block = re.search(r"ROLE_OPTIONS[^=]*=\s*\[(.*?)\n\];", LABELS_TS, re.DOTALL)
    assert block
    chips = dict(re.findall(r'code:\s*"([a-z_]+)",\s*label:\s*"([^"]+)"', block.group(1)))
    assert list(chips) == [ALL_ROLES, *ROLES]
    expected = {
        "data_scientist": "Khoa học dữ liệu",
        "fullstack": "Fullstack",
        "ba_po_pm": "BA / PO / PM",
        "security": "Bảo mật",
        "it_infra": "Hạ tầng & IT support",
        "ui_ux": "UI/UX",
        "game": "Phát triển game",
    }
    for code, label in expected.items():
        assert chips[code] == label


def test_gh284_ban_gia_co_city_shares_va_dong_nguoi_moi_cho_moi_ma_moi() -> None:
    for code in NEW.values():
        assert "all" in FAKE["city_shares"][code], code
        block = FAKE["city_shares"][code]["all"]
        assert block["total_cell_id"] == f"vn.{code}"
        for row in block["rows"]:
            assert row["cell_id"] in FAKE["cells"], row["cell_id"]
        assert f"vn.{code}.entry" in FAKE["cells"]
    assert [row["role"] for row in FAKE["newcomer_roles"]["rows"]] == ROLES
