# Trích prototype — hệ thống hình và hành vi trên màn

## Nguồn

Nguồn duy nhất là file `prototype/Hải Đồ IT — Bản đồ tuyển dụng & Cố vấn đa agent.html`. Tài liệu trang có tiêu đề «Hải Đồ IT — Bản đồ tuyển dụng & Cố vấn đa agent». File là một gói trang: lớp ngoài xếp 11 artboard thành iframe 1440px rộng, mỗi iframe chứa một trang React (`lang="vi"`) dùng font Be Vietnam Pro, JetBrains Mono và Space Grotesk. Tên artboard lấy đúng nhãn `<h2>` đặt phía trên từng iframe. Mỗi trang còn có `<title>` và `<h1>` riêng, ghi kèm bên dưới vì chúng khác nhãn artboard. Mọi con số trong prototype đều được file tự gọi là minh họa, số liệu ví dụ, hoặc «[NGUỒN DỮ LIỆU]».

Lớp vỏ xem prototype (nền quanh các iframe) dùng nền `#f5f4ef`, chữ `#1f1e1d`, nhãn artboard 13px đậm 500 màu `#6b6a68`, và bóng iframe `0 1px 3px rgba(0,0,0,.12)`. Đó là khung trình bày file, không phải giao diện sản phẩm bên trong iframe.

## Danh sách màn / artboard, đúng tên trong file

Các artboard xếp dọc, từ trên xuống, đúng thứ tự và đúng tên trong file:

1. **Thị trường · Bản đồ nhu cầu** — iframe 1440×1900. `<title>`: «Bản đồ nhu cầu tuyển dụng IT». Tệp điều hướng: `Main.dc.html`.
2. **Thị trường · Lương & hạn dùng kỹ năng** — iframe 1440×1800. `<title>`: «Lương thời gian thực và hạn dùng kỹ năng». Tệp: `Pulse.dc.html`.
3. **Thị trường · Lộ trình thật** — iframe 1440×1550. `<title>`: «Lộ trình thật của người giống bạn». Tệp: `Paths.dc.html`.
4. **Phát triển · Cố vấn đa agent** — iframe 1440×2200. `<title>`: «Cố vấn nghề nghiệp đa agent». Tệp: `Advisor.dc.html`.
5. **Phát triển · Mô phỏng Nếu–thì** — iframe 1440×1650. `<title>`: «Mô phỏng Nếu–thì». Tệp: `WhatIf.dc.html`.
6. **Phát triển · Hộ chiếu kỹ năng** — iframe 1440×1800. `<title>`: «Hộ chiếu kỹ năng». Tệp: `Passport.dc.html`.
7. **Ứng tuyển · Soi tin** — iframe 1440×1750. `<title>`: «Soi tin tuyển dụng». Tệp: `JobCheck.dc.html`.
8. **Ứng tuyển · Chỉ số phản hồi nhà tuyển dụng** — iframe 1440×1700. `<title>`: «Chỉ số phản hồi nhà tuyển dụng». Tệp: `Employers.dc.html`.
9. **Quyết định · So sánh offer & thương lượng** — iframe 1440×2150. `<title>`: «So sánh offer và tập thương lượng». Tệp: `Offer.dc.html`. Trên thanh con, mục đang chọn ghi «So sánh offer».
10. **Quyết định · Nhảy việc** — iframe 1440×2150. `<title>`: «Bộ công cụ nhảy việc». Tệp: `SwitchKit.dc.html`.
11. **Quyết định · Remote & Nhật** — iframe 1440×1800. `<title>`: «Remote quốc tế và thị trường Nhật». Tệp: `Global.dc.html`.

Điều hướng lặp trên mọi màn. Logo «HẢI ĐỒ·IT» trỏ về `Main.dc.html`. Nhóm chức năng có bốn mục, kèm số mono: «01 Thị trường», «02 Phát triển», «03 Ứng tuyển», «04 Quyết định». Nhóm đang mở có nền `#13202B`, viền trong `#2E4456`, và số chuyển sang `#62D9EE`. Dưới đó là thanh con của nhóm. Thị trường gồm «Bản đồ nhu cầu», «Lương & kỹ năng», «Lộ trình thật». Phát triển gồm «Cố vấn đa agent», «Mô phỏng Nếu–thì», «Hộ chiếu kỹ năng». Ứng tuyển gồm «Soi tin tuyển dụng», «Chỉ số phản hồi nhà tuyển dụng». Quyết định gồm «So sánh offer», «Nhảy việc», «Remote & Nhật». Mục con đang mở có gạch chân 2px màu `#62D9EE`.

Góc phải header là viên thuốc hồ sơ: avatar tròn chữ «M», chữ «Minh · Junior → Data/AI · Hà Nội». Nhãn aria ghi «Hồ sơ của bạn: Minh, Junior 2 năm, mục tiêu Data/AI Engineer, Hà Nội». Viên thuốc trỏ tới `Advisor.dc.html`, riêng trên màn cố vấn thì trỏ tới form `#hd-profile`. Dưới 720px, chữ hồ sơ và số nhóm bị ẩn.

## Màu

Nền sản phẩm là `#070B10`, phủ lưới 40px bằng `rgba(98,217,238,.05)`. Thẻ và panel dùng `#0D141C`, viền `#1C2A36`. Lớp trong hơn (ô nhập, bản đồ, nền phụ) dùng `#0A1118`. Nhật ký agent, hộp hợp đồng và mặt hộ chiếu dùng `#05080C`; thanh tiêu đề của các hộp đó dùng `#0A1017`. Dải ticker trên bản đồ cũng dùng `#0A1017`.

Chữ chính là `#E6EDF3`. Đoạn dẫn dùng `#A9B8C7`. Chữ phụ trên thẻ dùng `#C4D0DC`. Nhãn nhỏ, chân trang và meta dùng `#9FB0C2`. Số thứ tự và chữ mờ hơn dùng `#6E8091`. Chữ trong nhật ký và dòng hợp đồng dùng `#D5DEE7`. Chữ đặt trên nút chanh và trên chip đang chọn là `#0A0F05`.

Màu nhấn lạnh là `#62D9EE`. Nó xuất hiện ở gạch chân mục đang mở, số nhóm đang mở, viền avatar, cột bản đồ, vòng lương, phần bảo hiểm trên thanh offer, và trạng thái «đang chạy». Màu nhấn nóng là `#C5F36A`. Nó là nút chính, mức tăng, thực nhận, tick «đã có», viền focus 2px, và dấu chấm giữa chữ logo. Link là `#C5F36A`, hover thành `#E4FFB5`. Chip kỹ năng «đã có» hoặc lối chuyển dùng chữ `#E9FFC2`.

