# Implementation Plan: Nhận định trên trang Insights

**Branch**: `gh-338-nhan-dinh-insights` | **Date**: 2026-11-21 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification từ `specs/338-nhan-dinh-insights/spec.md`

## Summary

Mở rộng các hàm `buildMarketOverviewView`, `buildNewcomerView`, `buildSkillRolesView` trong `web/lib/` để sinh thêm câu nhận định hướng dẫn hành động, hiển thị bên cạnh biểu đồ hiện có. Không thêm API mới, chỉ dùng data đã có.

## Technical Context

**Language/Version**: TypeScript, Next.js 16, React 19

**Primary Dependencies**: Không thêm gì.

**Storage**: Không đổi.

**Testing**: `cd web && npx vitest run`

**Target Platform**: Trình duyệt, responsive từ 360 px.

## Constitution Check

- DEC-6: câu trên trang không chứa số.
- AD-22: web chỉ in số từ API, không tính số mới.
- Không viết spec vào `_bmad-output/`.

## Project Structure

```text
web/lib/
├── market-overview-view.ts   # Mở rộng takeaways()
├── newcomer-roles-view.ts    # Thêm field takeaways vào NewcomerView
└── skill-roles-view.ts       # Thêm field insight vào SkillRolesView

web/app/components/insights/
├── overview/market-overview-screen.tsx  # Hiển thị takeaways mở rộng (đã có)
├── newcomer-screen.tsx                 # Hiển thị takeaways mới
└── skill-roles-screen.tsx              # Hiển thị insight mới

web/tests/
├── fr338-market-overview-takeaways.test.tsx   # Test takeaways mở rộng
├── fr338-newcomer-takeaways.test.tsx          # Test newcomer takeaways
└── fr338-skill-roles-insight.test.tsx         # Test skill-roles insight
```

## Complexity Tracking

Không có vi phạm.
