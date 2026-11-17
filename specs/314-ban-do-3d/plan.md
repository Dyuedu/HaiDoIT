# Implementation Plan: Lối xem bản đồ 3D

**Branch**: `gh-314-ban-do-3d` | **Date**: 2026-11-17 | **Spec**: [spec.md](spec.md)

## Summary

Thêm lối 3D vào màn Bản đồ: hình Việt Nam đùn từ GeoJSON đã rút gọn, hai quần đảo vẽ riêng, ba cột cao theo `view.bars`, OrbitControls để xoay và nghiêng, khung thông tin cho cột đang chọn. Dò WebGL trước khi mở 3D; error boundary rơi về 2D. Gói three.js tải lười.

## Technical Context

**Language/Version**: TypeScript, Next.js 16, React 19.3, Tailwind 4, Vitest + Testing Library

**Primary Dependencies**: thêm `three@0.187.0`, `@react-three/fiber@9.8.2`, `@types/three@0.187.0` (dev). Không dùng `@react-three/drei`: OrbitControls lấy từ `three/examples/jsm`, nhãn vẽ bằng sprite.

**Testing**: `cd web && npx vitest run tests/fr33-ban-do-3d.test.tsx tests/fr33-ban-do-3d-hinh.test.ts`; toàn bộ `npx vitest run`, `npx tsc --noEmit`, `npm run lint`, `npm run build`; Chrome headless 1280px và 360px. jsdom không có WebGL: test màn thay component canvas bằng bản giả, test hình học chạy hàm thuần.

**Constraints**: FR-33, FR-36, AD-22, DoD 360px và bàn phím; lối 2D không tải three.js.

## Project Structure

```text
web/lib/geo/vietnam-outline.json                 # mới: viền rút gọn (geoBoundaries, CC BY 4.0)
web/lib/vietnam-geo.ts                           # mới: phép chiếu, viền, vị trí thành phố, Hoàng Sa, Trường Sa
web/lib/map-3d-view.ts                           # mới: view.bars → cột (vị trí, chiều cao, mờ, nhãn)
web/lib/webgl.ts                                 # mới: dò WebGL cho useSyncExternalStore
web/lib/viewport.ts                              # mới: màn rộng từ 640px (điện thoại mở 2D, NFR-12)
web/app/components/map/map-3d.tsx                # mới: Canvas, viền, đảo, cột, OrbitControls, nhãn sprite
web/app/components/map/map-3d-panel.tsx          # mới: khung 3D, nút chọn cột, khung thông tin, error boundary, lazy
web/app/components/map/view-switch.tsx           # 3D bật khi có WebGL; câu khi không có
web/app/components/map/map-screen.tsx            # lối 3D mặc định khi có WebGL
web/tests/fr33-ban-do-3d.test.tsx                # mới
web/tests/fr33-ban-do-3d-hinh.test.ts            # mới
web/tests/fr33-map-screen.test.tsx               # test nút 3D đổi theo hành vi mới
web/package.json, web/package-lock.json          # ba gói mới
```

**Structure Decision**: Hình học và cột là hàm thuần để test trong jsdom; component canvas mỏng. Khung thông tin và nút chọn cột nằm ngoài canvas (DOM thường) để bàn phím và trình đọc màn hình dùng được.

## Complexity Tracking

- `map-screen.tsx`, `view-switch.tsx` thuộc #46 (không có `specs/`), #160 (không có `specs/`), #163, #280, #293 (có): thêm đợt TDD cho #163, #280, #293.
- Thêm ba gói npm: cần cho WebGL và React; không thêm drei để giữ gói nhỏ.
