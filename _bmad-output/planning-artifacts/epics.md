---
status: final
stepsCompleted: ['step-01-validate-prerequisites', 'step-02-design-epics', 'step-03-create-stories', 'step-04-final-validation']
inputDocuments:
  - _bmad-output/planning-artifacts/prds/prd-HaiDoIT-2026-11-02/prd.md
  - _bmad-output/planning-artifacts/prds/prd-HaiDoIT-2026-11-02/addendum.md
  - _bmad-output/planning-artifacts/architecture/architecture-HaiDoIT-2026-11-03/ARCHITECTURE-SPINE.md
  - _bmad-output/planning-artifacts/architecture/architecture-HaiDoIT-2026-11-03/WORK-SPLIT.md
  - _bmad-output/planning-artifacts/ux-designs/ux-HaiDoIT-2026-11-03/DESIGN.md
  - _bmad-output/planning-artifacts/ux-designs/ux-HaiDoIT-2026-11-03/EXPERIENCE.md
---

# Hải Đồ IT - Epic Breakdown

## Overview

Tài liệu này phân rã yêu cầu của Hải Đồ IT (repo HaiDoIT) thành epic và story có thể triển khai, lấy từ PRD, addendum PRD, architecture spine và hợp đồng UX (`DESIGN.md` + `EXPERIENCE.md`).

Thuật ngữ dùng đúng bảng thuật ngữ PRD §3. Không đổi tên: tin tuyển dụng, JD, nguồn, snapshot, vòng đời tin, kỹ năng, vai trò, nhánh, vai trò mục tiêu, cấp bậc, ô thống kê, cỡ mẫu (n), ngưỡng mẫu 30, tỷ lệ xuất hiện, nhóm kỹ năng (cốt lõi / thường gặp / riêng của công ty), phân vị, hồ sơ kỹ năng, khoảng trống kỹ năng, kỹ năng cần bổ sung vào CV, mã phiên ẩn danh, sự kiện ẩn danh, đồ thị học trước – học sau, lộ trình học, kỹ năng nền tảng, chặng, danh mục tài liệu, mức khớp, kỹ năng chưa nhận diện, dấu hiệu cần kiểm tra, bảng chi tiết thành phố, thẻ Insights.

Phạm vi đã chốt trong PRD, chưa phải thứ tự epic:

- v1 gồm FR-1 đến FR-48. Ngoài phạm vi v1 là các mục PRD §8.2 (xu hướng theo thời gian, dự báo, viết lại CV, tài khoản, trạng thái đang học, OCR, thu thập mới LinkedIn, ứng dụng di động, trang công khai theo thành phố/kỹ năng/câu hỏi, extension Soi tin, kênh gửi lương).
- Review giữa kỳ cần luồng CV → lộ trình học chạy thật cho Backend (nhánh Java Backend) và Data/AI (nhánh Data Engineer).
- FR-48 và trang chính sách (FR-47) là P1 bản công khai, không thuộc review giữa kỳ. Đúng một trang cho mỗi vai trò mục tiêu trong danh sách lúc công khai (4–5 vai trò), cộng một trang chính sách.
- Lộ trình có thứ tự khi công khai: 4–5 vai trò mục tiêu. Vai trò chưa có đồ thị vẫn dùng được Cố vấn ở dạng danh sách nhóm, và vẫn có trang FR-48.

Brief không nằm trong đầu vào của lần trích này. `WORK-SPLIT.md` chỉ dùng cho một việc: xếp mức ưu tiên và thứ tự sprint ở mục kế tiếp. Nội dung story không lấy từ nó.

## Requirements Inventory

### Functional Requirements

FR-1: Hệ thống thu thập tin tuyển dụng mỗi ngày một lần từ từng nguồn đang bật. Mỗi nguồn có công tắc bật/tắt, đổi được mà không sửa code. Mỗi lượt chạy ghi thời điểm bắt đầu, kết thúc, trạng thái và số tin của từng nguồn. Nguồn tắt không nhận request. Một nguồn lỗi không dừng các nguồn khác. Nhóm vận hành nhận thông báo khi lượt chạy lỗi, hoặc khi số tin của một nguồn giảm quá 50% so với trung bình 7 ngày.

FR-2: Khi thu thập, hệ thống kiểm tra `robots.txt` và tôn trọng điều khoản nguồn, gửi User-Agent trung thực có thông tin liên hệ, giãn cách cố định giữa các request tới cùng nguồn, không đăng nhập, và dừng nguồn đó ngay khi gặp HTTP 403/429 hoặc captcha. URL bị `robots.txt` cấm thì không bao giờ được request. Khi gặp captcha, nhật ký ghi lý do dừng và nguồn không được thử lại cho tới lần chạy sau. R1–R4 ở PRD §6.1 là ngoại lệ đã chấp nhận: SM-C1 và FR-2 được hiểu là trừ các ngoại lệ đó. Ngoại lệ không nằm rải trong code; chúng là hàng có tên, có công tắc hai mức (nguồn và bước).

FR-3: Mỗi lần pipeline chạy thành công tạo một snapshot. Mỗi tin lưu vòng đời: ngày thấy lần đầu, ngày thấy lần cuối, số lần thấy, số lần đăng lại. Một tin trong 3 snapshot liên tiếp có số lần thấy bằng 3. Tin chỉ bị coi là biến mất khi vắng mặt ở ít nhất 3 lần chạy thành công liên tiếp của chính nguồn đó; khi xuất hiện lại thì tính thêm một lần đăng lại. Một đêm nguồn lỗi hoặc bị dừng (FR-2) không làm tăng số lần đăng lại.

FR-4: Hệ thống gom tin trùng thành cụm, không xóa. Trong cùng nguồn: theo mã tin, URL và nội dung. Giữa các nguồn: theo tên công ty đã chuẩn hóa và độ tương đồng tập kỹ năng. Mọi con số thống kê tính mỗi cụm đúng một lần. Có báo cáo precision/recall trên khoảng 100 cặp tin gán nhãn tay, và tỷ lệ trùng còn sót trên 100 tin ngẫu nhiên dưới 5%.

FR-5: Ngay khi đọc tin và trước khi lưu, hệ thống xóa tên, email, số điện thoại và Zalo của người tuyển dụng. Không bản ghi nào trong kho khớp mẫu email hoặc số điện thoại Việt Nam. Nhật ký mỗi lần xóa chỉ ghi loại thông tin, không ghi giá trị.

FR-6: Hệ thống trích kỹ năng trong JD và quy về mã bộ từ vựng. Từ khóa không khớp được ghi vào danh sách kỹ năng chưa nhận diện, kèm tần suất, để rà soát hằng tuần. Cùng lượt xử lý trích số năm kinh nghiệm yêu cầu (tối thiểu, tối đa) nếu tin có nêu; tin không nêu thì để trống, không đoán. Tin ghi "2–3 năm" lưu thành tối thiểu 2, tối đa 3. Mỗi kết quả trích xuất lưu phiên bản model và phiên bản prompt. Precision ≥ 85% và recall ≥ 80% trên bộ chuẩn 200 JD gán nhãn tay, lấy từ văn bản gốc (phần lớn tiếng Việt hoặc trộn Việt–Anh), không lấy từ bản viết lại tiếng Anh. Bộ từ vựng song ngữ: ví dụ "học máy" → `machine-learning`, "kiểm thử tự động" → `test-automation`, "cơ sở dữ liệu" → `sql`. "SpringBoot", "Spring Boot", "Java Spring Boot" quy về cùng một mã. Báo cáo precision/recall tách riêng nhóm kỹ năng viết bằng tiếng Việt, và có Cohen's kappa của 2 người trên 50 JD chung.

FR-7: Mỗi tin được gán một vai trò, một nhánh nếu có, một cấp bậc và một thành phố. Nhánh chỉ được tạo khi có từ 30 tin. Data/AI tách thành Data Analyst/BI, Data Engineer và AI/ML Engineer. Embedded tách khỏi Other. Tin không thuộc IT được gắn nhãn và loại khỏi mọi bảng tổng hợp; tỷ lệ loại được báo cáo theo nguồn. Có báo cáo độ chính xác phân loại vai trò trên bộ chuẩn 200 JD, và tỷ lệ Other trước và sau khi tách.

FR-8: Lương dạng số được quy về VND/tháng, gross. USD đổi theo tỷ giá cố định, cấu hình được. Tin ghi "thỏa thuận" hoặc không ghi lương được đánh dấu không có lương dạng số. Khoảng "1.000–1.500 USD" lưu thành khoảng VND theo tỷ giá cấu hình. Tỷ lệ tin có lương dạng số được báo cáo riêng theo nguồn.

FR-9: Sau mỗi snapshot, hệ thống tính lại tỷ lệ xuất hiện của từng kỹ năng trong từng ô thống kê, và nhóm kỹ năng theo θ_core và θ_common. Hai tham số cấu hình được, không viết cứng. Khởi tạo θ_core = 30%, θ_common = 10%. Đổi θ thì nhóm đổi ở lần tính kế tiếp, không cần triển khai lại. Ở cấu hình nghiệm thu Sprint 2, mỗi vai trò mục tiêu có ít nhất 3 kỹ năng cốt lõi (mục tiêu 3–5). θ hiệu chỉnh một lần ở Sprint 2 rồi đóng băng trước đợt thử nghiệm Sprint 6–7; mọi lần đổi sau ghi kèm lý do. Với mỗi phân vị trên ô có 30 ≤ n < 100, bước đêm chạy bootstrap không tham số, lấy mẫu có hoàn lại, B = 1.000, và lưu khoảng tin cậy 95% cùng giá trị phân vị.

FR-10: Người dùng tải một CV PDF hoặc DOCX, tối đa 5 MB, chỉ sau khi tích ô đồng ý. Ô đồng ý nêu rõ: văn bản CV được gửi tới nhà cung cấp AI bên ngoài và ghi tên nhà cung cấp; hệ thống không lưu file gốc hay thông tin định danh; hệ thống ghi thống kê ẩn danh theo mã phiên về các thao tác chọn kỹ năng. Chưa tích thì không tải lên được. Sau khi xử lý, file CV và văn bản trích không còn trên server. Trong lúc xử lý, giao diện hiện lần lượt các bước đang chạy.

FR-11: Nếu văn bản trích từ CV có dưới 30 ký tự có nghĩa, hệ thống báo lỗi trong vòng 1 giây và gợi ý ba cách: PDF xuất từ Word, Canva hoặc Overleaf; file DOCX; tự chọn kỹ năng. v1 không chạy OCR.

FR-12: Hệ thống trích kỹ năng từ văn bản CV theo cùng bộ từ vựng FR-6 và thêm vào hồ sơ kỹ năng. Cùng một CV luôn cho cùng một tập kỹ năng. Thời gian từ lúc tải CV đến lúc có hồ sơ nằm trong ngân sách 15 giây của toàn luồng.

FR-13: Người dùng tự thêm hoặc bỏ kỹ năng trong hồ sơ, không cần CV, bằng cách bấm nút trên đồ thị lộ trình hoặc tìm và chọn từ danh sách. Hồ sơ tự chọn và hồ sơ từ CV được Cố vấn và Soi tin xử lý giống nhau.

FR-14: Hồ sơ kỹ năng và vai trò mục tiêu lưu trong trình duyệt. Tải lại trang hoặc mở lại hôm sau vẫn còn. Nút xóa hồ sơ xóa toàn bộ dữ liệu Hải Đồ IT trong trình duyệt, gồm mã phiên ẩn danh. Đóng rồi mở lại trình duyệt trên cùng máy, hồ sơ vẫn còn cho tới khi xóa.

FR-15: Người dùng copy được một link chứa vai trò mục tiêu và danh sách mã kỹ năng. Mở link khôi phục đúng màn lộ trình trên cùng snapshot. URL không chứa tên, email hay nội dung CV. Link không gắn một snapshot cố định: mở ngày khác thì tính lại trên snapshot mới, và màn hình luôn ghi ngày snapshot đang dùng.

FR-16: Người dùng tải một bản tóm tắt hai phần: kỹ năng cần bổ sung vào CV, và lộ trình học theo chặng kèm link từ danh mục tài liệu. Bản tóm tắt ghi vai trò mục tiêu, cỡ mẫu và ngày dữ liệu.

FR-17: Hệ thống sinh mã phiên ẩn danh trong trình duyệt và ghi sự kiện ẩn danh cho: một trong ba lựa chọn FR-21, tải CV thành công hoặc thất bại, soi một tin, lưu kết quả. Sự kiện chỉ chứa mã phiên, loại thao tác, mã kỹ năng và vai trò mục tiêu. Không chứa nội dung CV, nội dung JD hay thông tin định danh. Xóa hồ sơ (FR-14) cũng xóa mã phiên khỏi trình duyệt.

FR-18: Người dùng chọn vai trò, nhánh nếu có, và cấp bậc. Cấp mặc định là Intern/Fresher/Junior. Đến từ bảng chi tiết thành phố thì vai trò được chọn sẵn. Vai trò chưa có đồ thị học trước – học sau thì không vẽ đồ thị; hiện danh sách kỹ năng theo nhóm cốt lõi và thường gặp, kèm tỷ lệ, và câu "Lộ trình học có thứ tự cho vai trò này đang được biên soạn". Nút từ bảng thành phố hiện cùng câu đó. Đổi vai trò hoặc cấp bậc thì lộ trình tính lại, không tải lại trang.

FR-19: Khi hồ sơ trống, Cố vấn hiện mọi kỹ năng cốt lõi và thường gặp của ô thống kê. Mỗi nút ghi tỷ lệ xuất hiện và nhóm. Màn hình ghi cỡ mẫu, nguồn và ngày snapshot. Nếu ô vai trò mục tiêu × cấp bậc có n < 30, hệ thống quay về theo thứ tự giữ cấp bậc trước, giữ nhánh sau: (1) nhánh × cấp bậc, (2) vai trò × cấp bậc, (3) nhánh × mọi cấp bậc, (4) vai trò × mọi cấp bậc. Nhãn ghi n và cơ cấu cấp bậc. Người chọn Intern/Fresher/Junior không nhận một tập mà Mid trở lên chiếm đa số, trừ bước cuối; khi đó nhãn ghi rõ tỷ lệ tin Mid trở lên. Chỉ tính tin có ngày thấy lần cuối trong 60 ngày tính tới snapshot đang dùng.

FR-20: Khi hồ sơ có dữ liệu, kỹ năng đã có được tô và không nằm trong lộ trình; mỗi khoảng trống được làm nổi bật kèm nhóm. Kỹ năng riêng của công ty không vào lộ trình, trừ kỹ năng nền tảng. Kỹ năng nền tảng luôn mang nhãn "Kỹ năng nền tảng (cần cho X)". Cập nhật hồ sơ (tải CV, tự chọn, hoặc FR-21) làm lộ trình tính lại trong vòng 1 giây.

FR-21: Mỗi khoảng trống có hai nút chính: "Tôi chưa biết" (kỹ năng ở lại lộ trình) và "Tôi đã biết, chỉ là CV chưa ghi" (thêm vào hồ sơ, vào danh sách cần bổ sung CV, tính lại lộ trình). Khi hồ sơ tạo từ CV, có thêm lựa chọn phụ nhỏ hơn: "CV của tôi có ghi rồi (hệ thống đọc sót)" — thêm vào hồ sơ, tính lại lộ trình, không vào danh sách cần bổ sung CV. Đổi được lựa chọn; lựa chọn sau cùng có hiệu lực. Mỗi lựa chọn ghi một sự kiện ẩn danh.

FR-22: Lộ trình học tất định, dựng bằng: (1) tập khoảng trống, (2) thêm tổ tiên còn thiếu trên đồ thị học trước – học sau, (3) xếp theo bốn tầng — chặng tăng dần; cùng chặng thì cốt lõi trước thường gặp; cùng nhóm thì tỷ lệ xuất hiện giảm dần; bằng nhau thì mã kỹ năng A–Z. Thuật toán là sắp xếp topo Kahn, hàng đợi ưu tiên khóa (chặng, nhóm, −tỷ lệ xuất hiện, mã kỹ năng), không phụ thuộc thứ tự trả về của cơ sở dữ liệu. Đồ thị khoảng 100–300 nút, tính trong bộ nhớ. Cùng hồ sơ, cùng vai trò mục tiêu, cùng snapshot luôn cho cùng lộ trình; có kiểm thử lặp lại. Không kỹ năng nào đứng trước tổ tiên của nó. Mọi kỹ năng cốt lõi hoặc thường gặp của vai trò mục tiêu phải có nút trên đồ thị trước khi triển khai, nếu không bước kiểm tra báo lỗi. Mỗi cạnh lưu nguồn tài liệu. Mỗi vai trò có biên bản rà soát (người, ngày, số cạnh). Vai trò chỉ được bật trong Cố vấn sau khi có biên bản.

FR-23: Bấm một nút mở bảng chi tiết: tỷ lệ xuất hiện và nhóm; lời dẫn ngắn vì sao thị trường cần kỹ năng này; tài liệu miễn phí từ danh mục đã kiểm duyệt. Lời dẫn do LLM viết sẵn một lần cho mỗi cặp kỹ năng × vai trò, được rà soát và lưu lại. Lời dẫn không chứa con số; số lấy từ bảng tổng hợp FR-9 và hiện ở ô riêng. Mọi link đều có trong danh mục. Kiểm thử xác nhận lời dẫn không chứa ký hiệu phần trăm hay số lượng tin; số trong tên công nghệ (Java 17, S3, EC2, OAuth2, Web3, HTML5, Vue 3) không bị tính. Bấm nút không gọi LLM.

FR-24: Khi đổi vai trò mục tiêu, nút trùng hồ sơ được tô sáng. Một dòng tóm tắt cho biết có bao nhiêu kỹ năng trong lộ trình mới trùng hồ sơ. Câu chữ dùng "vai trò có kỹ năng gần", không dùng "lộ trình chuyển việc". Đổi từ Backend sang Data Engineer với hồ sơ {Java, SQL, Git} thì tô đúng phần giao của hồ sơ với lộ trình Data Engineer.

FR-25: Giao diện mô tả nhóm thường gặp là "nên học sau khi đã nắm các kỹ năng cốt lõi". Không câu nào trên giao diện hay trong lời dẫn khuyên bỏ qua một kỹ năng, và không câu nào khuyên "đừng học".

FR-26: Người dùng dán nội dung tin dạng văn bản, dài từ 200 đến 20.000 ký tự. Hệ thống trích kỹ năng theo bộ từ vựng FR-6. Nội dung dán không được lưu trên server sau khi xử lý. Tin không thuộc IT thì báo "Tin này có vẻ không thuộc lĩnh vực IT" và không tính mức khớp. Mỗi lần soi ghi một sự kiện ẩn danh, không kèm nội dung tin.

FR-27: Hệ thống tự nhận diện vai trò, nhánh nếu có, và cấp bậc của tin, rồi hiện ở đầu kết quả dưới dạng ô chọn. Người dùng đổi vai trò hoặc cấp bậc và kết quả tính lại mà không dán lại tin. Đầu kết quả ghi cỡ mẫu của ô đang dùng. Khi n < 30, quay về theo thứ tự FR-19 và có nhãn n cùng cơ cấu cấp bậc.

FR-28: Khi hồ sơ có dữ liệu, hệ thống hiện mức khớp theo trọng số thị trường và một dòng đếm thô theo nhóm. Mức khớp = tổng trọng số kỹ năng đã nhận diện trong JD mà người dùng có, chia cho tổng trọng số mọi kỹ năng đã nhận diện trong JD. Trọng số: cốt lõi 3, thường gặp 2, riêng của công ty 1. Kỹ năng chưa nhận diện không tính. Ví dụ kiểm: 4/4 cốt lõi + 2/2 thường gặp + 0/2 riêng = 16/18 = 89%. Khi hồ sơ trống, mời tải CV hoặc tự chọn; phần so với thị trường vẫn hiện.

FR-29: Mỗi kỹ năng của tin xếp vào cốt lõi, thường gặp, riêng của công ty, hoặc chưa nhận diện. Kỹ năng chưa nhận diện hiện ở dòng riêng, ghi "không tính vào mức khớp", và vào danh sách chờ FR-6. Mỗi kỹ năng thiếu thuộc nhóm riêng của công ty có ghi chú "chỉ cần nếu bạn nhắm đúng công ty này".

FR-30: Hệ thống đặt tin vào phân vị của ô thống kê theo ba thước: số kỹ năng yêu cầu luôn hiện; số năm kinh nghiệm chỉ hiện khi trích được từ tin và ô có từ 30 tin có số năm trở lên, nếu không thì "chưa đủ dữ liệu (X/30 tin có số năm kinh nghiệm)"; lương chỉ hiện khi tin có lương dạng số và ô có từ 30 tin có lương, nếu không thì "chưa đủ dữ liệu (X/30 tin có lương)". Ngưỡng đếm số tin có đúng trường đó, không đếm toàn bộ tin của ô. Khi 30 ≤ n < 100, hiện phân vị kèm khoảng tin cậy 95% đã tính ở FR-9.

