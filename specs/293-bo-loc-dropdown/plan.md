# Implementation Plan: Bộ lọc bản đồ chọn bằng dropdown

**Branch**: `gh-293-bo-loc-dropdown` | **Date**: 2026-11-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/293-bo-loc-dropdown/spec.md`

## Summary

Thay `RoleChips`, `LevelChips`, `YearsChips` bằng một component `FilterSelect` (nhãn hiện, `<select>` gốc, ghi chú nối `aria-describedby`). `map-screen.tsx` giữ nguyên luồng dữ liệu; chỉ đổi phần dựng điều khiển: một lưới ba ô, rồi cụm `ViewSwitch`.

## Technical Context

**Language/Version**: TypeScript 5, Next.js 16, React 19, Tailwind 4

**Primary Dependencies**: Vitest, Testing Library, user-event. Không thêm gói.

**Storage**: Không.

**Testing**: `cd web && npx vitest run`; kiểm bố cục bằng Edge headless (playwright-core) ở 1280×900 và 360×640.

**Constraints**: `<select>` gốc; không `aria-pressed` ở điều khiển mới; `min-h-target` (44px); vòng focus dùng chung `:focus-visible` của `globals.css`; không cuộn ngang ở 360px. Không đổi API, config; `labels.ts` chỉ thêm hằng `LEVEL_ENTRY_NOTE` (đợt 2).

## Constitution Check

- AD-17: số, caption, ghi chú mẫu nhỏ không đổi.
- DoD (#137): vùng bấm ≥ 44px, `:focus-visible`, bàn phím, không cuộn ngang ở 360px.

## Project Structure

### Documentation (this feature)

```text
specs/293-bo-loc-dropdown/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── tasks.md
└── tdd.md
```

### Source Code (repository root)

```text
web/app/components/map/filter-select.tsx     (mới)
web/app/components/map/map-screen.tsx
web/app/components/map/role-chips.tsx        (xóa)
web/app/components/map/level-chips.tsx       (xóa)
web/app/components/map/years-chips.tsx       (xóa)
web/lib/labels.ts                            (sửa chú thích; đợt 2: thêm hằng `LEVEL_ENTRY_NOTE`)
web/tests/helpers/filters.ts                 (mới: hàm chọn ô lọc dùng chung cho test)
web/tests/fr33-map-screen.test.tsx
web/tests/fr33-level-filter.test.tsx
web/tests/fr33-years-filter.test.tsx
web/tests/fr33-role-chips-new-roles.test.tsx
web/tests/fr36-snapshot-caption.test.tsx     (chỉ nếu có chỗ hỏi chip; xem tdd.md)
web/tests/fr33-filter-selects.test.tsx       (mới: nhãn hiện, option viết cứng, mô tả, chọn lại cùng giá trị không gọi lại, class bố cục; đợt 2: test chốt AC 3 và đọc globals.css; không có test Tab)
tests/deploy/test_gh163_bo_loc_cap_bac_khop_config.py (đọc `LEVEL_ENTRY_NOTE` ở labels.ts, neo ở dòng `export const`)
web/app/components/map/filter-select.tsx     (đợt 2: mũi tên có `forced-colors:text-[CanvasText]`)
Thứ tự Tab nằm ở `fr33-map-screen` và `fr33-role-chips-new-roles`; Tab rồi chọn giá trị ở `fr33-level-filter`.
```

Spec cũ cập nhật cùng commit (CLAUDE.md): `specs/163-loc-ban-do-theo-cap-bac/`, `specs/280-loc-so-nam-kinh-nghiem/`, `specs/284-them-vai-tro/` (spec/plan/tasks/tdd). `specs/285-34-tinh-remote-nuoc-ngoai/` (test dòng tỉnh, Remote nằm trong `fr33-map-screen`; đợt 2 chỉ bỏ hai assert thừa trong file đó). #284 và #162: chỉ ghi chú trên GitHub (xem spec.md), không sửa AC.

## Complexity Tracking

Không có vi phạm.
