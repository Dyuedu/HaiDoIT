---
title: Đối chiếu nghiên cứu thị trường với PRD
type: prd-reconcile
source: _bmad-output/planning-artifacts/research/market-hai-do-it-nen-tang-nghe-nghiep-it-viet-n-2026-10-22/research.md
compared:
  - prd.md
  - addendum.md
language: vi
gap_count: 5
---

# Khoảng trống nghiên cứu mà PRD đang bỏ im

Nguồn là báo cáo thị trường ngày 2026-10-22. Đối chiếu với `prd.md` và `addendum.md` cùng thư mục. Không sửa hai tài liệu đó.

PRD và phụ lục đã giữ những cảnh báo đổi cách đọc: câu JobsGO gộp "thiếu lộ trình" với môi trường làm việc và chưa xác minh riêng; pháp lý để sau, không chặn v1; khoảng trống thu hẹp so với HireJack và ITviec. Phụ lục cũng đã chặn việc nâng lại thử giá, mức giá cũ, CAC, hỏi luật sư trước khi làm, và cố vấn đa agent như một bước trên sản phẩm. Năm mục dưới là phần còn lại.

## 1. Mẫu thành phố và mẫu lương mỏng hơn giả định Data/AI

Nghiên cứu ghi phân bố nhà tuyển dụng trả lời ITviec (H1/2024): TP. Hồ Chí Minh 76,7%, Hà Nội 21,4%, Đà Nẵng 1,9%. Một nguồn, từ sàn việc làm, có thể lệch. Các thành phố nhỏ rất ít dữ liệu. ITviec chỉ thu khoảng 1,8–2,3 nghìn phản hồi lương mỗi năm, quá mỏng để chia phân vị theo vai trò × cấp bậc × thành phố. Red team làm yếu thêm kỳ vọng dữ liệu cộng đồng sẽ đủ dày.

PRD giả định một số ô Data/AI theo thành phố dưới 30 tin và hẹn đo ở tuần 1. Bảy thành phố vẫn hiện, kể cả khi ít tin. Lương phân vị để sang v2 mà không kèm trần mẫu này. Người đọc có thể tưởng bản đồ bảy thành phố dày tương đương nhau, và v2 chỉ chờ thời gian.

Giữ bảy thành phố. Cảnh báo cần nằm cạnh mặt tiền và cạnh lương phân vị.

## 2. Phần trải nghiệm còn lại dễ bị sao chép; móc BHXH không phải số của dân IT

Nghiên cứu nói khoảng trống còn lại là trải nghiệm, không phải dữ liệu, nên dễ bị sao chép: các nền tảng lớn đang nắm tin và đã có AI. TopCV đã có máy tính gross/net, thuế TNCN và BHXH. Máy tính gross-net được ghi là đã phổ biến. Số 43,1% đóng BHXH thấp hơn thu nhập thực là một nguồn Navigos, cho người lao động nói chung, không có cắt riêng cho IT. Nếu dân IT đóng khác, móc miễn phí yếu đi.

PRD và phụ lục thu hẹp đúng so với HireJack và ITviec: còn lương công khai theo thành phố Việt Nam và lộ trình khoảng 90 ngày có Vì sao?. Hai tài liệu im về độ bền của khoảng trống đó, về việc máy tính lương–BHXH đã có trên sản phẩm khác, và về giới hạn của số BHXH. So sánh offer vì thế đứng như một việc đã được chứng minh cho dân IT.

## 3. Rủi ro pháp lý của mặt tiền được để sau, nhưng thiếu độ nặng

PRD ghi Điều 27 có thể coi thông tin thị trường miễn phí là dịch vụ việc làm phải xin phép, và Duy chấp nhận rủi ro, không chờ luật sư. Phụ lục giữ câu hỏi đó cùng điều khoản ITviec/TopDev, hoa hồng, và AI giáo dục từ tháng 9/2027.

Nghiên cứu gán bản đồ nhu cầu và lương vào rủi ro trung bình–cao theo câu chữ luật, vì thông tin thị trường lao động gồm cả tiền lương. Giấy phép đi với ký quỹ 300 triệu đồng. Chế tài cũ (Nghị định 12/2022) phạt 45–60 triệu đồng kể cả khi không thu phí; nghị định xử phạt mới chưa tìm được, nên mức phạt này chưa xác minh là còn áp dụng. Không thấy điều khoản miễn cho dịch vụ miễn phí. Người đọc câu "để sau, không chặn v1" chưa thấy mặt tiền nằm trong định nghĩa đó, cũng chưa thấy cái giá của giấy phép.

Cùng luật dữ liệu: ưu đãi năm năm của Điều 38 mất nếu theo dõi hành vi hoặc xử lý dữ liệu của "số lượng lớn" chủ thể; ngưỡng đó chưa tìm được. PRD chỉ yêu cầu bỏ thông tin cá nhân trước khi gọi API bên ngoài.

Đây là độ nặng của rủi ro đã chấp nhận. Không mở lại việc hỏi luật sư trước khi xây.

## 4. Số "lúc này" của ITviec quý 1/2025 đã bị chính báo cáo xếp cần cập nhật

PRD dùng tin AI/ML tăng 41% và lượt tìm "AI" tăng 89% như lý do thời điểm. Câu đã ghi là trên ITviec, và 34,3% đã được gọi là dự báo.

Bản đồ độ mới của báo cáo xếp nguồn tin ITviec quý 1/2025 vào nhóm cần cập nhật ngay, trước khi biến thành yêu cầu. Độ tin cậy của số đó là cao cho riêng nền tảng, thấp cho toàn quốc. Kỳ hạn độ mới của nhóm quy mô và tăng trưởng là 18 tháng; tính tới ngày báo cáo, mốc này đã quá hạn. PRD không gắn hạn dùng đó vào đoạn mở đầu.

## 5. "Ứng viên có thể trả" không kèm câu chưa có bằng chứng

PRD lấy các số nỗi đau làm lý do lúc này, và gọi review dự án là món ứng viên có thể trả ở v2. Hai tháng này không thu tiền ứng viên.

Báo cáo ghi độ tin cậy tổng trung bình. Nỗi đau mạnh chỉ chứng minh vấn đề có thật, không chứng minh người dùng trả tiền cho cố vấn. Nhóm đau nhất có thu nhập thấp nhất, trung vị khoảng 10–14 triệu đồng/tháng. Không tìm thấy bằng chứng dân IT Việt Nam trả phí định kỳ cho công cụ nghề nghiệp. Khuyến nghị thu tiền của báo cáo tự gắn độ tin cậy thấp–trung bình vì lý do đó.

Câu cần giữ là giới hạn bằng chứng trên món v2. Không đưa lại thử giá, mức 50.000đ hay 150.000đ.

## Đã đối chiếu và không lập thành khoảng trống

- Thử giá, phỏng vấn trước khi viết PRD, hỏi luật sư trước khi xây.
- Cố vấn đa agent như sản phẩm. PRD đã bỏ bước chạy nhiều agent.
- Mức giá cũ, mốc người dùng đã bỏ, CAC.
- Câu "thiếu lộ trình" chưa tách riêng. PRD đã ghi là giả định.
- Bảy thành phố, dữ liệu ITviec và TopDev đã trích, không chờ phép. Quyết định này đứng ở PRD.
- ChatGPT và lời khuyên chung. PRD đã ghi Học gì tiếp? và lộ trình mất lý do nếu người dùng không thấy dữ liệu thật hơn lời khuyên chung.
