# Đối chiếu prototype với hai bản UX

## Nguồn

Nguồn hình và hành vi là `extract-prototype.md`, rút từ `prototype/Hải Đồ IT — Bản đồ tuyển dụng & Cố vấn đa agent.html`. File đó có mười một artboard. Hai bản được đối chiếu là `DESIGN.md` và `EXPERIENCE.md` trong cùng thư mục, cả hai đang `status: draft`, cập nhật 2026-10-22. Tài liệu này không sửa hai bản đó và không đề xuất một hướng nhìn mới.

Quy tắc đã chốt nằm trong `.memlog.md`. Giao diện ưu tiên prototype. Năm chỗ trong kỳ này lấy mặt nhìn của prototype. Khi prototype và PRD lệch nhau về việc một màn có tồn tại, hoặc về một số có được hiện hay không, PRD thắng. Duy đã giữ các giả định của đường nhanh khi khép hai bản.

Năm chỗ là Bản đồ nhu cầu, Học gì tiếp?, Lộ trình 90 ngày, So sánh offer và Soi tin. Bản đồ nhu cầu lấy artboard «Thị trường · Bản đồ nhu cầu». Học gì tiếp? lấy artboard «Phát triển · Mô phỏng Nếu–thì». Lộ trình 90 ngày lấy khối lộ trình và tấm Vì sao? của artboard «Phát triển · Cố vấn đa agent». So sánh offer lấy phần nhập hai offer và kiểm tra bảo hiểm của artboard «Quyết định · So sánh offer & thương lượng». Soi tin lấy phần dán link của artboard «Ứng tuyển · Soi tin».

## Màu, chữ, khoảng cách, thành phần prototype đã vào DESIGN.md

Bảng màu trong `DESIGN.md` lấy từ iframe sản phẩm. Nền đêm là `#070B10`. Thẻ là `#0D141C`. Lớp lõm là `#0A1118`. Hàng đang chọn là `#13202B`. Hover hàng là `#111C26`. Chữ chính là `#E6EDF3`. Đoạn dẫn là `#A9B8C7`. Chữ phụ trên thẻ là `#C4D0DC`. Meta là `#9FB0C2`. Chữ mờ là `#6E8091`. Chữ trên nền chanh là `#0A0F05`. Màu chanh `#C5F36A` giữ nút chính, lương công khai khi đủ mẫu, dấu đã có và viền focus. Hover của link chanh là `#E4FFB5`. Màu lạnh `#62D9EE` giữ gạch chân mục đang mở, cột thành phố, khung dự báo nét đứt và phần bảo hiểm trên thanh offer. Offer B dùng `#B9A6FF` ở viền trên. Hổ phách `#F5A65B`, cùng nền `#140F09`, chữ `#FFD3A6` và viền `#5A3E22`, giữ lương đang ẩn, kỹ năng đang giảm và thuế trên thanh offer. Đỏ `#F0605D` được ghi là có trong prototype, với nền `#160C0C`, chữ `#FFC2C2` và viền `#5A2E2E`, và kỳ này không dùng màu đó để chấm một tin. Toast đảo nền `#E6EDF3` và chữ `#0A0F05`. Lưới 40px phủ nền bằng màu lạnh ở độ đục rất thấp. Viền thẻ `#1C2A36`, viền nút phụ `#243543` và viền nhấn `#2E4456` đều có token. Khung giấy ngoài iframe, nền `#f5f4ef`, được ghi là không thuộc sản phẩm.

Ba họ chữ vào đúng vai của prototype. Be Vietnam Pro, độ đậm 400, 500 và 600, là câu và điều hướng. JetBrains Mono, độ đậm 400 và 600, là kicker, số và chân trang. Space Grotesk, độ đậm 500 và 700, là tiêu đề, logo và chữ avatar. Tiêu đề bản đồ giữ `clamp(34px, 5vw, 60px)`, dòng 1.04, giãn chữ −0.02em. Tiêu đề các màn còn lại giữ `clamp(26px, 3vw, 34px)`, dòng 1.15, đậm 700. Tên thành phố trong panel phải là 38px đậm 700. Số đầu bản đồ là 26px đậm 700. Logo «HẢI ĐỒ·IT» là 20px đậm 700, giãn chữ 0.04em. Đoạn dẫn bản đồ là 17px, dòng 1.6. Câu thường là 15px, dòng 1.55. Mục điều hướng là 14px đậm 600. Kicker là 12px đậm 600, giãn chữ 0.08em. Chân trang là mono 12px.

