# Tasks: Chọn một kỹ năng bằng tiếng Anh hoặc tiếng Việt

**Input**: `specs/167-chon-mot-ky-nang/`

**Tests**: Viết trước theo `tdd.md`.

## Phase 1: Test

- [x] T001 Test gõ "học máy" → chọn → gọi API đúng mã, ghi kỹ năng đã dùng, URL đổi, `aria-pressed`, trong `web/tests/fr13-chon-mot-ky-nang.test.tsx`
- [x] T002 Test chọn nhanh từ hồ sơ; mở với `?skill=`; mã sai trong URL; không có kết quả
- [x] T003 Test `mentioned = false` (ABAP) và `mentioned = true` mọi dòng 0 (SAP); `unknown_skill`

## Phase 2: Implementation

- [x] T004 `skill-picker.tsx`
- [x] T005 Tên kỹ năng đã dùng và câu "chưa tin nào nhắc" trong `skill-roles-screen.tsx`
