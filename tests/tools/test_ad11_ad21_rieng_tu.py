"""Kiểm thử cổng AD-11 / AD-21: quyền riêng tư, không lưu CV/JD text và không PII trong file dữ liệu."""

import json
from pathlib import Path
import pytest
import tools.gates.check_gates as check_gates


def test_ad11_ad21_cv_text_in_schema_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    db_dir = tmp_path / "haido_core" / "db"
    db_dir.mkdir(parents=True)
    (db_dir / "models.py").write_text("class Job:\n    cv_text: str\n", encoding="utf-8")

    status, _detail, hits = check_gates.gate_ad11_ad21_rieng_tu()
    assert status == check_gates.FAIL
    assert any("cv_text" in h for h in hits)


def test_ad11_ad21_email_in_data_file_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True)
    (data_dir / "records.jsonl").write_text('{"title": "Dev", "contact": "hr_lead@company.vn"}\n', encoding="utf-8")

    status, _detail, hits = check_gates.gate_ad11_ad21_rieng_tu()
    assert status == check_gates.FAIL
    assert len(hits) == 1
    assert "data/records.jsonl:1" in hits[0]


def test_ad11_ad21_vn_phone_in_data_file_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True)
    (data_dir / "jobs.json").write_text('{"phone": "0987654321"}\n', encoding="utf-8")

    status, _detail, hits = check_gates.gate_ad11_ad21_rieng_tu()
    assert status == check_gates.FAIL
    assert len(hits) == 1
    assert "data/jobs.json:1" in hits[0]


def test_ad11_ad21_email_and_phone_in_tests_ignored(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    test_dir = tmp_path / "tests" / "fixtures"
    test_dir.mkdir(parents=True)
    (test_dir / "dummy.json").write_text('{"email": "test@domain.com", "phone": "0987654321"}\n', encoding="utf-8")

    status, _detail, hits = check_gates.gate_ad11_ad21_rieng_tu()
    assert status == check_gates.PASS
    assert hits == []


def test_ad11_ad21_error_does_not_leak_pii(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True)
    secret_email = "super_secret_pii@private.corp.vn"
    secret_phone = "0912345678"
    (data_dir / "pii.jsonl").write_text(f'{{"email": "{secret_email}", "tel": "{secret_phone}"}}\n', encoding="utf-8")

    status, _detail, hits = check_gates.gate_ad11_ad21_rieng_tu()
    assert status == check_gates.FAIL
    for hit in hits:
        assert secret_email not in hit
        assert secret_phone not in hit
        assert "pii.jsonl:1" in hit


def test_ad11_ad21_gate_does_not_skip_on_clean_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)

    db_dir = tmp_path / "haido_core" / "db"
    db_dir.mkdir(parents=True)
    (db_dir / "schema.py").write_text("class CleanTable:\n    id: int\n", encoding="utf-8")

    status, _detail, hits = check_gates.gate_ad11_ad21_rieng_tu()
    assert status == check_gates.PASS
    assert hits == []


def test_ad11_ad21_deferred_ledger_khong_con_muc_tam_cua_ad11():
    """Mục AD-11-temp chỉ là chỗ giữ chỗ tới khi có test CV 5 MB (#140); test đó đã có nên mục phải gỡ."""
    ledger_path = check_gates.ROOT / "tools" / "gates" / "deferred.json"
    assert ledger_path.is_file(), "deferred.json must exist"
    data = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert "AD-11-temp" not in data
    assert set(data) == {"FR-24", "FR-22"}


def test_ad11_ad21_test_cv_5mb_khong_file_tam_ton_tai():
    test_file = check_gates.ROOT / "tests" / "api" / "test_ad11_tai_cv_khong_file_tam.py"
    assert test_file.is_file()
    assert "def test_ad11_cv_dung_5_mib_duoc_nhan_va_khong_co_file_tam_moi" in test_file.read_text(encoding="utf-8")


def _api_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str, text: str, *sub: str) -> Path:
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)
    folder = tmp_path / "haido_api" / Path(*sub)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / name
    path.write_text(text, encoding="utf-8")
    return path