FR-31: Hệ thống đánh giá bảy dấu hiệu. Mỗi dấu hiệu kích hoạt hiện dữ kiện đã kích hoạt nó và một gợi ý hành động. Ngay dưới các dấu hiệu luôn có câu "Dấu hiệu là gợi ý để bạn tự kiểm tra. Đa số tin bị gắn dấu hiệu vẫn là tin thật." Không câu nào dùng "lừa đảo", "tin giả" hay "tin ma". Tin không ghi lương không phải dấu hiệu; phần lương hiện dòng trung tính "Tin không công bố khoảng lương. Bạn có thể tham khảo phân vị lương của vai trò này (nếu đủ mẫu) khi đàm phán." Mỗi quy tắc có kiểm thử với một tin mẫu kích hoạt và một tin mẫu không kích hoạt.

- D1 Yêu cầu kỹ năng dàn trải: số kỹ năng đã nhận diện ≥ P90 của ô. Gợi ý hỏi rõ 2–3 công nghệ nhóm thực sự dùng hằng ngày.
- D2 Tỷ lệ kỹ năng riêng cao: tin có ≥ 4 kỹ năng đã nhận diện và hơn 50% trong số đó thuộc nhóm riêng của công ty. Không tính kỹ năng chưa nhận diện.
- D3 Yêu cầu cao, lương thấp: tin có lương dạng số, ô có ≥ 30 tin có lương, số kỹ năng ≥ P75 trong khi lương trần ≤ P25.
- D4 Tin đăng lại nhiều lần: tin khớp một tin đã thu thập (FR-32) và tin đó có số lần đăng lại ≥ 2 hoặc xuất hiện liên tục qua ≥ 30 snapshot. Không khớp thì "không đánh giá được: tin chưa có trong dữ liệu".
- D5 Kênh liên hệ bất thường: chỉ liên hệ qua Zalo, Telegram hoặc email cá nhân, không có kênh công ty.
- D6 Đòi tiền trước: tin nhắc đặt cọc, phí đào tạo, phí hồ sơ hoặc phí giữ chỗ.
- D7 Không rõ công ty: tin không nêu tên công ty.

FR-32: Hệ thống tìm trong dữ liệu đã thu thập một tin trùng với tin được dán, cùng cách so khớp FR-4. Tìm thấy thì dùng vòng đời tin đó cho D4 và hiện link về tin gốc. Dán lại nguyên văn một tin đã có thì tìm đúng tin đó.

FR-33: Trang chủ là bản đồ 3D Việt Nam. Có cột cho Hà Nội, TP.HCM và Đà Nẵng. Người dùng chọn vai trò để lọc; mặc định "Tất cả". Chiều cao cột là tỷ trọng của thành phố đó trong tổng tin của vai trò đang chọn, trên toàn quốc. Một chiều cao chỉ mang một nghĩa. Cột có n < 30 vẫn vẽ theo tỷ trọng thật, trạng thái mờ, nhãn "Cỡ mẫu nhỏ (n = X < 30): số liệu chỉ để tham khảo", và vẫn bấm được. Thành phố khác gom thành "Khác" ở phần chú thích, không vẽ cột. Phần không xác định thành phố nằm trong phép cộng 100% cùng các cột và "Khác", không phải một cột. Người dùng xoay và nghiêng được bản đồ. Trỏ hoặc chạm một cột thì thấy tỷ trọng kèm cỡ mẫu. Khi chọn một vai trò, tổng các cột cộng "Khác" cộng phần không xác định thành phố bằng 100%. Cột Đà Nẵng luôn được vẽ.

FR-34: Bấm một cột mở bảng chi tiết thành phố: cơ cấu vai trò với tỷ trọng và cỡ mẫu từng vai trò; các kỹ năng có tỷ lệ xuất hiện cao nhất cho vai trò đang chọn hoặc cho tất cả; ngày snapshot. Mọi con số có cỡ mẫu. Ô n < 30 không hiện tỷ lệ, chỉ ghi "chưa đủ dữ liệu".

FR-35: Bảng chi tiết thành phố có nút "Xem lộ trình học và đối chiếu CV cho vai trò này". Nút mở Cố vấn với vai trò đã chọn. Vai trò chưa có đồ thị thì nút hiện thông báo FR-18. Bấm từ bảng Hà Nội, vai trò Backend, mở Cố vấn với vai trò mục tiêu Backend.

FR-36: Bản đồ luôn có chú thích: danh sách nguồn đang bật, ngày snapshot, và ba lưu ý — tin tuyển dụng không đồng nghĩa vị trí đang cần người; dữ liệu nghiêng về thành phố lớn và công ty lớn; con số lương chỉ phản ánh tin có công bố lương. Chú thích hiện trên mọi trạng thái của bản đồ, kể cả điện thoại. Bắt buộc có chế độ xem 2D hoặc bảng với cùng số liệu như bản đồ 3D. Người dùng chuyển qua lại được. Trình duyệt không chạy WebGL thì tự chuyển sang chế độ này, không hiện màn hình lỗi.

FR-37: v1 có năm loại thẻ Insights, mỗi thẻ do code tính trên snapshot mới nhất, không dùng LLM: Cửa vào cho người mới (tỷ lệ tin Intern/Fresher/Junior trong từng vai trò); Bộ kỹ năng hay đi cùng nhau (cặp kỹ năng cùng xuất hiện nhiều nhất theo vai trò); Bậc thang Junior → Senior (kỹ năng có tỷ lệ tăng nhiều nhất từ Intern/Fresher/Junior lên Senior trở lên, cùng vai trò); Khác biệt giữa các thành phố (kỹ năng chênh nhiều nhất giữa Hà Nội và TP.HCM; Đà Nẵng chỉ khi ô của nó đạt n ≥ 30); Ngành và nhà tuyển dụng nổi bật (ngành và công ty có nhiều tin nhất). Mỗi thẻ có một câu kết luận, các số căn cứ kèm cỡ mẫu và ngày, và một nút sang Cố vấn hoặc Bản đồ. Mỗi loại thẻ có kiểm thử so khớp số hiển thị với một truy vấn kiểm tra độc lập trên cùng snapshot. v1 không có nhận định xu hướng theo thời gian.

FR-38: Một thẻ chỉ hiển thị khi mọi con số trong thẻ tính trên ô có n ≥ 30. Thẻ so sánh (bậc thang, khác biệt thành phố) chỉ hiển thị khi chênh lệch đạt ít nhất 5 điểm phần trăm. Không thẻ nào dựa trên ô dưới 30 tin. Nếu một vai trò không có thẻ nào đủ điều kiện, trang ghi "chưa đủ dữ liệu cho vai trò này". Ngưỡng 5 điểm là lọc nhiễu, không phải kiểm định ý nghĩa thống kê.

FR-39: Câu kết luận tạo từ mẫu câu cố định, chỗ trống điền bằng số đã tính. Mỗi loại thẻ có 2–3 biến thể theo khoảng giá trị, ví dụ trên 50% "Áp đảo: hơn một nửa số tin…", từ 30% đến 50% "Khá phổ biến: khoảng một phần ba số tin…", dưới 10% "Rất hiếm: chỉ…". Biến thể được chọn đúng theo ranh giới khoảng. Cùng snapshot luôn cho cùng câu. Mọi số trong câu khớp số hiển thị bên dưới. Không dùng LLM vì câu luôn chứa số và số đổi mỗi ngày.

FR-40: Người dùng lọc thẻ theo vai trò. Nếu trình duyệt đã lưu vai trò mục tiêu (FR-14), bộ lọc được chọn sẵn vai trò đó. Đổi bộ lọc thì chỉ thẻ của vai trò đó hiện, cộng các thẻ áp dụng cho mọi vai trò.

FR-41: Chế độ thử nghiệm chỉ bật khi vào bằng link thử nghiệm (ví dụ `?mode=eval`). Giao diện luôn hiện nhãn "Chế độ thử nghiệm". Mọi sự kiện ẩn danh trong phiên được đánh dấu thuộc thử nghiệm theo cách tách được khỏi dữ liệu dùng thường. Người vào bằng link thường không bao giờ thấy modal thử nghiệm.

FR-42: Ngay khi vào link thử nghiệm, một modal che toàn bộ nền trước khi người thử thấy bất kỳ con số nào. Modal hỏi: nhóm trong trường hoặc ngoài trường; vai trò mục tiêu; đúng 3 kỹ năng người thử nghĩ mình cần học nhất, chọn từ bộ từ vựng bằng ô tìm có gợi ý (thành phần FR-13), lưu dưới dạng mã kỹ năng không phải văn bản tự do; một câu tự đánh giá thang 1–5 nguyên văn "Ở thời điểm hiện tại, mức độ rõ ràng của bạn về những kỹ năng cần ưu tiên học tiếp theo cho vị trí mục tiêu là bao nhiêu?" (1 = hoàn toàn mông lung, 5 = hoàn toàn rõ ràng về danh sách và thứ tự học). Chưa trả lời xong thì không đóng được modal. Ghi loại thiết bị (máy tính hay điện thoại).

FR-43: Modal cuối phiên tự bật khi người thử bấm "Lưu kết quả" (FR-16) hoặc "Copy link chia sẻ" (FR-15). Suốt phiên luôn có nút "Hoàn tất thử nghiệm & Đánh giá (1 phút)". Modal hỏi lại đúng nguyên văn câu tự đánh giá FR-42; ý định hành động "Sau phiên này, bạn có dự định sửa CV hoặc đổi thứ tự học trong 4 tuần tới không?" (Có / Không); và phần so sánh mù FR-44. Mỗi mã phiên chỉ gửi modal cuối phiên một lần.

FR-44: Modal cuối phiên hiện một tình huống mẫu cố định theo vai trò mục tiêu, gồm hồ sơ kỹ năng mẫu và JD mẫu, cùng hai phương án: một do Hải Đồ IT tạo trên đúng đầu vào đó tại một snapshot cố định, một là câu trả lời ChatGPT soạn sẵn cho cùng đầu vào. Hai phương án không ghi nguồn, cùng định dạng markdown trung tính, cùng cấu trúc gạch đầu dòng, độ dài tương đương. Thứ tự trái/phải đảo ngẫu nhiên 50/50. Người thử chấm từng phương án từ 1 đến 5 rồi chọn phương án hữu ích hơn. Hệ thống lưu vị trí đã hiển thị. Tình huống và cả hai phương án là dữ liệu tĩnh; lúc thử nghiệm không gọi API để lấy chúng. Trên điện thoại hai phương án xếp trên/dưới, vẫn đảo 50/50, vẫn lưu vị trí. Khoảng 40% người thử có thể dùng điện thoại, nên FR-21 và FR-42 đến FR-44 chạy đầy đủ trên điện thoại.

FR-45: Chế độ thử nghiệm không có ô email, Zalo hay thông tin liên hệ. Dữ liệu modal đầu phiên, sự kiện ẩn danh và modal cuối phiên nối với nhau chỉ bằng mã phiên. Một câu truy vấn xuất được bảng theo phiên: nhóm người dùng, 3 kỹ năng tự đoán, các lựa chọn đã biết / chưa biết, ý định hành động, điểm và lựa chọn của phần so sánh mù.

FR-46: Hệ thống chấm chất lượng tin được dán theo danh sách kiểm tra minh bạch và hiện từng mục đạt hoặc không đạt: có khoảng lương; có tên công ty; có mô tả trách nhiệm; có phúc lợi; chức danh, kỹ năng yêu cầu và cấp bậc có nhất quán không (ví dụ tuyển Fresher nhưng đòi từ 5 năm). Mỗi mục có quy tắc viết được và kiểm thử riêng. Không gộp thành một điểm chất lượng duy nhất.

FR-47: Có trang chính sách dữ liệu công khai, vào được từ chân trang mọi màn hình, gồm: mục đích nghiên cứu học thuật phi thương mại; nguồn đang dùng; dữ liệu thu thập và mức công bố tổng hợp; dữ liệu không lưu (CV, nội dung tin người dùng dán); cam kết xử lý yêu cầu gỡ trong 48 giờ. Kênh yêu cầu gỡ là email. User-Agent của crawler ghi địa chỉ liên hệ trỏ về kênh này. Trang không chứa chi tiết kỹ thuật thu thập hay bảng R1–R4. Trang không chứa câu khẳng định tuân thủ mâu thuẫn R1–R4. Hai câu bị cấm nguyên văn: "tuân thủ đầy đủ điều khoản của mọi nguồn" và "mọi dữ liệu đều đã được cấp phép", kể cả câu cùng nghĩa. Yêu cầu gỡ hợp lệ được xử lý và tin liên quan biến khỏi số liệu công khai từ snapshot kế tiếp, không sửa snapshot đã công bố. Không công bố toàn văn JD. Phía người dùng chỉ thấy số liệu tổng hợp và trường ngắn (chức danh, công ty, thành phố, khoảng lương), kèm link về tin gốc — trần này không áp vào trang FR-48.

FR-48: Mỗi vai trò mục tiêu trong danh sách lúc công khai có đúng một trang. URL không đổi khi sang snapshot mới, mở được không cần tài khoản, không chuyển hướng đăng nhập, không nằm trong chỉ dẫn chặn thu thập. Request không cookie nhận đủ đoạn đầu trong nội dung trả về. Ô duy nhất là vai trò đó × mọi cấp bậc × toàn quốc, chỉ tin có ngày thấy lần cuối trong 60 ngày. Trang không dùng thứ tự quay về, không vẽ tỷ trọng thành phố, không sửa FR-33. Khi n ≥ 30, đoạn đầu nêu ít nhất ba kỹ năng, mỗi kỹ năng một tỷ lệ xuất hiện. Khi n < 30, đoạn đầu chỉ là "chưa đủ dữ liệu (n = X)": không tên nhóm, không phần trăm. Phân vị số kỹ năng chỉ hiện khi n của ô ≥ 30. Phân vị lương và phân vị số năm chỉ hiện khi có ≥ 30 tin có đúng trường đó, cùng cửa FR-30. Mỗi số kèm n của đúng thước đo, danh sách nguồn đang bật và ngày snapshot. Trang có hai ý độ phủ của NFR trung thực số, gồm ba lưu ý FR-36. Chỉ dùng số liệu tổng hợp: không liệt kê tin, không chức danh, công ty, thành phố, lương của từng tin, không link tin gốc, không toàn văn JD. Ràng buộc trung thực FR-47 áp nguyên. Sau khi ứng dụng chuyển snapshot, kể cả snapshot thiếu nguồn, nội dung trang khớp snapshot đó; nguồn thiếu hiện trong danh sách nguồn; trang không giữ snapshot cũ hơn snapshot ứng dụng đang hiển thị. Mỗi URL có liên kết nhìn thấy tới trang chính sách. Ngoài phạm vi: không trang theo thành phố, kỹ năng hay câu hỏi trong v1; không lấy JSON-LD hay file hướng dẫn mô hình ngôn ngữ làm tiêu chí hoàn thành.

### NonFunctional Requirements

NFR-1: Từ lúc tải CV đến lúc lộ trình học cá nhân hóa hiển thị: dưới 15 giây. Có kiểm thử đo, không chỉ là câu trong tài liệu.

NFR-2: Từ lúc bấm "Soi tin" đến lúc có kết quả: dưới 15 giây. Có kiểm thử đo.

NFR-3: Đổi vai trò mục tiêu, cấp bậc, hoặc cập nhật hồ sơ: kết quả mới hiển thị trong vòng 1 giây. Có kiểm thử đo.

NFR-4: Sau khi xử lý xong, server không lưu file CV, văn bản CV hay nội dung JD người dùng dán. Nhật ký hệ thống không ghi nội dung CV hay JD. Access log của reverse proxy và API không ghi body.

NFR-5: Dữ liệu cá nhân của người dùng chỉ nằm trong trình duyệt và xóa được bằng một nút (FR-14). Không tài khoản, không session phía server.

NFR-6: Sự kiện ẩn danh chỉ chứa các trường FR-17 đã liệt kê.

NFR-7: Mọi con số hiển thị cho người dùng đều kèm cỡ mẫu, nguồn và ngày snapshot. Mọi con số truy ngược được về snapshot đã tạo ra nó. Mọi kết quả trích xuất bằng LLM truy ngược được về phiên bản model và prompt đã dùng.

NFR-8: Ô thống kê dưới ngưỡng mẫu thì nói "chưa đủ dữ liệu", không hiển thị một con số đoán. Ngoại lệ duy nhất đã chốt là tỷ trọng cột bản đồ FR-33: vẫn vẽ khi n < 30, ở trạng thái mờ, kèm nhãn cỡ mẫu nhỏ.

NFR-9: Mọi màn hình có số liệu (Bản đồ, Insights, Cố vấn, Soi tin, trang vai trò FR-48) và bản tóm tắt tải về đều có lưu ý độ phủ, gồm hai ý: dữ liệu chỉ gồm tin tuyển dụng IT đăng online trên N nguồn; và ba lưu ý chuẩn FR-36.

NFR-10: Lộ trình học, mức khớp, dấu hiệu cần kiểm tra và câu kết luận Insights là tất định: cùng đầu vào và cùng snapshot luôn cho cùng kết quả. Có kiểm thử lặp lại.

NFR-11: Nếu pipeline một đêm lỗi, giao diện vẫn chạy trên snapshot gần nhất và hiển thị đúng ngày của snapshot đó.

NFR-12: Ưu tiên máy tính. Trên điện thoại: Soi tin đầy đủ; Cố vấn dạng thẻ, đủ ba lựa chọn FR-21; Bản đồ dạng danh sách thành phố kèm thanh tỷ trọng; Insights xếp dọc, một thẻ một hàng; chế độ thử nghiệm FR-41 đến FR-45 đầy đủ. Có chế độ 2D hoặc bảng thay cho 3D (FR-36).

NFR-13: Giao diện tiếng Việt. Tên kỹ năng giữ dạng chuẩn tiếng Anh đã chuẩn hóa (Docker, Spring Boot).

NFR-14: Trần CV 5 MB bị chặn ở cả frontend lẫn reverse proxy, trước khi đọc body. File tải lên xử lý trong bộ nhớ. Không tạo file tạm khi tải một CV 5 MB.

NFR-15: Trần chi phí vận hành sau bảo vệ dưới 5–10 USD/tháng trên một VPS nhỏ. Lúc người dùng dùng thật, LLM chỉ được gọi ở trích CV (FR-12) và trích tin dán (FR-26). Lời dẫn Cố vấn viết sẵn. Insights không gọi LLM. Trích xuất hằng đêm chạy theo lô.

NFR-16: Không ô chat tự do. LLM không sinh con số, thứ tự học, hay câu kết luận Insights. Không khuyên nộp hay không nộp. Không kết luận tin thật hay giả. Không bán điểm đánh giá.

### Additional Requirements

**Hạt giống dựng hệ thống — ảnh hưởng Epic 1 Story 1.** Spine không chỉ định starter template bên ngoài. Story đầu dựng đúng cây mã và stack đã ghim, rồi bọc code kế thừa. Không clone một template public.

- Cây mã: `haido_core/` (`domain/`, `db/`, `crawl/`, `extract/`, `steps/`, `vocab/`), `haido_pipeline/`, `haido_api/`, `web/`, `scraper/` trong lúc chuyển, `eval_fixtures/`, `deploy/` (`compose.local.yml`, `compose.prod.yml`, Caddyfile, `.env.example`). `haido_core/domain/REGISTRY.md` khai tám phép dùng chung.
- Stack ghim ngày 03/11/2026: Python 3.13, PostgreSQL 18.6, Dagster 1.13.28, FastAPI 0.162.0, SQLAlchemy 2.1.6 kèm `greenlet` tường minh, Alembic 1.20.1, Pydantic 2.14.2, Uvicorn 0.54.0, psycopg 3.3.7, NetworkX 3.7, SciPy 1.18.1, anthropic SDK 2.4.0, Node.js 24 LTS, Next.js 16.4.4, React 19.3.1, deck.gl 9.4.1, @xyflow/react 12.12.1, maplibre-gl 6.16.0, Tailwind CSS 4.3.4, Caddy 2. Model trích xuất: `claude-haiku-5-5` cho lô đêm qua Batch API; `claude-sonnet-5-5` cho đường người dùng dán, chốt sau khi đo độ trễ Sprint 2. v1 chỉ dùng Claude. Đã loại Airflow, Neo4j, GraphRAG, pgvector, bge-m3, Node 22.
- Ranh giới tỉnh là GeoJSON tĩnh có phiên bản trong repo. Không gọi dịch vụ bản đồ bên ngoài lúc chạy.
- Hai môi trường, không staging. Local: Compose riêng, `dagster dev`, Postgres trong container, trên Windows. Prod: Compose riêng, một VPS 4 GB, Cloudflare (TLS, CDN, gói miễn phí) phía trước Caddy, Caddy tách `web` và `api`. Ba service Dagster (webserver, daemon, code location gRPC) cộng một run worker. Đúng một lượt chạy đồng thời. Bootstrap có trần bộ nhớ. `next build` không chạy trên prod: image build ở máy dev rồi đẩy lên. Dagster UI không bật thường trực. Có swap. Playwright chỉ ở nguồn chạy thủ công trên máy người thật, không trong container Dagster.
- `web/` không bao giờ kết nối Postgres, kể cả khi sinh trang công khai. Phụ thuộc một chiều: `web` → `haido_api` → `haido_core` → `domain`; `haido_pipeline` → `haido_core`. `haido_api` và `haido_pipeline` không biết nhau. Chặn import ngược và chuỗi kết nối Postgres từ `web/` ở CI.

