# Trích hành vi người dùng thấy — prototype Hải Đồ IT

Nguồn: `prototype/Hải Đồ IT — Bản đồ tuyển dụng & Cố vấn đa agent.html`.

Bản lưu là một bảng dọc gồm 11 artboard. Mỗi artboard tự chạy trạng thái của nó. Thanh điều hướng và các câu dẫn sang màn khác là liên kết tới file thiết kế anh em (`Main.dc.html`, `Pulse.dc.html`, `Paths.dc.html`, `Advisor.dc.html`, `WhatIf.dc.html`, `Passport.dc.html`, `JobCheck.dc.html`, `Employers.dc.html`, `Offer.dc.html`, `SwitchKit.dc.html`, `Global.dc.html`). Mọi con số, tên công ty trong ngoặc vuông, và câu “số liệu minh họa” trong bản này là dữ liệu prototype, không phải yêu cầu sản phẩm. Mục 6 gom các mẫu đó.

Khung chung trên mọi artboard: logo “HẢI ĐỒ · IT”; bốn nhóm “01 Thị trường”, “02 Phát triển”, “03 Ứng tuyển”, “04 Quyết định”; chip hồ sơ “Minh · Junior → Data/AI · Hà Nội” (aria: Junior 2 năm, mục tiêu Data / AI Engineer, Hà Nội). Chip trỏ về màn cố vấn. Trên màn cố vấn, hồ sơ ghi “DÙNG CHUNG MỌI MÀN”, nhưng sửa hồ sơ chỉ đổi kết quả của artboard đó.

## 1. Các màn, theo thứ tự gặp trên bảng

| # | Nhãn trên bảng | Nhãn trong thanh màn | Tiêu đề trang |
| --- | --- | --- | --- |
| 1 | Thị trường · Bản đồ nhu cầu | Bản đồ nhu cầu | Bản đồ nhu cầu tuyển dụng IT |
| 2 | Thị trường · Lương & hạn dùng kỹ năng | Lương & kỹ năng | Lương thời gian thực và hạn dùng kỹ năng |
| 3 | Thị trường · Lộ trình thật | Lộ trình thật | Lộ trình thật của người giống bạn |
| 4 | Phát triển · Cố vấn đa agent | Cố vấn đa agent | Cố vấn nghề nghiệp đa agent |
| 5 | Phát triển · Mô phỏng Nếu–thì | Mô phỏng Nếu–thì | Mô phỏng Nếu–thì |
| 6 | Phát triển · Hộ chiếu kỹ năng | Hộ chiếu kỹ năng | Hộ chiếu kỹ năng |
| 7 | Ứng tuyển · Soi tin | Soi tin tuyển dụng | Soi tin tuyển dụng |
| 8 | Ứng tuyển · Chỉ số phản hồi nhà tuyển dụng | Chỉ số phản hồi nhà tuyển dụng | Chỉ số phản hồi nhà tuyển dụng |
| 9 | Quyết định · So sánh offer & thương lượng | So sánh offer | So sánh offer và tập thương lượng |
| 10 | Quyết định · Nhảy việc | Nhảy việc | Bộ công cụ nhảy việc |
| 11 | Quyết định · Remote & Nhật | Remote & Nhật | Remote quốc tế và thị trường Nhật |

## 2. Từng màn: vào, ra, trạng thái, quy tắc đổi số

### 2.1 Bản đồ nhu cầu

Dòng mở: “Nhu cầu tuyển dụng IT, hôm nay và 18 tháng tới.” Dòng lọc: “Đang lọc theo mục tiêu của bạn: Data / AI. Kéo tầm nhìn để xem dự báo; chạm vào một thành phố để xem cơ cấu, lương và tín hiệu sớm.”

Lớp chào (mặc định bật, nút “Đã hiểu” tắt): “Chào Minh — bắt đầu từ đâu?” với ba bước “Xem Data/AI đang cần ở đâu”, “Nhận lộ trình từ Cố vấn”, “Soi tin trước khi nộp”.

Vào:

- Chip vai trò: “Tất cả”, “Backend”, “Frontend”, “Data / AI” (gắn “BẠN”), “DevOps / Cloud”, “Mobile”, “Bảo mật”. Mặc định Data / AI.
- Tầm nhìn: “NAY”, “+6T”, “+12T”, “+18T”. Mặc định NAY. Chọn mốc khác 0 thì tab thành phố chuyển sang “Dự báo”.
- Chạm thành phố trên bản đồ 3D. Nút “3D” / “2D”. Kéo xoay, kéo dọc để nghiêng. Chú thích: “Cột = tin hiện tại”, “Khung nét đứt = dự báo”, “Kéo để xoay · kéo dọc để nghiêng”.
- Tab thành phố: “Cơ cấu”, “Lương”, “Dự báo”.

Ra, khi trạng thái dữ liệu là ổn:

- Ba KPI: “TIN TUYỂN” (khi đang dự báo thì “TIN · +{n}T”), “TĂNG / NĂM”, “LƯƠNG TV” (tr ₫).
- “Cập nhật tuần 43/2026 · [NGUỒN DỮ LIỆU] · số liệu minh họa”.
- Cột thành phố: số tin, hoặc khi đang dự báo thì % chênh và số tin dự báo.
- Thẻ thành phố: vùng, số tin, % tăng, lương, cơ cấu vai trò (kèm “QA & khác”), “KỸ NĂNG ĐƯỢC SĂN ĐÓN” với “✓ = bạn đã có”.
- Khối lương thành phố, hoặc câu ẩn số (mục 3).
- “DỰ BÁO +{n} THÁNG”: khoảng tin, điểm giữa, % so với nay.
- “TÍN HIỆU SỚM”, hoặc “Chưa ghi nhận tín hiệu đáng kể cho thành phố này.”
- “Xếp hạng thành phố”: hạng, thành phố, mức cầu, tin, tăng.
- “Xu hướng kỹ năng”, “8 QUÝ GẦN NHẤT”, dải chạy tên kỹ năng và %.
- Liên kết: “Xem chi tiết lương theo kỹ năng, cấp bậc”, “Nhận lộ trình cho thị trường này”, “Kỹ năng của bạn còn “hạn” bao lâu? →”.
- Chân: “Số liệu, tín hiệu và dự báo là minh họa cho bản thiết kế — thay bằng [NGUỒN DỮ LIỆU TUYỂN DỤNG].” “HẢI ĐỒ·IT / v0.4”.

Trạng thái dữ liệu là thuộc tính xem trước của artboard, mặc định “ok”. Ba trạng thái còn lại có sẵn trên màn:

- Đang tải: vùng `aria-label` “Đang tải dữ liệu”.
- Lỗi: “Không tải được dữ liệu thị trường.” “Kết nối tới nguồn dữ liệu bị gián đoạn. Số liệu gần nhất bạn đã xem vẫn được lưu.” Nút “Thử lại” chỉ hiện toast “Đang kết nối lại nguồn dữ liệu…”.
- Rỗng: “Không có tin nào khớp bộ lọc.” “Thử chọn “Tất cả” hoặc một nhóm vai trò khác.” Nút “Bỏ lọc” đặt vai trò “Tất cả” và ép về trạng thái ổn.

Quy tắc đổi số (cơ chế trong artboard):

