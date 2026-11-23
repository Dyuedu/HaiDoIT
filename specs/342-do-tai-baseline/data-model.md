# Data Model: Đo sức chịu tải baseline

Không đổi schema, không có Alembic revision mới.

Tool seed dựng schema `haido` bằng Alembic `head` trên DB đo (`haido_load_test`), rồi ghi dữ liệu giả vào các bảng sẵn có qua `snapshot_store` và các bước `lifecycle`, `aggregate`, `publish`.
