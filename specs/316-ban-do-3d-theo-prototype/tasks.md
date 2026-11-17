# Tasks: Bản đồ 3D theo prototype

**Input**: `specs/316-ban-do-3d-theo-prototype/`

**Tests**: Viết trước theo `tdd.md`.

## Phase 1: Test

- [x] T001 Test hình học theo sân khấu 460×560: viền, Hoàng Sa, Trường Sa, ba thành phố nằm trong sân khấu; cột cao `value × 400`, trong `web/tests/fr33-ban-do-3d-hinh.test.ts`
- [x] T002 Test màn: khung 3D, sân khấu `rotateX(56deg) rotateZ(-16deg)` sau khi mở, thẻ nhãn, cột mẫu nhỏ ẩn tỷ trọng, chọn thẻ đổi mặt trên, trong `web/tests/fr33-ban-do-3d.test.tsx`
- [x] T003 Test ba nút xoay, đặt lại; kéo ngang/dọc; giới hạn 0–72°
- [x] T004 Test panel bên phải ở cả ba lối; không CSS 3D thì 2D; điện thoại 2D; không còn three.js trong `package.json`

## Phase 2: Implementation

- [x] T005 `vietnam-geo.ts` (sân khấu), `map-3d-view.ts`, `css3d.ts`
- [x] T006 `map-3d.tsx`, `map-3d.module.css`, `map-summary.tsx`, `map-screen.tsx`
- [x] T007 Gỡ `three`, `@react-three/fiber`, `@types/three`; xóa `webgl.ts`, `map-3d-panel.tsx`
- [x] T008 Thêm đợt TDD cho #314, #163, #280, #293

## Phase 3: Kiểm tay

- [x] T009 Ảnh chụp Chrome headless 1440px và 360px, đặt cạnh ảnh prototype màn 01
