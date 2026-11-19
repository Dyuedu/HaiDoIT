"""FR-19, AD-2, AD-7, AD-17 — tỷ lệ kỹ năng thật của một vai trò và cấp bậc (#151, #103, #106).

Số đọc từ `stat_skill_rates` và `stat_cells` của snapshot đọc được mới nhất. Ô được chọn bằng phép 2 (`select_cell`)
theo `n_scanned`; nhóm bằng phép 4 (`group_skills`) với θ của `config/rules.toml`. API không tổng hợp lại bảng tin.
"""

import json
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, event, text

from haido_api.fake_market import FakeMarket
from haido_api.main import create_app
from haido_api.stat_market import StatMarket
from haido_core.config import load_rules
from tests.steps.conftest import S

PATH = "/api/v1/skill-rates"
RULES = load_rules()
OLDER = "2026-04-30"


@pytest.fixture
def statements(pg_engine: Engine) -> Iterator[list[str]]:
    seen: list[str] = []

    def record(conn, cursor, statement, parameters, context, executemany) -> None:
        seen.append(statement)

    event.listen(pg_engine, "before_cursor_execute", record)
    yield seen
    event.remove(pg_engine, "before_cursor_execute", record)


def _client(engine: Engine) -> TestClient:
    fake = FakeMarket()
    stat = StatMarket(engine_factory=lambda: engine, rules=RULES)
    app = create_app({"city_shares": fake, "skill_rates": stat, "newcomer_roles": fake, "learning_path": fake, "skill_roles": fake})
    return TestClient(app, raise_server_exceptions=False)


def _snapshot(
    engine: Engine, day: str = S, *, status: str = "published", sources: tuple[str, ...] = ("itviec", "zalo")
) -> None:
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO haido.snapshots (snapshot_id, status, sources_failed) VALUES (:d, :s, '{}')"),
            {"d": day, "s": status},
        )
        for source in sources:
            conn.execute(text("INSERT INTO haido.stat_sources (snapshot_id, source) VALUES (:d, :s)"), {"d": day, "s": source})


def _cell(
    engine: Engine,
    role: str,
    level: str,
    n: int,
    scanned: int,
    rates: dict[str, int],
    *,
    mix: dict[str, int] | None = None,
    day: str = S,
    scope: str = "vn",
) -> None:
    """Một ô `stat_cells` và các hàng `stat_skill_rates` của nó. `rates` là skill -> n_with."""
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO haido.stat_cells (snapshot_id, role, branch, seniority, years, scope, n, seniority_mix, "
                "years_unstated, config_version) VALUES (:d, :r, 'all', :s, 'any', :sc, :n, CAST(:mix AS jsonb), 0, 'v')"
            ),
            {"d": day, "r": role, "s": level, "sc": scope, "n": n, "mix": json.dumps(mix or {})},
        )
        if scope != "vn":
            return
        for skill, with_ in rates.items():
            rate = with_ / scanned if scanned else 0.0
            conn.execute(
                text(
                    "INSERT INTO haido.stat_skill_rates (snapshot_id, role, branch, seniority, years, scope, skill, "
                    "n_with, n_scanned, rate, vocab_version) VALUES (:d, :r, 'all', :s, 'any', 'vn', :k, :w, :n, :x, 'seed-x')"
                ),
                {"d": day, "r": role, "s": level, "k": skill, "w": with_, "n": scanned, "x": rate},
            )


def _get(client: TestClient, role: str = "backend", level: str = "entry", have: str | None = None):
    params = {"role": role, "level": level}
    if have:
        params["have"] = have
    return client.get(PATH, params=params)


def _ok(client: TestClient, role: str = "backend", level: str = "entry", have: str | None = None) -> dict:
    resp = _get(client, role, level, have)
    assert resp.status_code == 200, resp.text
    return resp.json()


# 52 cụm đã quét: java 0.6 (core), sql 0.2 (common), git 0.1 (common, đúng θ), docker 0.05 (rare), rust 0 (rare)
GOOD = {"java": 36, "sql": 12, "git": 6, "docker": 3, "rust": 0}


