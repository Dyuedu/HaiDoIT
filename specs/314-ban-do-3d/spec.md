# Feature Specification: Lối xem bản đồ 3D

**Feature Branch**: `gh-314-ban-do-3d`

**Created**: 2026-11-17

**Status**: Implemented (PR #315). 2026-11-17: lối 3D được dựng lại bằng CSS 3D theo prototype ở #316; three.js bị gỡ. Điều kiện rơi về 2D đổi từ "không có WebGL" sang "không dựng được CSS 3D" (người dùng chốt 2026-11-17; FR-36 nên sửa câu chữ). Các scenario về canvas WebGL, OrbitControls và error boundary không còn áp dụng.

**Input**: GitHub issue [#314](https://github.com/Dyuedu/HaiDoIT/issues/314) — Build the 3D map view. Phục vụ story #112 (US-A3). Quyết định DEC-5 (#131) ghi ngày 17/11/2026: giữ bản đồ 3D theo FR-33. FR-33, FR-36, NFR-12, UX-DR12, UX-DR39, UX-DR50.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Xem tỷ trọng ba thành phố trên bản đồ 3D (Priority: P1)

Một sinh viên mở trang chủ trên máy tính có WebGL. Bản đồ mở ở lối 3D: hình Việt Nam có Hoàng Sa và Trường Sa, ba cột cho Hà Nội, TP.HCM, Đà Nẵng, cao theo tỷ trọng của thành phố trong số tin của vai trò đang chọn. Họ xoay, nghiêng bản đồ, trỏ vào một cột và thấy tỷ trọng kèm cỡ mẫu.

**Why this priority**: AC 1–4 của #314.

**Independent Test**: `web/tests/fr33-ban-do-3d.test.tsx`, `web/tests/fr33-ban-do-3d-hinh.test.ts`.

**Acceptance Scenarios**:

1. **Given** dữ liệu viền, **When** dựng bản đồ, **Then** có đất liền Việt Nam (geoBoundaries, CC BY 4.0) và hai quần đảo Hoàng Sa, Trường Sa, mỗi quần đảo có nhãn; các điểm đảo nằm trong vùng tọa độ của quần đảo đó. (AC 1)
2. **Given** envelope `city-shares`, **When** dựng cột, **Then** có đúng ba cột Hà Nội, TP.HCM, Đà Nẵng, theo `view.bars`; Đà Nẵng luôn có. (AC 1)
3. **Given** một cột, **When** tính chiều cao, **Then** chiều cao tỷ lệ thuận với `share.value` của chính dòng mà biểu đồ 2D vẽ (một chiều cao một nghĩa); hai cột có tỷ trọng gấp đôi nhau thì cao gấp đôi. (AC 2)
4. **Given** cột `low_sample_shown`, **When** dựng, **Then** cột vẫn cao theo tỷ trọng thật, mờ, và nhãn của nó có "Cỡ mẫu nhỏ (n = X < 30): số liệu chỉ để tham khảo"; cột vẫn chọn được. (AC 3)
5. **Given** lối 3D, **When** chọn một cột (trỏ, chạm, hoặc nút của cột đó bằng bàn phím), **Then** khung thông tin ghi tên thành phố, tỷ trọng và số tin, đọc qua `role="status"`. (AC 4)
6. **Given** lối 3D, **When** kéo chuột hay vuốt, **Then** bản đồ xoay và nghiêng (OrbitControls, góc nghiêng giới hạn để không lật xuống dưới mặt đất). (AC 4, kiểm tay)

### User Story 2 - Chuyển lối xem, và trình duyệt không có WebGL (Priority: P1)

**Acceptance Scenarios**:

1. **Given** trình duyệt có WebGL và màn rộng từ 640px, **When** mở bản đồ, **Then** lối 3D được chọn sẵn (UX-DR39); bấm "Biểu đồ 2D" hoặc "Bảng" thì chuyển, bấm "3D" thì quay lại. (AC 5)
2. **Given** trình duyệt không có WebGL, **When** mở bản đồ, **Then** lối 2D mở, nút 3D `aria-disabled` kèm câu "Trình duyệt này không chạy được bản đồ 3D, nên đang hiện biểu đồ 2D.", không có màn hình lỗi. (AC 5)
3. **Given** lối 3D lỗi khi dựng (mất context WebGL, lỗi tải), **When** lỗi xảy ra, **Then** màn chuyển sang lối 2D với cùng câu trên, không màn hình lỗi. (AC 5)
4. **Given** lối 3D, **When** xem, **Then** khung "Nguồn và lưu ý" và chú thích Khác / Làm từ xa / Nước ngoài / không xác định vẫn hiện như lối 2D. (AC 6)
5. **Given** server render, **When** trang tĩnh được dựng, **Then** HTML là lối 2D (server không có WebGL); trình duyệt có WebGL chuyển sang 3D sau khi hydrate, không lệch HTML.

### Edge Cases

- Điện thoại (dưới 640px): mở lối 2D, là danh sách thành phố kèm thanh tỷ trọng (NFR-12, UX-DR39), dù có WebGL; nút 3D vẫn bấm được, khung 3D cao 420px (UX-DR50); câu "Mở trên máy tính để xem bản đồ đầy đủ" giữ nguyên.
- Đổi vai trò, cấp hay số năm: cột đổi chiều cao theo envelope mới; khung thông tin bỏ chọn khi thành phố không còn.
- Gói three.js chỉ tải khi mở lối 3D (lazy), để lối 2D không nặng thêm.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Cột 3D đọc `view.bars` của `buildCitySharesView`, không tính lại tỷ trọng (AD-22).
- **FR-002**: Chiều cao = `share.value` × hằng số chiều cao tối đa; không chuẩn hóa theo cột cao nhất.
- **FR-003**: Hoàng Sa và Trường Sa luôn được vẽ và có nhãn.
- **FR-004**: Dò WebGL bằng `useSyncExternalStore` (snapshot server là "không có"); lỗi trong lối 3D bị chặn bằng error boundary và chuyển 2D.
- **FR-005**: Nguồn viền và giấy phép ghi ở `web/lib/geo/vietnam-outline.json` và trong chú thích của lối 3D.

## Success Criteria *(mandatory)*

- **SC-001**: `cd web && npx vitest run` xanh; `npx tsc --noEmit`, `npm run lint`, `npm run build` sạch.
- **SC-002**: Chrome headless 1280px và 360px: lối 3D vẽ được canvas, không cuộn ngang, nút ≥ 44px; kéo chuột đổi góc nhìn.

## Assumptions

- Không có tile hay dịch vụ bản đồ ngoài: hình Việt Nam là mặt phẳng đùn từ GeoJSON, chiếu tuyến tính quanh vĩ độ 16°B.
- Tọa độ các đảo của Hoàng Sa, Trường Sa là điểm đại diện xấp xỉ, đủ cho bản đồ tỷ lệ nhỏ; không dùng để đo đạc.
