---
name: Hải Đồ IT
description: Cách bốn chỗ của Hải Đồ IT (năm chỗ từ v1.1) hoạt động trên web, cho junior, fresher và người chuyển hướng.
status: final
created: 2026-10-22
updated: 2026-10-27
sources:
  - _bmad-output/planning-artifacts/prds/prd-HaiDoIT-2026-10-22/prd.md
  - _bmad-output/planning-artifacts/prds/prd-HaiDoIT-2026-10-22/addendum.md
  - _bmad-output/planning-artifacts/briefs/brief-HaiDoIT-2026-10-22/brief.md
  - _bmad-output/planning-artifacts/briefs/brief-HaiDoIT-2026-10-22/addendum.md
  - _bmad-output/planning-artifacts/research/market-hai-do-it-nen-tang-nghe-nghiep-it-viet-n-2026-10-22/research.md
  - prototype/Hải Đồ IT — Bản đồ tuyển dụng & Cố vấn đa agent.html
visual_priority: prototype/Hải Đồ IT — Bản đồ tuyển dụng & Cố vấn đa agent.html
---

# Hải Đồ IT — Trải nghiệm

Hai bản này là hợp đồng. `DESIGN.md` giữ mặt nhìn. Bản này giữ cách đi, trạng thái, và câu chữ ngắn. Khi DESIGN.md và EXPERIENCE.md lệch nhau, EXPERIENCE.md thắng về hành vi, và DESIGN.md thắng về mặt nhìn sau khi hành vi đã khớp. Khi một bản phác sau này lệch với hai hợp đồng, hai hợp đồng thắng.

Duy không nhận năm file trong `.working/key-*.html`. Những file đó không phải chuẩn mặt nhìn. Chuẩn mặt nhìn là file `prototype/Hải Đồ IT — Bản đồ tuyển dụng & Cố vấn đa agent.html`, và chỉ những phần phục vụ chức năng v1.

Năm chỗ lấy giao diện từ năm artboard sau. Hai tháng này chỉ xây bốn chỗ; So sánh offer chờ v1.1. Bản đồ nhu cầu lấy «Thị trường · Bản đồ nhu cầu», gồm bản đồ 3D, nút 3D và 2D, xoay trái, xoay phải, đặt lại, và thao tác kéo. Học gì tiếp? lấy «Phát triển · Mô phỏng Nếu–thì». Lộ trình 90 ngày lấy khối kết quả và ngăn Vì sao? của «Phát triển · Cố vấn đa agent». So sánh offer lấy phần nhập hai offer và kết quả của «Quyết định · So sánh offer & thương lượng». Soi tin lấy ô link và vùng kết quả của «Ứng tuyển · Soi tin».

Khi prototype và PRD lệch nhau về việc một chức năng có được làm, hoặc về một số có được hiện, PRD thắng. Mặt nhìn của chức năng còn lại giữ nguyên prototype. Trên các artboard đó, các chức năng sau không thuộc v1 nên không có mặt: nút «Chạy đa agent», phòng tập thương lượng, vòng điểm trên 100, chỉ số AI, nút theo dõi tin, và nút báo cáo cộng đồng. Câu do agent viết được ghi tên một trong bốn agent: Bản đồ, Học gì tiếp, Lộ trình, Soi tin. Màn không hiện kế hoạch và không hiện lời gọi tool. Lương công khai vẫn ẩn khi dưới 30 tin, kể cả khi prototype đang vẽ một số.

Đường này viết nhanh. Câu có nhãn [GIẢ ĐỊNH] là chỗ Duy chưa nói từng chữ. Các nhãn [GIẢ ĐỊNH] đã có trong PRD được giữ nguyên, không nâng thành sự thật đã đo.

## Foundation

Web một mặt, chữ Việt, mở trên trình duyệt điện thoại và trình duyệt máy bàn. Phần tử html của mọi bề mặt đặt `lang="vi"`. Không có ứng dụng cài máy. Không có hệ component có tên sẵn. Mặt nhìn là các token trong `DESIGN.md`.

[GIẢ ĐỊNH: web dùng được trên trình duyệt điện thoại, vì cảnh Lan bắt đầu trên điện thoại.]

Người dùng chính là junior khoảng 0–2 năm và fresher muốn chuyển hướng. Người dùng phụ là sinh viên năm cuối ngành IT. Cả hai dùng cùng một web. Trường và bootcamp, trong kỳ này, xem trên cùng web đó để đối chiếu chương trình của họ với thị trường. Không có cổng riêng. Lời một trường hoặc bootcamp đồng ý thử là một câu ghi ngoài sản phẩm, và kỳ này không có màn cho lời đó.

Kỳ này không có chỗ trả tiền, không có giá, và không có liên kết sang một khóa học.

## Information Architecture

| Bề mặt | Vào từ | Việc của bề mặt |
|---|---|---|
| Bản đồ nhu cầu | Mở web, hoặc logo | Ba thành phố: Hà Nội, TP. Hồ Chí Minh, Đà Nẵng. Số tin hôm nay, các mốc dự báo (chưa có số khi chưa có công thức đã đo), thẻ thành phố, dấu kỹ năng đã có |
| Học gì tiếp? | Thanh điều hướng, hoặc nút trên bản đồ | Thử kỹ năng giả định, thấy số tin, lương công khai hoặc trạng thái ẩn, và thời gian học |
| Lộ trình 90 ngày | Thanh điều hướng, hoặc nút tạo lộ trình | Ba chặng, Vì sao? trên từng nhận định, rồi ô email để lưu |
| So sánh offer — hoãn v1.1 | Thanh điều hướng, từ v1.1 | Hai offer, thực nhận cả năm, kiểm tra BHXH. Không có trên thanh điều hướng của hai tháng này. Các dòng offer bên dưới giữ cho v1.1. |
| Soi tin | Thanh điều hướng | Một link, số lần làm mới, hai ngày, tin trùng nếu có, lương bất thường hoặc câu chưa đủ mẫu |