- Số tin một vai trò = tổng tin thành phố nếu “Tất cả”, còn lại tổng tin × tỷ trọng vai trò.
- Ở mốc +6/+12/+18 tháng, số hiện = số nay × (1 + nhịp 6 tháng của thành phố × hệ số vai trò) mũ (số tháng / 6).
- Dải dự báo = điểm giữa ± (4% + 7% × số tháng / 6).
- Khi chip đang “NAY”, thẻ dự báo của thành phố vẫn tính mốc 12 tháng.
- “TĂNG / NĂM” là trung bình tăng năm của các thành phố, có trọng số số tin.
- “LƯƠNG TV” là trung bình lương gốc thành phố × hệ số vai trò, có trọng số số tin. KPI này luôn hiện số, không qua ngưỡng 30 mẫu.
- Lương chi tiết thành phố: trung vị = lương gốc × hệ số vai trò. Số mẫu lương = làm tròn (số tin vai trò tại thành phố × 0,38). Dưới 30 thì ẩn số. Đủ 30 thì hiện trung vị, P25 = 0,8 × trung vị, P75 = 1,27 × trung vị, thang 0–60 triệu.

### 2.2 Lương theo tuần và hạn dùng kỹ năng

Tiêu đề khối: “Lương theo tuần & hạn dùng kỹ năng”. Dòng phụ: “Đọc từ tin có công khai lương. Dưới 30 mẫu, Hải Đồ ẩn con số thay vì đoán.”

Vào: chip “KỸ NĂNG” (Java, Python, Go, TypeScript, Kubernetes, AWS, LLM/RAG, PHP; mặc định Python); “THÀNH PHỐ” (Toàn quốc, Hà Nội, TP.HCM, Đà Nẵng, Hải Phòng, Quy Nhơn, Cần Thơ; mặc định Hà Nội); “CẤP BẬC” (Fresher, Junior, Mid, Senior; mặc định Junior). Công tắc “Cảnh báo hằng tháng” mặc định bật; gạt chỉ đổi trạng thái công tắc, không đổi số.

Ra khi đủ mẫu: trung vị “tr ₫ / tháng”, huy hiệu độ tin cậy, “n = … tin có công khai lương”, thang “0 / 25 / 50 / 75 / 100 tr”, P10, P25, P75, P90, “TRUNG VỊ 12 TUẦN GẦN NHẤT” và % trong 12 tuần.

Ra khi thiếu mẫu: “Chưa đủ dữ liệu”, huy hiệu “DƯỚI NGƯỠNG 30 MẪU”, và câu “Chỉ có {n} tin phù hợp — chưa đủ 30 mẫu tối thiểu. Thử mở rộng sang “Toàn quốc” hoặc cấp bậc gần kề. Bạn cũng có thể đóng góp mức lương ẩn danh để làm dày dữ liệu.” Không có form đóng góp lương trên màn này.

Hạn dùng: “Kỹ năng của Minh còn “hạn” bao lâu?” Bảng “CẦU 8 QUÝ”, “XU HƯỚNG”, “NỬA ĐỜI CÒN LẠI”. Chọn một dòng thì mở “CHI TIẾT”, “LỐI CHUYỂN ĐỀ XUẤT”, “KIẾN THỨC TÁI DÙNG”, “THỜI GIAN CHUYỂN”, liên kết “Mô phỏng lối chuyển này”. Chú thích: ““Nửa đời” = thời gian ước tính để nhu cầu giảm còn một nửa nếu xu hướng giữ nguyên. Dữ liệu minh họa.” Chân “HẢI ĐỒ·IT / v0.2”.

Quy tắc đổi số:

- Trung vị = lương gốc cấp bậc × hệ số kỹ năng × hệ số thành phố.
- Số mẫu = làm tròn (số tin quốc gia của kỹ năng × tỷ lệ thành phố × tỷ lệ cấp bậc). Ngưỡng mặc định 30.
- n ≥ 100: “ĐỘ TIN CẬY CAO”. 30 ≤ n < 100: “ĐỘ TIN CẬY TRUNG BÌNH”. n < 30: ẩn phân vị và hiện câu thiếu mẫu.
- Phân vị khi hiện: P10 = 0,62, P25 = 0,8, P75 = 1,27, P90 = 1,6 lần trung vị. Đường 12 tuần là đường mẫu luôn đi lên, nhãn luôn có dấu cộng.
- Nửa đời đứng riêng khỏi bộ lọc lương. Tốc độ quý lấy từ 8 mốc cầu. Trên +1%/quý: “ĐANG LÊN”, “Đang tăng giá trị”. Dưới −1%/quý: “SUY GIẢM”, nửa đời “~{x} năm”. Còn lại: “ỔN ĐỊNH”, “Bền vững”. Chỉ kỹ năng suy giảm mới có lối chuyển.

### 2.3 Lộ trình thật

Dòng mở: “Minh khởi đầu từ PHP — đây là những gì đã xảy ra với người cùng điểm xuất phát, kèm thời gian và mức lương.”

Vào: “ĐIỂM XUẤT PHÁT” — “Junior PHP · giống bạn” hoặc “Fresher QA”. Biểu đồ ba cột “XUẤT PHÁT”, “NĂM 1–2”, “NĂM 3–4”. “Vuốt ngang để xem toàn bộ biểu đồ”. “ĐIỂM ĐẾN SAU 3–4 NĂM · CHẠM ĐỂ SOI”.

Ra: “{n} hồ sơ ẩn danh · 2019–2026”. Khối “CON ĐƯỜNG ĐANG SOI”: % , “THỜI GIAN TRUNG VỊ”, “LƯƠNG TRUNG VỊ”, “SỐ HỒ SƠ”, “CHẶNG GIỮA PHỔ BIẾN NHẤT”, “KỸ NĂNG HỌ ĐÃ BỔ SUNG”. Liên kết “Mô phỏng con đường này cho bạn”. Chân: “Hồ sơ được ẩn danh và gộp nhóm; nhóm dưới 20 người không hiển thị. Mọi số liệu là minh họa.” “HẢI ĐỒ·IT / v0.3”.

Quy tắc đổi số: bảng % và nhãn điểm đến gắn cứng theo điểm xuất phát. Số hồ sơ tại điểm đến = làm tròn (tổng hồ sơ × % điểm đến / 100). Câu “dưới 20 người” là dòng chữ trên màn; hai nhóm mẫu (1.240 và 860) đều nằm trên ngưỡng đó.

### 2.4 Cố vấn đa agent

Tiêu đề: “Cố vấn đa agent — lộ trình 90 ngày của riêng bạn”. Dòng phụ: “Agent điều phối chia việc cho 4 agent chuyên trách. Mọi kết quả đều có nút Vì sao? để xem nguồn.”

Vào, khối “Hồ sơ của Minh”:

- “MỤC TIÊU NGHỀ NGHIỆP”: Backend Engineer, Data / AI Engineer (mặc định), DevOps / Cloud Engineer, Frontend Engineer, Mobile Engineer.
- “KINH NGHIỆM”: thanh 0–10 năm. Nhãn “{n} năm · {cấp}”. 0–1 năm Fresher, 2–3 Junior, 4–6 Mid-level, 7–10 Senior. Mặc định 2 năm · Junior.
- “THÀNH PHỐ ƯU TIÊN”: Không giới hạn, Hà Nội (mặc định), TP. Hồ Chí Minh, Đà Nẵng, Hải Phòng, Quy Nhơn, Cần Thơ.
- “KỸ NĂNG ĐANG CÓ”: bấm để thêm hoặc bỏ. Mặc định Python, SQL, Git, JavaScript, Docker.

Nút “Chạy đa agent” / khi xong thì “Chạy lại” / khi đang chạy thì “Các agent đang làm việc…”. Nút “Đặt lại” trả hồ sơ về mặc định.

