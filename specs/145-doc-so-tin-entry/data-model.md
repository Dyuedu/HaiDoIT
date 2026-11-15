# Data model: Đọc số tin entry-level

Không đổi bảng, không đổi cột, không thêm revision Alembic (head vẫn `0008_haido_fact_city`).

Hàng được đọc trong `haido.stat_cells`:

| Cột | Giá trị |
|---|---|
| `snapshot_id` | snapshot do `_latest_readable(conn, "entry")` chọn |
| `scope` | `vn` |
| `branch` | `all` |
| `seniority` | `entry` (số entry-level) hoặc `all` (n của vai trò) |
| `years` | `any` |
| `role` | mọi mã khác `all` |

Cột dùng: `n`, `seniority_mix`.
