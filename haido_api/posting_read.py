"""Nguồn đọc chữ dán của `POST /api/v1/posting-reads` (#230, AD-9, AD-11).

Route chỉ chuyển chữ cho nguồn và trả kết quả; nó không giữ chữ. Hai nguồn:

- `fake` (mặc định): chọn kết quả từ `fixtures/fake_posting_reads.json`, tất định, xét theo thứ tự: (1) chữ đã cắt khoảng trắng
  ngắn hơn `min_chars` thì `too_short`; (2) không có dấu nào của `it_markers` thì xét tiếp: có dấu nào của `job_markers` (dấu của một
  tin tuyển dụng) là `not_it` ("Tin này có vẻ không thuộc lĩnh vực IT"), không có thì `not_posting`; (3) có dấu của `deposit_markers`
  thì tin có phí hoặc đặt cọc; (4) có dấu của `devops_markers` thì tin DevOps nhánh Cloud (đã có tin thu thập khớp); (5) còn lại là
  tin Backend Junior;
- `model`: cổng đọc bằng model của #232. Chưa cài đặt: mọi lần đọc trả 503 `read_unavailable`. Production dùng nguồn này, nên không
  bao giờ phục vụ kết quả giả (quy tắc #309). Mặc định khi không đặt biến là `fake` như mọi nguồn khác; prod đặt `model` trong
  `deploy/compose.prod.yml` và `tests/deploy/test_gh230_posting_nguon_prod.py` giữ điều đó (demo và loadtest cũng đặt `model`).

Kết quả của cổng đọc có thể vượt trần của hình (cụm chưa nhận diện, trích dẫn, số năm): `truncate_read` cắt trước khi dựng model, để
một câu trả lời hơi dài không thành lỗi. Lỗi còn lại của một lần đọc là 502 `read_failed`, route lo (AD-11: không ghi gì ngoài tên kiểu lỗi).

AD-11: nguồn không có trạng thái, không lưu và không ghi chữ dán ở đâu, kể cả trong thông điệp lỗi. Module này không import
cơ sở dữ liệu, không ghi file và không ghi nhật ký; `tests/api/test_ad11_posting_read.py` giữ điều đó. Sau này (FR-29, FR-26) sẽ có
đúng một đường ghi, ở mô-đun riêng: từ khóa, tần suất, lần thấy cuối của cụm chưa nhận diện, và sự kiện ẩn danh bốn trường; không
bao giờ chữ của tin. Trần tốc độ (AD-9) là của #231; trần cỡ thân ở `routes/posting.py`.
"""

import json
import os
import unicodedata
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Protocol

from haido_api.schemas.posting import (
    MAX_CONTACT_QUOTE_LEN,
    MAX_CONTACT_QUOTES,
    MAX_FEE_MENTIONS,
    MAX_FEE_QUOTE_LEN,
    MAX_UNRECOGNISED,
    MAX_UNRECOGNISED_LEN,
    MAX_YEARS_MIN,
    PostingReadData,
    PostingReadResponse,
)
from haido_core.vocab.skills import MAX_PROFILE_SKILLS, seed_version

READER_ENV = "HAIDO_POSTING_READER"
DEFAULT_READER = "fake"
FIXTURE = Path(__file__).parent / "fixtures" / "fake_posting_reads.json"


