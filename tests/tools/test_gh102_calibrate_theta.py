"""#102 (DAT.30) — `tools/theta/calibrate_theta.py` in bảng số kỹ năng core và common theo vai trò cho nhiều cặp θ.

Chỉ đọc `snapshots` và `stat_skill_rates` (bảng `stat_*`), không đụng bảng tin `job_*`.
"""

import re
from collections.abc import Iterator

import pytest
from sqlalchemy import Engine, event, text

from tests.api.test_fr19_skill_rates_stat import _cell, _snapshot
from tools.theta.calibrate_theta import PAIRS, Pair, calibrate, parse_pairs, render

DAY = "2026-11-19"
OLDER = "2026-11-10"
# 40 cụm đã quét: java 0.6, python 0.4, sql 0.2, git 0.1, docker 0.05, rust 0
RATES = {"java": 24, "python": 16, "sql": 8, "git": 4, "docker": 2, "rust": 0}


@pytest.fixture
def statements(pg_engine: Engine) -> Iterator[list[str]]:
    seen: list[str] = []

    def record(conn, cursor, statement, parameters, context, executemany) -> None:
        seen.append(statement)

    event.listen(pg_engine, "before_cursor_execute", record)
    yield seen
    event.remove(pg_engine, "before_cursor_execute", record)


def _seed(engine: Engine) -> None:
    _snapshot(engine, DAY)
    _cell(engine, "backend", "entry", 80, 40, RATES, day=DAY)
    _cell(engine, "qa", "entry", 45, 35, {"java": 14, "sql": 7}, day=DAY)
    _cell(engine, "game", "entry", 20, 29, {"java": 29}, day=DAY)  # n_scanned 29 < 30: bị bỏ
    _cell(engine, "backend", "all", 500, 400, {"java": 300}, day=DAY)  # cấp khác: bị bỏ


def test_gh102_dem_core_va_common_theo_vai_tro_cho_tung_cap_theta(pg_engine: Engine) -> None:
    _seed(pg_engine)
    day, rows = calibrate(pg_engine, (Pair(0.3, 0.1), Pair(0.5, 0.15)), level="entry", min_sample=30)
    assert day.isoformat() == DAY
    assert [(r.role, r.n_scanned) for r in rows] == [("backend", 40), ("qa", 35)]  # n_scanned giảm dần
    backend, qa = rows
    # θ 0.3/0.1: core = java, python; common = sql, git (đúng 0.1 vào common); docker và rust là rare
    assert backend.counts[Pair(0.3, 0.1)] == (2, 2)
    # θ 0.5/0.15: core = java; common = python, sql; git 0.1 < 0.15 là rare
    assert backend.counts[Pair(0.5, 0.15)] == (1, 2)
    assert qa.counts[Pair(0.3, 0.1)] == (1, 1)  # java 0.4 core; sql 0.2 common


def test_gh102_dung_snapshot_doc_duoc_moi_nhat_va_bo_qua_snapshot_open(pg_engine: Engine) -> None:
    _snapshot(pg_engine, OLDER)
    _cell(pg_engine, "backend", "entry", 80, 40, {"java": 4}, day=OLDER)
    _snapshot(pg_engine, DAY, status="open")
    _cell(pg_engine, "backend", "entry", 80, 40, RATES, day=DAY)
    day, rows = calibrate(pg_engine, (Pair(0.3, 0.1),), level="entry", min_sample=30)
    assert day.isoformat() == OLDER
    assert rows[0].counts[Pair(0.3, 0.1)] == (0, 1)


def test_gh102_snapshot_moi_hon_co_ty_le_nhung_khong_co_nguon_bi_bo_qua(pg_engine: Engine) -> None:
    # Cùng điều kiện với `_latest_with_skill_rates` của API: snapshot không có `stat_sources` thì API không đọc nó.
    _snapshot(pg_engine, OLDER)
    _cell(pg_engine, "backend", "entry", 80, 40, {"java": 4}, day=OLDER)
    _snapshot(pg_engine, DAY, sources=())
    _cell(pg_engine, "backend", "entry", 80, 40, RATES, day=DAY)
    day, rows = calibrate(pg_engine, (Pair(0.3, 0.1),), level="entry", min_sample=30)
    assert day.isoformat() == OLDER
    assert rows[0].counts[Pair(0.3, 0.1)] == (0, 1)


def test_gh102_vai_tro_co_n_scanned_dung_bang_min_sample_duoc_tinh(pg_engine: Engine) -> None:
    _snapshot(pg_engine, DAY)
    _cell(pg_engine, "backend", "entry", 80, 30, {"java": 15}, day=DAY)  # n_scanned == min_sample
    _cell(pg_engine, "qa", "entry", 80, 29, {"java": 15}, day=DAY)  # dưới một đơn vị
    _, rows = calibrate(pg_engine, (Pair(0.3, 0.1),), level="entry", min_sample=30)
    assert [(r.role, r.n_scanned) for r in rows] == [("backend", 30)]


def test_gh102_khong_co_snapshot_doc_duoc_la_loi_ro(pg_engine: Engine) -> None:
    with pytest.raises(LookupError, match="snapshot"):
        calibrate(pg_engine, (Pair(0.3, 0.1),), level="entry", min_sample=30)


def test_gh102_bang_markdown_co_ngay_cot_theta_va_ghi_chu_core_common(pg_engine: Engine) -> None:
    _seed(pg_engine)
    day, rows = calibrate(pg_engine, (Pair(0.3, 0.1), Pair(0.5, 0.15)), level="entry", min_sample=30)
    text_out = render(day, rows, (Pair(0.3, 0.1), Pair(0.5, 0.15)), level="entry", min_sample=30)
    lines = text_out.splitlines()
    assert DAY in lines[0]
    assert "| vai trò (n) | 0.3/0.1 | 0.5/0.15 |" in lines
    assert "| backend (40) | 2,2 | 1,2 |" in lines
    assert "| qa (35) | 1,1 | 0,2 |" in lines


def test_gh102_mac_dinh_so_sanh_bon_cap_theta_cua_bang_bang_chung() -> None:
    assert PAIRS == (Pair(0.3, 0.1), Pair(0.25, 0.1), Pair(0.35, 0.12), Pair(0.4, 0.15))


def test_gh102_parse_pairs_va_tu_choi_cap_sai() -> None:
    assert parse_pairs("0.3/0.1,0.4/0.15") == (Pair(0.3, 0.1), Pair(0.4, 0.15))
    for bad in ("0.3", "0.1/0.3", "a/b", "1.5/0.1", ""):
        with pytest.raises(ValueError):
            parse_pairs(bad)


def test_gh102_script_chi_chay_select_tren_snapshots_stat_skill_rates_va_stat_sources(
    pg_engine: Engine, statements: list[str]
) -> None:
    _seed(pg_engine)
    with pg_engine.connect() as conn:
        before = conn.execute(text("SELECT count(*) FROM haido.stat_skill_rates")).scalar_one()
    statements.clear()
    calibrate(pg_engine, PAIRS, level="entry", min_sample=30)
    assert statements
    touched: set[str] = set()
    for statement in statements:
        sql = " ".join(statement.split()).lower()
        assert sql.startswith("select "), sql
        touched |= set(re.findall(r"(?:from|join)\s+(?:haido\.)?(\w+)", sql))
    assert touched == {"snapshots", "stat_skill_rates", "stat_sources"}
    statements.clear()
    with pg_engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM haido.stat_skill_rates")).scalar_one() == before
