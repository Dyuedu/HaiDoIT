# Prompt cho Claude Design — Hải Đồ IT

Dán nguyên khối dưới đây vào một cuộc trò chuyện có Claude Design (Artifacts → Design, hoặc ngay trong chat). Đính kèm file prototype `imports/prototype-ban-do-co-van.html` trong cùng thư mục này. Nhờ Claude Design làm một prototype bấm được, mỗi màn một artboard, có nút Play.

---

Hãy thiết kế một prototype web bấm được cho Hải Đồ IT. Giao diện tiếng Việt. Người dùng là sinh viên IT năm cuối và fresher ở Việt Nam, mở trên laptop, không có tài khoản.

Sản phẩm trả lời một câu: kỹ năng này xuất hiện trong bao nhiêu phần trăm tin tuyển dụng cùng vai trò ở Việt Nam. Mọi con số trên màn đi kèm cỡ mẫu n và ngày snapshot. Thiếu dữ liệu thì viết "chưa đủ dữ liệu", không đoán, không để trống. Hệ thống không khuyên nộp hay không nộp, không có ô chat, không có hội thoại với agent.

## Nhìn theo prototype đính kèm, bố cục theo PRD

File đính kèm là prototype cũ, 11 màn, nền tối. Lấy từ nó ngôn ngữ hình: nền `#070B10`, chữ `#E6EDF3`, font Be Vietnam Pro, số và mã dùng JetBrains Mono, nút chính `#C5F36A` chữ `#0A0F05`, mục đang chọn `#62D9EE`. Mật độ kiểu bảng điều khiển, không phải trang marketing.

Không vẽ lại 11 màn đó. Những màn sau chỉ là ý cũ, không làm artboard: lương theo tuần, hạn dùng kỹ năng, dự báo 18 tháng, mô phỏng nếu-thì, hộ chiếu kỹ năng, chỉ số phản hồi nhà tuyển dụng, so sánh offer, tập thương lượng, nhảy việc, remote và Nhật, năm agent đang trò chuyện.

Thanh điều hướng đúng bốn mục: Bản đồ, Insights, Cố vấn, Soi tin. Trang chủ mở Bản đồ.

## Các artboard, đặt tên rõ

