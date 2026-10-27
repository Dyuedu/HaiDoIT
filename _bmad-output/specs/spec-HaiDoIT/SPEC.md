---
id: SPEC-HaiDoIT
companions:
  - ../../planning-artifacts/architecture/architecture-HaiDoIT-2026-10-22/ARCHITECTURE-SPINE.md
  - ../../planning-artifacts/ux-designs/ux-HaiDoIT-2026-10-22/DESIGN.md
  - ../../planning-artifacts/ux-designs/ux-HaiDoIT-2026-10-22/EXPERIENCE.md
  - ../../planning-artifacts/prds/prd-HaiDoIT-2026-10-22/addendum.md
sources:
  - ../../planning-artifacts/prds/prd-HaiDoIT-2026-10-22/prd.md
  - ../../planning-artifacts/briefs/brief-HaiDoIT-2026-10-22/brief.md
---

> **Canonical contract.** This SPEC and the files in `companions:` are the complete, preservation-validated contract for what to build, test, and validate. Source documents listed in frontmatter are for traceability — consult them only if you need narrative rationale or prose color this contract intentionally omits.

# Hải Đồ IT

## Why

Người mới vào nghề IT, fresher và người chuyển hướng ở Việt Nam không có chỗ thử một kỹ năng rồi thấy số việc và lương công khai đổi theo thành phố, trước khi bỏ vài tháng học. Các trang tuyển dụng đang ghép việc và đánh giá nhà tuyển dụng. Hải Đồ IT trả lời «học gì tiếp» bằng tin đang mở, rồi đưa lộ trình khoảng 90 ngày có nguồn.

## Capabilities

- **CAP-1** Bản đồ nhu cầu
  - **intent:** Người xem nhu cầu hôm nay tại ba thành phố, lọc theo vai trò, và mở một thành phố để thấy cơ cấu vai trò, lương công khai hoặc câu chưa đủ mẫu, dấu kỹ năng đã có, cùng tín hiệu sớm hoặc câu chưa ghi nhận.
  - **success:** Payload luôn đủ ba thành phố. Đổi vai trò thì số tin đổi. Chưa chọn thành phố thì không hiện lương đầu trang. Dưới 30 tin trong tập lương 180 ngày thì không hiện số lương. Chân trang hiện ngày của lần làm mới dữ liệu gần nhất. Trước khi có quy tắc phát hiện, thẻ dùng câu chưa ghi nhận tín hiệu. Các mốc 6, 12 và 18 tháng chưa có số cho đến khi có công thức dự báo đã đo.

- **CAP-2** Học gì tiếp?
  - **intent:** Người thêm hoặc bớt kỹ năng giả định và thấy số tin trước và sau, thời gian học, lương công khai hoặc trạng thái ẩn, cùng danh kỹ năng nên học tiếp.
  - **success:** Tin được đếm khi tập kỹ năng đang xét khớp từ 50% số kỹ năng của tin trở lên. Số trước dùng kỹ năng đã có; số sau dùng kỹ năng đã có cùng kỹ năng giả định đang chọn. Thêm kỹ năng giả định thì số sau không nhỏ hơn số trước. Danh xếp theo số tin mở thêm trên mỗi tuần học. Ô mỏng thì nới toàn quốc trước, rồi nhóm vai gần, và Vì sao? nói đang ở bước nào. Lương không lấy từ ô còn dưới 30 tin. Chưa có thành phố, cấp và vai trò mục tiêu thì chưa có chênh lệch.

- **CAP-3** Lộ trình 90 ngày
  - **intent:** Người nhận ba chặng, mỗi chặng một dự án, với Vì sao? trên mọi nhận định, rồi lưu bằng email và mở lại đúng bản đó trên máy khác.
  - **success:** Chưa có thành phố, cấp và vai trò mục tiêu thì không tạo lộ trình. Đủ ba chặng ngày 1–30, 31–60, 61–90. Nhận định bị loại vì thiếu dữ liệu vẫn có Vì sao? và không nêu một mức lương. Thiếu liên kết khóa vẫn lưu được. Thư gửi thất bại thì lộ trình chưa được lưu. Mở đúng liên kết trên máy khác thì ra đúng thành phố, cấp, vai trò, kỹ năng đã có và ba chặng. Sau ngày 14 liên kết vẫn mở. Trên các lộ trình đã lưu, mọi nhận định trỏ đúng tin tuyển hoặc số liệu nguồn.

