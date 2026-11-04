"""Remove recruiter contact details before anything is stored or sent out (AD-21).

    python redact.py     # data/raw/*.jsonl -> data/redacted/*.jsonl

Runs before every write: ingest and dedupe read data/redacted, never data/raw.
The log carries counts per type, never the values.

Regexes catch emails, Vietnamese phone numbers, Zalo numbers and names that follow
a contact phrase ("lien he chi Hoa"). A bare name with no such phrase is not caught.
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

MASK = "[đã xóa]"

# job_url holds numeric ids that look exactly like phone numbers.
SKIP_FIELDS = {"job_url", "site", "job_id", "salary", "date_posted", "first_published", "valid_through"}

CAP_WORD = r"[A-ZĐÀ-Ỹ][\wÀ-ỹ]*"
PATTERNS = [
    ("email", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), MASK),
    ("zalo", re.compile(r"(?i)(zalo[^\w]{0,6})\d[\d .-]{6,}\d"), r"\g<1>" + MASK),
    ("phone", re.compile(r"(?<!\d)(?:\+?84|0)[ .-]?(?:[35789]|2\d)(?:[ .-]?\d){8}(?!\d)"), MASK),
    ("name", re.compile(
        r"(?i:(liên hệ|liên lạc|gặp|contact)[:\s]+)"
        r"(?i:(?:mr|ms|mrs|anh|chị|a|c)\.?\s+)"
        + r"(?:" + CAP_WORD + r"\s*){1,4}"), r"\g<1> " + MASK),
]


def scrub_text(text: str, counts: collections.Counter) -> str:
    for kind, rx, repl in PATTERNS:
        text, n = rx.subn(repl, text)
        counts[kind] += n
    return text


def scrub(value, counts: collections.Counter):
    if isinstance(value, str):
        return scrub_text(value, counts)
    if isinstance(value, list):
        return [scrub(v, counts) for v in value]
    if isinstance(value, dict):
        return {k: scrub(v, counts) for k, v in value.items()}
    return value


def scrub_row(row: dict, counts: collections.Counter) -> dict:
    return {k: (v if k in SKIP_FIELDS else scrub(v, counts)) for k, v in row.items()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="data/raw")
    ap.add_argument("--out", default="data/redacted")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    counts: collections.Counter = collections.Counter()
    rows = 0
    for src in sorted(Path(args.raw).glob("*.jsonl")):
        tmp = out_dir / (src.name + ".tmp")
        with src.open(encoding="utf-8") as fin, tmp.open("w", encoding="utf-8") as fout:
            for line in fin:
                if line.strip():
                    fout.write(json.dumps(scrub_row(json.loads(line), counts), ensure_ascii=False) + "\n")
                    rows += 1
        tmp.replace(out_dir / src.name)
    print("redacted %d rows, removed: %s" % (rows, dict(counts) or "nothing"), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
