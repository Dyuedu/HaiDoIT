---
title: 'Product Brief: Hải Đồ IT'
status: final (superseded in part, see 2026-10-27 note)
created: '2026-10-22'
updated: '2026-10-27'
sources:
  - _bmad-output/planning-artifacts/research/market-hai-do-it-nen-tang-nghe-nghiep-it-viet-n-2026-10-22/research.md
  - prototype/Hải Đồ IT — Bản đồ tuyển dụng & Cố vấn đa agent.html
---

# Product Brief: Hải Đồ IT

> **Cập nhật 2026-10-27: một phần brief đã bị thay.** Brief giữ nguyên như lúc khép để truy vết. Khi lệch, PRD và SPEC thắng. Các điểm đã đổi:
> - **Doanh thu v1** là không. Không có link hoa hồng khóa học trong hai tháng này (PRD FR-11).
> - **Bản đồ nhu cầu** còn **ba thành phố**: Hà Nội, TP. Hồ Chí Minh, Đà Nẵng. Đo 832 tin: Hải Phòng 2, Cần Thơ, Quy Nhơn, Nha Trang 0.
> - **Dự báo 18 tháng** không có số cho đến khi có công thức đã đo (AD-12).
> - **Lương công khai** dùng tin có lương trong 180 ngày và đổi USD theo tỷ giá cố định. Đo: chỉ 24/832 tin có lương VND.
> - **Bốn agent** (Bản đồ, Học gì tiếp, Lộ trình, Soi tin) là yêu cầu bắt buộc.
> - **Bản JSON-LD gốc** lúc cào được lưu trên Silo, không hiện và không trả qua API.
> - **So sánh offer** hoãn sang v1.1.
>
> Chi tiết: `../../sprint-change-proposal-2026-10-27.md`.

## Tóm tắt

Hải Đồ IT là một ứng dụng web giúp **junior, fresher và người đang chuyển hướng trong ngành IT** trả lời câu hỏi *"học gì tiếp để có việc tốt hơn?"* bằng dữ liệu tuyển dụng thật, thay vì cảm tính hay lời khuyên chung chung của chatbot. Người dùng xem kỹ năng nào đang được săn đón, thử thêm kỹ năng vào hồ sơ để thấy số việc phù hợp và mức lương thay đổi ra sao, rồi nhận lộ trình 90 ngày. Mỗi bước trong lộ trình đều có nút **"Vì sao?"** dẫn về nguồn.

Thời điểm này thuận lợi vì thị trường IT Việt Nam đang phân cực. Tỷ lệ doanh nghiệp coi năng suất AI là lý do chính để không tuyển thêm tăng từ 5,9% (2024) lên 20,2% (2025), dự báo 34,3% năm 2026. Tuyển người dưới 1 năm kinh nghiệm giảm 13%, trong khi tin tuyển AI/ML trên ITviec tăng 41% và lượt tìm "AI" tăng 89%. Theo nghiên cứu thị trường, người muốn đổi hướng thì nhiều, nhưng chưa sản phẩm nào trả lời câu hỏi "chuyển sang đâu, học gì, mất bao lâu" bằng số liệu.

Hải Đồ IT **không phải sàn tuyển dụng**. Sản phẩm không ghép việc và không đánh giá công ty. v1 thu từ hoa hồng khóa học và từ trường hoặc bootcamp nhận thử. Ứng viên chưa trả tiền trong v1. Khoản ứng viên trả gắn với review dự án, để v2.

## Vấn đề

Người muốn chuyển hướng trong ngành IT thì nhiều. Cách họ đang xoay xở thì không có số liệu.

- **Ý định đổi việc rất cao.** 40,9% dân IT định nghỉ việc trong 12 tháng tới, và 26,3% trong số đó muốn đổi hướng nghề nghiệp (ITviec, n=2.324). 54,5% đang chủ động tìm việc (JobsGO).
- **Junior bị ép.** Người dưới 1 năm kinh nghiệm chiếm 45% số ca bị cắt giảm (JobOKO, 580 nghìn tin).
- **Cách xoay xở hiện nay** là tự đọc tin tuyển, hỏi ChatGPT, hỏi người quen, đăng ký khoá học theo cảm tính. **Cái giá phải trả** là hàng tháng học sai hướng, trong khi thu nhập junior chỉ khoảng 10–14 triệu đồng/tháng nên mỗi khoá học sai là một khoản mất đáng kể.

