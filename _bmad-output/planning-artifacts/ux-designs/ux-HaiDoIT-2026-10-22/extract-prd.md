# Trích UX từ PRD — Hải Đồ IT

Digest này chỉ lấy những gì `prd.md` và `addendum.md` đã viết cho hai xương sống DESIGN.md và EXPERIENCE.md. Không thêm đề xuất. Chỗ hai nguồn lệch chữ được kể cạnh nhau, không được gộp thành một quyết định.

## Nguồn và trạng thái

`prd.md` có tiêu đề Hải Đồ IT, `status: final`, tạo và cập nhật ngày 2026-10-22. `addendum.md` có tiêu đề Phụ lục PRD Hải Đồ IT, cùng trạng thái và cùng ngày. PRD dành cho Duy và hai người cùng làm, rồi cho các bước UX, kiến trúc và epic. Từ vựng nằm ở mục 4 của PRD. Chỗ suy ra khi viết PRD mang nhãn `[GIẢ ĐỊNH: ...]`, và mục 14 gom các giả định đó.

PRD đứng trên brief đã khép ngày 2026-10-22, phụ lục của brief, nghiên cứu thị trường cùng ngày, và prototype `prototype/Hải Đồ IT — Bản đồ tuyển dụng & Cố vấn đa agent.html`. Hành vi người dùng của phần v1 lấy từ prototype. Tên sản phẩm và những màn nằm ngoài v1 lấy từ brief. Công thức mẫu trong prototype không phải yêu cầu. Phần kỹ thuật, phương án đã loại, và tham số thuế nằm ở `addendum.md`.

Hải Đồ IT là web cho junior, fresher và người đang chuyển hướng trong ngành IT. Họ mở Bản đồ nhu cầu để thấy việc đang tuyển ở thành phố của mình, vào Học gì tiếp? để thử thêm một kỹ năng và thấy số tin cùng lương công khai đổi ra sao, rồi nhận Lộ trình 90 ngày. Mỗi nhận định trên lộ trình có nút Vì sao? trỏ về nguồn. Người dùng quyết định học gì trước khi bỏ tiền và thời gian. Trên web của hai tháng này không có khoản thu. Việc còn hình dạng tiền là một trường hoặc bootcamp nói đồng ý thử. Đó là một lời nói, không phải một màn. Ứng viên không trả tiền. Sản phẩm có hai tháng để ra mắt, ba người, chỉ web.

Khoảng trống PRD nói cần giữ khi viết là: một người ở Việt Nam thử thêm một kỹ năng, thấy số tin và lương công khai đổi theo thành phố và cấp bậc, rồi nhận lộ trình khoảng 90 ngày có Vì sao? trỏ về nguồn. Nếu người dùng không thấy dữ liệu thật hơn lời khuyên chung, phần Học gì tiếp? và Lộ trình 90 ngày mất lý do tồn tại.

## Bề mặt và hình thức

v1 là web. Mục 6 ghi không có ứng dụng di động cài trên máy, và web mở trên trình duyệt điện thoại là giả định ở mục 9. Mục 9 ghi nguyên câu `[GIẢ ĐỊNH: web dùng được trên trình duyệt điện thoại, vì UJ-1 bắt đầu trên điện thoại. Không làm ứng dụng cài máy.]` Mục 14 nhắc lại giả định rằng web dùng được trên trình duyệt điện thoại. NFR-5 ghi giao diện chữ Việt, và web dùng được ở bề rộng trình duyệt điện thoại và ở bề rộng máy bàn. NFR-6 ghi một lộ trình đã lưu mở lại được từ liên kết mở lại trên máy khác với máy đã tạo.

UJ-1 bắt đầu khi mở web trên điện thoại, chưa có email nào được lưu. UJ-2 xảy ra ngày thứ mười, trên máy khác. Ba người làm trong hai tháng. Người dùng chính và người dùng phụ dùng cùng một web. Không có cổng riêng, và không có cổng riêng cho trường hoặc bootcamp trong v1. Trường và bootcamp trong v1 xem chương trình của họ có khớp thị trường hay không trên cùng web với ứng viên. Gói riêng cho trường nằm ngoài v1.

Trên web của hai tháng này, tiền là không. Không có giá, gói, hay chỗ trả tiền của ứng viên trong v1.

## Kiến trúc thông tin

Mục 9 ghi điều hướng của v1 có năm chỗ, theo thứ tự chữ trong câu đó: Bản đồ nhu cầu, Học gì tiếp?, Lộ trình 90 ngày, So sánh offer, Soi tin. Bản đồ nhu cầu là chỗ mở vào. Xu hướng và hạn dùng kỹ năng không có mục riêng trên điều hướng.

Mục 8 và phụ lục cùng nói «Sáu chỗ» còn ở lại trên web. Mục 8 kể tiếp Bản đồ nhu cầu là mặt tiền, Học gì tiếp? và Lộ trình 90 ngày là phần lương công khai theo thành phố ở Việt Nam cùng lộ trình có nguồn, Soi tin và So sánh offer dùng được khi chưa lưu. Hai cách đếm, năm chỗ điều hướng và sáu chỗ còn ở lại, đứng cạnh nhau trong nguồn. Digest không chọn chỗ thứ sáu là mục nào.

Prototype có 11 màn. Phụ lục ghi PRD lấy hành vi của Bản đồ nhu cầu, của phần thử kỹ năng (đổi tên thành Học gì tiếp?), của khối lộ trình 90 ngày, của So sánh offer kèm kiểm tra BHXH, và của phần cảnh báo tin treo, tin trùng, lương bất thường trong Soi tin.

Các bề mặt có trong v1:

- Bản đồ nhu cầu là mặt tiền. Bảy thành phố là Hà Nội, Hải Phòng, Đà Nẵng, Quy Nhơn, Nha Trang, TP. Hồ Chí Minh, Cần Thơ. Toàn quốc là phạm vi nới của Học gì tiếp? khi ô một thành phố dưới ngưỡng 30 tin. Toàn quốc không phải thành phố thứ tám trên Bản đồ nhu cầu.
- Học gì tiếp? là chỗ thử kỹ năng giả định. Nhãn «Mô phỏng Nếu–thì» của prototype không dùng.
- Lộ trình 90 ngày là kế hoạch ba chặng sinh ra từ lựa chọn ở Học gì tiếp?. Ô email đứng lúc lộ trình hiện ra. Phụ lục ghi không kéo ô email lên Bản đồ nhu cầu, và không đổi thành mật khẩu.
- So sánh offer là công cụ nhập hai offer. Kiểm tra BHXH là phần của So sánh offer và nằm trên cùng màn.
- Soi tin là công cụ bản nhẹ. Người dùng đưa một link.
- Xu hướng và hạn dùng kỹ năng là lớp dữ liệu dùng chung cho Học gì tiếp? và cho lộ trình. Lớp này cho biết nhu cầu một kỹ năng đang tăng hay giảm. Không có màn riêng trong v1, và không có đường dẫn điều hướng tới một màn «Lương và hạn dùng». Lối «kỹ năng còn hạn bao lâu» của prototype không thành màn v1.