Lương được vẽ thành ba vai. Trung vị và thực nhận là `#C5F36A` (vạch giữa có bóng `0 0 14px rgba(197,243,106,.7)` trên màn lương). Khoảng P25–P75 và phần bảo hiểm là `#62D9EE` trên nền `rgba(98,217,238,.18)`. Phần thuế TNCN trên thanh offer là `#F5A65B`. Trục lương là đường `#1C2A36` dày 2px.

Cảnh báo là `#F5A65B`, chữ cảnh báo `#FFD3A6`, viền `#5A3E22`, nền `#140F09` hoặc `#1A130B`. Dùng cho mẫu dưới ngưỡng, kỹ năng suy giảm, tin «cần thận trọng», và hụt bảo hiểm. Rủi ro cao và điều khoản «trái luật» là `#F0605D`, chữ `#FFC2C2` hoặc `#FFB4B4`, nền `#160C0C`, viền `#5A2E2E`.

Đường và viền có tầng. `#1C2A36` là viền thẻ và đường kẻ. `#243543` là viền chip, ô nhập và nút ghost. `#2E4456` là viền đậm hơn, viền lớp chào, và viền trong của nhóm đang chọn. `#2A3E4E` là viền chip kỹ năng mặc định và cột cơ cấu khi không được tô. `#15212B` là đường kẻ hàng trong bảng kỹ năng.

Trạng thái chọn đảo màu: chip đang bật có nền `#E6EDF3` và chữ `#0A0F05`. Hàng và nút phân đoạn đang chọn có nền `#13202B`. Hover hàng và nhóm nav là `#111C26`. Nền thanh tiến độ và gauge là `#16222D`.

Bản đồ Việt Nam là các lớp xanh đậm từ `#04090D`, `#0A1E28`, `#0C2532`, `#0E2C3A`, `#103342` tới mặt `#0D2836`, viền ngoài `#62D9EE`. Cột thành phố đang chọn có mặt `#E6EDF3`, mặt bên `#8DB2C2` và `#5E8697`. Cột không chọn có mặt `#62D9EE`, mặt bên `#1F6A7C` và `#154B5B`. Khung dự báo nét đứt là `#C5F36A`.

Offer B và phương án Nhật dùng `#B9A6FF`. Mốc thưởng trên đồng hồ nhảy việc dùng `#E3D27A`. Agent hoàn tất dùng viền `#4E7A2E`, nền `#0F1A12`, dây nối `#5C8F35`. Thanh «trước» trên biểu đồ độ phủ vai trò dùng `#4A6478`. Các khúc thời gian học trên màn Nếu–thì lần lượt lấy `#C5F36A`, `#62D9EE`, `#F5A65B`, `#B9A6FF`, `#7BE0B0`, `#F2D16B`. Ba vùng chỉ số AI là `#2C5E6B` (con người dẫn dắt), `#5E5A3A` (AI hỗ trợ), `#6B4A2C` (tự động hoá cao). Hồ sơ trong ngăn «Vì sao?» dùng `#B9A6FF`.

## Chữ

Ba họ font được nhúng và dùng xuyên suốt. Be Vietnam Pro, các độ đậm 400, 500 và 600, là chữ thân và điều hướng. JetBrains Mono, độ đậm 400 và 600, là nhãn kicker, số, meta và nhật ký. Space Grotesk, độ đậm 500 và 700, là tiêu đề lớn, logo và chữ trong avatar. Fallback của thân là `system-ui, sans-serif`. Fallback của mono là `ui-monospace, Menlo, monospace`.

Trên bản đồ, tiêu đề chính là Space Grotesk 700, cỡ `clamp(34px, 5vw, 60px)`, dòng 1.04, giãn chữ −0.02em. Các màn còn lại dùng tiêu đề chính `clamp(26px, 3vw, 34px)`, dòng 1.15, đậm 700. Tên thành phố trong cột phải bản đồ là 38px đậm 700. Số lương lớn trên màn lương là `clamp(44px, 6vw, 72px)` đậm 700. KPI bản đồ là 26px đậm 700. Logo «HẢI ĐỒ·IT» là 20px đậm 700, giãn chữ 0.04em. Đoạn dẫn bản đồ là 17px, dòng 1.6. Đoạn dẫn các màn khác là 15px, dòng 1.55.

Nhóm nav là 14px đậm 600. Mục con là 14px đậm 500. Hồ sơ là 13px. Kicker là JetBrains Mono 12px đậm 600, giãn chữ 0.08em; một số kicker thu còn 11px hoặc 10px. Chip lọc trên bản đồ là 14px đậm 600, cao tối thiểu 44px. Chip trên các màn sau là 14px đậm 500, và đậm 600 khi đang bật. Nút phân đoạn trên bản đồ là JetBrains Mono 13px đậm 600. Nút chính dạng `.cta` cao 48px, đậm 600, nền `#C5F36A`. Nút `.run` trên màn cố vấn cao 52px, Space Grotesk 16px đậm 700. Nút ghost cao 44px, 14px đậm 500. Chân trang là mono 12px màu `#9FB0C2`. Toast là 14px đậm 600.

## Bo góc, khoảng cách, đổ bóng, lớp nổi bật

Khung nội dung rộng tối đa 1320px, padding ngang 24px, padding trên 40px ở bản đồ và 48px ở các màn khác, padding dưới 72px. Các khối chính cách nhau 28px trên bản đồ và 32px trên các màn còn lại.

Bo góc lặp lại như sau. Viên thuốc (chip lọc, hồ sơ, huy hiệu) là 999px. Thẻ và panel là 16px. Lớp chào, toast và thẻ trong là 12px. Nút, hàng bảng, ô nhập và phân đoạn là 10px. Nút trong phân đoạn là 7px. Logo là 8px. Thanh tiến độ nhỏ là 4px đến 6px. Avatar, chấm bản đồ và lõi cột là hình tròn.

Đổ bóng và lớp nổi quan sát được như sau. Nút chanh khi hover nổi lên 2px và có bóng `0 10px 30px rgba(197,243,106,.25)`; nút «Chạy đa agent» dùng bóng `0 12px 34px rgba(197,243,106,.28)`. Toast cố định giữa đáy, cách đáy 24px, bóng `0 12px 40px rgba(0,0,0,.5)`, nền `#E6EDF3`, chữ `#0A0F05`, tự tắt sau 2,4 giây. Nhóm nav và hàng đang chọn có viền trong `inset 0 0 0 1px`. Cột bản đồ có quầng sáng. Nút thành phố đang chọn có viền `#E6EDF3` và nền `#13202B`. Header dính trên nền `rgba(7,11,16,.88)` ở bản đồ và cố vấn, `rgba(7,11,16,.85)` ở các màn còn lại, có đường kẻ dưới `#1C2A36`.

