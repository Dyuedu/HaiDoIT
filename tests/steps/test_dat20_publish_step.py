"""#93 — bước `publish`: đóng snapshot S thành `published` hoặc `partial`."""

from dataclasses import replace

import pytest

from haido_core.steps.common import SnapshotClosedError, StepError
from tests.steps.conftest import Env, S


def _feed(env: Env, scraper_db, *, failed: tuple[str, ...] = (), skip: tuple[str, ...] = (), manual=()) -> None:
    """Một lượt chạy cho mỗi nguồn tự động (trừ `skip`); nguồn trong `failed` lỗi; `manual` là nguồn chạy tay."""
    for source in (*env.rules.auto_sources, *manual):
        if source not in skip:
            scraper_db.day(source, S, [f"{source}-1"], complete=source not in failed)
    env.ingest()
    env.lifecycle()
    env.aggregate()


def _snapshot(env: Env) -> tuple[str, list[str], bool]:
    [(status, failed, closed)] = env.query(
        "SELECT status, sources_failed, closed_at IS NOT NULL FROM haido.snapshots WHERE snapshot_id = :d", d=S
    )
    return status, failed, closed


def test_dat20_moi_nguon_tu_dong_chay_ok_thi_published_khong_nguon_loi(env: Env, scraper_db) -> None:
    _feed(env, scraper_db)
    result = env.publish()
    assert (result.status, result.sources_failed) == ("published", ())
    assert _snapshot(env) == ("published", [], True)


def test_dat20_co_nguon_tu_dong_loi_thi_partial_kem_danh_sach_nguon_loi_a_z(env: Env, scraper_db) -> None:
    _feed(env, scraper_db, failed=("zalo", "momo"))
    result = env.publish()
    assert (result.status, result.sources_failed) == ("partial", ("momo", "zalo"))
    assert _snapshot(env) == ("partial", ["momo", "zalo"], True)


def test_dat20_nguon_tu_dong_khong_co_luot_chay_cung_la_khong_chay_thanh_cong(env: Env, scraper_db) -> None:
    _feed(env, scraper_db, skip=("itviec",))
    assert env.publish().sources_failed == ("itviec",)
    assert _snapshot(env)[0] == "partial"


def test_dat20_nguon_chay_tay_loi_khong_lam_snapshot_thanh_partial(env: Env, scraper_db) -> None:
    _feed(env, scraper_db, failed=("topcv",), manual=("topcv",))
    assert "topcv" not in env.rules.auto_sources
    result = env.publish()
    assert (result.status, result.sources_failed) == ("published", ())


def test_dat20_danh_sach_nguon_tu_dong_lay_tu_config(env: Env, scraper_db) -> None:
    _feed(env, scraper_db, failed=("zalo",))
    only_itviec = replace(env.rules, auto_sources=("itviec",))
    assert env.publish(rules=only_itviec).status == "published"


@pytest.mark.parametrize("status", ["published", "partial"])
def test_dat20_snapshot_da_chot_thi_tu_choi_va_giu_nguyen(env: Env, scraper_db, status: str) -> None:
    _feed(env, scraper_db, failed=("zalo",) if status == "partial" else ())
    env.publish()
    before = _snapshot(env)
    with pytest.raises(SnapshotClosedError, match="đã chốt"):
        env.publish()
    assert _snapshot(env) == before


def test_dat20_sau_khi_publish_aggregate_lifecycle_va_ingest_deu_bi_tu_choi(env: Env, scraper_db) -> None:
    _feed(env, scraper_db)
    env.publish()
    cells = env.query("SELECT * FROM haido.stat_cells ORDER BY role, scope")
    for step in (env.aggregate, env.lifecycle, env.ingest):
        with pytest.raises(SnapshotClosedError):
            step()
    assert env.query("SELECT * FROM haido.stat_cells ORDER BY role, scope") == cells


def test_dat20_snapshot_chua_mo_thi_bao_loi_va_ngay_sai_thi_khong_ghi(env: Env) -> None:
    with pytest.raises(StepError, match="chưa mở"):
        env.publish()
    with pytest.raises(StepError, match="YYYY-MM-DD"):
        env.publish("2026-13-01")
    assert env.count("snapshots") == 0


def test_dat20_chua_aggregate_thi_publish_tu_choi_va_snapshot_van_open(env: Env, scraper_db) -> None:
    for source in env.rules.auto_sources:
        scraper_db.day(source, S, [f"{source}-1"])
    env.ingest()
    env.lifecycle()
    with pytest.raises(StepError, match="aggregate"):
        env.publish()
    assert _snapshot(env) == ("open", [], False)
