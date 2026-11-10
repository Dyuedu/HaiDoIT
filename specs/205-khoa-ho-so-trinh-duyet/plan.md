# Implementation Plan: Khóa hồ sơ trình duyệt và danh sách kỹ năng mồi

**Branch**: `gh-205-khoa-ho-so` | **Date**: 2026-11-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification từ `specs/205-khoa-ho-so-trinh-duyet/spec.md`

## Summary

Chốt hợp đồng biên trình duyệt (AD-23) thành code: module `web/lib/haido-keys.ts` có danh sách khóa đóng, đọc/ghi hồ sơ đã chuẩn hóa, và xóa theo tiền tố. Chốt định dạng mã kỹ năng ở cả Python và TypeScript. Thêm danh sách kỹ năng mồi ở `haido_core/vocab/skills_seed.json` và route `GET /api/v1/skills` để web đọc qua proxy `/api`.

## Technical Context

**Language/Version**: Python 3.13, FastAPI 0.162, Pydantic 2.14; TypeScript, Next.js 16, Vitest

**Primary Dependencies**: Không thêm gói.

**Storage**: `localStorage` của trình duyệt. Không đổi cơ sở dữ liệu.

**Testing**: `uv run pytest tests/core/test_fr13_skill_seed.py tests/api`; `cd web && npx vitest run tests/ad23-haido-keys.test.ts`

**Target Platform**: Web trên máy tính và điện thoại; API trong project `haido-prod`.

**Constraints**: Chỉ `haido-keys.ts` được chạm `localStorage` (cổng AD-23). Web không cộng, chia hay đếm trên mã kỹ năng (AD-22). Image web chỉ chép `web/`, nên danh sách mồi đi qua API.

**Scale/Scope**: 3 khóa, 100 kỹ năng mồi, 1 route đọc.

## Constitution Check

- AD-23: khóa có tiền tố `haido:`, khai trong một module, xóa theo tiền tố, mã phiên nằm trong danh sách.
- AD-22: module chỉ lưu và lọc mã, không tính toán.
- AD-17: route không có số nên không dùng Envelope; test AD-17 khai ngoại lệ tường minh và kiểm không có số.
- Không viết spec vào `_bmad-output/`.

## Project Structure

### Documentation (this feature)

```text
specs/205-khoa-ho-so-trinh-duyet/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── tasks.md
└── tdd.md
```

### Source Code (repository root)

```text
haido_core/vocab/skills.py
haido_core/vocab/skills_seed.json
haido_api/routes/skills.py
haido_api/schemas/skills.py
haido_api/main.py
docs/api/openapi.json
web/lib/haido-keys.ts
tests/core/test_fr13_skill_seed.py
tests/api/test_fr13_skills_route.py
tests/api/test_ad17_routes.py
web/tests/ad23-haido-keys.test.ts
```

**Structure Decision**: Một khóa hồ sơ thay cho mỗi trường một khóa, để vai trò, cấp bậc và kỹ năng không lệch nhau và có trường `v` để chuyển đổi về sau. Danh sách mồi có một nguồn duy nhất trong `haido_core`, web đọc qua API, để #96 thay file mà không đụng web.

## Complexity Tracking

`tests/api/test_ad17_routes.py` là test của #2 (chưa có `specs/`). Nó thêm `NUMBERLESS_ROUTES` để route không có số không bị bắt dùng Envelope, nhưng vẫn bị kiểm là không có số.
