# Implementation Plan: Bản đồ 3D theo prototype

**Branch**: `gh-316-ban-do-3d-theo-prototype` | **Date**: 2026-11-17 | **Spec**: [spec.md](spec.md)

## Summary

Bỏ lối 3D WebGL của #314, dựng lại bằng CSS 3D theo màn 01 của prototype: sân khấu nghiêng, tấm lưới, năm lớp SVG của hình Việt Nam, cột vuông năm mặt, thẻ nhãn quay ngược để luôn đứng thẳng, ba nút xoay và kéo bằng pointer. Thêm panel bên phải (tóm tắt từng nơi + "Nguồn và lưu ý") cho cả ba lối. Gỡ three.js.

## Technical Context

**Language/Version**: TypeScript, Next.js 16, React 19, Tailwind 4, CSS Modules, Vitest + Testing Library

**Primary Dependencies**: gỡ `three`, `@react-three/fiber`, `@types/three`. Không thêm gói.

**Testing**: `cd web && npx vitest run tests/fr33-ban-do-3d.test.tsx tests/fr33-ban-do-3d-hinh.test.ts`; toàn bộ; ảnh chụp Chrome headless so với prototype.

**Constraints**: DESIGN.md (perspective 1500px, khung 560/420px, `map-column`, `icon-button`), FR-33, FR-36, NFR-12, AD-22, `prefers-reduced-motion`.

## Project Structure

```text
web/lib/vietnam-geo.ts                          # thêm toStage, OUTLINE_PATH, vị trí đảo và nhãn trên sân khấu
web/lib/map-3d-view.ts                          # cột theo sân khấu: px, py, chiều cao px, thẻ
web/lib/css3d.ts                                # mới: dò preserve-3d (thay webgl.ts)
web/lib/webgl.ts                                # xóa
web/app/components/map/map-3d.tsx               # viết lại: CSS 3D (thay three.js)
web/app/components/map/map-3d.module.css        # mới: viewport, stage, plate, slab, mặt cột, thẻ
web/app/components/map/map-3d-panel.tsx         # xóa (gộp vào map-3d.tsx)
web/app/components/map/map-summary.tsx          # mới: panel bên phải
web/app/components/map/map-screen.tsx           # bố cục hai cột, lối 3D CSS, dò CSS 3D
web/tests/fr33-ban-do-3d.test.tsx               # viết lại
web/tests/fr33-ban-do-3d-hinh.test.ts           # cập nhật theo sân khấu
web/package.json, web/package-lock.json         # gỡ ba gói
```

**Structure Decision**: CSS của prototype đặt trong CSS Module (như `share-line.module.css`) vì transform 3D nhiều lớp khó viết bằng tiện ích Tailwind. Góc nhìn và chiều cao truyền bằng style nội tuyến như prototype.

## Complexity Tracking

- Sửa file của #314 (có `specs/`): thêm đợt TDD, ghi đổi điều kiện WebGL → CSS 3D (người dùng chốt).
- `map-screen.tsx` thuộc #46, #163, #280, #293: thêm đợt TDD cho #163, #280, #293.
