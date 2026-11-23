"""Kỹ năng thô mà tin của snapshot mới nhất nhắc tới, và kỹ năng nào đã có mã (#278). Chỉ đọc.

Dân số: mọi tin có dòng vòng đời ở snapshot đọc được mới nhất (`published` hoặc `partial`), thấy lần cuối trong cửa sổ
`window_days` ngày, nguồn không bị loại (`excluded_sources`), nhãn đã lưu là IT (khác `không thuộc IT`). Đếm theo tin,
không gộp cụm như `aggregate`, nên số tin ở đây có thể lớn hơn `n` của ô một chút; ngưỡng "20 tin" của #278 dùng số này.

Chuỗi kỹ năng thô lấy từ bảng `jobs` của scraper: `skills` (thẻ kỹ năng của site) và `skills_raw` (kỹ năng nguyên văn,
nếu có). Hai chuỗi cùng dạng gấp (`fold`: bỏ dấu, chữ thường) là một kỹ năng. Một tin nhắc một kỹ năng thì đếm một lần.
Không đọc văn bản JD, không ghi gì: hai engine đều chỉ-đọc.

In một JSON ra stdout:
- `skills`: mỗi kỹ năng một dòng, số tin giảm dần: `key`, `postings`, `code` (mã của từ vựng hiện hành hoặc `null`),
  `spellings` (tối đa 5 cách viết hay gặp nhất cùng số tin), `sources`.
- `roles`: mỗi vai trò: `postings`, `mentions` (lượt nhắc thô), `mapped` (lượt nhắc tra được mã), `share`.
- `meta`: snapshot, cửa sổ, phiên bản từ vựng và phiên bản luật phân loại đã dùng.

Chạy trên VPS qua container API đã deploy (chỉ đọc, không in thông tin đăng nhập):

    ssh <vps> 'docker exec -i haido-prod-api-1 python -' < tools/vocab/skill_gaps.py > skill_gaps.json

Ở máy dev: `HAIDO_DATABASE_URL=... HAIDO_SCRAPER_DATABASE_URL=... uv run python tools/vocab/skill_gaps.py`.

Đo lại ngoại tuyến, không cần DB: `uv run python tools/vocab/skill_gaps.py --after skill_gaps.json [--min-postings 20]`
đọc đầu ra của chính script (khóa `code` và `roles`; file đã lọc của #278 dùng `code_before`/`roles_before` cũng được),
chỉ giữ khóa có từ `--min-postings` tin, và tra lại từng khóa với từ vựng hiện hành (số "sau" ở mức khóa; tỷ lệ theo
vai trò cần chạy lại trên prod).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent.parent.parent  # chạy từ tools/vocab: gốc repo
if (
    _ROOT / "haido_core"
).is_dir():  # đưa qua stdin vào image đã có haido_core thì không cần
    sys.path.insert(0, str(_ROOT))

import sqlalchemy as sa
from sqlalchemy import Connection, Engine

from haido_core.config import RulesConfig, load_rules
from haido_core.db import snapshot_store
from haido_core.db.engine import make_read_engine, make_source_engine
from haido_core.db.scraper_source import SCRAPER_SCHEMA
from haido_core.db.tables import snapshots
from haido_core.domain.classify import NON_IT
from haido_core.domain.population import window_start
from haido_core.domain.posting_text import fold
from haido_core.vocab.skills import Vocabulary, load_exclusions, load_vocabulary

READABLE = ("published", "partial")
MAX_SPELLINGS = 5
URL_BATCH = 500
MIN_POSTINGS = 20  # ngưỡng "20 tin" của #278


@dataclass(frozen=True, slots=True)
class Posting:
    source: str
    role: str
    raw_skills: tuple[str, ...]


def _env_urls() -> None:
    """Cùng cách suy URL với `deploy/warehouse-night.sh`: thiếu biến của kho thì lấy `DATABASE_URL` của scraper."""
    base = os.getenv("DATABASE_URL", "")
    if not os.getenv("HAIDO_DATABASE_URL") and base:
        for prefix in ("postgresql+psycopg://", "postgresql://", "postgres://"):
            if base.startswith(prefix):
                os.environ["HAIDO_DATABASE_URL"] = (
                    "postgresql+psycopg://" + base[len(prefix) :]
                )
                break
    if not os.getenv("HAIDO_SCRAPER_DATABASE_URL"):
        # Prod đặt kho (schema `haido`) và bảng của scraper (schema `public`) chung một DB, nên trong container API chỉ
        # có `HAIDO_DATABASE_URL` thì đọc bảng của scraper qua chính URL đó (engine nguồn vẫn chỉ-đọc).
        fallback = base or os.getenv("HAIDO_DATABASE_URL", "")
        if fallback:
            os.environ["HAIDO_SCRAPER_DATABASE_URL"] = fallback


def latest_snapshot(conn: Connection) -> date | None:
    stmt = (
        sa.select(snapshots.c.snapshot_id)
        .where(snapshots.c.status.in_(READABLE))
        .order_by(snapshots.c.snapshot_id.desc())
        .limit(1)
    )
    return conn.execute(stmt).scalar_one_or_none()


def counted_postings(
    conn: Connection, day: date, rules: RulesConfig
) -> dict[str, tuple[str, str]]:
    """`source_url -> (nguồn, vai trò)` của các tin trong dân số (xem docstring của module)."""
    first_day = window_start(day, rules.window_days)
    excluded = {s.strip().lower() for s in rules.excluded_sources}
    lives = [
        (pid, source)
        for pid, source, seen in snapshot_store.lifecycle_postings(conn, day)
        if seen >= first_day and source.strip().lower() not in excluded
    ]
    facts = snapshot_store.facts_at(conn, day)
    urls = snapshot_store.posting_urls(conn, [pid for pid, _ in lives])
    out: dict[str, tuple[str, str]] = {}
    for pid, source in lives:
        fact = facts.get(pid)
        if fact is None or fact.role is None or fact.role == NON_IT or pid not in urls:
            continue
        out[urls[pid]] = (source, fact.role)
    return out


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except ValueError:
            return [part.strip() for part in value.split(",") if part.strip()]
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def raw_skills(conn: Connection, urls: Sequence[str]) -> dict[str, tuple[str, ...]]:
    """`job_url -> chuỗi kỹ năng thô` (thẻ của site cộng kỹ năng nguyên văn), theo thứ tự đọc, bỏ trùng."""
    has_raw = (
        conn.execute(
            sa.text(
                "SELECT 1 FROM information_schema.columns WHERE table_schema = :s AND table_name = 'jobs' "
                "AND column_name = 'skills_raw'"
            ),
            {"s": SCRAPER_SCHEMA},
        ).first()
        is not None
    )
    cols = "j.job_url, j.skills" + (", j.skills_raw" if has_raw else "")
    out: dict[str, tuple[str, ...]] = {}
    for i in range(0, len(urls), URL_BATCH):
        batch = list(urls[i : i + URL_BATCH])
        stmt = sa.text(
            f"SELECT {cols} FROM {SCRAPER_SCHEMA}.jobs j WHERE j.job_url = ANY(:u)"
        )
        for row in conn.execute(stmt, {"u": batch}):
            items = _strings(row[1]) + (_strings(row[2]) if has_raw else [])
            out[row[0]] = tuple(dict.fromkeys(items))
    return out


def summarize(postings: Iterable[Posting], vocab: Vocabulary) -> dict[str, Any]:
    """Bảng kỹ năng và bảng vai trò từ các tin (hàm thuần, test được không cần DB)."""
    per_key: Counter[str] = Counter()
    spellings: dict[str, Counter[str]] = defaultdict(Counter)
    sources: dict[str, set[str]] = defaultdict(set)
    roles: dict[str, list[int]] = defaultdict(
        lambda: [0, 0, 0]
    )  # tin, lượt nhắc, lượt có mã
    for posting in postings:
        bucket = roles[posting.role]
        bucket[0] += 1
        seen: set[str] = set()
        for text in posting.raw_skills:
            key = fold(text).strip()
            if not key or key in seen:
                continue
            seen.add(key)
            per_key[key] += 1
            spellings[key][text] += 1
            sources[key].add(posting.source)
            bucket[1] += 1
            bucket[2] += key in vocab.lookup or key in vocab.composites
    skills = [
        {
            "key": key,
            "postings": count,
            "code": vocab.lookup.get(key)
            or (
                "+".join(vocab.lookup[p] for p in vocab.composites[key])
                if key in vocab.composites
                else None
            ),
            "spellings": spellings[key].most_common(MAX_SPELLINGS),
            "sources": sorted(sources[key]),
        }
        for key, count in sorted(per_key.items(), key=lambda kv: (-kv[1], kv[0]))
    ]
    role_rows = {
        role: {
            "postings": p,
            "mentions": m,
            "mapped": k,
            "share": (k / m) if m else None,
        }
        for role, (p, m, k) in sorted(roles.items())
    }
    return {"skills": skills, "roles": role_rows}


def collect(
    warehouse: Engine, scraper: Engine, rules: RulesConfig, vocab: Vocabulary
) -> dict[str, Any]:
    with warehouse.connect() as conn:
        day = latest_snapshot(conn)
        if day is None:
            raise SystemExit("Chưa có snapshot đọc được (published hoặc partial).")
        population = counted_postings(conn, day, rules)
    with scraper.connect() as conn:
        raw = raw_skills(conn, sorted(population))
    postings = [
        Posting(source, role, raw.get(url, ()))
        for url, (source, role) in population.items()
    ]
    result = summarize(postings, vocab)
    result["meta"] = {
        "snapshot": day.isoformat(),
        "window_days": rules.window_days,
        "postings": len(postings),
        "postings_with_raw_skills": sum(1 for p in postings if p.raw_skills),
        "vocab_version": vocab.version,
        "vocab_codes": len(set(vocab.lookup.values())),
    }
    return result


def remap(
    gaps: dict[str, Any], vocab: Vocabulary, excluded: frozenset[str], min_postings: int = MIN_POSTINGS
) -> dict[str, Any]:
    """Tra lại các khóa của một lần chạy trước với từ vựng `vocab` (không cần DB).

    Nhận thẳng đầu ra của chính script (`skills[].code`, `roles`) hoặc file đã lọc của #278 (`code_before`,
    `roles_before`). Chỉ các khóa có từ `min_postings` tin trở lên được tính (đầu ra thô của script có đủ mọi khóa).

    Một lượt nhắc "có mã" khi khóa của nó nằm trong `lookup` hoặc `composites`, cùng quy tắc với `summarize`.
    `unresolved` là khóa vừa không có mã vừa không nằm trong danh sách loại trừ (AC1 của #278 đòi danh sách này rỗng).
    """
    skills = [s for s in gaps["skills"] if s["postings"] >= min_postings]
    total = sum(s["postings"] for s in skills)

    def mapped(key: str) -> bool:
        return key in vocab.lookup or key in vocab.composites

    before = [s for s in skills if (s["code_before"] if "code_before" in s else s.get("code")) is not None]
    after = [s for s in skills if mapped(s["key"])]
    unresolved = [s["key"] for s in skills if not mapped(s["key"]) and s["key"] not in excluded]
    return {
        "vocab_version_before": gaps.get("meta", {}).get("vocab_version"),
        "vocab_version_after": vocab.version,
        "keys": len(skills),
        "keys_mapped_before": len(before),
        "keys_mapped_after": len(after),
        "keys_excluded": sum(1 for s in skills if s["key"] in excluded),
        "keys_unresolved": unresolved,
        "tag_mentions": total,
        "tag_mentions_mapped_before": sum(s["postings"] for s in before),
        "tag_mentions_mapped_after": sum(s["postings"] for s in after),
        "tag_mention_share_before": sum(s["postings"] for s in before) / total if total else None,
        "tag_mention_share_after": sum(s["postings"] for s in after) / total if total else None,
        "roles_before": gaps.get("roles_before", gaps.get("roles", {})),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--after", type=Path, help="đo lại ngoại tuyến từ file JSON của một lần chạy trước")
    parser.add_argument(
        "--min-postings", type=int, default=MIN_POSTINGS, help="với --after: bỏ khóa có ít tin hơn số này (mặc định 20)"
    )
    args = parser.parse_args(argv)
    if args.after is not None:
        gaps = json.loads(args.after.read_text(encoding="utf-8"))
        report = remap(gaps, load_vocabulary(), load_exclusions().keys, args.min_postings)
        json.dump(report, sys.stdout, ensure_ascii=False, indent=1)
        sys.stdout.write("\n")
        return 0
    _env_urls()
    rules = load_rules()
    result = collect(make_read_engine(), make_source_engine(), rules, load_vocabulary())
    json.dump(result, sys.stdout, ensure_ascii=False, indent=1)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