def _good_entry(engine: Engine) -> None:
    _snapshot(engine)
    _cell(engine, "backend", "entry", 80, 60, {"java": 36, "sql": 12, "git": 6, "docker": 3, "rust": 0})
    _cell(engine, "backend", "all", 500, 400, {"java": 300, "sql": 100, "git": 10, "docker": 5, "rust": 0})


def test_fr19_o_du_mau_tra_core_common_theo_ty_le_giam_dan_roi_ma(pg_engine: Engine) -> None:
    _good_entry(pg_engine)
    body = _ok(_client(pg_engine))
    data = body["data"]
    assert data["role"] == "backend" and data["level"] == "entry"
    assert data["cell_id"] == "vn.backend.entry"
    # θ_core = 0.3, θ_common = 0.1: java core; sql 0.2 và git 0.1 common; docker (0.05) và rust (0) là rare, không có dòng
    assert [(r["skill"], r["group"]) for r in data["rows"]] == [("java", "core"), ("sql", "common"), ("git", "common")]
    assert [r["rate"]["value"] for r in data["rows"]] == [0.6, 0.2, 0.1]
    assert all(r["rate"]["kind"] == "skill_rate" and r["rate"]["display"] == "shown" for r in data["rows"])
    assert all(r["rate"]["cell_id"] == "vn.backend.entry" for r in data["rows"])
    assert data["core_size"] == 1 and data["have_core"] == 0


def test_fr19_hoa_ty_le_xep_theo_ma_ky_nang(pg_engine: Engine) -> None:
    _snapshot(pg_engine)
    _cell(pg_engine, "backend", "entry", 60, 60, {"sql": 30, "git": 30, "java": 30, "python": 18})
    rows = _ok(_client(pg_engine))["data"]["rows"]
    assert [r["skill"] for r in rows] == ["git", "java", "sql", "python"]


def test_ad17_meta_o_da_dung_co_n_cua_stat_cells_va_skill_count_la_n_scanned(pg_engine: Engine) -> None:
    _good_entry(pg_engine)
    body = _ok(_client(pg_engine))
    cell = body["meta"]["cells"]["vn.backend.entry"]
    assert cell["n"] == 80
    assert cell["n_by_measure"] == {"skill_count": 60}
    assert cell["insufficient_by_measure"] == {"skill_count": False}
    assert cell["fallback_label"] is None
    meta = body["meta"]
    assert meta["snapshot_date"] == S and meta["snapshot_status"] == "published"
    assert meta["sources"] == ["itviec", "zalo"]
    assert meta["thresholds"] == {"min_sample": 30, "theta_core": 0.3, "theta_common": 0.1, "theta_version": "theta-1"}
    assert meta["coverage_notes"][0]["code"] == "n_sources"


def test_fr19_ten_o_gom_cap_tho_va_all(pg_engine: Engine) -> None:
    _snapshot(pg_engine)
    _cell(pg_engine, "backend", "all", 500, 400, {"java": 300})
    _cell(pg_engine, "backend", "mid", 100, 90, {"java": 60})
    client = _client(pg_engine)
    assert _ok(client, level="all")["data"]["cell_id"] == "vn.backend"
    assert _ok(client, level="mid")["data"]["cell_id"] == "vn.backend.mid"


def test_fr19_ac2_cap_tho_thieu_mau_quay_ve_nhom_va_nhan_goi_ten_ca_hai_o(pg_engine: Engine) -> None:
    _snapshot(pg_engine)
    _cell(pg_engine, "backend", "fresher", 26, 26, {"java": 20, "sql": 5})
    _cell(pg_engine, "backend", "entry", 80, 52, {"java": 26, "sql": 13})
    _cell(pg_engine, "backend", "all", 500, 400, {"java": 300})
    body = _ok(_client(pg_engine), level="fresher")
    assert body["data"]["level"] == "fresher"
    assert body["data"]["cell_id"] == "vn.backend.entry"
    cell = body["meta"]["cells"]["vn.backend.entry"]
    assert cell["n"] == 80 and cell["n_by_measure"] == {"skill_count": 52}
    assert cell["fallback_label"] == (
        "Backend · Fresher chỉ có 26 tin đọc được kỹ năng (dưới 30), chưa đủ để tính riêng, "
        "nên số dưới đây lấy từ Backend · Entry (52 tin đọc được kỹ năng)."
    )
    assert [r["skill"] for r in body["data"]["rows"]] == ["java", "sql"]
    assert all(r["rate"]["display"] == "shown" for r in body["data"]["rows"])


