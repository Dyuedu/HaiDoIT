---
title: 'Trích PRD từ addendum Hải Đồ IT'
source: '_bmad-output/planning-artifacts/briefs/brief-HaiDoIT-2026-10-22/addendum.md'
source_created: '2026-10-22'
source_updated: '2026-10-22'
extracted: '2026-10-22'
---

# Trích addendum cho PRD Hải Đồ IT

Nguồn duy nhất: `addendum.md` (2026-10-22). Bản này không sửa nguồn. Quyết định đã chốt nằm ở mục 1. Phương án đã hủy, đã bỏ, hoặc chỉ được ghi "có thể" không phải yêu cầu.

## 1. Quyết định và lý do thuộc PRD

Hành vi người dùng thấy, phạm vi, và chính sách. Lý do giữ đúng mức addendum nêu, không kéo phần kỹ thuật hay số đo lường vào đây.

### Phạm vi màn

| Hạng mục (tên đã chốt) | Mức | Phạm vi người dùng thấy | Lý do addendum nêu |
|---|---|---|---|
| Bản đồ nhu cầu | v1, đúng prototype | Bảy thành phố: Hà Nội, Hải Phòng, Đà Nẵng, Quy Nhơn, Nha Trang, TP. Hồ Chí Minh, Cần Thơ. Có dự báo 18 tháng và tín hiệu sớm. Lương công khai ẩn số khi dưới 30 tin. | Duy cập nhật 2026-10-22. Quyết định thu còn ba thành phố và đổi dự báo thành kịch bản đã hủy. Ẩn lương vì prototype đang làm vậy. |
| Học gì tiếp? (trước là Mô phỏng Nếu–thì) | v1, lõi | Tên dùng trong sản phẩm là **Học gì tiếp?** | Chưa đối thủ nào làm. ChatGPT khó thay vì cần dữ liệu thật. |
| Lộ trình 90 ngày (trước là Cố vấn đa agent) | v1, lõi | Có lối "Vì sao?". Bản đầu không gắn với đa agent. | Đúng nỗi đau mạnh nhất. |
| Lương và hạn dùng kỹ năng | Kỹ năng: v1, lớp dữ liệu. Lương phân vị: v2 | Phần kỹ năng là lớp dữ liệu của v1. Lương phân vị không nằm trong v1. | Mẫu lương công khai mỏng. |
| So sánh offer | v1, miễn phí | Miễn phí. | 43,1% bị đóng BHXH theo mức thấp hơn thu nhập thực (một nguồn: Navigos). Rủi ro pháp lý thấp. |
| Soi tin tuyển dụng | v1, bản nhẹ | Tập trung vào tin treo: đếm số lần làm mới, phát hiện tin trùng. Không làm chức năng chống lừa đảo. | Không ai trả tiền cho tính năng này, nhưng tạo lòng tin. Lừa đảo việc làm không nằm trong top 5. |
| Tập thương lượng (nằm trong màn So sánh offer) | v2 | Không có trong v1. | Levels.fyi cho thấy người dùng trả tiền cho thương lượng gắn với kết quả. Giá ở Việt Nam chưa biết. |
| Hộ chiếu kỹ năng | Review dự án: v2. Bỏ "Ghép việc lại" | v1 không có review dự án và không có ghép việc. | Triplebyte thất bại, Findy lỗ. Ghép việc cần giấy phép. |
| Lộ trình thật của người giống bạn | Sau này | Không có trong v1. | Cần nhiều hồ sơ. Dễ bị nhận diện lại. |
| Chỉ số phản hồi nhà tuyển dụng | Không làm | Ngoài phạm vi. | reviewcongty bị chặn năm 2023. Nghị định 147 bắt xác thực bằng số điện thoại. |
| Bộ công cụ nhảy việc (agent pháp lý đọc hợp đồng) | Không làm | Ngoài phạm vi. | Ít bằng chứng nỗi đau. Rủi ro hành nghề tư vấn pháp luật. |
| Remote quốc tế và thị trường Nhật | Chỉ dạng nội dung | Không làm thành sản phẩm thị trường riêng. | Nhóm nhỏ (khoảng 6.000 kỹ sư Việt tại Nhật). |

