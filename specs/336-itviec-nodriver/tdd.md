# TDD Log: #336 ITviec nodriver

**Lệnh test**: `uv run --no-project --python 3.13 --with-requirements requirements-vps.txt --with pytest python -m pytest tests -q`

(Chạy trong `scraper/`, dùng requirements-vps.txt giống CI, không cài nodriver.)

## Đợt 1 — 2026-11-20: thêm nodriver path, sửa queue/export

### Danh sách hành vi cần test

1. `--playwright` chạy được `main()` Playwright (test observation cũ vẫn pass)
2. `queue_batch` lấy PENDING và FAILED dưới retry cap
3. `queue_batch` cho tin FAILED đủ 3 lần thử lại sau 7 ngày
4. `queue_batch` tôn trọng batch_size, PENDING trước FAILED
5. `export_jsonl` thay dòng thiếu mô tả thay vì ghi trùng
6. `export_jsonl` ghi nối khi không có dòng cần thay
7. Pipeline bọc itviec trong xvfb-run khi không có DISPLAY (sửa parametrize)

### RED

```
6 failed, 89 passed, 9 skipped in 7.05s

FAILED tests/test_observations.py::test_itviec_playwright_flag_runs_the_playwright_walk
  → AttributeError: unrecognized arguments: --playwright (main() chưa khai báo cờ)
FAILED tests/test_itviec_queue.py::test_queue_takes_pending_and_failed_under_the_retry_cap
  → AttributeError: module 'crawlers.itviec' has no attribute 'queue_batch'
FAILED tests/test_itviec_queue.py::test_exhausted_failed_job_waits_then_gets_a_fresh_try
  → AttributeError: module 'crawlers.itviec' has no attribute 'queue_batch'
FAILED tests/test_itviec_queue.py::test_queue_respects_the_batch_size_pending_first
  → AttributeError: module 'crawlers.itviec' has no attribute 'queue_batch'
FAILED tests/test_itviec_queue.py::test_export_replaces_a_row_without_description_instead_of_duplicating
  → AttributeError: module 'crawlers.itviec' has no attribute 'export_jsonl'
FAILED tests/test_itviec_queue.py::test_export_appends_only_when_nothing_is_replaced
  → AttributeError: module 'crawlers.itviec' has no attribute 'export_jsonl'
```

### GREEN

Sửa: thêm `--playwright` vào parser `main()`, đưa `queue_batch()` và
`export_jsonl()` ra cấp module, `_nodriver_main` gọi chúng, xóa bản lồng cũ.

```
95 passed, 9 skipped in 6.10s
```
