# Tasks: #336 ITviec nodriver + queue/export fixes

## Phase 1: Test

- [x] T001 Viết `test_itviec_playwright_flag_runs_the_playwright_walk` trong `test_observations.py`
- [x] T002 Viết `test_itviec_queue.py`: 5 test cho `queue_batch` và `export_jsonl`
- [x] T003 Sửa parametrize xvfb-run test gồm itviec
- [x] T004 Chạy pytest — RED: 6 fail (3× `queue_batch` missing, 2× `export_jsonl` missing, 1× `--playwright` unrecognized)

## Phase 2: Code

- [x] T005 `crawlers/itviec.py`: thêm `--playwright` vào parser của `main()`
- [x] T006 `crawlers/itviec.py`: đưa `queue_batch()` và `export_jsonl()` ra cấp module (import `sqlite3`, `datetime` ở đầu file). Xóa bản lồng bên trong `_nodriver_main`.
- [x] T007 `crawlers/itviec.py`: `_nodriver_main` gọi `queue_batch` và `export_jsonl` cấp module
- [x] T008 `pipeline.py`: đổi itviec type sang `"nodriver"`
- [x] T009 Chạy pytest — GREEN: 95 passed, 9 skipped

## Phase 3: Deploy

- [x] T010 Commit, push, tạo PR
- [ ] T011 Deploy tay lên VPS (build lớp mỏng)
