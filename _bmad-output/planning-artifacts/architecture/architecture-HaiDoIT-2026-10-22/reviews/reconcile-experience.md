---
title: Đối chiếu EXPERIENCE.md với architecture spine
type: architecture-reconcile
source: _bmad-output/planning-artifacts/ux-designs/ux-HaiDoIT-2026-10-22/EXPERIENCE.md
compared: _bmad-output/planning-artifacts/architecture/architecture-HaiDoIT-2026-10-22/ARCHITECTURE-SPINE.md
date: 2026-10-23
verdict: gaps
---

# Đối chiếu EXPERIENCE với spine

Spine và EXPERIENCE.md không bị sửa trong lần này. Bản này chỉ ghi chỗ hai người xây (API, lệnh nạp, trình duyệt) có thể làm khác nhau vì spine bỏ hợp đồng hoặc nói ngược EXPERIENCE.

Câu chữ trên màn và thứ tự bước mà EXPERIENCE đã khóa được xếp `story-detail` ở cuối. Chúng thành lỗ khi hai đơn vị có thể chọn khác chủ: ai tính, ai lưu, ai gửi thư, model hỏng thì ra gì, token và mở lại, phép tính offer, trạng thái rỗng làm đổi hợp đồng dữ liệu.

Nhãn `[GIẢ ĐỊNH]` giữ nguyên. Không nâng thành sự thật đã đo.

**Verdict: gaps.** Một mâu thuẫn về khoảng dự báo trước tuần 1. Nhiều lỗ hợp đồng dữ liệu ở ô mẫu, vòng đời tin, Học gì tiếp?, mở lại lộ trình, hình ba chặng, và phép tính offer.

## Đã khớp, không lập finding

- Web vẽ payload. Số tin, lương công khai và dự báo không tính trong Next.js (AD-2). Offer là ngoại lệ có chủ ở AD-9.
- Một Postgres Supabase, trình duyệt không nối Supabase, không đăng nhập Supabase (AD-3). Khớp «không mật khẩu, không hồ sơ công khai».
- Lệnh nạp là chỗ duy nhất ghi tin. Dòng giữ kỹ năng, thành phố, cấp bậc, khoảng lương, ngày đăng, link gốc. Không giữ mô tả, tên công ty, tên và liên hệ người tuyển (AD-4). Khớp Vì sao? không trỏ nguyên văn mô tả.
- Lương công khai là trung vị điểm giữa các khoảng VND, từ 30 tin; số điểm chẵn lấy trung bình hai điểm giữa; dưới 30 thì câu chưa đủ mẫu; không đổi USD (AD-6). Đây là «cách gộp nhiều khoảng» mà EXPERIENCE để cho kiến trúc. Ô nào được đem đi gộp thì chưa khóa — xem F3.
- Model local, một lần gọi, không API chat trả phí, không mạng năm agent. Lộ trình chỉ ghi khi thư gửi được (AD-7). Khớp cấm agent trên màn và khớp lưu lỗi. Hình của ba chặng thì xem F6.
- Token không đoán được, server lưu hash, một email một lộ trình, biết email không trả lộ trình trên màn, ngày 14 không làm token hết hạn, lưu lại hoặc gửi lại thì token mới và liên kết cũ ngừng mở (AD-8). Khớp phần EXPERIENCE đã nói. Payload mở lại và sự kiện đo 14 ngày thì xem F8.
- Không có API nhận nội dung offer. Soi tin không ghi server và không qua model (AD-9). Khớp UJ-3 và UJ-4 khi đóng trang.
- Danh kỹ năng và số tuần nằm trong Supabase, tên trùng pipeline, Next nhận danh từ FastAPI (AD-10). Khớp danh chip cố định. Cách cộng tuần và cách xếp hạng thì xem F4.
- Thư thật chỉ từ máy chạy web (AD-11). EXPERIENCE không nói môi trường máy code.
- Tín hiệu sớm, khi chưa có quy tắc phát hiện: thẻ dùng câu chưa ghi nhận (AD-12, nửa tín hiệu). Khớp State Patterns «Chưa có tín hiệu». Nửa khoảng dự báo thì xem F1.
- Không nút báo nguồn, không thư báo nguồn, không bảng báo nguồn (AD-13). Khớp giả định đường nhanh.
- Convention: lỗi API là một câu tiếng Việt đã có trong EXPERIENCE, không stack trace.

---

## F1. Khoảng dự báo trước tuần 1