[GIẢ ĐỊNH: câu «sáu chỗ» trong PRD là năm hàng trên cộng với lúc lưu email. Lúc lưu email nằm trên Lộ trình 90 ngày, không phải mục thứ sáu trên thanh.]

Xu hướng và hạn dùng kỹ năng là lớp dữ liệu dùng chung. Khối tám quý trên Bản đồ nhu cầu là chỗ người dùng nhìn thấy lớp đó. Học gì tiếp? và lộ trình đọc cùng lớp khi xếp hạng và khi viết Vì sao?. Không có mục «Lương & kỹ năng».

Không có bề mặt cho ghép việc, chỉ số phản hồi nhà tuyển dụng, đọc hợp đồng, lộ trình của người giống nhau, Remote hay Nhật, review dự án, phòng tập thương lượng, lương phân vị, hay bước chạy nhiều agent.

Hồ sơ phiên gồm thành phố, cấp bậc, vai trò mục tiêu, và kỹ năng đã có. Hồ sơ sống trên máy cho đến khi lộ trình được lưu. [GIẢ ĐỊNH: chỗ sửa hồ sơ nằm trên Học gì tiếp?, và Lộ trình 90 ngày dùng lại cùng các ô đó. Bản đồ chỉ đọc dấu đã có.]

Bản đồ nhu cầu và Học gì tiếp? dùng được khi chưa có email. So sánh offer và Soi tin vào thẳng, không có ô email, và đóng trình duyệt thì không còn gì trên máy chủ.

## Voice and Tone

Giọng ngắn nằm ở đây. Giọng thương hiệu nằm ở `DESIGN.md`, mục Brand & Style.

Sản phẩm trả lời bằng số đang có, bằng ngày làm mới, và bằng nguồn. Khi ô mẫu dưới 30 tin, câu nói chưa đủ mẫu. Khi một khoảng là dự báo, chữ «Dự báo» đứng cạnh khoảng đó. Khi một kỹ năng đang giảm, câu nói mức giảm.

| Nên viết | Tránh |
|---|---|
| «Chưa đủ mẫu.» | Một con số lương bịa để ô khỏi trống |
| «Dự báo» cạnh một khoảng | Một số dự báo viết như việc đã xảy ra |
| «Vì sao?» | «Tin mình đi» |
| «Kết quả là ước tính, không thay thế tư vấn thuế.» | «Tư vấn thuế» |
| «Chưa soi được tin này.» | «Dán mô tả công việc vào đây» |
| «Đã lưu. Liên kết mở lại đã gửi.» | «Đăng ký tài khoản» |
| «đã có» | Tên một người mẫu trên hồ sơ |

Tránh bốn cụm này trên mọi bề mặt: «tư vấn việc làm», «giới thiệu việc làm», «tư vấn pháp luật», «tư vấn thuế». Câu ước tính của offer được phép chứa cụm «không thay thế tư vấn thuế», vì đó là lời miễn trừ, không phải tên sản phẩm.

Không gắn nhãn «hoa hồng». Không gọi một khoản hoa hồng là tiền của kỳ này. Tên màn giữ đúng: Bản đồ nhu cầu, Học gì tiếp?, Lộ trình 90 ngày, So sánh offer, Soi tin, Vì sao?. Không dùng nhãn «Mô phỏng Nếu–thì» và không dùng «Cố vấn đa agent» như một bước trên màn.

[GIẢ ĐỊNH: các câu khóa dưới đây là chữ sẽ hiện trên màn.]

- Lương ẩn: «Chưa đủ mẫu.»
- Chưa có tín hiệu: «Chưa ghi nhận tín hiệu đáng kể cho thành phố này.»
- Link lạ: «Chưa soi được tin này.»
- Lưới bản đồ không tải được: «Không tải được dữ liệu thị trường.» Nút phụ: «Thử lại».
- Bộ lọc không còn tin: «Không có tin nào khớp bộ lọc.» Nút phụ: «Bỏ lọc».
- Chưa thêm kỹ năng giả định: «Chưa có kỹ năng giả định.» và không có dòng chênh lệch.
- Hai offer chênh dưới 1% thực nhận cả năm: «Hai offer gần ngang nhau.»
- Email không gửi được: «Chưa lưu được. Lộ trình vẫn còn trên máy này.»

Các số sau không được viết lên màn như một sự thật của sản phẩm: 0,12% đóng BHXH trên toàn bộ thu nhập; 60% lao động IT bị sa thải chưa có việc sau một năm; tin IT giảm 16,92%; gộp 40,9% với 54,5%; 34,3% như một việc đã đo; 93,49% dân IT dùng AI; mẫu 50 tin ghi «thương lượng» như bằng chứng lương IT; trung vị Data Engineer hoặc Data Analyst viết thành lương fresher; mọi số minh họa trong prototype; ảnh khoảng 832 tin viết thành quy mô đảm bảo. Các số ITviec quý 1/2025 về tin AI/ML tăng 41% và lượt tìm «AI» tăng 89% chỉ lên màn sau khi được đọc lại từ nguồn gốc.

## Component Patterns

Hành vi ở bảng này. Kích thước và màu nằm ở `DESIGN.md`, mục Components.