**Tám phép dùng chung, một bản cài đặt (AD-2).** Mọi phép sinh số hoặc phân loại dùng từ hai nơi nằm trong `haido_core/domain/` và có tên trong registry đóng. Mỗi phép có một chữ ký, gọi được cho một đối tượng và cho một lô. Không biến thể chỉ-theo-lô. Thêm phép thứ chín thì sửa registry trong cùng thay đổi. Tám phép: (1) mapping lượt nhắc → mã kỹ năng, (2) chọn ô thống kê và thứ tự quay về, (3) dân số ô trong cửa sổ 60 ngày đếm theo cụm, (4) nhóm kỹ năng theo θ, (5) phân vị, mốc, khoảng tin cậy, (6) phân loại vai trò / nhánh / cấp bậc / thành phố, (7) so khớp tin trong nguồn và chéo nguồn, (8) xếp thứ tự lộ trình theo quy tắc 4 tầng.

**Cổng trích xuất (AD-3, AD-9).** Cổng trả lượt nhắc kỹ năng nguyên văn kèm vị trí, và một tập trường có kiểu đã đóng (khoảng số năm, khoảng lương kèm đơn vị nguyên văn, kênh liên hệ, dấu hiệu thu phí, tên công ty, các mục chất lượng JD), mỗi trường kèm đoạn văn bản nguồn. Cổng không trả mã kỹ năng, nhãn vai trò/cấp bậc, hay con số tự tính. Quy về mã, quy lương về VND, quy nhãn phân loại là phép tất định trong `domain`, không gọi mạng. Đổi bộ từ vựng thì chạy lại mapping, không chạy lại LLM. Mọi lệnh gọi đi qua một interface trong `haido_core/extract/`. Mỗi bản ghi lưu `model_id`, `prompt_version`, `vocab_version`. Đầu ra khai bằng `output_config.format`, không bằng `tool_choice` cưỡng bức. Đường lúc chạy không phụ thuộc việc tắt thinking. Lô Batch hết hạn sau 24 giờ thì lượt chạy kết thúc `partial`, không công bố snapshot thiếu phần như thể đủ. Hai endpoint POST công khai có trần kích thước và trần tốc độ theo IP, cấu hình được.

**Snapshot và dòng dữ liệu (AD-4, AD-16, AD-19, AD-27, AD-28).**

- `job_observations` append-only, mỗi hàng treo vào một `pipeline_run`. Không `UPDATE` vòng đời tại chỗ. `stat_job_lifecycle` vật hóa vòng đời theo từng snapshot. Cửa sổ 60 ngày xét trên vòng đời của snapshot đang dùng.
- Snapshot chỉ do `open_snapshot` tạo, kết thúc `published` (mọi nguồn tự động đang bật có `pipeline_run` thành công) hoặc `partial` (kèm `sources_failed[]`). Cả hai đều đọc được. Chuyển trạng thái trong một transaction sau khi mọi bảng tổng hợp đã ghi xong. Hàng đã công bố không sửa, không xóa. Tính lại là sinh snapshot mới.
- Thứ tự một đêm là bất biến: `crawl` (cổng polite) → `redact` → `ingest` → dedupe trong nguồn → `fetch_details` → `extract` (Batch) → `mapping` → cluster chéo nguồn → `classify` → `normalize_salary` → `stat_job_lifecycle` → `aggregate` → `publish` → revalidate rồi mồi từng URL bằng GET. Ghép trùng trong nguồn đứng trước bước gọi LLM. Ghép trùng chéo nguồn đứng sau mapping. TopCV chạy tay, ngoài lượt đêm, ghi `pipeline_run` là nguồn thủ công, không phải asset đêm. Snapshot vẫn `published` khi TopCV không chạy.
- Mỗi bước pipeline là hàm trong `haido_core/steps/`, gọi được bằng CLI, không import Dagster. `haido_pipeline/` chỉ chứa asset và partition. Một snapshot = một daily partition, timezone `Asia/Ho_Chi_Minh`. `snapshot_id` dạng `YYYY-MM-DD` theo timezone đó.
- Giao diện đích mỗi nguồn: `crawl(cfg: SourceConfig) -> Iterator[RawJob]`, không `argparse`, không ghi file, không `print`. Giữ nguyên các hàm `parse_*`. Trạng thái thu thập chuyển vào bảng `source_crawl_state`. Một bước `ingest` duy nhất ghi `job_postings` + `job_observations`. LinkedIn tắt vĩnh viễn, không thu mới. TopCV ở chế độ `manual`.
- Nhịp một, thu quan sát (`crawl → redact → ingest → job_observations`), chạy tự động hằng ngày từ Sprint 1, không phụ thuộc bộ từ vựng, θ hay bảng `stat_*`, không được hoãn vì năng lực nhóm. Nhịp hai, tính tổng hợp, chạy được bằng CLI. Snapshot chạy tay và snapshot Dagster không phân biệt được ở tầng đọc.
- Dữ liệu nền nhập một lần thành snapshot gốc: `is_backfill = true`, `times_seen = 1`, D4 trả "không đánh giá được" cho mọi tin của nó. Đi qua đúng một lượt trích xuất bằng bộ máy mới. Mỗi tin mang `text_provenance ∈ {raw, rewritten_en}`. Mọi chỉ số phụ thuộc trích xuất kỹ năng báo cáo được tách theo `text_provenance`, có endpoint và truy vấn, không phải phép tính tay lúc viết báo cáo. Bộ chuẩn 200 JD và precision/recall tiếng Việt chỉ lấy từ tin `raw`. Văn bản gốc bất biến: không bước nào ghi đè `description`; bản làm sạch là trường mới. Không port `step-05` kế thừa.
- `aggregate` đếm `job_clusters`, không `job_postings`. Đại diện cụm chọn theo thứ tự: nguồn ưu tiên trong cấu hình, rồi bản ghi có nhiều trường thống kê nhất, rồi `job_url` A–Z. Mọi trường thống kê lấy từ đại diện.

**Tầng đọc (AD-5, AD-6, AD-7, AD-17, AD-22).**

- `haido_api` không chạy `GROUP BY`, phân vị, `AVG` hay `COUNT` trên bảng `job_*`. Được tra cứu theo khóa trên `stat_*`, và tính trên một tin người dùng dán chỉ bằng phép của registry. `stat_skill_rate` có một hàng cho mọi kỹ năng của ô, kể cả tỷ lệ 0. Hàng thiếu là lỗi dữ liệu.
- `stat_cells` khóa `(snapshot_id, role, branch, seniority, scope)`, lưu `n` và cơ cấu cấp bậc. Phép chọn ô là đường duy nhất, trả về ô, `n` và nhãn không tách rời. Chuỗi quay về chỉ đi trong cùng phạm vi: ô thành phố không quay về ô toàn quốc; ô thành phố thiếu mẫu thì "chưa đủ dữ liệu".
- API trả lộ trình đã xếp thứ tự. `web/` không có sắp xếp topo, không có so sánh 4 tầng, không có θ.
- Envelope mọi response có số: `{ data, meta }`. `meta` gồm `snapshot_date`, `snapshot_status`, `sources[]`, `sources_failed[]`, `thresholds`, `coverage_notes`, và một mục cho mỗi ô response dùng. Mỗi mục ô có `n`, `fallback_label`, `seniority_mix`, và `n_by_measure` cho số kỹ năng, số năm, lương, kèm `insufficient_by_measure`. Cổng hiển thị của một thước đo là `n_with_value` của chính thước đo đó. Một hàm duy nhất `domain.display_policy.suppression_for(measure_kind, n)` trả `null_data` hoặc `low_sample_shown`. Chỉ tỷ trọng cấu phần FR-33 được `low_sample_shown`. Tỷ lệ kỹ năng và phân vị luôn `null_data` khi dưới ngưỡng. `web/` không tự tính tỷ trọng. Thiếu `meta` là lỗi schema.
- Đường duy nhất gửi hồ sơ lên là `GET /api/v1/...?role=&level=&have=<mã,mã,...>`, cùng cách mã hóa link chia sẻ, trần 200 mã. Mức khớp, đếm theo nhóm, danh sách khoảng trống và số kỹ năng trùng chỉ do API trả. `web/` không chứa phép cộng, chia, trọng số hay đếm trên mã kỹ năng. Ghi chú addendum "FR-24 tính giao tập hợp ở frontend" bị spine này thay thế.
- Hình lỗi: `{ "error": { "code", "message", "snapshot_date" } }`. `code` snake_case, `message` tiếng Việt.
- Route: `/api/v1/<danh-từ-kebab>`. `GET` cho mọi dữ liệu thị trường, kể cả khi gửi hồ sơ. `POST` cho hai endpoint trích xuất, sự kiện ẩn danh, và các bảng `eval_*`. Tỷ lệ lưu số thực 0–1; làm tròn chỉ ở tầng hiển thị. Tiền là số nguyên VND/tháng gross, kèm `fx_version` của snapshot. Tỷ giá lúc quy đổi tin người dùng dán là tỷ giá của snapshot đang dùng.
- Chỉ `haido_core/steps/` ghi bảng thị trường. `haido_api` chỉ ghi `anon_events`, `unknown_mentions_pasted` và các bảng `eval_*`.

**Tham số, đồ thị, riêng tư, gỡ tin (AD-10, AD-11, AD-12, AD-21, AD-23).**

- Nằm trong bảng cấu hình có phiên bản, không có hằng số trong code: θ_core, θ_common, ngưỡng mẫu n = 30, cửa sổ 60 ngày, ngưỡng 30 tin để tạo nhánh, ngưỡng 5 điểm phần trăm FR-38, tỷ giá USD, công tắc từng nguồn, ngưỡng từng dấu hiệu D1–D7, B, estimator phân vị, trần kích thước và tốc độ hai endpoint POST. Mỗi snapshot lưu `config_version`.
- `skill_edges` chỉ chứa cạnh `PREREQUISITE` soạn tay, mỗi cạnh có nguồn và biên bản. Tần suất và đồng xuất hiện nằm ở bảng tổng hợp. Không phép tìm đường có trọng số đi qua cả hai loại cạnh.
- Đường ghi duy nhất cho lượt nhắc chưa nhận diện từ tin dán là `unknown_mentions_pasted` với ba cột `(keyword, freq, last_seen_date)`, không mã phiên, có `CHECK` độ dài và ký tự. Danh sách chờ từ pipeline đêm là bảng riêng kèm tần suất và lần thấy gần nhất. `anon_events` đúng bốn trường FR-17; `skill_code` có khóa ngoại tới `skills.code`. Không bảng nào nhận văn bản CV hay JD.
- Mã kỹ năng kebab-case, chỉ ASCII, không dấu, không bao giờ đổi. Bí danh song ngữ ở bảng riêng. Tên hiển thị là trường của `skills`, không suy từ mã. Vai trò, nhánh, cấp bậc, thành phố là enum trong `domain`, snake_case; chuỗi hiển thị tiếng Việt tra từ bảng.
- Mọi khóa `localStorage` có tiền tố `haido:` và được khai trong một module duy nhất dạng danh sách đóng. Không nơi nào gọi `localStorage` trực tiếp. Xóa hồ sơ xóa theo tiền tố. Mã phiên ẩn danh nằm trong danh sách đó. Link chia sẻ: `?role=<mã>&level=<mã>&have=<mã,mã,...>`.
- Bước `redact` chạy trước mọi lệnh ghi. Yêu cầu gỡ là hàng `takedown_requests`, sinh `source_exclusions`, áp trước `aggregate` của snapshot kế tiếp. Lệnh CLI dựng lại sinh snapshot mới với tập loại trừ khác. Không `DELETE` trên snapshot đã công bố.

**Trang công khai (AD-13, AD-14).** Sau khi snapshot chuyển `published` hoặc `partial`, bước cuối pipeline gọi route làm mới bằng secret dùng chung, rồi mồi từng URL trong sitemap bằng GET. Bước mồi thất bại thì lượt chạy báo lỗi. Trang nội dung không render động theo request. Chọn một mô hình ISR của Next 16 và khai trong `next.config`. Template chỉ gọi endpoint `stat_*`. Không render trường `description`. Route làm mới bảo vệ bằng header secret.

**Thử nghiệm (AD-18).** `anon_events` không thêm cờ thử nghiệm. Dữ liệu thử nghiệm nối qua bảng `eval_*` theo mã phiên. Loại thiết bị và vị trí trái/phải nằm trong `eval_post_session`. Bộ mã loại thao tác là enum đóng, dùng chung `web/` và `haido_api`, phân biệt đúng ba lựa chọn FR-21. `eval_pre_session` lưu 3 kỹ năng tự đoán dưới dạng mảng mã. Tình huống mẫu và câu ChatGPT là JSON tĩnh có phiên bản trong `eval_fixtures/`.

**Phân vị tất định (AD-26).** Seed dẫn xuất theo khóa `blake2b(snapshot_id | stat_cell_id | measure | p)`. Mỗi hàng phân vị lưu `seed`, `b`, `method`, `estimator`. Luật giá trị trùng chốt tường minh và có kiểm thử biên: ở n = 30 có thể P75 = P90, và D1 với D3 có thể kích hoạt cùng lúc.

**Cổng CI (AD-24).** Một job chặn merge, mỗi cổng là một kiểm thử có tên: hướng phụ thuộc; registry đóng tám phép; không tổng hợp trên `job_*` trong API; lời dẫn không có số trừ số trong tên công nghệ; câu chữ bị cấm (FR-25, FR-31, FR-47); hình dạng `meta`; riêng tư (không bảng nhận văn bản CV/JD, CV 5 MB không tạo file tạm, không bản ghi khớp email/điện thoại VN); tất định của lộ trình, mức khớp, dấu hiệu, câu Insights; đúng một head Alembic. Tên kiểm thử chứa mã FR hoặc AD.

**Sao lưu (AD-25).** `pg_dump` hằng ngày ra ngoài VPS, giữ 14 bản, có một lần phục hồi thử đã ghi biên bản trước Sprint 6. Dữ liệu `eval_*` sao lưu thêm sau mỗi ngày có phiên thử nghiệm. Không `DROP COLUMN` trên bảng mang dữ liệu snapshot lịch sử.

**Vận hành và dữ liệu nền.** Tin nền có ngày thấy lần cuối khoảng 26/10/2026 và rơi khỏi cửa sổ 60 ngày vào khoảng 25/12/2026. Dữ liệu nền là nhiên liệu review giữa kỳ. Tới lúc bảo vệ, số phải đứng trên dữ liệu nhóm tự thu. Bộ chuẩn 200 JD không lấy từ dữ liệu nền vì văn bản gốc đã mất; bộ chuẩn chỉ bắt đầu sau khi nhịp thu quan sát chạy. Báo động FR-1 dùng email cộng bảng `pipeline_run` là đủ cho v1.

**Đã hoãn, không đưa vào story v1.** Xu hướng theo thời gian và dự báo; pgvector và embedding; Apache AGE / Cypher; OCR; trang SEO theo thành phố, kỹ năng, câu hỏi; mô hình trích xuất rẻ hơn trước khi có số Sprint 2; tự động hóa TopCV; nhiều instance, hàng đợi, cache phân tán; tài khoản và ứng dụng di động; báo động Telegram/Slack; blue-green và môi trường thứ ba.

**Chỗ spine và PRD để mở — story không được tự chốt.**

- Kiểm định z-test cho thẻ so sánh Insights, ngoài ngưỡng 5 điểm (PRD câu hỏi 1).
- Danh sách vai trò/nhánh cuối, giá trị θ sau Sprint 2, tỷ giá USD, và 4–5 vai trò có đồ thị khi công khai.
- Ai kiểm duyệt danh mục tài liệu và chu kỳ kiểm link chết.
- Có hay không bộ chuẩn khoảng 20 CV.
- Ngưỡng D4 có nâng sau khi đủ lịch sử snapshot hay không.
- B = 1.000 có chạy kịp trong một lượt đồng thời hay không: đo Sprint 2, chưa giảm B trước số đo.
- Chất lượng đường người dùng dán (`claude-sonnet-5-5`) chưa có thước đo riêng; SM-6 đo đường lô.
- Chi phí Batch API chưa có ước lượng; cần ước lượng ở Sprint 2 trước khi coi trần 5–10 USD là đã kiểm.
- Vùng VPS chưa xác nhận. Hai bộ số báo cáo (pipeline cũ và pipeline mới) cần một bước hòa giải hoặc một câu giải thích, không trộn thành một bộ số.
- Phần "không xác định thành phố" trên bản đồ: PRD cộng vào 100% tách khỏi "Khác"; hợp đồng UX ghi chưa chốt chỗ đứng trên hình. Làm theo PRD cho đến khi có quyết định khác: không vẽ thành cột, không nuốt vào "Khác".

### UX Design Requirements

Hợp đồng UX là cặp `DESIGN.md` (hình) và `EXPERIENCE.md` (hành vi), trạng thái final, cập nhật 2026-11-04. Khi artboard lệch spine, làm theo spine. Không có hệ thống UI shadcn. Không thêm màu cho chế độ sáng.

UX-DR1: Dựng bảng màu thành token và dùng đúng nghĩa. Nền trang `#070B10`, header `#0A1017`, panel `#0D141C`, inset `#0A1118`, ô dán `#05080C`, khung cảnh báo `#141009`, chữ chính `#E6EDF3`. Vàng chanh `#C5F36A` chỉ cho việc chính và liên kết, chữ trên nút chính `#0A0F05`. Xanh lam `#62D9EE` là mục đang chọn hoặc con số đang đọc. Hổ phách `#F5A65B` là cỡ mẫu nhỏ, ô so sánh đã quay về, chưa đủ dữ liệu, hoặc hồ sơ tạm. Hổ phách không có nghĩa tin giả. Nút chính tắt dùng nền `#2A3A44` và chữ `#8496A6`. Không thêm bảng màu sáng và không đổi các hex này cho đẹp hơn.

UX-DR2: Chữ giao diện là Be Vietnam Pro. Số, cỡ mẫu n, ngày snapshot, phần trăm, mã, tên file và chân trang là JetBrains Mono. Thang chữ lấy từ token trong `DESIGN.md`, từ display 34px đến micro 10px. Không có bậc lớn hơn 34px. Phần trăm không viết bằng Be Vietnam Pro.

UX-DR3: Artboard xem ở rộng 1440px. Cột nội dung ứng dụng tối đa 1280px, đệm ngang 24px. Trang chính sách tối đa 760px. Trang vai trò tối đa 860px. Panel đệm 20px. Vùng bấm tối thiểu 44px. Nav cao 52px. Nút chính cao 48px trên các màn ứng dụng, cao 44px trên Bản đồ và màn CV scan. Góc nút 8px, panel 12px, chip hồ sơ và chip vai trò bo tròn đầy (999px).

UX-DR4: Độ sâu là viền 1px và lớp nền, không bóng đổ. Bóng đứng yên chỉ có ở toast (`0 12px 40px rgba(0,0,0,.5)`). `prefers-reduced-motion: reduce` tắt animation và transition, gồm vòng `.flash` trên màn khoảng trống.

UX-DR5: Các màn ứng dụng có lưới nền mờ: hai linear-gradient của màu selected ở độ phủ 0,04, ô 40px. Trang chính sách và trang vai trò không có lưới này; nền vẫn là canvas.

UX-DR6: `app-header` là một hàng flex-wrap: wordmark "HẢI ĐỒ" + dấu vàng chanh + "IT", bốn mục nav (Bản đồ, Insights, Cố vấn, Soi tin), chip hồ sơ. Mục đang mở có `aria-current="page"`, chữ chính và gạch dưới 2px màu selected. Nav có tên "Điều hướng chính". Trang chính sách và trang vai trò không dùng header nav này. Mục nav tràn thì cuộn ngang.

UX-DR7: `profile-chip` cao tối thiểu 44px. Ba trạng thái đã thấy: "Chưa có hồ sơ" (chấm slate), "Hồ sơ tạm · chưa lưu" (chấm hổ phách), "Hồ sơ: Java Backend · trong trình duyệt" (chấm vàng chanh). Bấm chip mở màn lưu hồ sơ.

UX-DR8: `button-primary` là một việc chính của màn. Tắt khi điều kiện chưa đủ, kèm câu giải thích, `cursor: not-allowed`. Không dùng nút chính cho liên kết phụ. Trỏ chuột đổi nền sang `#D6FA94`.

UX-DR9: `button-ghost` cho việc phụ: quay lại, chọn file khác, tải bản `.md`, soi tin khác. Nền trong, viền chip. Trỏ thì viền selected, chữ chính, không đổi nền.

