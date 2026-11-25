# Tasks: Mở lộ trình học từ một kỹ năng còn thiếu

**Input**: `specs/153-mo-lo-trinh-tu-ky-nang/`

**Tests**: Viết trước theo `tdd.md`.

## Phase 1: Test

- [x] T001 Test liên kết của dòng chưa tick; dòng đã tick không có liên kết, ghi "Đã có"; tick/bỏ tick đổi liên kết, trong `web/tests/fr22-mo-lo-trinh-tu-ky-nang.test.tsx`
- [x] T002 Test trang `/co-van`: gọi tên vai trò, cấp, kỹ năng; nút quay lại; mã lạ; không chữ số

## Phase 2: Implementation

- [x] T003 `learningPathHref` và liên kết trong `skill-list.tsx`
- [x] T004 `web/app/co-van/page.tsx`, `path-placeholder.tsx`

## Thay đổi sau merge (2026-11-25, #217)

- [x] T005 Thay bốn test trang giữ chỗ bằng test màn lộ trình trong `web/tests/fr22-mo-lo-trinh-tu-ky-nang.test.tsx`