| Thành phần | Dùng ở | Quy tắc |
|---|---|---|
| Logo | Mọi bề mặt | Bấm về Bản đồ nhu cầu. |
| Thanh điều hướng | Mọi bề mặt | Bốn mục: Bản đồ nhu cầu, Học gì tiếp?, Lộ trình 90 ngày, Soi tin. So sánh offer thành mục thứ năm ở v1.1. Mỗi mục cao ít nhất 44px. Mục đang mở có gạch chân {colors.accent-cold}. Dưới 720px các mục xuống dòng. |
| Dấu đã có | Danh kỹ năng thành phố | Chỉ rơi vào kỹ năng đã có trong hồ sơ phiên. Xóa một kỹ năng đã có thì dấu mất trong cùng phiên. Lần đầu, chưa có hồ sơ, không có dấu. |
| Danh kỹ năng thành phố | Tab Cơ cấu của thẻ thành phố | Mỗi dòng là một kỹ năng đang được nhắc trong tin của thành phố đó. Đây là danh mà UJ-2 nhìn thấy dấu Python và SQL. |
| Bảng xếp hạng | Bản đồ nhu cầu, dưới bản đồ | Cột là hạng, tên thành phố, và số tin đang mở. Bấm một hàng thì chọn đúng thành phố đó. Hàng đang chọn có gạch {colors.accent-cold}. |
| Viên hồ sơ phiên | Mọi bề mặt, sau khi đã có đủ ba mục | Bấm tới ô sửa trên Học gì tiếp?. Không mở hồ sơ công khai. |
| Lớp chào | Bản đồ nhu cầu | Một lần mỗi máy. Khi lớp mở, focus đứng trên nút «Đã hiểu». «Đã hiểu» đóng và ghi nhớ trên máy đó. |
| Chip vai trò | Bản đồ nhu cầu | Mặc định «Tất cả». Mỗi chip cao ít nhất 44px và có aria-pressed. Đổi chip thì số tin ba thành phố đổi theo vai trò. |
| Tầm nhìn | Bản đồ nhu cầu | «NAY» hiện số tin đang mở. Trước khi có công thức đã đo, «+6T», «+12T», «+18T» không có số và hiện «Chưa ghi nhận dự báo cho mốc này.» Khi có công thức, mỗi mốc hiện một khoảng có nhãn dự báo. Vì sao? của khoảng đó trỏ tới số tin đang dùng để tính. Chọn mốc khác «NAY» thì tab thẻ thành phố chuyển sang «Dự báo». Mỗi mốc là nút cao ít nhất 44px, có aria-pressed. Tên gọi được của cột thành phố ở mốc dự báo gồm tên thành phố, chữ «Dự báo», và khoảng đang hiện. |
| Bản đồ 3D | Bản đồ nhu cầu | Đúng bản đồ prototype. Bấm cột, nhãn, hoặc hàng xếp hạng thì cùng chọn một thành phố và đổi thẻ bên phải. Đủ ba thành phố kể cả khi một thành phố ít tin. Mở vào thế 3D. Kéo ngang xoay, kéo dọc nghiêng. |
| Nút thế bản đồ | Bản đồ nhu cầu | 3D, 2D, xoay trái, xoay phải, đặt lại. 2D chuyển sang thế phẳng. 3D trở lại thế nghiêng. Giảm chuyển động tắt animation, và không gỡ các nút này. |
| Thẻ thành phố | Bản đồ nhu cầu | Ba tab trong một tablist, mỗi tab cao ít nhất 44px và có aria-selected. Cơ cấu là tỷ lệ từng vai trò cộng một nhóm còn lại, tổng 100%, rồi đến danh kỹ năng thành phố. Lương là một số hoặc câu chưa đủ mẫu; khi số có dùng tin lương USD, dưới số có dòng tỷ giá và ngày áp dụng. Dự báo là câu «Chưa ghi nhận dự báo cho mốc này.» cho đến khi có công thức đã đo, rồi là một khoảng; kèm đúng một tín hiệu với Vì sao?, hoặc câu chưa ghi nhận. Khi đã có công thức và tầm nhìn đang là «NAY», chỗ dự báo lấy khoảng mốc 12 tháng. |
| Ô lương đầu trang | Bản đồ nhu cầu | Cùng một ô mẫu với lương trên thẻ. Chưa chọn thành phố thì không hiện số. Bộ lọc một vai trò thì ô đó là vai trò đang lọc. Bộ lọc «Tất cả» thì vai trò của ô là vai trò có nhiều tin nhất tại thành phố đó. Đã chọn cấp thì ô lấy cấp của hồ sơ phiên. Chưa chọn cấp thì dùng Junior. |
| Khối xu hướng tám quý | Bản đồ nhu cầu | Đọc lớp xu hướng. Không phải một màn riêng. Có chú giải chữ «tăng», «giảm» và «đi ngang». Khi lớp chưa có số, khối hiện «Chưa đủ mẫu.» |
| Nút chính | Bản đồ, Học gì tiếp?, Lộ trình, Soi tin | [GIẢ ĐỊNH: trên bản đồ, nút «Thử một kỹ năng cho thành phố này» mở Học gì tiếp? và mang theo thành phố đang chọn nếu đã chọn.] Trên Học gì tiếp? và trên lộ trình, nút «Tạo lộ trình 90 ngày» tạo ba chặng từ hồ sơ phiên và các kỹ năng giả định đang chọn. Khi thiếu thành phố, cấp bậc hoặc vai trò mục tiêu, nút tạo dùng aria-disabled, vẫn nằm trong thứ tự Tab, và aria-describedby trỏ tới câu đang hỏi ba mục đó. |
| Nút phụ | Bản đồ, Học gì tiếp? | «Thử lại» gọi lại nguồn. «Bỏ lọc» chọn lại «Tất cả». «Đặt lại» xóa kỹ năng giả định và đưa các số về trạng thái trước. |
| Chip kỹ năng | Học gì tiếp?, lộ trình | Danh để chọn là danh cố định của nhóm. Mỗi chip cao ít nhất 44px và có aria-pressed. Người dùng không gõ một kỹ năng tự do. Kỹ năng đã có và kỹ năng giả định đang chọn không còn trong danh nên học tiếp. |
| Danh nên học tiếp | Học gì tiếp? | Mỗi dòng hiện số tin tăng, số tuần, và số tin trên mỗi tuần. Xếp theo số tin mở thêm trên mỗi tuần học. Số tuần là số nhóm đã gán. Kỹ năng lớp dữ liệu đánh dấu là đang giảm không đứng hạng nhất, và Vì sao? của kỹ năng đó nói mức giảm. Bấm «Thêm» thì kỹ năng đó vào nhóm giả định và các số đổi ngay. |
| Thẻ chặng | Lộ trình 90 ngày | Đủ ba chặng, ngày 1–30, 31–60, 61–90. Mỗi chặng có kỹ năng của chặng, tên một dự án, và một câu sản phẩm người học làm ra. Kỹ năng trên lộ trình nằm trong kỹ năng giả định đang chọn. Khi không còn kỹ năng giả định, một chặng đào sâu kỹ năng đã có. Đổi kỹ năng giả định rồi tạo lại thì chữ trong chặng đổi theo. Một chặng không có liên kết khóa vẫn tạo và lưu được. Không có chỗ bấm sang một khóa học. |
| Nút Vì sao? | Thẻ thành phố khi có tín hiệu, lộ trình, danh đã nới | Mỗi nhận định đúng một nút, cao ít nhất 44px. Mở ngăn. Nhận định bị loại vì thiếu dữ liệu vẫn có nút, và câu nói thiếu dữ liệu, không nói một mức lương. |
| Ngăn Vì sao? | Đè lên bề mặt hiện tại | Nguồn từ tin thì trỏ tập tin đã trích hoặc link gốc, không trỏ nguyên văn mô tả. Nguồn từ báo cáo thì gọi tên báo cáo trong bốn tên ITviec, TopDev, TopCV, JobOKO. VietJobs chỉ được ghi công như nền lịch sử, không như tin đang mở. Kết quả đã nới thì nói ô gốc dưới 30 tin và nói đang ở bước toàn quốc hay bước nhóm vai gần. Ngăn dùng role dialog, tên lấy từ câu nhận định. Khi mở, focus vào nút đóng. Tab không đi ra trang phía sau. Escape hoặc bấm lớp mờ thì đóng, rồi trả focus về nút Vì sao? đã mở. Khi giảm chuyển động bật, ngăn hiện ngay, không trượt. |
| Ô email | Lộ trình 90 ngày, sau khi ba chặng đã hiện | Nhãn nhìn thấy gắn với input, autocomplete là email. Một email, không mật khẩu. Gửi được thì lưu hồ sơ lẫn lộ trình và đưa liên kết mở lại. Gửi thất bại thì lộ trình còn trên máy, câu lỗi có aria-invalid và aria-describedby, và chưa tính là tạo xong. Cùng email lưu lần nữa thì thay lộ trình trước và tính lại 14 ngày. |
| Ô nhận lại liên kết | Lộ trình 90 ngày, khi máy này chưa có lộ trình đã lưu | [GIẢ ĐỊNH: người dùng nhập lại email để nhận liên kết mới. Email chưa từng lưu thì câu «Chưa có lộ trình cho email này.»] |
| Panel offer | So sánh offer | Sửa một ô thì thực nhận cả năm tính lại. Ngày remote hiện trên panel và không đổi tiền. Chọn «Trên mức thấp hơn» thì hiện ô mức đóng. Khi offer là gross và căn cứ là lương thật, mức đóng bằng lương gross. Offer net mặc định dò ngược ra gross, trừ khi người dùng nhập mức khác. |
| Thanh thực nhận | So sánh offer | Mỗi offer có thực nhận cả năm, net mỗi tháng, thuế mỗi tháng, và thanh ba khúc. Căn cứ thuế và bảo hiểm đang dùng nằm trên màn, trong mục đóng sẵn «Tham số tính (kỳ tính thuế 2026)». Mục đó hiện đúng bộ số phụ lục PRD đã ghi cho bản đầu, và được thay khi quy định đổi. |
| Hộp hụt bảo hiểm | So sánh offer | Chỉ hiện khi căn cứ là mức thấp hơn lương gross đang dùng. Nói khoản hụt cả năm, gồm phần người lao động và phần công ty ở mức ước tính, và nói các chế độ tính trên mức thấp đó. |
| Kết quả soi tin | Soi tin | Luôn hiện số lần làm mới, ngày thấy đầu, ngày thấy gần nhất. Lần làm mới của một tin là số lần tin đó được thấy lại, và khác với ngày làm mới dữ liệu ghi ở chân Bản đồ nhu cầu. Có tin trùng thì liệt kê là có tin đang mở khác trùng kỹ năng, thành phố, cấp bậc và khoảng lương, không cần tên công ty. Lương bất thường chỉ khi ô mẫu đủ 30 tin và lương công khai không nằm trong khoảng ghi trên tin. Dưới ngưỡng thì câu «Chưa đủ mẫu để xét lương.» |
| Toast | Sau một việc vừa xong | Dùng role status. Có nút đóng cao ít nhất 44px. Hẹn giờ không phải cách duy nhất để câu biến mất. Không mang một quyết định mới. |
| Khối trạng thái | Bề mặt nào có đang tải, lỗi nguồn, hoặc rỗng trong State Patterns | Đang tải hiện thanh xương trên nền thẻ, và không hiện số mẫu. Lỗi và rỗng hiện một câu đã chốt. Nút phụ hiện khi dòng trạng thái đó có lối thử lại hoặc bỏ lọc. |