Khung nội dung rộng tối đa 1320px, padding ngang 24px. Bản đồ cách đỉnh 40px. Các màn khác cách đỉnh 48px. Đáy trang chừa 72px. Khối trên bản đồ cách nhau 28px. Khối trên các màn khác cách nhau 32px. Viên thuốc, chip và hồ sơ bo tròn đầy. Thẻ và panel bo 16px. Lớp chào và toast bo 12px. Nút, ô nhập và hàng bảng bo 10px. Logo bo 8px. Thanh tiến độ nhỏ được ghi từ 4px đến 6px. Nút chính cao 48px. Nút phụ cao 44px. Nút chính khi hover nhấc 2px và có bóng `0 10px 30px` từ màu chanh. Toast nằm giữa đáy, cách đáy 24px, bóng `0 12px 40px rgba(0,0,0,.5)`, và tự tắt sau 2,4 giây. Header dính, nền đêm ở độ đục cao, gạch dưới bằng `#1C2A36`. Ngăn Vì sao? rộng tối đa 560px, nền `#0A1118`, đè lớp mờ `rgba(3,6,9,.7)`. Hàng đang chọn có viền trong 1px. Khi `prefers-reduced-motion` bật, animation và transition tắt.

Các thành phần lặp của năm chỗ được gọi tên trong mục Components. Logo là hình vuông 34px, viền chanh 1.5px, ba chấm gồm hai chấm lạnh và một chấm chanh. Mục đang mở có gạch chân 2px màu lạnh. Chip vai trò cao ít nhất 44px và đảo thành nền sáng chữ tối khi đang bật. Tầm nhìn là hộp lõm với bốn nhãn «NAY», «+6T», «+12T», «+18T». Cột đang chọn có mặt chữ sáng. Cột không chọn có mặt màu lạnh. Khung dự báo là nét đứt màu chanh. Thẻ thành phố có ba tab «Cơ cấu», «Lương», «Dự báo». Ô lương thiếu mẫu là hộp nét đứt màu hổ phách. Khối xu hướng tám quý dùng cột chanh khi tăng, cột hổ phách khi giảm, cột lạnh khi đi ngang, và cột cuối đậm hơn cột đầu. Nút Vì sao? là viên thuốc mono nhỏ. Hai panel offer giữ viền trên lạnh cho offer A và tím cho offer B. Thanh thực nhận có ba khúc: thực nhận màu chanh, bảo hiểm màu lạnh, thuế màu hổ phách. Khối đang tải là các thanh xương trên nền thẻ.

## Hành vi prototype còn trong năm chỗ

Trên Bản đồ nhu cầu, bảy thành phố vẫn là cột. Bấm một cột, một nhãn hoặc một hàng trong bảng xếp hạng thì cùng chọn một thành phố và đổi thẻ bên phải. Chip vai trò làm số tin của bảy thành phố đổi theo vai trò đó. Tầm nhìn giữ bốn mốc của prototype. Chọn mốc khác «NAY» thì tab của thẻ chuyển sang «Dự báo». Khi tầm nhìn còn «NAY», chỗ dự báo của thành phố vẫn hiện khoảng mốc 12 tháng và có nhãn dự báo. Tab Cơ cấu là tỷ lệ từng vai trò cộng một nhóm còn lại. Tab Lương là một số khi ô mẫu đủ 30 tin. Tab Dự báo là một khoảng có nhãn, kèm một tín hiệu có Vì sao?, hoặc câu «Chưa ghi nhận tín hiệu đáng kể cho thành phố này.» Trên máy bàn, kéo ngang xoay cột và kéo dọc đổi độ nghiêng khi bản đồ ở thế khối. Bản đồ có nút thế khối và thế phẳng. Trên điện thoại, và khi trình duyệt bật giảm chuyển động, bản đồ mở ở thế phẳng. Lớp chào nằm trên bản đồ, mở một lần trên mỗi máy, và nút «Đã hiểu» đóng lớp. Đang tải hiện khối xương. Lỗi nguồn hiện «Không tải được dữ liệu thị trường» và nút «Thử lại». Bộ lọc không còn tin thì hiện «Không có tin nào khớp bộ lọc» và nút «Bỏ lọc». Khối «Xu hướng kỹ năng» tám quý nằm trên bản đồ, dưới bảng xếp hạng, và không phải một màn riêng. Kỹ năng đã có trong hồ sơ phiên mang dấu «đã có».

