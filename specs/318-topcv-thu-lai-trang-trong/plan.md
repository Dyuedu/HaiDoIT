# Implementation Plan: Trang listing TopCV rỗng thì thử lại sau

**Branch**: `gh-318-topcv-thu-lai-trang-trong` | **Date**: 2026-11-18 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification từ `specs/318-topcv-thu-lai-trang-trong/spec.md`

## Summary

Tách vòng quét listing của `topcv.py` thành ba phần:
- `fetch_listing_cards()`: tải một trang, tải lại tới `EMPTY_PAGE_TRIES` lần khi không có thẻ tin (giữ nguyên hành vi #302).
- `store_listing_cards()`: đưa thẻ vào `job_queue` và `seen` (chép nguyên khối cũ).
- `crawl_listing_pages()`: đi tới; trang rỗng ghi vào danh sách và đi tiếp; sau lượt đi, nếu có trang rỗng kẹp giữa hoặc thiếu so với tổng thì nghỉ rồi tải lại, tối đa `DEFERRED_ROUNDS` vòng.

Đợt 2 (cùng ngày, sau khi đọc lại log):
- `wait_for_cards()`: `fetch()` của trang listing đếm thẻ bằng JS tới khi số thẻ đứng yên và DOM đã parse, thay cho `select(..., timeout=6)`; ghi `last_fetch` (thời gian, `readyState`, số thẻ).
- `fetch_listing_cards(..., expected)`: trang trước trang cuối thiếu thẻ cũng tải lại; giữ lần nhiều thẻ nhất. Trang vẫn thiếu vào `short_pages` của vòng thử lại.
- `note_odd_page()`, `prune_debug_dir()`: log và lưu HTML trang rỗng/thiếu dưới `DEBUG_DIR`.

## Technical Context

**Language/Version**: Python 3.13, image `scraper-browser`.

**Primary Dependencies**: không thêm. Dùng `math.ceil`.

**Storage**: không đổi.

**Testing**: `cd scraper && python -m pytest tests -q`.

**Target Platform**: lượt đêm `daily.sh` trên VPS. Code `scraper/` phải deploy tay (xem `deploy.yml`: không chép `scraper/`).

## Constitution Check

- Trang bị chặn vẫn dừng lượt như #302.
- Thêm tối đa 2 lần nghỉ 120–240 giây và vài chục request chỉ trong đêm có trang rỗng. Timeout TopCV là 6 giờ; đêm 18/11 cả lượt TopCV mất 3.727 giây.
- Không viết spec vào `_bmad-output/`.

## Project Structure

```text
specs/318-topcv-thu-lai-trang-trong/      spec, plan, tasks, research, data-model, tdd
scraper/crawlers/topcv.py                 DEFERRED_ROUNDS, DEFERRED_PAUSE, EMPTY_PAGES_IN_A_ROW,
                                          fetch_listing_cards, store_listing_cards, crawl_listing_pages;
                                          LISTING_WAIT, CARD_POLL, CARD_STABLE_POLLS, wait_for_cards,
                                          DEBUG_DIR, note_odd_page, prune_debug_dir, TopCVBrowserClient.fetch
scraper/tests/test_observations.py        11 test mới (#318)
specs/302-topcv-tu-dong/                  spec, plan, tasks, tdd: User Story 5 đổi hành vi trang rỗng
```

## Complexity Tracking

- `scraper/crawlers/topcv.py` thuộc #302 (có `specs/`): scenario 2 của User Story 5 ("trang rỗng `EMPTY_PAGE_TRIES` lần liền mới là hết listing") đổi. Không AC nào của #302 bị sai: AC 1 (trang 1 bị chặn) vẫn giữ. Cập nhật `specs/302-topcv-tu-dong/` cùng commit.
- `scraper/tests/test_observations.py`: thuộc #296–#298, #302; chỉ thêm test, không sửa test cũ.
