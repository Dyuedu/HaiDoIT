# Tasks: Trả số tin entry-level, tỷ lệ và n của mỗi vai trò

**Input**: `specs/146-tra-so-nguoi-moi/`

**Tests**: Viết trước theo `tdd.md`.

## Phase 1: Test

- [x] T001 Test mọi vai trò của config có dòng, vai trò vắng là 0 trong `tests/api/test_fr37_newcomer_roles_stat.py`
- [x] T002 Test đủ mẫu mà 0 entry-level hiện 0; dưới 30 tin là `null_data` nhưng còn số; ngưỡng lấy từ config
- [x] T003 Test thứ tự dòng
- [x] T004 Test Envelope: ngày, trạng thái, nguồn, nguồn lỗi; 404 khi chưa có snapshot
- [x] T005 Test `compose.prod.yml` chọn `stat`, `compose.local.yml` giữ `fake` trong `tests/deploy/test_gh146_nguoi_moi_doc_snapshot_that.py`

## Phase 2: Implementation

- [x] T006 Viết `StatMarket.newcomer_roles`, `_cell_meta` trong `haido_api/stat_market.py`
- [x] T007 Đặt `HAIDO_MARKET_SOURCE_NEWCOMER_ROLES: stat` trong `deploy/compose.prod.yml`
- [x] T008 Sửa bảng nguồn trong `docs/api/envelope-meta.md`
- [x] T009 Thêm đợt TDD và sửa cạnh biên trong `specs/144-hinh-nguoi-moi/`

## Phase 3: Sau merge

- [ ] T010 Gọi `GET /api/v1/newcomer-roles` trên prod, kiểm 200, 17 dòng, ngày snapshot mới nhất

## Phase 5: Cập nhật 2026-11-13 (#148)

- [x] T011 Test ô hỏng entry > n (đỏ trước khi sửa) trong `tests/api/test_fr37_newcomer_roles_stat.py`
- [x] T012 Bảo vệ entry > n trong `StatMarket.newcomer_roles`
