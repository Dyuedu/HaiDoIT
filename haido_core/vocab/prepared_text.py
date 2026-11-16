"""Kiểm câu chữ viết sẵn (lời dẫn, tên tài liệu): không chữ số ngoài tên công nghệ, không `%` (FR-23, DEC-6 #132).

Một chỗ duy nhất giữ quy tắc. Cổng CI FR-24 của #138 (`tools/gates/check_gates.py`) gọi `prepared_text_problems` ở đây
thay vì viết quy tắc riêng.

Mọi kiểm tra chạy trên văn bản đã chuẩn hóa NFKC: `％` thành `%`, `²`, `①` và chữ số toàn chiều thành chữ số; "phần trăm"
bị bắt dù viết hoa, dạng NFD, cách nhiều dấu cách, dấu cách không ngắt hay xuống dòng giữa hai chữ.

Ngoài phạm vi: số viết bằng chữ ("mười hai", "hàng trăm") không bị bắt; tên công nghệ chỉ được miễn khi khớp nguyên
từ (không dính chữ hay số khác ở hai đầu), nên "Java 170" hay "MyS3" vẫn bị tính chữ số.
"""

import re
import unicodedata

TECH_NAMES: tuple[str, ...] = (
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
)
"""Tên công nghệ mà chữ số nằm trong tên: danh sách FR-23 (Java 17, S3, EC2, OAuth2, Web3, HTML5, Vue 3) và các tên
đã dùng trong test (HTTP/2, Base64, SHA-256)."""

_TECH = re.compile(
    r"(?<!\w)(?:"
    + "|".join(re.escape(n) for n in sorted(TECH_NAMES, key=len, reverse=True))
    + r")(?!\w)"
)
_DIGITS = re.compile(r"\d+")
_PERCENT_WORDS = re.compile(r"phần\s+trăm")


def digits_outside_tech(text: str) -> list[str]:
    """Các cụm chữ số còn lại sau khi che đúng các tên công nghệ ở `TECH_NAMES` (khớp nguyên từ)."""
    return _DIGITS.findall(_TECH.sub(" ", unicodedata.normalize("NFKC", text)))


def prepared_text_problems(text: str) -> list[str]:
    """Danh sách lỗi của một câu viết sẵn; rỗng là đạt. Cấm `%`, "phần trăm" và chữ số ngoài tên công nghệ."""
    text = unicodedata.normalize("NFKC", text)
    problems: list[str] = []
    if "%" in text:
        problems.append("có ký hiệu %")
    if _PERCENT_WORDS.search(text.casefold()):
        problems.append("có chữ 'phần trăm' (số liệu % ở bên ngoài lời dẫn)")
    digits = digits_outside_tech(text)
    if digits:
        problems.append(f"có chữ số ngoài tên công nghệ: {', '.join(digits)}")
    return problems