Ra:

- “5 AGENT” và pha “SẴN SÀNG” / “ĐANG CHẠY” / “HOÀN TẤT”.
- Nút mạng: “Điều phối / ORCHESTRATOR + PHẢN BIỆN”, “Trinh sát thị trường / MARKET SCOUT”, “Phân tích kỹ năng / SKILL GAP”, “Kiến trúc lộ trình / ROADMAP”, “Huấn luyện hồ sơ / CV COACH”. Nhãn nút: “SẴN SÀNG”, “ĐANG CHỜ”, “ĐANG XỬ LÝ”, “HOÀN TẤT”.
- Nhật ký “agents.log”, dòng lệnh `$ haido advisor --profile minh.json`, đếm “BƯỚC i/n”.
- Trước khi chạy: “Hồ sơ của Minh đã sẵn sàng. Bấm “Chạy đa agent” để nhận kế hoạch 90 ngày.” Đang chạy: “Các agent đang phân tích hồ sơ của bạn…”.
- Sau khi chạy, nếu sửa hồ sơ: “Hồ sơ đã thay đổi so với lần chạy trước — bấm “Chạy lại” để các agent cập nhật kết quả.”
- “Kết quả tổng hợp”: “Mức độ phù hợp vai trò” (% từng vai trò, vai trò mục tiêu được đánh dấu), “Khoảng cách kỹ năng” (“THIẾU {n} KỸ NĂNG · ≈ {tuần} TUẦN HỌC” hoặc “ĐỦ KỸ NĂNG CỐT LÕI”), “Lộ trình 90 ngày” ba chặng “NGÀY 01 – 30”, “NGÀY 31 – 60”, “NGÀY 61 – 90” kèm kỹ năng và “Dự án: …”. Chặng không có kỹ năng thiếu thì hiện “Đào sâu kỹ năng sẵn có”. Tiếp “Thị trường cho bạn” (hạng, thành phố, số tin, “+{%} / năm”), “Điểm nhấn cho CV”.
- Liên kết: “Xem nhu cầu các vai trò trên bản đồ →”, “Mô phỏng: học các kỹ năng còn thiếu →”, “Nộp dự án để lấy hộ chiếu kỹ năng →”, “Xem dự báo 18 tháng trên bản đồ →”, “Soi tin trước khi nộp CV →”.
- Chân: “Kết quả là gợi ý tham khảo, dựa trên dữ liệu minh họa — thay bằng [NGUỒN DỮ LIỆU TUYỂN DỤNG].” “HẢI ĐỒ·IT / v0.4”.

“Vì sao?” mở tấm “VÌ SAO? · AGENT PHẢN BIỆN”: tiêu đề khối, “ĐỘ TIN CẬY” %, “GIỮ LẠI”, “BỊ LOẠI”, công tắc “Hiện nhận định bị loại” (mặc định bật), từng nhận định “ĐÃ KIỂM CHỨNG” hoặc “BỊ LOẠI”, nguồn loại “TIN TUYỂN” / “SỐ LIỆU” / “HỒ SƠ”, “Lý do loại:”, nút “Báo nguồn sai hoặc đã cũ” (toast “Đã ghi nhận. Agent phản biện sẽ kiểm tra lại nguồn này.”), nút đóng “✕”.

Quy tắc đổi số: % phù hợp = số kỹ năng yêu cầu mà hồ sơ đang có / số kỹ năng yêu cầu. Số tuần = tổng tuần học của kỹ năng còn thiếu. Thị trường = làm tròn (tin IT của thành phố × tỷ trọng vai trò). Lấy 3 thành phố cao nhất; nếu đã chọn một thành phố thì thành phố đó được đưa lên đầu. Kỹ năng thiếu được chia đều vào 3 chặng 30 ngày. Nhật ký và điểm tin cậy trong tấm “Vì sao?” là kịch bản viết sẵn theo vai trò, không tính lại từ hồ sơ ngoài danh sách kỹ năng.

### 2.5 Mô phỏng Nếu–thì

Dòng mở: “Thêm kỹ năng giả định vào hồ sơ của Minh — xem số tin, lương và bản đồ thay đổi trước khi bỏ công học.”

Vào: “HỒ SƠ CỦA MINH · CỐ ĐỊNH” (Python, SQL, Git, JavaScript, Docker — không sửa trên màn này). “CẤP BẬC”: Fresher, Junior (mặc định), Mid, Senior. “KỸ NĂNG GIẢ ĐỊNH · CHẠM ĐỂ THÊM / BỚT”. Mặc định đã chọn LLM/RAG và AWS. “Xoá kịch bản” xóa hết kỹ năng giả định. Khối “Nên học gì tiếp?” có nút “+ Thêm” trên từng kỹ năng chưa chọn.

Ra: “THỜI GIAN HỌC” (“{tuần} tuần · ~{tháng} tháng”, hoặc “Chưa có kỹ năng giả định”). “TIN ĐỦ ĐIỀU KIỆN” trước / sau / chênh. “LƯƠNG KỲ VỌNG (TV)” trước / sau / chênh “tr ₫ / tháng”. “TIN MỞ / TUẦN HỌC” và chữ “hiệu suất của kịch bản”. “BẢN ĐỒ TRƯỚC / SAU” với “Trước”, “Sau”. “THAY ĐỔI THEO THÀNH PHỐ”, chú thích “Cột trái: hiện tại · cột phải: sau kịch bản”. “Vai trò được mở khoá” với “ĐỘ PHỦ KỸ NĂNG” trước → sau. “Nên học gì tiếp?” / “XẾP THEO TIN MỞ / TUẦN”: hạng, tên, “+{n} tin · {tuần} tuần · {tin/tuần}”. Liên kết “Học xong? Kiểm chứng bằng Hộ chiếu kỹ năng →”. Chân: “Mô hình ước tính trên dữ liệu minh họa — thay bằng [NGUỒN DỮ LIỆU TUYỂN DỤNG].” “HẢI ĐỒ·IT / v0.2”.

Không có trạng thái ẩn lương. Lương kỳ vọng luôn là một con số.

Quy tắc đổi số: độ phủ vai trò = kỹ năng yêu cầu đã có / kỹ năng yêu cầu. Tin một thành phố = tổng theo vai trò của (tin thành phố × tỷ trọng × độ phủ × độ phủ). Lương = lương gốc cấp bậc + 0,6 × tổng phụ trội kỹ năng × (1 + 0,25 × bậc cấp). Gốc cấp: Fresher 10, Junior 16, Mid 28, Senior 45 (triệu). Hiệu suất = số tin tăng thêm / số tuần học. Danh “nên học gì tiếp” xếp kỹ năng chưa thêm theo hiệu suất đó.

### 2.6 Hộ chiếu kỹ năng

Dòng mở: “Nộp repo dự án trong lộ trình — agent review theo yêu cầu tin tuyển, ký hộ chiếu nhà tuyển dụng tự xác minh được, rồi ghép việc lại.”

Bốn bước: “Học / Theo lộ trình 90 ngày từ agent cố vấn”, “Chứng minh / Nộp repo dự án thực hành”, “Kiểm chứng / Agent review theo yêu cầu tin tuyển”, “Ghép việc / Hộ chiếu mở thêm cơ hội”.

Vào: chọn một dự án trong “LỘ TRÌNH DATA / AI” / “DỰ ÁN TỪ LỘ TRÌNH 90 NGÀY” (ba chặng ngày 01–30, 31–60, 61–90; mặc định chặng 61–90). Ô “LINK REPO”, placeholder `https://github.com/[tên-bạn]/[tên-repo]`. Nút chạy review.

