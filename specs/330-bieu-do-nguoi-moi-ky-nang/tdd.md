# TDD: Danh sách người mới và kỹ năng theo vai trò thành biểu đồ

Lệnh (PowerShell):

```text
cd web && npx vitest run tests/us-a11-fr37-fr09-bieu-do.test.tsx
```

## Các hành vi

1. Thanh người mới dài theo tỷ lệ so với tỷ lệ lớn nhất; dòng `null_data` không có thanh.
2. Bảng số người mới có mọi vai trò; dòng vẫn là liên kết hồ sơ kỹ năng.
3. Cơ cấu cấp bậc theo thứ tự người mới, đoạn dài đúng tỷ lệ cấp của API.
4. Vai trò API ẩn tỷ lệ cấp: không có đoạn, ghi "chưa đủ dữ liệu".
5. `market-overview` lỗi: danh sách người mới vẫn hiện, không có biểu đồ cơ cấu.
6. Chấm lollipop đúng `share.value`; dòng `null_data` không có chấm.
7. Bảng số kỹ năng theo vai trò có mọi vai trò.

## Đợt 1 (2026-11-19)

### RED

Test viết trước code. `Tests 6 failed | 1 passed (7)`: chưa có thanh (`share-bar`), chấm (`share-dot`), bảng số và biểu đồ cơ cấu. Hành vi 5 xanh sẵn vì màn người mới chưa gọi `market-overview`.

### GREEN

- `npx vitest run` → `Test Files 30 passed (30)`, `Tests 373 passed (373)`; lint, `tsc --noEmit` sạch.
- Bảng số người mới có chữ số ngoài `ol`, làm `fr37 ad8` (bộ quét DEC-6 của #148) đỏ; kiểm lại bằng cách bỏ thay đổi bộ quét thì đúng test đó đỏ (`1 failed | 37 passed`). Bộ quét miễn thêm `table`. Bộ quét của `fr09` vẫn xanh khi không đổi nên giữ nguyên.