- **Severity:** cao
- **EXPERIENCE:** Component Patterns, Tầm nhìn và Thẻ thành phố; Ngưỡng, nguồn, và hồ sơ. «NAY» hiện số tin đang mở. «+6T», «+12T», «+18T» hiện một khoảng có nhãn «Dự báo». Vì sao? của khoảng đó trỏ tới số tin đang dùng để tính. Khi tầm nhìn đang là «NAY», chỗ dự báo trên thẻ thành phố vẫn hiện khoảng mốc 12 tháng, có nhãn dự báo. Tín hiệu là đúng một tín hiệu kèm Vì sao?, hoặc câu «Chưa ghi nhận tín hiệu đáng kể cho thành phố này.» khi chưa có quy tắc. Cách tính khoảng thuộc kiến trúc hoặc tuần 1, và người dùng vẫn thấy một khoảng có nhãn dự báo.
- **Spine:** AD-12 buộc cả dự báo 18 tháng và tín hiệu sớm. Trước tuần 1, màn dùng câu chưa ghi nhận. Quy tắc đo được mới thay câu đó. Deferred lặp lại: công thức dự báo chờ tuần 1, trước đó là câu chưa ghi nhận. AD-12 cấm hệ số minh họa của prototype.
- **Class:** contradiction

Hai bản trả lời khác nhau cho cùng một ô trên thẻ. Người làm theo spine để «+6T», «+12T», «+18T» và ô 12 tháng lúc «NAY» thành câu chưa ghi nhận, không có khoảng. Người làm theo EXPERIENCE vẫn vẽ một khoảng có chữ «Dự báo», và chỉ ô tín hiệu dùng câu chưa ghi nhận. Cả hai đều không được lấy hệ số minh họa của prototype. Spine đã chọn «không có số»; EXPERIENCE vẫn bắt buộc có khoảng.

Nửa tín hiệu sớm thì khớp: chưa có quy tắc thì câu chưa ghi nhận, không bịa một tín hiệu.

## F2. Vòng đời tin đang mở

- **Severity:** cao
- **EXPERIENCE:** Information Architecture; Component Patterns, Kết quả soi tin; State Patterns, Lương ẩn và đoạn tin treo; Ngưỡng, nguồn, và hồ sơ; UJ-3. Số trên bản đồ là số tin đang mở. Soi tin luôn có số lần làm mới, ngày thấy đầu và ngày thấy gần nhất khi link có trong dữ liệu. Lần làm mới của một tin là số lần tin đó được thấy lại, và khác với ngày làm mới dữ liệu ghi ở chân mọi màn. Tin trùng là tin đang mở khác, trùng kỹ năng, thành phố, cấp bậc và khoảng lương. Trước tuần 1, màn hiện ba sự kiện kiểm được. Câu «tin treo», nếu hiện, phải nói ngưỡng đang dùng, và ngưỡng đó là `[GIẢ ĐỊNH]` (làm mới từ lần thứ hai, hoặc vẫn đang mở sau 30 ngày kể từ ngày thấy đầu), chưa phải sự thật đã đo. VietJobs chỉ được ghi công như nền lịch sử, không như tin đang mở.
- **Spine:** AD-4 mô tả lần thấy lại: cập nhật ngày thấy gần nhất, giữ ngày thấy đầu. Không có bộ đếm lần thấy. Không có mốc «lần nạp dữ liệu» cho chân trang. Không định nghĩa tin biến mất khỏi file cào thì còn đang mở, bị đóng, hay bị xóa. Không có danh nguồn được tính là tin đang mở, nên không có chỗ loại VietJobs. Không có quy tắc «tin treo».
- **Class:** spine-hole

Ngày thấy đầu và ngày thấy gần nhất không suy ra được số lần thấy lại. Một lệnh nạp có thể đếm mỗi lần gặp trong file, lần khác chỉ ghi ngày. Một API có thể coi tin vắng mặt ở lần nạp mới là đã đóng, lần khác giữ mọi dòng từng nạp là đang mở. Xóa dòng khi tin biến mất thì link cũ thành «Chưa soi được tin này.» và mất ngày thấy đầu. Giữ mãi thì số tin đang mở không bao giờ giảm. Chân trang có thể lấy max(ngày thấy gần nhất) và trùng với ngày của từng tin, đúng chỗ EXPERIENCE tách hai mốc. Nhãn tin treo có thể bị một người gắn như sự thật từ ngưỡng giả định, người kia chỉ trả ba số.

## F3. Ô mẫu: vai trò, thành phố, cấp, lương