### Hành vi có điều kiện

- Ngưỡng **30 tin** chỉ quyết định có hiện lương công khai hay không. Đây không phải ngưỡng số người dùng.
- Việc tuần 1 là đo số mẫu theo vai trò × thành phố × có công khai lương hay không. Nếu nhóm Data/AI ở Hà Nội dưới 30 tin, **Học gì tiếp?** tính trên toàn quốc hoặc gộp các vai trò gần nhau. Quy tắc này đã chốt; kết quả đo chưa có (mục 4).
- "Vì sao?" lấy nguồn từ báo cáo công khai của ITviec, TopDev, TopCV, JobOKO. Cùng các báo cáo đó dùng để kiểm tra chéo xu hướng.

### Chính sách

- Ngày 2026-10-22 Duy quyết định: đưa số liệu đã trích vào sản phẩm, không xin phép và không chờ luật sư. Bốn câu hỏi pháp lý ở mục 4 được giữ để xem sau, không phải điều kiện để xây v1.
- Chỉ lưu dữ liệu đã trích xuất: kỹ năng, thành phố, cấp bậc, khoảng lương, ngày đăng, link gốc. Không lưu nguyên văn mô tả công việc. Loại bỏ tên và liên hệ của người tuyển dụng.
- Trước khi gọi API nước ngoài, bỏ thông tin cá nhân (chuyển dữ liệu xuyên biên giới).
- v1 không chạy quảng cáo mua người dùng.

## 2. Nội dung không đưa vào mạch chính PRD

Mỗi dòng: nội dung là gì, và vì sao để ở lớp sau. Không nâng các dòng này thành yêu cầu.

### Cách làm kỹ thuật — kiến trúc

- So sánh hai cách lấy dữ liệu (cào HTML job board ITviec/TopDev, kể cả sitemap và một request mỗi tin, với gọi một endpoint JSON công khai mỗi công ty, ví dụ `boards-api.greenhouse.io/v1/boards/<công-ty>/jobs`, trên Greenhouse, Lever, Workable, SmartRecruiters, Workday) — cách vận chuyển, thuộc kiến trúc.
- Bảng được phép và nhược điểm của từng cách (robots.txt cho phép và điều khoản không cấm rõ với cào, do nhóm tự kiểm tra; API do nhà cung cấp công bố để dùng công khai; cào phải lọc tin không thuộc IT và phụ thuộc đối thủ; API không có trường kỹ năng riêng và phải biết trước công ty dùng ATS nào) — lựa chọn pipeline, thuộc kiến trúc.
- Danh sách `BOARDS` trong `D:\FR_KS_FU_Java_03\SkillNexus\pipeline\scrapers\ats.py` (11 công ty; chạy thử 2026-10-21: 125 tin Việt Nam thành 78 tin IT) và hướng dò trang Careers để mở rộng — tài sản pipeline, thuộc kiến trúc.
- Trích kỹ năng từ mô tả công việc bằng LLM — cơ chế, thuộc kiến trúc. Chính sách bỏ thông tin cá nhân trước khi gọi API nằm ở mục 1.
- Crawl định kỳ từ sớm để Soi tin có lịch sử số lần làm mới và tin trùng — vận hành pipeline, thuộc kiến trúc. Hành vi đếm và phát hiện trùng nằm ở mục 1.
- Lộ trình bản đầu làm bằng tính toán từ dữ liệu rồi LLM viết, kèm "Vì sao?" — cơ chế, thuộc kiến trúc. PRD chỉ cần phạm vi "Lộ trình 90 ngày", không đa agent, và có "Vì sao?".
- Dùng báo cáo ITviec, TopDev, TopCV, JobOKO để kiểm tra chéo xu hướng — đối chiếu dữ liệu, thuộc kiến trúc. Việc "Vì sao?" bám các báo cáo đó là chính sách ở mục 1.

### Phương án đã xét và đã loại — để trong addendum, không viết thành yêu cầu

