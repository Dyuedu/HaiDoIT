---
title: Đối chiếu nghiên cứu thị trường với hai bản UX
type: ux-reconcile
source: _bmad-output/planning-artifacts/ux-designs/ux-HaiDoIT-2026-10-22/extract-research.md
compared:
  - DESIGN.md
  - EXPERIENCE.md
language: vi
---

# Đối chiếu UX với bản rút nghiên cứu

## Nguồn

Bản này đối chiếu `DESIGN.md` và `EXPERIENCE.md` với `extract-research.md` trong cùng thư mục. Bản rút đó lấy từ báo cáo thị trường ngày 2026-10-22, cùng các digest về bề mặt đối thủ, giọng người dùng, lòng tin và cách gọi tên có thể vướng luật. Hai bản UX không bị sửa trong lần đối chiếu này. Khuyến nghị trong bản rút vẫn là gợi ý. Bản này không biến chúng thành yêu cầu giao diện mới.

## Cảnh báo nghiên cứu mà hai bản UX đã giữ

Hai bản giữ lòng tin với AI bằng nút «Vì sao?» trên từng nhận định, kể cả nhận định bị loại, và bằng ngăn có câu nguồn. Cột tránh của Voice and Tone có cụm «Tin mình đi». Các số 86%, 81%, 5,4% và câu khảo sát ở Mỹ về ChatGPT không được viết thành chữ trên màn.

Voice and Tone cấm bốn cụm «tư vấn việc làm», «giới thiệu việc làm», «tư vấn pháp luật» và «tư vấn thuế» trên mọi bề mặt. Câu của So sánh offer được phép nói kết quả là ước tính và không thay thế tư vấn thuế. Kỳ này không có màn đọc hợp đồng. Màu đỏ của prototype không được dùng để gắn huy hiệu rủi ro cao cho một tin.

Lương công khai chỉ hiện một số khi ô mẫu đủ 30 tin. Dưới ngưỡng, màn nói «Chưa đủ mẫu.» và không điền một số cho ô khỏi trống. Đủ bảy thành phố vẫn hiện khi một thành phố ít tin, và lương của ô mỏng không hiện số, nên thành phố ít tin không bị vẽ như đã có mẫu lương dày. v1 không vẽ trục phân vị. Chữ «Dự báo» đứng cạnh khoảng dự báo.

Số 0,12% đóng BHXH trên toàn bộ thu nhập không được viết lên màn. Hộp hụt bảo hiểm chỉ hiện khi người dùng chọn đóng trên mức thấp hơn lương gross của chính offer đó. Inspiration ghi máy tính gross-net đã có ở TopCV, TopDev và Thư Viện Pháp Luật. So sánh offer ở lại vì PRD yêu cầu thực nhận cả năm và kiểm tra BHXH, và câu trên màn gọi kết quả là ước tính.

Lương không khóa sau form lấy email và số điện thoại. Email chỉ dùng để mở lại lộ trình sau khi ba chặng đã hiện.

Hai bản không mở bề mặt cho ghép việc, điểm khớp một người với một tin, chỉ số phản hồi nhà tuyển dụng, review nhà tuyển dụng ẩn danh, agent pháp lý thu phí, phòng tập thương lượng, lương phân vị, Remote hay Nhật, hộ chiếu kỹ năng, và bước chạy nhiều agent. Lương trên màn hoặc hiện một số, hoặc nói chưa đủ mẫu, trên chính màn đó.

Hồ sơ kỹ năng không có trang công khai. Email không hiện cho người khác. Trước khi gọi một API bên ngoài, thông tin cá nhân được bỏ khỏi phần gửi đi. Lớp chào và viên hồ sơ không gọi tên một người. Tên HireJack không xuất hiện trong hai bản.

Nhãn «tin treo», nếu hiện, phải nói ngưỡng đang dùng và nói ngưỡng đó chưa đo thành sự thật. Voice and Tone còn cấm viết 60% lao động IT bị sa thải chưa có việc sau một năm, cấm viết tin IT giảm 16,92%, cấm gộp 40,9% với 54,5%, cấm viết 34,3% như một việc đã đo, cấm viết 93,49% dân IT dùng AI như sự thật chắc, cấm lấy mẫu 50 tin ghi «thương lượng» làm bằng chứng lương IT, và cấm viết trung vị Data Engineer hoặc Data Analyst thành lương fresher. Cùng mục còn chặn số minh họa của prototype, chặn việc viết ảnh khoảng 832 tin thành quy mô đảm bảo, và chỉ cho số ITviec quý 1/2025 về tin AI/ML tăng 41% cùng lượt tìm «AI» tăng 89% lên màn sau khi được đọc lại từ nguồn gốc.

## Gợi ý nghiên cứu không đưa vào giao diện

Gợi ý R1 lấy cố vấn lộ trình 90 ngày làm điểm vào ở ngoài mặt tiền, vì PRD đã chốt Bản đồ nhu cầu là chỗ mở web.

Câu trong R1 về rủi ro bị sao chép và bị ChatGPT thay thế ở ngoài giao diện, vì đó là gợi ý chiến lược.

