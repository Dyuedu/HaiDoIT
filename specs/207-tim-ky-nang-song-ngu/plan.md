# Implementation Plan: Tìm kỹ năng bằng tiếng Anh và tiếng Việt

**Branch**: `gh-111-ho-so-ky-nang` | **Date**: 2026-11-16 | **Spec**: [spec.md](spec.md)

## Summary

`web/lib/vocab.ts`: đọc `GET /api/v1/skills`, `foldText` (cùng luật `fold` của Python), `searchSkills`. Component `skill-search.tsx` trên màn hồ sơ kỹ năng: ô tìm, tối đa 8 kết quả là checkbox, câu "không có kết quả" qua `role="status"`.

## Technical Context

**Language/Version**: TypeScript, React 19

**Testing**: `cd web && npx vitest run tests/fr13-tim-ky-nang-song-ngu.test.tsx`

**Constraints**: AD-22 (chỉ lọc, không đếm), FR-13.

## Project Structure

```text
web/lib/vocab.ts                                      # mới: fetchSkills, foldText, searchSkills
web/app/components/skill-profile/skill-search.tsx     # mới
web/tests/fr13-tim-ky-nang-song-ngu.test.tsx          # mới
web/tests/fixtures/skills.json                        # mới, response của GET /api/v1/skills
```

**Structure Decision**: Không thêm Fuse.js; luật bỏ dấu viết lại vài dòng theo `fold` của repo, để web và API cùng một luật.

## Complexity Tracking

Không có.
