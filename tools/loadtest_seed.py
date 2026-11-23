"""Nạp DB đo tải (#342): một snapshot đã công bố từ dữ liệu giả, sinh qua các bước thật của kho.

    HAIDO_TEST_DATABASE_URL=postgresql+psycopg://haido:haido_local@127.0.0.1:5434/haido_load_test \
        uv run python -m tools.loadtest_seed [--facts 5600] [--seed 342]

Script XÓA schema `haido` của DB trỏ tới (host local, tên DB kết thúc bằng `_test`), dựng lại bằng Alembic, nạp
`--facts` tin giả như `tools/bench_skill_rates.py` (kỹ năng phân bố Zipf, quan sát trong ba ngày, `lifecycle` thật),
rồi chạy `aggregate` và `publish` cho ngày cuối. Mọi nguồn tự động có lượt chạy hoàn tất, nên snapshot là
`published`, giống một đêm khỏe trên production.
"""

import argparse
import os
import sys
from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url

from haido_core.config import load_rules
from haido_core.db import snapshot_store
from haido_core.db.migrations.env import validate_migration_target
from haido_core.db.snapshot_store import RunValues
from haido_core.steps.aggregate import aggregate_snapshot
from haido_core.steps.publish import PublishResult, publish_snapshot
from tools.bench_skill_rates import _build

DAY = date(2026, 11, 10)


def check_target(url: str) -> str:
    """Trả URL nếu là DB local tên kết thúc bằng `_test`; ngược lại `ValueError`. Không kết nối."""
    checked = validate_migration_target(url, allow_remote=False)
    if not (make_url(checked).database or "").endswith("_test"):
        raise ValueError("DB phải có tên kết thúc bằng _test (script xóa schema haido).")
    return checked


def seed(url: str, *, facts: int, rng_seed: int, day: date = DAY) -> PublishResult:
    """Dựng lại schema, nạp `facts` tin giả, tổng hợp và công bố snapshot `day`."""
    url = check_target(url)
    _build(url, facts, rng_seed, day)
    rules = load_rules()
    engine = create_engine(url)
    try:
        with engine.begin() as conn:
            snapshot_store.upsert_runs(conn, day, (RunValues(s, "auto", True, 0, None) for s in rules.auto_sources))
        aggregate_snapshot(day.isoformat(), engine=engine, rules=rules)
        return publish_snapshot(day.isoformat(), engine=engine, rules=rules)
    finally:
        engine.dispose()


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--facts", type=int, default=5600)
    parser.add_argument("--seed", type=int, default=342)
    args = parser.parse_args()
    raw = os.environ.get("HAIDO_TEST_DATABASE_URL", "").strip()
    if not raw:
        sys.exit("HAIDO_TEST_DATABASE_URL chưa đặt.")
    try:
        result = seed(raw, facts=args.facts, rng_seed=args.seed)
    except ValueError as exc:
        sys.exit(str(exc))
    print(f"{args.facts} tin giả, snapshot {result.snapshot_id} {result.status}")


if __name__ == "__main__":
    main()
