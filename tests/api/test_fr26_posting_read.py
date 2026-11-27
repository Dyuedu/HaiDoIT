"""FR-26, FR-27, AD-9 — `POST /api/v1/posting-reads` (#230): hình response và nguồn giả chọn kết quả từ chữ dán."""

import re
from typing import Any

import pytest
from fastapi.testclient import TestClient
from posting_samples import (
    BACKEND_TEXT,
    CLOUD_SKILLS,
    CLOUD_TEXT,
    FEE_TEXT,
    NOT_IT_TEXT,
    NOT_POSTING_TEXT,
    POSTING_SKILLS,
    QUERY_FIELDS,
    SCREEN_ONLY_FIELDS,
    SENTINEL,
    SHORT_TEXT,
)
from pydantic import ValidationError

from haido_api.main import app, create_app
from haido_api.posting_read import (
    READER_ENV,
    FakePostingReader,
    ModelPostingReader,
    PostingReadRefused,
    load_reader,
)
from haido_api.schemas import posting as posting_schema
from haido_api.schemas.posting import (
    POSTING_READ_ERRORS,
    ContactChannel,
    PostingReadData,
    PostingReadResponse,
)
from haido_core.config import load_rules
from haido_core.vocab.skills import find_seed_skill, seed_version

URL = "/api/v1/posting-reads"


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


def _post(client: TestClient, text: str) -> dict[str, Any]:
    resp = client.post(URL, json={"text": text})
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_fr26_tin_backend_junior_co_du_su_kien_dong(client: TestClient) -> None:
    body = _post(client, BACKEND_TEXT)
    assert set(body) == {"data"}  # không có meta: không Stat, không ô thống kê (xem spec.md)
    PostingReadResponse.model_validate(body)
    data = body["data"]
    assert data["is_posting"] is True and data["reason"] is None
    assert data["role"] == "backend" and data["level"] == "junior"
    assert [s["code"] for s in data["skills"]] == POSTING_SKILLS
    assert all(s["mentions"] >= 1 for s in data["skills"])
    assert data["unrecognised"] and all(isinstance(u, str) for u in data["unrecognised"])
    assert data["years_min"] == 1
    assert data["salary"] == {"min": 10_000_000, "max": 18_000_000, "currency": "vnd", "period": "month"}
    assert data["company_named"] is True
    assert set(data["contacts"]) <= {c.value for c in ContactChannel}
    assert data["fee_mentions"] == []
    assert data["vocab_version"] == seed_version()
    assert data["model_id"] and data["prompt_version"]
    # FR-27 (nhánh), #244 (sự kiện của danh sách), #245 (trích dẫn liên hệ), #246 (tin thu thập khớp)
    assert data["branch"] is None
    assert data["duties_described"] is True and data["title_level"] == "junior" and data["salary_non_numeric"] is False
    assert [q["channel"] for q in data["contact_quotes"]] == ["company_email"]
    assert all(len(q["quote"]) <= 120 for q in data["contact_quotes"])
    assert data["collected"] is None


def test_fr26_moi_truong_cua_buoc_1_la_ve_query_hoac_chi_hien_tren_man(client: TestClient) -> None:
    """Mỗi trường của `data` thuộc đúng một danh sách: đi vào query (mã hoặc số) hoặc chỉ hiện trên màn (AD-22)."""
    fields = set(PostingReadData.model_fields)
    assert fields == QUERY_FIELDS | SCREEN_ONLY_FIELDS
    assert not QUERY_FIELDS & SCREEN_ONLY_FIELDS
    assert set(_post(client, BACKEND_TEXT)["data"]) == fields


def test_fr27_tin_devops_co_nhanh_va_tin_thu_thap_khop(client: TestClient) -> None:
    data = _post(client, CLOUD_TEXT)["data"]
    assert data["role"] == "devops" and data["level"] == "mid" and data["branch"] == "cloud"
    assert [s["code"] for s in data["skills"]] == CLOUD_SKILLS
    assert data["salary"] is None and data["salary_non_numeric"] is True  # "thỏa thuận": có nói lương, không có số
    collected = data["collected"]
    assert set(collected) == {"site", "first_seen", "repost_count", "snapshots_seen", "url"}
    assert collected["site"] and collected["url"].startswith("https://")  # FR-32: có link về tin gốc
    assert collected["repost_count"] >= 2 and collected["snapshots_seen"] >= 1
    PostingReadData.model_validate(data)