Lớp nổi riêng của từng chỗ: lớp chào đầu bản đồ; ngăn kéo «Vì sao?» trượt từ phải, rộng tối đa 560px, nền `#0A1118`, đè lên màn mờ `rgba(3,6,9,.7)`; vệt quét cyan khi đang soi tin; vệt quét trên file hợp đồng; mặt hộ chiếu nền `#0B1620` với sọc chéo mờ và con dấu «ĐÃ KIỂM CHỨNG». Khi `prefers-reduced-motion` bật, mọi animation và transition bị tắt.

## Thành phần lặp lại

Logo là hình vuông 34px, bo 8px, viền `#C5F36A` dày 1.5px. Bên trong có ba chấm: hai chấm `#62D9EE` và một chấm `#C5F36A`, nối bằng đường đứt `#E6EDF3`.

Header hai tầng xuất hiện trên mọi màn: hàng nhóm 01–04, rồi hàng mục con. Viên hồ sơ Minh nằm cùng hàng nhóm.

Chip lọc là nút bo tròn. Chip đang bật đảo thành nền sáng chữ tối. Trên bản đồ, chip «Data / AI» có thêm tem «BẠN». Bộ lọc phân đoạn là hộp `#0A1118` bo 10px, nút con trong suốt, nút đang chọn có nền `#13202B` và viền trong.

Thẻ thành phố xuất hiện theo hai cách. Trên bản đồ 3D, mỗi thành phố là một cột đặc, kèm nhãn nổi ghi tên và số tin hoặc phần trăm dự báo. Cột phải là panel chi tiết: vùng, tên, ba số (tin nay, tăng/năm, lương trung vị), rồi ba tab «Cơ cấu», «Lương», «Dự báo». Bên dưới bản đồ là bảng «Xếp hạng thành phố»: hạng, tên, vùng, thanh mức cầu, số tin, mức tăng. Bấm cột, nhãn hoặc hàng đều chọn cùng một thành phố.

Lương là một trục ngang. Hộp bo góc là khoảng phân vị. Vạch dày là trung vị. Khi số tin công khai lương dưới 30, trục biến mất và hiện hộp nét đứt màu hổ phách. Trên màn lương, trục còn có P10 và P90, thang 0–100 triệu, cộng biểu đồ 12 tuần. Trên phòng tập thương lượng, trục 0–40 triệu có hộp P25–P75, vạch trung vị, mốc «OFFER» và mốc «BẠN».

Nút có ba kiểu. Nút đặc `#C5F36A` chữ `#0A0F05` là hành động chính («Nhận lộ trình cho thị trường này», «Chạy đa agent», «Soi tin», «Gửi agent review», «Gửi trải nghiệm»). Nút ghost trong suốt, viền `#243543`, cao 44px. Nút «Vì sao?» là viên thuốc mono nhỏ, chữ `#A8EAF5`. Công tắc là viên 52×30, bật thì nút tròn chuyển sang `#C5F36A` hoặc `#62D9EE`.

Lớp chào chỉ có trên bản đồ, mở sẵn. Đó là thẻ bo 16px, viền `#2E4456`, nền `#0D141C`, tiêu đề «Chào Minh — bắt đầu từ đâu?», ba bước, và nút «Đã hiểu».

Dải quý và biểu đồ cột mini xuất hiện ở «Xu hướng kỹ năng» (8 quý) và ở bảng hạn dùng («CẦU 8 QUÝ»). Cột tăng màu `#C5F36A`, cột giảm màu `#F5A65B`, cột đi ngang màu `#62D9EE`. Cột cuối đậm hơn cột đầu. Bản đồ còn có dải ticker chạy ngang 60 giây, tạm dừng khi hover, lặp tên kỹ năng kèm mũi tên tăng hoặc giảm.

Biểu đồ khác: cột 3D trên bản đồ Việt Nam; dòng chảy ba cột trên «Lộ trình thật»; năm thẻ agent nối về giữa trên «Cố vấn đa agent»; chấm trước/sau trên bản đồ nhỏ của «Mô phỏng Nếu–thì»; vòng điểm 0–100 trên «Soi tin» và điểm huấn luyện viên; phễu và histogram trên «Chỉ số phản hồi»; thanh chồng thực nhận / bảo hiểm / thuế trên offer; đồng hồ thời gian trên «Nhảy việc»; thanh thực nhận và để dành trên «Remote & Nhật».

## Bố cục từng màn

**Thị trường · Bản đồ nhu cầu.** Phía trên là header, rồi dải ticker kỹ năng. Trong phần chính, lớp chào nằm trên cùng khi còn mở. Tiếp theo là khối tiêu đề bên trái và ba KPI bên phải: nhãn tin, «TĂNG / NĂM» màu chanh, «LƯƠNG TV». Dòng dưới KPI ghi «Cập nhật tuần 43/2026 · [NGUỒN DỮ LIỆU] · số liệu minh họa». Hàng lọc đặt chip vai trò bên trái và bộ «TẦM NHÌN» (NAY, +6T, +12T, +18T) bên phải. Khối giữa chia hai cột: bản đồ 3D bên trái, panel thành phố bên phải. Bản đồ có nút 3D / 2D, xoay trái, xoay phải, đặt lại, và dòng «Kéo để xoay · kéo dọc để nghiêng». Kéo ngang đổi góc quay, kéo dọc đổi độ nghiêng. Sau khi mở, bản đồ tự nghiêng vào thế 3D. Chú thích: «Cột = tin hiện tại»; khi đang xem dự báo thì thêm «Khung nét đứt = dự báo». Bấm một thành phố thì cột, nhãn và hàng xếp hạng cùng được chọn, và panel phải đổi số. Ba tab đổi phần thân panel: cơ cấu vai trò cộng «KỸ NĂNG ĐƯỢC SĂN ĐÓN», hoặc trục lương, hoặc dự báo cộng «TÍN HIỆU SỚM». Nút «Nhận lộ trình cho thị trường này» trỏ sang cố vấn. Phía dưới, bảng xếp hạng nằm bên trái, khối «Xu hướng kỹ năng» (8 quý) nằm bên phải, có link «Kỹ năng của bạn còn “hạn” bao lâu?». Chọn tầm nhìn khác «NAY» thì tab panel nhảy sang «Dự báo» và số trên cột chuyển thành phần trăm cộng số tin dự báo, màu chanh.

