# Tasks: API đọc tỷ lệ kỹ năng thật

**Input**: `specs/103-api-doc-ty-le-that/`

**Tests**: Viết trước theo `tdd.md`.

## Phase 1: Test

- [x] T001 Test mọi route có số, nguồn `stat`, trả `{data, meta}`; route chưa có số thật trả `{error}`, trong `tests/api/test_ad17_meta_nguon_stat.py`
- [x] T002 Test AD-7: SQL của `skill_rates` chỉ đọc `stat_*`, không `job_*`, không `group by`/`avg(`/`count(`, trong `tests/api/test_fr19_skill_rates_stat.py`

## Phase 2: Implementation

- [x] T003 Không có mã riêng: `StatMarket.skill_rates` (#151) làm hai test xanh; chạy cổng AD-7
