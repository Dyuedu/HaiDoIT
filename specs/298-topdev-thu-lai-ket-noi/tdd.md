# TDD: TopDev thử lại khi rớt kết nối

Theo `docs/templates/test-driven-tdd/test-driven-development.md`.

Lệnh (môi trường như job `scraper` của CI: Python 3.13, `requirements-vps.txt` + pytest):

```text
cd scraper
python -m pytest tests -q
```

`drops_connection_on(page, times, exc)` trong `scraper/tests/test_observations.py` kế thừa `fake_topdev`, ném lỗi ở trang listing được chỉ định trong `times` lần đầu và đếm số lần gọi. Fixture `sleeps` thay `topdev.time.sleep` để ghi lại các lần chờ.

## Các hành vi

1. Trang 2 rớt kết nối 2 lần → lượt đủ, có `Backend Developer-3`, chờ `[30, 60]`, log có URL trang 2, `attempt 1/`, `attempt 2/`.
2. Trang 2 `Timeout` một lần → lượt đủ.
3. Trang 2 rớt kết nối mãi → gọi đúng `CONNECT_TRIES` lần, lượt chưa xong, `error` có "Connection reset".
4. Trang 2 `BlockedError` → gọi một lần, không chờ.

## RED (2026-11-15)

`python -m pytest tests -q` → 3 failed, 58 passed, 9 skipped.

- Hành vi 1 đỏ: file seen chỉ có tin của danh mục IT; lỗi kết nối ở trang 2 làm dừng listing chung.
- Hành vi 2 đỏ: `assert False is True` (`listing_complete`).
- Hành vi 3 đỏ: `AttributeError: module 'crawlers.topdev' has no attribute 'CONNECT_TRIES'`.
- Hành vi 4 xanh sẵn: giữ lại để chặn bản sửa thử lại khi bị từ chối.

## GREEN (2026-11-15)

- `python -m pytest tests -q` → 61 passed, 9 skipped.
- `ruff check crawlers/topdev.py --select E,F,W` sạch.
