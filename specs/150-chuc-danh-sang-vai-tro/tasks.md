# Tasks: Chức danh gõ vào thành một vai trò

**Input**: `specs/150-chuc-danh-sang-vai-tro/`

**Tests**: Viết trước theo `tdd.md`.

## Phase 1: Test

- [x] T001 Test route: khớp, `generic`, `not_it`, chức danh rỗng/dài 422, response không số, trong `tests/api/test_fr18_role_for_title.py`
- [x] T002 Test màn: chức danh khớp ghi vai trò đã dùng và tải số; đổi vai trò; không khớp nói rõ, hiện danh sách vai trò, không số, trong `web/tests/fr18-role-for-title.test.tsx`

## Phase 2: Implementation

- [x] T003 `haido_api/schemas/roles.py`, `haido_api/routes/roles.py`, `haido_api/main.py`
- [x] T004 `NUMBERLESS_ROUTES`, quét router trong test Ordinal, OpenAPI, `envelope-meta.md`
- [x] T005 `web/lib/role-for-title.ts`
- [x] T006 `title-search.tsx` và nối vào màn hồ sơ kỹ năng (#152)
