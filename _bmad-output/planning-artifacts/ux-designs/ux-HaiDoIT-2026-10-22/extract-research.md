---
title: 'Rút UX từ nghiên cứu thị trường Hải Đồ IT'
type: 'ux-extract'
source_folder: '_bmad-output/planning-artifacts/research/market-hai-do-it-nen-tang-nghe-nghiep-it-viet-n-2026-10-22'
source_status: complete
extracted: '2026-10-22'
note: 'Chỉ ghi điều các file đã đọc nêu. Khuyến nghị của báo cáo được giữ nguyên là gợi ý. Thư mục nghiên cứu không dùng nhãn [GIẢ ĐỊNH].'
---

# Rút quan sát UX từ nghiên cứu thị trường (2026-10-22)

Báo cáo trả lời câu hỏi có nên thương mại hóa Hải Đồ IT hay không, và màn nào trong 11 màn prototype nên là điểm vào. Bản rút này chỉ giữ những gì chạm bề mặt người dùng đã thấy, lòng tin, ngôn ngữ, cách trình bày lương và thành phố, cùng các gợi ý mà chính báo cáo gọi là khuyến nghị. Độ tin cậy tổng thể của báo cáo là trung bình. Sổ nhận định ghi 21 mục đã xác minh, 7 mục chưa xác minh, và 1 mục bị lật (số liệu BHXH vòng 1).

## Nguồn đã đọc

Đã đọc toàn văn `research.md` (báo cáo đã tổng hợp, 2026-10-22).

Đã đọc thêm vì có bề mặt đối thủ, giọng người dùng, hoặc cảnh báo lòng tin và ngôn ngữ:

- `digests/compvn-r1-1.md` — bề mặt các sản phẩm Việt Nam, gồm ma trận tính năng.
- `digests/compglobal-r1-1.md` — sản phẩm quốc tế và bài học về bề mặt tương tự.
- `digests/comp-r2-1.md` — phần phát hiện về ứng dụng TopCV, HRCV, X-Interview, Job3s.vn và roadmap.sh.
- `digests/pains-r1-1.md` — nỗi đau, một giọng trên Voz, và mẫu lừa đảo qua TopCV.
- `digests/pains-r2-1.md` — giọng đánh giá trên App Store, sửa số BHXH, và lương ghi "thương lượng".
- `digests/redteam-r2-1.md` — bằng chứng làm yếu khoảng trống phía ứng viên, lòng tin với AI, và review ẩn danh.
- `digests/segments-r1-1.md` — hành vi tìm việc và các mức trung vị lương theo vai trò.
- `digests/reg-r2-1.md`, mục bảng rủi ro theo từng việc làm với dữ liệu — cách gọi tên tính năng có thể vướng luật.

Không đọc các file quy mô thị trường (`size-r1-1.md`, `size-r2-1.md`), file giá và chi phí thu hút (`wtp-r2-1.md`, `gtm-r1-1.md`), file soát trích dẫn (`citecheck-final.md`), file giấy phép vòng 3 (`reg-r3-1.md`), `.memlog.md`, và `research-briefing.html`. Bản HTML trùng nội dung báo cáo chính. Thư mục này không có chữ HireJack.

## Bề mặt đối thủ mà người dùng đã thấy

Junior Việt Nam, theo các nguồn đã đọc, đã chạm các sàn và công cụ sau. HireJack không xuất hiện trong thư mục nghiên cứu, nên bản rút này không mô tả HireJack và không coi đó là một bề mặt người dùng đã biết.

