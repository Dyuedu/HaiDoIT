# TDD: MoMo bỏ qua trang chi tiết 404

Theo `docs/templates/test-driven-tdd/test-driven-development.md`.

Lệnh (môi trường như job `scraper` của CI: Python 3.13, `requirements-vps.txt` + pytest):

```text
cd scraper
python -m pytest tests -q
```

`install_momo()` trong `scraper/tests/test_observations.py` thay `list_job_paths` (bước trình duyệt) bằng danh sách cố định, thay `browser_polite` bằng context rỗng, và thay `PoliteClient` bằng client giả trả `__NEXT_DATA__`, hoặc ném lỗi được chỉ định cho từng trang.

## Các hành vi

1. Ba tin, trang thứ hai ném `requests.HTTPError` 404 → raw file có tin 1 và 3, log có URL tin 2, dòng cuối có `saved 2 jobs` và `skipped 1`, file seen vẫn `listing_complete=True`.
2. Trang thứ hai ném `BlockedError("HTTP 429")` → raw file chỉ có tin 1.
3. Mọi trang ném `ConnectionError` → in đúng `MAX_CONSECUTIVE_FAILURES` dòng `detail ...` rồi `STOP -- 10 details failed in a row`.

## RED (2026-11-15)

`python -m pytest tests -q` → 2 failed, 55 passed, 9 skipped.

- Hành vi 1 đỏ: raw file chỉ có `a-1`, thiếu `c-3`. Lỗi 404 thoát ra `except` ngoài vòng và dừng.
- Hành vi 3 đỏ: `AttributeError: module 'crawlers.momo' has no attribute 'MAX_CONSECUTIVE_FAILURES'`.
- Hành vi 2 xanh sẵn: giữ lại để chặn bản sửa nuốt mất `BlockedError`.

## GREEN (2026-11-15)

- `python -m pytest tests -q` → 57 passed, 9 skipped.
- `ruff check crawlers/momo.py --select E,F,W` sạch.
