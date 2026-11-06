"""AD-4 — vòng đời tin tính tới một snapshot (Story 1.4)."""

from datetime import UTC, datetime

import pytest

from haido_core.domain.lifecycle import (
    Observation,
    SourceRun,
    job_lifecycle,
    snapshot_id_at,
)


def _runs(source: str, days: list[tuple[str, bool]]) -> list[SourceRun]:
    return [SourceRun(source, day, ok) for day, ok in days]


def _seen(source: str, days: list[str], job: str = "a") -> list[Observation]:
    return [Observation(job, source, day) for day in days]


def test_ad4_snapshot_theo_gio_ho_chi_minh() -> None:
    assert snapshot_id_at(datetime(2026, 11, 5, 16, 30, tzinfo=UTC)) == "2026-11-05"
    assert snapshot_id_at(datetime(2026, 11, 5, 17, 30, tzinfo=UTC)) == "2026-11-06"
    with pytest.raises(ValueError, match="múi giờ"):
        snapshot_id_at(datetime(2026, 11, 5, 17, 30))


def test_ad4_ba_luot_thanh_cong_lien_tiep_thi_thay_ba_lan() -> None:
    runs = _runs("itviec", [("2026-11-01", True), ("2026-11-02", False), ("2026-11-03", True), ("2026-11-04", True)])
    seen = _seen("itviec", ["2026-11-01", "2026-11-03", "2026-11-04"])
    life = job_lifecycle(runs, seen, "2026-11-04", window_days=60)
    assert len(life) == 1
    assert life[0].times_seen == 3
    assert life[0].repost_count == 0
    assert life[0].absent is False
    assert life[0].first_seen == "2026-11-01"
    assert life[0].last_seen == "2026-11-04"


def test_ad4_vang_ba_luot_moi_bien_mat_roi_dang_lai_tang_mot() -> None:
    days = ["2026-11-01", "2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05", "2026-11-06", "2026-11-07"]
    runs = _runs("itviec", [(day, True) for day in days])
    seen = _seen("itviec", ["2026-11-01", "2026-11-02", "2026-11-03", "2026-11-07"])
    life = job_lifecycle(runs, seen, "2026-11-07", window_days=60)
    assert life[0].times_seen == 4
    assert life[0].repost_count == 1
    assert life[0].absent is False
    midway = job_lifecycle(runs, seen, "2026-11-06", window_days=60)
    assert midway[0].absent is True
    assert midway[0].repost_count == 0
    assert midway[0].times_seen == 3


def test_ad4_dem_loi_khong_tang_dang_lai_va_khong_tinh_vang() -> None:
    runs = _runs(
        "itviec",
        [
            ("2026-11-01", True),
            ("2026-11-02", True),
            ("2026-11-03", False),
            ("2026-11-04", True),
        ],
    )
    seen = _seen("itviec", ["2026-11-01"])
    life = job_lifecycle(runs, seen, "2026-11-04", window_days=60)
    assert life[0].absent is False
    assert life[0].repost_count == 0
    assert life[0].times_seen == 1


def test_ad4_cua_so_60_ngay_cua_dung_snapshot() -> None:
    runs = _runs("itviec", [("2026-09-01", True), ("2026-11-05", True)])
    seen = _seen("itviec", ["2026-09-01"])
    old = job_lifecycle(runs, seen, "2026-09-01", window_days=60)
    assert old[0].in_window is True
    assert old[0].absent is False
    later = job_lifecycle(runs, seen, "2026-11-05", window_days=60)
    assert later[0].in_window is False
    assert later[0].times_seen == 1


def test_ad4_khong_sua_dau_vao() -> None:
    runs = tuple(_runs("itviec", [("2026-11-01", True), ("2026-11-02", True), ("2026-11-03", True)]))
    seen = tuple(_seen("itviec", ["2026-11-01", "2026-11-02", "2026-11-03"]))
    first = job_lifecycle(runs, seen, "2026-11-03", window_days=60)
    second = job_lifecycle(runs, seen, "2026-11-03", window_days=60)
    assert first == second
    assert runs[0].success is True
    assert seen[0].job_id == "a"
