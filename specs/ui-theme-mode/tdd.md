# Nhật ký TDD: Chế độ Sáng / Tối toàn hệ thống

**Spec**: [spec.md](spec.md)

## Đợt 1 — 2026-11-27

- **RED**: `cd web && npx vitest run tests/theme-mode.test.tsx tests/ad23-haido-keys.test.ts` → `2 failed (files) | 6 failed, 8 passed (14 tests)` (chưa có `haido:theme`, chưa có nút chuyển giao diện trong `AppHeader`, chưa có `:root[data-theme="light"]`, `FilterSelect` còn ép `[color-scheme:dark]` và `soi-tin` dùng hex nền tối).
- **Cổng AD-23**: Lượt chạy trung gian báo `AD-23 FAIL` do `web/tests/theme-mode.test.tsx` gọi trực tiếp `window.localStorage.getItem/setItem`; sửa test đi qua `readTheme`/`writeTheme` từ `@/lib/haido-keys`.
- **GREEN**:
  - `.venv\Scripts\python.exe tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24 AD-23` → `10 pass, 0 skipped, 0 failed`.
  - `npx vitest run` → `36 passed (36) | 450 passed (450)`.
  - `npx tsc --noEmit` → thoát `0`.
  - `npm run lint` (`eslint .`) → `0 errors, 0 warnings`.
  - `npm run build` (`next build`) → thoát `0`, các trang tĩnh `○ /`, `○ /insights`, `○ /soi-tin` vẫn giữ static generation (lượt đầu sau khi dọn `.next` báo `SecurityFatalError` của Next 16.4.4, chạy lại thoát `0`).
