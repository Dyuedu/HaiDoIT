---
stepsCompleted:
  - step-01-validate-prerequisites
inputDocuments:
  - _bmad-output/planning-artifacts/prds/prd-HaiDoIT-2026-10-22/prd.md
  - _bmad-output/planning-artifacts/prds/prd-HaiDoIT-2026-10-22/addendum.md
  - _bmad-output/planning-artifacts/architecture/architecture-HaiDoIT-2026-10-22/ARCHITECTURE-SPINE.md
  - _bmad-output/planning-artifacts/ux-designs/ux-HaiDoIT-2026-10-22/DESIGN.md
  - _bmad-output/planning-artifacts/ux-designs/ux-HaiDoIT-2026-10-22/EXPERIENCE.md
  - _bmad-output/specs/spec-HaiDoIT/SPEC.md
---

# HaiDoIT - Epic Breakdown

## Overview

Bản này liệt kê yêu cầu đã rút từ PRD, phụ lục, spec, UX và kiến trúc. Duy đã duyệt bốn epic vào 2026-10-25, sau khi hoãn epic So sánh offer sang v1.1. Mỗi epic đã có story.

Cập nhật 2026-10-27, theo `sprint-change-proposal-2026-10-27.md`: tin đủ điều kiện tính bằng mức khớp ≥ 50% thay luật AND; ba thành phố thay bảy; lương dùng cửa sổ 180 ngày và đổi USD theo tỷ giá cố định; bốn agent là yêu cầu bắt buộc; bản JSON-LD gốc giữ trên Silo.

Khi PRD hoặc UX còn vẽ một khoảng dự báo, yêu cầu đang sống theo spec và AD-12: trước khi có công thức đã đo, các mốc dự báo không có số.

Duy chọn cách A vào 2026-10-23, rồi chốt định nghĩa agent là LLM + lập kế hoạch + bộ nhớ + tool. Bốn agent là Bản đồ, Học gì tiếp, Lộ trình, Soi tin. PRD và UX viết trước đó còn cấm mạng năm agent trên màn. Yêu cầu đang sống cho phép ghi tên agent đã viết câu. Màn không hiện kế hoạch và không hiện lời gọi tool.

## Requirements Inventory

### Functional Requirements

FR1: Người xem nhu cầu hôm nay tại đúng ba thành phố: Hà Nội, TP. Hồ Chí Minh, Đà Nẵng. Ba thành phố vẫn có mặt khi một thành phố ít tin. Đổi bộ lọc vai trò thì số tin của thành phố đổi theo vai trò đó. Mỗi lần xem có ngày của lần làm mới dữ liệu gần nhất. Lần đầu không có hồ sơ mẫu. Khi chưa có kỹ năng đã có, không có dấu «đã có». Bộ lọc vai trò mặc định là Tất cả. Các vai trò là Tất cả, Backend, Frontend, Data/AI, DevOps/Cloud, Mobile, Bảo mật.

FR2: Người chuyển tầm nhìn sang 6, 12 hoặc 18 tháng. Trước khi có công thức đã đo, các mốc đó và ô dự báo trên thẻ lúc đang xem nay không có số và không có khoảng. Câu là «Chưa ghi nhận dự báo cho mốc này.» Mốc nay hiện số tin đang mở. v1 không dự báo lương. Khi có công thức đã đo, mỗi mốc là một khoảng số tin có nhãn dự báo, không phải một điểm, và ô trên thẻ lúc đang xem nay lấy khoảng 12 tháng. Không dùng hệ số minh họa của prototype.

FR3: Người chọn một thành phố và thấy cơ cấu vai trò, lương công khai hoặc câu chưa đủ mẫu, và đúng một tín hiệu sớm kèm Vì sao? hoặc câu «Chưa ghi nhận tín hiệu đáng kể cho thành phố này.» Cơ cấu là tỷ lệ tin của từng vai trò trong thành phố, cộng một nhóm còn lại, tổng 100%. Đã chọn thành phố thì lương trên thẻ và ô lương đầu trang cùng một ô mẫu. Một vai trò đang lọc thì ô là vai trò đó, thành phố đang chọn, và cấp của hồ sơ phiên. Chưa chọn cấp thì dùng Junior. Bộ lọc Tất cả thì vai trò của ô là vai trò có nhiều tin đang mở nhất tại thành phố đó. Chưa chọn thành phố thì ô lương đầu trang không hiện số. Đủ 30 tin trong tập lương 180 ngày thì hiện một lương công khai. Dưới ngưỡng thì không hiện số và có câu chưa đủ mẫu. Thành phố vẫn xem được khi lương đang ẩn. Chưa có quy tắc phát hiện thì thẻ dùng câu chưa ghi nhận tín hiệu.

FR4: Khi hồ sơ phiên có kỹ năng đã có, kỹ năng đó được đánh dấu trên danh kỹ năng của thành phố đang xem. Kỹ năng không nằm trong hồ sơ thì không có dấu. Xóa kỹ năng đã có thì dấu mất trong cùng phiên. Danh trên thẻ là kỹ năng đang được nhắc trong tin của thành phố đó, không phải cả danh chip.

FR5: Người thêm hoặc bớt kỹ năng giả định và thấy số tin trước và sau, thời gian học, và lương công khai trước và sau hoặc trạng thái ẩn. Số tin là số tin đủ điều kiện. Thời gian học là tổng số tuần của các kỹ năng giả định đang chọn. Chưa thêm kỹ năng giả định thì không có chênh lệch. Bỏ hết kỹ năng giả định thì các số trở về trạng thái trước. Danh kỹ năng để chọn là danh cố định, cùng taxonomy pipeline đã trích. Người dùng không gõ một kỹ năng ngoài danh. Học gì tiếp? chỉ dựng kịch bản cho Fresher và Junior.

FR6: Hệ thống xếp các kỹ năng còn lại theo số tin mở thêm trên mỗi tuần học. Người thêm được một kỹ năng từ danh đó vào kỹ năng giả định. Mỗi dòng hiện số tin tăng, số tuần, và số tin trên mỗi tuần. Số tuần là số nhóm gán trong danh, không suy từ tin. Kỹ năng đã nằm trong kỹ năng đã có hoặc đang giả định thì không còn trong danh. Kỹ năng lớp dữ liệu đánh dấu đang giảm không đứng hạng nhất.

FR7: Khi ô vai trò × thành phố × cấp có dưới 30 tin trong tập lương 180 ngày, Học gì tiếp? nới toàn quốc (gộp ba thành phố) cùng vai trò và cùng cấp trước. Vẫn dưới ngưỡng thì nới nhóm vai gần: Data/AI đứng riêng, Backend với Frontend, DevOps/Cloud với Bảo mật, Mobile đứng riêng. Vì sao? của kết quả đã nới nói ô gốc dưới 30 và nói đang ở bước toàn quốc hay bước nhóm vai gần. Không hiện lương lấy từ ô mỏng. Phạm vi đã nới vẫn dưới 30 thì lương tiếp tục ẩn và có câu chưa đủ mẫu. Đo 2026-10-27: không ô Fresher hoặc Junior nào đủ 30 tin có lương, kể cả toàn quốc, nên lúc ra mắt lương thường ẩn.