**ITviec** là sàn IT mà khảo sát của chính ITviec ghi là kênh tìm việc lớn (trang tuyển dụng nói chung chiếm 55,9% trong báo cáo 2023-24; con số do một sàn công bố). Người dùng thấy báo cáo lương hằng năm với trung vị tĩnh theo vai trò và số năm kinh nghiệm. Bản 2025-26 có 1.839 người trả lời. Bản 2024-25 có 2.324 người. PDF đầy đủ nằm sau form email, điện thoại và công ty. Trang báo cáo không có công cụ tra lương phân vị tương tác. Digest đối thủ ghi AI của ITviec nằm phía nhà tuyển dụng: "AI Match" gợi ý hồ sơ khớp mô tả công việc và giải thích vì sao. ITviec cũng có mục việc AI và Data, và có review công ty ẩn danh kèm kiểm duyệt. Quy chế hoạt động không mô tả dịch vụ trả phí cho ứng viên. ITviec đã có giấy phép dịch vụ việc làm. Vòng phản bác ghi báo cáo lương ITviec cắt theo vai trò, ngôn ngữ, số năm kinh nghiệm, tỉnh và quy mô công ty. Mẫu mỗi năm vẫn chỉ khoảng 1,8–2,3 nghìn người trên cả nước.

**TopDev** cho ứng viên một trình tạo CV, một máy tính lương gross-net, và một trắc nghiệm tính cách. Trang chủ, tại thời điểm nghiên cứu đọc, không có tính năng AI cho ứng viên và không có gói trả phí cho ứng viên. Báo cáo thị trường IT nằm ở khu nhà tuyển dụng. Sản phẩm trả phí "Tuyển dụng Premium" hướng tới nhà tuyển dụng. TopDev đã ra báo cáo lương nhiều năm. Một digest ghi báo cáo 2022 dựa trên 48.179 ứng viên, độ tin cậy trung bình và đã cũ.

**TopCV** là bề mặt ứng viên dày nhất trong nguồn này. Ứng dụng iOS có AI đánh giá mức độ phù hợp và khả năng cạnh tranh của ứng viên với từng việc, máy tính lương gross-net, thuế thu nhập cá nhân và BHXH, trắc nghiệm MBTI và MI, trình tạo CV, và theo dõi ứng tuyển. Có trang tra cứu lương theo vị trí. Vòng phản bác, chỉ từ đoạn trích tìm kiếm vì trang trả về lỗi 403, ghi trang đó kèm lời rằng số liệu không phản ánh lương thực nhận. Độ tin cậy của lời miễn trừ này là thấp đến trung bình. TopCV có thu tiền phía ứng viên bằng gói Pro, gói Premium, và dịch vụ lẻ (xem số người đã ứng tuyển, tải CV không logo). Thời hạn các gói không được nêu. Báo cáo cuối ghi khoảng 36 nghìn lượt đánh giá, điểm 4,8. Số hồ sơ TopCV tự công bố không thống nhất giữa bản tiếng Anh và bản tiếng Việt, khoảng 9–10 triệu. Đánh giá tiêu cực nhìn thấy được, phần nhiều từ 2022–2023, nói trình tạo CV mất chữ, giật, và một trường hợp nhà tuyển dụng lừa yêu cầu nạp tiền.

**VietnamWorks** có AI phía nhà tuyển dụng: sàng hồ sơ, gợi ý ứng viên, và Job Post AI được báo là ra mắt tháng 4/2026. Cùng với Cake và JobsGO, VietnamWorks có công cụ AI chấm CV, và nhóm này đã thành hàng miễn phí. Chân trang VietnamWorks, theo báo cáo, chỉ thấy đăng ký kinh doanh.

**JobsGO** xuất hiện như nguồn khảo sát hành vi và như một công cụ chấm CV. **Cake** có trình chấm CV bằng AI, miễn phí, giao diện tiếng Việt và tiếng Anh. **CareerLink** là nguồn các bài về lương ghi "thương lượng" và về ghosting. Đây là bài của một sàn, không phải một màn hình junior bắt buộc đã dùng hằng ngày.

