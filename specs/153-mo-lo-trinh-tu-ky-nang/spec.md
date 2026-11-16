# Feature Specification: Mở lộ trình học từ một kỹ năng còn thiếu

**Feature Branch**: `gh-111-ho-so-ky-nang`

**Created**: 2026-11-16

**Status**: Implemented, chờ merge.

**Input**: GitHub issue [#153](https://github.com/Dyuedu/HaiDoIT/issues/153) — Open the learning path from a missing skill. Phục vụ story #111 (US-A2), AC 7. Màn lộ trình (#121, các task #213–#219) đã dời sang Sprint 4 trong lần re-plan 16/11.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Chạm kỹ năng chưa có để đi tới lộ trình ở đúng kỹ năng đó (Priority: P1)

Một sinh viên xem hồ sơ Backend · Mới vào nghề, thấy Spring Boot chưa được tick, chạm vào tên Spring Boot. Trang Cố vấn mở với vai trò, cấp và kỹ năng đó.

**Why this priority**: AC của #153; AC 7 của #111.

**Independent Test**: `web/tests/fr22-mo-lo-trinh-tu-ky-nang.test.tsx`.

**Acceptance Scenarios**:

1. **Given** kỹ năng chưa tick, **When** xem dòng, **Then** tên kỹ năng là liên kết tới `/co-van?role=backend&level=entry&skill=spring_boot`. (AC)
2. **Given** kỹ năng đã tick, **When** xem dòng, **Then** tên không phải liên kết tới lộ trình và dòng ghi "Đã có".
3. **Given** người dùng tick một kỹ năng, **When** dòng cập nhật, **Then** liên kết lộ trình của dòng đó biến mất; bỏ tick thì liên kết trở lại.
4. **Given** mở `/co-van?role=backend&level=entry&skill=spring_boot` khi #121 chưa có, **When** xem, **Then** tiêu đề gọi tên vai trò, trang gọi tên kỹ năng ("Spring Boot") và cấp, nói lộ trình học có ở sprint sau, có nút quay lại hồ sơ kỹ năng của vai trò và cấp đó. Câu không có chữ số (DEC-6).
5. **Given** mã vai trò hoặc mã kỹ năng lạ, **When** mở `/co-van`, **Then** không in mã như một tên.

### Edge Cases

- Mở `/co-van` không có tham số: giữ câu giới thiệu chung của Cố vấn.
- Sprint 4 (#121) thay trang giữ chỗ bằng lộ trình thật mà không đổi liên kết `learningPathHref`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `learningPathHref(role, level, skill)` trong `web/lib/skill-profile-view.ts` là nơi duy nhất dựng liên kết.
- **FR-002**: `/co-van` đọc `role`, `level`, `skill`; tên kỹ năng từ bộ từ vựng (`haido_core/vocab`), không từ mã.
- **FR-003**: Liên kết và nút cao tối thiểu 44px.

## Success Criteria *(mandatory)*

- **SC-001**: `cd web && npx vitest run tests/fr22-mo-lo-trinh-tu-ky-nang.test.tsx` xanh.

## Assumptions

- Người dùng đã chọn lối "liên kết + trang giữ chỗ" (16/11/2026) thay vì dựng màn lộ trình tối thiểu, để không lấn việc của #213–#219.
