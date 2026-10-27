---
title: Hải Đồ IT
status: final
created: 2026-10-22
updated: 2026-10-27
---

> **Cập nhật 2026-10-27.** Sửa theo đo dữ liệu và quyết định của Duy, chi tiết ở `../../sprint-change-proposal-2026-10-27.md`: (1) tin đủ điều kiện tính bằng mức khớp ≥ 50%, thay luật «có đủ mọi kỹ năng» đang làm số sau giảm; (2) ba thành phố thay bảy; (3) lương dùng cửa sổ 180 ngày và đổi USD theo tỷ giá cố định; (4) bốn agent là yêu cầu bắt buộc; (5) bản JSON-LD gốc được lưu trên Silo, không hiện và không trả qua API; (6) So sánh offer hoãn sang v1.1; (7) dự báo không có số trước khi có công thức đã đo.

# PRD: Hải Đồ IT

## 0. Mục đích tài liệu

PRD này dành cho Duy và hai người cùng làm, rồi cho các bước UX, kiến trúc và epic. Từ vựng nằm ở mục 4. Yêu cầu chức năng đánh số FR-1 trở đi, gắn với hành trình UJ. Chỗ suy ra khi viết bản này mang nhãn `[GIẢ ĐỊNH: ...]`, gom lại ở mục 14.

PRD đứng trên brief đã khép ngày 2026-10-22, phụ lục của brief, nghiên cứu thị trường cùng ngày, và prototype `prototype/Hải Đồ IT — Bản đồ tuyển dụng & Cố vấn đa agent.html`. Hành vi người dùng của phần v1 lấy từ prototype. Tên sản phẩm và những màn nằm ngoài v1 lấy từ brief. Công thức mẫu trong prototype không phải yêu cầu. Phần kỹ thuật, phương án đã loại, và tham số thuế nằm ở `addendum.md`.

## 1. Tầm nhìn

Hải Đồ IT là web cho junior, fresher và người đang chuyển hướng trong ngành IT. Họ mở Bản đồ nhu cầu để thấy việc đang tuyển ở thành phố của mình, vào Học gì tiếp? để thử thêm một kỹ năng và thấy số tin cùng lương công khai đổi ra sao, rồi nhận Lộ trình 90 ngày. Mỗi nhận định trên lộ trình có nút Vì sao? trỏ về nguồn.

Người dùng quyết định học gì trước khi bỏ tiền và thời gian. Câu chữ trên Bản đồ nhu cầu, Học gì tiếp?, Lộ trình 90 ngày và Soi tin do bốn agent viết từ kết quả tool. Bốn agent là yêu cầu bắt buộc của v1. Trên web của hai tháng này không có khoản thu. Việc còn hình dạng tiền là một trường hoặc bootcamp nói đồng ý thử. Đó là một lời nói, không phải một màn. Ứng viên không trả tiền.

Sản phẩm có hai tháng để ra mắt, ba người, chỉ web. Đi tiếp sau hai tháng khi đủ bốn mức ở mục 13.

## 2. Vì sao lúc này

Thị trường IT Việt Nam đang phân cực. Tỷ lệ doanh nghiệp coi năng suất AI là lý do chính để không tuyển thêm tăng từ 5,9% (2024) lên 20,2% (2025), và được dự báo 34,3% năm 2026. Tuyển người dưới một năm kinh nghiệm giảm 13%. Trên ITviec, tin AI/ML tăng 41% và lượt tìm "AI" tăng 89%. ITviec (n=2.324) ghi 40,9% người làm IT định nghỉ trong 12 tháng tới, 26,3% trong số đó muốn đổi hướng. JobsGO ghi 54,5% đang chủ động tìm việc. JobOKO ghi người dưới một năm kinh nghiệm chiếm 45% số ca bị cắt giảm.

Ý định rời việc và sức ép lên junior đã có nguồn. Câu "họ thiếu một lộ trình" trong khảo sát JobsGO gộp với môi trường làm việc và chưa được xác minh riêng. Duy đã duyệt ngày 2026-10-23: nhu cầu một lộ trình có trích nguồn đủ để làm v1, dù câu khảo sát đó chưa tách riêng "thiếu lộ trình". Nếu người dùng không thấy dữ liệu thật hơn lời khuyên chung, phần Học gì tiếp? và Lộ trình 90 ngày mất lý do tồn tại.

Khoảng trống cần giữ khi viết: một người ở Việt Nam thử thêm một kỹ năng, thấy số tin và lương công khai đổi theo thành phố và cấp bậc, rồi nhận lộ trình khoảng 90 ngày có Vì sao? trỏ về nguồn. HireJack đã cho thử kỹ năng và đếm việc mới trên dữ liệu toàn cầu, đồng thời có ghép hồ sơ với tin. ITviec có biến động tin và bảng lương khảo sát, đồng thời có ghép việc và đánh giá nhà tuyển dụng. Máy tính lương và bảo hiểm đã có ở các trang tuyển dụng. Phần còn lại của Hải Đồ IT là trải nghiệm đó, và nó dễ bị làm theo. Các số ITviec về tin AI/ML và lượt tìm "AI" là quý 1/2025. Đọc lại trước khi đưa chúng lên sản phẩm. Hải Đồ IT không có lợi thế kho dữ liệu so với các nền tảng lớn. Cửa sổ tập trung vào junior và người chuyển hướng là ngắn, vì đã có sản phẩm mới vào thị trường trong năm 2026.

## 3. Người dùng

### 3.1 Việc họ cần xong

- Biết kỹ năng nào đang được tuyển ở thành phố mình hôm nay, trước khi chọn hướng học. Dự báo chỉ có số khi đã có công thức đo được.
- Thử một kỹ năng giả định và thấy số tin cùng lương công khai đổi, kể cả khi ô mẫu chưa đủ ngưỡng 30 tin và sản phẩm phải nói thẳng là chưa đủ.
- Có lộ trình 90 ngày với dự án thực hành, và mở lại được lộ trình đó trong 14 ngày.
- Trước khi nộp hồ sơ, biết một tin đang theo dõi có bị làm mới nhiều lần, có tin trùng, hoặc có lương bất thường hay không.
- Khi cầm hai offer, biết bên nào có thực nhận cả năm cao hơn, và bên nào đóng bảo hiểm thấp hơn lương ghi trên offer. Việc này thuộc v1.1.

Với người dùng chính, kết quả đời sống là có việc hoặc lên lương sau 3–6 tháng. Hai tháng ra mắt không đo kết quả đó. Hai tháng đo bốn mức ở mục 13.

### 3.2 Người dùng chính và người dùng phụ

