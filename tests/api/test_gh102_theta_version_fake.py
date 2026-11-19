"""#102 (DAT.30) — `meta.thresholds.theta_version` có mặt ở mọi route của bản giả và khớp sổ đăng ký θ.

Bản giả (`FakeMarket`) đọc `thresholds` từ `haido_api/fixtures/fake_market.json`. Fixture của web chép lại response của
bản giả (`test_ad17_web_fixtures.py`), nên đổi fixture thì sinh lại các file đó.
"""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from haido_api.main import app
from haido_core.config import load_rules
from haido_core.domain.envelope import Thresholds

ROOT = Path(__file__).resolve().parents[2]
RULES = load_rules()

REQUESTS = [
    ("/api/v1/city-shares", {"role": "backend"}),
    ("/api/v1/newcomer-roles", {}),
    ("/api/v1/skill-rates", {"role": "backend", "level": "entry"}),
    ("/api/v1/skill-roles", {"skill": "python"}),
    ("/api/v1/learning-path", {"role": "backend", "level": "entry"}),
]


@pytest.mark.parametrize(("path", "params"), REQUESTS)
def test_gh102_ac1_moi_route_cua_ban_gia_co_theta_version_dung_voi_so_dang_ky(path: str, params: dict) -> None:
    resp = TestClient(app).get(path, params=params)
    assert resp.status_code == 200, resp.text
    thresholds = resp.json()["meta"]["thresholds"]
    version = RULES.theta(thresholds["theta_version"])
    assert (thresholds["theta_core"], thresholds["theta_common"]) == (version.theta_core, version.theta_common)


def test_gh102_ac1_fixture_ban_gia_dung_phien_ban_hien_hanh() -> None:
    raw = json.loads((ROOT / "haido_api" / "fixtures" / "fake_market.json").read_text(encoding="utf-8"))
    assert raw["snapshot"]["thresholds"]["theta_version"] == RULES.theta_version


@pytest.mark.parametrize("value", [None, "", 1])
def test_gh102_thresholds_bat_buoc_co_theta_version_la_chuoi_khong_rong(value: object) -> None:
    data = {"min_sample": 30, "theta_core": 0.3, "theta_common": 0.1}
    if value is not None:
        data["theta_version"] = value
    with pytest.raises(ValidationError, match="theta_version"):
        Thresholds.model_validate(data)


def test_gh102_thresholds_nhan_theta_version() -> None:
    t = Thresholds.model_validate({"min_sample": 30, "theta_core": 0.3, "theta_common": 0.1, "theta_version": "theta-1"})
    assert t.theta_version == "theta-1"