UJ-3 vào thẳng Soi tin và không có ô email. UJ-4 vào thẳng So sánh offer và không có ô email. Bản đồ nhu cầu và Học gì tiếp? dùng được trước khi có email.

Nguồn loại khỏi v1, nên không có màn và không có mục điều hướng cho các việc này: ghép người dùng với tin đang mở và gợi ý tin vừa mở khóa; đánh giá nhà tuyển dụng, chỉ số phản hồi, và thu trải nghiệm ứng tuyển; đọc hợp đồng và tư vấn pháp lý; lộ trình của những người giống người dùng; màn Remote hoặc Nhật và chuyên mục nội dung đó trong hai tháng này; review dự án, hộ chiếu kỹ năng, và chỗ nộp repo; phòng tập thương lượng và lương theo phân vị; ứng dụng di động cài trên máy; cổng riêng cho trường hoặc bootcamp; mật khẩu, đăng nhập mạng xã hội, và hồ sơ công khai; giá, gói, và chỗ trả tiền của ứng viên; liên kết hoa hồng, nhãn hoa hồng, và số đếm lượt mở liên kết đó; Cố vấn đa agent như một bước trên màn hình; «Lộ trình thật của người giống bạn»; nhảy việc và agent pháp lý. Tên file prototype vẫn có cụm «Cố vấn đa agent». Phụ lục ghi cụm đó không được đưa vào yêu cầu như một bước trên màn hình. SM-3, việc một trường hoặc bootcamp nói đồng ý thử, không có màn hình. Web của hai tháng này không có chỗ bấm sang một khóa học. Soi tin không có nút theo dõi tin và không có nút báo cáo cộng đồng.

v2, ghi để biết chưa có bề mặt trong v1, gồm review dự án, phòng tập thương lượng, và lương theo phân vị. Thêm thành phố ngoài bảy thành phố, và ghép việc chỉ khi có giấy phép, nằm sau v1. Liên kết hoa hồng nằm ngoài hai tháng này.

## Hành vi từng màn

Hồ sơ là thành phố, cấp bậc, vai trò mục tiêu, và các kỹ năng đã có của một người. Hồ sơ sống trên máy cho đến khi lộ trình được lưu, rồi sống cùng email đó. Hồ sơ phiên là hồ sơ đang dùng trong lần mở web này. Trước khi lưu, hồ sơ phiên chỉ ở trên máy. Cấp bậc trong từ vựng là Fresher hoặc Junior. Dấu trên Bản đồ nhu cầu chỉ rơi vào kỹ năng đã có. Kỹ năng giả định là kỹ năng người dùng thêm trong Học gì tiếp? để xem số tin và lương công khai đổi, trước khi học thật.

### Bản đồ nhu cầu

Màn này thực hiện UJ-1, và dấu kỹ năng đã có còn khớp ở UJ-2. PRD mô tả mặt tiền đúng cách dùng của prototype ngày 2026-10-22 cho riêng màn này: bảy thành phố, nhu cầu hôm nay, dự báo 18 tháng, thẻ thành phố với cơ cấu, lương và tín hiệu sớm, dấu kỹ năng đã có. Lần đầu không có hồ sơ mẫu. `[GIẢ ĐỊNH: bộ lọc vai trò mặc định là "Tất cả", không mặc định Data/AI.]` Bộ lọc vai trò của v1 là Tất cả, Backend, Frontend, Data/AI, DevOps/Cloud, Mobile, Bảo mật. Hình khối 3D của prototype là cách trình bày cho UX, không phải yêu cầu của PRD. Phụ lục ghi bản đồ 3D là tài liệu tham chiếu cho UX, và PRD yêu cầu các việc người dùng làm được, không yêu cầu công nghệ vẽ.

FR-1: người dùng xem được số tin đang mở tại từng thành phố trong bảy thành phố, theo bộ lọc vai trò đang chọn. Đủ bảy thành phố có mặt kể cả khi một thành phố có ít tin. Đổi bộ lọc vai trò thì số tin của thành phố đổi theo vai trò đó. Mỗi lần xem có ngày của lần làm mới dữ liệu gần nhất. Khi chưa có kỹ năng đã có, không có dấu «đã có».

FR-2: người dùng chuyển tầm nhìn sang mốc 6, 12 hoặc 18 tháng và thấy số tin dự báo của thành phố đang xem. Mỗi mốc hiện một khoảng, có nhãn là dự báo, không hiện một số như thể đã xảy ra. Vì sao? của khoảng đó trỏ tới số tin đang dùng để tính. Không dùng hệ số minh họa cố định của prototype. Khi tầm nhìn vẫn là hôm nay, chỗ dự báo của thành phố vẫn hiện khoảng mốc 12 tháng, có nhãn là dự báo. Mốc «nay» hiện số tin đang mở, không hiện khoảng dự báo ở vị trí của số hiện tại. Dự báo nói về số tin. v1 không dự báo lương.

FR-3: người dùng chọn một thành phố và thấy cơ cấu vai trò, lương công khai hoặc trạng thái ẩn, và tín hiệu sớm hoặc câu chưa ghi nhận tín hiệu. Thẻ thành phố có cơ cấu vai trò của thành phố đó. Cơ cấu vai trò là tỷ lệ số tin của từng vai trò trong thành phố, cộng một nhóm còn lại. Các tỷ lệ cộng đủ 100%. Khi đã chọn thành phố, lương trên thẻ và ô lương đầu trang cùng lấy một ô mẫu. Bộ lọc một vai trò thì ô đó là vai trò đang lọc, thành phố đang chọn, và cấp bậc của hồ sơ phiên. Bộ lọc Tất cả thì vai trò của ô là vai trò có nhiều tin nhất tại thành phố đó. Chưa chọn thành phố thì ô lương đầu trang không hiện số. Khi ô mẫu đủ ngưỡng 30 tin, thẻ và ô đầu trang hiện một lương công khai. Dưới ngưỡng thì không hiện số, và có câu chưa đủ mẫu. Thành phố vẫn xem được khi lương đang ẩn. Thẻ hiện đúng một tín hiệu sớm kèm Vì sao?, hoặc hiện câu chưa ghi nhận tín hiệu đáng kể cho thành phố này. Khi chưa có quy tắc phát hiện, thẻ hiện câu chưa ghi nhận. Việc xây thẻ không chờ quy tắc đó.

FR-4: khi hồ sơ phiên đang có kỹ năng đã có, kỹ năng đó được đánh dấu trên danh kỹ năng của thành phố. Kỹ năng nằm trong kỹ năng đã có thì có dấu. Kỹ năng không nằm trong đó thì không có dấu. Xóa một kỹ năng đã có thì dấu mất trong cùng phiên. Sau UJ-2, dấu khớp với hồ sơ đã lưu, không khớp với máy trống.

