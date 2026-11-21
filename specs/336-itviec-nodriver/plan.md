# Implementation Plan: #336 ITviec nodriver + queue/export fixes

**Branch**: `gh-336-itviec-nodriver` | **Date**: 2026-11-20 | **Spec**: `specs/336-itviec-nodriver/spec.md`

## Summary

Thêm đường thực thi nodriver cho crawler ITviec (kiến trúc giống TopCV), giữ
nguyên `main()` Playwright cho test observation, và sửa ba lỗi dữ liệu: tin đã
có mô tả bị cào lại, mô tả rỗng được đánh COMPLETED, tin FAILED nằm mãi.

## Technical Context

**Language**: Python 3.13 | **Test**: pytest | **Platform**: Linux (VPS), Windows (dev)

## Files Changed

| File | Thay đổi |
|---|---|
| `scraper/crawlers/itviec.py` | Thêm `_nodriver_main()` (lazy import), `queue_batch()`, `export_jsonl()` ở cấp module. `main()` giữ nguyên + thêm `--playwright` arg. `__main__` mặc định gọi nodriver. |
| `scraper/pipeline.py` | `itviec.type` đổi từ `"playwright"` sang `"nodriver"`. |
| `scraper/tests/test_observations.py` | Thêm `test_itviec_playwright_flag_runs_the_playwright_walk`. Sửa xvfb-run test parametrize gồm itviec. |
| `scraper/tests/test_itviec_queue.py` | **Mới.** 5 test cho `queue_batch` và `export_jsonl` (SQLite tạm, không cần nodriver). |