Học gì tiếp? chỉ dựng kịch bản cho Fresher và Junior. Chưa chọn thành phố, cấp bậc và vai trò mục tiêu thì màn hỏi ba mục đó trước khi hiện chênh lệch. Tin đủ điều kiện là tin đang mở trong phạm vi đang tính, đúng vai trò mục tiêu và đúng cấp bậc, có ít nhất một kỹ năng, và có mức khớp tin từ 50% trở lên: số kỹ năng của tin nằm trong tập đang xét, chia cho số kỹ năng của tin. Số trước dùng kỹ năng đã có. Số sau dùng kỹ năng đã có cùng kỹ năng giả định đang chọn, nên thêm kỹ năng chỉ làm số tin tăng hoặc giữ nguyên. Thời gian học là tổng số tuần của các kỹ năng giả định đang chọn. Đổi thành phố hoặc cấp bậc thì số trước đổi. Thêm một kỹ năng đã có thì độ phủ trước tăng. Độ phủ của một vai trò là số kỹ năng yêu cầu của vai đó đang nằm trong kỹ năng đã có, chia cho số kỹ năng yêu cầu của vai đó. Danh kỹ năng yêu cầu đi cùng danh cố định.

Khi ô vai trò × thành phố × cấp bậc dưới 30 tin trong tập lương 180 ngày, Học gì tiếp? nới toàn quốc (gộp ba thành phố) cùng vai trò và cùng cấp bậc trước. Nếu ô đó vẫn dưới ngưỡng thì nới sang nhóm vai gần. Nhóm vai gần: Data/AI đứng riêng, Backend với Frontend, DevOps/Cloud với Bảo mật, Mobile đứng riêng. Đo 2026-10-27: không ô Fresher hoặc Junior nào đủ 30 tin có lương, kể cả toàn quốc, nên trạng thái lương ẩn là trạng thái thường gặp nhất lúc ra mắt và phải rõ ràng, không giống lỗi. Nguồn tin lệch về ITviec và về TP. Hồ Chí Minh. Lương của ô gốc mỏng không hiện số. Khi phạm vi đã nới đủ 30 tin, lương công khai của phạm vi đó được hiện.