**Thị trường · Lương & hạn dùng kỹ năng.** Tiêu đề «Lương theo tuần & hạn dùng kỹ năng» và dòng «Đọc từ tin có công khai lương. Dưới 30 mẫu, Hải Đồ ẩn con số thay vì đoán.» Khối trên chia hai: bên trái là ba nhóm lọc «KỸ NĂNG», «THÀNH PHỐ», «CẤP BẬC»; bên phải là số lương lớn, huy hiệu độ tin cậy, «n = … tin có công khai lương», trục phân vị, bốn ô P10 P25 P75 P90, và biểu đồ «TRUNG VỊ 12 TUẦN GẦN NHẤT». Bấm chip thì toàn bộ khối phải đổi theo. Khối dưới là «Kỹ năng của Minh còn “hạn” bao lâu?», công tắc «Cảnh báo hằng tháng» bật sẵn, bảng kỹ năng bên trái và panel chi tiết bên phải. Bấm một hàng kỹ năng thì panel phải đổi. Nếu kỹ năng có lối chuyển, panel hiện hộp «LỐI CHUYỂN ĐỀ XUẤT» và link «Mô phỏng lối chuyển này».

**Thị trường · Lộ trình thật.** Tiêu đề «Lộ trình thật của người giống bạn». Hàng chip «ĐIỂM XUẤT PHÁT» nằm trên biểu đồ. Biểu đồ dòng chảy có ba cột nhãn «XUẤT PHÁT», «NĂM 1–2», «NĂM 3–4». Dưới biểu đồ, danh sách «ĐIỂM ĐẾN SAU 3–4 NĂM · CHẠM ĐỂ SOI» ở bên trái; panel «CON ĐƯỜNG ĐANG SOI» ở bên phải, gồm phần trăm, thời gian trung vị, lương trung vị, số hồ sơ, «CHẶNG GIỮA PHỔ BIẾN NHẤT», «KỸ NĂNG HỌ ĐÃ BỔ SUNG», và link «Mô phỏng con đường này cho bạn». Bấm một điểm đến thì dòng chảy tới điểm đó chuyển sang màu chanh và panel phải đổi. Đổi điểm xuất phát thì biểu đồ vẽ lại và điểm đến đang soi về mục đầu.

**Phát triển · Cố vấn đa agent.** Tiêu đề «Cố vấn đa agent — lộ trình 90 ngày của riêng bạn», kèm viên «5 AGENT». Bên trái là form «Hồ sơ của Minh», nhãn «DÙNG CHUNG MỌI MÀN»: mục tiêu nghề nghiệp, thanh kinh nghiệm 0–10 năm, thành phố ưu tiên, lưới kỹ năng đang có, nút «Chạy đa agent» và «Đặt lại». Bên phải là «Mạng lưới agent»: một thẻ Điều phối ở giữa, bốn thẻ ở bốn góc (Trinh sát thị trường, Phân tích kỹ năng, Kiến trúc lộ trình, Huấn luyện hồ sơ), thanh tiến độ, và hộp nhật ký `agents.log`. Bấm chạy thì các thẻ lần lượt sang «ĐANG XỬ LÝ» rồi «HOÀN TẤT», dây nối chạy, và dòng nhật ký hiện dần. Dưới 640px, sơ đồ ẩn và thay bằng danh sách. Khi chạy xong, khối «Kết quả tổng hợp» hiện năm thẻ: «Mức độ phù hợp vai trò», «Khoảng cách kỹ năng», «Lộ trình 90 ngày», «Thị trường cho bạn», «Điểm nhấn cho CV». Mỗi thẻ có nút «Vì sao?». Bấm «Vì sao?» thì nền mờ và ngăn kéo phải mở, có độ tin cậy, số nhận định giữ lại, số bị loại, công tắc «Hiện nhận định bị loại», và nút «Báo nguồn sai hoặc đã cũ». Nếu sửa hồ sơ sau khi đã chạy, một dòng hổ phách hiện: hồ sơ đã đổi, cần «Chạy lại».

**Phát triển · Mô phỏng Nếu–thì.** Tiêu đề «Mô phỏng Nếu–thì» và dòng «Thêm kỹ năng giả định vào hồ sơ của Minh — xem số tin, lương và bản đồ thay đổi trước khi bỏ công học.» Bên trái là panel «Kịch bản»: kỹ năng cố định có ổ khóa, cấp bậc, lưới «KỸ NĂNG GIẢ ĐỊNH», thanh thời gian học, nút «Xoá kịch bản». Bên phải là ba ô «TIN ĐỦ ĐIỀU KIỆN», «LƯƠNG KỲ VỌNG (TV)», «TIN MỞ / TUẦN HỌC», rồi bản đồ chấm «Trước / Sau» cạnh bảng «THAY ĐỔI THEO THÀNH PHỐ». Phía dưới, «Vai trò được mở khoá» ở trái và «Nên học gì tiếp?» ở phải. Mỗi dòng «Nên học gì tiếp?» có nút «+ Thêm». Bấm thêm hoặc bấm chip giả định thì số, chấm bản đồ và độ phủ đổi ngay. Kịch bản mở sẵn với LLM/RAG và AWS.

**Phát triển · Hộ chiếu kỹ năng.** Tiêu đề «Hộ chiếu kỹ năng». Một hàng bốn chặng «Học», «Chứng minh», «Kiểm chứng», «Ghép việc» nằm trên. Bên trái là form «Nộp bằng chứng»: ba dự án radio từ lộ trình 90 ngày, ô «LINK REPO», nút «Gửi agent review». Bên phải là panel mono «AGENT REVIEW» với năm bước. Bấm gửi thì các bước chạy lần lượt, rồi hiện rubric chấm /4 và khối kết quả. Khối kết quả có mặt hộ chiếu bên trái (tên Minh, con dấu «ĐÃ KIỂM CHỨNG», mã, QR minh họa, «Sao chép link xác minh», «Tải PDF đính kèm CV») và panel «Ghép việc lại» bên phải (trước / sau, danh sách tin vừa mở khoá kèm phần trăm). Trước khi chạy xong, hộ chiếu và khối ghép việc không hiện.