def test_fr19_ac2_quay_ve_all_ghi_ty_le_mid_tro_len_cua_o_all(pg_engine: Engine) -> None:
    _snapshot(pg_engine)
    mix = {"intern": 10, "fresher": 20, "junior": 10, "mid": 40, "senior": 20}
    _cell(pg_engine, "backend", "fresher", 5, 5, {"java": 3})
    _cell(pg_engine, "backend", "entry", 12, 12, {"java": 6})
    _cell(pg_engine, "backend", "all", 100, 90, {"java": 45, "sql": 30}, mix=mix)
    body = _ok(_client(pg_engine), level="fresher")
    assert body["data"]["cell_id"] == "vn.backend"
    assert body["meta"]["cells"]["vn.backend"]["fallback_label"] == (
        "Backend · Fresher chỉ có 5 tin đọc được kỹ năng (dưới 30), chưa đủ để tính riêng, "
        "nên số dưới đây lấy từ Backend · mọi cấp (90 tin đọc được kỹ năng). Trong tập này 60% tin là Mid trở lên."
    )
    assert body["meta"]["cells"]["vn.backend"]["seniority_mix"] == mix


def test_ad17_quyet_dinh_theo_n_scanned_khong_theo_n_cua_o(pg_engine: Engine) -> None:
    # n = 100 qua ngưỡng, nhưng chỉ 12 cụm đã quét kỹ năng: ô entry không được dùng
    _snapshot(pg_engine)
    _cell(pg_engine, "backend", "entry", 100, 12, {"java": 10})
    _cell(pg_engine, "backend", "all", 500, 400, {"java": 300})
    body = _ok(_client(pg_engine))
    assert body["data"]["cell_id"] == "vn.backend"
    assert all(r["rate"]["display"] == "shown" for r in body["data"]["rows"])


def test_fr19_ac3_khong_tap_nao_du_30_thi_moi_ty_le_la_null_data(pg_engine: Engine) -> None:
    _snapshot(pg_engine)
    _cell(pg_engine, "backend", "entry", 20, 18, {"java": 9, "sql": 0, "git": 2})
    _cell(pg_engine, "backend", "all", 40, 25, {"python": 5, "java": 12, "sql": 0})
    body = _ok(_client(pg_engine), have="java")
    data = body["data"]
    assert data["cell_id"] == "vn.backend"
    # dòng: kỹ năng có n_with > 0 của ô cuối, theo mã (thứ tự không mang xếp hạng)
    assert [r["skill"] for r in data["rows"]] == ["java", "python"]
    for row in data["rows"]:
        assert row["rate"] == {"value": None, "kind": "skill_rate", "display": "null_data", "cell_id": "vn.backend"}
        assert row["group"] is None
    assert [r["have"] for r in data["rows"]] == [True, False]
    assert data["core_size"] is None and data["have_core"] is None
    cell = body["meta"]["cells"]["vn.backend"]
    assert cell["n"] == 40 and cell["n_by_measure"] == {"skill_count": 25}
    assert cell["insufficient_by_measure"] == {"skill_count": True}
    assert cell["fallback_label"] == (
        "Chưa có tập nào đủ 30 tin đọc được kỹ năng (Backend · Entry có 18 tin đọc được kỹ năng; "
        "Backend · mọi cấp có 25 tin đọc được kỹ năng), nên chưa đủ dữ liệu để hiện số."
    )