**HRCV**, ra mắt tháng 6/2026, phân tích CV, ghép việc, có máy tính gross-net, mục "tham khảo lương", và luyện phỏng vấn đang làm. Tuổi Trẻ ghi khoảng 3.400 người dùng website vào tháng 8/2026. Một nguồn, và sản phẩm không chuyên IT. **X-Interview** cho người dùng dán một mô tả công việc rồi luyện phỏng vấn bằng AI. Quy mô người dùng chưa rõ. **Job3s.vn** được Wikipedia ghi nhận giải Sao Khuê 2024 cho việc ghép ứng viên với nhà tuyển dụng bằng AI. Độ tin cậy thấp đến trung bình. **JobHopin** (tên AI "Bunny") là sàn ghép việc cũ hơn, độ tin cậy thấp đến trung bình.

**Thư Viện Pháp Luật** có máy tính gross-net miễn phí, đã cập nhật theo quy tắc 2026. Ứng dụng iOS "Tính Lương" chào so sánh offer và kiểm tra hợp đồng cùng phiếu lương. Máy tính gross-net vì vậy đã có ở TopCV, TopDev, Thư Viện Pháp Luật và vài ứng dụng miễn phí.

**LinkedIn** chiếm 16,4% kênh tìm việc trong khảo sát ITviec 2023-24. Việt Nam có khoảng 10 triệu tài khoản LinkedIn vào tháng 12/2025, đếm theo tập quảng cáo, không phải số người hoạt động hằng tháng. Sinh viên tìm thực tập qua Facebook 47,5%, người quen 37,5%, và chương trình của trường 30% (ITviec).

**reviewcongty** là bề mặt đánh giá công ty ẩn danh. Bộ Thông tin và Truyền thông chặn các tên miền của trang này vào tháng 6/2023. Trang sau đó vẫn chạy trên tên miền nhân bản. Hiệp hội doanh nghiệp đã kiến nghị xử lý các trang review. Digest vòng phản bác còn ghi có báo cáo về việc quản trị viên đòi tiền để gỡ nội dung, làm hỏng lòng tin vào dữ liệu. Độ tin cậy của chi tiết này là trung bình vì lấy từ đoạn trích.

Ở ngoài nước, báo cáo nêu LinkedIn Premium, Levels.fyi, Glassdoor, roadmap.sh, Google Career Dreamer, Findy, LAPRAS, Triplebyte, Hired, Glints, Final Round AI, Teal, và tiện ích GhostJob. Nguồn không chứng minh một junior Việt đã dùng các sản phẩm đó. Google Career Dreamer miễn phí và lúc nghiên cứu chỉ có ở Mỹ. roadmap.sh có lộ trình và gia sư AI ở gói trả phí, với giới hạn lượt chat ở bản miễn phí. Levels.fyi lấy lương do cộng đồng gửi và bán dịch vụ thương lượng có cam kết kết quả. Glassdoor đã bị nhập vào Indeed. Các tiện ích phát hiện tin tuyển dụng ảo gần như không có người dùng trả tiền.

Việc các bề mặt trên đang làm, mà báo cáo gắn với rủi ro pháp lý hoặc với một hàng hóa đã có khắp nơi, gồm các điểm sau. Đây là cách báo cáo đọc rủi ro, chưa phải một quyết định giao diện mới.

- Chấm độ khớp hồ sơ với từng tin và ghép việc, như TopCV, HRCV, VietnamWorks và Job3s, nằm trong nhóm báo cáo xếp rủi ro cao vì luật coi giới thiệu việc làm là dịch vụ việc làm.
- Review nhà tuyển dụng ẩn danh có tiền lệ bị chặn. ITviec có review nhưng kèm kiểm duyệt.
- AI viết tin và sàng hồ sơ phục vụ nhà tuyển dụng, không phải màn hình ứng viên tự xem hướng đi.
- Máy tính gross-net, chấm CV bằng AI, trình tạo CV và trắc nghiệm tính cách đã miễn phí hoặc rất phổ biến. Báo cáo gọi máy tính gross-net là hạng mục có sẵn, không phải khoảng trống.
- ITviec giữ báo cáo lương đầy đủ sau một form thu thông tin liên hệ.
- Bình luận về Triplebyte, độ tin cậy thấp về nguyên nhân, nói một thay đổi quyền riêng tư đã đưa hồ sơ ứng viên ra công khai khi người dùng không đồng ý rõ.

