"""#102 (DAT.30) — bước `aggregate` ghi phiên bản θ đã dùng vào hàng `snapshots` (cột `theta_version`, migration 0010)."""

from dataclasses import replace

import pytest

from haido_core.config import ThetaVersion
from haido_core.steps.common import StepError
from tests.steps.conftest import Env, S


def _with_test_version(env: Env):
    return replace(
        env.rules,
        theta_version="theta-test",
        theta_versions=(*env.rules.theta_versions, ThetaVersion("theta-test", 0.5, 0.15, "2026-11-19", "thử")),
    )


def _stored(env: Env) -> str | None:
    [(version,)] = env.query("SELECT theta_version FROM haido.snapshots WHERE snapshot_id = :d", d=S)
    return version


def _run(env: Env, scraper_db) -> None:
    scraper_db.run("itviec", S)
    env.ingest()
    env.lifecycle()


def test_gh102_ac1_aggregate_ghi_phien_ban_theta_hien_hanh_vao_snapshot(env: Env, scraper_db) -> None:
    _run(env, scraper_db)
    assert _stored(env) is None  # ingest chưa gắn phiên bản θ: chỉ aggregate dùng θ
    env.aggregate()
    assert _stored(env) == env.rules.theta_version == "theta-1"


def test_gh102_ac1_phien_ban_ghi_la_phien_ban_cua_rules_khong_phai_hang_so(env: Env, scraper_db) -> None:
    _run(env, scraper_db)
    env.aggregate(rules=_with_test_version(env))
    assert _stored(env) == "theta-test"


def test_gh102_ac1_chay_lai_aggregate_o_snapshot_open_ghi_de_phien_ban(env: Env, scraper_db) -> None:
    _run(env, scraper_db)
    env.aggregate()
    env.aggregate(rules=_with_test_version(env))
    assert _stored(env) == "theta-test"


def test_gh102_ac1_publish_giu_nguyen_phien_ban_theta_cua_snapshot(env: Env, scraper_db) -> None:
    _run(env, scraper_db)
    env.aggregate()
    env.publish()
    assert _stored(env) == "theta-1"


def test_gh102_ac1_phien_ban_hien_hanh_khong_co_trong_so_dang_ky_thi_aggregate_tu_choi_va_khong_ghi(env: Env, scraper_db) -> None:
    _run(env, scraper_db)
    with pytest.raises(StepError, match="theta-ma"):
        env.aggregate(rules=replace(env.rules, theta_version="theta-ma"))
    assert _stored(env) is None
    assert env.count("stat_cells") == 0
