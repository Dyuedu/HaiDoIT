# Feature Specification: Toàn cảnh thị trường trên Insights

**Feature Branch**: `gh-329-man-tong-quan`

**Created**: 2026-11-19

**Status**: Implemented, chờ merge.

**Input**: GitHub issue [#329](https://github.com/Dyuedu/HaiDoIT/issues/329) — Show the market overview on Insights. Task phục vụ story #326.

## Bối cảnh

Trang Insights hiện chỉ có hai danh sách chữ. Mockup ngày 2026-11-19 (số thật của snapshot 19/11) được duyệt làm hướng: chỉ số đầu trang, câu tóm tắt, biểu đồ tròn 3D theo cấp lọc biểu đồ vai trò, cột số năm và nơi làm việc, biểu đồ hai phía Hà Nội/TP.HCM. Số lấy từ `GET /api/v1/market-overview` (#327, #328).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Thấy toàn cảnh khi mở Insights (Priority: P1)

**Independent Test**: `web/tests/us-a11-ad22-toan-canh.test.tsx`.

**Acceptance Scenarios** (theo AC của #326):

1. **Given** API trả toàn cảnh, **When** mở Insights, **Then** có bốn chỉ số: tin IT đang mở, tỷ lệ người mới, tỷ lệ ở Hà Nội hoặc TP.HCM, tỷ lệ không ghi số năm; mỗi chỉ số có số tin và ngày cập nhật; tỷ lệ in đúng `share.value` của API. (AC 1)
2. **Given** biểu đồ tròn, **When** chọn Senior bằng nút chú thích, **Then** nút đó `aria-pressed`, biểu đồ vai trò đổi tên thành "Tin cấp Senior theo vai trò" và theo đúng `roles_by_level` của Senior; "Bỏ lọc cấp bậc" trả về thứ tự `roles`. (AC 2)
3. **Given** biểu đồ tròn, **When** dùng bàn phím, **Then** có nút "Xoay trái", "Xoay phải"; canvas `aria-hidden`. (AC 2 của #329)
4. **Given** toàn cảnh, **When** xem, **Then** có cột số năm (từ "Không cần kinh nghiệm" tới "Không ghi"), cột nơi làm việc (Hà Nội, TP.HCM, Đà Nẵng, Tỉnh khác, …) và biểu đồ hai phía cho mọi vai trò đủ mẫu trừ "Vai trò khác". (AC 3)
5. **Given** câu tóm tắt, **When** đọc, **Then** không có chữ số; câu đầu gọi tên hai cấp đứng đầu `levels_by_size`; có câu gọi tên hai vai trò đứng đầu `roles_by_entry_share`. (AC 4)
6. **Given** vai trò dưới 30 tin (Nhúng, 12 tin), **When** xem biểu đồ vai trò, **Then** dòng mờ và có "Mới có 12 tin, chưa đủ 30". (AC 5)
7. **Given** năm biểu đồ, **When** xem, **Then** mỗi biểu đồ có "Xem bảng số". (AC 6)
8. **Given** API trả `unknown_cell`, **When** mở, **Then** hiện câu của API, không có "Thử lại"; body sai hợp đồng thì "Không đọc được số liệu. Thử lại sau."

### Edge Cases

- Web không sắp xếp và không chia: thứ tự lấy từ `roles`, `roles_by_level`, `roles_by_entry_share`, `levels_by_size`; tỷ lệ in từ `share.value`. Độ dài thanh và chiều cao cột là tỷ lệ vẽ so với phần lớn nhất của biểu đồ, không phải số in ra.
- Biểu đồ tròn nghiêng làm miếng phía trước trông lớn hơn; phần trăm ghi trên miếng và trong nút chú thích.
- jsdom không có canvas: biểu đồ tròn bỏ qua phần vẽ, nút chú thích và bảng vẫn đủ.

## Requirements *(mandatory)*

- **FR-001**: Không thêm thư viện biểu đồ. Thanh, cột, hai phía vẽ bằng HTML/CSS; biểu đồ tròn vẽ bằng canvas.
- **FR-002**: Mỗi biểu đồ có một bảng số gập sẵn với đủ số của biểu đồ.
- **FR-003**: Câu chữ theo #324: "trên N tin", "Mới có N tin, chưa đủ 30", không có `n = `.

## Ngoài phạm vi

- Vẽ lại danh sách người mới và danh sách kỹ năng theo vai trò: #330.

## Success Criteria *(mandatory)*

- **SC-001**: `npx vitest run` xanh; `npm run lint`, `tsc --noEmit` sạch.