Người dùng chính là junior (khoảng 0–2 năm) và fresher muốn chuyển hướng, nhất là sang Data/AI hoặc DevOps/Cloud. Người dùng phụ là sinh viên năm cuối ngành IT. Cùng một web. Không có cổng riêng.

Trường đại học và bootcamp là bên có thể đồng ý thử trong v1, và là bên trả gói ở v2. Trong v1 họ dùng cùng web với ứng viên để xem chương trình của họ có khớp thị trường hay không. Gói riêng cho trường nằm ngoài v1.

### 3.3 Người không được phục vụ trong v1

- Nhà tuyển dụng cần đăng tin, sàng hồ sơ, hoặc được chấm điểm phản hồi.
- Người cần được ghép với một tin đang mở.
- Người cần đọc hợp đồng hoặc tư vấn pháp lý.
- Người cần lương theo phân vị, phòng tập thương lượng, hoặc review dự án có trả phí. Ba món đó là v2.
- Người tìm một thị trường Remote hoặc Nhật như một sản phẩm riêng.

### 3.4 Hành trình

Lan, Khoa và Mai chỉ là tên mock, để hành trình có người cụ thể. Ba cảnh không phải bằng chứng, và không chứng minh một người thật sẽ quay lại. Không có buổi ngồi với người thật nào trong bản này để kể. Khoa dán một link, xem xong, đóng trang, không lưu. Mai nhập hai offer, xem xong, đóng trang, không lưu. Lan tạo lộ trình, để lại email, rồi mở lại đúng lộ trình trong 14 ngày, vì SM-1 và SM-2 cần một cảnh để đo. Trong bản không có cảnh Lan suýt trả tiền cho một khóa. Không thêm cảnh đó.

**UJ-1. Lan tạo lộ trình 90 ngày lần đầu.**

- **Người và bối cảnh:** Lan, một năm làm PHP ở Đà Nẵng, muốn sang Data/AI. Sợ học nhầm một khóa.
- **Điểm vào:** mở web trên điện thoại, chưa có email nào được lưu.
- **Đường đi:** xem Bản đồ nhu cầu tại Đà Nẵng, đánh dấu Python và SQL là kỹ năng đã có, sang Học gì tiếp?, thêm một kỹ năng giả định, xem số tin và lương công khai (hoặc trạng thái ẩn), chọn một kỹ năng trong danh nên học tiếp, tạo lộ trình ba chặng, nhập email.
- **Điểm giá trị:** lộ trình hiện ra. Một nhận định có Vì sao? trỏ về nguồn. Một nhận định bị loại vì thiếu dữ liệu vẫn có Vì sao? giải thích vì sao bị loại.
- **Kết:** hồ sơ và lộ trình được lưu. Lan nhận liên kết mở lại. Hệ thống tính đây là một người đã tạo xong lộ trình.
- **Khi ô mẫu mỏng:** Data/AI ở Đà Nẵng dưới ngưỡng 30 tin. Học gì tiếp? nới toàn quốc trước, rồi nhóm vai gần nếu vẫn mỏng, và Vì sao? nói đang ở bước nào. Lương công khai của ô mỏng không hiện số.

**UJ-2. Lan mở lại lộ trình trong 14 ngày.**

- **Người và bối cảnh:** cùng Lan, ngày thứ mười, đang ở máy khác.
- **Điểm vào:** mở liên kết mở lại, hoặc nhập lại đúng email để nhận liên kết mới rồi mở lộ trình.
- **Đường đi:** thấy đúng lộ trình đã lưu. Trên Bản đồ nhu cầu, Python và SQL vẫn là kỹ năng đã có.
- **Điểm giá trị:** không phải chọn lại từ đầu.
- **Kết:** lần mở này được tính là mở lại trong 14 ngày, vì cùng email và còn trong cửa sổ tính từ lúc lưu. Cảnh này là chỗ đo SM-2. Nó không chứng minh một người thật sẽ quay lại.
- **Khi tạo lại:** Một email giữ một lộ trình. Tạo lộ trình mới thì thay lộ trình cũ và cửa sổ 14 ngày tính lại từ lần lưu mới.

**UJ-3. Khoa soi tin rồi đóng trang.**

- **Người và bối cảnh:** Khoa, sinh viên năm cuối ở Hà Nội, có một link tin.
- **Điểm vào:** vào thẳng Soi tin. Không có ô email.
- **Đường đi:** dán link. Nếu link đang có trong dữ liệu, thấy số lần làm mới của tin, tin trùng nếu có, và lương bất thường hoặc câu chưa đủ mẫu. Nếu link không có trong dữ liệu, thấy câu chưa soi được.
- **Điểm giá trị:** có câu trả lời về tin đang cầm, hoặc câu chưa soi được.
- **Kết:** không lưu. Đóng trình duyệt thì không còn gì trên máy chủ.
- **Khi dữ liệu không đủ:** Soi tin không xin nguyên văn mô tả công việc.

**UJ-4. Mai so sánh hai offer rồi đóng trang.** *(Hoãn v1.1 cùng So sánh offer.)*

- **Người và bối cảnh:** Mai, fresher ở Đà Nẵng, đang cầm hai offer. Một bên đóng bảo hiểm trên mức thấp hơn lương.
- **Điểm vào:** vào thẳng So sánh offer. Không có ô email.
- **Đường đi:** nhập hai offer, gồm căn cứ đóng bảo hiểm. Thấy bên nào có thực nhận cả năm cao hơn, và thấy khoản hụt nếu căn cứ đóng thấp hơn lương.
- **Điểm giá trị:** câu kết quả gọi tên công ty Mai đã nhập, và ghi đây là ước tính.
- **Kết:** không lưu. Đóng trình duyệt thì không còn gì trên máy chủ.

## 4. Thuật ngữ

Dùng đúng các từ này trong yêu cầu, hành trình và chỉ số.

