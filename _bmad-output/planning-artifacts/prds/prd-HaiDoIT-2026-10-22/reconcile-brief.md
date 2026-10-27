# Đối chiếu brief → PRD

Nguồn: `brief.md`. Hoa hồng, sáu mặt v1, email lúc tạo lộ trình, Lan/Khoa/Mai, ngưỡng tin treo, tín hiệu sớm, và SM-4 100% đã được quyết định sau ghi đè đúng chỗ; không liệt kê lại.

## 1. VietJobs chỉ là nền lịch sử, và phải ghi công

Brief, mục Dữ liệu: «Dataset VietJobs (VinNLP/VinUniversity, giấy phép MIT, có ghi công): 48.092 tin, trong đó 1.906 tin IT và 1.144 tin có lương. Không có tên công ty và ngày đăng, nên chỉ dùng làm nền lịch sử.»

PRD mục 10 và phụ lục mục «Dữ liệu và pipeline» khóa pipeline SkillNexus, trường được giữ, và ảnh 832 tin đang mở. Hai chỗ đó chưa có VietJobs. Cần nói rõ dataset này không có tên công ty và ngày đăng, chỉ được dùng làm nền lịch sử, và khi đưa vào Vì sao? hoặc tài liệu nguồn thì ghi công VinNLP/VinUniversity theo giấy phép MIT. Nhu cầu hôm nay, dự báo 18 tháng và Học gì tiếp? không đếm các tin này như tin đang mở.

## 2. ATS là nguồn chiến lược, tỷ trọng phải tăng

Brief, mục Dữ liệu: «API ATS là nguồn chiến lược» (Greenhouse, Lever, Workable, JSON công khai, một request mỗi công ty, tự lập danh sách công ty). «Mục tiêu là tăng dần tỷ trọng nguồn này để giảm phụ thuộc vào ITviec.»

Phụ lục có ảnh ATS 78 tin và xếp cách lấy JSON ATS vào việc kiến trúc. Mục tiêu tăng tỷ trọng để bớt phụ thuộc ITviec chưa thành ràng buộc của hai tháng. PRD mục 10 cần giữ mục tiêu đó: danh sách công ty dùng ATS nào là tài sản phải mở rộng, còn cách gọi endpoint vẫn để kiến trúc.

## 3. Mẫu lệch về ITviec và về TP.HCM

Brief, rủi ro 1: «ITviec chiếm khoảng 78% nguồn và vốn lệch về TP.HCM.» Câu giả định ngay sau đó (Data/AI từng thành phố có thể dưới 30 tin, đo trong tuần 1) PRD đã giữ ở FR-7 và mục 14.

Kết luận lệch nguồn và lệch thành phố chưa có ở mục 10, đoạn Số mỏng. Bản đồ nhu cầu và câu nới «toàn quốc» ở FR-7 cần đứng cạnh sự thật này: toàn quốc trong ảnh hiện tại vẫn là một mẫu khoảng ba phần tư ITviec và lệch TP.HCM. Giả định Data/AI dưới 30 tin giữ nguyên nhãn, đo tuần 1.

## 4. Trường và bootcamp dùng sản phẩm để đo chương trình

Brief, mục Đối tượng: trường đại học và bootcamp dùng đây làm «công cụ hướng nghiệp và minh chứng đầu ra». Mục Tầm nhìn: trong 2–3 năm Hải Đồ IT là «la bàn kỹ năng» của dân IT Việt Nam, «nơi trường học và bootcamp đo xem chương trình của họ có khớp với thị trường không.»

PRD mục 1 đã có nửa dành cho người học (quyết định học gì trước khi bỏ tiền và thời gian). Mục 3.2 và SM-3 chỉ còn «một lời đồng ý thử», cùng web, không cổng riêng. Mục 7.2 có review dự án, phân vị, thêm thành phố, ghép việc khi có phép. Hai mục 1 và 3.2 cần thêm việc trường và bootcamp đối chiếu chương trình với thị trường. Đó là lý do của lời đồng ý, vẫn là một lời nói ở ngoài sản phẩm, không thành màn và không thành cổng trong hai tháng này.

## 5. Không có lợi thế dữ liệu, và cửa sổ tập trung thì ngắn

Brief, mục Điểm khác biệt: «Nói thẳng: Hải Đồ IT không có lợi thế về dữ liệu. TopCV có khoảng 9–10 triệu hồ sơ, ITviec có báo cáo lương hằng năm, và cả hai đều có thể làm theo.» Cùng mục: lợi thế còn lại là «tốc độ và sự tập trung vào một nhóm người dùng», «chỉ tồn tại trong một khoảng thời gian ngắn, vì HRCV và X-Interview đã vào thị trường trong năm 2026.»

Phụ lục mục «Khoảng trống cạnh tranh đã thu hẹp» và PRD mục 2 đã thu hẹp câu «chưa đối thủ nào» (HireJack, ITviec). Phần thu hẹp đó giữ nguyên. Mục 2 vẫn cần hai câu brief chưa được thay: sản phẩm không có lợi thế dữ liệu, TopCV và ITviec có thể làm theo; cửa sổ của tốc độ và của một nhóm người dùng là ngắn vì HRCV và X-Interview đã vào thị trường năm 2026.