FR8: Số trước trong Học gì tiếp? tính từ thành phố, cấp bậc, vai trò mục tiêu và kỹ năng đã có của hồ sơ phiên. Đổi thành phố hoặc cấp thì số trước đổi. Thêm một kỹ năng đã có thì độ phủ trước tăng và kỹ năng đó không bị gợi ý như thể chưa có. Chưa chọn đủ thành phố, cấp và vai trò mục tiêu thì chưa hiện chênh lệch. Tin đủ điều kiện là tin đang mở, trong phạm vi đang tính, đúng vai trò mục tiêu, đúng cấp, có ít nhất một kỹ năng, và có mức khớp tin từ 50% trở lên với tập đang xét. Mức khớp tin là số kỹ năng của tin nằm trong tập, chia cho số kỹ năng của tin. Thêm kỹ năng giả định thì số sau không nhỏ hơn số trước.

FR9: Người tạo lộ trình 90 ngày từ hồ sơ phiên và các kỹ năng giả định đang chọn. Chưa có thành phố, cấp và vai trò mục tiêu thì không tạo được. Đủ ba chặng, ngày 1–30, 31–60, 61–90. Mỗi chặng có kỹ năng của chặng, tên một dự án thực hành, và một câu người học làm ra cái gì. Kỹ năng trên lộ trình nằm trong kỹ năng giả định đang chọn, hoặc là kỹ năng đã có được đào sâu khi không còn kỹ năng giả định. Đổi kỹ năng giả định rồi tạo lại thì nội dung chặng đổi theo. Một chặng không có liên kết khóa vẫn tạo và lưu được.

FR10: Mỗi nhận định trên lộ trình có đúng một Vì sao?, kể cả nhận định bị loại vì thiếu dữ liệu. Nhận định từ tin trỏ tập đã trích hoặc link gốc, không trỏ nguyên văn mô tả. Nhận định từ báo cáo gọi tên một trong bốn: ITviec, TopDev, TopCV, JobOKO. Nhận định thiếu dữ liệu nói thiếu dữ liệu và không nêu một mức lương. Lộ trình đã lưu mà còn nhận định thiếu Vì sao? thì không đạt mốc 100%. Lộ trình đó vẫn tính là một lộ trình đã lưu.

FR11: Hai tháng này không có liên kết khóa, không có nhãn hoa hồng, và không đếm lượt mở liên kết đó. Web không có chỗ bấm sang một khóa học. Khoản này không được gọi là tiền của kỳ này.

FR12: Người lưu lộ trình bằng một email. Gửi được thì lưu hồ sơ lẫn lộ trình và gửi liên kết mở lại. Không có mật khẩu. Bản đồ nhu cầu và Học gì tiếp? dùng được trước khi có email. Hồ sơ lúc đó chỉ ở trên máy. Gửi thất bại thì lộ trình còn trên máy và chưa tính là tạo xong. Không có hồ sơ công khai. Email không hiện cho người khác. Ô email đứng lúc lộ trình hiện, không đứng trên Bản đồ nhu cầu.

FR13: Người mở đúng liên kết thì thấy đúng thành phố, cấp, vai trò mục tiêu, kỹ năng đã có và ba chặng của lần lưu, kể cả trên máy khác. Sau ngày 14 liên kết vẫn mở đúng lộ trình. Lần mở trong 14 ngày kể từ lúc lưu được tính vào phép đo. Lần mở sau ngày 14 không tính. Một email một lộ trình. Lưu lần nữa thì thay lộ trình trước và 14 ngày tính lại từ lần lưu mới. Email chưa có lộ trình thì không tạo dòng trống. So sánh offer và Soi tin không đòi email.

FR14: Xu hướng và hạn dùng kỹ năng là một lớp dữ liệu dùng chung cho Bản đồ nhu cầu, Học gì tiếp? và lộ trình. Không có mục điều hướng riêng và không có màn hạn dùng. Chưa có chuỗi đã đo thì khối hiện «Chưa đủ mẫu.» và không có kỹ năng nào bị đánh dấu đang giảm. Khi một kỹ năng bị đánh dấu đang giảm, kỹ năng đó không đứng hạng nhất và Vì sao? nói mức giảm. v1 không xin người dùng đóng góp mức lương của chính họ.

FR15: Người nhập hai offer và thấy offer nào có thực nhận cả năm cao hơn, cùng mức chênh, hoặc câu hai offer gần ngang nhau khi chênh dưới 1% thực nhận cả năm. Mỗi offer có tên công ty, lương tháng, gross hoặc net, số người phụ thuộc, số tháng thưởng, phụ cấp, số ngày remote mỗi tuần, căn cứ đóng bảo hiểm, và mức đóng khi chọn mức thấp hơn. Ngày remote hiện cùng offer và không đổi thực nhận cả năm. Offer gross đóng trên lương thật thì mức đóng bằng lương gross. Offer net thì mức đóng mặc định là gross đã dò ngược, trừ khi người dùng nhập mức khác. Đổi một ô thì thực nhận tính lại. Màn hiện bộ số thuế và BHXH 2026 trong phụ lục, và câu kết quả là ước tính, không thay thế tư vấn thuế. Đóng trang thì không còn nội dung offer trên máy chủ.

FR16: Khi một offer đóng bảo hiểm trên mức thấp hơn lương gross đang dùng, màn hiện khoản hụt cả năm, gồm phần người lao động và phần công ty ở mức ước tính, và nói các chế độ tính trên mức thấp đó. Offer đóng trên lương thật thì không có câu hụt. Mức đóng không vượt quá lương gross của offer đó.

FR17: Người dán một link đang có trong dữ liệu và thấy số lần làm mới, ngày thấy đầu, ngày thấy gần nhất, tin trùng nếu có, và kết luận lương. Ba số kiểm được mà không cần nhãn tin treo. Có tin trùng thì đó là tin đang mở khác, khác link, cùng kỹ năng, thành phố, cấp bậc và khoảng lương. Câu cảnh báo không cần tên công ty. Lương bất thường chỉ khi ô của tin đủ 30 tin có khoảng lương và lương công khai không nằm trong khoảng của tin. Dưới ngưỡng thì câu chưa đủ mẫu để xét lương, không kết luận bất thường. Không hiện điểm trên 100, không hiện nhãn đáng tin hoặc rủi ro cao, không hiện chỉ số AI. Ngưỡng tin treo chưa được đo. Trước tuần 1 không gắn nhãn tin treo như sự thật và không viết test như thể quy tắc tạm đã đúng.

FR18: Link không có trong dữ liệu thì câu «Chưa soi được tin này.» Không có ô dán mô tả công việc. Chữ người dùng dán nhầm không được lưu và không được hiện.