NFR-3: khi nguồn dữ liệu lỗi, Bản đồ nhu cầu nói không tải được và giữ số của lần xem gần nhất nếu máy đang có số đó. Có lối thử lại. NFR-4: khi bộ lọc không còn tin, Bản đồ nhu cầu nói không có tin khớp và có lối bỏ lọc về Tất cả.

### Học gì tiếp?

Màn này thực hiện UJ-1. Người dùng thêm hoặc bớt kỹ năng giả định trên hồ sơ phiên và thấy ba thứ đổi: số tin đủ điều kiện, lương công khai, thời gian học. Danh nên học tiếp xếp theo số tin mở thêm trên mỗi tuần học. Tên trên sản phẩm là Học gì tiếp?.

FR-5: người dùng thêm hoặc bỏ kỹ năng giả định và thấy số tin trước và sau, thời gian học, và lương công khai trước và sau hoặc trạng thái ẩn. Số tin là số tin đủ điều kiện. Tin đủ điều kiện là tin đang mở trong phạm vi đang tính, đúng vai trò mục tiêu và đúng cấp bậc, và có đủ mọi kỹ năng đã có cùng mọi kỹ năng giả định đang chọn. Thời gian học là tổng số tuần của các kỹ năng giả định đang chọn. Chưa thêm kỹ năng giả định thì không có chênh lệch, và thời gian học là trạng thái chưa có kỹ năng giả định. Mỗi dòng trong danh nên học tiếp hiện số tin tăng, số tuần, và số tin trên mỗi tuần. Bỏ hết kỹ năng giả định thì các số trở về trạng thái trước. `[GIẢ ĐỊNH: danh kỹ năng để chọn là danh cố định do nhóm giữ, cùng taxonomy mà pipeline đã trích. Người dùng không gõ một kỹ năng tự do ngoài danh.]` `[GIẢ ĐỊNH: Học gì tiếp? chỉ dựng kịch bản cho cấp Fresher và Junior.]`

FR-6: hệ thống xếp các kỹ năng còn lại trong danh theo số tin mở thêm trên mỗi tuần học, và người dùng thêm được một kỹ năng từ danh đó vào kỹ năng giả định. Thứ hạng cao hơn là số tin tăng thêm chia cho số tuần học lớn hơn. `[GIẢ ĐỊNH: số tuần học của mỗi kỹ năng là số do nhóm gán trong danh, không phải số suy ra tự động từ tin tuyển.]` Phụ lục ghi số tuần học của từng kỹ năng do nhóm gán trong danh kỹ năng cố định, và danh đó đi cùng taxonomy pipeline đang trích. Kỹ năng đã nằm trong kỹ năng đã có hoặc trong kỹ năng giả định thì không còn trong danh nên học tiếp.

FR-7: khi ô vai trò × thành phố × cấp bậc dưới ngưỡng 30 tin, Học gì tiếp? nới theo thứ tự đã viết: trước hết toàn quốc, cùng vai trò và cùng cấp bậc; nếu ô đó vẫn dưới ngưỡng thì nới sang nhóm vai gần. Không hiện lương công khai lấy từ ô mỏng. Vì sao? của kết quả đã nới nói ô gốc dưới ngưỡng 30 tin và nói đang đứng ở bước toàn quốc hay bước nhóm vai gần. Nếu phạm vi đã nới vẫn dưới ngưỡng 30 tin, lương công khai tiếp tục ẩn và có câu chưa đủ mẫu. `[GIẢ ĐỊNH: một số ô Data/AI theo thành phố sẽ dưới ngưỡng 30 tin. Đo trong tuần 1. Trước khi đo, đây chưa phải sự thật.]` `[GIẢ ĐỊNH: Data/AI đứng riêng; Backend với Frontend; DevOps/Cloud với Bảo mật; Mobile đứng riêng.]` Mục 14 ghi thứ tự nới là toàn quốc rồi nhóm này.

FR-8: số «trước» tính từ thành phố, cấp bậc, vai trò mục tiêu và kỹ năng đã có của hồ sơ phiên. Đổi thành phố hoặc cấp bậc trong hồ sơ phiên thì số trước đổi. Thêm một kỹ năng đã có thì độ phủ trước tăng và kỹ năng đó không bị gợi ý như thể chưa có. Độ phủ, với một vai trò, là số kỹ năng yêu cầu của vai đó đang nằm trong kỹ năng đã có, chia cho số kỹ năng yêu cầu của vai đó. Danh kỹ năng yêu cầu đi cùng danh kỹ năng cố định. Chưa chọn thành phố, cấp bậc và vai trò mục tiêu thì Học gì tiếp? hỏi các mục đó trước khi hiện chênh lệch.

### Lộ trình 90 ngày

Màn này thực hiện UJ-1 và UJ-2. Lựa chọn đang có ở Học gì tiếp? trở thành lộ trình ba chặng. Mỗi chặng có một dự án thực hành. Mọi nhận định có Vì sao?. Người dùng lưu bằng một email và nhận liên kết mở lại. Màn không có bước chạy nhiều agent. Nhận định là một câu trên lộ trình nói nên học gì, nên bỏ gì, hoặc vì sao một hướng bị loại. Phụ lục ghi lộ trình bản đầu được tính từ dữ liệu rồi mới viết câu, và cơ chế đó, gồm việc có dùng mô hình ngôn ngữ hay không, thuộc kiến trúc. PRD chỉ yêu cầu ba chặng, một dự án mỗi chặng, và Vì sao? trên mọi nhận định.

FR-9: người dùng tạo lộ trình từ hồ sơ phiên và các kỹ năng giả định đang chọn. Lộ trình có ba chặng, ngày 1–30, 31–60 và 61–90. Mỗi chặng có một dự án thực hành. Không tạo được lộ trình khi Học gì tiếp? chưa có thành phố, cấp bậc và vai trò mục tiêu. Đủ ba chặng. Mỗi chặng có các kỹ năng của chặng đó, tên một dự án thực hành, và một câu nói người học làm ra cái gì. Kỹ năng trên lộ trình nằm trong kỹ năng giả định đang chọn, hoặc là kỹ năng đã có được chặng đào sâu khi không còn kỹ năng giả định. Đổi kỹ năng giả định rồi tạo lại thì nội dung chặng đổi theo lựa chọn mới.

FR-10: mỗi nhận định trên lộ trình có Vì sao? trỏ tới nguồn đúng với câu đó, kể cả nhận định bị loại vì thiếu dữ liệu. Đếm nhận định trên một lộ trình đã tạo thì mỗi nhận định có đúng một Vì sao? mở được. Vì sao? của một nhận định dựa trên tin trỏ tới tập tin đã trích hoặc tới link gốc, không trỏ tới nguyên văn mô tả công việc. Vì sao? của một nhận định dựa trên báo cáo gọi tên báo cáo. Nhận định bị loại vì dưới ngưỡng 30 tin vẫn có Vì sao?, và câu đó nói thiếu dữ liệu chứ không nói một mức lương. Lộ trình đã lưu mà còn nhận định thiếu Vì sao? thì không đạt SM-4. Lộ trình đó vẫn tính vào SM-1. SM-4 lấy ngưỡng đi tiếp 100%. Phụ lục ghi mốc đi tiếp về nguồn vẫn là 100% và không hạ xuống 95%.