**Ứng tuyển · Soi tin.** Tiêu đề «Soi tin: có thật không, AI làm được bao nhiêu?» Ô nhập «Dán link hoặc nội dung tin tuyển dụng…» và nút «Soi tin» nằm trên. Bên trái là danh sách «TIN VỪA SOI», mỗi tin có vòng điểm. Bên phải, khi đang soi, là một panel có vệt quét và dòng bước «[n/4]». Khi không soi, panel phải có tên tin, lương, link «Công ty này phản hồi ứng viên ra sao?», nút «Báo cáo tin» và «Theo dõi», rồi hai cột: «Độ tin cậy» (vòng /100, lời khuyên, danh sách tín hiệu) và «Chỉ số ảnh hưởng AI» (thang ba vùng, đầu việc, «KỸ NĂNG BỀN NÊN ĐẦU TƯ»). Bấm một tin ở trái thì cột phải đổi theo tin đó. Với tin rủi ro cao, cột AI đổi thành hộp đỏ và không chấm đầu việc.

**Ứng tuyển · Chỉ số phản hồi nhà tuyển dụng.** Tiêu đề «Công ty nào trả lời ứng viên, công ty nào “mất hút”?» Hàng «SẮP XẾP» có ba chip. Bảng bên trên gồm công ty, hồi âm sau, tỷ lệ hồi âm, số vòng, cả quy trình, và huy hiệu. Bấm một hàng thì khối dưới đổi. Khối dưới bên trái là chi tiết: phễu trên 100 hồ sơ, histogram «THỜI GIAN ĐẾN LẦN HỒI ÂM ĐẦU TIÊN», ba ô «NÓI LƯƠNG Ở», «BÀI TEST VỀ NHÀ», «BÁO KẾT QUẢ KHI TRƯỢT», và link «Soi một tin của công ty này trước khi nộp». Bên phải là form «Đóng góp trải nghiệm», nhãn «ẨN DANH». Bấm «Gửi trải nghiệm» thì form nhường chỗ cho hộp «Cảm ơn bạn!».

**Quyết định · So sánh offer & thương lượng.** Tiêu đề «So sánh offer & tập thương lượng». Phía trên là «Nhập hai offer», bộ «NGƯỜI PHỤ THUỘC» 0–3, và hai panel A (viền trên `#62D9EE`) và B (viền trên `#B9A6FF`). Mỗi panel có tên công ty, lương, Gross/Net, «Trên lương thật» hoặc «Trên mức thấp hơn», thưởng, phụ cấp, remote mỗi tuần. Chọn «Trên mức thấp hơn» thì hiện thêm ô «MỨC ĐÓNG BẢO HIỂM». Ngay dưới là dải kết luận màu xanh đậm, rồi hai cột kết quả: thực nhận mỗi năm, gross, net, thuế, thanh ba màu, và hộp cảnh báo nếu bảo hiểm đóng trên mức thấp. Một mục `<details>` «Tham số tính (kỳ tính thuế 2026)» đóng sẵn. Phía dưới là khối «PHÒNG TẬP THƯƠNG LƯỢNG»: trục thị trường, hội thoại với «Agent HR (mô phỏng)», hàng «CHỌN CÁCH TRẢ LỜI», và cột «Huấn luyện viên». Chưa chọn chiến lược thì hội thoại chỉ có một câu của HR và ba chấm chờ. Bấm một chiến lược thì câu của Minh và câu trả lời của HR hiện ra, mốc «BẠN» xuất hiện trên trục, và điểm huấn luyện viên được chấm.

**Quyết định · Nhảy việc.** Tiêu đề «Nhảy việc: “lint” hợp đồng & chọn ngày nghỉ». Hàng đếm «trái luật», «cần cân nhắc», «lưu ý», «ổn» nằm trên, cạnh nút «Tải hợp đồng khác (PDF, DOCX)». Bên trái là khung file `hop-dong-lao-dong_[cong-ty-A].pdf` với vệt quét và các dòng điều khoản. Bên phải là «AGENT PHÁP LÝ». Bấm một dòng hoặc một phát hiện thì dòng đó được chọn và, nếu không phải mục «ổn», khối phải mở thêm lý do và hộp «ĐỀ XUẤT SỬA». Phía dưới là «ĐỒNG HỒ THỜI ĐIỂM NHẢY VIỆC». Panel trái chọn loại hợp đồng, ngày chi thưởng tháng 13, điều kiện thưởng, và lương gross. Panel phải hiện bốn mốc «BẮT ĐẦU PHỎNG VẤN», «NỘP ĐƠN NGHỈ», «NGÀY LÀM CUỐI», «THƯỞNG GIỮ ĐƯỢC», rồi một trục từ 22/10/2026 đến 31/05/2027 có dải «MÙA TUYỂN CAO ĐIỂM» và các mốc HÔM NAY, PHỎNG VẤN, THƯỞNG, TẾT, NGÀY CUỐI. Đổi loại hợp đồng hoặc điều kiện thưởng thì các ngày tính lại.

**Quyết định · Remote & Nhật.** Tiêu đề «Remote nước ngoài hay onsite Nhật — có thật sự hơn ở nhà?», kèm hình quả địa cầu nhỏ ba chấm nối nét đứt. Ba panel nhập liệu nằm ngang: A «LÀM TRONG NƯỚC» viền `#62D9EE`, B «REMOTE CHO CÔNG TY NƯỚC NGOÀI» viền `#C5F36A`, C «ONSITE NHẬT BẢN» viền `#B9A6FF`. B có công tắc Freelance hoặc EOR và múi giờ Châu Á – Úc, Châu Âu, Mỹ. Khối dưới bên trái là «Quy về cùng thước đo», mỗi phương án có thanh thực nhận, thanh để dành, và tem «ĐỂ DÀNH NHIỀU NHẤT» trên phương án cao nhất. Bên phải là bảng «Những thứ không có trên bảng lương» với ký hiệu ●●●, ●●○, ●○○. Phía cuối là «Lộ trình BrSE — kỹ sư cầu nối thị trường Nhật», năm thẻ N5→N4, N3, N2, BrSE, ONSITE. Sửa ô nhập thì thanh và tem cập nhật ngay.

## Microcopy đáng giữ, nguyên văn ngắn

