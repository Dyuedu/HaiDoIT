---
name: Hải Đồ IT
description: Hành vi của bảng điều khiển số liệu kỹ năng. Một bề mặt web, không tài khoản, hồ sơ nằm trong trình duyệt.
status: final
created: 2026-11-03
updated: 2026-11-05
sources:
  - '{planning_artifacts}/prds/prd-HaiDoIT-2026-11-02/prd.md'
  - '{planning_artifacts}/prds/prd-HaiDoIT-2026-11-02/addendum.md'
  - '{planning_artifacts}/architecture/architecture-HaiDoIT-2026-11-03/ARCHITECTURE-SPINE.md'
---

# Hải Đồ IT — Experience Spine

Hình thức nhìn nằm ở `DESIGN.md`. Spine này chỉ giữ hành vi. Khi artboard lệch spine, làm theo spine. Danh sách lệch nằm một lần ở Information Architecture.

## Foundation

Một bề mặt web. Bối cảnh kể trong prompt thiết kế là laptop. Không có hệ thống UI shadcn, không có tài khoản, không có ô chat, không có hội thoại với agent.

`DESIGN.md` là hợp đồng hình. Hồ sơ kỹ năng và vai trò mục tiêu nằm trong trình duyệt. Cố vấn và Soi tin đọc chung một hồ sơ. Xoá hồ sơ xoá dữ liệu Hải Đồ IT trong trình duyệt, gồm mã phiên ẩn danh.

Ngôn ngữ giao diện là tiếng Việt. Tên kỹ năng giữ dạng tiếng Anh đã chuẩn hoá (Docker, Spring Boot).

## Information Architecture

Mở ứng dụng thì vào Bản đồ. Nav ứng dụng có đúng bốn mục: Bản đồ, Insights, Cố vấn, Soi tin.

Trang chính sách và trang vai trò đứng riêng: không có nav bốn mục, đọc được không cần tài khoản. Chân trang của mọi màn ứng dụng có liên kết “Chính sách dữ liệu”.

| # | Artboard | Tên | Vào từ | Việc của màn |
|---|---|---|---|---|
| 1 | `ban-do` | Bản đồ nhu cầu | Mở ứng dụng | Tỷ trọng toàn quốc của vai trò đang chọn, theo Hà Nội, TP.HCM, Đà Nẵng. Có lối 3D, biểu đồ 2D, bảng |
| 2 | `ban-do-ha-noi` | Bảng chi tiết thành phố | Bấm cột Hà Nội | Tỷ trọng vai trò trong thành phố, kỹ năng hàng đầu, rồi sang Cố vấn |
| 3 | `co-van-chung` | Lộ trình chung | Nav, hoặc nút từ bảng thành phố | Đồ thị nút của ô thống kê khi chưa có hồ sơ |
| 4 | `co-van-cv` | Đồng ý và tải CV | “Đối chiếu với CV của tôi” | Ô đồng ý, rồi kéo thả PDF hoặc DOCX |
| 5 | `co-van-dang-doc` | Đang đọc | Sau khi gửi CV hợp lệ | Liệt kê từng bước, trong khoảng 8–10 giây |
| 6 | `co-van-khoang-trong` | Xác nhận khoảng trống | Hết bước đọc | Ba lựa chọn cho mỗi khoảng trống; lưu tóm tắt chỉ khi đã xác nhận hết |
| 7 | `co-van-ky-nang` | Chi tiết một kỹ năng | Bấm một nút kỹ năng | Lời dẫn không có số; số ở ô riêng; tài liệu miễn phí đã kiểm duyệt |
| 8 | `co-van-luu` | Lưu hồ sơ và tải tóm tắt | Nút lưu sau khi xác nhận hết | Hồ sơ trong trình duyệt; tóm tắt hai phần |
| 9 | `cv-anh-scan` | CV ảnh scan | PDF trích được dưới 30 ký tự | Báo lý do trong 1 giây và ba lối thoát |
| 10 | `soi-tin-dan` | Soi tin | Nav | Một ô dán, nút “Soi tin”. Không ô chat |
| 11 | `soi-tin-ket-qua` | Kết quả soi tin | Sau “Soi tin” | Mức khớp, phân vị, dấu hiệu cần kiểm tra. Đổi ô thống kê không dán lại |
| 12 | `insights` | Insights | Nav | Thẻ câu mẫu. Thẻ n < 30 chỉ ghi chú, không hiện tỷ lệ |
| 13 | `co-van-khong-cv` | Tự chọn, không CV | “Chưa có CV”, hoặc từ Insights | Tự bật kỹ năng đã có. Đổi vai trò thì tô kỹ năng trùng và có dòng đếm |
| 14 | `chinh-sach-du-lieu` | Chính sách dữ liệu | Chân trang, hoặc URL riêng | Mục đích, nguồn, mức công bố, dữ liệu không lưu, email gỡ |
| 15 | `trang-vai-tro` | Trang một vai trò | URL công khai | Một ô: vai trò đó × mọi cấp bậc × toàn quốc |