UX-DR10: `button-danger` là biến thể ghost của "Xoá hồ sơ khỏi trình duyệt": viền `#5A3E22`, chữ `#FFD3A6`. Trỏ thì viền hổ phách và chữ `#FFE6CC`. Xóa hồ sơ kỹ năng, vai trò mục tiêu và mã phiên ẩn danh.

UX-DR11: `chip` là pill, có `aria-pressed`. Trên Bản đồ, một vai trò được chọn: viền selected, nền selected độ phủ 0,14. Trên màn tự chọn, chưa chọn là nét đứt `#3A5163` và nền trong; đã chọn thì nét liền. Bấm lần nữa để bỏ kỹ năng.

UX-DR12: `segmented-control` trên Bản đồ là "3D", "Biểu đồ 2D", "Bảng", cùng một bộ số liệu, chữ mono 12px. Trên màn tự chọn, cụm này đổi vai trò mục tiêu, chữ Be Vietnam Pro 14px. Artboard vẽ cụm Bản đồ cao 38px; khi dựng đưa về 44px. Đang chọn: nền selected 0,16 và viền trong selected.

UX-DR13: `icon-button` vuông 44px cho xoay trái 30 độ, xoay phải 30 độ và đặt lại góc nhìn trên Bản đồ. Có `aria-label`. Không thay cho việc kéo. Ngưỡng kéo trước khi tính là đang kéo: 6px. Kéo xoay, kéo dọc để nghiêng.

UX-DR14: `panel` là khối nội dung nền panel, viền `#1C2A36`, góc 12px. Không tự mở, không tự đóng. `kicker` là nhãn ngắn mono 11px, in hoa, giãn cách 0,08em, không chứa câu khuyên. Trên khung cảnh báo, kicker chuyển hổ phách.

UX-DR15: `data-table` chữ 14px. Đầu cột 11px mono, giãn cách 0,06em, màu chữ muted. Hàng ngăn bằng `#15212B`. Cột số canh phải, JetBrains Mono. Mỗi số có n. Ô n < 30 trên bảng thành phố không hiện tỷ lệ, chỉ "chưa đủ dữ liệu".

UX-DR16: `site-footer` có trên mọi màn ứng dụng: gạch trên, chữ mono 12px. Một bên là câu meta snapshot, một bên là liên kết "Chính sách dữ liệu" màu primary.

UX-DR17: `map-column` vẽ ba cột Hà Nội, TP.HCM, Đà Nẵng trong khung cao 560px, perspective 1500px. Dưới 640px khung còn 420px và tỷ lệ 0,62. Mặt trên cột màu selected; cột đang chọn đổi mặt trên thành chữ chính. Mặt trước/sau `#1F6A7C`, hai bên `#154B5B`. Cột n < 30 opacity 0,4, nhãn viền hổ phách đậm. Phần trăm của cột mờ nằm trong lớp ẩn và chỉ hiện khi trỏ, chạm hoặc focus, không chỉ khi trỏ chuột. Nhãn đứng là câu cỡ mẫu nhỏ. Cột có câu aria gồm tên nơi, phần trăm, n, và câu cỡ mẫu nhỏ khi n < 30. Bấm cột mở bảng thành phố. "Khác" nằm ở chú thích kèm tỷ trọng, không phải cột, sao cho cột + Khác + phần không xác định thành phố = 100%.

UX-DR18: `meter` dùng rãnh `#13202B` hoặc `#16222D`, phần đủ mẫu tô selected. Trên Bản đồ, thanh của cột n < 30 vẫn có bề rộng, phủ sọc, phần trăm ẩn đến khi trỏ, chạm hoặc focus. Trên bảng thành phố, Insights và trang vai trò, n < 30 thì không vẽ tỷ lệ. Kỹ năng chưa có trên màn tự chọn tô `#3E6A80`.

UX-DR19: `level-bar` cao khoảng 26–28px, các đoạn dùng `#1F4A58`, `#2E5A6A`, `#3E8296`, `#62D9EE`, `#A8EAF5`. Số đếm ghi bằng chữ cạnh thanh, kèm n và ngày. Cùng một hex không gắn với một cấp bậc trên mọi màn. Không gán tên cấp cho các hex này khi dựng. Thanh này hiện khi Cố vấn quay về ô rộng hơn, và trên trang vai trò khi n ≥ 30.

UX-DR20: `skill-node` trên lộ trình chung là thẻ 200×88px, nền panel, góc 10px, viền 1,5px, phần trăm mono 22px. Trỏ: viền selected, dịch lên 2px. Bấm mở chi tiết kỹ năng. Nút ghi tỷ lệ xuất hiện và nhóm. Trên màn tự chọn: thẻ tĩnh nền inset; đã có thì viền và thanh selected; chưa có thì viền `#1C2A36` và thanh `#3E6A80`. Kỹ năng đã có được tô và không nằm trong danh sách còn phải học.

UX-DR21: `select` nền inset, cao 44px, góc 8px, mũi tên là hai tam giác selected. Đổi vai trò hoặc ô đối chiếu thì kết quả tính lại, không tải lại trang, không dán lại tin.

UX-DR22: `checkbox` khung 24×24, viền `#4A6478`, góc 6px. Đã chọn: nền selected, dấu tích màu chữ nút chính. Nhãn là vùng bấm đi cùng. Chưa chọn thì không gửi CV. Nhãn nêu văn bản CV được gửi tới nhà cung cấp AI bên ngoài (ghi tên; spine chốt Claude), không lưu file gốc hay thông tin định danh, và có thống kê ẩn danh theo mã phiên. `drop-zone` nhận PDF có lớp chữ hoặc DOCX, tối đa 5 MB, kéo thả hoặc chọn file, góc 14px, viền nét đứt selected.

UX-DR23: `step-list` liệt kê từng bước đang chạy, không thay bằng một vòng xoay. Năm bước: đọc chữ trong file, gửi văn bản tới dịch vụ AI, chuẩn hóa tên kỹ năng, đối chiếu với ô thống kê, xếp khoảng trống. Câu ngưỡng ở bước cuối dùng θ_core 30% và θ_common 10%, không dùng 60% và 30% in trên artboard. Bước xong hoặc đang chạy dùng chữ chính; bước chờ dùng chữ dim. Đồng hồ màu selected. Artboard chạy khoảng 8–10 giây.

UX-DR24: `gap-actions` có hai nút chính cao 44px: "Tôi chưa biết" và "Tôi đã biết, chỉ là CV chưa ghi". Khi hồ sơ tạo từ CV, lựa chọn phụ là chữ gạch chân 13px: "CV của tôi có ghi rồi (hệ thống đọc sót)". Đang chọn: nền selected 0,14 và viền trong selected. Huy hiệu khoảng trống cốt lõi màu hổ phách; huy hiệu thường gặp màu chữ muted. Đổi được lựa chọn; lựa chọn sau cùng có hiệu lực. Chip và nút xác nhận dùng `aria-pressed`.

UX-DR25: `stat-block` tách số khỏi lời dẫn: tỷ lệ xuất hiện, n, ngày, nguồn, nền inset, góc 12px, số JetBrains Mono. Lời dẫn không chứa số. Tài liệu chỉ lấy từ danh mục đã kiểm duyệt. Bấm nút không gọi mô hình lúc đó. Phần "hay đi cùng" khi chưa đủ 30 tin ghi "chưa đủ dữ liệu", không hiện tỷ lệ.

UX-DR26: `toast` cố định, giữa, cách đáy 24px, nền chữ chính, chữ màu mực nút chính, `aria-live="polite"`. Artboard hiện khoảng 2,4 giây cho "đã tạo file tóm tắt" hoặc "đã lưu N kỹ năng trong trình duyệt". Dòng đếm kỹ năng trùng cũng dùng `aria-live="polite"`.

UX-DR27: `paste-field` là một ô, không có ô chat. Nền `#05080C`, mono 14px / dòng 1,7, cao tối thiểu 340px, kéo dọc được, có đếm ký tự. Nội dung không được lưu sau khi xử lý. Ô trống thì nút "Soi tin" tắt. Đã có chữ trong khoảng 200 đến 20.000 ký tự thì nút bật.

UX-DR28: `match-ring` là vòng 132px, chỉ hiện khi hồ sơ có dữ liệu. Số ở tâm mono 34px. Dòng phụ là đếm thô theo nhóm. Dòng trọng số: cốt lõi 3, thường gặp 2, riêng của công ty 1. Hợp đồng số đã chốt của UJ-2 là mức khớp 89% và dòng "4/4 cốt lõi, 2/2 thường gặp, 0/2 riêng của công ty". Không lấy bộ số trên artboard kết quả làm số của sản phẩm.

UX-DR29: `sign-card` hiện mỗi dấu hiệu đã kích hoạt: mã, dữ kiện đã kích hoạt, gợi ý để tự kiểm tra. Ô mã D màu hổ phách, viền hổ phách đậm. Không phải kết luận tin giả. Câu dưới các dấu hiệu lấy nguyên từ FR-31.

UX-DR30: `insight-card` có một câu mẫu, số căn cứ kèm n và ngày, và một lối sang Cố vấn hoặc Bản đồ. Số trong câu mẫu màu selected. Câu trên thẻ là mẫu có số điền từ bảng, không phải đoạn văn tự do. Artboard đang dùng mẫu "[vai trò]: [x]% tin nhận Intern hoặc Fresher (n = [n])" và "Trong [n] tin có [A], [x]% cũng nhắc [B]"; năm loại thẻ FR-37 vẫn phải có mẫu của chính loại đó theo FR-39.

UX-DR31: `notice` dùng cho nhóm so sánh đã quay về và cho CV không đọc được chữ. Nền `#141009`, viền hổ phách đậm, kicker hổ phách. Khung CV scan dùng `role="alert"`. Khung quay về ô thống kê dùng `role="status"`. Nhãn quay về nêu n của ô bị thiếu, và n cùng cơ cấu cấp bậc của ô đang dùng. Ví dụ đã chốt ở Cố vấn: Java Backend · Intern–Junior có 26 tin, dùng Backend · Intern–Junior, n = 52, cơ cấu 13 Intern, 7 Fresher, 32 Junior.

UX-DR32: `doc-section` cho trang chính sách: tiêu đề mục 20px, thân 16px màu `#D5DEE7`, line-height 1,7. Số mục mono. Dưới 560px các mục xếp một cột. Đọc được không cần tài khoản, không có nav bốn mục. Năm mục: mục đích nghiên cứu học thuật phi thương mại; nguồn đang dùng; công bố mức tổng hợp; CV và tin dán không lưu; yêu cầu gỡ trong 48 giờ. Không có bảng R1–R4. Không có hai câu cấm của FR-47.

UX-DR33: Mười lăm màn, đúng việc sau. Màn 1–13 dùng header bốn mục. Màn 14 và 15 không có nav đó.

- `ban-do`: mở ứng dụng vào đây. Vai trò mặc định "Tất cả" (artboard mở sẵn Backend thì bỏ). Lối xem 3D. Chú thích nguồn, ngày snapshot và ba câu FR-36 đang hiện.
- `ban-do-ha-noi`: bấm cột Hà Nội. Cơ cấu vai trò, kỹ năng hàng đầu, ngày snapshot. Mọi số có n.
- `co-van-chung`: lộ trình chung khi chưa có hồ sơ. Không vẽ nhóm riêng của công ty. Kỹ năng nền tảng mang nhãn "Kỹ năng nền tảng (cần cho X)".
- `co-van-cv`: ô đồng ý rồi kéo thả PDF hoặc DOCX.
- `co-van-dang-doc`: từng bước, khoảng 8–10 giây.
- `co-van-khoang-trong`: ba lựa chọn cho mỗi khoảng trống. Nút lưu chỉ bật khi đã xác nhận hết. Câu "Còn {số} khoảng trống chưa xác nhận."
- `co-van-ky-nang`: kỹ năng người dùng vừa bấm, không cố định là Docker của artboard.
- `co-van-luu`: hồ sơ trong trình duyệt và tóm tắt hai phần, ghi vai trò mục tiêu, n, ngày. Có xóa hồ sơ.
- `cv-anh-scan`: dưới 30 ký tự có nghĩa, báo trong 1 giây, ba lối thoát, không OCR. Artboard minh họa phát hiện khi chưa gửi gì ra ngoài.
- `soi-tin-dan`: một ô dán, nút "Soi tin", không ô chat.
- `soi-tin-ket-qua`: mức khớp, phân vị, dấu hiệu. Đổi ô thống kê không dán lại.
- `insights`: thẻ câu mẫu. Bộ lọc vai trò theo FR-40 dù artboard chưa vẽ bộ lọc.
- `co-van-khong-cv`: tự bật kỹ năng đã có. Đổi vai trò thì tô kỹ năng trùng và có dòng "Có N kỹ năng trong lộ trình này trùng với hồ sơ của bạn."
- `chinh-sach-du-lieu`: từ chân trang hoặc URL riêng.
- `trang-vai-tro`: một ô vai trò × mọi cấp bậc × toàn quốc. Không thứ tự quay về, không tỷ trọng thành phố. Gọi cấp Mid, không gọi Middle như artboard.

UX-DR34: Ngưỡng nhóm kỹ năng của sản phẩm là cốt lõi ≥ 30%, thường gặp từ 10% đến dưới 30%, riêng của công ty dưới 10%. Bỏ chữ artboard "Cốt lõi ≥ 60% · Thường gặp 30–59% · Riêng của công ty < 30%" và câu "ngưỡng 60% và 30%" trong bước đọc CV. Nút kỹ năng nét đứt trên artboard theo ngưỡng 60/30 không phải quy tắc hình.

UX-DR35: Ba lưu ý FR-36 luôn nhìn thấy trên Bản đồ, đúng câu trong PRD, không dùng ba câu khác đang in trên artboard. Kèm danh sách nguồn đang bật và ngày snapshot.

UX-DR36: Lộ trình chung không có cột "RIÊNG CỦA CÔNG TY" và không có nút Kafka của artboard `co-van-chung`, trừ khi một kỹ năng là kỹ năng nền tảng với nhãn "Kỹ năng nền tảng (cần cho X)".

UX-DR37: Soi tin không dùng cách artboard gán D1 cho email cá nhân, D2 cho tin đăng lại, hay cụm "tin giả". D1 là số kỹ năng yêu cầu cao hơn 90% số tin cùng ô. D2 là hơn một nửa kỹ năng đã nhận diện thuộc nhóm riêng của công ty. "Tin không công bố khoảng lương" là dòng trung tính, không phải dấu hiệu.

UX-DR38: Nút "chọn file khác" trên artboard cao 36px và cụm 3D / 2D / bảng cao 38px. Khi dựng, đưa cả hai về sàn 44px.

UX-DR39: Mở ứng dụng thì vào Bản đồ, vai trò "Tất cả", lối 3D, chú thích đang hiện. Đổi vai trò thì chiều cao cột đổi theo tỷ trọng toàn quốc của vai trò đó. WebGL không chạy thì tự chuyển sang lối 2D hoặc bảng, không màn hình lỗi. Trên điện thoại, Bản đồ là danh sách thành phố và thanh tỷ trọng, kèm gợi ý mở trên máy tính; lối 2D hoặc bảng vẫn có.

UX-DR40: Vai trò chưa có đồ thị học trước – học sau thì không vẽ đồ thị. Hiện danh sách theo nhóm cốt lõi và thường gặp, kèm tỷ lệ, và câu "Lộ trình học có thứ tự cho vai trò này đang được biên soạn". Nút từ bảng thành phố nói cùng câu. Ô thành phố n < 30 trên bảng chi tiết không hiện tỷ lệ, chỉ "chưa đủ dữ liệu".

UX-DR41: Chưa tích ô đồng ý thì nút "Đọc CV và đối chiếu" tắt, kèm câu "Đánh dấu ô đồng ý ở trên để tiếp tục." Đã đồng ý và đã có file thì nút bật. CV dưới 30 ký tự có nghĩa thì trong 1 giây sang màn scan, nêu lý do và ba lối: PDF xuất từ Word, Canva hoặc Overleaf; DOCX; tự chọn kỹ năng. v1 không OCR.

UX-DR42: Trên màn khoảng trống, "Tôi chưa biết" ở lại lộ trình; "Tôi đã biết, chỉ là CV chưa ghi" vào danh sách cần ghi CV; "CV của tôi có ghi rồi" vào hồ sơ và không vào danh sách cần ghi CV. Nút "Lưu hồ sơ và tải bản tóm tắt" tắt cho tới khi mọi khoảng trống đã có lựa chọn. Cao trào đã chốt: CV đã ghi Java, Git, REST API, Spring Boot, MySQL; "đã biết nhưng CV chưa ghi" cho SQL, PostgreSQL, Docker và Microservices; "chưa biết" cho CI/CD rồi Redis. Redis không phải riêng của công ty. Lộ trình còn lại xếp CI/CD trước Redis. Hai bộ số minh họa (UJ-1 và artboard n = 52) chưa chốt bộ nào là ví dụ kể chuyện; phân loại kỹ năng của cao trào lấy theo ngưỡng 30/10, không theo ngưỡng 60 của artboard.

UX-DR43: Màn chi tiết kỹ năng là kỹ năng người dùng vừa bấm. Lời dẫn không số, số ở `stat-block`, tài liệu từ danh mục đã kiểm duyệt, không gọi mô hình lúc bấm.

UX-DR44: Soi tin khi ô dán trống thì nút tắt. Tin không thuộc IT thì câu "Tin này có vẻ không thuộc lĩnh vực IT" và không tính mức khớp. Có hồ sơ thì đầu trang "Đang đối chiếu với: [vai trò] · [cấp]", đổi được mà không dán lại. Lương chưa đủ mẫu thì "chưa đủ dữ liệu (X/30 tin có lương)"; số kỹ năng yêu cầu vẫn có phân vị. Hồ sơ trống lúc soi thì mời tải CV hoặc tự chọn; phần so với thị trường vẫn hiện. Tin ngắn hơn 200 hoặc dài hơn 20.000 ký tự chưa có câu báo trên artboard; ngưỡng vẫn là FR-26 và phải có câu báo khi dựng.

UX-DR45: Năm loại thẻ FR-37 đều phải làm. Artboard Insights chỉ vẽ "Cửa vào cho người mới" và "Bộ kỹ năng hay đi cùng nhau". Ba loại còn lại chưa có hình: bậc thang Junior → Senior, khác biệt giữa các thành phố, ngành và nhà tuyển dụng nổi bật. Thẻ đủ mẫu có câu mẫu, n và ngày. Nếu một vai trò không có thẻ nào đủ điều kiện, trang ghi "chưa đủ dữ liệu cho vai trò này."

UX-DR46: Đã chốt theo FR-38 khi duyệt Epic 4. Thẻ chỉ hiện khi mọi số của thẻ có n ≥ 30. Thẻ so sánh còn cần chênh ít nhất 5 điểm phần trăm. Thẻ n < 30 không nằm trên trang.

UX-DR47: Trang vai trò khi n ≥ 30 có đoạn đầu ít nhất ba kỹ năng, mỗi kỹ năng một tỷ lệ, kèm n, nguồn đang bật và ngày snapshot. Khi n < 30, đoạn đầu chỉ "chưa đủ dữ liệu (n = X)", không tên nhóm, không phần trăm. Phân vị lương hoặc số năm chỉ khi có ít nhất 30 tin có đúng trường đó. Có liên kết tới chính sách. Không liệt kê tin, không tên công ty, không link tin gốc.

UX-DR48: Tự chọn kỹ năng bằng cách bấm để thêm hoặc bỏ, không cần CV. Minh họa đã chốt: Java, SQL, Git. Đổi sang Data Engineer thì tô kỹ năng trùng và hiện "Có N kỹ năng trong lộ trình này trùng với hồ sơ của bạn." Không có câu "Data giờ khó xin việc" hay "Backend bão hòa".

UX-DR49: Sàn truy cập. Các cặp chữ chính trên canvas đo được từ 8,9:1 trở lên; nút chính 15,1:1. Cặp chữ nút tắt (`#8496A6` trên `#2A3A44`) đo 3,9:1 và chưa có quyết định đổi hex; story không tự đổi màu này. `:focus-visible` có trên liên kết và nút; màn Bản đồ còn gắn cho input, select, textarea. Mọi điều khiển nhận cùng vòng `#C5F36A`, dày 2px, lệch 2px. Thứ tự tab theo thứ tự đọc. Chưa có sơ đồ phím tắt. Đồng hồ đang đọc trên artboard đặt `aria-live="off"`; chưa chốt trình đọc có cần nghe bước đang chạy hay không, nên không tự bật live region cho đồng hồ.

UX-DR50: Điện thoại không phải ứng dụng riêng và chưa có artboard. Làm theo PRD: Soi tin đầy đủ; Cố vấn là danh sách khoảng trống dạng thẻ, đủ ba lựa chọn FR-21, kèm gợi ý mở trên máy tính; Bản đồ là danh sách thành phố và thanh tỷ trọng; Insights một thẻ một hàng; FR-41 đến FR-45 đầy đủ, hai phương án so sánh mù xếp trên/dưới. Mốc đã có hình: dưới 640px khung bản đồ 3D còn cao 420px; dưới 560px mục trang chính sách một cột. Insights, trang chính sách ngoài mốc 560px, và trang vai trò chưa có quy tắc xếp lại riêng ngoài flex-wrap.