- **Hồ sơ** — thành phố, cấp bậc, vai trò mục tiêu, và các kỹ năng đã có của một người. Hồ sơ sống trên máy cho đến khi lộ trình được lưu, rồi sống cùng email đó.
- **Hồ sơ phiên** — hồ sơ đang dùng trong lần mở web này. Trước khi lưu, hồ sơ phiên chỉ ở trên máy.
- **Cấp bậc** — Fresher hoặc Junior. Học gì tiếp? chỉ dựng kịch bản cho hai cấp này. Khi chưa chọn cấp, ô lương trên thẻ thành phố dùng Junior.
- **Kỹ năng đã có** — kỹ năng người dùng đánh dấu là mình đã có. Dấu trên Bản đồ nhu cầu chỉ rơi vào kỹ năng đã có.
- **Kỹ năng giả định** — kỹ năng người dùng thêm trong Học gì tiếp? để xem số tin và lương công khai đổi, trước khi học thật.
- **Bản đồ nhu cầu** — mặt tiền. Nhu cầu hôm nay và các mốc dự báo tại ba thành phố: Hà Nội, TP. Hồ Chí Minh, Đà Nẵng.
- **Dự báo 18 tháng** — số tin ở các mốc 6, 12 và 18 tháng, hiện thành một khoảng có nhãn dự báo khi đã có công thức đo được. Trước đó các mốc nói «Chưa ghi nhận dự báo cho mốc này.»
- **Học gì tiếp?** — chỗ thử kỹ năng giả định, xem số tin, lương công khai và thời gian học đổi, rồi xem danh kỹ năng nên học tiếp.
- **Lộ trình 90 ngày** — kế hoạch ba chặng sinh ra từ lựa chọn ở Học gì tiếp?. Mỗi chặng có một dự án thực hành.
- **Nhận định** — một câu trên lộ trình nói nên học gì, nên bỏ gì, hoặc vì sao một hướng bị loại.
- **Vì sao?** — lối từ một nhận định, hoặc từ một tín hiệu sớm, tới nguồn.
- **Nguồn** — một tập tin đã trích (kỹ năng, thành phố, cấp bậc, khoảng lương, ngày đăng, link gốc) hoặc một báo cáo công khai được gọi tên (ITviec, TopDev, TopCV, JobOKO).
- **Ô mẫu** — một nhóm tin dùng để quyết định có hiện lương công khai hay không, cắt theo vai trò, thành phố và cấp bậc. Tin trong ô mẫu là tin có lương đã thấy trong 180 ngày gần nhất, đang mở hay đã đóng. Khi Học gì tiếp? nới phạm vi, ô mẫu là phạm vi đã nới.
- **Mức khớp tin** — với một tin, số kỹ năng của tin nằm trong tập kỹ năng đang xét, chia cho số kỹ năng của tin. Ví dụ tin cần Python, SQL, Docker, AWS; người có Python và SQL khớp 2/4 = 50%.
- **Tin đủ điều kiện** — tin đang mở trong phạm vi đang tính, đúng vai trò mục tiêu và đúng cấp bậc, có ít nhất một kỹ năng, và có mức khớp tin từ 50% trở lên với tập kỹ năng đang xét. Tập trước là kỹ năng đã có. Tập sau là kỹ năng đã có cùng kỹ năng giả định đang chọn. Thêm kỹ năng chỉ làm số tin tăng hoặc giữ nguyên. Ngưỡng 50% là tham số nhóm giữ và đo lại.
- **Độ phủ** — với một vai trò, số kỹ năng yêu cầu của vai đó đang nằm trong kỹ năng đã có, chia cho số kỹ năng yêu cầu của vai đó. Danh kỹ năng yêu cầu đi cùng danh kỹ năng cố định.
- **Nhóm vai gần** — bước nới thứ hai sau toàn quốc. Data/AI đứng riêng. Backend với Frontend. DevOps/Cloud với Bảo mật. Mobile đứng riêng.
- **Ngưỡng 30 tin** — dưới 30 tin trong ô mẫu thì mọi số lương công khai đều ẩn. Ngưỡng này không phải mốc 30 người tạo lộ trình.
- **Lương công khai** — một số lương của ô mẫu khi ô đó đủ ngưỡng 30 tin. Tin chỉ ghi lương USD được đổi sang VND theo một tỷ giá cố định, và màn ghi tỷ giá cùng ngày áp dụng khi số đang hiện có dùng tin USD. v1 không hiện dải phân vị.
- **Tín hiệu sớm** — câu nói một thành phố đang có việc mới vì một sự kiện nào đó, hiện trên thẻ thành phố. Chưa có cách phát hiện. Khi chưa có quy tắc, thẻ hiện «chưa ghi nhận tín hiệu».
- **Toàn quốc** — phạm vi nới của Học gì tiếp? khi ô một thành phố dưới ngưỡng 30 tin, gộp ba thành phố. Toàn quốc không phải thành phố thứ tư trên Bản đồ nhu cầu.
- **So sánh offer** — công cụ nhập hai offer và so thực nhận cả năm. Hoãn sang v1.1.
- **Thực nhận cả năm** — số tiền về tay sau thuế và bảo hiểm, tính cho cả năm, từ dữ liệu người dùng nhập.
- **Kiểm tra BHXH** — phần của So sánh offer. Cảnh báo khi căn cứ đóng thấp hơn lương ghi trên offer.
- **Soi tin** — công cụ bản nhẹ. Người dùng đưa một link. Sản phẩm báo tin treo, tin trùng và lương bất thường khi dữ liệu cho phép.
- **Tin treo** — tin tuyển dụng bị đăng đi đăng lại. Ngưỡng chưa được đo. Tuần 1 đo quy tắc tạm: làm mới từ lần thứ hai, hoặc còn mở sau 30 ngày kể từ ngày thấy đầu. Trước khi đo, không viết test và không gắn nhãn như thể ngưỡng đã đúng.
- **Tin trùng** — tin đang mở khác, khác link, trùng kỹ năng, thành phố, cấp bậc và khoảng lương với tin đang soi.
- **Lương bất thường** — lương công khai của ô mẫu không nằm trong khoảng lương ghi trên tin. Khi ô đó đang ẩn lương, không kết luận lương bất thường.
- **Lần làm mới của tin** — số lần cùng một tin được thấy lại. Khác với ngày làm mới dữ liệu của cả Bản đồ nhu cầu.
- **Liên kết mở lại** — liên kết gửi tới email đã lưu lộ trình. Mở liên kết là vào đúng hồ sơ và lộ trình đó.
- **Hoa hồng giới thiệu khóa học** — khoản một trang khóa học trả khi người dùng bấm từ lộ trình sang khóa của trang đó. Hai tháng này chưa có tên công ty khóa nào, nên khoản bằng không. Không xây link, không gắn nhãn «hoa hồng», không đếm lượt bấm, và không gọi là tiền của kỳ này.
- **Xu hướng và hạn dùng kỹ năng** — lớp dữ liệu dùng chung. Cho biết nhu cầu một kỹ năng đang tăng hay giảm. Không có màn riêng trong v1.

## 5. Tính năng

### 5.1 Bản đồ nhu cầu

**Mô tả:** Đây là mặt tiền, đúng cách dùng của prototype ngày 2026-10-22 cho riêng màn này, trừ số thành phố: ba thành phố, nhu cầu hôm nay, các mốc dự báo, thẻ thành phố với cơ cấu, lương và tín hiệu sớm, dấu kỹ năng đã có. Lần đầu không có hồ sơ mẫu. Bộ lọc vai trò mặc định là Tất cả. Bộ lọc vai trò của v1 là Tất cả, Backend, Frontend, Data/AI, DevOps/Cloud, Mobile, Bảo mật. Hình khối 3D của prototype là cách trình bày cho UX, không phải yêu cầu của PRD này. Thực hiện UJ-1.

