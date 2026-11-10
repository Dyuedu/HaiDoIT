"""AD-4 — bước `ingest`: mở snapshot S và chép lượt chạy, quan sát, dữ kiện tin (Story 1.4)."""

from dataclasses import replace
from datetime import date

import pytest
from sqlalchemy import text

from haido_core.config import load_rules
from haido_core.db import snapshot_store
from haido_core.db.scraper_source import (
    SourceFactsRow,
    SourceObservationRow,
    SourceRunRow,
    SourceSnapshot,
)
from haido_core.steps.common import SnapshotClosedError, StepError
from haido_core.steps.ingest import ingest_snapshot, plan_ingest
from tests.steps.conftest import Env

RULES = replace(load_rules(), config_version="t", window_days=60, auto_sources=("itviec", "zalo"))
S = "2026-11-03"


class FakeReader:
    def __init__(self, data: SourceSnapshot) -> None:
        self.data = data
        self.calls = 0

    def read(self, snapshot_id: date) -> SourceSnapshot:
        self.calls += 1
        return self.data


def _data(
    runs: tuple[SourceRunRow, ...] = (SourceRunRow("itviec", True, 2, None),),
    urls: tuple[tuple[str, str], ...] = (("itviec", "u1"), ("itviec", "u2")),
    facts: tuple[SourceFactsRow, ...] = (),
) -> SourceSnapshot:
    return SourceSnapshot(runs, tuple(SourceObservationRow(u, s) for s, u in urls), facts)


# ------------------------------------------------------------------ thuần, không DB


def test_ad4_plan_nguon_ngoai_config_la_manual_va_success_theo_listing_complete() -> None:
    data = _data(
        runs=(SourceRunRow("topcv", True, 1, None), SourceRunRow("itviec", False, 1, "bị chặn")),
        urls=(("topcv", "t1"), ("itviec", "i1")),
    )
    plan = plan_ingest(date(2026, 11, 3), data, RULES.auto_sources)
    runs = {r.source: r for r in plan.runs}
    assert (runs["topcv"].mode, runs["topcv"].success) == ("manual", True)
    assert (runs["itviec"].mode, runs["itviec"].success, runs["itviec"].error) == ("auto", False, "bị chặn")


def test_ad4_plan_khong_co_luot_nao_thi_bao_loi() -> None:
    with pytest.raises(StepError, match="chưa có lượt chạy"):
        plan_ingest(date(2026, 11, 3), _data(runs=(), urls=()), RULES.auto_sources)


def test_ad4_plan_quan_sat_cua_nguon_khong_co_luot_thi_bao_loi() -> None:
    with pytest.raises(StepError, match="không có lượt chạy"):
        plan_ingest(date(2026, 11, 3), _data(urls=(("zalo", "z1"),)), RULES.auto_sources)


def test_ad4_plan_tin_khong_co_hang_jobs_van_co_quan_sat_nhung_khong_co_du_kien() -> None:
    facts = (SourceFactsRow("u1", "Dev", "A", "Hà Nội", "3 năm", "Senior"),)
    plan = plan_ingest(date(2026, 11, 3), _data(facts=facts), RULES.auto_sources)
    assert [(o.source, o.source_url) for o in plan.observations] == [("itviec", "u1"), ("itviec", "u2")]
    assert [(f.source, f.source_url) for f in plan.facts] == [("itviec", "u1")]
    assert plan.facts[0].location_text == "Hà Nội"


def test_ad4_plan_tat_dinh_khong_phu_thuoc_thu_tu_dau_vao() -> None:
    a = _data(runs=(SourceRunRow("zalo", True, 1, None), SourceRunRow("itviec", True, 2, None)),
              urls=(("zalo", "z"), ("itviec", "u2"), ("itviec", "u1")))  # fmt: skip
    b = _data(runs=(SourceRunRow("itviec", True, 2, None), SourceRunRow("zalo", True, 1, None)),
              urls=(("itviec", "u1"), ("itviec", "u2"), ("zalo", "z")))  # fmt: skip
    assert plan_ingest(date(2026, 11, 3), a, RULES.auto_sources) == plan_ingest(date(2026, 11, 3), b, RULES.auto_sources)


@pytest.mark.parametrize("bad", ["2026-13-01", "2026-11-31", "20261103", "hôm nay", "2026-1-3", ""])
def test_ad4_ngay_sai_thi_khong_doc_nguon_va_khong_ghi(bad: str) -> None:
    reader = FakeReader(_data())
    with pytest.raises(StepError, match="YYYY-MM-DD"):
        ingest_snapshot(bad, reader=reader, engine=None, rules=RULES)  # type: ignore[arg-type]
    assert reader.calls == 0


# ------------------------------------------------------------------ Postgres thật


