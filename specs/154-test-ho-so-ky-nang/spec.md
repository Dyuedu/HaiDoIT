# Feature Specification: Test hồ sơ kỹ năng theo AC của #111

**Feature Branch**: `gh-111-ho-so-ky-nang`

**Created**: 2026-11-16

**Status**: Implemented, chờ merge.

**Input**: GitHub issue [#154](https://github.com/Dyuedu/HaiDoIT/issues/154) — Test the skill profile. Phục vụ story #111 (US-A2).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Mỗi AC của #111 có một test mang mã FR (Priority: P1)

Người review mở một file và thấy bảy test, mỗi test một AC của #111, tên test có mã FR mà nó giữ. Test chạy trên màn thật (`SkillProfileScreen`) với `fetch` thay bằng response của API giả.

**Why this priority**: AC 1, 2 của #154.

**Independent Test**: `web/tests/fr18-fr19-us-a2-ac.test.tsx`.

**Acceptance Scenarios**:

1. **Given** file test, **When** đọc tên test, **Then** có đúng bảy test bắt đầu bằng `AC1` … `AC7` và mỗi tên có một mã `FR-` (FR-18, FR-19, FR-13, FR-14, FR-22). (AC 2)
2. **Given** bảy AC của #111, **When** đối chiếu bảng dưới, **Then** mỗi AC có một test. (AC 1)

| AC của #111 | Test | Mã |
|---|---|---|
| 1. Chức danh → một vai trò, màn ghi vai trò, đổi được | `AC1 FR-18 …` | FR-18 |
| 2. Không khớp: nói rõ, danh sách vai trò, không số | `AC2 FR-18 …` | FR-18 |
| 3. Không chọn cấp → `entry` (#134), đổi được | `AC3 FR-18 …` | FR-18 |
| 4. ≥ 30 tin: tỷ lệ và nhóm, theo tỷ lệ | `AC4 FR-19 …` | FR-19 |
| 5. < 30: gọi tên ô rộng hơn và n; không ô nào đủ thì "chưa đủ dữ liệu" | `AC5 FR-19 …` | FR-19 |
| 6. Kỹ năng đã lưu được tick, đếm core | `AC6 FR-14 …` | FR-14, AD-22 |
| 7. Chạm kỹ năng chưa có mở lộ trình ở kỹ năng đó | `AC7 FR-22 …` | FR-22 |

### Edge Cases

- Một test kiểm tên các test trong file (đếm bảy, mỗi tên có `FR-`), để thêm hay đổi tên test không làm mất một AC.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Test chạy màn thật, không mock component con.
- **FR-002**: Dữ liệu là fixture sinh từ API giả, đã khóa bằng `tests/api/test_ad17_web_fixtures.py`.

## Success Criteria *(mandatory)*

- **SC-001**: `cd web && npx vitest run tests/fr18-fr19-us-a2-ac.test.tsx` xanh.

## Assumptions

- Test chi tiết từng task nằm ở file riêng của task (#149, #150, #152, #153, #206, #207); file này là bản đồ AC.
