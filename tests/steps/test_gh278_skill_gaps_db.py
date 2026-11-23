"""#278 — `tools/vocab/skill_gaps.py` trên Postgres thật: kho `haido` cộng bảng `public.jobs` của scraper.

Chỉ-đọc: mọi câu SQL của script là SELECT, hai engine đều ở chế độ chỉ-đọc, và kho không đổi sau khi chạy.
"""

import json
import re
from collections.abc import Iterator
from datetime import date

import pytest
from sqlalchemy import Engine, event, text

from haido_core.db.engine import make_read_engine, make_source_engine
from haido_core.vocab.skills import load_vocabulary
from tests.steps.conftest import Env, S
from tools.vocab.skill_gaps import (
    collect,
    counted_postings,
    latest_snapshot,
    raw_skills,
)

DEVOPS_JD = "Yêu cầu\nPython, Docker, Kubernetes, Terraform, AWS, CI/CD, Linux.\n"
NON_IT_TITLE = "Nhân viên kế toán tổng hợp"


def _skills(*names: str) -> str:
    return json.dumps(list(names), ensure_ascii=False)


@pytest.fixture
def statements(pg_engine: Engine) -> Iterator[list[str]]:
    seen: list[str] = []

    def record(conn, cursor, statement, parameters, context, executemany) -> None:
        seen.append(statement)

    event.listen(pg_engine, "before_cursor_execute", record)
    yield seen
    event.remove(pg_engine, "before_cursor_execute", record)


def _feed(env: Env, scraper_db) -> None:
    """u1, u2: DevOps (thẻ + kỹ năng nguyên văn); u3: nguồn bị loại; u4: không thuộc IT; u5: DevOps không có thẻ."""
    scraper_db.job("u1", "topcv", title="DevOps Engineer", location="Hà Nội", description=DEVOPS_JD,
                   skills=_skills("Python", "Cơ sở dữ liệu", "Hà Nội"), skills_raw=_skills("cơ sở dữ liệu", "Docker"))
    scraper_db.job("u2", "itviec", title="DevOps Engineer", location="Hà Nội", description=DEVOPS_JD,
                   skills=_skills("Database", "Python", "Lạ Hoắc"))
    scraper_db.job("u3", "linkedin", title="DevOps Engineer", location="Hà Nội", description=DEVOPS_JD,
                   skills=_skills("Python"))
    scraper_db.job("u4", "topcv", title=NON_IT_TITLE, location="Hà Nội", description="Yêu cầu\nExcel.\n",
                   skills=_skills("Python"))
    scraper_db.job("u5", "topcv", title="DevOps Engineer", location="Hà Nội", description=DEVOPS_JD)
    for source, urls in (("topcv", ["u1", "u4", "u5"]), ("itviec", ["u2"]), ("linkedin", ["u3"])):
        scraper_db.day(source, S, urls)
    env.ingest()
    env.lifecycle()
    env.aggregate()
    env.publish()


def test_gh278_counted_postings_chi_lay_tin_it_cua_nguon_khong_bi_loai(env: Env, scraper_db) -> None:
    _feed(env, scraper_db)
    with env.write.connect() as conn:
        day = latest_snapshot(conn)
        assert day == date.fromisoformat(S)
        population = counted_postings(conn, day, env.rules)
    assert population == {"u1": ("topcv", "DevOps"), "u2": ("itviec", "DevOps"), "u5": ("topcv", "DevOps")}


def test_gh278_raw_skills_ghep_the_va_ky_nang_nguyen_van_bo_trung(env: Env, scraper_db) -> None:
    _feed(env, scraper_db)
    with env.write.connect() as conn:
        result = raw_skills(conn, ["u1", "u2", "u5", "u-khong-co"])
    assert result["u1"] == ("Python", "Cơ sở dữ liệu", "Hà Nội", "cơ sở dữ liệu", "Docker")
    assert result["u2"] == ("Database", "Python", "Lạ Hoắc")
    assert result["u5"] == ()
    assert "u-khong-co" not in result


def test_gh278_collect_ra_bang_ky_nang_va_ty_le_theo_vai_tro(env: Env, scraper_db, pg_url: str) -> None:
    _feed(env, scraper_db)
    warehouse, scraper = make_read_engine(pg_url), make_source_engine(pg_url)
    try:
        result = collect(warehouse, scraper, env.rules, load_vocabulary())
    finally:
        warehouse.dispose()
        scraper.dispose()
    assert result["meta"]["snapshot"] == S
    assert result["meta"]["postings"] == 3
    assert result["meta"]["postings_with_raw_skills"] == 2
    assert result["meta"]["vocab_version"] == load_vocabulary().version
    skills = {s["key"]: s for s in result["skills"]}
    assert skills["python"]["postings"] == 2
    assert skills["python"]["code"] == "python"
    assert skills["co so du lieu"]["postings"] == 1  # u1 ghi hai lần (thẻ và nguyên văn), đếm một lần
    assert skills["co so du lieu"]["code"] == "databases"
    assert skills["database"]["code"] == "databases"
    assert skills["la hoac"]["code"] is None
    assert skills["ha noi"]["code"] is None
    # u1: python, co so du lieu, ha noi, docker (4 lượt, 3 có mã); u2: database, python, la hoac (3 lượt, 2 có mã).
    assert result["roles"]["DevOps"] == {"postings": 3, "mentions": 7, "mapped": 5, "share": 5 / 7}


def test_gh278_collect_chi_doc_khong_ghi_gi(env: Env, scraper_db, pg_url: str, statements: list[str]) -> None:
    _feed(env, scraper_db)
    before = env.counts()
    statements.clear()
    warehouse, scraper = make_read_engine(pg_url), make_source_engine(pg_url)
    captured: list[str] = []
    for engine in (warehouse, scraper):
        event.listen(engine, "before_cursor_execute", lambda c, cur, stmt, p, ctx, many: captured.append(stmt))
    try:
        collect(warehouse, scraper, env.rules, load_vocabulary())
        by_script = list(captured)
        with pytest.raises(Exception, match="read-only"), warehouse.begin() as conn:
            conn.execute(text("DELETE FROM haido.job_postings"))
    finally:
        warehouse.dispose()
        scraper.dispose()
    assert by_script
    ok = re.compile(r"^\s*(SELECT|WITH)\b", re.IGNORECASE)
    assert [s for s in by_script if not ok.match(s)] == []
    assert statements == []  # engine ghi của test không bị script dùng
    assert env.counts() == before
