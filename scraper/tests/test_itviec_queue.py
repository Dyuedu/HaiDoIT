"""Hàng đợi SQLite và export JSONL của đường nodriver trong crawlers.itviec.

Không cần nodriver: các hàm này nằm ở cấp module.
"""

import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from crawlers import itviec  # noqa: E402

NOW = datetime(2026, 11, 20, 12, 0, 0)


def make_db(path, rows):
    """rows: (job_url, status, retry_count, updated_at)."""
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE job_queue (job_url TEXT PRIMARY KEY, title TEXT, company_name TEXT, "
        "salary_preview TEXT, location TEXT, work_model TEXT, skills_json TEXT, "
        "status TEXT DEFAULT 'PENDING', retry_count INTEGER DEFAULT 0, "
        "discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP)"
    )
    conn.execute(
        "CREATE TABLE job_details (job_url TEXT PRIMARY KEY, title TEXT, company_name TEXT, "
        "salary TEXT, location TEXT, work_model TEXT, skills_json TEXT, description_text TEXT, "
        "date_posted TEXT, employment_type TEXT, experience_months INTEGER, raw_json_ld TEXT, "
        "scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, synced_to_pg INTEGER DEFAULT 0)"
    )
    for url, status, retries, updated in rows:
        conn.execute(
            "INSERT INTO job_queue (job_url, status, retry_count, updated_at) VALUES (?,?,?,?)",
            (url, status, retries, updated),
        )
    conn.commit()
    return conn


def urls(rows):
    return sorted(r[0] for r in rows)


# ------------------------------------------------------------- queue_batch


def test_queue_takes_pending_and_failed_under_the_retry_cap(tmp_path):
    conn = make_db(tmp_path / "q.db", [
        ("p", "PENDING", 0, None),
        ("f1", "FAILED", 1, NOW.isoformat()),
        ("done", "COMPLETED", 0, NOW.isoformat()),
    ])
    assert urls(itviec.queue_batch(conn, 0, NOW)) == ["f1", "p"]


def test_exhausted_failed_job_waits_then_gets_a_fresh_try(tmp_path):
    conn = make_db(tmp_path / "q.db", [
        ("recent", "FAILED", 3, "2026-11-18T12:00:00"),
        ("old", "FAILED", 3, "2026-11-10T12:00:00"),
    ])
    assert urls(itviec.queue_batch(conn, 0, NOW)) == ["old"]


def test_queue_respects_the_batch_size_pending_first(tmp_path):
    conn = make_db(tmp_path / "q.db", [
        ("f1", "FAILED", 1, NOW.isoformat()),
        ("p", "PENDING", 0, None),
    ])
    assert urls(itviec.queue_batch(conn, 1, NOW)) == ["p"]


# ------------------------------------------------------------- export_jsonl


def add_detail(conn, url, desc):
    conn.execute("UPDATE job_queue SET status='COMPLETED' WHERE job_url=?", (url,))
    conn.execute(
        "INSERT INTO job_details (job_url, title, description_text, skills_json) VALUES (?,?,?,?)",
        (url, "t", desc, "[]"),
    )
    conn.commit()


def read(path):
    return [json.loads(x) for x in Path(path).read_text(encoding="utf-8").splitlines()]


def test_export_replaces_a_row_without_description_instead_of_duplicating(tmp_path):
    db = tmp_path / "q.db"
    out = tmp_path / "itviec.jsonl"
    out.write_text(
        json.dumps({"site": "itviec", "job_url": "a", "title": "old"}) + "\n"
        + json.dumps({"site": "itviec", "job_url": "b", "description": "giu nguyen"}) + "\n",
        encoding="utf-8",
    )
    conn = make_db(db, [("a", "PENDING", 0, None), ("c", "PENDING", 0, None)])
    add_detail(conn, "a", "mo ta a")
    add_detail(conn, "c", "mo ta c")
    conn.close()

    itviec.export_jsonl(db, out)

    rows = read(out)
    assert [r["job_url"] for r in rows] == ["a", "b", "c"]
    assert rows[0]["description"] == "mo ta a"
    assert rows[1]["description"] == "giu nguyen"


def test_export_appends_only_when_nothing_is_replaced(tmp_path):
    db = tmp_path / "q.db"
    out = tmp_path / "itviec.jsonl"
    first = json.dumps({"site": "itviec", "job_url": "b", "description": "x"}) + "\n"
    out.write_text(first, encoding="utf-8")
    conn = make_db(db, [("b", "PENDING", 0, None), ("c", "PENDING", 0, None)])
    add_detail(conn, "b", "khac")
    add_detail(conn, "c", "mo ta c")
    conn.close()

    itviec.export_jsonl(db, out)

    rows = read(out)
    assert [r["job_url"] for r in rows] == ["b", "c"]
    assert rows[0]["description"] == "x"
