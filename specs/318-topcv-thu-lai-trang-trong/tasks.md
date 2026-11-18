# Tasks: Trang listing TopCV rỗng thì thử lại sau

**Input**: Design documents from `specs/318-topcv-thu-lai-trang-trong/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Tests**: Viết trước theo `tdd.md`. Test mới phải đỏ trước khi sửa code.

## Phase 1: Tests

- [x] T001 [US1] Test trang rỗng giữa listing được thử lại sau khi đi qua các trang sau, trong `scraper/tests/test_observations.py`
- [x] T002 [US1] Test đuôi listing rỗng, thiếu so với tổng, được thử lại
- [x] T003 [US2] Test trang rỗng mọi vòng: file seen `complete = false`, `error` có "pages still empty: 2"; số lần tải = `EMPTY_PAGE_TRIES × (1 + DEFERRED_ROUNDS)`
- [x] T004 [US3] Test không có tổng: dừng sau `EMPTY_PAGES_IN_A_ROW` trang rỗng liền
- [x] T005 Chạy, ghi RED vào `tdd.md`

## Phase 2: Implementation

- [x] T006 Thêm hằng `DEFERRED_ROUNDS`, `DEFERRED_PAUSE`, `EMPTY_PAGES_IN_A_ROW` trong `scraper/crawlers/topcv.py`
- [x] T007 Tách `fetch_listing_cards()`, `store_listing_cards()`; viết lại `crawl_listing_pages()`
- [x] T008 Chạy, ghi GREEN vào `tdd.md`
- [x] T009 Cập nhật `specs/302-topcv-tu-dong/` (User Story 5, FR-006, đợt TDD mới)

## Phase 2b: Chờ trang tải xong, trang thiếu thẻ, chẩn đoán

- [x] T012 [US5] Test `wait_for_cards`: chờ số thẻ đứng yên; bỏ cuộc sau `LISTING_WAIT`
- [x] T013 [US6] Test trang thiếu thẻ được tải lại; trang cuối thiếu thẻ không tải lại; trang thiếu mãi vẫn giữ thẻ và vào vòng thử lại
- [x] T014 [US7] Test HTML trang rỗng được lưu vào `DEBUG_DIR` và log có dòng chẩn đoán
- [x] T015 Chạy, ghi RED
- [x] T016 Thêm `wait_for_cards`, `note_odd_page`, `prune_debug_dir`; sửa `TopCVBrowserClient.fetch`, `fetch_listing_cards`, `crawl_listing_pages`
- [x] T017 Chạy, ghi GREEN

## Phase 3: Deploy và kiểm

- [ ] T010 Sau merge: chép `scraper/crawlers/topcv.py` lên `/opt/haidoit/scraper/` và build lại `scraper-browser` trên VPS (lớp mỏng trên `pre-299`, xem ghi chú deploy)
- [ ] T011 Sáng hôm sau: đọc `daily-*.log`, ghi vào `tdd.md` dòng "Vòng thử lại" (nếu có) và `topcv listed=… complete=…`
- [ ] T018 Nếu có trang rỗng hoặc thiếu thẻ: đọc HTML trong volume `scraper_data` (`/app/data/state/topcv_debug/<ngày>/`), kết luận trang chậm hay trang chặn, ghi vào `tdd.md`