def test_ad11_upload_sach_trong_haido_api_thi_pass(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _api_file(
        tmp_path,
        monkeypatch,
        "uploads.py",
        "from starlette.requests import Request\n\n\nasync def read(request: Request) -> bytes:\n"
        "    return b''.join([c async for c in request.stream()])\n",
    )

    status, _detail, hits = check_gates.gate_ad11_ad21_rieng_tu()
    assert status == check_gates.PASS
    assert hits == []


@pytest.mark.parametrize(
    ("text", "pattern"),
    [
        ("from fastapi import UploadFile\n", "UploadFile"),
        ("async def tai(cv: UploadFile): ...\n", "UploadFile"),
        ("from fastapi import File\n\ncv = File(...)\n", "File("),
        ("cv = File (...)\n", "File("),
        ("async def tai(request):\n    form = await request.form()\n", ".form("),
        ("async def tai(request):\n    form = await request.form (max_files=1)\n", ".form("),
        ("import tempfile\n", "tempfile"),
        ("from tempfile import SpooledTemporaryFile\n", "tempfile"),
        ("path = tempfile.mkstemp()\n", "tempfile"),
        ("from starlette import formparsers\n", "formparsers"),
        ("p = MultiPartParser(h, s)\n", "MultiPartParser"),
        ("p = FormParser(h, s)\n", "FormParser"),
        ("async def f(r):\n    await parse_form(r)\n", "parse_form"),
        ("p = create_form_parser(h, s)\n", "create_form_parser"),
        ("f = await request._get_form()\n", "_get_form"),
        ("f = SpooledTemporaryFile()\n", "SpooledTemporaryFile"),
        ("f = NamedTemporaryFile()\n", "NamedTemporaryFile"),
        ("async def tai(consent: str = Form(...)): ...\n", "Form("),
        ("x = Form (...)\n", "Form("),
    ],
)
def test_ad11_upload_dung_file_tam_hoac_form_thi_fail(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, text: str, pattern: str
):
    path = _api_file(tmp_path, monkeypatch, "routes_cv.py", text, "routes")

    status, _detail, hits = check_gates.gate_ad11_ad21_rieng_tu()
    assert status == check_gates.FAIL
    rel = path.relative_to(tmp_path).as_posix()
    assert any(h.startswith(rel + ":") and pattern in h for h in hits), hits


def test_ad11_upload_vi_pham_bao_so_dong_va_khong_lo_noi_dung_dong(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _api_file(tmp_path, monkeypatch, "x.py", "ok = 1\nsecret_cv = 'BI-MAT'  # tempfile\n")

    _status, _detail, hits = check_gates.gate_ad11_ad21_rieng_tu()
    assert len(hits) == 1
    assert "haido_api/x.py:2:" in hits[0]
    assert "BI-MAT" not in hits[0]


def test_ad11_upload_bo_qua_thu_muc_tests_va_pycache_trong_haido_api(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _api_file(tmp_path, monkeypatch, "test_x.py", "import tempfile\nx = request.form()\n", "tests")
    _api_file(tmp_path, monkeypatch, "cache.py", "import tempfile\n", "__pycache__")

    status, _detail, hits = check_gates.gate_ad11_ad21_rieng_tu()
    assert status == check_gates.PASS
    assert hits == []


def test_ad11_upload_ngoai_haido_api_khong_bi_quet(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(check_gates, "ROOT", tmp_path)
    (tmp_path / "scraper").mkdir()
    (tmp_path / "scraper" / "dump.py").write_text("import tempfile\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_dump.py").write_text("import tempfile\n", encoding="utf-8")

    status, _detail, hits = check_gates.gate_ad11_ad21_rieng_tu()
    assert status == check_gates.PASS
    assert hits == []


def test_ad11_ad21_real_repo_passes():
    status, _detail, hits = check_gates.gate_ad11_ad21_rieng_tu()
    assert status == check_gates.PASS
    assert hits == []
