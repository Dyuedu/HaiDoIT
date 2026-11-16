# Feature Specification: Tìm kỹ năng bằng tiếng Anh và tiếng Việt

**Feature Branch**: `gh-111-ho-so-ky-nang`

**Created**: 2026-11-16

**Status**: Implemented, chờ merge.

**Input**: GitHub issue [#207](https://github.com/Dyuedu/HaiDoIT/issues/207) — Search the skill list in English and Vietnamese. Serves #120; dùng chung cho #113 (#167 gộp vào đây theo re-plan 16/11). Danh sách là `GET /api/v1/skills` (danh sách mồi của #205; bộ từ vựng v1 là #96, chưa duyệt).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Gõ tên kỹ năng tiếng Việt hay tiếng Anh, tick được (Priority: P1)

Một sinh viên gõ "học máy" vào ô tìm kỹ năng trên hồ sơ kỹ năng. Danh sách gợi ý có "Học máy (Machine Learning)". Họ tick nó, và nó vào hồ sơ.

**Why this priority**: AC 1, 2 của #207.

**Independent Test**: `web/tests/fr13-tim-ky-nang-song-ngu.test.tsx`.

**Acceptance Scenarios**:

1. **Given** danh sách kỹ năng, **When** gõ "học máy", **Then** kết quả có Machine Learning. (AC 1)
2. **Given** gõ không dấu "hoc may", chữ hoa "HỌC MÁY", hay tiếng Anh "machine", **When** tìm, **Then** vẫn có Machine Learning. Bỏ dấu theo cùng luật `fold` của `haido_core/domain/posting_text.py` (chữ thường, bỏ dấu, `đ` → `d`).
3. **Given** gõ bí danh "ml" hoặc "reactjs", **When** tìm, **Then** có Machine Learning, React.
4. **Given** kết quả, **When** tick Machine Learning, **Then** mã `machine_learning` vào hồ sơ (lưu theo #206), và ô của nó hiện đã tick. (AC 2)
5. **Given** gõ một chuỗi không khớp kỹ năng nào, **When** tìm, **Then** màn ghi "Không có kỹ năng nào khớp" qua vùng `role="status"`.
6. **Given** ô trống, **When** xem, **Then** không hiện danh sách gợi ý.
7. **Given** nhiều kết quả, **When** tìm, **Then** tối đa 8 kết quả; khớp đầu tên đứng trước khớp giữa tên.

### Edge Cases

- `GET /api/v1/skills` lỗi: ô tìm báo không tải được danh sách kỹ năng; phần còn lại của màn vẫn dùng được.
- Đây là lọc và hiện trên danh sách, không phải số học trên mã kỹ năng (AD-22 cho phép).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Tìm trên `name_en`, `name_vi`, `aliases`, đã bỏ dấu và chữ thường.
- **FR-002**: Mỗi kết quả là một checkbox gốc có nhãn "Tên tiếng Việt (Tên tiếng Anh)" khi hai tên khác nhau.
- **FR-003**: Hàm tìm nằm ở `web/lib/vocab.ts` để #113 dùng lại.

## Success Criteria *(mandatory)*

- **SC-001**: `cd web && npx vitest run tests/fr13-tim-ky-nang-song-ngu.test.tsx` xanh.

## Assumptions

- Tìm chạy ở trình duyệt trên danh sách ~225 kỹ năng; không gọi API mỗi lần gõ.