### NonFunctional Requirements

NFR1: Mọi số lương công khai trên mọi màn đều vắng mặt khi tập lương của ô mẫu dưới 30 tin. Tập lương là tin có lương đã thấy trong 180 ngày, đang mở hay đã đóng. Lương USD đổi sang VND bằng tỷ giá cố định trong cấu hình, và màn ghi tỷ giá cùng ngày áp dụng khi dùng tin USD. Gồm ô lương đầu Bản đồ nhu cầu, thẻ thành phố, Học gì tiếp?, và kết luận lương của Soi tin. Không hạ ngưỡng để hiện thêm số. Không hiện dải phân vị.

NFR2: Dòng tin trên Postgres không có mô tả, tiêu đề, tên công ty, tên và liên hệ người tuyển. Màn không hiện nguyên văn mô tả, kể cả chữ người dùng dán. Chữ người dùng dán không được lưu. Bản JSON-LD gốc lấy lúc cào nằm trong Silo; Duy chốt giữ bản này ngày 2026-10-27 và chấp nhận rủi ro pháp lý. API công khai không trả bản đó. Chỉ lệnh nạp và đồ thị agent đọc.

NFR3: Khi nguồn dữ liệu lỗi, Bản đồ nhu cầu nói «Không tải được dữ liệu thị trường.» và có lối thử lại. Nếu máy còn số của lần xem gần nhất thì giữ số đó.

NFR4: Khi bộ lọc không còn tin, Bản đồ nhu cầu nói «Không có tin nào khớp bộ lọc.» và có lối bỏ lọc về Tất cả.

NFR5: Giao diện chữ Việt. Web dùng được ở bề rộng trình duyệt điện thoại và ở bề rộng máy bàn. Không làm ứng dụng cài máy. Việc chạy trên điện thoại vẫn là giả định trong PRD, vì cảnh mock bắt đầu trên điện thoại.

NFR6: Một lộ trình đã lưu mở lại được từ liên kết trên máy khác với máy đã tạo. Biết email không trả lộ trình trên màn.

NFR7: Bốn mức đi tiếp đo trên người thật, không mua người dùng: từ 30 email đã lưu một lộ trình, từ 25% số đó mở lại trong 14 ngày và ít nhất 8 email, từ 1 trường hoặc bootcamp có ghi chú đồng ý thử, và 100% nhận định trên lộ trình đã lưu có Vì sao? trỏ đúng nguồn. Số tin được gợi ý để nộp không phải thành công. Hai tháng này không đo ví ứng viên và không đo CAC.

### Additional Requirements

- Không dùng starter template. Không lấy mật khẩu, JWT, hay shadcn của full-stack-fastapi-template. Mặt nhìn lấy DESIGN.md và prototype đã chốt, không lấy các file mock đã bị loại.
- Một repo. `frontend/` là Next.js 16.4.2. `backend/` là FastAPI 0.159.1 trên Python 3.12. `scraper/` ghi file. Next.js chỉ gọi HTTP của FastAPI và vẽ payload. Phép tính duy nhất trên trình duyệt là So sánh offer.
- Một Postgres Supabase gói trả phí, dùng chung cho máy chạy web và máy code. Chuỗi nối chỉ nằm trong backend, qua SQLModel 0.0.48. Không dùng đăng nhập Supabase. Trình duyệt không gọi API tự sinh của Supabase.
- Docker Compose 5.6.1 trên máy chạy web bật web, FastAPI, Ollama 0.40.8, Neo4j 2026.10.0-community, Redis 8.8.3 và Silo `pgsty/silo:RELEASE.2026-10-18T00-00-00Z`. Compose không bật Postgres. Neo4j, Redis và Silo chỉ có một bản, trên máy đó. Máy code nối tới ba dịch vụ đó và tới Supabase, không dựng bản thứ hai. Thư thật chỉ gửi từ máy chạy web, qua hộp thư của nhóm. Máy code không gửi thư cho người dùng.
- Cào nằm trong repo này. Hai kênh: HTML của ITviec, TopDev, Cốc Cốc, và JSON công khai của Greenhouse, Lever, Workable. Không cào TopCV, VietnamWorks, CareerViet, Glints, SmartRecruiters. Đọc robots.txt, danh xưng trung thực, giãn cách ít nhất 3 giây, dừng khi trang chặn bot. Không gọi Ollama và không gọi API mô hình bên ngoài để trích kỹ năng.
- Mỗi lần cào đủ kênh ghi đè object `open-jobs/open-jobs.jsonl` trên Silo, rồi đẩy một phần tử vào list Redis `ingest`. Kênh lỗi thì không ghi đè. Lệnh nạp lấy phần tử đó và đọc đúng object. `source` chỉ là itviec, topdev, coccoc, greenhouse, lever, workable. `skills` là mảng tên có trong `scraper/taxonomy.json`. Lương VND là số nguyên hoặc null. Lương USD là số như nguồn ghi hoặc null, giữ ở cột `salary_min_usd` và `salary_max_usd`. `city` chỉ là Hà Nội, TP. Hồ Chí Minh hoặc Đà Nẵng; dòng khác bị bỏ. Lệnh nạp tự tính `source_id` bằng SHA-256 hex thường của source, ký tự U+001F, rồi URL, theo `jobboards.compute_source_id`. Client Silo là `minio` 7.2.20. Client Redis là `redis` 8.1.0.
- Lệnh nạp là chỗ duy nhất ghi bảng `job_posting`. Đang mở nghĩa là có trong file của lần nạp thành công gần nhất. Tin vắng mặt được giữ, không đếm trên bản đồ, không xóa. `seen_count` tăng một mỗi lần nạp mới. Chân trang đọc `ingest_run.succeeded_at` theo ngày lịch Asia/Ho_Chi_Minh. VietJobs không vào tập đang mở.
- Bảng `skill` seed tên từ `scraper/taxonomy.json`. Nhóm sửa số tuần, vai trò và cờ kỹ năng yêu cầu. Nhóm không đổi tên trên Supabase. Vai trò của tin là vai trò được nhiều kỹ năng của tin gán nhất. Hòa hoặc chưa gán thì tin không có vai trò. Lệnh nạp chiếu bảng đó sang Neo4j: nút `Skill` và `Role`, cạnh `HAS_ROLE` và `REQUIRED_FOR`. Neo4j không giữ tin, lương, hay số đếm. Driver là `neo4j` 6.4.1.
- Bốn agent là yêu cầu bắt buộc của v1 (Duy, 2026-10-27). Một agent là LLM + lập kế hoạch + bộ nhớ + tool. LLM là Ollama 0.40.8 và Qwen3 8B. LangChain 1.4.7 để model sinh lời gọi tool. LangGraph 1.2.16 chạy tool và đưa kết quả lại. Bốn agent: Bản đồ, Học gì tiếp, Lộ trình, Soi tin. So sánh offer không có agent. Bản đồ chỉ có `market_snapshot` và `graph_retrieve`. Học gì tiếp chỉ có `skill_delta` và `graph_retrieve`. Lộ trình chỉ có `roadmap_frame`, `read_saved_roadmap` và `graph_retrieve`. Soi tin chỉ có `lookup_posting`, `graph_retrieve` và `read_bronze`. Một lượt dừng sau 6 bước sinh của model, hoặc sau 2 lần từ chối câu liên tiếp. Chưa có câu đạt thì điền câu mẫu từ kết quả tool đã có. Chưa có kết quả tool thì dùng câu lỗi trong EXPERIENCE.md. `lookup_posting` trả thêm `source_id` và `skills`. Không thấy tin thì `source_id` null, `skills` rỗng, và lượt kết thúc với «Chưa soi được tin này.» `read_bronze` không trả JSON-LD. Vì sao? nằm trong cùng payload với câu. `roadmap_frame` giữ tối đa ba kỹ năng giả định hạng cao nhất, mỗi chặng một kỹ năng. Phần tử Redis `ingest` là JSON có `sha256` của object ảnh. Chỉ máy chạy web lấy list đó. Postgres commit chỉ sau khi Neo4j cập nhật xong. Không có vector DB và không có embedding. GraphRAG dùng `neo4j-graphrag` 1.22.0 chỉ để truy xuất. Cạnh là `(:Skill)-[:HAS_ROLE]->(:Role)` và `(:Skill)-[:REQUIRED_FOR]->(:Role)`. Cắt 40 nút trong cùng tầng theo `taxonomy.json` với Skill và theo thứ tự vai AD-14 với Role. Không có agent đọc hợp đồng, ghép việc, chấm nhà tuyển dụng, hay đọc CV. Lộ trình chỉ commit sau khi hộp thư nhận. Thư lỗi thì rollback.
- Prefix `bronze/` trên Silo giữ JSON-LD mô tả đã đọc lúc cào, một object một tin, khóa bằng `source_id`. Chỉ lệnh nạp và đồ thị agent đọc. API công khai không trả prefix đó.
- API công khai trả số gộp và một lần tra đúng link người dán. Không trả danh tin để ứng tuyển, không ghép hồ sơ, không điểm nhà tuyển dụng, không đọc hợp đồng.
- Số đã trích, gồm ITviec và TopDev, được đưa vào sản phẩm. Không xin phép trang nguồn và không chờ luật sư trước khi làm. Câu hỏi pháp lý không chặn hai tháng xây.
- Lan, Khoa, Mai chỉ là tên mock của cảnh. Không phải bằng chứng người dùng. Không thêm cảnh suýt trả tiền cho một khóa.
- Tên miền và vùng Supabase chọn lúc đưa máy chạy web lên. Công thức dự báo, quy tắc tín hiệu sớm, ngưỡng nhãn tin treo, và quy tắc tám quý chờ tuần 1 đo.