- **Severity:** cao
- **EXPERIENCE:** Information Architecture (bảy thành phố); Component Patterns, Chip vai trò, Bản đồ 3D, Ô lương đầu trang, Danh kỹ năng thành phố, Thẻ thành phố; dòng Fresher và Junior. Đổi chip vai trò thì số tin bảy thành phố đổi theo vai trò. Đủ bảy thành phố kể cả khi một thành phố ít tin: Hà Nội, Hải Phòng, Đà Nẵng, Quy Nhơn, Nha Trang, TP. Hồ Chí Minh, Cần Thơ. Ô lương đầu trang cùng ô mẫu với lương trên thẻ. Chưa chọn thành phố thì không hiện số. Bộ lọc một vai trò thì ô đó là vai trò đang lọc. Bộ lọc «Tất cả» thì vai trò của ô là vai trò có nhiều tin nhất tại thành phố đó. Đã chọn cấp thì lấy cấp hồ sơ phiên. Chưa chọn cấp thì dùng Junior `[GIẢ ĐỊNH từ PRD]`. Lương ẩn thì thành phố và số tin vẫn hiện. Danh kỹ năng trên thẻ thành phố là kỹ năng đang được nhắc trong tin của thành phố đó, không phải cả danh chip. Học gì tiếp? chỉ dựng kịch bản cho Fresher và Junior `[GIẢ ĐỊNH từ PRD]`. Cơ cấu vai trò cộng một nhóm còn lại, tổng 100%.
- **Spine:** AD-4 lưu kỹ năng, thành phố, cấp bậc, khoảng lương, ngày đăng, link gốc. Không có vai trò trên dòng tin. AD-6 định nghĩa cách gộp lương của «ô đang tính» và không nói ô đó cắt theo vai trò nào, cấp nào. AD-10 là danh chip và số tuần, không phải danh kỹ năng đang được nhắc trong tin của một thành phố. Không có danh bảy thành phố, không có quy tắc luôn trả đủ bảy dòng, không có giá trị chuẩn của cấp bậc.
- **Class:** spine-hole

Thiếu vai trò trên dòng tin thì hai người có thể gán vai trò từ kỹ năng theo hai bảng khác nhau, hoặc một người lọc được theo chip và người kia chỉ có tổng theo thành phố. Cùng AD-6, ô «Tất cả» có thể thành trung vị cả thành phố, hoặc trung vị của vai trò đông tin nhất ở cấp Junior. Danh trên thẻ thành phố có thể là mọi chip trong AD-10, kể cả kỹ năng thành phố không nhắc, rồi dấu «đã có» rơi nhầm. Thành phố viết «HCM» và «TP. Hồ Chí Minh» tách đôi số. Thành phố 0 tin có thể biến mất khỏi payload trong khi EXPERIENCE vẫn vẽ đủ bảy cột. Cấp pipeline ngoài Fresher và Junior có thể bị bỏ hoặc thành một kịch bản thứ ba trên Học gì tiếp?.

Cơ cấu «tổng 100% và một nhóm còn lại» cùng lỗ, mức thấp hơn: AD-2 giao FastAPI tính số, còn quy tắc phần trăm thì không có trong spine.

## F4. Hợp đồng số của Học gì tiếp?

- **Severity:** cao
- **EXPERIENCE:** Component Patterns, Danh nên học tiếp, và hai đoạn ngay dưới bảng. Tin đủ điều kiện là tin đang mở trong phạm vi đang tính, đúng vai trò mục tiêu và đúng cấp bậc, và có đủ mọi kỹ năng đã có cùng mọi kỹ năng giả định đang chọn. Thời gian học là tổng số tuần của các kỹ năng giả định đang chọn. Độ phủ của một vai trò là số kỹ năng yêu cầu của vai đó đang nằm trong kỹ năng đã có, chia cho số kỹ năng yêu cầu của vai đó. Danh kỹ năng yêu cầu đi cùng danh cố định. Thêm một kỹ năng đã có thì độ phủ trước tăng. Khi ô vai trò × thành phố × cấp bậc dưới 30 tin, nới toàn quốc cùng vai trò và cùng cấp bậc trước, rồi nới sang nhóm vai gần nếu vẫn dưới ngưỡng. Nhóm vai gần là `[GIẢ ĐỊNH từ PRD]`: Data/AI đứng riêng; Backend với Frontend; DevOps/Cloud với Bảo mật; Mobile đứng riêng. Lương ô gốc mỏng không hiện số. Khi phạm vi đã nới đủ 30 tin, lương công khai của phạm vi đó được hiện. Vì sao? của kết quả đã nới nói ô gốc dưới 30 và đang ở bước toàn quốc hay bước nhóm vai gần. Danh nên học tiếp xếp theo số tin mở thêm trên mỗi tuần học. Mỗi dòng có số tin tăng, số tuần, và số tin trên mỗi tuần. Kỹ năng lớp dữ liệu đánh dấu đang giảm không đứng hạng nhất. `[GIẢ ĐỊNH]` ô Data/AI theo thành phố có thể dưới 30 tin là việc đo trong tuần 1, chưa phải sự thật.
- **Spine:** AD-2 giao FastAPI tính số tin, lương và dự báo. AD-6 áp ngưỡng 30 cho việc hiện trung vị của ô đang tính. AD-10 lưu số tuần từng kỹ năng. Không có vị từ tin đủ điều kiện, thứ tự nới, nhóm vai, quy tắc lương của ô đã nới, độ phủ, hay cách xếp «tin tăng trên mỗi tuần». Memlog đã chốt «bước nới phạm vi chỉ tính trong FastAPI»; câu đó không thành AD.
- **Class:** spine-hole