- «HẢI ĐỒ·IT»
- «Chào Minh — bắt đầu từ đâu?»
- «Nhu cầu tuyển dụng IT, hôm nay và 18 tháng tới.»
- «Đang lọc theo mục tiêu của bạn: Data / AI. Kéo tầm nhìn để xem dự báo; chạm vào một thành phố để xem cơ cấu, lương và tín hiệu sớm.»
- «Cột = tin hiện tại»
- «Khung nét đứt = dự báo»
- «Kéo để xoay · kéo dọc để nghiêng»
- «✓ = bạn đã có»
- «Chỉ có … tin công khai lương — dưới 30 mẫu, Hải Đồ không hiển thị con số.»
- «Không có tin nào khớp bộ lọc»
- «Không tải được dữ liệu thị trường»
- «Kỹ năng của bạn còn “hạn” bao lâu?»
- «Đọc từ tin có công khai lương. Dưới 30 mẫu, Hải Đồ ẩn con số thay vì đoán.»
- «Chưa đủ dữ liệu»
- «Kỹ năng của Minh còn “hạn” bao lâu?»
- «“Nửa đời” = thời gian ước tính để nhu cầu giảm còn một nửa nếu xu hướng giữ nguyên.»
- «Thêm kỹ năng giả định vào hồ sơ của Minh — xem số tin, lương và bản đồ thay đổi trước khi bỏ công học.»
- «Nên học gì tiếp?»
- «Cố vấn đa agent — lộ trình 90 ngày của riêng bạn»
- «Mọi kết quả đều có nút Vì sao? để xem nguồn.»
- «Vì sao?»
- «Hiện nhận định bị loại»
- «Báo nguồn sai hoặc đã cũ»
- «Hồ sơ đã thay đổi so với lần chạy trước — bấm “Chạy lại” để các agent cập nhật kết quả.»
- «Soi tin: có thật không, AI làm được bao nhiêu?»
- «Dán link hoặc nội dung tin tuyển dụng…»
- «Không phân tích tin này: agent kiểm định đã gắn cờ rủi ro cao. Đừng nộp hồ sơ hay chuyển tiền trước khi xác minh.»
- «Điểm tin cậy là cảnh báo tham khảo, không phải kết luận pháp lý.»
- «Công ty nào trả lời ứng viên, công ty nào “mất hút”?»
- «Chỉ hiển thị công ty có từ 20 trải nghiệm trở lên.»
- «So tiền thật về tay theo biểu thuế 2026 — và soi công ty đóng bảo hiểm trên lương thật hay mức thấp hơn.»
- «Tập với agent HR trước khi trả lời thật.»
- «Kết quả là ước tính tham khảo, không thay thế tư vấn thuế.»
- «Tính toán tham khảo, không phải tư vấn thuế hay pháp lý.»
- «Nhảy việc: “lint” hợp đồng & chọn ngày nghỉ»
- «Gợi ý tham khảo, không phải tư vấn pháp lý. Điều khoản quan trọng nên hỏi luật sư.»
- «Nộp đơn ngày nào là “đẹp” nhất?»
- «Remote nước ngoài hay onsite Nhật — có thật sự hơn ở nhà?»
- «Những thứ không có trên bảng lương»
- «●●● tốt · ●●○ trung bình · ●○○ bất lợi»
- «Số liệu, tín hiệu và dự báo là minh họa cho bản thiết kế — thay bằng [NGUỒN DỮ LIỆU TUYỂN DỤNG].»

Chân trang các màn đều nhắc dữ liệu là minh họa. Số phiên bản ghi trên chân trang là v0.4 ở bản đồ và cố vấn, v0.3 ở lộ trình thật, chỉ số phản hồi, nhảy việc và Remote & Nhật, v0.2 ở các màn còn lại.

## Trạng thái quan sát được

Bản đồ có bốn trạng thái dữ liệu, mặc định là có dữ liệu. Trạng thái đang tải hiện khối xương shimmer. Trạng thái lỗi hiện «Không tải được dữ liệu thị trường» và nút «Thử lại», nút này chỉ mở toast «Đang kết nối lại nguồn dữ liệu…». Trạng thái rỗng hiện «Không có tin nào khớp bộ lọc» và nút «Bỏ lọc», nút này chọn lại «Tất cả». Lớp chào mở sẵn và biến mất sau «Đã hiểu». Thành phố, vai trò, tầm nhìn và tab có trạng thái chọn. Tab lương có trạng thái đủ mẫu và trạng thái ẩn số. Tab dự báo có trạng thái có tín hiệu và trạng thái «Chưa ghi nhận tín hiệu đáng kể cho thành phố này.» Bản đồ có thế 3D, thế 2D, và trạng thái đang kéo.

Màn lương ẩn số và hiện «Chưa đủ dữ liệu» khi số tin dưới ngưỡng mẫu, mặc định 30. Huy hiệu có ba chữ: «ĐỘ TIN CẬY CAO» từ 100 tin, «ĐỘ TIN CẬY TRUNG BÌNH» khi đủ ngưỡng nhưng dưới 100, và «DƯỚI NGƯỠNG … MẪU» khi chưa đủ. Hàng kỹ năng có trạng thái chọn. Công tắc cảnh báo bật sẵn. Hộp lối chuyển chỉ hiện khi kỹ năng có hướng chuyển.

Lộ trình thật có chip xuất phát đang chọn và điểm đến đang soi. Nhóm dưới 20 người được chân trang nói là không hiển thị; trong dữ liệu mẫu không có nhóm nào dưới ngưỡng đó đang bị giấu trên màn.

Cố vấn có ba pha: sẵn sàng, đang chạy, hoàn tất. Lúc chưa chạy, khối kết quả là khung nét đứt «Hồ sơ của Minh đã sẵn sàng. Bấm “Chạy đa agent” để nhận kế hoạch 90 ngày.» Lúc đang chạy, khung đó đổi câu và nút ghi «Các agent đang làm việc…». Sau khi chạy, nếu hồ sơ đổi, hiện cảnh báo stale. Ngăn «Vì sao?» đóng sẵn. Công tắc nhận định bị loại bật sẵn. Nhận định bị loại có gạch ngang và nền hổ phách.

Mô phỏng Nếu–thì cập nhật ngay khi thêm hoặc bớt kỹ năng. «Xoá kịch bản» xóa hết kỹ năng giả định và các ô đổi thành «Chưa thay đổi» hoặc «—».

Hộ chiếu trước khi gửi chỉ hiện form và danh sách bước ở trạng thái chờ. Khi đang review, một bước quay, các bước trước có dấu tick. Khi xong, rubric, mặt hộ chiếu và khối «Ghép việc lại» cùng xuất hiện. Nút sao chép và tải PDF chỉ mở toast.

Soi tin mặc định đang mở một tin trong danh sách, không ở trạng thái đang quét. Bấm «Soi tin» thì panel phải đổi thành vệt quét bốn bước, rồi nhảy sang tin kế tiếp. Tin điểm cao dùng chữ «ĐÁNG TIN» màu chanh, tin giữa dùng «CẦN THẬN TRỌNG» màu hổ phách, tin thấp dùng «RỦI RO CAO» màu `#F0605D`. Tin rủi ro cao ẩn phần tách đầu việc.

Chỉ số phản hồi có hàng đang chọn, ba kiểu sắp xếp, và trạng thái đã gửi của form ẩn danh.