## Giải pháp

Một luồng chính gồm 3 bước, cùng 2 công cụ miễn phí để kéo người dùng vào:

1. **Bản đồ nhu cầu**, mặt tiền của sản phẩm, giữ nguyên thiết kế prototype cập nhật ngày 2026-10-22. Bảy thành phố: Hà Nội, Hải Phòng, Đà Nẵng, Quy Nhơn, Nha Trang, TP. Hồ Chí Minh, Cần Thơ. Dòng đầu: nhu cầu hôm nay và 18 tháng tới. Kéo để xem dự báo. Chạm một thành phố để xem cơ cấu, lương và tín hiệu sớm. Có đánh dấu "✓ bạn đã có".
2. **Học gì tiếp?**, phần lõi: người dùng thêm kỹ năng giả định (ví dụ Docker, RAG) để xem số tin phù hợp, lương kỳ vọng và thời gian học thay đổi thế nào. Hệ thống gợi ý kỹ năng nên học tiếp, xếp theo số việc mở thêm trên mỗi tuần học.
3. **Lộ trình 90 ngày**: biến lựa chọn ở bước 2 thành kế hoạch 3 chặng, mỗi chặng có một dự án thực hành. Mọi nhận định đều có nút "Vì sao?" chỉ ra tin tuyển hoặc số liệu làm căn cứ, kể cả những nhận định đã bị loại vì thiếu dữ liệu.

Hai công cụ miễn phí:
- **So sánh offer:** quy về thực nhận cả năm, và cảnh báo khi công ty đóng BHXH theo mức thấp hơn lương thật. Theo Navigos, 43,1% người lao động gặp trường hợp này.
- **Soi tin:** cảnh báo tin treo, tin trùng lặp và mức lương bất thường trước khi nộp CV.

## Điểm khác biệt

Nói thẳng: **Hải Đồ IT không có lợi thế về dữ liệu.** TopCV có khoảng 9–10 triệu hồ sơ, ITviec có báo cáo lương hằng năm, và cả hai đều có thể làm theo. Khác biệt nằm ở ba điểm:

- **Trả lời câu hỏi "nếu tôi học X thì sao?" bằng số liệu.** Chưa đối thủ nào trong nước hay quốc tế làm điều này, trong phạm vi nghiên cứu đã tìm. ChatGPT thì không có dữ liệu tin tuyển dụng Việt Nam theo thời gian thực.
- **Minh bạch nguồn ("Vì sao?").** Lập trình viên Việt Nam hay kiểm tra lại kết quả AI: 86% luôn hoặc thường xuyên làm vậy. Trích nguồn là cách lấy được lòng tin của nhóm người dùng này.
- **Đứng về phía ứng viên.** Các nền tảng lớn kiếm tiền từ nhà tuyển dụng và dồn AI cho phía nhà tuyển dụng (AI Match, AI Screening, Job Post AI).

Lợi thế thực tế còn lại là **tốc độ và sự tập trung vào một nhóm người dùng**. Lợi thế này chỉ tồn tại trong một khoảng thời gian ngắn, vì HRCV và X-Interview đã vào thị trường trong năm 2026.

## Đối tượng

- **Người dùng chính:** junior (0–2 năm kinh nghiệm) và fresher muốn chuyển hướng, nhất là sang Data/AI, Cloud/DevOps. Họ cần biết nên học gì, mất bao lâu và đáng hay không. Với họ, thành công là có lộ trình rõ, học đúng thứ thị trường cần, và có được việc hoặc lên lương sau 3–6 tháng.
- **Người dùng phụ:** sinh viên năm cuối các ngành IT, với khoảng 50–60 nghìn người tốt nghiệp mỗi năm. Sinh viên tìm thực tập chủ yếu qua Facebook (47,5%) và chương trình của trường (30%).
- **Bên trả tiền tiềm năng:** trường đại học và bootcamp. Đây là công cụ hướng nghiệp và minh chứng đầu ra cho họ. Coursera Việt Nam có 1,8 triệu người học, cho thấy nhu cầu học kỹ năng rất lớn.

