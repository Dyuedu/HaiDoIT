"""Hai ví dụ của `GET /api/v1/posting-check` khi `market` và `warnings` ở hình `ready` (#230, vòng review 2026-11-27).

API giả luôn trả `not_ready` cho hai mục này tới #240–#246, nên hình `ready` không có response thật để sao chép. Hai ví dụ
này dựng từ response giả (phần `match` và `meta` là thật) cộng hai mục `ready` viết tay, rồi được kiểm bằng chính schema
(`Envelope[PostingCheckData]`, gồm cả `check_against_meta`). Chúng chỉ là ví dụ: `web/tests/fixtures/posting-check-ready-*.json`
chép lại chúng cho test của web, và `test_fr30_fr31_posting_ready_shapes.py` giữ file bằng kết quả của hàm ở đây.

- `full`: ô `vn.backend` (n = 157; 110 tin có số năm; 35 tin có lương). Tin đăng lương USD, nên có quy đổi theo tỷ giá của snapshot;
  số năm và số kỹ năng không có khoảng tin cậy (n từ 100). Cả bảy dấu hiệu đều kích hoạt trừ D2: cố ý chọn ca nhiều nhất.
- `sparse`: ô `vn.backend.junior` (n = 32; 24 tin có số năm; 9 tin có lương). Số năm "chưa đủ dữ liệu (24/30)", số kỹ năng có khoảng
  tin cậy (32 trong [30, 100)), tin không ghi lương (dòng trung tính, D3 không đánh giá được), D4 không đánh giá được vì tin chưa có
  trong dữ liệu.
"""

import copy
from typing import Any

from fastapi.testclient import TestClient
from posting_samples import HAVE_16_OF_18, POSTING_SKILLS, csv

from haido_api.main import app

NAMES = ("full", "sparse")


def stat(value: float | None, cell_id: str) -> dict[str, Any]:
    return {"value": value, "kind": "percentile", "display": "shown" if value is not None else "null_data", "cell_id": cell_id}


def _base(name: str) -> dict[str, Any]:
    level = "intern" if name == "full" else "junior"  # `intern` quay về `vn.backend`; `junior` có ô riêng
    resp = TestClient(app).get(
        "/api/v1/posting-check",
        params={"role": "backend", "level": level, "skills": csv(POSTING_SKILLS), "have": csv(HAVE_16_OF_18)},
    )
    assert resp.status_code == 200, resp.text
    body: dict[str, Any] = resp.json()
    return body


def full_market(cell: str) -> dict[str, Any]:
    return {
        "status": "ready",
        "cell_id": cell,
        "note": "comparisons_not_verdict",
        "years": {"state": "compared", "percentile": stat(62.0, cell), "ci_low": None, "ci_high": None},
        "skill_count": {"state": "compared", "percentile": stat(94.0, cell), "ci_low": None, "ci_high": None},
        "salary": {
            "state": "compared",
            "position": "below",
            "low": stat(12_000_000.0, cell),
            "high": stat(20_000_000.0, cell),
            "converted": {
                "min_vnd_month": 8_000_000,
                "max_vnd_month": 9_000_000,
                "fx": {"rate": 25_000, "unit": "vnd_per_usd", "fx_version": "fx-2026-11-03"},
            },
            "note": None,
        },
    }


def sparse_market(cell: str) -> dict[str, Any]:
    return {
        "status": "ready",
        "cell_id": cell,
        "note": "comparisons_not_verdict",
        "years": {"state": "not_enough_data", "percentile": stat(None, cell), "ci_low": None, "ci_high": None},
        "skill_count": {
            "state": "compared",
            "percentile": stat(40.0, cell),
            "ci_low": stat(28.0, cell),
            "ci_high": stat(53.0, cell),
        },
        "salary": {"state": "not_stated", "position": None, "low": None, "high": None, "converted": None, "note": "salary_not_stated"},
    }


def _sign(code: str, status: str = "not_triggered", **extra: Any) -> dict[str, Any]:
    return {"code": code, "status": status, "reason": None, "fact": None, "action": None, "source_field": None, **extra}


def full_warnings(cell: str) -> dict[str, Any]:
    return {
        "status": "ready",
        "checklist": [
            {"code": "company_named", "present": False},
            {"code": "salary_stated", "present": True},
            {"code": "duties_described", "present": True},
            {"code": "title_matches_level", "present": True},
        ],
        "signs": [
            _sign("d1_wide_skills", "triggered", fact={"kind": "d1_wide_skills", "skill_count": 14, "p90": stat(12.0, cell)}, action="ask_daily_stack"),
            _sign("d2_specific_heavy"),
            _sign(
                "d3_high_req_low_pay",
                "triggered",
                fact={
                    "kind": "d3_high_req_low_pay",
                    "skill_count": 14,
                    "p75_skill_count": stat(10.0, cell),
                    "salary_ceiling_vnd_month": 9_000_000,
                    "p25_salary": stat(12_000_000.0, cell),
                },
                action="compare_pay_before_applying",
            ),
            _sign("d4_reposted", "triggered", fact={"kind": "d4_reposted", "reposts": 3, "snapshots_seen": 41}, action="check_original_posting"),
            _sign(
                "d5_unusual_contact",
                "triggered",
                fact={"kind": "d5_unusual_contact", "channels": ["zalo", "telegram"]},
                action="verify_company_channel",
                source_field="contacts",
            ),
            _sign(
                "d6_fee_first",
                "triggered",
                fact={"kind": "d6_fee_first", "quote_count": 1},
                action="no_payment_before_verifying",
                source_field="fee_mentions",
            ),
            _sign("d7_no_company", "triggered", fact={"kind": "d7_no_company"}, action="look_up_company"),
        ],
        "collected_match": {"repost_count": 3, "snapshots_seen": 41},
        "salary_note": None,
        "disclaimer": "signs_are_hints",
    }


def sparse_warnings(cell: str) -> dict[str, Any]:
    return {
        "status": "ready",
        "checklist": [{"code": c, "present": True} for c in ("company_named", "salary_stated", "duties_described", "title_matches_level")],
        "signs": [
            _sign("d1_wide_skills"),
            _sign("d2_specific_heavy", "triggered", fact={"kind": "d2_specific_heavy", "recognised_count": 5, "specific_count": 3}, action="check_company_stack"),
            _sign("d3_high_req_low_pay", "not_evaluable", reason="no_numeric_salary"),
            _sign("d4_reposted", "not_evaluable", reason="not_in_data"),
            _sign("d5_unusual_contact"),
            _sign("d6_fee_first"),
            _sign("d7_no_company"),
        ],
        "collected_match": None,
        "salary_note": "salary_not_stated",
        "disclaimer": "signs_are_hints",
    }


def ready_example(name: str) -> dict[str, Any]:
    """Response `{data, meta}` đủ hình `ready`. `match`, `meta` lấy từ API giả; `market`, `warnings` viết tay."""
    body = copy.deepcopy(_base(name))
    cell = "vn.backend" if name == "full" else "vn.backend.junior"
    assert body["data"]["cell_id"] == cell
    body["data"]["market"] = full_market(cell) if name == "full" else sparse_market(cell)
    body["data"]["warnings"] = full_warnings(cell) if name == "full" else sparse_warnings(cell)
    return body
