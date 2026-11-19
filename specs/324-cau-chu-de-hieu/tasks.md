# Tasks: Câu chữ trên màn hình viết bằng tiếng Việt dễ hiểu

**Input**: `specs/324-cau-chu-de-hieu/`

## Phase 1: Test

- [x] T001 [US1–US4] Viết `web/tests/fr36-gh324-cau-chu-de-hieu.test.tsx`: quét chữ ba màn không có `n = `, "snapshot", "entry-level"; câu thiếu mẫu; khung nguồn; tiêu đề bản đồ.
- [x] T002 Đổi câu kỳ vọng trong các test cũ theo bảng đã duyệt.
- [x] T003 Chạy `npx vitest run`, ghi RED vào `tdd.md`.

## Phase 2: Code

- [x] T004 Thêm `web/lib/source-labels.ts`.
- [x] T005 Sửa `city-shares-view.ts`, `newcomer-roles-view.ts`, `skill-roles-view.ts`, `skill-profile-view.ts`.
- [x] T006 Sửa `snapshot-caption.tsx`, `load-error.tsx`, `map-3d.tsx`, `newcomer-list.tsx`, `skill-roles-list.tsx`, `page.tsx`.
- [x] T007 Chạy `npx vitest run`, `npm run lint`, `npm run build`; ghi GREEN.

## Phase 3: Spec của issue cũ

- [x] T008 Thêm đợt tdd vào các thư mục `specs/` liên quan; sửa câu cũ trong scenario.