Offer tính lại khi sửa ô. Cảnh báo hụt bảo hiểm chỉ hiện khi chọn «Trên mức thấp hơn». Tham số thuế nằm trong mục đóng. Phòng tập ở trạng thái chưa chọn cho đến khi bấm một trong ba cách trả lời. Huấn luyện viên trước đó hiện «—» và dòng «Chọn một cách trả lời để agent chấm điểm và góp ý.»

Nhảy việc mở sẵn một điều khoản được chọn. Mục «ổn» không có khối đề xuất sửa. Bấm tải hợp đồng chỉ mở toast, không mở hộp chọn tệp trong prototype. Các ngày trên đồng hồ đổi theo loại hợp đồng và điều kiện thưởng.

Remote & Nhật không có trạng thái rỗng. Tem «ĐỂ DÀNH NHIỀU NHẤT» dán lên phương án có số để dành cao nhất. Đổi múi giờ thì dòng ghi chú giờ làm và cột «Giờ làm việc» trong bảng đổi theo.

## Màn hoặc khối có trong prototype mà tên gợi việc ghép việc, đánh giá nhà tuyển dụng, agent pháp lý, Remote/Nhật, thương lượng, lương phân vị, đa agent

Chỉ liệt kê những gì đang có trên prototype.

Ghép việc: artboard «Phát triển · Hộ chiếu kỹ năng». Đoạn mở đầu kết bằng «rồi ghép việc lại». Chặng thứ tư ghi «Ghép việc» và «Hộ chiếu mở thêm cơ hội». Panel «Ghép việc lại», nhãn «BƯỚC 4 / 4», so «TRƯỚC» và «SAU» theo «tin phù hợp ≥ 70%», rồi danh sách tin kèm phần trăm khớp.

Đánh giá nhà tuyển dụng: artboard «Ứng tuyển · Chỉ số phản hồi nhà tuyển dụng». Thanh con ghi «Chỉ số phản hồi nhà tuyển dụng». Bảng có cột «ĐÁNH GIÁ» với huy hiệu «PHẢN HỒI TỐT», «TRUNG BÌNH», «HAY MẤT HÚT». Chip sắp xếp gồm «Hồi âm nhanh nhất», «Ít “mất hút” nhất», «Quy trình ngắn nhất». Từ màn soi tin có link «Công ty này phản hồi ứng viên ra sao?».

Agent pháp lý: trên artboard «Quyết định · Nhảy việc», cột phải ghi «AGENT PHÁP LÝ». Toast khi bấm tải hợp đồng ghi «agent pháp lý sẽ đọc trong khoảng 30 giây.» Cột này gạch điều khoản theo Bộ luật Lao động 2019 và đưa «ĐỀ XUẤT SỬA». Dòng dưới cột ghi đây là gợi ý tham khảo, không phải tư vấn pháp lý. Chân trang màn soi tin ghi điểm tin cậy không phải kết luận pháp lý. Chân trang màn offer ghi tính toán không phải tư vấn thuế hay pháp lý.

Remote/Nhật: artboard «Quyết định · Remote & Nhật», thanh con «Remote & Nhật», tệp `Global.dc.html`. Tiêu đề màn hỏi remote nước ngoài hay onsite Nhật. Ba phương án A trong nước, B remote, C onsite Nhật, cộng khối «Lộ trình BrSE». Trên «Lộ trình thật», một điểm đến mẫu là «Remote / Freelance quốc tế». Trên offer, mỗi offer có ô «REMOTE / TUẦN».

Thương lượng: tên artboard «Quyết định · So sánh offer & thương lượng». `<title>` là «So sánh offer và tập thương lượng». Khối dưới ghi «PHÒNG TẬP THƯƠNG LƯỢNG» và «Tập với agent HR trước khi trả lời thật.» Có «Agent HR (mô phỏng)» và «AGENT COACH». Ba cách trả lời: «Neo theo dữ liệu P75», «Đổi lấy lợi ích khác», «Chấp nhận ngay».

Lương phân vị: tab «Lương» trên bản đồ vẽ P25, trung vị, P75 và «n = …». Màn «Thị trường · Lương & hạn dùng kỹ năng» vẽ P10, P25, trung vị, P75, P90. Phòng tập thương lượng vẽ hộp P25–P75, vạch trung vị, mốc OFFER và mốc BẠN, với chú thích «Hộp: P25 16 – P75 26 · vạch: trung vị 20».

Đa agent: tên artboard «Phát triển · Cố vấn đa agent», tiêu đề trang «Cố vấn nghề nghiệp đa agent», tiêu đề tài liệu gốc có «Cố vấn đa agent». Trên màn này có «5 AGENT», nút «Chạy đa agent», thẻ Điều phối ghi «ORCHESTRATOR + PHẢN BIỆN», và bốn agent Trinh sát thị trường, Phân tích kỹ năng, Kiến trúc lộ trình, Huấn luyện hồ sơ. Ngăn «Vì sao?» ghi «AGENT PHẢN BIỆN». Màn hộ chiếu có «Gửi agent review» và «AGENT REVIEW». Màn soi tin có «AGENT KIỂM ĐỊNH» và «AGENT CHỈ SỐ AI». Màn offer có «Agent HR (mô phỏng)» và «AGENT COACH».

## Số liệu mẫu trong prototype

Mọi số dưới đây là số mẫu trong file, không phải số thật. Các màn đều ghi «số liệu minh họa», «dữ liệu minh họa», hoặc «ví dụ minh họa».

Bản đồ, vai trò «Tất cả», số tin đang mở mẫu: Hà Nội 3.960, Hải Phòng 420, Đà Nẵng 1.140, Quy Nhơn 260, Nha Trang 150, TP. Hồ Chí Minh 4.820, Cần Thơ 210. Mức tăng mỗi năm mẫu: Hà Nội 9%, Hải Phòng 21%, Đà Nẵng 17%, Quy Nhơn 14%, Nha Trang 6%, TP. Hồ Chí Minh 12%, Cần Thơ 8%. Lương trung vị IT mẫu, triệu đồng mỗi tháng: Hà Nội 26, Hải Phòng 19, Đà Nẵng 22, Quy Nhơn 18, Nha Trang 16, TP. Hồ Chí Minh 28, Cần Thơ 15. Tỷ trọng Data/AI mẫu: Hà Nội 16%, Hải Phòng 12%, Đà Nẵng 12%, Quy Nhơn 34%, Nha Trang 8%, TP. Hồ Chí Minh 18%, Cần Thơ 10%. Dòng cập nhật ghi tuần 43/2026. Xu hướng 8 quý mẫu: LLM / RAG +64%, Kubernetes +22%, Go +18%, TypeScript +15%, Python +12%, Rust +9%, PHP −6%. Kỹ năng hồ sơ Minh dùng để đánh dấu «đã có» là Python, SQL, Git, JavaScript, Docker. Ngưỡng ẩn lương là dưới 30 tin công khai lương. Số tin có lương được tính bằng khoảng 38% số tin của vai trò tại thành phố đó.

