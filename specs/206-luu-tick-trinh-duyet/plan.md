# Implementation Plan: Lưu kỹ năng đã tick trong trình duyệt

**Branch**: `gh-111-ho-so-ky-nang` | **Date**: 2026-11-16 | **Spec**: [spec.md](spec.md)

## Summary

`SkillProfileScreen` đọc hồ sơ bằng `useSyncExternalStore` qua `web/lib/profile-store.ts` (server và lần hydrate đầu thấy hồ sơ rỗng, nên HTML không lệch), và gọi `saveProfile()` (bọc `writeProfile()`) mỗi lần tick, bỏ tick, đổi vai trò hay cấp. Bộ nhớ bị chặn thì hồ sơ vẫn đổi trong phiên. Không sửa `haido-keys.ts`.

## Technical Context

**Language/Version**: TypeScript, React 19

**Testing**: `cd web && npx vitest run tests/fr14-luu-tick-trinh-duyet.test.tsx`; cổng `tools/gates/check_gates.py` (AD-23).

**Constraints**: AD-23 (danh sách khóa đóng), AD-22 (trần 200 mã).

## Project Structure

```text
web/lib/profile-store.ts                                # mới: hồ sơ cho useSyncExternalStore (bọc readProfile/writeProfile)
web/app/components/skill-profile/skill-profile-screen.tsx  # đọc/ghi hồ sơ
web/tests/fr14-luu-tick-trinh-duyet.test.tsx               # mới
```

**Structure Decision**: Một store nhỏ thay cho đọc trong `useEffect` (lint `react-hooks/set-state-in-effect` chặn `setState` đồng bộ trong effect). Store không gọi `localStorage`, nên cổng AD-23 vẫn giữ một module duy nhất.

## Complexity Tracking

Không có.