Hình:

- `imports/prototype-ban-do-co-van.html` — ngôn ngữ hình cũ (nền, chữ, font, nút). Không phải 15 màn v1, và không vẽ lại 11 màn bị loại.
- `mockups/gallery.html` — bản xuất 15 màn đã sửa. File người dùng xuất vẫn nằm ở thư mục UX, tên có đuôi `(1).html`.
- `mockups/screens/01.html` đến `mockups/screens/15.html` — từng màn, cùng thứ tự bảng trên.

**Spine thắng mock.** Những chỗ artboard đang lệch, làm theo các dòng sau, không theo chữ in trên hình:

- Ngưỡng nhóm kỹ năng lấy từ bảng thuật ngữ: cốt lõi ≥ 30% (θ_core), thường gặp từ 10% đến dưới 30% (θ_common), riêng của công ty dưới 10%. Artboard in “Cốt lõi ≥ 60% · Thường gặp 30–59% · Riêng của công ty < 30%”, và bước đọc CV ghi “ngưỡng 60% và 30%”.
- Bản đồ: cột chỉ Hà Nội, TP.HCM, Đà Nẵng. Chiều cao là tỷ trọng toàn quốc của vai trò đang chọn. “Khác” không phải cột; chú thích kèm tỷ trọng. Cột n < 30 vẫn đứng, mờ (opacity 0,4 trên artboard). Nhãn đứng: “Cỡ mẫu nhỏ (n = X < 30): số liệu chỉ để tham khảo”. Phần trăm của cột đó chỉ khi trỏ, chạm, hoặc focus (lớp `.rev`). Ba lưu ý độ phủ của FR-36 luôn nhìn thấy, kèm nguồn đang bật và ngày snapshot. FR-33 đặt vai trò mặc định là “Tất cả”; artboard mở sẵn Backend. Artboard cộng “cột + Khác = 100%” và ghi “Khác gộp các tỉnh còn lại”. FR-33 còn một phần “không xác định thành phố” trong phép cộng 100%. [NOTE FOR UX] Chưa chốt phần không xác định thành phố đứng riêng hay nằm trong Khác.
- Ba lưu ý FR-36, luôn nhìn thấy trên Bản đồ: tin tuyển dụng không đồng nghĩa với vị trí đang thực sự cần người; dữ liệu nghiêng về thành phố lớn và công ty lớn; con số lương chỉ phản ánh những tin có công bố lương. Ba câu trên artboard Bản đồ là câu khác.
- Lộ trình chung không vẽ nhóm riêng của công ty, trừ kỹ năng nền tảng với nhãn “Kỹ năng nền tảng (cần cho X)”. Artboard `co-van-chung` vẫn có cột “RIÊNG CỦA CÔNG TY” và nút Kafka.
- Màn chi tiết kỹ năng là kỹ năng người dùng vừa bấm. Artboard đang minh họa Docker. Trong cao trào đã chốt, phần còn phải học là CI/CD rồi Redis, nên Docker trên artboard không phải kỹ năng còn lại của hành trình.
- Soi tin: D1 là số kỹ năng yêu cầu cao hơn 90% số tin cùng ô; D2 là hơn một nửa kỹ năng đã nhận diện thuộc nhóm riêng của công ty. Cả hai là việc cần kiểm tra, không phải kết luận tin giả. Artboard gán D1 cho email cá nhân và D2 cho tin đăng lại, và có cụm “tin giả”. Câu dưới các dấu hiệu lấy từ FR-31: “Dấu hiệu là gợi ý để bạn tự kiểm tra. Đa số tin bị gắn dấu hiệu vẫn là tin thật.”
- Mức khớp đã chốt của UJ-2 là 89%, dòng “4/4 cốt lõi, 2/2 thường gặp, 0/2 riêng của công ty”. Bộ kỹ năng minh họa trên artboard kết quả không ra hai con số này.

## Voice and Tone

Giọng microcopy. Giọng hình nằm ở `DESIGN.md`.

Nêu dữ kiện. Mọi số kèm n và ngày snapshot. Thiếu dữ liệu thì viết “chưa đủ dữ liệu”, không đoán, không để trống. Không khuyên nộp hay không nộp. Không kết luận tin thật hay giả. Không dùng các từ “lừa đảo”, “tin giả”, “tin ma”. Nhóm thường gặp được nói là “nên học sau khi đã nắm các kỹ năng cốt lõi”. Không câu nào khuyên bỏ qua một kỹ năng.