## Mô hình doanh thu

Thu tiền **gắn với kết quả**, không bán thuê bao "lời khuyên". Lý do: nghiên cứu mới chỉ thấy ứng viên trả các khoản nhỏ (TopCV thu 10.000–500.000đ), còn các dịch vụ thu tiền tốt đều gắn với kết quả (Levels.fyi, Edupia, bootcamp "học trước, trả sau").

- **v1:** hoa hồng giới thiệu khoá học tại từng bước trong lộ trình, và thử nghiệm (pilot) với 1–2 trường hoặc bootcamp. Ứng viên không trả tiền. Không có gói, không có cửa giả, không có giá.
- **v2:** review dự án cuối lộ trình là món ứng viên có thể trả. Các gói cho trường nằm ở đây. Ví ứng viên chỉ được đo khi món này có tên.

## Tiêu chí thành công (sau 2 tháng)

Đi tiếp khi đủ bốn mức dưới đây. Mức 500 người thử đã bỏ: hai tháng gồm cả thời gian xây, và v1 không mua người dùng. Ngưỡng 30 người tạo xong lộ trình là ngưỡng sản phẩm. Ngưỡng 30 tin là quy tắc riêng: lương công khai chỉ hiện số khi đủ 30 tin.

| Chỉ số | Ngưỡng "đi tiếp" |
|---|---|
| Người thật tạo xong lộ trình 90 ngày | ≥ 30 |
| Trong số đó, mở lại lộ trình trong 14 ngày | ≥ 25% (ít nhất 8 người) |
| Trường hoặc bootcamp đồng ý thử nghiệm | ≥ 1 |
| Nhận định có "Vì sao?" trỏ đúng nguồn | 100% |

## Phạm vi

**Trong v1** (2 tháng, 3 người, web):
- Bản đồ nhu cầu (đúng prototype: bảy thành phố, dự báo 18 tháng, tín hiệu sớm)
- Học gì tiếp?
- Lộ trình 90 ngày có "Vì sao?"
- Xu hướng và hạn dùng kỹ năng (lớp dữ liệu nền)
- So sánh offer + kiểm tra BHXH
- Soi tin (bản nhẹ)

**Để v2:** review dự án (điểm thu tiền chính), phòng tập thương lượng, lương theo phân vị.

**Không làm:**
- ghép việc hoặc gợi ý tin "vừa mở khoá", vì cần giấy phép dịch vụ việc làm;
- chỉ số phản hồi và đánh giá nhà tuyển dụng ẩn danh, vì có tiền lệ bị chặn;
- agent pháp lý đọc hợp đồng thu phí;
- lộ trình thật của người giống bạn;
- remote/Nhật (chỉ làm dạng nội dung);
- app mobile.

## Dữ liệu và ràng buộc

- **Tài sản sẵn có từ dự án cũ SkillNexus.** Code pipeline nằm ở `D:\FR_KS_FU_Java_03\SkillNexus\pipeline`, ngoài repo này. Gồm bộ cào lịch sự (đọc robots.txt, User-Agent trung thực, giãn cách ≥ 3 giây, dừng khi bị chặn), bộ trích kỹ năng theo taxonomy, và bộ nạp dataset VietJobs. Đã có test offline. Hải Đồ IT dùng lại pipeline này.
- **Nguồn đang có:**
  - **Tin đang mở** từ ITviec (652), TopDev (99), API ATS (78) và Cốc Cốc (3), tổng khoảng 832 tin tại một thời điểm. Mỗi tin chỉ sống khoảng 1 tháng, nên phải cào hằng ngày để tích luỹ dữ liệu.
  - **Dataset VietJobs** (VinNLP/VinUniversity, giấy phép MIT, có ghi công): 48.092 tin, trong đó 1.906 tin IT và 1.144 tin có lương. Không có tên công ty và ngày đăng, nên chỉ dùng làm nền lịch sử.
  - Bổ sung bằng báo cáo công khai (ITviec, TopDev, TopCV, JobOKO).
