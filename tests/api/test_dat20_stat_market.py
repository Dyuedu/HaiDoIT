"""#93 — `GET /api/v1/city-shares` đọc số đã công bố từ `stat_*`, không cộng lại từ bảng tin."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, event, text

from haido_api.fake_market import FakeMarket
from haido_api.main import create_app
from haido_api.routes.market import load_sources
from haido_api.schemas.market import CitySharesData
from haido_api.stat_market import StatMarket
from haido_core.config import load_rules
from haido_core.domain.display_policy import DisplayState
from haido_core.domain.envelope import Envelope
from tests.steps.conftest import S

CITIES = ["ha_noi", "ho_chi_minh", "da_nang", "other", "unknown"]
RULES = load_rules()


@pytest.fixture
def statements(pg_engine: Engine) -> Iterator[list[str]]:
    """Mọi câu SQL mà engine của test chạy từ lúc này, để kiểm API không đụng bảng tin."""
    seen: list[str] = []

    def record(conn, cursor, statement, parameters, context, executemany) -> None:
        seen.append(statement)

    event.listen(pg_engine, "before_cursor_execute", record)
    yield seen
    event.remove(pg_engine, "before_cursor_execute", record)


@pytest.fixture
def client(pg_engine: Engine) -> TestClient:
    app = create_app({"city_shares": StatMarket(engine_factory=lambda: pg_engine, rules=RULES), "skill_rates": FakeMarket(), "newcomer_roles": FakeMarket()})
    return TestClient(app, raise_server_exceptions=False)


def _seed(
    engine: Engine,
    day: str = S,
    status: str = "published",
    *,
    failed: tuple[str, ...] = (),
    sources: tuple[str, ...] = ("zalo", "itviec"),
    runs: tuple[str, ...] = (),
    roles: dict[str, dict[str, int]] | None = None,
    with_shares: bool = True,
) -> None:
    """Dựng thẳng hàng `stat_*` của một snapshot, không có tin nào trong bảng tin.

    `sources` là `stat_sources` (nguồn có tin được đếm); `runs` là lượt chạy ở S, mặc định không có.
    """
    roles = {"backend": {"ha_noi": 40, "da_nang": 3, "unknown": 7}} if roles is None else roles
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO haido.snapshots (snapshot_id, status, sources_failed) VALUES (:d, :s, :f)"),
            {"d": day, "s": status, "f": list(failed)},
        )
        for source in sources:
            conn.execute(
                text("INSERT INTO haido.stat_sources (snapshot_id, source) VALUES (:d, :s)"), {"d": day, "s": source}
            )
        for source in runs:
            conn.execute(
                text(
                    "INSERT INTO haido.pipeline_runs (snapshot_id, source, mode, success, seen_count) "
                    "VALUES (:d, :s, 'auto', :ok, 0)"
                ),
                {"d": day, "s": source, "ok": source not in failed},
            )
        for role, counts in roles.items():
            total = sum(counts.values())
            for scope in (*CITIES, "vn"):
                n = total if scope == "vn" else counts.get(scope, 0)
                conn.execute(
                    text(
                        "INSERT INTO haido.stat_cells VALUES (:d, :r, 'all', 'all', :sc, :n, CAST(:mix AS jsonb), 'v')"
                    ),
                    {"d": day, "r": role, "sc": scope, "n": n, "mix": f'{{"junior": {n}}}' if n else "{}"},
                )
                if scope != "vn" and with_shares:
                    share = n / total if total else (1.0 if scope == "unknown" else 0.0)
                    conn.execute(
                        text("INSERT INTO haido.stat_city_shares VALUES (:d, :r, :sc, :v)"),
                        {"d": day, "r": role, "sc": scope, "v": share},
                    )


def _get(client: TestClient, role: str = "backend"):
    return client.get("/api/v1/city-shares", params={"role": role})


def _ok(client: TestClient, role: str = "backend") -> dict:
    resp = _get(client, role)
    assert resp.status_code == 200, resp.text
    return resp.json()


# ---------------------------------------------------------------- AC: số có sẵn để web hiển thị


def test_dat20_moi_thanh_pho_co_ty_trong_va_n_cua_vai_tro_tren_toan_quoc(pg_engine: Engine, client: TestClient) -> None:
    _seed(pg_engine)
    body = _ok(client)
    data, meta = body["data"], body["meta"]
    assert data["role"] == "backend" and data["total_cell_id"] == "vn.backend"
    assert [r["city"] for r in data["rows"]] == CITIES
    assert [r["share"]["value"] for r in data["rows"]] == [0.8, 0.0, 0.06, 0.0, 0.14]
    assert [r["share"]["cell_id"] for r in data["rows"]] == [f"{c}.backend" for c in CITIES]
    assert all(r["share"]["kind"] == "composition_share" for r in data["rows"])
    assert meta["cells"]["vn.backend"]["n"] == 50
    assert meta["cells"]["ha_noi.backend"]["n"] == 40
    assert meta["cells"]["da_nang.backend"]["n"] == 3
    assert meta["cells"]["ha_noi.backend"]["seniority_mix"] == {"junior": 40}
    assert meta["cells"]["vn.backend"]["fallback_label"] is None
    assert set(meta["cells"]) == {"vn.backend", *(f"{c}.backend" for c in CITIES)}


def test_dat20_da_nang_luon_co_dong_mau_nho_van_co_so_va_danh_dau_mo(pg_engine: Engine, client: TestClient) -> None:
    _seed(pg_engine)
    rows = {r["city"]: r["share"] for r in _ok(client)["data"]["rows"]}
    assert rows["da_nang"]["value"] == pytest.approx(0.06)
    assert rows["da_nang"]["display"] == DisplayState.LOW_SAMPLE_SHOWN
    assert rows["ha_noi"]["display"] == DisplayState.SHOWN  # n = 40 >= 30
    assert rows["other"]["display"] == DisplayState.LOW_SAMPLE_SHOWN  # n = 0 vẫn có hàng, vẫn có số
    assert rows["other"]["value"] == 0.0


def test_dat20_display_chi_den_tu_suppression_for_voi_min_sample_cua_config(pg_engine: Engine) -> None:
    _seed(pg_engine)
    from dataclasses import replace

    strict = replace(RULES, min_sample=41)
    app = create_app({"city_shares": StatMarket(engine_factory=lambda: pg_engine, rules=strict), "skill_rates": FakeMarket(), "newcomer_roles": FakeMarket()})
    body = TestClient(app).get("/api/v1/city-shares", params={"role": "backend"}).json()
    assert body["meta"]["thresholds"]["min_sample"] == 41
    assert {r["city"]: r["share"]["display"] for r in body["data"]["rows"]}["ha_noi"] == DisplayState.LOW_SAMPLE_SHOWN


def test_dat20_nam_dong_cho_moi_vai_tro_ke_ca_all_va_tong_bang_1(pg_engine: Engine, client: TestClient) -> None:
    roles = {role: {"ha_noi": 2, "ho_chi_minh": 1, "unknown": 1} for role in ("all", *RULES.roles)}
    _seed(pg_engine, roles=roles)
    for role in roles:
        rows = _ok(client, role)["data"]["rows"]
        assert [r["city"] for r in rows] == CITIES
        assert sum(r["share"]["value"] for r in rows) == pytest.approx(1.0)


def test_dat20_response_la_envelope_hop_le(pg_engine: Engine, client: TestClient) -> None:
    _seed(pg_engine)
    Envelope[CitySharesData].model_validate(_ok(client))


# ---------------------------------------------------------------- AC: meta


def test_dat20_meta_co_ngay_snapshot_nguon_dang_bat_a_z_va_ghi_chu_so_nguon(pg_engine: Engine, client: TestClient) -> None:
    _seed(pg_engine, sources=("zalo", "itviec", "topcv", "momo"))
    meta = _ok(client)["meta"]
    assert meta["snapshot_date"] == S
    assert meta["snapshot_status"] == "published"
    assert meta["sources"] == ["itviec", "momo", "topcv", "zalo"]
    assert meta["sources_failed"] == []
    assert meta["thresholds"] == {"min_sample": 30, "theta_core": 0.3, "theta_common": 0.1}
    notes = {n["code"]: n["text"] for n in meta["coverage_notes"]}
    assert notes["n_sources"] == "Dữ liệu chỉ gồm tin tuyển dụng IT đăng online trên 4 nguồn."
    assert [n["code"] for n in meta["coverage_notes"]] == [n.code for n in RULES.coverage_notes]


def test_dat20_snapshot_partial_van_doc_duoc_kem_nguon_loi(pg_engine: Engine, client: TestClient) -> None:
    _seed(pg_engine, status="partial", failed=("zalo",))
    meta = _ok(client)["meta"]
    assert (meta["snapshot_status"], meta["sources_failed"]) == ("partial", ["zalo"])
    assert meta["sources"] == ["itviec", "zalo"]


def test_dat20_n_by_measure_va_insufficient_by_measure_la_rong(pg_engine: Engine, client: TestClient) -> None:
    _seed(pg_engine)
    cells = _ok(client)["meta"]["cells"]
    assert all(c["n_by_measure"] == {} and c["insufficient_by_measure"] == {} for c in cells.values())


# ---------------------------------------------------------------- AC: chọn snapshot


def test_dat20_doc_snapshot_published_hoac_partial_moi_nhat_co_stat_city_shares(pg_engine: Engine, client: TestClient) -> None:
    _seed(pg_engine, "2026-11-01", "published", roles={"backend": {"ha_noi": 1}})
    _seed(pg_engine, "2026-11-02", "partial", failed=("zalo",), roles={"backend": {"ha_noi": 2}})
    _seed(pg_engine, "2026-11-03", "open", roles={"backend": {"ha_noi": 3}})  # đang mở: chưa đọc được
    _seed(pg_engine, "2026-11-04", "published", roles={"backend": {"ha_noi": 4}}, with_shares=False)  # chưa tổng hợp
    meta = _ok(client)["meta"]
    assert meta["snapshot_date"] == "2026-11-02"
    assert meta["snapshot_status"] == "partial"
    assert meta["cells"]["vn.backend"]["n"] == 2


def test_dat20_snapshot_moi_hon_duoc_chot_thi_so_chuyen_theo(pg_engine: Engine, client: TestClient) -> None:
    _seed(pg_engine, "2026-11-01", roles={"backend": {"ha_noi": 1}})
    assert _ok(client)["meta"]["snapshot_date"] == "2026-11-01"
    _seed(pg_engine, "2026-11-02", roles={"backend": {"ha_noi": 5}})
    body = _ok(client)
    assert body["meta"]["snapshot_date"] == "2026-11-02"
    assert body["meta"]["cells"]["vn.backend"]["n"] == 5


# ---------------------------------------------------------------- AC: unknown_cell


def test_dat20_vai_tro_khong_co_tin_o_s_thi_404_unknown_cell_kem_ngay_snapshot(pg_engine: Engine, client: TestClient) -> None:
    _seed(pg_engine, roles={"backend": {"ha_noi": 5}, "qa": {}})
    for role in ("qa", "khong_co_vai_tro_nay"):
        resp = _get(client, role)
        assert resp.status_code == 404
        error = resp.json()["error"]
        assert error["code"] == "unknown_cell" and error["snapshot_date"] == S and error["message"]


def test_dat20_khong_co_snapshot_doc_duoc_thi_404_unknown_cell_khong_co_ngay(pg_engine: Engine, client: TestClient) -> None:
    resp = _get(client)
    assert resp.status_code == 404
    assert resp.json()["error"] == {
        "code": "unknown_cell",
        "message": resp.json()["error"]["message"],
        "snapshot_date": None,
    }
    _seed(pg_engine, "2026-11-03", "open")
    assert _get(client).json()["error"]["snapshot_date"] is None


# ---------------------------------------------------------------- AC: không cộng lại từ bảng tin


def test_dat20_api_khong_dung_den_bang_tin_va_van_tra_so_khi_bang_tin_trong(
    pg_engine: Engine, client: TestClient, statements: list[str]
) -> None:
    _seed(pg_engine)
    statements.clear()
    assert _get(client).status_code == 200
    assert statements, "API phải chạy truy vấn"
    for sql in statements:
        assert "job_" not in sql
        assert "stat_job_lifecycle" not in sql
        assert "group by" not in sql.lower() and "count(" not in sql.lower() and "sum(" not in sql.lower()
    assert any("stat_city_shares" in s for s in statements) and any("stat_cells" in s for s in statements)


# ---------------------------------------------------------------- AC: kết nối mở khi có yêu cầu, route giữ nguyên


def test_dat20_dung_nguon_khong_mo_ket_noi_va_khong_can_bien_moi_truong(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HAIDO_DATABASE_URL", raising=False)
    calls: list[int] = []

    def factory() -> Engine:
        calls.append(1)
        raise AssertionError("không được dựng engine lúc dựng nguồn")

    StatMarket()  # không đọc HAIDO_DATABASE_URL, không dựng engine
    StatMarket(engine_factory=factory)
    assert calls == []


def test_dat20_engine_chi_dung_o_yeu_cau_dau_tien_va_dung_lai(pg_engine: Engine) -> None:
    _seed(pg_engine)
    built: list[int] = []

    def factory() -> Engine:
        built.append(1)
        return pg_engine

    app = create_app({"city_shares": StatMarket(engine_factory=factory, rules=RULES), "skill_rates": FakeMarket(), "newcomer_roles": FakeMarket()})
    client = TestClient(app)
    assert built == []
    assert client.get("/api/v1/city-shares", params={"role": "backend"}).status_code == 200
    assert client.get("/api/v1/city-shares", params={"role": "backend"}).status_code == 200
    assert built == [1]


def test_dat20_thieu_url_luc_co_yeu_cau_thi_500_internal_error_khong_lo_chi_tiet(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HAIDO_DATABASE_URL", raising=False)
    app = create_app({"city_shares": StatMarket(rules=RULES), "skill_rates": FakeMarket(), "newcomer_roles": FakeMarket()})
    resp = TestClient(app, raise_server_exceptions=False).get("/api/v1/city-shares", params={"role": "backend"})
    assert resp.status_code == 500
    assert resp.json()["error"]["code"] == "internal_error"


def test_dat20_stat_la_mot_nguon_chon_duoc_qua_bien_moi_truong_cho_city_shares() -> None:
    sources = load_sources({"HAIDO_MARKET_SOURCE_CITY_SHARES": "stat"})
    assert isinstance(sources["city_shares"], StatMarket)
    assert isinstance(sources["skill_rates"], FakeMarket)
    assert isinstance(load_sources({})["city_shares"], FakeMarket)


def test_dat20_skill_rates_chua_co_so_that_nen_la_unknown_cell_khong_co_ngay(pg_engine: Engine) -> None:
    _seed(pg_engine)
    app = create_app({"city_shares": FakeMarket(), "skill_rates": StatMarket(engine_factory=lambda: pg_engine, rules=RULES), "newcomer_roles": FakeMarket()})
    resp = TestClient(app).get("/api/v1/skill-rates", params={"role": "backend", "level": "junior"})
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "unknown_cell"


# ---------------------------------------------------------------- bộ lọc theo snapshot và theo ô all/all


def test_dat20_ty_trong_va_nguon_chi_lay_cua_snapshot_dang_doc_khong_tron_ngay_cu(
    pg_engine: Engine, client: TestClient
) -> None:
    _seed(
        pg_engine,
        "2026-11-01",
        sources=("zalo", "itviec", "topcv"),
        roles={"backend": {"ha_noi": 10, "ho_chi_minh": 30}},
    )
    _seed(pg_engine, "2026-11-02", sources=("momo", "zalo"), roles={"backend": {"ha_noi": 60, "da_nang": 20}})
    body = _ok(client)
    meta = body["meta"]
    assert meta["snapshot_date"] == "2026-11-02"
    assert meta["sources"] == ["momo", "zalo"]
    notes = {n["code"]: n["text"] for n in meta["coverage_notes"]}
    assert notes["n_sources"] == "Dữ liệu chỉ gồm tin tuyển dụng IT đăng online trên 2 nguồn."
    shares = {r["city"]: r["share"]["value"] for r in body["data"]["rows"]}
    assert shares == pytest.approx({"ha_noi": 0.75, "ho_chi_minh": 0.0, "da_nang": 0.25, "other": 0.0, "unknown": 0.0})


def test_dat20_chi_dung_hang_stat_cells_all_all_khi_cung_pham_vi_co_hang_khac(
    pg_engine: Engine, client: TestClient
) -> None:
    _seed(pg_engine, roles={"backend": {"ha_noi": 40, "da_nang": 3, "unknown": 7}})
    with pg_engine.begin() as conn:
        for scope in (*CITIES, "vn"):
            conn.execute(
                text(
                    "INSERT INTO haido.stat_cells VALUES (:d, 'backend', 'be', 'junior', :sc, 999, "
                    "CAST('{\"junior\": 999}' AS jsonb), 'v')"
                ),
                {"d": S, "sc": scope},
            )
    cells = _ok(client)["meta"]["cells"]
    assert cells["vn.backend"]["n"] == 50
    assert cells["ha_noi.backend"]["n"] == 40
    assert cells["da_nang.backend"]["n"] == 3


# ---------------------------------------------------------------- #259: meta.sources đọc từ stat_sources theo khóa


def test_dat259_meta_sources_la_stat_sources_a_z_khong_phai_nguon_co_luot_chay_o_s(
    pg_engine: Engine, client: TestClient
) -> None:
    # topcv chạy tay mười ngày trước (có tin trong cửa sổ, không có lượt chạy ở S); zalo chạy ở S nhưng không có tin nào được đếm.
    _seed(pg_engine, sources=("topcv", "itviec"), runs=("zalo", "itviec"))
    meta = _ok(client)["meta"]
    assert meta["sources"] == ["itviec", "topcv"]
    notes = {n["code"]: n["text"] for n in meta["coverage_notes"]}
    assert notes["n_sources"] == "Dữ liệu chỉ gồm tin tuyển dụng IT đăng online trên 2 nguồn."


def test_dat259_n_trong_ghi_chu_bang_do_dai_danh_sach_nguon(pg_engine: Engine, client: TestClient) -> None:
    _seed(pg_engine, sources=("zalo", "momo", "topdev", "itviec", "topcv"))
    meta = _ok(client)["meta"]
    assert meta["sources"] == ["itviec", "momo", "topcv", "topdev", "zalo"]
    notes = {n["code"]: n["text"] for n in meta["coverage_notes"]}
    assert notes["n_sources"] == "Dữ liệu chỉ gồm tin tuyển dụng IT đăng online trên 5 nguồn."


def test_dat259_snapshot_khong_co_stat_sources_thi_bi_bo_qua_va_lui_ve_snapshot_cu_day_du(
    pg_engine: Engine, client: TestClient
) -> None:
    # snapshot mới hơn có số nhưng không có hàng stat_sources (aggregate trước migration 0004): web sẽ coi là không đọc được.
    _seed(pg_engine, "2026-11-01", sources=("itviec",), roles={"backend": {"ha_noi": 1}})
    _seed(pg_engine, "2026-11-02", sources=(), roles={"backend": {"ha_noi": 9}})
    meta = _ok(client)["meta"]
    assert meta["snapshot_date"] == "2026-11-01"
    assert meta["sources"] == ["itviec"]


def test_dat259_chi_co_snapshot_khong_co_stat_sources_thi_404_unknown_cell_khong_co_ngay(
    pg_engine: Engine, client: TestClient
) -> None:
    _seed(pg_engine, sources=())
    resp = _get(client)
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "unknown_cell"
    assert resp.json()["error"]["snapshot_date"] is None


def test_dat259_api_doc_stat_sources_theo_khoa_va_khong_dung_pipeline_runs(
    pg_engine: Engine, client: TestClient, statements: list[str]
) -> None:
    _seed(pg_engine, runs=("zalo",))
    statements.clear()
    assert _get(client).status_code == 200
    assert any("stat_sources" in s for s in statements)
    for sql in statements:
        assert "pipeline_runs" not in sql and "job_" not in sql
