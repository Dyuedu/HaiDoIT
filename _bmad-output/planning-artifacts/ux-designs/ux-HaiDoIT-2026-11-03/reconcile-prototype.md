# Đối chiếu — prototype cũ

Ý bị bỏ khi chưng cất UX. Không phải spine. Không sửa `DESIGN.md` hay `EXPERIENCE.md`.

Nguồn chữ: `.memlog.md`, `.working/claude-design-prompt.md` (mục những màn không làm), `EXPERIENCE.md` (Inspiration & Anti-patterns, Information Architecture), `DESIGN.md` (Brand & Style, phần màu và font). Prototype: `imports/prototype-ban-do-co-van.html`. File khoảng 5 MB, một dòng rất dài. Không đọc hết. Lệnh tìm chuỗi chạy xong: 11 tiêu đề `<h2>`, rồi đếm vài cụm. Thân từng màn không nằm ở dạng chữ thường.

## Giữ lại

Ngôn ngữ hình, theo prompt và Brand & Style: nền tối, chữ sáng, nút chính vàng chanh, mục đang chọn xanh lam, mật độ bảng điều khiển. Chữ giao diện là Be Vietnam Pro. Số và mã là JetBrains Mono. Hai tên font có trong file prototype.

Ba tiêu đề không có trong danh sách bỏ, và được dựng lại thành màn mới:

- Thị trường · Bản đồ nhu cầu → Bản đồ
- Thị trường · Lộ trình thật → lộ trình Cố vấn, đồ thị nút
- Ứng tuyển · Soi tin → Soi tin

Nav ứng dụng còn bốn mục: Bản đồ, Insights, Cố vấn, Soi tin. Chuỗi Insights không có trong prototype.

## Bỏ, có chủ đích

Prompt và mục Inspiration & Anti-patterns không làm artboard cho các ý sau. Tám tiêu đề prototype khớp danh sách đó:

- Thị trường · Lương & hạn dùng kỹ năng — lương theo tuần; hạn dùng kỹ năng
- Phát triển · Cố vấn đa agent — năm agent đang trò chuyện. Mục Cố vấn giữ; hội thoại agent bỏ
- Phát triển · Mô phỏng Nếu–thì — mô phỏng nếu-thì
- Phát triển · Hộ chiếu kỹ năng — hộ chiếu kỹ năng
- Ứng tuyển · Chỉ số phản hồi nhà tuyển dụng — chỉ số phản hồi nhà tuyển dụng
- Quyết định · So sánh offer & thương lượng — so sánh offer; tập thương lượng
- Quyết định · Nhảy việc — nhảy việc
- Quyết định · Remote & Nhật — remote và Nhật

Dự báo 18 tháng cũng nằm trong danh sách bỏ. Không có chuỗi `18 tháng` ở phần chữ đọc được.

Cùng mục anti-pattern, các cách PRD đã loại (không phải tiêu đề màn prototype): trạng thái “đang học” trên hồ sơ; gán số tuần cho từng kỹ năng; câu Insights do mô hình viết; “không ghi lương” là một dấu hiệu; chiều cao cột bằng tỷ trọng của vai trò trong thành phố.

## Chưa đọc nên chưa biết có bị rơi không

Thân 11 màn nằm trong khối nén hoặc mã hoá. `tháng`, `tuần`, `18 tháng`, `lương theo tuần` không có trong phần chữ thường. Chưa biết màn Lương hoặc Lộ trình thật có viết lương theo tuần hay dự báo 18 tháng bên trong hay không.

Chuỗi `18` xuất hiện rất nhiều lần. Không lần từng chỗ.

Nhãn nav bên trong màn không thấy ngoài 11 tiêu đề. Bốn nhóm Thị trường, Phát triển, Ứng tuyển, Quyết định chỉ biết qua tên màn.

Năm mã màu trong prompt (`#070B10`, `#E6EDF3`, `#C5F36A`, `#0A0F05`, `#62D9EE`) không thấy dạng chữ trong file. Chưa đối hex với CSS thật của prototype.