### UX Design Requirements

UX-DR1: Dựng token màu của DESIGN.md: nền đêm, thẻ, lớp lõm, chữ, chữ dẫn, chữ meta, chữ mờ, chanh, chanh hover, chữ trên chanh, lạnh, offer B, hổ phách, nền cảnh báo, chữ cảnh báo, viền cảnh báo, nền toast và chữ toast. Năm chỗ của v1 không dùng đỏ như huy hiệu tin đáng tin hay rủi ro cao.

UX-DR2: Nền là canvas đêm. Lưới 40px phủ bằng màu lạnh ở độ đục rất thấp, đúng lớp lưới của prototype.

UX-DR3: Logo là hình vuông 34px, ba chấm của prototype, chữ «HẢI ĐỒ·IT». Bấm logo về Bản đồ nhu cầu.

UX-DR4: Thanh bốn mục (So sánh offer thành mục thứ năm ở v1.1), mỗi mục cao ít nhất 44px. Mục đang mở có gạch chân 2px màu lạnh. Dưới 720px các mục xuống dòng và vẫn cao ít nhất 44px.

UX-DR5: Viên hồ sơ phiên cao khoảng 44px, chỉ hiện khi đã có thành phố, cấp và vai trò. Chữ là ba mục đó. Không có tên người và không có avatar. Bấm thì tới chỗ sửa hồ sơ trên Học gì tiếp?.

UX-DR6: Lớp chào chỉ trên Bản đồ nhu cầu, một lần mỗi máy, không gọi tên người. Ba dòng nói xem một thành phố, thử một kỹ năng, rồi tạo lộ trình. Khi lớp mở, focus đứng trên nút «Đã hiểu». «Đã hiểu» đóng và ghi nhớ trên máy đó.

UX-DR7: Chip vai trò là viên thuốc, cao ít nhất 44px, có aria-pressed. Đang bật thì nền chữ đậm và chữ trên nền đó. Danh vai trò là Tất cả, Backend, Frontend, Data/AI, DevOps/Cloud, Mobile, Bảo mật.

UX-DR8: Tầm nhìn có bốn nút «NAY», «+6T», «+12T», «+18T», mỗi nút cao ít nhất 44px và có aria-pressed. «NAY» hiện số tin đang mở. Trước khi có công thức dự báo đã đo, ba mốc còn lại không vẽ khoảng. Chọn mốc khác «NAY» thì tab thẻ thành phố chuyển sang «Dự báo».

UX-DR9: Bản đồ là khối 3D của prototype, không thay bằng biểu đồ cột phẳng. Mở vào thế 3D. Kéo ngang xoay, kéo dọc nghiêng. Bấm cột, nhãn, hoặc hàng xếp hạng thì cùng chọn một thành phố. Nhãn nổi ghi tên thành phố và số tin đang mở. Đủ ba cột kể cả khi một thành phố không có tin.

UX-DR10: Cụm nút thế bản đồ là 3D, 2D, xoay trái, xoay phải, đặt lại. Mỗi nút cao ít nhất 44px. 2D là thế phẳng trong cùng khối. Giảm chuyển động tắt animation và transition, không gỡ các nút và không gỡ thao tác kéo. Dưới 720px khối 3D đứng trước thẻ thành phố.

UX-DR11: Thẻ thành phố có ba tab «Cơ cấu», «Lương», «Dự báo» trong một tablist. Mỗi tab cao ít nhất 44px và có aria-selected. Cơ cấu là tỷ lệ cộng đủ 100% rồi đến danh kỹ năng thành phố. Tab lương đủ mẫu hiện một số màu chanh. Tab lương thiếu mẫu hiện hộp lương ẩn nét đứt. Tab dự báo, khi chưa có tín hiệu, hiện câu chưa ghi nhận.

UX-DR12: Ô lương đầu trang cùng số và cùng màu chanh với tab lương của thành phố đang chọn. Chưa chọn thành phố thì không hiện số. Đã chọn thành phố mà dưới 30 tin thì hiện câu chưa đủ mẫu.

