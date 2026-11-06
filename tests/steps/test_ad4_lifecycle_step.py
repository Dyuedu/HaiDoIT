"""AD-4 — bước `lifecycle`: gọi `job_lifecycle` rồi ghi `stat_job_lifecycle` (Story 1.4)."""

from dataclasses import replace

import pytest
from sqlalchemy import text

from haido_core.steps.common import SnapshotClosedError, StepError
from tests.steps.conftest import Env

DAYS = ["2026-11-01", "2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05"]


def _life(env: Env, url: str, day: str):
    return env.query(
        "SELECT l.times_seen, l.first_seen::text, l.last_seen::text, l.repost_count, l.absent, l.in_window, "
        "l.config_version FROM haido.stat_job_lifecycle l JOIN haido.job_postings p ON p.id = l.posting_id "
        "WHERE p.source_url = :u AND l.snapshot_id = :d",
        u=url,
        d=day,
    )


def _feed(env: Env, scraper_db, plan: dict[str, tuple[bool, list[str]]]) -> None:
    """Nạp scraper và ingest từng ngày: `{ngày: (listing_complete, [url])}`."""
    for day, (complete, urls) in plan.items():
        scraper_db.day("itviec", day, urls, complete=complete)
        env.ingest(day)


def test_ad4_ba_luot_lien_thi_thay_ba_lan_dau_s1_cuoi_s3(env: Env, scraper_db) -> None:
    _feed(env, scraper_db, {d: (True, ["x"]) for d in DAYS[:3]})
    result = env.lifecycle(DAYS[2])
    assert result.rows == 1
    assert _life(env, "x", DAYS[2]) == [(3, DAYS[0], DAYS[2], 0, False, True, env.rules.config_version)]


def test_ad4_moi_tin_da_thay_co_mot_hang_vong_doi_kem_config_version(env: Env, scraper_db) -> None:
    _feed(env, scraper_db, {DAYS[0]: (True, ["a", "b"]), DAYS[1]: (True, ["b", "c"])})
    env.lifecycle(DAYS[1])
    rows = env.query("SELECT count(*), count(DISTINCT posting_id), min(config_version) FROM haido.stat_job_lifecycle")
    assert rows == [(3, 3, env.rules.config_version)]
    assert env.query("SELECT snapshot_id::text FROM haido.snapshots") != []
    assert env.query("SELECT status FROM haido.snapshots WHERE snapshot_id = :d", d=DAYS[1]) == [("open",)]


def test_ad4_dem_loi_khong_tinh_vang_khong_tang_dang_lai(env: Env, scraper_db) -> None:
    _feed(
        env,
        scraper_db,
        {DAYS[0]: (True, ["x"]), DAYS[1]: (False, []), DAYS[2]: (False, []), DAYS[3]: (False, []), DAYS[4]: (True, ["x"])},
    )
    env.lifecycle(DAYS[4])
    # ba lượt liền bị lỗi: chưa thể kết luận tin biến mất, nên đăng lại = 0
    assert _life(env, "x", DAYS[4]) == [(2, DAYS[0], DAYS[4], 0, False, True, env.rules.config_version)]


def test_ad4_mat_roi_dang_lai_s4_absent_s5_dang_lai_1(env: Env, scraper_db) -> None:
    _feed(
        env,
        scraper_db,
        {DAYS[0]: (True, ["x"]), DAYS[1]: (True, ["y"]), DAYS[2]: (True, ["y"]), DAYS[3]: (True, ["y"]),
         DAYS[4]: (True, ["x", "y"])},
    )  # fmt: skip
    env.lifecycle(DAYS[3])
    assert _life(env, "x", DAYS[3]) == [(1, DAYS[0], DAYS[0], 0, True, True, env.rules.config_version)]
    env.lifecycle(DAYS[4])
    assert _life(env, "x", DAYS[4]) == [(2, DAYS[0], DAYS[4], 1, False, True, env.rules.config_version)]


