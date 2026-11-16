# Data model: TopCV chạy trong lượt đêm trên VPS

Không đổi bảng, cột, revision Alembic của Postgres. File seen và raw của TopCV giữ định dạng cũ.

SQLite của TopCV (`job_queue`, `job_details`) không đổi schema. Chỉ đổi chỗ đặt mặc định:

| | Trước | Sau |
|---|---|---|
| Hàng đợi khi chạy tay | `topcv_jobs.db` ở gốc repo (`TOPCV_DB` trong `topcv-manual.sh`) | `scraper/data/state/topcv_jobs.db` |
| Profile Chrome | `./chrome_topcv_profile` theo thư mục chạy | `data/state/chrome_topcv_profile` |
| Trên VPS | không có | volume `deploy_scraper_data`, `/app/data/state/` |