UX-DR51: Giọng microcopy nêu dữ kiện. Mọi số kèm n và ngày snapshot. Thiếu dữ liệu thì viết "chưa đủ dữ liệu", không đoán, không để trống, không kèm lời xin lỗi thay cho việc giấu số. Không khuyên nộp hay không nộp. Không kết luận tin thật hay giả. Không dùng "lừa đảo", "tin giả", "tin ma". Nhóm thường gặp được nói là "nên học sau khi đã nắm các kỹ năng cốt lõi". Không câu nào khuyên bỏ qua một kỹ năng. Không dùng "lộ trình chuyển việc".

UX-DR52: Không đưa vào sản phẩm các màn đã loại: lương theo tuần, hạn dùng kỹ năng, dự báo 18 tháng, mô phỏng nếu-thì, hộ chiếu kỹ năng, chỉ số phản hồi nhà tuyển dụng, so sánh offer, tập thương lượng, nhảy việc, remote và Nhật, năm agent trò chuyện. Không đưa lại trạng thái "đang học", số tuần cho từng kỹ năng, câu Insights do mô hình viết, "không ghi lương" là một dấu hiệu, hay chiều cao cột bằng tỷ trọng của vai trò trong thành phố. Nút "Chạy lại mô phỏng" là điều khiển prototype, không ship. Nút "Huỷ" trên màn đang đọc chưa có đích; không tự bịa đích. Toast xóa hồ sơ trên artboard nói sẽ xóa sau khi xác nhận, nhưng không có hình hộp xác nhận; không tự thêm modal xác nhận cho đến khi có quyết định. Escape không gán cho hộp thoại nào của 15 màn này. Mười lăm màn không có lớp modal. Modal thử nghiệm FR-42 đến FR-44 nằm ngoài 15 màn và vẫn phải làm theo PRD.

UX-DR53: Những việc PRD bắt buộc nhưng chưa có hình vẫn phải làm, bám chữ PRD chứ không chờ artboard: vai trò chưa có đồ thị; ô thành phố n < 30; hồ sơ trống lúc xem kết quả Soi tin; tin không thuộc IT; tin ngoài khoảng 200–20.000 ký tự; phân vị số năm kinh nghiệm; kỹ năng chưa nhận diện; khoảng tin cậy khi 30 ≤ n < 100; danh sách đạt/không đạt FR-46, không gộp một điểm; nút "Copy link lộ trình" FR-15; bộ lọc vai trò Insights FR-40; modal đầu phiên và cuối phiên của chế độ thử nghiệm.

UX-DR54: Ô thả CV còn trống chưa có hình riêng; artboard `co-van-cv` mở sẵn file đã thả. Khi dựng vẫn phải có trạng thái ô trống, nút chính tắt. Nguồn, email gỡ, tên nhóm và ngày cập nhật trên artboard chính sách còn là chỗ giữ; nội dung thật lấy từ vận hành, không bịa trong story. Tên nhà cung cấp trên ô đồng ý lấy từ quyết định Claude của spine, vì artboard chỉ ghi "một dịch vụ AI bên ngoài".

### FR Coverage Map

FR-1: Epic 1 - Thu thập hằng ngày theo từng nguồn đang bật
FR-2: Epic 1 - Thu thập lịch sự, ngoại lệ R1–R4 là dữ liệu có tên
FR-3: Epic 1 - Snapshot và vòng đời tin
FR-4: Epic 1 - Gom tin trùng thành cụm, mỗi cụm tính một lần
FR-5: Epic 1 - Xóa thông tin cá nhân của người đăng tin trước khi lưu
FR-6: Epic 1 - Chuẩn hóa kỹ năng song ngữ và số năm kinh nghiệm
FR-7: Epic 1 - Phân loại vai trò, nhánh, cấp bậc, thành phố
FR-8: Epic 1 - Chuẩn hóa lương về VND/tháng gross
FR-9: Epic 1 - Bảng tổng hợp, nhóm kỹ năng theo θ, bootstrap phân vị
FR-10: Epic 2 - Tải CV sau khi đồng ý
FR-11: Epic 2 - Báo CV ảnh scan trong 1 giây, không OCR
FR-12: Epic 2 - Trích kỹ năng từ CV vào hồ sơ
FR-13: Epic 2 - Tự chọn kỹ năng, không cần CV
FR-14: Epic 2 - Lưu hồ sơ trong trình duyệt và xóa sạch
FR-15: Epic 2 - Link chia sẻ vai trò và mã kỹ năng
FR-16: Epic 2 - Tải bản tóm tắt hai phần
FR-17: Epic 2 - Sự kiện ẩn danh đúng bốn trường
FR-18: Epic 2 - Chọn vai trò mục tiêu và cấp bậc
FR-19: Epic 2 - Lộ trình chung và thứ tự quay về ô thống kê
FR-20: Epic 2 - Lộ trình cá nhân, trừ kỹ năng đã có
FR-21: Epic 2 - Ba lựa chọn xác nhận khoảng trống
FR-22: Epic 2 - Dựng lộ trình tất định theo bốn tầng
FR-23: Epic 2 - Chi tiết kỹ năng, lời dẫn không chứa số
FR-24: Epic 2 - Tô kỹ năng trùng khi đổi vai trò
FR-25: Epic 2 - Diễn đạt nhóm thường gặp, không khuyên bỏ qua kỹ năng
FR-26: Epic 3 - Dán tin và trích kỹ năng
FR-27: Epic 3 - Nhận diện vai trò và cấp bậc của tin
FR-28: Epic 3 - Mức khớp có trọng số
FR-29: Epic 3 - Phân nhóm kỹ năng của tin, kể cả chưa nhận diện
FR-30: Epic 3 - Phân vị số kỹ năng, số năm, lương
FR-31: Epic 3 - Bảy dấu hiệu cần kiểm tra
FR-32: Epic 3 - Khớp tin dán với tin đã thu thập
FR-33: Epic 1 - Bản đồ ba cột theo tỷ trọng toàn quốc
FR-34: Epic 1 - Bảng chi tiết thành phố
FR-35: Epic 2 - Từ bảng thành phố sang Cố vấn với vai trò đã chọn
FR-36: Epic 1 - Chú thích nguồn, ba lưu ý, lối 2D/bảng và WebGL
FR-37: Epic 4 - Năm loại thẻ Insights
FR-38: Epic 4 - Ngưỡng hiện thẻ
FR-39: Epic 4 - Câu kết luận từ mẫu câu cố định
FR-40: Epic 4 - Lọc thẻ theo vai trò
FR-41: Epic 6 - Bật chế độ thử nghiệm bằng link
FR-42: Epic 6 - Modal đầu phiên, trước khi thấy số
FR-43: Epic 6 - Modal cuối phiên, một lần mỗi mã phiên
FR-44: Epic 6 - So sánh mù trên tình huống mẫu cố định
FR-45: Epic 6 - Ẩn danh tuyệt đối và xuất một bảng theo phiên
FR-46: Epic 3 - Chất lượng JD từng mục đạt hoặc không đạt
FR-47: Epic 5 - Trang chính sách dữ liệu và yêu cầu gỡ
FR-48: Epic 5 - Trang thị trường công khai theo vai trò mục tiêu

## Epic List

### Epic 1: Thấy nhu cầu thị trường trên bản đồ
Sinh viên mở ứng dụng và thấy Hà Nội, TP.HCM, Đà Nẵng chiếm bao nhiêu phần tin của vai trò đang chọn. Mỗi số có cỡ mẫu, nguồn và ngày snapshot. Đêm pipeline lỗi thì bản đồ vẫn mở trên snapshot gần nhất. Cây mã, việc bọc scraper, chuẩn hóa lương và phân vị nằm trong epic này vì bản đồ cần số thật từ snapshot đêm.
**FRs covered:** FR-1, FR-2, FR-3, FR-4, FR-5, FR-6, FR-7, FR-8, FR-9, FR-33, FR-34, FR-36

### Epic 2: Biết mình thiếu gì và học gì trước
Sinh viên tải CV hoặc tự chọn kỹ năng, xác nhận khoảng trống, nhận lộ trình có thứ tự, lưu hồ sơ trong trình duyệt, tải tóm tắt và copy link. Từ bảng thành phố bấm sang Cố vấn với vai trò đã chọn. Hai vai trò của review giữa kỳ và bốn đến năm vai trò lúc công khai là cùng một việc, làm theo thứ tự đó.
**FRs covered:** FR-10, FR-11, FR-12, FR-13, FR-14, FR-15, FR-16, FR-17, FR-18, FR-19, FR-20, FR-21, FR-22, FR-23, FR-24, FR-25, FR-35

### Epic 3: Soi một tin trước khi nộp
Sinh viên dán một JD và thấy mức khớp với hồ sơ, phân vị so với mặt bằng, bảy dấu hiệu cần tự kiểm tra, và từng mục chất lượng đạt hoặc không đạt.
**FRs covered:** FR-26, FR-27, FR-28, FR-29, FR-30, FR-31, FR-32, FR-46

### Epic 4: Đọc những điểm đáng chú ý trong dữ liệu
Sinh viên lọc theo vai trò và đọc năm loại thẻ. Câu trên thẻ là mẫu điền số. Người đọc chưa cần hồ sơ. Epic này đứng trên snapshot của Epic 1. Thẻ n < 30 không hiện, theo FR-38.
**FRs covered:** FR-37, FR-38, FR-39, FR-40

### Epic 5: Đọc mặt bằng một vai trò mà không mở ứng dụng
Người đọc hoặc trình thu thập mở một URL ổn định và thấy đoạn trả lời khớp snapshot ứng dụng đang hiển thị. Có trang chính sách và kênh gỡ tin trong 48 giờ.
**FRs covered:** FR-47, FR-48

### Epic 6: Hoàn tất một phiên thử nghiệm mà không để lại danh tính
Người thử vào bằng link thử nghiệm, trả lời trước khi thấy số, dùng sản phẩm, rồi chấm so sánh mù. Nhóm xuất được một bảng theo mã phiên.
**FRs covered:** FR-41, FR-42, FR-43, FR-44, FR-45

Phụ thuộc: Epic 2, Epic 4 và Epic 5 đứng trên Epic 1. Epic 3 cần Epic 1 và Epic 2. Epic 6 cần Epic 1 và Epic 2. Epic 4 chạy được trước Epic 2; thứ tự trên đây đặt vòng học và soi tin trước năm loại thẻ.

## Mức ưu tiên và thứ tự thực hiện

Đáp ứng PRD §10 câu 7: mọi story đã gắn một mức. Mức ghi ngay dưới tiêu đề mỗi story, kèm sprint dự kiến.

- **P0** — bắt buộc cho review giữa kỳ 22–28/11 (cuối Sprint 3).
- **P1** — bắt buộc trước khi công khai.
- **P2** — làm nếu kịp. Không story nào của v1 ở mức này; phần "làm nếu kịp" là việc hạ tầng (bọc Dagster) chứ không phải FR. Khi trượt lịch thì cắt theo thứ tự ở `WORK-SPLIT.md` §5, không tự hạ mức một story.

**Số epic không phải thứ tự làm.** Thứ tự làm là `WORK-SPLIT.md` §3, và nó cắt ngang các epic. Hai chỗ dễ đi sai nếu chỉ đọc số epic:

- **Story 1.15 (bảng và 2D) ở Sprint 1, là lát cắt chạy thật đầu tiên. Story 1.16 và 1.17 vẫn ở Sprint 5**, vì 1.16 cần tỷ lệ kỹ năng. Review giữa kỳ vẫn cần luồng CV → lộ trình có thứ tự cho Backend (nhánh Java Backend) và Data Engineer — tức Epic 2 — chứ không cần bản đồ 3D. Xem `sprint-change-proposal-2026-11-05.md`.
- **Epic 3, 4, 5, 6 đều là P1**, nằm sau mốc 22–28/11. Phần P0 của Epic 1 dừng ở Story 1.13 (API đọc số kèm cỡ mẫu) và Story 1.14 (dữ liệu nền).

Thứ tự P0 theo sprint, để dev đi tuần tự:

| Sprint | Story P0 |
|---|---|
| 1 (2–8/11) | 1.1, 1.4, 1.20, 1.21, 1.15 |
| 2 (9–15/11) | 1.2, 1.3, 1.5, 1.6, 1.7, 1.9, 1.11, 1.14, 2.1, 2.2, 2.6, 2.9, 2.10, 2.11 |
| 3 (16–22/11) | 1.8, 1.13, 2.3, 2.7, 2.8, 2.12 |

Mốc 20/11: chạy tay toàn chuỗi nhịp hai cho hai vai trò trên, đóng băng snapshot dùng cho review. Sau 21/11 không đụng code tới hết buổi review.

Story P1 theo sprint: Sprint 1 — 5.1. Sprint 2 — 1.19. Sprint 3 — 2.4, 2.5, 2.13. Sprint 4 — 1.10, 1.12, 1.18, 3.1–3.7. Sprint 5 — 1.16, 1.17, 5.2–5.5. Sprint 6 — 4.1–4.6, 6.1–6.6.

Trong Sprint 1, nhịp một chạy qua cầu nối tạm C-11 (chore trên GitHub, không có story ở đây): crawler cũ ghi JSONL theo ngày, rồi bước `ingest` xóa liên hệ người đăng và nạp vào kho. Cầu nối bị gỡ khi Story 1.3 xong.

Không được cắt dù trượt, theo `WORK-SPLIT.md` §5: nhịp một hằng ngày (C-11 ở Sprint 1, rồi 1.2–1.4), sao lưu (1.19), bộ chuẩn 200 JD (1.7, 1.9), chế độ thử nghiệm (Epic 6).

## Epic 1: Thấy nhu cầu thị trường trên bản đồ

Sinh viên mở ứng dụng và thấy Hà Nội, TP.HCM, Đà Nẵng chiếm bao nhiêu phần tin của vai trò đang chọn. Mỗi số có cỡ mẫu, nguồn và ngày snapshot. Đêm pipeline lỗi thì bản đồ vẫn mở trên snapshot gần nhất.

### Story 1.1: Mở khung Hải Đồ IT trên máy dev

**Mức ưu tiên:** P0 — Sprint 1

As a thành viên nhóm,
I want chạy Hải Đồ IT trên máy dev và thấy đúng khung bảng điều khiển tối,
So that mọi màn sau có một chỗ để hiện số, và một import đi ngược chiều bị chặn trước khi merge.

**Acceptance Criteria:**

**Given** repo theo cây `haido_core`, `haido_pipeline`, `haido_api`, `web`, `deploy`
**When** chạy Compose local
**Then** Postgres, API và web cùng lên. Web mở nền `#070B10`, wordmark "HẢI ĐỒ IT", chữ Be Vietnam Pro
**And** chưa có bảng tin, snapshot hay thống kê. Alembic có đúng một head
**And** thanh đầu có bốn mục. Mục Bản đồ là trang hiện tại, `aria-current="page"`
**And** CI thất bại nếu `web` có chuỗi kết nối Postgres, hoặc phụ thuộc đi ngược chiều spine
**And** `compose.prod` không chạy `next build` trên máy chủ

### Story 1.2: Chạy một lượt thu thập lịch sự

**Mức ưu tiên:** P0 — Sprint 2. Trong Sprint 1, nhịp một chạy qua cầu nối C-11

As a nhóm vận hành,
I want bật hoặc tắt từng nguồn và thấy nhật ký của một lượt chạy,
So that nguồn tắt không bị gọi, và một nguồn bị chặn thì dừng có lý do.

**Acceptance Criteria:**

**Given** một nguồn giả lập và công tắc bật/tắt
**When** lượt chạy bắt đầu
**Then** ghi thời điểm bắt đầu, kết thúc, trạng thái và số tin của nguồn đó
**And** nguồn tắt không nhận request nào
**And** URL bị `robots.txt` cấm không bị request
**And** User-Agent trung thực, có địa chỉ liên hệ. Các request tới cùng nguồn giãn cách cố định. Không đăng nhập
**And** HTTP 403, 429 hoặc captcha làm dừng nguồn đó, nhật ký ghi lý do, và nguồn không được thử lại cho tới lượt sau
**And** mọi request đi qua một cổng duy nhất. Ngoại lệ R1–R4 là hàng có tên, có công tắc theo nguồn và theo bước
**And** crawler dùng trình duyệt cũng hỏi cổng trước mỗi lần mở trang, nên URL bị `robots.txt` cấm không bị mở

### Story 1.3: Lưu tin đã xóa liên hệ người đăng

**Mức ưu tiên:** P0 — Sprint 2. Trong Sprint 1, nhịp một chạy qua cầu nối C-11; bước `redact` làm trong C-11 rồi story này dùng lại

As a nhóm vận hành,
I want các nguồn tự động đang bật đổ tin vào kho sau khi xóa liên hệ người tuyển dụng,
So that mỗi ngày có quan sát mới mà kho không chứa email hay số điện thoại.

**Acceptance Criteria:**

**Given** các crawler kế thừa
**When** lượt đêm chạy
**Then** mỗi nguồn tự động có `crawl(cfg) -> Iterator[RawJob]`, không tự ghi file. Các hàm `parse_*` được giữ
**And** trạng thái thu thập nằm trong bảng, không nằm trong file
**And** LinkedIn không bị gọi. TopCV không phải asset của lượt đêm. Snapshot vẫn công bố được khi TopCV không chạy
**And** tên, email, số điện thoại và Zalo của người đăng tin bị xóa trước khi ghi
**And** không bản ghi nào khớp mẫu email hoặc số điện thoại Việt Nam. Nhật ký chỉ ghi loại thông tin đã xóa
**And** một nguồn lỗi không dừng các nguồn khác
**And** quan sát chỉ được thêm, không sửa vòng đời tại chỗ

### Story 1.4: Chốt snapshot và vòng đời tin

**Mức ưu tiên:** P0 — Sprint 1

As a sinh viên,
I want mỗi lượt thu thành công tạo một snapshot có ngày,
So that số sau này truy được về đúng ngày, và một đêm lỗi không làm tin trông như bị đăng lại.

**Acceptance Criteria:**

**Given** một tin xuất hiện trong ba lượt thành công liên tiếp của nguồn đó
**When** vòng đời được tính
**Then** số lần thấy bằng 3. `snapshot_id` là `YYYY-MM-DD` theo `Asia/Ho_Chi_Minh`
**And** tin chỉ bị coi là biến mất khi vắng mặt ở ít nhất ba lượt thành công liên tiếp của chính nguồn đó. Xuất hiện lại thì số lần đăng lại tăng một
**And** một đêm nguồn lỗi hoặc bị dừng không làm tăng số lần đăng lại
**And** cửa sổ 60 ngày xét trên vòng đời của snapshot đang dùng
**And** hàng đã ghi cho snapshot đó không bị sửa và không bị xóa

### Story 1.5: Bỏ bản sao trong cùng nguồn trước khi gọi mô hình

**Mức ưu tiên:** P0 — Sprint 2

As a nhóm vận hành,
I want các tin trùng trong cùng một nguồn được gom trước bước trích xuất,
So that mô hình không chạy trên các bản sao.

**Acceptance Criteria:**

**Given** hai tin cùng nguồn, trùng mã tin, URL hoặc nội dung
**When** bước loại trùng trong nguồn chạy
**Then** chúng thuộc một cụm, và bước trích xuất sau đó chỉ nhận đại diện
**And** bước này đứng trước mọi lệnh gọi mô hình trong thứ tự một đêm
**And** tin không bị xóa. Cụm còn giữ các bản ghi thành viên

### Story 1.6: Trích dữ kiện JD theo lô

**Mức ưu tiên:** P0 — Sprint 2

As a nhóm vận hành,
I want mỗi JD trả về lượt nhắc nguyên văn và các trường có kiểu,
So that đổi bộ từ vựng sau này không phải gọi lại mô hình cho toàn bộ tin cũ.

**Acceptance Criteria:**

**Given** một JD trong lô đêm
**When** cổng trích xuất chạy
**Then** kết quả gồm lượt nhắc kỹ năng nguyên văn kèm vị trí, và các trường đóng: khoảng số năm, khoảng lương kèm đơn vị nguyên văn, kênh liên hệ, dấu hiệu thu phí, tên công ty, các mục chất lượng JD. Mỗi trường kèm đoạn văn bản nguồn
**And** kết quả không chứa mã kỹ năng, nhãn vai trò hay con số tự tính
**And** bản ghi lưu `model_id`, `prompt_version`, `vocab_version`. Lô đêm dùng `claude-haiku-5-5` qua Batch API
**And** đầu ra khai bằng `output_config.format`
**And** lô chưa xong sau 24 giờ thì lượt chạy kết thúc `partial`
**And** tin ghi "2–3 năm" lưu tối thiểu 2, tối đa 3. Tin không nêu số năm thì để trống

### Story 1.7: Quy lượt nhắc về mã kỹ năng

