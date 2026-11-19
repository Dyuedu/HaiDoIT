# Feature Specification: Bản đồ 3D theo prototype

**Feature Branch**: `gh-316-ban-do-3d-theo-prototype`

**Created**: 2026-11-17

**Status**: Implemented, chờ merge.

**Input**: GitHub issue [#316](https://github.com/Dyuedu/HaiDoIT/issues/316) — Match the 3D map to the prototype. Phục vụ story #112 (US-A3). Thiết kế: `_bmad-output/planning-artifacts/ux-designs/ux-HaiDoIT-2026-11-03/` (màn 01 "Bản đồ nhu cầu 3D", `DESIGN.md` mục Bản đồ, `map-column`, `icon-button`). Thay lối 3D WebGL của #314.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Bản đồ 3D trông và dùng như prototype (Priority: P1)

Một sinh viên mở trang chủ trên máy tính. Bản đồ nghiêng dần vào khung, ba cột vuông mọc lên ở Hà Nội, TP.HCM, Đà Nẵng, mỗi cột có thẻ nhãn ghi tên, tỷ trọng và số tin. Họ bấm nút xoay, kéo để xoay và nghiêng, chạm thẻ của Đà Nẵng (cỡ mẫu nhỏ) để thấy tỷ trọng. Bên phải là panel tóm tắt từng nơi và khung nguồn, lưu ý.

**Why this priority**: AC 1–5 của #316.

**Independent Test**: `web/tests/fr33-ban-do-3d.test.tsx`, `web/tests/fr33-ban-do-3d-hinh.test.ts`.

**Acceptance Scenarios**:

1. **Given** lối 3D, **When** xem, **Then** có khung `perspective: 1500px` cao 560px (420px dưới 640px, tỷ lệ 0,62), sân khấu 460×560 nghiêng `rotateX` 56° và `rotateZ` −16°, tấm lưới mờ dần, hình Việt Nam viền `selected` tô chấm, và "QĐ. Hoàng Sa", "QĐ. Trường Sa" kèm chấm đảo. (AC 1)
2. **Given** ba cột, **When** dựng, **Then** mỗi cột là khối vuông 28px, cao `share.value × 400` px (100% là 400px, như `p × 4` của prototype), mặt trên `selected`, mặt trước/sau `column-face`, hai bên `column-side`; cột đang chọn có mặt trên `text`. (AC 2)
3. **Given** cột đủ mẫu, **When** xem thẻ, **Then** thẻ ghi tên và "41,7% · 848/2.040 tin". **Given** cột mẫu nhỏ, **Then** cột opacity 0,4, thẻ viền `amber-deep`, có câu "Cỡ mẫu nhỏ (n = X < 30): số liệu chỉ để tham khảo", và tỷ trọng chỉ hiện khi trỏ, focus hoặc chạm (`.rev`). Tên đọc được của thẻ luôn có tỷ trọng và n. (AC 3)
4. **Given** lối 3D, **When** bấm "Xoay trái 30 độ", "Xoay phải 30 độ", "Đặt lại góc nhìn", **Then** `rotateZ` giảm 30°, tăng 30°, về 56°/−16°. **When** kéo ngang, **Then** `rotateZ` đổi 0,35° mỗi px; **When** kéo dọc, **Then** `rotateX` đổi 0,3° mỗi px, trong 0–72°. Kéo chỉ bắt đầu sau 6px. (AC 4)
5. **Given** mở lối 3D, **When** 250ms trôi qua, **Then** sân khấu nghiêng từ 0° lên 56° và cột mọc từ 0 lên chiều cao thật (chuyển động 1,1–1,4s); `prefers-reduced-motion: reduce` tắt chuyển động. (AC 4)
6. **Given** có số, **When** xem, **Then** panel bên phải "Tin <vai trò> nằm ở đâu" liệt kê ba nơi (tỷ trọng lớn, "848 / 2.040 tin · 03/11/2026", câu cỡ mẫu nhỏ nếu có, tỷ trọng mẫu nhỏ ẩn sau nút "Trỏ hoặc chạm để xem %"), rồi các dòng Làm từ xa, Nước ngoài, Không xác định; dưới đó là khung "Nguồn và lưu ý". Panel có ở cả ba lối. (AC 5)

### User Story 2 - Không chạy được CSS 3D (Priority: P1)

**Acceptance Scenarios**:

1. **Given** trình duyệt không hỗ trợ `transform-style: preserve-3d` (`CSS.supports`), **When** mở bản đồ, **Then** lối 2D mở, nút 3D `aria-disabled` kèm câu giải thích, không màn hình lỗi. (AC 6; thay điều kiện "không có WebGL" của #314, người dùng chốt 17/11/2026)
2. **Given** điện thoại (dưới 640px), **When** mở, **Then** lối 2D (NFR-12), nút 3D vẫn bấm được.
3. **Given** `web/package.json`, **When** đọc, **Then** không còn `three`, `@react-three/fiber`, `@types/three`. (AC 6)

### Edge Cases

- "Khác" không thành cột (DESIGN.md, FR-33). Từ #285 dữ liệu không còn dòng "Khác"; các phần không thành cột là Làm từ xa, Nước ngoài, Không xác định (như lối 2D), các tỉnh còn lại ở lối Bảng.
- Nút "Xem chi tiết Hà Nội" của prototype mở bảng chi tiết thành phố (FR-34), chưa có issue: không làm, không đặt nút giả.
- Tỷ trọng giữ một chữ số thập phân như lối 2D và bảng (không làm tròn số nguyên kiểu prototype), để ba lối cùng một số.
- Hình Việt Nam dùng viền geoBoundaries thật (chiếu vào sân khấu 460×560) thay cho đa giác vẽ tay của prototype, giữ đúng style (lớp nền, viền `selected`, chấm).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Cột đọc `view.bars` (AD-22); chiều cao không chuẩn hóa theo cột cao nhất.
- **FR-002**: Thẻ nhãn và nút là phần tử DOM, bấm và đọc được bằng bàn phím, trình đọc màn hình; vùng bấm ≥ 44px.
- **FR-003**: Dò CSS 3D bằng `useSyncExternalStore` (server: không, nên HTML tĩnh là lối 2D).
- **FR-004**: Màu từ token DESIGN.md (`selected`, `column-face`, `column-side`, `map-land`, `map-line`, `amber-deep`).

## Success Criteria *(mandatory)*

- **SC-001**: `cd web && npx vitest run` xanh; `tsc`, `lint`, `build` sạch.
- **SC-002**: Ảnh chụp Chrome headless 1440px đặt cạnh ảnh prototype màn 01: cùng bố cục, nghiêng, kiểu cột, thẻ, nút, panel.
