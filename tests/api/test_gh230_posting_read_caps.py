"""AD-9, AD-11, FR-26 — trần cỡ thân của `POST /api/v1/posting-reads` và kết quả đọc quá cỡ (#230, vòng review 2026-11-27).

Hai việc: (1) thân quá lớn bị từ chối trước khi phân tích (`Content-Length` và đếm byte lúc đọc, như `haido_api/uploads.py`
làm với CV) bằng 413 `text_too_long` nêu giới hạn; (2) kết quả của cổng đọc vượt trần (cụm chưa nhận diện, trích dẫn, số năm)
bị cắt trước khi dựng model, và lỗi còn lại là 502 `read_failed`, không phải 500.
"""

import copy
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from posting_samples import BACKEND_TEXT, SENTINEL, query_from_read

from haido_api.main import app, create_app
from haido_api.posting_read import FIXTURE, FakePostingReader, truncate_read
from haido_api.schemas.posting import (
    MAX_CONTACT_QUOTES,
    MAX_FEE_MENTIONS,
    MAX_FEE_QUOTE_LEN,
    MAX_TEXT_CHARS,
    MAX_UNRECOGNISED,
    MAX_UNRECOGNISED_LEN,
    MAX_YEARS_MIN,
    PostingReadData,
    PostingReadRequest,
)
from haido_core.config import load_rules
from haido_core.vocab.skills import MAX_PROFILE_SKILLS, load_seed_skills

URL = "/api/v1/posting-reads"
JSON_HEADERS = {"content-type": "application/json"}


class _Spy:
    """Nguồn đọc đếm số lần được gọi: thân quá lớn không bao giờ được tới đây."""

    def __init__(self) -> None:
        self.calls = 0
        self._real = FakePostingReader()

    def read(self, text: str) -> Any:
        self.calls += 1
        return self._real.read(text)


def _body(text: str) -> bytes:
    return json.dumps({"text": text}, ensure_ascii=False).encode("utf-8")


def _assert_too_long(resp: Any) -> None:
    assert resp.status_code == 413, resp.text[:200]
    error = resp.json()["error"]
    assert error["code"] == "text_too_long" and error["snapshot_date"] is None
    assert "20.000" in error["message"]  # nêu giới hạn
    assert SENTINEL not in resp.text


# ----------------------------------------------------------------------------------------------- trần cỡ thân (AD-9)


def test_ad9_tran_nam_trong_rules_toml_va_phu_du_20000_ky_tu() -> None:
    rules = load_rules()
    assert rules.posting_max_chars == MAX_TEXT_CHARS == 20_000  # FR-26
    # 20.000 ký tự, tệ nhất 4 byte UTF-8 mỗi ký tự, cộng phần phụ trội của JSON: trần byte phải phủ được.
    assert rules.posting_max_body_bytes >= 4 * rules.posting_max_chars + 1024
    assert rules.posting_max_body_bytes <= 1024 * 1024  # không mở cửa cho thân lớn vào bộ nhớ


def test_ad9_text_khai_max_length_20000_trong_schema_va_openapi() -> None:
    assert PostingReadRequest.model_json_schema()["properties"]["text"]["maxLength"] == 20_000
    schema = app.openapi()["components"]["schemas"]["PostingReadRequest"]
    assert schema["properties"]["text"]["maxLength"] == 20_000


def test_ad9_content_length_vuot_tran_bi_tu_choi_truoc_khi_phan_tich() -> None:
    spy = _Spy()
    client = TestClient(create_app(posting_reader=spy))
    big = _body("a" * (load_rules().posting_max_body_bytes + 1))
    resp = client.post(URL, content=big, headers=JSON_HEADERS)
    _assert_too_long(resp)
    assert spy.calls == 0


def test_ad9_content_length_khai_qua_lon_bi_chan_ngay_du_than_that_nho() -> None:
    """Chặn ở `Content-Length` là chặn trước khi đọc một byte nào của thân: khai 10 MB thì không cần chờ thân đến."""
    spy = _Spy()
    client = TestClient(create_app(posting_reader=spy))
    resp = client.post(URL, content=_body("nhỏ thôi"), headers={**JSON_HEADERS, "content-length": str(10 * 1024 * 1024)})
    _assert_too_long(resp)
    assert spy.calls == 0
    resp = client.post(URL, content=_body("nhỏ thôi"), headers={**JSON_HEADERS, "content-length": "9" * 40})  # số dài vô lý
    _assert_too_long(resp)


