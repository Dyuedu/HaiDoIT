# Feature Specification: Test "vai trò nào dùng kỹ năng" theo AC của #113

**Feature Branch**: `gh-113-vai-tro-dung-ky-nang`

**Created**: 2026-11-17

**Status**: Implemented, chờ merge. 2026-11-19 (#324): câu chữ trên màn viết lại bằng tiếng Việt dễ hiểu (bỏ nhãn `n = `, "snapshot"); số và hành vi không đổi.

**Input**: GitHub issue [#170](https://github.com/Dyuedu/HaiDoIT/issues/170) — Test which roles use a skill. Phục vụ story #113 (US-A4).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Mỗi AC của #113 có một test mang mã FR (Priority: P1)

Người review mở một file và thấy năm test, mỗi test một AC của #113, tên test có mã FR. Test chạy trang `/insights` thật với `fetch` thay bằng response của API giả.

**Why this priority**: AC 1, 2 của #170.

**Independent Test**: `web/tests/fr09-fr13-us-a4-ac.test.tsx`.

**Acceptance Scenarios**:

1. **Given** file test, **When** đọc tên test, **Then** có đúng năm test `AC1` … `AC5`, mỗi tên có một mã `FR-`. (AC 2)
2. **Given** năm AC của #113, **When** đối chiếu bảng, **Then** mỗi AC có một test. (AC 1)

| AC của #113 | Test | Mã |
|---|---|---|
| 1. Gõ kỹ năng tiếng Anh hoặc tiếng Việt khớp một kỹ năng, màn ghi kỹ năng đó | `AC1 FR-13 …` | FR-13 |
| 2. Mỗi vai trò có tỷ lệ tin entry-level nhắc kỹ năng, theo tỷ lệ, bằng một câu thường | `AC2 FR-09 …` | FR-09, AD-22 |
| 3. Vai trò dưới 30 tin entry-level đọc được kỹ năng ghi "Mới có X tin, cần ít nhất 30" (câu chữ theo #324, X là `skill_count`) | `AC3 FR-09 …` | FR-09 |
| 4. Kỹ năng không tin nào nhắc thì nói như vậy | `AC4 FR-09 …` | FR-09 |
| 5. Chạm vai trò mở hồ sơ kỹ năng (#111) | `AC5 FR-18 …` | FR-18 |

### Edge Cases

- Một test kiểm tên các test trong file (đúng năm `AC`, mỗi tên có `FR-`).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Test chạy trang thật, không mock component con.
- **FR-002**: Dữ liệu là fixture `skill-roles-*.json` của #166, đã khóa bằng `tests/api/test_ad17_web_fixtures.py`.

## Success Criteria *(mandatory)*

- **SC-001**: `cd web && npx vitest run tests/fr09-fr13-us-a4-ac.test.tsx` xanh.

## Assumptions

- Test chi tiết nằm ở file của #167 và #169; file này là bản đồ AC, như #154 với #111.
