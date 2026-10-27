# Trích UX từ brief — Hải Đồ IT

Bản trích này chỉ ghi những gì `brief.md` và `addendum.md` đã viết, để dùng cho DESIGN.md và EXPERIENCE.md. Không thêm đề xuất. Không hòa giải với tài liệu khác.

## Nguồn và trạng thái

Product Brief có tên "Product Brief: Hải Đồ IT", `status: final`, tạo và cập nhật ngày 2026-10-22. Brief dẫn hai nguồn: bản nghiên cứu thị trường `market-hai-do-it-nen-tang-nghe-nghiep-it-viet-n-2026-10-22` và prototype `Hải Đồ IT — Bản đồ tuyển dụng & Cố vấn đa agent.html`.

Addendum có tên "Addendum: Product Brief Hải Đồ IT", tạo và cập nhật ngày 2026-10-22. Dòng mở gọi file này là chi tiết dành cho PRD và kiến trúc. Mục E ghi ba mục đã chốt ngày 2026-10-22 và nói ba mục đó không còn là giả định mở.

Hải Đồ IT trong v1 là ứng dụng web. Khung làm là 2 tháng, 3 người, web. Brief liệt kê app mobile trong mục không làm.

## Người dùng và việc họ cần làm

Hải Đồ IT giúp junior, fresher và người đang chuyển hướng trong ngành IT trả lời câu hỏi "học gì tiếp để có việc tốt hơn?" bằng dữ liệu tuyển dụng thật, thay vì cảm tính hay lời khuyên chung chung của chatbot. Người dùng xem kỹ năng nào đang được săn đón, thử thêm kỹ năng vào hồ sơ để thấy số việc phù hợp và mức lương thay đổi ra sao, rồi nhận lộ trình 90 ngày. Mỗi bước trong lộ trình đều có nút "Vì sao?" dẫn về nguồn.

Người dùng chính là junior (0–2 năm kinh nghiệm) và fresher muốn chuyển hướng, nhất là sang Data/AI, Cloud/DevOps. Họ cần biết nên học gì, mất bao lâu và đáng hay không. Với họ, thành công là có lộ trình rõ, học đúng thứ thị trường cần, và có được việc hoặc lên lương sau 3–6 tháng.

Người dùng phụ là sinh viên năm cuối các ngành IT, với khoảng 50–60 nghìn người tốt nghiệp mỗi năm. Sinh viên tìm thực tập chủ yếu qua Facebook (47,5%) và chương trình của trường (30%). Brief không mô tả một luồng riêng cho sinh viên.

Bên trả tiền tiềm năng là trường đại học và bootcamp. Brief gọi sản phẩm là công cụ hướng nghiệp và minh chứng đầu ra cho họ. Coursera Việt Nam có 1,8 triệu người học, và brief dùng con số này để nói nhu cầu học kỹ năng rất lớn. v1 thử nghiệm với 1–2 trường hoặc bootcamp. Brief không mô tả một màn riêng cho trường trong v1. Các gói cho trường nằm ở v2.

Hải Đồ IT không phải sàn tuyển dụng. Sản phẩm không ghép việc và không đánh giá công ty.

Brief mô tả một luồng chính gồm 3 bước, cùng 2 công cụ miễn phí để kéo người dùng vào. Brief không kể một phiên làm việc của một người có tên. Addendum ghi brief không mở bằng một người minh họa; phần vấn đề dùng số liệu đã có nguồn; chuyện thật của Duy không chặn brief và không chặn việc xây.

Cách người dùng đang xoay xở, theo brief, là tự đọc tin tuyển, hỏi ChatGPT, hỏi người quen, đăng ký khoá học theo cảm tính. Cái giá phải trả là hàng tháng học sai hướng, trong khi thu nhập junior chỉ khoảng 10–14 triệu đồng/tháng nên mỗi khoá học sai là một khoản mất đáng kể. Brief không gắn tên nguồn cho khoảng thu nhập này trong mục vấn đề. Addendum liệt cùng khoảng này là lương trung vị junior dưới 1 năm kinh nghiệm, độ tin cậy trung bình, trích từ nghiên cứu.