FR-11: hai tháng này không xây liên kết khóa, không xây nhãn hoa hồng giới thiệu khóa học, và không đếm lượt mở liên kết đó. Một chặng không có liên kết khóa vẫn đủ để tạo và lưu lộ trình. Lộ trình tạo và lưu được khi mọi chặng đều không có liên kết khóa. Web của hai tháng này không có chỗ bấm sang một khóa học. Không có số đếm lượt mở liên kết khóa. Khoản này không được gọi là tiền của kỳ này. Phụ lục ghi hoa hồng bị cắt khỏi tiền của kỳ này vì chưa có nhà cung cấp khóa, và lộ trình vẫn tạo và vẫn lưu khi chặng không có liên kết khóa.

FR-12: người dùng lưu lộ trình bằng một email. Hệ thống lưu hồ sơ và lộ trình với email đó, rồi gửi liên kết mở lại. Không có mật khẩu. Gửi email hợp lệ thì hồ sơ và lộ trình được lưu, và người dùng nhận được liên kết mở lại. Gửi email thất bại thì lộ trình vẫn ở trên máy trong phiên đó, và chưa được tính là tạo xong. Không có trang hồ sơ công khai. Email không hiện cho người khác. Email chỉ dùng để lưu và mở lại lộ trình.

FR-13: người có email đã lưu mở lại được đúng hồ sơ và lộ trình đó bằng liên kết mở lại, hoặc bằng cách nhập lại email để nhận liên kết mới. Mở liên kết thì thành phố, cấp bậc, vai trò mục tiêu, kỹ năng đã có và ba chặng khớp lần lưu. Cùng email, mở lại trong 14 ngày kể từ lúc lưu, được tính là một lần mở lại cho SM-2. Sau ngày 14, liên kết mở lại vẫn mở đúng lộ trình. Cửa sổ 14 ngày chỉ dùng để đo SM-2. So sánh offer và Soi tin không đòi email. `[GIẢ ĐỊNH: một email một lộ trình. Lưu lần nữa thì thay lộ trình trước và mốc 14 ngày tính từ lần lưu mới.]` UJ-2 ghi một câu giả định khác chữ: `[GIẢ ĐỊNH: một email giữ một lộ trình. Tạo lộ trình mới thì thay lộ trình cũ và cửa sổ 14 ngày tính lại từ lần lưu mới.]` Phụ lục ghi giả định đang để Duy sửa: một email giữ một lộ trình; lưu lần mới thì thay lộ trình cũ và tính lại 14 ngày. Ba câu đứng cạnh nhau trong nguồn.

Phụ lục ghi cách lưu đã được đồng ý ngày 2026-10-22: xem Bản đồ nhu cầu và Học gì tiếp? trước khi có email; hồ sơ nằm trên máy đến lúc tạo lộ trình; lúc lưu, một email và một liên kết mở lại, không mật khẩu; mở lại trong 14 ngày là cùng email mở đúng lộ trình đó. Nguồn không chọn tài khoản có mật khẩu, vì hai tháng và ba người không đủ để làm đăng nhập thành sản phẩm. Nguồn không chọn chỉ lưu trên một trình duyệt, vì mốc đi tiếp là mở lại trong 14 ngày, thường trên máy khác.

### Xu hướng và hạn dùng kỹ năng

FR-14: khi lớp dữ liệu nói nhu cầu một kỹ năng đang giảm, Học gì tiếp? và lộ trình không trình bày kỹ năng đó như thể nhu cầu đứng yên. Vì sao? trích lớp này khi nhận định dùng nó. Kỹ năng mà lớp dữ liệu đánh dấu là đang giảm không đứng hạng nhất trong danh nên học tiếp. Vì sao? của kỹ năng đó nói mức giảm. v1 không xin người dùng đóng góp mức lương của chính họ.

### So sánh offer

Màn này thực hiện UJ-4. Miễn phí, dùng được khi chưa lưu. Người dùng nhập hai offer và thấy thực nhận cả năm, kèm kiểm tra BHXH. Phòng tập thương lượng không có trong v1. Kết quả là ước tính, không phải tư vấn thuế. Ngoài phạm vi của màn: không có phòng tập thương lượng, không có thang phân vị bên cạnh offer. Đóng trình duyệt thì không còn gì trên máy chủ.

FR-15: mỗi offer có tên công ty, lương tháng, loại gross hoặc net, số người phụ thuộc, số tháng thưởng, phụ cấp, số ngày remote mỗi tuần, căn cứ đóng bảo hiểm (trên lương thật hoặc trên mức thấp hơn), và mức đóng khi chọn mức thấp hơn. Số ngày remote hiện cùng offer và không đổi thực nhận cả năm. Khi offer là gross và căn cứ là lương thật, mức đóng bằng lương gross. Khi offer là net, mức đóng mặc định bằng gross đã dò ngược, trừ khi người dùng nhập mức khác. Kết quả gọi tên công ty, nói offer nào cao hơn và chênh bao nhiêu mỗi năm, hoặc nói hai offer gần ngang nhau khi chênh dưới 1% thực nhận cả năm. Mỗi offer hiện thực nhận cả năm, net mỗi tháng, thuế mỗi tháng, và thanh thực nhận, bảo hiểm, thuế. Đổi một ô nhập thì thực nhận cả năm tính lại. Trên màn có căn cứ thuế và bảo hiểm đang dùng để tính, và có câu kết quả là ước tính, không thay thế tư vấn thuế. Mục 14 xếp câu «hai offer được gọi là gần ngang nhau khi chênh dưới 1% thực nhận cả năm» vào mục lục giả định, trong khi FR-15 viết câu đó như hệ quả kiểm được. Digest không gộp hai cách ghi.

FR-16: khi một offer đóng bảo hiểm trên mức thấp hơn lương gross đang dùng để tính, So sánh offer hiện khoản hụt cả năm và nói các chế độ sẽ tính trên mức thấp đó. Offer đóng trên lương thật thì không có câu hụt. Offer đóng trên mức thấp hơn thì có khoản hụt cả năm, gồm phần người lao động và phần công ty ở mức ước tính. Mức đóng không vượt quá lương gross của offer đó.

Phụ lục ghi kỳ tính đang gắn trên prototype, để hiện trong căn cứ trên màn và để tính bản đầu, và được thay khi quy định đổi. Các số đó là: giảm trừ bản thân 15,5 triệu đồng mỗi tháng; người phụ thuộc 6,2 triệu đồng mỗi tháng; biểu thuế năm bậc gồm 5% đến 10 triệu, 10% đến 30 triệu, 20% đến 60 triệu, 30% đến 100 triệu, 35% trên phần còn lại; người lao động 10,5% (BHXH 8%, BHYT 1,5%, BHTN 1%); trần BHXH và BHYT 50,6 triệu từ 01/07/2026; trần BHTN 106,2 triệu cho vùng I; phần công ty khoảng 21,5%. Phụ lục nhắc lại số ngày remote hiện cùng offer và không đổi thực nhận cả năm. Kết quả trên màn luôn là ước tính, không phải tư vấn thuế. Mục 10 ghi thực nhận cả năm và dự báo 18 tháng đều có nhãn là ước tính hoặc dự báo, và tham số thuế cùng trần bảo hiểm đang dùng hiện trên màn So sánh offer.

