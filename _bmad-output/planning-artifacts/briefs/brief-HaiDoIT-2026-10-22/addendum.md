---
title: 'Addendum: Product Brief Hải Đồ IT'
created: '2026-10-22'
updated: '2026-10-22'
---

# Addendum: chi tiết dành cho PRD và kiến trúc

## A. Đối chiếu 11 màn prototype với phạm vi

| Màn prototype | Quyết định | Lý do (theo nghiên cứu) |
|---|---|---|
| Bản đồ nhu cầu | v1, đúng prototype | Duy cập nhật 2026-10-22: giữ bảy thành phố (Hà Nội, Hải Phòng, Đà Nẵng, Quy Nhơn, Nha Trang, TP. Hồ Chí Minh, Cần Thơ), dự báo 18 tháng và tín hiệu sớm. Quyết định thu còn ba thành phố và đổi dự báo thành kịch bản bị hủy. Lương công khai vẫn ẩn số khi dưới 30 tin, vì prototype đang làm vậy. |
| Mô phỏng Nếu–thì → **Học gì tiếp?** | v1, lõi | Chưa đối thủ nào làm; ChatGPT khó thay vì cần dữ liệu thật |
| Cố vấn đa agent → **Lộ trình 90 ngày** | v1, lõi | Đúng nỗi đau mạnh nhất. Bản đầu không nhất thiết đa agent: tính toán từ dữ liệu → LLM viết lộ trình → "Vì sao?" |
| Lương & hạn dùng kỹ năng | Phần kỹ năng: v1 (lớp dữ liệu) · Phần lương phân vị: v2 | Mẫu lương công khai mỏng |
| So sánh offer | v1, miễn phí | 43,1% bị đóng BHXH theo mức thấp hơn thu nhập thực (một nguồn: Navigos); rủi ro pháp lý thấp |
| Soi tin tuyển dụng | v1, bản nhẹ | Không ai trả tiền cho tính năng này, nhưng tạo lòng tin. Tập trung vào tin treo, không phải chống lừa đảo (lừa đảo việc làm không nằm trong top 5) |
| Tập thương lượng (trong màn So sánh offer) | v2 | Levels.fyi cho thấy người dùng trả tiền cho thương lượng gắn với kết quả; chưa biết giá ở Việt Nam |
| Hộ chiếu kỹ năng | Review dự án: v2 · Bỏ phần "Ghép việc lại" | Triplebyte thất bại, Findy lỗ; ghép việc cần giấy phép |
| Lộ trình thật của người giống bạn | Sau này | Cần nhiều hồ sơ; dễ bị nhận diện lại |
| Chỉ số phản hồi nhà tuyển dụng | Không làm | reviewcongty bị chặn năm 2023; Nghị định 147 bắt xác thực bằng số điện thoại |
| Bộ công cụ nhảy việc (agent pháp lý đọc hợp đồng) | Không làm (có thể để danh sách kiểm tra miễn phí) | Ít bằng chứng nỗi đau; rủi ro hành nghề tư vấn pháp luật |
| Remote quốc tế và thị trường Nhật | Chỉ làm dạng nội dung | Nhóm nhỏ (khoảng 6.000 kỹ sư Việt tại Nhật) |

## B. Kế hoạch dữ liệu: ghi chú cho kiến trúc

- **Nguồn người dùng cung cấp:** ITviec 652 · TopDev 99 · API ATS 78 · Cốc Cốc 3 (khoảng 832 tin IT). *Chưa rõ:* đây là số tin tại một thời điểm hay trong một khoảng thời gian.
- **So sánh hai cách lấy dữ liệu** (theo nhóm):

  | | Cào job board (ITviec, TopDev) | API ATS (Greenhouse, Lever, Workable, SmartRecruiters, Workday) |
  |---|---|---|
  | Cách lấy | Tải từng trang HTML, đọc khối dữ liệu nhúng trong trang | Gọi một endpoint JSON công khai, ví dụ `boards-api.greenhouse.io/v1/boards/<công-ty>/jobs` |
  | Số request | Mỗi tin một request (kèm sitemap) | Mỗi công ty một request cho toàn bộ tin |
  | Nguồn tin | Trang trung gian đăng lại | Chính công ty đăng (nguồn gốc) |
  | Được phép? | robots.txt cho phép, điều khoản sử dụng không cấm rõ (nhóm tự kiểm tra) | Nhà cung cấp công bố để dùng công khai |
  | Nhược điểm | Phải lọc tin không thuộc IT; phụ thuộc vào đối thủ | Không có trường kỹ năng riêng; phải biết trước công ty nào dùng ATS nào |