Chủ tính số đã nghiêng về FastAPI, nên lỗ không phải «Next có được tự nới hay không». Lỗ là hai người viết FastAPI vẫn ra hai payload. Một người đếm tin có bất kỳ kỹ năng nào trong tập đã chọn. EXPERIENCE đòi đủ mọi kỹ năng đã có và mọi kỹ năng giả định. Một người ẩn lương suốt khi ô thành phố dưới 30, kể cả sau khi phạm vi nới đã đủ 30. EXPERIENCE hiện lương của phạm vi đã nới. Một người xếp theo tổng tin tăng, người kia chia cho số tuần. Nhóm vai gần còn là giả định: spine im nên một người có thể hard-code, người kia bỏ bước nới thứ hai. Không có AD nào giữ câu «ô Data/AI mỏng là giả định, đo tuần 1», nên một seed có thể gắn sẵn Hải Phòng Data/AI là ô mỏng.

## F5. Lớp xu hướng tám quý

- **Severity:** cao
- **EXPERIENCE:** Information Architecture; Component Patterns, Khối xu hướng tám quý và Danh nên học tiếp. Xu hướng và hạn dùng kỹ năng là một lớp dùng chung. Khối tám quý trên Bản đồ nhu cầu là chỗ người dùng nhìn thấy lớp đó. Học gì tiếp? và lộ trình đọc cùng lớp khi xếp hạng và khi viết Vì sao?. Khối có chú giải tăng, giảm, đi ngang. Khi lớp chưa có số, khối hiện «Chưa đủ mẫu.». Kỹ năng bị lớp đánh dấu đang giảm không đứng hạng nhất, và Vì sao? nói mức giảm.
- **Spine:** Không có lớp tám quý, không có chuỗi theo quý, không có cờ đang giảm. AD-12 chỉ buộc câu chưa ghi nhận cho dự báo 18 tháng và tín hiệu sớm. AD-4 giữ ảnh tin hiện tại cùng ngày thấy, không giữ lịch sử sau khi tin không còn mở. Capability map không có chủ cho lớp này.
- **Class:** spine-hole

Trạng thái rỗng làm đổi số trên một màn khác. Khi lớp chưa có số, Học gì tiếp? không có kỹ năng nào bị cấm hạng nhất, và khối tám quý nói chưa đủ mẫu. Người xây có thể bịa chuỗi quý từ ngày đăng của tin đang mở, người khác áp câu của AD-12 («chưa ghi nhận») vào khối này, người thứ ba bỏ khối. Ba cách ra ba hợp đồng. Tin đã đóng không còn trong bảng thì tám quý không dựng lại được từ các cột AD-4. Chủ của chuỗi quý (lệnh nạp ghi snapshot, hay API tính lúc đọc) chưa được gọi tên.

## F6. Hình ba chặng khi model chạy và khi model hỏng

