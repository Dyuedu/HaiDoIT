# Feature Specification: Hồ sơ kỹ năng của một vai trò ở một cấp

**Feature Branch**: `gh-111-ho-so-ky-nang`

**Created**: 2026-11-16

**Status**: Implemented, chờ merge.

**Input**: GitHub issue [#152](https://github.com/Dyuedu/HaiDoIT/issues/152) — Show the skill profile for a role and level. Phục vụ story #111 (US-A2), AC 3–6. Số giả của #149, số thật của #151. Cấp mặc định của #134 (DEC-8). Thay trang giữ chỗ `/ho-so-ky-nang` của #147.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Xem kỹ năng tin tuyển dụng đòi, ở cấp của mình (Priority: P1)

Một sinh viên chạm Backend trên danh sách người mới (#147), mở `/ho-so-ky-nang?role=backend&level=entry`. Màn hiện từng kỹ năng với tỷ lệ tin đòi nó và nhóm (cốt lõi, thường gặp, riêng của công ty), theo thứ tự API gửi. Họ đổi cấp được.

**Why this priority**: AC 1–3 của #152; AC 3–6 của #111.

**Independent Test**: `web/tests/fr19-skill-profile.test.tsx`.

**Acceptance Scenarios**:

1. **Given** URL không có `level`, **When** mở trang, **Then** ô Cấp bậc là "Mới vào nghề" (`entry`, #134) và màn gọi `skill-rates?level=entry`. (AC 1)
2. **Given** màn đã có số, **When** đổi ô Cấp bậc sang Intern, **Then** màn gọi `skill-rates?level=intern` và URL đổi theo. (AC 1)
3. **Given** ô đủ 30 tin, **When** xem, **Then** mỗi dòng có tên kỹ năng (tên tiếng Việt từ `GET /api/v1/skills`), tỷ lệ ("65,4%") và nhóm ("Cốt lõi"), đúng thứ tự `data.rows`; web không sắp lại (AD-22). (AC 2)
4. **Given** ô quay về (Backend · Intern), **When** xem, **Then** màn hiện nguyên văn `fallback_label` và n của ô đã dùng ("n = 157").
5. **Given** không ô nào đủ 30 (Data Engineer · Entry), **When** xem, **Then** mỗi dòng ghi "chưa đủ dữ liệu", không có dấu %, không tên nhóm, không dòng đếm core.
6. **Given** hồ sơ có `java`, `sql`, `git`, **When** xem Backend · Entry, **Then** ba dòng đó được tick, và dòng đếm ghi `have_core/core_size` do API trả ("3/6") kèm "kỹ năng cốt lõi bạn đã có". Web không đếm (AD-22). (AC 3)
7. **Given** API trả 404 `unknown_cell` (cấp không có ô), **When** mở, **Then** thông báo lỗi, không có nút "Thử lại", không có số. Mạng hỏng thì có "Thử lại".
8. **Given** envelope sai hợp đồng (`have` không phải bool, `have_core` lớn hơn `core_size` hoặc chỉ một trong hai là `null`, `rate` không phải `skill_rate`, thiếu ô; web không đếm lại dòng core, AD-22), **When** đọc, **Then** coi là không đọc được.

### Edge Cases

- Điện thoại 360px: không cuộn ngang; tên kỹ năng và ô số xếp chồng.
- Mã vai trò lạ trong URL: không in mã như tên; màn coi như chưa chọn vai trò.
- URL không có `role` mà hồ sơ trình duyệt có vai trò mục tiêu (#206): dùng vai trò đó.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `/ho-so-ky-nang` đọc `role`, `level` từ URL; `level` mặc định `entry`.
- **FR-002**: Số đọc từ `skill-rates` qua proxy `/api/*`, gửi hồ sơ bằng `have=` (AD-22).
- **FR-003**: Thứ tự dòng, cờ `have` và số đếm core lấy nguyên từ API.
- **FR-004**: Có khung "Nguồn và lưu ý" như màn Bản đồ và màn người mới.
- **FR-005**: Mô tả nhóm thường gặp là "nên học sau khi đã nắm các kỹ năng cốt lõi" (FR-25).

## Success Criteria *(mandatory)*

- **SC-001**: `cd web && npx vitest run` xanh; `npx tsc --noEmit`, `npm run lint`, `npm run build` sạch.
- **SC-002**: Chrome headless 360px: không cuộn ngang, ô tick và liên kết cao ≥ 44px.

## Assumptions

- Câu `fallback_label` do API viết (có chữ số n). Màn hiện nguyên văn như hợp đồng `envelope-meta.md`.
