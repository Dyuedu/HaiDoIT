# Implementation Plan: Chức danh gõ vào thành một vai trò

**Branch**: `gh-111-ho-so-ky-nang` | **Date**: 2026-11-16 | **Spec**: [spec.md](spec.md)

## Summary

Route mới `GET /api/v1/role-for-title` đưa chức danh vào phép 6 (`RuleClassifier.classify` với `PostingFacts` chỉ có `title`), đổi nhãn sang mã vai trò như `aggregate`, trả `matched` / `generic` / `not_it`. Màn hồ sơ kỹ năng có ô chức danh gọi route này.

## Technical Context

**Language/Version**: Python 3.13 + FastAPI; TypeScript, Next.js 16, React 19

**Testing**: `uv run pytest tests/api/test_fr18_role_for_title.py -q`; `cd web && npx vitest run tests/fr18-role-for-title.test.tsx`

**Constraints**: AD-2 (dùng phép 6, không cài lại), AD-5 (route không tính), AD-17 (response không số thì không Envelope).

## Project Structure

```text
haido_api/schemas/roles.py                         # mới: RoleForTitleData, RoleForTitleResponse
haido_api/routes/roles.py                          # mới: GET /api/v1/role-for-title
haido_api/main.py                                  # include_router
tests/api/test_fr18_role_for_title.py              # mới
tests/api/test_ad17_routes.py                      # NUMBERLESS_ROUTES thêm route mới
tests/api/test_ad17_ordinal_allowlist.py           # quét router mới
docs/api/openapi.json, docs/api/envelope-meta.md   # sinh lại, mô tả route
web/lib/role-for-title.ts                          # mới: fetchRoleForTitle
web/app/components/skill-profile/title-search.tsx  # mới: ô chức danh, thông báo không khớp, danh sách vai trò
web/tests/fr18-role-for-title.test.tsx             # mới
```

**Structure Decision**: Route riêng `roles.py` vì không phải số liệu thị trường. Bộ phân loại dựng một lần (`functools.cache`), cấu hình đọc từ `config/classify.toml`.

## Complexity Tracking

- `haido_api/main.py` thuộc #2 và các issue route trước (chỉ thêm một `include_router`).
