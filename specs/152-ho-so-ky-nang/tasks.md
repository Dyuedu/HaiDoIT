# Tasks: Hồ sơ kỹ năng của một vai trò ở một cấp

**Input**: `specs/152-ho-so-ky-nang/`

**Tests**: Viết trước theo `tdd.md`.

## Phase 1: Test

- [x] T001 Test cấp mặc định `entry`, đổi cấp gọi lại và đổi URL, trong `web/tests/fr19-skill-profile.test.tsx`
- [x] T002 Test dòng: tên, tỷ lệ, nhóm, đúng thứ tự API
- [x] T003 Test quay về (`fallback_label`, n), chưa đủ dữ liệu
- [x] T004 Test tick theo hồ sơ, dòng đếm core lấy từ API
- [x] T005 Test lỗi `unknown_cell`, mạng hỏng, envelope sai hợp đồng

## Phase 2: Implementation

- [x] T006 `web/lib/skill-rates.ts`
- [x] T007 `web/lib/skill-profile-view.ts`
- [x] T008 `skill-list.tsx`, `skill-profile-screen.tsx`, `web/app/ho-so-ky-nang/page.tsx`
- [x] T009 Thêm đợt TDD cho #147, #148

## Phase 3: Kiểm tay

- [x] T010 Chrome headless 360px và 1280px trên `next start` với API local (nguồn giả)
