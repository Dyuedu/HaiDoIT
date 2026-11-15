# Data model: bộ lọc bản đồ chọn bằng dropdown

Không đổi. Issue chỉ đổi điều khiển của web.

- Bảng, cột: không đổi.
- Revision Alembic: không đổi (head giữ nguyên).
- `config/rules.toml`, `config_version`: không đổi.
- API `GET /api/v1/city-shares` và `docs/api/openapi.json`: không đổi; web vẫn gửi `role`, `level`, `years`.
- `web/lib/labels.ts`: danh sách và thứ tự không đổi (chỉ sửa chữ "Chip", "Nút" trong chú thích thành "Lựa chọn").
