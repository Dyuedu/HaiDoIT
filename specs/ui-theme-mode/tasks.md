# Tasks: Chế độ Sáng / Tối toàn hệ thống

- [x] T001 Tạo spec & plan tại `specs/ui-theme-mode/`
- [x] T002 [TDD RED→GREEN] Viết `web/tests/theme-mode.test.tsx` và cập nhật `web/tests/ad23-haido-keys.test.ts`
- [x] T003 Cài `haido:theme` trong `web/lib/haido-keys.ts`, `web/lib/theme-store.ts`, `web/app/layout.tsx`
- [x] T004 Thêm token `:root[data-theme="light"]` trong `web/app/globals.css`, `ThemeToggle` trong `app-header.tsx`, và chuyển `map-3d`, `pie-3d`, `charts`, `filter-select`, `soi-tin` sang biến CSS theo theme
- [x] T005 Chạy `tools/gates/check_gates.py`, `vitest`, `tsc`, `lint`, `next build` và cập nhật `specs/205-*`, `specs/ui-theme-mode/tdd.md`
