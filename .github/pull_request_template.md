Closes #

## Thay đổi gì

<!-- Một đoạn. Người rà soát đọc được mà không cần hỏi lại. -->

## Acceptance Criteria

<!-- Dán từng dòng Given/When/Then của issue, và chỉ ra chỗ nào trong code hoặc test thỏa dòng đó. -->

- [ ] Mọi dòng AC của issue đã đạt

## Definition of Done

Đầy đủ ở [`DOD.md`](../_bmad-output/planning-artifacts/DOD.md). Tick những dòng áp dụng cho PR này:

- [ ] Số hiển thị kèm cỡ mẫu, ngày snapshot, nguồn — tách khỏi lời dẫn
- [ ] Mẫu nhỏ chặn qua `display_policy.suppression_for`, không so `n < 30` rải rác
- [ ] Ngưỡng và tham số đọc từ cấu hình có phiên bản, không hardcode
- [ ] Phép dùng lại có đúng một chữ ký trong `REGISTRY.md`
- [ ] Alembic đúng một head
- [ ] Hướng phụ thuộc không đảo
- [ ] Thao tác người dùng không gọi mô hình ngoài hai đường cho phép
- [ ] Không có nội dung CV hay JD trong bảng, log, sự kiện, file tạm
- [ ] Có kiểm thử cho AC chính, tên test chứa mã FR hoặc AD
- [ ] Cổng CI của AD liên quan còn xanh
- [ ] Màn hình chạy đủ trên điện thoại, có `aria-*`, focus thấy được
- [ ] Lệnh CLI mới đã ghi vào `README` hoặc `docs/`

## Người rà soát cần nhìn kỹ chỗ nào

<!-- Chỉ thẳng file và lý do. Không để trống. -->