Phần báo cáo cho là chưa thấy ai làm, trong phạm vi đã tìm và chưa chứng minh là không tồn tại, gồm tra lương phân vị có ngưỡng mẫu, cố vấn hội thoại có trích nguồn, mô phỏng nếu học thêm một kỹ năng thì số việc và lương đổi ra sao, quét dấu hiệu tin treo, và soát điều khoản hợp đồng. Vòng phản bác làm yếu câu "phía ứng viên còn trống": lương, điểm khớp bằng AI và máy tính lương đã có trên TopCV và ITviec. Khoảng còn có thể mở là phân vị chi tiết, cố vấn hội thoại, soát hợp đồng và quét tin. Việc không tìm thấy không chứng minh các tính năng đó vắng mặt. Báo cáo cũng nói chưa thấy sản phẩm nào gộp dữ liệu thị trường lao động với cố vấn AI đa agent, và nói thẳng đó là một khoảng trống mô tả, không phải bằng chứng có nhu cầu.

## Cảnh báo về lòng tin, ngôn ngữ, lương, thành phố

**Lòng tin với AI.** Agoda, qua Viet Nam News, ghi 86% lập trình viên Việt Nam luôn hoặc thường xuyên kiểm tra lại kết quả AI. Độ tin cậy trung bình, và nguồn là đoạn trích. TopCV tự công bố 93,49% dân IT-phần mềm dùng AI trong công việc, không nêu phương pháp, độ tin cậy thấp. e-Conomy SEA ghi 81% người Việt được khảo sát tương tác với công cụ AI hằng ngày. Độ tin cậy cao cho khảo sát đó, và đó là dân số chung, không riêng dân IT. Vòng phản bác nói ChatGPT và Gemini miễn phí đã là phương án thay thế cho một cố vấn nghề. Con số "47% Gen Z cho rằng ChatGPT tư vấn nghề tốt hơn sếp" là khảo sát ở Mỹ năm 2023, độ tin cậy thấp đến trung bình, không phải Việt Nam. Ứng dụng tự hướng dẫn ở một lĩnh vực lân cận chỉ giữ chân người dùng trung vị 2,5–3,5 tuần. Đó không phải số đo của ứng dụng hướng nghiệp. Một digest còn ghi bản tóm tắt ITviec rằng 73% doanh nghiệp dùng AI rộng, nhưng chỉ 5,4% tin hoàn toàn đầu ra. Trang này chưa được tải, nên chỉ là manh mối, chưa phải dữ kiện của báo cáo cuối.

**Giọng người dùng đã ghi lại.** VnExpress International thuật lại Le Nam, 23 tuổi, phỏng vấn khoảng 10 lần trong 6 tháng và được một công ty nói họ cắt tuyển junior vì AI giúp senior làm nhanh hơn. Khanh Linh nói bốn năm đại học là chưa đủ. Bài đó cũng nói tin "entry-level" vẫn đòi 2–5 năm kinh nghiệm. Một đoạn trên Voz, trang trả về lỗi 403 nên chỉ còn đoạn trích, kể người viết đã nộp hơn trăm hồ sơ trên TopCV, VietnamWorks và ITviec, được nhiều lịch phỏng vấn rồi bị ghost từ Tết, và nói thị trường không mở cho fresher. Độ tin cậy thấp. Các câu trích của Joseph, 23 tuổi, trong bài VnExpress tháng 1/2026 là giọng ở Anh, không phải người dùng Việt Nam.