- **CAP-4** So sánh offer — **hoãn v1.1** (Duy, 2026-10-25). Không xây trong hai tháng này. Giữ hợp đồng dưới đây cho v1.1.
  - **intent:** Người so thực nhận cả năm của hai offer và thấy khoản hụt khi căn cứ đóng bảo hiểm thấp hơn lương, mà không cần tài khoản.
  - **success:** Đóng trang thì không còn nội dung offer trên máy chủ. Ngày remote không đổi tiền. Kết quả dùng bộ số thuế và BHXH 2026 trong phụ lục. Màn nói đây là ước tính. Chênh dưới 1% thực nhận cả năm thì hai offer gần ngang.

- **CAP-5** Soi tin
  - **intent:** Người đưa một link và thấy tin đó được làm mới bao nhiêu lần, ngày thấy đầu, ngày thấy gần nhất, tin trùng nếu có, và lương có bất thường hay không.
  - **success:** Link không có trong dữ liệu thì câu chưa soi được, và chữ dán nhầm không được lưu. Ô dưới 30 tin thì không kết luận lương bất thường. Trước tuần 1, màn hiện ba số kiểm được và không gắn nhãn tin treo như sự thật đã đo.

- **CAP-6** Xu hướng kỹ năng
  - **intent:** Người thấy hướng tăng, giảm hoặc đi ngang của kỹ năng trên bản đồ, và Học gì tiếp? cùng lộ trình dùng cùng lớp dữ liệu đó khi xếp hạng và khi viết Vì sao?.
  - **success:** Không có mục điều hướng riêng cho lớp này. Chưa có chuỗi đã đo thì khối hiện chưa đủ mẫu và không có kỹ năng nào bị đánh dấu đang giảm. Khi một kỹ năng bị đánh dấu đang giảm, kỹ năng đó không đứng hạng nhất và Vì sao? nói mức giảm.

## Constraints