Hình cố vấn hội thoại ở ngoài giao diện, vì PRD đã bỏ bước chạy nhiều agent, còn hai bản UX giữ «Vì sao?» trên từng nhận định.

Gợi ý R2 về thu tiền theo kết quả, qua trường, bootcamp, hoa hồng khóa học hoặc gói lộ trình kèm review dự án ở ngoài giao diện, vì đó là gợi ý và vì PRD đã cắt chỗ trả tiền, hoa hồng và review dự án khỏi kỳ này.

Gợi ý R5 về đối tác dữ liệu, dữ liệu công khai đã tổng hợp, hoặc góp lương để xem lương ở ngoài giao diện, vì đó là gợi ý nguồn dữ liệu và vì PRD đã chọn đưa số liệu đã trích vào sản phẩm.

Câu trong R5 rằng bản đồ chỉ hiện thành phố có đủ mẫu ở ngoài giao diện, vì PRD đã giữ đủ bảy thành phố kể cả khi một thành phố ít tin.

Phần «không theo dõi hành vi người dùng» trong R6 ở ngoài chữ trên màn, vì đó là gợi ý cách xử lý dữ liệu.

Việc che ảnh căn cước và số tài khoản ở ngoài giao diện, vì PRD đã cắt màn đọc hợp đồng.

Gợi ý R7 để remote, Nhật và BrSE ở dạng nội dung ở ngoài giao diện, vì PRD đã cắt màn và chuyên mục đó trong hai tháng này.

Tiền lệ yếu của hộ chiếu kỹ năng trong R7 ở ngoài giao diện, vì PRD đã cắt hộ chiếu kỹ năng khỏi kỳ này.

Gợi ý R8 về phỏng vấn người dùng và ý kiến luật sư trước khi viết ở ngoài giao diện, vì đó là gợi ý quy trình và vì PRD đã để câu hỏi pháp lý sau, không chặn v1.

Giới hạn rằng 43,1% là số của người lao động nói chung, không có cắt riêng cho IT, ở ngoài câu trên So sánh offer, vì bản rút giữ đó là giới hạn của một nguồn.

Câu khảo sát gộp môi trường làm việc với «muốn có lộ trình» ở ngoài giao diện, vì báo cáo đánh dấu câu này chưa xác minh và cần tách khỏi câu hỏi về môi trường.

## Số và câu bị cấm đã có mặt trong Voice and Tone hay chưa

Các số bị cấm và bốn cụm dễ thành cam kết pháp lý đã có trong Voice and Tone của `EXPERIENCE.md`. Mục đó liệt kê 0,12% đóng BHXH trên toàn bộ thu nhập, 60% lao động IT bị sa thải chưa có việc sau một năm, tin IT giảm 16,92%, việc gộp 40,9% với 54,5%, 34,3% viết như một việc đã đo, 93,49% dân IT dùng AI, mẫu 50 tin ghi «thương lượng» dùng như bằng chứng lương IT, và trung vị Data Engineer hoặc Data Analyst viết thành lương fresher. Cùng mục cấm «tư vấn việc làm», «giới thiệu việc làm», «tư vấn pháp luật» và «tư vấn thuế», và cho phép câu «không thay thế tư vấn thuế» chỉ như lời miễn trừ. Cột tránh còn có «Tên một người mẫu trên hồ sơ».

Một số điều cấm khác của bản rút nằm ngoài Voice and Tone và đã được hai bản giữ ở chỗ khác. Việc không khóa bảng lương sau form xin số điện thoại nằm ở Do's and Don'ts của `DESIGN.md` và ở Inspiration của `EXPERIENCE.md`. Việc không chấm khớp người với tin, không làm review ẩn danh, và không biến máy tính gross-net thành điểm khác biệt nằm ở Inspiration. Việc không công bố hồ sơ và việc bỏ thông tin cá nhân trước API nằm ở mục Ngưỡng, nguồn, và hồ sơ. Việc không mở các màn ghép việc, phản hồi nhà tuyển dụng, hợp đồng, phân vị, thương lượng, Remote hay Nhật nằm ở Information Architecture và ở Do's and Don'ts.

Vài câu và số nhạy của bản rút chưa có dòng cấm riêng trong Voice and Tone, và cũng không thành chữ trên màn. Nhóm này gồm ba tỷ lệ thành phố 76,7%, 21,4% và 1,9%, số 43,1%, khoảng trung vị fresher 10–14 triệu viết như một ô duy nhất, các số 86%, 81% và 5,4%, câu 47% Gen Z ở Mỹ, câu giữ chân 2,5–3,5 tuần, các lời kể của Le Nam, Khanh Linh, đoạn Voz và Joseph, tên trắc nghiệm MBTI hoặc MI, trình tạo CV, tên HireJack, một mức giá thử cụ thể, một cửa thử tính năng chưa có, và một số chi phí thu hút người dùng. Foundation đã nói kỳ này không có chỗ trả tiền và không có giá. Hai bản không thêm các hạng đó vào Voice and Tone, để khỏi biến một điều đang bị loại thành chữ mới trên màn.