def test_ad9_than_khong_co_content_length_bi_chan_khi_dem_byte() -> None:
    spy = _Spy()
    client = TestClient(create_app(posting_reader=spy))
    ceiling = load_rules().posting_max_body_bytes

    def chunks() -> Iterator[bytes]:  # không có Content-Length: gửi từng khối (chunked)
        # JSON hợp lệ với `text` ngắn, theo sau là khoảng trắng vượt trần byte: chỉ đếm byte lúc đọc mới chặn được (không phải
        # `max_length` của `text`, vốn không bị vi phạm).
        yield b'{"text": "nho thoi"}'
        for _ in range(ceiling // 1000 + 5):
            yield b" " * 1000

    resp = client.post(URL, content=chunks(), headers=JSON_HEADERS)
    assert "content-length" not in resp.request.headers
    _assert_too_long(resp)
    assert spy.calls == 0


def test_ad9_text_20001_ky_tu_la_413_du_than_nho_hon_tran_byte() -> None:
    spy = _Spy()
    client = TestClient(create_app(posting_reader=spy))
    resp = client.post(URL, content=_body("a" * (MAX_TEXT_CHARS + 1)), headers=JSON_HEADERS)
    _assert_too_long(resp)
    assert spy.calls == 0


def test_fr26_text_dung_20000_ky_tu_van_duoc_doc() -> None:
    spy = _Spy()
    client = TestClient(create_app(posting_reader=spy))
    assert client.post(URL, json={"text": "a" * MAX_TEXT_CHARS}).status_code == 200
    assert client.post(URL, json={"text": "ế" * MAX_TEXT_CHARS}).status_code == 200  # 3 byte mỗi ký tự, vẫn dưới trần byte
    assert client.post(URL, json={"text": "😀" * MAX_TEXT_CHARS}).status_code == 200  # 4 byte mỗi ký tự
    assert spy.calls == 3


def test_ad9_loi_422_cua_than_sai_hinh_khong_doi() -> None:
    client = TestClient(app)
    for payload in ({}, {"text": 123}, {"text": "x", "extra": 1}):
        resp = client.post(URL, json=payload)
        assert resp.status_code == 422 and resp.json()["error"]["code"] == "invalid_query"
    resp = client.post(URL, content=b"{khong phai json", headers=JSON_HEADERS)
    assert resp.status_code == 422 and SENTINEL not in resp.text


def test_ad9_413_khai_trong_openapi_va_noi_ro_gioi_han() -> None:
    op = app.openapi()["paths"][URL]["post"]
    assert "413" in op["responses"]
    assert "20.000" in op["responses"]["413"]["description"] or "20000" in op["responses"]["413"]["description"]


# ------------------------------------------------------------------------- kết quả đọc quá cỡ (AD-11, #230 vòng review)


def _fixture_with(tmp_path: Path, **patch: Any) -> Path:
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    raw["reads"]["backend"].update(patch)
    target = tmp_path / "reads.json"
    target.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
    return target


def _client(reader: Any) -> TestClient:
    return TestClient(create_app(posting_reader=reader), raise_server_exceptions=False)


def test_ad11_ket_qua_qua_co_bi_cat_thay_vi_sap(tmp_path: Path) -> None:
    oversized = _fixture_with(
        tmp_path,
        unrecognised=["x" * 200] * 80 + ["   "],
        fee_mentions=["q" * 300] * 9,
        contact_quotes=[{"channel": "company_email", "quote": "c" * 500}] * 9,
        years_min=99,
    )
    resp = _client(FakePostingReader(oversized)).post(URL, json={"text": BACKEND_TEXT})
    assert resp.status_code == 200, resp.text[:300]
    data = resp.json()["data"]
    assert len(data["unrecognised"]) == MAX_UNRECOGNISED and all(len(u) <= MAX_UNRECOGNISED_LEN for u in data["unrecognised"])
    assert len(data["fee_mentions"]) == MAX_FEE_MENTIONS and all(len(q) <= MAX_FEE_QUOTE_LEN for q in data["fee_mentions"])
    assert len(data["contact_quotes"]) == MAX_CONTACT_QUOTES
    assert all(len(q["quote"]) <= MAX_FEE_QUOTE_LEN for q in data["contact_quotes"])
    assert data["years_min"] is None  # số năm vô lý là lỗi đọc, không phải sự kiện: không đoán, không kẹp về 60
    PostingReadData.model_validate(data)


def test_ad11_cat_la_ham_thuan_va_khong_doi_dau_vao() -> None:
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))["reads"]["backend"]
    raw["unrecognised"] = ["a" * 90, "", "b"]
    raw["years_min"] = MAX_YEARS_MIN + 1
    before = copy.deepcopy(raw)
    cut = truncate_read(raw)
    assert raw == before
    assert cut["unrecognised"] == ["a" * MAX_UNRECOGNISED_LEN, "b"]  # cụm rỗng bị bỏ, cụm dài bị cắt
    assert cut["years_min"] is None
    assert truncate_read(cut) == cut  # đã cắt thì cắt lại không đổi
    raw["years_min"] = MAX_YEARS_MIN
    assert truncate_read(raw)["years_min"] == MAX_YEARS_MIN  # đúng trần thì giữ


