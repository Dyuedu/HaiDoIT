# Implementation Plan: Test hồ sơ kỹ năng theo AC của #111

**Branch**: `gh-111-ho-so-ky-nang` | **Date**: 2026-11-16 | **Spec**: [spec.md](spec.md)

## Summary

Một file test web, bảy test theo bảy AC của #111, cộng một test khóa tên. Dùng helper thay `fetch` theo đường dẫn (`web/tests/helpers/skill-profile.ts`).

## Technical Context

**Language/Version**: TypeScript, Vitest, Testing Library

**Testing**: `cd web && npx vitest run tests/fr18-fr19-us-a2-ac.test.tsx`

## Project Structure

```text
web/tests/fr18-fr19-us-a2-ac.test.tsx   # mới
web/tests/helpers/skill-profile.ts      # mới, dùng chung với test của #150, #152, #153, #206, #207
```

**Structure Decision**: Test khóa tên đọc chính file test bằng `node:fs` (môi trường Vitest có Node), không cần cấu hình reporter.

## Complexity Tracking

Không có.