**Mức ưu tiên:** P0 — Sprint 2

As a sinh viên,
I want "SpringBoot", "Spring Boot" và "học máy" được tính là cùng các kỹ năng chuẩn,
So that tỷ lệ trên bản đồ không vỡ vì cách viết.

**Acceptance Criteria:**

**Given** lượt nhắc đã trích và bộ từ vựng song ngữ
**When** phép mapping chạy
**Then** "SpringBoot", "Spring Boot" và "Java Spring Boot" về `spring-boot`. "học máy" về `machine-learning`. "kiểm thử tự động" về `test-automation`. "cơ sở dữ liệu" về `sql`
**And** từ không khớp vào danh sách chờ, kèm tần suất và lần thấy gần nhất
**And** thêm một bí danh rồi chạy lại mapping, không gọi lại mô hình
**And** một bộ fixture đã gán nhãn cho ra precision và recall, tách riêng kỹ năng viết bằng tiếng Việt trên tin `raw`
**And** bộ chuẩn 200 JD do hai người gán, trong đó 50 JD cả hai cùng gán; báo cáo có Cohen's kappa của hai người trên 50 JD chung đó, tính lại được bằng một lệnh trên nhãn đã lưu
**And** phép này có một chữ ký trong registry, dùng được cho một tin và cho một lô

### Story 1.8: Gom tin trùng giữa các nguồn

**Mức ưu tiên:** P0 — Sprint 3

As a sinh viên,
I want một tin đăng trên hai sàn chỉ được tính một lần,
So that tỷ trọng thành phố không phình vì tin đăng lại chéo nguồn.

**Acceptance Criteria:**

**Given** hai tin khác nguồn, cùng tên công ty đã chuẩn hóa và tập kỹ năng gần nhau
**When** bước gom cụm chạy
**Then** chúng thuộc một cụm. Mọi số thống kê sau này đếm cụm, không đếm bản ghi thô
**And** đại diện của cụm chọn theo thứ hạng nguồn trong cấu hình, rồi bản ghi có nhiều trường thống kê hơn, rồi `job_url` A–Z
**And** có báo cáo precision/recall trên một fixture khoảng 100 cặp đã gán nhãn, và cách đo tỷ lệ trùng còn sót trên 100 tin
**And** phép so khớp nằm trong registry, cùng phép sẽ dùng cho tin người dùng dán

### Story 1.9: Gán vai trò, nhánh, cấp bậc và thành phố

**Mức ưu tiên:** P0 — Sprint 2

As a sinh viên,
I want mỗi tin thuộc một vai trò, một cấp bậc và một thành phố,
So that bản đồ lọc được theo vai trò và không tính tin ngoài ngành IT.

**Acceptance Criteria:**

**Given** một tin đã có cụm, và đã có vai trò, cấp bậc, thành phố từ Story 1.20
**When** phép phân loại chạy
**Then** tin có thêm một nhánh nếu đủ điều kiện
**And** nhánh chỉ xuất hiện khi có từ 30 tin. Ngưỡng này đọc từ cấu hình
**And** có cách chấm độ chính xác vai trò, cấp bậc và nhánh trên bộ fixture 200 JD

### Story 1.10: Quy lương về VND của snapshot

**Mức ưu tiên:** P1 — Sprint 4

As a sinh viên,
I want lương USD và lương "thỏa thuận" được xử lý cùng một cách trên mọi tin của một snapshot,
So that phân vị lương sau này không trộn đơn vị.

**Acceptance Criteria:**

**Given** tin ghi "1.000–1.500 USD" và tin ghi "thỏa thuận"
**When** bước chuẩn hóa lương chạy
**Then** khoảng USD thành VND/tháng gross theo tỷ giá của chính snapshot đó
**And** "thỏa thuận" hoặc tin không ghi lương được đánh dấu không có lương dạng số
**And** tỷ lệ tin có lương dạng số báo cáo được theo nguồn
**And** tỷ giá nằm trong cấu hình có phiên bản, không viết cứng trong code

### Story 1.11: Tính tỷ lệ và nhóm kỹ năng cho từng ô

**Mức ưu tiên:** P0 — Sprint 2

As a sinh viên,
I want mỗi kỹ năng trong một ô có tỷ lệ xuất hiện và nhóm cốt lõi, thường gặp hoặc riêng của công ty,
So that bản đồ và các màn sau dùng cùng một bộ số.

**Acceptance Criteria:**

**Given** một snapshot đã phân loại
**When** bước tổng hợp chạy bằng CLI
**Then** mỗi ô thống kê lưu `n` và cơ cấu cấp bậc. Khóa ô gồm snapshot, vai trò, nhánh, cấp bậc và phạm vi
**And** bảng tỷ lệ có một hàng cho mọi kỹ năng của ô, kể cả tỷ lệ 0
**And** θ_core khởi tạo 30%, θ_common khởi tạo 10%. Đổi θ thì nhóm đổi ở lần tính kế tiếp, không cần triển khai lại
**And** ngưỡng mẫu 30, cửa sổ 60 ngày và θ nằm trong cấu hình có phiên bản. Snapshot lưu `config_version`
**And** tin không thuộc IT không vào các bảng này
**And** `haido_api` không có `GROUP BY`, phân vị, `AVG` hay `COUNT` trên bảng `job_*`

### Story 1.12: Tính phân vị có khoảng tin cậy tất định

**Mức ưu tiên:** P1 — Sprint 4

As a sinh viên,
I want phân vị lương và phân vị số kỹ năng chạy lại ra đúng số cũ,
So that cùng một snapshot không đổi số giữa hai lần tính.

**Acceptance Criteria:**

**Given** một ô có 30 ≤ n < 100
**When** phân vị được tính
**Then** lưu giá trị phân vị và khoảng tin cậy 95% từ bootstrap không tham số, B = 1.000
**And** seed dẫn xuất từ snapshot, ô, thước đo và mức phân vị. Chạy lại cho cùng kết quả
**And** mỗi hàng lưu seed, B, method và estimator
**And** luật khi P75 bằng P90 được kiểm thử ở biên n = 30
**And** B và estimator đọc từ cấu hình

### Story 1.13: Đọc số qua API kèm cỡ mẫu

**Mức ưu tiên:** P0 — Sprint 3

As a sinh viên,
I want mọi số bản đồ đi kèm ngày snapshot, nguồn và cỡ mẫu,
So that màn hình không phải tự tính, và mẫu nhỏ không bị bịa thành một tỷ lệ kỹ năng.

**Acceptance Criteria:**

**Given** một snapshot đã tổng hợp
**When** client gọi API tỷ lệ kỹ năng
**Then** thân phản hồi là `data` và `meta`. `meta` có ngày snapshot, trạng thái, nguồn đang bật, nguồn lỗi, ngưỡng, hai ý độ phủ, và một mục cho mỗi ô
**And** mỗi mục ô có `n`, nhãn quay về, cơ cấu cấp bậc, và `n` riêng cho số kỹ năng, số năm, lương
**And** tỷ lệ kỹ năng và phân vị dưới ngưỡng trả về trạng thái chưa đủ dữ liệu
**And** chỉ tỷ trọng cấu phần của bản đồ được phép hiện khi n < 30, kèm cờ mẫu nhỏ
**And** thiếu `meta` thì kiểm thử schema thất bại
**And** endpoint tỷ trọng thành phố của Story 1.21 qua cùng kiểm thử schema
**And** hình lỗi là `error.code`, `error.message` tiếng Việt, và `snapshot_date`

### Story 1.14: Nhập bộ dữ liệu nền một lần

**Mức ưu tiên:** P0 — Sprint 2

As a sinh viên,
I want bản đồ có số từ bộ 3.469 tin nền,
So that review giữa kỳ có mặt bằng Backend và Data/AI trước khi nhóm tự thu đủ nhiều ngày.

**Acceptance Criteria:**

**Given** bộ dữ liệu nền
**When** lệnh nhập một lần chạy
**Then** tạo một snapshot gốc với `is_backfill = true` và `times_seen = 1`
**And** mỗi tin có `text_provenance` là `raw` hoặc `rewritten_en`
**And** văn bản gốc không bị ghi đè. Bản làm sạch là trường mới
**And** tin nền đi qua đúng một lượt trích xuất của bộ máy mới, rồi qua cùng các bước gom cụm, phân loại và tổng hợp
**And** dấu hiệu đăng lại nhiều lần với tin nền là "không đánh giá được"
**And** chỉ số kỹ năng truy vấn được tách theo `text_provenance`
**And** bộ chấm tiếng Việt không lấy tin `rewritten_en`

### Story 1.15: Xem tỷ trọng ba thành phố

**Mức ưu tiên:** P0 — Sprint 1

As a sinh viên,
I want mở ứng dụng và thấy Hà Nội, TP.HCM, Đà Nẵng chiếm bao nhiêu phần tin,
So that tôi biết vai trò mình chọn đang tập trung ở đâu, kể cả khi mẫu một thành phố còn nhỏ.

**Acceptance Criteria:**

**Given** snapshot đã công bố hoặc snapshot gần nhất còn đọc được
**When** sinh viên mở ứng dụng
**Then** vào Bản đồ, vai trò mặc định "Tất cả", và thấy bảng cùng biểu đồ 2D trên cùng số liệu
**And** chiều cao là tỷ trọng của thành phố trong tổng tin toàn quốc của vai trò đang chọn
**And** cột cộng phần "Khác" cộng phần không xác định thành phố bằng 100%. "Khác" nằm ở chú thích, không phải một cột
**And** Đà Nẵng luôn có mặt. Cột n < 30 vẫn vẽ, mờ, nhãn "Cỡ mẫu nhỏ (n = X < 30): số liệu chỉ để tham khảo". Phần trăm của cột đó chỉ hiện khi trỏ, chạm hoặc focus
**And** ba lưu ý của FR-36, danh sách nguồn đang bật và ngày snapshot luôn nhìn thấy
**And** mọi số có cỡ mẫu. Ô dưới 30 trên bảng không hiện tỷ lệ, chỉ "chưa đủ dữ liệu"
**And** trên điện thoại, bản đồ là danh sách thành phố và thanh tỷ trọng, kèm gợi ý mở trên máy tính
**And** cụm 3D / 2D / bảng cao tối thiểu 44px. Vòng focus dày 2px, màu `#C5F36A`, lệch 2px
**And** khi Story 1.17 chưa xong, Bản đồ mở ở lối 2D. Nút 3D có mặt ở trạng thái tắt, có `aria-disabled` và chú thích "Bản đồ 3D sắp có"
**And** đêm pipeline lỗi thì trang vẫn mở và ghi ngày của snapshot đang hiển thị
**And** ngưỡng nhóm trên giao diện là 30% và 10%

### Story 1.16: Mở bảng chi tiết một thành phố

**Mức ưu tiên:** P1 — Sprint 5

As a sinh viên,
I want bấm một thành phố và thấy cơ cấu vai trò cùng các kỹ năng hàng đầu,
So that tôi biết trong thành phố đó vai trò nào đang chiếm bao nhiêu phần.

**Acceptance Criteria:**

**Given** bản đồ đang hiện một snapshot
**When** sinh viên bấm Hà Nội, TP.HCM hoặc Đà Nẵng, kể cả cột mẫu nhỏ
**Then** bảng hiện cơ cấu vai trò với tỷ trọng và cỡ mẫu, các kỹ năng có tỷ lệ cao nhất, và ngày snapshot
**And** mọi số có cỡ mẫu. Ô n < 30 chỉ ghi "chưa đủ dữ liệu", không vẽ tỷ lệ
**And** cột số canh phải bằng JetBrains Mono

### Story 1.17: Xoay bản đồ 3D

**Mức ưu tiên:** P1 — Sprint 5

As a sinh viên,
I want xoay và nghiêng bản đồ 3D của ba thành phố,
So that tôi nhìn được cùng bộ số theo chiều cao cột, và máy không chạy WebGL vẫn xem được.

**Acceptance Criteria:**

**Given** cùng số liệu với bảng và biểu đồ 2D
**When** sinh viên kéo hoặc bấm nút xoay
**Then** bản đồ xoay, nghiêng được, và đặt lại được góc nhìn. Nút xoay có `aria-label`. Ngưỡng kéo là 6px
**And** cột n < 30 opacity 0,4. Cột đang chọn đổi mặt trên thành màu chữ chính
**And** trình duyệt không chạy WebGL thì tự chuyển sang biểu đồ 2D hoặc bảng, không hiện màn hình lỗi
**And** `prefers-reduced-motion: reduce` tắt animation
**And** bấm cột 3D mở bảng chi tiết thành phố của Story 1.16

### Story 1.18: Báo khi một nguồn gãy hoặc sụt tin

**Mức ưu tiên:** P1 — Sprint 4

As a nhóm vận hành,
I want nhận email khi lượt chạy lỗi hoặc một nguồn mất quá nửa lượng tin,
So that một nguồn chết không trôi qua im lặng.

**Acceptance Criteria:**

**Given** lịch sử `pipeline_run` của một nguồn
**When** lượt chạy lỗi, hoặc số tin của nguồn giảm quá 50% so với trung bình 7 ngày
**Then** nhóm vận hành nhận email
**And** ngưỡng 50% nằm trong cấu hình và được đánh dấu là giả định
**And** không cần Telegram hay Slack

### Story 1.19: Sao lưu snapshot ra ngoài VPS

**Mức ưu tiên:** P1 — Sprint 2. Sprint 1 vẫn chạy `pg_dump` một lần theo cổng ra sprint

As a nhóm vận hành,
I want mỗi ngày có một bản sao cơ sở dữ liệu ở ngoài máy chủ,
So that một snapshot đã qua không mất theo ổ đĩa.

**Acceptance Criteria:**

**Given** Postgres đang chứa snapshot
**When** lịch sao lưu chạy
**Then** `pg_dump` ghi ra ngoài VPS và giữ 14 bản
**And** một lần phục hồi từ bản dump đã chạy thành công và có biên bản
**And** migration không `DROP COLUMN` trên bảng đang mang snapshot lịch sử

### Story 1.20: Gán vai trò, cấp bậc và thành phố bằng luật tất định

**Mức ưu tiên:** P0 — Sprint 1

As a sinh viên,
I want mỗi tin có một vai trò, một cấp bậc và một thành phố ngay từ tuần đầu,
So that bản đồ lọc được theo vai trò và không tính tin ngoài ngành IT.

**Acceptance Criteria:**

**Given** một tin đã nạp vào kho
**When** phép phân loại chạy
**Then** tin có đúng một vai trò trong danh sách của cấu hình hoặc nhãn "không thuộc IT", đúng một cấp bậc, và đúng một thành phố: Hà Nội, TP.HCM, Đà Nẵng, Khác, hoặc không xác định
**And** phép là hàm thuần trong `domain`, là phép 6 của registry, gọi được cho một tin và cho một lô. Cùng đầu vào luôn cho cùng nhãn
**And** luật chỉ đọc chức danh, nguồn, danh mục của nguồn, cấp bậc và địa điểm nguồn ghi. Không gọi mô hình
**And** Data/AI tách thành Data Analyst/BI, Data Engineer và AI/ML Engineer. Embedded không nằm trong Other
**And** tin ghi nhiều thành phố được gán theo một quy tắc viết rõ trong cấu hình, có kiểm thử
**And** tin không thuộc IT được gắn nhãn và bị loại khỏi mọi bảng tổng hợp. Tỷ lệ loại báo cáo được theo nguồn

### Story 1.21: Tính và đọc tỷ trọng thành phố kèm cỡ mẫu

**Mức ưu tiên:** P0 — Sprint 1

As a sinh viên,
I want số tỷ trọng thành phố đến từ snapshot thật, kèm cỡ mẫu, nguồn và ngày,
So that màn Bản đồ không phải tự tính, và mẫu nhỏ được đánh dấu đúng.

**Acceptance Criteria:**

**Given** một snapshot đã nạp và đã phân loại
**When** bước tổng hợp chạy
**Then** có một ô thống kê cho mỗi thành phố × vai trò và một ô toàn quốc cho mỗi vai trò, kể cả "Tất cả". Mỗi ô có n và cơ cấu cấp bậc
**And** bước tổng hợp đếm cụm, không đếm bản ghi thô. Cho tới khi có Story 1.5 và 1.8, mỗi tin là một cụm của riêng nó
**And** với mỗi vai trò, tỷ trọng ba thành phố cộng phần Khác và phần không xác định bằng 100%
**When** client gọi `GET /api/v1/city-shares?role=`
**Then** thân phản hồi theo envelope của AD-17, đọc snapshot mới nhất còn đọc được, và route cùng schema giữ nguyên như bản dữ liệu giả của C-1
**And** `haido_api` không chạy `GROUP BY`, `COUNT` hay `AVG` trên bảng `job_*`

## Epic 2: Biết mình thiếu gì và học gì trước

Sinh viên tải CV hoặc tự chọn kỹ năng, xác nhận khoảng trống, nhận lộ trình có thứ tự, lưu hồ sơ trong trình duyệt, tải tóm tắt và copy link. Từ bảng thành phố bấm sang Cố vấn với vai trò đã chọn.

### Story 2.1: Xem lộ trình chung của vai trò đang chọn

**Mức ưu tiên:** P0 — Sprint 2

As a sinh viên,
I want chọn vai trò và cấp bậc rồi thấy kỹ năng cốt lõi và thường gặp của ô thống kê,
So that tôi biết thị trường đang yêu cầu gì trước khi có hồ sơ.

**Acceptance Criteria:**

**Given** snapshot đã có bảng tỷ lệ
**When** sinh viên mở Cố vấn
**Then** cấp bậc mặc định là Intern/Fresher/Junior. Mỗi kỹ năng hiện tỷ lệ, nhóm, cỡ mẫu, nguồn và ngày snapshot
**And** kỹ năng riêng của công ty không có trong danh sách
**And** nhóm thường gặp được nói là "nên học sau khi đã nắm các kỹ năng cốt lõi"
**And** đổi vai trò hoặc cấp bậc thì danh sách tính lại, không tải lại trang, trong vòng 1 giây
**Given** ô Java Backend × Intern/Fresher/Junior có 26 tin
**When** sinh viên chọn ô đó
**Then** màn giữ cấp bậc và ghi dùng Backend × Intern/Fresher/Junior, n = 52, cơ cấu 13 Intern, 7 Fresher, 32 Junior. Khung này có `role="status"`
**And** người chọn Intern/Fresher/Junior không nhận một tập mà Mid trở lên chiếm đa số, trừ bước cuối của thứ tự quay về. Khi đó nhãn ghi rõ tỷ lệ tin Mid trở lên
**Given** vai trò chưa có đồ thị học trước đã được duyệt
**When** sinh viên mở vai trò đó, hoặc bấm từ bảng thành phố
**Then** không vẽ đồ thị. Hiện danh sách theo nhóm, kèm câu "Lộ trình học có thứ tự cho vai trò này đang được biên soạn"
**And** bấm từ bảng Hà Nội với vai trò Backend thì Cố vấn mở sẵn Backend
**And** trên điện thoại, danh sách này là các thẻ

### Story 2.2: Tự chọn kỹ năng và giữ hồ sơ trong trình duyệt

**Mức ưu tiên:** P0 — Sprint 2

As a sinh viên,
I want bấm để đánh dấu kỹ năng đã có, rồi thấy chúng còn sau khi tải lại trang,
So that tôi đối chiếu được với thị trường khi chưa có CV.

**Acceptance Criteria:**

**Given** danh sách kỹ năng của vai trò đang chọn
**When** sinh viên bấm một kỹ năng, hoặc tìm và chọn từ danh sách
**Then** kỹ năng vào hồ sơ, được tô, và không còn trong phần còn phải học. Bấm lần nữa thì bỏ ra
**And** API nhận hồ sơ qua `have` là các mã kỹ năng. `web` không tự đếm, không tự giao tập hợp
**And** lộ trình tính lại trong vòng 1 giây
**And** chip hồ sơ chuyển sang trạng thái đã có kỹ năng
**Given** hồ sơ đang nằm trong trình duyệt
**When** sinh viên tải lại trang hoặc đóng rồi mở lại trình duyệt
**Then** hồ sơ và vai trò mục tiêu vẫn còn
**And** mọi khóa có tiền tố `haido:` và được khai trong một module. Không chỗ nào gọi `localStorage` trực tiếp
**When** sinh viên bấm "Xoá hồ sơ khỏi trình duyệt"
**Then** mọi khóa tiền tố `haido:` biến mất, và một toast báo hồ sơ đã xóa

### Story 2.3: Thấy kỹ năng trùng khi đổi vai trò

**Mức ưu tiên:** P0 — Sprint 3

As a sinh viên,
I want đổi từ Backend sang Data Engineer và thấy kỹ năng nào của mình nằm trong lộ trình mới,
So that tôi biết phần nào học một lần dùng được cho cả hai hướng.

**Acceptance Criteria:**