def test_ad11_ket_qua_van_sai_sau_khi_cat_la_502_read_failed_khong_phai_500(tmp_path: Path) -> None:
    broken = _fixture_with(tmp_path, role="vai_tro_khong_co_trong_cau_hinh_" + SENTINEL)
    resp = _client(FakePostingReader(broken)).post(URL, json={"text": BACKEND_TEXT})
    assert resp.status_code == 502, resp.text[:300]
    error = resp.json()["error"]
    assert error["code"] == "read_failed" and error["message"]
    assert SENTINEL not in resp.text  # ValidationError của pydantic chứa giá trị đầu vào: không được lọt ra


def test_ad22_nhieu_hon_200_ky_nang_bi_cat_o_buoc_1_nen_query_buoc_2_dung_200(tmp_path: Path) -> None:
    """`skills` của bước một có trần bằng trần của bước hai (`MAX_PROFILE_SKILLS`): tin nhắc quá 200 kỹ năng không làm bước hai 422."""
    codes = [s.code for s in load_seed_skills()][: MAX_PROFILE_SKILLS + 40]
    assert len(codes) > MAX_PROFILE_SKILLS
    many = _fixture_with(tmp_path, skills=[{"code": c, "mentions": 1} for c in codes])
    client = _client(FakePostingReader(many))
    resp = client.post(URL, json={"text": BACKEND_TEXT})
    assert resp.status_code == 200, resp.text[:300]
    read = resp.json()["data"]
    assert [s["code"] for s in read["skills"]] == codes[:MAX_PROFILE_SKILLS]  # cắt giữ thứ tự, bỏ phần dư ở cuối
    query = query_from_read(read)
    assert len(query["skills"].split(",")) == MAX_PROFILE_SKILLS
    assert client.get("/api/v1/posting-check", params=query).status_code == 200


def test_ad22_model_tu_choi_hon_200_ky_nang_va_ham_cat_la_ham_thuan() -> None:
    raw = FakePostingReader().read(BACKEND_TEXT).data.model_dump(mode="json")
    raw["skills"] = [{"code": s.code, "mentions": 1} for s in load_seed_skills()][: MAX_PROFILE_SKILLS + 1]
    before = copy.deepcopy(raw)
    with pytest.raises(ValueError):
        PostingReadData.model_validate(raw)
    assert len(truncate_read(raw)["skills"]) == MAX_PROFILE_SKILLS
    assert raw == before
    PostingReadData.model_validate(truncate_read(raw))


def test_ad9_loi_422_truong_la_khong_nhac_ten_truong_nguoi_dung_gui() -> None:
    """Tên khóa lạ do người dùng gửi có thể là chữ của tin dán: 422 chỉ nói "trường lạ", không lặp lại tên."""
    text = BACKEND_TEXT
    assert len(text) > 200
    resp = TestClient(app).post(URL, json={"text": text, SENTINEL: 1})
    assert resp.status_code == 422 and resp.json()["error"]["code"] == "invalid_query"
    assert SENTINEL not in resp.text
    assert "trường không có trong hợp đồng" in resp.json()["error"]["message"]