def test_fr19_co_have_tick_dong_va_dem_core(pg_engine: Engine) -> None:
    _snapshot(pg_engine)
    _cell(pg_engine, "backend", "entry", 100, 100, {"java": 60, "spring_boot": 40, "sql": 20, "git": 5})
    data = _ok(_client(pg_engine), have="java,sql,khong_co_trong_o")["data"]
    assert {r["skill"]: r["have"] for r in data["rows"]} == {"java": True, "spring_boot": False, "sql": True}
    assert data["core_size"] == 2 and data["have_core"] == 1


def test_fr19_vai_tro_khong_co_trong_config_la_404_unknown_cell(pg_engine: Engine) -> None:
    _good_entry(pg_engine)
    resp = _get(_client(pg_engine), role="java_backend")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "unknown_cell"


def test_fr19_vai_tro_khong_co_tin_nao_la_404_kem_ngay_snapshot(pg_engine: Engine) -> None:
    _good_entry(pg_engine)
    resp = _get(_client(pg_engine), role="game")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "unknown_cell"
    assert resp.json()["error"]["snapshot_date"] == S


def test_fr19_cap_khong_hop_le_van_la_422(pg_engine: Engine) -> None:
    _good_entry(pg_engine)
    assert _get(_client(pg_engine), level="khong_co").status_code == 422


def test_fr19_chua_co_snapshot_doc_duoc_la_404_khong_ngay(pg_engine: Engine) -> None:
    resp = _get(_client(pg_engine))
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "unknown_cell"
    assert resp.json()["error"]["snapshot_date"] is None


def test_fr19_snapshot_open_hoac_thieu_nguon_khong_doc_duoc(pg_engine: Engine) -> None:
    _snapshot(pg_engine, OLDER)
    _cell(pg_engine, "backend", "entry", 80, 60, GOOD, day=OLDER)
    _snapshot(pg_engine, "2026-05-02", status="open")
    _cell(pg_engine, "backend", "entry", 80, 60, {"python": 50}, day="2026-05-02")
    _snapshot(pg_engine, "2026-05-03", sources=())
    _cell(pg_engine, "backend", "entry", 80, 60, {"python": 50}, day="2026-05-03")
    body = _ok(_client(pg_engine))
    assert body["meta"]["snapshot_date"] == OLDER
    assert "java" in {r["skill"] for r in body["data"]["rows"]}


def test_fr19_snapshot_partial_doc_duoc_va_ghi_trang_thai(pg_engine: Engine) -> None:
    _snapshot(pg_engine, status="partial")
    _cell(pg_engine, "backend", "entry", 80, 60, GOOD)
    assert _ok(_client(pg_engine))["meta"]["snapshot_status"] == "partial"


def test_ad7_chi_doc_bang_stat_va_khong_tong_hop_trong_sql(pg_engine: Engine, statements: list[str]) -> None:
    # Đường đủ mẫu, quay về và 404: không đường nào đọc bảng tin hay tổng hợp trong SQL (đường không tập nào đủ: test sau).
    _good_entry(pg_engine)
    _cell(pg_engine, "backend", "mid", 10, 8, {"java": 4})
    client = _client(pg_engine)
    for role, level in (("backend", "fresher"), ("backend", "mid"), ("game", "entry"), ("java_backend", "entry")):
        statements.clear()
        resp = _get(client, role, level)
        assert resp.status_code in (200, 404), resp.text
        sql = " ".join(statements).lower()
        assert "job_" not in sql, (role, level)
        for banned in ("group by", "avg(", "count(", "sum(", "max(", "min(", "having", "percentile"):
            assert banned not in sql, (role, level, banned)
        if role == "backend":
            assert "stat_skill_rates" in sql and "stat_cells" in sql


def test_ad7_duong_khong_tap_nao_du_cung_chi_doc_bang_stat(pg_engine: Engine, statements: list[str]) -> None:
    _snapshot(pg_engine)
    _cell(pg_engine, "backend", "entry", 20, 18, {"java": 9})
    _cell(pg_engine, "backend", "all", 40, 25, {"java": 12})
    statements.clear()
    body = _ok(_client(pg_engine))
    assert body["meta"]["cells"]["vn.backend"]["insufficient_by_measure"] == {"skill_count": True}
    sql = " ".join(statements).lower()
    assert "stat_skill_rates" in sql and "job_" not in sql
    for banned in ("group by", "avg(", "count(", "sum(", "max(", "min(", "having", "percentile"):
        assert banned not in sql