| Viết | Không viết |
|---|---|
| “Cỡ mẫu nhỏ (n = 23 < 30): số liệu chỉ để tham khảo.” | Xoá phần trăm và để cột không nhãn |
| “Chưa đủ dữ liệu (n = 21).” | Một tỷ lệ kèm lời xin lỗi |
| “Chưa đủ dữ liệu (X/30 tin có lương).” | Một mức lương phỏng đoán |
| “Tin không công bố khoảng lương. Bạn có thể tham khảo phân vị lương của vai trò này (nếu đủ mẫu) khi đàm phán.” | Coi việc không ghi lương là một dấu hiệu |
| “Bạn đáp ứng 6/8 kỹ năng trong tin này: 4/4 cốt lõi, 2/2 thường gặp, 0/2 riêng của công ty.” | “Nên nộp” hoặc “bỏ qua tin này” |
| “Có N kỹ năng trong lộ trình này trùng với hồ sơ của bạn.” | “Lộ trình chuyển việc” |
| “Lộ trình học có thứ tự cho vai trò này đang được biên soạn.” | Một đồ thị trống không câu giải thích |

Câu trên thẻ Insights là mẫu có số điền từ bảng, không phải đoạn văn viết tự do. Artboard đang dùng các mẫu: “[vai trò]: [x]% tin nhận Intern hoặc Fresher (n = [n])” và “Trong [n] tin có [A], [x]% cũng nhắc [B]”.

## Component Patterns

Hành vi. Hình nằm ở `DESIGN.md`.

| Component | Dùng ở | Quy tắc |
|---|---|---|
| `app-header` | Màn 1–13 | Bốn mục. Trang đang mở mang `aria-current="page"`. Màn 14 và 15 không có nav này. |
| `profile-chip` | Màn 1–13 | Ba câu đã thấy: “Chưa có hồ sơ”; “Hồ sơ tạm · chưa lưu”; “Hồ sơ: Java Backend · trong trình duyệt”. Bấm vào mở màn lưu hồ sơ. |
| `button-primary` | Việc chính của màn | Một việc chính. Tắt khi điều kiện chưa đủ, kèm câu giải thích. Không dùng cho liên kết phụ. |
| `button-ghost` | Việc phụ | Quay lại, chọn file khác, tải bản `.md`, soi tin khác. |
| `button-danger` | Màn lưu hồ sơ | “Xoá hồ sơ khỏi trình duyệt”. Xoá hồ sơ kỹ năng, vai trò mục tiêu, và mã phiên ẩn danh. |
| `chip` | Bản đồ, Cố vấn, tự chọn | `aria-pressed`. Trên Bản đồ, một vai trò được chọn. Trên tự chọn, mỗi kỹ năng bật hoặc tắt. |
| `segmented-control` | Bản đồ; tự chọn | Bản đồ: “3D”, “Biểu đồ 2D”, “Bảng”, cùng số liệu. Tự chọn: đổi vai trò mục tiêu. |
| `icon-button` | Bản đồ | Xoay trái 30 độ, xoay phải 30 độ, đặt lại góc nhìn. Có `aria-label`. Không thay cho việc kéo. |
| `panel` | Hầu hết màn ứng dụng | Khối nội dung. Không tự mở, không tự đóng. |
| `kicker` | Meta | Nhãn ngắn. Không chứa câu khuyên. |
| `data-table` | Bảng thành phố, trang vai trò, bảng Bản đồ | Mỗi số có n. Ô n < 30 trên bảng thành phố không hiện tỷ lệ, chỉ “chưa đủ dữ liệu”. |
| `site-footer` | Mọi màn ứng dụng | Liên kết chính sách luôn có. |
| `map-column` | Bản đồ 3D | Bấm Hà Nội mở bảng thành phố. Kéo để xoay, kéo dọc để nghiêng. Cột n < 30 vẫn bấm được. |
| `meter` | 2D, bảng thành phố, Insights, trang vai trò | Bề rộng là tỷ trọng hoặc tỷ lệ xuất hiện. Trên Bản đồ, thanh của cột n < 30 vẫn có bề rộng, phủ sọc, phần trăm ẩn đến khi trỏ, chạm hoặc focus. Trên bảng thành phố, Insights và trang vai trò, n < 30 thì không vẽ tỷ lệ. |
| `level-bar` | Cố vấn khi quay về ô rộng hơn; trang vai trò khi n ≥ 30 | Kèm số đếm từng cấp và n, ngày. |
| `skill-node` | Lộ trình chung; tự chọn | Bấm mở chi tiết kỹ năng. Nút ghi tỷ lệ xuất hiện và nhóm kỹ năng. Kỹ năng đã có được tô và không nằm trong danh sách còn phải học. |
| `select` | Lộ trình chung; kết quả Soi tin | Đổi vai trò hoặc ô đối chiếu. Kết quả tính lại, không tải lại trang, không dán lại tin. |
| `checkbox` | Tải CV | Chưa chọn thì không gửi. Nhãn nêu văn bản CV được gửi tới nhà cung cấp dịch vụ AI bên ngoài, không lưu file gốc hay thông tin định danh, và có thống kê ẩn danh theo mã phiên. |
| `drop-zone` | Tải CV | PDF có lớp chữ hoặc DOCX, tối đa 5 MB. Kéo thả hoặc chọn file. |
| `step-list` | Đang đọc | Một dòng một bước, không một vòng xoay thay cho danh sách. Artboard liệt kê năm bước: đọc chữ trong file, gửi văn bản tới dịch vụ AI, chuẩn hoá tên kỹ năng, đối chiếu với ô thống kê, xếp khoảng trống. Câu ngưỡng ở bước cuối theo θ_core và θ_common, không theo 60% và 30%. |
| `gap-actions` | Khoảng trống | Hai nút: “Tôi chưa biết”; “Tôi đã biết, chỉ là CV chưa ghi”. Khi hồ sơ tạo từ CV, thêm lựa chọn nhỏ hơn: “CV của tôi có ghi rồi (hệ thống đọc sót)”. Đổi được lựa chọn; lựa chọn sau cùng có hiệu lực. |
| `stat-block` | Chi tiết kỹ năng | Tỷ lệ xuất hiện, n, ngày, nguồn. Tách khỏi lời dẫn. Lời dẫn không chứa số. |
| `toast` | Lưu hồ sơ; tự chọn | `aria-live="polite"`. Artboard hiện khoảng 2,4 giây: đã tạo file tóm tắt, hoặc đã lưu N kỹ năng trong trình duyệt. |
| `paste-field` | Soi tin | Một ô. Đếm ký tự. Nội dung không được lưu sau khi xử lý. |
| `match-ring` | Kết quả Soi tin | Hiện khi hồ sơ có dữ liệu. Dòng phụ là đếm thô theo nhóm. Dòng trọng số: cốt lõi 3, thường gặp 2, riêng của công ty 1. |
| `sign-card` | Kết quả Soi tin | Mỗi dấu hiệu kích hoạt: mã, dữ kiện đã kích hoạt, gợi ý để tự kiểm tra. Không phải kết luận. |
| `insight-card` | Insights | Một câu mẫu, số căn cứ kèm n và ngày, một lối sang Cố vấn hoặc Bản đồ. n < 30 thì câu “chưa đủ dữ liệu (n = X)”, không có tỷ lệ. |
| `notice` | Quay về ô rộng hơn; CV scan | `role="status"` hoặc `role="alert"`. Nêu n của ô bị thiếu, và n cùng cơ cấu cấp bậc của ô đang dùng. |
| `doc-section` | Chính sách | Năm mục đã có trên artboard: mục đích, nguồn đang dùng, công bố mức tổng hợp, CV và tin dán không lưu, yêu cầu gỡ. |

