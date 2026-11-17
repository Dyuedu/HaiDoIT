# Tasks: Lối xem bản đồ 3D

**Input**: `specs/314-ban-do-3d/`

**Tests**: Viết trước theo `tdd.md`.

## Phase 1: Test

- [x] T001 Test hình học: viền có đất liền, Hoàng Sa và Trường Sa có điểm trong vùng tọa độ và có nhãn, phép chiếu giữ hướng bắc–nam, trong `web/tests/fr33-ban-do-3d-hinh.test.ts`
- [x] T002 Test cột: đúng ba thành phố theo `view.bars`, chiều cao tỷ lệ với `share.value`, cột mẫu nhỏ mờ và có câu "Cỡ mẫu nhỏ"
- [x] T003 Test màn: có WebGL thì mở 3D, chuyển 2D/Bảng/3D; chọn cột hiện tỷ trọng và n trong `role="status"`; chú thích vẫn hiện, trong `web/tests/fr33-ban-do-3d.test.tsx`
- [x] T004 Test không có WebGL: mở 2D, nút 3D `aria-disabled` kèm câu; lỗi trong lối 3D chuyển 2D không màn hình lỗi
- [x] T005 Sửa test nút 3D cũ trong `web/tests/fr33-map-screen.test.tsx` theo hành vi mới

## Phase 2: Implementation

- [x] T006 `web/lib/geo/vietnam-outline.json`, `web/lib/vietnam-geo.ts`
- [x] T007 `web/lib/map-3d-view.ts`, `web/lib/webgl.ts`
- [x] T008 Cài `three`, `@react-three/fiber`, `@types/three`; `map-3d.tsx`, `map-3d-panel.tsx`
- [x] T009 `view-switch.tsx`, `map-screen.tsx`
- [x] T010 Thêm đợt TDD cho #163, #280, #293

## Phase 3: Kiểm tay

- [x] T011 Chrome headless 1280px và 360px: canvas vẽ, kéo đổi góc nhìn, không cuộn ngang
