# Data model: Endpoint tỷ lệ kỹ năng giả

Không đổi bảng, cột hay revision Alembic.

Đổi hình API `GET /api/v1/skill-rates`:

| Chỗ | Trước | Sau |
|---|---|---|
| Query `level` | chuỗi snake_case bất kỳ | `all` + `level_options` của `config/rules.toml` |
| Query `have` | không có | mã kỹ năng, ngăn bằng dấu phẩy, tối đa 200 (AD-22) |
| `data.rows[].have` | không có | `bool` |
| `data.core_size` | không có | số dòng `group = core`; `null` khi mọi `rate` là `null_data` |
| `data.have_core` | không có | số dòng core có `have`; `null` cùng lúc với `core_size` |
| Thứ tự `data.rows` | theo fixture | có tỷ lệ trước, tỷ lệ giảm dần, rồi mã |

Fixture `haido_api/fixtures/fake_market.json`: thêm `skill_rates[role].entry` và `.all` cho mọi vai trò của `config/rules.toml`, dùng ô `vn.<role>` và `vn.<role>.entry` đã có.