## State Patterns

| Trạng thái | Bề mặt | Cách xử lý |
|---|---|---|
| Mở lần đầu | Bản đồ nhu cầu | Lớp chào. Bộ lọc «Tất cả». Tầm nhìn «NAY». Chưa chọn thành phố. Không có dấu đã có. Không có hồ sơ mẫu. |
| Đang tải | Bản đồ nhu cầu | Khối xương đúng chỗ cột, thẻ và bảng. |
| Lỗi nguồn | Bản đồ nhu cầu | «Không tải được dữ liệu thị trường.» và «Thử lại». Nếu máy còn số của lần xem gần nhất thì giữ số đó. |
| Hết tin | Bản đồ nhu cầu | «Không có tin nào khớp bộ lọc.» và «Bỏ lọc». |
| Lương ẩn | Bản đồ, Học gì tiếp?, Soi tin | Không có số lương. Có câu chưa đủ mẫu. Thành phố và số tin vẫn hiện. |
| Chưa có tín hiệu | Thẻ thành phố | «Chưa ghi nhận tín hiệu đáng kể cho thành phố này.» Khi chưa có quy tắc phát hiện, đây là câu của thẻ. |
| Chưa đủ hồ sơ | Học gì tiếp?, Lộ trình | Hỏi thành phố, cấp bậc, vai trò mục tiêu. Chưa hiện chênh lệch và chưa tạo được lộ trình. |
| Chưa có kỹ năng giả định | Học gì tiếp? | «Chưa có kỹ năng giả định.» Thời gian học ở trạng thái chưa có. Không có dòng chênh lệch. |
| Đã thêm kỹ năng giả định | Học gì tiếp? | Số tin trước và sau, thời gian học, lương trước và sau hoặc trạng thái ẩn, đổi ngay khi bấm. Đổi thành phố hoặc cấp bậc trong hồ sơ phiên thì số trước đổi. |
| Đã xóa kịch bản | Học gì tiếp? | Các số trở về trạng thái trước. |
| Lộ trình chưa tạo | Lộ trình 90 ngày | Ô hồ sơ. Nút tạo. Chưa có ba thẻ và chưa có ô email. |
| Lộ trình đã hiện, chưa lưu | Lộ trình 90 ngày | Ba thẻ, mỗi nhận định có Vì sao?, ô email ở dưới. |
| Lưu được | Lộ trình 90 ngày | Toast hoặc câu «Đã lưu. Liên kết mở lại đã gửi.» |
| Lưu lỗi | Lộ trình 90 ngày | «Chưa lưu được. Lộ trình vẫn còn trên máy này.» Chưa tính là tạo xong. |
| Mở lại đúng liên kết | Lộ trình 90 ngày | Đúng thành phố, cấp, vai trò, kỹ năng đã có, và ba chặng của lần lưu. Sau ngày 14 liên kết vẫn mở đúng lộ trình. Cửa sổ 14 ngày chỉ để đo. |
| Máy khác, chưa có liên kết trong tay | Lộ trình 90 ngày | Ô nhập lại email. Email chưa từng lưu thì câu «Chưa có lộ trình cho email này.» |
| Offer thiếu ô | So sánh offer | Chưa hiện câu bên nào cao hơn. |
| Offer đủ ô | So sánh offer | Câu gọi tên công ty đã nhập, nói bên nào cao hơn và chênh bao nhiêu mỗi năm, hoặc nói gần ngang nhau. Có câu ước tính. |
| Đóng bảo hiểm trên mức thấp | So sánh offer | Thêm hộp hụt. Offer đóng trên lương thật thì không có câu hụt. |
| Soi tin chưa dán | Soi tin | Ô link và nút «Soi tin». Không có danh tin mẫu. |
| Link có trong dữ liệu | Soi tin | Ba số luôn có. Tin trùng, lương bất thường, hoặc câu chưa đủ mẫu tùy dữ liệu. |
| Link không có | Soi tin | «Chưa soi được tin này.» Không có ô dán mô tả. |
| Mất mạng | Bản đồ nhu cầu, Học gì tiếp?, Soi tin | [GIẢ ĐỊNH: dùng cùng trạng thái lỗi nguồn, và giữ số lần xem gần nhất nếu máy còn số đó.] |
| Đang tải | Học gì tiếp?, Soi tin | Cùng khối xương của bản đồ, trên vùng số của màn đó. |
| Lỗi nguồn | Học gì tiếp?, Soi tin | «Không tải được dữ liệu thị trường.» và «Thử lại». Câu lỗi nằm trong role alert. |
| Đang mở liên kết | Lộ trình 90 ngày | Khối xương trên chỗ ba chặng. Nếu máy này còn lộ trình vừa lưu, giữ lộ trình đó trong lúc chờ. |
| Liên kết không trả lộ trình | Lộ trình 90 ngày | «Không tải được dữ liệu thị trường.» Nếu máy này còn bản đã lưu, bản đó vẫn ở trên màn. |
| Giảm chuyển động | Bản đồ nhu cầu | Không chạy animation vào thế 3D. Nút 3D, 2D, xoay và đặt lại vẫn dùng được. |

