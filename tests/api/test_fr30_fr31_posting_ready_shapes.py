"""FR-30, FR-31, AD-10, AD-17, AD-26 — hình `ready` của `market` và `warnings` ở `GET /api/v1/posting-check` (#230, vòng review).

API giả còn `not_ready` tới #240–#246, nhưng hợp đồng đã chốt phải mang được mọi issue sau mà chỉ thêm, không đổi: test này kiểm
hình `ready` bằng hai ví dụ viết tay (`posting_examples.py`) và các kiểu sai, mỗi kiểu phải bị schema từ chối.
"""

import copy
import json
from collections.abc import Callable
from typing import Any, get_args

import pytest
from fastapi.testclient import TestClient
from posting_examples import NAMES, ready_example, stat
from pydantic import ValidationError

from haido_api.main import app
from haido_api.schemas.posting import (
    CHECKLIST_CODES,
    MARKET_MEASURE_OF,
    NOT_EVALUABLE_REASONS,
    SIGN_ACTION,
    SIGN_CODES,
    PostingCheckData,
    PostingMarket,
    PostingSalaryComparison,
    PostingWarnings,
)
from haido_core.domain.envelope import Envelope

BANNED = ["lừa đảo", "tin giả", "tin ma", "đừng học", "bỏ qua một kỹ năng"]  # FR-25/31/47


def _validate(body: dict[str, Any]) -> Envelope[PostingCheckData]:
    return Envelope[PostingCheckData].model_validate(body)


@pytest.mark.parametrize("name", NAMES)
def test_fr30_vi_du_ready_hop_le_voi_envelope_ke_ca_meta(name: str) -> None:
    body = ready_example(name)
    parsed = _validate(body)
    assert parsed.data.market.status == "ready" and parsed.data.warnings.status == "ready"
    assert json.loads(parsed.model_dump_json()) == body  # khứ hồi: schema không thêm, không bớt trường nào


def test_fr30_market_not_ready_la_null_het_ke_ca_cell_id() -> None:
    market = TestClient(app).get(
        "/api/v1/posting-check", params={"role": "backend", "level": "junior", "skills": "java"}
    ).json()["data"]["market"]
    assert market == {"status": "not_ready", "cell_id": None, "years": None, "skill_count": None, "salary": None, "note": None}


def test_fr31_warnings_not_ready_la_rong_va_khong_co_cau_co_dinh() -> None:
    warnings = TestClient(app).get(
        "/api/v1/posting-check", params={"role": "backend", "level": "junior", "skills": "java"}
    ).json()["data"]["warnings"]
    assert warnings == {
        "status": "not_ready",
        "checklist": [],
        "signs": [],
        "collected_match": None,
        "salary_note": None,
        "disclaimer": None,
    }


# ------------------------------------------------------------------------------------------------ FR-30: market


def test_fr30_mau_so_x_tren_30_lay_tu_o_cua_market_va_dem_dung_tung_thuoc_do() -> None:
    """"chưa đủ dữ liệu (X/30 ...)": X là `n_by_measure` của ô `market.cell_id`, theo thước của chính trường (FR-30)."""
    assert MARKET_MEASURE_OF == {"years": "experience_years", "skill_count": "skill_count", "salary": "salary"}
    body = ready_example("sparse")
    market = body["data"]["market"]
    cell = body["meta"]["cells"][market["cell_id"]]
    assert market["years"]["state"] == "not_enough_data"
    assert cell["n_by_measure"]["experience_years"] == 24 and cell["insufficient_by_measure"]["experience_years"] is True
    assert cell["n"] == 32 != cell["n_by_measure"]["experience_years"]  # không phải n của ô


def test_fr30_market_cell_id_co_the_khac_cell_id_cua_match() -> None:
    body = ready_example("sparse")
    body["data"]["market"] = _market_on(body, "vn.backend")
    body["meta"]["cells"]["vn.backend"] = ready_example("full")["meta"]["cells"]["vn.backend"]
    assert body["data"]["market"]["cell_id"] != body["data"]["cell_id"]
    _validate(body)  # mỗi mục tự trỏ ô của mình; X/30 theo ô của `market`, không theo ô của `match`


def _market_on(body: dict[str, Any], cell: str) -> dict[str, Any]:
    market = copy.deepcopy(ready_example("full")["data"]["market"])
    assert market["cell_id"] == cell
    return market


