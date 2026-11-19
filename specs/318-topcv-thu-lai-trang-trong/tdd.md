# TDD: Trang listing TopCV rỗng thì thử lại sau

Theo `docs/templates/test-driven-tdd/test-driven-development.md`.

Lệnh (môi trường như job `scraper` của CI: Python 3.13, `requirements-vps.txt` + pytest, venv tạm trên máy dev):

```text
cd scraper
python -m pytest tests -q -p no:cacheprovider
```

`walk_counted(module, monkeypatch, pages)` trong `scraper/tests/test_observations.py` chạy `crawl_listing_pages` với client giả đếm số lần tải mỗi trang và ghi thứ tự tải; `DEFERRED_PAUSE` đặt `(0, 0)`. `empty_then(ids, total)` là trang rỗng 3 lần đầu rồi có tin.

## Các hành vi

1. Tổng 4, trang 2 rỗng 3 lần rồi có tin → thấy 4 tin, `complete`; trang 3 được tải trước lần tải thứ tư của trang 2.
2. Tổng 4, trang 3–4 rỗng 3 lần rồi có tin → thấy 4 tin, `complete`.
3. Tổng 3, trang 2 rỗng mãi, qua `main()` → `listing_complete = false`, `error` có "pages still empty: 2".
4. Như 3 → trang 2 được tải `EMPTY_PAGE_TRIES × (1 + DEFERRED_ROUNDS)` lần.
5. Không có tổng, trang 2 rỗng 3 lần rồi có tin → thấy 3 tin, `complete`, trang cao nhất được tải là `3 + EMPTY_PAGES_IN_A_ROW`.
6. Test cũ của #302 (chặn, trang 1 rỗng, thiếu so với tổng, trang lặp, tải lại trang rỗng) giữ xanh.

## RED (2026-11-18)

`python -m pytest tests -q -p no:cacheprovider` → 5 failed, 77 passed, 9 skipped.

- Hành vi 1 đỏ: `assert (1 == 4)`: trang 2 rỗng kết thúc listing.
- Hành vi 2 đỏ: `assert (2 == 4)`: trang 3 rỗng kết thúc listing.
- Hành vi 3 đỏ: `assert 'pages still empty: 2' in 'met 1 of 3 listed jobs'`: lượt dừng ở trang 2, chỉ kiểm tổng bắt được.
- Hành vi 4 đỏ: `AttributeError: module 'crawlers.topcv' has no attribute 'DEFERRED_ROUNDS'`.
- Hành vi 5 đỏ: `assert (1 == 3)`.

## GREEN (2026-11-18)

Lần chạy đầu sau khi sửa code: 1 failed, 81 passed. Lỗi nằm ở test hành vi 1: `log.index(2, 3)` tìm từ vị trí 3 của log, trúng lần tải thứ ba của trang 2 chứ không phải lần thứ tư. Sửa test thành vị trí lần tải thứ `EMPTY_PAGE_TRIES + 1` của trang 2.

- `python -m pytest tests -q -p no:cacheprovider` → 82 passed, 9 skipped.
- Đưa `topcv.py` về bản cũ (`git stash`) và chạy lại → 5 failed như RED, xác nhận test bắt đúng thay đổi.
- `ruff check --select E,F,W --line-length 120 scraper/crawlers/topcv.py`: 5 lỗi, đều ở phần chi tiết JD có sẵn từ trước (E501 dòng 418, W291, W292); không có lỗi ở code mới.

## Đợt 2: chờ trang tải xong, trang thiếu thẻ, chẩn đoán (2026-11-18)

Lý do: đọc lại `daily-2026-11-18.log` thấy trang 24 chỉ có 22/50 thẻ và listing không gặp Cloudflare. Nhiều khả năng `fetch()` đọc HTML quá sớm (xem `research.md`). Đợt 1 không bắt được trang thiếu thẻ.

`FakeTopCVPage` trả chuỗi `"số thẻ|readyState"` theo kịch bản, có `sleep`/`clock` giả để test thời gian chờ không tốn giây thật.

Hành vi mới:

7. Số thẻ 0, 10, 30, 50, 50, 50 → `wait_for_cards` trả `(50, "complete")`.
8. Không bao giờ có thẻ → trả 0 sau `LISTING_WAIT` (tối đa thêm một `CARD_POLL`).
9. Tổng 6, trang 2 lần đầu 1/2 thẻ rồi 2/2 → thấy 6 tin, `complete`, trang 2 tải 2 lần.
10. Trang cuối 1/2 thẻ → tải 1 lần.
11. Trang 2 thiếu thẻ mãi → thẻ vẫn vào `seen` (5 tin), trang 2 tải `EMPTY_PAGE_TRIES × (1 + DEFERRED_ROUNDS)` lần.
12. Trang 2 rỗng lần đầu → `DEBUG_DIR/<ngày>/page-2-try-1.html` đúng HTML đó, log có "Trang 2 lần 1: 0 thẻ".

### RED (2026-11-18)

`python -m pytest tests -q -p no:cacheprovider` → 5 failed, 83 passed, 9 skipped.

- Hành vi 7, 8 đỏ: `AttributeError: module 'crawlers.topcv' has no attribute 'wait_for_cards'`.
- Hành vi 9 đỏ: `assert (5 == 6)`: trang thiếu thẻ được nhận luôn.
- Hành vi 10 xanh sẵn: giữ để chặn bản sửa tải lại nhầm trang cuối.
- Hành vi 11 đỏ: `assert 1 == (3 * (1 + 2))`.
- Hành vi 12 đỏ: `AttributeError: module 'crawlers.topcv' has no attribute 'DEBUG_DIR'`.

### GREEN (2026-11-18)

- `python -m pytest tests -q -p no:cacheprovider` → 88 passed, 9 skipped.
- `ruff check --select E,F,W --line-length 120 scraper/crawlers/topcv.py`: chỉ còn 5 lỗi cũ ở phần chi tiết JD (E501, W291, W292).
- `TopCVBrowserClient.fetch` (gọi `wait_for_cards` với trình duyệt thật) không có test tự động; kiểm bằng lượt chạy trên VPS.

## Kiểm trên VPS

Chưa deploy. Ghi vào đây sau đêm đầu chạy bản mới.
