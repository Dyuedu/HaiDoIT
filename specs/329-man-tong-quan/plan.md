# Implementation Plan: Toàn cảnh thị trường trên Insights

**Branch**: `gh-329-man-tong-quan` | **Date**: 2026-11-19 | **Spec**: [spec.md](spec.md)

## Summary

Client và bộ kiểm hợp đồng cho `market-overview`, view builder chỉ tra số và gắn nhãn, các biểu đồ HTML/CSS và một biểu đồ tròn 3D canvas, đặt ở đầu `/insights`.

## File sẽ sửa

| File | Việc |
|---|---|
| `web/lib/market-overview.ts` | Mới: kiểu, `fetchMarketOverview`, `isMarketOverviewEnvelope` |
| `web/lib/market-overview-view.ts` | Mới: chỉ số, miếng, thanh vai trò theo cấp, cột, hai phía, câu tóm tắt |
| `web/app/components/insights/overview/palette.ts` | Mới: màu cấp bậc và nơi làm việc |
| `web/app/components/insights/overview/pie-3d.tsx` | Mới: biểu đồ tròn 3D, nút xoay, nút chú thích |
| `web/app/components/insights/overview/charts.tsx` | Mới: thanh, cột, hai phía, bảng số |
| `web/app/components/insights/overview/market-overview-screen.tsx` | Mới: gọi API, trạng thái, bố cục |
| `web/app/insights/page.tsx` | Thêm mục toàn cảnh ở đầu trang |
| `web/tests/us-a11-ad22-toan-canh.test.tsx` | Test mới |
| `web/tests/fr37-newcomer-list.test.tsx`, `web/tests/helpers/skill-roles.ts` | Mock `fetch` trả "đang tải" cho route mới, để test cũ chỉ kiểm mục của chúng |

## Issue cũ có file bị đụng

- `web/app/insights/page.tsx`: #147, #169 (thêm một mục ở đầu, hai mục cũ giữ nguyên).
- `web/tests/fr37-newcomer-list.test.tsx`: #147, #148; `web/tests/helpers/skill-roles.ts`: #169, #170.