**Given** hồ sơ {Java, SQL, Git}
**When** sinh viên đổi sang Data Engineer
**Then** các kỹ năng thuộc cả hồ sơ lẫn lộ trình Data Engineer được tô
**And** có dòng "Có N kỹ năng trong lộ trình này trùng với hồ sơ của bạn." N là số API trả về
**And** câu chữ dùng "vai trò có kỹ năng gần", không dùng "lộ trình chuyển việc"
**And** kết quả hiện trong vòng 1 giây

### Story 2.4: Copy link lộ trình

**Mức ưu tiên:** P1 — Sprint 3

As a sinh viên,
I want copy một link của vai trò và các kỹ năng đang có,
So that tôi mở lại đúng lộ trình trên máy khác mà không gửi nội dung CV.

**Acceptance Criteria:**

**Given** một hồ sơ và một vai trò mục tiêu
**When** sinh viên copy link
**Then** URL có dạng `role`, `level` và `have` là các mã kỹ năng, trần 200 mã
**And** URL không chứa tên, email hay nội dung CV
**When** link được mở trên máy khác, cùng snapshot
**Then** lộ trình hiện giống máy gốc
**When** link được mở vào một ngày có snapshot mới
**Then** lộ trình tính lại trên snapshot đó, và màn hình ghi ngày snapshot mới

### Story 2.5: Ghi thao tác bằng mã phiên ẩn danh

**Mức ưu tiên:** P1 — Sprint 3

As a nhóm nghiên cứu,
I want mỗi thao tác chọn kỹ năng gắn với một mã phiên trong trình duyệt,
So that thống kê không chứa nội dung CV hay tên người dùng.

**Acceptance Criteria:**

**Given** trình duyệt chưa có mã phiên
**When** sinh viên thao tác trên Cố vấn
**Then** một mã phiên ngẫu nhiên nằm trong danh sách khóa `haido:`
**And** bảng sự kiện chỉ có mã phiên, loại thao tác, mã kỹ năng và vai trò mục tiêu
**And** `skill_code` là khóa ngoại tới mã kỹ năng. Một chuỗi tự do bị từ chối
**And** bộ mã thao tác là enum đóng, dùng chung `web` và API, có đủ ba lựa chọn xác nhận khoảng trống, tải CV thành công, tải CV thất bại, soi tin, và lưu kết quả
**And** sự kiện không có cột cho nội dung CV hay JD
**When** sinh viên xóa hồ sơ
**Then** mã phiên cũng biến khỏi trình duyệt

### Story 2.6: Dựng thứ tự học từ đồ thị đã kiểm

**Mức ưu tiên:** P0 — Sprint 2

As a sinh viên,
I want các kỹ năng còn thiếu xếp theo chặng học trước – học sau,
So that cùng hồ sơ và cùng snapshot luôn cho cùng một thứ tự.

**Acceptance Criteria:**

**Given** một đồ thị fixture các cạnh học trước, mỗi cạnh có nguồn tài liệu
**When** API dựng lộ trình
**Then** thứ tự là sắp xếp topo Kahn, khóa (chặng, nhóm, tỷ lệ xuất hiện giảm dần, mã kỹ năng A–Z)
**And** kỹ năng tổ tiên còn thiếu được kéo vào với nhãn "Kỹ năng nền tảng (cần cho X)"
**And** kỹ năng riêng của công ty không vào lộ trình, trừ kỹ năng nền tảng
**And** không kỹ năng nào đứng trước tổ tiên của nó. Chạy lặp lại trên cùng đầu vào cho cùng kết quả
**And** vai trò có kỹ năng cốt lõi hoặc thường gặp chưa có nút trên đồ thị thì không được bật lộ trình có thứ tự
**And** vai trò chưa có biên bản rà soát vẫn hiện danh sách nhóm của Story 2.1
**And** `web` không có sắp xếp topo và không có θ. Bấm nút trên đồ thị thêm hoặc bỏ kỹ năng trong hồ sơ của Story 2.2
**And** cạnh đồng xuất hiện không được dùng làm cạnh học trước

### Story 2.7: Bật lộ trình có thứ tự cho Backend

**Mức ưu tiên:** P0 — Sprint 3

As a sinh viên,
I want vai trò Backend, gồm nhánh Java Backend, có lộ trình đã xếp thứ tự,
So that review giữa kỳ chạy được hành trình đối chiếu CV cho hướng Java.

**Acceptance Criteria:**

**Given** các cạnh Backend và Java Backend, mỗi cạnh có nguồn tài liệu
**When** biên bản rà soát ghi người rà, ngày và số cạnh
**Then** Cố vấn vẽ đồ thị có thứ tự cho vai trò đó
**And** câu "đang được biên soạn" không còn trên vai trò đã có biên bản

### Story 2.8: Bật lộ trình có thứ tự cho Data Engineer

**Mức ưu tiên:** P0 — Sprint 3

As a sinh viên,
I want nhánh Data Engineer có lộ trình đã xếp thứ tự,
So that review giữa kỳ so được Backend với Data trên cùng một cách dựng lộ trình.

**Acceptance Criteria:**

**Given** các cạnh Data Engineer, mỗi cạnh có nguồn tài liệu
**When** biên bản rà soát ghi người rà, ngày và số cạnh
**Then** Cố vấn vẽ đồ thị có thứ tự cho Data Engineer
**And** đổi từ Backend sang Data Engineer vẫn tô kỹ năng trùng theo Story 2.3

### Story 2.9: Tải CV sau khi đồng ý

**Mức ưu tiên:** P0 — Sprint 2

As a sinh viên,
I want đọc điều kiện rồi tải CV, và được chặn ngay nếu file là ảnh scan,
So that văn bản CV chỉ rời máy tôi khi tôi đã đồng ý, và file không đọc được thì không bị gửi đi.

**Acceptance Criteria:**

**Given** ô thả còn trống
**When** sinh viên chưa tích đồng ý
**Then** nút "Đọc CV và đối chiếu" tắt, kèm câu "Đánh dấu ô đồng ý ở trên để tiếp tục."
**And** nhãn đồng ý ghi tên Claude, nêu văn bản CV được gửi tới nhà cung cấp đó, không lưu file gốc hay thông tin định danh, và có thống kê ẩn danh theo mã phiên
**Given** một PDF hoặc DOCX dưới 5 MB và ô đã được tích
**When** sinh viên thả file hoặc chọn file
**Then** nút chính bật
**And** file trên 5 MB bị chặn ở trình duyệt và ở reverse proxy trước khi đọc body. Một CV 5 MB không tạo file tạm
**Given** văn bản trích được dưới 30 ký tự có nghĩa
**When** file được tải lên
**Then** trong vòng 1 giây có báo lý do và ba lối: PDF xuất từ Word, Canva hoặc Overleaf; file DOCX; tự chọn kỹ năng
**And** không chạy OCR. Không có yêu cầu nào gửi văn bản ra ngoài

### Story 2.10: Đọc kỹ năng từ CV

**Mức ưu tiên:** P0 — Sprint 2-3

As a sinh viên,
I want thấy từng bước đang chạy rồi nhận hồ sơ kỹ năng từ CV,
So that tôi biết hệ thống đang làm gì, và cùng một CV luôn ra cùng các kỹ năng.

**Acceptance Criteria:**

**Given** một CV có lớp chữ và ô đồng ý đã được tích
**When** sinh viên bấm đọc CV
**Then** màn hiện lần lượt năm bước: đọc chữ trong file, gửi văn bản tới dịch vụ AI, chuẩn hóa tên kỹ năng, đối chiếu với ô thống kê, xếp khoảng trống. Câu ngưỡng dùng 30% và 10%
**And** từ lúc tải CV đến lúc lộ trình cá nhân hóa hiện là dưới 15 giây
**And** cùng một CV cho cùng một tập mã kỹ năng, theo bộ từ vựng của FR-6
**And** hồ sơ này được Cố vấn xử lý giống hồ sơ tự chọn
**And** sau khi xử lý, file CV và văn bản CV không còn trên server, và không nằm trong nhật ký
**And** sự kiện ghi thành công hoặc thất bại, không kèm nội dung CV
**And** đồng hồ đang đọc có `aria-live="off"`

### Story 2.11: Xác nhận từng khoảng trống

**Mức ưu tiên:** P0 — Sprint 2

As a sinh viên,
I want với mỗi kỹ năng còn thiếu được nói đã biết hay chưa biết,
So that lộ trình chỉ còn những gì tôi thực sự cần học, và CV được nhắc những gì tôi đã có.

**Acceptance Criteria:**

**Given** một khoảng trống trên lộ trình
**When** sinh viên chọn
**Then** có hai nút chính: "Tôi chưa biết" và "Tôi đã biết, chỉ là CV chưa ghi"
**And** "Tôi chưa biết" giữ kỹ năng trên lộ trình
**And** "Tôi đã biết, chỉ là CV chưa ghi" thêm kỹ năng vào hồ sơ và vào danh sách cần bổ sung CV
**Given** hồ sơ được tạo từ CV
**When** khoảng trống hiện ra
**Then** có thêm lựa chọn nhỏ hơn: "CV của tôi có ghi rồi (hệ thống đọc sót)". Kỹ năng vào hồ sơ và không vào danh sách cần bổ sung CV
**And** chọn lại được. Lựa chọn sau cùng có hiệu lực. Lộ trình tính lại trong vòng 1 giây
**And** mỗi lựa chọn ghi một sự kiện với mã riêng
**And** nút "Lưu hồ sơ và tải bản tóm tắt" tắt cho tới khi mọi khoảng trống đã có lựa chọn, kèm câu "Còn {số} khoảng trống chưa xác nhận."
**And** trên điện thoại, ba lựa chọn vẫn có mặt trên thẻ
**And** không câu nào khuyên bỏ qua một kỹ năng

### Story 2.12: Xem vì sao một kỹ năng có trên lộ trình

**Mức ưu tiên:** P0 — Sprint 3

As a sinh viên,
I want bấm một kỹ năng và đọc lời giải thích cùng tài liệu miễn phí,
So that tôi hiểu vì sao nên học nó mà không nhận một con số do mô hình bịa.

**Acceptance Criteria:**

**Given** một nút kỹ năng
**When** sinh viên bấm
**Then** mở đúng kỹ năng vừa bấm. Ô số hiện tỷ lệ, nhóm, cỡ mẫu, ngày và nguồn, tách khỏi lời dẫn
**And** lời dẫn lấy từ bản đã lưu. Bấm nút không gọi mô hình
**And** lời dẫn không chứa ký hiệu phần trăm hay số lượng tin. Số trong tên công nghệ như Java 17, S3, EC2, OAuth2, Web3, HTML5, Vue 3 vẫn được phép
**And** mọi link thuộc danh mục tài liệu đã kiểm duyệt
**And** phần "hay đi cùng" khi dưới 30 tin ghi "chưa đủ dữ liệu", không hiện tỷ lệ

### Story 2.13: Tải bản tóm tắt hai phần

**Mức ưu tiên:** P1 — Sprint 3

As a sinh viên,
I want tải một bản tóm tắt những gì cần ghi vào CV và thứ tự học,
So that tôi sửa CV và học theo chặng mà không cần mở lại ứng dụng.

**Acceptance Criteria:**

**Given** mọi khoảng trống đã có lựa chọn
**When** sinh viên bấm lưu và tải
**Then** file có hai phần: kỹ năng đã có nhưng cần ghi vào CV, và lộ trình theo chặng kèm link tài liệu
**And** file ghi vai trò mục tiêu, cỡ mẫu và ngày snapshot
**And** một toast báo đã tạo bản tóm tắt
**And** một sự kiện lưu kết quả được ghi, không kèm nội dung CV
**And** bản tóm tắt có hai ý độ phủ dữ liệu

## Epic 3: Soi một tin trước khi nộp

Sinh viên dán một JD và thấy mức khớp với hồ sơ, phân vị so với mặt bằng, bảy dấu hiệu cần tự kiểm tra, và từng mục chất lượng đạt hoặc không đạt.

### Story 3.1: Dán tin và thấy vai trò được nhận

**Mức ưu tiên:** P1 — Sprint 4

As a sinh viên,
I want dán một JD và thấy hệ thống gán vai trò cùng cấp bậc,
So that tôi biết mình đang được so với ô thống kê nào trước khi đọc mức khớp.

**Acceptance Criteria:**

**Given** ô dán trống
**When** sinh viên mở Soi tin
**Then** nút "Soi tin" tắt. Ô có đếm ký tự, cao tối thiểu 340px, và không có ô chat
**Given** văn bản ngắn hơn 200 ký tự hoặc dài hơn 20.000 ký tự
**When** sinh viên bấm Soi tin
**Then** có câu báo độ dài, và không tính mức khớp
**Given** một JD từ 200 đến 20.000 ký tự
**When** sinh viên bấm Soi tin
**Then** cổng trích xuất trả lượt nhắc nguyên văn và các trường có kiểu, rồi phép phân loại gán vai trò, nhánh nếu có, và cấp bậc
**And** đầu kết quả hiện ô chọn "Đang đối chiếu với: [vai trò] · [cấp]", kèm cỡ mẫu của ô đang dùng
**And** đổi vai trò hoặc cấp bậc thì ô được chọn lại, không phải dán lại tin
**And** khi n < 30, nhãn quay về theo thứ tự của FR-19 và ghi n cùng cơ cấu cấp bậc
**Given** tin không thuộc IT
**When** kết quả trả về
**Then** có câu "Tin này có vẻ không thuộc lĩnh vực IT" và không tính mức khớp
**And** sau khi xử lý, nội dung tin không còn trên server và không nằm trong nhật ký. Một sự kiện soi tin được ghi, không kèm nội dung tin
**And** endpoint có trần kích thước và trần tốc độ theo IP, đọc từ cấu hình
**And** ô dán và nút dùng được trên điện thoại

### Story 3.2: Thấy mức khớp và nhóm kỹ năng của tin

**Mức ưu tiên:** P1 — Sprint 4

As a sinh viên,
I want thấy mình khớp bao nhiêu phần với tin vừa dán, theo trọng số thị trường,
So that một kỹ năng hiếm không kéo điểm của người đã đủ khung cốt lõi xuống mức không còn ý nghĩa.

**Acceptance Criteria:**

**Given** hồ sơ có dữ liệu và tin có 4 kỹ năng cốt lõi, 2 thường gặp, 2 riêng của công ty, người dùng thiếu đúng 2 kỹ năng riêng
**When** kết quả hiện
**Then** mức khớp là 89%, tức 16/18. Dòng phụ là "Bạn đáp ứng 6/8 kỹ năng trong tin này: 4/4 cốt lõi, 2/2 thường gặp, 0/2 riêng của công ty."
**And** vòng mức khớp ghi thêm trọng số: cốt lõi 3, thường gặp 2, riêng của công ty 1
**And** kỹ năng chưa nhận diện hiện ở dòng riêng, ghi "không tính vào mức khớp", và không đổi tử số hay mẫu số
**And** mỗi kỹ năng thiếu thuộc nhóm riêng của công ty có ghi chú "chỉ cần nếu bạn nhắm đúng công ty này"
**And** từ khóa chưa nhận diện vào bảng chỉ có từ khóa, tần suất và ngày thấy. Bảng không có mã phiên
**Given** hồ sơ trống
**When** sinh viên soi tin
**Then** màn mời tải CV hoặc tự chọn kỹ năng
**And** đổi ô đối chiếu thì mức khớp tính lại mà không dán lại tin, trong vòng 1 giây
**And** số do API trả. `web` không cộng trọng số

### Story 3.3: Thấy tin đứng ở đâu so với mặt bằng

**Mức ưu tiên:** P1 — Sprint 4

As a sinh viên,
I want thấy phân vị số kỹ năng, số năm kinh nghiệm và lương của tin,
So that tôi biết một con số chỉ xuất hiện khi ô có đủ tin mang đúng trường đó.

**Acceptance Criteria:**

**Given** một tin đã được nhận vai trò
**When** phần so với thị trường hiện
**Then** phân vị số kỹ năng yêu cầu luôn hiện
**And** phân vị số năm chỉ hiện khi trích được số năm từ tin và ô có ít nhất 30 tin có số năm. Nếu không, ghi "chưa đủ dữ liệu (X/30 tin có số năm kinh nghiệm)"
**And** phân vị lương chỉ hiện khi tin có lương dạng số và ô có ít nhất 30 tin có lương. Nếu không, ghi "chưa đủ dữ liệu (X/30 tin có lương)"
**And** ngưỡng đếm số tin có đúng trường đó, không đếm mọi tin của ô
**And** khi 30 ≤ n < 100, phân vị hiện kèm khoảng tin cậy 95% đã tính sẵn
**And** lương quy đổi của tin dán dùng tỷ giá của snapshot đang dùng
**Given** hồ sơ trống
**When** sinh viên soi tin
**Then** phần phân vị vẫn hiện
**And** đổi ô đối chiếu thì phân vị tính lại mà không dán lại tin

### Story 3.4: Khớp tin vừa dán với tin đã thu thập

**Mức ưu tiên:** P1 — Sprint 4

As a sinh viên,
I want biết tin vừa dán đã có trong dữ liệu chưa,
So that tôi mở được tin gốc và các dấu hiệu về lịch sử đăng có căn cứ.

**Acceptance Criteria:**

**Given** một tin đã có trong snapshot
**When** sinh viên dán lại nguyên văn tin đó
**Then** hệ thống tìm đúng tin, bằng cùng phép so khớp đã dùng để gom cụm
**And** kết quả có link về tin gốc
**Given** tin dán không khớp tin nào
**When** kết quả hiện
**Then** phần lịch sử đăng ghi "không đánh giá được: tin chưa có trong dữ liệu"
**Given** tin thuộc snapshot nền
**When** tin đó được khớp
**Then** lịch sử đăng lại cũng ghi "không đánh giá được"

### Story 3.5: Thấy dấu hiệu về độ rộng yêu cầu và lương

**Mức ưu tiên:** P1 — Sprint 4

As a sinh viên,
I want thấy khi một tin đòi nhiều kỹ năng hơn mặt bằng, hoặc đòi nhiều mà trả thấp,
So that tôi tự hỏi lại nhà tuyển dụng mà không bị kết luận tin giả.

**Acceptance Criteria:**

**Given** số kỹ năng đã nhận diện của tin ≥ P90 của ô
**When** kết quả hiện
**Then** D1 hiện dữ kiện đã kích hoạt và gợi ý hỏi rõ 2–3 công nghệ nhóm thực sự dùng
**Given** tin có ít nhất 4 kỹ năng đã nhận diện và hơn 50% thuộc nhóm riêng của công ty
**When** kết quả hiện
**Then** D2 hiện. Kỹ năng chưa nhận diện không tính vào tỷ lệ này
**Given** tin có lương dạng số, ô có ít nhất 30 tin có lương, số kỹ năng ≥ P75 và lương trần ≤ P25
**When** kết quả hiện
**Then** D3 hiện
**And** mỗi quy tắc có một tin mẫu kích hoạt và một tin mẫu không kích hoạt
**And** dưới các dấu hiệu có câu "Dấu hiệu là gợi ý để bạn tự kiểm tra. Đa số tin bị gắn dấu hiệu vẫn là tin thật."
**And** không câu nào dùng "lừa đảo", "tin giả" hay "tin ma", và không câu nào khuyên nộp hay không nộp

### Story 3.6: Thấy dấu hiệu về lịch sử đăng và cách liên hệ

**Mức ưu tiên:** P1 — Sprint 4

As a sinh viên,
I want thấy tin đăng lại nhiều lần, kênh liên hệ lạ, đòi tiền trước, hoặc không nêu tên công ty,
So that tôi biết việc cần tự kiểm tra trước khi gửi thông tin cá nhân.

**Acceptance Criteria:**

**Given** tin khớp một tin đã thu thập và tin đó có số lần đăng lại ≥ 2, hoặc xuất hiện liên tục qua ít nhất 30 snapshot
**When** kết quả hiện
**Then** D4 hiện số lần đăng lại
**Given** tin không khớp tin đã thu thập
**When** kết quả hiện
**Then** D4 ghi "không đánh giá được: tin chưa có trong dữ liệu"
**Given** tin chỉ để lại Zalo, Telegram hoặc email cá nhân
**When** kết quả hiện
**Then** D5 hiện
**Given** tin nhắc đặt cọc, phí đào tạo, phí hồ sơ hoặc phí giữ chỗ
**When** kết quả hiện
**Then** D6 hiện
**Given** tin không nêu tên công ty
**When** kết quả hiện
**Then** D7 hiện
**Given** tin không ghi lương
**When** phần lương hiện
**Then** có dòng "Tin không công bố khoảng lương. Bạn có thể tham khảo phân vị lương của vai trò này (nếu đủ mẫu) khi đàm phán." Đây không phải một dấu hiệu
**And** mỗi quy tắc D4 đến D7 có một tin mẫu kích hoạt và một tin mẫu không kích hoạt
**And** ngưỡng của từng dấu hiệu đọc từ cấu hình

### Story 3.7: Xem từng mục chất lượng của tin

**Mức ưu tiên:** P1 — Sprint 4

As a sinh viên,
I want thấy tin đạt hay không đạt từng mục kiểm tra,
So that tôi đọc được lý do cụ thể thay vì một điểm chất lượng gộp.