Brief nêu ý định đổi việc cao: 40,9% dân IT định nghỉ việc trong 12 tháng tới, và 26,3% trong số đó muốn đổi hướng nghề nghiệp (ITviec, n=2.324); 54,5% đang chủ động tìm việc (JobsGO). Người dưới 1 năm kinh nghiệm chiếm 45% số ca bị cắt giảm (JobOKO, 580 nghìn tin). Theo nghiên cứu thị trường, người muốn đổi hướng thì nhiều, nhưng chưa sản phẩm nào trả lời câu hỏi "chuyển sang đâu, học gì, mất bao lâu" bằng số liệu.

Sau 2 tháng, brief đi tiếp khi đủ bốn mức: ít nhất 30 người thật tạo xong lộ trình 90 ngày; trong số đó, ít nhất 25% (ít nhất 8 người) mở lại lộ trình trong 14 ngày; ít nhất 1 trường hoặc bootcamp đồng ý thử nghiệm; 100% nhận định có "Vì sao?" trỏ đúng nguồn. Addendum nói mức 30 người là ngưỡng sản phẩm, còn mức 30 tin chỉ dùng để quyết định có hiện lương công khai hay không. Việc mở lại lộ trình trong 14 ngày là ngưỡng brief đã viết. Brief không mô tả tài khoản, đăng nhập hay chỗ lưu lộ trình.

## Màn và hành vi đã chốt

Tên brief dùng cho v1 là Bản đồ nhu cầu, Học gì tiếp?, Lộ trình 90 ngày, Vì sao?, So sánh offer, kiểm tra BHXH, và Soi tin. Addendum gọi màn tương ứng trên prototype là "Soi tin tuyển dụng", rồi gọi lại "tính năng Soi tin".

Bản đồ nhu cầu là mặt tiền. Brief nói giữ nguyên thiết kế prototype cập nhật ngày 2026-10-22. Bảy thành phố là Hà Nội, Hải Phòng, Đà Nẵng, Quy Nhơn, Nha Trang, TP. Hồ Chí Minh và Cần Thơ. Dòng đầu là nhu cầu hôm nay và 18 tháng tới. Người dùng kéo để xem dự báo. Người dùng chạm một thành phố để xem cơ cấu, lương và tín hiệu sớm. Có đánh dấu "✓ bạn đã có". Brief không nói đánh dấu này gắn vào kỹ năng, thành phố hay một thứ khác. Lương công khai chỉ hiện số khi có từ 30 tin. Khi dưới 30 tin, lương công khai ẩn số. Bảy thành phố và dự báo 18 tháng vẫn nằm trên bản đồ. Brief không định nghĩa thêm "cơ cấu" và "tín hiệu sớm" ngoài việc chúng xuất hiện khi chạm một thành phố.

Học gì tiếp? là phần lõi. Trên prototype, màn này tên "Mô phỏng Nếu–thì"; brief và addendum đổi tên thành Học gì tiếp?. Người dùng thêm kỹ năng giả định, ví dụ Docker, RAG, để xem số tin phù hợp, lương kỳ vọng và thời gian học thay đổi thế nào. Hai tên kỹ năng đó là ví dụ brief đưa ra. Hệ thống gợi ý kỹ năng nên học tiếp, xếp theo số việc mở thêm trên mỗi tuần học. Brief gắn khác biệt của sản phẩm với việc trả lời câu hỏi "nếu tôi học X thì sao?" bằng số liệu.

Lộ trình 90 ngày biến lựa chọn ở bước 2 thành kế hoạch 3 chặng. Mỗi chặng có một dự án thực hành. Mọi nhận định đều có nút "Vì sao?" chỉ ra tin tuyển hoặc số liệu làm căn cứ, kể cả những nhận định đã bị loại vì thiếu dữ liệu. Trên prototype, màn này tên "Cố vấn đa agent". Addendum nói bản đầu không nhất thiết đa agent: tính toán từ dữ liệu, rồi LLM viết lộ trình, rồi "Vì sao?". Hoa hồng giới thiệu khoá học trong v1 gắn tại từng bước trong lộ trình. Brief không mô tả nút, câu chữ hay vị trí của khoản hoa hồng đó trên màn.

