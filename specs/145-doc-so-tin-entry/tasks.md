# Tasks: Đọc số tin entry-level của mỗi vai trò từ cơ cấu cấp bậc toàn quốc

**Input**: `specs/145-doc-so-tin-entry/`

**Tests**: Viết trước theo `tdd.md`.

## Phase 1: Test

- [x] T001 Test số entry-level là n của ô `vn` nhóm `entry`, mix giữ nguyên, ô thành phố bị bỏ qua, trong `tests/api/test_fr37_newcomer_roles_stat.py`
- [x] T002 Test không câu SQL nào chạm `job_*`, `public.*`, không `sum(`/`count(`
- [x] T003 Test đọc snapshot đã công bố mới nhất, bỏ qua snapshot `open`

## Phase 2: Implementation

- [x] T004 Thêm `_national_cells` và hằng `ENTRY` vào `haido_api/stat_market.py`

## Phase 3: Kiểm trên số thật

- [x] T005 Chạy `StatMarket.newcomer_roles` trên DB local `haido` (bản sao prod 12/11), so với `city-shares?level=entry` của prod