Ra: “AGENT REVIEW” chạy 5 nhịp viết sẵn (“Clone repo & đọc cấu trúc”, “Đọc README, chạy được không?”, “Chạy bộ kiểm thử”, “Đối chiếu yêu cầu trong tin tuyển”, “Ký hộ chiếu kỹ năng”). Nội dung ô repo không được đọc. “CHẤM THEO YÊU CẦU TRONG TIN TUYỂN DỤNG”: năm tiêu chí, điểm /4, mức “Chưa đạt / Cơ bản / Khá / Vững / Thành thạo”. Thẻ “HỘ CHIẾU KỸ NĂNG · SKILL PASSPORT” mang tên Minh, “Data / AI Engineer · Junior”, “ĐÃ KIỂM CHỨNG”, kỹ năng “MỚI”, “MÃ XÁC MINH HD-2026-7F3A-91C2”, “Cấp ngày 22/10/2026 · nhà tuyển dụng xác minh tại [ĐƯỜNG DẪN XÁC MINH]”. “Sao chép link xác minh” toast đã sao chép mã. “Tải PDF đính kèm CV” toast “Đang tạo PDF hộ chiếu kỹ năng…”. Khối “Ghép việc lại” / “BƯỚC 4 / 4”: “TRƯỚC” “tin phù hợp ≥ 70%”, “SAU”, chênh, “VỪA MỞ KHOÁ” ba tin (chức danh, công ty, thành phố, % khớp). Liên kết “Cập nhật lộ trình với cố vấn”. Chân: “Kết quả review, mã xác minh và tin tuyển là minh họa cho bản thiết kế.” “HẢI ĐỒ·IT / v0.2”.

Quy tắc đổi số: điểm, mã, và danh sách việc gắn cứng theo dự án đang chọn. Mốc trước luôn 1.120 tin; mốc sau = 1.120 + một số cộng sẵn của dự án.

### 2.7 Soi tin tuyển dụng

Tiêu đề: “Soi tin: có thật không, AI làm được bao nhiêu?” Dòng phụ: “Agent kiểm định chấm độ tin cậy; agent chỉ số AI tách mô tả thành đầu việc.”

Vào: ô “Link hoặc nội dung tin tuyển dụng”, nút “Soi tin” (khi đang chạy: “Đang soi…”). Danh “TIN VỪA SOI” bốn tin mẫu, bấm để chọn. “Báo cáo tin” toast “Đã gửi báo cáo. Cảm ơn bạn đã giúp cộng đồng.” “Theo dõi” toast “Đã theo dõi — Hải Đồ sẽ báo khi tin thay đổi.”

Ra: điểm /100, phán quyết, lời khuyên, từng tín hiệu, “Chỉ số ảnh hưởng AI” với ba mốc “Con người dẫn dắt”, “AI hỗ trợ”, “Tự động hoá cao”, “TÁCH THEO ĐẦU VIỆC”, “KỸ NĂNG BỀN NÊN ĐẦU TƯ”. Liên kết “Công ty này phản hồi ứng viên ra sao? →”. Chân: “Tin, công ty và điểm số là ví dụ minh họa. Điểm tin cậy là cảnh báo tham khảo, không phải kết luận pháp lý.” “HẢI ĐỒ·IT / v0.2”.

Trạng thái rủi ro cao: “Không phân tích tin này: agent kiểm định đã gắn cờ rủi ro cao. Đừng nộp hồ sơ hay chuyển tiền trước khi xác minh.” Khối đầu việc và chỉ số AI bị giấu.

Bốn bước soi viết sẵn: “Tra mã số thuế & pháp nhân”, “Dò tin trùng lặp, lịch sử làm mới”, “So khoảng lương với thị trường”, “Tách đầu việc, chấm chỉ số AI”. Bấm “Soi tin” không phân tích chữ trong ô: nó chạy hoạt ảnh rồi nhảy sang tin mẫu kế tiếp và xóa ô.

Quy tắc đổi số: ≥ 75 “ĐÁNG TIN” và “Không phát hiện dấu hiệu bất thường. Có thể ứng tuyển như bình thường.” 40–74 “CẦN THẬN TRỌNG” và “Có thể là tin treo để gom hồ sơ. Hỏi rõ tiến độ tuyển trước khi đầu tư thời gian.” Dưới 40 “RỦI RO CAO” và “Nhiều dấu hiệu lừa đảo. Không nộp phí, không gửi giấy tờ cá nhân.” Chỉ số AI = trung bình % các đầu việc. Đầu việc ≥ 60 “Tự động hoá cao”, 35–59 “AI hỗ trợ”, dưới 35 “Con người dẫn dắt”.

### 2.8 Chỉ số phản hồi nhà tuyển dụng

Tiêu đề: “Công ty nào trả lời ứng viên, công ty nào “mất hút”?” Dòng phụ: “Từ trải nghiệm ứng tuyển ẩn danh. Chỉ hiển thị công ty có từ 20 trải nghiệm trở lên.”

Vào: “SẮP XẾP” — “Hồi âm nhanh nhất”, “Ít “mất hút” nhất”, “Quy trình ngắn nhất”. Bấm một dòng công ty. Khối “Đóng góp trải nghiệm” / “ẨN DANH”: chọn công ty, “HỒI ÂM ĐẦU TIÊN SAU” (< 3 ngày, 3–7 ngày, 1–2 tuần, 2–4 tuần, > 1 tháng, Chưa có), “SỐ VÒNG ĐÃ QUA” (số, 0–8), nút “Gửi trải nghiệm”.

Ra: bảng “CÔNG TY”, “HỒI ÂM SAU”, “TỶ LỆ HỒI ÂM”, “SỐ VÒNG”, “CẢ QUY TRÌNH”, “ĐÁNH GIÁ”. Chi tiết: “{n} trải nghiệm · 6 tháng gần nhất”, “PHỄU ỨNG TUYỂN (TRÊN 100 HỒ SƠ)” với “Nộp hồ sơ”, “Được hồi âm”, “Phỏng vấn vòng 1”, “Vòng cuối”, “Nhận offer”, “THỜI GIAN ĐẾN LẦN HỒI ÂM ĐẦU TIÊN” (< 3 ngày, 3–7 ngày, 1–2 tuần, 2–4 tuần, Không hồi âm), “NÓI LƯƠNG Ở”, “BÀI TEST VỀ NHÀ”, “BÁO KẾT QUẢ KHI TRƯỢT”. Liên kết “Soi một tin của công ty này trước khi nộp →”. Sau khi gửi: “Cảm ơn bạn!” và “Trải nghiệm được gộp vào chỉ số sau khi kiểm tra trùng lặp. Không lưu tên hay email của bạn.” Gửi không đổi bảng. Chân: “Tên công ty dạng giữ chỗ; mọi số liệu là minh họa cho bản thiết kế.” “HẢI ĐỒ·IT / v0.3”.

Quy tắc đổi số: điểm xếp loại = tỷ lệ hồi âm − (số ngày hồi âm × 2). ≥ 70 “PHẢN HỒI TỐT”, ≥ 40 “TRUNG BÌNH”, còn lại “HAY MẤT HÚT”. Câu “từ 20 trải nghiệm” là điều kiện hiện dòng; bảy công ty mẫu đều có từ 37 trải nghiệm trở lên, nên màn không diễn trạng thái bị giấu.

### 2.9 So sánh offer và tập thương lượng