def test_ad4_ingest_mo_snapshot_open_va_moi_quan_sat_co_luot_chay_dung_nguon(env: Env, scraper_db) -> None:
    scraper_db.day("itviec", S, ["i1", "i2"])
    scraper_db.day("zalo", S, ["z1"], complete=False)
    scraper_db.job("i1", "itviec", title="Backend Dev", company="A", location="Hà Nội",
                   experience_level="3 năm", job_level="Senior")  # fmt: skip
    result = env.ingest()
    assert (result.runs, result.observations) == (2, 3)
    assert env.query("SELECT status, closed_at FROM haido.snapshots") == [("open", None)]
    rows = env.query(
        "SELECT p.source, p.source_url, r.source, r.snapshot_id::text, r.success "
        "FROM haido.job_observations o JOIN haido.job_postings p ON p.id=o.posting_id "
        "JOIN haido.pipeline_runs r ON r.id=o.pipeline_run_id ORDER BY 2"
    )
    assert rows == [
        ("itviec", "i1", "itviec", S, True),
        ("itviec", "i2", "itviec", S, True),
        ("zalo", "z1", "zalo", S, False),
    ]
    assert env.query("SELECT title, company, location_text, experience_level, job_level FROM haido.job_posting_facts") == [
        ("Backend Dev", "A", "Hà Nội", "3 năm", "Senior")
    ]


def test_ad4_nguon_ngoai_danh_sach_tu_dong_ghi_mode_manual(env: Env, scraper_db) -> None:
    scraper_db.day("topcv", S, ["t1"])
    scraper_db.day("itviec", S, ["i1"])
    env.ingest()
    assert env.query("SELECT source, mode FROM haido.pipeline_runs ORDER BY source") == [
        ("itviec", "auto"),
        ("topcv", "manual"),
    ]


def test_ad4_chay_lai_ingest_khi_open_khong_sinh_hang_trung(env: Env, scraper_db) -> None:
    scraper_db.day("itviec", S, ["i1", "i2"])
    scraper_db.job("i1", "itviec", title="Dev")
    env.ingest()
    first = env.counts()
    assert first == {"snapshots": 1, "pipeline_runs": 1, "job_postings": 2, "job_posting_facts": 1, "job_observations": 2}
    env.ingest()
    env.ingest()
    assert env.counts() == first


def test_ad4_chay_lai_cap_nhat_luot_chay_theo_scraper_moi_nhat(env: Env, scraper_db) -> None:
    scraper_db.day("itviec", S, ["i1"], complete=False)
    env.ingest()
    assert env.query("SELECT success, seen_count, error FROM haido.pipeline_runs") == [(False, 1, "bị chặn")]
    scraper_db.day("itviec", S, ["i1", "i2"], complete=True)
    env.ingest()
    assert env.query("SELECT success, seen_count, error FROM haido.pipeline_runs") == [(True, 2, None)]
    assert env.count("job_observations") == 2


def test_ad4_snapshot_da_chot_thi_tu_choi_va_khong_ghi_gi(env: Env, scraper_db) -> None:
    scraper_db.day("itviec", S, ["i1"])
    env.ingest()
    before = env.counts()
    for status in ("published", "partial"):
        with env.write.begin() as conn:  # bước publish của #69 đặt trạng thái; ở đây giả lập
            conn.execute(text("UPDATE haido.snapshots SET status=:s, closed_at=now()"), {"s": status})
        scraper_db.day("itviec", S, ["i1", "i2", "i3"])
        scraper_db.day("zalo", S, ["z1"])
        with pytest.raises(SnapshotClosedError, match="đã chốt"):
            env.ingest()
        assert env.counts() == before
        assert env.query("SELECT success, seen_count FROM haido.pipeline_runs") == [(True, 1)]


def test_ad4_chua_co_du_lieu_ngay_s_thi_khong_mo_snapshot(env: Env, scraper_db) -> None:
    scraper_db.day("itviec", "2026-11-02", ["i1"])
    with pytest.raises(StepError, match="chưa có lượt chạy"):
        env.ingest()
    assert env.counts() == dict.fromkeys(env.counts(), 0)


def test_ad4_ngay_sai_voi_postgres_khong_ghi(env: Env, scraper_db) -> None:
    scraper_db.day("itviec", S, ["i1"])
    with pytest.raises(StepError, match="YYYY-MM-DD"):
        env.ingest("2026-13-01")
    assert env.count("snapshots") == 0