**Yêu cầu chức năng:**

#### FR-1: Xem nhu cầu hôm nay tại ba thành phố

Người dùng xem được số tin đang mở tại từng thành phố trong ba thành phố, theo bộ lọc vai trò đang chọn. Thực hiện UJ-1.

**Hệ quả kiểm được:**

- Đủ ba thành phố có mặt kể cả khi một thành phố có ít tin.
- Đổi bộ lọc vai trò thì số tin của thành phố đổi theo vai trò đó.
- Mỗi lần xem có ngày của lần làm mới dữ liệu gần nhất.
- Không có hồ sơ mẫu sẵn. Khi chưa có kỹ năng đã có, không có dấu "đã có".

#### FR-2: Xem dự báo 18 tháng

Người dùng chuyển tầm nhìn sang mốc 6, 12 hoặc 18 tháng và thấy số tin dự báo của thành phố đang xem. Thực hiện UJ-1.

**Hệ quả kiểm được:**

- Trước khi có công thức đã đo, các mốc 6, 12, 18 tháng và chỗ dự báo trên thẻ không có số và không có khoảng. Câu là «Chưa ghi nhận dự báo cho mốc này.» Không dùng hệ số minh họa cố định của prototype.
- Khi có công thức đã đo, mỗi mốc hiện một khoảng có nhãn dự báo, không hiện một số như thể đã xảy ra. Vì sao? của khoảng đó trỏ tới số tin đang dùng để tính. Khi tầm nhìn là hôm nay, chỗ dự báo trên thẻ lấy khoảng mốc 12 tháng.
- Mốc "nay" hiện số tin đang mở, không hiện khoảng dự báo ở vị trí của số hiện tại.
- Dự báo nói về số tin. v1 không dự báo lương.

#### FR-3: Xem một thành phố

Người dùng chọn một thành phố và thấy cơ cấu vai trò, lương công khai hoặc trạng thái ẩn, và tín hiệu sớm hoặc câu chưa ghi nhận tín hiệu. Thực hiện UJ-1.

**Hệ quả kiểm được:**

- Thẻ thành phố có cơ cấu vai trò của thành phố đó.
- Khi đã chọn thành phố, lương trên thẻ và ô lương đầu trang cùng lấy một ô mẫu. Bộ lọc một vai trò thì ô đó là vai trò đang lọc, thành phố đang chọn, và cấp bậc của hồ sơ phiên. Chưa chọn cấp thì dùng Junior. Bộ lọc Tất cả thì vai trò của ô là vai trò có nhiều tin nhất tại thành phố đó.
- Chưa chọn thành phố thì ô lương đầu trang không hiện số.
- Khi ô mẫu đó đủ ngưỡng 30 tin, thẻ và ô đầu trang hiện một lương công khai. Dưới ngưỡng thì không hiện số, và có câu chưa đủ mẫu.
- Cơ cấu vai trò là tỷ lệ số tin của từng vai trò trong thành phố, cộng một nhóm còn lại. Các tỷ lệ cộng đủ 100%.
- Thẻ hiện đúng một tín hiệu sớm kèm Vì sao?, hoặc hiện câu chưa ghi nhận tín hiệu đáng kể cho thành phố này.
- Khi chưa có quy tắc phát hiện, thẻ hiện câu chưa ghi nhận. Việc xây thẻ không chờ quy tắc đó.
- Thành phố vẫn xem được khi lương đang ẩn.

#### FR-4: Thấy kỹ năng đã có trên bản đồ

Khi hồ sơ phiên đang có kỹ năng đã có, kỹ năng đó được đánh dấu trên danh kỹ năng của thành phố. Thực hiện UJ-1 và UJ-2.

**Hệ quả kiểm được:**

- Kỹ năng nằm trong kỹ năng đã có thì có dấu. Kỹ năng không nằm trong đó thì không có dấu.
- Xóa một kỹ năng đã có thì dấu mất trong cùng phiên.
- Sau UJ-2, dấu khớp với hồ sơ đã lưu, không khớp với máy trống.

**Ngoài phạm vi:** không có màn riêng cho xu hướng và hạn dùng kỹ năng. Lối "kỹ năng còn hạn bao lâu" của prototype không thành màn v1.

### 5.2 Học gì tiếp?

**Mô tả:** Người dùng thêm hoặc bớt kỹ năng giả định trên hồ sơ phiên và thấy ba thứ đổi: số tin đủ điều kiện, lương công khai, thời gian học. Danh nên học tiếp xếp theo số tin mở thêm trên mỗi tuần học. Tên trên sản phẩm là Học gì tiếp?. Nhãn "Mô phỏng Nếu–thì" của prototype không dùng. Thực hiện UJ-1.

**Yêu cầu chức năng:**

#### FR-5: Thử kỹ năng giả định

Người dùng thêm hoặc bỏ kỹ năng giả định và thấy số tin trước và sau, thời gian học, và lương công khai trước và sau hoặc trạng thái ẩn. Thực hiện UJ-1.

**Hệ quả kiểm được:**

- Số tin là số tin đủ điều kiện. Thời gian học là tổng số tuần của các kỹ năng giả định đang chọn. Chưa thêm kỹ năng giả định thì không có chênh lệch, và thời gian học là trạng thái chưa có kỹ năng giả định.
- Mỗi dòng trong danh nên học tiếp hiện số tin tăng, số tuần, và số tin trên mỗi tuần.
- Bỏ hết kỹ năng giả định thì các số trở về trạng thái trước.
- Danh kỹ năng để chọn là danh cố định do nhóm giữ, cùng taxonomy mà pipeline đã trích. Người dùng không gõ một kỹ năng tự do ngoài danh.
- Học gì tiếp? chỉ dựng kịch bản cho cấp Fresher và Junior.

#### FR-6: Xếp kỹ năng nên học tiếp

Hệ thống xếp các kỹ năng còn lại trong danh theo số tin mở thêm trên mỗi tuần học, và người dùng thêm được một kỹ năng từ danh đó vào kỹ năng giả định. Thực hiện UJ-1.

**Hệ quả kiểm được:**

- Thứ hạng cao hơn là số tin tăng thêm chia cho số tuần học lớn hơn.
- Số tuần học của mỗi kỹ năng là số do nhóm gán trong danh, không phải số suy ra tự động từ tin tuyển.
- Kỹ năng đã nằm trong kỹ năng đã có hoặc trong kỹ năng giả định thì không còn trong danh nên học tiếp.