**Ngôn ngữ dễ thành cam kết pháp lý.** Luật Việc làm 2025, có hiệu lực 01/01/2026, gộp "tư vấn, giới thiệu việc làm" và "thu thập, phân tích, lưu trữ, cung cấp thông tin về thị trường lao động" vào dịch vụ việc làm. Thông tin thị trường lao động trong luật gồm cả tiền lương và thu nhập. Báo cáo không tìm thấy điều khoản miễn giấy phép cho dịch vụ miễn phí hoặc cho việc chỉ cung cấp thông tin. Câu này còn mở và báo cáo nói cần ý kiến luật sư hoặc Sở Nội vụ. Digest quy định gợi ý cách nói cho từng việc, và ghi rõ phần "lời khuyên kỹ năng thuần túy nằm ngoài tư vấn việc làm" là chưa kiểm chứng. Gọi một màn đọc hợp đồng là "tư vấn pháp luật" bị digest xếp rủi ro cao nếu thu phí. Gọi máy tính lương là "tư vấn thuế" hoặc khai thuế thay người dùng cũng bị tách riêng. Báo cáo cuối nói màn so sánh offer và máy tính net nên kèm miễn trừ trách nhiệm và không khai thuế thay người dùng. AI dùng cho giáo dục nằm trong danh mục rủi ro cao. Danh mục đó không có tuyển dụng hay nhân sự. Định vị "định hướng và học kỹ năng" vì vậy đổi một rủi ro dịch vụ việc làm lấy nghĩa vụ của AI giáo dục. Đây là lựa chọn báo cáo nêu, chưa phải câu chữ đã chốt cho giao diện.

**Lương.** Trung vị fresher khoảng 10–14 triệu đồng mỗi tháng là cách báo cáo tóm tắt vài ô: back-end dưới 1 năm là 12,4 triệu, full-stack dưới 1 năm là 10,1 triệu. Digest phân khúc còn ghi tester dưới 1 năm 14,15 triệu và BA dưới 1 năm 12,2 triệu. Data Engineer 41,3 triệu và Data Analyst hoặc Data Scientist 40,65 triệu là trung vị chung, không phải lương fresher. Cỡ mẫu từng ô không được nêu. Khoảng 54% tin tuyển ghi "thương lượng" đến từ 50 tin mới nhất trong chuyên mục nhân sự trên CareerLink, không phải tin IT. Vietcetera có bài nói khoảng lương công bố đôi khi "để cho có". Đó là bài báo, độ tin cậy thấp. Ứng viên Mỹ muốn thấy lương. Báo cáo nói không tìm được tỷ lệ tương đương ở Việt Nam. Về BHXH, số đúng sau khi sửa lỗi đọc là 43,1% được đóng trên mức lương cố định thấp hơn thu nhập thực, 10,7% đóng theo lương tối thiểu vùng, và 38,3% đóng trên toàn bộ lương gross. Không có cắt riêng cho IT. Nguồn là Navigos, một nguồn. Con số vòng 1 "chỉ 0,12% được đóng trên toàn bộ thu nhập" đã bị lật.

**Thành phố.** Trong số nhà tuyển dụng trả lời khảo sát ITviec kỳ đầu năm 2024, TP. Hồ Chí Minh chiếm 76,7%, Hà Nội 21,4%, Đà Nẵng 1,9%. Chỉ một nguồn, và nguồn là sàn việc làm nên có thể lệch. Báo cáo nói các thành phố nhỏ có rất ít dữ liệu. Mẫu lương khoảng hai nghìn người mỗi năm được báo cáo coi là quá mỏng để chia phân vị theo vai trò, cấp bậc và thành phố, nhất là nơi nhu cầu tuyển đã lệch về TP. Hồ Chí Minh. Nghiên cứu không nêu danh sách thành phố của sản phẩm. Với lộ trình ẩn danh, báo cáo ghi prototype đang đặt ngưỡng n lớn hơn hoặc bằng 20, rồi suy luận rằng công ty nhỏ vẫn dễ bị nhận ra. Phần "dễ bị nhận ra" là suy luận của báo cáo.

