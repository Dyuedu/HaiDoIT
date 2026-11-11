# Tasks: Build image kho trong workflow deploy

**Input**: Design documents from `specs/273-image-kho-trong-deploy/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Tests**: Viết trước theo `tdd.md`. Test mới phải đỏ trước khi sửa code.

## Phase 1: Tests

- [x] T001 [US1] Test matrix có `warehouse` và `paths` có `config/**` trong `tests/deploy/test_gh273_image_kho.py`
- [x] T002 [US3] Test workflow `scp -p` hai file lịch đêm, và `daily.sh` có mode `100755`
- [x] T003 [US2] Test `compose.scraper.yml` dùng image GHCR, `pull_policy: never`, scraper vẫn build
- [x] T004 [US2] Test `daily.sh` đọc `.warehouse-tag` trước khi chạy kho
- [x] T005 [US2] Test chạy `vps-deploy.sh` với lệnh giả: kéo image kho trước logout, ghi tag khi khỏe, giữ tag cũ khi hỏng

## Phase 2: Implementation

- [x] T006 Sửa `.github/workflows/deploy.yml`: matrix, `config/**`, scope cache, `scp -p`
- [x] T007 Sửa `deploy/vps-deploy.sh`: `docker pull` image kho, ghi `.warehouse-tag`
- [x] T008 Sửa `deploy/compose.scraper.yml` và `deploy/daily.sh`; `git update-index --chmod=+x deploy/daily.sh`
- [x] T009 Đổi chuỗi image trong `tests/deploy/test_daily_warehouse.py` (#90)

## Phase 3: Sau merge

- [ ] T010 Run deploy xanh; trên VPS có image kho `sha-<commit>` và `.warehouse-tag`
- [ ] T011 Chạy bước kho qua đường của `daily.sh` trên VPS với snapshot đã chốt: image GHCR khởi động, migration chạy, bước `ingest` dừng ở `SnapshotClosedError` mà không ghi gì
- [ ] T012 Sáng 12/11: log lượt đêm ghi `image kho: sha-...`, `stat_sources` có hàng của `2026-11-12`, `/api/v1/city-shares` trả 200
