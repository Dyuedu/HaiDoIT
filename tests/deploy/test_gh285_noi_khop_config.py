"""#285 — 34 tỉnh, Remote, Nước ngoài: cùng mã và nhãn ở config, bộ phân loại, web và bản giả."""

import json
import re
from pathlib import Path

from haido_core.config import load_classify_config, load_rules

ROOT = Path(__file__).resolve().parents[2]
LABELS_TS = (ROOT / "web" / "lib" / "labels.ts").read_text(encoding="utf-8")
FAKE = json.loads((ROOT / "haido_api" / "fixtures" / "fake_market.json").read_text(encoding="utf-8"))
SPECIAL = {"remote", "abroad", "unknown"}


def _web_city_labels() -> dict[str, str]:
    block = re.search(r"CITY_LABELS[^=]*=\s*\{(.*?)\n\};", LABELS_TS, re.DOTALL)
    assert block, "không thấy CITY_LABELS trong web/lib/labels.ts"
    return dict(re.findall(r'^\s*([a-z_]+):\s*"([^"]+)"', block.group(1), re.MULTILINE))


def test_gh285_config_co_34_tinh_remote_nuoc_ngoai_khong_xac_dinh_va_khong_con_other() -> None:
    codes = load_rules().city_codes
    provinces = {label: code for label, code in codes.items() if code not in SPECIAL}
    assert len(provinces) == 34
    assert codes["Remote"] == "remote"
    assert codes["Nước ngoài"] == "abroad"
    assert "other" not in codes.values()


def test_gh285_moi_tinh_cua_bo_phan_loai_co_ma() -> None:
    codes = load_rules().city_codes
    for rule in load_classify_config().city_rules:
        assert rule.label in codes, rule.label


def test_gh285_nhom_luon_co() -> None:
    rules = load_rules()
    assert rules.always_cities == ("ha_noi", "ho_chi_minh", "da_nang", "remote", "abroad", "unknown")
    assert set(rules.always_cities) <= set(rules.city_codes.values())


def test_gh285_nhan_web_cua_34_tinh_trung_nhan_config() -> None:
    web = _web_city_labels()
    for label, code in load_rules().city_codes.items():
        assert code in web, code
        if code not in SPECIAL:
            assert web[code] == label, code


def test_gh285_ban_gia_khong_con_other_va_co_nhom_luon_co() -> None:
    for role, levels in FAKE["city_shares"].items():
        for key, block in levels.items():
            cities = [row["city"] for row in block["rows"]]
            assert "other" not in cities, (role, key)
            assert set(load_rules().always_cities) <= set(cities), (role, key)