- **Severity:** cao
- **EXPERIENCE:** Component Patterns, Nút chính và Thẻ chặng; UJ-1. Nút tạo lập ba chặng từ hồ sơ phiên và các kỹ năng giả định đang chọn. Đủ ba chặng, ngày 1–30, 31–60, 61–90. Mỗi chặng có kỹ năng của chặng, tên một dự án, và một câu sản phẩm người học làm ra. Kỹ năng trên lộ trình nằm trong kỹ năng giả định đang chọn. Khi không còn kỹ năng giả định, một chặng đào sâu kỹ năng đã có. Đổi kỹ năng giả định rồi tạo lại thì chữ trong chặng đổi theo. Một chặng không có liên kết khóa vẫn tạo và lưu được. Không có chỗ bấm sang khóa học.
- **Spine:** AD-7: FastAPI tính số trước. Ollama viết ba câu từ các số đó. Model không được bịa số tin hoặc lương. Vì sao? trỏ về số. Model hỏng thì điền câu mẫu từ cùng các số. Một lần gọi. Lộ trình chỉ ghi khi email lưu được.
- **Class:** spine-hole

Đường model hỏng đã có chủ: câu mẫu, cùng các số, một lần gọi. Hình câu mẫu thì chưa có. «Ba câu» có thể là ba đoạn văn tự do, không cắt ngày 1–30 / 31–60 / 61–90, không có tên dự án, và chọn một kỹ năng ngoài tập giả định. Người kia để FastAPI gán kỹ năng và khung ngày, model chỉ viết tên dự án và câu sản phẩm. Cả hai đều thỏa AD-7. Câu mẫu lúc Ollama hỏng cùng chỗ trống đó, nên bản fallback và bản model có thể lệch khung. Liên kết khóa có thể nằm trong câu của model vì spine không cấm URL trong ba câu.

## F7. Payload của Vì sao?

- **Severity:** cao
- **EXPERIENCE:** Component Patterns, Nút Vì sao? và Ngăn Vì sao?; Ngưỡng, nguồn, và hồ sơ. Nguồn từ tin thì trỏ tập đã trích hoặc link gốc, không trỏ nguyên văn mô tả. Nguồn từ báo cáo thì gọi tên một trong bốn: ITviec, TopDev, TopCV, JobOKO. VietJobs chỉ là nền lịch sử. Kết quả đã nới thì nói ô gốc dưới 30 tin và nói đang ở bước toàn quốc hay bước nhóm vai gần. Nhận định bị loại vì thiếu dữ liệu vẫn có nút, và câu nói thiếu dữ liệu, không nói một mức lương. Trước khi gọi một API bên ngoài, bỏ thông tin cá nhân khỏi phần được gửi đi.
- **Spine:** AD-7 nói Vì sao? trỏ về số. AD-4 không lưu mô tả và không lưu liên hệ người tuyển, nên hai thứ đó không có trong database để trả ra. Không có AD nào bắt payload gồm link gốc, tên báo cáo trong bốn tên, bước nới, hoặc câu thiếu dữ liệu không kèm lương. Ollama chạy trên máy nhóm (AD-7, AD-11), không phải API chat trả phí. Không có quy tắc prompt loại email.
- **Class:** spine-hole

Một ngăn chỉ hiện trung vị và số tin là đủ AD-7, và thiếu link gốc hoặc tập đã trích mà EXPERIENCE bắt với nhận định từ tin. Báo cáo TopCV và JobOKO không có chỗ lưu, nên một người bỏ nhánh «nguồn từ báo cáo», người kia nhét báo cáo vào bảng tin đang mở. Nhận định bị loại có thể biến mất, hoặc model điền một mức lương cho ô mỏng. AD-6 và câu «model không bịa lương» chặn mức lương bịa nếu người xây nối hai AD; spine không nói câu thiếu dữ liệu vẫn phải có mặt.

Việc gọi API bên ngoài và việc bỏ thông tin cá nhân: spine đã chọn model local. Email người dùng đi ra hộp thư nhóm là thư mở lại, không phải prompt. Spine không nói prompt Ollama có được chứa email hay không. Mức thấp hơn F7, cùng lỗ chủ của nội dung gửi sang model.

## F8. Mở lại token, cửa sổ 14 ngày, và kết cục lưu