Soi tin không có nút theo dõi tin và không có nút báo cáo cộng đồng. So sánh offer không lưu trên máy chủ. Không có trạng thái từ chối quyền, vì không có hồ sơ công khai và không có vai trò người xem bị chặn.

Nhãn «tin treo» chưa có ngưỡng đã đo. Quy tắc tạm để đo ở tuần 1 là làm mới từ lần thứ hai, hoặc vẫn đang mở sau 30 ngày kể từ ngày thấy đầu. Trước khi tuần 1 đo, màn vẫn hiện số lần làm mới và hai ngày như sự kiện kiểm được. Câu kết luận tin treo, nếu hiện, phải nói ngưỡng đang dùng, và ngưỡng đó chưa phải sự thật đã đo.

## Interaction Primitives

Bấm để làm. Trên bản đồ 3D, kéo ngang để xoay và kéo dọc để nghiêng, đúng thao tác của prototype. Nút 2D đặt bản đồ phẳng. Nút 3D trả bản đồ về thế nghiêng.

Escape đóng lớp chào khi focus đang ở trong lớp, đóng ngăn Vì sao? rồi trả focus về nút đã mở, và đóng mục tham số thuế nếu đang mở. Khi lớp chào đang mở, focus đứng trên «Đã hiểu», và nút đó nằm ngay sau logo. Tab đi theo thứ tự đọc: logo, năm mục, nội dung chính, rồi việc chính của màn.

Ô nhập email, offer, và link nhận bàn phím. Chip vai trò và chip kỹ năng là nút thật, bấm được bằng bàn phím.

Bị cấm trên kỳ này: kéo để sắp xếp lại, cuộn vô hạn, lớp hộp thoại chồng hai tầng, nút chỉ hiện khi rê chuột trên điện thoại, bước «chạy agent» trước khi lộ trình hiện, và ô dán nguyên văn mô tả công việc.

## Accessibility Floor

Hành vi ở đây. Tương phản của từng mã màu nằm ở `DESIGN.md`, mục Colors.

[GIẢ ĐỊNH: mục tiêu là WCAG 2.2 AA trên web responsive. Các cặp chịu lực và cách vẽ viền đã được khóa trong `DESIGN.md`, mục Colors. Chữ bắt buộc dùng {colors.ink} hoặc {colors.ink-lead} trên {colors.surface}.]

- Mọi nút có tên gọi được, gồm Vai trò, Tầm nhìn, Thành phố, và «Vì sao?» kèm một đoạn ngắn của nhận định.
- Khi sang màn, trình đọc nhận tên bề mặt.
- Ô lương ẩn được đọc bằng câu «Chưa đủ mẫu.», không phải bằng một số bị khuyết.
- Thứ tự Tab khớp thứ tự đọc. Escape đóng lớp trên cùng.
- Câu lỗi nguồn, câu bộ lọc rỗng, và câu lưu thất bại nằm trong role alert ngay khi chúng xuất hiện.
- Vùng bấm của mục điều hướng, chip, nút Vì sao?, nút chính, nút phụ và nút đóng cao ít nhất 44px.
- Giảm chuyển động thì bản đồ không chạy animation, ngăn Vì sao? hiện ngay, và toast hiện ngay, không trượt. Nút 3D, 2D, xoay và đặt lại vẫn dùng được.
- Viền focus dày 2px, màu {colors.accent-hot}, cách mép control 2px để vòng nằm trên nền tối.