### Soi tin

Màn này thực hiện UJ-3. Bản nhẹ, miễn phí, dùng được khi chưa lưu. Người dùng đưa một link. Sản phẩm báo tin treo, tin trùng và lương bất thường khi dữ liệu đã có cho phép. Không chấm điểm lừa đảo, không tách đầu việc theo AI, không tra mã số thuế. Đóng trình duyệt thì không còn gì trên máy chủ. Khi dữ liệu không đủ, Soi tin không xin nguyên văn mô tả công việc.

FR-17: người dùng dán một link gốc đang có trong dữ liệu và thấy số lần làm mới, ngày thấy đầu và ngày thấy gần nhất, tin trùng nếu có, và kết luận về lương. Ba số lần làm mới, ngày thấy đầu và ngày thấy gần nhất kiểm được mà không cần kết luận tin treo. `[GIẢ ĐỊNH: ngưỡng tạm của tin treo là làm mới từ lần thứ hai, hoặc vẫn đang mở sau 30 ngày kể từ ngày thấy đầu. Tuần 1 đo xem ngưỡng có nhận nhầm tin lành hay không. Trước khi đo, không viết test coi ngưỡng này là đúng.]` Mục 4 ghi ngưỡng tạm ở FR-17 là giả định, chưa phải sự thật, và trước khi tuần 1 đo thì không viết test như thể ngưỡng đó đã đúng. Mục 14 ghi trước tuần 1, test chỉ kiểm số lần làm mới và hai ngày, không kiểm nhãn tin treo như thể ngưỡng đã đúng. Có tin trùng thì liệt kê là có tin đang mở khác trùng kỹ năng, thành phố, cấp bậc và khoảng lương. Câu cảnh báo không cần tên công ty. Tin trùng là tin đang mở khác, khác link, trùng kỹ năng, thành phố, cấp bậc và khoảng lương với tin đang soi. Khi ô mẫu của tin đủ ngưỡng 30 tin và lương công khai không nằm trong khoảng lương ghi trên tin, hiện lương bất thường. Khi ô mẫu dưới ngưỡng 30 tin, không kết luận lương bất thường. Hiện câu chưa đủ mẫu để xét lương. Lương bất thường là lương công khai của ô mẫu không nằm trong khoảng lương ghi trên tin; khi ô đó đang ẩn lương, không kết luận lương bất thường. Không hiện điểm trên 100, không hiện nhãn đáng tin hoặc rủi ro cao, không hiện chỉ số AI.

FR-18: khi link không có trong dữ liệu, Soi tin nói chưa soi được tin này. Không có ô dán nguyên văn mô tả công việc. Nội dung người dùng dán không được lưu. Không có nút theo dõi tin và không có nút báo cáo cộng đồng trong v1.

Lần làm mới của tin là số lần cùng một tin được thấy lại. Cách gọi này khác với ngày làm mới dữ liệu của cả Bản đồ nhu cầu.

### Quy tắc hiển số dùng chung

Ngưỡng 30 tin nghĩa là dưới 30 tin trong ô mẫu thì mọi số lương công khai đều ẩn. Ngưỡng này không phải mốc 30 người tạo lộ trình. Ô mẫu là một nhóm tin dùng để quyết định có hiện lương công khai hay không, cắt theo vai trò, thành phố và cấp bậc. Khi Học gì tiếp? nới phạm vi, ô mẫu là phạm vi đã nới. Lương công khai là một số lương của ô mẫu khi ô đó đủ ngưỡng 30 tin. v1 không hiện dải phân vị.

NFR-1: mọi số lương công khai trên mọi màn đều vắng mặt khi ô mẫu dưới ngưỡng 30 tin. Gồm ô lương trên đầu Bản đồ nhu cầu, thẻ thành phố, Học gì tiếp?, và kết luận lương của Soi tin. SM-C1 đếm số lương công khai đang hiện, và số đó không được tăng bằng cách hạ ngưỡng 30 tin.

Phụ lục ghi xung đột với prototype đã được xử lý khi viết PRD, và digest chỉ thuật lại cách nguồn đã ghi. Ô «LƯƠNG TV» trên prototype luôn hiện số; PRD áp ngưỡng 30 tin cho mọi lương công khai, kể cả ô đó. Prototype vẽ P25 và P75 khi đủ mẫu; lương theo phân vị là v2; v1 chỉ một lương công khai. Công thức nhân hệ số, lương gốc 10, 16, 28, 45 triệu, và các điểm viết sẵn trong prototype là dữ liệu minh họa, không thành yêu cầu. Cách gộp nhiều khoảng lương thành một lương công khai, cách tính dự báo 18 tháng, và cách phát hiện tín hiệu sớm để kiến trúc hoặc tuần 1 chốt. PRD chỉ khóa điều người dùng thấy: một số khi đủ 30 tin, một khoảng có nhãn dự báo, một tín hiệu hoặc câu chưa ghi nhận.

Mục 4 ghi tín hiệu sớm là câu nói một thành phố đang có việc mới vì một sự kiện nào đó, hiện trên thẻ thành phố. Chưa có cách phát hiện. Khi chưa có quy tắc, thẻ hiện «chưa ghi nhận tín hiệu». Phụ lục gọi tín hiệu sớm là câu «thành phố này đang có việc mới vì một sự kiện nào đó», và ghi thẻ thành phố xây với câu chưa ghi nhận. FR-3 còn dùng cụm «câu chưa ghi nhận tín hiệu đáng kể cho thành phố này» và «câu chưa ghi nhận». Mục 12 dùng «câu chưa ghi nhận tín hiệu đáng kể». Các cụm này đứng trong nguồn cho cùng một trạng thái chưa có quy tắc. Digest không chọn một chuỗi làm câu chữ duy nhất.

Mục 4 ghi khi chưa chọn cấp, ô lương trên thẻ thành phố dùng Junior. FR-3 ghi chưa chọn cấp thì dùng Junior. Mục 14 xếp câu «chưa chọn cấp bậc thì ô lương trên thẻ dùng Junior» vào mục lục giả định. Digest không gộp định nghĩa ở mục 4 với nhãn giả định ở mục 14.