**Hành vi chọn việc, để khỏi thiết kế nhầm thứ người dùng đang cân.** JobsGO ghi cơ hội phát triển 72,7%, văn hóa công ty 69,7%, lương thưởng 67,7%. ITviec ghi mid và senior coi trọng review của nhân viên (70%) và phúc lợi (57%) khi chọn việc. Câu "hơn 70% muốn môi trường cởi mở, sáng tạo và lộ trình rõ ràng, chỉ khoảng một phần ba thấy công ty đáp ứng" gộp môi trường với lộ trình, một nguồn, và báo cáo đánh dấu chưa xác minh. Thị trường tuyển trên riêng ITviec vẫn tăng ở các quý được trích, nên vòng phản bác nói nỗi đau có thể là chọn hướng nào. Câu "không có việc" không được nguồn nâng thành sự thật.

## Gợi ý nghiên cứu (ghi rõ là gợi ý, không phải quyết định)

Mục 9 của báo cáo tự gọi các dòng dưới đây là khuyến nghị. Độ tin cậy tổng thể của quyết định "nên theo đuổi nhưng thu hẹp" là trung bình. Bản rút này không biến chúng thành yêu cầu màn hình.

- R1, độ tin cậy trung bình: điểm vào mà báo cáo gợi ý là cố vấn lộ trình 90 ngày có chỗ trích nguồn ("Vì sao?"), mô phỏng Nếu–thì, và xu hướng kỹ năng, cho junior, fresher và người chuyển hướng. Báo cáo gắn gợi ý này với nỗi đau trước AI và với khoảng trống trải nghiệm, rồi ghi ngay rủi ro bị sao chép và bị ChatGPT thay thế.
- R2, độ tin cậy thấp đến trung bình: thu tiền gắn với kết quả, qua trường, bootcamp, hoa hồng khóa học, hoặc gói lộ trình kèm review dự án, thay vì bán thuê bao lời khuyên. Báo cáo nói chưa có bằng chứng dân IT sẵn lòng trả. Phần thử một mức giá cụ thể không đưa vào bản rút UX này.
- R3, độ tin cậy trung bình: dùng so sánh offer theo thực nhận, có kiểm tra mức đóng BHXH, và soi tin treo làm phần miễn phí để kéo người vào. Căn cứ là tỷ lệ đóng BHXH lệch thu nhập, việc không ai trả tiền cho máy phát hiện tin ảo, và việc máy tính gross-net đã phổ biến.
- R4, độ tin cậy cao về căn cứ pháp lý: hoãn ghép việc, tin "vừa mở khóa", chỉ số phản hồi nhà tuyển dụng, và agent pháp lý thu phí cho đến khi có giấy phép hoặc ý kiến pháp lý.
- R5, độ tin cậy cao về căn cứ dữ liệu: giải nguồn dữ liệu trước khi viết code. Ba hướng báo cáo liệt kê là đối tác dữ liệu, dữ liệu công khai đã tổng hợp, hoặc cơ chế góp lương để xem lương. Câu gợi ý kèm theo là bản đồ thành phố chỉ hiện nơi có đủ mẫu. Báo cáo không chốt con số "đủ".
- R6, độ tin cậy cao: ẩn danh trước khi gọi mô hình ngôn ngữ, che ảnh căn cước và số tài khoản trong hợp đồng, và không theo dõi hành vi người dùng. Theo dõi hành vi trên mạng là dữ liệu nhạy cảm trong nghị định báo cáo trích.
- R7, độ tin cậy trung bình: để remote, Nhật và BrSE ở dạng nội dung. Lộ trình thật cần lượng dữ liệu lớn. Hộ chiếu kỹ năng thu phí nhà tuyển dụng có tiền lệ quốc tế yếu (Triplebyte dừng, Findy vẫn lỗ, LAPRAS tăng chậm).
- R8 nói cần kiểm chứng trước khi viết PRD, gồm phỏng vấn junior hoặc fresher và vài trường hoặc bootcamp, cùng ý kiến luật sư về Điều 27. Cách thử giá mà báo cáo nêu trong mục này không được chép vào bản rút này.