Trên Học gì tiếp?, kịch bản nằm bên trái, số và bảng thành phố nằm bên phải khi còn đủ chỗ. Thêm hoặc bớt một kỹ năng giả định thì số tin, thời gian học và lương, hoặc trạng thái ẩn, đổi ngay. Nút «Đặt lại» xóa kỹ năng giả định và đưa các số về trạng thái trước. Danh nên học tiếp xếp theo số tin mở thêm trên mỗi tuần học. Bấm «Thêm» thì kỹ năng đó vào nhóm giả định. Kỹ năng đã có không còn trong danh đó. Chưa có kỹ năng giả định thì câu «Chưa có kỹ năng giả định.» hiện, và không có dòng chênh lệch.

Trên Lộ trình 90 ngày, kết quả là ba chặng ngày 1–30, 31–60 và 61–90. Mỗi nhận định có nút «Vì sao?», kể cả nhận định bị loại vì thiếu dữ liệu. Ngăn Vì sao? trượt từ mép phải, đè lớp mờ, và đóng khi bấm Escape hoặc bấm lớp mờ. Nút «Báo nguồn sai hoặc đã cũ» nằm trong ngăn này. Nguồn từ tin trỏ tới tập tin đã trích hoặc link gốc. Nguồn từ báo cáo thì gọi tên báo cáo. Nguyên văn mô tả công việc không hiện trong ngăn.

Trên So sánh offer, hai panel đứng cạnh nhau khi còn chỗ. Sửa một ô thì thực nhận cả năm tính lại. Ngày remote hiện trên panel và không đổi số tiền. Chọn đóng bảo hiểm trên mức thấp hơn thì ô mức đóng hiện thêm, và hộp hụt bảo hiểm hiện khoản hụt cả năm. Mỗi offer hiện thực nhận cả năm, net mỗi tháng, thuế mỗi tháng và thanh ba khúc. Câu kết quả gọi tên công ty đã nhập, nói bên nào cao hơn và chênh bao nhiêu, hoặc nói hai offer gần ngang nhau khi chênh dưới 1% thực nhận cả năm. Mục «Tham số tính (kỳ tính thuế 2026)» đóng sẵn. Câu trên màn nói kết quả là ước tính và không thay thế tư vấn thuế.

Trên Soi tin, ô dán link nằm trên cùng, nút chính ghi «Soi tin», và kết quả nằm bên dưới. Người dùng dán một link rồi đọc số lần làm mới, ngày thấy đầu và ngày thấy gần nhất trên cùng màn.

Năm chỗ dùng chung vài hành vi của prototype. Logo «HẢI ĐỒ·IT» đưa về Bản đồ nhu cầu. Header dính trên mọi màn. Toast là một câu, tự tắt, và không mở một quyết định mới. Viền focus dày 2px màu chanh. Chip đang bật đảo nền sáng và chữ tối.

## Thứ của prototype không vào hai bản