UX-DR13: Danh kỹ năng thành phố nằm trong tab Cơ cấu. Mỗi dòng là một kỹ năng đang được nhắc trong tin của thành phố đó. Kỹ năng thuộc hồ sơ phiên có dấu tick màu chanh và chữ «đã có». Kỹ năng ngoài hồ sơ không có dấu.

UX-DR14: Bảng xếp hạng dưới bản đồ có cột hạng, tên thành phố, và số tin đang mở. Không có cột mức tăng theo năm và không có cột lương. Hàng đang chọn có gạch chân 2px màu lạnh. Bấm một hàng thì chọn đúng thành phố đó.

UX-DR15: Khối xu hướng tám quý nằm trên Bản đồ nhu cầu, dưới bảng xếp hạng. Có chú giải chữ «tăng», «giảm», «đi ngang». Cột tăng màu chanh, cột giảm màu hổ phách, cột đi ngang màu lạnh. Khi lớp chưa có số, khối hiện «Chưa đủ mẫu.» Không có dải ticker chạy ngang.

UX-DR16: Nút chính cao 48px. Trên bản đồ, chữ là «Thử một kỹ năng cho thành phố này» và mở Học gì tiếp?, mang theo thành phố đang chọn nếu đã chọn. Trên Học gì tiếp? và Lộ trình, chữ là «Tạo lộ trình 90 ngày». Trên Soi tin, chữ là «Soi tin». Khi thiếu thành phố, cấp hoặc vai trò mục tiêu, nút tạo dùng aria-disabled, vẫn nằm trong thứ tự Tab, và aria-describedby trỏ tới câu đang hỏi ba mục đó.

UX-DR17: Nút phụ cao 44px. «Thử lại» gọi lại nguồn. «Bỏ lọc» chọn lại Tất cả. «Đặt lại» xóa kỹ năng giả định và đưa các số về trạng thái trước.

UX-DR18: Chip kỹ năng cao ít nhất 44px và có aria-pressed. Kỹ năng đã có có dấu tick. Kỹ năng giả định đang bật dùng nền chanh. Kỹ năng đang giảm có tem chữ cảnh báo. Người dùng không gõ một kỹ năng tự do. Kỹ năng đã có hoặc đang giả định không còn trong danh nên học tiếp.

UX-DR19: Mỗi dòng danh nên học tiếp có tên kỹ năng, số tin tăng, số tuần, số tin trên mỗi tuần, và nút «Thêm». Bấm «Thêm» thì kỹ năng vào nhóm giả định và các số đổi ngay.

UX-DR20: Ba thẻ chặng nhãn «Ngày 1–30», «Ngày 31–60», «Ngày 61–90». Mỗi thẻ có kỹ năng của chặng, tên một dự án thực hành, và một câu người học làm ra cái gì. Ô email chỉ đứng dưới ba thẻ sau khi lộ trình đã hiện.

UX-DR21: Mỗi nhận định có một nút «Vì sao?» cao ít nhất 44px, kể cả nhận định bị loại. Ngăn là dialog, rộng bằng phần nhỏ hơn giữa bề rộng màn hình và 560px. Khi mở, focus vào nút đóng. Tab không đi ra trang phía sau. Escape hoặc bấm lớp mờ thì đóng và trả focus về nút đã mở. Giảm chuyển động thì ngăn hiện ngay, không trượt. Không có nút «Báo nguồn sai hoặc đã cũ».

UX-DR22: Ô email có nhãn nhìn thấy gắn với input và autocomplete là email. Ô nhận lại liên kết dùng cùng kiểu viền. Email chưa từng lưu thì câu «Chưa có lộ trình cho email này.» Gửi được thì câu «Đã lưu. Liên kết mở lại đã gửi.» Gửi thất bại thì «Chưa lưu được. Lộ trình vẫn còn trên máy này.» và aria-invalid.

UX-DR23: Hai panel offer. Offer A viền trên màu lạnh. Offer B viền trên màu offer B. Thanh thực nhận có ba khúc cộng đủ chiều ngang: thực nhận màu chanh, bảo hiểm màu lạnh, thuế màu hổ phách. Hộp hụt dùng nền cảnh báo, chữ cảnh báo, nét đứt, không dùng đỏ. Mục «Tham số tính (kỳ tính thuế 2026)» hiện đúng bộ số phụ lục.

UX-DR24: Thẻ kết quả soi tin liệt kê số lần làm mới, ngày thấy đầu, ngày thấy gần nhất. Tin trùng và lương bất thường chỉ dùng hộp cảnh báo khi đã có kết luận. Không có vòng điểm trên 100. Chưa dán link thì chỉ có ô link và nút «Soi tin», không có danh tin mẫu.

UX-DR25: Đang tải là thanh xương trên nền thẻ, không hiện số mẫu. Lỗi và rỗng là một câu đã chốt, kèm nút phụ khi có lối thử lại hoặc bỏ lọc. Lỗi nguồn của Học gì tiếp? và Soi tin nằm trong role alert. Toast dùng role status, có nút đóng cao ít nhất 44px, và hẹn giờ không phải cách duy nhất để câu biến mất.

UX-DR26: Các nút chịu bấm cao ít nhất 44px. Chip và mốc tầm nhìn có aria-pressed. Tab có aria-selected. Chữ bắt buộc đọc dùng màu chữ hoặc màu dẫn, không dùng màu mờ một mình. Mục tiêu WCAG 2.2 AA vẫn là giả định trong EXPERIENCE, chưa được Duy duyệt thành chuẩn bắt buộc.

UX-DR27: Từ 720px trở lên, header một hàng. Bản đồ, Học gì tiếp? và Lộ trình chia hai cột. Hai offer nằm cạnh nhau khi còn đủ chỗ. Dưới 720px, bản đồ 3D đứng trước thẻ thành phố và các nút thế bản đồ còn. Việc xếp một cột cho phần còn lại vẫn là giả định trong EXPERIENCE.

UX-DR28: Các câu đã chốt phải hiện đúng chữ: «Chưa đủ mẫu.», «Không tải được dữ liệu thị trường.», «Không có tin nào khớp bộ lọc.», «Chưa lưu được. Lộ trình vẫn còn trên máy này.», «Chưa có lộ trình cho email này.», «Chưa soi được tin này.», «Đã lưu. Liên kết mở lại đã gửi.», «Chưa ghi nhận tín hiệu đáng kể cho thành phố này.», «Chưa ghi nhận dự báo cho mốc này.», «Kết quả là ước tính, không thay thế tư vấn thuế.», «Hai offer gần ngang nhau.»

UX-DR29: Câu do agent viết ghi tên đúng một agent: Bản đồ, Học gì tiếp, Lộ trình, hoặc Soi tin. So sánh offer không ghi tên agent. Màn không hiện kế hoạch và không hiện lời gọi tool. Không có nút «Chạy đa agent».

### FR Coverage Map