Xu hướng và hạn dùng kỹ năng nằm trong v1 với tư cách lớp dữ liệu nền. Brief không mô tả hành vi trên một màn riêng. Addendum đối chiếu màn prototype "Lương & hạn dùng kỹ năng": phần kỹ năng là v1, lớp dữ liệu; phần lương phân vị là v2, vì mẫu lương công khai mỏng.

So sánh offer là công cụ miễn phí, đi cùng kiểm tra BHXH, để kéo người dùng vào. Công cụ quy offer về thực nhận cả năm, và cảnh báo khi công ty đóng BHXH theo mức thấp hơn lương thật. Brief dẫn Navigos: 43,1% người lao động gặp trường hợp này. Brief không nói con số 43,1% có nằm trên màn hay không. Addendum xếp "Tập thương lượng" nằm trong màn So sánh offer của prototype sang v2.

Soi tin là bản nhẹ, miễn phí, để kéo người dùng vào. Công cụ cảnh báo tin treo, tin trùng lặp và mức lương bất thường trước khi nộp CV. Addendum nói không ai trả tiền cho tính năng này, nhưng nó tạo lòng tin, và tập trung vào tin treo, không phải chống lừa đảo, vì lừa đảo việc làm không nằm trong top 5. Addendum nói tính năng Soi tin, gồm đếm số lần làm mới và phát hiện tin trùng, cần crawl định kỳ từ sớm. Brief không định nghĩa thêm dấu hiệu của "tin treo" và "mức lương bất thường".

Mỗi tin chỉ giữ kỹ năng, thành phố, cấp bậc, khoảng lương, ngày đăng và link gốc. Brief nói không lưu và không hiển thị nguyên văn mô tả công việc. Addendum nói thêm là loại bỏ tên và liên hệ của người tuyển dụng. Báo cáo công khai của ITviec, TopDev, TopCV và JobOKO được dùng để kiểm tra chéo xu hướng và làm nguồn cho "Vì sao?". Dataset VietJobs chỉ dùng làm nền lịch sử vì không có tên công ty và ngày đăng. Quyết định ngày 2026-10-22: Duy chọn đưa số liệu đã trích vào sản phẩm ngay, gồm ITviec và TopDev. Mỗi tin chỉ sống khoảng 1 tháng. Brief viết tổng khoảng 832 tin tại một thời điểm, gồm ITviec 652, TopDev 99, API ATS 78 và Cốc Cốc 3. Addendum ghi chưa rõ các số đó là số tin tại một thời điểm hay trong một khoảng thời gian.

## Giọng và cách nói về tiền, lương, việc làm

Brief đặt sản phẩm đối diện với cảm tính và lời khuyên chung chung của chatbot. Câu người dùng cần được trả lời là "học gì tiếp để có việc tốt hơn?", và ở phần khác biệt là "nếu tôi học X thì sao?".

Brief nói thẳng rằng Hải Đồ IT không có lợi thế về dữ liệu. Khác biệt brief giữ là trả lời bằng số liệu, minh bạch nguồn qua "Vì sao?", và đứng về phía ứng viên. Brief viết lập trình viên Việt Nam hay kiểm tra lại kết quả AI: 86% luôn hoặc thường xuyên làm vậy, và trích nguồn là cách lấy được lòng tin của nhóm này. Brief không gắn tên nguồn cho con số 86%. Các nền tảng lớn, theo brief, kiếm tiền từ nhà tuyển dụng và dồn AI cho phía nhà tuyển dụng.

Trong tầm nhìn 2–3 năm, brief gọi Hải Đồ IT là "la bàn kỹ năng" của dân IT Việt Nam: nơi sinh viên và junior quyết định học gì trước khi bỏ tiền và thời gian.

