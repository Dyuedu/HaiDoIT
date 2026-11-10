"""AD-11 (#140) — tải CV chỉ qua bộ nhớ: kiểm cỡ và kiểu trước khi đọc thân, không để file tạm.

App FastAPI ở đây chỉ dựng trong test; chưa có route CV thật (thuộc #194/#195/#196). Các test gọi
thẳng ASGI để đếm số khối thân request mà helper đã đọc, vì TestClient đọc hết thân rồi mới gửi.
"""

import asyncio
import builtins
import dataclasses
import hashlib
import io
import json
import os
import tempfile
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from haido_api.errors import install_error_handlers
from haido_api.uploads import MULTIPART_OVERHEAD, read_cv_upload
from haido_core.config import RulesConfig, load_rules

PDF = "application/pdf"
DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
MIB = 1024 * 1024
LIMIT = 5 * MIB
BOUNDARY = "haidoboundary7d3f"
CONTENT_TYPE = f"multipart/form-data; boundary={BOUNDARY}"
PDF_HEAD = b"%PDF-1.7\n"
DOCX_HEAD = b"PK\x03\x04"


def _app(rules: RulesConfig | None = None) -> FastAPI:
    app = FastAPI()
    install_error_handlers(app)

    @app.post("/cv")
    async def tai_cv(request: Request) -> dict[str, Any]:
        cv = await read_cv_upload(request, rules=rules)
        return {
            "size": len(cv.content),
            "sha256": hashlib.sha256(cv.content).hexdigest(),
            "filename": cv.filename,
            "content_type": cv.content_type,
        }

    @app.post("/cv-form")
    async def tai_cv_bang_form(request: Request) -> dict[str, int]:
        """Đối chứng: đường mặc định của Starlette phải chạm file tạm khi file lớn."""
        form = await request.form()
        return {"fields": len(form)}

    return app


def _file(data: bytes, *, name: str = "cv", filename: str = "cv.pdf", ctype: str | None = PDF) -> bytes:
    head = f'--{BOUNDARY}\r\nContent-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'
    if ctype is not None:
        head += f"Content-Type: {ctype}\r\n"
    return head.encode() + b"\r\n" + data + b"\r\n"


def _field(name: str, value: str) -> bytes:
    head = f'--{BOUNDARY}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n'
    return head.encode() + value.encode() + b"\r\n"


def _body(*parts: bytes) -> bytes:
    return b"".join(parts) + f"--{BOUNDARY}--\r\n".encode()


def _pdf(size: int) -> bytes:
    return PDF_HEAD + b"x" * (size - len(PDF_HEAD))


def _chunks(body: bytes, size: int = 64 * 1024) -> list[bytes]:
    return [body[i : i + size] for i in range(0, len(body), size)] or [b""]


@dataclass
class Exchange:
    status: int
    json: dict[str, Any]
    raw: bytes
    consumed: int
    total: int
    headers: dict[str, str] = dataclasses.field(default_factory=dict)


def _call(
    app: FastAPI,
    chunks: Iterable[bytes],
    *,
    content_type: str | None = CONTENT_TYPE,
    content_length: object = ...,
    path: str = "/cv",
    disconnect: bool = False,
) -> Exchange:
    """Gọi ASGI; `content_length=...` nghĩa là khai đúng tổng cỡ, `None` nghĩa là không gửi header."""
    pending = list(chunks)
    total = len(pending)
    headers: list[tuple[bytes, bytes]] = []
    if content_type is not None:
        headers.append((b"content-type", content_type.encode()))
    length = sum(len(c) for c in pending) if content_length is ... else content_length
    if length is not None:
        headers.append((b"content-length", str(length).encode()))
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "root_path": "",
        "headers": headers,
        "client": ("testclient", 5000),
        "server": ("testserver", 80),
    }
    sent: list[dict[str, Any]] = []

    async def receive() -> dict[str, Any]:
        if not pending:
            return {"type": "http.disconnect"}
        body = pending.pop(0)
        return {"type": "http.request", "body": body, "more_body": bool(pending) or disconnect}

    async def send(message: dict[str, Any]) -> None:
        sent.append(message)

    asyncio.run(app(scope, receive, send))
    start = next(m for m in sent if m["type"] == "http.response.start")
    raw = b"".join(m.get("body", b"") for m in sent if m["type"] == "http.response.body")
    headers_out = {k.decode().lower(): v.decode() for k, v in start["headers"]}
    return Exchange(start["status"], json.loads(raw), raw, total - len(pending), total, headers_out)