- Web, không ứng dụng cài máy. Dùng được ở bề rộng trình duyệt điện thoại và máy bàn. Bốn mục điều hướng: Bản đồ nhu cầu, Học gì tiếp?, Lộ trình 90 ngày, Soi tin. Bản đồ nhu cầu là chỗ mở vào. So sánh offer là mục thứ năm ở v1.1. Ba người, hai tháng.
- Không phải sàn tuyển dụng. Người xem số gộp, và chỉ tra một link mình dán. Không ghép hồ sơ với tin, không điểm nhà tuyển dụng, không đọc hợp đồng.
- Thành phố chỉ có ba tên: Hà Nội, TP. Hồ Chí Minh, Đà Nẵng. Thu từ bảy ngày 2026-10-27 vì Hải Phòng có 2 tin, còn Cần Thơ, Quy Nhơn và Nha Trang có 0. Toàn quốc là bước nới của Học gì tiếp?, gộp ba thành phố, không phải thành phố thứ tư.
- Lương công khai là một số. Tập lương của một ô là tin có lương đã thấy trong 180 ngày, đang mở hay đã đóng. Tin chỉ có lương USD được đổi sang VND bằng một tỷ giá cố định trong cấu hình, và màn ghi tỷ giá cùng ngày áp dụng khi số đang hiện có dùng tin USD. Ẩn trên mọi màn khi tập lương dưới 30 tin. Không hạ ngưỡng để hiện thêm số. Không hiện dải phân vị.
- Dòng tin trên Postgres không có mô tả, tiêu đề, tên công ty, tên và liên hệ người tuyển. Màn không hiện nguyên văn mô tả. Chữ người dùng dán không được lưu. Bản JSON-LD gốc lấy lúc cào được lưu trên Silo `bronze/`; Duy chốt giữ bản này ngày 2026-10-27 và chấp nhận rủi ro pháp lý. API công khai không trả bản đó. Chỉ lệnh nạp và đồ thị agent đọc.
- Không mật khẩu, không đăng nhập mạng xã hội, không hồ sơ công khai. Email chỉ để lưu và mở lại lộ trình. Ô email đứng lúc lộ trình hiện, không đứng trên Bản đồ nhu cầu. So sánh offer và Soi tin dùng được khi chưa lưu.
- Tin đang mở được làm mới mỗi ngày. VietJobs chỉ được ghi công như nền lịch sử. Không cào TopCV, VietnamWorks, CareerViet, Glints, SmartRecruiters. Lấy tin thì đọc robots.txt, danh xưng trung thực, giãn cách ít nhất 3 giây, và dừng khi bị chặn.
- Số đã trích, gồm ITviec và TopDev, được đưa vào sản phẩm. Không xin phép trang nguồn và không chờ luật sư trước khi làm. Câu hỏi pháp lý không chặn hai tháng xây.
- Trước khi có công thức đã đo, dự báo 6, 12 và 18 tháng không hiện số. Không dùng hệ số minh họa của prototype. v1 không dự báo lương.
- Cách xây theo architecture spine. Mặt nhìn theo DESIGN.md. Luồng, câu chữ và trạng thái theo EXPERIENCE.md. Bộ số thuế và BHXH 2026 theo phụ lục PRD.
- Bốn agent là yêu cầu bắt buộc của v1 (Duy, 2026-10-27): Bản đồ, Học gì tiếp, Lộ trình và Soi tin. Mỗi agent có đủ bốn phần: LLM Ollama, lập kế hoạch, bộ nhớ, và tool. Mỗi agent chỉ thấy đúng tool được giao. So sánh offer không có agent. Một lượt dừng sau 6 bước sinh của model, hoặc sau 2 lần từ chối câu liên tiếp. Vì sao? trả trong cùng lượt. Mọi số trong câu và trong Vì sao? phải có trong kết quả tool của lượt đó. Quan hệ kỹ năng lấy bằng GraphRAG trên đồ thị Neo4j đang có. Không có embedding và không có vector DB. Màn ghi tên agent đã viết câu, không hiện kế hoạch và không hiện lời gọi tool.
- Chưa chọn cấp thì ô lương dùng Junior. Học gì tiếp? chỉ dựng kịch bản cho Fresher và Junior. Bộ lọc vai trò mặc định là Tất cả.
- Khi ô một thành phố còn mỏng, nới toàn quốc cùng vai trò và cùng cấp trước, rồi nới nhóm vai gần: Data/AI đứng riêng, Backend với Frontend, DevOps/Cloud với Bảo mật, Mobile đứng riêng.
- Một email giữ một lộ trình. Lưu lần mới thì thay lộ trình cũ và tính lại 14 ngày.
- Danh kỹ năng để chọn là danh cố định. Người dùng không gõ một kỹ năng ngoài danh. Số tuần học do nhóm gán, không suy từ tin.
- Đo ngày 2026-10-27 trên 832 tin: không ô Fresher hoặc Junior nào đủ 30 tin có lương, kể cả toàn quốc và kể cả khi đã đổi USD. Lúc ra mắt lương thường ẩn, và trạng thái ẩn phải rõ trên mọi màn. Ngưỡng mức khớp 50% là tham số nhóm, đo lại khi kho tin lớn hơn. Ngưỡng tin treo chờ tuần 1. Trước đó không gắn nhãn tin treo như sự thật.
- Lan, Khoa, Mai chỉ là tên mock của cảnh. Không phải bằng chứng người dùng. Không thêm cảnh suýt trả tiền cho một khóa.

## Non-goals

- Ghép việc, gợi ý tin vừa mở khóa, đánh giá nhà tuyển dụng, chỉ số phản hồi, và trải nghiệm ứng tuyển.
- Đọc hợp đồng, tư vấn pháp lý, và lộ trình của những người giống người dùng.
- Review dự án, chỗ nộp repo, phòng tập thương lượng, và lương theo phân vị.
- Giá, gói, chỗ trả tiền của ứng viên, liên kết khóa học, nhãn hoa hồng, và đếm lượt mở liên kết đó.
- Nút báo nguồn, agent đọc hợp đồng, agent ghép việc, agent chấm nhà tuyển dụng, agent đọc CV, ứng dụng cài máy, và cổng riêng cho trường hoặc bootcamp.
- Thêm thành phố, màn Remote, và màn Nhật trong hai tháng này.
- So sánh offer và kiểm tra BHXH trong hai tháng này (hoãn v1.1).

## Success signal

Hai tháng được tính là đi tiếp khi đủ cả bốn mức, đo trên người thật, không mua người dùng. Ít nhất 30 email đã lưu một lộ trình. Trong số đó, ít nhất 25% mở lại đúng lộ trình trong 14 ngày kể từ lúc lưu, và không dưới 8 email. Ít nhất một trường hoặc bootcamp có ghi chú ngày, tên, người đồng ý, và câu họ sẽ thử web cùng ứng viên. Mọi nhận định trên lộ trình đã lưu có Vì sao? trỏ đúng tin tuyển hoặc số liệu nguồn. Một câu không có nguồn là cả mốc trượt. Không hạ ngưỡng 30 tin để có thêm lương đang hiện. Số tin được gợi ý để nộp không phải thành công.
