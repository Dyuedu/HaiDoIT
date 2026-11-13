# Implementation Plan: Màn người mới và lối sang hồ sơ kỹ năng

**Branch**: `gh-147-man-nguoi-moi` | **Date**: 2026-11-12 | **Spec**: [spec.md](spec.md)

## Summary

Thay trang giữ chỗ `/insights` bằng mục "Cửa vào cho người mới": client component gọi `fetchNewcomerRoles`, dựng view bằng `buildNewcomerView`, hiện danh sách liên kết và khung "Nguồn và lưu ý" (dùng lại `SnapshotCaption`, `LoadError` của Bản đồ). Thêm trang giữ chỗ `/ho-so-ky-nang` đọc `searchParams` (Next 16: `Promise`).

## Technical Context

**Language/Version**: TypeScript, Next.js 16, React 19, Tailwind 4, Vitest + Testing Library

**Primary Dependencies**: Không thêm gói.

**Testing**: `cd web && npx vitest run tests/fr37-newcomer-list.test.tsx`; toàn bộ `npx vitest run`, `npx tsc --noEmit`, `npm run lint`, `npm run build`; Chrome headless ở 360px và 1280px.

**Constraints**: AD-22, AD-17, DEC-6, DoD 360px và bàn phím.

## Project Structure

```text
web/lib/city-shares.ts                         # export các hàm kiểm hợp đồng (isRecord, isMeta, readErrorBody, …), không đổi hành vi
web/lib/newcomer-roles.ts                      # fetchNewcomerRoles, kiểm envelope
web/lib/newcomer-roles-view.ts                 # mới: buildNewcomerView, skillProfileHref
web/app/components/insights/newcomer-list.tsx  # mới
web/app/components/insights/newcomer-screen.tsx# mới
web/app/insights/page.tsx                      # mục người mới
web/app/ho-so-ky-nang/page.tsx                 # mới: trang giữ chỗ
web/tests/fr37-newcomer-list.test.tsx          # mới
```

**Structure Decision**: Dùng lại hàm kiểm `Meta` và lỗi của `city-shares.ts` bằng cách export thay vì chép, để hai màn cùng một luật đọc envelope. View model riêng (`newcomer-roles-view.ts`) như `city-shares-view.ts`, để component chỉ render chuỗi.

## Complexity Tracking

- `web/lib/city-shares.ts` thuộc #144, #163, #280, #285 (có `specs/`) và #46 (không có): chỉ thêm `export`, thêm đợt TDD cho các issue có `specs/`.
- `web/app/insights/page.tsx` thuộc #1 (không có `specs/`): ghi trong mô tả PR.
