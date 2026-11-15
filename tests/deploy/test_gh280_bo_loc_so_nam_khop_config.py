"""#280 — bộ chọn số năm của bản đồ là các mốc trong config, `any` đứng đầu và là mặc định."""

import re
from pathlib import Path

from haido_api.routes.market import YEARS_CODES
from haido_core.config import ANY_YEARS, load_rules

ROOT = Path(__file__).resolve().parents[2]
LABELS = ROOT / "web" / "lib" / "labels.ts"


def _chips() -> list[tuple[str, str]]:
    text = LABELS.read_text(encoding="utf-8")
    block = re.search(r"export const YEARS_OPTIONS[^=]*=\s*\[(.*?)\n\];", text, re.DOTALL)
    assert block, "không thấy YEARS_OPTIONS trong web/lib/labels.ts"
    return re.findall(r'\{\s*code:\s*"([^"]+)",\s*label:\s*"([^"]+)"\s*\}', block.group(1))


def test_gh280_nut_so_nam_la_any_roi_cac_moc_trong_config_theo_thu_tu() -> None:
    expected = [ANY_YEARS, *(str(n) for n in load_rules().years_options)]
    assert [code for code, _ in _chips()] == expected
    assert list(YEARS_CODES) == expected


def test_gh280_nut_so_nam_co_nhan_tieng_viet_khong_rong_va_khong_trung() -> None:
    labels = dict(_chips())
    assert all(label.strip() for label in labels.values())
    assert len(set(labels.values())) == len(labels)
    assert labels[ANY_YEARS] == "Mọi số năm"
    assert labels["0"] == "Không cần kinh nghiệm"
    for n in load_rules().years_options:
        if n > 0:
            assert labels[str(n)] == f"Tối đa {n} năm"


def test_gh280_so_nam_mac_dinh_cua_web_la_any() -> None:
    assert re.search(r'DEFAULT_YEARS\s*=\s*"any"', LABELS.read_text(encoding="utf-8"))
