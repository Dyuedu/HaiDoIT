# Data model: Trang listing TopCV rỗng thì thử lại sau

Không đổi bảng, cột, revision Alembic của Postgres. SQLite của TopCV (`job_queue`, `job_details`) không đổi schema.

File seen của TopCV giữ định dạng cũ. Trường `error` có thêm một dạng lý do: `pages still empty: <số trang, cách nhau dấu phẩy>`, có thể đứng cạnh `met N of M listed jobs` (nối bằng `; ` như cũ).

Thêm thư mục chẩn đoán (không phải dữ liệu sản phẩm, không vào pipeline):

| Đường dẫn | Nội dung | Giữ |
|---|---|---|
| `data/state/topcv_debug/<YYYY-MM-DD>/page-<n>-try-<k>.html` | HTML lần tải trang listing rỗng hoặc thiếu thẻ trong lượt đi | 7 ngày, tối đa 40 file mỗi lượt |
| `data/state/topcv_debug/<YYYY-MM-DD>/page-<n>-round-<r>-try-<k>.html` | như trên, trong vòng thử lại | như trên |

Trên VPS nằm trong volume `deploy_scraper_data` (`/app/data/state/`). Đổi chỗ bằng biến `TOPCV_DEBUG_DIR`.
