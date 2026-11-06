"""#8 — bản thư xin phép đã có đủ ý, và chưa được ghi là đã gửi."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT / "docs" / "permissions"
FILES = ("itviec.md", "topcv.md", "repo-goc.md")


def test_perm08_ba_thu_noi_ro_muc_dich_tan_suat_va_cach_go() -> None:
    for name in FILES:
        text = (FOLDER / name).read_text(encoding="utf-8")
        assert "học thuật" in text
        assert "phi thương mại" in text
        assert "một lượt mỗi ngày" in text
        assert "48 giờ" in text
        assert "từ chối" in text
        assert "tuân thủ đầy đủ" not in text
        assert "chưa gửi" in text


def test_perm08_bang_theo_doi_chua_co_ngay_gui() -> None:
    text = (FOLDER / "README.md").read_text(encoding="utf-8")
    assert "Chưa thư nào được gửi" in text
    for name in FILES:
        assert name in text
