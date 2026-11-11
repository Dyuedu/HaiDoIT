"""AD-17 — hai route số liệu thị trường, bản giả, hình lỗi và ảnh chụp OpenAPI.

Sinh lại `docs/api/openapi.json` sau khi đổi schema:
    HAIDO_UPDATE_OPENAPI=1 uv run pytest tests/api -q
"""

import json
import math
import os
from datetime import date
from pathlib import Path
from typing import Any

import pytest
from fastapi.routing import APIRoute, iter_route_contexts
from fastapi.testclient import TestClient
from pydantic import ValidationError

from haido_api.fake_market import FIXTURE, FakeMarket
from haido_api.main import app, create_app
from haido_api.market_source import UnknownCell
from haido_api.routes.market import SOURCE_ENV, load_sources
from haido_api.schemas.market import (
    CityShareRow,
    CitySharesData,
    SkillRateRow,
    SkillRatesData,
)
from haido_core.domain.display_policy import DisplayState, MeasureKind, suppression_for
from haido_core.domain.envelope import Envelope, Stat

ROOT = Path(__file__).resolve().parents[2]
OPENAPI_DOC = ROOT / "docs" / "api" / "openapi.json"

# Mỗi route dưới /api/v1 phải có ở đây một truy vấn hợp lệ. Thêm route mà quên thêm dòng
# này thì test_ad17_moi_route_tra_envelope đỏ.
SAMPLE_QUERY: dict[str, dict[str, str]] = {
    "/api/v1/city-shares": {"role": "ai_ml"},
    "/api/v1/skill-rates": {"role": "ai_ml", "level": "entry"},
    "/api/v1/newcomer-roles": {},
}

# Route không trả con số nào nên không dùng Envelope (AD-17 chỉ áp cho response chứa số).
# Test bên dưới kiểm response của chúng không có số. Thêm route vào đây phải có lý do.
NUMBERLESS_ROUTES: frozenset[str] = frozenset({"/api/v1/skills"})


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


def _get(client: TestClient, path: str, **params: str) -> dict[str, Any]:
    resp = client.get(path, params=params)
    assert resp.status_code == 200, resp.text
    return resp.json()


def _assert_error(resp: Any, status: int, code: str) -> dict[str, Any]:
    assert resp.status_code == status, resp.text
    body = resp.json()
    assert set(body) == {"error"}
    assert set(body["error"]) == {"code", "message", "snapshot_date"}
    assert body["error"]["code"] == code
    assert body["error"]["message"]
    return body["error"]


def _api_routes() -> dict[str, APIRoute]:
    """Route dưới /api/v1 theo đường dẫn đầy đủ. FastAPI 0.162 gắn router con một cách lười,
    nên phải duyệt qua `iter_route_contexts` thay vì `app.routes`."""
    return {
        ctx.path: ctx.original_route
        for ctx in iter_route_contexts(app.routes)
        if isinstance(ctx.original_route, APIRoute) and (ctx.path or "").startswith("/api/v1")
    }


# ---------------------------------------------------------------- AC: mọi route trả Envelope


def test_ad17_moi_route_tra_envelope(client: TestClient) -> None:
    all_routes = _api_routes()
    openapi_paths = {p for p in app.openapi()["paths"] if p.startswith("/api/v1")}
    assert set(all_routes) == openapi_paths
    routes = {p: r for p, r in all_routes.items() if p not in NUMBERLESS_ROUTES}
    assert set(routes) == set(SAMPLE_QUERY)
    for path in NUMBERLESS_ROUTES:
        assert path in all_routes, path
        assert _numbers(_get(client, path)) == [], f"{path} có số nhưng không dùng Envelope"
    for path, route in routes.items():
        model = route.response_model
        assert isinstance(model, type) and issubclass(model, Envelope), path
        assert model.__pydantic_generic_metadata__["args"], f"{path}: Envelope chưa gắn kiểu data"
        model.model_validate(_get(client, path, **SAMPLE_QUERY[path]))


def _numbers(node: Any) -> list[Any]:
    """Mọi số trong JSON, bỏ qua bool."""
    if isinstance(node, bool):
        return []
    if isinstance(node, int | float):
        return [node]
    if isinstance(node, dict):
        return [n for v in node.values() for n in _numbers(v)]
    if isinstance(node, list):
        return [n for v in node for n in _numbers(v)]
    return []


def _stats(node: Any) -> list[dict[str, Any]]:
    if isinstance(node, dict):
        if {"value", "kind", "display", "cell_id"} <= set(node):
            return [node]
        return [s for v in node.values() for s in _stats(v)]
    if isinstance(node, list):
        return [s for v in node for s in _stats(v)]
    return []