def _set(path: list[Any], value: Any) -> Callable[[dict[str, Any]], None]:
    def apply(body: dict[str, Any]) -> None:
        node: Any = body
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = value

    return apply


M = ["data", "market"]
W = ["data", "warnings"]


def _sign_at(body: dict[str, Any], code: str) -> dict[str, Any]:
    return next(s for s in body["data"]["warnings"]["signs"] if s["code"] == code)


def _drop_sign(code: str) -> Callable[[dict[str, Any]], None]:
    def apply(body: dict[str, Any]) -> None:
        body["data"]["warnings"]["signs"] = [s for s in body["data"]["warnings"]["signs"] if s["code"] != code]

    return apply


def _swap_signs(body: dict[str, Any]) -> None:
    signs = body["data"]["warnings"]["signs"]
    signs[0], signs[1] = signs[1], signs[0]


def _edit_sign(target: str, **patch: Any) -> Callable[[dict[str, Any]], None]:
    def apply(body: dict[str, Any]) -> None:
        _sign_at(body, target).update(patch)

    return apply


def _edit_fact(target: str, **patch: Any) -> Callable[[dict[str, Any]], None]:
    def apply(body: dict[str, Any]) -> None:
        _sign_at(body, target)["fact"].update(patch)

    return apply


# (tên ví dụ, cách làm sai, lý do). Mỗi dòng phải bị `Envelope[PostingCheckData]` từ chối.
BAD_MARKET: list[tuple[str, Callable[[dict[str, Any]], None], str]] = [
    ("full", _set([*M, "cell_id"], None), "ready thì cell_id có giá trị"),
    ("full", _set([*M, "cell_id"], "khong.co.o"), "cell_id không có trong meta.cells"),
    ("full", _set([*M, "years"], None), "ready thì đủ ba mục"),
    ("full", _set([*M, "note"], None), "ready thì có câu ghi chú cố định"),
    ("full", _set([*M, "note"], "So sánh chỉ để tham khảo"), "câu ghi chú của market là mã cố định, không phải chữ tự do"),
    ("full", lambda b: b["data"]["market"]["years"]["percentile"].update(cell_id="vn.backend.junior"), "Stat khác ô của market"),
    ("full", lambda b: b["data"]["market"]["years"].update(ci_low=stat(50.0, "vn.backend"), ci_high=stat(70.0, "vn.backend")), "n = 110 từ 100: không có khoảng tin cậy"),
    ("full", lambda b: b["data"]["market"]["skill_count"].update(state="not_enough_data", percentile=stat(None, "vn.backend")), "n = 157 đủ mẫu thì không được not_enough_data"),
    ("sparse", lambda b: b["data"]["market"]["years"].update(state="compared", percentile=stat(50.0, "vn.backend.junior")), "n = 24 dưới 30 thì không thể compared"),
    ("sparse", lambda b: b["data"]["market"]["skill_count"].update(ci_low=None, ci_high=None), "30 <= n < 100 phải có khoảng tin cậy"),
    ("sparse", lambda b: b["data"]["market"]["skill_count"].update(ci_high=None), "khoảng tin cậy đi cặp"),
    ("sparse", lambda b: b["data"]["market"]["skill_count"].update(ci_low=stat(45.0, "vn.backend.junior")), "ci_low phải ≤ phân vị"),
    ("sparse", lambda b: b["data"]["market"]["skill_count"].update(ci_high=stat(30.0, "vn.backend.junior")), "ci_high phải ≥ phân vị"),
    ("sparse", lambda b: b["data"]["market"]["years"].update(ci_low=stat(1.0, "vn.backend.junior"), ci_high=stat(2.0, "vn.backend.junior")), "not_enough_data thì không có khoảng tin cậy"),
    ("sparse", lambda b: b["data"]["market"]["skill_count"]["percentile"].update(value=140.0), "phân vị vượt 100"),
    ("sparse", lambda b: b["data"]["market"]["skill_count"]["percentile"].update(kind="skill_rate", value=0.4), "phân vị phải có kind percentile"),
    ("sparse", lambda b: b["data"]["market"]["skill_count"].update(state="not_stated"), "not_stated chỉ cho số năm"),
    ("full", lambda b: b["data"]["market"]["salary"].update(converted=None), "compared thì có giá trị quy đổi"),
    ("full", lambda b: b["data"]["market"]["salary"].update(position=None), "compared thì có vị trí"),
    ("full", lambda b: b["data"]["market"]["salary"].update(low=None), "compared thì có P25"),
    ("full", lambda b: b["data"]["market"]["salary"].update(note="salary_not_stated"), "compared thì không có câu trung tính"),
    ("full", lambda b: b["data"]["market"]["salary"].update(low=stat(30_000_000.0, "vn.backend")), "P25 không được lớn hơn P75"),
    ("full", lambda b: b["data"]["market"]["salary"]["converted"].update(min_vnd_month=10_000_000), "min quy đổi lớn hơn max"),
    ("full", lambda b: b["data"]["market"]["salary"]["converted"].update(min_vnd_month=None, max_vnd_month=None), "quy đổi phải có min hoặc max"),
    ("full", lambda b: b["data"]["market"]["salary"]["converted"]["fx"].update(rate=0), "tỷ giá phải dương"),
    ("full", lambda b: b["data"]["market"]["salary"]["converted"]["fx"].update(unit="usd_per_vnd"), "đơn vị tỷ giá là tập đóng"),
    ("full", lambda b: b["data"]["market"]["salary"]["converted"]["fx"].update(fx_version=""), "fx_version không được rỗng"),
    ("full", lambda b: b["data"]["market"]["salary"].update(position="beside"), "vị trí là tập đóng"),
    ("full", lambda b: b["data"]["market"]["salary"].update(state="not_numeric"), "not_numeric thì không có số"),
    ("sparse", lambda b: b["data"]["market"]["salary"].update(note=None), "not_stated phải có câu trung tính"),
    ("sparse", lambda b: b["data"]["market"]["salary"].update(position="within"), "not_stated thì không có vị trí"),
    ("sparse", lambda b: b["data"]["market"]["salary"].update(converted={"min_vnd_month": 1, "max_vnd_month": 2, "fx": None}), "not_stated thì không có quy đổi"),
    ("sparse", lambda b: b["data"]["market"]["salary"].update(note="khac"), "câu trung tính là mã cố định"),
    ("sparse", lambda b: b["data"]["market"].update(salary={"state": "waiting", "position": None, "low": None, "high": None, "converted": None, "note": None}), "trạng thái ngoài tập đóng"),
]