def test_fr26_ma_ky_nang_vai_tro_va_cap_nam_trong_bo_ma(client: TestClient) -> None:
    rules = load_rules()
    for text in (BACKEND_TEXT, FEE_TEXT):
        data = _post(client, text)["data"]
        assert data["role"] in rules.roles
        assert data["level"] in set(rules.level_codes.values())
        assert all(find_seed_skill(s["code"]) for s in data["skills"])


def test_fr26_tin_co_phi_dat_coc_khong_ten_cong_ty(client: TestClient) -> None:
    data = _post(client, FEE_TEXT)["data"]
    assert data["is_posting"] is True
    assert data["company_named"] is False
    assert data["salary"] is None and data["years_min"] is None
    assert set(data["contacts"]) == {"zalo", "telegram"}
    assert data["fee_mentions"]
    assert all(len(q) <= 120 for q in data["fee_mentions"])


def test_fr26_khong_phai_tin_khong_co_gi_de_khop(client: TestClient) -> None:
    data = _post(client, NOT_POSTING_TEXT)["data"]
    assert data["is_posting"] is False and data["reason"] == "not_posting"
    _assert_empty(data)


def test_fr26_khong_thuoc_it_co_dau_tin_tuyen_dung_la_not_it(client: TestClient) -> None:
    """FR-26, UX-DR44: "Tin này có vẻ không thuộc lĩnh vực IT": tin tuyển dụng không có dấu IT nào."""
    data = _post(client, NOT_IT_TEXT)["data"]
    assert data["is_posting"] is False and data["reason"] == "not_it"
    _assert_empty(data)


def test_fr26_not_it_va_not_posting_khac_nhau_o_dau_tin_tuyen_dung(client: TestClient) -> None:
    # Quy tắc của bản giả: sau `too_short`, có dấu IT thì xét tiếp; không có dấu IT mà có dấu tin tuyển dụng
    # (`job_markers`) là `not_it`; không có cả hai là `not_posting`.
    assert _post(client, NOT_POSTING_TEXT)["data"]["reason"] == "not_posting"
    assert _post(client, NOT_IT_TEXT)["data"]["reason"] == "not_it"
    assert _post(client, NOT_IT_TEXT.upper())["data"]["reason"] == "not_it"  # không phân biệt hoa thường
    assert _post(client, NOT_IT_TEXT + " Java")["data"]["is_posting"] is True  # một dấu IT là đủ để không phải not_it
    assert _post(client, SHORT_TEXT.replace("Backend Java", "kế toán"))["data"]["reason"] == "too_short"  # ngắn thắng


def test_fr26_qua_ngan_khong_co_gi_de_khop(client: TestClient) -> None:
    data = _post(client, SHORT_TEXT)["data"]
    assert data["is_posting"] is False and data["reason"] == "too_short"
    _assert_empty(data)


def _assert_empty(data: dict[str, Any]) -> None:
    assert data["role"] is None and data["level"] is None
    assert data["skills"] == [] and data["unrecognised"] == []
    assert data["years_min"] is None and data["salary"] is None
    assert data["company_named"] is False
    assert data["contacts"] == [] and data["fee_mentions"] == []
    assert data["branch"] is None and data["title_level"] is None and data["collected"] is None
    assert data["duties_described"] is False and data["salary_non_numeric"] is False and data["contact_quotes"] == []
    assert data["model_id"] and data["prompt_version"] and data["vocab_version"]


def test_fr26_chon_ket_qua_theo_thu_tu_ngan_roi_khong_it_roi_phi_roi_backend(client: TestClient) -> None:
    pad = " " * 300
    assert _post(client, pad + "Tuyển Java" + pad)["data"]["reason"] == "too_short"  # cắt khoảng trắng trước khi đo
    assert _post(client, SHORT_TEXT + " đặt cọc")["data"]["reason"] == "too_short"  # ngắn thắng mọi dấu khác
    deposit_no_it = NOT_POSTING_TEXT + " Cần đặt cọc trước."
    assert _post(client, deposit_no_it)["data"]["reason"] == "not_posting"  # không có dấu IT thì chưa xét phí
    assert _post(client, BACKEND_TEXT.upper() + " ĐẶT CỌC")["data"]["fee_mentions"]  # không phân biệt hoa thường
    assert _post(client, CLOUD_TEXT + " đặt cọc")["data"]["fee_mentions"]  # phí thắng nhánh DevOps
    assert _post(client, BACKEND_TEXT + " devops")["data"]["role"] == "devops"  # DevOps thắng Backend