def _assert_error(ex: Exchange, status: int, code: str | None = None) -> str:
    assert ex.status == status, ex.raw
    assert set(ex.json) == {"error"}
    assert set(ex.json["error"]) == {"code", "message", "snapshot_date"}
    assert ex.json["error"]["snapshot_date"] is None
    if code is not None:
        assert ex.json["error"]["code"] == code
    return ex.json["error"]["message"]


_WRITE_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC


def _forbid_disk_writes(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mọi lần mở file để ghi hay tạo mới đều raise; mở để đọc vẫn được."""
    real_open = builtins.open
    real_os_open = os.open

    def guarded_open(file: Any, mode: str = "r", *a: Any, **k: Any) -> Any:
        if any(c in mode for c in "wax+"):
            raise AssertionError(f"open ghi file: mode={mode}")
        return real_open(file, mode, *a, **k)

    def guarded_os_open(path: Any, flags: int, *a: Any, **k: Any) -> Any:
        if flags & _WRITE_FLAGS:
            raise AssertionError("os.open ghi file")
        return real_os_open(path, flags, *a, **k)

    def no_write(*_a: object, **_k: object) -> None:
        raise AssertionError("Path.write_* bị gọi")

    monkeypatch.setattr(builtins, "open", guarded_open)
    monkeypatch.setattr(io, "open", guarded_open)
    monkeypatch.setattr(os, "open", guarded_os_open)
    monkeypatch.setattr(Path, "write_bytes", no_write)
    monkeypatch.setattr(Path, "write_text", no_write)


def _private_tmp(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    private = tmp_path / "rieng"
    private.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(private))
    return private


def _forbid_temp_files(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    calls: list[str] = []

    def make(name: str):
        def boom(*_a: object, **_k: object) -> None:
            calls.append(name)
            raise AssertionError(f"tempfile.{name} bị gọi")

        return boom

    for name in ("SpooledTemporaryFile", "TemporaryFile", "NamedTemporaryFile", "mkstemp", "mkdtemp", "TemporaryDirectory"):
        monkeypatch.setattr(tempfile, name, make(name))
    return calls


# --------------------------------------------------------------------------- chấp nhận, không file tạm


def test_ad11_cv_dung_5_mib_duoc_nhan_va_khong_co_file_tam_moi(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    app = _app()
    cv = _pdf(LIMIT)
    assert len(cv) == 5 * 1024 * 1024
    client = TestClient(app)
    private = _private_tmp(monkeypatch, tmp_path)
    calls = _forbid_temp_files(monkeypatch)
    _forbid_disk_writes(monkeypatch)

    resp = client.post("/cv", files={"cv": ("cv.pdf", cv, PDF)})

    assert resp.status_code == 200, resp.text
    assert resp.json() == {
        "size": LIMIT,
        "sha256": hashlib.sha256(cv).hexdigest(),
        "filename": "cv.pdf",
        "content_type": PDF,
    }
    assert calls == []
    assert list(private.iterdir()) == []


def test_ad11_cv_5_mib_qua_asgi_tung_khoi_khong_cham_file_tam(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    app = _app()
    cv = _pdf(LIMIT)
    private = _private_tmp(monkeypatch, tmp_path)
    calls = _forbid_temp_files(monkeypatch)
    _forbid_disk_writes(monkeypatch)

    ex = _call(app, _chunks(_body(_file(cv)), 7001))

    assert ex.status == 200, ex.raw
    assert ex.json["sha256"] == hashlib.sha256(cv).hexdigest()
    assert ex.consumed == ex.total
    assert calls == []
    assert list(private.iterdir()) == []


def test_ad11_doi_chung_duong_form_mac_dinh_cham_file_tam_voi_cv_5_mib(monkeypatch: pytest.MonkeyPatch) -> None:
    """Chứng minh cách chặn file tạm ở trên có hiệu lực: đường `request.form()` bị chặn đúng chỗ."""
    app = _app()
    client = TestClient(app, raise_server_exceptions=False)
    calls = _forbid_temp_files(monkeypatch)

    resp = client.post("/cv-form", files={"cv": ("cv.pdf", _pdf(LIMIT), PDF)})

    assert resp.status_code == 500
    assert calls


def test_ad11_cv_docx_duoc_nhan() -> None:
    app = _app()
    docx = DOCX_HEAD + b"\x14\x00\x00\x00" + b"w" * 2000

    ex = _call(app, _chunks(_body(_file(docx, filename="cv.docx", ctype=DOCX))))

    assert ex.status == 200, ex.raw
    assert ex.json["content_type"] == DOCX
    assert ex.json["filename"] == "cv.docx"
    assert ex.json["sha256"] == hashlib.sha256(docx).hexdigest()


def test_ad11_cv_nhan_khi_co_them_truong_chu_va_thu_tu_bat_ky() -> None:
    app = _app()
    cv = _pdf(3000)

    ex = _call(app, _chunks(_body(_field("consent", "true"), _file(cv), _field("note", "x"))))

    assert ex.status == 200, ex.raw
    assert ex.json["sha256"] == hashlib.sha256(cv).hexdigest()


def test_ad11_cv_chia_khoi_nho_den_tung_byte_van_dung() -> None:
    app = _app()
    cv = _pdf(900)

    ex = _call(app, _chunks(_body(_file(cv)), 1))

    assert ex.status == 200, ex.raw
    assert ex.json["sha256"] == hashlib.sha256(cv).hexdigest()


def test_ad11_ten_file_chi_giu_phan_ten_khong_giu_duong_dan() -> None:
    app = _app()

    ex = _call(app, _chunks(_body(_file(_pdf(500), filename="C:\\Users\\an\\Desktop\\cv an.pdf"))))

    assert ex.status == 200, ex.raw
    assert ex.json["filename"] == "cv an.pdf"


# --------------------------------------------------------------------------- cỡ, trước và trong khi đọc


def test_ad11_content_length_vuot_tran_thi_413_ma_chua_doc_than() -> None:
    app = _app()
    body = _body(_file(_pdf(LIMIT + 2 * MULTIPART_OVERHEAD)))  # ngoài cửa sổ phụ trội của multipart

    ex = _call(app, _chunks(body))

    message = _assert_error(ex, 413)
    assert ex.consumed == 0
    assert "tối đa 5 MB" in message


def test_ad11_content_length_khai_lon_nhung_than_nho_van_bi_chan_truoc_khi_doc() -> None:
    app = _app()

    ex = _call(app, [b"khong doc"], content_length=50 * MIB)

    _assert_error(ex, 413)
    assert ex.consumed == 0


def test_ad11_content_length_nho_gia_ma_than_lon_thi_413_va_dung_doc_ngay() -> None:
    app = _app()
    body = _body(_file(_pdf(LIMIT + 3 * MIB)))
    chunks = _chunks(body, 64 * 1024)

    ex = _call(app, chunks, content_length=2048)

    _assert_error(ex, 413)
    assert ex.consumed < ex.total
    assert ex.consumed <= LIMIT // (64 * 1024) + 3  # dừng ngay sau khối làm vượt trần, không đọc nốt phần còn lại


def test_ad11_truong_chu_qua_lon_voi_content_length_nho_gia_thi_413() -> None:
    app = _app()
    body = _body(_field("note", "n" * (LIMIT + 128 * 1024)), _file(_pdf(500)))

    ex = _call(app, _chunks(body), content_length=1024)

    _assert_error(ex, 413, "cv_too_large")
    assert ex.consumed < ex.total


def test_ad11_file_vuot_tran_1_byte_thi_413_du_content_length_vua_khit() -> None:
    app = _app()
    body = _body(_file(_pdf(LIMIT + 1)))
    assert len(body) < LIMIT + MULTIPART_OVERHEAD  # qua được cổng Content-Length, phải bị chặn bằng đếm byte

    ex = _call(app, _chunks(body))

    _assert_error(ex, 413, "cv_too_large")


def test_ad11_content_length_thieu_thi_411_ma_chua_doc_than() -> None:
    app = _app()

    ex = _call(app, _chunks(_body(_file(_pdf(500)))), content_length=None)

    message = _assert_error(ex, 411, "length_required")
    assert ex.consumed == 0
    assert "tối đa 5 MB" in message


@pytest.mark.parametrize("gia_tri", ["9" * 21, "9" * 5000])
def test_ad11_content_length_rat_dai_thi_413_khong_bi_500(gia_tri: str) -> None:
    app = _app()

    ex = _call(app, _chunks(_body(_file(_pdf(500)))), content_length=gia_tri)

    _assert_error(ex, 413, "cv_too_large")
    assert ex.consumed == 0


def test_ad11_than_dung_content_length_cong_phu_troi_duoc_qua_cong_truoc_khi_doc() -> None:
    app = _app()
    cv = _pdf(500)
    base = len(_body(_field("note", ""), _file(cv)))
    body = _body(_field("note", "n" * (LIMIT + MULTIPART_OVERHEAD - base)), _file(cv))
    assert len(body) == LIMIT + MULTIPART_OVERHEAD

    ex = _call(app, _chunks(body))

    assert ex.status == 200, ex.raw
    assert ex.consumed > 0


def test_ad11_than_hon_tran_cong_phu_troi_1_byte_thi_413_voi_0_khoi_da_doc() -> None:
    app = _app()
    cv = _pdf(500)
    base = len(_body(_field("note", ""), _file(cv)))
    body = _body(_field("note", "n" * (LIMIT + MULTIPART_OVERHEAD + 1 - base)), _file(cv))
    assert len(body) == LIMIT + MULTIPART_OVERHEAD + 1

    ex = _call(app, _chunks(body))

    _assert_error(ex, 413, "cv_too_large")
    assert ex.consumed == 0


@pytest.mark.parametrize("gia_tri", ["abc", "-1", "1.5", ""])
def test_ad11_content_length_khong_phai_so_nguyen_khong_am_thi_400(gia_tri: str) -> None:
    app = _app()

    ex = _call(app, _chunks(_body(_file(_pdf(500)))), content_length=gia_tri)

    _assert_error(ex, 400, "cv_invalid_upload")
    assert ex.consumed == 0


# --------------------------------------------------------------------------- Content-Type của request


@pytest.mark.parametrize(
    "content_type",
    [None, "application/json", "application/pdf", "multipart/form-data", "multipart/form-data; boundary=", "text/plain"],
)
def test_ad11_khong_phai_multipart_hoac_thieu_boundary_thi_415_ma_chua_doc_than(content_type: str | None) -> None:
    app = _app()

    ex = _call(app, _chunks(_body(_file(_pdf(500)))), content_type=content_type)

    message = _assert_error(ex, 415, "cv_unsupported_type")
    assert ex.consumed == 0
    assert "multipart/form-data" in message


def test_ad11_content_type_request_viet_hoa_va_boundary_co_ngoac_van_nhan() -> None:
    app = _app()
    body = _body(_file(_pdf(500)))

    ex = _call(app, _chunks(body), content_type=f'Multipart/Form-Data; Boundary="{BOUNDARY}"')

    assert ex.status == 200, ex.raw


# --------------------------------------------------------------------------- kiểu của part và byte đầu


def test_ad11_part_khai_image_png_thi_415_truoc_khi_doc_du_lieu_cua_part() -> None:
    app = _app()
    body = _body(_file(b"%PDF-" + b"p" * (200 * 1024), filename="a.png", ctype="image/png"))
    ket_thuc_header = body.index(b"\r\n\r\n") + 4
    # khối đầu dừng đúng sau header của part; dữ liệu của part nằm ở các khối sau
    chunks = [body[:ket_thuc_header], *_chunks(body[ket_thuc_header:], 4096)]

    ex = _call(app, chunks)

    message = _assert_error(ex, 415, "cv_unsupported_type")
    assert ex.consumed == 1
    assert ex.total > 40
    assert "PDF" in message
    assert "DOCX" in message


def test_ad11_part_khong_khai_content_type_thi_415() -> None:
    app = _app()

    ex = _call(app, _chunks(_body(_file(_pdf(500), ctype=None))))

    _assert_error(ex, 415, "cv_unsupported_type")


def test_ad11_content_type_cua_part_co_tham_so_va_viet_hoa_van_nhan() -> None:
    app = _app()

    ex = _call(app, _chunks(_body(_file(_pdf(500), ctype="Application/PDF; charset=binary"))))

    assert ex.status == 200, ex.raw


def test_ad11_khai_pdf_nhung_byte_dau_sai_thi_415() -> None:
    app = _app()
    gia = b"MZ\x90\x00" + b"exe-gia-pdf" * 100

    ex = _call(app, _chunks(_body(_file(gia))))

    _assert_error(ex, 415, "cv_unsupported_type")


def test_ad11_khai_docx_nhung_byte_dau_la_pdf_thi_415() -> None:
    app = _app()

    ex = _call(app, _chunks(_body(_file(_pdf(500), filename="cv.docx", ctype=DOCX))))

    _assert_error(ex, 415, "cv_unsupported_type")


def test_ad11_khai_pdf_nhung_byte_dau_la_zip_thi_415() -> None:
    app = _app()

    ex = _call(app, _chunks(_body(_file(DOCX_HEAD + b"x" * 500))))

    _assert_error(ex, 415, "cv_unsupported_type")


def test_ad11_file_rong_hoac_ngan_hon_chu_ky_thi_415() -> None:
    app = _app()

    for data in (b"", b"%PD"):
        ex = _call(app, _chunks(_body(_file(data))))
        _assert_error(ex, 415, "cv_unsupported_type")


def test_ad11_byte_dau_sai_thi_dung_doc_ngay_khong_cho_het_file() -> None:
    app = _app()
    body = _body(_file(b"NOTPDF" + b"z" * LIMIT))

    ex = _call(app, _chunks(body, 4096))

    _assert_error(ex, 415, "cv_unsupported_type")
    assert ex.consumed < ex.total // 10


# --------------------------------------------------------------------------- số part


def test_ad11_khong_co_part_cv_thi_400() -> None:
    app = _app()

    ex = _call(app, _chunks(_body(_field("consent", "true"))))

    _assert_error(ex, 400, "cv_invalid_upload")


def test_ad11_part_ten_khac_cv_thi_400() -> None:
    app = _app()

    ex = _call(app, _chunks(_body(_file(_pdf(500), name="resume"))))

    _assert_error(ex, 400, "cv_invalid_upload")


def test_ad11_part_cv_khong_phai_file_thi_400() -> None:
    app = _app()

    ex = _call(app, _chunks(_body(_field("cv", "chu thuong"))))

    _assert_error(ex, 400, "cv_invalid_upload")


def test_ad11_hai_part_file_thi_400_ngay_khi_thay_part_thu_hai() -> None:
    app = _app()
    body = _body(_file(_pdf(500)), _file(_pdf(LIMIT // 2), filename="cv2.pdf"))

    ex = _call(app, _chunks(body, 4096))

    _assert_error(ex, 400, "cv_invalid_upload")
    assert ex.consumed < ex.total


def test_ad11_hai_part_cv_cung_ten_nhung_part_sau_la_png_van_la_400_vi_la_part_thu_hai() -> None:
    app = _app()
    body = _body(_file(_pdf(500)), _file(b"\x89PNG", filename="a.png", ctype="image/png"))

    ex = _call(app, _chunks(body))

    _assert_error(ex, 400, "cv_invalid_upload")


def test_ad11_thieu_dau_ket_thuc_thi_400() -> None:
    app = _app()
    cat_dut = _body(_file(_pdf(4000)))[:2000]

    ex = _call(app, _chunks(cat_dut))

    _assert_error(ex, 400, "cv_invalid_upload")


def test_ad11_cat_dut_ngay_sau_part_cv_khi_moi_co_dong_boundary_thi_400() -> None:
    app = _app()
    cat = _file(_pdf(500)) + f"--{BOUNDARY}\r\n".encode()

    ex = _call(app, _chunks(cat))

    _assert_error(ex, 400, "cv_invalid_upload")


def test_ad11_cat_dut_giua_header_cua_part_sau_cv_thi_400() -> None:
    app = _app()
    cat = _file(_pdf(500)) + f"--{BOUNDARY}\r\nContent-Disp".encode()

    ex = _call(app, _chunks(cat))

    _assert_error(ex, 400, "cv_invalid_upload")


def test_ad11_mat_ket_noi_giua_than_thi_400() -> None:
    app = _app()
    body = _body(_file(_pdf(5000)))

    ex = _call(app, _chunks(body[:3000], 1000), disconnect=True)

    _assert_error(ex, 400, "cv_invalid_upload")


def test_ad11_khong_chon_file_filename_rong_thi_400_chua_chon_tep() -> None:
    app = _app()

    ex = _call(app, _chunks(_body(_file(b"", filename="", ctype="application/octet-stream"))))

    message = _assert_error(ex, 400, "cv_invalid_upload")
    assert "chưa chọn tệp CV" in message


def test_ad11_ten_file_bo_ky_tu_dieu_khien_va_bidi() -> None:
    app = _app()

    ex = _call(app, _chunks(_body(_file(_pdf(500), filename="a\u202egpj.exe\x01\u2066.pdf"))))

    assert ex.status == 200, ex.raw
    assert ex.json["filename"] == "agpj.exe.pdf"


def test_ad11_ten_file_qua_dai_cat_con_255_ky_tu() -> None:
    app = _app()

    ex = _call(app, _chunks(_body(_file(_pdf(500), filename="a" * 400 + ".pdf"))))

    assert ex.status == 200, ex.raw
    assert len(ex.json["filename"]) == 255


def test_ad11_ten_file_chi_con_ky_tu_bi_loai_thi_dung_cv() -> None:
    app = _app()

    ex = _call(app, _chunks(_body(_file(_pdf(500), filename="\u202e\u202e\x01"))))

    assert ex.status == 200, ex.raw
    assert ex.json["filename"] == "cv"


def test_ad11_than_khong_phai_multipart_dung_dinh_dang_thi_400() -> None:
    app = _app()

    ex = _call(app, _chunks(b"day khong phai multipart" * 20))

    _assert_error(ex, 400, "cv_invalid_upload")


# --------------------------------------------------------------------------- thông điệp


def _all_error_exchanges() -> list[Exchange]:
    app = _app()
    secret = b"BI-MAT-NOI-DUNG-CV-0912345678"
    return [
        _call(app, _chunks(_body(_file(_pdf(LIMIT + 2 * MULTIPART_OVERHEAD))))),
        _call(app, _chunks(_body(_file(secret))), content_length=None),
        _call(app, _chunks(_body(_file(secret))), content_type="application/json"),
        _call(app, _chunks(_body(_file(secret, ctype="image/png", filename="bi-mat.png")))),
        _call(app, _chunks(_body(_file(b"MZ" + secret)))),
        _call(app, _chunks(_body(_field("consent", "true")))),
        _call(app, _chunks(_body(_file(PDF_HEAD + secret), _file(PDF_HEAD + secret)))),
        _call(app, [_body(_file(PDF_HEAD + secret))[:90]]),
        _call(app, _chunks(_body(_file(secret))), content_length="abc"),
    ]


def test_ad11_moi_thong_diep_la_tieng_viet_neu_gioi_han_va_kieu_nhan() -> None:
    for ex in _all_error_exchanges():
        assert ex.status in {400, 411, 413, 415}
        message = _assert_error(ex, ex.status)
        assert "tối đa 5 MB" in message, message
        assert "PDF" in message and "DOCX" in message, message
        assert any(ch in message for ch in "ăâêôơưđ"), message


def test_ad11_thong_diep_khong_chua_noi_dung_file_hay_ten_file_hay_kieu_nguoi_dung_khai() -> None:
    for ex in _all_error_exchanges():
        text = ex.raw.decode("utf-8")
        assert "BI-MAT" not in text
        assert "0912345678" not in text
        assert "%PDF" not in text
        assert "bi-mat.png" not in text
        assert "image/png" not in text


def test_ad11_trang_thai_va_ma_loi_on_dinh_theo_tung_truong_hop() -> None:
    got = [(ex.status, ex.json["error"]["code"]) for ex in _all_error_exchanges()]
    assert got == [
        (413, "cv_too_large"),
        (411, "length_required"),
        (415, "cv_unsupported_type"),
        (415, "cv_unsupported_type"),
        (415, "cv_unsupported_type"),
        (400, "cv_invalid_upload"),
        (400, "cv_invalid_upload"),
        (400, "cv_invalid_upload"),
        (400, "cv_invalid_upload"),
    ]


# --------------------------------------------------------------------------- quy tắc không mặc định


def _small_rules() -> RulesConfig:
    return dataclasses.replace(load_rules(), cv_max_bytes=1024, cv_types=(PDF,))


def test_ad11_tran_theo_rules_chu_khong_phai_5_mib() -> None:
    app = _app(_small_rules())

    ok = _call(app, _chunks(_body(_file(_pdf(1024)))))
    over = _call(app, _chunks(_body(_file(_pdf(1025)))))

    assert ok.status == 200, ok.raw
    message = _assert_error(over, 413, "cv_too_large")
    assert "tối đa 1 KB" in message


def test_ad11_cong_content_length_theo_rules() -> None:
    app = _app(_small_rules())

    ex = _call(app, _chunks(_body(_file(_pdf(1024 + 2 * MULTIPART_OVERHEAD)))))

    _assert_error(ex, 413, "cv_too_large")
    assert ex.consumed == 0


def test_ad11_kieu_theo_rules_docx_bi_tu_choi_khi_chi_cho_pdf() -> None:
    app = _app(_small_rules())

    ex = _call(app, _chunks(_body(_file(DOCX_HEAD + b"x" * 100, filename="cv.docx", ctype=DOCX))))

    message = _assert_error(ex, 415, "cv_unsupported_type")
    assert "Chỉ nhận tệp PDF," in message
    assert "DOCX" not in message


def test_ad11_kieu_co_trong_rules_nhung_khong_co_chu_ky_thi_bi_tu_choi() -> None:
    rules = dataclasses.replace(load_rules(), cv_types=("image/png",))
    app = _app(rules)

    ex = _call(app, _chunks(_body(_file(b"\x89PNG" + b"x" * 100, filename="a.png", ctype="image/png"))))

    _assert_error(ex, 415, "cv_unsupported_type")


def test_ad11_loi_tai_len_dong_ket_noi() -> None:
    app = _app()

    ex = _call(app, _chunks(_body(_file(_pdf(500), ctype="image/png"))))

    assert ex.headers.get("connection") == "close"
