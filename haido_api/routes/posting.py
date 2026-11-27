"""Route đọc chữ tin dán (#230). Route chỉ chuyển chữ cho nguồn đọc rồi trả kết quả (AD-5).

AD-11: không ghi chữ dán vào đâu, kể cả nhật ký và lỗi. Mọi lỗi của nguồn đọc được bắt tại đây: chỉ ghi tên kiểu của lỗi (không thông
điệp, không vết gọi hàm, vì thông điệp của một ngoại lệ có thể mang chữ của tin), trả 502 `read_failed`, và không ném lại lên máy chủ ASGI.

AD-9: thân bị chặn cỡ trước khi phân tích, như `haido_api/uploads.py` làm với CV: `Content-Length` vượt `posting_read.max_body_bytes`
của `config/rules.toml` bị từ chối ngay; thân không khai độ dài (hoặc khai gian) bị dừng lúc đọc khi vượt trần. Chữ dài hơn 20.000 ký tự
(FR-26) trong thân nhỏ hơn trần byte cũng là 413. Cả hai: 413 `text_too_long`, câu nêu giới hạn, nguồn đọc không được gọi. Trần tốc độ
theo IP (`rate_limited`) và câu chữ trên màn là của #231; nguồn đọc thật là của #232. Chọn nguồn bằng `HAIDO_POSTING_READER` (xem
`haido_api.posting_read`).
"""

import functools
import logging
from collections.abc import Callable, Coroutine
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute

from haido_api.errors import error_response
from haido_api.posting_read import PostingReader, PostingReadRefused
from haido_api.schemas.error import ErrorEnvelope
from haido_api.schemas.posting import (
    POSTING_READ_MESSAGES,
    PostingReadRequest,
    PostingReadResponse,
)
from haido_core.config import load_rules

logger = logging.getLogger("haido_api.posting")

_MAX_LENGTH_DIGITS = 12  # dài hơn thì chắc chắn vượt mọi trần, khỏi gọi int() trên chuỗi khổng lồ


@functools.cache
def _max_body_bytes() -> int:
    return load_rules().posting_max_body_bytes


def _too_long() -> Response:
    # Đóng kết nối: để trình duyệt thấy lỗi thay vì bị reset khi ta từ chối trước khi đọc hết thân.
    return error_response(413, "text_too_long", POSTING_READ_MESSAGES["text_too_long"], headers={"Connection": "close"})


def _text_too_long(exc: RequestValidationError) -> bool:
    return any(e.get("type") == "string_too_long" and tuple(e.get("loc", ()))[-1:] == ("text",) for e in exc.errors())


class _BodyGuard:
    """Đếm byte của thân lúc đọc; vượt trần thì giả vờ client ngắt, để lớp đọc thân của FastAPI dừng ngay."""

    def __init__(self, request: Request, limit: int) -> None:
        self.exceeded = False
        self._receive = request.receive
        self._limit = limit
        self._received = 0

    async def receive(self) -> Any:
        message = await self._receive()
        if message["type"] == "http.request":
            self._received += len(message.get("body", b""))
            if self._received > self._limit:
                self.exceeded = True
                return {"type": "http.disconnect"}
        return message


class _PostingReadRoute(APIRoute):
    """Route của `posting-reads`: chặn cỡ thân trước khi FastAPI phân tích JSON (AD-9)."""

    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        original = super().get_route_handler()

        async def handler(request: Request) -> Response:
            limit = _max_body_bytes()
            declared = request.headers.get("content-length", "")
            if declared.isascii() and declared.isdigit() and (len(declared) > _MAX_LENGTH_DIGITS or int(declared) > limit):
                return _too_long()
            guard = _BodyGuard(request, limit)
            try:
                return await original(Request(request.scope, guard.receive))
            except RequestValidationError as exc:
                if guard.exceeded or _text_too_long(exc):
                    return _too_long()
                raise
            except Exception:
                if guard.exceeded:  # lớp đọc thân của FastAPI đổi ngắt kết nối thành 400
                    return _too_long()
                raise

        return handler


router = APIRouter(
    prefix="/api/v1",
    tags=["posting"],
    route_class=_PostingReadRoute,
    responses={
        413: {
            "model": ErrorEnvelope,
            "description": (
                "Chữ dán vượt giới hạn cỡ (`text_too_long`): dài hơn 20.000 ký tự (FR-26), hoặc thân vượt trần byte của "
                "`posting_read.max_body_bytes`. Bị từ chối trước khi phân tích và trước khi đọc (AD-9); câu lỗi nêu giới hạn."
            ),
        },
        422: {
            "model": ErrorEnvelope,
            "description": "Thân sai hình: thiếu `text`, `text` không phải chuỗi, hoặc có trường lạ (`invalid_query`).",
        },
        429: {
            "model": ErrorEnvelope,
            "description": "Quá nhiều lần đọc trong một khoảng thời gian (`rate_limited`, #231).",
        },
        500: {"model": ErrorEnvelope, "description": "Lỗi máy chủ (`internal_error`, `invalid_response`)."},
        502: {
            "model": ErrorEnvelope,
            "description": (
                "Cổng model trả kết quả không dùng được, hoặc nguồn đọc gặp lỗi (`read_failed`). Route chỉ ghi tên kiểu của lỗi (AD-11)."
            ),
        },
        503: {
            "model": ErrorEnvelope,
            "description": "Chưa đọc được tin dán (`read_unavailable`): cổng model chưa sẵn sàng (#232).",
        },
        504: {"model": ErrorEnvelope, "description": "Cổng model quá thời gian chờ (`read_timeout`, #232, #238)."},
    },
)


def _reader(request: Request) -> PostingReader:
    reader: PostingReader = request.app.state.posting_reader
    return reader


@router.post(
    "/posting-reads",
    response_model=PostingReadResponse,
    summary="Đọc một tin tuyển dụng dán vào",
)
def post_posting_read(
    body: PostingReadRequest,
    reader: Annotated[PostingReader, Depends(_reader)],
) -> PostingReadResponse:
    """Đọc chữ dán qua cổng model đúng một lần và trả các sự kiện đóng đã trích; không lưu gì (AD-11).

    Response là `{data}`, không có `meta`: không có số liệu thị trường nào trong đó. Chữ không phải tin tuyển dụng IT, tin tuyển dụng
    ngoài IT hoặc chữ quá ngắn trả 200 với `is_posting = false` và `reason` (`not_posting`, `not_it`, `too_short`). Chữ quá 20.000
    ký tự hoặc thân quá trần byte: 413 `text_too_long`. Các lỗi còn lại của đường thật nằm ở mô tả các mã 429, 502, 503, 504. Bước hai là
    `GET /api/v1/posting-check`, chỉ nhận mã và số rút từ kết quả này; trích dẫn nguyên văn (`unrecognised`, `fee_mentions`,
    `contact_quotes`) và link tin thu thập (`collected.url`) chỉ hiện trên màn, không đi lên bước hai.
    """
    try:
        return reader.read(body.text)
    except PostingReadRefused:
        raise
    except Exception as exc:  # noqa: BLE001 - AD-11: mọi lỗi của nguồn đọc đều thành 502, không lỗi nào thoát lên máy chủ
        # AD-11: thông điệp của ngoại lệ (kể cả ValidationError) có thể mang chữ của tin: chỉ ghi tên kiểu, không đính vết gọi hàm.
        logger.error("posting_read_failed type=%s", type(exc).__name__)
    # Ném ngoài khối `except` để không kéo theo ngoại lệ gốc (và chữ trong nó) làm `__context__`.
    raise PostingReadRefused(502, "read_failed", "Nguồn đọc gặp lỗi.")
