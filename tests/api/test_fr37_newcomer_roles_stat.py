"""FR-37, AD-7, AD-17 — số thật của màn người mới (#145, #146), đọc từ `stat_cells` đã công bố.

#145: số tin entry-level của mỗi vai trò là `n` của ô toàn quốc ở nhóm cấp `entry` mà `aggregate` đã ghi
(Intern + Fresher + Junior), không cộng lại từ bảng tin.
#146: API trả mọi vai trò của config, kèm số entry-level, tỷ lệ và n, trong Envelope có ngày snapshot và nguồn.
"""

import json
from collections.abc import Iterator
from dataclasses import replace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, event, text

from haido_api.fake_market import FakeMarket
from haido_api.main import create_app
from haido_api.stat_market import StatMarket
from haido_core.config import load_rules
from haido_core.domain.display_policy import DisplayState
from tests.steps.conftest import S

PATH = "/api/v1/newcomer-roles"
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


def _client(engine: Engine, rules=RULES) -> TestClient:
    fake = FakeMarket()
    stat = StatMarket(engine_factory=lambda: engine, rules=rules)
    app = create_app({"city_shares": fake, "skill_rates": fake, "newcomer_roles": stat})
    return TestClient(app, raise_server_exceptions=False)


def _cell(conn, day: str, role: str, seniority: str, n: int, mix: dict[str, int], scope: str = "vn") -> None:
    conn.execute(
        text(
            "INSERT INTO haido.stat_cells (snapshot_id, role, branch, seniority, years, scope, n, seniority_mix, "
            "years_unstated, config_version) "
            "VALUES (:d, :r, 'all', :s, 'any', :sc, :n, CAST(:mix AS jsonb), 0, 'v')"
        ),
        {"d": day, "r": role, "s": seniority, "sc": scope, "n": n, "mix": json.dumps(mix)},
    )


def _seed(
    engine: Engine,
    roles: dict[str, dict[str, int]],
    *,
    day: str = S,
    status: str = "published",
    sources: tuple[str, ...] = ("itviec", "zalo"),
    failed: tuple[str, ...] = (),
) -> None:
    """Dựng một snapshot chỉ gồm hàng `stat_*`: mỗi vai trò là số tin theo cấp thô ở toàn quốc.

    Ghi như `aggregate`: ô `all` có n là tổng và mix mọi cấp; ô `entry` có n là Intern+Fresher+Junior và mix của ba cấp đó.
    Thêm một hàng `stat_city_shares` cấp `entry` để snapshot đọc được như ở bản đồ.
    """
    entry = RULES.level_groups["entry"]
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO haido.snapshots (snapshot_id, status, sources_failed) VALUES (:d, :s, :f)"),
            {"d": day, "s": status, "f": list(failed)},
        )
        for source in sources:
            conn.execute(
                text("INSERT INTO haido.stat_sources (snapshot_id, source) VALUES (:d, :s)"), {"d": day, "s": source}
            )
        for role, by_level in roles.items():
            mix_all = {lv: k for lv, k in by_level.items() if k > 0}
            mix_entry = {lv: k for lv, k in by_level.items() if lv in entry and k > 0}
            _cell(conn, day, role, "all", sum(by_level.values()), mix_all)
            _cell(conn, day, role, "entry", sum(mix_entry.values()), mix_entry)
            # một ô thành phố cùng cấp entry, để chắc phép đọc chỉ lấy ô toàn quốc
            _cell(conn, day, role, "entry", 999, {"junior": 999}, scope="ha_noi")
            conn.execute(
                text(
                    "INSERT INTO haido.stat_city_shares (snapshot_id, role, seniority, years, city, share) "
                    "VALUES (:d, :r, 'entry', 'any', 'ha_noi', 1.0)"
                ),
                {"d": day, "r": role},
            )


def _ok(client: TestClient) -> dict:
    resp = client.get(PATH)
    assert resp.status_code == 200, resp.text
    return resp.json()


def _rows(body: dict) -> dict[str, tuple[int, int, dict]]:
    cells = body["meta"]["cells"]
    return {
        r["role"]: (cells[r["entry_cell_id"]]["n"], cells[r["total_cell_id"]]["n"], r["share"])
        for r in body["data"]["rows"]
    }


