---
title: Đối chiếu phụ lục PRD với architecture spine
source: _bmad-output/planning-artifacts/prds/prd-HaiDoIT-2026-10-22/addendum.md
compared: ARCHITECTURE-SPINE.md
verdict: gaps
---

# Đối chiếu phụ lục PRD với spine

Đối chiếu `addendum.md` với `ARCHITECTURE-SPINE.md`. Không sửa hai file đó.

Chuẩn dùng ở đây: spine chỉ phải khóa chỗ hai bên xây độc lập có thể ra hai hợp đồng khác nhau. Một con số mà story đọc được từ phụ lục không tự thành lỗ, trừ khi hai đơn vị có thể giao hai bộ số hoặc hai chủ của cùng bộ số.

## Findings

### 1. high · spine-hole

- **Addendum** (§ Tiền của hai tháng này): Tin treo là tin đăng đi đăng lại. Ngưỡng tạm (làm mới từ lần thứ hai, hoặc còn mở sau 30 ngày) là giả định, chưa phải sự thật. Trước tuần 1 không được viết test như thể ngưỡng đã đúng. Test được phép kiểm số lần làm mới và hai mốc ngày.
- **Spine:** AD-4 giữ ngày thấy đầu và ngày thấy gần nhất khi gặp lại tin. Không có cột số lần làm mới. Không có quy tắc nào nói ngưỡng tin treo phải để ngoài sản phẩm cho đến khi đo, kiểu AD-12 làm với dự báo. Soi tin chỉ được nhắc là không ghi server và không qua model (AD-9).
- **Class:** spine-hole
- **Vì sao là lỗ:** Lệnh nạp và màn Soi tin là hai đơn vị. Một bên có thể chỉ cập nhật hai mốc ngày; bên kia có thể bịa số lần làm mới hoặc đóng đinh ngưỡng tạm thành luật. Cả hai vẫn thỏa AD-4.

### 2. high · spine-hole

- **Addendum** (§ Dữ liệu và pipeline): Trích kỹ năng từ mô tả bằng mô hình ngôn ngữ là cơ chế, thuộc kiến trúc. Trước khi gọi API bên ngoài phải bỏ thông tin cá nhân. Nguyên văn mô tả không được lưu sau khi trích.
- **Spine:** AD-4 cấm giữ mô tả trên dòng tin, và AD-5 nói file trao tay là bản ghi đã trích. Không nói trích bằng mô hình nào, trích ở đâu, và không cấm gửi nguyên văn ra API bên ngoài. AD-7 cấm API chat trả phí và buộc Ollama chỉ cho lộ trình 90 ngày, không cho bộ cào.
- **Class:** spine-hole
- **Vì sao là lỗ:** Bộ cào có thể gọi API ngoài bằng mô tả thô, hoặc trích cục bộ. Hai cách đó không cùng chủ với bộ số của lộ trình. Cấm lưu mô tả không chặn lúc gọi API.

### 3. medium · spine-hole

- **Addendum** (§ Dữ liệu và pipeline): Cách lấy tin — HTML của các trang đang chạy, và JSON công khai của ATS — là việc kiến trúc. PRD chỉ khóa trường được giữ, làm mới hằng ngày, và điều kiện lịch sự đã chốt trong brief.
- **Spine:** AD-5 khóa chỗ đặt code (trong repo này), tay trao bằng file, và cấm `backend/` gọi thẳng SkillNexus. Không khóa hai kênh lấy (HTML và JSON ATS). Lịch hằng ngày và lịch sự (robots, không vượt trang chặn) không có trong spine.
- **Class:** spine-hole cho hai kênh lấy. Lịch hằng ngày và lịch sự là story-detail: một lịch trên máy chạy web, phụ lục nói PRD đã khóa, không phải hai chủ.
- **Vì sao kênh lấy là lỗ:** Phụ lục giao cách lấy cho kiến trúc. Hai bộ cào có thể bỏ HTML hoặc bỏ ATS mà vẫn đúng AD-5, vì lệnh nạp chỉ thấy file.

### 4. medium · spine-hole

