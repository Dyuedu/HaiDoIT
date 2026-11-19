# TDD: Toàn cảnh thị trường đọc số thật

Lệnh:

```text
uv run pytest -q -p no:cacheprovider tests/api/test_ad22_market_overview_stat.py
```

## Các hành vi

1. Số tin vai trò, Hà Nội/TP.HCM của vai trò, nơi, mốc số năm đúng bằng `n` của các ô.
2. Chưa có snapshot đọc được thì 404 `unknown_cell`.

## Đợt 1 (2026-11-19)

### RED

Chưa chạy được trên máy làm việc: không có Postgres (Docker Desktop tắt), hai test skip với "HAIDO_TEST_DATABASE_URL chưa đặt". Không ghi RED khi chưa chạy thật. Test được viết trước code; CI của dự án bắt buộc chạy test Postgres (thiếu biến thì `pytest.fail`).

### GREEN

Ghi sau khi CI của PR chạy.