Tiêu đề khối: “So sánh offer & tập thương lượng”. Dòng phụ: “So tiền thật về tay theo biểu thuế 2026 — và soi công ty đóng bảo hiểm trên lương thật hay mức thấp hơn.”

Vào, “Nhập hai offer”, hai cột “OFFER A” / “OFFER B”:

- “NGƯỜI PHỤ THUỘC”: 0, 1, 2, 3. Mặc định 0.
- Tên công ty. Mặc định “[Công ty A]”, “[Công ty B]”.
- “LƯƠNG / THÁNG (TR ₫)”. Mặc định 24 và 27.
- “LOẠI LƯƠNG”: “Gross” / “Net”. Mặc định Gross.
- “CĂN CỨ ĐÓNG BẢO HIỂM”: “Trên lương thật” / “Trên mức thấp hơn”. A mặc định lương thật, B mặc định mức thấp hơn.
- “MỨC ĐÓNG BẢO HIỂM (TR ₫)”. Mặc định 5,31.
- “THƯỞNG (THÁNG)”, “PHỤ CẤP (TR)”, “REMOTE / TUẦN”. A mặc định thưởng 1, phụ cấp 1, remote 2. B mặc định 0.

Ra: câu offer nào “cho thực nhận cao hơn ~{n} tr ₫ / năm”, hoặc “Hai offer gần như ngang nhau về thực nhận.” Nếu offer thắng đóng bảo hiểm trên mức thấp hơn và khoản hụt trên 0,5 triệu/năm thì thêm “Nhưng hụt ~{n} tr ₫ bảo hiểm mỗi năm”. Mỗi offer: “THỰC NHẬN / NĂM”, “GROSS”, “NET / THÁNG”, “THUẾ / THÁNG”, thanh “Thực nhận / Bảo hiểm / Thuế TNCN”. Khi đóng thấp hơn: “Bảo hiểm đóng trên {mức} thay vì lương thật: mỗi năm hụt ~{n} tr ₫ tiền đóng vào quỹ (cả phần công ty). Hưu trí, thai sản, trợ cấp thất nghiệp sẽ tính trên mức thấp này.” Dòng “Remote {n} ngày/tuần · thưởng {n} tháng · phụ cấp {n} tr”.

Khối “Tham số tính (kỳ tính thuế 2026)” hiện đúng các mốc này: “Giảm trừ bản thân 15,5 tr/tháng · người phụ thuộc 6,2 tr/tháng (Nghị quyết 110/2025/UBTVQH15).” “Biểu thuế 5 bậc: 5% đến 10 tr · 10% đến 30 tr · 20% đến 60 tr · 30% đến 100 tr · 35% trên 100 tr.” “Người lao động đóng 10,5% (BHXH 8%, BHYT 1,5%, BHTN 1%); trần BHXH/BHYT 50,6 tr (từ 01/7/2026), trần BHTN 106,2 tr (vùng I). Phần công ty ~21,5%.” “Kết quả là ước tính tham khảo, không thay thế tư vấn thuế.”

Liên kết: “Đã chọn offer? Tính ngày nghỉ việc cũ để giữ thưởng tháng 13 →”.

Khối “PHÒNG TẬP THƯƠNG LƯỢNG”: “Tập với agent HR trước khi trả lời thật.” Nhãn tĩnh “THỊ TRƯỜNG · DATA ENGINEER · JUNIOR · HÀ NỘI”, “n = 186 tin · minh họa”, “Thang 0–40 tr ₫”, “Hộp: P25 16 – P75 26 · vạch: trung vị 20”, mốc “OFFER 24”. “Agent HR (mô phỏng)”, “vai: trưởng phòng nhân sự · ngân sách chặt”. Ba cách trả lời: “Neo theo dữ liệu P75”, “Đổi lấy lợi ích khác”, “Chấp nhận ngay”. Chưa chọn thì huấn luyện viên nói “Chọn một cách trả lời để agent chấm điểm và góp ý.” Đã chọn thì hiện hội thoại, điểm, và checklist “✓” / “✕”. Chân: “Tính toán tham khảo, không phải tư vấn thuế hay pháp lý. Dữ liệu thị trường là minh họa.” “HẢI ĐỒ·IT / v0.2”.

Quy tắc đổi số tiền:

- Gross nhập thẳng. Net được dò ngược ra gross sao cho thực nhận tháng khớp số đã nhập.
- Mức đóng bảo hiểm = lương gross nếu “Trên lương thật”; nếu “Trên mức thấp hơn” thì lấy mức đã nhập, nhưng không dưới 5,31 và không quá gross.
- Phần người lao động = 9,5% trên min(mức đóng, 50,6) + 1% trên min(mức đóng, 106,2). Phần công ty trong khoản hụt = 20,5% trên cùng trần 50,6 + 1% trên trần 106,2.
- Giảm trừ = 15,5 + 6,2 × số người phụ thuộc.
- Thuế tháng và thuế năm theo năm bậc ở trên. Thực nhận năm = 12 × (gross + phụ cấp) + thưởng × gross − 12 × bảo hiểm − thuế năm.
- Khoản hụt năm = 12 × (phần người lao động hụt + phần công ty hụt) so với đóng trên full gross.
- Hộp P25/P75 và “n = 186” không đổi theo offer. Mốc “BẠN” chỉ nhảy khi chọn một cách trả lời (27 hoặc 24 triệu). Điểm huấn luyện là điểm viết sẵn của từng câu, không chấm từ số offer.

### 2.10 Nhảy việc

Tiêu đề: “Nhảy việc: “lint” hợp đồng & chọn ngày nghỉ”. Dòng phụ: “Gạch chân điều khoản trái Bộ luật Lao động 2019, rồi tính ngày nộp đơn để giữ thưởng tháng 13 và kịp mùa tuyển.”

Vào: nút “Tải hợp đồng khác (PDF, DOCX)”. Bấm chỉ toast “Chọn tệp hợp đồng — agent pháp lý sẽ đọc trong khoảng 30 giây.” Không có ô chọn tệp; hợp đồng trên màn là bản gắn sẵn `hop-dong-lao-dong_[cong-ty-A].pdf · bản minh họa`. Bấm một dòng để soi. “LOẠI HỢP ĐỒNG HIỆN TẠI” quyết “Báo trước tối thiểu”. “NGÀY CHI THƯỞNG THÁNG 13” (ô ngày, mặc định 2027-01-29). “ĐIỀU KIỆN NHẬN THƯỞNG (THEO DÒNG 7)”: “Phải còn làm việc” (mặc định) hoặc “Tính theo tháng làm”. “LƯƠNG GROSS HIỆN TẠI (TR ₫)”, mặc định 18.

Ra: đếm “trái luật”, “cần cân nhắc”, “lưu ý”, “ổn”. Tấm “AGENT PHÁP LÝ · {n} PHÁT HIỆN”: mức, “DÒNG”, điều luật, tiêu đề, vì sao, “ĐỀ XUẤT SỬA”. “Gợi ý tham khảo, không phải tư vấn pháp lý. Điều khoản quan trọng nên hỏi luật sư.”