- **Nguồn không dùng được:** TopCV và VietnamWorks chặn bot hoặc chỉ có API nội bộ. CareerViet và Glints cấm crawl trong điều khoản sử dụng. SmartRecruiters chặn trong robots.txt.
- **API ATS là nguồn chiến lược:** tin do chính công ty đăng qua hệ thống quản lý tuyển dụng (Greenhouse, Lever, Workable…), lấy dạng JSON công khai. Greenhouse ghi rõ *"Job Board data is publicly available"*. Mỗi công ty chỉ cần một request. Nhược điểm là phải tự lập danh sách công ty dùng ATS nào (ví dụ NAVER Vietnam dùng Greenhouse, Gradion dùng Lever), và phải trích kỹ năng từ mô tả công việc. Mục tiêu là tăng dần tỷ trọng nguồn này để giảm phụ thuộc vào ITviec.
- **Giới hạn hiển thị:** lương công khai chỉ hiện số khi có từ 30 tin, đúng quy tắc đang gắn trên prototype. Bảy thành phố và dự báo 18 tháng vẫn nằm trên bản đồ.
- **Cách đưa vào sản phẩm:** v1 dùng số liệu đã trích từ mọi nguồn pipeline đang chạy, gồm ITviec và TopDev. Mỗi tin chỉ giữ kỹ năng, thành phố, cấp bậc, khoảng lương, ngày đăng và link gốc. Không lưu và không hiển thị nguyên văn mô tả công việc. Pipeline giữ cách lấy hiện tại: đọc robots.txt, không vượt trang chặn bot.
- **Quyết định 2026-10-22:** Duy chọn đưa các số liệu đó vào sản phẩm ngay. Không xin phép các trang và không chờ ý kiến luật sư trước khi làm.

## Rủi ro và giả định chưa kiểm chứng

1. **Mẫu dữ liệu mỏng.** ITviec chiếm khoảng 78% nguồn và vốn lệch về TP.HCM. Nhóm Data/AI ở từng thành phố có thể dưới 30 mẫu `[GIẢ ĐỊNH — cần đo ngay trong tuần 1]`.
2. **Ứng viên có mở ví không.** Chưa có bằng chứng. Hai tháng này không đo câu đó. Tiền đo được trong v1 là hoa hồng khoá học và một trường hoặc bootcamp đồng ý thử. Ví ứng viên để v2, khi món bán là review dự án.
3. **CAC không đo trong v1.** Nghiên cứu không tìm được số chi phí có một người dùng tại Việt Nam. Hai tháng này không chạy quảng cáo để mua người dùng. Đo CAC khi có kênh trả phí hoặc khi có món v2.
4. **Pháp lý không chặn v1.** Điều khoản ITviec và TopDev hạn chế sao chép và khai thác thương mại; Điều 27 Luật Việc làm chưa được kiểm tra. Duy chấp nhận rủi ro này và vẫn đưa số liệu vào sản phẩm. Các câu hỏi để sau nằm ở addendum, mục D.
5. **ChatGPT là đối thủ thay thế.** Nếu người dùng không thấy giá trị của dữ liệu thật, phần lõi mất lợi thế.

## Tầm nhìn

Trong 2–3 năm, Hải Đồ IT trở thành **"la bàn kỹ năng" của dân IT Việt Nam**: nơi sinh viên và junior quyết định học gì trước khi bỏ tiền và thời gian; nơi trường học và bootcamp đo xem chương trình của họ có khớp với thị trường không. Khi đã có đủ người dùng và dữ liệu, sản phẩm mở rộng sang review dự án, tra lương theo phân vị, thành phố ngoài bảy thành phố trên bản đồ, và có thể cả ghép việc nếu xin được giấy phép.