1. Artboard «Thị trường · Lương & hạn dùng kỹ năng» bị cắt khỏi kỳ này, gồm lương theo tuần, biểu đồ mười hai tuần, bảng nửa đời, công tắc cảnh báo hằng tháng và hộp lối chuyển. Phân loại: cắt vì ngoài kỳ này.
2. Artboard «Thị trường · Lộ trình thật», với biểu đồ dòng chảy của người giống nhau, bị cắt khỏi kỳ này. Phân loại: cắt vì ngoài kỳ này.
3. Mạng năm agent, nút «Chạy đa agent», nhật ký `agents.log` và các thẻ mức phù hợp vai trò, khoảng cách kỹ năng, thị trường cho bạn cùng điểm nhấn CV bị cắt khỏi Lộ trình 90 ngày. Phân loại: cắt vì ngoài kỳ này.
4. Artboard «Phát triển · Hộ chiếu kỹ năng», gồm chặng ghép việc, mặt hộ chiếu và khối tin vừa mở khoá, bị cắt khỏi kỳ này. Phân loại: cắt vì ngoài kỳ này.
5. Artboard «Ứng tuyển · Chỉ số phản hồi nhà tuyển dụng», gồm bảng công ty, phễu hồ sơ và form kể trải nghiệm, bị cắt khỏi kỳ này. Phân loại: cắt vì ngoài kỳ này.
6. Khối «Phòng tập thương lượng», hội thoại với agent HR, ba cách trả lời và điểm huấn luyện viên bị cắt khỏi So sánh offer. Phân loại: cắt vì ngoài kỳ này.
7. Artboard «Quyết định · Nhảy việc», gồm agent pháp lý và đồng hồ chọn ngày nghỉ, bị cắt khỏi kỳ này. Phân loại: cắt vì ngoài kỳ này.
8. Artboard «Quyết định · Remote & Nhật», gồm ba phương án thu nhập và lộ trình BrSE, bị cắt khỏi kỳ này. Phân loại: cắt vì ngoài kỳ này.
9. Danh tin mẫu, vệt quét bốn bước, nút theo dõi, nút báo cáo và link sang chỉ số phản hồi bị cắt khỏi Soi tin. Phân loại: cắt vì ngoài kỳ này.
10. Các mã chỉ xuất hiện trên nhật ký agent, mặt hộ chiếu, vùng chỉ số AI và đồng hồ nhảy việc không vào bảng token. Phân loại: cắt vì ngoài kỳ này.
11. Phần trăm «TĂNG / NĂM» trên KPI đầu bản đồ và trên bảng xếp hạng bị cắt. Phân loại: cắt vì PRD cấm hiện số.
12. Điểm giữa và phần trăm so với hôm nay trong tab dự báo bị cắt, vì người dùng chỉ được thấy một khoảng có nhãn dự báo. Phân loại: cắt vì PRD cấm hiện số.
13. Số lương mà prototype luôn vẽ bị cắt khi ô mẫu dưới 30 tin, ở ô đầu bản đồ, ở tab lương và ở Học gì tiếp?. Phân loại: cắt vì PRD cấm hiện số.
14. Số minh họa trong file prototype, gồm 3.960 tin và lương 26 triệu, bị cắt khỏi vai dữ liệu đang chạy. Phân loại: cắt vì PRD cấm hiện số.
15. Trục P10, P25, trung vị, P75, P90 và hộp phân vị trong phòng tập bị cắt. Phân loại: cắt vì PRD cấm hiện số.
16. Số tin trước và sau của từng thành phố trên Học gì tiếp? bị cắt, vì màn này chỉ có một số trước và một số sau cho cả kịch bản. Phân loại: cắt vì PRD cấm hiện số.
17. Độ phủ trước và sau của từng vai trò trên Học gì tiếp? bị cắt. Phân loại: cắt vì PRD cấm hiện số.
18. Ô «Tin mở / tuần học» của đúng kịch bản đang chọn bị cắt. Phân loại: cắt vì PRD cấm hiện số.
19. Ba số tin tăng, số tuần và số tin trên mỗi tuần trên từng dòng «nên học tiếp» bị cắt. Phân loại: cắt vì PRD cấm hiện số.
20. Vòng điểm trên 100, nhãn đáng tin hoặc rủi ro cao, và chỉ số ảnh hưởng AI bị cắt khỏi Soi tin. Phân loại: cắt vì PRD cấm hiện số.
21. Hai số đếm «Giữ lại» và «Bị loại» trong tấm Vì sao? bị cắt. Phân loại: cắt vì PRD cấm hiện số.
22. Bốn nhóm «01 Thị trường» đến «04 Quyết định» và thanh mục con bị thay bằng năm mục phẳng. Phân loại: giả định đường nhanh đã chọn khác.
23. Viên hồ sơ «Minh», avatar chữ «M» và hồ sơ điền sẵn Data/AI bị thay bằng viên chỉ hiện khi đã có thành phố, cấp bậc và vai trò, và bấm thì tới Học gì tiếp?. Phân loại: giả định đường nhanh đã chọn khác.
24. Nút «Nhận lộ trình cho thị trường này» bị thay bằng «Thử một kỹ năng cho thành phố này», và đích mở là Học gì tiếp?. Phân loại: giả định đường nhanh đã chọn khác.
25. Lời chào «Chào Minh — bắt đầu từ đâu?» bị thay bằng lớp chào không gọi tên, với ba dòng xem thành phố, thử một kỹ năng, rồi tạo lộ trình. Phân loại: giả định đường nhanh đã chọn khác.
26. Dải ticker kỹ năng chạy ngang 60 giây bị cắt khỏi Bản đồ nhu cầu. Phân loại: giả định đường nhanh đã chọn khác.
27. Cách thu dưới 720px của prototype bị thay bằng một cột cho mọi khối hai cột, và bản đồ điện thoại mở ở thế phẳng. Phân loại: giả định đường nhanh đã chọn khác.
28. Bộ lọc mở sẵn Data/AI và tem «BẠN» bị thay bằng bộ lọc mặc định «Tất cả» khi chưa có hồ sơ. Phân loại: giả định đường nhanh đã chọn khác.
29. Công tắc «Hiện nhận định bị loại» bị cắt, và nhận định bị loại vẫn có nút Vì sao?. Phân loại: giả định đường nhanh đã chọn khác.
30. Thanh thời gian học nhiều màu theo từng kỹ năng, cùng tổng đổi ra số tháng, bị cắt khỏi Học gì tiếp?. Phân loại: giả định đường nhanh đã chọn khác.
31. Cấp Mid và Senior trên kịch bản Nếu–thì bị cắt, và màn chỉ dựng Fresher với Junior. Phân loại: giả định đường nhanh đã chọn khác.
32. Kịch bản mở sẵn LLM/RAG và AWS bị cắt. Phân loại: giả định đường nhanh đã chọn khác.
33. Tên màn «Mô phỏng Nếu–thì» và bước «Cố vấn đa agent» bị thay bằng «Học gì tiếp?» và «Lộ trình 90 ngày». Phân loại: giả định đường nhanh đã chọn khác.
34. Câu ẩn lương dài của prototype bị thay bằng «Chưa đủ mẫu.» Phân loại: giả định đường nhanh đã chọn khác.
35. Chân trang «số liệu minh họa» và số phiên bản v0.2 đến v0.4 bị thay bằng ngày làm mới gần nhất và câu lương ẩn khi dưới 30 tin. Phân loại: giả định đường nhanh đã chọn khác.
36. Nút «Thử lại» của prototype, vốn chỉ mở toast đang kết nối lại, bị thay bằng một lần gọi lại nguồn và có thể giữ số của lần xem gần nhất. Phân loại: giả định đường nhanh đã chọn khác.
37. Tên vùng trên thẻ thành phố và trên bảng xếp hạng không có trong hai bản. Phân loại: giả định đường nhanh đã chọn khác.
38. Ba nút xoay trái, xoay phải và đặt lại không có trong hai bản, trong khi thao tác kéo và nút thế khối với thế phẳng vẫn còn. Phân loại: giả định đường nhanh đã chọn khác.