**Acceptance Criteria:**

**Given** một tin đã dán
**When** phần chất lượng hiện
**Then** từng mục có trạng thái đạt hoặc không đạt, kèm lý do: có khoảng lương, có tên công ty, có mô tả trách nhiệm, có phúc lợi, và chức danh với kỹ năng cùng cấp bậc có nhất quán không
**And** tin tuyển Fresher nhưng đòi từ 5 năm kinh nghiệm là mục nhất quán không đạt
**And** không có một điểm chất lượng duy nhất
**And** mỗi mục có kiểm thử riêng
**And** từ lúc bấm "Soi tin" đến lúc có mức khớp, phân vị, dấu hiệu và danh sách chất lượng là dưới 15 giây
**And** trên điện thoại, Soi tin làm đủ các việc trên, không phải bản rút gọn

## Epic 4: Đọc những điểm đáng chú ý trong dữ liệu

Sinh viên lọc theo vai trò và đọc năm loại thẻ. Câu trên thẻ là mẫu điền số. Chưa cần hồ sơ. Thẻ có ô dưới 30 tin không hiện, theo FR-38.

### Story 4.1: Đọc thẻ cửa vào cho người mới

**Mức ưu tiên:** P1 — Sprint 6

As a sinh viên,
I want thấy tỷ lệ tin Intern/Fresher/Junior của một vai trò,
So that tôi biết hướng đó có cửa cho người mới hay không, với một câu cố định chứ không phải một đoạn văn viết tự do.

**Acceptance Criteria:**

**Given** một snapshot đã tổng hợp
**When** bước tổng hợp chạy
**Then** thẻ "Cửa vào cho người mới" được ghi cùng snapshot, từ tỷ lệ tin Intern/Fresher/Junior trong từng vai trò
**And** API trả thẻ kèm `meta`. `web` không tự tính tỷ lệ
**When** sinh viên mở Insights mà chưa có hồ sơ
**Then** thẻ hiện một câu mẫu, số căn cứ kèm cỡ mẫu và ngày, và một nút mở Cố vấn với đúng vai trò của thẻ
**And** câu mẫu có các biến thể theo khoảng giá trị, gồm trên 50%, từ 30% đến 50%, và dưới 10%. Đúng ranh giới thì đúng biến thể. Cùng snapshot cho cùng câu
**And** mọi số trong câu khớp số hiện bên dưới
**And** thẻ chỉ hiện khi mọi số của thẻ tính trên ô có n ≥ 30
**And** một truy vấn kiểm tra độc lập trên cùng snapshot khớp số đang hiện
**And** trên điện thoại, thẻ xếp một thẻ một hàng
**And** trang có hai ý độ phủ dữ liệu

### Story 4.2: Đọc thẻ bộ kỹ năng hay đi cùng nhau

**Mức ưu tiên:** P1 — Sprint 6

As a sinh viên,
I want thấy các cặp kỹ năng cùng xuất hiện nhiều nhất trong một vai trò,
So that tôi biết kỹ năng nào thường được nhà tuyển dụng nhắc cùng nhau.

**Acceptance Criteria:**

**Given** snapshot đã có tỷ lệ kỹ năng
**When** bước tổng hợp chạy
**Then** thẻ ghi các cặp kỹ năng cùng xuất hiện nhiều nhất theo từng vai trò
**When** sinh viên mở thẻ
**Then** câu mẫu có dạng đếm trên số tin có kỹ năng A rồi nêu tỷ lệ tin đó cũng nhắc kỹ năng B, kèm n
**And** biến thể câu chọn theo khoảng giá trị, và cùng snapshot cho cùng câu
**And** thẻ chỉ hiện khi mọi ô dùng để tính có n ≥ 30
**And** số trên thẻ khớp một truy vấn độc lập
**And** nút của thẻ mở Cố vấn với vai trò của thẻ

### Story 4.3: Đọc thẻ bậc thang Junior sang Senior

**Mức ưu tiên:** P1 — Sprint 6

As a sinh viên,
I want thấy kỹ năng nào tăng mạnh từ tin Intern/Fresher/Junior lên tin Senior trở lên,
So that tôi phân biệt được kỹ năng của người mới với kỹ năng mặt bằng cấp cao đòi thêm.

**Acceptance Criteria:**

**Given** cùng một vai trò có ô Intern/Fresher/Junior và ô Senior trở lên
**When** cả hai ô có n ≥ 30 và có kỹ năng chênh ít nhất 5 điểm phần trăm
**Then** thẻ hiện các kỹ năng có mức tăng lớn nhất, kèm hai tỷ lệ, cỡ mẫu và ngày
**Given** một ô dưới 30 tin, hoặc mức chênh dưới 5 điểm phần trăm
**When** sinh viên mở Insights
**Then** thẻ bậc thang của vai trò đó không hiện
**And** câu lấy từ mẫu cố định. Cùng snapshot cho cùng câu. Số trong câu khớp số bên dưới
**And** số khớp một truy vấn độc lập
**And** nút mở Cố vấn với vai trò của thẻ
**And** ngưỡng 5 điểm phần trăm đọc từ cấu hình

### Story 4.4: Đọc thẻ khác biệt giữa các thành phố

**Mức ưu tiên:** P1 — Sprint 6

As a sinh viên,
I want thấy kỹ năng nào lệch nhiều nhất giữa Hà Nội và TP.HCM,
So that tôi không dùng một tỷ lệ toàn quốc để kết luận về một thành phố.

**Acceptance Criteria:**

**Given** ô Hà Nội và ô TP.HCM của cùng vai trò đều có n ≥ 30, và có kỹ năng chênh ít nhất 5 điểm phần trăm
**When** sinh viên mở thẻ
**Then** thẻ hiện các kỹ năng chênh nhiều nhất, kèm hai tỷ lệ và cỡ mẫu từng thành phố
**And** ô thành phố không đủ mẫu thì thẻ không lấy số toàn quốc để thế
**Given** ô Đà Nẵng của vai trò đó có n ≥ 30
**When** thẻ được tính
**Then** Đà Nẵng được đưa vào phép so sánh
**Given** ô Đà Nẵng có n < 30
**When** thẻ được tính
**Then** Đà Nẵng không có số trên thẻ
**And** nút của thẻ mở Bản đồ với vai trò đang xem
**And** số khớp một truy vấn độc lập trên cùng snapshot

### Story 4.5: Đọc thẻ ngành và nhà tuyển dụng nổi bật

**Mức ưu tiên:** P1 — Sprint 6

As a sinh viên,
I want thấy ngành và công ty đang có nhiều tin nhất trong một vai trò,
So that tôi biết mặt bằng tin đang tập trung vào đâu.

**Acceptance Criteria:**

**Given** snapshot đã gán ngành và công ty cho các cụm tin
**When** ô của vai trò có n ≥ 30
**Then** thẻ hiện các ngành và các công ty có nhiều tin nhất, kèm số tin, cỡ mẫu và ngày
**Given** ô vai trò có n < 30
**When** sinh viên mở Insights
**Then** thẻ này không hiện
**And** câu lấy từ mẫu cố định và khớp số bên dưới
**And** số khớp một truy vấn độc lập
**And** nút mở Bản đồ với vai trò của thẻ

### Story 4.6: Lọc thẻ theo vai trò

**Mức ưu tiên:** P1 — Sprint 6

As a sinh viên,
I want lọc Insights theo vai trò đang nhắm,
So that tôi chỉ đọc các thẻ của hướng đó, và thấy một câu rõ khi hướng đó chưa đủ dữ liệu.

**Acceptance Criteria:**

**Given** trình duyệt đã lưu vai trò mục tiêu
**When** sinh viên mở Insights
**Then** bộ lọc chọn sẵn vai trò đó
**When** sinh viên đổi bộ lọc
**Then** chỉ còn thẻ của vai trò đó và các thẻ áp dụng cho mọi vai trò
**Given** vai trò không có thẻ nào đủ điều kiện
**When** trang hiện
**Then** có câu "chưa đủ dữ liệu cho vai trò này."
**And** năm loại thẻ dùng chung trang này. Ba loại chưa có hình vẫn hiện khi đủ điều kiện

## Epic 5: Đọc mặt bằng một vai trò mà không mở ứng dụng

Người đọc hoặc trình thu thập mở một URL ổn định và thấy đoạn trả lời khớp snapshot ứng dụng đang hiển thị. Có trang chính sách và kênh gỡ tin trong 48 giờ.

### Story 5.1: Đọc chính sách dữ liệu từ chân trang

**Mức ưu tiên:** P1 — Sprint 1

As a người đọc,
I want mở một trang chính sách không cần tài khoản,
So that tôi biết dữ liệu được dùng để làm gì, dữ liệu nào không được lưu, và gửi yêu cầu gỡ bằng cách nào.

**Acceptance Criteria:**

**Given** một màn ứng dụng
**When** người đọc nhìn chân trang
**Then** có liên kết "Chính sách dữ liệu"
**When** người đọc mở trang
**Then** trang không có nav bốn mục và không có lưới nền. Dưới 560px, các mục xếp một cột
**And** trang có năm mục: mục đích nghiên cứu học thuật phi thương mại, nguồn đang dùng, công bố ở mức tổng hợp, CV và tin dán không được lưu, yêu cầu gỡ trong 48 giờ qua email
**And** nguồn, email, tên nhóm và ngày cập nhật lấy từ cấu hình
**And** trang không chứa bảng R1–R4 và không chứa hai câu "tuân thủ đầy đủ điều khoản của mọi nguồn" và "mọi dữ liệu đều đã được cấp phép", kể cả câu cùng nghĩa
**And** User-Agent của crawler ghi địa chỉ liên hệ trỏ về email trên trang

### Story 5.2: Gỡ tin khỏi số công khai ở snapshot sau

**Mức ưu tiên:** P1 — Sprint 5

As a nhà tuyển dụng,
I want một yêu cầu gỡ hợp lệ làm tin của tôi biến khỏi số liệu công khai,
So that số đã công bố hôm qua không bị sửa, và số từ snapshot sau không còn tin đó.

**Acceptance Criteria:**

**Given** một yêu cầu gỡ hợp lệ được ghi nhận
**When** snapshot kế tiếp chạy bước tổng hợp
**Then** tin liên quan không còn trong số công khai của snapshot đó
**And** hàng của snapshot đã công bố không bị sửa và không bị xóa
**And** yêu cầu lưu thời điểm nhận, để thấy yêu cầu nào đã quá 48 giờ

### Story 5.3: Đọc trang vai trò khi đủ mẫu

**Mức ưu tiên:** P1 — Sprint 5

As a người đọc,
I want mở URL của một vai trò và thấy ít nhất ba kỹ năng kèm tỷ lệ,
So that tôi đọc được mặt bằng mà không cần tài khoản và không cần mở ứng dụng.

**Acceptance Criteria:**

**Given** danh sách vai trò lúc công khai trong cấu hình, và ô vai trò × mọi cấp bậc × toàn quốc có n ≥ 30
**When** người đọc mở URL của vai trò đó, kể cả request không cookie
**Then** có đúng một URL cho vai trò đó. URL không đổi khi sang snapshot mới, không chuyển hướng đăng nhập, và không nằm trong chỉ dẫn chặn thu thập
**And** đoạn đầu trong nội dung trả về có ít nhất ba kỹ năng, mỗi kỹ năng một tỷ lệ, kèm n, nguồn đang bật và ngày snapshot
**And** trang không dùng thứ tự quay về và không vẽ tỷ trọng thành phố
**And** phân vị số kỹ năng hiện khi n của ô ≥ 30. Phân vị lương và phân vị số năm chỉ hiện khi có ít nhất 30 tin có đúng trường đó
**And** trang có hai ý độ phủ, gồm ba lưu ý của FR-36, và có liên kết tới trang chính sách
**And** trang không liệt kê tin, không có chức danh, công ty, thành phố, lương của từng tin, không có link tin gốc và không có toàn văn JD
**And** template chỉ gọi endpoint số tổng hợp
**And** trang không có nav bốn mục và không có lưới nền. Cấp bậc được gọi là Mid
**And** trang không chứa hai câu cấm của Story 5.1

### Story 5.4: Giấu số khi trang vai trò chưa đủ mẫu

**Mức ưu tiên:** P1 — Sprint 5

As a người đọc,
I want trang vai trò nói chưa đủ dữ liệu khi mẫu nhỏ,
So that tôi không nhận một tỷ lệ hay một phân vị được tính trên quá ít tin.

**Acceptance Criteria:**

**Given** ô vai trò × mọi cấp bậc × toàn quốc có n < 30
**When** người đọc mở URL
**Then** đoạn đầu chỉ là "chưa đủ dữ liệu (n = X)". Không có tên nhóm kỹ năng và không có phần trăm
**Given** n của ô ≥ 30 nhưng số tin có lương dưới 30
**When** trang hiện
**Then** phân vị lương không hiện, kể cả khi các tỷ lệ kỹ năng vẫn hiện
**Given** số tin có số năm kinh nghiệm dưới 30
**When** trang hiện
**Then** phân vị số năm không hiện

### Story 5.5: Trang vai trò khớp snapshot ứng dụng đang hiển thị

**Mức ưu tiên:** P1 — Sprint 5

As a người đọc,
I want trang vai trò đổi số ngay khi ứng dụng chuyển snapshot,
So that trang công khai không giữ số của đêm hôm trước trong khi ứng dụng đã sang đêm nay.

**Acceptance Criteria:**

**Given** snapshot chuyển sang `published` hoặc `partial`
**When** bước cuối pipeline chạy
**Then** pipeline gọi route làm mới bằng secret, rồi gửi GET tới từng URL trong sitemap
**And** bước mồi thất bại thì lượt chạy báo lỗi
**And** trang không render động theo từng request
**When** người đọc mở URL sau bước mồi, kể cả snapshot thiếu nguồn
**Then** ngày và số trên trang khớp bảng tổng hợp của snapshot đó. Nguồn thiếu có trong danh sách nguồn
**And** trang không giữ snapshot cũ hơn snapshot ứng dụng đang hiển thị
**And** thêm dữ liệu có cấu trúc cho công cụ tìm kiếm không phải tiêu chí hoàn thành của story này

## Epic 6: Hoàn tất một phiên thử nghiệm mà không để lại danh tính

Người thử vào bằng link thử nghiệm, trả lời trước khi thấy số, dùng sản phẩm, rồi chấm so sánh mù. Nhóm xuất được một bảng theo mã phiên.

### Story 6.1: Vào bằng link thử nghiệm

**Mức ưu tiên:** P1 — Sprint 6

As a người thử,
I want vào một link riêng và thấy mình đang ở chế độ thử nghiệm,
So that phiên của tôi tách được khỏi người dùng thường, mà không phải để lại email.

**Acceptance Criteria:**

**Given** người dùng mở ứng dụng không có `mode=eval`
**When** họ dùng Bản đồ, Cố vấn hoặc Soi tin
**Then** không thấy nhãn thử nghiệm và không thấy modal thử nghiệm
**Given** người thử mở `?mode=eval`
**When** trang tải
**Then** giao diện luôn hiện nhãn "Chế độ thử nghiệm"
**And** phiên được nối với bảng `eval_*` bằng mã phiên ẩn danh
**And** `anon_events` vẫn chỉ có bốn trường. Không có cờ thử nghiệm trên bảng đó
**And** một truy vấn tách được phiên thử nghiệm khỏi sự kiện sử dụng thường

### Story 6.2: Trả lời trước khi thấy số

**Mức ưu tiên:** P1 — Sprint 6

As a người thử,
I want được hỏi mình đang nghĩ gì trước khi nhìn thấy số liệu,
So that câu trả lời đầu phiên không bị ảnh hưởng bởi những gì sản phẩm sắp cho xem.

**Acceptance Criteria:**

**Given** người thử vừa mở link thử nghiệm
**When** trang tải
**Then** một modal che toàn bộ nền trước khi bất kỳ con số nào của Bản đồ hiện ra
**And** modal hỏi nhóm trong trường hoặc ngoài trường, vai trò mục tiêu, đúng 3 kỹ năng, và câu nguyên văn "Ở thời điểm hiện tại, mức độ rõ ràng của bạn về những kỹ năng cần ưu tiên học tiếp theo cho vị trí mục tiêu là bao nhiêu?" với thang 1 đến 5
**And** 3 kỹ năng chọn từ bộ từ vựng bằng ô tìm có gợi ý, và được lưu bằng mã kỹ năng
**And** chưa trả lời xong thì không đóng được modal
**And** loại thiết bị, máy tính hoặc điện thoại, được ghi ở bản ghi đầu phiên
**And** modal không có ô email, Zalo hay thông tin liên hệ
**And** modal làm đủ việc này trên điện thoại

### Story 6.3: Gửi đánh giá cuối phiên một lần

**Mức ưu tiên:** P1 — Sprint 6

As a người thử,
I want trả lời lại đúng câu lúc đầu và nói mình có định sửa CV hay không,
So that nhóm có một cặp điểm trước và sau cho cùng một phiên.

**Acceptance Criteria:**

**Given** một phiên thử nghiệm đang mở
**When** người thử dùng sản phẩm
**Then** luôn có nút "Hoàn tất thử nghiệm & Đánh giá (1 phút)"
**When** người thử bấm nút đó, hoặc bấm "Lưu kết quả", hoặc bấm "Copy link chia sẻ"
**Then** modal cuối phiên mở
**And** modal hỏi lại đúng nguyên văn câu thang 1 đến 5 của Story 6.2, và câu "Sau phiên này, bạn có dự định sửa CV hoặc đổi thứ tự học trong 4 tuần tới không?" với hai lựa chọn Có và Không
**And** mỗi mã phiên chỉ gửi được modal cuối một lần. Lần gửi sau bị từ chối
**And** modal làm đủ việc này trên điện thoại
**And** không có ô email, Zalo hay thông tin liên hệ

### Story 6.4: Chấm so sánh mù

**Mức ưu tiên:** P1 — Sprint 6

As a người thử,
I want chấm hai phương án tư vấn không ghi nguồn,
So that lựa chọn của tôi không dựa vào việc biết đâu là Hải Đồ IT.

**Acceptance Criteria:**

**Given** vai trò mục tiêu của người thử có tình huống mẫu trong repo
**When** modal cuối phiên mở
**Then** hiện một hồ sơ kỹ năng mẫu, một JD mẫu, và hai phương án: một do Hải Đồ IT tạo sẵn trên đầu vào đó tại một snapshot cố định, một là câu trả lời ChatGPT soạn sẵn cho cùng đầu vào
**And** hai phương án đọc từ file JSON có phiên bản. Lúc mở modal không có request nào lấy nội dung phương án
**And** hai phương án không ghi nguồn, cùng dạng markdown gạch đầu dòng, độ dài tương đương
**And** thứ tự trái và phải đảo ngẫu nhiên 50/50, và vị trí đã hiện được lưu
**And** người thử chấm từng phương án từ 1 đến 5, rồi chọn phương án mình thấy hữu ích hơn. Chưa chấm và chưa chọn thì chưa gửi được modal cuối
**Given** người thử dùng điện thoại
**When** hai phương án hiện
**Then** chúng xếp trên và dưới, vẫn đảo 50/50, và vị trí đã hiện vẫn được lưu
**Given** vai trò chưa có file tình huống mẫu
**When** modal cuối mở
**Then** phần so sánh không gọi API để tạo phương án mới

### Story 6.5: Xuất một bảng theo phiên

**Mức ưu tiên:** P1 — Sprint 6

As a nhóm nghiên cứu,
I want một câu truy vấn ra đủ số liệu của từng phiên,
So that báo cáo thử nghiệm ghép được câu trả lời đầu, các lựa chọn kỹ năng, và phần chấm cuối mà không cần danh tính.

**Acceptance Criteria:**

**Given** các phiên đã có modal đầu, sự kiện xác nhận khoảng trống, và modal cuối
**When** chạy một câu truy vấn
**Then** mỗi phiên một dòng, gồm nhóm trong trường hoặc ngoài trường, 3 mã kỹ năng tự đoán, các lựa chọn "đã biết / chưa biết", ý định hành động, điểm và lựa chọn của phần so sánh mù
**And** các lựa chọn kỹ năng lấy từ sự kiện của Story 2.5, nối bằng mã phiên
**And** kết quả không có email, Zalo hay thông tin liên hệ
**And** 3 kỹ năng trong bảng là mã kỹ năng

### Story 6.6: Sao lưu phiên thử nghiệm sau ngày có người thử

**Mức ưu tiên:** P1 — Sprint 6

As a nhóm nghiên cứu,
I want dữ liệu thử nghiệm có bản sao riêng sau mỗi ngày có phiên,
So that mất máy chủ không làm mất phiên ẩn danh không thể hỏi lại.

**Acceptance Criteria:**

**Given** một ngày có ít nhất một phiên thử nghiệm được ghi
**When** lịch sao lưu chạy
**Then** các bảng `eval_*` có một bản sao thêm ở ngoài VPS
**And** một lần phục hồi bản sao đó đọc lại được dòng của phiên