def test_ad4_lifecycle_s4_khong_dung_tin_cua_ngay_sau(env: Env, scraper_db) -> None:
    _feed(env, scraper_db, {DAYS[0]: (True, ["x"]), DAYS[1]: (True, ["x"]), DAYS[2]: (True, ["x"])})
    env.lifecycle(DAYS[1])
    assert _life(env, "x", DAYS[1])[0][0] == 2


def test_ad4_cua_so_ngay_lay_tu_config(env: Env, scraper_db) -> None:
    _feed(env, scraper_db, {DAYS[0]: (True, ["x"]), DAYS[1]: (True, ["y"]), DAYS[2]: (True, ["y"])})
    env.lifecycle(DAYS[2], rules=replace(env.rules, window_days=1, config_version="khac"))
    assert _life(env, "x", DAYS[2]) == [(1, DAYS[0], DAYS[0], 0, False, False, "khac")]


def test_ad4_snapshot_da_chot_thi_lifecycle_tu_choi_va_khong_ghi(env: Env, scraper_db) -> None:
    _feed(env, scraper_db, {DAYS[0]: (True, ["x"])})
    env.lifecycle(DAYS[0])
    for status in ("published", "partial"):
        with env.write.begin() as conn:
            conn.execute(text("UPDATE haido.snapshots SET status=:s"), {"s": status})
        with pytest.raises(SnapshotClosedError, match="đã chốt"):
            env.lifecycle(DAYS[0], rules=replace(env.rules, config_version="moi"))
        assert _life(env, "x", DAYS[0])[0][-1] == env.rules.config_version


def test_ad4_snapshot_chua_mo_thi_lifecycle_bao_loi(env: Env) -> None:
    with pytest.raises(StepError, match="chưa mở"):
        env.lifecycle(DAYS[0])
    assert env.count("snapshots") == 0


def test_ad4_ngay_sai_thi_lifecycle_khong_ghi(env: Env) -> None:
    with pytest.raises(StepError, match="YYYY-MM-DD"):
        env.lifecycle("2026-13-01")


def test_ad4_chay_lai_lifecycle_khong_nhan_doi_hang(env: Env, scraper_db) -> None:
    _feed(env, scraper_db, {DAYS[0]: (True, ["x", "y"])})
    env.lifecycle(DAYS[0])
    env.lifecycle(DAYS[0])
    assert env.count("stat_job_lifecycle") == 2


@pytest.mark.determinism
def test_ad4_determinism_chay_hai_lan_ra_cung_hang(env: Env, scraper_db) -> None:
    _feed(
        env,
        scraper_db,
        {DAYS[0]: (True, ["b", "a", "c"]), DAYS[1]: (False, []), DAYS[2]: (True, ["c", "a"]), DAYS[3]: (True, ["a"])},
    )
    sql = "SELECT * FROM haido.stat_job_lifecycle ORDER BY snapshot_id, posting_id"
    env.lifecycle(DAYS[3])
    first = env.query(sql)
    env.lifecycle(DAYS[3])
    assert env.query(sql) == first
    assert len(first) == 3


def test_ad4_loi_giua_chung_thi_giu_nguyen_hang_cu(env: Env, scraper_db, monkeypatch: pytest.MonkeyPatch) -> None:
    from haido_core.db import snapshot_store

    _feed(env, scraper_db, {DAYS[0]: (True, ["x"])})
    env.lifecycle(DAYS[0])
    real = snapshot_store.replace_lifecycle

    def after_delete(conn, day, version, rows):
        real(conn, day, version, [])
        raise RuntimeError("giả lập lỗi sau khi xóa hàng cũ")

    monkeypatch.setattr(snapshot_store, "replace_lifecycle", after_delete)
    with pytest.raises(RuntimeError):
        env.lifecycle(DAYS[0])
    assert env.count("stat_job_lifecycle") == 1