- **Severity:** cao
- **EXPERIENCE:** Information Architecture; Component Patterns, Ô email và Ô nhận lại liên kết; State Patterns, Mở lại đúng liên kết, Máy khác, Lưu lỗi; UJ-2; Ngưỡng, nguồn, và hồ sơ. Hồ sơ phiên (thành phố, cấp bậc, vai trò mục tiêu, kỹ năng đã có) sống trên máy đến lúc lưu. Gửi được thì lưu hồ sơ lẫn lộ trình và đưa liên kết mở lại. Mở đúng liên kết thì ra đúng thành phố, cấp, vai trò, kỹ năng đã có, và ba chặng của lần lưu. UJ-2 trên máy khác: dấu «đã có» của Python và SQL vẫn hiện trên bản đồ, không chọn lại từ đầu. Sau ngày 14 liên kết vẫn mở đúng lộ trình. Cửa sổ 14 ngày chỉ để đo: lần mở trong cửa sổ, cùng email, tính từ lúc lưu, được tính là mở lại; lần mở sau ngày 14 không tính. Lưu lần nữa thì thay lộ trình trước và tính lại 14 ngày `[GIẢ ĐỊNH từ PRD]`. Email chưa từng lưu thì câu «Chưa có lộ trình cho email này.» và không tạo một lộ trình trống `[GIẢ ĐỊNH]`. Gửi thất bại thì lộ trình còn trên máy, chưa tính là tạo xong. Email không hiện cho người khác.
- **Spine:** AD-8 lưu hash của token cạnh đúng một lộ trình của email đó. Biết email không trả lộ trình trên màn. Ngày 14 không làm token hết hạn. Gửi lại thư hoặc lưu lần nữa thì token mới, liên kết cũ ngừng mở. «Hồ sơ trên trình duyệt cho đến lúc lưu.» Không nói bản lưu gồm thành phố, cấp, vai trò và kỹ năng đã có. Không nói response mở token trả các trường đó để trình duyệt ghi vào hồ sơ phiên. Không có sự kiện «đã mở» trên server, không có mốc cửa sổ để lần mở sau ngày 14 bị loại khỏi phép đo, không nói lưu mới thì cửa sổ tính lại. Không nói email chưa có thì không tạo dòng. Không cấm màn mở lại hiện email. AD-7 và convention: chỉ ghi lộ trình khi thư gửi được.
- **Class:** spine-hole

Đọc sát «hồ sơ trên trình duyệt cho đến lúc lưu», một người để hồ sơ chỉ ở trình duyệt và server chỉ giữ ba câu. Máy khác mở token thì có chữ lộ trình, bản đồ không có dấu đã có. EXPERIENCE UJ-2 cần response mở token mang hồ sơ đã lưu, và Next ghi hồ sơ đó vào phiên trên máy mới.

Cửa sổ 14 ngày đo trên máy khác, nên sự kiện mở phải ở server, cạnh `saved_at`. Spine chỉ nói token không hết hạn. Một người không ghi lần mở. Một người đếm trong localStorage và mất số khi đổi máy. Một người cho ngày 14 làm token chết, trái cả AD-8 lẫn EXPERIENCE.

Nhánh phụ, mức trung bình, cùng hợp đồng lưu:

- Email lạ trên ô nhận lại liên kết không được tạo lộ trình trống. Spine có «gửi lại thư» mà không cấm upsert một dòng rỗng. Lần gửi sau sẽ có token cho một lộ trình EXPERIENCE nói là chưa từng lưu.
- Thư và dòng phải cùng một kết cục. EXPERIENCE: thư thất bại thì chưa lưu, và email đó đi vào câu «Chưa có lộ trình cho email này.». Spine nói chỉ ghi khi thư gửi được, và không nói rollback nếu dòng đã commit rồi SMTP mới trả lỗi. Dòng sót làm ô nhận lại liên kết gửi được thư cho một lần lưu màn hình đã gọi là thất bại.
- Màn mở lại có thể in email của người lưu. EXPERIENCE cấm email hiện cho người khác. AD-8 chỉ cấm trả lộ trình khi biết email.

## F9. Phép tính offer trên trình duyệt

- **Severity:** cao
- **EXPERIENCE:** Component Patterns, Panel offer, Thanh thực nhận, Hộp hụt bảo hiểm; State Patterns, Offer thiếu ô, Offer đủ ô, Đóng bảo hiểm trên mức thấp; Voice and Tone; UJ-4. Sửa một ô thì thực nhận cả năm tính lại. Ngày remote hiện trên panel và không đổi tiền. Chọn «Trên mức thấp hơn» thì hiện ô mức đóng. Offer gross và căn cứ là lương thật thì mức đóng bằng lương gross. Offer net mặc định dò ngược ra gross, trừ khi người dùng nhập mức khác. Hụt chỉ khi căn cứ thấp hơn lương gross đang dùng. Khoản hụt là cả năm, gồm phần người lao động và phần công ty ở mức ước tính, và các chế độ tính trên mức thấp đó. Đóng trên lương thật thì không có câu hụt. Thiếu ô bắt buộc thì chưa có câu bên nào cao hơn. EXPERIENCE không liệt kê ô nào là bắt buộc. Chênh dưới 1% thực nhận cả năm thì «Hai offer gần ngang nhau.» `[GIẢ ĐỊNH]`. Mục «Tham số tính (kỳ tính thuế 2026)» hiện đúng bộ số phụ lục PRD và được thay khi quy định đổi. Đóng trang thì không còn gì trên máy chủ.
- **Spine:** AD-9. FastAPI chỉ trả bộ số thuế và BHXH 2026 trong phụ lục PRD. Trình duyệt tự tính thực nhận và khoản hụt. Không có API nhận nội dung offer.
- **Class:** spine-hole