@pytest.mark.parametrize(("name", "mutate", "why"), BAD_MARKET, ids=[w for _, _, w in BAD_MARKET])
def test_fr30_market_sai_hinh_bi_tu_choi(name: str, mutate: Callable[[dict[str, Any]], None], why: str) -> None:
    body = ready_example(name)
    _validate(body)
    mutate(body)
    with pytest.raises(ValidationError):
        _validate(body)


def test_fr30_luong_co_bon_trang_thai_va_khong_con_not_comparable() -> None:
    states = get_args(PostingSalaryComparison.model_fields["state"].annotation)
    assert set(states) == {"compared", "not_enough_data", "not_stated", "not_numeric"}  # quy đổi lo cả USD và theo năm


def test_fr30_not_numeric_va_not_enough_data_hop_le() -> None:
    body = ready_example("sparse")
    body["data"]["market"]["salary"] = {
        "state": "not_numeric", "position": None, "low": None, "high": None, "converted": None, "note": None
    }
    _validate(body)
    body["data"]["market"]["salary"] = {
        "state": "not_enough_data",
        "position": None,
        "low": stat(None, "vn.backend.junior"),
        "high": stat(None, "vn.backend.junior"),
        "converted": {"min_vnd_month": 10_000_000, "max_vnd_month": 18_000_000, "fx": None},
        "note": None,
    }
    _validate(body)  # n lương = 9 < 30: "chưa đủ dữ liệu (9/30 tin có lương)"; giá trị quy đổi vẫn hiện để màn nói lương của tin
    body["data"]["market"]["years"] = {"state": "not_stated", "percentile": None, "ci_low": None, "ci_high": None}
    _validate(body)  # tin không ghi số năm


def test_fr30_salary_not_enough_data_nhung_du_mau_la_sai() -> None:
    body = ready_example("full")
    body["data"]["market"]["salary"].update(state="not_enough_data", position=None)
    body["data"]["market"]["salary"]["low"] = stat(None, "vn.backend")
    body["data"]["market"]["salary"]["high"] = stat(None, "vn.backend")
    with pytest.raises(ValidationError):  # n lương = 35 đủ mẫu
        _validate(body)


