# Feature Specification: Màn người mới và lối sang hồ sơ kỹ năng

**Feature Branch**: `gh-147-man-nguoi-moi`

**Created**: 2026-11-12

**Status**: Implemented, chờ merge.

**Input**: GitHub issue [#147](https://github.com/Dyuedu/HaiDoIT/issues/147) — Show the newcomer list and open a role's skill profile. Phục vụ story #110 (US-A1). Hình dữ liệu của #144; số thật của #145, #146 (PR #290). Quy tắc câu không có số của DEC-6 (#132).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Xem vai trò nào còn tuyển người mới (Priority: P1)

Một sinh viên mở Insights và thấy mọi vai trò, mỗi dòng có số tin cho người mới (Intern, Fresher, Junior), tỷ lệ trong số tin của vai trò và n, theo thứ tự API gửi. Ngày snapshot, nguồn và lưu ý độ phủ nằm ở khung chú thích bên dưới.

**Why this priority**: AC 1, 2 của #147; là phần demo của #110.

**Independent Test**: `web/tests/fr37-newcomer-list.test.tsx`.

**Acceptance Scenarios**:

1. **Given** response của API giả, **When** mở `/insights`, **Then** danh sách có một dòng mỗi vai trò, nhãn tiếng Việt, đúng thứ tự `data.rows`; web không sắp xếp lại (AD-22).
2. **Given** vai trò đủ mẫu, **When** xem dòng, **Then** có "501 tin cho người mới", "57,1%", "n = 877".
3. **Given** vai trò dưới 30 tin (`null_data`), **When** xem dòng, **Then** ghi "chưa đủ dữ liệu (12/30)" thay cho tỷ lệ, không có dấu %, viền nét đứt hổ phách; dòng nằm sau các dòng có tỷ lệ vì API gửi như vậy. (AC 1)
4. **Given** `min_sample = 50` trong `meta.thresholds`, **When** xem dòng đó, **Then** ghi "(12/50)".
5. **Given** vai trò đủ mẫu mà không có tin entry-level (`devops`), hoặc không có tin nào (`other`), **When** xem, **Then** dòng ghi "0 tin cho người mới" và vẫn ở trong danh sách. (AC 2)
6. **Given** danh sách, **When** đọc khung "Nguồn và lưu ý", **Then** có ngày snapshot, nguồn và mọi lưu ý độ phủ.
7. **Given** API trả 404 `unknown_cell` kèm ngày, **When** mở trang, **Then** có thông báo lỗi, ngày snapshot, không có nút "Thử lại", không có danh sách.
8. **Given** mạng hỏng, **When** mở trang, **Then** báo "Không đọc được số liệu", bấm "Thử lại" thì tải lại được.
9. **Given** envelope sai hợp đồng (share không phải `level_share`, `cell_id` khác ô vai trò, thiếu ô, `shown` mà không có giá trị, `null_data` mà có giá trị, vai trò lặp, không có dòng, `levels` rỗng), **When** đọc, **Then** coi là không đọc được, không hiện số.

### User Story 2 - Chạm một vai trò để mở hồ sơ kỹ năng (Priority: P1)

**Why this priority**: AC 3 của #147.

**Acceptance Scenarios**:

1. **Given** danh sách, **When** chạm dòng AI/ML, **Then** đi tới `/ho-so-ky-nang?role=ai_ml&level=entry`.
2. **Given** #111 chưa có, **When** mở trang đó, **Then** tiêu đề gọi tên vai trò ("Hồ sơ kỹ năng: AI/ML"), ghi cấp "Mới vào nghề", và nói hồ sơ kỹ năng có ở sprint sau; có nút quay lại `/insights`.
3. **Given** mã vai trò lạ, **When** mở trang, **Then** không in mã như một tên, ghi "Không có vai trò này".

### User Story 3 - Câu không chứa số (DEC-6) (Priority: P1)

1. **Given** câu giới thiệu của mục người mới và câu của trang giữ chỗ, **When** kiểm, **Then** không có chữ số.

### Edge Cases

- Điện thoại 360px: tên vai trò và ô số xếp chồng, không cuộn ngang; từ `sm` thành hai cột.
- Snapshot `partial`: khung chú thích ghi nguồn lỗi như màn Bản đồ.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `/insights` có mục "Cửa vào cho người mới" gọi `GET /api/v1/newcomer-roles` phía trình duyệt qua proxy `/api/*`.
- **FR-002**: Số đọc từ `meta.cells` và `share`; web không tính lại, không sắp xếp lại (AD-22).
- **FR-003**: `null_data` ghi "chưa đủ dữ liệu (n/min_sample)"; ngưỡng lấy từ `meta.thresholds`.
- **FR-004**: Mỗi dòng là một liên kết tới `/ho-so-ky-nang?role=<mã>&level=entry`, cao tối thiểu 44px.
- **FR-005**: `/ho-so-ky-nang` là trang giữ chỗ tới khi #111 (#152) thay bằng hồ sơ thật.

## Success Criteria *(mandatory)*

- **SC-001**: `cd web && npx vitest run` xanh, có `tests/fr37-newcomer-list.test.tsx`.
- **SC-002**: `npx tsc --noEmit`, `npm run lint`, `npm run build` sạch.
- **SC-003**: Chrome headless ở 360px: không cuộn ngang, mọi dòng cao ≥ 44px; bấm dòng đầu sang trang giữ chỗ đúng vai trò.

## Assumptions

- Danh sách người mới là mục đầu của Insights (FR-37, EXPERIENCE.md màn 12). Bộ lọc vai trò của Insights (FR-40) chưa làm.
- Đường dẫn `/ho-so-ky-nang` là tạm; #152 có thể đổi, khi đó sửa `skillProfileHref` trong `web/lib/newcomer-roles-view.ts`.
