# TDD: Câu chữ trên màn hình viết bằng tiếng Việt dễ hiểu

Theo `docs/templates/test-driven-tdd/test-driven-development.md`.

Lệnh:

```text
cd web && npx vitest run
```

## Các hành vi

1. Ba màn (Bản đồ, Insights, Hồ sơ kỹ năng) không hiện `n = `, "snapshot", "entry-level".
2. Dòng người mới: tỷ lệ và "X trên N tin dành cho người mới".
3. Dòng kỹ năng theo vai trò: "… tin AI/ML cho người mới có nhắc tới Python", "tính trên N tin".
4. Hồ sơ kỹ năng quay về ô rộng: "Tính trên N tin".
5. Thiếu mẫu: "Mới có N tin, cần ít nhất M" / "Mới có N tin, chưa đủ M (để so sánh chắc chắn)" / "Chưa có tin nào".
6. Khung nguồn: "Đang xem", "Cập nhật", tên nguồn, "Lần cập nhật này chưa lấy đủ tin từ …".
7. Tiêu đề bản đồ "N tin <vai trò> · <cấp>, <số năm>"; "tin IT" khi mọi vai trò.
8. Câu số tin bị bỏ vì không ghi số năm, câu chưa tin nào nhắc tới kỹ năng.

## Đợt 1 (2026-11-19)

Ghi chú môi trường: trên máy Windows này, chạy Vitest từ Git Bash (`/d/...`) làm mọi file báo "Vitest failed to find the current suite", kể cả trên cây sạch; chạy từ PowerShell (`D:\...`) thì bình thường. Mọi kết quả dưới đây chạy từ PowerShell.

### RED

`npx vitest run` → `Test Files 14 failed | 14 passed (28)`, `Tests 42 failed | 299 passed (341)`.

Đỏ đúng lý do:

- `fr36-gh324-cau-chu-de-hieu.test.tsx`, `fr36-snapshot-caption.test.tsx`: không nạp được `@/lib/source-labels` (file chưa có).
- `fr37-newcomer-list.test.tsx` (7 test): `notEnoughText` chưa có; dòng vẫn ghi "501 tin cho người mới", "n = 877", "chưa đủ dữ liệu (12/30)".
- `fr09-*`, `fr13-chon-mot-ky-nang`, `fr09-fr13-us-a4-ac` (7 test): vẫn "tin AI/ML mới vào nghề nhắc tới Python", "n = 501", "chưa đủ dữ liệu (4/30)", "Chưa tin tuyển dụng hiện tại nào nhắc tới ABAP.".
- `fr19-skill-profile`, `fr18-fr19-us-a2-ac` (2 test): vẫn "n = 157".
- `fr33-*` (26 test): vẫn "Cỡ mẫu nhỏ (n = 21 < 30): số liệu chỉ để tham khảo", "Nguồn lỗi ở snapshot này: topdev", "Bộ lọc", "Ngày snapshot", "Tất cả · Mới vào nghề · Mọi số năm", câu số tin bị bỏ cũ. Hai test "đổi vai trò…" và "response về muộn…" đỏ vì chúng chờ nhãn mẫu nhỏ theo câu mới trước khi kiểm phần còn lại.

### GREEN

Thêm `web/lib/source-labels.ts`; sửa bốn view và sáu component theo `plan.md`. Hai test cũ còn kiểm khung nguồn theo chữ cũ ("Mới vào nghề" viết hoa giữa câu, mã `itviec`) được sửa theo câu đã duyệt.

- `npx vitest run` → `Test Files 28 passed (28)`, `Tests 357 passed (357)`.
- `npm run lint` sạch; `npx tsc --noEmit` sạch; `npx next build` qua (7 route).

## Đợt #330 (2026-11-19): danh sách thành biểu đồ, AC của issue này không đổi

Lý do: #330 thêm thanh vào danh sách người mới, lollipop vào danh sách kỹ năng theo vai trò, bảng số cho cả hai và biểu đồ cơ cấu cấp bậc (`web/lib/newcomer-roles-view.ts`, `skill-roles-view.ts`, `market-overview-view.ts`, các component trong `web/app/components/insights/`). Chữ, số, thứ tự và luật ẩn số không đổi. Bộ quét DEC-6 trong `web/tests/fr37-newcomer-list.test.tsx` miễn thêm `table` (bảng số là ô số theo thiết kế).

- RED và GREEN: `specs/330-bieu-do-nguoi-moi-ky-nang/tdd.md` (`npx vitest run` → 373 passed).
