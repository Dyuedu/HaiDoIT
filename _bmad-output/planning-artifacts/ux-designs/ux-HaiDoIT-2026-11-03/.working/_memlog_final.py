import subprocess
from pathlib import Path

root = Path(r"D:\FR_KS_FU_Java_03\HaiDoIT")
ws = root / "_bmad-output" / "planning-artifacts" / "ux-designs" / "ux-HaiDoIT-2026-11-03"
script = root / "_bmad" / "scripts" / "memlog.py"
notes = [
    (
        "event",
        "Các [NOTE FOR UX] và câu hỏi mở không chặn đóng: phần không xác định thành phố, tương phản nút tắt 3,9:1, nút Huỷ, aria-live đồng hồ đọc CV, tên nhà cung cấp AI, hai bộ số minh họa, cỡ mẫu Soi tin 24/39 so với 89%, thẻ Insights còn thiếu hình, hộp xác nhận xoá, ô thả trống, placeholder chính sách, Middle/Mid, màu level-bar. Giữ trong EXPERIENCE.md.",
    ),
    (
        "event",
        "15 bề mặt IA đều có hình trong mockups/gallery.html và mockups/screens/01.html–15.html. Spine-only: ô thả CV trống, hộp xác nhận xoá, ba loại thẻ Insights còn lại, bố cục điện thoại, các trạng thái lỗi chưa vẽ. Không vẽ thêm.",
    ),
    ("event", "spines finalized"),
]
for kind, text in notes:
    subprocess.run(
        [
            "uv",
            "run",
            str(script),
            "append",
            "--workspace",
            str(ws),
            "--type",
            kind,
            "--text",
            text,
        ],
        check=True,
        cwd=root,
    )
