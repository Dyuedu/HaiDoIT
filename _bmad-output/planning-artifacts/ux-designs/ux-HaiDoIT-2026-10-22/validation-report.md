# Validation Report — Hải Đồ IT

- **DESIGN.md:** `_bmad-output/planning-artifacts/ux-designs/ux-HaiDoIT-2026-10-22/DESIGN.md`
- **EXPERIENCE.md:** `_bmad-output/planning-artifacts/ux-designs/ux-HaiDoIT-2026-10-22/EXPERIENCE.md`
- **Run at:** 2026-10-22T20:55+07:00

## Overall verdict

Hai bản là hợp đồng đọc được cho bốn hành trình. UJ-1 đến UJ-4 có người, các bước, một đỉnh và một đường trật. Mọi màu có mã hex. Rubric không có lỗi critical. Bốn mục high nằm ở danh kỹ năng trên bản đồ, bảng xếp hạng, lỗi dữ liệu của Học gì tiếp? với Soi tin, và một lệch bố cục «bảng thành phố».

Lăng kính khả năng tiếp cận kéo bức tranh xuống mức thin. Bốn lỗi critical là viền ô nhập khoảng 1,5:1, vòng focus trùng màu nút chính, mục điều hướng thấp hơn 24px, và mốc tầm nhìn đang chọn dưới 3:1. Sau báo cáo này, các lỗi critical và high đã được viết vào hai bản. Ảnh minh họa vẫn chưa có, vì bước màn hình then chốt chưa chạy.

## Category verdicts

- Flow coverage — strong
- Token completeness — adequate
- Component coverage — adequate
- State coverage — adequate
- Visual reference coverage — thin
- Bloat & overspecification — adequate
- Inheritance discipline — adequate
- Shape fit — strong
- Accessibility review — thin

## Findings by severity

### Critical (4)

**[Khả năng tiếp cận]** — Viền ô nhập dưới 3:1 (DESIGN.md, Ô email)
Viền `#243543` trên `#0A1118` khoảng 1,5:1. Ô offer và ô link sẽ copy cặp này.
Fix: viền tĩnh dày 2px màu `#62D9EE`. Đã đưa vào bản.

**[Khả năng tiếp cận]** — Vòng focus trùng màu nút chính (Accessibility Floor)
Viền `#C5F36A` trên nền `#C5F36A` là 1:1.
Fix: vòng focus cách mép control 2px để nằm trên nền tối. Đã đưa vào bản.

**[Khả năng tiếp cận]** — Mục điều hướng thấp hơn 24px (Thanh điều hướng)
Chữ 14px không có chiều cao vùng bấm.
Fix: mỗi mục cao ít nhất 44px. Đã đưa vào bản.

**[Khả năng tiếp cận]** — Mốc tầm nhìn đang chọn dưới 3:1 (Tầm nhìn)
Nền chọn và viền trong đều dưới 3:1.
Fix: gạch 2px màu `#62D9EE`. Đã đưa vào bản.

### High (14)

**[Rubric — Component coverage]** — Dấu «đã có» không có danh chứa trên bản đồ.
Fix: thêm Danh kỹ năng thành phố trong tab Cơ cấu. Đã đưa vào bản.

**[Rubric — Component coverage]** — Bảng xếp hạng được bấm nhưng không có hàng thành phần.
Fix: cột hạng, tên, số tin. Không có cột mức tăng và không có cột lương. Đã đưa vào bản.

**[Rubric — State coverage]** — Học gì tiếp? và Soi tin thiếu đang tải, lỗi nguồn, mất mạng.
Fix: dùng lại câu và nút của bản đồ. Đã đưa vào bản.

**[Rubric — Inheritance]** — DESIGN.md còn «bảng thành phố» ở Học gì tiếp?, EXPERIENCE.md chỉ có một cặp số.
Fix: bỏ bảng thành phố khỏi bố cục. Khi hai bản lệch, EXPERIENCE.md thắng về hành vi. Đã đưa vào bản.

**[Khả năng tiếp cận]** — Hộp lương ẩn có viền dưới 3:1. Fix: nét đứt màu `#F5A65B`. Đã đưa vào bản.

**[Khả năng tiếp cận]** — Nút Vì sao? dưới 44px. Đã đưa vào bản.

**[Khả năng tiếp cận]** — Lớp chào không nhận focus khi mở. Đã đưa vào bản.

**[Khả năng tiếp cận]** — Ngăn Vì sao? chưa có role dialog và bẫy Tab. Đã đưa vào bản.

**[Khả năng tiếp cận]** — Nút tạo bị khóa chưa có aria-disabled. Đã đưa vào bản.

**[Khả năng tiếp cận]** — Chip và tab thiếu aria-pressed hoặc aria-selected. Đã đưa vào bản.

**[Khả năng tiếp cận]** — Toast tự tắt sau 2,4 giây và không có role status. Đã đưa vào bản.

**[Khả năng tiếp cận]** — Ô email chưa gắn label, autocomplete và aria-invalid. Đã đưa vào bản.

**[Khả năng tiếp cận]** — Thiếu `lang="vi"`. Đã đưa vào bản.

**[Khả năng tiếp cận]** — Header năm mục chưa xuống dòng dưới 720px. Đã đưa vào bản.

### Medium (12)

**[Rubric — Token completeness]** — Vài cặp chữ chịu lực chưa được liệt kê lúc đọc. Các cặp chính đã được bổ sung sau báo cáo.

**[Rubric — Token completeness]** — Độ đục của lưới, header và bóng nút chưa thành token. Chưa sửa.

**[Rubric — Component coverage]** — Nút thế khối và thế phẳng chưa có hàng lúc đọc. Đã thêm hàng «Khối» và «Phẳng» sau báo cáo.

**[Rubric — Component coverage]** — Khối tám quý thiếu quy tắc rỗng và chú giải. Đã thêm chú giải chữ và câu «Chưa đủ mẫu.»

**[Rubric — State coverage]** — Mở liên kết thiếu đang tải và lỗi. Đã thêm hai hàng.

**[Rubric — Visual reference]** — Chưa có mockup. Để bước màn hình then chốt.

**[Rubric — Bloat]** — Độ đậm 500 và chữ avatar chưa gắn vai. Chưa sửa.

**[Rubric — Bloat]** — Đoạn tin đủ điều kiện nên là bảng. Chưa sửa.

**[Rubric — Inheritance]** — «Độ tin cậy» trong ngăn Vì sao? không có trong PRD. Đã bỏ khỏi DESIGN.md.

**[Khả năng tiếp cận]** — Câu lỗi chưa có role alert lúc đọc. Đã thêm.

**[Khả năng tiếp cận]** — Tên cột dự báo thiếu chữ «Dự báo». Đã thêm.

**[Khả năng tiếp cận]** — Khối tám quý chỉ phân biệt hướng bằng màu. Đã thêm chú giải chữ.

### Low (3)

**[Rubric]** — Bốn token danger và ink-card chưa có chỗ dùng. Chưa xóa.

**[Rubric]** — Giảm chuyển động chưa nói ngăn hiện ngay lúc đọc. Đã thêm.

**[Rubric]** — Shapes còn avatar và thanh tiến độ dù không có thành phần đó. Chưa sửa.

## Reviewer files

- `review-rubric.md`
- `review-accessibility.md`