Tin đang mở được làm mới hằng ngày, vì một tin chỉ sống khoảng một tháng. Bản đồ nhu cầu hiện ngày của lần làm mới gần nhất. Nguồn tin lệch về ITviec và về TP. Hồ Chí Minh. Phụ lục ghi khoảng 832 tin đang mở tại một thời điểm, trong một lần kiểm kê: ITviec 652, TopDev 99, ATS 78, Cốc Cốc 3. Đây là ảnh của một lúc, không phải quy mô đảm bảo của sản phẩm. VietJobs chỉ là nền lịch sử và được ghi công, không phải tin đang mở. Các số ITviec về tin AI/ML tăng 41% và lượt tìm «AI» tăng 89% là quý 1/2025. PRD ghi đọc lại trước khi đưa chúng lên sản phẩm.

Mỗi tin chỉ giữ kỹ năng, thành phố, cấp bậc, khoảng lương, ngày đăng và link gốc. Không lưu và không hiện nguyên văn mô tả công việc. Nguồn, theo mục 4, là một tập tin đã trích (kỹ năng, thành phố, cấp bậc, khoảng lương, ngày đăng, link gốc) hoặc một báo cáo công khai được gọi tên (ITviec, TopDev, TopCV, JobOKO).

## Hành trình có tên nhân vật

PRD giữ nguyên câu này ở mục 3.4: `[GIẢ ĐỊNH: Lan, Khoa và Mai là tên tạm, để hành trình có người cụ thể. Ba cảnh không phải bằng chứng, và không chứng minh một người thật sẽ quay lại. Không có buổi ngồi với người thật nào trong bản này để kể.]` Cùng mục ghi Khoa dán một link, xem xong, đóng trang, không lưu. Mai nhập hai offer, xem xong, đóng trang, không lưu. Lan tạo lộ trình, để lại email, rồi mở lại đúng lộ trình trong 14 ngày, vì SM-1 và SM-2 cần một cảnh để đo. Trong bản không có cảnh Lan suýt trả tiền cho một khóa. Không thêm cảnh đó. Mục 14 nhắc lại: Lan, Khoa, Mai là tên tạm gắn nhãn giả định; không phải bằng chứng; cảnh mở lại không chứng minh một người thật sẽ quay lại; không thêm cảnh suýt trả tiền cho một khóa. Phụ lục ghi Duy chọn, trong phòng ngày 2026-10-22: không kể một buổi người dùng thật; Lan, Khoa, Mai ở lại làm người của cảnh và giữ nhãn bản dựng; không thêm cảnh suýt trả tiền cho một khóa.

Việc người dùng cần xong, trước các cảnh, là năm việc. Biết kỹ năng nào đang được tuyển ở thành phố mình, hôm nay và trong dự báo 18 tháng, trước khi chọn hướng học. Thử một kỹ năng giả định và thấy số tin cùng lương công khai đổi, kể cả khi ô mẫu chưa đủ ngưỡng 30 tin và sản phẩm phải nói thẳng là chưa đủ. Có lộ trình 90 ngày với dự án thực hành, và mở lại được lộ trình đó trong 14 ngày. Trước khi nộp hồ sơ, biết một tin đang theo dõi có bị làm mới nhiều lần, có tin trùng, hoặc có lương bất thường hay không. Khi cầm hai offer, biết bên nào có thực nhận cả năm cao hơn, và bên nào đóng bảo hiểm thấp hơn lương ghi trên offer. Với người dùng chính, kết quả đời sống là có việc hoặc lên lương sau 3–6 tháng. Hai tháng ra mắt không đo kết quả đó.

Người dùng chính là junior (khoảng 0–2 năm) và fresher muốn chuyển hướng, nhất là sang Data/AI hoặc DevOps/Cloud. Người dùng phụ là sinh viên năm cuối ngành IT. Cùng một web. Không có cổng riêng. v1 không phục vụ nhà tuyển dụng cần đăng tin, sàng hồ sơ, hoặc được chấm điểm phản hồi; người cần được ghép với một tin đang mở; người cần đọc hợp đồng hoặc tư vấn pháp lý; người cần lương theo phân vị, phòng tập thương lượng, hoặc review dự án có trả phí; người tìm một thị trường Remote hoặc Nhật như một sản phẩm riêng.

**UJ-1. Lan tạo lộ trình 90 ngày lần đầu.** Lan, một năm làm PHP ở Hải Phòng, muốn sang Data/AI. Sợ học nhầm một khóa. Điểm vào: mở web trên điện thoại, chưa có email nào được lưu. Đường đi: xem Bản đồ nhu cầu tại Hải Phòng, đánh dấu Python và SQL là kỹ năng đã có, sang Học gì tiếp?, thêm một kỹ năng giả định, xem số tin và lương công khai (hoặc trạng thái ẩn), chọn một kỹ năng trong danh nên học tiếp, tạo lộ trình ba chặng, nhập email. Điểm giá trị: lộ trình hiện ra. Một nhận định có Vì sao? trỏ về nguồn. Một nhận định bị loại vì thiếu dữ liệu vẫn có Vì sao? giải thích vì sao bị loại. Kết: hồ sơ và lộ trình được lưu. Lan nhận liên kết mở lại. Hệ thống tính đây là một người đã tạo xong lộ trình. Khi ô mẫu mỏng, nguồn viết: Data/AI ở Hải Phòng dưới ngưỡng 30 tin; Học gì tiếp? nới toàn quốc trước, rồi nhóm vai gần nếu vẫn mỏng, và Vì sao? nói đang ở bước nào; lương công khai của ô mỏng không hiện số. Cảnh Hải Phòng trong UJ-1 là cảnh của hành trình. FR-7 vẫn gắn nhãn `[GIẢ ĐỊNH: một số ô Data/AI theo thành phố sẽ dưới ngưỡng 30 tin. Đo trong tuần 1. Trước khi đo, đây chưa phải sự thật.]` Digest không nâng cảnh đó thành số đã đo.

**UJ-2. Lan mở lại lộ trình trong 14 ngày.** Cùng Lan, ngày thứ mười, đang ở máy khác. Điểm vào: mở liên kết mở lại, hoặc nhập lại đúng email để nhận liên kết mới rồi mở lộ trình. Đường đi: thấy đúng lộ trình đã lưu. Trên Bản đồ nhu cầu, Python và SQL vẫn là kỹ năng đã có. Điểm giá trị: không phải chọn lại từ đầu. Kết: lần mở này được tính là mở lại trong 14 ngày, vì cùng email và còn trong cửa sổ tính từ lúc lưu. Cảnh này là chỗ đo SM-2. Nó không chứng minh một người thật sẽ quay lại. Khi tạo lại, nguồn gắn `[GIẢ ĐỊNH: một email giữ một lộ trình. Tạo lộ trình mới thì thay lộ trình cũ và cửa sổ 14 ngày tính lại từ lần lưu mới.]`

**UJ-3. Khoa soi tin rồi đóng trang.** Khoa, sinh viên năm cuối ở Cần Thơ, có một link tin. Điểm vào: vào thẳng Soi tin. Không có ô email. Đường đi: dán link. Nếu link đang có trong dữ liệu, thấy số lần làm mới của tin, tin trùng nếu có, và lương bất thường hoặc câu chưa đủ mẫu. Nếu link không có trong dữ liệu, thấy câu chưa soi được. Điểm giá trị: có câu trả lời về tin đang cầm, hoặc câu chưa soi được. Kết: không lưu. Đóng trình duyệt thì không còn gì trên máy chủ. Khi dữ liệu không đủ, Soi tin không xin nguyên văn mô tả công việc.