def test_fr19_cung_tham_so_cung_ket_qua(pg_engine: Engine) -> None:
    _good_entry(pg_engine)
    client = _client(pg_engine)
    assert _ok(client, level="fresher") == _ok(client, level="fresher")


def test_fr19_ac3_o_cuoi_khong_co_ky_nang_nao_duoc_nhac_van_co_dong_de_man_hinh_doc_duoc(pg_engine: Engine) -> None:
    # Web coi `rows` rỗng là response hỏng, nên ô cuối không có kỹ năng nào được nhắc thì liệt kê mọi mã của ô, theo mã.
    _snapshot(pg_engine)
    _cell(pg_engine, "backend", "entry", 10, 8, {"java": 0, "sql": 0})
    _cell(pg_engine, "backend", "all", 20, 15, {"python": 0, "git": 0})
    data = _ok(_client(pg_engine))["data"]
    assert [r["skill"] for r in data["rows"]] == ["git", "python"]
    assert all(r["rate"]["display"] == "null_data" and r["group"] is None for r in data["rows"])


def test_fr19_o_co_trong_stat_cells_nhung_khong_co_hang_ty_le_la_404_kem_ngay(pg_engine: Engine) -> None:
    # Ô có tin (n > 0) nhưng không hàng `stat_skill_rates` nào cho vai trò này: không được trả "có 0 tin" và dòng rỗng.
    _snapshot(pg_engine)
    _cell(pg_engine, "frontend", "all", 300, 250, {"react": 150})
    _cell(pg_engine, "backend", "all", 100, 0, {})
    resp = _get(_client(pg_engine), role="backend", level="all")
    assert resp.status_code == 404
    error = resp.json()["error"]
    assert error["code"] == "unknown_cell" and error["snapshot_date"] == S
    assert S in error["message"] and "tỷ lệ kỹ năng" in error["message"]


def test_fr19_o_du_mau_nhung_moi_ky_nang_hiem_tra_dong_rong_va_core_size_0(pg_engine: Engine) -> None:
    # Hợp lệ: ô đủ mẫu mà mọi kỹ năng dưới θ_common (0.1) thì không dòng nào, `core_size = 0`, `have_core = 0`.
    _snapshot(pg_engine)
    _cell(pg_engine, "backend", "entry", 60, 60, {"docker": 3, "rust": 0})
    body = _ok(_client(pg_engine), have="docker")
    assert body["data"]["rows"] == []
    assert body["data"]["core_size"] == 0 and body["data"]["have_core"] == 0
    cell = body["meta"]["cells"]["vn.backend.entry"]
    assert cell["insufficient_by_measure"] == {"skill_count": False} and cell["fallback_label"] is None


def test_ad17_n_scanned_khac_nhau_trong_mot_o_la_loi_toan_ven_du_lieu_khong_chon_ngam(pg_engine: Engine) -> None:
    # #101 ghi cùng `n_scanned` ở mọi hàng của ô; hai giá trị khác nhau là dữ liệu hỏng, không được lặng lẽ chọn một.
    _snapshot(pg_engine)
    _cell(pg_engine, "backend", "entry", 80, 60, {"java": 36})
    with pg_engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO haido.stat_skill_rates (snapshot_id, role, branch, seniority, years, scope, skill, "
                "n_with, n_scanned, rate, vocab_version) VALUES (:d, 'backend', 'all', 'entry', 'any', 'vn', 'sql', "
                "1, 59, 0.02, 'seed-x')"
            ),
            {"d": S},
        )
    stat = StatMarket(engine_factory=lambda: pg_engine, rules=RULES)
    with pytest.raises(RuntimeError, match=r"backend.*entry.*59.*60"):
        stat.skill_rates(role="backend", level="entry")