def test_fr26_dung_200_ky_tu_thi_khong_con_ngan(client: TestClient) -> None:
    base = "Java developer tuyển dụng. "
    assert _post(client, (base * 20)[:199])["data"]["reason"] == "too_short"
    assert _post(client, (base * 20)[:200])["data"]["is_posting"] is True


def test_fr26_tat_dinh_cung_chu_cung_ket_qua(client: TestClient) -> None:
    assert client.post(URL, json={"text": BACKEND_TEXT}).content == client.post(URL, json={"text": BACKEND_TEXT}).content


@pytest.mark.parametrize(
    "patch",
    [
        {"reason": "not_posting"},  # là tin mà có lý do
        {"role": "khong_co"},
        {"level": "ceo"},
        {"skills": [{"code": "khong_co_ky_nang", "mentions": 1}]},
        {"skills": [{"code": "java", "mentions": 0}]},
        {"skills": [{"code": "java", "mentions": 1}, {"code": "java", "mentions": 2}]},
        {"unrecognised": ["x"] * 51},
        {"unrecognised": ["x" * 61]},
        {"fee_mentions": ["q"] * 6},
        {"fee_mentions": ["q" * 121]},
        {"contacts": ["zalo", "zalo"]},
        {"contacts": ["fax"]},
        {"years_min": -1},
        {"years_min": 61},
        {"reason": "not_it"},  # là tin mà có lý do
        {"branch": "khong_co"},
        {"branch": "cloud"},  # nhánh của devops, không phải của backend
        {"title_level": "ceo"},
        {"title_level": "unknown"},  # chức danh không cho biết cấp thì là null
        {"salary_non_numeric": True},  # có lương dạng số thì không thể "lương không có số"
        {"contact_quotes": [{"channel": "zalo", "quote": "q"}]},  # kênh không nằm trong contacts
        {"contact_quotes": [{"channel": "company_email", "quote": "q"}] * 6},
        {"contact_quotes": [{"channel": "company_email", "quote": "q" * 121}]},
        {"contact_quotes": [{"channel": "company_email", "quote": ""}]},
        {"collected": {"site": "s", "first_seen": "2026-10-01", "repost_count": 1, "snapshots_seen": 1, "url": None}},
        {"collected": {"site": "s", "first_seen": "2026-10-01", "repost_count": 1, "snapshots_seen": 1, "url": "ftp://x"}},
        {"collected": {"site": "s", "first_seen": "2026-10-01", "repost_count": -1, "snapshots_seen": 1, "url": "https://x.vn/1"}},
        {"collected": {"site": "s", "first_seen": "2026-10-01", "repost_count": 1, "snapshots_seen": 1, "url": "https://x.vn/1", "x": 1}},
        {"duties_described": None},
        {"salary": {"min": 20, "max": 10, "currency": "vnd", "period": "month"}},
        {"salary": {"min": 1, "max": 2, "currency": "eur", "period": "month"}},
    ],
)
def test_fr26_data_sai_la_loi(client: TestClient, patch: dict[str, Any]) -> None:
    valid = _post(client, BACKEND_TEXT)["data"]
    PostingReadData.model_validate(valid)
    with pytest.raises(ValidationError):
        PostingReadData.model_validate({**valid, **patch})


def test_fr26_bo_kiem_khong_doc_lai_rules_toml_moi_lan_kiem(monkeypatch: pytest.MonkeyPatch, client: TestClient) -> None:
    """`PostingReadData` kiểm mã vai trò, cấp và nhánh với `config/rules.toml` và `classify.toml`; đọc file một lần, không mỗi response."""
    valid = _post(client, BACKEND_TEXT)["data"]
    calls = {"rules": 0, "classify": 0}
    real_classify = posting_schema.load_classify_config

    def counting_rules(*args: Any, **kwargs: Any) -> Any:
        calls["rules"] += 1
        return load_rules(*args, **kwargs)

    def counting_classify(*args: Any, **kwargs: Any) -> Any:
        calls["classify"] += 1
        return real_classify(*args, **kwargs)

    posting_schema._rules.cache_clear()
    posting_schema._read_vocab.cache_clear()
    posting_schema.branch_codes.cache_clear()
    monkeypatch.setattr(posting_schema, "load_rules", counting_rules)
    monkeypatch.setattr(posting_schema, "load_classify_config", counting_classify)
    try:
        for _ in range(25):
            PostingReadData.model_validate(valid)
            PostingReadData.model_validate({**valid, "role": "devops", "branch": "cloud"})
        assert calls["rules"] == 1 and calls["classify"] == 1
    finally:
        monkeypatch.undo()
        posting_schema._rules.cache_clear()
        posting_schema._read_vocab.cache_clear()
        posting_schema.branch_codes.cache_clear()


