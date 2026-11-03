---
title: "Đối chiếu PRD ↔ ARCHITECTURE-SPINE"
type: reconcile
input: '_bmad-output/planning-artifacts/prds/prd-HaiDoIT-2026-11-02/prd.md (996 dòng, 47 FR) + addendum.md'
derived: '_bmad-output/planning-artifacts/architecture/architecture-HaiDoIT-2026-11-03/ARCHITECTURE-SPINE.md'
created: 2026-11-03
---

# Đối chiếu PRD ↔ ARCHITECTURE-SPINE

## 0. Cách đọc tài liệu này

Spine là tài liệu ngắn, cố ý chỉ giữ bất biến. Bản đối chiếu này **không** tính là lỗi khi spine
không nhắc lại một yêu cầu của PRD. Nó chỉ tìm những chỗ mà một yêu cầu của PRD **đặt ra một ràng
buộc kiến trúc thật** — tức là nếu không viết ra, hai người làm hai phần khác nhau sẽ làm khác nhau,
hoặc sẽ làm sai — mà spine không có AD, không có convention, không có dòng Deferred, và không có
Câu hỏi mở nào chạm tới.

Ba mức đánh giá:

- **đã bọc** — có AD, convention, Deferred hoặc Câu hỏi mở chạm đúng ràng buộc.
- **không cần bọc** — yêu cầu nằm trọn trong một màn hình hoặc một hàm, không có nguy cơ hai bản cài đặt.
- **RƠI** — có ràng buộc kiến trúc thật, không chỗ nào trong spine chạm tới. Khi chỉ một phần của FR
  bị rơi thì ghi **RƠI (một phần)** kèm đúng phần bị rơi.

**Kết luận chung.** Spine đứng vững về xương sống: paradigm pipes-and-filters + read-model đúng là
cái trả lời cho ba lời hứa trung tâm của PRD (tất định, truy vết, chạy trên snapshot cũ), và
AD-2/AD-3/AD-4/AD-5/AD-6/AD-7/AD-8/AD-10 bọc gọn phần khó nhất của §3 và §5. Nhưng nó rơi **một
nhóm có hệ thống**: (a) mọi ràng buộc liên quan tới **rủi ro pháp lý R1–R4 và nghĩa vụ gỡ dữ liệu**
— nhóm này không xuất hiện một lần nào trong spine; (b) **bộ phân loại và bộ so khớp tin** — cùng
một lý lẽ đã sinh ra AD-2 nhưng không được áp cho hai bộ máy còn lại; (c) toàn bộ nhóm **ràng buộc
câu chữ và thiết bị**. Thêm vào đó có bốn mâu thuẫn trực tiếp, trong đó một mâu thuẫn nằm ngay bên
trong spine (AD-1 ↔ sơ đồ triển khai) và một mâu thuẫn làm hỏng chính trang chủ (AD-17 ↔ FR-33).

---

## 1. Bảng đi hết FR-1 → FR-47