Đồng hồ: “BẮT ĐẦU PHỎNG VẤN” (“~6 tuần trước ngày nộp đơn”), “NỘP ĐƠN NGHỈ”, “NGÀY LÀM CUỐI”, “THƯỞNG GIỮ ĐƯỢC” (“ước tính 1 tháng lương”). “DÒNG THỜI GIAN · 22/10/2026 → 31/05/2027”, “Mùa cao điểm: dữ liệu minh họa”, nhãn “MÙA TUYỂN CAO ĐIỂM”. Một câu chuyện tóm tắt ngày. Liên kết “So sánh offer mới trước khi nộp đơn →”. Chân: “Căn cứ: Bộ luật Lao động 2019 (Điều 17, 25, 26, 35, 127). Hợp đồng là ví dụ minh họa. Tết Nguyên đán 2027: 06/02/2027.” “HẢI ĐỒ·IT / v0.3”.

Quy tắc đổi ngày:

- Báo trước: không xác định thời hạn 45 ngày, xác định thời hạn 30 ngày, ngắn “3 ngày làm việc”.
- Nếu “Phải còn làm việc”: nộp đơn = ngày chi thưởng + 1, chú thích “1 ngày sau khi nhận thưởng”.
- Nếu “Tính theo tháng làm”: nộp đơn = 15/02/2027 trừ số ngày báo trước trừ 14 ngày, chú thích “canh ngày làm cuối sát mùa tuyển”. Câu chuyện nói không cần chờ ngày chi.
- Ngày nộp đơn không sớm hơn 23/10/2026.
- Phỏng vấn = nộp đơn − 42 ngày, không sớm hơn 22/10/2026. Ngày làm cuối = nộp đơn + số ngày báo trước.
- Mùa cao điểm vẽ từ 15/02/2027 đến 30/04/2027. Nếu ngày làm cuối rơi từ 21 ngày trước mùa đến hết mùa, câu chuyện nói “rơi đúng mùa tuyển cao điểm sau Tết”; không thì “nằm ngoài mùa cao điểm, cân nhắc dời lịch.”
- “THƯỞNG GIỮ ĐƯỢC” hiện bằng số lương gross đã nhập (tr ₫) ở cả hai điều kiện thưởng.

### 2.11 Remote và Nhật

Tiêu đề: “Remote nước ngoài hay onsite Nhật — có thật sự hơn ở nhà?” Dòng phụ: “Quy về cùng thước đo: thực nhận và để dành mỗi tháng, sau thuế, chi phí tự lo và những thứ không có trên bảng lương.”

Vào:

- “A · LÀM TRONG NƯỚC”: “LƯƠNG GROSS / THÁNG (TR ₫)” mặc định 18, “CHI PHÍ SỐNG Ở VN / THÁNG (TR ₫)” mặc định 12. Chú thích “Bảo hiểm 10,5% trên lương thật · giảm trừ 15,5 tr · biểu thuế 5 bậc”.
- “B · REMOTE CHO CÔNG TY NƯỚC NGOÀI”: “USD / THÁNG” mặc định 1.200, “TỶ GIÁ USD (₫)” mặc định 26.000, “HÌNH THỨC” “Freelance · tự khai thuế” (mặc định) hoặc “Qua EOR tại VN”, “CHI PHÍ TỰ LO / THÁNG (TR ₫)” mặc định 2, “MÚI GIỜ ĐỐI TÁC”: “Châu Á – Úc”, “Châu Âu”, “Mỹ”.
- “C · ONSITE NHẬT BẢN”: “LƯƠNG JPY / THÁNG” mặc định 280.000, “TỶ GIÁ JPY (₫)” mặc định 170, “THUẾ + BẢO HIỂM (%)” mặc định 22, “SINH HOẠT JPY / THÁNG” mặc định 160.000. Chú thích “Tỷ lệ khấu trừ là ước tính — tự điều chỉnh theo hợp đồng thực tế”.

Ra: “Quy về cùng thước đo” / “TRIỆU ₫ / THÁNG”. Ba cột “Thực nhận” và “Để dành”. Cột để dành cao nhất gắn “ĐỂ DÀNH NHIỀU NHẤT”. Ghi chú: A “Có BHXH, BHYT, BHTN đầy đủ.” B freelance “Không có BHXH bắt buộc, đã trừ {n} tr chi phí tự lo.” B qua EOR “EOR đóng bảo hiểm như nhân viên trong nước.” Cả hai kèm giờ làm: Châu Á – Úc “trùng giờ hành chính”, Châu Âu “làm lệch sang chiều tối”, Mỹ “thường họp đêm khuya”. C “Để dành = thực nhận trừ {n} JPY sinh hoạt, quy đổi về VND.”

Bảng “Những thứ không có trên bảng lương”: “Bảo hiểm xã hội & hưu trí”, “Giờ làm việc”, “Rủi ro tỷ giá”, “Ổn định hợp đồng”, “Gần gia đình”. Chấm “●●● tốt · ●●○ trung bình · ●○○ bất lợi”. Freelance làm BHXH và ổn định hợp đồng xuống mức bất lợi; qua EOR thì BHXH tốt và hợp đồng trung bình. Múi giờ chỉ đổi hàng “Giờ làm việc”.

“Lộ trình BrSE — kỹ sư cầu nối thị trường Nhật”, “THỜI LƯỢNG ƯỚC TÍNH, TÙY NGƯỜI”: “N5→N4 / Nền tảng tiếng Nhật / ~4–6 tháng”, “N3 / Đọc tài liệu kỹ thuật / ~6–9 tháng”, “N2 / Giao tiếp với khách hàng / ~9–12 tháng”, “BrSE / Kỹ sư cầu nối / kèm 2–3 năm kinh nghiệm”, “ONSITE / Làm việc tại Nhật / tùy cơ hội”. Liên kết “So sánh chi tiết các offer trong nước →”. Chân: “Ước tính tham khảo; cách tính thuế cho thu nhập từ nước ngoài phụ thuộc loại hợp đồng — nên hỏi chuyên gia thuế. Tỷ giá tự nhập.” “HẢI ĐỒ·IT / v0.3”.

Quy tắc đổi số:

- A: trừ bảo hiểm cùng cách 9,5% + 1% như màn offer, rồi thuế trên (gross − bảo hiểm − 15,5). Để dành = thực nhận − chi phí sống VN.
- B đổi USD sang triệu đồng. Freelance: trừ thuế trên (số đó − 15,5) rồi trừ chi phí tự lo, không trừ bảo hiểm. EOR: dùng công thức trong nước. Để dành của B vẫn trừ chi phí sống VN.
- C: thực nhận yên = lương × (1 − % khấu trừ). Để dành yên = thực nhận yên − sinh hoạt. Cả hai quy ra triệu đồng theo tỷ giá JPY.
- Cột thắng là cột có số để dành cao nhất, không phải thực nhận cao nhất.

## 3. Thành phố, kỹ năng, lương, dự báo, tín hiệu, 90 ngày, Vì sao, offer, BHXH, soi tin

### Thành phố

Bản đồ, cố vấn (phần thị trường), mô phỏng, và hộ chiếu dùng bảy thành phố: Hà Nội, Hải Phòng, Đà Nẵng, Quy Nhơn, Nha Trang, TP. Hồ Chí Minh, Cần Thơ.

Hai chỗ chọn thành phố hẹp hơn bảy:

- Lương theo tuần: “Toàn quốc” cộng sáu thành phố, nhãn “TP.HCM”, không có Nha Trang.
- Thành phố ưu tiên của cố vấn: “Không giới hạn” cộng sáu thành phố, không có Nha Trang trong danh chọn. Nha Trang vẫn có thể hiện ở “Thị trường cho bạn” vì danh tính lấy từ bộ bảy thành phố.

### Kỹ năng người dùng thấy