# ---------------------------------------------------------------- #145: đọc từ cơ cấu cấp bậc toàn quốc


def test_fr37_so_tin_entry_level_la_n_cua_o_toan_quoc_nhom_entry(pg_engine: Engine) -> None:
    _seed(pg_engine, {"backend": {"intern": 4, "fresher": 6, "junior": 10, "mid": 20, "senior": 8, "unknown": 2}})
    body = _ok(_client(pg_engine))
    entry_n, total_n, share = _rows(body)["backend"]
    assert (entry_n, total_n) == (20, 50)
    assert body["meta"]["cells"]["vn.backend.entry"]["seniority_mix"] == {"intern": 4, "fresher": 6, "junior": 10}
    assert share["value"] == pytest.approx(0.4)
    assert body["data"]["levels"] == ["intern", "fresher", "junior"]


def test_fr37_doc_so_nguoi_moi_khong_cham_bang_tin(pg_engine: Engine, statements: list[str]) -> None:
    _seed(pg_engine, {"backend": {"junior": 40}})
    statements.clear()
    _ok(_client(pg_engine))
    touched = " ".join(statements).lower()
    assert statements, "phải có ít nhất một câu SQL"
    assert "job_" not in touched
    assert "public." not in touched
    assert "sum(" not in touched and "count(" not in touched


def test_fr37_doc_snapshot_cong_bo_moi_nhat_bo_qua_snapshot_dang_mo(pg_engine: Engine) -> None:
    _seed(pg_engine, {"backend": {"junior": 40}}, day=OLDER)
    _seed(pg_engine, {"backend": {"junior": 5}}, day=S, status="open")
    body = _ok(_client(pg_engine))
    assert body["meta"]["snapshot_date"] == OLDER
    assert _rows(body)["backend"][0] == 40


# ---------------------------------------------------------------- #146: mọi vai trò, số, tỷ lệ, n, Envelope


def test_fr37_moi_vai_tro_cua_config_deu_co_dong(pg_engine: Engine) -> None:
    _seed(pg_engine, {"backend": {"junior": 40}, "qa": {"senior": 35}})
    rows = _rows(_ok(_client(pg_engine)))
    assert set(rows) == set(RULES.roles)
    # vai trò vắng trong snapshot (chưa có tin nào): 0 tin, n = 0, không có tỷ lệ
    assert rows["game"][:2] == (0, 0)
    assert rows["game"][2]["display"] == DisplayState.NULL_DATA


def test_fr37_vai_tro_du_mau_khong_co_tin_entry_hien_0(pg_engine: Engine) -> None:
    _seed(pg_engine, {"qa": {"senior": 35}})
    entry_n, total_n, share = _rows(_ok(_client(pg_engine)))["qa"]
    assert (entry_n, total_n) == (0, 35)
    assert share["value"] == 0.0
    assert share["display"] == DisplayState.SHOWN


def test_fr37_vai_tro_duoi_30_tin_khong_co_ty_le_nhung_van_co_so(pg_engine: Engine) -> None:
    _seed(pg_engine, {"ui_ux": {"intern": 3, "mid": 9}})
    entry_n, total_n, share = _rows(_ok(_client(pg_engine)))["ui_ux"]
    assert (entry_n, total_n) == (3, 12)
    assert share["display"] == DisplayState.NULL_DATA
    assert share["value"] is None
    assert share["kind"] == "level_share" and share["cell_id"] == "vn.ui_ux"


def test_fr37_nguong_mau_lay_tu_config(pg_engine: Engine) -> None:
    _seed(pg_engine, {"ui_ux": {"intern": 3, "mid": 9}})
    rules = replace(RULES, min_sample=10)
    body = _ok(_client(pg_engine, rules))
    assert _rows(body)["ui_ux"][2]["display"] == DisplayState.SHOWN
    assert body["meta"]["thresholds"]["min_sample"] == 10