## State Patterns

| Trạng thái | Màn | Cách xử lý |
|---|---|---|
| Mở ứng dụng | `ban-do` | Vào Bản đồ. Vai trò mặc định “Tất cả”. Lối xem 3D; khi Story 1.17 chưa xong thì lối 2D, nút 3D tắt và có chú thích “Bản đồ 3D sắp có”. Chú thích nguồn, ngày snapshot, và ba lưu ý FR-36 đang hiện. |
| Đổi vai trò | `ban-do` | Chiều cao cột đổi theo tỷ trọng toàn quốc của vai trò đó. |
| WebGL không chạy | `ban-do` | Tự chuyển sang lối 2D hoặc bảng. Không màn hình lỗi. |
| Bảng thành phố | `ban-do-ha-noi` | Cơ cấu vai trò, kỹ năng hàng đầu của vai trò đang chọn, ngày snapshot. Mọi số có n. |
| Ô thành phố n < 30 | `ban-do-ha-noi` | Không hiện tỷ lệ. Chỉ “chưa đủ dữ liệu”. |
| Chưa có đồ thị học trước – học sau | `co-van-chung` | Không vẽ đồ thị. Danh sách theo nhóm cốt lõi và thường gặp, kèm tỷ lệ. Câu “Lộ trình học có thứ tự cho vai trò này đang được biên soạn”. Nút từ bảng thành phố nói cùng câu. |
| Ô vai trò × cấp n < 30 | `co-van-chung`, `soi-tin-ket-qua` | Giữ cấp bậc, quay về ô rộng hơn theo thứ tự đã định ở bảng thuật ngữ. Nhãn ghi n và cơ cấu cấp bậc. Minh họa đã chốt ở Cố vấn: Java Backend · Intern–Junior có 26 tin, dùng Backend · Intern–Junior, n = 52, cơ cấu 13 Intern, 7 Fresher, 32 Junior. |
| Hồ sơ trống | `co-van-chung` | Lộ trình chung: cốt lõi và thường gặp. Hai lối: tự chọn, hoặc đối chiếu CV. |
| Chưa đồng ý | `co-van-cv` | Nút “Đọc CV và đối chiếu” tắt. Câu “Đánh dấu ô đồng ý ở trên để tiếp tục.” |
| Đã đồng ý và đã có file | `co-van-cv` | Nút chính bật, sang màn đang đọc. |
| Đang đọc | `co-van-dang-doc` | Từng bước đổi trạng thái. Artboard chạy 8,8 giây và ghi “/ ~9 giây”, nằm trong khoảng 8–10 giây. Xong thì sang khoảng trống. |
| CV scan | `cv-anh-scan` | Dưới 30 ký tự có nghĩa. Trong 1 giây. Artboard minh họa 12 ký tự, phát hiện sau 0,4 giây, và ghi chưa gửi gì ra ngoài. Ba lối: PDF xuất từ Word, Canva hoặc Overleaf; file DOCX; tự chọn kỹ năng. v1 không chạy OCR. |
| Chưa xác nhận hết | `co-van-khoang-trong` | Nút “Lưu hồ sơ và tải bản tóm tắt” tắt. Câu “Còn {số} khoảng trống chưa xác nhận.” |
| Đã xác nhận hết | `co-van-khoang-trong` | Nút lưu bật. “Tôi chưa biết” ở lại lộ trình. “Tôi đã biết, chỉ là CV chưa ghi” vào danh sách cần ghi CV. “CV của tôi có ghi rồi” vào hồ sơ, không vào danh sách cần ghi CV. |
| Chi tiết kỹ năng | `co-van-ky-nang` | Lời dẫn không số. Số ở `stat-block`. Tài liệu chỉ từ danh mục đã kiểm duyệt. Bấm nút không gọi mô hình lúc đó. Phần “hay đi cùng” khi chưa đủ 30 tin ghi “chưa đủ dữ liệu”, không hiện tỷ lệ. |
| Đã lưu | `co-van-luu` | Tóm tắt hai phần: kỹ năng đã có nhưng cần ghi vào CV; lộ trình theo chặng, kèm link tài liệu. Ghi vai trò mục tiêu, n, ngày. Có “Xoá hồ sơ”. |
| Ô dán trống | `soi-tin-dan` | Nút “Soi tin” tắt. |
| Đã có chữ | `soi-tin-dan` | Nút “Soi tin” bật. Độ dài cho phép là 200 đến 20.000 ký tự. |
| Tin không thuộc IT | `soi-tin-dan` | Câu “Tin này có vẻ không thuộc lĩnh vực IT”. Không tính mức khớp. |
| Kết quả, có hồ sơ | `soi-tin-ket-qua` | Đầu trang “Đang đối chiếu với: Java Backend · Fresher/Junior”, đổi được. |
| Lương chưa đủ mẫu | `soi-tin-ket-qua` | “Chưa đủ dữ liệu (X/30 tin có lương)”. Số kỹ năng yêu cầu vẫn có phân vị. |
| Tin không ghi lương | `soi-tin-ket-qua` | Dòng trung tính ở mục Voice. Không phải dấu hiệu. |
| Hồ sơ trống lúc soi | `soi-tin-ket-qua` | Mời tải CV hoặc tự chọn. Phần so với thị trường vẫn hiện. |
| Thẻ đủ mẫu | `insights` | Câu mẫu có số, n, ngày. |
| Thẻ n < 30 | `insights` | Thẻ vẫn ở trên trang, viền hổ phách. Chỉ ghi chú “chưa đủ dữ liệu (n = X)”. Không hiện tỷ lệ. |
| Không thẻ nào đủ | `insights` | “Chưa đủ dữ liệu cho vai trò này.” |
| Tự chọn | `co-van-khong-cv` | Bấm để thêm hoặc bỏ. Minh họa Lan: Java, SQL, Git. Đổi sang Data Engineer thì tô kỹ năng trùng và hiện “Có N kỹ năng trong lộ trình này trùng với hồ sơ của bạn.” |
| Chính sách | `chinh-sach-du-lieu` | Đọc được ngay. Không trạng thái đăng nhập. |
| Trang vai trò, n ≥ 30 | `trang-vai-tro` | Đoạn đầu ít nhất ba kỹ năng, mỗi kỹ năng một tỷ lệ, kèm n, nguồn đang bật, ngày snapshot. |
| Trang vai trò, n < 30 | `trang-vai-tro` | Đoạn đầu chỉ “chưa đủ dữ liệu (n = X)”. Không tên nhóm, không phần trăm. |
| Phân vị lương hoặc số năm trên trang vai trò | `trang-vai-tro` | Chỉ khi có ít nhất 30 tin có đúng trường đó. Dưới ngưỡng thì “chưa đủ dữ liệu”, không hiện số của thước đo đó. |