- Bản đồ, dấu ✓ trên kỹ năng thành phố nếu trùng Python, SQL, Git, JavaScript, Docker.
- Lương: tám kỹ năng lọc ở mục 2.2. Hạn dùng: jQuery, PHP, SQL, JavaScript, Python, Docker.
- Cố vấn, kho chọn: Python, JavaScript, TypeScript, Java, SQL, React, Node.js, Docker, Kubernetes, AWS, Linux, CI/CD, Machine Learning, LLM/RAG, System Design, Kotlin/Swift, Git.
- Mô phỏng, phần giả định: TypeScript, Java, React, Node.js, Kubernetes, AWS, Linux, CI/CD, Machine Learning, LLM/RAG, System Design, Kotlin/Swift. Hồ sơ cố định giống năm kỹ năng mặc định của cố vấn.
- Xu hướng 8 quý trên bản đồ: LLM / RAG, Kubernetes, Go, TypeScript, Python, Rust, PHP.

### Lương — ngưỡng trích đúng chữ

Trên bản đồ, khi số mẫu dưới 30:

“Chỉ có {n} tin công khai lương — dưới 30 mẫu, Hải Đồ không hiển thị con số.”

Trên màn lương:

“Đọc từ tin có công khai lương. Dưới 30 mẫu, Hải Đồ ẩn con số thay vì đoán.”

“Chỉ có {n} tin phù hợp — chưa đủ 30 mẫu tối thiểu.”

Huy hiệu: “ĐỘ TIN CẬY CAO” từ 100 tin, “ĐỘ TIN CẬY TRUNG BÌNH” từ 30 đến dưới 100, “DƯỚI NGƯỠNG 30 MẪU” khi dưới 30.

Cách đếm mẫu trên bản đồ: làm tròn (số tin của vai trò tại thành phố × 0,38). KPI “LƯƠNG TV” không dùng ngưỡng này.

Cách đếm trên màn lương: làm tròn (số tin quốc gia của kỹ năng × tỷ lệ thành phố × tỷ lệ cấp bậc).

Trong tấm “Vì sao?” của lộ trình, một nhận định bị loại có lý do viết sẵn: “Chỉ 18 tin vị trí RAG có công khai lương — dưới ngưỡng 30 mẫu.” Số 18 nằm trong kịch bản minh họa của tấm đó.

Mô phỏng Nếu–thì luôn hiện “LƯƠNG KỲ VỌNG”, không có nhánh ẩn.

### Dự báo

Tầm nhìn trên bản đồ: hôm nay, +6 tháng, +12 tháng, +18 tháng. Tiêu đề màn nói “hôm nay và 18 tháng tới.” Công thức và dải sai số ở mục 2.1. Thẻ dự báo khi đang đứng ở “NAY” vẫn tính +12 tháng.

### Tín hiệu sớm

Nhãn “TÍN HIỆU SỚM”. Mỗi tín hiệu có loại, câu chữ, và “tác động sau {khoảng}”. Hết tín hiệu thì “Chưa ghi nhận tín hiệu đáng kể cho thành phố này.” Trong dữ liệu gắn trên bản đồ, Nha Trang và Cần Thơ rơi vào câu này. Các thành phố kia có tín hiệu loại “TRUNG TÂM DỮ LIỆU”, “AI”, “FDI · ĐIỆN TỬ”, “BÁN DẪN”, với trễ “6–12 tháng”, “9–15 tháng”, hoặc “12–18 tháng”. Nội dung sự kiện đặt trong ngoặc vuông, xem mục 6.

### Lộ trình 90 ngày và “Vì sao?”

Có. Tiêu đề màn cố vấn dùng “lộ trình 90 ngày của riêng bạn”. Khối kết quả tên “Lộ trình 90 ngày”, ba chặng “NGÀY 01 – 30”, “NGÀY 31 – 60”, “NGÀY 61 – 90”. Hộ chiếu gọi “DỰ ÁN TỪ LỘ TRÌNH 90 NGÀY” và bước “Theo lộ trình 90 ngày từ agent cố vấn”. Nút “Vì sao?” có trên từng khối kết quả của cố vấn; tấm mở tên “VÌ SAO? · AGENT PHẢN BIỆN”.

### So sánh offer và kiểm BHXH

Cùng một màn với tập thương lượng. Kiểm bảo hiểm là cặp lựa chọn “Trên lương thật” / “Trên mức thấp hơn”, cộng ô “MỨC ĐÓNG BẢO HIỂM”, và câu hụt quỹ khi đóng thấp hơn. Không có ô nhập sổ BHXH hay mã số bảo hiểm. Tham số 10,5%, trần 50,6 tr và 106,2 tr, giảm trừ 15,5 và 6,2, biểu thuế năm bậc, nằm đúng chữ ở mục 2.9.

### Soi tin

Màn riêng “Soi tin tuyển dụng”. Người dùng dán link hoặc nội dung, bấm “Soi tin”, xem điểm /100, tín hiệu, chỉ số AI theo đầu việc, báo cáo hoặc theo dõi. Kết quả thực tế của nút soi là tin mẫu kế tiếp, như mục 2.7. Ngưỡng điểm: 75 và 40.

## 4. Tên khác với “Học gì tiếp?”, “Lộ trình 90 ngày”, “Hải trình 90 ngày”

Prototype dùng các nhãn sau.

- Màn và mục nav là “Mô phỏng Nếu–thì” (trên bảng: “Phát triển · Mô phỏng Nếu–thì”). Trong màn đó, một khối kết quả có tiêu đề “Nên học gì tiếp?” và dòng phụ “XẾP THEO TIN MỞ / TUẦN”. Chuỗi “Học gì tiếp?” không phải tên màn.
- “Lộ trình 90 ngày” là nhãn đang dùng, ở tiêu đề cố vấn, ở khối kết quả, và ở hộ chiếu (“LỘ TRÌNH 90 NGÀY”, “lộ trình 90 ngày”).
- Chuỗi “Hải trình 90 ngày” không có trong prototype.

Nhãn ngắn khác trên cùng một việc, để khỏi lẫn khi đọc:

- Bảng ghi “Lương & hạn dùng kỹ năng”; nav ghi “Lương & kỹ năng”; tiêu đề khối ghi “Lương theo tuần & hạn dùng kỹ năng”.
- Nav quyết định ghi “So sánh offer”; tiêu đề khối ghi “So sánh offer & tập thương lượng”; bảng ghi “So sánh offer & thương lượng”.
- Nav ứng tuyển ghi “Soi tin tuyển dụng”; bảng ghi “Soi tin”.

## 5. Hành vi giống sàn việc, chấm nhà tuyển dụng, hoặc soi hợp đồng

Ba cụm này có mặt trên prototype.

Ghép việc, trên hộ chiếu kỹ năng. Dòng mở nói “ghép việc lại”. Bước 4 tên “Ghép việc” / “Hộ chiếu mở thêm cơ hội”. Khối “Ghép việc lại” liệt kê ba tin với chức danh, công ty, thành phố và “%” khớp, so “TRƯỚC / SAU” số “tin phù hợp ≥ 70%”. Không có nút nộp hồ sơ, không có ô tìm tin, không có trang danh sách việc để lướt. Soi tin có danh bốn tin mẫu, “Theo dõi”, “Báo cáo tin”, và lương ghi trên tin; việc chính của màn là chấm tin, không phải nhận hồ sơ.

