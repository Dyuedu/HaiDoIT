# TDD: TopCV chạy trong lượt đêm trên VPS

Theo `docs/templates/test-driven-tdd/test-driven-development.md`.

Lệnh (môi trường như job `scraper` của CI: Python 3.13, `requirements-vps.txt` + pytest; repo gốc dùng `uv`):

```text
cd scraper
python -m pytest tests -q
cd ..
uv run pytest tests/deploy -q
```

`run_topcv_main(module, monkeypatch, pages, argv)` trong `scraper/tests/test_observations.py` thay `TopCVBrowserClient` bằng client giả (trang chi tiết trả `NOT_FOUND`), đặt `sys.argv`, chạy `main()` và trả danh sách trang chi tiết đã mở. `capture_run` thay `pipeline.subprocess.run` để ghi lại lệnh và timeout.

## Các hành vi

1. `job_queue` có URL cũ, trang 1 bị chặn → file seen `job_urls = []`, `listing_complete = false`.
2. `--skip-details` → không mở trang chi tiết, listing `complete`.
3. `--limit 2` với 3 tin chờ → mở 2 trang chi tiết.
4. Không đặt biến môi trường → `DB_PATH`, `PROFILE_DIR` dưới `data/state`.
5. `pipeline.py crawl --sources topcv --skip-details --limit 5` → topcv nhận `["--skip-details", "--limit", "5"]`.
6. Linux không có `DISPLAY` → lệnh topcv bắt đầu bằng `xvfb-run`, timeout `6 * 3600`.
7. Có `DISPLAY`, hoặc momo/itviec → không bọc `xvfb-run` (3 ca).
8. `daily.sh` có `--sources momo,itviec,topcv`.
9. `Dockerfile.browser` có Chrome, xvfb, `CHROME_PATH`, `nodriver==` ghim, `playwright==1.64.1`.
10. `scraper-browser` có `shm_size: 1g`.
11. `topcv-manual.sh` không đặt `TOPCV_DB`.

## RED (2026-11-16)

`python -m pytest tests -q -p no:cacheprovider` → 6 failed, 64 passed, 9 skipped.

- Hành vi 1, 2, 3 đỏ: `sqlite3.OperationalError: unable to open database file` ở `export_jsonl`. `main()` gọi `export_jsonl()` với `db_path` mặc định bị chốt lúc định nghĩa hàm, không theo `DB_PATH`. Log của hành vi 1 có `seen: 1 jobs, listing_complete=False`: fallback đã ghi URL cũ vào file seen, rồi `process_job_queue` vỡ ở `q_title[:48]` vì tiêu đề `NULL`.
- Hành vi 4 đỏ: `PROFILE_DIR` là `<cwd>/chrome_topcv_profile`.
- Hành vi 5 đỏ: `assert [] == ['--skip-details', '--limit', '5']`, nguồn `nodriver` không nhận cờ nào.
- Hành vi 6 đỏ: lệnh bắt đầu bằng `python.exe`, không có `xvfb-run`.
- Hành vi 7 xanh sẵn: giữ để chặn bản sửa bọc nhầm momo, itviec.

`uv run pytest tests/deploy/test_gh302_topcv_tu_dong.py -q` → 4 failed (hành vi 8–11): chuỗi cần có chưa có trong file.

## GREEN (2026-11-16)

- `python -m pytest tests -q -p no:cacheprovider` → 70 passed, 9 skipped.
- `uv run pytest tests/deploy -q` → 62 passed (gồm test của #262, #273).
- Ruff không chạy trên `scraper/` trong CI; `ruff --select E,F,W` trên `topcv.py`, `pipeline.py` chỉ còn lỗi E501 (88 cột) giống các dòng cũ của hai file.

`-p no:cacheprovider`: venv thử của máy dev lỗi `No module named '_pytest.stepwise'`, không liên quan code.

## Đợt 2: lượt thử trên VPS dừng sớm (2026-11-16)

Lý do: `docker compose run --rm scraper-browser pipeline.py crawl --sources topcv --limit 5` trên VPS báo `[topcv] OK in 312s`, `seen: 705 jobs, listing_complete=True`. Các lượt chạy tay 05–10/11 thấy 2.520–2.886 tin. Log: trang 1–15 mỗi trang 50 tin, trang 16 "Không tìm thấy danh sách job". Probe ngay sau đó tải trang 16, 17: mỗi trang 50 tin, tiêu đề "Tuyển dụng 2.293 việc làm", không có trang kiểm tra Cloudflare. File seen sai đổi tên thành `seen/2026-11-16/topcv.json.test-bad`.

Hành vi mới:

12. Tiêu đề "Tuyển dụng 2.293 việc làm" → `listed_total` = 2293; không có tiêu đề → `None`.
13. Trang 2 rỗng một lần rồi có tin; trang 3 rỗng mãi → thấy 2 tin, `complete`, trang 2 gọi 2 lần, trang 3 gọi `EMPTY_PAGE_TRIES` lần.
14. Tổng 100, listing hết sau 2 tin → `listing_complete = false`, `error` có "met 2 of 100".
15. Tổng 2, thấy 2 → `listing_complete = true`.

### RED (2026-11-16)

`python -m pytest tests -q -p no:cacheprovider` → 3 failed, 71 passed, 9 skipped.

- Hành vi 12 đỏ: `AttributeError: module 'crawlers.topcv' has no attribute 'listed_total'`.
- Hành vi 13 đỏ: `assert (1 == 2)`: trang rỗng đầu tiên kết thúc listing.
- Hành vi 14 đỏ: `assert True is False` (`listing_complete`).
- Hành vi 15 xanh sẵn: giữ để chặn bản sửa đánh dấu chưa đủ khi đã đủ.

### GREEN (2026-11-16)

- `python -m pytest tests -q -p no:cacheprovider` → 74 passed, 9 skipped.

### Kiểm trên VPS (2026-11-16)

Build lại `scraper-browser` với `topcv.py` mới, chạy `pipeline.py crawl --sources topcv --skip-details`: 47 trang, `seen: 2294 jobs, listing_complete=True`, `[topcv] OK in 645s`. Tiêu đề ghi 2.293 việc làm. Trang 47 lặp lại trang 46 nên lượt dừng ở đó; lượt này không trang nào phải tải lại. 108 tin mới vào hàng đợi ở trạng thái `PENDING`.
