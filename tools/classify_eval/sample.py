"""Chọn mẫu để tự gán nhãn (#283) và in phần chức danh + mục yêu cầu ra màn hình. Không ghi văn bản JD ra file.

    HAIDO_EVAL_DATABASE_URL=postgresql+psycopg://... uv run python tools/classify_eval/sample.py 0 30

Mẫu cố định (seed 283): 120 tin ngẫu nhiên trong cửa sổ 60 ngày kết thúc ở `SNAPSHOT`, cộng 30 tin có chức danh nhắc
AI, ML, LLM hoặc khoa học dữ liệu. In từ vị trí `start`, `count` tin.
"""

import hashlib
import os
import random
import re
import sys

from sqlalchemy import create_engine, text

from haido_core.config import load_classify_config
from haido_core.domain.posting_text import fold, requirement_text

SNAPSHOT = "2026-11-12"
SEED = 283
AI_TITLE = re.compile(r"\bai\b|\bml\b|machine learning|deep learning|llm|data scien|khoa hoc du lieu|tri tue nhan tao|"
                      r"computer vision|\bnlp\b|genai|generative")


def url_key(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]


def postings(engine) -> list[tuple[str, str, str, str | None, str | None, str | None]]:
    with engine.connect() as conn:
        return conn.execute(
            text(
                "SELECT j.job_url, j.site, coalesce(j.title, ''), j.job_level, j.experience_level, "
                "coalesce(nullif(j.description_consolidated, ''), j.description) "
                "FROM public.jobs j WHERE j.site <> 'linkedin' AND EXISTS (SELECT 1 FROM public.job_observations o "
                "WHERE o.job_url = j.job_url AND o.snapshot_date > CAST(:d AS date) - 60 "
                "AND o.snapshot_date <= CAST(:d AS date)) ORDER BY j.job_url"
            ),
            {"d": SNAPSHOT},
        ).all()


AI_STRICT = re.compile(r"ai engineer|ai developer|machine learning|\bml engineer|data scien|llm|computer vision|"
                       r"deep learning|mlops|\bnlp\b|ky su ai|khoa hoc du lieu|ai/ml|applied ai|ai research")


def choose(rows: list) -> list:
    """120 ngẫu nhiên + 30 chức danh nhắc AI/ML + 30 chức danh có cụm AI/ML chặt hơn (đợt hai, để đủ 30 tin
    AI/ML hoặc khoa học dữ liệu theo nhãn tay: đợt một chỉ có 16)."""
    rnd = random.Random(SEED)
    picked = rnd.sample(rows, 120)
    chosen = {r[0] for r in picked}
    ai_pool = [r for r in rows if r[0] not in chosen and AI_TITLE.search(fold(r[2]))]
    ai = rnd.sample(ai_pool, 30)
    chosen |= {r[0] for r in ai}
    strict_pool = [r for r in rows if r[0] not in chosen and AI_STRICT.search(fold(r[2]))]
    return picked + ai + rnd.sample(strict_pool, 30)


HOLDOUT_SEED = 2830


def holdout(rows: list) -> list:
    """40 tin ngẫu nhiên ngoài mẫu chính, gán nhãn sau khi luật đã chốt: không dùng để sửa luật."""
    used = {r[0] for r in choose(rows)}
    return random.Random(HOLDOUT_SEED).sample([r for r in rows if r[0] not in used], 40)


def main() -> None:
    which = "holdout" if sys.argv[1] == "holdout" else "main"
    args = sys.argv[2:] if which == "holdout" else sys.argv[1:]
    start, count = int(args[0]), int(args[1])
    engine = create_engine(os.environ["HAIDO_EVAL_DATABASE_URL"])
    cfg = load_classify_config()
    rows = postings(engine)
    picked = holdout(rows) if which == "holdout" else choose(rows)
    for i, (url, site, title, job_level, exp_level, desc) in enumerate(picked[start : start + count], start):
        body = requirement_text(desc, cfg)
        req = body.find("yeu cau")
        if req < 0:
            req = body.find("requirement")
        excerpt = body[max(req, 0) : max(req, 0) + 650].replace("\n", " | ")
        print(f"### {i} {url_key(url)} [{site}] {title} | cấp nguồn: {job_level or ''} {exp_level or ''}")
        print(excerpt)
        print()


if __name__ == "__main__":
    main()