def _all_fixture_requests() -> list[tuple[str, dict[str, str]]]:
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    # #163: mỗi vai trò có `all` và `entry`; #280: khóa `<cấp>.y<N>` là cấp đó ở mốc số năm N.
    reqs = [
        ("/api/v1/city-shares", {"role": role, "level": key.split(".y")[0], "years": key.split(".y")[1]})
        if ".y" in key
        else ("/api/v1/city-shares", {"role": role, "level": key})
        for role, keys in raw["city_shares"].items()
        for key in keys
    ]
    reqs += [
        ("/api/v1/skill-rates", {"role": role, "level": level})
        for role, levels in raw["skill_rates"].items()
        for level in levels
    ]
    reqs.append(("/api/v1/newcomer-roles", {}))
    return reqs


@pytest.mark.parametrize(("path", "params"), _all_fixture_requests())
def test_ad17_display_chi_do_suppression_for_quyet(
    client: TestClient, path: str, params: dict[str, str]
) -> None:
    body = _get(client, path, **params)
    meta = body["meta"]
    min_sample = meta["thresholds"]["min_sample"]
    stats = _stats(body["data"])
    assert stats
    for stat in stats:
        n = meta["cells"][stat["cell_id"]]["n"]
        assert stat["display"] == suppression_for(stat["kind"], n, min_sample=min_sample)
    for cell in meta["cells"].values():
        for measure, n in cell["n_by_measure"].items():
            hidden = suppression_for(MeasureKind.PERCENTILE, n, min_sample=min_sample)
            assert cell["insufficient_by_measure"][measure] is (hidden is DisplayState.NULL_DATA)


# ---------------------------------------------------------------- I/O Matrix


def test_ad17_ty_trong_thanh_pho_du_mau_va_mau_nho(client: TestClient) -> None:
    body = _get(client, "/api/v1/city-shares", role="ai_ml")
    cells = body["meta"]["cells"]
    rows = {row["city"]: row["share"] for row in body["data"]["rows"]}

    assert cells[rows["ha_noi"]["cell_id"]]["n"] == 412
    assert rows["ha_noi"]["display"] == "shown"
    assert cells[rows["da_nang"]["cell_id"]]["n"] == 21
    assert rows["da_nang"]["display"] == "low_sample_shown"
    assert rows["da_nang"]["value"] is not None
    assert {"other", "unknown"} <= set(rows)
    assert math.isclose(math.fsum(s["value"] for s in rows.values()), 1.0, abs_tol=1e-9)

    total_n = cells[body["data"]["total_cell_id"]]["n"]
    for share in rows.values():  # không làm tròn: đúng bằng n của ô chia n toàn quốc
        assert share["value"] == cells[share["cell_id"]]["n"] / total_n


def test_ad17_quay_ve_o_rong(client: TestClient) -> None:
    body = _get(client, "/api/v1/skill-rates", role="java_backend", level="entry")
    cell = body["meta"]["cells"][body["data"]["cell_id"]]
    assert body["data"]["cell_id"] == "vn.backend.entry"
    assert cell["n"] == 52
    assert "Java Backend" in cell["fallback_label"] and "26" in cell["fallback_label"]
    assert cell["seniority_mix"] == {"intern": 13, "fresher": 7, "junior": 32}
    assert all(row["rate"]["display"] == "shown" for row in body["data"]["rows"])


def test_ad17_cung_o_chon_thang_thi_khong_co_nhan_quay_ve(client: TestClient) -> None:
    body = _get(client, "/api/v1/skill-rates", role="backend", level="entry")
    assert body["meta"]["cells"]["vn.backend.entry"]["fallback_label"] is None


def test_ad17_o_duoi_nguong_tra_null_data(client: TestClient) -> None:
    body = _get(client, "/api/v1/skill-rates", role="data_engineer", level="senior")
    assert body["meta"]["cells"][body["data"]["cell_id"]]["n"] == 18
    rows = body["data"]["rows"]
    assert rows
    for row in rows:
        assert row["rate"]["value"] is None
        assert row["rate"]["display"] == "null_data"
        assert row["group"] is None
    skills = [row["skill"] for row in rows]
    assert skills == sorted(skills), "thứ tự dòng không được lộ xếp hạng của tỷ lệ đã ẩn"


@pytest.mark.parametrize(
    ("path", "params"),
    [
        ("/api/v1/city-shares", {"role": "khong_ton_tai"}),
        ("/api/v1/skill-rates", {"role": "khong_ton_tai", "level": "entry"}),
        ("/api/v1/skill-rates", {"role": "ai_ml", "level": "khong_ton_tai"}),
    ],
)
def test_ad17_khong_co_o_tra_404(client: TestClient, path: str, params: dict[str, str]) -> None:
    error = _assert_error(client.get(path, params=params), 404, "unknown_cell")
    assert error["snapshot_date"] == "2026-11-03"
    for submitted in params.values():
        assert submitted not in error["message"]