def test_fr37_thu_tu_dong_co_ty_le_truoc_roi_so_entry_giam_dan(pg_engine: Engine) -> None:
    _seed(
        pg_engine,
        {
            "backend": {"junior": 20, "mid": 30},  # 20 entry, có tỷ lệ
            "qa": {"junior": 35},  # 35 entry, có tỷ lệ
            "devops": {"junior": 20, "senior": 20},  # 20 entry, có tỷ lệ, cùng số với backend
            "ui_ux": {"intern": 25},  # 25 entry nhưng dưới 30 tin
            "mobile": {"mid": 40},  # 0 entry, có tỷ lệ
        },
    )
    order = [r["role"] for r in _ok(_client(pg_engine))["data"]["rows"]]
    shown = ["qa", "backend", "devops", "mobile"]
    assert order[: len(shown)] == shown
    assert order[len(shown)] == "ui_ux"
    rest = order[len(shown) + 1 :]
    assert rest == sorted(rest)  # các vai trò 0 tin, dưới ngưỡng, theo mã


def test_fr37_envelope_co_ngay_snapshot_nguon_va_nguon_loi(pg_engine: Engine) -> None:
    _seed(pg_engine, {"backend": {"junior": 40}}, status="partial", sources=("zalo", "itviec"), failed=("topdev",))
    meta = _ok(_client(pg_engine))["meta"]
    assert meta["snapshot_date"] == S
    assert meta["snapshot_status"] == "partial"
    assert meta["sources"] == ["itviec", "zalo"]
    assert meta["sources_failed"] == ["topdev"]


def test_fr37_chua_co_snapshot_doc_duoc_la_404(pg_engine: Engine) -> None:
    resp = _client(pg_engine).get(PATH)
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "unknown_cell"


# ---------------------------------------------------------------- #148: khóa thứ tự (#110 AC1, AC2) và ô hỏng


def test_fr37_148_moi_dong_co_ty_le_theo_n_rieng_va_thu_tu_la_bat_bien(pg_engine: Engine) -> None:
    """#110 AC1, AC2, AD-7: tỷ lệ mỗi dòng là entry / n của CHÍNH vai trò đó, không phải tổng n của mọi vai trò.

    Nhiều vai trò có n khác nhau, nên chia cho tổng n của cả bảng (hay cho n của vai trò khác) làm test đỏ. Cũng khóa
    thứ tự: mọi dòng `null_data` sau mọi dòng `shown` dù có nhiều entry hơn, cùng số entry thì theo mã.
    """
    _seed(
        pg_engine,
        {
            "qa": {"junior": 60, "mid": 40},  # 60 entry, n = 100
            "backend": {"junior": 40, "mid": 10},  # 40 entry, n = 50
            "devops": {"junior": 40, "mid": 80},  # 40 entry, n = 120, cùng số entry với backend
            "mobile": {"junior": 5, "mid": 30},  # 5 entry, n = 35: có tỷ lệ, ít entry hơn ui_ux
            "ui_ux": {"intern": 29},  # 29 entry, n = 29 dưới 30 tin: null_data
            "game": {"intern": 10, "mid": 5},  # 10 entry, null_data
            "embedded": {"mid": 4},  # 0 entry, null_data
        },
    )
    body = _ok(_client(pg_engine))
    rows = body["data"]["rows"]
    cells = body["meta"]["cells"]
    shown = [r for r in rows if r["share"]["display"] == DisplayState.SHOWN]
    own_n = [cells[r["total_cell_id"]]["n"] for r in shown]
    assert len(shown) >= 3 and len(set(own_n)) == len(own_n), "cần từ 3 vai trò có tỷ lệ với n khác nhau"
    expected = {"qa": (60, 100), "backend": (40, 50), "devops": (40, 120), "mobile": (5, 35)}
    for r in shown:
        entry_n, n = expected[r["role"]]
        assert cells[r["entry_cell_id"]]["n"] == entry_n
        assert cells[r["total_cell_id"]]["n"] == n
        assert r["share"]["cell_id"] == r["total_cell_id"]
        assert r["share"]["value"] == pytest.approx(entry_n / n), r["role"]
    kinds = [r["share"]["display"] for r in rows]
    first_null = kinds.index(DisplayState.NULL_DATA)
    assert all(k == DisplayState.SHOWN for k in kinds[:first_null])
    assert all(k == DisplayState.NULL_DATA for k in kinds[first_null:])
    key = [(-cells[r["entry_cell_id"]]["n"], r["role"]) for r in rows]
    assert key[:first_null] == sorted(key[:first_null])
    assert key[first_null:] == sorted(key[first_null:])
    assert [r["role"] for r in rows[:first_null]] == ["qa", "backend", "devops", "mobile"]
    assert [r["role"] for r in rows[first_null : first_null + 2]] == ["ui_ux", "game"]


