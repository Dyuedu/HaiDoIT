# Implementation Plan: Test "vai trò nào dùng kỹ năng" theo AC của #113

**Branch**: `gh-113-vai-tro-dung-ky-nang` | **Date**: 2026-11-17 | **Spec**: [spec.md](spec.md)

## Summary

Một file test web, năm test theo năm AC của #113, cộng một test khóa tên. Dùng helper `web/tests/helpers/skill-roles.ts`.

## Technical Context

**Language/Version**: TypeScript, Vitest, Testing Library

**Testing**: `cd web && npx vitest run tests/fr09-fr13-us-a4-ac.test.tsx`

## Project Structure

```text
web/tests/fr09-fr13-us-a4-ac.test.tsx   # mới
web/tests/helpers/skill-roles.ts        # mới, dùng chung với test của #167, #169
```

**Structure Decision**: Như `web/tests/fr18-fr19-us-a2-ac.test.tsx` (#154).

## Complexity Tracking

Không có.