def test_ad17_thieu_tham_so_tra_422_hinh_chuan(client: TestClient) -> None:
    resp = client.get("/api/v1/skill-rates", params={"role": "data_engineer"})
    error = _assert_error(resp, 422, "invalid_query")
    assert "detail" not in resp.json()
    assert "level" in error["message"]


def test_ad17_tham_so_sai_dinh_dang_tra_422(client: TestClient) -> None:
    resp = client.get("/api/v1/city-shares", params={"role": "Data AI"})
    error = _assert_error(resp, 422, "invalid_query")
    assert "Data AI" not in error["message"]


def test_ad17_loi_404_va_405_cua_starlette_cung_hinh_chuan(client: TestClient) -> None:
    _assert_error(client.get("/api/v1/khong-co"), 404, "not_found")
    resp = client.post("/api/v1/city-shares", params={"role": "ai_ml"})
    _assert_error(resp, 405, "method_not_allowed")
    assert resp.headers["allow"] == "GET"


# ---------------------------------------------------------------- nguồn dữ liệu


def test_ad17_nguong_doc_tu_fixture(tmp_path: Path) -> None:
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    raw["snapshot"]["thresholds"]["min_sample"] = 500
    fixture = tmp_path / "fake_market.json"
    fixture.write_text(json.dumps(raw), encoding="utf-8")

    env = FakeMarket(fixture).city_shares(role="ai_ml")
    shares = {row.city: row.share for row in env.data.rows}
    assert shares["ha_noi"].display is DisplayState.LOW_SAMPLE_SHOWN
    assert env.meta.thresholds.min_sample == 500


def test_ad17_chon_nguon_rieng_cho_tung_phep() -> None:
    fake = FakeMarket()

    class _CityOnly:
        def city_shares(self, *, role: str, level: str, years: str = "any") -> Any:
            raise UnknownCell("nguồn thử", snapshot_date=date(2026, 11, 4))

        def skill_rates(self, *, role: str, level: str) -> Any:
            raise AssertionError("skill_rates không được đi qua nguồn này")

    test_client = TestClient(create_app({"city_shares": _CityOnly(), "skill_rates": fake, "newcomer_roles": fake}))
    error = _assert_error(test_client.get("/api/v1/city-shares?role=ai_ml"), 404, "unknown_cell")
    assert error["snapshot_date"] == "2026-11-04"
    assert test_client.get("/api/v1/skill-rates?role=ai_ml&level=entry").status_code == 200


def test_ad17_bien_moi_truong_chon_nguon() -> None:
    sources = load_sources({})
    assert set(sources) == set(SOURCE_ENV)
    assert all(isinstance(s, FakeMarket) for s in sources.values())
    assert sources["city_shares"] is sources["skill_rates"]
    assert isinstance(load_sources({SOURCE_ENV["skill_rates"]: " fake "})["skill_rates"], FakeMarket)
    with pytest.raises(ValueError, match="HAIDO_MARKET_SOURCE_CITY_SHARES"):
        load_sources({SOURCE_ENV["city_shares"]: "postgres"})


def test_ad17_thieu_nguon_cho_mot_phep_la_loi_khoi_dong() -> None:
    with pytest.raises(ValueError, match="skill_rates"):
        create_app({"city_shares": FakeMarket()})


def test_ad17_nguon_tra_sai_hop_dong_thanh_loi_500() -> None:
    class _Broken:
        def city_shares(self, *, role: str, level: str, years: str = "any") -> Any:
            return {"data": {"role": role, "level": level, "total_cell_id": "vn.x", "rows": []}}

        def skill_rates(self, *, role: str, level: str) -> Any:
            raise RuntimeError("hỏng")

    broken = _Broken()
    test_client = TestClient(
        create_app({"city_shares": broken, "skill_rates": broken, "newcomer_roles": broken}), raise_server_exceptions=False
    )
    _assert_error(test_client.get("/api/v1/city-shares?role=ai_ml"), 500, "invalid_response")
    _assert_error(
        test_client.get("/api/v1/skill-rates?role=ai_ml&level=entry"), 500, "internal_error"
    )


def test_ad17_nguon_dung_model_sai_thanh_invalid_response() -> None:
    class _BuildsBadStat:
        def city_shares(self, *, role: str, level: str, years: str = "any") -> Any:
            return Stat(value=0.5, kind="skill_rate", display="low_sample_shown", cell_id="o")

        def skill_rates(self, *, role: str, level: str) -> Any:
            raise AssertionError("không gọi tới")

    source = _BuildsBadStat()
    test_client = TestClient(create_app({"city_shares": source, "skill_rates": source, "newcomer_roles": source}))
    _assert_error(test_client.get("/api/v1/city-shares?role=ai_ml"), 500, "invalid_response")


