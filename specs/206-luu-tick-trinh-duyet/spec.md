# Feature Specification: Lưu kỹ năng đã tick trong trình duyệt

**Feature Branch**: `gh-111-ho-so-ky-nang`

**Created**: 2026-11-16

**Status**: Implemented, chờ merge.

**Input**: GitHub issue [#206](https://github.com/Dyuedu/HaiDoIT/issues/206) — Store the skill profile in the browser. Serves #120; trong re-plan 16/11 dùng cho #111 AC 6 (kỹ năng đã lưu được tick). Khóa và module của #205 (`web/lib/haido-keys.ts`, AD-23).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Mở lại trang, kỹ năng đã tick vẫn còn (Priority: P1)

Một sinh viên tick Java và SQL trên hồ sơ Backend, đóng tab, hôm sau mở lại cùng trình duyệt. Java và SQL vẫn được tick, và dòng đếm core tính cả hai.

**Why this priority**: AC của #206.

**Independent Test**: `web/tests/fr14-luu-tick-trinh-duyet.test.tsx`.

**Acceptance Scenarios**:

1. **Given** hồ sơ trống, **When** tick Java rồi gỡ màn và dựng lại (mở lại trang), **Then** Java vẫn được tick. (AC)
2. **Given** đã tick, **When** đọc `localStorage`, **Then** chỉ khóa `haido:profile` đổi, giá trị là JSON `{v: 1, role, level, skills}` của #205, `skills` giữ thứ tự tick.
3. **Given** đã tick Java, **When** bỏ tick, **Then** Java ra khỏi `skills` đã lưu.
4. **Given** đổi ô Vai trò hoặc Cấp bậc, **When** đọc hồ sơ đã lưu, **Then** `role`, `level` là giá trị mới (vai trò mục tiêu, FR-14); `skills` không đổi.
5. **Given** mở `/ho-so-ky-nang` không có `role` mà hồ sơ đã lưu có `role = backend`, **When** mở, **Then** màn dùng Backend.
6. **Given** trình duyệt chặn bộ nhớ (truy cập `localStorage` ném lỗi), **When** tick, **Then** màn không vỡ và ô vẫn tick trong phiên đó. Báo cho người dùng biết là việc của #210.

### Edge Cases

- Hồ sơ hỏng (JSON sai, sai phiên bản): `readProfile` của #205 trả hồ sơ rỗng; màn bắt đầu không có tick.
- Đã có 200 mã (trần AD-22): `writeProfile` cắt ở trần; màn không thêm mã thứ 201.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Mọi đọc ghi đi qua `readProfile`/`writeProfile` của `web/lib/haido-keys.ts`; không file nào khác gọi `localStorage` (cổng AD-23).
- **FR-002**: Ghi ngay khi tick, bỏ tick, đổi vai trò, đổi cấp.

## Success Criteria *(mandatory)*

- **SC-001**: `cd web && npx vitest run tests/fr14-luu-tick-trinh-duyet.test.tsx` xanh; cổng AD-23 pass.

## Assumptions

- Nút "Xóa hồ sơ" (FR-14) và thông báo khi bộ nhớ bị chặn (#210) không thuộc issue này.