Thu tiền gắn với kết quả, không bán thuê bao "lời khuyên". Brief nêu lý do: nghiên cứu mới chỉ thấy ứng viên trả các khoản nhỏ, và brief ghi TopCV thu 10.000–500.000đ; các dịch vụ thu tiền tốt đều gắn với kết quả. Khoảng đó là mức brief dẫn về TopCV, không phải giá của Hải Đồ IT. Trong v1, ứng viên không trả tiền. Không có gói và không có giá. Tiền v1 là hoa hồng giới thiệu khoá học tại từng bước trong lộ trình, và thử nghiệm với trường hoặc bootcamp. Brief gọi món ứng viên có thể trả ở v2 là review dự án cuối lộ trình. Ví ứng viên chỉ được đo khi món này có tên. Hai tháng này không đo câu ứng viên có mở ví không.

Lương công khai trên bản đồ chỉ hiện số khi đủ 30 tin; dưới ngưỡng đó thì ẩn số. So sánh offer nói về thực nhận cả năm và về mức đóng BHXH so với lương thật. Lương theo phân vị để v2. Brief không mô tả cách viết một mức lương khi số đã đủ 30 tin, ngoài việc hiện số.

Sản phẩm không nói như một sàn tuyển dụng. Soi tin nói trước khi người dùng nộp CV, ở bản nhẹ, về tin treo, tin trùng và lương bất thường.

## Điều brief nói về prototype

Prototype được dẫn tên file là `Hải Đồ IT — Bản đồ tuyển dụng & Cố vấn đa agent.html`. Brief và addendum không bảo bám mọi màn trong file đó. Addendum mở bằng mục "Đối chiếu 11 màn prototype với phạm vi".

Với Bản đồ nhu cầu, brief bảo làm đúng prototype. Câu trong phần giải pháp là: "Bản đồ nhu cầu, mặt tiền của sản phẩm, giữ nguyên thiết kế prototype cập nhật ngày 2026-10-22." Câu trong phạm vi v1 là: "Bản đồ nhu cầu (đúng prototype: bảy thành phố, dự báo 18 tháng, tín hiệu sớm)". Câu về lương là: lương công khai chỉ hiện số khi có từ 30 tin, đúng quy tắc đang gắn trên prototype. Addendum ghi quyết định "v1, đúng prototype", rồi viết: giữ bảy thành phố đã liệt kê, dự báo 18 tháng và tín hiệu sớm; quyết định thu còn ba thành phố và đổi dự báo thành kịch bản bị hủy; lương công khai vẫn ẩn số khi dưới 30 tin, vì prototype đang làm vậy.

Với các màn còn lại, addendum đổi tên, tách phạm vi, hoặc để ngoài v1. "Mô phỏng Nếu–thì" thành Học gì tiếp?, vẫn v1 và là lõi. "Cố vấn đa agent" thành Lộ trình 90 ngày, vẫn v1 và là lõi, và bản đầu không nhất thiết đa agent. "Lương & hạn dùng kỹ năng" không đi nguyên màn: phần kỹ năng là lớp dữ liệu v1, phần lương phân vị là v2. So sánh offer là v1 và miễn phí. Soi tin tuyển dụng là v1, bản nhẹ. Tập thương lượng trong màn So sánh offer là v2. Hộ chiếu kỹ năng: review dự án là v2, và bỏ phần "Ghép việc lại". Lộ trình thật của người giống bạn được addendum ghi là "Sau này", trong khi brief xếp việc này vào mục không làm. Chỉ số phản hồi nhà tuyển dụng là không làm. Bộ công cụ nhảy việc, tức agent pháp lý đọc hợp đồng, là không làm; addendum thêm trong ngoặc là có thể để danh sách kiểm tra miễn phí. Remote quốc tế và thị trường Nhật chỉ làm dạng nội dung.

## Việc không làm

Trong v1 không làm app mobile. Không làm ghép việc hoặc gợi ý tin "vừa mở khoá", vì cần giấy phép dịch vụ việc làm. Không làm chỉ số phản hồi và đánh giá nhà tuyển dụng ẩn danh, vì có tiền lệ bị chặn. Addendum thêm: reviewcongty bị chặn năm 2023, và Nghị định 147 bắt xác thực bằng số điện thoại. Không làm agent pháp lý đọc hợp đồng thu phí. Không làm lộ trình thật của người giống bạn trong danh sách không làm của brief. Addendum ghi cùng việc này là "Sau này", với lý do cần nhiều hồ sơ và dễ bị nhận diện lại. Remote/Nhật chỉ làm dạng nội dung. Addendum nói nhóm này nhỏ, khoảng 6.000 kỹ sư Việt tại Nhật. Hai cách ghi "không làm" và "sau này" cùng đứng trong hai file.

