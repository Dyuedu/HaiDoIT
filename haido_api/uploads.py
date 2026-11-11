"""Nhận CV tải lên chỉ trong bộ nhớ (AD-11, #140): kiểm cỡ và kiểu trước khi đọc thân, không có file tạm.

Client gửi `multipart/form-data` với đúng một file tên `cv`. Thứ tự kiểm:

1. Trước khi đọc thân: `Content-Type` phải là multipart có boundary (415), `Content-Length` phải có
   (411) và không vượt `cv_max_bytes` cộng phần phụ trội của multipart (413).
2. Đọc thân từng khối bằng `request.stream()` và đưa cho bộ phân tích cấp thấp `MultipartParser`.
   Không dùng bộ phân tích form cấp cao của Starlette hay python-multipart: chúng ghi file lớn ra đĩa.
3. Khi header của một part xong, trước khi nhận dữ liệu của nó: part phải là file `cv` duy nhất và
   kiểu khai báo phải nằm trong `cv_types` (415). Thiếu file `cv` hoặc có hai file trở lên thì 400.
4. Đếm byte lúc đọc: vượt `cv_max_bytes` (header khai gian hoặc không có độ dài) thì dừng đọc ngay (413).
   Byte đầu phải khớp chữ ký của kiểu đã khai (415).

Lỗi đi qua `UploadRejected`, do `errors.install_error_handlers` đổi sang hình lỗi chuẩn. Thông điệp
tiếng Việt, nêu giới hạn và kiểu được nhận, không bao giờ chứa nội dung file, tên file hay kiểu client khai.
"""

import unicodedata
from dataclasses import dataclass, field
from functools import lru_cache

from python_multipart.exceptions import FormParserError
from python_multipart.multipart import MultipartParser, parse_options_header
from starlette.requests import ClientDisconnect, Request

from haido_core.config import CV_SIGNATURES, CV_TYPE_NAMES, RulesConfig, load_rules

FIELD_NAME = "cv"
"""Tên part chứa file CV."""

MULTIPART_OVERHEAD = 8 * 1024
"""Phần phụ trội cho phép ngoài `cv_max_bytes`: boundary, header của part, các trường chữ (consent...)."""

_MAX_BOUNDARY = 70  # RFC 2046
_MIB = 1024 * 1024
_MAX_LENGTH_DIGITS = 20  # dài hơn thì chắc chắn vượt mọi trần, khỏi gọi int() trên chuỗi khổng lồ
_MAX_FILENAME = 255


