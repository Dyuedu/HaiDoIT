# Tasks: TopDev thử lại khi rớt kết nối

**Input**: Design documents from `specs/298-topdev-thu-lai-ket-noi/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Tests**: Viết trước theo `tdd.md`. Test mới phải đỏ trước khi sửa code.

## Phase 1: Tests

- [x] T001 [US1][US4] Test rớt kết nối 2 lần ở trang 2: lượt đủ, hai lần chờ tăng gấp đôi, log có URL và số lần thử, trong `scraper/tests/test_observations.py`
- [x] T002 [US1] Test timeout một lần: lượt đủ
- [x] T003 [US2] Test rớt kết nối mãi: gọi đúng `CONNECT_TRIES` lần, lượt chưa xong
- [x] T004 [US3] Test `BlockedError`: gọi một lần, không chờ

## Phase 2: Implementation

- [x] T005 Thêm `get_listing_page()` và hằng số trong `scraper/crawlers/topdev.py`

## Phase 3: Sau merge

- [ ] T006 Đêm đầu tiên có rớt kết nối: log có `retrying`, TopDev vẫn `complete=True`