class PostingReadRefused(Exception):
    """Đường đọc từ chối hoặc không đọc được. `errors.py` đổi thành `{error: {code, message, snapshot_date}}`.

    `code` là một khóa của `schemas.posting.POSTING_READ_ERRORS` (mã lạ được coi là `read_failed`). Thông điệp `message` chỉ dành cho
    người phát triển (test, nhật ký của chính nguồn): nó không bao giờ chứa chữ của tin, và response luôn dùng câu chuẩn của mã lỗi
    (`POSTING_READ_MESSAGES`), không dùng `message`.
    """

    def __init__(self, status_code: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message


class PostingReader(Protocol):
    """Đọc chữ dán qua cổng model đúng một lần.

    Hợp đồng lỗi (AD-11): nguồn chỉ ném `PostingReadRefused` cho lỗi đã biết. Thông điệp của mọi ngoại lệ, kể cả `ValidationError`
    của pydantic vốn chứa giá trị đầu vào, có thể mang chữ của tin, nên route bắt mọi ngoại lệ của nguồn, chỉ ghi tên kiểu của nó,
    trả 502 `read_failed` và không ném lại lên máy chủ ASGI.
    """

    def read(self, text: str) -> PostingReadResponse:
        """Trích sự kiện đóng từ `text`. Không lưu `text`.

        Raises:
            PostingReadRefused: quá nhiều lần, hoặc cổng model không đọc được. Thông điệp không chứa chữ của tin.
        """
        ...


def _fold(text: str) -> str:
    return unicodedata.normalize("NFC", text).casefold()


def _cut_texts(items: Any, *, max_items: int, max_len: int) -> Any:
    """Cắt từng chuỗi về `max_len`, bỏ chuỗi rỗng, giữ tối đa `max_items`. Giá trị không phải danh sách chuỗi được để nguyên."""
    if not isinstance(items, list):
        return items
    cut = [s.strip()[:max_len] if isinstance(s, str) else s for s in items]
    return [s for s in cut if s != ""][:max_items]


def truncate_read(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Cắt kết quả của cổng đọc về các trần của `PostingReadData` trước khi dựng model (hàm thuần, không đổi `raw`).

    Cắt: `unrecognised` (tối đa 50 cụm, mỗi cụm 60 ký tự), `fee_mentions` (5 × 120), `contact_quotes` (5 × 120 ký tự mỗi `quote`),
    `skills` (tối đa `MAX_PROFILE_SKILLS` = 200, bằng trần của `skills=` ở bước hai, giữ thứ tự).
    `years_min` quá `MAX_YEARS_MIN` là lỗi đọc chứ không phải sự kiện, nên thành `null` (không đoán, không kẹp về trần).
    Mọi sai khác khác (mã lạ, kênh không có trong `contacts`...) không được vá: dựng model sẽ báo lỗi và route trả 502.
    """
    out = dict(raw)
    if "unrecognised" in raw:
        out["unrecognised"] = _cut_texts(raw["unrecognised"], max_items=MAX_UNRECOGNISED, max_len=MAX_UNRECOGNISED_LEN)
    if "fee_mentions" in raw:
        out["fee_mentions"] = _cut_texts(raw["fee_mentions"], max_items=MAX_FEE_MENTIONS, max_len=MAX_FEE_QUOTE_LEN)
    if isinstance(raw.get("skills"), list):
        out["skills"] = raw["skills"][:MAX_PROFILE_SKILLS]
    quotes = raw.get("contact_quotes")
    if isinstance(quotes, list):
        cut: list[Any] = []
        for item in quotes:
            if isinstance(item, Mapping) and isinstance(item.get("quote"), str):
                text = item["quote"].strip()[:MAX_CONTACT_QUOTE_LEN]
                if text:
                    cut.append({**item, "quote": text})
            else:
                cut.append(item)
        out["contact_quotes"] = cut[:MAX_CONTACT_QUOTES]
    years = raw.get("years_min")
    if isinstance(years, int) and not isinstance(years, bool) and years > MAX_YEARS_MIN:
        out["years_min"] = None
    return out


class FakePostingReader:
    """Nguồn giả. Chỉ giữ cấu hình đọc từ fixture lúc khởi tạo; mỗi lần đọc không để lại gì."""

    def __init__(self, fixture: Path = FIXTURE) -> None:
        raw: dict[str, Any] = json.loads(fixture.read_text(encoding="utf-8"))
        self._model_id: str = raw["model_id"]
        self._prompt_version: str = raw["prompt_version"]
        self._min_chars: int = raw["min_chars"]
        self._it_markers: tuple[str, ...] = tuple(_fold(m) for m in raw["it_markers"])
        self._job_markers: tuple[str, ...] = tuple(_fold(m) for m in raw["job_markers"])
        self._deposit_markers: tuple[str, ...] = tuple(_fold(m) for m in raw["deposit_markers"])
        self._devops_markers: tuple[str, ...] = tuple(_fold(m) for m in raw["devops_markers"])
        self._reads: dict[str, dict[str, Any]] = raw["reads"]

    def read(self, text: str) -> PostingReadResponse:
        folded = _fold(text.strip())
        if len(folded) < self._min_chars:
            return self._not_a_posting("too_short")
        if not any(marker in folded for marker in self._it_markers):
            return self._not_a_posting("not_it" if any(marker in folded for marker in self._job_markers) else "not_posting")
        if any(marker in folded for marker in self._deposit_markers):
            key = "fee"
        elif any(marker in folded for marker in self._devops_markers):
            key = "cloud"
        else:
            key = "backend"
        data = PostingReadData(
            is_posting=True,
            reason=None,
            **truncate_read(self._reads[key]),
            **self._trace(),
        )
        return PostingReadResponse(data=data)

    def _trace(self) -> dict[str, str]:
        return {"model_id": self._model_id, "prompt_version": self._prompt_version, "vocab_version": seed_version()}

    def _not_a_posting(self, reason: str) -> PostingReadResponse:
        data = PostingReadData(
            is_posting=False,
            reason=reason,  # type: ignore[arg-type]
            role=None,
            branch=None,
            level=None,
            skills=[],
            unrecognised=[],
            years_min=None,
            salary=None,
            salary_non_numeric=False,
            company_named=False,
            duties_described=False,
            title_level=None,
            contacts=[],
            contact_quotes=[],
            fee_mentions=[],
            collected=None,
            **self._trace(),
        )
        return PostingReadResponse(data=data)


class ModelPostingReader:
    """Cổng đọc bằng model (#232). Chưa cài đặt: từ chối với 503 `read_unavailable`."""

    def read(self, text: str) -> PostingReadResponse:
        raise PostingReadRefused(503, "read_unavailable", "Cổng đọc bằng model chưa cài đặt (#232).")


IMPLEMENTATIONS = {"fake": FakePostingReader, "model": ModelPostingReader}


def load_reader(environ: Mapping[str, str] = os.environ) -> PostingReader:
    """Dựng nguồn đọc theo biến `HAIDO_POSTING_READER` (`fake` mặc định, `model` ở production)."""
    name = environ.get(READER_ENV, "").strip() or DEFAULT_READER
    if name not in IMPLEMENTATIONS:
        known = ", ".join(sorted(IMPLEMENTATIONS))
        raise ValueError(f"{READER_ENV}={name!r} không phải nguồn đã biết. Chọn một trong: {known}.")
    return IMPLEMENTATIONS[name]()
