"""In bảng hiệu chỉnh θ (#102): số kỹ năng core và common của từng vai trò, cho nhiều cặp θ. Chỉ đọc.

    HAIDO_DATABASE_URL=postgresql+psycopg://... PYTHONPATH=. uv run python tools/theta/calibrate_theta.py \
        [--level entry] [--pairs 0.3/0.1,0.25/0.1,0.35/0.12,0.4/0.15]

Đọc `snapshots`, `stat_skill_rates` và `stat_sources` của snapshot đọc được mới nhất (`published` hoặc `partial`, có hàng tỷ
lệ và có nguồn: cùng điều kiện với `_latest_with_skill_rates` của API), ô toàn
quốc, nhánh `all`, số năm `any`, ở cấp `--level` (mặc định `entry`). Chỉ vai trò có `n_scanned >= min_sample` (lấy từ
`config/rules.toml`); ô `all` không phải vai trò nên bị bỏ. Không đọc bảng tin, không ghi gì: engine đọc của API mở mỗi
transaction ở chế độ chỉ-đọc.

Mỗi ô của bảng là `core,common`: số kỹ năng có `rate >= θ_core`, và số kỹ năng có `θ_common <= rate < θ_core` (đúng bằng
số dòng `common` mà API trả). Kỹ năng rare không được đếm. In cùng dạng bảng với `docs/data/theta.md` (bảng đó lấy từ API
`skill-roles` công khai của snapshot 2026-11-19).
"""

import argparse
import sys
from dataclasses import dataclass
from datetime import date

import sqlalchemy as sa
from sqlalchemy import Engine

from haido_core.config import ALL_ROLES, load_rules
from haido_core.db.tables import snapshots, stat_skill_rates, stat_sources

READABLE = ("published", "partial")


@dataclass(frozen=True, slots=True)
class Pair:
    theta_core: float
    theta_common: float

    @property
    def label(self) -> str:
        return f"{self.theta_core:g}/{self.theta_common:g}"


PAIRS = (Pair(0.3, 0.1), Pair(0.25, 0.1), Pair(0.35, 0.12), Pair(0.4, 0.15))
"""Các cặp của bảng bằng chứng trong `docs/data/theta.md`; cặp đầu là cặp đã chọn."""


@dataclass(frozen=True, slots=True)
class RoleRow:
    role: str
    n_scanned: int
    counts: dict[Pair, tuple[int, int]]
    """Cặp θ -> (số kỹ năng core, số kỹ năng common)."""


def parse_pairs(text: str) -> tuple[Pair, ...]:
    """`0.3/0.1,0.4/0.15` thành các cặp. θ phải trong [0, 1] và `common <= core`."""
    pairs = []
    for part in text.split(","):
        try:
            core, common = (float(x) for x in part.split("/"))
        except ValueError:
            raise ValueError(f"Cặp θ phải có dạng core/common, nhận {part!r}.") from None
        if not (0 <= common <= core <= 1):
            raise ValueError(f"Cặp θ {part!r} phải thỏa 0 <= common <= core <= 1.")
        pairs.append(Pair(core, common))
    return tuple(pairs)


def calibrate(
    engine: Engine, pairs: tuple[Pair, ...], *, level: str, min_sample: int
) -> tuple[date, list[RoleRow]]:
    """Ngày snapshot đã đọc và các dòng theo `n_scanned` giảm dần rồi mã vai trò.

    Raises:
        LookupError: chưa có snapshot đọc được nào có tỷ lệ kỹ năng.
    """
    t = stat_skill_rates
    has_rates = sa.exists().where(t.c.snapshot_id == snapshots.c.snapshot_id)
    has_sources = sa.exists().where(stat_sources.c.snapshot_id == snapshots.c.snapshot_id)
    latest = (
        sa.select(snapshots.c.snapshot_id)
        .where(snapshots.c.status.in_(READABLE), has_rates, has_sources)
        .order_by(snapshots.c.snapshot_id.desc())
        .limit(1)
    )
    with engine.connect() as conn:
        day = conn.execute(latest).scalar_one_or_none()
        if day is None:
            raise LookupError("Chưa có snapshot đã công bố nào có tỷ lệ kỹ năng.")
        rows = conn.execute(
            sa.select(t.c.role, t.c.n_scanned, t.c.rate).where(
                t.c.snapshot_id == day,
                t.c.seniority == level,
                t.c.scope == "vn",
                t.c.branch == "all",
                t.c.years == "any",
                t.c.role != ALL_ROLES,
                t.c.n_scanned >= min_sample,
            )
        ).all()
    rates: dict[str, list[float]] = {}
    scanned: dict[str, int] = {}
    for role, n_scanned, rate in rows:
        rates.setdefault(role, []).append(rate)
        scanned[role] = n_scanned
    out = [
        RoleRow(
            role,
            scanned[role],
            {
                p: (
                    sum(r >= p.theta_core for r in values),
                    sum(p.theta_common <= r < p.theta_core for r in values),
                )
                for p in pairs
            },
        )
        for role, values in rates.items()
    ]
    out.sort(key=lambda r: (-r.n_scanned, r.role))
    return day, out


def render(day: date, rows: list[RoleRow], pairs: tuple[Pair, ...], *, level: str, min_sample: int) -> str:
    """Bảng Markdown. Mỗi ô là `core,common`."""
    lines = [
        f"Snapshot {day.isoformat()}, cấp {level}, vai trò có từ {min_sample} tin đọc được kỹ năng. Mỗi ô là core,common.",
        "",
        "| vai trò (n) | " + " | ".join(p.label for p in pairs) + " |",
        "|---|" + "---|" * len(pairs),
    ]
    for row in rows:
        cells = " | ".join(f"{row.counts[p][0]},{row.counts[p][1]}" for p in pairs)
        lines.append(f"| {row.role} ({row.n_scanned}) | {cells} |")
    return "\n".join(lines)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # bảng có tiếng Việt; stdout Windows mặc định cp1252
    from haido_core.db.engine import make_read_engine

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--level", default="entry")
    parser.add_argument("--pairs", default=",".join(p.label for p in PAIRS))
    args = parser.parse_args()
    try:
        pairs = parse_pairs(args.pairs)
    except ValueError as exc:
        sys.exit(str(exc))
    min_sample = load_rules().min_sample
    engine = make_read_engine()
    try:
        day, rows = calibrate(engine, pairs, level=args.level, min_sample=min_sample)
    except LookupError as exc:
        sys.exit(str(exc))
    print(render(day, rows, pairs, level=args.level, min_sample=min_sample))


if __name__ == "__main__":
    main()
