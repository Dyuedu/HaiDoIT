"""Đọc văn bản từ file CV (PDF hoặc DOCX) hoàn toàn trong bộ nhớ (AD-11).

Không tạo file tạm, không ghi log nội dung CV, phát hiện sớm file scan / dưới 30 ký tự có nghĩa (#196).
"""

from __future__ import annotations

import io
import zipfile
from xml.etree import ElementTree as ET

from pypdf import PdfReader
from pypdf.errors import PdfReadError

PDF_MIME = "application/pdf"
DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

MIN_MEANINGFUL_CHARS = 30
MAX_DOCUMENT_CHARS = 30_000

_UNREADABLE_MSG = (
    "Không đọc được chữ từ tệp CV (có thể đây là PDF dạng ảnh scan hoặc tệp trống). "
    "Hãy dùng PDF xuất từ Word, Canva hoặc Overleaf, tải tệp DOCX, hoặc tự chọn kỹ năng ở bên dưới."
)
_WORD_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


class UnreadableCvError(ValueError):
    """Tệp CV không đọc được chữ (ảnh scan, mã hóa, rỗng hoặc hỏng)."""

    def __init__(self, message: str = _UNREADABLE_MSG) -> None:
        super().__init__(message)
        self.message = message


def _count_meaningful(text: str) -> int:
    return sum(1 for ch in text if ch.isalnum())


def _read_pdf_bytes(raw_bytes: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(raw_bytes))
        if reader.is_encrypted:
            try:
                if reader.decrypt("") == 0:
                    raise UnreadableCvError()
            except Exception as exc:
                raise UnreadableCvError() from exc
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(part for part in pages if part.strip())
    except UnreadableCvError:
        raise
    except (PdfReadError, ValueError, EOFError, OSError, KeyError) as exc:
        raise UnreadableCvError() from exc


def _extract_word_xml(xml_bytes: bytes) -> str:
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise UnreadableCvError() from exc
    lines: list[str] = []
    for para in root.iter(f"{_WORD_NS}p"):
        runs = [node.text for node in para.iter(f"{_WORD_NS}t") if node.text]
        joined = "".join(runs).strip()
        if joined:
            lines.append(joined)
    return "\n".join(lines)


def _read_docx_bytes(raw_bytes: bytes) -> str:
    try:
        with zipfile.ZipFile(io.BytesIO(raw_bytes)) as archive:
            names = set(archive.namelist())
            if "word/document.xml" not in names:
                raise UnreadableCvError()
            parts: list[str] = [_extract_word_xml(archive.read("word/document.xml"))]
            extras = sorted(
                name
                for name in names
                if name.startswith(("word/header", "word/footer")) and name.endswith(".xml")
            )
            for name in extras:
                chunk = _extract_word_xml(archive.read(name))
                if chunk:
                    parts.append(chunk)
            return "\n".join(part for part in parts if part.strip())
    except UnreadableCvError:
        raise
    except (zipfile.BadZipFile, KeyError, OSError, ValueError) as exc:
        raise UnreadableCvError() from exc


def extract_document_chars(raw_bytes: bytes, content_type: str) -> str:
    """Trích chữ từ PDF/DOCX trong bộ nhớ. Ném `UnreadableCvError` nếu dưới 30 ký tự có nghĩa hoặc file hỏng."""
    normalized = content_type.split(";", 1)[0].strip().lower()
    if normalized == PDF_MIME:
        parsed = _read_pdf_bytes(raw_bytes)
    elif normalized == DOCX_MIME:
        parsed = _read_docx_bytes(raw_bytes)
    else:
        raise UnreadableCvError()

    cleaned = "\n".join(line.strip() for line in parsed.splitlines() if line.strip())
    if _count_meaningful(cleaned) < MIN_MEANINGFUL_CHARS:
        raise UnreadableCvError()
    return cleaned[:MAX_DOCUMENT_CHARS]
