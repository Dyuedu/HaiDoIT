# Data model: TopCV chạy trong lượt đêm trên VPS

Không đổi bảng, cột, revision Alembic của Postgres. File seen và raw của TopCV giữ định dạng cũ.

SQLite của TopCV (`job_queue`, `job_details`) không đổi schema. Chỉ đổi chỗ đặt mặc định:

| | Trước | Sau |
|---|---|---|
| Hàng đợi khi chạy tay | `topcv_jobs.db` ở gốc repo (`TOPCV_DB` trong `topcv-manual.sh`) | `scraper/data/state/topcv_jobs.db` |
| Profile Chrome | `./chrome_topcv_profile` theo thư mục chạy | `data/state/chrome_topcv_profile` |
| Trên VPS | không có | volume `deploy_scraper_data`, `/app/data/state/` |

## 2026-11-17

Không đổi bảng, cột, revision Alembic. `config/rules.toml`: `[sources].auto` thêm `topcv`, `config_version` từ `2026-11-13.3` lên `2026-11-17.1`; `stat_job_lifecycle` và `stat_cells` của snapshot mới ghi phiên bản này. `haido.pipeline_runs.mode` của TopCV từ `manual` thành `auto`.
