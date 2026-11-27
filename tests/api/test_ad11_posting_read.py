"""AD-11 — chữ của tin dán là tạm: nguồn đọc không giữ trạng thái, route không ghi log, không cache, không ghi đĩa (#230)."""

import builtins
import inspect
import logging
import re
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import pytest
from fastapi.testclient import TestClient
from posting_samples import (
    BACKEND_TEXT,
    FEE_TEXT,
    NOT_POSTING_TEXT,
    SENTINEL,
    SHORT_TEXT,
)

from haido_api import posting_read
from haido_api.main import create_app
from haido_api.posting_read import (
    FakePostingReader,
    ModelPostingReader,
    PostingReader,
    PostingReadRefused,
)
from haido_api.routes import posting as posting_route
from haido_api.schemas.posting import PostingReadData

URL = "/api/v1/posting-reads"
ALL_TEXTS = [BACKEND_TEXT, FEE_TEXT, NOT_POSTING_TEXT, SHORT_TEXT]


def test_ad11_nguon_gia_khong_giu_trang_thai_sau_khi_doc() -> None:
    reader = FakePostingReader()
    before = repr(sorted(vars(reader)))
    first = [reader.read(t) for t in ALL_TEXTS]
    assert repr(sorted(vars(reader))) == before
    assert SENTINEL not in repr(vars(reader))
    assert [reader.read(t) for t in ALL_TEXTS] == first  # đọc lại ra cùng kết quả: không có gì tích lại


def test_ad11_ket_qua_khong_chua_chu_dan_nguyen_van() -> None:
    reader = FakePostingReader()
    for text in ALL_TEXTS:
        assert SENTINEL not in reader.read(text).model_dump_json()
    # chỉ trích dẫn phí ngắn mới có chữ của tin, và bị chặn ở 120 ký tự
    assert all(len(q) <= 120 for q in reader.read(FEE_TEXT).data.fee_mentions)


@pytest.mark.parametrize("reader", [FakePostingReader(), ModelPostingReader()], ids=["fake", "model"])
def test_ad11_route_khong_ghi_log_chu_dan(reader: Any, caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.DEBUG)
    client = TestClient(create_app(posting_reader=reader), raise_server_exceptions=False)
    for text in ALL_TEXTS:
        client.post(URL, json={"text": text})
    client.post(URL, json={"text": SENTINEL, "extra": 1})  # sai hình
    client.post(URL, content=SENTINEL.encode(), headers={"content-type": "application/json"})  # không phải JSON
    assert caplog.records is not None
    assert SENTINEL not in caplog.text
    assert BACKEND_TEXT[:40] not in caplog.text


class _Collect(logging.Handler):
    """Gom mọi bản ghi, kể cả `exc_info`, của các logger mà một lỗi thoát khỏi route sẽ đi qua."""

    def __init__(self) -> None:
        super().__init__(level=logging.DEBUG)
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        if all(record is not seen for seen in self.records):  # cùng một bản ghi đi lên nhiều logger cha: chỉ đếm một lần
            self.records.append(record)

    def dump(self) -> str:
        """Mọi thứ mà một người đọc log sẽ thấy: thông điệp đã định dạng, traceback, và các trường của bản ghi."""
        formatter = logging.Formatter()
        return "\n".join(formatter.format(r) + repr(sorted(r.__dict__.items(), key=lambda kv: kv[0])) for r in self.records)


@contextmanager
def _capture() -> Iterator[_Collect]:
    handler = _Collect()
    loggers = [logging.getLogger(name) for name in ("", "uvicorn", "uvicorn.error", "haido_api", "haido_api.posting", "starlette")]
    saved = [(lg, lg.level) for lg in loggers]
    for lg in loggers:
        lg.addHandler(handler)
        lg.setLevel(logging.DEBUG)
    try:
        yield handler
    finally:
        for lg, level in saved:
            lg.removeHandler(handler)
            lg.setLevel(level)


class _TextInMessage(Exception):
    def __str__(self) -> str:
        return f"đọc hỏng ở chữ: {self.args[0]}"


def _raise_validation_error(text: str) -> Any:
    PostingReadData.model_validate({"is_posting": True, "reason": text})  # ValidationError chứa giá trị đầu vào


FAILURES = {
    "runtime": lambda t: RuntimeError(t),
    "value": lambda t: ValueError(f"không đọc được {t}"),
    "key": lambda t: KeyError(t),
    "custom_str": lambda t: _TextInMessage(t),
}