- Thu bản đồ còn ba thành phố, và đổi dự báo thành kịch bản — đã hủy ngày 2026-10-22; phạm vi giữ nguyên prototype bảy thành phố, dự báo 18 tháng, tín hiệu sớm.
- Giữ đa agent cho bản đầu của lộ trình — không bắt buộc; không ghi đa agent thành yêu cầu v1.
- Đưa lương phân vị vào v1 — chuyển v2 vì mẫu lương công khai mỏng.
- Đưa tập thương lượng vào v1 — chuyển v2; giá Việt Nam chưa biết nên chưa thành yêu cầu.
- "Ghép việc lại" trong Hộ chiếu kỹ năng — đã bỏ; lý do thất bại của Triplebyte, lỗ của Findy, và giấy phép chỉ giải thích quyết định bỏ, không thành thiết kế.
- Lộ trình thật của người giống bạn trong v1 — để sau này; nhu cầu nhiều hồ sơ và rủi ro nhận diện lại không thành yêu cầu v1.
- Chỉ số phản hồi nhà tuyển dụng — không làm; vụ reviewcongty (2023) và Nghị định 147 chỉ là lý do loại.
- Agent pháp lý đọc hợp đồng — không làm. Cụm "có thể để danh sách kiểm tra miễn phí" là khả năng chưa được chọn, không phải yêu cầu.
- Làm Remote quốc tế và thị trường Nhật thành tính năng sản phẩm — chỉ giữ dạng nội dung.
- Mốc 500 người thử — đã bỏ, vì hai tháng gồm cả thời gian xây và v1 không mua người dùng.
- Mở brief bằng một người minh họa tên Minh — đã bỏ.
- Xin phép hoặc chờ luật sư trước khi đưa số liệu đã trích vào sản phẩm — đã bỏ; quyết định ngược nằm ở mục 1.

### Quy mô và ngưỡng đo — addendum hoặc thước đo sau, không phải mạch hành vi

- Bảng mục C của addendum, giữ nguyên độ tin cậy: lập trình viên đang đi làm ~480–560 nghìn (một nguồn, TopDev); người tốt nghiệp IT mỗi năm ~50–60 nghìn (trung bình); định nghỉ việc trong 12 tháng 40,9% và đang chủ động tìm việc 54,5% (hai nguồn); lương trung vị junior dưới 1 năm ~10–14 triệu/tháng (trung bình); tuyển người dưới 1 năm kinh nghiệm −13% (trung bình–cao); tỷ lệ doanh nghiệp coi AI là lý do chính để không tuyển thêm 5,9% → 20,2% → 34,3% dự báo 2026 (trung bình–cao); giá TopCV thu từ ứng viên 10.000–500.000đ (cao) — quy mô thị trường trích từ nghiên cứu, không phải yêu cầu.
- Khoảng 832 tin IT theo nguồn người dùng cung cấp: ITviec 652, TopDev 99, API ATS 78, Cốc Cốc 3 — kiểm kê dữ liệu cho kiến trúc. Addendum ghi chưa rõ đây là một thời điểm hay một khoảng thời gian.
- Khoảng 6.000 kỹ sư Việt tại Nhật — số dùng để giải thích vì sao Remote/Nhật chỉ là nội dung.
- Ngưỡng đi tiếp: ít nhất 30 người thật tạo xong lộ trình 90 ngày, và ít nhất 25% số đó (8 người) mở lại lộ trình trong 14 ngày. Mức 30 người là ngưỡng sản phẩm — thước đo sau khi có sản phẩm, không phải hành vi trên màn hình.
- CAC: v1 không đo. Chưa có số Việt Nam. Đo lại khi có kênh trả phí hoặc món v2 — đo lường để sau.

### Persona — UX hoặc addendum

- Minh, và chuyện thật của Duy — độ sâu persona. Brief không mở bằng một người minh họa; phần vấn đề dùng số liệu đã có nguồn; chuyện Duy không chặn brief và không chặn việc xây. Đây là cách viết bài toán, thuộc UX hoặc addendum, không phải yêu cầu chức năng.