def test_ad17_instance_sua_bang_model_copy_van_bi_kiem_lai() -> None:
    fake = FakeMarket()

    class _CopiesWithGroup:
        def city_shares(self, *, role: str, level: str, years: str = "any") -> Any:
            return fake.city_shares(role=role, level=level, years=years)

        def skill_rates(self, *, role: str, level: str) -> Any:
            env = fake.skill_rates(role=role, level=level)
            rows = [row.model_copy(update={"group": "core"}) for row in env.data.rows]
            return env.model_copy(update={"data": env.data.model_copy(update={"rows": rows})})

    source = _CopiesWithGroup()
    test_client = TestClient(create_app({"city_shares": source, "skill_rates": source, "newcomer_roles": source}))
    resp = test_client.get("/api/v1/skill-rates?role=data_engineer&level=senior")
    _assert_error(resp, 500, "invalid_response")


# ---------------------------------------------------------------- validator riêng của route


def _s(value: float | None, display: str, cell_id: str, kind: str) -> dict[str, Any]:
    return {"value": value, "kind": kind, "display": display, "cell_id": cell_id}


def _share(city: str, value: float | None, display: str = "shown") -> dict[str, Any]:
    return {"city": city, "share": _s(value, display, f"{city}.r", "composition_share")}


def _rate(cell_id: str = "vn.r", display: str = "shown", group: str | None = "core") -> dict:
    value = None if display == "null_data" else 0.5
    return {"skill": "java", "rate": _s(value, display, cell_id, "skill_rate"), "group": group}


def test_ad17_share_phai_la_composition_share() -> None:
    with pytest.raises(ValidationError, match="share phải là composition_share"):
        CityShareRow.model_validate({"city": "ha_noi", "share": _s(0.5, "shown", "o", "skill_rate")})


@pytest.mark.parametrize(
    ("rows", "match"),
    [
        ([_share("ha_noi", 0.5), _share("da_nang", 0.4)], "Tổng tỷ trọng phải bằng 1"),
        ([], "rows"),
        ([_share("ha_noi", 0.5), _share("ha_noi", 0.5)], "Mã thành phố bị trùng: ha_noi"),
        (
            [_share("ha_noi", 1.0), _share("da_nang", None, display="null_data")],
            "Tỷ trọng phải có giá trị, thiếu ở: da_nang",
        ),
    ],
    ids=["tong_khac_1", "rong", "trung_city", "share_null"],
)
def test_ad17_city_shares_data_sai_la_loi(rows: list[dict], match: str) -> None:
    with pytest.raises(ValidationError, match=match):
        CitySharesData.model_validate({"role": "r", "level": "all", "total_cell_id": "vn.r", "rows": rows})


def test_ad17_rate_phai_la_skill_rate() -> None:
    row = _rate()
    row["rate"]["kind"] = "percentile"
    with pytest.raises(ValidationError, match="rate phải là skill_rate"):
        SkillRateRow.model_validate(row)


def test_ad17_null_data_khong_co_group() -> None:
    with pytest.raises(ValidationError, match="group phải là null"):
        SkillRateRow.model_validate(_rate(display="null_data", group="core"))


def test_ad17_rate_hien_thi_phai_co_group() -> None:
    with pytest.raises(ValidationError, match="group phải có"):
        SkillRateRow.model_validate(_rate(group=None))


def test_ad17_moi_rate_thuoc_o_cua_data() -> None:
    body = {"role": "r", "level": "l", "cell_id": "vn.r", "rows": [_rate(), _rate("vn.khac")]}
    with pytest.raises(ValidationError, match="có ô lạ: vn.khac"):
        SkillRatesData.model_validate(body)


@pytest.mark.determinism
def test_ad17_ban_gia_tat_dinh(client: TestClient) -> None:
    for path, params in _all_fixture_requests():
        assert client.get(path, params=params).content == client.get(path, params=params).content


# ---------------------------------------------------------------- AC: ảnh chụp OpenAPI


def test_ad17_openapi_da_commit_khop_voi_code() -> None:
    current = json.loads(json.dumps(app.openapi(), ensure_ascii=False))
    if os.environ.get("HAIDO_UPDATE_OPENAPI") == "1":
        OPENAPI_DOC.write_text(
            json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
    assert OPENAPI_DOC.exists(), "Chưa có docs/api/openapi.json. Chạy: HAIDO_UPDATE_OPENAPI=1 uv run pytest tests/api"
    committed = json.loads(OPENAPI_DOC.read_text(encoding="utf-8"))
    assert committed == current, (
        "docs/api/openapi.json lệch với schema trong code. "
        "Sinh lại: HAIDO_UPDATE_OPENAPI=1 uv run pytest tests/api, rồi commit file."
    )