#### FR-7: Nói rõ khi ô mẫu dưới ngưỡng 30 tin

Khi ô vai trò × thành phố × cấp bậc dưới ngưỡng 30 tin, Học gì tiếp? nới theo thứ tự: trước hết toàn quốc, cùng vai trò và cùng cấp bậc; nếu ô đó vẫn dưới ngưỡng thì nới sang nhóm vai gần. Không hiện lương công khai lấy từ ô mỏng. Thực hiện UJ-1.

**Hệ quả kiểm được:**

- Vì sao? của kết quả đã nới nói ô gốc dưới ngưỡng 30 tin và nói đang đứng ở bước toàn quốc hay bước nhóm vai gần.
- Không hiện lương công khai của ô dưới ngưỡng 30 tin.
- Nếu phạm vi đã nới vẫn dưới ngưỡng 30 tin, lương công khai tiếp tục ẩn và có câu chưa đủ mẫu.
- Đo ngày 2026-10-27 trên 832 tin: không ô Fresher hoặc Junior nào đủ 30 tin có lương, kể cả toàn quốc và kể cả khi đã đổi USD. Lúc ra mắt, lương thường ẩn cho đến khi cửa sổ 180 ngày tích lũy đủ. Màn phải đẹp và rõ ở trạng thái ẩn.

#### FR-8: Trạng thái trước lấy từ hồ sơ phiên

Số "trước" trong Học gì tiếp? tính từ thành phố, cấp bậc, vai trò mục tiêu và kỹ năng đã có của hồ sơ phiên. Thực hiện UJ-1.

**Hệ quả kiểm được:**

- Đổi thành phố hoặc cấp bậc trong hồ sơ phiên thì số trước đổi.
- Thêm một kỹ năng đã có thì độ phủ trước tăng, số trước không giảm, và kỹ năng đó không bị gợi ý như thể chưa có.
- Thêm một kỹ năng giả định thì số sau không nhỏ hơn số trước.
- Chưa chọn thành phố, cấp bậc và vai trò mục tiêu thì Học gì tiếp? hỏi các mục đó trước khi hiện chênh lệch.

### 5.3 Lộ trình 90 ngày

**Mô tả:** Lựa chọn đang có ở Học gì tiếp? trở thành lộ trình ba chặng. Mỗi chặng có một dự án thực hành. Mọi nhận định có Vì sao?. Người dùng lưu bằng một email và nhận liên kết mở lại. Agent Lộ trình viết tên dự án và câu của từng chặng từ khung đã tính. Màn ghi tên agent, không có bước «chạy agent» trước khi lộ trình hiện, và không hiện kế hoạch hay lời gọi tool. Thực hiện UJ-1 và UJ-2.

**Yêu cầu chức năng:**

#### FR-9: Tạo ba chặng và một dự án mỗi chặng

Người dùng tạo lộ trình 90 ngày từ hồ sơ phiên và các kỹ năng giả định đang chọn. Lộ trình có ba chặng, ngày 1–30, 31–60 và 61–90. Mỗi chặng có một dự án thực hành. Thực hiện UJ-1.

**Hệ quả kiểm được:**

- Không tạo được lộ trình khi Học gì tiếp? chưa có thành phố, cấp bậc và vai trò mục tiêu.
- Đủ ba chặng. Mỗi chặng có các kỹ năng của chặng đó, tên một dự án thực hành, và một câu nói người học làm ra cái gì.
- Kỹ năng trên lộ trình nằm trong kỹ năng giả định đang chọn, hoặc là kỹ năng đã có được chặng đào sâu khi không còn kỹ năng giả định.
- Đổi kỹ năng giả định rồi tạo lại thì nội dung chặng đổi theo lựa chọn mới.

#### FR-10: Mọi nhận định có Vì sao?

Mỗi nhận định trên lộ trình có Vì sao? trỏ tới nguồn đúng với câu đó, kể cả nhận định bị loại vì thiếu dữ liệu. Thực hiện UJ-1.

**Hệ quả kiểm được:**

- Đếm nhận định trên một lộ trình đã tạo thì mỗi nhận định có đúng một Vì sao? mở được.
- Vì sao? của một nhận định dựa trên tin trỏ tới tập tin đã trích hoặc tới link gốc, không trỏ tới nguyên văn mô tả công việc.
- Vì sao? của một nhận định dựa trên báo cáo gọi tên báo cáo.
- Nhận định bị loại vì dưới ngưỡng 30 tin vẫn có Vì sao?, và câu đó nói thiếu dữ liệu chứ không nói một mức lương.
- Lộ trình đã lưu mà còn nhận định thiếu Vì sao? thì không đạt SM-4. Lộ trình đó vẫn tính vào SM-1.

#### FR-11: Không xây hoa hồng trong hai tháng này

Hai tháng này không xây liên kết khóa, không xây nhãn hoa hồng giới thiệu khóa học, và không đếm lượt mở liên kết đó. Một chặng không có liên kết khóa vẫn đủ để tạo và lưu lộ trình. Thực hiện UJ-1.

**Hệ quả kiểm được:**

- Lộ trình tạo và lưu được khi mọi chặng đều không có liên kết khóa.
- Web của hai tháng này không có chỗ bấm sang một khóa học.
- Không có số đếm lượt mở liên kết khóa. Khoản này không được gọi là tiền của kỳ này.

#### FR-12: Lưu hồ sơ và lộ trình bằng email

Người dùng lưu lộ trình bằng một email. Hệ thống lưu hồ sơ và lộ trình với email đó, rồi gửi liên kết mở lại. Không có mật khẩu. Thực hiện UJ-1.

**Hệ quả kiểm được:**

- Bản đồ nhu cầu và Học gì tiếp? dùng được trước khi có email. Hồ sơ lúc đó chỉ ở trên máy.
- Gửi email hợp lệ thì hồ sơ và lộ trình được lưu, và người dùng nhận được liên kết mở lại.
- Gửi email thất bại thì lộ trình vẫn ở trên máy trong phiên đó, và chưa được tính là tạo xong.
- Không có trang hồ sơ công khai. Email không hiện cho người khác.

#### FR-13: Mở lại đúng lộ trình đã lưu

Người có email đã lưu mở lại được đúng hồ sơ và lộ trình đó bằng liên kết mở lại, hoặc bằng cách nhập lại email để nhận liên kết mới. Thực hiện UJ-2.

**Hệ quả kiểm được:**