def test_ad4_du_kien_doi_o_s3_thi_them_ban_moi_va_giu_ban_cu(env: Env, scraper_db) -> None:
    scraper_db.job("x", "itviec", title="Dev", company="A")
    for day in ("2026-11-01", "2026-11-02"):
        scraper_db.day("itviec", day, ["x"])
        env.ingest(day)
    assert env.count("job_posting_facts") == 1  # S2 giống S1: không thêm bản
    scraper_db.job("x", "itviec", title="Senior Dev", company="A")
    scraper_db.day("itviec", "2026-11-03", ["x"])
    env.ingest("2026-11-03")
    assert env.query("SELECT snapshot_id::text, title FROM haido.job_posting_facts ORDER BY 1") == [
        ("2026-11-01", "Dev"),
        ("2026-11-03", "Senior Dev"),
    ]
    with env.write.connect() as conn:
        at_s2 = snapshot_store.facts_at(conn, date(2026, 11, 2))
        at_s3 = snapshot_store.facts_at(conn, date(2026, 11, 3))
    assert [f.title for f in at_s2.values()] == ["Dev"]
    assert [f.title for f in at_s3.values()] == ["Senior Dev"]


def test_ad4_chay_lai_khi_du_kien_doi_cung_ngay_giu_ban_dau_cua_s(env: Env, scraper_db) -> None:
    scraper_db.day("itviec", S, ["i1"])
    scraper_db.job("i1", "itviec", title="Dev v1")
    env.ingest()
    before = env.counts()
    scraper_db.job("i1", "itviec", title="Dev v2")
    second = env.ingest()
    assert second.facts_added == 0
    assert env.counts() == before
    assert env.query("SELECT snapshot_id::text, title FROM haido.job_posting_facts") == [(S, "Dev v1")]


def test_ad4_chay_bu_s_cu_khong_them_ban_moi_cho_tin_da_thay_o_snapshot_sau(env: Env, scraper_db) -> None:
    scraper_db.job("x", "itviec", title="v1")
    for day in ("2026-11-01", "2026-11-03"):
        scraper_db.day("itviec", day, ["x"])
        env.ingest(day)
    scraper_db.job("x", "itviec", title="v2")
    scraper_db.day("itviec", "2026-11-02", ["x"])
    result = env.ingest("2026-11-02")
    assert result.facts_added == 0
    assert env.query("SELECT snapshot_id::text FROM haido.job_posting_facts WHERE snapshot_id = '2026-11-02'") == []
    with env.write.connect() as conn:
        at_s3 = snapshot_store.facts_at(conn, date(2026, 11, 3))
    assert [f.title for f in at_s3.values()] == ["v1"]


def test_ad4_chay_bu_s_cu_tin_chi_thay_o_s_van_co_du_kien(env: Env, scraper_db) -> None:
    scraper_db.day("itviec", "2026-11-03", ["x"])
    scraper_db.job("x", "itviec", title="v1")
    env.ingest("2026-11-03")
    scraper_db.day("itviec", "2026-11-02", ["y"])
    scraper_db.job("y", "itviec", title="Y")
    assert env.ingest("2026-11-02").facts_added == 1
    assert env.query(
        "SELECT p.source_url, f.snapshot_id::text, f.title FROM haido.job_posting_facts f "
        "JOIN haido.job_postings p ON p.id=f.posting_id WHERE f.snapshot_id = '2026-11-02'"
    ) == [("y", "2026-11-02", "Y")]


def test_ad4_tin_chua_co_trong_jobs_van_co_tin_va_quan_sat_nhung_khong_co_du_kien(env: Env, scraper_db) -> None:
    scraper_db.day("itviec", S, ["moi"])
    env.ingest()
    assert env.counts()["job_postings"] == 1
    assert env.counts()["job_observations"] == 1
    assert env.counts()["job_posting_facts"] == 0


def test_ad4_loi_giua_chung_thi_khong_con_hang_nao_cua_lan_chay(
    env: Env, scraper_db, monkeypatch: pytest.MonkeyPatch
) -> None:
    scraper_db.day("itviec", S, ["i1"])
    scraper_db.job("i1", "itviec", title="Dev")

    def boom(*args, **kwargs):
        raise RuntimeError("giả lập lỗi giữa chừng")

    monkeypatch.setattr(snapshot_store, "insert_observations", boom)
    with pytest.raises(RuntimeError):
        env.ingest()
    assert env.counts() == dict.fromkeys(env.counts(), 0)


def test_ad4_doc_nguon_khong_cham_cot_van_ban_va_khong_ghi_vao_bang_scraper(env: Env, scraper_db) -> None:
    import inspect

    from haido_core.db import scraper_source

    assert "description" not in inspect.getsource(scraper_source).lower()
    jd = "văn bản JD không được chép"
    scraper_db.day("itviec", S, ["i1"])
    scraper_db.job("i1", "itviec", title="Dev", description=jd)
    jobs_sql = "SELECT * FROM public.jobs ORDER BY job_url"
    before = env.query(jobs_sql)
    env.ingest()
    facts = env.query("SELECT to_jsonb(f)::text FROM haido.job_posting_facts f")
    assert facts and all(jd not in row[0] for row in facts)
    assert env.query(jobs_sql) == before
    assert any(jd in str(v) for v in before[0])