## Interaction Primitives

- Bấm để chọn. Chip và nút xác nhận dùng `aria-pressed`.
- Bản đồ: kéo để xoay, kéo dọc để nghiêng. Artboard còn nút xoay và nút đặt lại góc nhìn. Ngưỡng kéo trước khi tính là đang kéo: 6px.
- Phần trăm cột n < 30: trỏ, chạm (`.tap`), hoặc focus. Không để phần trăm chỉ hiện khi trỏ chuột.
- Ô dán: dán văn bản, xoá nội dung, “Soi tin”. Đổi ô đối chiếu trên kết quả không đòi hỏi dán lại.
- Tự chọn: bấm lần nữa để bỏ kỹ năng.
- Escape không được gán cho một hộp thoại nào trên artboard. Không có lớp modal của sản phẩm trong 15 màn này.
- Cấm trên các màn này: ô chat, agent trò chuyện, khuyên nộp hoặc không nộp, kết luận tin giả, dự đoán khi thiếu mẫu.

Artboard có nút “Huỷ” trên màn đang đọc và nút “Chạy lại mô phỏng”. [NOTE FOR UX] “Chạy lại mô phỏng” là điều khiển của prototype. Script không ghi “Huỷ” đưa người dùng về đâu.

## Accessibility Floor

Tương phản nằm ở `DESIGN.md`. Các cặp chữ chính trên `{colors.canvas}` đo được từ 8,9:1 trở lên. Nút chính đạt 15,1:1. [NOTE FOR UX] Chữ nút tắt, `{colors.text-dim}` trên `{colors.disabled}`, đo được 3,9:1. Chưa có quyết định đổi màu.

