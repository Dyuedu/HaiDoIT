# Data model: Bật deploy

Không thêm bảng và không thêm revision Alembic.

Bước deploy chạy `alembic upgrade head` trên schema `haido` đã có. Con trỏ phiên bản vẫn là bảng `haido.alembic_version`. API mới chỉ được `up` sau khi lệnh đó trả mã 0.

`compose.prod.yml` không khai Postgres. URL đích là `HAIDO_DATABASE_URL` đã nội suy trên VPS, cùng cơ sở dữ liệu mà cron kho đang ghi.
