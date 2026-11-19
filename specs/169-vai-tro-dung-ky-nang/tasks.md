# Tasks: Vai trò nào dùng một kỹ năng

**Input**: `specs/169-vai-tro-dung-ky-nang/`

**Tests**: Viết trước theo `tdd.md`.

## Phase 1: Test

- [x] T001 Test danh sách đúng thứ tự API, câu tỷ lệ với ô số riêng, n theo `skill_count`, trong `web/tests/fr09-vai-tro-dung-ky-nang.test.tsx`
- [x] T002 Test dòng `null_data` ghi "chưa đủ dữ liệu (X/30)", ngưỡng từ meta
- [x] T003 Test chạm dòng mở `/ho-so-ky-nang?role=&level=entry`
- [x] T004 Test lỗi `unknown_cell`, mạng hỏng; khung "Nguồn và lưu ý"; câu không chữ số

## Phase 2: Implementation

- [x] T005 `web/lib/skill-roles-view.ts`, `web/lib/location-search.ts`
- [x] T006 `skill-roles-list.tsx`, `skill-roles-screen.tsx`, mục trên `web/app/insights/page.tsx`
- [x] T007 Thêm đợt TDD cho #147

## Phase 3: Kiểm tay

- [x] T008 Chrome headless 360px và 1280px trên `next start` với API local (nguồn giả)
