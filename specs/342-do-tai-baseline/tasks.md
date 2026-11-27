# Tasks: Đo sức chịu tải baseline của API bằng k6

**Input**: Design documents từ `specs/342-do-tai-baseline/`

## Phase 1: Tests (RED trước)

- [x] T001 [KB2, KB3] Test compose đo và script k6: `tests/deploy/test_gh342_do_tai_baseline.py`
- [x] T002 [P] [KB1] Test seed: `tests/tools/test_gh342_loadtest_seed.py`

## Phase 2: Implementation (GREEN)

- [x] T003 [KB1] `tools/loadtest_seed.py`
- [x] T004 [P] [KB2] `deploy/compose.loadtest.yml`
- [x] T005 [P] [KB3] `loadtest/k6/baseline.js`, `loadtest/k6/params.json`
- [x] T006 [P] `loadtest/README.md`

## Phase 3: Đo

- [x] T007 [KB3] Chạy kịch bản `smoke` để kiểm tra mọi endpoint trả 200
- [x] T008 [KB4] Chạy kịch bản `breakpoint`, ghi kết quả vào `ket-qua-do.md`

## Dependencies

- T001, T002 song song → RED
- T003–T006 song song → GREEN
- T007 sau T003–T005; T008 sau T007

- [x] T-230 Cập nhật 2026-11-27 theo #230: thêm nguồn `posting_check` (và các mục cộng thêm) vào các file của issue này; kiểm bằng `tdd.md` mục "Đợt sửa 2026-11-27"
