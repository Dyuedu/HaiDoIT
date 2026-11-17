"""FR-09, AD-7, AD-17 — tỷ lệ tin entry-level của từng vai trò có nhắc một kỹ năng, số thật (#168, #166, #103).

Số đọc từ `stat_skill_rates` và `stat_cells` của snapshot đọc được mới nhất; `n_scanned` của hàng entry là cỡ mẫu của phép
đo (`skill_count`), không phải `n` của ô. API không tổng hợp lại bảng tin.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

from haido_api.fake_market import FakeMarket
from haido_api.main import create_app
from haido_api.schemas.market import SkillRolesData
from haido_api.stat_market import StatMarket
from haido_core.config import load_rules
from haido_core.domain.envelope import Envelope
from tests.api.test_fr19_skill_rates_stat import OLDER, _cell, _snapshot, statements  # noqa: F401
from tests.steps.conftest import S

PATH = "/api/v1/skill-roles"
RULES = load_rules()
ROLES = tuple(RULES.roles)


def _client(engine: Engine) -> TestClient:
    fake = FakeMarket()
    stat = StatMarket(engine_factory=lambda: engine, rules=RULES)
    app = create_app(
        {"city_shares": fake, "skill_rates": fake, "newcomer_roles": fake, "learning_path": fake, "skill_roles": stat}
    )
    return TestClient(app, raise_server_exceptions=False)


def _get(client: TestClient, skill: str = "python"):
    return client.get(PATH, params={"skill": skill})


def _ok(client: TestClient, skill: str = "python") -> dict:
    resp = _get(client, skill)
    assert resp.status_code == 200, resp.text
    return resp.json()


def _entry(engine: Engine, role: str, n: int, scanned: int, with_: int, skill: str = "python", day: str = S, **kw) -> None:
    _cell(engine, role, "entry", n, scanned, {skill: with_}, day=day, **kw)


def _all_roles(engine: Engine, with_: int = 900, skill: str = "python", day: str = S) -> None:
    """Ô `role = all`, `seniority = all`: mọi cấp, mọi vai trò (nguồn của `mentioned`)."""
    _cell(engine, "all", "all", 5000, 4000, {skill: with_}, day=day)


def _order(body: dict) -> list[str]:
    return [r["role"] for r in body["data"]["rows"]]


def _by_role(body: dict) -> dict[str, dict]:
    return {r["role"]: r for r in body["data"]["rows"]}


def _seed_mixed(engine: Engine) -> None:
    _snapshot(engine)
    _all_roles(engine)
    _entry(engine, "backend", 80, 60, 30)  # 0.5
    _entry(engine, "frontend", 100, 80, 40)  # 0.5, n_scanned lớn hơn backend: hòa tỷ lệ thì chỉ mã xếp trước backend
    _entry(engine, "ai_ml", 90, 80, 72)  # 0.9
    _entry(engine, "mobile", 40, 40, 0)  # đủ mẫu, 0 tin nhắc
    _entry(engine, "devops", 20, 20, 15)  # dưới 30
    _entry(engine, "qa", 29, 29, 3)  # dưới 30, lớn hơn devops
    _entry(engine, "game", 43, 12, 6)  # n đủ mà quét kỹ năng chỉ 12


def test_fr09_ac1_xep_theo_ty_le_giam_dan_roi_ma_vai_tro(pg_engine: Engine) -> None:
    _seed_mixed(pg_engine)
    body = _ok(_client(pg_engine))
    shown = [r for r in body["data"]["rows"] if r["share"]["display"] == "shown"]
    assert [(r["role"], r["share"]["value"]) for r in shown] == [
        ("ai_ml", 0.9),
        ("backend", 0.5),
        ("frontend", 0.5),
        ("mobile", 0),
    ]
    assert [r["share"]["display"] for r in body["data"]["rows"]] == ["shown"] * 4 + ["null_data"] * (len(ROLES) - 4)
    assert all(r["share"]["kind"] == "skill_rate" for r in body["data"]["rows"])
    assert body["data"]["skill"] == {"code": "python", "name_en": "Python", "name_vi": "Python"}
    assert body["data"]["level"] == "entry" and body["data"]["levels"] == ["intern", "fresher", "junior"]


def test_fr09_ac2_vai_tro_duoi_30_la_null_data_x_tren_30_va_xep_theo_co_mau_giam_dan(pg_engine: Engine) -> None:
    _seed_mixed(pg_engine)
    body = _ok(_client(pg_engine))
    hidden = [r for r in body["data"]["rows"] if r["share"]["display"] == "null_data"]
    assert all(r["share"]["value"] is None for r in hidden)
    cells = body["meta"]["cells"]
    sizes = [cells[r["share"]["cell_id"]]["n_by_measure"]["skill_count"] for r in hidden]
    assert sizes == sorted(sizes, reverse=True)
    # qa 29, devops 20, game 12; các vai trò còn lại có 0 mẫu, theo mã
    assert [r["role"] for r in hidden][:3] == ["qa", "devops", "game"]
    tail = [r["role"] for r in hidden][3:]
    assert len(tail) == len(ROLES) - 7 and tail == sorted(tail)
    assert all(sizes[i + 3] == 0 for i in range(len(tail)))
    assert cells["vn.devops.entry"]["n_by_measure"] == {"skill_count": 20}
    assert cells["vn.devops.entry"]["insufficient_by_measure"] == {"skill_count": True}
    assert cells["vn.backend.entry"]["insufficient_by_measure"] == {"skill_count": False}


def test_fr09_ac2_n_du_nhung_quet_ky_nang_duoi_30_van_la_null_data_x_la_n_scanned(pg_engine: Engine) -> None:
    _seed_mixed(pg_engine)
    body = _ok(_client(pg_engine))
    assert _by_role(body)["game"]["share"]["display"] == "null_data"
    cell = body["meta"]["cells"]["vn.game.entry"]
    assert cell["n"] == 43 and cell["n_by_measure"] == {"skill_count": 12}


def test_fr09_vai_tro_khong_co_o_entry_la_n_0_null_data_va_van_co_dong(pg_engine: Engine) -> None:
    _seed_mixed(pg_engine)
    body = _ok(_client(pg_engine))
    assert sorted(_order(body)) == sorted(ROLES)
    row = _by_role(body)["security"]
    assert row["share"]["display"] == "null_data" and row["share"]["cell_id"] == "vn.security.entry"
    cell = body["meta"]["cells"]["vn.security.entry"]
    assert cell["n"] == 0 and cell["seniority_mix"] == {}
    assert cell["n_by_measure"] == {"skill_count": 0} and cell["insufficient_by_measure"] == {"skill_count": True}
    assert cell["fallback_label"] is None


def test_fr09_du_mau_va_khong_tin_nao_nhac_la_0_khong_phai_null(pg_engine: Engine) -> None:
    _seed_mixed(pg_engine)
    row = _by_role(_ok(_client(pg_engine)))["mobile"]
    assert row["share"]["value"] == 0 and row["share"]["display"] == "shown"


def test_fr09_o_entry_co_n_va_co_cau_cap_cua_stat_cells(pg_engine: Engine) -> None:
    _snapshot(pg_engine)
    _all_roles(pg_engine)
    _entry(pg_engine, "backend", 80, 60, 30, mix={"intern": 10, "fresher": 30, "junior": 40})
    body = _ok(_client(pg_engine))
    cell = body["meta"]["cells"]["vn.backend.entry"]
    assert cell["n"] == 80 and cell["seniority_mix"] == {"intern": 10, "fresher": 30, "junior": 40}
    assert cell["n_by_measure"] == {"skill_count": 60}
    meta = body["meta"]
    assert meta["snapshot_date"] == S and meta["snapshot_status"] == "published"
    assert meta["sources"] == ["itviec", "zalo"]
    assert meta["thresholds"] == {"min_sample": 30, "theta_core": 0.3, "theta_common": 0.1}
    assert meta["coverage_notes"][0]["code"] == "n_sources"
    assert set(meta["cells"]) == {f"vn.{r}.entry" for r in ROLES}


def test_fr09_dung_nguong_mau_n_scanned_bang_min_sample_la_shown_con_thieu_1_la_null_data(pg_engine: Engine) -> None:
    ms = RULES.min_sample
    _snapshot(pg_engine)
    _all_roles(pg_engine)
    _entry(pg_engine, "backend", ms, ms, 3)
    _entry(pg_engine, "frontend", ms, ms - 1, 3)
    by_role = _by_role(_ok(_client(pg_engine)))
    assert by_role["backend"]["share"]["display"] == "shown" and by_role["backend"]["share"]["value"] == 0.1
    assert by_role["frontend"]["share"]["display"] == "null_data" and by_role["frontend"]["share"]["value"] is None


def test_fr09_chi_dung_hang_cua_ky_nang_da_chon(pg_engine: Engine) -> None:
    _snapshot(pg_engine)
    _cell(pg_engine, "all", "all", 5000, 4000, {"python": 900, "java": 800})
    _cell(pg_engine, "backend", "entry", 80, 60, {"python": 30, "java": 60})
    client = _client(pg_engine)
    assert _by_role(_ok(client, "python"))["backend"]["share"]["value"] == 0.5
    assert _by_role(_ok(client, "java"))["backend"]["share"]["value"] == 1.0


def test_fr09_mentioned_true_khi_chi_cap_khac_entry_nhac(pg_engine: Engine) -> None:
    _snapshot(pg_engine)
    _all_roles(pg_engine, with_=40)
    _entry(pg_engine, "backend", 80, 60, 0)
    _cell(pg_engine, "backend", "mid", 100, 90, {"python": 40})  # nhắc ở cấp khác: không đổi kết quả entry
    body = _ok(_client(pg_engine))
    assert body["data"]["mentioned"] is True
    assert _by_role(body)["backend"]["share"]["value"] == 0


def test_fr09_mentioned_chi_lay_tu_hang_all_x_all_khong_lay_hang_all_x_entry(pg_engine: Engine) -> None:
    _snapshot(pg_engine)
    _all_roles(pg_engine, with_=40)
    _cell(pg_engine, "all", "entry", 900, 800, {"python": 0})  # hàng role=all, seniority=entry: không phải nguồn
    _entry(pg_engine, "backend", 80, 60, 0)
    assert _ok(_client(pg_engine))["data"]["mentioned"] is True


def test_fr09_mentioned_false_khi_khong_tin_nao_nhac(pg_engine: Engine) -> None:
    _snapshot(pg_engine)
    _all_roles(pg_engine, with_=0)
    _cell(pg_engine, "all", "entry", 900, 800, {"python": 0})
    _entry(pg_engine, "backend", 80, 60, 0)
    body = _ok(_client(pg_engine))
    assert body["data"]["mentioned"] is False
    assert _by_role(body)["backend"]["share"]["value"] == 0


def test_fr09_ky_nang_khong_co_hang_o_snapshot_la_404_unknown_cell_kem_ngay(pg_engine: Engine) -> None:
    _snapshot(pg_engine)
    _all_roles(pg_engine)  # chỉ python có hàng
    _entry(pg_engine, "backend", 80, 60, 30)
    resp = _get(_client(pg_engine), "java")
    assert resp.status_code == 404
    err = resp.json()["error"]
    assert err["code"] == "unknown_cell" and err["snapshot_date"] == S


def test_fr09_chua_co_snapshot_doc_duoc_la_404_khong_ngay(pg_engine: Engine) -> None:
    resp = _get(_client(pg_engine))
    assert resp.status_code == 404
    err = resp.json()["error"]
    assert err["code"] == "unknown_cell" and err["snapshot_date"] is None


def test_fr09_ma_ngoai_bo_tu_vung_la_404_unknown_skill_va_sai_dinh_dang_la_422(pg_engine: Engine) -> None:
    _snapshot(pg_engine)
    _all_roles(pg_engine)
    client = _client(pg_engine)
    resp = _get(client, "khong_co_ky_nang")
    assert resp.status_code == 404 and resp.json()["error"]["code"] == "unknown_skill"
    assert client.get(PATH, params={"skill": "Sai Dinh Dang"}).status_code == 422


def test_fr09_bo_snapshot_moi_khong_co_stat_sources(pg_engine: Engine) -> None:
    _snapshot(pg_engine, OLDER)
    _all_roles(pg_engine, day=OLDER)
    _entry(pg_engine, "backend", 80, 60, 30, day=OLDER)
    _snapshot(pg_engine, S, sources=())
    _all_roles(pg_engine, day=S)
    _entry(pg_engine, "backend", 80, 60, 6, day=S)
    body = _ok(_client(pg_engine))
    assert body["meta"]["snapshot_date"] == OLDER
    assert _by_role(body)["backend"]["share"]["value"] == 0.5


def test_fr09_chon_snapshot_doc_duoc_moi_nhat_bo_open_va_cu(pg_engine: Engine) -> None:
    _snapshot(pg_engine, OLDER)
    _all_roles(pg_engine, day=OLDER)
    _entry(pg_engine, "backend", 80, 60, 30, day=OLDER)
    _snapshot(pg_engine, "2026-12-31", status="open")
    _all_roles(pg_engine, day="2026-12-31")
    _entry(pg_engine, "backend", 80, 60, 6, day="2026-12-31")
    body = _ok(_client(pg_engine))
    assert body["meta"]["snapshot_date"] == OLDER
    assert _by_role(body)["backend"]["share"]["value"] == 0.5
    _snapshot(pg_engine, S)
    _all_roles(pg_engine)
    _entry(pg_engine, "backend", 80, 60, 45)
    body = _ok(_client(pg_engine))
    assert body["meta"]["snapshot_date"] == S
    assert _by_role(body)["backend"]["share"]["value"] == 0.75


def test_fr09_snapshot_partial_doc_duoc_va_ghi_trang_thai(pg_engine: Engine) -> None:
    _snapshot(pg_engine, status="partial")
    _all_roles(pg_engine)
    _entry(pg_engine, "backend", 80, 60, 30)
    with pg_engine.begin() as conn:
        conn.execute(text("UPDATE haido.snapshots SET sources_failed = ARRAY['jobsgo'] WHERE snapshot_id = :d"), {"d": S})
    meta = _ok(_client(pg_engine))["meta"]
    assert meta["snapshot_status"] == "partial"
    assert meta["sources_failed"] == ["jobsgo"]


def test_fr09_n_scanned_lon_hon_n_la_du_lieu_hong_500_va_ten_vai_tro(pg_engine: Engine) -> None:
    _snapshot(pg_engine)
    _all_roles(pg_engine)
    _entry(pg_engine, "backend", 40, 60, 30)
    resp = _get(_client(pg_engine))
    assert resp.status_code == 500
    market = StatMarket(engine_factory=lambda: pg_engine, rules=RULES)
    with pytest.raises(RuntimeError, match=S + r".*backend"):
        market.skill_roles(skill="python")


def test_fr09_vai_tro_co_n_with_o_entry_khi_all_x_all_la_0_la_du_lieu_hong_nem_loi_co_ngu_canh(pg_engine: Engine) -> None:
    _snapshot(pg_engine)
    _all_roles(pg_engine, with_=0)
    _entry(pg_engine, "backend", 80, 60, 30)
    resp = _get(_client(pg_engine))
    assert resp.status_code == 500
    market = StatMarket(engine_factory=lambda: pg_engine, rules=RULES)
    with pytest.raises(RuntimeError, match=S + r".*python.*backend"):
        market.skill_roles(skill="python")


def test_ad7_chi_doc_bang_stat_va_khong_tong_hop_trong_sql(pg_engine: Engine, statements: list[str]) -> None:  # noqa: F811
    _seed_mixed(pg_engine)
    client = _client(pg_engine)
    statements.clear()
    _ok(client)
    sql = " ".join(statements).lower()
    assert "stat_skill_rates" in sql and "stat_cells" in sql
    assert "job_" not in sql
    for banned in ("count(", "sum(", "avg(", "group by"):
        assert banned not in sql


def test_fr09_cung_tham_so_cung_ket_qua(pg_engine: Engine) -> None:
    _seed_mixed(pg_engine)
    client = _client(pg_engine)
    assert _ok(client) == _ok(client)


def test_ad17_response_qua_kiem_envelope_va_khop_schema_data(pg_engine: Engine) -> None:
    _seed_mixed(pg_engine)
    body = _ok(_client(pg_engine))
    env = Envelope[SkillRolesData].model_validate(body)
    assert [r.role for r in env.data.rows] == _order(body)
    assert env.data.mentioned is True
