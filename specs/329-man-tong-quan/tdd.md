# TDD: Toàn cảnh thị trường trên Insights

Theo `docs/templates/test-driven-tdd/test-driven-development.md`.

Lệnh (PowerShell; từ Git Bash Vitest báo "failed to find the current suite", xem #324):

```text
cd web && npx vitest run tests/us-a11-ad22-toan-canh.test.tsx
```

## Các hành vi

1. Bốn chỉ số, có số tin và ngày; tỷ lệ in đúng `share.value`.
2. Chọn cấp bằng nút chú thích: nút `aria-pressed`, biểu đồ vai trò theo `roles_by_level` của cấp đó; bỏ lọc trả về `roles`.
3. Nút xoay; canvas `aria-hidden`.
4. Cột số năm, cột nơi làm việc, biểu đồ hai phía theo thứ tự API.
5. Câu tóm tắt không có chữ số, gọi tên theo `levels_by_size` và `roles_by_entry_share`.
6. Vai trò dưới 30 tin mờ, ghi "Mới có 12 tin, chưa đủ 30".
7. Năm biểu đồ, năm bảng số.
8. `unknown_cell` không có "Thử lại"; body sai hợp đồng thì "Không đọc được số liệu".
9. Bộ kiểm hợp đồng nhận fixture, từ chối thứ hạng thiếu vai trò.

## Đợt 1 (2026-11-19)

Thứ tự thực tế: code của màn được viết trước test (lệch quy trình). Để RED vẫn là lần chạy thật, test được viết xong rồi tạm cất code mới (`git stash -u` các file `web/lib/market-overview*.ts`, `web/app/components/insights/overview/`, `web/app/insights/page.tsx`) và chạy.

### RED

`Test Files 1 failed (1)`, `Tests no tests`: `Failed to resolve import "@/app/components/insights/overview/market-overview-screen"`. Đỏ đúng lý do: màn chưa có.

### GREEN

- Trả code lại: `tests/us-a11-ad22-toan-canh.test.tsx` 9 passed.
- Cả bộ lần đầu: `4 failed | 362 passed`. Bốn test cũ dựng cả `/insights` với mock `fetch` không biết `/api/v1/market-overview`: phần toàn cảnh thành "không đọc được", thêm một `alert` và một nút "Thử lại". Sửa mock (`fr37-newcomer-list.test.tsx`, `helpers/skill-roles.ts`) để route mới không bao giờ trả, phần toàn cảnh đứng ở "Đang tải"; các test cũ vẫn chỉ kiểm mục của chúng.
- `npx vitest run` → `Test Files 29 passed (29)`, `Tests 366 passed (366)`. `npm run lint`, `npx tsc --noEmit` sạch.
- Chụp trang ở máy với API bản giả (`next start`, 1280 px và 390 px): không tràn ngang, chọn Senior lọc đúng biểu đồ vai trò.
- `next build` ở máy dừng ở bước cuối với `SecurityFatalError: Your version of Next.js is affected by a known security vulnerability` (Next.js 16.4.4) sau khi đã "Compiled successfully"; không phải lỗi của thay đổi này. Đã báo người dùng.
