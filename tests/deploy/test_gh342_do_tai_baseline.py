"""#342 — môi trường đo tải: `deploy/compose.loadtest.yml` phải chạy API như production, và script k6 chỉ gọi những
gì API có thật.

Nếu compose đo lệch prod (image khác, lệnh khác, nguồn `fake`), con số baseline đo một hệ thống khác. Nếu script gọi
đường dẫn, vai trò hay kỹ năng không có, k6 đếm 404 thành lỗi và bài đo dừng sớm vì sai kịch bản, không phải vì tải.
"""

import json
import re
from pathlib import Path

import pytest
import yaml

from haido_api.main import create_app
from haido_api.routes.market import SOURCE_ENV
from haido_core.config import load_rules
from haido_core.vocab.skills import load_seed_skills

ROOT = Path(__file__).resolve().parents[2]
DEPLOY = ROOT / "deploy"
K6 = ROOT / "loadtest" / "k6"


def _services(name: str) -> dict:
    return yaml.safe_load((DEPLOY / name).read_text(encoding="utf-8"))["services"]


def _load_api() -> dict:
    return _services("compose.loadtest.yml")["api"]


def test_gh342_api_build_tu_dockerfile_cua_prod() -> None:
    build = _load_api()["build"]
    assert build["dockerfile"] == "deploy/api.Dockerfile"
    assert (DEPLOY / build["context"]).resolve() == ROOT


def test_gh342_api_khong_ghi_de_lenh_cua_image() -> None:
    api = _load_api()
    assert "command" not in api and "entrypoint" not in api, "đổi lệnh thì không còn đo uvicorn một worker như prod"


@pytest.mark.parametrize("op", sorted(SOURCE_ENV))
def test_gh342_api_doc_stat_cho_moi_nguon(op: str) -> None:
    assert str(_load_api()["environment"].get(SOURCE_ENV[op])) == "stat"


def test_gh342_api_gioi_han_hai_cpu_nhu_vps() -> None:
    limits = _load_api()["deploy"]["resources"]["limits"]
    assert float(limits["cpus"]) == 2.0


def test_gh342_healthcheck_giong_prod() -> None:
    assert _load_api()["healthcheck"]["test"] == _services("compose.prod.yml")["api"]["healthcheck"]["test"]


def test_gh342_moi_cong_chi_mo_tren_localhost() -> None:
    for name, svc in _services("compose.loadtest.yml").items():
        for port in svc.get("ports", []):
            assert str(port).startswith("127.0.0.1:"), f"{name} mở cổng {port} ra ngoài localhost"


def test_gh342_db_do_co_ten_ket_thuc_bang_test() -> None:
    # Tool seed xóa schema haido; chỉ chạy trên DB tên `_test` (FR-1).
    assert _services("compose.loadtest.yml")["postgres"]["environment"]["POSTGRES_DB"].endswith("_test")


def _script() -> str:
    return (K6 / "baseline.js").read_text(encoding="utf-8")


def test_gh342_moi_duong_dan_trong_script_co_trong_openapi() -> None:
    paths = set(re.findall(r"/api/v1/[a-z0-9-]+", _script()))
    assert paths, "script không gọi endpoint nào"
    known = set(create_app().openapi()["paths"])
    assert sorted(paths - known) == []


def test_gh342_script_khong_goi_lo_trinh_vi_stat_luon_404() -> None:
    assert "/api/v1/learning-path" not in _script()


def _params() -> dict:
    return json.loads((K6 / "params.json").read_text(encoding="utf-8"))


def test_gh342_vai_tro_trong_params_co_trong_rules() -> None:
    roles = _params()["roles"]
    assert roles
    assert sorted(set(roles) - set(load_rules().role_codes.values())) == []


def test_gh342_cap_bac_trong_params_hop_le() -> None:
    rules = load_rules()
    allowed = set(rules.level_codes.values()) | set(rules.level_groups) | {"all"}
    levels = _params()["levels"]
    assert levels
    assert sorted(set(levels) - allowed) == []


def test_gh342_ky_nang_trong_params_co_trong_tu_vung() -> None:
    skills = _params()["skills"]
    assert skills
    assert sorted(set(skills) - {s.code for s in load_seed_skills()}) == []


def test_gh342_co_smoke_va_breakpoint_dung_ramping_arrival_rate() -> None:
    script = _script()
    assert re.search(r"\bsmoke\s*:", script)
    assert re.search(r"\bbreakpoint\s*:", script)
    assert "'ramping-arrival-rate'" in script or '"ramping-arrival-rate"' in script


def test_gh342_nguong_p95_va_loi_dung_bai_do_khi_vuot() -> None:
    script = _script()
    for metric, rule in (("http_req_duration", "p(95)<200"), ("http_req_failed", "rate<0.001")):
        block = re.search(rf"{metric}\s*:\s*\[(.*?)\]", script, re.DOTALL)
        assert block, f"thiếu ngưỡng {metric}"
        assert rule in block.group(1) and "abortOnFail: true" in block.group(1)
