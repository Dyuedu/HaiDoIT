# Tasks: Tỷ lệ kỹ năng theo vai trò, số thật

**Input**: `specs/168-ky-nang-vai-tro-that/`

**Tests**: Viết trước theo `tdd.md`.

## Phase 1: Test

- [x] T001 Test xếp hạng theo tỷ lệ rồi mã, 0 khi đủ mẫu, `mentioned`, meta ô entry, snapshot chọn, trong `tests/api/test_fr09_skill_roles_stat.py`
- [x] T002 Test dưới 30: `null_data`, X là `n_scanned`, ô không có, thứ tự theo X
- [x] T003 Test 404 (chưa snapshot, kỹ năng không có hàng), 500 khi `n_scanned > n`, SQL chỉ `stat_*`
- [x] T004 `tests/api/test_ad17_meta_nguon_stat.py`: `skill-roles` vào REAL

## Phase 2: Implementation

- [x] T005 `StatMarket.skill_roles` và `_skill_role_rows` trong `haido_api/stat_market.py`
- [x] T006 `tests/api/test_fr09_skill_roles.py`: thay test "stat luôn 404"
- [x] T007 `deploy/compose.prod.yml` (comment), `docs/api/envelope-meta.md`, docstring `test_gh166_*`
- [x] T008 Cập nhật `specs/` của các issue cũ có file chung
- [x] T009 Mutation: bỏ thứ tự theo cỡ mẫu, `mentioned` từ ô entry, `display` theo `n`, bỏ lọc kỹ năng

## Phase 3: Sửa theo review (2026-11-17)

- [x] T010 Test trước: hòa tỷ lệ mà `n_scanned` lớn hơn, `mentioned` bỏ qua hàng `all × entry`, ngưỡng `min_sample` và `min_sample - 1`, đuôi `null_data` theo mã, snapshot không có nguồn, `sources_failed`, guard dữ liệu mâu thuẫn, `UnknownSkill` trước kết nối, factory đếm lần gọi, trong `tests/api/test_fr09_skill_roles_stat.py` và `tests/api/test_fr09_skill_roles.py`
- [x] T011 `haido_api/stat_market.py`: `UnknownSkill` trước kết nối, guard `n_with`, khóa sắp xếp dùng `DisplayState.NULL_DATA` nhất quán, `_skill_role_rows` trả thêm `n_with` theo vai trò
- [x] T012 Mutation lại cho các hành vi mới (xem `tdd.md`, đợt review)

- [x] T-230 Cập nhật 2026-11-27 theo #230: thêm nguồn `posting_check` (và các mục cộng thêm) vào các file của issue này; kiểm bằng `tdd.md` mục "Đợt sửa 2026-11-27"
