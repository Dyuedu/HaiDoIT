"""Đo thời gian bước `aggregate` có và không tính tỷ lệ kỹ năng (#101). In bảng Markdown.

    HAIDO_TEST_DATABASE_URL=postgresql+psycopg://haido:haido_local@127.0.0.1:5433/<tên>_test \
        PYTHONPATH=. uv run python tools/bench_skill_rates.py [--facts 5600] [--runs 7] [--seed 101]

Script XÓA schema `haido` của DB trỏ tới (tên phải kết thúc bằng `_test`, host local), dựng lại bằng Alembic, rồi nạp
dữ liệu giả: `--facts` tin với kỹ năng phân bố Zipf trên từ vựng hiện hành, nhãn đã lưu như `ingest` ghi, quan sát
trong ba ngày liên tiếp và dòng vòng đời do bước `lifecycle` thật sinh ra. Sau đó chạy `aggregate_snapshot` nhiều lần
cho ngày cuối, mỗi lần ở hai chế độ xen kẽ (tắt rồi bật):

- `bật`: bước như trong sản phẩm;
- `tắt`: `aggregate_skill_rates` được thay bằng hàm trả rỗng, nên không có hàng `stat_skill_rates`.

Với mỗi chế độ, bảng báo trung vị và khoảng (nhỏ nhất–lớn nhất) của: tổng thời gian bước, thời gian tính tỷ lệ kỹ năng
(`aggregate_skill_rates`), thời gian ghi (`replace_stats`, một transaction). Phần còn lại là việc không đổi của bước
(đọc dữ kiện, phân loại, gộp cụm, tính ô).
"""

import argparse
import os
import random
import statistics
import sys
import time
from collections.abc import Callable
from datetime import date, timedelta
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from haido_core.config import load_classify_config, load_rules
from haido_core.db import snapshot_store
from haido_core.db.migrations.env import validate_migration_target
from haido_core.db.snapshot_store import FactVersion, RunValues
from haido_core.steps import aggregate as aggregate_module
from haido_core.steps.aggregate import aggregate_snapshot
from haido_core.steps.lifecycle import lifecycle_snapshot
from haido_core.vocab.skills import load_seed_skills, seed_version

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ("itviec", "topdev", "vietnamworks", "topcv")
TITLES = (
    "Backend Developer", "Frontend Developer", "Fullstack Engineer", "Data Engineer", "Data Analyst", "QA Engineer",
    "DevOps Engineer", "Mobile Developer", "Business Analyst", "AI Engineer", "Security Engineer", "Embedded Engineer",
)  # fmt: skip


def _alembic_config() -> Config:
    cfg = Config()
    cfg.set_main_option("script_location", str(ROOT / "haido_core" / "db" / "migrations"))
    return cfg


