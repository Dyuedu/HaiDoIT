# Implementation Plan: Câu chữ trên màn hình viết bằng tiếng Việt dễ hiểu

**Branch**: `gh-324-cau-chu-de-hieu` | **Date**: 2026-11-19 | **Spec**: [spec.md](spec.md)

## Summary

Đổi chữ ở tầng dựng view (`web/lib/*-view.ts`) và vài component in chữ cố định. Thêm `web/lib/source-labels.ts` cho tên nguồn. Không đổi API, không đổi số.

## Technical Context

Next.js, React, TypeScript, Vitest + Testing Library. Không đụng Python, DB.

## File sẽ sửa

| File | Việc |
|---|---|
| `web/lib/source-labels.ts` | Mới: tên hiển thị của 8 nguồn, `sourceLabel`, `sourcesText` |
| `web/lib/city-shares-view.ts` | Câu mẫu nhỏ, `notEnoughText`, `failedSourcesText`, `filtersText`, `title` của bản đồ, câu số tin bị bỏ |
| `web/lib/newcomer-roles-view.ts` | `entryText` "X trên N tin dành cho người mới", bỏ `nText`, câu thiếu mẫu |
| `web/lib/skill-roles-view.ts` | Câu "cho người mới có nhắc tới", `nText` "tính trên N tin", câu chưa ai nhắc |
| `web/lib/skill-profile-view.ts` | `nText` "Tính trên N tin", dòng "Đang xem" |
| `web/app/components/map/snapshot-caption.tsx` | Nhãn "Đang xem", "Cập nhật", tên nguồn |
| `web/app/components/map/load-error.tsx` | "Cập nhật:" thay "Ngày snapshot:" |
| `web/app/components/map/map-3d.tsx` | Tiêu đề khung lấy `view.title` |
| `web/app/components/insights/newcomer-list.tsx` | Tỷ lệ + câu "trên N tin", bỏ ô `n` |
| `web/app/components/insights/skill-roles-list.tsx` | Dùng `nText` mới |
| `web/app/page.tsx` | Câu giới thiệu "kèm số tin, nguồn và ngày cập nhật" |
| `web/tests/fr36-gh324-cau-chu-de-hieu.test.tsx` | Test mới |
| `web/tests/*.test.ts(x)` | Đổi câu kỳ vọng theo bảng đã duyệt |

## Issue cũ có file bị đụng

- Có `specs/`: #103, #106, #147, #151, #152, #153, #154, #163, #167, #169, #170, #206, #207, #280, #285, #314, #316. Mỗi thư mục thêm một đợt tdd; `spec.md` của issue có câu cũ trong scenario thì sửa câu đó.
- Chưa có `specs/`: #1, #46 (ghi trong mô tả PR).

## Thay đổi sau merge (2026-11-25, #217)

`web/lib/skill-profile-view.ts`: `learningPathHref` nhận `skill` tùy chọn. Hành vi của issue này không đổi.