## 3. Mâu thuẫn hoặc sức căng

Addendum không có mục đối chiếu với một "sản phẩm hướng nghiệp v1 điển hình". Nó tự ghi các sức căng sau:

- Soi tin vẫn ở v1 dù không ai trả tiền, vì tính năng tạo lòng tin. Phạm vi là tin treo, vì lừa đảo việc làm không nằm trong top 5.
- Ghép việc bị bỏ dù là hướng gắn với sản phẩm nghề nghiệp: Triplebyte thất bại, Findy lỗ, và ghép việc cần giấy phép.
- Chỉ số phản hồi nhà tuyển dụng không làm: reviewcongty bị chặn năm 2023, và Nghị định 147 bắt xác thực bằng số điện thoại.
- Agent pháp lý đọc hợp đồng không làm: ít bằng chứng nỗi đau, và có rủi ro hành nghề tư vấn pháp luật.
- Remote quốc tế và thị trường Nhật chỉ làm dạng nội dung, vì nhóm khoảng 6.000 kỹ sư Việt tại Nhật.
- Lương phân vị để v2 vì mẫu lương công khai mỏng; lương công khai trên bản đồ ẩn số khi dưới 30 tin.
- Quyết định thu còn ba thành phố và đổi dự báo thành kịch bản đã hủy. Phạm vi giữ bảy thành phố, dự báo 18 tháng, và tín hiệu sớm.
- Prototype mang tên cố vấn đa agent. Bản đầu của Lộ trình 90 ngày không nhất thiết đa agent.
- README SkillNexus ghi bộ cào chỉ dành cho phân tích phi thương mại. Điều khoản ITviec (§2.2) và TopDev hạn chế sao chép, hiển thị và khai thác thương mại khi chưa có đồng ý bằng văn bản. Duy vẫn quyết định đưa số liệu đã trích vào sản phẩm, không xin phép. Addendum giữ câu hỏi này để xem sau và nói rõ nó không chặn v1.
- Hai ngưỡng cùng mang số 30: 30 người là ngưỡng sản phẩm (tạo lộ trình và mở lại); 30 tin chỉ dùng để quyết định có hiện lương công khai hay không.

## 4. Câu hỏi còn mở

Addendum đánh dấu chưa rõ hoặc để sau. Không câu nào trong mục pháp lý là điều kiện để xây v1.

1. Khoảng 832 tin (ITviec 652, TopDev 99, API ATS 78, Cốc Cốc 3) là số tại một thời điểm hay trong một khoảng thời gian. Addendum ghi *chưa rõ*.
2. Điều 27 Luật Việc làm 74/2025: cung cấp miễn phí thống kê thị trường lao động và lộ trình học có thuộc "dịch vụ việc làm" phải xin phép không?
3. ITviec §2.2 và điều khoản TopDev hạn chế sao chép, hiển thị và khai thác thương mại nội dung khi chưa có đồng ý bằng văn bản. README SkillNexus ghi bộ cào chỉ dành cho phân tích phi thương mại. Câu này được giữ để xem sau, cùng với quyết định đã chốt ở mục 1.
4. Hoa hồng giới thiệu khoá học: có cần đăng ký gì không?
5. Luật AI: nếu định vị là "giáo dục" thì có rơi vào danh mục AI rủi ro cao trong giáo dục không (thời hạn tuân thủ 9/2027)?
6. Kết quả đo tuần 1 theo vai trò × thành phố × có công khai lương hay không chưa có. Quy tắc đã chốt: nếu Data/AI ở Hà Nội dưới 30 tin thì Học gì tiếp? tính trên toàn quốc hoặc gộp các vai trò gần nhau. Chưa biết điều kiện đó có đúng hay không.
7. Giá người dùng ở Việt Nam trả cho tập thương lượng chưa biết. Đây là lý do để v2, không phải việc phải chốt cho v1.
8. Số CAC Việt Nam chưa có. v1 không đo; đo lại khi có kênh trả phí hoặc món v2.
