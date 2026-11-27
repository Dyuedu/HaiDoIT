# Feature Specification: Chế độ Sáng / Tối toàn hệ thống (Light/Dark Mode)

**Feature Branch**: `gh-216-lo-trinh-that`
**Created**: 2026-11-27
**Status**: In Progress

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Chuyển đổi chế độ Sáng / Tối từ thanh điều hướng (Priority: P1)

Người dùng ở bất kỳ trang nào (`/`, `/insights`, `/co-van`, `/soi-tin`, `/ho-so-ky-nang`) đều thấy nút chuyển chế độ Sáng/Tối trên thanh đầu trang (`AppHeader`). Bấm nút sẽ đổi ngay toàn bộ giao diện giữa Nền tối (`dark`) và Nền sáng (`light`) với độ tương phản rõ ràng, đồng thời giữ nguyên lựa chọn khi tải lại trang.

**Acceptance Scenarios**:

1. **Given** người dùng chưa lưu lựa chọn giao diện, **When** mở ứng dụng trên hệ điều hành chuộng chế độ sáng (`prefers-color-scheme: light`) hoặc mặc định tối (`dark`), **Then** giao diện áp đúng `data-theme="light"` hoặc `"dark"` ngay trước lần vẽ đầu tiên (hạn chế chớp màn hình).
2. **Given** người dùng bấm nút chuyển chế độ trên thanh điều hướng, **When** đang ở `"dark"`, **Then** `document.documentElement.dataset.theme` đổi thành `"light"`, `colorScheme` thành `"light"`, lưu vào khóa đóng `haido:theme` (qua `haido-keys.ts`, tuân thủ `AD-23`), và mọi trang/biểu đồ (`Map3D`, `Pie3D`, `PathGraph`, thẻ, ô chọn `<select>`) đều đổi sang bảng màu sáng đọc rõ.
3. **Given** người dùng gọi `clearHaidoData()`, **When** xóa dữ liệu trình duyệt của Hải Đồ IT, **Then** khóa `haido:theme` cũng được dọn sạch theo tiền tố `haido:`.

## Requirements *(mandatory)*

- **FR-001**: Danh sách khóa đóng `HAIDO_KEYS` trong `web/lib/haido-keys.ts` bổ sung `theme: "haido:theme"`; mọi truy cập `localStorage` vẫn nằm duy nhất trong `web/lib/haido-keys.ts` (`AD-23`).
- **FR-002**: `web/app/globals.css` giữ nguyên bảng màu tối mặc định tại `@theme static` (`--color-primary: #c5f36a`) và định nghĩa đầy đủ biến màu chế độ sáng trên `:root[data-theme="light"]` (`color-scheme: light`).
- **FR-003**: `web/app/components/app-header.tsx` hiển thị nút `ThemeToggle` có kích thước chạm tối thiểu `44px` (`min-h-target`), nhãn tiếng Việt truy cập được (`aria-label`).
- **FR-004**: Các thành phần có màu cứng trước đây (`map-3d`, `pie-3d`, `charts`, `filter-select`, `soi-tin`) chuyển sang đọc token CSS theo theme đang chọn.