| FR | Ràng buộc kiến trúc mà FR đặt ra | Spine chạm ở đâu | Đánh giá |
|---|---|---|---|
| FR-1 | Công tắc bật/tắt theo nguồn, đổi không sửa code; nhật ký từng lượt chạy theo nguồn; một nguồn lỗi không làm dừng nguồn khác; báo động | AD-10 (công tắc là dữ liệu có phiên bản), AD-15, AD-16, ER `SOURCE`–`PIPELINE_RUN` "theo từng nguồn", Deferred "Báo động qua Telegram" | đã bọc |
| FR-2 | Quy tắc lịch sự khi thu thập: đọc `robots.txt`, User-Agent trung thực có liên hệ, giãn cách cố định theo nguồn, không đăng nhập, **dừng nguồn ngay khi 403/429/captcha** và không thử lại tới lượt sau | Không có. AD-16 chỉ nói crawler "giữ nguyên giao diện hiện tại"; AD-10 bọc công tắc nhưng không bọc cổng lịch sự | **RƠI** |
| FR-3 | Snapshot mỗi lượt chạy thành công; vòng đời tin; "biến mất" = vắng ≥ 3 lượt chạy thành công **của chính nguồn đó**; đêm lỗi không làm tăng số lần đăng lại | AD-4, AD-15 (một snapshot = một daily partition), AD-16, ER `SOURCE`–`PIPELINE_RUN`, Convention khóa `snapshot_id` | đã bọc |
| FR-4 | Ghép trùng hai tầng, gom thành cụm chứ không xóa, mọi thống kê tính mỗi cụm một lần | AD-16, ER `JOB_RAW`–`JOB_CLUSTER`–`JOB`, bước `dedupe` trong dòng dữ liệu | đã bọc (nhưng xem FR-32: phép so khớp này phải dùng lại được lúc chạy) |
| FR-5 | **Xóa tên/email/điện thoại/Zalo của người đăng tin ngay khi đọc tin và trước khi lưu**; không bản ghi nào trong kho khớp mẫu email hoặc số điện thoại VN; ghi nhật ký chỉ loại thông tin | Không có. Dòng dữ liệu đi `crawl → ingest vào job_raw` không có bước làm sạch. AD-11 chỉ bọc **nội dung người dùng** (CV/JD), không bọc PII trong tin tuyển dụng | **RƠI** |
| FR-6 | Trích kỹ năng → mã trong bộ từ vựng; bộ từ vựng song ngữ; danh sách chờ kèm tần suất; lưu phiên bản model + prompt; **cùng lượt xử lý trích luôn số năm kinh nghiệm (min, max)** | AD-2, AD-3, AD-9, Convention mã kỹ năng + bí danh tiếng Việt, `haido_core/vocab/` | **RƠI (một phần)** — phần số năm kinh nghiệm bị AD-3 loại ra; xem Mâu thuẫn M3 |
| FR-7 | Gán vai trò/nhánh/cấp bậc/thành phố; nhánh chỉ tồn tại từ 30 tin; tách Data/AI và Embedded; **tin ngoài IT bị gắn nhãn và loại khỏi mọi bảng tổng hợp** | AD-2 (có ghi FR-7 trong Binds), bước `classify`, Convention enum vai trò/nhánh/cấp bậc, Câu hỏi mở 5 | **RƠI (một phần)** — AD-2 chỉ bọc "bộ máy kỹ năng"; không AD nào nói bộ **phân loại** cũng chỉ có một bản cài đặt, dùng chung với FR-26/FR-27. Bất biến "tin ngoài IT không bao giờ vào `stat_*`" cũng chỉ ngầm theo thứ tự bước |
| FR-8 | Lương quy về VND/tháng gross; tỷ giá USD cấu hình được | AD-10, Convention "Tiền: số nguyên, VND/tháng, gross", Câu hỏi mở 4 | đã bọc |
| FR-9 | Tính lại tỷ lệ và nhóm kỹ năng sau mỗi snapshot; θ_core/θ_common là tham số; bootstrap B = 1.000 cho CI 95% khi 30 ≤ n < 100, lưu cùng giá trị phân vị | AD-4, AD-5, AD-10, bước `aggregate`, ER `STAT_PERCENTILE` "mốc và CI", Stack SciPy, Câu hỏi mở 3 và 5 | đã bọc |
| FR-10 | Tải CV PDF/DOCX ≤ 5 MB sau khi tích đồng ý; không lưu file gốc; hiện từng bước đang chạy | AD-11 ("xử lý trong bộ nhớ, không chạm đĩa"), Capability map 4.2 | đã bọc — nhẹ: trần 5 MB chặn ở reverse proxy (addendum) chưa thành convention của Caddy |
| FR-11 | Văn bản < 30 ký tự có nghĩa ⇒ báo lỗi **trong 1 giây**; v1 không OCR | Deferred "OCR cho CV ảnh scan — FR-11 đã có ba đường thoát" | đã bọc — xem Yêu cầu lặng L6 (phải parse cục bộ **trước** khi gọi LLM mới đạt 1 giây) |
| FR-12 | Trích kỹ năng từ CV theo cùng bộ từ vựng FR-6; cùng CV cho cùng tập kỹ năng; nằm trong ngân sách 15 giây | AD-2, AD-3, AD-9, AD-11, Capability map 4.2 | đã bọc — ngân sách 15 giây: xem L5 |
| FR-13 | Tự chọn kỹ năng; hồ sơ tự chọn và hồ sơ từ CV được xử lý **giống hệt nhau** | AD-2, AD-7 (API nhận hồ sơ kỹ năng, không quan tâm nguồn gốc) | đã bọc |
| FR-14 | Hồ sơ + vai trò mục tiêu lưu trong trình duyệt; nút "Xóa hồ sơ" xóa sạch, gồm cả mã phiên ẩn danh | AD-11, Convention "Xác thực: không tài khoản, không session phía server", Capability map 4.2 (`localStorage`) | đã bọc |
| FR-15 | Link chứa vai trò + mã kỹ năng, không chứa gì khác; link **không** gắn snapshot cố định ⇒ mở ngày khác thì tính lại | AD-4, Convention "Link chia sẻ: `?role=&level=&have=`" | đã bọc |
| FR-16 | Tải về bản tóm tắt 2 phần; **bản tóm tắt ghi rõ vai trò mục tiêu, cỡ mẫu và ngày dữ liệu** (và theo §5, cả lưu ý về độ phủ dữ liệu) | Không có. AD-17 chỉ bọc envelope `{data, meta}` của **response API**; file tải về là chỗ thứ hai mà `meta` có thể rơi, và spine không nói nó sinh ở `web/` hay `haido_api/` | **RƠI** |
| FR-17 | Sinh mã phiên ẩn danh ở trình duyệt; sự kiện **chỉ** chứa mã phiên, loại thao tác, mã kỹ năng, vai trò mục tiêu; không bao giờ chứa nội dung CV/JD | AD-11 (có kiểm thử chặn), ER `ANON_EVENT`, Convention "Đột biến trạng thái", Convention ghi log | đã bọc — nhưng xem Mâu thuẫn M4 (`is_eval` của AD-18 là trường thứ năm) |
| FR-18 | Chọn vai trò/nhánh/cấp bậc, mặc định Intern/Fresher/Junior; **vai trò chưa có đồ thị học trước ⇒ không vẽ đồ thị, hiện danh sách theo nhóm + dòng thông báo**; đổi vai trò/cấp bậc tính lại không tải lại trang | Chỉ chạm gián tiếp: AD-12 đòi mỗi cạnh có biên bản rà soát (FR-22 nói vai trò chỉ được bật sau khi có biên bản). Không có cờ "vai trò đã bật / đã có đồ thị" trong hợp đồng API; `meta` của AD-17 không có trường này | **RƠI** — chế độ xuống hạng (không đồ thị) và cờ bật vai trò |
| FR-19 | Lộ trình chung từ bảng tổng hợp; ghi cỡ mẫu/nguồn/ngày; quay về theo thứ tự §3 kèm nhãn; không bao giờ đưa người chọn Fresher vào tập đa số Mid trừ bước cuối | AD-5, AD-6 (một hàm duy nhất, trả về cả ô và nhãn), AD-17 (`fallback_label`) | đã bọc |
| FR-20 | Kỹ năng đã có tô xanh và ra khỏi lộ trình; khoảng trống nổi bật; cập nhật hồ sơ ⇒ tính lại **trong 1 giây** | AD-5, AD-7 (Binds có nêu NFR "trong vòng 1 giây") | đã bọc — xem L5 về mâu thuẫn mềm giữa AD-7 và ngân sách 1 giây |
| FR-21 | Ba lựa chọn; lựa chọn phụ **chỉ có khi hồ sơ được tạo từ CV**; đổi lựa chọn được, lựa chọn sau cùng có hiệu lực; mỗi lựa chọn ghi một sự kiện | AD-11 (các trường của FR-17), Capability map 4.3 | **RƠI (một phần)** — hồ sơ kỹ năng phải mang **nguồn gốc từng kỹ năng** (CV / tự chọn) để bật-tắt lựa chọn phụ và để SM-9/SM-10 đo được. Không chỗ nào trong spine chứa nguồn gốc này; Convention link chia sẻ còn khẳng định URL "chỉ mã kỹ năng, không gì khác", nên sau khi mở link chia sẻ lựa chọn phụ phải tự tắt — điều này cần nói ra |
| FR-22 | Dựng tất định theo quy tắc 4 tầng; không kỹ năng nào đứng trước tổ tiên; **bước kiểm tra tự động: mọi kỹ năng cốt lõi/thường gặp phải có nút trong đồ thị, thiếu thì báo lỗi trước khi triển khai**; mỗi cạnh có nguồn + biên bản rà soát | AD-7, AD-8, AD-12 (`[ADOPTED]`), Stack NetworkX, cây mã nguồn `domain/` | đã bọc — nhẹ: θ và tỷ lệ đổi **mỗi đêm**, nên cổng kiểm tra "mọi kỹ năng cốt lõi đều có nút" phải chạy trong lượt chạy hằng đêm, không chỉ trước khi triển khai. Spine chưa nói nó sống ở đâu |
| FR-23 | Lời dẫn viết sẵn offline cho từng cặp kỹ năng × vai trò, có rà soát; **bấm nút không gọi LLM**; lời dẫn không chứa con số; mọi link lấy từ danh mục tài liệu | AD-8 (nêu đúng bước offline + kiểm thử chặn chữ số), ER `BLURB` và `RESOURCE`, §6.4 | đã bọc |
| FR-24 | Tô sáng kỹ năng trùng khi đổi vai trò + dòng tóm tắt | AD-7 (cho phép đúng hai phép ở frontend, trong đó có giao tập này) | đã bọc — riêng câu chữ "vai trò có kỹ năng gần", không dùng "lộ trình chuyển việc": xem L1 |
| FR-25 | Giao diện gọi nhóm thường gặp là "nên học sau khi đã nắm các kỹ năng cốt lõi"; **hệ thống không bao giờ khuyên "đừng học"**; kết quả kiểm chứng được là một phép kiểm trên **toàn bộ câu chữ giao diện và lời dẫn** | Không có. AD-8 có kiểm thử chặn **chữ số** trong văn bản LLM, nhưng không có nơi chứa câu chữ giao diện và không có kiểm thử từ ngữ bị cấm | **RƠI** |
| FR-26 | Dán 200–20.000 ký tự; trích theo bộ từ vựng; không lưu nội dung; **tin ngoài IT ⇒ báo và không tính mức khớp**; ghi sự kiện ẩn danh | AD-2, AD-3, AD-9, AD-11, Convention route POST | đã bọc, trừ phần "ngoài IT" — gộp vào RƠI của FR-7 |
| FR-27 | **Tự nhận diện vai trò (và nhánh) + cấp bậc của tin được dán**; đổi được, tính lại không dán lại; ghi cỡ mẫu; quay về như FR-19 | AD-5, AD-6, AD-17 bọc phần ô thống kê và nhãn. Phần **nhận diện** thì không: `domain/` liệt kê 9 nhóm hàm và không có phân loại vai trò/cấp bậc; AD-3 lại cấm cổng LLM trả về bất cứ thứ gì ngoài lượt nhắc nguyên văn | **RƠI** — phần nhận diện vai trò/cấp bậc lúc chạy |
| FR-28 | Mức khớp có trọng số 3/2/1; dòng đếm thô theo nhóm; kỹ năng chưa nhận diện không ảnh hưởng | AD-2, `domain/` ("mức khớp") | đã bọc |
| FR-29 | Phân nhóm kỹ năng của tin; kỹ năng chưa nhận diện hiện riêng và vào danh sách chờ | AD-2, AD-3 (danh sách chờ), ER `UNKNOWN_MENTION` | đã bọc |
| FR-30 | Ba thước đo phân vị; lương và số năm kinh nghiệm chỉ hiện khi **ô có ≥ 30 tin có trường đó**; nếu không thì ghi "chưa đủ dữ liệu (**X**/30 tin có lương)"; 30 ≤ n < 100 thì hiện kèm CI 95% | AD-5 (ngoại lệ đặt giá trị vào mốc đã tính sẵn), AD-6, AD-17 | **RƠI (một phần)** — ngưỡng của FR-30 đếm **số tin có trường đó**, không phải `n` của ô. `meta` của AD-17 chỉ có `n`, nên con số **X** để in "X/30 tin có lương" không có đường ra khỏi API |
| FR-31 | Bảy dấu hiệu D1–D7 với ngưỡng cấu hình; ghi chú bắt buộc "đa số tin bị gắn dấu hiệu vẫn là tin thật"; "không ghi lương" **không** là dấu hiệu; **không câu chữ nào dùng từ "lừa đảo", "tin giả", "tin ma"** | AD-2, AD-5, AD-8, AD-10 (ngưỡng D1–D7 là cấu hình), `domain/` ("dấu hiệu D1-D7") | **RƠI (một phần)** — ràng buộc từ ngữ bị cấm, và ghi chú bắt buộc kèm mọi dấu hiệu. D4 còn phụ thuộc FR-32 (đang RƠI) |
| FR-32 | Tìm trong dữ liệu đã thu thập một tin trùng với tin được dán, **dùng cùng cách so khớp như FR-4**; không tìm thấy ⇒ D4 "không đánh giá được" | Không có. FR-4 sống ở `haido_core/steps/` (bước `dedupe`), còn `domain/` không liệt kê phép so khớp tin. Không AD nào nói phép so khớp chỉ có một bản cài đặt dùng chung cho pipeline và API | **RƠI** |
| FR-33 | Chiều cao cột = tỷ trọng toàn quốc; **cột n < 30 không bị ẩn, vẫn vẽ theo tỷ trọng thật, trạng thái mờ + nhãn cỡ mẫu nhỏ**; Đà Nẵng luôn được vẽ; tổng tỷ trọng = 100% | AD-5, AD-17, Capability map 4.5 (deck.gl) | **MÂU THUẪN** với AD-17 — xem M1 |
| FR-34 | Bảng chi tiết: cơ cấu vai trò, kỹ năng hàng đầu, ngày snapshot; mọi số có cỡ mẫu; n < 30 ⇒ "chưa đủ dữ liệu" | AD-5, AD-6, AD-17 | đã bọc |
| FR-35 | Nút sang Cố vấn với vai trò chọn sẵn; nếu chưa có đồ thị thì hiện thông báo như FR-18 | Capability map 4.5 và 4.3 | không cần bọc — nhưng rơi cùng FR-18 ở phần cờ "vai trò đã có đồ thị" |
| FR-36 | Chú thích nguồn đang bật + ngày + ba lưu ý chuẩn, hiện trên **mọi** trạng thái kể cả điện thoại; **bắt buộc có chế độ 2D/bảng cùng số liệu, chuyển qua lại được, tự chuyển khi không chạy được WebGL, không hiện màn hình lỗi** | AD-17 (Binds có FR-36, `meta.sources[]`), Capability map 4.5 ghi "(deck.gl + chế độ bảng)" | **RƠI (một phần)** — chế độ 2D/bảng chỉ xuất hiện trong một ô bảng; việc **phát hiện WebGL và tự xuống hạng không màn hình lỗi** không có AD nào, dù đây là phương án dự phòng cho buổi demo |
| FR-37 | Năm loại thẻ; "Bậc thang Junior → Senior" cần so hai cấp bậc, "Khác biệt giữa các thành phố" cần ô thành phố × vai trò, "**Ngành** và nhà tuyển dụng nổi bật" cần phân loại ngành (Fintech, Banking) | AD-2, AD-5, AD-8, AD-12 ("đồng xuất hiện nằm ở bảng tổng hợp"), ER `INSIGHT_CARD` | **RƠI (một phần)** — không có thực thể, bước, enum hay dòng Deferred nào cho **taxonomy ngành**; và `stat_cells` khóa `(snapshot_id, role, branch, seniority, scope)` khiến chiều **thành phố** phải chui vào `scope` mà không nói rõ |
| FR-38 | Thẻ chỉ hiện khi mọi số tính trên n ≥ 30; thẻ so sánh cần chênh ≥ 5 điểm phần trăm (ngưỡng cấu hình); không thẻ nào đủ ⇒ "chưa đủ dữ liệu cho vai trò này" | AD-2, AD-5, AD-6, AD-10, AD-17 | đã bọc |
| FR-39 | Câu kết luận từ mẫu câu cố định, 2–3 biến thể theo khoảng giá trị; **không dùng LLM** | AD-8 ("Insights không gọi LLM") | đã bọc |
| FR-40 | Lọc thẻ theo vai trò; chọn sẵn theo vai trò đã lưu trong trình duyệt | Capability map 4.6 | không cần bọc |
| FR-41 | `?mode=eval` bật nhãn và đánh dấu mọi sự kiện trong phiên; dữ liệu thử nghiệm tách được khỏi dữ liệu thường | AD-18 (cờ `is_eval`, bảng `eval_*`) | đã bọc — nhưng cách bọc này tạo Mâu thuẫn M4 với FR-17 |
| FR-42 | Modal che toàn bộ nền **trước khi** người thử thấy bất kỳ con số nào; 3 kỹ năng lưu dạng mã; câu tự đánh giá 1–5; **ghi lại loại thiết bị** (theo FR-44) | AD-18, ER `EVAL_PRE_SESSION`, `eval_fixtures/` | **RƠI (một phần)** — trường loại thiết bị, và ràng buộc "chặn trước khi render số" (ảnh hưởng tới ISR/hydrate của `web/`) |
| FR-43 | Modal cuối phiên tự bật từ FR-15/FR-16; hỏi lại **nguyên văn** câu của FR-42; mỗi mã phiên chỉ gửi được một lần | AD-18 | đã bọc — nhẹ: "một lần một phiên" là một ràng buộc idempotency phía server, chưa thành convention |
| FR-44 | So sánh mù: hai phương án **không ghi nguồn**, thứ tự đảo ngẫu nhiên 50/50, **hệ thống lưu vị trí đã hiển thị**; dữ liệu tĩnh, không gọi API; trên điện thoại xếp dọc nhưng vẫn đảo và vẫn lưu vị trí | AD-18 (file JSON tĩnh có phiên bản, không gọi API lúc thử nghiệm) | **RƠI (một phần)** — việc đảo 50/50 và **lưu vị trí đã hiển thị** là điều kiện để SM-3 phân tích thiên lệch vị trí; không trường nào, không AD nào |
| FR-45 | Ẩn danh tuyệt đối, không ô liên hệ; nối mọi thứ bằng mã phiên; **một câu truy vấn duy nhất xuất được bảng kết quả** | AD-18 (hai bảng riêng cùng mã phiên), ER `EVAL_PRE_SESSION`–`EVAL_POST_SESSION` | đã bọc |
| FR-46 | Danh sách kiểm tra minh bạch, từng mục đạt/không đạt, **không gộp thành một điểm duy nhất**; có mục kiểm tra tính nhất quán chức danh × kỹ năng × cấp bậc | AD-5 (Binds có FR-46), `domain/` ("chất lượng JD") | đã bọc |
| FR-47 | Trang chính sách công khai; **kênh yêu cầu gỡ, xử lý trong 48 giờ, tin liên quan biến khỏi số liệu công khai từ snapshot kế tiếp**; trang không đăng chi tiết kỹ thuật thu thập hay R1–R4; **ràng buộc trung thực**: không khẳng định tuân thủ trái với R1–R4; không công bố toàn văn JD | AD-14 bọc đúng **một** vế: không render `description`, chỉ đọc bảng tổng hợp | **RƠI (một phần)** — (a) cơ chế gỡ: không có bảng chặn/danh sách gỡ, không bước nào áp nó trước `aggregate`, và AD-4 còn nói hàng của snapshot đã công bố "không bao giờ bị sửa hay xóa"; (b) ràng buộc trung thực của câu chữ trang công khai không có convention hay kiểm thử nào |

