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

CI của PR #331 (job "Python - ruff and pytest", Postgres thật): hai test của `tests/api/test_ad22_market_overview_stat.py` qua. Cùng lượt chạy, `tests/api/test_ad17_meta_nguon_stat.py::test_ad17_103_route_chua_co_so_that_tra_loi_chuan_khong_co_data` đỏ: test này liệt kê route đã có số thật (`REAL`) và chờ 404 `unknown_cell` ở route còn lại; `market-overview` đọc nguồn thật nên trả 200. Thêm route vào `REAL` (ý của test #103 không đổi: route có số thật trả `data` và `meta`, route chưa có trả lỗi chuẩn). Kết quả CI sau sửa ghi ở mô tả PR.
