# Feature Specification: Chọn một kỹ năng bằng tiếng Anh hoặc tiếng Việt

**Feature Branch**: `gh-113-vai-tro-dung-ky-nang`

**Created**: 2026-11-17

**Status**: Implemented, chờ merge.

**Input**: GitHub issue [#167](https://github.com/Dyuedu/HaiDoIT/issues/167) — Search skills in English and Vietnamese. Phục vụ story #113 (US-A4), AC 1 và 4. Hàm tìm song ngữ đã có ở #207 (`searchSkills` của `web/lib/vocab.ts`); cờ `mentioned` của #166.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Gõ tên kỹ năng, chọn đúng một kỹ năng, thấy màn đã dùng kỹ năng nào (Priority: P1)

Một sinh viên gõ "học máy" vào ô tìm của mục "Kỹ năng của bạn dùng ở vai trò nào", chọn "Học máy (Machine Learning)". Màn ghi rõ kỹ năng đã dùng rồi hiện các vai trò.

**Why this priority**: AC 1 của #167; AC 1 của #113.

**Independent Test**: `web/tests/fr13-chon-mot-ky-nang.test.tsx`.

**Acceptance Scenarios**:

1. **Given** danh sách kỹ năng, **When** gõ "học máy" (hoặc "hoc may", "machine", "ml"), **Then** kết quả có nút "Học máy (Machine Learning)". (AC 1)
2. **Given** kết quả, **When** chọn nút đó, **Then** màn gọi `skill-roles?skill=machine_learning`, ghi "Kỹ năng: Học máy (Machine Learning)" theo `data.skill` của API, URL thành `/insights?skill=machine_learning`, và nút đã chọn có `aria-pressed = true`. (AC 1)
3. **Given** hồ sơ trình duyệt có kỹ năng đã tick (#206), **When** mở mục, **Then** các kỹ năng đó hiện thành nút chọn nhanh "Kỹ năng trong hồ sơ của bạn".
4. **Given** mở `/insights?skill=python`, **When** trang tải, **Then** Python đã được chọn và danh sách hiện ngay. Mã sai định dạng trong URL thì coi như chưa chọn.
5. **Given** gõ chuỗi không khớp, **When** tìm, **Then** "Không có kỹ năng nào khớp" trong `role="status"`.

### User Story 2 - Kỹ năng không tin nào nhắc (Priority: P1)

**Acceptance Scenarios**:

1. **Given** `data.mentioned = false` (ABAP), **When** chọn, **Then** màn ghi "Chưa tin tuyển dụng hiện tại nào nhắc tới ABAP." và không hiện danh sách vai trò hay tỷ lệ 0%. (AC 2)
2. **Given** `mentioned = true` mà mọi dòng hiện bằng 0 (SAP: có tin ở cấp khác), **When** chọn, **Then** màn vẫn hiện danh sách, không ghi "chưa tin nào nhắc". Web không suy cờ này từ các dòng (AD-22).
3. **Given** `unknown_skill` (mã hợp lệ nhưng không có trong bộ từ vựng, ví dụ từ URL), **When** mở, **Then** thông báo của API, không "Thử lại".

### Edge Cases

- Danh sách kỹ năng không tải được: ô tìm báo lỗi; chọn nhanh từ hồ sơ và `?skill=` vẫn dùng được.
- Câu "chưa tin nào nhắc" có tên kỹ năng; tên có chữ số (ví dụ "Vue 3") không phải số liệu.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Tìm dùng lại `searchSkills` (#207); kết quả là nút chọn một, không phải ô tick.
- **FR-002**: Tên kỹ năng đã dùng lấy từ `data.skill` của `skill-roles`, không từ chuỗi người dùng gõ.
- **FR-003**: Câu "chưa tin nào nhắc" chỉ dựa vào `data.mentioned`.

## Success Criteria *(mandatory)*

- **SC-001**: `cd web && npx vitest run tests/fr13-chon-mot-ky-nang.test.tsx` xanh.

## Assumptions

- #167 từng được ghi là gộp vào #207 (re-plan 16/11). #207 làm phần tìm và tick cho hồ sơ; #167 làm phần chọn một kỹ năng cho #113 và câu "chưa tin nào nhắc", dùng lại hàm tìm của #207.