**Tổng kết bảng:** 47 FR → **28 đã bọc**, **2 không cần bọc**, **16 RƠI** (toàn phần hoặc một phần),
**1 mâu thuẫn trực tiếp** (FR-33).

- RƠI toàn phần: FR-2, FR-5, FR-16, FR-18, FR-25, FR-27, FR-32.
- RƠI một phần: FR-6, FR-7 (kéo theo FR-26), FR-21, FR-30, FR-31, FR-36, FR-37, FR-42, FR-44, FR-47.

---

## 2. Yêu cầu lặng — những ràng buộc không phải FR mà cấu trúc AD dễ làm rơi

### L1 — Không có nơi nào chứa câu chữ, và không có phép kiểm nào trên câu chữ

PRD ràng buộc câu chữ ở **năm** chỗ độc lập, và cả năm đều có "kết quả kiểm chứng được" dạng một
phép kiểm trên văn bản:

- FR-25: "Hệ thống **không bao giờ** khuyên 'đừng học' một kỹ năng nào" → "Không câu chữ nào trên
  giao diện hay trong lời dẫn chứa lời khuyên bỏ qua một kỹ năng."
- FR-31: "Không câu chữ nào dùng các từ **'lừa đảo', 'tin giả' hay 'tin ma'**."
- FR-31: ghi chú bắt buộc ngay dưới các dấu hiệu: "Dấu hiệu là gợi ý để bạn tự kiểm tra. Đa số tin
  bị gắn dấu hiệu vẫn là tin thật."
