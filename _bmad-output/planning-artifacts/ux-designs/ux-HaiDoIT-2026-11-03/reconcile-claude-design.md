# Đối chiếu — Claude Design (1).html

Bản xuất không đuôi `(1)` không còn là nguồn. Đối chiếu chỉ lấy `Hải Đồ IT — Prototype Bản đồ & Cố vấn (ux 2026-11-03) (1).html`.

## Ý trên artboard không đi vào spine

- `co-van-chung`, `co-van-dang-doc`, `co-van-khoang-trong`, `soi-tin-ket-qua`: artboard in “Cốt lõi ≥ 60% · Thường gặp 30–59% · Riêng của công ty < 30%”. Bước cuối lúc đọc CV ghi “ngưỡng 60% và 30% số tin”. Spine giữ bảng thuật ngữ: cốt lõi ≥ 30% (θ_core), thường gặp từ 10% đến dưới 30% (θ_common), riêng của công ty dưới 10%.
- `ban-do`, mục “Đọc số này thế nào”: artboard viết tin công khai (không có tin nội bộ hay giới thiệu), tin trùng đã gộp thành một vị trí, và cột mờ khi dưới 30 tin. Spine giữ ba lưu ý FR-36: tin tuyển dụng không đồng nghĩa vị trí đang cần người; dữ liệu nghiêng về thành phố lớn và công ty lớn; lương chỉ phản ánh tin có công bố lương.
- `ban-do`: artboard ghi “Khác gộp các tỉnh còn lại, không phải một địa điểm” và “cộng với các cột = 100%”. Vai trò mở sẵn Backend (Frontend, Data, QA/Tester, DevOps, Mobile). Spine giữ ba cột Hà Nội, TP.HCM, Đà Nẵng; “Khác” chỉ ở chú thích, kèm tỷ trọng; vai trò mặc định là “Tất cả”. Phần “không xác định thành phố” trong phép cộng 100% chưa chốt đứng riêng hay nằm trong Khác.
- `co-van-chung`: artboard có cột “RIÊNG CỦA CÔNG TY” và nút Kafka (6/52). Spine không vẽ nhóm riêng của công ty trên lộ trình chung, trừ kỹ năng nền tảng với nhãn “Kỹ năng nền tảng (cần cho X)”.
- `co-van-ky-nang`: artboard là trang Docker, lời dẫn “Docker đóng gói một ứng dụng cùng môi trường chạy của nó…”. Spine giữ màn này là kỹ năng người dùng vừa bấm. Cao trào đã chốt: phần còn phải học là CI/CD rồi Redis, nên Docker không phải kỹ năng còn lại của hành trình.
- `soi-tin-ket-qua`: D1 là “Email liên hệ là địa chỉ cá nhân” (gmail.com); D2 là “Tin xuất hiện lại nhiều lần” (3 lần trong 45 ngày). Câu dưới dấu hiệu: “không phải kết luận tin giả”. `soi-tin-dan` liệt kê việc Hải Đồ không làm, gồm “Kết luận một tin là thật hay giả”. Spine giữ D1 là số kỹ năng yêu cầu cao hơn 90% số tin cùng ô; D2 là hơn một nửa kỹ năng đã nhận diện thuộc nhóm riêng của công ty. Cả hai là việc cần kiểm tra. Câu dưới dấu hiệu lấy từ FR-31: “Dấu hiệu là gợi ý để bạn tự kiểm tra. Đa số tin bị gắn dấu hiệu vẫn là tin thật.”
- `soi-tin-ket-qua`: ô đang mở là Java Backend · Fresher/Junior, 24 tin, rồi quay về Backend · Fresher/Junior, n = 39. Bộ kỹ năng trên màn ra “4/4 cốt lõi, 2/3 thường gặp, 0/1 riêng của công ty” (84%). Spine giữ mức khớp 89% và dòng “4/4 cốt lõi, 2/2 thường gặp, 0/2 riêng của công ty”. Spine không lấy 24 và 39 làm số của sản phẩm.
- `soi-tin-dan`: “9 kỹ năng đã có · 2 kỹ năng đang học”. `co-van-dang-doc`: “Chạy lại mô phỏng” và “Huỷ”; script không ghi Huỷ đưa về đâu. `co-van-cv`: lối “Prototype: xem trường hợp CV là PDF ảnh scan”. `trang-vai-tro`: “Middle 168”. Spine giữ ba câu chip hồ sơ (“Chưa có hồ sơ”; “Hồ sơ tạm · chưa lưu”; “Hồ sơ: Java Backend · trong trình duyệt”). Hai nút và lối prototype không phải điều khiển sản phẩm. Bảng thuật ngữ gọi cấp đó là Mid.

