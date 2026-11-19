# Feature Specification: Danh sách người mới và kỹ năng theo vai trò thành biểu đồ

**Feature Branch**: `gh-330-bieu-do-nguoi-moi-ky-nang`

**Created**: 2026-11-19

**Status**: Implemented, chờ merge.

**Input**: GitHub issue [#330](https://github.com/Dyuedu/HaiDoIT/issues/330) — Draw the newcomer and skill-across-roles lists as charts. Task phục vụ #326, #110, #113.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Nhìn được ngay vai trò nào rộng cửa (Priority: P1)

**Independent Test**: `web/tests/us-a11-fr37-fr09-bieu-do.test.tsx`; test cũ của #110 (`fr37-*`) và #113 (`fr09-*`, `fr13-*`) giữ nguyên.

**Acceptance Scenarios**:

1. **Given** danh sách người mới, **When** xem, **Then** dòng có tỷ lệ có một thanh dài theo tỷ lệ API gửi so với tỷ lệ lớn nhất của danh sách; dòng chưa đủ dữ liệu không có thanh; chữ, thứ tự và câu thiếu mẫu như cũ. (AC 1)
2. **Given** danh sách người mới, **When** mở "Xem bảng số", **Then** bảng có mọi vai trò. (AC 2)
3. **Given** `market-overview` trả được, **When** xem, **Then** dưới danh sách có "Cơ cấu cấp bậc của từng vai trò" theo đúng thứ tự danh sách người mới; mỗi đoạn dài đúng tỷ lệ cấp API gửi; vai trò API ẩn tỷ lệ cấp ghi "chưa đủ dữ liệu". `market-overview` lỗi thì chỉ thiếu biểu đồ này.
4. **Given** mục kỹ năng theo vai trò, **When** chọn Python, **Then** dòng có tỷ lệ có biểu đồ lollipop trên trục 0–100%, chấm đứng đúng `share.value`; dòng chưa đủ dữ liệu không có chấm; có bảng số. (AC 1, AC 2)
5. **Given** một dòng, **When** chọn, **Then** vẫn mở hồ sơ kỹ năng của vai trò. (AC 3)

## Requirements *(mandatory)*

- **FR-001**: Không tính số mới (AD-22). Độ dài thanh người mới là tỷ lệ vẽ so với tỷ lệ lớn nhất; chấm lollipop và đoạn cơ cấu dùng nguyên `share.value`.
- **FR-002**: Biểu đồ chỉ để nhìn (`aria-hidden`); số đọc được là chữ của dòng và bảng số.
- **FR-003**: Bảng số là ô số theo thiết kế như danh sách `ol`; bộ quét DEC-6 của #148 miễn `table`.

## Success Criteria *(mandatory)*

- **SC-001**: `npx vitest run` xanh; lint, `tsc --noEmit` sạch.
