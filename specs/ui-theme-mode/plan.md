# Implementation Plan: Chế độ Sáng / Tối toàn hệ thống

**Date**: 2026-11-27 | **Spec**: [spec.md](spec.md)

## Technical Context & Structure

- `web/lib/haido-keys.ts`: thêm `HAIDO_KEYS.theme = "haido:theme"`, `ThemeMode`, `readTheme()`, `writeTheme()` (đồng bộ thêm cookie `haido_theme` cho anti-FOUC).
- `web/lib/theme-store.ts`: store `useSyncExternalStore` + đọc/lắng nghe `prefers-color-scheme` và `storage` event, không gọi `localStorage` trực tiếp (`AD-23`).
- `web/app/layout.tsx`: thêm `suppressHydrationWarning` trên `<html>` và inline bootstrap script trong `<head>` đọc cookie `haido_theme` hoặc `prefers-color-scheme` trước first-paint (không gọi `localStorage` ngoài `haido-keys.ts`).
- `web/app/globals.css`: mở rộng biến bản đồ 3D và định nghĩa đầy đủ override màu cho `:root[data-theme="light"]`.
- `web/app/components/theme-toggle.tsx` & `web/app/components/app-header.tsx`: thêm nút chuyển Sáng/Tối ở góc phải thanh đầu trang.
- `web/app/components/map/filter-select.tsx`, `web/app/soi-tin/page.tsx`, `web/app/components/map/map-3d.module.css`, `web/app/components/map/map-3d.tsx`, `web/app/components/insights/overview/charts.tsx`, `web/app/components/insights/overview/pie-3d.tsx`: dùng biến CSS thích ứng cả 2 theme.
