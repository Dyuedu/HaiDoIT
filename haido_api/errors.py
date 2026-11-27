"""Đưa mọi lỗi về hình chuẩn `{"error": {"code", "message", "snapshot_date"}}`, tiếng Việt.

Kể cả lỗi 422 mặc định của FastAPI (`{"detail": [...]}`) và 404/405 của Starlette.
Thông điệp không lặp lại giá trị người dùng gửi lên.
"""

import logging
from collections.abc import Mapping, Sequence
from datetime import date
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from haido_api.market_source import CheckUnavailable, UnknownCell, UnknownSkill
from haido_api.posting_read import PostingReadRefused
from haido_api.schemas.error import ErrorBody, ErrorEnvelope
from haido_api.schemas.posting import POSTING_READ_ERRORS, POSTING_READ_MESSAGES
from haido_api.uploads import UploadRejected
from haido_core.extract import AdvisorGenerationError, UnreadableCvError

logger = logging.getLogger("haido_api")


class MissingConsentError(ValueError):
    """Người dùng chưa đồng ý điều kiện gửi văn bản CV tới dịch vụ AI."""

    def __init__(self, message: str = "Hãy đánh dấu ô đồng ý trước khi phân tích CV.") -> None:
        super().__init__(message)
        self.message = message

_HTTP_CODES: dict[int, tuple[str, str]] = {
    404: ("not_found", "Không có đường dẫn này."),
    405: ("method_not_allowed", "Đường dẫn này không hỗ trợ phương thức đã dùng."),
}


def error_response(
    status_code: int,
    code: str,
    message: str,
    *,
    snapshot_date: date | None = None,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    body = ErrorEnvelope(error=ErrorBody(code=code, message=message, snapshot_date=snapshot_date))
    return JSONResponse(status_code=status_code, content=body.model_dump(mode="json"), headers=headers)


def invalid_query_message(errors: Sequence[Any]) -> str:
    """Câu tiếng Việt cho lỗi 422, chỉ nêu tên tham số."""
    thieu: list[str] = []
    sai: list[str] = []
    la = False
    for err in errors:
        if err.get("type") == "extra_forbidden":
            la = True  # không nêu tên: khóa lạ do người gửi đặt, có thể là chữ của tin dán (AD-11)
            continue
        name = str(err.get("loc", ("?",))[-1])
        (thieu if err.get("type") == "missing" else sai).append(name)
    parts = []
    if thieu:
        parts.append("thiếu tham số " + ", ".join(dict.fromkeys(thieu)))
    if sai:
        parts.append("tham số sai định dạng: " + ", ".join(dict.fromkeys(sai)))
    if la:
        parts.append("có trường không có trong hợp đồng")
    return "Truy vấn không hợp lệ: " + "; ".join(parts or ["không đọc được tham số"]) + "."


async def _unknown_cell(_: Request, exc: UnknownCell) -> JSONResponse:
    return error_response(404, "unknown_cell", exc.message, snapshot_date=exc.snapshot_date)


async def _unknown_skill(_: Request, exc: UnknownSkill) -> JSONResponse:
    return error_response(404, "unknown_skill", exc.message)


async def _check_unavailable(_: Request, exc: CheckUnavailable) -> JSONResponse:
    return error_response(503, "check_unavailable", exc.message)


async def _posting_read_refused(_: Request, exc: PostingReadRefused) -> JSONResponse:
    # AD-11: câu và HTTP lấy từ bảng của mã lỗi, không bao giờ từ thông điệp của nguồn đọc (nó có thể lỡ mang chữ của tin);
    # mã không có trong bảng là lỗi của nguồn, trả như `read_failed`. Ở đây không ghi gì.
    code = exc.code if exc.code in POSTING_READ_ERRORS else "read_failed"
    return error_response(POSTING_READ_ERRORS[code], code, POSTING_READ_MESSAGES[code])


async def _upload_rejected(_: Request, exc: UploadRejected) -> JSONResponse:
    # Đóng kết nối: để trình duyệt thấy lỗi thay vì bị reset khi ta từ chối trước khi đọc hết thân.
    return error_response(exc.status_code, exc.code, exc.message, headers={"Connection": "close"})


async def _missing_consent(_: Request, exc: MissingConsentError) -> JSONResponse:
    return error_response(400, "cv_consent_required", exc.message)


async def _unreadable_cv(_: Request, exc: UnreadableCvError) -> JSONResponse:
    return error_response(422, "cv_unreadable", exc.message)


async def _advisor_failed(_: Request, exc: AdvisorGenerationError) -> JSONResponse:
    return error_response(502, "advisor_unavailable", str(exc))


async def _invalid_query(_: Request, exc: RequestValidationError) -> JSONResponse:
    return error_response(422, "invalid_query", invalid_query_message(exc.errors()))


async def _http_error(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    code, message = _HTTP_CODES.get(exc.status_code, ("http_error", "Yêu cầu không xử lý được."))
    return error_response(exc.status_code, code, message, headers=exc.headers)


async def _invalid_response(
    request: Request, exc: ResponseValidationError | ValidationError
) -> JSONResponse:
    """Response của route, hoặc model nguồn dựng ra trong lúc xử lý request, sai hợp đồng."""
    where = sorted({".".join(str(p) for p in e.get("loc", ())) for e in exc.errors()})
    logger.error("response_invalid path=%s loc=%s", request.url.path, where)
    return error_response(
        500, "invalid_response", "Máy chủ tạo ra dữ liệu sai hợp đồng. Lỗi đã được ghi lại."
    )


async def _internal_error(request: Request, exc: Exception) -> JSONResponse:
    logger.error("internal_error path=%s type=%s", request.url.path, type(exc).__name__)
    return error_response(500, "internal_error", "Máy chủ gặp lỗi ngoài dự kiến.")


def install_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(UnknownCell, _unknown_cell)
    app.add_exception_handler(UnknownSkill, _unknown_skill)
    app.add_exception_handler(CheckUnavailable, _check_unavailable)
    app.add_exception_handler(UploadRejected, _upload_rejected)
    app.add_exception_handler(PostingReadRefused, _posting_read_refused)
    app.add_exception_handler(MissingConsentError, _missing_consent)
    app.add_exception_handler(UnreadableCvError, _unreadable_cv)
    app.add_exception_handler(AdvisorGenerationError, _advisor_failed)
    app.add_exception_handler(RequestValidationError, _invalid_query)
    app.add_exception_handler(StarletteHTTPException, _http_error)
    app.add_exception_handler(ResponseValidationError, _invalid_response)
    app.add_exception_handler(ValidationError, _invalid_response)
    app.add_exception_handler(Exception, _internal_error)