def _build(url: str, n_facts: int, seed: int, day: date) -> None:
    rng = random.Random(seed)
    rules = load_rules()
    classify = load_classify_config()
    codes = [skill.code for skill in load_seed_skills()]
    weights = [1 / (rank + 1) ** 1.1 for rank in range(len(codes))]  # Zipf: vài mã rất hay gặp, đuôi dài
    roles = [label for label in rules.role_codes if label != "Other"]
    levels = list(rules.level_codes)
    cities = list(rules.city_codes)
    days = [day - timedelta(days=2), day - timedelta(days=1), day]
    companies = [f"Công ty {i}" for i in range(max(50, n_facts // 3))]

    engine = create_engine(url)
    with engine.begin() as conn:
        conn.exec_driver_sql("DROP SCHEMA IF EXISTS haido CASCADE; DROP TABLE IF EXISTS public.alembic_version")
    os.environ["HAIDO_DATABASE_URL"] = url
    command.upgrade(_alembic_config(), "head")

    pairs = [(rng.choice(SOURCES), f"https://bench.test/{i}") for i in range(n_facts)]
    seen_on = [sorted(rng.sample(days, rng.randint(1, len(days)))) for _ in pairs]
    with engine.begin() as conn:
        for d in days:
            snapshot_store.insert_open(conn, d)
        ids = snapshot_store.ensure_postings(conn, pairs)
        run_ids: dict[tuple[date, str], int] = {}
        for d in days:
            runs = snapshot_store.upsert_runs(conn, d, (RunValues(s, "auto", True, 0, None) for s in SOURCES))
            run_ids.update({(d, s): rid for s, rid in runs.items()})
        for pair, first_days in zip(pairs, seen_on, strict=True):
            posting_id = ids[pair]
            k = min(len(codes), max(1, int(rng.lognormvariate(1.9, 0.5))))
            skills = tuple(sorted({c: rng.randint(1, 3) for c in rng.choices(codes, weights, k=k)}.items()))
            role = rng.choice(roles)
            fact = FactVersion(
                rng.choice(TITLES), rng.choice(companies), rng.choice(cities), None, rng.choice(levels), None,
                role, None, rng.choice(levels), skills, classify.version, rng.choice(cities), seed_version(),
            )  # fmt: skip
            snapshot_store.insert_facts(conn, first_days[0], [(posting_id, fact)])
            snapshot_store.insert_observations(
                conn, first_days[0], [(posting_id, run_ids[(first_days[0], pair[0])])]
            )
            for d in first_days[1:]:
                snapshot_store.insert_observations(conn, d, [(posting_id, run_ids[(d, pair[0])])])
    for d in days:
        lifecycle_snapshot(d.isoformat(), engine=engine, rules=rules)
    engine.dispose()


def _timed(sink: list[float], fn: Callable) -> Callable:
    def run(*args, **kwargs):
        start = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            sink.append(time.perf_counter() - start)

    return run


def _measure(url: str, day: date, runs: int) -> dict[str, dict[str, list[float]]]:
    engine = create_engine(url)
    rules = load_rules()
    real_rates = aggregate_module.aggregate_skill_rates
    real_replace = snapshot_store.replace_stats
    out: dict[str, dict[str, list[float]]] = {m: {"total": [], "compute": [], "insert": []} for m in ("bật", "tắt")}
    try:
        aggregate_snapshot(day.isoformat(), engine=engine, rules=rules)  # làm nóng bộ nhớ đệm, không tính
        for _ in range(runs):
            for mode in ("tắt", "bật"):  # chế độ bật chạy sau cùng: số hàng báo cuối là của chế độ bật
                sink = out[mode]
                rates = real_rates if mode == "bật" else (lambda *a, **k: ())
                aggregate_module.aggregate_skill_rates = _timed(sink["compute"], rates)
                snapshot_store.replace_stats = _timed(sink["insert"], real_replace)
                start = time.perf_counter()
                aggregate_snapshot(day.isoformat(), engine=engine, rules=rules)
                sink["total"].append(time.perf_counter() - start)
    finally:
        aggregate_module.aggregate_skill_rates = real_rates
        snapshot_store.replace_stats = real_replace
        with engine.connect() as conn:
            counts = {
                t: conn.execute(text(f"SELECT count(*) FROM haido.{t}")).scalar_one()
                for t in ("job_posting_facts", "stat_job_lifecycle", "stat_cells", "stat_skill_rates")
            }
        engine.dispose()
    print(f"Số hàng sau lượt cuối (chế độ bật): {counts}\n")
    return out


def _cell(values: list[float]) -> str:
    return f"{statistics.median(values):.3f} ({min(values):.3f}–{max(values):.3f})"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # bảng có tiếng Việt; stdout Windows mặc định cp1252
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--facts", type=int, default=5600)
    parser.add_argument("--runs", type=int, default=7)
    parser.add_argument("--seed", type=int, default=101)
    args = parser.parse_args()
    if args.runs < 5:
        sys.exit("--runs phải từ 5 trở lên để báo trung vị và khoảng.")
    raw = os.environ.get("HAIDO_TEST_DATABASE_URL", "").strip()
    if not raw:
        sys.exit("HAIDO_TEST_DATABASE_URL chưa đặt.")
    url = validate_migration_target(raw, allow_remote=False)
    if not (make_url(url).database or "").endswith("_test"):
        sys.exit("DB phải có tên kết thúc bằng _test (script xóa schema haido).")
    day = date(2026, 11, 10)
    _build(url, args.facts, args.seed, day)
    print(f"{args.facts} dữ kiện, {args.runs} lượt mỗi chế độ, seed {args.seed}, từ vựng {seed_version()}\n")
    result = _measure(url, day, args.runs)
    print("Giây, trung vị (nhỏ nhất–lớn nhất):\n")
    print("| Chế độ | Tổng bước | Tính tỷ lệ kỹ năng | Ghi (`replace_stats`) |")
    print("|---|---|---|---|")
    for mode, cols in result.items():
        print(f"| {mode} | {_cell(cols['total'])} | {_cell(cols['compute'])} | {_cell(cols['insert'])} |")
    on, off = result["bật"], result["tắt"]
    delta = statistics.median(on["total"]) - statistics.median(off["total"])
    print(f"\nChênh lệch trung vị tổng: {delta:+.3f} giây ({statistics.median(on['total']) / statistics.median(off['total']):.2f} lần).")


if __name__ == "__main__":
    main()