1. `ban-do` — Bản đồ nhu cầu 3D. Cột cho Hà Nội, TP.HCM, Đà Nẵng, và "Khác". Chiều cao cột là tỷ trọng vai trò. Đà Nẵng ít tin vẫn có cột, mờ, kèm nhãn cỡ mẫu nhỏ. Có lối xem 2D hoặc bảng. Chú thích nguồn và ba lưu ý độ phủ luôn nhìn thấy.
2. `ban-do-ha-noi` — Minh bấm cột Hà Nội. Bảng chi tiết thành phố: tỷ trọng vai trò, kỹ năng hàng đầu, mỗi số có n và ngày. Nút "Xem lộ trình học và đối chiếu CV cho vai trò này".
3. `co-van-chung` — Cố vấn. Vai trò Backend đã chọn, cấp Intern/Fresher/Junior. Nhánh Java Backend đang có 26 tin, dưới 30, nên màn giữ cấp bậc và ghi nhãn quay về Backend cùng cấp, n = 52, kèm cơ cấu cấp bậc. Lộ trình là đồ thị nút, mỗi nút có tỷ lệ. Không có nhân vật agent.
4. `co-van-cv` — Ô đồng ý nêu rõ văn bản CV được gửi tới một dịch vụ AI bên ngoài, không lưu lại. Minh kéo thả `CV_Minh_JavaBackend.pdf`.
5. `co-van-dang-doc` — 8 đến 10 giây. Liệt kê từng bước đang chạy, không một vòng xoay chung chung.
6. `co-van-khoang-trong` — Cao trào. Java và MySQL tô xanh vì đã có trong CV. PostgreSQL, Microservices, Docker là khoảng trống thường gặp. Ba nút cho mỗi kỹ năng: "Tôi chưa biết", "Tôi đã biết, chỉ là CV chưa ghi", và một lối nhỏ "CV của tôi có ghi rồi (hệ thống đọc sót)". SQL bị báo là khoảng trống cốt lõi. Sau khi Minh xác nhận, lộ trình xếp lại theo chặng.
7. `co-van-ky-nang` — Bấm một nút kỹ năng: vì sao thị trường cần, kèm tài liệu miễn phí đã kiểm duyệt. Lời dẫn không chứa số.
8. `co-van-luu` — Hồ sơ nằm trong trình duyệt. Nút tải bản tóm tắt hai phần: kỹ năng đã có nhưng cần ghi vào CV, và lộ trình theo chặng kèm link tài liệu.
9. `cv-anh-scan` — PDF ảnh scan, dưới 30 ký tự. Trong một giây, nói lý do và ba lối: PDF xuất từ Word, Canva hoặc Overleaf; file DOCX; tự chọn kỹ năng trên màn.
10. `soi-tin-dan` — Một ô dán nội dung tin, nút "Soi tin". Không ô chat.
11. `soi-tin-ket-qua` — Đầu trang: "Đang đối chiếu với: Java Backend · Fresher/Junior", đổi được mà không dán lại. Mức khớp 89%, dòng phụ "4/4 cốt lõi, 2/2 thường gặp, 0/2 riêng của công ty". Lương: "chưa đủ dữ liệu (X/30 tin có lương)". Số kỹ năng yêu cầu vẫn có phân vị. Dấu hiệu D1 và D2 là việc cần kiểm tra, không phải kết luận tin giả. "Tin không công bố khoảng lương" là một dòng trung tính, không phải dấu hiệu.
12. `insights` — Thẻ cho Lan. "Cửa vào cho người mới" và "Bộ kỹ năng hay đi cùng nhau". Thẻ dưới 30 mẫu thì ghi chú, không hiện một tỷ lệ. Câu trên thẻ là mẫu câu có số lấy từ bảng, không phải đoạn văn AI.
13. `co-van-khong-cv` — Lan không có CV. Tự bấm Java, SQL, Git để đánh dấu đã có. Đổi sang Data Engineer thì các kỹ năng trùng được tô, kèm một dòng "Có N kỹ năng trong lộ trình này trùng với hồ sơ của bạn."
14. `chinh-sach-du-lieu` — Trang công khai. Mục đích nghiên cứu học thuật, nguồn đang dùng, dữ liệu công bố ở mức tổng hợp, CV và tin dán không được lưu, kênh email gỡ trong 48 giờ. Không có bảng rủi ro nội bộ. Không có câu "tuân thủ đầy đủ điều khoản của mọi nguồn" hay "mọi dữ liệu đều đã được cấp phép".
15. `trang-vai-tro` — Một trang công khai cho vai trò Backend, không cần tài khoản. Ô là vai trò đó, mọi cấp bậc, toàn quốc. Khi n ≥ 30, đoạn đầu có ít nhất ba kỹ năng, mỗi kỹ năng một tỷ lệ, kèm n, nguồn đang bật và ngày snapshot. Khi n < 30, đoạn đầu chỉ là "chưa đủ dữ liệu (n = X)". Không liệt kê tin, không tên công ty, không link tin gốc. Có liên kết tới trang chính sách.

Nối các artboard 1 đến 8 thành một luồng bấm được của Minh, tối Chủ nhật, từ bài đăng Facebook vào Bản đồ rồi tới tải bản tóm tắt. Artboard 10 và 11 là sáng hôm sau, hồ sơ vẫn còn. Artboard 12 và 13 là luồng của Lan. 14 và 15 đứng riêng, đọc được không cần vào ứng dụng.

Mỗi artboard ghi chú một dòng vì sao màn đó tồn tại, để người xây sau đọc được trên canvas. Xuất cả bộ thành một file HTML.
