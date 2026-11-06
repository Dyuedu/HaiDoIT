"""CLI `haido` (Story 1.4): `haido ingest|lifecycle --snapshot YYYY-MM-DD`.

Mỗi lệnh là một bước ở `haido_core/steps/`, chạy tay hoặc từ lịch; không phụ thuộc Dagster.
Mã thoát 0 là thành công, 1 là lỗi đã biết (thông báo tiếng Việt ở stderr, không in URL hay
mật khẩu), 2 là cú pháp lệnh sai.

    HAIDO_SCRAPER_DATABASE_URL   nguồn: bảng của scraper, đọc chỉ-đọc
    HAIDO_DATABASE_URL           đích: schema haido (host ngoài localhost cần HAIDO_ALLOW_REMOTE_WRITE=1)
"""

import argparse
import sys
from collections.abc import Callable, Sequence
from datetime import UTC, datetime

from sqlalchemy.exc import SQLAlchemyError

from haido_core.config import ConfigError, load_rules
from haido_core.db.engine import (
    DatabaseConfigError,
    make_source_engine,
    make_write_engine,
)
from haido_core.db.scraper_source import ScraperPostgresReader
from haido_core.domain.lifecycle import snapshot_id_at
from haido_core.steps.common import StepError, parse_snapshot_id
from haido_core.steps.ingest import ingest_snapshot
from haido_core.steps.lifecycle import lifecycle_snapshot


def _now() -> datetime:
    return datetime.now(UTC)


def _run_ingest(snapshot_id: str) -> str:
    rules = load_rules()
    target = source = None
    try:
        target = make_write_engine()
        source = make_source_engine()
        result = ingest_snapshot(snapshot_id, reader=ScraperPostgresReader(source), engine=target, rules=rules)
    finally:
        if source is not None:
            source.dispose()
        if target is not None:
            target.dispose()
    return (
        f"Đã ingest snapshot {result.snapshot_id.isoformat()} (open): {result.runs} lượt chạy, "
        f"{result.postings} tin, {result.observations} quan sát, {result.facts_added} dữ kiện mới."
    )


def _run_lifecycle(snapshot_id: str) -> str:
    rules = load_rules()
    target = make_write_engine()
    try:
        result = lifecycle_snapshot(snapshot_id, engine=target, rules=rules)
    finally:
        target.dispose()
    return (
        f"Đã tính vòng đời snapshot {result.snapshot_id.isoformat()}: {result.rows} tin "
        f"(config_version {result.config_version})."
    )


COMMANDS: dict[str, Callable[[str], str]] = {"ingest": _run_ingest, "lifecycle": _run_lifecycle}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="haido", description="Các bước chạy tay của Hải Đồ IT.")
    sub = parser.add_subparsers(dest="command", required=True)
    helps = {
        "ingest": "Mở snapshot S rồi chép lượt chạy, quan sát, dữ kiện tin của S từ bảng scraper (chỉ thêm).",
        "lifecycle": "Tính vòng đời tin tới S và ghi stat_job_lifecycle.",
    }
    for name, text in helps.items():
        cmd = sub.add_parser(name, help=text, description=text)
        cmd.add_argument(
            "--snapshot",
            metavar="YYYY-MM-DD",
            help="Ngày snapshot theo Asia/Ho_Chi_Minh (mặc định: hôm nay).",
        )
    return parser


def _utf8_output() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
        except (AttributeError, ValueError):
            pass


def main(argv: Sequence[str] | None = None) -> int:
    _utf8_output()
    args = _build_parser().parse_args(argv)
    try:
        snapshot_id = args.snapshot if args.snapshot is not None else snapshot_id_at(_now())
        parse_snapshot_id(snapshot_id)
        print(COMMANDS[args.command](snapshot_id))
    except (StepError, DatabaseConfigError, ConfigError) as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        return 1
    except SQLAlchemyError as exc:
        # Không in nội dung lỗi của driver: có thể chứa host hoặc tham số kết nối.
        print(
            f"Lỗi cơ sở dữ liệu ({type(exc).__name__}): không hoàn tất, các hàng của lần chạy này đã được hoàn tác.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