class UploadRejected(Exception):
    """Tải lên bị từ chối. `errors.py` đổi thành response `{error: {code, message, snapshot_date}}`."""

    def __init__(self, status_code: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message


@dataclass(frozen=True, slots=True)
class CvUpload:
    content: bytes
    filename: str
    content_type: str


@lru_cache(maxsize=1)
def _default_rules() -> RulesConfig:
    return load_rules()


def _size_text(max_bytes: int) -> str:
    mib = max_bytes / _MIB
    return f"{mib:g} MB".replace(".", ",") if mib >= 1 else f"{max_bytes // 1024} KB"


def _types_text(types: tuple[str, ...]) -> str:
    names = [CV_TYPE_NAMES.get(t, t) for t in types]
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " hoặc " + names[-1]


class _Reject:
    """Dựng các lỗi, mỗi thông điệp kèm một câu nêu kiểu được nhận và giới hạn cỡ."""

    def __init__(self, rules: RulesConfig) -> None:
        self._note = f"Chỉ nhận tệp {_types_text(rules.cv_types)}, tối đa {_size_text(rules.cv_max_bytes)}."

    def _make(self, status: int, code: str, text: str) -> UploadRejected:
        return UploadRejected(status, code, f"{text} {self._note}")

    def not_multipart(self) -> UploadRejected:
        return self._make(
            415, "cv_unsupported_type", f"Yêu cầu phải gửi dạng multipart/form-data kèm boundary, với một tệp tên {FIELD_NAME}."
        )

    def length_required(self) -> UploadRejected:
        return self._make(411, "length_required", "Yêu cầu phải có Content-Length để biết cỡ tệp trước khi đọc.")

    def bad_length(self) -> UploadRejected:
        return self._make(400, "cv_invalid_upload", "Content-Length phải là số nguyên không âm.")

    def no_file(self) -> UploadRejected:
        return self._make(400, "cv_invalid_upload", "Bạn chưa chọn tệp CV.")

    def too_large(self) -> UploadRejected:
        return self._make(413, "cv_too_large", "Tệp CV lớn hơn mức cho phép.")

    def wrong_type(self) -> UploadRejected:
        return self._make(415, "cv_unsupported_type", "Loại tệp không được nhận.")

    def wrong_content(self) -> UploadRejected:
        return self._make(415, "cv_unsupported_type", "Nội dung tệp không khớp định dạng đã khai.")

    def invalid(self) -> UploadRejected:
        return self._make(400, "cv_invalid_upload", f"Phải gửi đúng một tệp trong phần tên {FIELD_NAME}.")

    def malformed(self) -> UploadRejected:
        return self._make(400, "cv_invalid_upload", "Nội dung tải lên không đầy đủ hoặc sai định dạng.")


def _boundary(request: Request) -> bytes | None:
    """Boundary của request multipart, hoặc None khi không phải multipart hay thiếu boundary."""
    media, params = parse_options_header(request.headers.get("content-type", ""))
    raw = {k.lower(): v for k, v in params.items()}.get(b"boundary", b"")
    if media.lower() != b"multipart/form-data" or not raw or len(raw) > _MAX_BOUNDARY:
        return None
    return raw


def _declared_length(request: Request, reject: _Reject) -> int:
    raw = request.headers.get("content-length")
    if raw is None:
        raise reject.length_required()
    if not raw.isascii() or not raw.isdigit():
        raise reject.bad_length()
    if len(raw) > _MAX_LENGTH_DIGITS:
        raise reject.too_large()
    return int(raw)


def _clean_filename(name: str) -> str:
    """Chỉ giữ phần tên, bỏ ký tự điều khiển và bidi, cắt còn 255 ký tự; rỗng thì dùng "cv"."""
    base = name.replace("\\", "/").rsplit("/", 1)[-1]
    kept = "".join(c for c in base if unicodedata.category(c) not in {"Cc", "Cf"})
    return kept[:_MAX_FILENAME] or "cv"


@dataclass
class _Reader:
    """Trạng thái của một lần đọc; các hàm `on_*` là callback của `MultipartParser`."""

    rules: RulesConfig
    reject: _Reject
    buffer: bytearray = field(default_factory=bytearray)
    filename: str = ""
    content_type: str = ""
    collecting: bool = False
    signature_checked: bool = False
    file_parts: int = 0
    finished: bool = False
    ended: bool = False
    _field: bytearray = field(default_factory=bytearray)
    _value: bytearray = field(default_factory=bytearray)
    _headers: dict[bytes, bytes] = field(default_factory=dict)

    def on_part_begin(self) -> None:
        self._headers = {}
        self.collecting = False

    def on_header_begin(self) -> None:
        self._field.clear()
        self._value.clear()

    def on_header_field(self, data: bytes, start: int, end: int) -> None:
        self._field += data[start:end]

    def on_header_value(self, data: bytes, start: int, end: int) -> None:
        self._value += data[start:end]

    def on_header_end(self) -> None:
        self._headers[bytes(self._field).lower()] = bytes(self._value)

    def on_headers_finished(self) -> None:
        """Quyết định nhận hay bỏ part, trước khi dữ liệu của part đến."""
        _, params = parse_options_header(self._headers.get(b"content-disposition", b""))
        if b"filename" not in params:
            if params.get(b"name") == FIELD_NAME.encode():
                raise self.reject.invalid()  # phần `cv` phải là một file, không phải trường chữ
            return  # trường chữ khác (đồng ý...) được bỏ qua, dữ liệu của nó không được giữ
        self.file_parts += 1
        if self.file_parts > 1 or params.get(b"name") != FIELD_NAME.encode():
            raise self.reject.invalid()
        if not params[b"filename"]:
            raise self.reject.no_file()  # form gửi đi khi chưa chọn tệp: filename rỗng
        declared, _ = parse_options_header(self._headers.get(b"content-type", b""))
        content_type = declared.decode("latin-1").lower()
        if content_type not in self.rules.cv_types:
            raise self.reject.wrong_type()
        self.content_type = content_type
        self.filename = _clean_filename(params[b"filename"].decode("utf-8", errors="replace"))
        self.collecting = True

    def on_part_data(self, data: bytes, start: int, end: int) -> None:
        if not self.collecting:
            return
        if len(self.buffer) + (end - start) > self.rules.cv_max_bytes:
            raise self.reject.too_large()
        self.buffer += data[start:end]
        signature = CV_SIGNATURES.get(self.content_type, b"")
        if not self.signature_checked and len(self.buffer) >= len(signature):
            self._check_signature()

    def on_end(self) -> None:
        self.ended = True

    def on_part_end(self) -> None:
        if not self.collecting:
            return
        if not self.signature_checked:
            self._check_signature()  # file ngắn hơn chữ ký
        self.collecting = False
        self.finished = True

    def _check_signature(self) -> None:
        self.signature_checked = True
        signature = CV_SIGNATURES.get(self.content_type)
        if signature is None or not self.buffer.startswith(signature):
            raise self.reject.wrong_content()


async def read_cv_upload(request: Request, rules: RulesConfig | None = None) -> CvUpload:
    """Đọc file CV từ request multipart, chỉ trong bộ nhớ. Raise `UploadRejected` khi không hợp lệ."""
    rules = rules if rules is not None else _default_rules()
    reject = _Reject(rules)

    boundary = _boundary(request)
    if boundary is None:
        raise reject.not_multipart()
    ceiling = rules.cv_max_bytes + MULTIPART_OVERHEAD
    if _declared_length(request, reject) > ceiling:
        raise reject.too_large()

    reader = _Reader(rules, reject)
    parser = MultipartParser(
        boundary,
        {
            "on_part_begin": reader.on_part_begin,
            "on_header_begin": reader.on_header_begin,
            "on_header_field": reader.on_header_field,
            "on_header_value": reader.on_header_value,
            "on_header_end": reader.on_header_end,
            "on_headers_finished": reader.on_headers_finished,
            "on_part_data": reader.on_part_data,
            "on_part_end": reader.on_part_end,
            "on_end": reader.on_end,
        },
    )
    received = 0
    try:
        async for chunk in request.stream():
            received += len(chunk)
            if received > ceiling:  # Content-Length khai gian hoặc không đúng thực tế
                raise reject.too_large()
            parser.write(chunk)
        parser.finalize()
    except FormParserError as exc:
        raise reject.malformed() from exc
    except ClientDisconnect as exc:
        raise reject.malformed() from exc

    if not reader.ended:  # thân bị cắt: chưa thấy boundary đóng
        raise reject.malformed()
    if reader.file_parts == 0:
        raise reject.invalid()
    if not reader.finished:
        raise reject.malformed()
    return CvUpload(bytes(reader.buffer), reader.filename, reader.content_type)
