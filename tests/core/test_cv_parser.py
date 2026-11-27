"""TDD cho haido_core.extract.cv_parser: đọc PDF/DOCX trong bộ nhớ, phát hiện CV scan."""

import io
import zipfile

import pytest

from haido_core.extract.cv_parser import UnreadableCvError, extract_document_chars

PDF_MIME = "application/pdf"
DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def _minimal_pdf(text: str) -> bytes:
    """Dựng PDF 1 trang tối giản trong bộ nhớ chứa chuỗi ASCII `text`."""
    safe = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream = f"BT\n/F1 12 Tf\n72 720 Td\n({safe}) Tj\nET\n".encode("latin-1")
    objs = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        (
            b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n"
        ),
        b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
        f"5 0 obj\n<< /Length {len(stream)} >>\nstream\n".encode("ascii") + stream + b"endstream\nendobj\n",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objs:
        offsets.append(len(out))
        out.extend(obj)
    xref_pos = len(out)
    out.extend(f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode("ascii"))
    for off in offsets[1:]:
        out.extend(f"{off:010d} 00000 n \n".encode("ascii"))
    out.extend(
        f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode("ascii")
    )
    return bytes(out)


def _minimal_docx(paragraphs: list[str]) -> bytes:
    """Dựng DOCX hợp lệ trong bộ nhớ."""
    body_xml = "".join(
        f"<w:p><w:r><w:t>{p}</w:t></w:r></w:p>" for p in paragraphs
    )
    doc_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{body_xml}</w:body></w:document>"
    )
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>')
        zf.writestr("word/document.xml", doc_xml.encode("utf-8"))
    return buf.getvalue()


def test_cv_parser_doc_pdf_co_lop_chu_thanh_cong() -> None:
    pdf_bytes = _minimal_pdf("Backend Java Developer with Spring Boot, SQL, Docker and Git experience.")
    extracted = extract_document_chars(pdf_bytes, PDF_MIME)
    assert "Spring Boot" in extracted
    assert "Docker" in extracted


def test_cv_parser_doc_docx_co_tieng_viet_thanh_cong() -> None:
    docx_bytes = _minimal_docx(
        [
            "Nguyễn Văn An - Lập trình viên Backend",
            "Kỹ năng: Java, Spring Boot, PostgreSQL, Docker, kiểm thử tự động",
        ]
    )
    extracted = extract_document_chars(docx_bytes, DOCX_MIME)
    assert "Nguyễn Văn An" in extracted
    assert "PostgreSQL" in extracted
    assert "kiểm thử tự động" in extracted


def test_cv_parser_pdf_anh_scan_hoac_it_chu_bao_unreadable() -> None:
    scan_pdf = _minimal_pdf("CV")
    with pytest.raises(UnreadableCvError, match="Word, Canva hoặc Overleaf"):
        extract_document_chars(scan_pdf, PDF_MIME)


def test_cv_parser_docx_rong_hoac_hong_bao_unreadable() -> None:
    empty_docx = _minimal_docx(["   ", "abc"])
    with pytest.raises(UnreadableCvError, match="DOCX"):
        extract_document_chars(empty_docx, DOCX_MIME)

    with pytest.raises(UnreadableCvError):
        extract_document_chars(b"PK\x03\x04not-a-valid-zip", DOCX_MIME)


def test_cv_parser_pdf_hong_bao_unreadable() -> None:
    with pytest.raises(UnreadableCvError):
        extract_document_chars(b"%PDF-1.7\ncorrupted-body", PDF_MIME)
