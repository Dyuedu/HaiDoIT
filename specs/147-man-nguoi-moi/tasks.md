# Tasks: Màn người mới và lối sang hồ sơ kỹ năng

**Input**: `specs/147-man-nguoi-moi/`

**Tests**: Viết trước theo `tdd.md`.

## Phase 1: Test

- [x] T001 [US1] Test danh sách theo thứ tự API, không sắp xếp lại, số của dòng đủ mẫu, trong `web/tests/fr37-newcomer-list.test.tsx`
- [x] T002 [US1] Test dòng dưới ngưỡng ghi "chưa đủ dữ liệu (n/ngưỡng)", ngưỡng từ meta; dòng 0 tin vẫn ở lại
- [x] T003 [US1] Test khung chú thích; lỗi `unknown_cell`; mạng hỏng và thử lại
- [x] T004 [US1] Test tám kiểu envelope sai hợp đồng
- [x] T005 [US2] Test liên kết của dòng; trang giữ chỗ gọi tên vai trò, mã lạ
- [x] T006 [US3] Test câu không có chữ số (DEC-6)

## Phase 2: Implementation

- [x] T007 Export hàm kiểm trong `web/lib/city-shares.ts`
- [x] T008 `fetchNewcomerRoles` và kiểm envelope trong `web/lib/newcomer-roles.ts`
- [x] T009 `web/lib/newcomer-roles-view.ts`
- [x] T010 `newcomer-list.tsx`, `newcomer-screen.tsx`, `web/app/insights/page.tsx`
- [x] T011 `web/app/ho-so-ky-nang/page.tsx`
- [x] T012 Thêm đợt TDD cho #144, #163, #280, #285

## Phase 3: Kiểm tay

- [x] T013 Chrome headless 360px và 1280px trên `next start` với API local (nguồn giả)

## Phase 4: Sau merge

- [ ] T014 Khi PR #290 đã deploy, mở `/insights` trên prod và kiểm số khớp `GET /api/v1/newcomer-roles`