- Vùng bấm tối thiểu `{spacing.target}`. Nav `{spacing.nav}`. Ô kiểm vẽ 24px; nhãn là vùng chữ đi cùng. Nút “chọn file khác” trên artboard đang cao 36px, cụm 3D / 2D / bảng cao 38px; khi dựng, đưa cả hai về `{spacing.target}`.
- `:focus-visible` có trên liên kết và nút. Màn Bản đồ còn gắn cho `input`, `select`, `textarea`. Mọi điều khiển nhận cùng vòng `{colors.primary}`, dày 2px, lệch 2px.
- Nav có tên “Điều hướng chính”. Cột bản đồ có câu `aria` gồm tên nơi, phần trăm, n, và câu cỡ mẫu nhỏ khi n < 30.
- Toast và dòng đếm kỹ năng trùng dùng `aria-live="polite"`. Khung CV scan dùng `role="alert"`. Khung quay về ô thống kê dùng `role="status"`.
- Đồng hồ đang đọc trên artboard đặt `aria-live="off"`. [NOTE FOR UX] Chưa chốt trình đọc có cần nghe bước đang chạy hay không.
- `prefers-reduced-motion: reduce` tắt animation và transition, gồm cả vòng `.flash`.
- Thứ tự tab theo thứ tự đọc trên artboard. Chưa có sơ đồ phím tắt.

## Responsive & Platform

Web một bề mặt. Laptop là bối cảnh của Minh và Lan trong PRD. Điện thoại không phải một ứng dụng riêng.

| Chỗ | Việc đã có bằng chứng |
|---|---|
| Artboard | Xem trước rộng 1440px. Khối `flex-wrap`. |
| Cột nội dung | Tối đa `{spacing.content}`, đệm `{spacing.page}`. |
| Dưới 640px | Khung bản đồ 3D còn cao 420px, tỷ lệ 0,62. |
| Dưới 560px | Mục trang chính sách xếp một cột. |
| Điện thoại, Bản đồ | FR-36: danh sách thành phố và thanh tỷ trọng, kèm gợi ý mở trên máy tính. Lối 2D hoặc bảng vẫn có. |
| Điện thoại, Cố vấn | FR-25: danh sách khoảng trống dạng thẻ, vẫn đủ ba lựa chọn FR-21, kèm gợi ý mở trên máy tính. |
| Điện thoại, Soi tin | FR-32: làm đủ việc của Soi tin. |

[NOTE FOR UX] Không có artboard điện thoại. Insights, trang chính sách và trang vai trò chưa có quy tắc xếp lại nào ngoài `flex-wrap` và mốc 560px của trang chính sách.

## Inspiration & Anti-patterns

Ngôn ngữ hình lấy từ prototype cũ: nền `{colors.canvas}`, chữ `{colors.text}`, Be Vietnam Pro, JetBrains Mono cho số, nút `{colors.primary}` với chữ `{colors.primary-ink}`, mục chọn `{colors.selected}`. File đó là `imports/prototype-ban-do-co-van.html`.

Đồ thị nút của Cố vấn là dạng PRD gọi là tham khảo roadmap.sh: nút kỹ năng, cạnh nghĩa là học trước. Không chép một bảng màu của roadmap.sh.

Không vẽ lại 11 màn đã loại: lương theo tuần, hạn dùng kỹ năng, dự báo 18 tháng, mô phỏng nếu-thì, hộ chiếu kỹ năng, chỉ số phản hồi nhà tuyển dụng, so sánh offer, tập thương lượng, nhảy việc, remote và Nhật, năm agent trò chuyện.

Cũng không đưa lại các cách đã loại trong PRD: trạng thái “đang học” trên hồ sơ; gán số tuần cho từng kỹ năng; câu Insights do mô hình viết; “không ghi lương” là một dấu hiệu; chiều cao cột bằng tỷ trọng của vai trò trong thành phố.

## Key Flows

### UJ-1 — Minh, tối Chủ nhật, từ bài đăng Facebook

Minh, 22 tuổi, sinh viên năm cuối, hướng Java Backend. Chưa có tài khoản, chưa từng vào Hải Đồ IT.