Màn lương, mức lương gốc theo cấp mẫu: Fresher 11, Junior 18, Mid 32, Senior 50 triệu. Hệ số thành phố mẫu: toàn quốc 1, Hà Nội 0,97, TP.HCM 1,04, Đà Nẵng 0,86, Hải Phòng 0,80, Quy Nhơn 0,78, Cần Thơ 0,72. Nha Trang có trên bản đồ nhưng không có trong hàng chip thành phố của màn này. Ngưỡng mẫu mặc định là 30. Huy hiệu cao từ 100 tin. Đang mở sẵn: Python, Hà Nội, Junior, và hàng jQuery. Lối chuyển mẫu: jQuery sang React + TypeScript, 55% tái dùng, 6 tuần; PHP sang Node.js + TypeScript, 60% tái dùng, 5 tuần.

Lộ trình thật, nhóm mẫu: «Junior PHP · giống bạn» với 1.240 hồ sơ ẩn danh, và «Fresher QA» với 860 hồ sơ, cả hai ghi 2019–2026. Một đường mẫu từ Junior PHP tới Senior Backend là 3,5 năm, lương «15 → 40 tr ₫». Chân trang nói nhóm dưới 20 người không hiển thị.

Cố vấn mở sẵn mục tiêu Data / AI Engineer, 2 năm, Hà Nội, và năm kỹ năng Python, SQL, Git, JavaScript, Docker. Nhật ký mẫu nói đối chiếu 14 nguồn, giữ 9 nhận định, loại 5. Các truy vấn trong ngăn «Vì sao?» là số mẫu, ví dụ 1.284 tin, 61% tin nhắc Docker, 3.120 tin Data/AI, +64% LLM/RAG, 260 tin IT tại Quy Nhơn, 34% Data/AI, 8.780 tin tại Hà Nội và TP.HCM, và 18 tin RAG có lương bị loại vì dưới 30 mẫu. Mã hồ sơ mẫu là HD-2026-7F3A.

Mô phỏng Nếu–thì mở sẵn cấp Junior và hai kỹ năng giả định LLM/RAG (4 tuần) và AWS (4 tuần). Lương gốc mẫu: Fresher 10, Junior 16, Mid 28, Senior 45 triệu, rồi cộng phần thưởng kỹ năng. Cùng bảy thành phố và cùng số tin với bản đồ.

Hộ chiếu mở sẵn dự án «Chatbot RAG trên bộ tài liệu tiếng Việt». Trước khi kiểm chứng, số tin phù hợp mẫu là 1.120. Ba mức tăng mẫu là +140, +310 và +460 tin. Ba tin vừa mở khoá của dự án RAG mẫu là AI Engineer (LLM) tại Quy Nhơn 88%, Backend Engineer – AI Platform tại TP.HCM 80%, Applied ML Engineer tại Hà Nội 76%. Mã xác minh mẫu là HD-2026-7F3A-91C2, cấp ngày 22/10/2026. Mức hộ chiếu sẵn có: Python Vững, SQL Vững, Git Thành thạo, Docker Khá, đều ghi đã kiểm chứng năm 2026.

Soi tin có bốn tin mẫu. Backend Engineer (Go), [Công ty Fintech A], TP.HCM, 35–50 tr, điểm 92, «ĐÁNG TIN». Data Analyst, [Công ty Logistics B], Hà Nội, 18–25 tr, điểm 58, «CẦN THẬN TRỌNG», đang được chọn khi mở màn. Tin «Lập trình viên làm tại nhà — không cần kinh nghiệm», điểm 12, «RỦI RO CAO». QA Automation Engineer, [Công ty Phần mềm C], Đà Nẵng, 20–30 tr, điểm 84. Ngưỡng chữ: từ 75 là đáng tin, từ 40 là cần thận trọng, dưới 40 là rủi ro cao.

Chỉ số phản hồi có bảy công ty đặt tên trong ngoặc vuông. Ví dụ [Công ty Fintech A] tại TP.HCM: n = 214, hồi âm sau 3 ngày, tỷ lệ 88%, 3 vòng, cả quy trình 21 ngày. [Công ty AI E] tại Quy Nhơn: n = 37. Phễu luôn bắt đầu từ 100 hồ sơ nộp. Màn nói chỉ hiện công ty từ 20 trải nghiệm.

Offer mở sẵn offer A «[Công ty A]» 24 triệu gross, đóng bảo hiểm trên lương thật, thưởng 1 tháng, phụ cấp 1 triệu, remote 2 ngày/tuần. Offer B «[Công ty B]» 27 triệu gross, đóng trên mức 5,31 triệu, không thưởng, không phụ cấp, không remote, 0 người phụ thuộc. Giảm trừ mẫu: bản thân 15,5 triệu/tháng, người phụ thuộc 6,2 triệu/tháng. Người lao động đóng 10,5%. Trần mẫu: BHXH/BHYT 50,6 triệu, BHTN 106,2 triệu. Phòng tập dùng thị trường mẫu Data Engineer, Junior, Hà Nội, n = 186, P25 16 triệu, trung vị 20 triệu, P75 26 triệu, offer đang thảo luận 24 triệu. Ba điểm huấn luyện viên mẫu là 92, 76 và 45.

Nhảy việc mở sẵn lương gross 18 triệu, hợp đồng không thời hạn (báo trước 45 ngày), thưởng tháng 13 vào 29/01/2027, điều kiện phải còn làm việc. Mốc «hôm nay» trên trục là 22/10/2026. Mùa tuyển mẫu từ 15/02/2027 đến 30/04/2027. Tết mẫu là 06/02/2027. Phỏng vấn được đặt khoảng 6 tuần trước ngày nộp đơn.

Remote & Nhật mở sẵn: lương trong nước 18 triệu gross, chi phí sống 12 triệu; remote 1.200 USD, tỷ giá 26.000 đồng, freelance, chi phí tự lo 2 triệu, múi giờ Châu Á – Úc; Nhật 280.000 JPY, tỷ giá 170 đồng, khấu trừ 22%, sinh hoạt 160.000 JPY. Lộ trình BrSE mẫu: N5→N4 khoảng 4–6 tháng, N3 khoảng 6–9 tháng, N2 khoảng 9–12 tháng, BrSE kèm 2–3 năm kinh nghiệm.
