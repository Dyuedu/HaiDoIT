# Tasks: Production không bao giờ phục vụ fixture giả của thị trường

**Input**: `specs/309-prod-khong-doc-du-lieu-gia/`

## Phase 1: Test

- [x] T001 [US1] Viết `tests/deploy/test_gh309_prod_khong_doc_du_lieu_gia.py`: mỗi khóa `SOURCE_ENV` là `stat` trong compose.prod, `load_sources` của prod chỉ dựng `StatMarket`, compose.local giữ `fake`. Chạy, ghi RED.

## Phase 2: Code

- [x] T002 [US1] Thêm hai dòng `stat` vào `deploy/compose.prod.yml`. Chạy, ghi GREEN.
- [x] T003 Cập nhật bảng nguồn trong `docs/api/envelope-meta.md`.
- [x] T004 Thêm đợt tdd vào `specs/146`, `specs/166`, `specs/262`, `specs/273`.
- [x] T005 Chạy pytest đầy đủ, ruff, cổng.