1. Minh mở liên kết. Ứng dụng vào `ban-do`, nav bốn mục, Bản đồ đang chọn.
2. Minh chọn vai trò và nhìn ba cột. Cột n < 30 vẫn đứng, mờ, nhãn cỡ mẫu nhỏ. “Khác” nằm ở chú thích. Ba lưu ý FR-36 và nguồn, ngày snapshot đang hiện.
3. Minh bấm cột Hà Nội. `ban-do-ha-noi` hiện tỷ trọng vai trò và kỹ năng hàng đầu, mỗi số có n và ngày.
4. Minh bấm “Xem lộ trình học và đối chiếu CV cho vai trò này”. `co-van-chung` mở với Backend đã chọn, cấp mặc định Intern/Fresher/Junior. Minh đổi nhánh Java Backend.
5. Ô Java Backend · Intern–Junior có 26 tin. Màn giữ cấp bậc và ghi dùng Backend · Intern–Junior, n = 52, cơ cấu 13 Intern, 7 Fresher, 32 Junior.
6. Minh đọc ô đồng ý trên `co-van-cv`, tích, rồi thả `CV_Minh_JavaBackend.pdf`.
7. `co-van-dang-doc` hiện từng bước trong 8–10 giây.
8. **Cao trào.** Trên `co-van-khoang-trong`, CV đã ghi Java, Git, REST API, Spring Boot, MySQL. Minh bấm “Tôi đã biết, chỉ là CV chưa ghi” cho SQL, PostgreSQL, Docker và Microservices. Minh bấm “Tôi chưa biết” cho CI/CD rồi Redis. Redis không phải riêng của công ty. Lộ trình còn lại xếp CI/CD trước Redis. Nút lưu chỉ bật khi mọi khoảng trống đã có lựa chọn.
9. Minh mở một nút trên `co-van-ky-nang`: lời dẫn không có số, số nằm ô riêng, kèm tài liệu miễn phí đã kiểm duyệt. Màn này là kỹ năng Minh bấm, không cố định là Docker của artboard.
10. `co-van-luu` giữ hồ sơ trong trình duyệt. Minh tải bản tóm tắt hai phần.

**Đường hỏng:** file là PDF ảnh scan, dưới 30 ký tự có nghĩa. Trong 1 giây, `cv-anh-scan` nói lý do và đưa ba lối: PDF xuất từ Word, Canva hoặc Overleaf; DOCX; tự chọn kỹ năng. Không OCR. Artboard ghi chưa có gì được gửi ra ngoài.

### UJ-2 — Minh, sáng hôm sau, hai tin Java Backend

Hồ sơ tối qua vẫn còn trong trình duyệt. CV đã được Minh sửa ở ngoài sản phẩm.

1. Minh mở `soi-tin-dan`. Chip hồ sơ còn. Không có ô chat.
2. Minh dán tin công ty A và bấm “Soi tin”.
3. `soi-tin-ket-qua` mở với “Đang đối chiếu với: Java Backend · Fresher/Junior”. Minh đổi vai trò hoặc cấp mà không dán lại. Nếu ô dưới 30 tin, nhãn ghi ô đang được dùng, kèm n và cơ cấu cấp bậc.
4. **Cao trào.** Mức khớp 89%. Dòng “4/4 cốt lõi, 2/2 thường gặp, 0/2 riêng của công ty”. Hai kỹ năng còn thiếu thuộc nhóm riêng của công ty. Lương: “chưa đủ dữ liệu (X/30 tin có lương)”. “Tin không công bố khoảng lương” là dòng trung tính, không phải dấu hiệu. D1 và D2 hiện như việc cần kiểm tra, đúng nghĩa ở Information Architecture, không phải kết luận tin giả. Minh tự quyết định nộp hay không. Sản phẩm không nói hộ.
5. Minh dán tin công ty B và đọc dấu hiệu của tin đó theo cùng quy tắc.

**Đường hỏng:** ô dán trống, nút “Soi tin” tắt. Tin ngắn hơn 200 ký tự hoặc dài hơn 20.000 ký tự chưa có câu báo trên artboard; ngưỡng vẫn là của FR-26.

### UJ-3 — Lan, chưa có CV, Backend rồi Data Engineer

Lan, 20 tuổi, đầu năm 3, mở liên kết trên laptop. Chưa có CV.

1. Lan xem Hà Nội rồi TP.HCM trên `ban-do`.
2. Lan mở `insights`. Thẻ “Cửa vào cho người mới” và “Bộ kỹ năng hay đi cùng nhau”. Câu trên thẻ là mẫu có số. Thẻ n < 30 chỉ ghi chú, không hiện tỷ lệ.
3. Lan vào `co-van-khong-cv`, bỏ qua CV, và bật Java, SQL, Git.
4. Lan đổi sang Data Engineer. Các kỹ năng trùng được tô. Có dòng “Có N kỹ năng trong lộ trình này trùng với hồ sơ của bạn.”
5. **Cao trào.** Lan thấy bằng số: hướng Data còn những kỹ năng cốt lõi nào, và kỹ năng nào có ở cả hai hướng. Không có câu “Data giờ khó xin việc” hay “Backend bão hòa”.
6. Lan lấy tài liệu miễn phí của kỹ năng chung.