Chấm nhà tuyển dụng: cả màn “Chỉ số phản hồi nhà tuyển dụng”. Xếp “PHẢN HỒI TỐT”, “TRUNG BÌNH”, “HAY MẤT HÚT” từ tốc độ hồi âm, tỷ lệ hồi âm, số vòng, độ dài quy trình, phễu đến “Nhận offer”. Điều kiện hiện: “Chỉ hiển thị công ty có từ 20 trải nghiệm trở lên.” Có form “Đóng góp trải nghiệm” ẩn danh. Soi tin cũng có câu “Công ty này phản hồi ứng viên ra sao?”.

Soi hợp đồng: màn nhảy việc. Tiêu đề dùng “lint” hợp đồng. Nút tải PDF/DOCX. Khối “AGENT PHÁP LÝ” gạch “TRÁI LUẬT”, “CẦN CÂN NHẮC”, “LƯU Ý”, “ỔN”, kèm điều Bộ luật Lao động và “ĐỀ XUẤT SỬA”. Dòng chữ trên màn: “Gợi ý tham khảo, không phải tư vấn pháp lý. Điều khoản quan trọng nên hỏi luật sư.” Tệp không được đọc; bản trên màn là hợp đồng minh họa gắn sẵn. Màn offer cũng ghi “không phải tư vấn thuế hay pháp lý”. Màn soi tin ghi điểm tin cậy “không phải kết luận pháp lý”.

## 6. Dữ liệu mẫu của prototype

Cả mười một màn đều ghi số liệu là minh họa, hoặc để chỗ `[NGUỒN DỮ LIỆU]` / `[NGUỒN DỮ LIỆU TUYỂN DỤNG]`. Các mẫu dưới đây là đồ của artboard.

Hồ sơ người xem: Minh, Junior, 2 năm, mục tiêu Data / AI, Hà Nội, kỹ năng Python, SQL, Git, JavaScript, Docker. Mã hộ chiếu HD-2026-7F3A và HD-2026-7F3A-91C2, cấp 22/10/2026. Tuần dữ liệu ghi trên bản đồ và màn lương: tuần 43/2026.

Tin IT gắn trên bản đồ (tổng, % tăng/năm, lương gốc triệu): Hà Nội 3.960 / 9% / 26; Hải Phòng 420 / 21% / 19; Đà Nẵng 1.140 / 17% / 22; Quy Nhơn 260 / 14% / 18; Nha Trang 150 / 6% / 16; TP. Hồ Chí Minh 4.820 / 12% / 28; Cần Thơ 210 / 8% / 15. Tỷ trọng vai trò, nhịp 6 tháng, kỹ năng săn đón, và câu tín hiệu sớm là mảng cùng bản ghi. Tín hiệu đặt tên sự kiện trong ngoặc vuông, ví dụ “[Dự án trung tâm dữ liệu quy mô lớn]”, “[Nhà máy điện tử]”, “[Khu công viên phần mềm & AI]”.

Xu hướng 8 quý trên bản đồ: LLM / RAG +64%, Kubernetes +22%, Go +18%, TypeScript +15%, Python +12%, Rust +9%, PHP −6%.

Lương theo tuần dùng số tin quốc gia mẫu: Java 900, Python 820, Go 260, TypeScript 700, Kubernetes 300, AWS 520, LLM/RAG 210, PHP 380, rồi nhân tỷ lệ thành phố và cấp bậc. Hạn dùng dùng tám điểm cầu cho jQuery, PHP, SQL, JavaScript, Python, Docker. Lối chuyển mẫu: jQuery → “React + TypeScript”, 55%, 6 tuần; PHP → “Node.js + TypeScript”, 60%, 5 tuần.

Lộ trình thật: “Junior PHP” 1.240 hồ sơ và “Fresher QA” 860 hồ sơ, cửa sổ “2019–2026”. Điểm đến và mức lương dạng “15 → 40 tr ₫”, “12 → 35 tr ₫” gắn trong bảng của artboard, gồm “Ra khỏi ngành IT”, “Vẫn ở mức Mid”, “Remote / Freelance quốc tế”.

Cố vấn: tuần học viết sẵn (Git 1 tuần, LLM/RAG 4, Machine Learning 8, …) và ba dự án mẫu theo vai trò, ví dụ Data / AI: pipeline SQL, mô hình ML, “Chatbot RAG trên bộ tài liệu tiếng Việt”. Nhật ký kết bằng “Đối chiếu 14 nguồn · giữ 9 nhận định · loại 5 nhận định thiếu dữ liệu.” Trích dẫn tin dạng “#48850 · [Công ty Fintech A]”, “#48213 · [Công ty AI E] · Quy Nhơn”, “#47702”. Một nhận định bị loại vì “18 tin” RAG. Nhận định khác bị loại vì không có dữ liệu quản lý, cách lọc CV, chi phí sinh hoạt, hay độ dài CV.

Mô phỏng dùng cùng bộ tin và tỷ trọng bảy thành phố, lương gốc Fresher 10, Junior 16, Mid 28, Senior 45, và bảng phụ trội từng kỹ năng.

Hộ chiếu: ba repo mẫu (đường dẫn file giả), điểm /4, việc mở khóa ví dụ “Data Engineer” tại “[Công ty Logistics B]” Hà Nội 81%, “AI Engineer (LLM)” tại “[Công ty AI E]” Quy Nhơn 88%. Mốc 1.120 tin và các mức cộng 140 / 310 / 460 là hằng số của artboard.

Soi tin, bốn tin: “Backend Engineer (Go)”, “[Công ty Fintech A]”, TP.HCM, “35–50 tr”, điểm 92, “ĐĂNG 3 NGÀY TRƯỚC · LẦN ĐẦU”; “Data Analyst”, “[Công ty Logistics B]”, Hà Nội, “18–25 tr”, điểm 58, “LÀM MỚI LẦN 6 · 74 NGÀY”; “Lập trình viên làm tại nhà — không cần kinh nghiệm”, tài khoản “IT Jobs Global”, “Toàn quốc”, “60–90 tr”, điểm 12, “12 BÁO CÁO”; “QA Automation Engineer”, “[Công ty Phần mềm C]”, Đà Nẵng, “20–30 tr”, điểm 84.

Phản hồi nhà tuyển dụng: bảy tên giữ chỗ từ “[Công ty Fintech A]” đến “[Công ty Outsourcing G]”, n từ 37 đến 214, cùng phễu và câu “Nói lương ở” / “Bài test về nhà” / “Báo kết quả khi trượt”.

Offer mẫu: “[Công ty A]” 24 gross, đóng đủ, thưởng 1, phụ cấp 1, remote 2; “[Công ty B]” 27 gross, đóng thấp, mức 5,31. Hộp thị trường tĩnh “n = 186”, P25 16, trung vị 20, P75 26, thang 0–40, vị trí Data Engineer Junior Hà Nội. Ba câu thoại với HR và điểm 92 / 76 / 45 là kịch bản.

Hợp đồng minh họa gồm chín điều, trong đó thử việc 90 ngày, lương thử việc 70%, giữ bản gốc bằng, phạt 200.000 đồng đi muộn, cấm cạnh tranh 24 tháng, thưởng tháng 13 nếu còn làm việc. Ngày mặc định: chi thưởng 2027-01-29, Tết 06/02/2027, mùa tuyển 15/02/2027–30/04/2027, lương 18 triệu, hợp đồng không xác định thời hạn.

Remote mặc định: 18 triệu và chi phí sống 12 triệu trong nước; 1.200 USD, tỷ giá 26.000, freelance, tự lo 2 triệu, múi Châu Á – Úc; 280.000 JPY, tỷ giá 170, khấu trừ 22%, sinh hoạt 160.000 JPY. Năm bậc BrSE là lịch ước lượng gắn trên màn.