def test_fr37_148_bien_nguong_mau_30_co_ty_le_29_null_data(pg_engine: Engine) -> None:
    """Biên của `min_sample` (30 trong config): n = 30 có tỷ lệ, n = 29 là null_data."""
    assert RULES.min_sample == 30
    _seed(pg_engine, {"backend": {"junior": 10, "mid": 20}, "qa": {"junior": 9, "mid": 20}})
    rows = _rows(StatMarket(engine_factory=lambda: pg_engine, rules=RULES).newcomer_roles().model_dump(mode="json"))
    assert rows["backend"][1] == 30
    assert rows["backend"][2]["display"] == DisplayState.SHOWN
    assert rows["backend"][2]["value"] == pytest.approx(10 / 30)
    assert rows["qa"][1] == 29
    assert rows["qa"][2]["display"] == DisplayState.NULL_DATA
    assert rows["qa"][2]["value"] is None


def _set_entry_n(engine: Engine, role: str, entry_n: int) -> None:
    with engine.begin() as conn:
        result = conn.execute(
            text(
                "UPDATE haido.stat_cells SET n = :n WHERE snapshot_id = :d AND role = :r "
                "AND scope = 'vn' AND seniority = 'entry'"
            ),
            {"n": entry_n, "d": S, "r": role},
        )
        assert result.rowcount == 1, f"phải sửa đúng một ô entry của {role}"


def test_fr37_ad17_o_hong_entry_lon_hon_n_thi_loi_noi_ro_vai_tro_va_hai_so(pg_engine: Engine) -> None:
    """Ô entry có n lớn hơn n của vai trò là dữ liệu hỏng: không trả tỷ lệ > 1, không cắt xuống 1."""
    _seed(pg_engine, {"backend": {"junior": 40, "mid": 10}, "qa": {"junior": 35}})
    _set_entry_n(pg_engine, "backend", 80)
    stat = StatMarket(engine_factory=lambda: pg_engine, rules=RULES)
    with pytest.raises(RuntimeError, match=r"backend.*80.*50|backend.*50.*80"):
        stat.newcomer_roles()


def test_fr37_ad17_o_hong_entry_lon_hon_n_la_500_envelope_chuan(pg_engine: Engine) -> None:
    _seed(pg_engine, {"backend": {"junior": 40, "mid": 10}})
    _set_entry_n(pg_engine, "backend", 80)
    resp = _client(pg_engine).get(PATH)
    assert resp.status_code == 500
    assert resp.json()["error"]["code"] == "internal_error"


def test_fr37_ad17_entry_bang_n_van_hop_le_tyle_bang_1(pg_engine: Engine) -> None:
    _seed(pg_engine, {"backend": {"junior": 40}})
    share = _rows(_ok(_client(pg_engine)))["backend"][2]
    assert share["value"] == 1.0


def test_fr37_ad17_o_hong_cung_bi_chan_khi_vai_tro_duoi_nguong_mau(pg_engine: Engine) -> None:
    """Dưới ngưỡng thì không tính tỷ lệ nên schema không bắt được; số entry > n vẫn phải bị chặn."""
    _seed(pg_engine, {"ui_ux": {"intern": 3, "mid": 9}})
    _set_entry_n(pg_engine, "ui_ux", 20)
    with pytest.raises(RuntimeError, match=r"ui_ux.*20.*12"):
        StatMarket(engine_factory=lambda: pg_engine, rules=RULES).newcomer_roles()
