# Feature Specification: Chức danh gõ vào thành một vai trò, và màn ghi vai trò đã dùng

**Feature Branch**: `gh-111-ho-so-ky-nang`

**Created**: 2026-11-16

**Status**: Implemented, chờ merge.

**Input**: GitHub issue [#150](https://github.com/Dyuedu/HaiDoIT/issues/150) — Map a typed job title to a role and show which role was used. Phục vụ story #111 (US-A2), AC 1 và 2. Phép 6 (`RuleClassifier`, `haido_core/domain/classify.py`).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Gõ chức danh, thấy vai trò Hải Đồ dùng (Priority: P1)

Một sinh viên mở hồ sơ kỹ năng, gõ "Lập trình viên Java" và bấm tìm. Màn ghi "Hải Đồ dùng vai trò Backend" và ô Vai trò chọn sẵn Backend. Họ đổi sang vai trò khác được.

**Why this priority**: AC 1, 2 của #150; AC 1 của #111.

**Independent Test**: `tests/api/test_fr18_role_for_title.py`, `web/tests/fr18-role-for-title.test.tsx`.

**Acceptance Scenarios**:

1. **Given** chức danh "Java Backend Developer" hoặc "Lập trình viên Java", **When** gọi `GET /api/v1/role-for-title?title=…`, **Then** trả `{"data": {"status": "matched", "role": "backend"}}`. Phép 6 chỉ nhận chức danh, không nhận mô tả. (AC 1)
2. **Given** chức danh khớp, **When** màn nhận kết quả, **Then** màn ghi tên vai trò đã dùng (nhãn tiếng Việt), ô Vai trò chọn vai trò đó, và hồ sơ kỹ năng tải số của vai trò đó. (AC 1)
3. **Given** màn đã có vai trò, **When** người dùng chọn vai trò khác trong ô Vai trò, **Then** hồ sơ tải lại số của vai trò mới. (AC 2)

### User Story 2 - Chức danh không khớp vai trò IT nào (Priority: P1)

**Acceptance Scenarios**:

1. **Given** "Kế toán" (phép 6 ra `không thuộc IT`), **When** gọi, **Then** `{"status": "not_it", "role": null}`. (AC 3)
2. **Given** "Developer", "Kỹ sư phần mềm" (phép 6 ra `Other`), **When** gọi, **Then** `{"status": "generic", "role": null}`: chức danh IT nhưng không chỉ một vai trò. (AC 3)
3. **Given** `not_it` hoặc `generic`, **When** màn nhận kết quả, **Then** màn nói chức danh không khớp vai trò IT nào, hiện danh sách vai trò để chọn, và không hiện con số nào (không tỷ lệ, không n). (AC 3)
4. **Given** chức danh rỗng, chỉ có khoảng trắng, hoặc dài hơn 120 ký tự, **When** gọi, **Then** 422 `invalid_query`; màn không gọi API khi ô trống.

### Edge Cases

- Response không chứa số nên không dùng Envelope (AD-17 chỉ áp cho response có số), như `GET /api/v1/skills`.
- Không ghi chức danh vào log hay response (DoD dòng 9 áp cho văn bản JD; chức danh người dùng gõ xử lý cùng cách).
- Nhãn phép 6 đổi sang mã vai trò qua `report_as` của `config/classify.toml` rồi `[labels.role]` của `config/rules.toml`, đúng cách `aggregate` làm, để vai trò của màn trùng vai trò của số liệu.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `GET /api/v1/role-for-title?title=` trả `{data: {status, role}}`; `status` ∈ `matched`, `generic`, `not_it`.
- **FR-002**: `role` là mã của `config/rules.toml` khi `matched`, `null` khi không.
- **FR-003**: Màn gọi qua proxy `/api/*`; kết quả không khớp không hiện số.

## Success Criteria *(mandatory)*

- **SC-001**: `uv run pytest tests/api -q` và `cd web && npx vitest run` xanh.

## Assumptions

- Vai trò `other` ("Vai trò khác") không phải đích của ô chức danh; người dùng vẫn chọn được nó trong ô Vai trò.