@pytest.mark.parametrize("kind", [*FAILURES, "chained", "validation", "refused_with_text", "refused_unknown_code"])
def test_ad11_nguon_loi_bat_ngo_khong_ghi_chu_dan_va_route_tu_xu_ly_502(kind: str) -> None:
    class _Boom:
        def read(self, text: str) -> Any:
            if kind == "validation":
                _raise_validation_error(text)
            if kind == "refused_with_text":
                raise PostingReadRefused(503, "read_unavailable", f"cổng lỗi: {text}")
            if kind == "refused_unknown_code":
                raise PostingReadRefused(418, "am_tra", f"ấm trà: {text}")
            if kind == "chained":
                try:
                    raise RuntimeError(text)
                except RuntimeError as inner:
                    raise RuntimeError("ngoài") from inner
            raise FAILURES[kind](text)

    # raise_server_exceptions=True (mặc định): nếu route để lỗi thoát ra ASGI thì TestClient ném lại, test này đỏ.
    client = TestClient(create_app(posting_reader=_Boom()))
    with _capture() as logs:
        resp = client.post(URL, json={"text": SENTINEL})
    expected = {"refused_with_text": (503, "read_unavailable")}.get(kind, (502, "read_failed"))
    assert (resp.status_code, resp.json()["error"]["code"]) == expected  # route xử lý, không phải 500 của máy chủ
    assert SENTINEL not in resp.text  # kể cả thông điệp của nguồn: máy chủ dùng câu chuẩn của mã lỗi
    dump = logs.dump()
    assert SENTINEL not in dump  # không ở message, args, exc_info, exc_text, ở bất kỳ logger nào kể cả uvicorn.error
    assert all(r.exc_info is None and r.exc_text is None for r in logs.records)  # không bao giờ ghi traceback


def test_ad11_chi_ghi_ten_kieu_cua_loi() -> None:
    class _Boom:
        def read(self, text: str) -> Any:
            raise _TextInMessage(text)

    with _capture() as logs:
        TestClient(create_app(posting_reader=_Boom())).post(URL, json={"text": SENTINEL})
    ours = [r for r in logs.records if r.name.startswith("haido_api")]
    assert len(ours) == 1 and ours[0].levelno == logging.ERROR
    assert "_TextInMessage" in ours[0].getMessage() and ours[0].args in ((), ("_TextInMessage",))


def test_ad11_hop_dong_cua_nguon_doc_noi_thong_diep_khong_mang_chu_cua_tin() -> None:
    doc = " ".join((inspect.getdoc(PostingReader) or "", inspect.getdoc(PostingReader.read) or "", inspect.getdoc(PostingReadRefused) or ""))
    doc = doc.casefold()
    assert "thông điệp" in doc and "chữ của tin" in doc and "502" in doc


def test_ad11_post_khong_vao_cache_response() -> None:
    app = create_app(response_cache=True)
    client = TestClient(app)
    for text in ALL_TEXTS:
        assert client.post(URL, json={"text": text}).status_code == 200
    assert len(app.state.response_cache) == 0


def test_ad11_khong_ghi_file_khi_doc(monkeypatch: pytest.MonkeyPatch) -> None:
    real_open = builtins.open

    def guarded(file: Any, mode: str = "r", *args: Any, **kwargs: Any) -> Any:
        if any(flag in str(mode) for flag in "wax+"):
            raise AssertionError(f"ghi file {file!r} khi đọc tin dán")
        return real_open(file, mode, *args, **kwargs)

    client = TestClient(create_app())
    monkeypatch.setattr(builtins, "open", guarded)
    for text in ALL_TEXTS:
        assert client.post(URL, json={"text": text}).status_code == 200


def test_ad11_ma_nguon_va_route_khong_co_dau_vet_luu_tru() -> None:
    """Nguồn đọc và route không chạm cơ sở dữ liệu hay đĩa. Đường ghi duy nhất sau này (AD-11: từ khóa, tần suất, lần thấy cuối
    của cụm chưa nhận diện ở FR-29; sự kiện ẩn danh bốn trường ở FR-26) nằm ở một mô-đun riêng mà route gọi với đúng các trường
    đó, không bao giờ với chữ của tin; test này vẫn giữ nguyên cho route và nguồn đọc, và chỉ đổi khi mô-đun ghi đó có mặt."""
    for module in (posting_read, posting_route):
        source = inspect.getsource(module)
        for banned in ("sqlalchemy", "open(", "write_text", "write_bytes", "tempfile", "print(", "traceback"):
            assert banned not in source, f"{module.__name__} có `{banned}`"


def test_ad11_nguon_doc_khong_ghi_log_con_route_chi_ghi_ten_kieu() -> None:
    assert "logging" not in inspect.getsource(posting_read)
    route_source = inspect.getsource(posting_route)
    assert "exc_info" not in route_source and ".exception(" not in route_source
    log_calls = re.findall(r"logger\.\w+\(.*\)", route_source)
    assert log_calls, "route phải ghi một dòng cho lỗi của nguồn đọc"
    for call in log_calls:
        assert "type(" in call and "__name__" in call and "exc" not in call.replace("type(exc)", ""), call