**UJ-4. Mai so sánh hai offer rồi đóng trang.** Mai, fresher ở Đà Nẵng, đang cầm hai offer. Một bên đóng bảo hiểm trên mức thấp hơn lương. Điểm vào: vào thẳng So sánh offer. Không có ô email. Đường đi: nhập hai offer, gồm căn cứ đóng bảo hiểm. Thấy bên nào có thực nhận cả năm cao hơn, và thấy khoản hụt nếu căn cứ đóng thấp hơn lương. Điểm giá trị: câu kết quả gọi tên công ty Mai đã nhập, và ghi đây là ước tính. Kết: không lưu. Đóng trình duyệt thì không còn gì trên máy chủ.

## Giọng văn và microcopy đã chốt

Mục 4 bắt dùng đúng các từ đã định nghĩa trong yêu cầu, hành trình và chỉ số. Tên sản phẩm và tên màn giữ nguyên: Bản đồ nhu cầu, Học gì tiếp?, Lộ trình 90 ngày, So sánh offer, Soi tin, Vì sao?, Kiểm tra BHXH. Nhãn «Mô phỏng Nếu–thì» không dùng. Không gắn nhãn «hoa hồng». Không gọi khoản hoa hồng của kỳ này là tiền của kỳ này.

Các câu hoặc cụm nguồn đã gọi tên cho trạng thái trên màn:

- Dấu kỹ năng dùng chữ «đã có». Khi chưa có kỹ năng đã có, không có dấu «đã có».
- Dự báo có nhãn là dự báo. Mốc hiện tại trong nguồn được gọi là «nay».
- Dưới ngưỡng lương, Bản đồ nhu cầu và Học gì tiếp? có câu chưa đủ mẫu. Soi tin, khi không kết luận lương bất thường, hiện câu chưa đủ mẫu để xét lương.
- Tín hiệu sớm, khi có, là câu nói một thành phố đang có việc mới vì một sự kiện nào đó. Phụ lục viết «thành phố này đang có việc mới vì một sự kiện nào đó». Trạng thái chưa có tín hiệu được nguồn gọi bằng nhiều cụm: «chưa ghi nhận tín hiệu», «câu chưa ghi nhận tín hiệu đáng kể cho thành phố này», «câu chưa ghi nhận», «câu chưa ghi nhận tín hiệu đáng kể».
- Học gì tiếp?, khi chưa thêm kỹ năng giả định, có trạng thái chưa có kỹ năng giả định, và không có chênh lệch.
- Vì sao? của kết quả đã nới nói ô gốc dưới ngưỡng 30 tin và nói đang đứng ở bước toàn quốc hay bước nhóm vai gần.
- Nhận định bị loại vì dưới ngưỡng 30 tin nói thiếu dữ liệu chứ không nói một mức lương. Vì sao? của kỹ năng đang giảm nói mức giảm.
- Soi tin, khi link không có trong dữ liệu, nói chưa soi được tin này. UJ-3 gọi đây là câu chưa soi được.
- Soi tin không hiện điểm trên 100, không hiện nhãn đáng tin hoặc rủi ro cao, không hiện chỉ số AI. Câu cảnh báo tin trùng không cần tên công ty.
- So sánh offer có câu kết quả là ước tính, không thay thế tư vấn thuế. Phụ lục ghi kết quả trên màn luôn là ước tính, không phải tư vấn thuế. UJ-4 ghi câu kết quả gọi tên công ty đã nhập, và ghi đây là ước tính. Cụm «hai offer gần ngang nhau» gắn với chênh dưới 1% thực nhận cả năm, và mục 14 xếp điều kiện 1% vào mục lục giả định.
- NFR-3 dùng chữ không tải được, kèm lối thử lại. NFR-4 dùng chữ không có tin khớp, kèm lối bỏ lọc về Tất cả.
- Bộ lọc có mục «Tất cả».

Nguồn còn khóa một thái độ của câu chữ: sản phẩm nói thẳng khi ô mẫu chưa đủ ngưỡng 30 tin; một khoảng dự báo không hiện như một số đã xảy ra; kỹ năng đang giảm không được trình bày như thể nhu cầu đứng yên. Câu chữ luật chạm Bản đồ nhu cầu và lương công khai, nhưng mục 12 không chốt một câu pháp lý để đặt lên màn, và các câu đó không chặn v1.

## Việc PRD cố ý để lại cho UX

Phụ lục ghi một câu: lớp chào «Đã hiểu», dải tám quý, và nút báo nguồn sai trên prototype là việc của UX. PRD không bắt buộc chúng. Nguồn không mô tả hành vi, câu chữ bên trong, hay vị trí của ba món này ngoài chính các tên đó.

PRD mục 5.1 ghi hình khối 3D của prototype là cách trình bày cho UX, không phải yêu cầu của PRD này. Phụ lục ghi bản đồ 3D là tài liệu tham chiếu cho UX. PRD yêu cầu các việc người dùng làm được, không yêu cầu công nghệ vẽ.

Các việc nguồn giao cho kiến trúc hoặc cho tuần 1, gồm cách gộp nhiều khoảng lương thành một lương công khai, cách tính dự báo 18 tháng, cách phát hiện tín hiệu sớm, và cơ chế viết câu lộ trình, không được phụ lục gọi là việc của UX. Chúng nằm ở mục câu hỏi mở bên dưới.

## Ràng buộc khả năng tiếp cận, mật độ, ngôn ngữ, chuyển động

NFR-5 là ràng buộc ngôn ngữ và bề rộng mà nguồn có nêu: giao diện chữ Việt; web dùng được ở bề rộng trình duyệt điện thoại và ở bề rộng máy bàn. Giả định điện thoại nằm ở mục 9 và được nhắc ở mục 14. Nguồn không nêu tỷ lệ tương phản, điều khiển bàn phím, trình đọc màn hình, chế độ giảm chuyển động, hay giao diện tối.

Nguồn không nêu quy tắc chuyển động. Hình khối 3D không phải yêu cầu. Phụ lục để công nghệ vẽ ngoài yêu cầu của PRD.

Mật độ và những gì được phép hiện, theo các yêu cầu đã khóa:

