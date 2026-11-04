"""Step 04: consolidate tech job descriptions — rule-based cleanup (no LLM).

Reads data/tech_filtered.jsonl, cleans each raw `description`:
  - strips residual HTML tags/entities
  - removes common boilerplate (apply-now, marketing fluff, nav/footer)
  - normalizes whitespace
  - extracts section structure where possible

Outputs data/consolidated.jsonl with clean text in `description_consolidated`
while preserving the original `description`.

No API key needed.
"""

import argparse
import json
import re
import unicodedata
from html import unescape
from pathlib import Path

from crawlers.base import read_jsonl


# ── Boilerplate patterns to strip ────────────────────────────────────────────

_BOILERPLATE_LINES_VI = [
    r"ứng tuyển ngay",
    r"nộp đơn ứng tuyển",
    r"gửi cv .{0,40}(email|mail|qua)",
    r"apply now",
    r"click (here|vào đây)",
    r"nếu bạn quan tâm.{0,60}(liên hệ|gửi)",
    r"vui lòng gửi",
    r"hồ sơ ứng tuyển (bao )?gồm",
    r"lưu ý.{0,30}(không hoàn trả|hồ sơ)",
    r"cảnh báo.{0,30}(lừa đảo|giả mạo)",
    r"cảnh giác.{0,30}(lừa đảo|giả mạo)",
    r"nhà tuyển dụng.{0,30}(không thu|miễn phí)",
    r"top \d+ (reasons?|lý do)",
    r"tại sao.{0,20}(nên gia nhập|chọn chúng tôi|bạn sẽ yêu)",
    r"why you.{0,20}(love|should|will)",
    r"equal opportunity",
    r"chính sách bảo mật",
    r"privacy policy",
    r"chúng tôi cam kết.{0,40}(bình đẳng|đa dạng)",
    r"we are (an? )?equal",
    r"report this job",
    r"báo cáo tin tuyển dụng",
    r"share this job",
    r"chia sẻ .{0,20}việc làm",
    r"việc làm tương tự",
    r"similar jobs",
    r"xem thêm .{0,20}việc làm",
    r"ngày đăng\s*:",
    r"hạn nộp\s*:",
    r"ngày hết hạn\s*:",
    r"lượt xem\s*:",
    r"số lượng tuyển\s*:",
    r"hình thức làm việc\s*:",
    r"cấp bậc\s*:",
    r"mã .{0,10}(việc làm|tin tuyển dụng)\s*:",
]

_BOILERPLATE_RE = re.compile(
    r"^(" + "|".join(_BOILERPLATE_LINES_VI) + r").*$",
    re.IGNORECASE | re.MULTILINE,
)

# Blocks of marketing fluff that span multiple lines
_MARKETING_BLOCKS = [
    re.compile(
        r"(top \d+ reasons? to join us|tại sao bạn nên gia nhập)\s*\n(.+\n){0,5}",
        re.IGNORECASE,
    ),
    re.compile(
        r"(why you.{0,20}love working here)\s*\n(.+\n){0,5}",
        re.IGNORECASE,
    ),
]

# ── HTML / entity cleanup ────────────────────────────────────────────────────

_HTML_TAG_RE = re.compile(r"<[^>]{1,200}>")
_HTML_ENTITY_RE = re.compile(r"&[a-zA-Z]+;|&#\d+;|&#x[0-9a-fA-F]+;")
_URL_RE = re.compile(r"https?://\S+")

# ── Section header normalization ─────────────────────────────────────────────

_SECTION_MAP = {
    "mo ta cong viec": "## Mô tả công việc",
    "mo ta": "## Mô tả công việc",
    "job description": "## Mô tả công việc",
    "responsibilities": "## Mô tả công việc",
    "your role": "## Mô tả công việc",
    "the job": "## Mô tả công việc",
    "about the role": "## Mô tả công việc",
    "job responsibilities": "## Mô tả công việc",
    "yeu cau cong viec": "## Yêu cầu",
    "yeu cau": "## Yêu cầu",
    "requirements": "## Yêu cầu",
    "qualifications": "## Yêu cầu",
    "your skills": "## Yêu cầu",
    "skills and experience": "## Yêu cầu",
    "your skills and experience": "## Yêu cầu",
    "requirements / qualifications": "## Yêu cầu",
    "must have": "## Yêu cầu",
    "nice to have": "## Ưu tiên",
    "quyen loi": "## Quyền lợi",
    "phuc loi": "## Quyền lợi",
    "che do": "## Quyền lợi",
    "benefits": "## Quyền lợi",
    "benefits for you": "## Quyền lợi",
    "what we offer": "## Quyền lợi",
    "why join us": "## Quyền lợi",
    "dia diem lam viec": "## Địa điểm",
    "work location": "## Địa điểm",
    "thoi gian lam viec": "## Thời gian làm việc",
    "working hours": "## Thời gian làm việc",
}


def _remove_diacritics(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _normalize_header(line: str) -> str | None:
    stripped = line.strip().rstrip(":").strip()
    if not stripped or len(stripped) > 80:
        return None
    key = _remove_diacritics(stripped).lower().strip()
    return _SECTION_MAP.get(key)


# ── Main cleanup ─────────────────────────────────────────────────────────────


def clean_description(text: str) -> str:
    if not text or not text.strip():
        return ""

    text = unescape(text)
    text = _HTML_TAG_RE.sub("", text)
    text = _HTML_ENTITY_RE.sub("", text)

    for block_re in _MARKETING_BLOCKS:
        text = block_re.sub("", text)

    text = _BOILERPLATE_RE.sub("", text)

    lines = text.splitlines()
    out: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if out and out[-1] != "":
                out.append("")
            continue

        header = _normalize_header(stripped)
        if header:
            if out and out[-1] != "":
                out.append("")
            out.append(header)
            continue

        out.append(stripped)

    result = "\n".join(out).strip()
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Consolidate tech descriptions (rule-based, no LLM)"
    )
    parser.add_argument("--in", dest="src", type=str, default="data/tech_filtered.jsonl")
    parser.add_argument("--out", type=str, default="data/consolidated.jsonl")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    rows = read_jsonl(args.src)
    dedup: dict[str, dict] = {}
    for r in rows:
        dedup.setdefault(r.get("job_url"), r)
    rows = list(dedup.values())
    print(f"{len(rows)} unique tech jobs", flush=True)

    if args.limit:
        rows = rows[: args.limit]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with out.open("w", encoding="utf-8") as fh:
        for row in rows:
            desc = row.get("description", "")
            cleaned = clean_description(desc)
            merged = {**row, "description_consolidated": cleaned}
            fh.write(json.dumps(merged, ensure_ascii=False) + "\n")
            count += 1

    print(f"wrote {count} jobs to {out}", flush=True)


if __name__ == "__main__":
    main()
