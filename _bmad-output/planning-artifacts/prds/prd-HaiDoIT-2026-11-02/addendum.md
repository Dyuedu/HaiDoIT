---
title: "Addendum: PRD Hải Đồ IT"
created: 2026-11-03
updated: 2026-11-03
---

# Addendum: chi tiết cho kiến trúc, UX và chương Thực nghiệm

Tài liệu này giữ những chi tiết **làm thế nào** và những **phương án đã bị loại** trong lúc viết PRD. Kế hoạch 8 sprint, phương án stack và các quyết định kiến trúc ban đầu nằm ở addendum của product brief (`../../briefs/brief-HaiDoIT-2026-11-02/addendum.md`).

## 1. Ghi chú hiện thực theo từng FR

- **FR-9, ngưỡng θ:** khởi tạo θ_core = 30%, θ_common = 10%. Lý do chọn 30%: JD là văn bản tự nhiên, nhiều nhà tuyển dụng không liệt kê những kỹ năng "hiển nhiên". Một kỹ năng xuất hiện tường minh trong hơn 1/3 số tin của một nhánh đã là tín hiệu cầu mạnh. Với ngưỡng 50%, nhóm cốt lõi gần như rỗng; số liệu kiểm tra ngày 02/11:
  - Backend chỉ có Java và Microservices (54%);
  - Data/AI chỉ có Python (64%).
- **FR-10:** giới hạn 5 MB được chặn ở cả frontend lẫn reverse proxy. CV dạng văn bản của sinh viên thường nặng 100 KB – 1,5 MB.
- **FR-14:** xóa hồ sơ là xóa mọi khóa của Hải Đồ IT trong `localStorage`, gồm cả mã phiên ẩn danh.
- **FR-15:** link chia sẻ mã hóa vai trò mục tiêu cùng mảng mã kỹ năng vào tham số của URL.
- **FR-21, giao diện:**
  - "Tôi chưa biết" và "Tôi đã biết, chỉ là CV chưa ghi" là hai nút chính;
  - "CV của tôi có ghi rồi (hệ thống đọc sót)" là link chữ hoặc biểu tượng nhỏ đặt cạnh, để giữ phân cấp thị giác. Lựa chọn phụ này cũng giúp người dùng không cảm thấy bị hệ thống đổ lỗi khi CV của họ đã ghi rõ kỹ năng.
- **FR-22, thuật toán:**
  - **thuật toán:** sắp xếp topo theo Kahn, dùng hàng đợi ưu tiên với khóa (chặng, nhóm, −tỷ lệ xuất hiện, mã kỹ năng). Không bao giờ phụ thuộc vào thứ tự trả về của cơ sở dữ liệu;
  - **phạm vi tính:** đồ thị khoảng 100–300 nút, đủ nhỏ để tính trong bộ nhớ;
  - **kỹ năng nền tảng:** được kéo vào bằng phép truy vết tổ tiên.
- **FR-23:** kiểm thử regex cho lời dẫn phải loại trừ các số nằm trong tên công nghệ (Java 17, S3, EC2, OAuth2, Web3, HTML5, Vue 3).
- **FR-24:** việc tô sáng kỹ năng trùng là phép giao tập hợp giữa hai mảng mã kỹ năng, tính ngay ở frontend, không cần API riêng.
- **FR-28, công thức mức khớp:**
  - **công thức:** mức khớp = round(Σ w(s), với s ∈ S_JD ∩ S_hồ sơ ÷ Σ w(s), với s ∈ S_JD × 100); trọng số w: cốt lõi 3, thường gặp 2, riêng của công ty 1. S_JD chỉ gồm kỹ năng đã nhận diện;
  - **vì sao có trọng số:** không dùng trung bình không trọng số, vì một JD có 2 kỹ năng cốt lõi và 6 kỹ năng hiếm sẽ kéo mức khớp của người đã nắm đủ khung cốt lõi xuống còn 25%;
  - **ví dụ kiểm tra:** 4/4 cốt lõi + 2/2 thường gặp + 0/2 riêng = 16/18 = 89%; 4/4 + 1/2 + 1/2 = 15/18 = 83%.