def test_fr30_rang_buoc_giua_hai_ca_sparse_va_full_khong_dung_chung_trang_thai() -> None:
    full, sparse = ready_example("full")["data"]["market"], ready_example("sparse")["data"]["market"]
    assert full["salary"]["converted"]["fx"]["unit"] == "vnd_per_usd"
    assert sparse["skill_count"]["ci_low"] is not None and full["skill_count"]["ci_low"] is None


# ----------------------------------------------------------------------------------------------- FR-31: warnings


def test_fr31_bay_dau_hieu_d1_den_d7_dung_thu_tu_va_tung_dau_hieu_co_goi_y() -> None:
    assert SIGN_CODES == (
        "d1_wide_skills", "d2_specific_heavy", "d3_high_req_low_pay", "d4_reposted",
        "d5_unusual_contact", "d6_fee_first", "d7_no_company",
    )  # fmt: skip
    assert set(SIGN_ACTION) == set(SIGN_CODES) and len(set(SIGN_ACTION.values())) == 7
    assert CHECKLIST_CODES == ("company_named", "salary_stated", "duties_described", "title_matches_level")  # #244: bốn mục


def test_fr31_du_bay_dau_hieu_moi_lan_ready_kem_cau_ghi_chu_co_dinh() -> None:
    for name in NAMES:
        warnings = ready_example(name)["data"]["warnings"]
        assert [s["code"] for s in warnings["signs"]] == list(SIGN_CODES)
        assert warnings["disclaimer"] == "signs_are_hints"  # "Dấu hiệu là gợi ý để bạn tự kiểm tra. Đa số tin bị gắn dấu hiệu vẫn là tin thật."


def test_fr31_du_kien_cua_tung_dau_hieu_mang_con_so_da_kich_hoat() -> None:
    signs = {s["code"]: s for s in ready_example("full")["data"]["warnings"]["signs"]}
    d1, d3, d4 = signs["d1_wide_skills"]["fact"], signs["d3_high_req_low_pay"]["fact"], signs["d4_reposted"]["fact"]
    assert set(d1) == {"kind", "skill_count", "p90"} and d1["p90"]["kind"] == "percentile"  # D1: số kỹ năng so với P90
    assert set(d3) == {"kind", "skill_count", "p75_skill_count", "salary_ceiling_vnd_month", "p25_salary"}  # D3: P75 và P25
    assert d3["p75_skill_count"]["kind"] == d3["p25_salary"]["kind"] == "percentile"
    assert set(d4) == {"kind", "reposts", "snapshots_seen"}
    assert signs["d5_unusual_contact"]["fact"]["channels"] == ["zalo", "telegram"] and signs["d5_unusual_contact"]["source_field"] == "contacts"
    assert signs["d6_fee_first"]["fact"] == {"kind": "d6_fee_first", "quote_count": 1}
    assert signs["d6_fee_first"]["source_field"] == "fee_mentions"
    assert signs["d7_no_company"]["source_field"] is None  # source_field có thể null
    d2 = {s["code"]: s for s in ready_example("sparse")["data"]["warnings"]["signs"]}["d2_specific_heavy"]["fact"]
    assert set(d2) == {"kind", "recognised_count", "specific_count"}


def test_fr31_d4_chua_co_trong_du_lieu_la_khong_danh_gia_duoc_khong_phai_khong_kich_hoat() -> None:
    sparse = ready_example("sparse")["data"]["warnings"]
    d4 = next(s for s in sparse["signs"] if s["code"] == "d4_reposted")
    assert (d4["status"], d4["reason"]) == ("not_evaluable", "not_in_data") and sparse["collected_match"] is None