FR1: Epic 1 — Xem nhu cầu ba thành phố
FR2: Epic 1 — Mốc 6, 12, 18 tháng chưa có số
FR3: Epic 1 — Thẻ thành phố, lương hoặc câu chưa đủ mẫu, tín hiệu sớm
FR4: Epic 1 — Dấu kỹ năng đã có trên thẻ thành phố
FR5: Epic 2 — Thử kỹ năng giả định, số việc và lương trước sau
FR6: Epic 2 — Xếp hạng kỹ năng nên học tiếp
FR7: Epic 2 — Nới toàn quốc rồi nhóm vai gần
FR8: Epic 2 — Số trước theo hồ sơ phiên
FR9: Epic 3 — Ba chặng lộ trình 90 ngày
FR10: Epic 3 — Vì sao? trên mọi nhận định
FR11: Epic 3 — Không có liên kết khóa trong hai tháng này
FR12: Epic 3 — Lưu lộ trình bằng email
FR13: Epic 3 — Mở lại đúng lộ trình trên máy khác
FR14: Epic 1 — Lớp xu hướng dùng chung
FR15: [Deferred v1.1] So sánh thực nhận hai offer
FR16: [Deferred v1.1] Khoản hụt bảo hiểm
FR17: Epic 4 — Soi một link đang có trong dữ liệu
FR18: Epic 4 — Link không có trong dữ liệu

## Epic List

### Epic 1: Xem nhu cầu ba thành phố
Người mở web, lọc vai trò, chọn thành phố, và thấy số tin, lương hoặc câu chưa đủ mẫu, tín hiệu sớm hoặc câu chưa ghi nhận, và các mốc 6, 12, 18 tháng chưa có số.
**FRs covered:** FR1, FR2, FR3, FR4, FR14

### Epic 2: Thử một kỹ năng trước khi học
Người chọn thành phố, cấp và vai trò, thêm hoặc bớt kỹ năng giả định, và thấy số việc cùng lương đổi trước khi học.
**FRs covered:** FR5, FR6, FR7, FR8

### Epic 3: Nhận lộ trình 90 ngày và mở lại
Người nhận ba chặng có Vì sao?, lưu bằng email, và mở đúng lộ trình đó trên máy khác.
**FRs covered:** FR9, FR10, FR11, FR12, FR13

### Epic 4: Soi một link tuyển dụng (nguyên là Epic 5)
Người dán một link và thấy số lần làm mới, hai ngày, tin trùng nếu có, và kết luận lương. Đóng vai trò phễu đầu vào dẫn sang Học gì tiếp? và Lộ trình.
**FRs covered:** FR17, FR18

*(Ghi chú: Tính năng So sánh hai offer - FR15, FR16 đã được hoãn sang v1.1 theo quyết định của Duy để dồn lực hoàn thiện 4 agent cốt lõi trong 2 tháng).*

---

## Epic 1: Xem nhu cầu ba thành phố

Người mở web, lọc vai trò, chọn thành phố, và thấy số tin, lương hoặc câu chưa đủ mẫu, tín hiệu sớm hoặc câu chưa ghi nhận, và các mốc 6, 12, 18 tháng chưa có số. Epic này gánh toàn bộ nền tảng cào, lưu trữ, hàng đợi, đồ thị và khung LangGraph dùng chung.

### Story 1.1: Khởi tạo schema dữ liệu hạt giống và Fixture kiểm thử

As a developer & tester,
I want to initialize the Postgres tables, Neo4j skill graph, and a 20-job fixture set,
So that the team can build and test downstream features immediately without waiting for the web scraper.

**Acceptance Criteria:**

**Given** a clean development database,
**When** the seed command runs,
**Then** table `skill` is seeded with normalized skill names from `scraper/taxonomy.json`, containing columns `name`, `weeks`, `role`, and 6 flags `required_*` (AD-10).
**And** Neo4j Community initializes nodes `Skill`, `Role` and relationships `(:Skill)-[:HAS_ROLE]->(:Role)` and `(:Skill)-[:REQUIRED_FOR]->(:Role)` (AD-19, AD-22).
**And** 20 realistic job postings from ITviec/TopDev are loaded into `job_posting` for reproducible testing (Murat fixture requirement).

### Story 1.2: Pipeline cào tin, lưu Silo Bronze và Lệnh nạp đồng bộ

As a system,
I want to scrape job postings, archive raw JSON-LD to Silo bronze, and ingest clean records into Postgres and Neo4j,
So that market data is refreshed daily without leaking employer PII or job descriptions to public queries.

**Acceptance Criteria:**

**Given** the scraper runs across HTML and ATS JSON channels,
**When** scraping completes successfully for all channels,
**Then** it overwrites object `open-jobs/open-jobs.jsonl` and archives per-job JSON-LD in Silo prefix `bronze/` keyed by `source_id` (AD-5, AD-21).
**And** skills are extracted purely via in-memory taxonomy scanning without external LLM calls.
**And** a completion message containing the file SHA-256 is pushed to Redis list `ingest` (AD-20).
**And** rows whose city is not Hà Nội, TP. Hồ Chí Minh or Đà Nẵng are dropped; USD salary is kept as-is in `salary_min_usd`/`salary_max_usd`, never converted by the scraper (AD-5).
**And** the loader reads the file, calculates lowercase hex `source_id = SHA256(source + 0x1F + url)`, updates `job_posting` (increments `seen_count`, marks missing as `is_open=false`), syncs Neo4j, and writes `ingest_run.succeeded_at` atomically (AD-4, AD-19).

### Story 1.3: Động cơ tính toán số gộp và API Bản đồ thị trường

As a web client,
I want to fetch aggregated market demand, median salaries, and status signals for three cities,
So that users see accurate job counts and compliant salary figures without browser-side database connections.

**Acceptance Criteria:**

**Given** a request to the market overview API,
**When** filtering by role (All or one of the six roles) and city,
**Then** the response returns all three cities — Hà Nội, TP. Hồ Chí Minh, Đà Nẵng — (even with zero jobs) with their active job counts (AD-14).
**And** the salary set of a cell is every salaried posting with `last_seen` within 180 days of the latest successful ingest, open or closed; USD-only salaries are converted with the configured fixed `USD_VND_RATE` (AD-6).
**And** median salary is calculated for cells whose salary set has >= 30 postings; otherwise salary is hidden with the sentence «Chưa đủ mẫu.» (AD-6).
**And** when a shown median uses any USD posting, the response carries the rate and its effective date for display (AD-6).
**And** horizon marks +6M, +12M, +18M return «Chưa ghi nhận dự báo cho mốc này.» (AD-12).
**And** trend layer returns «Chưa đủ mẫu.» (AD-16).
**And** responses are cached in Redis and invalidated on new `ingest_run` (AD-20).

### Story 1.4: Khung LangGraph dùng chung và Agent Bản đồ

As an application user,
I want the Map Agent to synthesize city demand and skill relationships with cited facts,
So that I understand market signals without hallucinated numbers or leaked tool calls.

**Acceptance Criteria:**