## Responsive & Platform

| Bề rộng | Cách xếp |
|---|---|
| Từ 720px trở lên | Header một hàng. Bản đồ, Học gì tiếp?, và Lộ trình 90 ngày chia hai cột. Hai offer nằm cạnh nhau khi còn đủ chỗ. |
| Dưới 720px | [GIẢ ĐỊNH: một cột. Bốn mục điều hướng xuống dòng. Kịch bản của Học gì tiếp? nằm trước các số. Hồ sơ lộ trình nằm trước ba chặng. Hai offer xếp dọc. Viên hồ sơ, nếu đã có, rút còn thành phố và vai trò. Ngăn Vì sao? rộng bằng phần nhỏ hơn giữa bề rộng màn hình và 560px.] Bản đồ 3D của prototype nằm trước thẻ thành phố. Nút 3D, 2D, xoay, đặt lại và thao tác kéo vẫn còn. |

Không có ứng dụng iOS hay Android. Không có cử chỉ riêng của hệ điều hành. In ấn và PDF không thuộc kỳ này.

## Inspiration & Anti-patterns

Lấy từ prototype, trong phần còn thuộc kỳ này: bản đồ cột là mặt tiền (ba cột thay bảy), hộp lương nét đứt khi dưới 30 tin, ngăn Vì sao? trượt từ phải, hai panel offer với thanh ba màu, và ô dán link ở Soi tin.

Lấy từ brief: Bản đồ nhu cầu giữ cách dùng của prototype ngày 2026-10-22, gồm các thành phố (ba từ 2026-10-27), kéo để xem dự báo, chạm thành phố để xem cơ cấu, lương và tín hiệu sớm.

Tránh các bề mặt người dùng Việt đã thấy, khi chúng kéo sản phẩm sang việc khác:

- Báo cáo lương ITviec khóa sau form email và số điện thoại. Lương trên Hải Đồ IT hoặc hiện một số, hoặc nói chưa đủ mẫu, trên chính màn đó.
- Điểm khớp hồ sơ với từng tin của TopCV, HRCV và các sàn ghép việc. Kỳ này không chấm một người với một tin.
- Review nhà tuyển dụng ẩn danh. Không có bảng công ty nào trả lời, và không có form kể trải nghiệm ứng tuyển.
- Máy tính gross-net đã có ở TopCV, TopDev và Thư Viện Pháp Luật. So sánh offer ở lại vì PRD yêu cầu thực nhận cả năm và kiểm tra BHXH, và câu trên màn gọi kết quả là ước tính.
- Cố vấn hội thoại không nguồn. Mỗi nhận định trên lộ trình có Vì sao?.

## Ngưỡng, nguồn, và hồ sơ

Ngưỡng 30 tin chỉ quyết định lương công khai có hiện hay không. Ngưỡng 30 người tạo lộ trình là mốc đo sản phẩm. Hai ngưỡng này không dùng chung một câu trên màn.

Một lương công khai là một số của ô mẫu khi ô đó đủ 30 tin trong tập lương 180 ngày. Khi số có dùng tin lương USD, dưới số ghi «Có tin lương USD, đổi theo {tỷ giá} đ/USD ngày {ngày}.» v1 không hiện dải phân vị. v1 không dự báo lương. v1 không xin người dùng đóng góp mức lương của chính họ. Cách gộp nhiều khoảng lương thành một số, cách tính khoảng dự báo, và cách phát hiện tín hiệu sớm thuộc kiến trúc hoặc tuần 1. Người dùng vẫn thấy: một số khi đủ mẫu, một khoảng có nhãn dự báo, một tín hiệu hoặc câu chưa ghi nhận.

Vì sao? của nhận định dựa trên tin dùng các trường được giữ: kỹ năng, thành phố, cấp bậc, khoảng lương, ngày đăng, link gốc. Không hiện nguyên văn mô tả. Không hiện tên và liên hệ người tuyển dụng. Trước khi gọi một API bên ngoài, bỏ thông tin cá nhân khỏi phần được gửi đi.

Email chỉ dùng để lưu và mở lại lộ trình. Email không hiện cho người khác. Không có mật khẩu, không có đăng nhập mạng xã hội, và không có trang hồ sơ công khai.

Chân trang mỗi màn ghi ngày của lần làm mới dữ liệu gần nhất. [GIẢ ĐỊNH: chân trang còn một câu «Lương công khai ẩn khi dưới 30 tin.» Chân trang không viết «số liệu minh họa».]

## Key Flows

Lan, Khoa và Mai chỉ là tên mock. Ba cảnh không phải bằng chứng, và không chứng minh một người thật sẽ quay lại. Không có buổi ngồi với người thật nào để kể. Không thêm cảnh Lan suýt trả tiền cho một khóa.

### UJ-1. Lan tạo lộ trình 90 ngày lần đầu

Lan, một năm làm PHP ở Đà Nẵng, muốn sang Data/AI.

1. Lan mở web trên điện thoại. Chưa có email nào được lưu.
2. Lớp chào hiện. Lan bấm «Đã hiểu».
3. Lan xem Bản đồ nhu cầu, chọn Đà Nẵng, và thấy số tin, cơ cấu, lương hoặc câu chưa đủ mẫu, và câu chưa ghi nhận tín hiệu hoặc một tín hiệu có Vì sao?.
4. Lan sang Học gì tiếp?, đặt thành phố Đà Nẵng, cấp Junior, vai trò mục tiêu, và đánh dấu Python cùng SQL là kỹ năng đã có.
5. Lan thêm một kỹ năng giả định trong danh cố định, thấy số tin trước và sau, thời gian học, và lương hoặc trạng thái ẩn.
6. Lan chọn một dòng trong danh nên học tiếp.
7. Lan bấm «Tạo lộ trình 90 ngày».
8. **Đỉnh:** ba chặng hiện ra. Một nhận định có Vì sao? trỏ về nguồn. Một nhận định bị loại vì thiếu dữ liệu vẫn có Vì sao? giải thích vì sao bị loại.
9. Lan nhập email. Hồ sơ và lộ trình được lưu. Lan nhận liên kết mở lại.

