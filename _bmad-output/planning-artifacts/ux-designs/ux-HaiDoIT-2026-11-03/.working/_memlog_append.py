import subprocess
from pathlib import Path

root = Path(r"D:\FR_KS_FU_Java_03\HaiDoIT")
ws = root / "_bmad-output" / "planning-artifacts" / "ux-designs" / "ux-HaiDoIT-2026-11-03"
text = (
    "Đã chưng cất DESIGN.md và EXPERIENCE.md, status draft. "
    "Spine thắng mock ở ngưỡng 30/10, ba lưu ý FR-36, vai trò mặc định Tất cả, "
    "không vẽ nhóm riêng của công ty, chi tiết kỹ năng là kỹ năng vừa bấm, "
    "D1/D2 theo FR-31, mức khớp 89%. "
    "Đối chiếu: reconcile-prototype.md và reconcile-claude-design.md. "
    "Chưa chạy reviewer, chưa final."
)
subprocess.run(
    [
        "uv",
        "run",
        str(root / "_bmad" / "scripts" / "memlog.py"),
        "append",
        "--workspace",
        str(ws),
        "--type",
        "event",
        "--text",
        text,
    ],
    check=True,
    cwd=root,
)
