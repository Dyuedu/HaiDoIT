"""#163 — bộ chọn cấp bậc của bản đồ là các cấp trong config, mặc định là cấp của #134."""

import json
import re
from pathlib import Path

from haido_api.routes.market import LEVEL_CODES
from haido_core.config import ALL_LEVELS, load_rules

ROOT = Path(__file__).resolve().parents[2]
LABELS = ROOT / "web" / "lib" / "labels.ts"


def _chips() -> list[tuple[str, str]]:
    text = LABELS.read_text(encoding="utf-8")
    block = re.search(r"export const LEVEL_OPTIONS[^=]*=\s*\[(.*?)\n\];", text, re.DOTALL)
    assert block, "không thấy LEVEL_OPTIONS trong web/lib/labels.ts"
    return re.findall(r'\{\s*code:\s*"([^"]+)",\s*label:\s*"([^"]+)"\s*\}', block.group(1))


def test_gh163_nut_cap_bac_la_cap_trong_config_roi_den_all_theo_thu_tu() -> None:
    assert [code for code, _ in _chips()] == [*load_rules().level_options, ALL_LEVELS]


def test_gh163_nut_cap_bac_co_nhan_tieng_viet_khong_rong_va_khong_trung() -> None:
    labels = [label for _, label in _chips()]
    assert all(label.strip() for label in labels)
    assert len(set(labels)) == len(labels)
    names = dict(_chips())
    assert names[ALL_LEVELS] == "Mọi cấp bậc"
    assert names["unknown"] == "Chưa ghi cấp bậc"
    assert names["entry"] == "Mới vào nghề"


def test_gh163_cap_mac_dinh_cua_web_la_entry_nhu_134_va_nam_trong_config() -> None:
    text = LABELS.read_text(encoding="utf-8")
    assert re.search(r'DEFAULT_LEVEL\s*=\s*"entry"', text)
    assert "entry" in load_rules().level_options
    assert load_rules().level_groups["entry"] == ("intern", "fresher", "junior")


def test_gh163_dong_chu_thich_nhom_entry_liet_ke_dung_nhan_cua_nhom_trong_config_theo_thu_tu() -> None:
    names = dict(_chips())
    members = [names[code] for code in load_rules().level_groups["entry"]]
    expected = f"Mới vào nghề gồm {', '.join(members[:-1])} và {members[-1]}."
    # #293: dòng chú thích là hằng `LEVEL_ENTRY_NOTE` trong labels.ts, ô Cấp bậc của map-screen.tsx dùng hằng đó.
    text = LABELS.read_text(encoding="utf-8")
    note = re.search(r'^export const LEVEL_ENTRY_NOTE\s*=\s*"([^"]*)";', text, re.MULTILINE)
    assert note, "không thấy `export const LEVEL_ENTRY_NOTE` trong web/lib/labels.ts"
    screen = (ROOT / "web" / "app" / "components" / "map" / "map-screen.tsx").read_text(encoding="utf-8")
    assert "note={LEVEL_ENTRY_NOTE}" in screen
    assert note.group(1) == expected


def test_gh163_api_nhan_dung_cac_cap_cua_nut() -> None:
    assert [code for code, _ in _chips()] == [*LEVEL_CODES[1:], ALL_LEVELS]
    assert LEVEL_CODES[0] == ALL_LEVELS


def test_gh163_ban_gia_chi_co_cap_all_va_entry_la_ma_trong_config() -> None:
    fixture = json.loads((ROOT / "haido_api" / "fixtures" / "fake_market.json").read_text(encoding="utf-8"))
    allowed = {ALL_LEVELS, *load_rules().level_options}
    for role, keys in fixture["city_shares"].items():
        levels = {key for key in keys if ".y" not in key}  # #280: khóa `<cấp>.y<N>` là mốc số năm của cấp đó
        assert levels == {"all", "entry"}, role
        assert {key.split(".y")[0] for key in keys} <= levels
        assert set(levels) <= allowed