- FR-24: dùng cách nói "vai trò có kỹ năng gần", **không** dùng "lộ trình chuyển việc".
- FR-47: trang công khai **không được khẳng định** những điều trái với R1–R4, ví dụ "tuân thủ đầy đủ
  điều khoản của mọi nguồn".

Spine có đúng một phép kiểm trên văn bản — AD-8 chặn chữ số trong văn bản do LLM sinh — và đúng một
convention về chuỗi hiển thị, nhưng chỉ cho vai trò/nhánh/cấp bậc/thành phố ("Chuỗi hiển thị tiếng
Việt tra từ bảng, không viết trong code"). Câu chữ của giao diện, của nhãn dấu hiệu, của trang chính
sách thì nằm rải trong JSX và trong `BLURB`. Không bất biến nào bắt chúng đi qua một chỗ kiểm được.

Hệ quả: năm kết quả kiểm chứng được ở trên không có cách nào thành kiểm thử tự động, trong khi
Convention "Tên kiểm thử" của spine lại đòi kiểm thử mang mã FR. Đây là một khoảng trống có hệ thống,
không phải năm chi tiết lẻ.

### L2 — Yêu cầu thiết bị (§5 và FR-36) chỉ còn là một ô trong bảng

§5 "Thiết bị" đặt năm ràng buộc: Soi tin đầy đủ trên điện thoại; Cố vấn hiển thị dạng thẻ **gồm cả
ba lựa chọn của FR-21**; Bản đồ thành danh sách thành phố kèm thanh tỷ trọng; Insights xếp dọc, một
thẻ một hàng; **chế độ thử nghiệm FR-41 → FR-45 chạy đầy đủ**. FR-44 còn ghi rõ lý do: "Khoảng 40%
người thử có thể dùng điện thoại, nên FR-21 và FR-42 đến FR-44 phải chạy đầy đủ trên điện thoại."
FR-36 thêm: **bắt buộc** có chế độ 2D/bảng, tự chuyển khi không chạy được WebGL, **không hiện màn
hình lỗi**.

Spine chạm vào đúng hai chỗ: một nhãn trong sơ đồ triển khai ("người dùng — máy tính hoặc điện
thoại") và một ngoặc đơn trong bảng Capability ("deck.gl + chế độ bảng"). Không AD, không convention,
không Deferred. Mà đây là ràng buộc kiến trúc thật: nó quyết định bản đồ phải có **hai** bộ đọc cùng
một dữ liệu (deck.gl và bảng), và quyết định chế độ thử nghiệm không được dựa vào bất cứ thứ gì chỉ
có trên máy tính — đúng mẫu lỗi mà SM-1 → SM-3 sẽ hứng nếu 40% người thử bị kẹt.

### L3 — Lưu ý về độ phủ dữ liệu phải có mặt ở chỗ `meta` không với tới

§5 "Trung thực của con số": "**Mọi màn hình có số liệu** (Bản đồ nhu cầu, Insights, Cố vấn, Soi tin)
**và bản tóm tắt tải về** đều có lưu ý về độ phủ dữ liệu", gồm "dữ liệu chỉ gồm tin tuyển dụng IT
đăng online trên N nguồn" cộng ba lưu ý chuẩn của FR-36.

AD-17 bọc rất tốt vế đầu cho API: `meta` có `sources[]`, `snapshot_date`, `n`. Nhưng `meta` **không**
có ba lưu ý chuẩn, và **bản tóm tắt tải về (FR-16) không đi qua AD-17 chút nào**. Đó là hai chỗ mà
lời hứa trung tâm của sản phẩm có thể rơi mà hệ thống vẫn chạy bình thường — đúng loại hỏng mà AD-17
nói nó muốn chặn.

### L4 — Ngôn ngữ giao diện: tên hiển thị của kỹ năng không có chỗ ở

§5 "Ngôn ngữ": "Giao diện tiếng Việt. **Tên kỹ năng giữ nguyên dạng chuẩn tiếng Anh**, ví dụ Docker,
Spring Boot."

Convention của spine nói mã kỹ năng là `kebab-case, chỉ ASCII, không dấu`, là khóa chính, và "Bí danh
(gồm bí danh tiếng Việt) nằm ở bảng riêng". ER có `SKILL_ALIAS`. Nhưng không có trường **tên hiển thị
chuẩn**: từ `spring-boot` không có đường nào ra "Spring Boot" ngoài việc đoán trong frontend — và
đoán sẽ ra "Spring Boot" nhưng cũng sẽ ra "Ci Cd", "Mysql", "Postgresql", "Nextjs". Convention cho
vai trò/nhánh/cấp bậc/thành phố thì đã có ("tra từ bảng"); kỹ năng — thứ xuất hiện dày nhất trên
giao diện — thì không.

### L5 — Hai ngân sách hiệu năng: 15 giây có một nửa, 1 giây có một mâu thuẫn mềm

**15 giây** (FR-12, FR-26, §5, SM-4) xuất hiện trong spine đúng một lần, ở **Câu hỏi mở số 2** (vùng
đặt VPS). Không AD nào bọc nó: không ràng buộc timeout cho cổng LLM, không hành vi khi Claude API
chậm hoặc lỗi lúc người dùng đang chờ, trong khi Stack chọn `claude-sonnet-5-5` (model lớn hơn model
của lô hằng đêm) cho đúng hai đường đi đồng bộ này. Đây là ngân sách duy nhất mà PRD gắn trực tiếp
vào một chỉ số thành công (SM-4), nên để nó ở mục Câu hỏi mở là nhẹ hơn mức nó đáng.

**1 giây** (FR-20, §5) thì AD-7 có nêu trong Binds, nhưng AD-7 lại là lý do ngân sách này khó: AD-7
cấm frontend sắp xếp, nên **mỗi** lần bấm FR-21, **mỗi** lần đổi vai trò hoặc cấp bậc đều là một
vòng mạng tới VPS. Spine không nói gì về caching, prefetch, hay việc một lượt bấm FR-21 có thể tính
lại ở client từ kết quả đã có. AD-7 vẫn là quyết định đúng, nhưng nó đang gánh một ngân sách mà nó
không nói cách đạt, và Câu hỏi mở số 2 chỉ nhắc 15 giây, không nhắc 1 giây.

### L6 — Thứ tự "parse cục bộ trước, gọi LLM sau" (FR-11)

FR-11 đòi thông báo lỗi CV ảnh scan xuất hiện **trong vòng 1 giây** kể từ lúc tải lên. Điều đó buộc
việc rút văn bản và đếm 30 ký tự có nghĩa phải chạy **trước** khi gọi cổng LLM của AD-9 — nếu không,
người dùng chờ cả vòng LLM rồi mới nhận lỗi. Spine mô tả cổng trích xuất nhưng không nói đường đi
của endpoint CV có hai chặng. Nhỏ, nhưng là một thứ tự dễ làm sai và sẽ sai âm thầm.

### L7 — `stat_cells.scope` chưa được định nghĩa, mà §3 có hai họ ô thống kê khác nhau

§3 định nghĩa **hai** loại ô: Cố vấn/Soi tin dùng *vai trò × cấp bậc, toàn quốc*; Bản đồ/Insights
dùng *thành phố × vai trò*. Và chỉ họ thứ nhất có chuỗi quay về. AD-6 cho `stat_cells` khóa
`(snapshot_id, role, branch, seniority, scope)` — chiều **thành phố** phải nằm trong `scope`, nhưng
spine không nói, và cũng không nói rằng hàm chọn ô duy nhất của AD-6 chỉ áp chuỗi quay về cho họ thứ
nhất. Thêm nữa §3 còn một bộ lọc dễ rơi: "Chỉ tính những tin có ngày thấy lần cuối trong vòng **60
ngày** tính tới snapshot đang dùng" — con số 60 ngày không xuất hiện ở đâu trong spine, kể cả trong
AD-10, nơi lẽ ra nó là một tham số cấu hình có phiên bản.

---

## 3. Mâu thuẫn — chỗ spine nói khác PRD

### M1 — AD-17 làm trang chủ không vẽ được (nặng)

- **Spine, AD-17:** "Khi `n < 30`: `data` phải là `null` và `meta.insufficient_data = true` — không
  bao giờ là một con số đoán."
- **PRD, FR-33:** "**Cột có n < 30:** cột không bị ẩn, mà vẫn vẽ theo **tỷ trọng thật**, ở trạng thái
  mờ, kèm nhãn 'Cỡ mẫu nhỏ (n = X < 30): số liệu chỉ để tham khảo'." Và: "Cột Đà Nẵng **luôn** được
  vẽ." Và kết quả kiểm chứng được: "Khi chọn một vai trò, tổng tỷ trọng của các cột cộng với phần
  'Khác' và phần không xác định thành phố bằng **100%**."

Hai câu này loại trừ nhau. Nếu API trả `null` cho mọi ô n < 30 thì Đà Nẵng (64 tin, phần lớn ô dưới
ngưỡng theo FR-37) không vẽ được, nhãn "n = X" không in được vì không có X, và tổng tỷ trọng không
thể bằng 100%. Addendum của PRD còn ghi rõ lý do đã **loại** phương án ẩn cột: "Thành phố ít tin
trông như 'thánh địa'; phải ẩn cột Đà Nẵng."

Điều PRD thực sự phân biệt là: **tỷ trọng** (một tỷ lệ cấu phần, vẫn hiển thị khi mẫu nhỏ, kèm nhãn
mờ) khác **tỷ lệ xuất hiện của kỹ năng và phân vị** (chặn dưới ngưỡng — FR-34 và §5). AD-17 đang gộp
cả hai vào một quy tắc. Cần sửa AD-17 để nêu rõ ngoại lệ này, kèm `meta.small_sample = true` thay vì
`data = null`.

### M2 — Spine tự mâu thuẫn: `web/` có biết Postgres hay không? (nặng)

- **Spine, bảng bốn tầng:** `web/` — "Biết hợp đồng HTTP của `haido_api`; **không biết Postgres**".
- **Spine, AD-1** (Binds: *tất cả*; "Một `import` đi ngược chiều là lỗi, **có kiểm thử chặn**"): sơ
  đồ chỉ có `web --> api`. Không có cạnh `web --> pg`.
- **Spine, Triển khai và môi trường:** sơ đồ có `web --> pg`, và phần chữ ngay sau: "`web` đọc
  Postgres **chỉ** lúc sinh trang nội dung công khai (AD-14)".

Một trong hai phải nhường. Đây không phải lỗi biên tập: nó quyết định `web/` có cần driver Postgres,
chuỗi kết nối và quyền trên cơ sở dữ liệu hay không — tức là quyết định bề mặt tấn công của một tiến
trình chạy công khai, và quyết định kiểm thử chặn import của AD-1 bắt hay không bắt. Cách giải rẻ
nhất và giữ được AD-1: trang công khai cũng đọc qua `haido_api` lúc build/revalidate. Cách còn lại:
viết thẳng một ngoại lệ vào AD-1 và nói rõ `web/` dùng một kết nối chỉ-đọc riêng.

### M3 — AD-3 loại bỏ hai thứ FR-6 và FR-27 bắt buộc phải có (nặng)

- **Spine, AD-3:** "cổng LLM **chỉ** trả về các lượt nhắc nguyên văn trích từ văn bản."
- **PRD, FR-6:** "Trong cùng lượt xử lý đó, hệ thống trích luôn **số năm kinh nghiệm yêu cầu** (tối
  thiểu, tối đa) nếu tin có nêu." (Và: "Tin ghi '2–3 năm kinh nghiệm' được lưu thành tối thiểu 2,
  tối đa 3.")
- **PRD, FR-27:** "Hệ thống **tự nhận diện vai trò** (và nhánh, nếu có) **cùng cấp bậc** của tin."

Số năm kinh nghiệm là một cặp số, không phải lượt nhắc kỹ năng; vai trò và cấp bậc là một nhãn phân
loại, không phải lượt nhắc. Theo đúng chữ của AD-3, cả hai đều không được đi qua cổng LLM — nhưng
spine cũng không đặt chúng ở đâu khác: `domain/` liệt kê 9 nhóm hàm và không có phân loại; bước
`classify` tồn tại trong dòng dữ liệu hằng đêm nhưng không có bản dùng được lúc chạy cho FR-27.

Đây là phần chìm của một khoảng trống lớn hơn: **AD-2 nói "một bộ máy kỹ năng duy nhất" nhưng không
có AD tương ứng cho hai bộ máy còn lại cũng được dùng ở cả hai phía** — bộ **phân loại** (FR-7 hằng
đêm ↔ FR-26/FR-27 lúc chạy) và bộ **so khớp tin** (FR-4 hằng đêm ↔ FR-32 lúc chạy). Lý lẽ "Prevents"
của AD-2 ("cùng một CV cho hai kết quả khác nhau tùy cửa vào") áp nguyên xi cho cả hai: nếu FR-27
nhận diện vai trò bằng một cách khác FR-7, thì ô thống kê người dùng được so vào không phải ô mà tin
của họ sẽ thuộc về nếu nó được thu thập.

### M4 — `is_eval` là trường thứ năm của một danh sách PRD đã đóng

- **Spine, AD-18:** "mọi sự kiện ẩn danh có cờ `is_eval`."
- **PRD, FR-17:** "Sự kiện **chỉ** chứa mã phiên ẩn danh, loại thao tác, mã kỹ năng và vai trò mục
  tiêu."
- **PRD, §5 Quyền riêng tư:** "Sự kiện ẩn danh **chỉ** chứa những trường đã liệt kê ở FR-17."

Cộng thêm FR-44, vốn đòi ghi **loại thiết bị** và **vị trí trái/phải đã hiển thị**. Về rủi ro riêng
tư thì ba trường này vô hại, nhưng chúng mâu thuẫn với một câu "chỉ" mà AD-11 của spine lại muốn
biến thành kiểm thử. Phải chọn: hoặc sửa FR-17 cho phép trường kỹ thuật, hoặc đặt `is_eval` và loại
thiết bị ở bảng `eval_*` bên cạnh, không đặt trên `anon_events`.

### M5 — AD-4 bất biến đối đầu với nghĩa vụ gỡ dữ liệu (nặng)

- **Spine, AD-4:** "Hàng thuộc snapshot đã công bố **không bao giờ** bị sửa hay xóa."
- **PRD, FR-47:** "cam kết xử lý mọi yêu cầu gỡ trong **48 giờ**", và "Một yêu cầu gỡ hợp lệ được xử
  lý, và tin liên quan biến khỏi số liệu công khai **từ snapshot kế tiếp**."

Chữ "từ snapshot kế tiếp" của PRD cứu AD-4 trong trường hợp thường, và đó là một thiết kế đẹp. Nhưng
nó chỉ cứu được **một** loại yêu cầu. Hai loại còn lại thì không:

- **FR-5 / §6.2 (Luật 91/2025):** nếu một lượt chạy làm sót PII của người đăng tin vào `job_raw`,
  nghĩa vụ là xóa khỏi dữ liệu đang có, không phải "từ mai không thu nữa".
- **R3/R4 (§6.1):** 625 tin LinkedIn và 555 tin ITviec **đang được tính vào số liệu công khai** trong
  lúc chờ xin phép. §6.1 còn tính sẵn con số nếu phải loại ra: "số tin còn 2.289, trong đó Backend
  còn 184 tin và Java Backend còn 105 tin". Tức là PRD đã lường trước tình huống **phải loại một
  nguồn ra khỏi số liệu đã công bố**. Với AD-4 như đang viết, việc đó là dựng lại toàn bộ chuỗi
  snapshot — và spine không có bước nào, bảng nào hay dòng Deferred nào cho việc dựng lại.

Cần một van: ví dụ AD-4 giữ nguyên tính bất biến của *bảng tổng hợp*, cộng một bảng
`suppressions`/`takedowns` được áp ở bước `aggregate`, và một đường chạy lại có chủ đích cho các
snapshot cũ, có ghi lý do.

### M6 — Câu "ngoại lệ duy nhất" của AD-5 rộng hơn ý nó muốn nói (nhẹ)

AD-5: "**Ngoại lệ duy nhất** được phép tính lúc chạy: đặt một giá trị của tin người dùng dán vào các
mốc phân vị **đã tính sẵn**." Nhưng lúc chạy, API còn phải tính **mức khớp** (FR-28), **bảy dấu
hiệu** D1–D7 (FR-31), **chất lượng JD** (FR-46) và **lộ trình đã xếp thứ tự** (AD-7) — spine tự đặt
cả bốn vào `domain/`, và AD-7 còn nói rõ API trả về lộ trình đã xếp. Ý thật của AD-5 là "không chạy
phép **tổng hợp trên bảng tin**", và câu đầu của Rule đã nói đúng điều đó; chỉ chữ "ngoại lệ duy
nhất" là quá rộng. Sửa một dòng.

### M7 — Convention route cấm đúng những POST mà FR-42 → FR-45 cần (nhẹ)

- **Spine, Consistency Conventions:** "Chỉ `GET` cho dữ liệu thị trường; `POST` **chỉ** cho hai
  endpoint trích xuất phù du và cho sự kiện ẩn danh."
- **Spine, Consistency Conventions (dòng khác):** "`haido_api` chỉ ghi vào `anon_events` và hai bảng
  `eval_*`."

Hai dòng cách nhau mấy hàng trong cùng một bảng đã không khớp: ghi vào `eval_pre_session` và
`eval_post_session` (FR-42, FR-43, FR-44) cần POST, mà dòng route không cho phép. Thêm `POST` cho
hai endpoint eval vào danh sách là xong, nhưng phải viết ra.

---

## 4. Vượt phạm vi — spine thêm thứ PRD không có

Trang nội dung công khai (SEO/AEO/GEO) được loại khỏi mục này vì spine đã tự khai ở Câu hỏi mở số 1.
Ngoài nó:

| # | Spine thêm gì | PRD nói gì | Đánh giá |
|---|---|---|---|
| V1 | `web/` đọc trực tiếp Postgres (sơ đồ triển khai và phần chữ sau sơ đồ) | PRD không nói về tầng; nhưng spine tự nói ngược lại ở AD-1 và ở bảng bốn tầng | **Cần quyết** — xem M2. Đây là một cạnh phụ thuộc mới ở runtime, không phải chi tiết triển khai |
| V2 | `is_eval` trên **mọi** sự kiện ẩn danh (AD-18) | FR-17 và §5 đóng danh sách trường | **Cần quyết** — xem M4 |
| V3 | `level` trong link chia sẻ: `?role=&level=&have=` | FR-15 chỉ nói "vai trò mục tiêu và danh sách mã kỹ năng" | Chấp nhận được, thậm chí cần: kết quả kiểm chứng được của FR-15 ("hiển thị đúng lộ trình học như trên máy gốc") không đạt nếu thiếu cấp bậc. Nên ghi lại là một mở rộng có ý thức |
| V4 | Chốt hai model khác nhau: `claude-haiku-5-5` cho lô hằng đêm, `claude-sonnet-5-5` lúc người dùng dán | §6.4 chỉ nói "chuyển bước trích xuất sang mô hình nhỏ, **nhưng chỉ sau khi đã đo** trên bộ chuẩn 200 JD" | Hợp lệ (chọn công nghệ là việc của kiến trúc), Deferred đã nêu điều kiện đổi. Nhưng chú ý: spine dùng **hai** model cho **hai** đường trích xuất, nên SM-6 đo trên bộ 200 JD (đường lô) **không** nói gì về chất lượng của đường người dùng dán (FR-12, FR-26, SM-10). PRD cũng không lường trường hợp này |
| V5 | "Hai môi trường, không có staging" | PRD không nói | Hợp lệ với 3 người / 8 tuần |
| V6 | AD-9: "v1 **chỉ** dùng Claude; không có nhà cung cấp thứ hai" | FR-10 chỉ đòi ô đồng ý **ghi rõ tên nhà cung cấp** | Hợp lệ, và còn giúp FR-10 viết được câu đồng ý cụ thể |

Không mục nào trong spine bị PRD cấm thẳng. Nhóm vượt phạm vi thật chỉ gồm V1 và V2, và cả hai đã
nằm trong danh sách mâu thuẫn.

---

## 5. Rủi ro R1–R4 và pháp lý §6.2

### Trạng thái: để trống gần như hoàn toàn

Tìm cả spine: "R1", "R2", "R3", "R4", "né phát hiện bot", "Điều 289", "LinkedIn", "ITviec", "TopCV",
"robots.txt", "Luật 91/2025" — **không xuất hiện một lần nào**. §6.2 được nhắc đúng một lần, trong
Binds của AD-14, và AD-14 chỉ bọc một vế rất hẹp: trang công khai không render toàn văn JD.

Đây là khoảng trống nặng nhất của bản đối chiếu, vì §6.1 ghi rõ ba trong bốn rủi ro ở mức "**Rất
cao**", R1 "có thể rơi vào Điều 289 Bộ luật Hình sự", và R1 "Chạy cả trên **bản công khai**".

### Năm chỗ cụ thể cần một bất biến

1. **R1/R2 đang sống trong AD-16 mà AD-16 không biết.** AD-16 nói "mỗi crawler **giữ nguyên giao
   diện hiện tại**". Đúng về ranh giới kỹ thuật, nhưng hệ quả là kỹ thuật né phát hiện bot của
   crawler TopCV, ITviec, TopDev và của step-03 được bảo tồn nguyên vẹn vào bản công khai, mà không
   AD nào nói đó là một ngoại lệ đã chấp nhận, có điều kiện, và phải bỏ khi thương mại hóa (§6.1:
   "bỏ kỹ thuật này khi thương mại hóa"). Một người đọc spine mà không đọc §6.1 sẽ không biết mình
   đang bảo tồn cái gì.

2. **Độ mịn của công tắc không khớp với độ mịn của rủi ro.** AD-10 cho công tắc **theo từng nguồn**.
   Nhưng R2 nằm ở "**bước** lấy mô tả đầy đủ (step-03)" — một bước pipeline, không phải một nguồn.
   Muốn tắt R2 mà vẫn giữ nguồn thì cần công tắc **theo bước**, không có trong AD-10.

3. **FR-2 không có cổng, nên "trừ R1–R4" không có chỗ để trừ.** §6.1 nói "SM-C1 và FR-2 được hiểu là
   'trừ R1–R4'". Một ngoại lệ chỉ ghi được nếu có một quy tắc để trừ vào. Spine không có quy tắc đó
   (xem FR-2 RƠI), nên hiện tại ranh giới giữa "nguồn tuân thủ FR-2" và "nguồn thuộc R1–R4" không
   tồn tại ở đâu trong mã.

4. **R3/R4 cần nguồn gốc truy được tới từng tin, và cần một đường loại trừ.** `JOB_RAW.source` trong
   ER cho phép lọc theo nguồn, đó là điều kiện cần. Nhưng không bất biến nào nói rằng mọi bảng tổng
   hợp phải tính lại được **sau khi loại một nguồn**, và AD-4 lại cấm sửa snapshot đã công bố (M5).
   §6.1 đã tính sẵn kịch bản này (3.469 → 2.289 tin), nên nó là một yêu cầu, không phải một giả định.

5. **§6.2 có hai cột chống, spine chỉ đỡ một.** §6.2 nói: "CV chỉ được xử lý khi người dùng đồng ý
   (FR-10)" — AD-11 bọc rất chắc; "thông tin cá nhân của người đăng tin bị xóa ngay lúc thu thập
   (FR-5)" — **không bọc gì cả**. Cột thứ hai này là cột duy nhất bảo vệ hệ thống trước Luật 91/2025
   ở phía dữ liệu thu thập, vốn là phía có khối lượng lớn hơn phía CV rất nhiều.

### Đề xuất tối thiểu: hai AD mới

- **AD-19 — Cổng thu thập và danh sách ngoại lệ có tên.** Mọi request ra ngoài đi qua một cổng duy
  nhất trong `scraper/` hoặc `haido_core/steps/`: kiểm `robots.txt`, User-Agent cấu hình được có địa
  chỉ liên hệ của FR-47, giãn cách theo nguồn, và **dừng nguồn ngay khi 403/429/captcha**, ghi lý do
  dừng vào `pipeline_run`. Ngoại lệ chỉ tồn tại dưới dạng **dữ liệu có tên** (bảng cấu hình của
  AD-10, một hàng cho R1, một hàng cho R2), không bao giờ dưới dạng một nhánh `if` trong code. Công
  tắc có hai mức: theo nguồn **và** theo bước.
- **AD-20 — Làm sạch trước khi ghi, và loại trừ được sau khi ghi.** Không bản ghi nào vào `job_raw`
  trước khi đi qua hàm làm sạch PII trong `domain/` (FR-5), có kiểm thử quét mẫu email và số điện
  thoại VN trên toàn bảng. Mọi tin mang `source` và `takedown_status`; bước `aggregate` **luôn** đọc
  bảng `suppressions`; và có một lệnh CLI dựng lại bảng tổng hợp của một dải snapshot khi một nguồn
  hoặc một tin bị loại — kèm ghi lý do, vì đây là ngoại lệ duy nhất cho AD-4.

Đồng thời: AD-14 cần thêm vế thứ hai của FR-47 (ràng buộc trung thực của câu chữ trang công khai),
hoặc nhận một convention ở nhóm L1.

---

## 6. Việc cần làm, theo thứ tự

**Phải sửa trước khi chia epic**

1. **M2** — chốt `web/` ↔ Postgres. Một trong hai câu của spine phải đổi.
2. **M1** — sửa AD-17 để tỷ trọng của bản đồ (FR-33) không bị quy tắc `n < 30 ⇒ data = null` giết.
3. **M5 + §5 pháp lý** — thêm AD-19 và AD-20, và một van cho AD-4.
4. **FR-5** — bước làm sạch PII phải xuất hiện trong dòng dữ liệu một đêm.
5. **M3** — thêm một AD "một bộ phân loại duy nhất, một bộ so khớp tin duy nhất" (bọc FR-7/FR-26/
   FR-27 và FR-4/FR-32), và nới AD-3 cho số năm kinh nghiệm.

**Phải thêm trước khi viết story**

6. **L1** — một nơi chứa câu chữ, cộng kiểm thử từ ngữ bị cấm (FR-25, FR-31, FR-24, FR-47).
7. **FR-18** — cờ "vai trò đã có đồ thị" trong hợp đồng API, và chế độ danh sách khi chưa có.
8. **FR-30** — thêm mẫu số phụ (`n_salary`, `n_yoe`) vào `meta` của AD-17.
9. **L2** — một AD hoặc convention cho thiết bị: hai bộ đọc cho bản đồ, phát hiện WebGL, chế độ thử
   nghiệm đầy đủ trên điện thoại.
10. **FR-16 + L3** — nơi sinh bản tóm tắt tải về, và lưu ý độ phủ dữ liệu trên mọi màn hình có số.

**Sửa một dòng**

11. **M6** (câu "ngoại lệ duy nhất" của AD-5), **M7** (route POST cho eval), **L4** (tên hiển thị kỹ
    năng), **L7** (`scope` và bộ lọc 60 ngày), **FR-21** (nguồn gốc kỹ năng trong hồ sơ), **FR-37**
    (taxonomy ngành), **FR-44** (vị trí đã hiển thị + loại thiết bị), **FR-42** (chặn trước khi
    render số), **L5** (đưa 15 giây và 1 giây từ Câu hỏi mở thành ràng buộc).