- **Danh sách công ty cho ATS:** `BOARDS` trong `D:\FR_KS_FU_Java_03\SkillNexus\pipeline\scrapers\ats.py` (11 công ty, chạy thử 2026-10-21: 125 tin Việt Nam → 78 tin IT). Đây là tài sản dữ liệu cần mở rộng có hệ thống. Có thể dò công ty Việt Nam dùng ATS nào qua trang "Careers" của họ.
- **Việc cần làm trong tuần 1:** đo số mẫu theo vai trò × thành phố × có công khai lương hay không. Nếu nhóm Data/AI ở Hà Nội dưới 30 tin, "Học gì tiếp?" phải tính trên toàn quốc hoặc gộp các vai trò gần nhau.
- **Lịch sử theo thời gian:** tính năng Soi tin (đếm số lần làm mới, phát hiện tin trùng) cần crawl định kỳ từ sớm.
- **Lưu trữ:** chỉ lưu dữ liệu đã trích xuất (kỹ năng, thành phố, cấp bậc, khoảng lương, ngày đăng, link gốc); không lưu nguyên văn mô tả công việc; loại bỏ tên và liên hệ của người tuyển dụng.
- **Trích xuất kỹ năng từ mô tả công việc:** dùng LLM. Phải bỏ thông tin cá nhân trước khi gọi API nước ngoài (chuyển dữ liệu xuyên biên giới).
- **Bổ sung:** dùng báo cáo công khai (ITviec, TopDev, TopCV, JobOKO) để kiểm tra chéo xu hướng và làm nguồn cho "Vì sao?".

## C. Số liệu thị trường (trích từ nghiên cứu, kèm nguồn trong research.md)

| Số liệu | Giá trị | Độ tin cậy |
|---|---|---|
| Lập trình viên đang đi làm | ~480–560 nghìn | Một nguồn (TopDev) |
| Người tốt nghiệp IT mỗi năm | ~50–60 nghìn | TB |
| Định nghỉ việc trong 12 tháng / đang chủ động tìm việc | 40,9% / 54,5% | Hai nguồn |
| Lương trung vị junior dưới 1 năm kinh nghiệm | ~10–14 triệu/tháng | TB |
| Tuyển người dưới 1 năm kinh nghiệm | −13% | TB–cao |
| Tỷ lệ doanh nghiệp coi AI là lý do chính để không tuyển thêm | 5,9% → 20,2% → 34,3% (dự báo 2026) | TB–cao |
| Giá TopCV thu từ ứng viên | 10.000–500.000đ | Cao |

## D. Câu hỏi pháp lý — không chặn v1

Duy quyết định ngày 2026-10-22: đưa số liệu đã trích vào sản phẩm, không xin phép và không chờ luật sư. Các câu hỏi dưới đây giữ lại để xem sau, không phải điều kiện để xây v1.

1. Điều 27 Luật Việc làm 74/2025: cung cấp miễn phí thống kê thị trường lao động và lộ trình học có thuộc "dịch vụ việc làm" phải xin phép không?
2. ITviec §2.2 và điều khoản TopDev hạn chế sao chép, hiển thị và khai thác thương mại nội dung khi chưa có đồng ý bằng văn bản. README SkillNexus ghi bộ cào chỉ dành cho phân tích phi thương mại.
3. Hoa hồng giới thiệu khoá học: có cần đăng ký gì không?
4. Luật AI: nếu định vị là "giáo dục" thì có rơi vào danh mục AI rủi ro cao trong giáo dục không (thời hạn tuân thủ 9/2027)?

## E. Ba mục đã chốt ngày 2026-10-22

Duy nhờ trả lời giúp. Ba mục này không còn là giả định mở.

- **Minh.** Brief không mở bằng một người minh họa. Phần vấn đề dùng số liệu đã có nguồn. Chuyện thật của Duy không chặn brief và không chặn việc xây.
- **500 người và 25%.** Ngưỡng đi tiếp là ít nhất 30 người thật tạo xong lộ trình 90 ngày, và ít nhất 25% số đó (8 người) mở lại lộ trình trong 14 ngày. Mức 30 người là ngưỡng sản phẩm. Mức 30 tin chỉ dùng để quyết định có hiện lương công khai hay không. Mức 500 người thử bị bỏ vì hai tháng gồm cả thời gian xây và v1 không mua người dùng.
- **CAC.** v1 không đo và không chạy quảng cáo mua người dùng. Chưa có số Việt Nam. Đo lại khi có kênh trả phí hoặc món v2.

## F. Cập nhật 2026-10-27

Các mục A và B ở trên giữ như lúc khép. Những điểm sau thay chúng:

- **Mục A, Bản đồ nhu cầu:** còn ba thành phố (Hà Nội, TP. Hồ Chí Minh, Đà Nẵng). Đo trên 832 tin: Hà Nội 355, TP. Hồ Chí Minh 444, Đà Nẵng 21, Hải Phòng 2, ba thành phố còn lại 0.
- **Mục A, Lộ trình 90 ngày:** câu "bản đầu không nhất thiết đa agent" không còn đúng. Bốn agent là yêu cầu bắt buộc.
- **Mục A, So sánh offer:** hoãn sang v1.1.
- **Mục B, Lưu trữ:** bản JSON-LD gốc lúc cào được lưu trên Silo `bronze/` (AD-21). Dòng tin trên Postgres vẫn không có mô tả. Duy chấp nhận rủi ro; câu hỏi pháp lý thêm vào PRD mục 12.
- **Mục B, Trích kỹ năng:** dùng taxonomy, không dùng LLM (AD-5).
- **Mục B, Việc tuần 1:** ô lương đã đo; xem `../../sprint-change-proposal-2026-10-27.md`.