- Mở liên kết thì thành phố, cấp bậc, vai trò mục tiêu, kỹ năng đã có và ba chặng khớp lần lưu.
- Cùng email, mở lại trong 14 ngày kể từ lúc lưu, được tính là một lần mở lại cho SM-2. Sau ngày 14, liên kết mở lại vẫn mở đúng lộ trình. Cửa sổ 14 ngày chỉ dùng để đo SM-2.
- Một email một lộ trình. Lưu lần nữa thì thay lộ trình trước và mốc 14 ngày tính từ lần lưu mới.
- So sánh offer và Soi tin không đòi email.

### 5.4 Xu hướng và hạn dùng kỹ năng

**Mô tả:** Lớp dữ liệu dùng chung cho Học gì tiếp? và cho lộ trình. Không có mục riêng trên điều hướng. Thực hiện UJ-1.

#### FR-14: Khuyến nghị tôn trọng xu hướng kỹ năng

Khi lớp dữ liệu nói nhu cầu một kỹ năng đang giảm, Học gì tiếp? và lộ trình không trình bày kỹ năng đó như thể nhu cầu đứng yên. Vì sao? trích lớp này khi nhận định dùng nó. Thực hiện UJ-1.

**Hệ quả kiểm được:**

- Kỹ năng mà lớp dữ liệu đánh dấu là đang giảm không đứng hạng nhất trong danh nên học tiếp. Vì sao? của kỹ năng đó nói mức giảm.
- Không có đường dẫn điều hướng tới một màn "Lương và hạn dùng".
- v1 không xin người dùng đóng góp mức lương của chính họ.

### 5.5 So sánh offer — hoãn v1.1

> Duy hoãn So sánh offer sang v1.1 ngày 2026-10-25 để dồn lực cho bốn agent. FR-15 và FR-16 giữ nguyên làm yêu cầu của v1.1, không thuộc hai tháng này.

**Mô tả:** Miễn phí, dùng được khi chưa lưu. Người dùng nhập hai offer và thấy thực nhận cả năm, kèm kiểm tra BHXH. Phòng tập thương lượng không có trong v1. Kết quả là ước tính, không phải tư vấn thuế. Thực hiện UJ-4.

#### FR-15: So thực nhận cả năm của hai offer

Người dùng nhập hai offer và thấy offer nào có thực nhận cả năm cao hơn, cùng mức chênh. Thực hiện UJ-4.

**Hệ quả kiểm được:**

- Mỗi offer có tên công ty, lương tháng, loại gross hoặc net, số người phụ thuộc, số tháng thưởng, phụ cấp, số ngày remote mỗi tuần, căn cứ đóng bảo hiểm (trên lương thật hoặc trên mức thấp hơn), và mức đóng khi chọn mức thấp hơn.
- Số ngày remote hiện cùng offer và không đổi thực nhận cả năm.
- Khi offer là gross và căn cứ là lương thật, mức đóng bằng lương gross. Khi offer là net, mức đóng mặc định bằng gross đã dò ngược, trừ khi người dùng nhập mức khác.
- Kết quả gọi tên công ty, nói offer nào cao hơn và chênh bao nhiêu mỗi năm, hoặc nói hai offer gần ngang nhau khi chênh dưới 1% thực nhận cả năm. Mỗi offer hiện thực nhận cả năm, net mỗi tháng, thuế mỗi tháng, và thanh thực nhận, bảo hiểm, thuế. Thực hiện UJ-4.
- Đổi một ô nhập thì thực nhận cả năm tính lại.
- Trên màn có căn cứ thuế và bảo hiểm đang dùng để tính, và có câu kết quả là ước tính, không thay thế tư vấn thuế.

#### FR-16: Cảnh báo khi căn cứ đóng bảo hiểm thấp hơn lương

Khi một offer đóng bảo hiểm trên mức thấp hơn lương gross đang dùng để tính, So sánh offer hiện khoản hụt cả năm và nói các chế độ sẽ tính trên mức thấp đó. Thực hiện UJ-4.

**Hệ quả kiểm được:**

- Offer đóng trên lương thật thì không có câu hụt.
- Offer đóng trên mức thấp hơn thì có khoản hụt cả năm, gồm phần người lao động và phần công ty ở mức ước tính.
- Mức đóng không vượt quá lương gross của offer đó.
- Kiểm tra BHXH nằm trên cùng màn với So sánh offer.

**Ngoài phạm vi:** không có phòng tập thương lượng, không có thang phân vị bên cạnh offer.

### 5.6 Soi tin

**Mô tả:** Bản nhẹ, miễn phí, dùng được khi chưa lưu. Người dùng đưa một link. Sản phẩm báo tin treo, tin trùng và lương bất thường khi dữ liệu đã có cho phép. Không chấm điểm lừa đảo, không tách đầu việc theo AI, không tra mã số thuế. Thực hiện UJ-3.

#### FR-17: Soi một link đang có trong dữ liệu

Người dùng dán một link gốc đang có trong dữ liệu và thấy số lần làm mới, ngày thấy đầu và ngày thấy gần nhất, tin trùng nếu có, và kết luận về lương. Thực hiện UJ-3.

**Hệ quả kiểm được:**

- Hiện số lần làm mới, ngày thấy đầu và ngày thấy gần nhất. Ba số này kiểm được mà không cần kết luận tin treo.
- Ngưỡng tin treo chưa được đo. Tuần 1 đo quy tắc tạm: làm mới từ lần thứ hai, hoặc vẫn đang mở sau 30 ngày kể từ ngày thấy đầu. Trước khi đo, không viết test coi quy tắc này là đúng, và không gắn nhãn tin treo như sự thật.
- Có tin trùng thì liệt kê là có tin đang mở khác trùng kỹ năng, thành phố, cấp bậc và khoảng lương. Câu cảnh báo không cần tên công ty.
- Khi ô mẫu của tin đủ ngưỡng 30 tin và lương công khai không nằm trong khoảng lương ghi trên tin, hiện lương bất thường.
- Khi ô mẫu dưới ngưỡng 30 tin, không kết luận lương bất thường. Hiện câu chưa đủ mẫu để xét lương.
- Không hiện điểm trên 100, không hiện nhãn đáng tin hoặc rủi ro cao, không hiện chỉ số AI.

#### FR-18: Link lạ không bị ép thành mô tả công việc

Khi link không có trong dữ liệu, Soi tin nói chưa soi được tin này. Thực hiện UJ-3.

**Hệ quả kiểm được:**

- Không có ô dán nguyên văn mô tả công việc.
- Nội dung người dùng dán không được lưu.
- Không có nút theo dõi tin và không có nút báo cáo cộng đồng trong v1.

## 6. Ngoài phạm vi

