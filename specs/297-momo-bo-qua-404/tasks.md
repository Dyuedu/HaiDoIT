# Tasks: MoMo bỏ qua trang chi tiết 404

**Input**: Design documents from `specs/297-momo-bo-qua-404/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Tests**: Viết trước theo `tdd.md`. Test mới phải đỏ trước khi sửa code.

## Phase 1: Tests

- [x] T001 Thêm `install_momo()` (stub listing, client HTTP giả) vào `scraper/tests/test_observations.py`
- [x] T002 [US1][US3] Test một trang 404 bị bỏ qua, hai tin còn lại được lưu, dòng cuối có `skipped 1`
- [x] T003 [US2] Test `BlockedError` vẫn dừng
- [x] T004 Test `MAX_CONSECUTIVE_FAILURES` lỗi liền nhau thì dừng

## Phase 2: Implementation

- [x] T005 Sửa vòng tải chi tiết trong `scraper/crawlers/momo.py`

## Phase 3: Sau merge

- [ ] T006 Đêm đầu tiên có tin MoMo bị gỡ: log có `detail ...: 404`, số lưu = listed − skipped
