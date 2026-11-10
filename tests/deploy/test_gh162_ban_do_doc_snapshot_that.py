"""#162 — bản đồ đọc snapshot đã công bố ở production, và chip vai trò là các vai trò trong config."""

import json
import re
from pathlib import Path

import yaml

from haido_core.config import ALL_ROLES, load_rules

ROOT = Path(__file__).resolve().parents[2]
CITY_SHARES_VAR = "HAIDO_MARKET_SOURCE_CITY_SHARES"


def _api_env(compose: str) -> dict[str, str]:
    env = yaml.safe_load((ROOT / "deploy" / compose).read_text(encoding="utf-8"))["services"]["api"]["environment"]
    assert isinstance(env, dict)
    return {k: str(v) for k, v in env.items()}


def _chips() -> list[tuple[str, str]]:
    text = (ROOT / "web" / "lib" / "labels.ts").read_text(encoding="utf-8")
    block = re.search(r"ROLE_OPTIONS[^=]*=\s*\[(.*?)\n\];", text, re.DOTALL)
    assert block, "không thấy ROLE_OPTIONS trong web/lib/labels.ts"
    return re.findall(r'\{\s*code:\s*"([^"]+)",\s*label:\s*"([^"]+)"\s*\}', block.group(1))


# ---------------------------------------------------------------- AC: số của bản đồ đến từ snapshot đã công bố


def test_gh162_compose_prod_chon_nguon_stat_cho_city_shares() -> None:
    assert _api_env("compose.prod.yml")[CITY_SHARES_VAR] == "stat"


def test_gh162_compose_local_giu_nguon_gia_de_smoke_chay_tren_db_rong() -> None:
    # compose.local chạy ở job smoke của CI với DB rỗng: nguồn `stat` sẽ trả 404 unknown_cell, không có `data`.
    assert _api_env("compose.local.yml").get(CITY_SHARES_VAR, "fake") == "fake"


def test_gh162_vai_tro_smoke_cua_ci_la_vai_tro_trong_config_va_co_trong_ban_gia() -> None:
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    roles = set(re.findall(r"city-shares\?role=([a-z_]+)", ci))
    assert roles, "smoke phải gọi city-shares với một vai trò"
    fixture = json.loads((ROOT / "haido_api" / "fixtures" / "fake_market.json").read_text(encoding="utf-8"))
    assert roles <= {ALL_ROLES, *load_rules().roles}
    assert roles <= set(fixture["city_shares"])


# ---------------------------------------------------------------- AC: chip vai trò là các vai trò đã cấu hình


def test_gh162_chip_vai_tro_la_all_cong_cac_vai_tro_trong_config_theo_thu_tu() -> None:
    chips = _chips()
    assert [code for code, _ in chips] == [ALL_ROLES, *load_rules().roles]


def test_gh162_chip_co_nhan_tieng_viet_khong_rong_va_khong_trung() -> None:
    labels = [label for _, label in _chips()]
    assert all(label.strip() for label in labels)
    assert len(set(labels)) == len(labels)
    assert dict(_chips())[ALL_ROLES] == "Tất cả"


def test_gh162_ban_gia_chi_co_vai_tro_la_ma_trong_config() -> None:
    fixture = json.loads((ROOT / "haido_api" / "fixtures" / "fake_market.json").read_text(encoding="utf-8"))
    assert set(fixture["city_shares"]) <= {ALL_ROLES, *load_rules().roles}


def test_gh162_api_dockerfile_copy_config_de_load_rules_chay_duoc_khi_nguon_la_stat() -> None:
    lines = (ROOT / "deploy" / "api.Dockerfile").read_text(encoding="utf-8").splitlines()
    copies = [line.split()[1:-1] for line in lines if line.strip().upper().startswith("COPY ")]
    assert any(srcs == ["config"] or srcs == ["config/"] for srcs in copies), "api.Dockerfile thiếu COPY config"