## Ý artboard thiếu so với hành vi đã chốt

- `co-van-cv`: ô đồng ý nói “một dịch vụ AI bên ngoài” và “không được lưu lại”. FR-10 yêu cầu ghi tên nhà cung cấp. Spine còn giữ: không lưu file gốc hay thông tin định danh, và có thống kê ẩn danh theo mã phiên.
- Chưa có hình cho các trạng thái đã có câu: vai trò chưa có đồ thị học trước – học sau; ô thành phố n < 30 trên bảng chi tiết; hồ sơ trống lúc xem kết quả Soi tin; tin không thuộc IT; tin ngắn hơn 200 hoặc dài hơn 20.000 ký tự; phân vị số năm kinh nghiệm; kỹ năng chưa nhận diện; khoảng tin cậy khi 30 ≤ n < 100; danh sách đạt hoặc không đạt của chất lượng JD (FR-46), mỗi mục riêng; nút “Copy link lộ trình” (FR-15); bộ lọc vai trò của Insights (FR-40). Chưa có artboard điện thoại, trong khi FR-36, FR-25 và FR-32 đã giao việc trên điện thoại.
- `insights`: artboard có “Cửa vào cho người mới” và “Bộ kỹ năng hay đi cùng nhau”. FR-37 còn ba loại chưa có hình: bậc thang Junior → Senior, khác biệt giữa các thành phố, ngành và nhà tuyển dụng nổi bật.
- `co-van-luu`: toast xoá nói hồ sơ sẽ bị xoá sau khi xác nhận. Chưa có hình hộp xác nhận. Spine: xoá hồ sơ còn xoá mã phiên ẩn danh; artboard không ghi ý này.
- `co-van-cv` mở sẵn file `CV_Minh_JavaBackend.pdf` đã thả. Chưa có hình ô thả còn trống.
- Cột n < 30 trên Bản đồ: chú thích artboard là “trỏ hoặc chạm”. Spine hiện phần trăm khi trỏ, chạm hoặc focus.
- Bộ số kể chuyện chưa chốt. UJ-1 ghi SQL 35%, PostgreSQL 27%, Docker 17%, Microservices 19%, CI/CD 13%, Redis 12%. `co-van-luu` in theo n = 52: SQL 81% (42/52), PostgreSQL 38% (20/52), Docker 35% (18/52), Microservices 31% (16/52), CI/CD 33% (17/52), Redis 31% (16/52). Spine không nhận bộ artboard làm số sản phẩm. Phân loại cao trào Minh vẫn như Key Flows, không theo ngưỡng 60%.
- Màu đoạn `level-bar` lệch cấp giữa màn cố vấn và `trang-vai-tro`. Spine chưa có thang màu cấp bậc; xem `DESIGN.md`.

## Placeholder còn để trống

- `chinh-sach-du-lieu`: `[Nguồn 1]`, `[Nguồn 2]`, `[loại trang]`, `[ngày]`, `[email liên hệ]`, `[tên nhóm / đơn vị nghiên cứu]`, `[ngày cập nhật]`.
- Cùng chỗ `[Nguồn 1]`, `[Nguồn 2]` trên chú thích nguồn của Bản đồ, bảng thành phố, Cố vấn, bản tóm tắt, Soi tin, Insights và trang vai trò.
- `co-van-ky-nang`: “Kiểm duyệt: [người kiểm duyệt] · [ngày]” trên hai tài liệu.