def test_fr27_ma_nhanh_la_snake_case_khong_trung_va_thuoc_vai_tro_cua_rules() -> None:
    mapping = posting_schema.branch_codes()
    assert mapping["cloud"] == "devops" and mapping["llm_agent"] == "ai_ml" and mapping["product_owner"] == "ba_po_pm"
    assert all(re.fullmatch(r"[a-z0-9]+(_[a-z0-9]+)*", code) for code in mapping)
    assert set(mapping.values()) <= set(load_rules().roles)


def test_fr26_khong_phai_tin_thi_phai_rong_va_phai_co_ly_do(client: TestClient) -> None:
    empty = _post(client, SHORT_TEXT)["data"]
    PostingReadData.model_validate(empty)
    for reason in ("not_posting", "too_short", "not_it"):
        PostingReadData.model_validate({**empty, "reason": reason})
    with pytest.raises(ValidationError):
        PostingReadData.model_validate({**empty, "reason": "khac"})
    leftovers = (
        {"reason": None}, {"role": "backend"}, {"company_named": True}, {"skills": [{"code": "java", "mentions": 1}]},
        {"branch": "cloud"}, {"title_level": "junior"}, {"duties_described": True}, {"salary_non_numeric": True},
        {"contact_quotes": [{"channel": "zalo", "quote": "q"}]},
    )  # fmt: skip
    for patch in leftovers:
        with pytest.raises(ValidationError):
            PostingReadData.model_validate({**empty, **patch})


def test_fr26_than_sai_hinh_la_422_va_khong_lap_lai_chu(client: TestClient) -> None:
    for payload in ({}, {"text": 123}, {"text": "x", "extra": 1}, {"text": SENTINEL, "role": "backend"}):
        resp = client.post(URL, json=payload)
        assert resp.status_code == 422, resp.text
        assert resp.json()["error"]["code"] == "invalid_query"
        assert SENTINEL not in resp.text


def test_fr26_ma_loi_cua_duong_that_da_khai() -> None:
    assert POSTING_READ_ERRORS == {
        "text_too_long": 413,
        "rate_limited": 429,
        "read_failed": 502,
        "read_unavailable": 503,
        "read_timeout": 504,
    }
    op = app.openapi()["paths"][URL]["post"]
    for status in ("413", "422", "429", "502", "503", "504"):
        assert status in op["responses"], status
        assert op["responses"][status]["content"]["application/json"]["schema"]["$ref"].endswith("ErrorEnvelope")
    description = " ".join(r["description"] for r in op["responses"].values())
    for code in POSTING_READ_ERRORS:
        assert code in description, code


def test_ad9_nguon_model_chua_cai_tra_503_read_unavailable() -> None:
    test_client = TestClient(create_app(posting_reader=ModelPostingReader()))
    resp = test_client.post(URL, json={"text": BACKEND_TEXT})
    assert resp.status_code == 503
    error = resp.json()["error"]
    assert error["code"] == "read_unavailable"
    assert SENTINEL not in resp.text
    with pytest.raises(PostingReadRefused) as info:
        ModelPostingReader().read(BACKEND_TEXT)
    assert (info.value.status_code, info.value.code) == (503, "read_unavailable")


def test_ad9_chon_nguon_bang_bien_moi_truong() -> None:
    assert READER_ENV == "HAIDO_POSTING_READER"
    assert isinstance(load_reader({}), FakePostingReader)
    assert isinstance(load_reader({READER_ENV: " fake "}), FakePostingReader)
    assert isinstance(load_reader({READER_ENV: "model"}), ModelPostingReader)
    with pytest.raises(ValueError, match="HAIDO_POSTING_READER"):
        load_reader({READER_ENV: "gpt"})


def test_ad9_nguon_do_loi_cua_rieng_no_thanh_hinh_loi_chuan() -> None:
    class _TooLong:
        def read(self, text: str) -> Any:
            raise PostingReadRefused(413, "text_too_long", "Tin dài quá giới hạn.")

    resp = TestClient(create_app(posting_reader=_TooLong())).post(URL, json={"text": "x"})
    assert resp.status_code == 413
    body = resp.json()
    assert body["error"]["code"] == "text_too_long" and body["error"]["snapshot_date"] is None
    assert "20.000" in body["error"]["message"]  # câu của máy chủ nêu giới hạn, không phải câu của nguồn đọc
