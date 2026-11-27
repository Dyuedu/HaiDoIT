"""FR-27, FR-28, FR-29 — `GET /api/v1/posting-check` (#230): mục `match` có số, `market` và `warnings` còn `not_ready`.

Hình `ready` của hai mục sau nằm ở `test_fr30_fr31_posting_ready_shapes.py`.
"""

from typing import Any

import pytest
from fastapi.testclient import TestClient
from posting_samples import HAVE_16_OF_18, POSTING_SKILLS, csv

from haido_api.main import app
from haido_api.posting_match import build_match, match_percent
from haido_api.schemas.posting import PostingCheckData
from haido_core.config import load_rules
from haido_core.domain.envelope import Envelope

URL = "/api/v1/posting-check"
BASE = {"role": "backend", "level": "junior", "skills": csv(POSTING_SKILLS)}


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


def _get(client: TestClient, **extra: str) -> dict[str, Any]:
    resp = client.get(URL, params={**BASE, **extra})
    assert resp.status_code == 200, resp.text
    return resp.json()


def _by_code(match: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {s["skill"]["code"]: s for s in match["skills"]}


def test_fr28_hinh_envelope_va_ba_muc(client: TestClient) -> None:
    body = _get(client, have=csv(HAVE_16_OF_18))
    Envelope[PostingCheckData].model_validate(body)
    data = body["data"]
    assert set(data) == {"role", "level", "branch", "cell_id", "has_profile", "match", "market", "warnings"}
    assert data["branch"] is None
    assert data["cell_id"] == "vn.backend.junior"
    assert data["cell_id"] in body["meta"]["cells"]
    assert data["match"]["status"] == "ready"


def test_fr28_vi_du_16_tren_18_la_89_phan_tram(client: TestClient) -> None:
    match = _get(client, have=csv(HAVE_16_OF_18))["data"]["match"]
    assert match["level"] == {"points": 16, "max_points": 18, "percent": 89}


def test_fr28_dem_tho_theo_nhom(client: TestClient) -> None:
    match = _get(client, have=csv(HAVE_16_OF_18))["data"]["match"]
    assert match["groups"] == [
        {"group": "core", "total": 4, "had": 4},
        {"group": "common", "total": 2, "had": 2},
        {"group": "specific", "total": 2, "had": 0},
    ]


def test_fr28_ky_nang_ngoai_tin_khong_doi_muc_khop(client: TestClient) -> None:
    # `rest_api` và `python` có trong hồ sơ nhưng tin không nêu: không vào tử số lẫn mẫu số (mức khớp chỉ tính kỹ năng của tin).
    match = _get(client, have=csv([*HAVE_16_OF_18, "rest_api", "python"]))["data"]["match"]
    assert match["level"] == {"points": 16, "max_points": 18, "percent": 89}
    assert [g["had"] for g in match["groups"]] == [4, 2, 0]


def test_fr28_trong_so_lay_tu_cau_hinh_co_phien_ban() -> None:
    rules = load_rules()
    assert rules.posting_match_weights == {"core": 3, "common": 2, "specific": 1}
    match = _get(TestClient(app), have="java")["data"]["match"]
    assert match["config_version"] == rules.config_version
    assert match["level"] == {"points": 3, "max_points": 18, "percent": 17}


def test_fr28_build_match_dung_trong_so_duoc_truyen_vao() -> None:
    rates = TestClient(app).get("/api/v1/skill-rates", params={"role": "backend", "level": "junior"}).json()
    from haido_api.schemas.market import SkillRatesData

    data = SkillRatesData.model_validate(rates["data"])
    equal = build_match(data, POSTING_SKILLS, set(HAVE_16_OF_18), {"core": 1, "common": 1, "specific": 1}, "t")
    assert equal.level is not None
    assert (equal.level.points, equal.level.max_points, equal.level.percent) == (6, 8, 75)


@pytest.mark.parametrize(
    ("points", "max_points", "percent"),
    [(16, 18, 89), (1, 2, 50), (5, 8, 63), (1, 3, 33), (2, 3, 67), (0, 5, 0), (5, 5, 100)],
)
def test_fr28_phan_tram_lam_tron_nua_len(points: int, max_points: int, percent: int) -> None:
    assert match_percent(points, max_points) == percent


def test_fr29_nhom_cua_tung_ky_nang_va_thu_tu_do_may_chu(client: TestClient) -> None:
    match = _get(client)["data"]["match"]
    groups = [s["group"] for s in match["skills"]]
    assert groups == ["core"] * 4 + ["common"] * 2 + ["specific"] * 2
    by_code = _by_code(match)
    assert by_code["java"]["group"] == "core"
    assert by_code["docker"]["group"] == "common"
    assert by_code["kafka"]["group"] == "specific"
    assert by_code["java"]["skill"]["name_en"] and by_code["java"]["skill"]["name_vi"]
    rates = [s["rate"]["value"] for s in match["skills"][:4]]
    assert rates == sorted(rates, reverse=True)
    for s in match["skills"]:
        assert s["rate"]["kind"] == "skill_rate"
        assert s["rate"]["cell_id"] == "vn.backend.junior"


def test_fr29_ky_nang_hiem_trong_o_la_specific_ke_ca_khi_khong_co_dong(client: TestClient) -> None:
    body = _get(client, skills="java,python")
    by_code = _by_code(body["data"]["match"])
    assert by_code["python"]["group"] == "specific"
    assert by_code["python"]["rate"]["value"] == 0.0
    assert by_code["python"]["rate"]["display"] == "shown"
    assert by_code["java"]["group"] == "core"


def test_fr28_cv_first_la_ky_nang_vua_co_vua_duoc_tin_nhac(client: TestClient) -> None:
    match = _get(client, have="python,docker,java")["data"]["match"]
    assert match["cv_first"] == ["java", "docker"]  # thứ tự của `skills`: core trước common


def test_fr28_tung_ky_nang_co_co_have(client: TestClient) -> None:
    match = _get(client, have=csv(HAVE_16_OF_18))["data"]["match"]
    assert {c: s["have"] for c, s in _by_code(match).items()} == {
        **{c: True for c in HAVE_16_OF_18},
        "kafka": False,
        "linux": False,
    }


def test_fr28_khong_ho_so_chi_hien_nhom_va_ty_le(client: TestClient) -> None:
    data = _get(client)["data"]
    assert data["has_profile"] is False
    match = data["match"]
    assert match["status"] == "ready"
    assert match["level"] is None
    assert match["cv_first"] == []
    assert all(s["have"] is None for s in match["skills"])
    assert [(g["group"], g["total"], g["had"]) for g in match["groups"]] == [
        ("core", 4, None),
        ("common", 2, None),
        ("specific", 2, None),
    ]
    assert all(s["rate"]["value"] is not None for s in match["skills"])


def test_fr28_co_ho_so_bat_co_have(client: TestClient) -> None:
    assert _get(client, have="git")["data"]["has_profile"] is True


def test_fr27_o_duoi_30_quay_ve_o_rong_hon_co_nhan(client: TestClient) -> None:
    body = _get(client, level="intern", have=csv(HAVE_16_OF_18))
    data = body["data"]
    assert data["level"] == "intern"
    assert data["cell_id"] == "vn.backend"  # Backend · Intern chỉ có 13 tin
    cell = body["meta"]["cells"][data["cell_id"]]
    assert cell["fallback_label"] and "13" in cell["fallback_label"]
    assert data["match"]["status"] == "ready"
    assert all(s["rate"]["cell_id"] == "vn.backend" for s in data["match"]["skills"])


def test_fr27_khong_o_nao_du_30_thi_not_enough_data(client: TestClient) -> None:
    body = _get(client, role="data_engineer", level="entry", skills="python,sql,airflow", have="python")
    match = body["data"]["match"]
    assert match["status"] == "not_enough_data"
    assert match["groups"] == []
    assert match["level"] is None
    assert match["cv_first"] == ["python"]  # kỹ năng hồ sơ có và tin nêu vẫn liệt kê dù không chia nhóm được
    for s in match["skills"]:
        assert s["group"] is None
        assert s["rate"]["display"] == "null_data" and s["rate"]["value"] is None
    assert {c: s["have"] for c, s in _by_code(match).items()}["python"] is True
    cell = body["meta"]["cells"][body["data"]["cell_id"]]
    assert cell["n_by_measure"]["skill_count"] < body["meta"]["thresholds"]["min_sample"]
    assert cell["fallback_label"]


def test_fr28_tin_khong_co_ky_nang_nhan_dien(client: TestClient) -> None:
    resp = client.get(URL, params={"role": "backend", "level": "junior", "have": "java"})
    assert resp.status_code == 200
    match = resp.json()["data"]["match"]
    assert match["status"] == "no_skills"
    assert match["skills"] == [] and match["groups"] == [] and match["level"] is None


def test_fr28_vai_tro_la_404(client: TestClient) -> None:
    resp = client.get(URL, params={**BASE, "role": "khong_ton_tai"})
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "unknown_cell"


def test_fr28_market_va_warnings_chua_xong_la_not_ready(client: TestClient) -> None:
    data = _get(client, have=csv(HAVE_16_OF_18))["data"]
    assert data["market"] == {"status": "not_ready", "cell_id": None, "years": None, "skill_count": None, "salary": None, "note": None}
    assert data["warnings"] == {
        "status": "not_ready",
        "checklist": [],
        "signs": [],
        "collected_match": None,
        "salary_note": None,
        "disclaimer": None,
    }


def test_fr28_doi_vai_tro_hay_cap_khong_can_dan_lai(client: TestClient) -> None:
    junior = _get(client, have=csv(HAVE_16_OF_18))["data"]
    entry = _get(client, level="entry", have=csv(HAVE_16_OF_18))["data"]
    assert junior["cell_id"] != entry["cell_id"]
    assert entry["match"]["level"] is not None