Các câu còn mở có ảnh hưởng tới chữ trên màn hình: ứng viên IT có trả thuê bao định kỳ hay không thì chưa có dữ liệu. Điều 27 có áp cho thông tin miễn phí hay không thì chưa thấy điều khoản miễn. Tỷ lệ ghosting và số tin treo tại Việt Nam mới có một nguồn từ nhà cung cấp. Câu về "muốn có lộ trình" cần nguồn thứ hai và cần tách khỏi câu hỏi về môi trường.

## Điều không lấy vào giao diện

Những mục sau có trong nghiên cứu nhưng không nên thành chữ, số, hoặc kiểu màn hình.

- Không hiện "0,12% được đóng BHXH trên toàn bộ thu nhập". Báo cáo đã xác định đó là đọc nhầm.
- Không hiện "60% lao động IT bị sa thải chưa có việc sau một năm". Báo cáo loại số này vì không nêu phương pháp, và các giọng trong bài đó không phải người Việt.
- Không hiện "tin IT giảm 16,92%". Báo cáo nói con số này không có trên trang công bố gốc của JobOKO, nên chưa xác minh.
- Không gộp 40,9% (định nghỉ trong 12 tháng, ITviec) với 54,5% (đang chủ động tìm việc, JobsGO) thành một tỷ lệ. Blog ITviec còn làm tròn 40,9% thành 40%.
- Không viết 34,3% như một việc đã đo. Đó là dự báo năm 2026 về tỷ lệ doanh nghiệp nêu năng suất AI là lý do không tuyển thêm.
- Không viết 93,49% dân IT dùng AI như một sự thật chắc. TopCV tự công bố và không nêu cách đo.
- Không lấy mẫu 50 tin nhân sự ghi "thương lượng" làm bằng chứng lương IT bị giấu.
- Không lấy trung vị Data Engineer hoặc Data Analyst làm lương fresher.
- Không vẽ các thành phố nhỏ như thể đã có mẫu lương dày. Nguồn địa lý duy nhất trong báo cáo cuối là ba tỷ lệ TP. Hồ Chí Minh, Hà Nội và Đà Nẵng, từ một khảo sát nhà tuyển dụng trên một sàn.
- Không làm màn ghép việc, tin vừa mở khóa, chỉ số phản hồi nhà tuyển dụng, hay điểm review công ty ẩn danh. Nhóm này là khuyến nghị hoãn và có tiền lệ chặn.
- Không gọi sản phẩm là tư vấn việc làm, giới thiệu việc làm, tư vấn pháp luật, hoặc tư vấn thuế.
- Không khóa một bảng lương sau form lấy email và số điện thoại theo kiểu PDF của ITviec.
- Không đưa trắc nghiệm MBTI hoặc MI, trình tạo CV, và máy tính gross-net thành thứ sản phẩm này khác người khác. Chúng đã có trên các bề mặt người dùng đang dùng.
- Không công bố hồ sơ kỹ năng của người dùng ra ngoài khi chưa có đồng ý rõ. Tiền lệ Triplebyte được nhắc đúng với độ tin cậy thấp về nguyên nhân.
- Không theo dõi hành vi người dùng để giữ cách xử lý dữ liệu mà báo cáo mô tả ở R6.
- Không đưa ảnh căn cước hoặc số tài khoản vào nội dung gửi cho mô hình ngôn ngữ.
- Không bịa bề mặt HireJack. Tên này không có trong thư mục nghiên cứu đã đọc.
- Không đưa vào giao diện các hạng mục đã loại khỏi bản rút này: một mức giá thử cụ thể, cửa thử tính năng chưa có, một số chi phí thu hút người dùng, và một tên người dùng giả định không xuất hiện trong nghiên cứu.