Chủ đã khóa: trình duyệt tính, server không nhận offer, bộ số lấy từ API để còn đổi khi quy định đổi. Phép tính thì chưa khóa. Cùng bộ số 2026, một trình duyệt dò ngược net ra gross, trình duyệt kia cộng thuế lên net. Một bên loại ngày remote khỏi tiền, bên kia nhân hệ số. Một bên hụt gồm phần công ty, bên kia chỉ phần người lao động. Ngưỡng 1% còn là giả định, nên một bên nói «gần ngang» ở 1%, bên kia ở bất kỳ chênh nào nhỏ. Danh ô bắt buộc là chỗ im của cả hai bản: EXPERIENCE chỉ nói «thiếu ô bắt buộc thì chưa gọi tên bên cao hơn».

## F10. Soi tin: khóa tra, tin trùng, lương bất thường

- **Severity:** cao
- **EXPERIENCE:** Component Patterns, Kết quả soi tin; State Patterns, Link có trong dữ liệu và Link không có; UJ-3. Link có trong dữ liệu thì luôn có số lần làm mới và hai ngày, cộng tin trùng nếu có, và lương bất thường hoặc câu «Chưa đủ mẫu để xét lương.». Tin trùng là tin đang mở khác, trùng kỹ năng, thành phố, cấp bậc và khoảng lương, không cần tên công ty. Lương bất thường chỉ khi ô mẫu đủ 30 tin và lương công khai không nằm trong khoảng ghi trên tin. Dưới ngưỡng thì không kết luận bất thường. Link không có thì «Chưa soi được tin này.», không có ô dán mô tả. Nội dung dán nhầm không được lưu.
- **Spine:** Capability map để Soi tin ở FastAPI đọc Supabase, Next vẽ. AD-9 không ghi server và không qua model. AD-4 có link gốc và `source_id`. Không buộc tra cứu bằng link gốc. Không định nghĩa tin trùng. Không định nghĩa ô mẫu dùng để xét lương của một tin khi người dùng không có hồ sơ phiên. Soi tin vào thẳng, không có ô email.
- **Class:** spine-hole

Ba chỗ lệch được mà vẫn đúng các AD hiện có. Tra cứu có thể khóa theo `source_id` (người dùng không có), theo link gốc đúng chuỗi, hoặc theo link đã cắt query. Cùng một link dán, một API trả ba số, API kia trả «Chưa soi được tin này.». EXPERIENCE cũng không định nghĩa cách chuẩn hóa URL; spine cần ít nhất buộc khóa là link gốc đã lưu, nếu không hai API chọn hai khóa. Tin trùng có thể so khớp một phần kỹ năng hoặc cả tập. Lương bất thường cần một ô mẫu. Không có vai trò trên dòng tin (F3) và không có hồ sơ phiên, ô đó có thể là thành phố × cấp, hoặc vai trò suy ra × thành phố × cấp. Hai ô cho hai kết luận khác nhau với cùng ngưỡng 30 của AD-6. Bộ đếm lần làm mới phụ thuộc F2.

## F11. Chủ hồ sơ phiên trước lúc lưu

- **Severity:** trung bình
- **EXPERIENCE:** Information Architecture; Component Patterns, Dấu đã có và Viên hồ sơ phiên. Hồ sơ phiên gồm thành phố, cấp bậc, vai trò mục tiêu và kỹ năng đã có, sống trên máy đến lúc lưu. Bản đồ, Học gì tiếp? và Lộ trình đọc cùng hồ sơ đó. Dấu «đã có» mất trong cùng phiên khi xóa kỹ năng. Lần đầu, chưa có hồ sơ, không có dấu. Chỗ sửa hồ sơ nằm trên Học gì tiếp? `[GIẢ ĐỊNH]`, Lộ trình dùng lại cùng các ô, bản đồ chỉ đọc dấu.
- **Spine:** AD-8 có một câu «Hồ sơ trên trình duyệt cho đến lúc lưu.» Không nói hồ sơ đó là một kho dùng chung cho năm bề mặt, còn sau khi tải lại trang.
- **Class:** spine-hole

