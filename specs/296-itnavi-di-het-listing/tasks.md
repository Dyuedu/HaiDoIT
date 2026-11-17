# Tasks: ITnavi đi hết listing

**Input**: Design documents from `specs/296-itnavi-di-het-listing/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Tests**: Viết trước theo `tdd.md`. Test mới phải đỏ trước khi sửa code.

## Phase 1: Tests

- [x] T001 [US1] Test một trang trùng giữa listing không kết thúc lượt quét, trong `scraper/tests/test_observations.py`
- [x] T002 [US1] Test site lặp trang cuối: dừng sau `STALE_PAGES` trang, lượt đủ
- [x] T003 [US2] Test listing trống sớm khi tổng in trên trang lớn hơn nhiều: lượt chưa xong, `error` có hai con số
- [x] T004 [US2] Test listing trống ở cuối, gặp đủ tổng: lượt đủ
- [x] T005 [US3] Test chạm `--pages`: lượt chưa xong

## Phase 2: Implementation

- [x] T006 Thêm `STALE_PAGES`, `MIN_COVERAGE`, `listed_total()` và sửa vòng lặp trong `scraper/crawlers/itnavi.py`

## Phase 4: Trang rỗng tạm thời (2026-11-17)

- [x] T008 [US5] Test trang trống một lần được tải lại; trang trống mãi tải đúng `EMPTY_PAGE_TRIES` lần
- [x] T009 Thêm `EMPTY_PAGE_TRIES` và vòng tải lại trong `scraper/crawlers/itnavi.py`

## Phase 3: Sau merge

- [ ] T007 Ba đêm liền trên VPS: số listed lệch ≤ 10%, gone < 10% listed; ghi số vào `tdd.md`