- **FR-29 và FR-6, danh sách chờ kỹ năng chưa nhận diện:** lưu thành bảng gồm từ khóa, tần suất, lần thấy gần nhất. Nhóm rà soát hằng tuần.
- **FR-38:** 5 điểm phần trăm là ngưỡng lọc nhiễu thực tế. Với hai tỷ lệ khoảng 20% trên khoảng 300 tin mỗi bên, sai số chuẩn của hiệu hai tỷ lệ khoảng 3,3 điểm. Chênh 5 điểm chỉ khoảng 1,5 lần sai số, chưa đạt mức ý nghĩa 95% (xem câu hỏi mở số 1 trong PRD).

## 2. Thiết kế chế độ thử nghiệm (cho chương Thực nghiệm)

- **Ba bước trong một phiên:**
  1. modal đầu phiên;
  2. dùng sản phẩm bình thường, có ghi sự kiện ẩn danh;
  3. modal cuối phiên.

  Cả ba nối với nhau bằng mã phiên ẩn danh. Cuối Sprint 7, chỉ cần một câu truy vấn JOIN là ra bảng số liệu.
- **Bảng `eval_pre_session`:** lưu 3 kỹ năng tự đoán dưới dạng mảng mã kỹ năng, ví dụ `["docker", "redis", "kafka"]`.
- **So sánh mù:** mỗi vai trò mục tiêu được hỗ trợ có một tình huống mẫu cố định, gồm hồ sơ kỹ năng mẫu và JD mẫu. Ví dụ: "ứng viên đã biết Java, Spring Boot, MySQL và nhắm tới Java Backend". Cả hai phương án đều được chuẩn bị sẵn dưới dạng JSON tĩnh:
  - phương án Hải Đồ IT do chính hệ thống tạo trên đúng đầu vào mẫu, tại một snapshot cố định;
  - phương án ChatGPT là câu trả lời cho cùng đầu vào đó.
- **Các phương án đã loại:**
  - **dùng Google Form bên ngoài:** người thử phải tự copy mã phiên, rất dễ ghép sai dữ liệu;
  - **thu email hoặc Zalo để hỏi lại sau 7 ngày:** phá vỡ cam kết ẩn danh;
  - **so sánh kết quả cá nhân hóa của người thử với câu trả lời ChatGPT cho CV mẫu:** người thử nhận ra ngay phương án nào nói về mình, nên phép so sánh không còn mù.

## 3. Các phương án đã cân nhắc và bị loại trong PRD

| Chủ đề | Phương án bị loại | Lý do |
|---|---|---|
| Ngưỡng nhóm kỹ năng | Cố định ở 50% và 10% | Nhóm cốt lõi gần như rỗng trên dữ liệu thật |
| Ngưỡng nhóm kỹ năng | Phân nhóm tương đối (top N của mỗi vai trò) | Khó giải thích, mất câu nói "phần lớn thị trường yêu cầu" |
| Mức khớp | Không trọng số | Kỹ năng hiếm kéo tụt điểm của người đã đủ khung cốt lõi |
| Hồ sơ kỹ năng | Thêm trạng thái "đang học" | Làm mức khớp bị thổi phồng; kỹ năng định học đã nằm trên lộ trình học |
| Lộ trình học | Gắn số tuần học cho từng kỹ năng | Không bảo vệ được căn cứ của con số; tốc độ học khác nhau giữa từng người |
| Lộ trình học | Thêm cạnh Redis → Kafka | Không phải quan hệ học trước thật; hai kỹ năng ngang hàng thì xếp bằng quy tắc 4 tầng |
| Bản đồ | Chiều cao cột = tỷ trọng của vai trò *trong* thành phố | Thành phố ít tin trông như "thánh địa"; phải ẩn cột Đà Nẵng |
| Bản đồ | So sánh song song hai thành phố | Thẻ Insights "Khác biệt giữa các thành phố" đã trả lời câu hỏi này |
| Insights | LLM viết câu kết luận | Câu kết luận luôn chứa con số đổi mỗi ngày; có rủi ro viết sai số |
| Soi tin | "Không ghi lương" là một dấu hiệu | Kích hoạt trên khoảng 76% tin, gây mệt mỏi vì cảnh báo |
| Soi tin | D2 tính cả kỹ năng chưa nhận diện | Khi đó D2 đo độ phủ của bộ từ vựng, không đo tin tuyển dụng |
| Soi tin | Thêm thành phố vào ô thống kê | Mẫu thưa đi 2–3 lần; kỹ năng cốt lõi của một nhánh không khác nhau theo tỉnh thành |
| Lưu trữ | Neo4j độc lập, GraphRAG | Chỉ có một bài toán đồ thị thật; xem addendum của brief |