BAD_WARNINGS: list[tuple[str, Callable[[dict[str, Any]], None], str]] = [
    ("full", _drop_sign("d7_no_company"), "đủ bảy dấu hiệu"),
    ("full", _swap_signs, "đúng thứ tự D1 đến D7"),
    ("full", lambda b: b["data"]["warnings"]["signs"].append(copy.deepcopy(b["data"]["warnings"]["signs"][0])), "không trùng mã"),
    ("full", _edit_sign("d1_wide_skills", code="d9_la"), "mã dấu hiệu là tập đóng"),
    ("full", _edit_sign("d1_wide_skills", status="maybe"), "trạng thái là tập đóng"),
    ("full", _edit_sign("d1_wide_skills", fact=None), "triggered thì phải có dữ kiện"),
    ("full", _edit_sign("d1_wide_skills", action=None), "triggered thì phải có gợi ý hành động"),
    ("full", _edit_sign("d1_wide_skills", action="look_up_company"), "gợi ý đúng của dấu hiệu"),
    ("full", _edit_sign("d1_wide_skills", source_field="contacts"), "D1 không có nguồn trích dẫn"),
    ("full", _edit_sign("d1_wide_skills", reason="not_in_data"), "triggered thì không có lý do"),
    ("full", _edit_fact("d1_wide_skills", kind="d2_specific_heavy"), "kiểu dữ kiện phải khớp mã dấu hiệu"),
    ("full", _edit_fact("d1_wide_skills", skill_count=-1), "số kỹ năng không âm"),
    ("full", _edit_fact("d1_wide_skills", p90=None), "D1 phải mang P90"),
    ("full", _edit_fact("d1_wide_skills", p90=stat(12.0, "vn.backend") | {"display": "null_data", "value": None}), "P90 phải hiện số"),
    ("full", _edit_fact("d1_wide_skills", extra=1), "dữ kiện không có trường lạ"),
    ("full", _edit_fact("d3_high_req_low_pay", p25_salary=None), "D3 phải mang P25"),
    ("full", _edit_fact("d3_high_req_low_pay", p75_skill_count=None), "D3 phải mang P75"),
    ("full", _edit_fact("d4_reposted", snapshots_seen=-1), "số lần thấy không âm"),
    ("full", _edit_fact("d4_reposted", reposts=5), "D4 phải đúng với collected_match"),
    ("full", _set([*W, "collected_match"], None), "D4 kích hoạt thì phải có tin thu thập khớp"),
    ("full", _edit_fact("d5_unusual_contact", channels=[]), "D5 phải nêu kênh"),
    ("full", _edit_fact("d5_unusual_contact", channels=["company_email"]), "kênh công ty không phải dấu hiệu D5"),
    ("full", _edit_sign("d5_unusual_contact", source_field=None), "D5 trích từ contacts"),
    ("full", _edit_sign("d6_fee_first", source_field="contacts"), "D6 trích từ fee_mentions"),
    ("full", _edit_fact("d6_fee_first", quote_count=0), "D6 phải có ít nhất một trích dẫn"),
    ("full", _edit_fact("d6_fee_first", quote_count=6), "tối đa 5 trích dẫn phí"),
    ("sparse", _edit_sign("d1_wide_skills", fact={"kind": "d1_wide_skills", "skill_count": 3, "p90": stat(1.0, "vn.backend.junior")}), "not_triggered thì không có dữ kiện"),
    ("sparse", _edit_sign("d1_wide_skills", action="ask_daily_stack"), "not_triggered thì không có gợi ý"),
    ("sparse", _edit_sign("d3_high_req_low_pay", reason=None), "not_evaluable phải có lý do"),
    ("sparse", _edit_sign("d3_high_req_low_pay", reason="không rõ"), "lý do là tập đóng"),
    ("sparse", _edit_sign("d2_specific_heavy", status="not_evaluable", reason="not_in_data", fact=None, action=None), "D2 chỉ không đánh giá được vì ô chưa đủ mẫu"),
    ("sparse", _edit_sign("d4_reposted", reason="not_enough_data"), "D4 chỉ không đánh giá được vì không có trong dữ liệu"),
    ("sparse", _edit_sign("d7_no_company", status="not_evaluable", reason="not_in_data"), "D7 luôn đánh giá được"),
    ("sparse", _edit_sign("d4_reposted", status="not_triggered", reason=None), "không có tin thu thập khớp thì D4 không đánh giá được"),
    ("sparse", _set([*W, "collected_match"], {"repost_count": 1, "snapshots_seen": 1}), "có tin khớp thì D4 đánh giá được"),
    ("sparse", _set([*W, "disclaimer"], None), "ready thì có câu ghi chú cố định"),
    ("sparse", _set([*W, "disclaimer"], "Dấu hiệu là gợi ý"), "câu ghi chú là mã cố định, không phải chữ tự do"),
    ("sparse", _set([*W, "salary_note"], "tuy_y"), "câu lương trung tính là mã cố định"),
    ("sparse", _set([*W, "checklist"], []), "ready thì đủ bốn mục"),
    ("sparse", lambda b: b["data"]["warnings"]["checklist"].reverse(), "bốn mục đúng thứ tự"),
    ("sparse", lambda b: b["data"]["warnings"]["checklist"][0].update(present="có"), "present là bool hoặc null, không phải chữ"),
    ("sparse", _set([*W, "collected_match"], {"repost_count": -1, "snapshots_seen": 1}), "số lần đăng lại không âm"),
    ("sparse", lambda b: b["data"]["warnings"].update(status="not_ready"), "not_ready thì mọi thứ rỗng"),
    ("sparse", lambda b: b["data"]["warnings"]["signs"][3].update(status="triggered", reason=None, fact={"kind": "d4_reposted", "reposts": 1, "snapshots_seen": 1}, action="check_original_posting"), "D4 kích hoạt mà không có tin khớp"),
]