**Given** LangGraph 1.2.16 with Ollama Qwen3 8B,
**When** the user inspects a city on the map,
**Then** Agent Bản đồ is triggered with exactly two tools: `market_snapshot` and `graph_retrieve` (AD-18, AD-22).
**And** the agent execution terminates within 6 model steps or after 2 consecutive rejected responses.
**And** FastAPI validates all job numbers, salaries, and sample sizes against tool outputs; invalid statements are rejected or fall back to standard template sentences.
**And** the output contains the narrative and a "Vì sao?" explanation in a single JSON payload.

### Story 1.5: Giao diện Bản đồ nhu cầu 3D và Thẻ thành phố

As a user visiting Hải Đồ IT,
I want an interactive 3D map with city breakdown cards and role filters,
So that I can explore tech job opportunities across Vietnam on mobile and desktop.

**Acceptance Criteria:**

**Given** the Next.js frontend loaded on browser,
**When** viewing the home page,
**Then** the night theme canvas renders a 3D bar map of three cities with controls (3D, 2D, rotate, tilt, reset) (UX-DR9, UX-DR10).
**And** header contains 4 navigation items (Bản đồ, Học gì tiếp?, Lộ trình, Soi tin) with >= 44px touch targets (UX-DR4).
**And** selecting a city updates the city card with 3 tabs: Cơ cấu (100% breakdown + skill list with owned ticks), Lương (lime text or dashed hidden box), and Dự báo (UX-DR11, UX-DR12, UX-DR13).
**And** primary action button «Thử một kỹ năng cho thành phố này» navigates smoothly to Học gì tiếp?.

---

## Epic 2: Thử một kỹ năng trước khi học

Người chọn thành phố, cấp và vai trò, thêm hoặc bớt kỹ năng giả định, và thấy số việc cùng lương đổi trước khi học.

### Story 2.1: Động cơ tính tin đủ điều kiện và Thuật toán xếp hạng kỹ năng nên học

As an aspiring IT professional exploring career growth,
I want to see how each additional skill increases eligible job postings per study week,
So that I can prioritize learning high-leverage skills first.

**Acceptance Criteria:**

**Given** target city, role, and level in the session profile,
**When** no hypothetical skills are selected,
**Then** eligible jobs count matches owned skills only and extra job delta is 0 (FR5, FR8, AD-15).
**And** a posting is eligible for a skill set S when it is open, in scope, matches target role and level, has at least one skill, and `|posting.skills ∩ S| / |posting.skills| >= MATCH_MIN` (default 0.5, read from backend config) (AD-15).
**And** "before" uses S = owned skills; "after" uses S = owned ∪ selected hypothetical skills; therefore after >= before for every input (property test over random skill sets).
**And** regression: owned {Python, SQL} + hypothetical {Docker} must never yield after < before (the old strict-AND rule gave 14 → 0).
**And** postings with an empty `skills` array are never eligible.
**And** unselected skills are ranked by `extra_jobs / study_weeks` descending (FR6).
**And** skills already owned or currently hypothetical are excluded from the ranking list.
**And** skills flagged as declining in the trend layer are disqualified from rank #1 (AD-16).
**And** role coverage percentage is computed as `owned_required_skills / total_required_skills_for_role` based on the 6 flags in table `skill` (AD-10).

### Story 2.2: Thuật toán nới phạm vi mẫu lương khi dưới 30 tin

As a system,
I want to widen the salary sample scope in strict order when local data is thin,
So that users never see misleading salary numbers computed from fewer than 30 jobs.

**Acceptance Criteria:**

**Given** a role × city × level cell whose 180-day salary set (VND plus USD converted at the fixed rate) has fewer than 30 postings,
**When** calculating median salary for Before and After sets,
**Then** scope widens first to nationwide (the three cities combined) for the same role and level (AD-15).
**And** if still under 30 jobs, scope widens to neighbor role groups (Data/AI isolated, Backend + Frontend, DevOps/Cloud + Security, Mobile isolated).
**And** if >= 30 salaried jobs are reached in a widened scope, its median is returned along with the widening stage tag for the "Vì sao?" explanation.
**And** if still under 30 jobs after all widening steps, salary is hidden with status «Chưa đủ mẫu.» (AD-6).

### Story 2.3: Agent Học gì tiếp và Tool `skill_delta`

As an application user,
I want the Learning Recommendation Agent to explain the impact of my hypothetical skill choices,
So that I understand both the numerical gains and the architectural context behind them.

**Acceptance Criteria:**

**Given** LangGraph registered with Agent Học gì tiếp,
**When** the user modifies hypothetical skills,
**Then** the agent is invoked with exactly two tools: `skill_delta` and `graph_retrieve` (AD-18, AD-22).
**And** tool `skill_delta` supplies before/after counts, study weeks, rank, and salary status.
**And** tool `graph_retrieve` fetches related skill nodes and roles up to 2 edges deep.
**And** FastAPI validates all job counts, salary numbers, and study weeks against tool output; invalid responses are rejected or fall back to standard templates.
**And** the output provides the headline and the "Vì sao?" reason in a single unified JSON payload.

### Story 2.4: Giao diện Học gì tiếp? và Quản lý hồ sơ phiên

As a user on the Học gì tiếp? page,
I want an interactive interface with skill chips, ranking table, and Before/After cards,
So that I can experiment with skill paths and proceed to 90-day roadmap generation.

**Acceptance Criteria:**

**Given** the Học gì tiếp? Next.js view,
**When** city, role, and level are selected,
**Then** the 44px session profile pill appears in the header and syncs with `sessionStorage` (UX-DR5).
**And** owned skill chips display green checkmarks; hypothetical skill chips use lime background; declining skills show amber warning tags (UX-DR18).
**And** clicking «Thêm» on a ranked skill adds it to hypothetical selections and refreshes the Before/After card instantly (UX-DR19).
**And** clicking «Đặt lại» clears all hypothetical skills (UX-DR17).
**And** primary button «Tạo lộ trình 90 ngày» is enabled only when city, level, and role are complete, linking to the 90-day roadmap view (UX-DR16).

---

## Epic 3: Nhận lộ trình 90 ngày và mở lại

Người nhận ba chặng có Vì sao?, lưu bằng email, và mở đúng lộ trình đó trên máy khác.

### Story 3.1: Tool `roadmap_frame` và Thuật toán phân bổ kỹ năng 3 chặng

As an application user,
I want my 90-day roadmap structured into three distinct 30-day stages focusing on top-ranked skills,
So that I have a clear, realistic progression without skill overload.

**Acceptance Criteria:**

**Given** hypothetical skills selected in Học gì tiếp?,
**When** tool `roadmap_frame` constructs the roadmap framework,
**Then** it takes at most the top 3 hypothetical skills ranked by AD-15, assigning exactly one primary skill per stage: Days 1–30, 31–60, 61–90 (AD-7).
**And** if fewer than 3 hypothetical skills were selected, subsequent stages deepen owned skills with the highest open-job demand in scope (ties broken by `taxonomy.json` order).
**And** the tool returns the 3 stages with their target skills, associated open job counts, and citation references.

