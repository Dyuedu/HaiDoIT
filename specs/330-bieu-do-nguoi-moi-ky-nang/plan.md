# Implementation Plan: Danh sách người mới và kỹ năng theo vai trò thành biểu đồ

**Branch**: `gh-330-bieu-do-nguoi-moi-ky-nang` | **Date**: 2026-11-19 | **Spec**: [spec.md](spec.md)

## File sẽ sửa

| File | Việc |
|---|---|
| `web/lib/newcomer-roles-view.ts` | `barLength` của dòng |
| `web/lib/skill-roles-view.ts` | `dot` của dòng |
| `web/lib/market-overview-view.ts` | `buildLevelMixRows` |
| `web/app/components/insights/newcomer-list.tsx` | Thanh trong dòng |
| `web/app/components/insights/skill-roles-list.tsx` | Lollipop trong dòng |
| `web/app/components/insights/level-mix-chart.tsx` | Mới: thanh xếp chồng 100% |
| `web/app/components/insights/newcomer-screen.tsx` | Gọi thêm `market-overview`, bảng số, biểu đồ cơ cấu |
| `web/app/components/insights/skill-roles-screen.tsx` | Bảng số |
| `web/tests/us-a11-fr37-fr09-bieu-do.test.tsx` | Test mới |
| `web/tests/fr37-newcomer-list.test.tsx` | Bộ quét DEC-6 miễn `table` |

## Issue cũ có file bị đụng

Có `specs/`: #147, #148, #152, #153, #154, #167, #169, #170, #206, #207, #324, #329 (thêm đợt tdd).