- **Addendum** (§ Prototype và phần v1 lấy gì): PRD khóa hình lộ trình: ba chặng, một dự án mỗi chặng, Vì sao? trên mọi nhận định. Cơ chế (có dùng mô hình ngôn ngữ hay không) thuộc kiến trúc. Cùng mục Tiền của hai tháng này: lộ trình vẫn tạo và vẫn lưu khi chặng không có liên kết khóa; liên kết, nhãn, và đếm lượt mở không xây trong kỳ này.
- **Spine:** AD-7 khóa cơ chế: FastAPI tính số trước, Ollama viết ba câu, Vì sao? trỏ về số, một lần gọi, câu mẫu khi model hỏng, chỉ ghi khi email lưu được. Không khóa ba chặng và một dự án mỗi chặng. Không nói payload lưu được khi thiếu liên kết khóa.
- **Class:** spine-hole
- **Vì sao là lỗ:** FastAPI và Next.js dùng chung payload lộ trình. «Ba câu» không buộc ba chặng với một dự án, nên hai bên có thể ghi hai hình khác nhau. Liên kết khóa là story-detail (không xây), trừ khi một bên biến nó thành trường bắt buộc của payload — spine không cấm điều đó.

### 5. medium · spine-hole

- **Addendum** (§ Tiền của hai tháng này; § Prototype và phần v1 lấy gì): Tín hiệu sớm là câu thành phố đang có việc mới vì một sự kiện, và chưa có cách phát hiện. Thẻ thành phố xây với câu chưa ghi nhận. Cách tính dự báo 18 tháng và cách phát hiện tín hiệu sớm để kiến trúc hoặc tuần 1 chốt. Người dùng thấy một khoảng có nhãn dự báo, hoặc một tín hiệu, hoặc câu chưa ghi nhận.
- **Spine:** AD-12 và mục Deferred: trước tuần 1 dùng câu chưa ghi nhận; công thức chờ đo. Không khóa đầu ra là một khoảng có nhãn, và không khóa tín hiệu là câu vì một sự kiện chứ không phải một kiểu tăng khác.
- **Class:** spine-hole
- **Vì sao là lỗ:** Trạng thái trước tuần 1 đã khớp. Khi có quy tắc đo được, API và màn có thể giao một điểm số hoặc một khoảng, và tín hiệu có thể không còn là câu sự kiện. Deferred chưa khóa hình đầu ra, nên hai đơn vị vẫn lệch được lúc thay câu chưa ghi nhận.

### 6. low · contradiction

- **Addendum** (§ Cách lưu lộ trình): Mở lại trong 14 ngày là cùng email mở đúng lộ trình đó. Giả định đang để Duy sửa: một email một lộ trình; lưu lần mới thì thay lộ trình cũ và tính lại 14 ngày.
- **Spine:** AD-8 khớp một lộ trình mỗi email, hồ sơ trên trình duyệt đến lúc lưu, token mới khi lưu hoặc gửi lại, liên kết cũ ngừng mở. «Ngày 14 không làm token hết hạn.» Không có cửa sổ 14 ngày để tính lại.
- **Class:** contradiction
- **Vì sao không phải lỗ:** Câu đã khóa («mở lại trong 14 ngày») đọc được là mốc đo, không phải hạn token. Spine đã chọn một phía (token không hết hạn), nên hai bên không tự ý đặt TTL khác nhau. Phần còn lệch là giả định «tính lại 14 ngày»: spine không giữ một mốc ngày để tính lại. Mức low vì giả định đó đang chờ Duy sửa.

### 7. low · story-detail

