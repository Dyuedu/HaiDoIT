# Implementation Plan: Mở lộ trình học từ một kỹ năng còn thiếu

**Branch**: `gh-111-ho-so-ky-nang` | **Date**: 2026-11-16 | **Spec**: [spec.md](spec.md)

## Summary

Dòng kỹ năng chưa tick có liên kết `learningPathHref(role, level, skill)` tới `/co-van`. Trang `/co-van` thành trang giữ chỗ đọc `searchParams`: gọi tên vai trò, cấp, kỹ năng (tên lấy từ `GET /api/v1/skills` phía trình duyệt), nói lộ trình có ở sprint sau.

## Technical Context

**Language/Version**: TypeScript, Next.js 16, React 19

**Testing**: `cd web && npx vitest run tests/fr22-mo-lo-trinh-tu-ky-nang.test.tsx`

**Constraints**: DEC-6 (câu không số), FR-25 (không khuyên bỏ qua kỹ năng).

## Project Structure

```text
web/lib/skill-profile-view.ts                        # learningPathHref
web/app/components/skill-profile/skill-list.tsx      # liên kết của dòng chưa tick
web/app/co-van/page.tsx                              # trang giữ chỗ đọc role, level, skill
web/app/components/advisor/path-placeholder.tsx      # mới: gọi tên kỹ năng (client, đọc /api/v1/skills)
web/tests/fr22-mo-lo-trinh-tu-ky-nang.test.tsx       # mới
```

**Structure Decision**: Tên kỹ năng lấy qua API từ trình duyệt như màn hồ sơ, không import file JSON của Python vào web.

## Complexity Tracking

- `web/app/co-van/page.tsx` thuộc #1 (không có `specs/`): ghi trong mô tả PR.

## Thay đổi sau merge (2026-11-25, #217)

`web/app/co-van/page.tsx` thành màn lộ trình; `web/app/components/advisor/path-placeholder.tsx` bị xóa; `learningPathHref` nhận `skill` tùy chọn. Chi tiết: `specs/217-man-lo-trinh/plan.md`.