Sau lúc lưu, lỗ lớn hơn nằm ở F8. Trước lúc lưu, «trên máy» có thể thành state trong bộ nhớ của một route. Sang Bản đồ hoặc tải lại thì mất dấu «đã có», trong khi EXPERIENCE giữ dấu đến lúc lưu. Một người dùng localStorage, người kia dùng state theo trang. Đây là chủ lưu, không phải câu chữ màn.

---

## Story-detail

Những mục dưới EXPERIENCE đã nói đủ để một người vẽ màn làm theo. Spine im là đúng tầm initiative, miễn là không đụng các lỗ F1–F11.

### S1. Câu chữ lỗi và trạng thái đã có câu

- **Severity:** thấp
- **EXPERIENCE:** Voice and Tone và State Patterns đã khóa «Chưa đủ mẫu.», «Không tải được dữ liệu thị trường.», «Không có tin nào khớp bộ lọc.», «Chưa lưu được. Lộ trình vẫn còn trên máy này.», «Chưa có lộ trình cho email này.», «Chưa soi được tin này.», «Đã lưu. Liên kết mở lại đã gửi.». Liên kết không trả lộ trình dùng lại câu «Không tải được dữ liệu thị trường.». Lỗi nguồn giữ số lần xem gần nhất nếu máy còn. Đang mở liên kết thì giữ lộ trình vừa lưu trên máy đó trong lúc chờ.
- **Spine:** Convention đã trỏ lỗi API vào đúng các câu trong EXPERIENCE. Không nhắc cache lần xem gần nhất.
- **Class:** story-detail

Cache nằm trong một client Next. EXPERIENCE đã nói giữ số nào. Không có hai chủ.

### S2. Đi trên màn, focus, chuyển động, xếp responsive

- **Severity:** thấp
- **EXPERIENCE:** Component Patterns và Interaction Primitives, Accessibility Floor, Responsive. Lớp chào một lần mỗi máy, nút «Đã hiểu». Escape, focus, vùng bấm 44px, giảm chuyển động, thứ tự Tab, toast, thao tác kéo bản đồ 3D, năm mục, dưới 720px thì một cột.
- **Spine:** Không ghi các quy tắc này.
- **Class:** story-detail

### S3. Thứ tự bốn cảnh và câu kết quả offer

- **Severity:** thấp
- **EXPERIENCE:** Key Flows UJ-1 đến UJ-4. Thứ tự bước của Lan, Khoa, Mai. Câu kết quả offer gọi tên công ty đã nhập và có câu ước tính. Chân trang có thêm câu «Lương công khai ẩn khi dưới 30 tin.» `[GIẢ ĐỊNH]`.
- **Spine:** Không kể lại các cảnh. AD-9 đã giao chủ tính tiền. Ngày làm mới ở chân trang thuộc F2, không thuộc mục này.
- **Class:** story-detail

Phép tính để ra «bên nào cao hơn» thuộc F9. Câu chữ sau khi đã có hai số thì thuộc mục này.

### S4. Những thứ kỳ này không có trên màn

- **Severity:** thấp
- **EXPERIENCE:** không ô dán mô tả, không theo dõi tin, không báo cáo cộng đồng, không chỗ trả tiền, không liên kết khóa học, không mục điều hướng thứ sáu, không hồ sơ công khai, không từ chối quyền.
- **Spine:** AD-7 không mạng năm agent. AD-8 không mật khẩu. AD-9 không ghi offer và Soi tin. AD-13 không báo nguồn. Các mục còn lại không cần một AD mới để khỏi hiện nút.
- **Class:** story-detail

---

## Việc spine nên khóa, theo mức

Ưu tiên khi sửa spine, không sửa trong lần đối chiếu này:

1. F1 — khoảng dự báo trước tuần 1 là mâu thuẫn trực tiếp với thẻ thành phố và tầm nhìn.
2. F2 và F3 — không có vai trò, không có định nghĩa đang mở, không có số lần thấy, thì bản đồ, Học gì tiếp? và Soi tin không ra cùng một số.
3. F4 — vị từ tin đủ điều kiện, thứ tự nới, và lương của phạm vi đã nới.
4. F8 — response mở token phải dựng lại hồ sơ phiên, và lần mở trong 14 ngày là một sự kiện trên server.
5. F9 — các cạnh phép tính offer. F6 đứng cạnh đó: câu mẫu lúc model hỏng phải cùng khung ba chặng với lúc model chạy.
