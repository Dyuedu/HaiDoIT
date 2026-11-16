# Implementation Plan: Hồ sơ kỹ năng của một vai trò ở một cấp

**Branch**: `gh-111-ho-so-ky-nang` | **Date**: 2026-11-16 | **Spec**: [spec.md](spec.md)

## Summary

Thay trang giữ chỗ `/ho-so-ky-nang` bằng màn thật: server page đọc `searchParams`, client component `SkillProfileScreen` ghép ô chức danh (#150), ô Vai trò, ô Cấp bậc, danh sách kỹ năng có tick (#152, #153), ô tìm kỹ năng (#207), lưu hồ sơ (#206). Số đọc `skill-rates` với `have=`; tên kỹ năng đọc `GET /api/v1/skills`.

## Technical Context

**Language/Version**: TypeScript, Next.js 16, React 19, Tailwind 4, Vitest + Testing Library

**Primary Dependencies**: Không thêm gói.

**Testing**: `cd web && npx vitest run`; `npx tsc --noEmit`, `npm run lint`, `npm run build`; Chrome headless 360px.

**Constraints**: AD-17, AD-22, AD-23, DEC-6, FR-25, DoD 360px và bàn phím.

## Project Structure

```text
web/lib/profile-store.ts                                # mới: hồ sơ cho useSyncExternalStore (bọc readProfile/writeProfile)
web/lib/skill-rates.ts                                  # mới: kiểu, fetchSkillRates, kiểm envelope
web/lib/skill-profile-view.ts                           # mới: buildSkillProfileView, learningPathHref
web/lib/newcomer-roles-view.ts                          # sửa chú thích skillProfileHref (không còn giữ chỗ)
web/app/ho-so-ky-nang/page.tsx                          # thay trang giữ chỗ
web/app/components/skill-profile/skill-profile-screen.tsx  # mới
web/app/components/skill-profile/skill-list.tsx         # mới
web/tests/fr19-skill-profile.test.tsx                   # mới
web/tests/fr37-newcomer-list.test.tsx                   # bỏ test trang giữ chỗ (đã thay)
web/tests/helpers/skill-profile.ts                      # mới: thay fetch theo đường dẫn
web/tests/fixtures/skill-rates-*.json, skills.json      # mới, sinh từ API giả
```

**Structure Decision**: View model riêng như `newcomer-roles-view.ts`, để component chỉ render chuỗi. Dùng lại `FilterSelect`, `LoadError`, `SnapshotCaption`.

## Complexity Tracking

- `web/app/ho-so-ky-nang/page.tsx` và `web/tests/fr37-newcomer-list.test.tsx` thuộc #147/#148 (có `specs/`): thêm đợt TDD; FR-005 của #147 đã báo trước trang này sẽ bị thay.
- `web/lib/newcomer-roles-view.ts` thuộc #147: chỉ sửa chú thích.
