# Feature Specification: Vai trò nào dùng một kỹ năng

**Feature Branch**: `gh-113-vai-tro-dung-ky-nang`

**Created**: 2026-11-17

**Status**: Implemented, chờ merge. 2026-11-19 (#324): câu chữ trên màn viết lại bằng tiếng Việt dễ hiểu (bỏ nhãn `n = `, "snapshot"); số và hành vi không đổi.

**Input**: GitHub issue [#169](https://github.com/Dyuedu/HaiDoIT/issues/169) — Show which roles use a skill. Phục vụ story #113 (US-A4), AC 2, 3, 5. Hình dữ liệu và fixture của #166 (`GET /api/v1/skill-roles?skill=`, `web/lib/skill-roles.ts`); số thật là #168. Chỗ đặt màn: mục mới trên `/insights` (người dùng chọn 17/11/2026).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Thấy vai trò nào nhắc kỹ năng mình có, nhiều hay ít (Priority: P1)

Một sinh viên biết Python mở `/insights`, chọn Python ở mục "Kỹ năng của bạn dùng ở vai trò nào". Màn liệt kê từng vai trò theo thứ tự API gửi, mỗi dòng một câu như "77,6% tin AI/ML mới vào nghề nhắc tới Python", kèm n. Chạm một vai trò thì mở hồ sơ kỹ năng của vai trò đó ở cấp mới vào nghề.

**Why this priority**: AC 1, 2 của #169; AC 2, 3, 5 của #113.

**Independent Test**: `web/tests/fr09-vai-tro-dung-ky-nang.test.tsx`.

**Acceptance Scenarios**:

1. **Given** `skill=python`, **When** mở `/insights?skill=python`, **Then** danh sách có một dòng mỗi vai trò, đúng thứ tự `data.rows`; web không sắp lại (AD-22).
2. **Given** dòng có tỷ lệ, **When** xem, **Then** dòng ghi tỷ lệ ("77,6%") ở ô số riêng, liền với câu "tin AI/ML cho người mới có nhắc tới Python", và "tính trên 501 tin" (câu chữ theo #324) là cỡ mẫu của phép đo (`n_by_measure.skill_count`). (AC 1 của #169)
3. **Given** dòng `null_data`, **When** xem, **Then** ghi "Mới có 4 tin, cần ít nhất 30" (câu chữ theo #324) với 4 là `skill_count` và 30 là `meta.thresholds.min_sample`, không có dấu %. (AC 3 của #113)
4. **Given** một dòng, **When** chạm, **Then** đi tới `/ho-so-ky-nang?role=<vai trò>&level=<data.level>` (#111). (AC 2 của #169)
5. **Given** API trả 404 `unknown_cell` (kỹ năng chưa có số, hoặc production trước #168), **When** chọn kỹ năng, **Then** thông báo lỗi, không có "Thử lại", không có danh sách. Mạng hỏng thì có "Thử lại".
6. **Given** danh sách, **When** đọc khung "Nguồn và lưu ý", **Then** có ngày snapshot, nguồn, lưu ý độ phủ, và bộ lọc ghi "Mới vào nghề".

### Edge Cases

- Câu không chứa chữ số ngoài ô số (DEC-6): tỷ lệ và n đứng ở `span` riêng.
- Điện thoại 360px: tên vai trò và ô số xếp chồng, không cuộn ngang.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Mục "Kỹ năng của bạn dùng ở vai trò nào" trên `/insights`, dưới "Cửa vào cho người mới".
- **FR-002**: Số đọc từ `skill-roles` qua proxy `/api/*`; web không tính, không sắp xếp (AD-22).
- **FR-003**: Mỗi dòng là liên kết tới hồ sơ kỹ năng, cao tối thiểu 44px.
- **FR-004**: Kỹ năng đã chọn nằm trong URL (`?skill=`) để chia sẻ được.

## Success Criteria *(mandatory)*

- **SC-001**: `cd web && npx vitest run` xanh; `npx tsc --noEmit`, `npm run lint`, `npm run build` sạch.
- **SC-002**: Chrome headless 360px: không cuộn ngang, ô bấm ≥ 44px.

## Assumptions

- Production trả 404 `unknown_cell` cho tới khi #168 có số thật (compose prod đặt `stat`, #166). Màn hiện thông báo đó, không hiện số giả.