@pytest.mark.parametrize(("name", "mutate", "why"), BAD_WARNINGS, ids=[w for _, _, w in BAD_WARNINGS])
def test_fr31_warnings_sai_hinh_bi_tu_choi(name: str, mutate: Callable[[dict[str, Any]], None], why: str) -> None:
    body = ready_example(name)
    mutate(body)
    with pytest.raises(ValidationError):
        _validate(body)


def test_fr31_not_ready_ma_con_du_lieu_bi_tu_choi() -> None:
    for patch in ({"disclaimer": "signs_are_hints"}, {"salary_note": "salary_not_stated"}, {"collected_match": {"repost_count": 1, "snapshots_seen": 1}}):
        with pytest.raises(ValidationError):
            PostingWarnings.model_validate({"status": "not_ready", "checklist": [], "signs": [], "collected_match": None, "salary_note": None, "disclaimer": None, **patch})
    with pytest.raises(ValidationError):
        PostingMarket.model_validate({"status": "not_ready", "cell_id": "vn.backend", "years": None, "skill_count": None, "salary": None})


def test_fr31_khong_cau_chu_cam_o_bat_ky_vi_du_nao() -> None:
    """FR-25/31/47: không "lừa đảo", "tin giả", "tin ma" trong bất kỳ giá trị nào của hình `ready`, kể cả mã câu."""
    for name in NAMES:
        text = json.dumps(ready_example(name), ensure_ascii=False).casefold()
        assert not [word for word in BANNED if word in text]
    assert not [w for w in BANNED if any(w in str(v).casefold() for v in (*SIGN_ACTION.values(), *SIGN_CODES))]


def test_fr30_market_not_ready_ma_con_cau_ghi_chu_bi_tu_choi() -> None:
    body = TestClient(app).get("/api/v1/posting-check", params={"role": "backend", "level": "junior", "skills": "java"}).json()
    body["data"]["market"]["note"] = "comparisons_not_verdict"
    with pytest.raises(ValidationError):
        _validate(body)


@pytest.mark.parametrize("name", NAMES)
def test_fr30_market_ready_mang_cau_so_sanh_khong_phai_phan_quyet(name: str) -> None:
    """#125 AC5 và #242: so sánh với thị trường không phải phán quyết về tin; câu ghi chú là mã cố định, màn dựng chữ."""
    assert ready_example(name)["data"]["market"]["note"] == "comparisons_not_verdict"


def test_fr31_d2_khong_danh_gia_duoc_khi_o_chua_du_mau_la_hop_le_vi_nhom_ky_nang_chi_co_o_n_tu_30() -> None:
    body = ready_example("sparse")
    sign = _sign_at(body, "d2_specific_heavy")
    sign.update(status="not_evaluable", reason="not_enough_data", fact=None, action=None)
    _validate(body)
    assert NOT_EVALUABLE_REASONS["d2_specific_heavy"] == frozenset({"not_enough_data"})
    assert "d5_unusual_contact" not in NOT_EVALUABLE_REASONS and "d7_no_company" not in NOT_EVALUABLE_REASONS


def test_fr31_checklist_present_null_la_khong_biet_va_hop_le() -> None:
    """`title_matches_level` không biết được khi `title_level` null hoặc cấp là `unknown`: `null`, không phải `false`."""
    body = ready_example("sparse")
    item = body["data"]["warnings"]["checklist"][3]
    assert item["code"] == "title_matches_level"
    item["present"] = None
    parsed = _validate(body)
    assert parsed.data.warnings.checklist[3].present is None
    assert json.loads(parsed.model_dump_json()) == body
