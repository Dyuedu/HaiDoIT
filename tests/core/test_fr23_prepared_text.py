"""FR-23 — kiểm câu chữ viết sẵn: không chữ số ngoài tên công nghệ, không `%` (#212, sửa sau review).

Một hàm duy nhất ở `haido_core.vocab.prepared_text`; cổng CI của #138 nên dùng lại hàm này thay vì viết quy tắc riêng.
Ngoài phạm vi: số viết bằng chữ ("mười hai") không bị bắt.
"""

import pytest

from haido_core.vocab.prepared_text import (
    TECH_NAMES,
    digits_outside_tech,
    prepared_text_problems,
)


def test_fr23_ten_cong_nghe_theo_danh_sach_fr23() -> None:
    for name in (
        "Java 17",
        "S3",
        "EC2",
        "OAuth2",
        "Web3",
        "HTML5",
        "Vue 3",
        "HTTP/2",
        "Base64",
        "SHA-256",
    ):
        assert name in TECH_NAMES


@pytest.mark.parametrize(
    "text",
    [
        "Học Java 17 và S3 trước",
        "Dùng EC2, OAuth2 và Web3",
        "HTML5 với Vue 3",
        "HTTP/2 và Base64, SHA-256",
    ],
)
def test_fr23_so_trong_ten_cong_nghe_khong_bi_tinh(text: str) -> None:
    assert digits_outside_tech(text) == []


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Có 30 tin", ["30"]),
        ("Java 17 và 12 năm", ["12"]),
        ("Java 17 17", ["17"]),
        ("Java 1717", ["1717"]),
        ("Java 170", ["170"]),
        ("Học S33", ["33"]),
        ("Bước 2 của Vue 3", ["2"]),
        ("MyS3 bucket", ["3"]),
        ("Vue 31", ["31"]),
    ],
)
def test_fr23_chu_so_khac_van_bi_bat_va_ten_chi_khop_nguyen_the(
    text: str, expected: list[str]
) -> None:
    assert digits_outside_tech(text) == expected


@pytest.mark.parametrize("text", ["Tăng 5%", "chiếm 5 %", "một %", "100%"])
def test_fr23_phan_tram_o_dau_cung_bi_tu_choi(text: str) -> None:
    assert any("%" in p for p in prepared_text_problems(text))


def test_fr23_phan_tram_bang_chu_bi_tu_choi() -> None:
    assert prepared_text_problems("Chiếm phần trăm lớn")


def test_fr23_van_ban_sach_khong_co_loi() -> None:
    assert prepared_text_problems("Học Java 17 trước khi học framework.") == []
