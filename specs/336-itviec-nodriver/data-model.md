# Data Model: #336 ITviec nodriver

## PostgreSQL / Alembic

Không đổi. Không có revision mới.

## SQLite (scraper local)

Thêm bảng `job_queue` và `job_details` trong `data/state/itviec_jobs.db` (tạo bởi
`init_db()` bên trong `_nodriver_main`). Có migrate tự động cho cột `retry_count`
và `synced_to_pg` nếu DB cũ thiếu.

| Bảng | Cột mới | Mô tả |
|---|---|---|
| `job_queue` | `retry_count INTEGER DEFAULT 0` | Số lần đã thử lại |
| `job_details` | `synced_to_pg INTEGER DEFAULT 0` | Đánh dấu đã đẩy lên PG (dùng sau) |

## JSONL

`data/raw/itviec.jsonl` — schema giữ nguyên. `export_jsonl` giờ ghi nối hoặc
thay dòng thiếu mô tả, không bao giờ truncate.
