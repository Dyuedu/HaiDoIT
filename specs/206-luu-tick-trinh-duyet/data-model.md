# Data model: Lưu tick trong trình duyệt

Không đổi bảng, cột, revision Alembic hay hình API.

Trình duyệt: dùng khóa `haido:profile` đã khai ở #205, không thêm khóa.

```json
{ "v": 1, "role": "backend", "level": "entry", "skills": ["java", "sql"] }
```

| Trường | Ghi khi |
|---|---|
| `role` | chọn vai trò (ô Vai trò, chức danh khớp, danh sách vai trò) |
| `level` | đổi ô Cấp bậc, hoặc mở trang có `level` hợp lệ |
| `skills` | tick, bỏ tick (ở danh sách kỹ năng hoặc ô tìm kỹ năng) |