Khi trật: ô Data/AI ở Đà Nẵng dưới 30 tin thì lương ô đó không hiện số, Học gì tiếp? nới toàn quốc trước rồi nhóm vai gần nếu vẫn mỏng, và Vì sao? nói đang ở bước nào. Đo 2026-10-27: Đà Nẵng có 21 tin đang mở, nên cảnh này gần như chắc chắn xảy ra. Khi email không gửi được, lộ trình còn trên máy và chưa tính là tạo xong.

### UJ-2. Lan mở lại lộ trình trong 14 ngày

Cùng Lan, ngày thứ mười, trên một máy khác.

1. Lan mở liên kết mở lại, hoặc nhập lại đúng email để nhận liên kết mới rồi mở.
2. Lộ trình hiện đúng ba chặng đã lưu.
3. Lan mở Bản đồ nhu cầu.
4. **Đỉnh:** Python và SQL vẫn có dấu «đã có». Lan không phải chọn lại từ đầu.
5. Lần mở này được tính là mở lại trong 14 ngày vì cùng email và còn trong cửa sổ tính từ lúc lưu.

Khi trật: sau ngày 14, liên kết vẫn mở đúng lộ trình, và lần mở đó không tính vào cửa sổ 14 ngày. [GIẢ ĐỊNH: email chưa từng lưu thì màn nói «Chưa có lộ trình cho email này.» và không tạo một lộ trình trống.] Một email giữ một lộ trình. Tạo lộ trình mới thì thay lộ trình cũ và cửa sổ 14 ngày tính lại từ lần lưu mới.

### UJ-3. Khoa soi tin rồi đóng trang

Khoa, sinh viên năm cuối ở Hà Nội, đang cầm một link tin.

1. Khoa vào thẳng Soi tin. Không có ô email.
2. Khoa dán link và bấm «Soi tin».
3. **Đỉnh:** nếu link có trong dữ liệu, Khoa thấy số lần làm mới, ngày thấy đầu và ngày thấy gần nhất, cùng tin trùng nếu có, và lương bất thường hoặc câu chưa đủ mẫu. Nếu link không có, Khoa thấy «Chưa soi được tin này.»
4. Khoa đóng trang. Không có gì được lưu trên máy chủ.

Khi trật: dữ liệu không đủ để xét lương thì không có kết luận lương bất thường, và màn không xin nguyên văn mô tả công việc. Nội dung dán nhầm vào ô không được lưu.

### UJ-4. Mai so sánh hai offer rồi đóng trang

*Hoãn v1.1 cùng So sánh offer. Giữ cảnh này cho v1.1.*

Mai, fresher ở Đà Nẵng, đang cầm hai offer. Một bên đóng bảo hiểm trên mức thấp hơn lương.

1. Mai vào thẳng So sánh offer. Không có ô email.
2. Mai nhập hai offer, gồm căn cứ đóng bảo hiểm và mức đóng nếu chọn mức thấp hơn.
3. **Đỉnh:** câu kết quả gọi tên công ty Mai đã nhập, nói bên nào có thực nhận cả năm cao hơn và chênh bao nhiêu, hoặc nói hai offer gần ngang nhau, và hiện khoản hụt của bên đóng thấp. Câu ghi đây là ước tính.
4. Mai đóng trang. Không có gì được lưu trên máy chủ.

Khi trật: một offer còn thiếu ô bắt buộc thì chưa có câu bên nào cao hơn. Đổi số ngày remote không đổi thực nhận. Đóng trình duyệt thì hai offer không còn trên máy chủ.

## Giả định đường nhanh còn để Duy sửa

Các câu dưới đây là chỗ đường nhanh đã điền vì chưa có lời chốt. Sửa câu nào thì câu đó ra khỏi danh này.

- Mức cược là sản phẩm tiêu dùng, kèm bốn cụm chữ cần tránh đã nêu ở Voice and Tone.
- Lớp chào không tên, một lần mỗi máy, nút «Đã hiểu».
- Khối tám quý nằm trên Bản đồ nhu cầu. Không có ticker chạy.
- Nút «Báo nguồn sai hoặc đã cũ» không có trong kỳ này. Duy đã bỏ chức năng đó.
- Bản đồ 3D, nút 3D, 2D, xoay trái, xoay phải và đặt lại đã được Duy chốt theo prototype. Không còn là giả định. Dưới 720px bản đồ vẫn là khối đó, xếp trước thẻ thành phố. Giảm chuyển động chỉ tắt animation.
- Điều hướng bốn mục phẳng trong hai tháng này, năm mục từ v1.1. Viên hồ sơ không có tên người.
- «Sáu chỗ» gồm lúc lưu email, không gồm mục điều hướng thứ sáu.
- Chỉ mặt tối. Dưới 720px thì một cột.
- Các câu khóa ở mục Voice and Tone, gồm «Chưa có lộ trình cho email này.»
- Nút trên Bản đồ nhu cầu ghi «Thử một kỹ năng cho thành phố này» và mở Học gì tiếp?.