### Story 3.2: Agent Lộ trình và Cơ chế sinh dự án thực hành có Vì sao?

As an aspiring engineer,
I want concrete practical project deliverables and evidence-based explanations for each roadmap stage,
So that I understand what real-world capability I will build and why it matters to employers.

**Acceptance Criteria:**

**Given** Agent Lộ trình registered in LangGraph with tools `roadmap_frame`, `read_saved_roadmap`, and `graph_retrieve`,
**When** generating roadmap content,
**Then** it calls `roadmap_frame` first and Ollama (Qwen3 8B) writes only the project name and exactly one deliverable sentence per stage (AD-7, AD-18).
**And** it contains no external course URLs, affiliate tags, or hallucinated salary figures (FR9, FR11).
**And** 100% of statements carry a "Vì sao?" reason citing extracted skill sets, raw job links, or one of four reports: ITviec, TopDev, TopCV, JobOKO (FR10).
**And** FastAPI validation enforces termination within 6 model steps or 2 consecutive rejections, falling back to standard templates on failure.

### Story 3.3: Dịch vụ gửi thư và Lưu trữ lộ trình với Token giao dịch

As a user saving my roadmap,
I want an email with an unguessable reopen link,
So that I can access my roadmap later from any device without creating a username and password.

**Acceptance Criteria:**

**Given** a generated 90-day roadmap,
**When** the user submits their email,
**Then** the server initiates a database transaction to insert a row with `token_hash`, email, profile fields, and 3-stage JSON into `saved_roadmap` (AD-8).
**And** the web server sends an email containing the reopen token link via group SMTP (AD-11).
**And** the database transaction commits only after the SMTP server accepts the message; if mail delivery fails, the transaction is rolled back completely leaving no database row (FR12).
**And** saving again with the same email issues a new token, invalidates the previous link, and resets the 14-day tracking window.

### Story 3.4: Endpoint mở lại lộ trình bằng Token và Theo dõi mốc 14 ngày

As a returning user opening my roadmap link,
I want to view my saved roadmap on another device without exposing my email address,
So that my privacy is protected while my return visit counts toward product success metrics.

**Acceptance Criteria:**

**Given** a request to `GET /roadmap/reopen/{token}`,
**When** the token SHA-256 matches an active `token_hash`,
**Then** the response returns city, level, target role, owned skills, and the 3 stages, strictly omitting the user email (FR13, NFR6).
**And** the server records the access timestamp; if opened within 14 days of creation, it increments the 14-day retention metric (NFR7).
**And** links accessed after day 14 continue to display the roadmap fully but do not count toward the 14-day retention metric.

### Story 3.5: Giao diện Lộ trình 90 ngày, Dialog Vì sao? và Luồng lưu/mở lại

As a user on the Lộ trình 90 ngày page,
I want an accessible interface displaying three progression cards, justification dialogs, and email save forms,
So that I can inspect my learning plan and seamlessly resume my session on mobile or desktop.

**Acceptance Criteria:**

**Given** the Next.js roadmap view,
**When** rendered,
**Then** three stage cards (Ngày 1–30, Ngày 31–60, Ngày 61–90) display skills, project names, and deliverable sentences (UX-DR20).
**And** clicking «Vì sao?» opens an accessible modal dialog (max 560px, Escape closes, focus trap) (UX-DR21).
**And** the email input appears below the cards with visible label and status announcements: «Đã lưu. Liên kết mở lại đã gửi.» on success or «Chưa lưu được. Lộ trình vẫn còn trên máy này.» on failure (UX-DR22).
**And** opening via a token link automatically populates the session profile in `sessionStorage`, making the header profile pill active across the application.


---

## Epic 4: Soi một link tuyển dụng

Người dán một link và thấy số lần làm mới, hai ngày, tin trùng nếu có, và kết luận lương. Đóng vai trò phễu đầu vào dẫn sang Học gì tiếp? và Lộ trình.

### Story 4.1: Động cơ đối chiếu tin tuyển dụng và Tool `lookup_posting`

As an application user,
I want to look up a job posting URL and see refresh count, dates, duplicate status, and salary evaluation,
So that I can verify the posting's credibility without relying on arbitrary hype scores.

**Acceptance Criteria:**

**Given** a URL input by the user,
**When** looked up by trimmed `source_url` in table `job_posting`,
**Then** if absent, returns `is_found = false`, `source_id = null`, and `skills = []` (FR17, FR18, AD-4).
**And** if present, returns `seen_count`, `first_seen`, `last_seen`, and detected duplicate postings sharing the same skills, city, level, and salary range.
**And** flags salary as an outlier only if the posting's role × city × level cell has >= 30 VND-salaried jobs and the median falls outside the posting's range; under 30 jobs, reports insufficient sample size (AD-6).
**And** returns `source_id` and normalized `skills` array as keys/seeds for downstream tools (AD-18).

### Story 4.2: Tool `read_bronze` an toàn và Agent Soi tin

As a job seeker inspecting a posting,
I want an agent-synthesized technical breakdown with cited facts and no employer PII,
So that I understand core technical expectations while privacy and copyright constraints are upheld.

**Acceptance Criteria:**

**Given** LangGraph registered with Agent Soi tin and tools `lookup_posting`, `graph_retrieve`, and `read_bronze`,
**When** inspecting a found posting,
**Then** tool `read_bronze` fetches the raw JSON-LD from Silo prefix `bronze/` and sanitizes it, stripping employer names, titles, contacts, emails, and phone numbers (AD-4, AD-21).
**And** tool `graph_retrieve` queries Neo4j for related skills using the posting's skills as seeds up to 2 edges deep (AD-22).
**And** Ollama (Qwen3 8B) synthesizes technical observations and a "Vì sao?" reason without verbatim description text or company names.
**And** FastAPI validation rejects hallucinated numbers or leaked PII, terminating within 6 model steps or 2 consecutive rejections.

### Story 4.3: Giao diện Soi tin tuyển dụng và Cầu nối phễu sang Học gì tiếp?

As a visitor exploring a job opportunity,
I want an intuitive inspect interface that warns of stale/duplicate jobs and provides a direct bridge to skill gap analysis,
So that I can immediately check missing skills on Học gì tiếp? and build a 90-day learning roadmap.

**Acceptance Criteria:**

**Given** the Soi tin Next.js interface,
**When** rendered,
**Then** it provides a single URL input field and primary button «Soi tin» (height >= 44px) without raw description input or sample job catalogs (UX-DR16, UX-DR24).
**And** the result card displays seen count, first/last seen dates, and amber warning boxes for duplicates or salary outliers without 100-point trust badges.
**And** if not found, displays «Chưa soi được tin này.» with role alert (UX-DR25, UX-DR28).
**And** for found postings, renders extracted skill tags and an action button «Đối chiếu kỹ năng trên Học gì tiếp?» which populates the posting's city, role, and skills into `sessionStorage` and navigates smoothly to Học gì tiếp?.