**Đường hỏng:** một thẻ Insights có n < 30. Thẻ vẫn ở trên trang, viền hổ phách, câu “chưa đủ dữ liệu (n = X)”, không có phần trăm.

### Trang chính sách — người đọc, không tài khoản

1. Người đọc mở liên kết ở chân trang, hoặc mở thẳng `chinh-sach-du-lieu`.
2. Trang không có nav bốn mục.
3. **Cao trào.** Người đọc thấy đủ: mục đích nghiên cứu học thuật, phi thương mại; nguồn đang dùng; dữ liệu công bố ở mức tổng hợp; CV và tin dán không được lưu; email gỡ, xử lý trong 48 giờ.
4. Trang không có bảng rủi ro nội bộ. Không có câu “tuân thủ đầy đủ điều khoản của mọi nguồn” hay “mọi dữ liệu đều đã được cấp phép”.

Không có đường hỏng dạng n < 30. Trang không phụ thuộc hồ sơ.

### Trang vai trò — người đọc, không tài khoản

1. Người đọc mở URL của một vai trò. URL không đòi hỏi tài khoản.
2. Ô duy nhất là vai trò đó × mọi cấp bậc × toàn quốc. Trang không dùng thứ tự quay về của Cố vấn, không vẽ tỷ trọng thành phố.
3. **Cao trào, n ≥ 30.** Đoạn đầu có ít nhất ba kỹ năng, mỗi kỹ năng một tỷ lệ, kèm n, nguồn đang bật và ngày snapshot.
4. Trang có liên kết tới chính sách. Không liệt kê tin, không tên công ty, không link tin gốc.

**Đường hỏng:** n < 30. Đoạn đầu chỉ “chưa đủ dữ liệu (n = X)”. Không tên nhóm kỹ năng, không phần trăm.

## Chỗ chưa đủ bằng chứng

[NOTE FOR UX] Tên nhà cung cấp dịch vụ AI chưa có trên artboard. FR-10 yêu cầu ghi tên trong ô đồng ý. Ô trên artboard chỉ nói “một dịch vụ AI bên ngoài”, và chưa nói ý thống kê ẩn danh.

[NOTE FOR UX] Hai bộ số minh họa đang lệch. UJ-1 ghi SQL 35%, PostgreSQL 27%, Docker 17%, Microservices 19%, CI/CD 13%, Redis 12%. Artboard tính theo n = 52, ví dụ SQL 42/52, Redis 16/52. Chưa chốt bộ nào là ví dụ kể chuyện. Phân loại kỹ năng của cao trào Minh vẫn như Key Flows, không theo ngưỡng 60% của artboard.

Câu hỏi mở: cỡ mẫu minh họa của ô Soi tin khi n < 30 là bao nhiêu? Artboard ghi Java Backend · Fresher/Junior có 24 tin rồi quay về n = 39, và bộ kỹ năng đó không ra mức khớp 89% hay dòng 4/4, 2/2, 0/2. Spine giữ mức khớp và dòng đếm đã chốt, không lấy 24 và 39 làm số của sản phẩm.

[NOTE FOR UX] Chưa có hình cho: vai trò chưa có đồ thị học trước – học sau; ô thành phố n < 30 trên bảng chi tiết; hồ sơ trống lúc xem kết quả Soi tin; tin không thuộc IT; tin ngắn hơn 200 hoặc dài hơn 20.000 ký tự; phân vị số năm kinh nghiệm; kỹ năng chưa nhận diện; khoảng tin cậy khi 30 ≤ n < 100; danh sách đạt hoặc không đạt của chất lượng JD (FR-46), không gộp một điểm; nút “Copy link lộ trình” (FR-15); bộ lọc vai trò của Insights (FR-40).

[NOTE FOR UX] FR-37 có năm loại thẻ. Artboard Insights chỉ vẽ “Cửa vào cho người mới” và “Bộ kỹ năng hay đi cùng nhau”. Ba loại còn lại chưa có hình: bậc thang Junior → Senior, khác biệt giữa các thành phố, ngành và nhà tuyển dụng nổi bật.

[NOTE FOR UX] Toast xoá hồ sơ trên artboard nói sẽ xoá sau khi xác nhận, nhưng không có hình hộp xác nhận.

[NOTE FOR UX] `co-van-cv` mở sẵn file đã thả. Chưa có hình ô thả còn trống.

[NOTE FOR UX] Nguồn, email gỡ, tên nhóm nghiên cứu và ngày cập nhật chính sách trên artboard còn là chỗ giữ `[Nguồn 1]`, `[email liên hệ]`, `[tên nhóm / đơn vị nghiên cứu]`, `[ngày cập nhật]`.

[NOTE FOR UX] Artboard trang vai trò ghi cấp “Middle”. Bảng thuật ngữ gọi cấp đó là Mid.

[NOTE FOR UX] Màu các đoạn `level-bar` không ổn định giữa màn cố vấn và trang vai trò. Xem `DESIGN.md`.