- Không ghép người dùng với tin đang mở, và không gợi ý tin vừa mở khóa.
- Không đánh giá nhà tuyển dụng, không có chỉ số phản hồi, không thu trải nghiệm ứng tuyển.
- Không đọc hợp đồng và không tư vấn pháp lý.
- Không có lộ trình của những người giống người dùng trong v1. Hướng này để sau, vì dễ nhận diện lại một người từ một nhóm nhỏ.
- Không có màn Remote hoặc Nhật, và không có chuyên mục nội dung đó trong hai tháng này.
- Không có review dự án, hộ chiếu kỹ năng, hay chỗ nộp repo trong v1.
- Không có phòng tập thương lượng và không có lương theo phân vị trong v1.
- Không có ứng dụng di động cài trên máy. Web mở trên trình duyệt điện thoại là giả định ở mục 9.
- Không có cổng riêng cho trường hoặc bootcamp trong v1.
- Không có mật khẩu, đăng nhập mạng xã hội, hay hồ sơ công khai.
- Không có giá, gói, hay chỗ trả tiền của ứng viên trong v1.
- Không có liên kết hoa hồng, nhãn hoa hồng, hay số đếm lượt mở liên kết đó trong hai tháng này.
- Không chạy quảng cáo để mua người dùng trong hai tháng này.
- Không hiện nguyên văn mô tả công việc và không trả nó qua API công khai. Dòng tin trên Postgres không có mô tả, tên và liên hệ của người tuyển dụng. Bản JSON-LD gốc lúc cào được lưu trên Silo theo NFR-2.

## 7. Phạm vi MVP

### 7.1 Trong v1

- Bản đồ nhu cầu với ba thành phố, các mốc dự báo (chưa có số khi chưa có công thức), tín hiệu sớm, dấu kỹ năng đã có, lương công khai theo ngưỡng 30 tin.
- Học gì tiếp? với kỹ năng giả định, danh xếp theo tin mở thêm trên mỗi tuần học, và cách nới khi ô mẫu mỏng.
- Lộ trình 90 ngày, Vì sao? trên mọi nhận định, lưu bằng email và liên kết mở lại. Ô email đứng lúc lộ trình hiện ra, không đứng trên Bản đồ nhu cầu.
- Xu hướng và hạn dùng kỹ năng như lớp dữ liệu của hai mục trên.
- Soi tin bản nhẹ, dùng được khi chưa lưu.
- Bốn agent Bản đồ, Học gì tiếp, Lộ trình, Soi tin, là yêu cầu bắt buộc.
- Làm mới dữ liệu tin đang mở mỗi ngày, vì một tin chỉ sống khoảng một tháng.

### 7.2 Để sau

- **v1.1.** So sánh offer và kiểm tra BHXH (FR-15, FR-16, UJ-4).
- **v2.** Review dự án. Đây là món ứng viên có thể trả, và là chỗ các gói cho trường nằm.
- **v2.** Phòng tập thương lượng.
- **v2.** Lương theo phân vị.
- **Sau v1, khi có người dùng và dữ liệu.** Thêm thành phố ngoài ba thành phố, khi Duy duyệt sau một lần đo mới. Ghép việc chỉ khi có giấy phép. Hai hướng này không phải việc của hai tháng này.
- **Ngoài hai tháng này.** Liên kết hoa hồng, nhãn hoa hồng, và việc đếm lượt mở liên kết đó. Chưa có nhà cung cấp khóa, nên khoản đó bằng không trong kỳ này.
- **Để đo sau.** Ví ứng viên, và CAC, chỉ đo khi có món v2 hoặc khi có kênh trả phí.

`[NOTE FOR PM: review dự án là điểm thu về sau. Hai tháng này không đo ví ứng viên, nên đừng kéo form nộp repo vào v1 để "cho có đường thu".]`

## 8. Thu tiền

Trên web của hai tháng này, tiền là không. Bốn chỗ ở lại: Bản đồ nhu cầu là mặt tiền, Học gì tiếp? và Lộ trình 90 ngày là phần lương công khai theo thành phố ở Việt Nam cùng lộ trình có nguồn, Soi tin dùng được khi chưa lưu. So sánh offer quay lại ở v1.1.

Việc còn hình dạng tiền là một trường hoặc bootcamp nói đồng ý thử. Đó là một lời nói, không phải một màn, và không phải một cổng riêng. Ứng viên không trả. Không có giá trên sản phẩm.

Hoa hồng giới thiệu khóa học không phải tiền của kỳ này. Gói trả phí cho trường, và khoản ứng viên trả cho review dự án, nằm ở v2.

## 9. Nền tảng

v1 là web. `[GIẢ ĐỊNH: web dùng được trên trình duyệt điện thoại, vì UJ-1 bắt đầu trên điện thoại. Không làm ứng dụng cài máy.]` Ba người, hai tháng.

Điều hướng của v1 có bốn chỗ: Bản đồ nhu cầu, Học gì tiếp?, Lộ trình 90 ngày, Soi tin. So sánh offer thành mục thứ năm ở v1.1. Bản đồ nhu cầu là chỗ mở vào. Xu hướng và hạn dùng kỹ năng không có mục riêng.

Bốn agent là yêu cầu bắt buộc, Duy chốt ngày 2026-10-27. Mỗi agent có LLM, lập kế hoạch, bộ nhớ và tool, theo AD-18 của kiến trúc.

## 10. Ràng buộc

**Dữ liệu tin.** Mỗi tin chỉ giữ kỹ năng, thành phố, cấp bậc, khoảng lương, ngày đăng và link gốc. Pipeline hiện có được dùng lại. Pipeline đọc robots.txt, không vượt trang chặn bot, danh xưng trung thực, giãn cách, và dừng khi bị chặn. Nguồn không dùng cho việc lấy tin: những trang chặn bot, những trang cấm thu thập trong điều khoản, và những hệ thống chặn trong robots.txt. Chi tiết nguồn và cách lấy nằm ở phụ lục brief, không lặp ở đây.

**Quyết định ngày 2026-10-22.** Số liệu đã trích được đưa vào sản phẩm, gồm ITviec và TopDev. Không xin phép và không chờ ý kiến luật sư trước khi làm. Duy chấp nhận rủi ro này. Câu chữ luật chạm Bản đồ nhu cầu và lương công khai. Các câu hỏi pháp lý ở mục 12 không chặn v1. API ATS là hướng để giảm dần phần tin lấy từ ITviec. Cách lấy nằm ở phụ lục.

**Việc riêng tư.** Email chỉ dùng để lưu và mở lại lộ trình. Trước khi gọi một API bên ngoài, bỏ thông tin cá nhân khỏi phần được gửi đi. Bản JSON-LD gốc chỉ nằm trên Silo theo NFR-2. Dòng tin trên Postgres không có tên và liên hệ người tuyển dụng.

