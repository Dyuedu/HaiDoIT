# Implementation Plan: Vai trò nào dùng một kỹ năng

**Branch**: `gh-113-vai-tro-dung-ky-nang` | **Date**: 2026-11-17 | **Spec**: [spec.md](spec.md)

## Summary

Mục mới trên `/insights`: client component `SkillRolesScreen` gồm ô chọn một kỹ năng (#167), gọi `fetchSkillRoles` (#166), dựng view bằng `buildSkillRolesView`, hiện danh sách liên kết sang hồ sơ kỹ năng và khung "Nguồn và lưu ý". Kỹ năng đã chọn đồng bộ với `?skill=` của URL.

## Technical Context

**Language/Version**: TypeScript, Next.js 16, React 19, Tailwind 4, Vitest + Testing Library

**Primary Dependencies**: Không thêm gói.

**Testing**: `cd web && npx vitest run tests/fr09-vai-tro-dung-ky-nang.test.tsx`; toàn bộ `npx vitest run`, `npx tsc --noEmit`, `npm run lint`, `npm run build`; Chrome headless 360px và 1280px.

**Constraints**: AD-17, AD-22, DEC-6, DoD 360px và bàn phím.

## Project Structure

```text
web/lib/skill-roles-view.ts                        # mới: buildSkillRolesView
web/lib/location-search.ts                         # mới: đọc ?skill= bằng useSyncExternalStore (server: rỗng)
web/app/components/insights/skill-roles-screen.tsx # mới
web/app/components/insights/skill-roles-list.tsx   # mới
web/app/insights/page.tsx                          # thêm mục
web/tests/fr09-vai-tro-dung-ky-nang.test.tsx       # mới
web/tests/helpers/skill-roles.ts                   # mới: thay fetch cho /insights
```

**Structure Decision**: View model riêng như `newcomer-roles-view.ts`. Đọc URL bằng `useSyncExternalStore` (snapshot server rỗng) để `/insights` vẫn dựng tĩnh và không lệch HTML khi hydrate.

## Complexity Tracking

- `web/app/insights/page.tsx` thuộc #1 (không có `specs/`) và #147 (có): thêm đợt TDD cho #147.
