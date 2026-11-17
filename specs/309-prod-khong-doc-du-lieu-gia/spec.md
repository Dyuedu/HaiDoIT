# Feature Specification: Production không bao giờ phục vụ fixture giả của thị trường

**Feature Branch**: `gh-309-prod-khong-doc-du-lieu-gia`

**Created**: 2026-11-17

**Status**: Implemented, chờ merge.

**Input**: GitHub issue [#309](https://github.com/Dyuedu/HaiDoIT/issues/309) — Production never serves the fake market fixture. Task ràng buộc, hạn 2026-11-18.

## Bối cảnh

Mã chọn nguồn mặc định `fake` cho mọi phép (`haido_api/routes/market.py`, `DEFAULT_SOURCE`). `deploy/compose.prod.yml` chỉ đặt `stat` cho `city_shares`, `newcomer_roles`, `skill_roles`. Ngày 2026-11-17, gọi thử prod cho thấy `skill-rates` và `learning-path` trả số của `haido_api/fixtures/fake_market.json`: meta ghi `published`, snapshot 2026-11-03, bảy nguồn thật. Màn hồ sơ kỹ năng hiện tỷ lệ giả ở cấp "Mới vào nghề" và báo "Không có ô thống kê…" kèm ngày giả ở cấp Fresher.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Prod chỉ đọc nguồn thật (Priority: P1)

Người dùng prod không bao giờ thấy số của fixture giả. Phép chưa có bản thật trả 404 `unknown_cell` "chưa có số liệu thật", không kèm ngày snapshot.

**Independent Test**: `tests/deploy/test_gh309_prod_khong_doc_du_lieu_gia.py`.

**Acceptance Scenarios**:

1. **Given** `deploy/compose.prod.yml`, **When** đọc môi trường của service `api`, **Then** mỗi khóa của `SOURCE_ENV` có giá trị `stat`. (AC 1)
2. **Given** môi trường của prod, **When** dựng nguồn bằng `load_sources`, **Then** mọi phép đều là `StatMarket`; `skill-rates` và `learning-path` trả 404 `unknown_cell` tới #151 và #216. (AC 1)
3. **Given** một phép mới được thêm vào `SOURCE_ENV` mà compose.prod không có dòng `stat`, **When** chạy test, **Then** test đỏ và nêu tên biến thiếu. (AC 2)
4. **Given** `deploy/compose.local.yml`, **When** đọc môi trường, **Then** mọi phép giữ `fake` (smoke của CI chạy trên DB rỗng).

### Edge Cases

- Màn hồ sơ kỹ năng trên prod sẽ báo "Tỷ lệ kỹ năng chưa có số liệu thật." ở mọi vai trò và cấp tới khi #151 xong. Web không ghi dòng ngày khi `snapshot_date = null` (`web/app/components/map/load-error.tsx`).
- `learning-path` chưa có màn gọi (`/co-van` là trang giữ chỗ), nhưng API công khai nên vẫn phải chặn.

## Requirements *(mandatory)*

- **FR-001**: Mọi khóa của `SOURCE_ENV` có mặt trong `deploy/compose.prod.yml` với giá trị `stat`.
- **FR-002**: Test đọc danh sách khóa từ chính `SOURCE_ENV`, không chép tay, để phép mới tự rơi vào kiểm tra.
- **FR-003**: compose.local không đổi.

## Ngoài phạm vi

- Đánh dấu dữ liệu giả cho người nhìn thấy được (đổi `snapshot_status` hay nguồn của fixture): kéo theo sửa mọi fixture web phải bằng hệt API giả; test ở FR-002 đã chặn đường lọt nên bỏ khỏi issue.
- Đổi câu lỗi "Không có ô thống kê…" của bản giả.

## Success Criteria *(mandatory)*

- **SC-001**: Sau deploy, `GET /api/v1/skill-rates?role=ai_ml&level=entry` và `GET /api/v1/learning-path?role=backend&level=entry` trên prod trả 404 `unknown_cell`, `snapshot_date = null`.

  Cập nhật 2026-11-17 (#151): `skill-rates` giờ trả số thật của `stat_skill_rates`; riêng `learning-path` vẫn 404 tới #216.