**Số mỏng.** Dưới ngưỡng 30 tin thì không có lương công khai. Học gì tiếp? nới phạm vi và nói đã nới. Nguồn tin lệch về ITviec và về TP.HCM. Đo ngày 2026-10-27 trên 832 tin: chỉ 24 tin có lương VND, toàn bộ từ TopDev, và 140 tin chỉ có lương USD, phần lớn từ ITviec. Vì vậy ô lương đếm tin trong 180 ngày gần nhất và đổi USD theo tỷ giá cố định. VietJobs chỉ là nền lịch sử và được ghi công, không phải tin đang mở.

**Làm mới.** Tin đang mở được làm mới hằng ngày. Bản đồ nhu cầu hiện ngày của lần làm mới gần nhất.

**Ước tính.** Thực nhận cả năm (v1.1) và dự báo 18 tháng đều có nhãn là ước tính hoặc dự báo. Tham số thuế và trần bảo hiểm đang dùng hiện trên màn So sánh offer. Bộ số của kỳ tính thuế 2026 nằm ở addendum để làm bản đầu, và được thay khi quy định đổi.

## 11. Yêu cầu phi chức năng

- **NFR-1.** Mọi số lương công khai trên mọi màn đều vắng mặt khi ô mẫu dưới ngưỡng 30 tin. Gồm ô lương trên đầu Bản đồ nhu cầu, thẻ thành phố, Học gì tiếp?, và kết luận lương của Soi tin.
- **NFR-2.** Không hiện nguyên văn mô tả công việc trên màn và không trả nó qua API công khai. Dòng tin trên Postgres không có mô tả, tiêu đề, tên công ty, tên và liên hệ người tuyển. Bản JSON-LD gốc đọc lúc cào được lưu trên Silo `bronze/`, chỉ lệnh nạp và agent Soi tin đọc qua tool đã lọc. Chữ người dùng dán không được lưu ở đâu cả. Duy chốt giữ bản gốc ngày 2026-10-27 và chấp nhận rủi ro pháp lý ở mục 12.
- **NFR-3.** Khi nguồn dữ liệu lỗi, Bản đồ nhu cầu nói không tải được và giữ số của lần xem gần nhất nếu máy đang có số đó. Có lối thử lại.
- **NFR-4.** Khi bộ lọc không còn tin, Bản đồ nhu cầu nói không có tin khớp và có lối bỏ lọc về Tất cả.
- **NFR-5.** Giao diện chữ Việt. Web dùng được ở bề rộng trình duyệt điện thoại và ở bề rộng máy bàn.
- **NFR-6.** Một lộ trình đã lưu mở lại được từ liên kết mở lại trên máy khác với máy đã tạo.

## 12. Câu hỏi mở

1. **Tín hiệu sớm tính bằng gì.** Chưa có quy tắc phát hiện. Thẻ thành phố xây được với câu chưa ghi nhận tín hiệu đáng kể, theo FR-3. Quy tắc chỉ thành việc phải xây khi tuần 1 cho một quy tắc kiểm được. Chủ: Duy.
2. **Ngưỡng tin treo.** Chưa được đo. Quy tắc tạm để đo ở tuần 1 là làm mới từ lần thứ hai, hoặc còn mở sau 30 ngày. Chưa phải sự thật. Trước khi đo, không viết test như thể quy tắc đã đúng.
3. **Kết quả đo tuần 1.** Đã đo ô lương ngày 2026-10-27 trên một ảnh 832 tin; kết quả nằm ở mục 10 và ở sprint change proposal. Còn mở: ô lương sau khi cửa sổ 180 ngày tích lũy, ngưỡng mức khớp 50% có cho số tin hợp lý không, ngưỡng tin treo, và nếu dữ liệu cho phép, một quy tắc tín hiệu sớm.
4. **Pháp lý, để sau, không chặn v1.** Điều 27 Luật Việc làm có coi thông tin thị trường và lộ trình học miễn phí là dịch vụ việc làm phải xin phép hay không. Hoa hồng giới thiệu khóa học có phải đăng ký gì không, khi khoản đó được xây sau kỳ này. Nếu sản phẩm được gọi là giáo dục thì Luật AI có đặt vào nhóm rủi ro cao hay không, mốc tuân thủ đang được nói tới là tháng 9/2027. Lưu bản JSON-LD gốc của ITviec và TopDev trên Silo có vi phạm điều khoản hạn chế sao chép của hai trang không. Các câu này không chặn hai tháng xây.

## 13. Chỉ số thành công

Bốn mức dưới đây cùng phải đạt thì hai tháng được tính là đi tiếp. Đo trên người thật đã lưu lộ trình bằng email. Không mua người dùng để đạt mức.

**Chính**

- **SM-1.** Số email đã lưu ít nhất một lộ trình 90 ngày. Ngưỡng đi tiếp: từ 30 email. Đo bằng số hồ sơ đã lưu, không tính phiên chỉ xem. Kiểm FR-12.
- **SM-2.** Trong các email của SM-1, tỷ lệ mở lại đúng lộ trình trong 14 ngày kể từ lúc lưu. Ngưỡng đi tiếp: từ 25%, và ít nhất 8 email. Kiểm FR-13.
- **SM-3.** Số trường hoặc bootcamp đồng ý thử sản phẩm. Ngưỡng đi tiếp: từ 1. Đếm khi nhóm có một ghi chú có ngày, tên trường hoặc bootcamp, người đã nói đồng ý, và câu họ sẽ thử cùng web với ứng viên. Không có màn hình cho việc này. Kiểm mục 8.
- **SM-4.** Tỷ lệ nhận định trên các lộ trình đã lưu có Vì sao? trỏ đúng tin tuyển hoặc số liệu nguồn. Ngưỡng đi tiếp: 100%. Một câu không có nguồn là cả mốc trượt. Không hạ xuống 95%. Kiểm FR-10.

**Đối trọng, không lấy làm mục tiêu để kéo**

- **SM-C1.** Số lương công khai đang hiện. Không được tăng bằng cách hạ ngưỡng 30 tin. Đối trọng với sức hút của những con số trên Bản đồ nhu cầu và Học gì tiếp?.
- **SM-C2.** Số tin được gợi ý để nộp, và số lần nộp hồ sơ. Không phải thành công của v1. Đối trọng với SM-1, để sản phẩm không biến thành chỗ ghép việc.

Hai tháng này không đo ví ứng viên, không đo CAC, và không đếm lượt mở liên kết khóa.

## 14. Mục lục giả định

Những mục Duy đã duyệt ngày 2026-10-23 không còn trong danh này. Chúng là yêu cầu.

- Mục 9. Web dùng được trên trình duyệt điện thoại, vì UJ-1 bắt đầu trên điện thoại. Không làm ứng dụng cài máy.
