# Implementation Plan: Chọn một kỹ năng bằng tiếng Anh hoặc tiếng Việt

**Branch**: `gh-113-vai-tro-dung-ky-nang` | **Date**: 2026-11-17 | **Spec**: [spec.md](spec.md)

## Summary

Component `skill-picker.tsx`: ô tìm dùng `searchSkills` của #207, kết quả là nút chọn một (`aria-pressed`), cộng hàng chọn nhanh từ hồ sơ trình duyệt (#206). `SkillRolesScreen` (#169) ghi tên kỹ năng theo `data.skill` và câu "chưa tin nào nhắc" theo `data.mentioned`.

## Technical Context

**Language/Version**: TypeScript, React 19

**Testing**: `cd web && npx vitest run tests/fr13-chon-mot-ky-nang.test.tsx`

**Constraints**: AD-22 (không suy `mentioned`), FR-13.

## Project Structure

```text
web/app/components/insights/skill-picker.tsx       # mới
web/app/components/insights/skill-roles-screen.tsx # tên kỹ năng đã dùng, câu "chưa tin nào nhắc"
web/lib/skill-roles-view.ts                        # skillName, notMentionedText
web/tests/fr13-chon-mot-ky-nang.test.tsx           # mới
```

**Structure Decision**: Không dùng lại `SkillSearch` của hồ sơ (ô tick, nhiều kỹ năng); viết component chọn một nhưng dùng chung `searchSkills`, `fetchSkills`, `skillDisplayName`.

## Complexity Tracking

Không có.