- Đủ bảy thành phố có mặt kể cả khi một thành phố có ít tin.
- Lương công khai là một số khi đủ 30 tin, hoặc vắng mặt khi dưới ngưỡng, kèm câu chưa đủ mẫu. v1 không hiện dải phân vị.
- Dự báo là một khoảng có nhãn, ở các mốc 6, 12 và 18 tháng. Khi tầm nhìn là hôm nay, chỗ dự báo của thành phố vẫn hiện khoảng mốc 12 tháng. v1 không dự báo lương.
- Thẻ thành phố hiện đúng một tín hiệu sớm kèm Vì sao?, hoặc câu chưa ghi nhận. Thành phố vẫn xem được khi lương đang ẩn.
- Cơ cấu vai trò cộng một nhóm còn lại, và các tỷ lệ cộng đủ 100%.
- Lộ trình có đúng ba chặng, ngày 1–30, 31–60 và 61–90. Mỗi chặng có một dự án thực hành và một câu nói người học làm ra cái gì. Mỗi nhận định có đúng một Vì sao?.
- Soi tin hiện số lần làm mới, ngày thấy đầu và ngày thấy gần nhất. Không hiện điểm trên 100, nhãn đáng tin, nhãn rủi ro cao, hay chỉ số AI.
- So sánh offer hiện thực nhận cả năm, net mỗi tháng, thuế mỗi tháng, và thanh thực nhận, bảo hiểm, thuế, cùng căn cứ thuế và bảo hiểm đang dùng. Số ngày remote hiện cùng offer.
- Ô email đứng lúc lộ trình hiện ra. Email không hiện cho người khác. Không có trang hồ sơ công khai.
- Không lưu và không hiện nguyên văn mô tả công việc, dù người dùng dán vào một ô (NFR-2). Không lưu tên và liên hệ của người tuyển dụng. Trước khi gọi một API bên ngoài, bỏ thông tin cá nhân khỏi phần được gửi đi.

## Câu hỏi mở và giả định còn ảnh hưởng tới giao diện

Mục 12 để bốn câu mở. Tín hiệu sớm chưa có quy tắc phát hiện. Thẻ thành phố xây được với câu chưa ghi nhận tín hiệu đáng kể, theo FR-3. Quy tắc chỉ thành việc phải xây khi tuần 1 cho một quy tắc kiểm được. Chủ của câu này là Duy. Ngưỡng tin treo ở FR-17 là giả định: lần làm mới thứ hai, hoặc còn mở sau 30 ngày. Chưa phải sự thật. Tuần 1 đo xem quy tắc có nhận nhầm tin lành hay không. Trước khi đo, không viết test như thể quy tắc đã đúng, và mục 14 giới hạn test ở số lần làm mới và hai ngày. Kết quả đo tuần 1 chưa có: số tin Data/AI theo từng thành phố, có lương công khai hay không. Thứ tự nới nằm ở FR-7 và nhóm vai gần vẫn là giả định. Cùng tuần đó đo ngưỡng tin treo và, nếu dữ liệu cho phép, một quy tắc tín hiệu sớm. Pháp lý để sau và không chặn v1: Điều 27 Luật Việc làm có coi thông tin thị trường và lộ trình học miễn phí là dịch vụ việc làm phải xin phép hay không; hoa hồng giới thiệu khóa học có phải đăng ký gì không khi khoản đó được xây sau kỳ này; nếu sản phẩm được gọi là giáo dục thì Luật AI có đặt vào nhóm rủi ro cao hay không, với mốc tuân thủ đang được nói tới là tháng 9/2027. Phụ lục thêm câu Điều khoản ITviec và TopDev hạn chế sao chép và khai thác thương mại khi chưa có đồng ý bằng văn bản, và ghi các câu này không chặn v1. Nguồn không chốt câu chữ pháp lý trên Bản đồ nhu cầu hay trên lương công khai.

Các giả định mục 14 còn đụng tới giao diện, giữ nguyên nhãn:

- `[GIẢ ĐỊNH: nhu cầu một lộ trình có trích nguồn là mạnh đủ để làm v1, dù câu khảo sát đó chưa tách riêng "thiếu lộ trình".]` Câu «họ thiếu một lộ trình» trong khảo sát JobsGO được nguồn ghi là gộp với môi trường làm việc và chưa được xác minh riêng. Phụ lục ghi PRD không nâng câu này thành sự thật đã đo.
- `[GIẢ ĐỊNH: Lan, Khoa và Mai là tên tạm, để hành trình có người cụ thể. Ba cảnh không phải bằng chứng, và không chứng minh một người thật sẽ quay lại. Không có buổi ngồi với người thật nào trong bản này để kể.]`
- Một email một lộ trình, với ba cách viết đã trích ở phần Lộ trình 90 ngày. Phụ lục ghi giả định này đang để Duy sửa.
- `[GIẢ ĐỊNH: bộ lọc vai trò mặc định là "Tất cả", không mặc định Data/AI.]`
- `[GIẢ ĐỊNH: danh kỹ năng để chọn là danh cố định do nhóm giữ, cùng taxonomy mà pipeline đã trích. Người dùng không gõ một kỹ năng tự do ngoài danh.]`
- `[GIẢ ĐỊNH: Học gì tiếp? chỉ dựng kịch bản cho cấp Fresher và Junior.]`
- `[GIẢ ĐỊNH: số tuần học của mỗi kỹ năng là số do nhóm gán trong danh, không phải số suy ra tự động từ tin tuyển.]` Nguồn không ghi từng số tuần.
- `[GIẢ ĐỊNH: Data/AI đứng riêng; Backend với Frontend; DevOps/Cloud với Bảo mật; Mobile đứng riêng.]`
- Câu chưa chọn cấp bậc thì ô lương trên thẻ dùng Junior vừa nằm trong định nghĩa mục 4 và FR-3, vừa được mục 14 liệt kê trong mục lục giả định.
- `[GIẢ ĐỊNH: một số ô Data/AI theo thành phố sẽ dưới ngưỡng 30 tin. Đo trong tuần 1. Trước khi đo, đây chưa phải sự thật.]` Mục 14 thêm rằng nguồn tin lệch về ITviec và TP. Hồ Chí Minh.
- Câu hai offer gần ngang nhau khi chênh dưới 1% thực nhận cả năm vừa là hệ quả của FR-15, vừa được mục 14 liệt kê trong mục lục giả định.
- `[GIẢ ĐỊNH: web dùng được trên trình duyệt điện thoại, vì UJ-1 bắt đầu trên điện thoại. Không làm ứng dụng cài máy.]`
- `[GIẢ ĐỊNH: ngưỡng tạm của tin treo là làm mới từ lần thứ hai, hoặc vẫn đang mở sau 30 ngày kể từ ngày thấy đầu. Tuần 1 đo xem ngưỡng có nhận nhầm tin lành hay không. Trước khi đo, không viết test coi ngưỡng này là đúng.]`

Hai cách đếm bề mặt, «năm chỗ» ở mục 9 và «sáu chỗ» ở mục 8 cùng phụ lục, chưa được nguồn giải thích thành một danh sách thống nhất. Cách gộp nhiều khoảng lương thành một lương công khai, cách tính dự báo 18 tháng, và cách phát hiện tín hiệu sớm chưa khóa ngoài điều người dùng thấy. Cơ chế viết câu của lộ trình thuộc kiến trúc. Các số ITviec quý 1/2025 cần được đọc lại trước khi đưa lên sản phẩm. Ảnh khoảng 832 tin là một lúc kiểm kê, không phải quy mô đảm bảo.