Để v2, không phải màn v1: review dự án, là điểm thu tiền chính; phòng tập thương lượng, mà addendum gọi là tập thương lượng trong màn So sánh offer; lương theo phân vị. Addendum nói chưa biết giá thương lượng ở Việt Nam. Tầm nhìn 2–3 năm nói tới thành phố ngoài bảy thành phố trên bản đồ, và có thể cả ghép việc nếu xin được giấy phép. Đó không phải phạm vi v1.

Không lưu và không hiển thị nguyên văn mô tả công việc. Không giữ tên và liên hệ của người tuyển dụng. Không hiện số lương công khai khi dưới 30 tin. Ứng viên không trả tiền trong v1, và v1 không có gói, không có giá.

## Giả định và câu hỏi mở còn ảnh hưởng giao diện

Brief gắn đúng một nhãn nội tuyến. ITviec chiếm khoảng 78% nguồn và vốn lệch về TP.HCM. Nhóm Data/AI ở từng thành phố có thể dưới 30 mẫu `[GIẢ ĐỊNH — cần đo ngay trong tuần 1]`. Addendum giao việc tuần 1: đo số mẫu theo vai trò, theo thành phố, và theo việc có công khai lương hay không. Addendum viết tiếp: nếu nhóm Data/AI ở Hà Nội dưới 30 tin, "Học gì tiếp?" phải tính trên toàn quốc hoặc gộp các vai trò gần nhau. Đó là điều kiện addendum nêu sau khi đo, chưa phải kết quả đã đo.

Brief viết tổng khoảng 832 tin tại một thời điểm. Addendum đánh dấu chưa rõ các số ITviec 652, TopDev 99, API ATS 78 và Cốc Cốc 3 là số tin tại một thời điểm hay trong một khoảng thời gian.

"Tín hiệu sớm" và "cơ cấu" là thứ bản đồ phải hiện khi chạm thành phố. "Tin treo", "tin trùng lặp" và "mức lương bất thường" là thứ Soi tin phải cảnh báo. "✓ bạn đã có" là đánh dấu brief yêu cầu trên bản đồ. Cả hai file không định nghĩa thêm các cụm này, và không nói đánh dấu gắn vào đối tượng nào.

Xu hướng và hạn dùng kỹ năng là lớp dữ liệu v1. Brief không mô tả màn, trạng thái rỗng, hay chỗ lớp này xuất hiện trong luồng ba bước. Brief không mô tả màn cho trường và bootcamp trong v1. Brief không kể hành trình của một người có tên.

ChatGPT được brief ghi là đối thủ thay thế, trong mục rủi ro chưa kiểm chứng: nếu người dùng không thấy giá trị của dữ liệu thật, phần lõi mất lợi thế. Brief không mô tả một màn so sánh với chatbot.

Addendum mục D giữ các câu hỏi pháp lý để xem sau, và nói chúng không phải điều kiện để xây v1. Trong đó có câu liệu cung cấp miễn phí thống kê thị trường lao động và lộ trình học có thuộc "dịch vụ việc làm" phải xin phép không, và câu nếu định vị là "giáo dục" thì có rơi vào danh mục AI rủi ro cao trong giáo dục không. Brief không chọn từ "giáo dục" làm tên gọi sản phẩm. Tên gọi tầm nhìn đã viết là "la bàn kỹ năng".

Addendum mục E nói ba mục đã chốt không còn là giả định mở. Phần còn ảnh hưởng giao diện là: không mở sản phẩm bằng một người minh họa; ngưỡng 30 người tạo xong lộ trình là ngưỡng sản phẩm; ngưỡng 30 tin chỉ quyết định có hiện lương công khai hay không.
