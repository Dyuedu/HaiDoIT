# Feature Specification: Câu chữ trên màn hình viết bằng tiếng Việt dễ hiểu

**Feature Branch**: `gh-324-cau-chu-de-hieu`

**Created**: 2026-11-19

**Status**: Implemented, chờ merge. 2026-11-25 (#217): `learningPathHref` nhận `skill` tùy chọn, hành vi không đổi.

**Input**: GitHub issue [#324](https://github.com/Dyuedu/HaiDoIT/issues/324) — Rewrite on-screen copy in plain Vietnamese. Task phục vụ #110, #111, #112, #113, #280.

## Bối cảnh

Chữ trên Bản đồ, Insights và Hồ sơ kỹ năng đọc như ghi chú của lập trình viên: mỗi con số gắn nhãn thống kê `n = 585`, chú thích ghi "Ngày snapshot", "Nguồn lỗi ở snapshot này: itnavi", "Cỡ mẫu nhỏ (n = 12 < 30)", nguồn ghi bằng mã viết thường. Người dùng ngày 2026-11-19 duyệt bảng câu thay thế; issue này đổi chữ, không đổi số.

Người dùng đã đồng ý ý của AC cũ vẫn giữ nguyên: AC của #110 và #113 ghi "not enough data (X/30)"; câu mới "Mới có X tin, cần ít nhất 30" vẫn nói đủ X và ngưỡng.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Cỡ mẫu đọc thành câu (Priority: P1)

Người xem thấy số tin dưới dạng một cụm từ, không thấy ký hiệu `n`.

**Independent Test**: `web/tests/fr36-gh324-cau-chu-de-hieu.test.tsx` dựng từng màn và quét chữ hiển thị.

**Acceptance Scenarios**:

1. **Given** Bản đồ, Insights hay Hồ sơ kỹ năng đã có số, **When** đọc mọi chữ trên màn, **Then** không có chuỗi `n = `. (AC 1)
2. **Given** dòng vai trò ở màn người mới có tỷ lệ, **When** đọc dòng, **Then** thấy tỷ lệ "29,4%" và câu "172 trên 585 tin dành cho người mới". (AC 6)
3. **Given** dòng vai trò ở mục kỹ năng dùng ở vai trò nào, **When** đọc dòng, **Then** thấy "77,6% tin AI/ML cho người mới có nhắc tới Python" và "tính trên 501 tin". (AC 6)
4. **Given** Hồ sơ kỹ năng quay về ô rộng hơn, **When** đọc khung báo, **Then** thấy "Tính trên 157 tin". (AC 1)

### User Story 2 - Nhóm ít tin nói rõ thiếu bao nhiêu (Priority: P1)

**Acceptance Scenarios**:

1. **Given** dòng dưới ngưỡng ở màn người mới hoặc mục kỹ năng theo vai trò, **When** đọc, **Then** thấy "Mới có 12 tin, cần ít nhất 30"; dòng không có tin nào ghi "Chưa có tin nào". (AC 2)
2. **Given** dòng thành phố mẫu nhỏ trên Bản đồ, **When** đọc, **Then** thấy "Mới có 21 tin, chưa đủ 30 để so sánh chắc chắn"; trong bảng, cột ghi chú là "Mới có 21 tin, chưa đủ 30"; dòng có 0 tin ghi "Chưa có tin nào". (AC 3)

### User Story 3 - Khung nguồn viết như người nói (Priority: P1)

**Acceptance Scenarios**:

1. **Given** khung "Nguồn và lưu ý", **When** đọc nhãn, **Then** thấy "Đang xem", "Nguồn", "Cập nhật"; nguồn ghi "CareerLink, ITnavi, ITviec, MoMo Careers, TopCV, TopDev, VietnamWorks, Zalo Careers". (AC 4)
2. **Given** snapshot `partial` lỗi nguồn `topdev`, **When** đọc khung, **Then** thấy "Lần cập nhật này chưa lấy đủ tin từ TopDev". (AC 4)
3. **Given** bộ lọc mọi vai trò, mới vào nghề, mọi số năm, **When** đọc dòng "Đang xem", **Then** thấy "Mọi vai trò, mới vào nghề, mọi số năm kinh nghiệm". (AC 4)
4. **Given** lọc số năm khác "Mọi số năm", **When** đọc câu số tin bị bỏ, **Then** thấy "5 tin không ghi số năm kinh nghiệm nên không được tính (mọi vai trò, mới vào nghề)."

### User Story 4 - Tiêu đề bản đồ và các câu còn lại (Priority: P2)

**Acceptance Scenarios**:

1. **Given** Bản đồ 3D vai trò Backend, mọi cấp, mọi số năm, **When** đọc tiêu đề khung, **Then** thấy "521 tin Backend · mọi cấp bậc, mọi số năm kinh nghiệm"; vai trò "Tất cả" ghi "tin IT". (AC 5)
2. **Given** kỹ năng chưa tin nào nhắc, **When** đọc, **Then** thấy "Hiện chưa tin tuyển dụng nào nhắc tới ABAP." (AC 6)
3. **Given** chữ hiện trên các màn, **When** tìm "snapshot" hoặc "entry-level", **Then** không thấy. Câu giới thiệu Bản đồ ghi "kèm số tin, nguồn và ngày cập nhật". (AC 7)

### Edge Cases

- `fallback_label`, `coverage_notes` và câu lỗi là chữ do API gửi; web in nguyên văn, ngoài phạm vi.
- Nhãn trong ô chọn ("Mọi số năm", "Mọi cấp bậc") giữ nguyên; chỉ dòng "Đang xem" và tiêu đề viết thường chữ đầu của phần sau.
- Mã nguồn chưa có tên hiển thị thì in nguyên mã.

## Requirements *(mandatory)*

- **FR-001**: Không chữ hiển thị nào chứa `n = `. Cỡ mẫu ghi "trên N tin" (người mới), "tính trên N tin" (kỹ năng theo vai trò), "Tính trên N tin" (Hồ sơ kỹ năng).
- **FR-002**: Một hàm chung dựng câu thiếu mẫu: 0 tin thì "Chưa có tin nào"; ngược lại "Mới có N tin, cần ít nhất M" (danh sách) hoặc "Mới có N tin, chưa đủ M" (thêm " để so sánh chắc chắn" ở dòng chú thích bản đồ).
- **FR-003**: Tên nguồn hiển thị lấy từ `web/lib/source-labels.ts`; khung nguồn và câu nguồn thiếu đều dùng nó.
- **FR-004**: Số, thứ tự, ẩn số theo ngưỡng giữ đúng như API gửi (AD-22). Chỉ chữ đổi. (AC 8)

## Ngoài phạm vi

- Thiết kế lại bố cục trang Insights (mockup riêng).
- Chữ do API gửi (`fallback_label`, `coverage_notes`, câu lỗi).

## Success Criteria *(mandatory)*

- **SC-001**: `cd web && npx vitest run` xanh, gồm test mới của #324 và các test cũ đã đổi câu.
- **SC-002**: Mở `/`, `/insights`, `/ho-so-ky-nang` trên bản build: không thấy `n = `, "snapshot", "entry-level".