- **Addendum** (§ So sánh offer, bộ số để làm bản đầu): Bộ số 2026 để tính bản đầu và để hiện trong căn cứ. Giảm trừ bản thân 15,5 triệu/tháng, người phụ thuộc 6,2 triệu/tháng. Năm bậc thuế (5% đến 10 triệu, 10% đến 30 triệu, 20% đến 60 triệu, 30% đến 100 triệu, 35% phần còn lại). Người lao động 10,5% (BHXH 8%, BHYT 1,5%, BHTN 1%). Trần BHXH và BHYT 50,6 triệu từ 01/07/2026. Trần BHTN 106,2 triệu cho vùng I. Phần công ty khoảng 21,5%. Số ngày remote hiện cùng offer và không đổi thực nhận cả năm. Kết quả trên màn là ước tính, không phải tư vấn thuế. Thay khi quy định đổi.
- **Spine:** AD-9 không chép từng số. FastAPI chỉ trả bộ số thuế và BHXH 2026 trong phụ lục PRD. Trình duyệt tự tính thực nhận và khoản hụt. Không có API nhận nội dung offer.
- **Class:** story-detail
- **Vì sao không phải lỗ:** Một chủ của bộ số (FastAPI trả đúng bộ trong phụ lục). Một chỗ tính (trình duyệt). Story đọc số và quy tắc remote từ phụ lục. Không có hai bộ số hay hai chủ. Câu «ước tính» là chữ trên màn, không phải hợp đồng giữa hai đơn vị.

### 8. low · story-detail

- **Addendum:** Các mục sau có trong phụ lục và spine không nhắc, hoặc spine khóa chặt hơn mà không đổi hợp đồng giữa hai đơn vị.
  - § Tiền của hai tháng này: tiền trên web là không; hoa hồng và đếm lượt mở khóa không xây trong kỳ này; ô email đứng lúc lộ trình hiện, không kéo lên Bản đồ nhu cầu, không thành mật khẩu. Mốc đi tiếp về nguồn giữ 100%, không hạ 95% — đây là ngưỡng quyết định, không phải luật tính.
  - § Prototype và phần v1 lấy gì: lương phân vị là v2, v1 một lương công khai. Lớp chào «Đã hiểu», dải tám quý, và nút báo nguồn sai là việc của UX, PRD không bắt buộc. Spine AD-13 đi xa hơn: cấm nút, cấm thư, cấm bảng báo nguồn, để khỏi một người gửi thư và người kia ghi bảng.
  - § Dữ liệu và pipeline: khoảng 832 tin (ITviec 652, TopDev 99, ATS 78, Cốc Cốc 3) là ảnh một lúc, không phải quy mô đảm bảo. Spine không biến ảnh đó thành năng lực. Pipeline đang nằm ngoài repo là chỗ code hiện có; AD-5 đọc đúng hướng chuyển code vào `scraper/`, không gọi runtime.
  - Làm mới hằng ngày và điều kiện lịch sự đã chốt trong brief: PRD khóa, một lịch trên máy chạy web. Xem mục 3.
- **Spine:** AD-6 đã là một lương công khai (trung vị). AD-8 đã cấm mật khẩu. AD-11 là một máy chạy web. Không có giá, không có hoa hồng.
- **Class:** story-detail
- **Vì sao không phải lỗ:** Đây là phạm vi, chữ trên màn, hoặc một lịch một chủ. AD-13 không trái «không bắt buộc»; nó chốt một phía để hai người không làm hai kiểu báo nguồn.

## Đã khớp

Không lập finding cho các chỗ phụ lục đẩy sang kiến trúc và spine đã khóa một phía:

- Cách gộp lương công khai (§ Prototype và phần v1 lấy gì): AD-6 là trung vị điểm giữa, đủ 30 tin, dưới 30 thì câu chưa đủ mẫu, không đổi USD.
- Cơ chế viết lộ trình sau khi đã có số (§ Prototype và phần v1 lấy gì): AD-7 chọn Ollama một lần gọi, không mạng năm agent, câu mẫu khi hỏng.
- Một email một lộ trình, hồ sơ trên máy đến lúc lưu, không mật khẩu (§ Cách lưu lộ trình): AD-8.
- Danh kỹ năng cố định, số tuần do nhóm gán, trùng taxonomy pipeline (§ Prototype và phần v1 lấy gì): AD-10.
- Trường giữ trên tin và không lưu nguyên văn mô tả (§ Dữ liệu và pipeline): AD-4 liệt kê kỹ năng, thành phố, cấp bậc, khoảng lương, ngày đăng, link gốc; cấm mô tả.
- Câu chưa ghi nhận trước tuần 1 cho thẻ thành phố (§ Tiền của hai tháng này): AD-12. Lỗ ở mục 5 là hình đầu ra sau khi có quy tắc, không phải câu tạm.
