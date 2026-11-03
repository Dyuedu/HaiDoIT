---
title: 'Rà soát theo good-spine checklist — ARCHITECTURE-SPINE.md'
target: '_bmad-output/planning-artifacts/architecture/architecture-HaiDoIT-2026-11-03/ARCHITECTURE-SPINE.md'
baseline:
  - '_bmad-output/planning-artifacts/prds/prd-HaiDoIT-2026-11-02/prd.md'
  - '_bmad-output/planning-artifacts/prds/prd-HaiDoIT-2026-11-02/addendum.md'
  - '_bmad-output/planning-artifacts/briefs/brief-HaiDoIT-2026-11-02/addendum.md (tham chiếu kế hoạch 8 sprint)'
reviewer: 'rà soát độc lập theo lăng kính rubric'
date: '2026-11-03'
verdict: 'CHƯA ĐẠT ở dạng hiện tại — nền tảng tốt, cần một lượt sửa có mục tiêu trước khi chia epic'
---

# Rà soát theo good-spine checklist

## 0. Tóm tắt điều hành

**Verdict: CHƯA ĐẠT ở dạng hiện tại — nhưng không phải vì viết sai, mà vì thiếu.**

Đây là một spine ở trên mức trung bình rõ rệt. Nó có một paradigm được chọn **kèm lý do tại sao không chọn CRUD**, 18 AD mà phần lớn có mục `Prevents` nêu đúng một thất bại cụ thể thay vì một khẩu hiệu, một bảng convention sắc nét, một bảng Stack có ngày tra cứu và danh sách **đã loại** kèm lý do, và một mục Câu hỏi mở tự thừa nhận lỗ hổng lớn nhất của chính nó (trang SEO chưa có FR). Những thứ dễ phân kỳ nhất và đắt nhất khi phân kỳ — bộ máy kỹ năng dùng chung (AD-2), ranh giới LLM/tất định (AD-3, AD-8), tính bất biến của snapshot (AD-4), tầng đọc không tính (AD-5), thứ tự lộ trình chỉ ở Python (AD-7) — đều đã bị đóng đinh đúng chỗ.

Vấn đề nằm ở năm chỗ, và cả năm đều ảnh hưởng trực tiếp tới 3 dev làm song song trong 8 tuần:

1. **Không có cổng cưỡng chế.** Ít nhất 6 AD kết thúc bằng "có kiểm thử chặn" / "có kiểm thử hợp đồng chặn" (AD-1, AD-8, AD-11, AD-17, AD-12 ngầm, convention Tên kiểm thử). Nhưng spine **không nơi nào nói có một cổng CI chặn merge**, và mục Deferred còn chủ động hoãn "CI/CD nhiều tầng" với câu "`docker compose up -d` sau khi test xanh là đủ" — tức giả định một cổng test mà spine chưa dựng. Khi không có cổng, mọi Rule dạng "có kiểm thử chặn" tụt xuống thành nguyện vọng.
2. **AD-3 viết chữ "chỉ" quá chặt và vô tình chặn 4 tính năng.** Cổng LLM "**chỉ** trả về các lượt nhắc nguyên văn" làm cho FR-6 (số năm kinh nghiệm), FR-27 (vai trò + cấp bậc của tin dán), FR-31 D5–D7 (kênh liên hệ, đòi tiền trước, không rõ công ty) và FR-46 (chất lượng JD) không còn cửa nào để lấy dữ kiện ra khỏi văn bản.
3. **AD-17 mâu thuẫn thẳng với FR-33 và không đủ hình dạng cho FR-30/FR-34/FR-37.** AD-17 là AD duy nhất mà toàn bộ frontend tiêu thụ, nên sai ở đây là sai ở cả bốn tính năng đọc số.
4. **Phong bì vận hành thiếu hai mảng: sao lưu (hoàn toàn trắng, không có cả trong Deferred) và di trú schema (chỉ xuất hiện như một chữ "Alembic" trong cây mã nguồn).** Trên 1 VPS với ≥25 snapshot tích lũy (SM-5) và dữ liệu thử nghiệm 30–50 người (FR-45) không tái tạo được, đây là rủi ro mất bằng chứng đồ án, không chỉ rủi ro kỹ thuật.
5. **Toàn bộ hợp đồng trạng thái phía trình duyệt bị để trắng.** Ba dev đọc chung một "hồ sơ kỹ năng + vai trò mục tiêu" trong `localStorage` và ghi chung một bảng `anon_events`, nhưng spine không cố định khóa `localStorage`, hình dạng hồ sơ, hay **bộ mã loại thao tác** của sự kiện ẩn danh. Đây chính là chỗ FR-14, FR-17, FR-40, FR-45 và gần như toàn bộ chỉ số chính (SM-1, SM-2, SM-3, SM-9, SM-12) sẽ vỡ.

Đánh giá theo từng mục của checklist ở dưới. Tổng: **5 phát hiện critical, 12 high, 14 medium.** Không có mục nào trong checklist mà spine đạt trọn vẹn, nhưng mục 1 và mục 2 đạt phần lớn.

---

## 1. Spine có cố định đúng những điểm dễ phân kỳ cho tầng dưới không?

### 1.1 Những điểm phân kỳ đã được cố định tốt

Trước khi nói thiếu, cần ghi nhận: với một hệ 7 tính năng do 3 người làm song song, spine đã bắt đúng **những điểm phân kỳ có hậu quả không thể sửa muộn**:

| Điểm phân kỳ | AD | Đánh giá |
|---|---|---|
| Hai bản cài đặt của phép văn bản → mã kỹ năng → nhóm kỹ năng | AD-2 | Đúng điểm nguy hiểm nhất. Nếu để lệch, SM-6 và SM-8 mất nghĩa đúng như `Prevents` nói |
| Tầng đọc tự tính số thị trường | AD-5 | Đúng. Soi tin (dev B, sprint 4) và Insights (dev C, sprint 6) chắc chắn sẽ viết hai câu `GROUP BY` khác nhau nếu không có Rule này |
| Thứ tự quay về ô thống kê bị dựng lại hai lần | AD-6 | Đúng và rất cụ thể. Đây là chỗ Cố vấn và Soi tin gặp nhau ở hai sprint khác nhau |
| Cài lại quy tắc 4 tầng bằng TypeScript để đạt 1 giây | AD-7 | Đúng. Đây là phân kỳ *có động cơ* — dev frontend có lý do hợp lý để làm việc sai — nên việc nêu tên nó trước có giá trị cao |
| Snapshot nửa vời bị đọc; hai tính năng hiển thị hai đêm khác nhau | AD-4 | Đúng, và cơ chế (một transaction, chọn `published` mới nhất) đủ cụ thể để hai dev không hiểu khác nhau |
| Hai nguồn sự thật song song (JSONL vs Postgres) | AD-16 | Đúng, và đây là phân kỳ *kế thừa* — không nêu ra thì mặc định rơi vào trạng thái xấu |
| Bị khóa vào Dagster ở tuần 1 | AD-15 | Đúng, và là loại quyết định đáng giá nhất trong một dự án 8 tuần |
| Trộn cạnh `PREREQUISITE` với đồng xuất hiện | AD-12 | Đúng. Đây là phân kỳ dễ xảy ra vì "có trọng số" nghe hay hơn |

Mức độ cụ thể của mục `Prevents` cũng cao hơn thường thấy: AD-11 nêu đúng cơ chế thất bại thật ("một người thêm log request body để debug rồi vẫn qua review"), AD-3 nêu đúng cái giá ("thêm một bí danh mà phải gọi lại LLM cho toàn bộ tin lịch sử"). Đây là dấu hiệu spine được viết từ kinh nghiệm chứ không từ mẫu.

### 1.2 Những điểm phân kỳ **thật** bị bỏ sót

#### [CRITICAL-1] Hợp đồng trạng thái phía trình duyệt và bộ mã sự kiện ẩn danh

Ba dev cùng đọc và ghi hai thứ dùng chung mà spine không cố định:

**(a) `localStorage`.** FR-14 lưu hồ sơ kỹ năng + vai trò mục tiêu; FR-40 đọc vai trò mục tiêu để chọn sẵn bộ lọc Insights; Soi tin đọc hồ sơ để tính mức khớp (FR-28); FR-17 lưu mã phiên ẩn danh; FR-41 lưu cờ chế độ thử nghiệm. Addendum §1 FR-14 còn đòi "xóa hồ sơ là xóa **mọi** khóa của Hải Đồ IT trong `localStorage`, gồm cả mã phiên ẩn danh".

Spine cố định **hình dạng link chia sẻ** (convention "Link chia sẻ") nhưng không cố định hình dạng `localStorage`. Hậu quả rất cụ thể: dev A (Cố vấn, sprint 3) tạo `haido.profile`, dev B (Soi tin, sprint 4) tạo `skillProfile`, dev C (Insights, sprint 6) tạo `haidoit:targetRole`. Nút "Xóa hồ sơ" của dev A sẽ **bỏ sót** khóa của hai người kia, và kết quả kiểm chứng được của FR-14 ("không còn dữ liệu nào của Hải Đồ IT trong bộ nhớ trình duyệt") sai **mà mọi test đơn lẻ vẫn xanh**. Đây đúng loại thất bại mà spine tồn tại để chặn.

Thiếu luôn: hình dạng hồ sơ có phiên bản không? Nếu sprint 5 đổi hình dạng, hồ sơ cũ trong trình duyệt người dùng (FR-14 đòi "mở lại vào hôm sau vẫn còn") sẽ làm app lỗi.

**(b) Bộ mã loại thao tác của `anon_events`.** AD-11 nói "đúng các trường FR-17 liệt kê" và AD-18 nói "mọi sự kiện ẩn danh có cờ `is_eval`". Nhưng FR-17 liệt kê *tên trường*, không liệt kê *giá trị* của trường "loại thao tác". Và ba lựa chọn của FR-21 phải phân biệt được **đúng ba giá trị khác nhau**, vì:

- SM-1 tử số chỉ tính "Tôi chưa biết", **không** tính hai lựa chọn kia;
- SM-9 chỉ tính "Tôi đã biết, chỉ là CV chưa ghi", **loại** "CV của tôi có ghi rồi";
- SM-10 lấy mẫu số từ đúng "CV của tôi có ghi rồi".

FR-45 đòi "**một câu truy vấn duy nhất**" xuất được bảng kết quả. Nếu dev A ghi `event_type='gap_choice'` với `payload={choice:'known'}` còn dev C ở sprint 6 viết câu truy vấn mong `event_type='gap_already_known_not_in_cv'`, thì cuối Sprint 7 **không có bảng số liệu nào cho chương Thực nghiệm**, và không còn thời gian chạy lại đợt thử nghiệm. Spine có convention cho mã lỗi ("`code` là hằng snake_case") nhưng không có cho mã sự kiện — một bỏ sót không đối xứng, trong khi mã sự kiện quan trọng hơn mã lỗi với đồ án này.

> **Đề xuất:** thêm **AD-19 — Hợp đồng trạng thái phía trình duyệt**. Rule: mọi khóa `localStorage` nằm dưới một tiền tố duy nhất `haido:` và được liệt kê ở **một hằng số duy nhất** trong `web/`; nút Xóa hồ sơ duyệt chính danh sách đó; hồ sơ lưu kèm `schema_version`, đọc phải phiên bản khác thì xóa chứ không đoán. Và **AD-20 — Bộ mã sự kiện ẩn danh là enum đóng**, định nghĩa một lần trong `haido_core/domain/`, Pydantic chặn giá trị lạ, mỗi mã có đúng một chỉ số SM tiêu thụ nó (bảng mã → SM nằm ngay trong AD).

#### [CRITICAL-2] Không có cổng cưỡng chế (CI) mà 6 AD đã dựa vào

Các Rule sau đều kết thúc bằng một lời hứa về kiểm thử: AD-1 ("một `import` đi ngược chiều là lỗi, có kiểm thử chặn"), AD-8 ("có kiểm thử tự động chặn"), AD-11 ("có kiểm thử xác nhận không bảng nào nhận văn bản CV hay JD"), AD-17 ("thiếu `meta` là lỗi schema, có kiểm thử hợp đồng chặn"), cộng FR-22 ("bước kiểm tra báo lỗi **trước khi triển khai**") và convention Tên kiểm thử.

Spine không nói: những kiểm thử đó chạy ở đâu, cái gì chặn merge, và "trước khi triển khai" nghĩa là bước nào trong quy trình nào. Mục Deferred làm tình hình xấu hơn: dòng "CI/CD nhiều tầng, blue-green" bị hoãn với lý do "`docker compose up -d` **sau khi test xanh** là đủ" — tức spine *tham chiếu* một cổng test như thứ đã tồn tại, trong khi chính nó chưa đặt ra. Brief sprint 1 có ghi "Khung repo, Compose, CI", nhưng spine là tài liệu hợp đồng; thứ không có trong spine thì không ai bị buộc.

Đây là phát hiện có hệ số nhân cao nhất trong bài rà soát này: nó không làm sai một AD, nó làm **sáu** AD tụt từ cưỡng chế được xuống nguyện vọng.

> **Đề xuất:** thêm vào mục Invariants một **AD-21 — Cổng kiểm thử là một**: một lệnh duy nhất (`make check` hoặc tương đương) chạy toàn bộ kiểm thử bất biến (import-linter cho AD-1, schema test cho AD-4/AD-17, grep test cho AD-8/AD-10, test "không bảng nào chứa CV/JD" cho AD-11, test tổ tiên/lặp lại cho FR-22); GitHub Actions chạy đúng lệnh đó trên mọi PR; **không merge vào `main` khi lệnh đó đỏ**; triển khai chỉ từ `main`. Và sửa dòng Deferred để nó hoãn *blue-green và nhiều môi trường*, không hoãn cổng test.

#### [HIGH-1] Chính tắc hóa cụm tin (FR-4) và bảo đảm "mỗi cụm đúng một lần"

FR-4 nói "các tin trùng nhau được gom thành một cụm thay vì bị xóa. **Mọi con số thống kê tính mỗi cụm đúng một lần.**" Spine thể hiện điều này trong sơ đồ ER (`JOB_CLUSTER ||--|| JOB : "đại diện"`) nhưng **không có AD nào** nói:

- tin nào trong cụm là tin đại diện, và quy tắc chọn có tất định không;
- khi hai thành viên của cụm khác nhau về lương, chức danh, thành phố, công ty (chuyện bình thường khi cùng tin đăng trên TopCV và CareerLink) thì **giá trị nào thắng**;
- mọi bước tổng hợp đếm trên `JOB` (cụm) chứ không trên `JOB_RAW`.

Ba dev gặp dữ liệu này ở ba sprint khác nhau: dev ghép trùng (sprint 1–2), dev tính tổng hợp (sprint 2), dev Soi tin FR-32 (sprint 4, phải so khớp tin dán với *cụm* để lấy vòng đời cho D4). Nếu bước tổng hợp đếm `job_raw`, **mọi con số trong sản phẩm sai cùng một hướng** — TopCV chiếm 38% dữ liệu nền nên tin đăng chéo sẽ bị nhân đôi — và SM-7 (đo precision/recall của dedup) vẫn xanh vì nó đo bước dedup, không đo bước đếm. Đây là phân kỳ thầm lặng: không có test nào tự nhiên bắt được nó.

> **Đề xuất:** mở rộng AD-16 hoặc thêm một AD: cụm là đơn vị đếm duy nhất; quy tắc chọn tin đại diện là một hàm thuần trong `domain` (ví dụ: nguồn có thứ tự ưu tiên cố định, rồi `first_seen` sớm nhất, rồi `job_raw.id`); mọi bảng `stat_*` có một kiểm thử đối chiếu `COUNT(DISTINCT cluster_id)`.

#### [HIGH-2] Không có cổng HTTP ra ngoài dùng chung (FR-2) — bất đối xứng với AD-9

Spine có **một cổng duy nhất cho LLM** (AD-9) với lý do rất đúng. Nhưng nó **không có cổng nào cho HTTP đi ra tới các nguồn tin**, trong khi đó là bề mặt rủi ro lớn nhất của cả dự án: FR-2 đòi bốn quy tắc lịch sự (robots.txt, User-Agent trung thực có liên hệ, giãn cách cố định, dừng ngay khi 403/429/captcha), và §6.1 R1–R4 nói rõ rủi ro **"Rất cao, có thể rơi vào Điều 289 Bộ luật Hình sự"**.

Tệ hơn, AD-16 **làm việc ngược lại**: "mỗi crawler giữ nguyên giao diện hiện tại" đóng băng 9 crawler kế thừa, nghĩa là bốn quy tắc của FR-2 sẽ nằm rải rác trong 9 bản cài đặt (hoặc không nằm ở đâu). Kết quả kiểm chứng được của FR-2 — "URL bị `robots.txt` cấm thì **không bao giờ** được request" — là một bất biến toàn hệ, loại khẳng định chỉ chứng minh được nếu có đúng một chỗ đi ra mạng.

Liên quan: spine **không nhắc R1–R4 một lần nào**. Kỹ thuật né phát hiện bot (TopCV, ITviec, TopDev, step-03) sẽ sống trong code suốt v1, và brief nói "bỏ kỹ thuật này khi thương mại hóa". Không có AD nào khoanh vùng nó vào một chỗ tắt được, nên khi cần bỏ thì phải đi tìm.

> **Đề xuất:** thêm **AD-22 — Một cổng HTTP ra nguồn duy nhất**. Rule: mọi request tới một nguồn đi qua một hàm duy nhất trong `haido_core/` nhận `source_id`; hàm đó kiểm `robots.txt`, gắn User-Agent có liên hệ (FR-47), giữ giãn cách theo cấu hình của nguồn (AD-10), và trả lỗi kết thúc nguồn khi gặp 403/429/captcha; crawler nào gọi `requests`/`httpx` trực tiếp là lỗi, có kiểm thử grep chặn. Mọi mã né phát hiện bot nằm **chỉ** trong các module có tên `*_evasive.py`, bật/tắt bằng công tắc nguồn, để R1–R4 có một bề mặt đóng được bằng một dòng cấu hình.

#### [HIGH-3] FR-5 không có nhà: xóa PII của người đăng tin đặt ở đâu?

FR-5: "**Ngay khi đọc tin và trước khi lưu**, hệ thống xóa tên, email, số điện thoại và Zalo của người tuyển dụng". Kết quả kiểm chứng được là một bất biến toàn kho: "không bản ghi nào trong kho dữ liệu khớp mẫu email hoặc số điện thoại Việt Nam".

Trong spine: FR-5 **không xuất hiện trong `Binds` của bất kỳ AD nào**, và **không có bước nào trong sơ đồ "Dòng dữ liệu một đêm"** (crawl → ingest → dedupe → mentions → mapping → classify → salary → aggregate → publish). AD-11 chỉ nói về nội dung *người dùng*, không nói về PII của người đăng tin.

Hệ quả phân kỳ: dev viết crawler cho rằng bước `ingest` lọc; dev viết `ingest` cho rằng crawler đã lọc (AD-16 nói crawler "giữ nguyên giao diện hiện tại" nên có thể hiểu là crawler không được thêm việc). Kết quả: PII vào `job_raw` và vi phạm Luật 91/2025 mà §6.2 đang cố tránh — lại là loại vi phạm *đứng im*, không gây lỗi, chỉ bị phát hiện khi ai đó chạy một câu grep (hoặc khi hội đồng chạy nó).

> **Đề xuất:** đưa FR-5 thành một bước có tên trong sơ đồ dòng dữ liệu (`scrub` giữa `crawl` và `ingest`), và thêm Rule: hàm scrub là hàm thuần trong `domain`, bước `ingest` gọi nó **bắt buộc**, có kiểm thử chạy mẫu email/điện thoại VN trên toàn bộ `job_raw` trong cổng CI.

#### [HIGH-4] FR-7 không có AD, và AD-8 ngầm cấm cách làm dễ nhất

FR-7 (gán vai trò, nhánh, cấp bậc, thành phố cho mỗi tin) là một bước trong sơ đồ (`classify`) nhưng **không AD nào nói nó làm bằng gì**. Trong khi đó AD-8 nói "LLM **chỉ** được gọi ở ba chỗ" và ba chỗ đó không gồm phân loại. Vậy FR-7 buộc phải là quy tắc tất định — nhưng FR-7 đòi "báo cáo độ chính xác phân loại vai trò trên bộ chuẩn 200 JD" và còn đòi tách Data/AI thành 3 nhánh, tách Embedded khỏi "Other", loại tin không thuộc IT. Đó là khối lượng công việc đáng kể với một bộ quy tắc viết tay.

Phân kỳ cụ thể: dev A ở sprint 2 hoàn toàn có thể đọc AD-3 ("cổng LLM trả lượt nhắc nguyên văn") rồi mở rộng prompt để lấy thêm vai trò/cấp bậc — hợp lý, và trái AD-8. Dev B thì viết regex trên chức danh. Hai cách cho hai con số độ chính xác khác nhau và không ai biết số nào vào báo cáo.

> **Đề xuất:** một dòng trong AD-3 hoặc một AD riêng: FR-7 là **phân loại tất định** trên (chức danh đã chuẩn hóa, tập mã kỹ năng đã mapping, trường thành phố của nguồn), là hàm thuần trong `domain`, không gọi mạng; hoặc nếu dùng LLM thì nói rõ đó là **chỗ gọi thứ tư** và sửa AD-8 cho khớp. Hiện trạng — im lặng cộng một lệnh cấm ngầm — là trạng thái tệ nhất trong ba.

#### [HIGH-5] Chính sách thất bại một phần của lượt chạy đêm

Ba yêu cầu chồng nhau mà spine chưa hòa giải:

- FR-1: "một nguồn bị lỗi **không làm dừng** các nguồn khác";
- FR-3: tin chỉ coi là biến mất khi vắng mặt ở "ít nhất 3 **lần chạy thành công liên tiếp của chính nguồn đó**", và "một đêm nguồn bị lỗi **không bao giờ** làm tăng số lần đăng lại";
- AD-4: snapshot chuyển `published` "trong **đúng một transaction** ở cuối lượt chạy".

Câu chưa ai trả lời: **khi 2 trong 9 nguồn lỗi, snapshot đêm đó có được công bố không?** Hai câu trả lời đều hợp lý và dẫn tới hai hệ thống khác nhau:

- *Công bố* → cần khái niệm "thành công theo từng nguồn" tách khỏi "snapshot đã công bố", và `pipeline_run` phải mang trạng thái per-source để FR-3 đếm đúng;
- *Không công bố* → một nguồn lỗi làm mất cả đêm, SM-5 (≥95% lượt chạy thành công, ≥25 snapshot trong 4 tuần) rất khó đạt với 9 nguồn, và NFR "khả dụng" phải gánh nhiều hơn dự kiến.

Dev pipeline (sprint 1) và dev vòng đời tin + D4 (sprint 4) sẽ giả định khác nhau, và sai lệch chỉ lộ ra ở D4 ("tin đã đăng lại X lần") — tức ở một con số hiển thị cho người dùng.

> **Đề xuất:** một dòng trong AD-4: snapshot được công bố khi **ít nhất một nguồn đang bật chạy thành công**; `pipeline_run` lưu trạng thái **theo từng nguồn**; vòng đời tin (FR-3) chỉ đếm trên các lượt chạy thành công *của nguồn đó*, đọc từ `pipeline_run`, không đọc từ danh sách snapshot.

#### [HIGH-6] Batch API không đồng bộ vs "một lượt chạy một đêm"

Stack chọn `claude-haiku-5-5` qua **Batch API** cho lô hằng đêm (đúng theo §6.4). Nhưng Batch API là không đồng bộ, không có bảo đảm độ trễ. AD-4 lại đòi snapshot công bố "ở cuối lượt chạy, **sau khi mọi bảng tổng hợp của nó đã ghi xong**", và bảng tổng hợp phụ thuộc vào bước `mentions`.

Spine không có Rule cho: lượt chạy đêm mà batch chưa trả về thì làm gì. Ba lối ra (chờ có timeout; công bố snapshot không có mentions mới; tách thành hai partition) dẫn tới ba thiết kế pipeline khác nhau, và dev pipeline phải chọn ở **sprint 1–2**, trước khi ai kịp đo.

> **Đề xuất:** nói rõ trong AD-4 hoặc AD-15: bước `mentions` là một asset **chờ kết quả batch với hạn chót**; quá hạn thì lượt chạy đêm đó công bố snapshot với mentions của lần gần nhất (và `pipeline_run` ghi rõ), hoặc không công bố — nhưng phải chọn một.

#### [MEDIUM-1] Nơi sống của phép so khớp FR-4 / FR-32

FR-32 đòi Soi tin so khớp tin dán với tin đã thu thập "dùng **cùng cách so khớp** như FR-4". FR-4 là bước `dedupe` trong `steps/`. AD-5 cho phép API đọc, và AD-1 cho phép `api → core`, nên về kỹ thuật không vi phạm gì. Nhưng spine không nói phép so khớp là **hàm thuần trong `domain`** (cây mã nguồn liệt kê 9 hàm trong `domain/` và không có nó). Dev B ở sprint 4 sẽ hoặc tự viết lại, hoặc phải refactor code của dev A giữa sprint — đúng loại phân kỳ AD-2 đang chặn cho bộ máy kỹ năng, nhưng không được chặn cho bộ máy so khớp.

#### [MEDIUM-2] Không có thứ tự phân định cuối cho các danh sách top-N

NFR "tất định" phủ "câu kết luận của Insights". FR-37 có hai loại thẻ là danh sách top-N ("các cặp kỹ năng cùng xuất hiện nhiều nhất", "các kỹ năng chênh lệch nhiều nhất"), FR-34 có "các kỹ năng có tỷ lệ xuất hiện cao nhất", FR-33 có "thứ hạng". Addendum đã nêu nguyên tắc đúng — "không bao giờ phụ thuộc vào thứ tự trả về của cơ sở dữ liệu" — **nhưng chỉ cho FR-22**. Khi hai kỹ năng bằng tỷ lệ, `ORDER BY rate DESC LIMIT 5` cho kết quả đổi giữa hai lần chạy trên cùng snapshot, và kiểm thử "cùng snapshot cho cùng câu kết luận" (FR-39) sẽ đỏ ngẫu nhiên — loại lỗi tốn nhiều giờ nhất để tìm trong tuần cuối.

> **Đề xuất:** thêm một dòng convention: mọi danh sách có thứ tự trả về cho người dùng phải có khóa sắp xếp **toàn phần**, chốt bằng mã kỹ năng A–Z (giống tầng 4 của FR-22).

#### [MEDIUM-3] Snapshot hạt giống cho môi trường dev

Spine nói "hai môi trường, không có staging: local và prod". Nhưng ba dev ở sprint 3–6 cần **một snapshot đã công bố** để phát triển Cố vấn, Soi tin, Bản đồ, Insights. Nếu mỗi người tự tạo dữ liệu mẫu, thì (a) số trong ba bản demo khác nhau, (b) không ai tái tạo được lỗi của người khác, (c) Review giữa kỳ 22–28/11 phụ thuộc vào máy của một người. Đây là phân kỳ rất đời thường và rất dễ chặn bằng một dòng.

#### [MEDIUM-4] Hợp đồng "vai trò chưa có đồ thị học trước" (FR-18 / FR-35)

FR-18 đòi: vai trò chưa có đồ thị thì Cố vấn không vẽ, mà hiển thị danh sách theo nhóm kèm dòng "Lộ trình học có thứ tự cho vai trò này đang được biên soạn"; FR-35 đòi **nút từ bảng chi tiết thành phố hiển thị cùng thông báo đó**. Đó là một cờ mà API phải trả và **hai dev khác nhau ở hai sprint khác nhau** (dev A sprint 3, dev C sprint 5) phải đọc. `meta` của AD-17 không có trường nào cho nó. Hai bên sẽ tự suy ra từ dữ liệu theo hai cách (một bên kiểm "mảng lộ trình rỗng", một bên hardcode danh sách vai trò) và câu chữ sẽ lệch — trong khi FR-35 đòi "cùng thông báo đó".

### 1.3 Kết luận mục 1

**Đạt phần lớn, nhưng thiên lệch hệ thống.** Spine cố định rất tốt những phân kỳ **bên trong Python** (AD-1 đến AD-10, AD-12, AD-15, AD-16) và **giữa pipeline và API**. Nó cố định yếu hơn những phân kỳ **ở biên** — biên trình duyệt (CRITICAL-1), biên mạng đi ra (HIGH-2), biên quy trình (CRITICAL-2) — và những phân kỳ **giữa hai dev ở hai sprint cách nhau** (HIGH-1, MEDIUM-1, MEDIUM-4). Vì đúng ba người làm song song và đúng tám tuần, nhóm phân kỳ thứ hai mới là nhóm sẽ gây đau.

---

## 2. Mỗi AD có Rule cưỡng chế được không, và Rule đó có ngăn đúng cái nó tuyên bố ngăn không?

Thang đánh giá: **Cưỡng chế được** (có cách kiểm tự động rõ ràng) · **Cưỡng chế được một phần** (một nửa Rule kiểm được) · **Nguyện vọng** (chỉ dựa vào kỷ luật/review).

| AD | Cưỡng chế | Có ngăn đúng cái nó tuyên bố? | Ghi chú |
|---|---|---|---|
| AD-1 | Được (import-linter) | **Không hoàn toàn** — sơ đồ phụ thuộc của chính AD-1 sai so với phần Triển khai (xem §6) | Không nêu công cụ; dựa vào CI chưa có |
| AD-2 | Một phần | Nửa Python: có. Nửa frontend: **không kiểm được** | Xem [HIGH-7] |
| AD-3 | Được | Ngăn đúng, nhưng chữ "chỉ" **chặn cả 4 FR hợp lệ** | Xem [CRITICAL-3] |
| AD-4 | Một phần | Có, trừ phần bất biến chỉ dựa vào kỷ luật | Xem [MEDIUM-5] |
| AD-5 | Được (nếu cấp quyền DB) | Có | Rule tốt; nên nêu cơ chế |
| AD-6 | Được | Có, nhưng khóa thiếu chiều thành phố | Xem [MEDIUM-6] |
| AD-7 | Một phần | Có, nhờ hợp đồng API, không nhờ Rule | Lệnh cấm phía frontend là nguyện vọng |
| AD-8 | Được | Có. Rule tốt nhất trong spine | Regex + danh sách loại trừ đã có trong addendum |
| AD-9 | Được | Có, nhưng thiếu hợp đồng timeout/suy giảm | Xem [HIGH-8] |
| AD-10 | Được | Có, nhưng danh sách tham số **không đầy đủ** | Xem [MEDIUM-7] |
| AD-11 | Một phần | **Rule bị mặc định của framework phá** | Xem [CRITICAL-4] |
| AD-12 | Được (ràng buộc schema) | Có | Còn sót dấu `[ADOPTED]` trong tiêu đề |
| AD-13 | Một phần | **Không** khi lệnh gọi làm mới thất bại | Xem [MEDIUM-8]; cơ chế `revalidatePath` còn bị phát biểu sai — xem ghi chú phạm vi ở §4.1 |
| AD-14 | Được (nếu cấp quyền DB) | Có | `Binds: FR-47` là liên kết lỏng, xem §5 |
| AD-15 | Được | Có | Rule rất sắc |
| AD-16 | Được | Có, nhưng đụng FR-2 và FR-5 | Xem HIGH-2, HIGH-3 |
| AD-17 | Được | **Không** — mâu thuẫn FR-33, thiếu hình dạng cho FR-30/34/37 | Xem [CRITICAL-5] |
| AD-18 | Được | Có, nhưng vô dụng nếu thiếu enum sự kiện | Xem CRITICAL-1 |

### Các AD có vấn đề về cưỡng chế

#### [CRITICAL-3] AD-3 — chữ "chỉ" chặn FR-6, FR-27, FR-30, FR-31 D5–D7, FR-46

Rule: *"cổng LLM **chỉ** trả về các lượt nhắc nguyên văn trích từ văn bản."*

Đây là Rule **cưỡng chế được rất tốt** (kiểm schema đầu ra của cổng là xong) và ngăn đúng cái nó tuyên bố ngăn. Vấn đề là nó ngăn **thêm** bốn thứ mà PRD đòi, và spine không mở cửa nào khác:

| Cần trích từ văn bản | FR | Có phải "lượt nhắc kỹ năng nguyên văn"? |
|---|---|---|
| Số năm kinh nghiệm yêu cầu (tối thiểu, tối đa) | FR-6 (nói rõ "trong **cùng lượt xử lý đó**") | Không |
| Vai trò + cấp bậc của tin người dùng dán | FR-27 | Không |
| Kênh liên hệ (Zalo/Telegram/Gmail cá nhân, không có kênh công ty) | FR-31 D5 | Không |
| Nhắc tới đặt cọc / phí đào tạo / phí hồ sơ / phí giữ chỗ | FR-31 D6 | Không |
| Có nêu tên công ty hay không | FR-31 D7 | Không |
| Có khoảng lương, có trách nhiệm công việc, có phúc lợi, chức danh nhất quán với cấp bậc | FR-46 (5 mục) | Không |
| Lương dạng số và đơn vị | FR-8 | Không |

Đọc đúng chữ, AD-3 làm toàn bộ cột bên trái **không có đường ra khỏi văn bản**. Thực tế sẽ xảy ra: dev B ở sprint 4 cần D5–D7 và FR-46, thấy cổng LLM không trả về gì dùng được, rồi làm một trong hai việc — (a) mở rộng prompt của cổng và phá AD-3 lặng lẽ, hoặc (b) viết một bộ regex riêng trong `haido_api/` và phá AD-1 + AD-5. Cả hai đều là phân kỳ, và cả hai đều có lý do chính đáng vào lúc đó. Một AD mà việc tuân thủ nó khiến yêu cầu không thực hiện được thì sẽ bị phá, không phải bị tuân thủ.

Lưu ý: ý định của AD-3 vẫn đúng và quan trọng — cái cần bảo vệ là *"mapping lượt nhắc → mã kỹ năng là tất định, đổi bí danh không phải gọi lại LLM"*. Ý định đó không đòi cổng chỉ trả về lượt nhắc.

> **Sửa đề xuất:** đổi Rule thành: *"cổng LLM chỉ trả về **dữ kiện trích nguyên văn hoặc trích có cấu trúc trực tiếp từ văn bản** — lượt nhắc kỹ năng, số năm kinh nghiệm, khoảng lương, sự hiện diện của các trường mà FR-46 và D5–D7 kiểm. Cổng **không bao giờ** trả về mã kỹ năng, nhóm kỹ năng, vai trò, cấp bậc, thứ tự, hay bất kỳ phán xét nào. Mọi phép quy chiếu và phán xét trên dữ kiện đó là hàm thuần trong `domain`, không gọi mạng."* Giữ nguyên câu chốt "Đổi bộ từ vựng ⇒ chạy lại mapping, không chạy lại LLM" — nó vẫn đúng và vẫn là lõi của AD.

#### [CRITICAL-4] AD-11 — "không chạm đĩa" bị mặc định của FastAPI phá ngay

Rule: *"File tải lên xử lý trong bộ nhớ, không chạm đĩa."*

Với stack đã chọn (FastAPI 0.162 + Starlette), `UploadFile` dùng `SpooledTemporaryFile` và **tự ghi xuống đĩa khi file vượt ngưỡng spool (mặc định 1 MB)**. FR-10 cho phép CV tới **5 MB**, và addendum nói CV sinh viên thường 100 KB – 1,5 MB. Nghĩa là một phần đáng kể CV thật **sẽ** được framework ghi ra `/tmp` trong container, trong khi Rule tuyên bố điều ngược lại và `Prevents` của AD-11 là "phá cam kết riêng tư mà không ai thấy" — đúng tình huống đang xảy ra.

Phần còn lại của AD-11 thì rất tốt và cưỡng chế được: "endpoint... không có lệnh ghi nào vào cơ sở dữ liệu", "có kiểm thử xác nhận không bảng nào nhận văn bản CV hay JD". Nhưng kiểm thử đó kiểm **bảng**, không kiểm **đĩa** — nên lỗ hổng này đi qua đúng cái test mà AD-11 dựng.

> **Sửa đề xuất:** nêu cơ chế, không chỉ nêu ý chí: đặt `spool_max_size` lớn hơn giới hạn 5 MB (hoặc đọc body thành `bytes` rồi parse), chặn 5 MB **ở Caddy** (addendum FR-10 đã đòi điều này; spine chưa ghi), và thêm vào kiểm thử của AD-11 một lượt kiểm "sau khi xử lý một CV 4 MB, không file mới nào trong `/tmp` của container api".

#### [CRITICAL-5] AD-17 — mâu thuẫn FR-33 và thiếu hình dạng cho phản hồi nhiều ô

AD-17 là AD có đòn bẩy cao nhất trong spine: nó là hợp đồng duy nhất mà cả bốn tính năng đọc số đều tiêu thụ, và Rule của nó cưỡng chế được xuất sắc (schema Pydantic + kiểm thử hợp đồng). Nhưng nội dung đang sai ba chỗ:

**(a) Mâu thuẫn trực tiếp với FR-33.** AD-17: *"Khi `n < 30`: `data` phải là `null` và `meta.insufficient_data = true` — không bao giờ là một con số đoán."* FR-33: *"**Cột có n < 30:** cột **không bị ẩn**, mà **vẫn vẽ theo tỷ trọng thật**, ở trạng thái mờ, kèm nhãn 'Cỡ mẫu nhỏ (n = X < 30): số liệu chỉ để tham khảo'"*, và kết quả kiểm chứng được nói thẳng "Cột Đà Nẵng **luôn** được vẽ". Hai câu không thể cùng đúng. Nếu dev C viết frontend theo FR-33 và dev B viết API theo AD-17, bản đồ sẽ không có cột Đà Nẵng và một kết quả kiểm chứng được của PRD sai.

**(b) `meta` phẳng không khớp phản hồi nhiều ô.** `meta` của AD-17 có **một** `stat_cell`, **một** `n`, **một** `fallback_label`. Nhưng:
- FR-33 trả 3 thành phố + "Khác" — mỗi cột một `n` riêng, mỗi cột có thể dưới ngưỡng riêng;
- FR-34 trả cơ cấu vai trò — "tỷ trọng và cỡ mẫu của **từng vai trò**", và "ô thống kê có n < 30 thì không hiển thị tỷ lệ" **theo từng dòng**;
- FR-37 trả nhiều thẻ, mỗi thẻ tính trên ô khác nhau, và FR-38 lọc **theo từng thẻ**.

Với `meta` phẳng, ba dev sẽ tự chọn ba cách: nhúng `meta` con vào từng phần tử, hay nhồi một `n` tổng vào `meta` rồi mất thông tin per-row, hay trả về mảng `meta` song song. Và NFR "trung thực của con số" ("**mọi** con số hiển thị cho người dùng đều kèm cỡ mẫu") sẽ bị vi phạm bởi cách dễ nhất.

**(c) `n` đơn lẻ không đủ cho FR-30.** FR-30 có ba thước đo với **ba ngưỡng khác nhau**: số kỹ năng dùng `n` của ô; số năm kinh nghiệm cần "≥ 30 tin **có số năm kinh nghiệm**"; lương cần "≥ 30 tin **có lương**". Và khi không đủ phải hiển thị "chưa đủ dữ liệu (**X**/30 tin có lương)" — tức cần cả `X`. AD-17 không có chỗ cho `n_with_salary`, `n_with_experience`, nên dev B sẽ phải tự thêm trường, và kiểm thử hợp đồng của AD-17 sẽ phải nới ra — làm chính AD-17 mất lực.

Thiếu luôn: `meta.confidence_interval` cho FR-30 ("30 ≤ n < 100 thì hiển thị phân vị kèm khoảng tin cậy 95%"), và một trường cho cờ "vai trò chưa có đồ thị học trước" (MEDIUM-4).

> **Sửa đề xuất:** đổi AD-17 thành hợp đồng hai tầng: `meta` ở gốc chỉ giữ cái **thật sự toàn cục** (`snapshot_date`, `sources[]`, `config_version`, `thresholds`); mọi con số đi kèm một `cell` **ở chính phần tử chứa nó** (`stat_cell`, `n`, `n_with_salary`, `n_with_experience`, `fallback_label`, `ci`, `small_sample: bool`). Và sửa quy tắc n<30 cho khớp PRD: *"n < 30 thì `data` là `null` và `insufficient_data = true`, **trừ các con số tỷ trọng của Bản đồ nhu cầu (FR-33), vẫn trả giá trị thật kèm `small_sample = true`**"* — nêu ngoại lệ tường minh, đúng kiểu AD-5 đã làm rất tốt với ngoại lệ phân vị.

#### [HIGH-7] AD-2 — nửa frontend là nguyện vọng, và đụng FR-13/FR-42

Rule: *"Pipeline, API và frontend không được cài lại bất kỳ phần nào của nó, kể cả một phiên bản 'tạm' hay 'đơn giản hóa'."*

Với Python, AD-1 + AD-5 cho đủ sức cưỡng chế. Với frontend thì **không có cách nào kiểm tự động** việc "đã cài lại một phần" — nó là một lệnh cấm viết code tương tự, loại Rule chỉ sống được bằng review.

Nghiêm trọng hơn, có một áp lực thật đẩy frontend về phía vi phạm: FR-13 đòi "tìm và chọn từ danh sách kỹ năng", FR-42 đòi chọn 3 kỹ năng "từ bộ từ vựng kỹ năng bằng ô tìm kiếm **có gợi ý**". Gợi ý tức thì đòi dữ liệu từ vựng (gồm bí danh, để người dùng gõ "springboot" ra `spring-boot`) nằm ở trình duyệt. Mà "từ văn bản người dùng gõ → mã kỹ năng" chính là **một phần** của phép mà AD-2 độc quyền hóa. Spine không nói ranh giới: frontend được nhận danh sách gì, và tìm kiếm trên trường nào.

> **Sửa đề xuất:** thêm vào AD-2 một câu cho phép tường minh và hẹp: *"frontend được nhận từ API một danh sách `(mã kỹ năng, tên hiển thị, từ khóa tìm kiếm)` để làm ô tìm kiếm có gợi ý (FR-13, FR-42), và chỉ dùng nó để **chọn** một mã có sẵn. Frontend không bao giờ suy ra mã kỹ năng từ văn bản tự do, không bao giờ chứa bảng bí danh dùng cho mục đích khác."* Rule hẹp mà kiểm được (frontend không gọi endpoint trích xuất cho ô tìm kiếm) tốt hơn một lệnh cấm rộng mà không kiểm được.

#### [HIGH-8] AD-9 — thiếu hợp đồng timeout, thử lại, và suy giảm

AD-9 cố định cổng, phiên bản và nhà cung cấp — tốt. Nhưng hai trong ba chỗ gọi là **lúc người dùng đang chờ** (FR-12, FR-26) với ngân sách **15 giây** (NFR §5, SM-4), và Rule không nói gì về: timeout là bao nhiêu, thử lại mấy lần, và người dùng thấy gì khi Claude chậm hoặc lỗi.

Phân kỳ chắc chắn: dev A (FR-12, sprint 3) đặt timeout 20s và hiện spinner; dev B (FR-26, sprint 4) đặt timeout 10s và báo lỗi; thực đo ở Sprint 7 ra hai con số khác nhau cho cùng một NFR, và SM-4 không có một ngưỡng duy nhất để đo. NFR "khả dụng" của PRD chỉ phủ "pipeline một đêm bị lỗi", **không** phủ "cổng LLM lỗi lúc người dùng đang chờ" — nên không ai thừa hưởng câu trả lời từ PRD.

> **Sửa đề xuất:** vào AD-9: một ngân sách thời gian duy nhất cho đường gọi lúc chạy (ví dụ 12 s, chừa 3 s cho phần còn lại của 15 s), **không thử lại** đường đồng bộ (thử lại là vỡ ngân sách), và một mã lỗi duy nhất theo convention `Hình lỗi` để hai tính năng hiển thị cùng một câu tiếng Việt.

#### [MEDIUM-5] AD-4 — tính bất biến không có cơ chế

"Hàng thuộc snapshot đã công bố không bao giờ bị sửa hay xóa" là bất biến quan trọng nhất của spine, nhưng Rule không nêu cách chặn. Nó kiểm được rẻ: convention "Đột biến trạng thái" đã nói chỉ `steps/` ghi vào bảng thị trường — nên chỉ cần thêm rằng tài khoản DB của `api` và của `web` **không có quyền** `UPDATE`/`DELETE` trên bảng `stat_*`, và (nếu muốn chắc) một trigger `BEFORE UPDATE OR DELETE` chặn hàng có snapshot ở trạng thái `published`. Đó là biến một nguyện vọng thành một bất biến ở tầng dữ liệu bằng ba dòng SQL.

#### [MEDIUM-6] AD-6 — khóa `stat_cells` thiếu chiều thành phố

Khóa: `(snapshot_id, role, branch, seniority, scope)`. Nhưng §3 định nghĩa **hai** loại ô thống kê: Cố vấn/Soi tin dùng *vai trò × cấp bậc toàn quốc*; Bản đồ/Insights dùng **thành phố × vai trò**. FR-37 còn cần thêm cả hai chiều cùng lúc ("khác biệt giữa Hà Nội và TP.HCM" theo từng kỹ năng, "Đà Nẵng được đưa vào khi ô thống kê của nó đạt n ≥ 30").

Nếu `scope` là chỗ nhồi thành phố (ví dụ `scope='city:hanoi'`) thì nên nói ra, vì mọi câu truy vấn và mọi ràng buộc đều phụ thuộc vào việc đó. Nếu không, dev C sẽ tạo một bảng `stat_city_cells` thứ hai với quy tắc ngưỡng riêng — chính cái AD-6 đang chặn ("Không nơi nào khác được dựng lại chuỗi quay về").

#### [MEDIUM-7] AD-10 — "mọi tham số hiệu chỉnh được" mà danh sách thiếu

Rule liệt kê: θ_core, θ_common, tỷ giá USD, công tắc nguồn, ngưỡng D1–D7. Thiếu, dù cùng tính chất:

- **n = 30** (ngưỡng mẫu, §3) — và SM-13 nói rõ mục đích là trả lời "vì sao 30 mà không phải 20 hay 50", tức con số này sẽ bị thí nghiệm;
- **60 ngày** (cửa sổ `last_seen` của ô thống kê, §3);
- **5 điểm phần trăm** (FR-38) — FR-38 có trong `Binds` của AD-10 nhưng con số không có trong Rule;
- **B = 1.000** (số lần bootstrap, FR-9) — câu hỏi mở số 12 của PRD nói có thể phải giảm B, tức đổi được mà không triển khai lại là đúng cái cần;
- **4 kỹ năng / 50%** (điều kiện D2), **30 tin có lương / có số năm** (FR-30);
- **50%** (ngưỡng báo động sụt tin của FR-1).

Hiện trạng tệ ở chỗ AD-17 đã **viết cứng "n < 30" vào Rule của nó**, nên hai AD đang nói hai điều khác nhau về cùng một con số. Và tiêu đề AD-10 ("Mọi tham số hiệu chỉnh được…") hứa nhiều hơn Rule của nó cho.

#### [MEDIUM-8] AD-13 — không có đường xử lý khi lệnh gọi làm mới thất bại

Rule: "sau khi một snapshot chuyển `published`, bước cuối của pipeline gọi route làm mới của `web/`". `Prevents` là "trang SEO hiển thị số của đêm nay trong khi API trả số của đêm qua". Nhưng nếu lệnh gọi đó lỗi (container `web` đang restart, secret sai, Next.js đang build), snapshot đã `published` còn trang tĩnh vẫn là của đêm trước — **đúng cái `Prevents` nói, và Rule không chặn**. Vì ISR tĩnh không tự hết hạn theo thiết kế này, trạng thái lệch sẽ **giữ nguyên vô hạn** tới đêm sau.

> **Sửa đề xuất:** làm mới là một bước có thể thử lại và **có xác minh**: sau khi gọi, đọc lại một trang và so `snapshot_date` in trên trang với snapshot vừa công bố; lệch thì đánh dấu lượt chạy là lỗi (để email FR-1 bắn). Hoặc đơn giản hơn: cho mỗi trang công khai một `revalidate` theo thời gian làm lưới an toàn, và lệnh gọi làm mới chỉ là đường nhanh.

#### [MEDIUM-9] AD-12 — còn sót dấu `[ADOPTED]` trong tiêu đề

Tiêu đề: *"### AD-12 — Hai loại cạnh kỹ năng không bao giờ trộn `[ADOPTED]`"*. Đây là dấu vết từ `.memlog.md` lọt vào bản hợp đồng. Nhỏ, nhưng spine là tài liệu người khác đọc để ra quyết định, và một token lạ trong tiêu đề AD làm người đọc mất một phút đoán nó có nghĩa gì (và nó có nghĩa khác với 17 AD còn lại không).

### 2.1 Kết luận mục 2

Chất lượng Rule **cao hơn trung bình đáng kể**: 11/18 AD có Rule kiểm được bằng một cách rõ ràng, và không có AD nào dùng chữ "nên" hay "cố gắng" — toàn bộ đều viết ở dạng cấm/buộc. Đó là điểm mạnh thật.

Nhưng:
- **Không AD nào nêu công cụ hay nơi chạy kiểm thử** → CRITICAL-2 kéo cả nhóm xuống;
- **4 AD có Rule không ngăn đúng cái nó tuyên bố**: AD-1 (sơ đồ sai), AD-13 (không có nhánh thất bại), AD-17 (mâu thuẫn FR-33), AD-11 (mặc định framework phá Rule);
- **1 AD ngăn quá nhiều**: AD-3 chặn 4 FR hợp lệ — và đây là dạng lỗi nguy hiểm hơn ngăn quá ít, vì nó tạo áp lực phá luật có lý do;
- **3 AD có nửa Rule là nguyện vọng**: AD-2 (frontend), AD-7 (frontend), AD-4 (bất biến).

---

## 3. Có mục nào trong Deferred mà nếu hoãn thì hai đơn vị vẫn build lệch nhau?

Mục Deferred có cấu trúc tốt — ba cột (Hoãn / Vì sao hoãn được / Quay lại khi) và phần lớn lý do có neo vào PRD. Rà từng dòng:

| Dòng Deferred | An toàn? | Nhận xét |
|---|---|---|
| Xu hướng theo thời gian và dự báo | **An toàn** | §8.2 đã loại; không ai cần nó để build gì ở v1 |
| pgvector và embedding | **An toàn** | Lý do đúng và đã rà 47 FR (xem `.memlog.md`); không mở biên nào |
| Apache AGE, Cypher | **An toàn** | Chỉ là phương án trình bày; đồ thị trong bộ nhớ không đổi |
| OCR cho CV ảnh scan | **An toàn** | FR-11 có ba đường thoát; ngưỡng 30 ký tự là logic nhỏ, một chỗ |
| Mở rộng trang SEO sang thành phố/kỹ năng/câu hỏi | **KHÔNG — [HIGH-9]** | Xem dưới |
| Mô hình nhỏ rẻ cho trích xuất | **An toàn** | AD-9 + AD-10 làm nó thành một dòng cấu hình. Đây là ví dụ hoãn đúng cách |
| Nhiều instance, hàng đợi, cache phân tán | **KHÔNG — [HIGH-10]** | Xem dưới |
| Tài khoản người dùng, ứng dụng di động | **An toàn** | §7, §8.2 |
| Báo động Telegram/Slack | **Một phần — [MEDIUM-10]** | Xem dưới |
| CI/CD nhiều tầng, blue-green | **KHÔNG — [CRITICAL-2 / HIGH-11]** | Xem dưới |

### [HIGH-9] "Mở rộng trang SEO" hoãn được, nhưng **lược đồ URL thì không**

Lý do hoãn ("Template sinh theo dữ liệu; thêm trang là thêm dòng, không thêm code") là đúng về *công sức*, nhưng bỏ qua một điều: **URL của trang được index là cửa một chiều**. Đổi đường dẫn sau khi Google đã index là mất toàn bộ tín hiệu đã tích (hoặc phải dựng redirect — đúng loại việc nhóm 3 người ở tuần 7 không muốn).

Spine cố định rất kỹ `Route API` (`/api/v1/<danh-từ-kebab>`) và `Link chia sẻ` (`?role=&level=&have=`) nhưng **không cố định đường dẫn trang công khai**. Hai đơn vị cần nó **ngay bây giờ**: dev web (sinh 5–8 trang vai trò, sprint 5) và bất cứ ai đặt link trong bản tải về FR-16, trong trang chính sách dữ liệu FR-47, và trong chân trang mọi màn hình (FR-47 đòi trang chính sách "truy cập được từ chân trang của **mọi** màn hình").

Nếu dev web chọn `/vai-tro/java-backend` và sau này muốn thêm thành phố, cấu trúc `/vai-tro/java-backend/ha-noi` có thể hợp hoặc không hợp với cách `generateStaticParams` đã viết. Một dòng convention bây giờ là miễn phí; sửa sau thì không.

> **Đề xuất:** thêm vào bảng Consistency Conventions một dòng `Đường dẫn trang công khai` cố định lược đồ cho cả v1 và phần hoãn, ví dụ `/lo-trinh/<mã-vai-trò>` cho v1 và dành trước `/lo-trinh/<mã-vai-trò>/<mã-thành-phố>`, `/ky-nang/<mã>`, `/hoi-dap/<slug>`. Mã trong URL **dùng đúng mã enum của `domain`**, không dùng chuỗi hiển thị tiếng Việt — khớp với convention "Chuỗi hiển thị tiếng Việt tra từ bảng, không viết trong code".

### [HIGH-10] Hoãn "hàng đợi, cache" được; hoãn **mọi phát biểu về đồng thời và giới hạn tốc độ** thì không

Lý do hoãn: "Một VPS, một pipeline hằng đêm, **không có tải đồng thời đáng kể**". Giả định này đúng với ngày thường, nhưng sai đúng vào lúc quan trọng nhất:

- **Sprint 6–7:** 30–50 người thử, vào từ **một link Facebook** (PRD §9 và brief §4). Phân bố truy cập của một link Facebook là nhọn, không phẳng. Mỗi phiên gọi `claude-sonnet-5-5` lúc trích CV (FR-12) và lúc soi tin (FR-26), **đồng bộ, với ngân sách 15 giây**, trên 1 VPS 4 GB đang chạy Postgres + Dagster + Next.js + API.
- **Đo SM-4** (dưới 15 giây) diễn ra đúng trong cửa sổ đó. Nếu 10 người bấm cùng lúc, con số vào báo cáo là con số của trạng thái tắc.

Thiếu luôn một thứ liên quan chặt: **không có AD hay convention nào đặt giới hạn tốc độ và giới hạn kích thước cho hai endpoint POST gọi LLM**. Addendum FR-10 nói giới hạn 5 MB "được chặn ở cả frontend lẫn reverse proxy", nhưng spine không ghi điều đó vào Caddy. FR-26 cho 20.000 ký tự. Cả hai endpoint đều **công khai, không xác thực** (convention "Xác thực: không có tài khoản") và **mỗi lần gọi tốn tiền**. Trần chi phí §6.4 là **5–10 USD/tháng** — một người lặp một vòng `curl` qua đêm là vượt trần, và SM-C5 (chi phí LLM mỗi phiên) trở thành con số vô nghĩa.

> **Đề xuất:** không cần hàng đợi. Cần ba dòng: giới hạn tốc độ theo IP ở Caddy cho hai route POST; giới hạn kích thước body ở Caddy (5 MB cho CV, 20 KB cho JD dán); và một **giới hạn đồng thời** cho cổng LLM (ví dụ semaphore 4) để tắc thì xếp hàng trong tiến trình thay vì làm sập VPS. Thêm một dòng vào Deferred cho đúng: *hoãn hàng đợi phân tán; **không** hoãn giới hạn tốc độ và giới hạn đồng thời.*

### [MEDIUM-10] "Báo động qua email là đủ" — nhưng email chưa có chủ

Lý do hoãn: "FR-1 chỉ đòi 'nhóm vận hành nhận thông báo'; email cộng bảng `pipeline_run` là đủ". Vấn đề: **email cũng chưa được thiết kế ở đâu cả.** Không có AD, không có convention, không có service trong `docker-compose`, không có dòng nào về SMTP, không có ngưỡng.

FR-1 có hai kích hoạt: lượt chạy lỗi, và "số tin của một nguồn **giảm quá 50% so với trung bình 7 ngày**". Cái thứ hai là một phép tính trên lịch sử `pipeline_run` — tức một bước pipeline thật, cần ai đó viết. Spine không nêu nó trong sơ đồ dòng dữ liệu, không nêu trong cây mã nguồn, và Deferred lại nói nó "đủ rồi". Kết quả: FR-1 có một kết quả kiểm chứng được mà **không ai được giao**, và SM-5 (≥95% lượt chạy thành công trong ≥4 tuần) phụ thuộc vào việc phát hiện lỗi sớm.

Đây không hẳn là hai đơn vị build lệch nhau, mà là một yêu cầu rơi vào khe giữa "đã hoãn" và "chưa làm" — dạng rủi ro riêng của mục Deferred: một dòng Deferred viết như thể việc đã xong.

### [CRITICAL-2 / HIGH-11] "CI/CD nhiều tầng, blue-green" — hoãn quá rộng

Đã phân tích ở CRITICAL-2 về cổng test. Thêm hai thứ dòng này hoãn kèm mà không nên:

**(a) Thứ tự di trú schema khi triển khai.** "`docker compose up -d` là đủ" không nói Alembic chạy lúc nào: trước khi container api lên, trong entrypoint của api, hay bằng tay. Với 3 dev và nhiều nhánh song song, đây là thứ sẽ gãy ở lần triển khai thứ ba. Xem thêm §4.2.

**(b) Triển khai trùng giờ chạy pipeline.** Lượt chạy đêm có thể dài (Batch API). `docker compose up -d` lúc 2 giờ sáng giữa một lượt chạy sẽ giết Dagster daemon giữa transaction công bố — tức đánh trực tiếp vào bất biến quan trọng nhất (AD-4) và vào SM-5. Một dòng ("không triển khai trong cửa sổ chạy đêm; hoặc dừng schedule trước khi triển khai") là đủ.

### 3.1 Kết luận mục 3

**7/10 dòng hoãn an toàn và có lý do neo vào PRD** — tỷ lệ tốt. Ba dòng có vấn đề, và cả ba có cùng dạng lỗi: **hoãn một thứ lớn kéo theo hoãn luôn một quyết định nhỏ mà hôm nay vẫn phải có.** Hoãn blue-green kéo theo hoãn cổng test và thứ tự migration; hoãn hàng đợi kéo theo hoãn giới hạn tốc độ; hoãn mở rộng SEO kéo theo hoãn lược đồ URL. Cách sửa cho cả ba giống nhau: viết lại cột "Hoãn" cho hẹp hơn, và nêu rõ phần **không** hoãn.

---

## 4. Có chiều cấu trúc nào bị để im hoàn toàn không? (phong bì vận hành)

Rà sáu mảng mà checklist nêu tên.

### 4.1 Triển khai và môi trường — **ĐẠT về mức phủ** (hai sai sót nội dung do lăng kính khác bắt)

> **Ghi chú phạm vi.** Bài rà soát này đánh giá *chiều cấu trúc có bị để im hay không*, không kiểm lại tính đúng của từng chi tiết kỹ thuật. Hai sai sót nội dung trong phần này đã được hai lăng kính rà soát khác phát hiện và không lặp lại ở đây: (a) sơ đồ triển khai mô tả Dagster là "daemon + UI", trong khi thực tế cần 3 service long-running cộng một run worker cho mỗi lượt chạy — tức bảng service và ngân sách RAM của VPS 4 GB phải tính lại (liên quan trực tiếp tới MEDIUM-16 ở §4.7); (b) AD-13 phát biểu sai cơ chế `revalidatePath` — nó chỉ đánh dấu cache hết hạn, không sinh lại trang. Điểm (b) **làm MEDIUM-8 nặng hơn**, không nhẹ hơn: nếu lệnh gọi chỉ đánh dấu hết hạn, thì trang được sinh lại vào *request đầu tiên sau đó*, nên "Trang nội dung không bao giờ render động theo request" và "pipeline gọi route làm mới" không mô tả cùng một cơ chế, và cửa sổ lệch số giữa trang công khai và API dài hơn spine giả định.

Đánh giá về mức phủ:

Có sơ đồ triển khai đầy đủ (Cloudflare → Caddy → web/api, Postgres, Dagster trong một Compose), hai môi trường nêu tường minh với điểm khác nhau duy nhất là file `.env`, thư mục `deploy/` trong cây mã nguồn, và câu quan trọng "`web` đọc Postgres **chỉ** lúc sinh trang nội dung công khai". Quyết định "không có staging" được nêu *tường minh* chứ không bị bỏ qua — đó là cách làm đúng.

Thiếu nhỏ: không nói ai chạy `docker compose up -d` và từ đâu (từ máy dev? từ VPS? pull image hay build trên VPS?). Với 3 dev và 1 VPS, build trên VPS 4 GB (Next.js build ngốn RAM) có thể làm Postgres bị OOM giữa lúc chạy. **[MEDIUM-11]**

### 4.2 Di trú schema — **GẦN NHƯ TRẮNG [HIGH-12]**

Alembic xuất hiện **đúng hai lần** trong spine: một dòng trong bảng Stack ("Alembic 1.20.1") và một comment trong cây mã nguồn ("`db/` # model SQLAlchemy + migration Alembic"). Không có AD, không có convention, không có dòng nào trong Deferred.

Với 3 dev làm 7 tính năng song song trên **một** schema trong 8 tuần, những thứ sau gần như chắc chắn xảy ra và chưa có câu trả lời:

- **Nhiều head Alembic.** Dev A và dev B mỗi người tạo một revision từ cùng một `down_revision` trong cùng tuần. Merge xong là có hai head, `alembic upgrade head` lỗi, và người giải quyết là người ít hiểu cả hai migration nhất. Đây là lỗi tốn nửa ngày mỗi lần và sẽ xảy ra nhiều lần.
- **Thay đổi phá hủy với dữ liệu không tái tạo được.** Từ sprint 1 pipeline đã chạy mỗi đêm (brief: "bật snapshot hằng ngày" ở sprint 1). Đến sprint 4, một `ALTER TABLE ... DROP COLUMN` hay một đổi tên cột mà không viết data migration là **mất snapshot lịch sử**, mà SM-5 cần ≥25 snapshot và không có cách nào thu lại ngày đã qua.
- **Quan hệ giữa migration và AD-4.** AD-4 nói hàng của snapshot đã công bố "không bao giờ bị sửa". Một migration *là* sửa. Spine không nói migration có được phép sửa bảng `stat_*` lịch sử không, và nếu không thì phải làm gì khi cần thêm cột.

> **Đề xuất:** thêm **AD-23 — Di trú schema chỉ cộng thêm, một head**. Rule: luôn đúng một head Alembic trên `main` (có kiểm thử trong cổng CI: `alembic heads` trả về đúng 1 dòng); trong 8 tuần v1, migration **chỉ được thêm** bảng/cột/index — không `DROP`, không `RENAME`, không đổi kiểu thu hẹp; cột mới luôn nullable hoặc có default; migration chạy trong entrypoint của `api` trước khi phục vụ, một lần, có khóa. Thêm một dòng: muốn bỏ một cột thì để lại sau v1.

### 4.3 Sao lưu — **TRẮNG HOÀN TOÀN [CRITICAL-6]**

Không một chữ nào trong spine nói về sao lưu, phục hồi, volume của Postgres, hay thậm chí dữ liệu nằm ở đâu trên đĩa VPS. Nó cũng **không có trong Deferred** — tức không phải một quyết định hoãn có ý thức, mà là một chiều bị để im.

Vì sao đây là critical với đúng dự án này, không phải một lời khuyên chung:

1. **Dữ liệu không tái tạo được.** SM-5 đòi **≥25 snapshot** tích lũy qua **≥4 tuần liên tiếp**. Snapshot là ảnh chụp của thị trường *tại một ngày đã qua* — mất là mất vĩnh viễn, không crawl lại được. Nếu Postgres chết ở tuần 6, SM-5 không thể đạt trước khi nộp báo cáo (20–25/12) dù nhóm làm gì.
2. **Dữ liệu thử nghiệm càng không tái tạo được.** FR-45 và SM-1/2/3/9/12 dựa trên 30–50 phiên thử nghiệm, thu trong Sprint 7, **ẩn danh tuyệt đối** (không email, không hỏi lại). Mất bảng `eval_*` = mất toàn bộ chương Thực nghiệm, và không có cách nào liên lạc lại người thử.
3. **Chỉ có một bản.** Một VPS, một container Postgres, không replica, không staging. Tất cả rủi ro tập trung vào một volume Docker trên một máy thuê.
4. **Đồ thị học trước và danh mục tài liệu là lao động người.** FR-22 đòi mỗi cạnh có nguồn tài liệu và **biên bản rà soát của giảng viên**; bộ từ vựng song ngữ và 200 JD gán nhãn tay là hàng tuần công của 3 người. Nếu những thứ này sống trong bảng Postgres (ER có `SKILL`, `SKILL_ALIAS`, `SKILL_EDGE`, `RESOURCE`, `BLURB`) thì mất DB = mất luôn chúng.

Điểm thứ 4 còn gợi một câu hỏi thiết kế mà spine chưa trả lời (xem [MEDIUM-12] ở §4.6): dữ liệu do người soạn nên sống trong **repo** (versioned, có PR, có review — đúng như `haido_core/vocab/` ngụ ý) rồi seed vào DB, chứ không nên chỉ sống trong DB.

> **Đề xuất (nhỏ, đủ cho 8 tuần):** thêm **AD-24 — Sao lưu là một bước của pipeline**. Rule: sau mỗi lần công bố snapshot, bước cuối chạy `pg_dump` nén vào `deploy/backups/` và giữ 14 bản gần nhất; `pipeline_run` ghi kết quả dump (nên dump lỗi thì email FR-1 bắn); **mỗi tuần một bản dump được copy ra ngoài VPS** (máy dev hoặc một kho miễn phí); mọi dữ liệu do người soạn (từ vựng, bí danh, cạnh `PREREQUISITE`, danh mục tài liệu, lời dẫn đã rà, `eval_fixtures/`) nằm trong repo là nguồn sự thật và được seed vào DB, không nhập trực tiếp vào DB. Thêm: một lần thử phục hồi ở Sprint 2 — bản sao lưu chưa từng được phục hồi thì chưa phải bản sao lưu.

### 4.4 Hạ tầng và nhà cung cấp — **ĐẠT, có một câu hỏi mở đúng chỗ**

VPS ≥4 GB đã có, Docker Compose + Caddy, 4 service, Cloudflare gói miễn phí cho TLS/CDN, Claude API là nhà cung cấp LLM duy nhất (AD-9), các nguồn tin là phụ thuộc bên ngoài. Vùng đặt VPS được nêu **đúng** như một câu hỏi mở số 2, kèm số độ trễ cụ thể (30–50 ms Singapore vs 250 ms châu Âu) và neo vào ngân sách 15 giây của FR-12/FR-26. Đây là cách nêu câu hỏi mở tốt: có số, có hệ quả, có người quyết.

Thiếu nhỏ: không nói phụ thuộc vào Cloudflare có bắt buộc không (nếu hội đồng hỏi "hệ thống chạy được mà không có Cloudflare chứ?"), và không nói gì về tên miền. **[thấp]**

### 4.5 Vận hành — **MỘT PHẦN**

Có: bảng `pipeline_run` (ER), convention ghi log ("JSON có cấu trúc, một dòng một sự kiện, không bao giờ ghi body / CV / JD" — rất tốt và cưỡng chế được), NFR khả dụng (chạy trên snapshot cũ), Dagster UI cho sơ đồ dòng dữ liệu và lịch sử chạy (đúng cái FR-1 đòi).

Thiếu:

- **[HIGH-13] Dagster UI có bị lộ ra Internet không?** Sơ đồ triển khai đặt `dag["dagster: daemon + UI"]` **trong** subgraph VPS, nhưng mũi tên từ `caddy` chỉ đi tới `web` và `api` — tức ngụ ý UI không qua Caddy. Nhưng spine **không nói ra**. Dagster UI không có xác thực theo mặc định, và nó cho phép **kích hoạt chạy lại asset** — tức một Dagster UI mở ra Internet là quyền điều khiển pipeline cho người lạ, trên cùng VPS giữ dữ liệu thử nghiệm. Với convention "Xác thực: không có tài khoản, không có session phía server", một người đọc spine hoàn toàn có thể kết luận "không cần xác thực cho gì cả" và mở port. Cần một câu tường minh.
- **[MEDIUM-13] Vòng quay log và dung lượng đĩa.** Log JSON có cấu trúc + Dagster + Postgres WAL + dump sao lưu (nếu thêm AD-24) + ảnh Docker, trên một VPS nhỏ. Đĩa đầy là một trong những cách sập phổ biến nhất của loại triển khai này, và nó làm **mất snapshot của đêm đó** (tức đánh vào SM-5). Một dòng về `max-size`/`max-file` của Docker log driver là đủ.
- **[MEDIUM-14] Đo chi phí LLM.** SM-C5 đòi theo dõi "chi phí của mỗi lần trích CV và mỗi lần soi tin", §6.4 đặt trần 5–10 USD/tháng. AD-9 buộc mỗi bản ghi lưu `model_id`, `prompt_version`, `vocab_version` — nhưng **không lưu số token hay chi phí**, và ER không có trường nào cho nó. Không có số thì SM-C5 không báo cáo được và trần chi phí không kiểm được. Thêm `input_tokens`, `output_tokens` vào bản ghi của cổng là gần như miễn phí nếu làm từ đầu, và rất khó bù nếu để muộn (vì cần số *lịch sử*).
- **Thiếu: thời điểm chạy đêm.** Convention cố định `snapshot_id` theo `Asia/Ho_Chi_Minh` (tốt) nhưng không cố định giờ chạy. Liên quan tới HIGH-6 (Batch API) và HIGH-11(b) (triển khai trùng giờ chạy). **[thấp–trung bình]**

### 4.6 Bảo mật — **MỘT PHẦN, có hai lỗ cụ thể**

Có: không tài khoản/không session (giảm bề mặt tấn công rất nhiều — một quyết định bảo mật tốt, dù động cơ là quyền riêng tư), secret qua biến môi trường, route làm mới bảo vệ bằng header secret dùng chung, AD-11 chặn ghi nội dung người dùng, AD-14 chặn JD thô lọt ra trang công khai, convention log không ghi body.

Thiếu:

- **[HIGH-10 đã nêu]** Không giới hạn tốc độ / kích thước trên hai endpoint POST công khai gọi LLM có phí.
- **[HIGH-13 đã nêu]** Dagster UI không được nói rõ là không lộ.
- **[MEDIUM-15] CORS / nguồn gốc request.** Hai endpoint POST nhận CV và JD từ trình duyệt. Không có dòng nào về CORS hay chặn theo origin. Không chí tử (không có cookie, không có session để CSRF), nhưng có nghĩa là bất kỳ trang nào cũng gọi được endpoint có phí của Hải Đồ IT — lại quay về vấn đề chi phí.
- **[MEDIUM-12] Nguồn sự thật của dữ liệu do người soạn.** Convention nói "secret qua biến môi trường; tham số hiệu chỉnh được qua bảng cấu hình có phiên bản (AD-10). **Không có nơi cấu hình thứ ba**". Nhưng thực tế spine đã có nơi thứ ba: `haido_core/vocab/` ("bộ từ vựng song ngữ, đồ thị học trước, danh mục tài liệu — dữ liệu có phiên bản") **và** các bảng `SKILL`, `SKILL_ALIAS`, `SKILL_EDGE`, `RESOURCE` trong ER. Hai nơi cho cùng một dữ liệu, không nói nơi nào thắng, không nói ai seed ai, không nói cái gì làm `vocab_version` tăng (mà AD-9 lưu `vocab_version` vào mỗi bản ghi và AD-3 nói "đổi bộ từ vựng ⇒ chạy lại mapping"). Nhóm rà danh sách chờ **hằng tuần** (FR-6, FR-29) nên đây là đường đi nóng, cả ba dev đều chạm. Nếu một người thêm bí danh bằng `INSERT` vào DB và một người thêm vào file vocab, lần seed sau sẽ xóa hoặc ghi đè công của người kia.
- **Thiếu: thời gian lưu dữ liệu.** `anon_events` và `eval_*` giữ bao lâu? PRD nghiêng mạnh về quyền riêng tư nhưng không nêu, và spine cũng không. Thấp với v1 (ẩn danh thật), nhưng là câu hội đồng có thể hỏi.

### 4.7 Những chiều khác

- **Hiệu năng/tài nguyên:** spine quyết Dagster thay Airflow **chính vì** RAM (rất tốt, có dẫn chứng), nhưng không có ngân sách tài nguyên cho 4 service trên 4 GB. Next.js build + Postgres + Dagster daemon + bootstrap B=1.000 (câu hỏi mở 3) cùng cạnh nhau. Một bảng nhỏ "service → RAM dự kiến" sẽ cho biết 4 GB có đủ không **trước** khi phát hiện ở tuần 6. **[MEDIUM-16]**
- **Khả năng truy cập (a11y) và trình duyệt hỗ trợ:** không nói. FR-36 có xử lý WebGL không chạy (tốt). Phần còn lại ở ngoài tầm của spine — chấp nhận được.
- **Khoanh vùng rủi ro pháp lý R1–R4:** để im hoàn toàn, đã nêu ở HIGH-2. Đây là chiều mà spine im lặng nhiều nhất so với mức độ quan trọng của nó trong PRD (§6.1 chiếm một bảng riêng, và R1/R2 ở mức "có thể rơi vào Điều 289 Bộ luật Hình sự").

### 4.8 Kết luận mục 4

| Mảng | Trạng thái |
|---|---|
| Triển khai và môi trường | Đạt |
| Hạ tầng / nhà cung cấp | Đạt (câu hỏi mở về vùng đặt máy là đúng cách) |
| Vận hành | Một phần — thiếu vòng quay log, đo chi phí, giờ chạy, phơi bày Dagster UI |
| **Sao lưu** | **Trắng hoàn toàn — CRITICAL** |
| **Di trú schema** | **Gần như trắng — HIGH** |
| Bảo mật | Một phần — thiếu giới hạn tốc độ/kích thước, phơi bày Dagster UI, nguồn sự thật của vocab |

Hai mảng trắng đều là loại "không đau trong 4 tuần đầu, rất đau ở tuần 6–8" — đúng pha mà nhóm không còn dư thời gian.

---

## 5. Spine có phủ các capability mà PRD đòi không? (FR-1..FR-47)

Bảng `Capability → Architecture Map` của spine phủ đủ 7 tính năng ở mức nhóm, và `binds` ở frontmatter liệt kê đủ 7 khoảng FR. Nhưng rà ở mức từng FR thì có một số FR không có AD lẫn convention nào chạm tới, trong khi lẽ ra phải có.

### 5.1 Bảng phủ theo FR

Ký hiệu: ✓ phủ đủ · ~ phủ một phần · ✗ không có AD/convention nào chạm

| FR | Trạng thái | Ghi chú |
|---|---|---|
| FR-1 Thu thập hằng ngày theo nguồn | ~ | AD-10 (công tắc), AD-15, AD-16 phủ phần thu thập. **Phần báo động (lỗi + sụt 50%) không có chủ** — xem MEDIUM-10 |
| FR-2 Thu thập lịch sự | **✗** | **Không AD nào.** Và AD-16 làm khó hơn. Xem HIGH-2 |
| FR-3 Snapshot và vòng đời tin | ~ | AD-4 phủ snapshot. **Vòng đời tin + thất bại một phần chưa có chính sách** — xem HIGH-5 |
| FR-4 Loại tin trùng lặp | ~ | ER có `JOB_CLUSTER`. **Không AD nào về chính tắc hóa cụm / đếm một lần** — xem HIGH-1 |
| FR-5 Loại PII người đăng tin | **✗** | **Không AD nào, không bước nào trong sơ đồ dòng dữ liệu** — xem HIGH-3 |
| FR-6 Chuẩn hóa kỹ năng | ~ | AD-2, AD-3, AD-9 phủ rất tốt phần kỹ năng. **Số năm kinh nghiệm bị AD-3 chặn** — xem CRITICAL-3 |
| FR-7 Phân loại vai trò/nhánh/cấp/thành phố | **✗** | Có bước trong sơ đồ, **không AD nào nói làm bằng gì**, và AD-8 ngầm cấm LLM — xem HIGH-4 |
| FR-8 Chuẩn hóa lương | ✓ | AD-10 (tỷ giá) + convention `Tiền` (số nguyên VND/tháng gross). Tốt |
| FR-9 Bảng tổng hợp và θ | ✓ | AD-4 + AD-10. **B=1.000 không nằm trong danh sách tham số** — MEDIUM-7 |
| FR-47 Chính sách dữ liệu và yêu cầu gỡ | ~ | `Binds` của AD-14 có FR-47 nhưng liên kết lỏng. **Cơ chế gỡ mâu thuẫn AD-4** — xem §6 |
| FR-10 Tải CV có đồng ý | ~ | AD-11 phủ phần không lưu. **Giới hạn 5 MB ở proxy không được ghi** — xem CRITICAL-4 |
| FR-11 CV ảnh scan | ~ | OCR đã hoãn đúng cách. Ngưỡng 30 ký tự là logic nhỏ, không cần AD |
| FR-12 Trích kỹ năng từ CV | ~ | AD-2/3/9/11 phủ tốt. **Thiếu hợp đồng timeout/suy giảm** — HIGH-8 |
| FR-13 Tự chọn kỹ năng | ~ | **Căng với AD-2** (ô tìm kiếm có gợi ý cần dữ liệu từ vựng ở trình duyệt) — HIGH-7 |
| FR-14 Lưu và xóa hồ sơ trong trình duyệt | **✗** | **Không AD/convention nào về `localStorage`** — CRITICAL-1 |
| FR-15 Link chia sẻ | ✓ | Convention `Link chia sẻ` rất sắc |
| FR-16 Tải kết quả | **✗** | Xem dưới |
| FR-17 Sự kiện ẩn danh | ~ | AD-11/AD-18 chạm. **Bộ mã loại thao tác không được cố định** — CRITICAL-1 |
| FR-18 Chọn vai trò và cấp bậc | ~ | **Cờ "vai trò chưa có đồ thị" không có trong `meta`** — MEDIUM-4 |
| FR-19 Lộ trình học chung | ✓ | AD-5, AD-6, AD-17 |
| FR-20 Lộ trình học cá nhân hóa | ✓ | AD-7 |
| FR-21 Xác nhận khoảng trống | ~ | Phụ thuộc bộ mã sự kiện — CRITICAL-1 |
| FR-22 Dựng lộ trình tất định | ✓ | AD-7 + AD-12. Phủ tốt nhất trong spine |
| FR-23 Chi tiết một kỹ năng | ✓ | AD-8 (lời dẫn offline, không chứa số) + AD-9. ER có `BLURB`, `RESOURCE` |
| FR-24 Tô sáng kỹ năng trùng | ✓ | AD-7 cho phép tường minh. Tốt |
| FR-25 Diễn đạt khách quan | ~ | Không có cơ chế kiểm, dù kiểm được — xem MEDIUM-17 |
| FR-26 Dán tin và trích kỹ năng | ~ | AD-3/AD-11. Giới hạn 20.000 ký tự không ở đâu — HIGH-10 |
| FR-27 Nhận diện vai trò/cấp bậc của tin | ~ | AD-6/AD-17 phủ phần ô thống kê. **Phần nhận diện bị AD-3 chặn** — CRITICAL-3 |
| FR-28 Mức khớp | ✓ | Cây mã nguồn có "mức khớp" trong `domain/`. Công thức ở addendum |
| FR-29 Phân nhóm kỹ năng của tin | ✓ | AD-2 + danh sách chờ của AD-3 |
| FR-30 Phân vị so với thị trường | ~ | AD-5 tốt (ngoại lệ đặt giá trị vào mốc đã tính). **`meta` không đủ trường** — CRITICAL-5 |
| FR-31 Dấu hiệu D1–D7 | ~ | AD-10 phủ ngưỡng. **D5/D6/D7 không có nguồn dữ kiện** — CRITICAL-3. **D4 cần đọc vòng đời lúc chạy** — xem §6 |
| FR-46 Chất lượng JD | **✗** | 5 mục kiểm đều cần dữ kiện trích từ văn bản mà AD-3 chặn — CRITICAL-3 |
| FR-32 Khớp tin dán với tin đã thu thập | ~ | **Nơi sống của phép so khớp không được cố định** — MEDIUM-1 |
| FR-33 Bản đồ 3D theo tỷ trọng | **✗ (mâu thuẫn)** | **AD-17 mâu thuẫn trực tiếp** — CRITICAL-5. Khóa `stat_cells` thiếu thành phố — MEDIUM-6 |
| FR-34 Bảng chi tiết thành phố | ~ | AD-5/AD-17; cần `meta` theo từng dòng — CRITICAL-5 |
| FR-35 Đi tiếp sang Cố vấn | ~ | Cùng cờ với FR-18 — MEDIUM-4 |
| FR-36 Chú thích nguồn + chế độ 2D | ✓ | `meta.sources[]` của AD-17; capability map ghi "deck.gl + chế độ bảng" |
| FR-37 Năm loại thẻ Insights | **✗ một phần** | Xem dưới — thiếu thực thể công ty/ngành và bảng đồng xuất hiện |
| FR-38 Ngưỡng hiển thị thẻ | ~ | AD-10 `Binds` có FR-38 nhưng 5 điểm % không trong Rule |
| FR-39 Câu kết luận của thẻ | ~ | AD-8 phủ "không LLM". Mẫu câu không nằm trong `domain/` — xem dưới |
| FR-40 Lọc thẻ theo vai trò | ~ | Đọc vai trò từ `localStorage` — CRITICAL-1 |
| FR-41–FR-45 Chế độ thử nghiệm | ✓ | AD-18 rất tốt (bảng riêng, cờ `is_eval`, fixture JSON tĩnh có phiên bản) |
| Trang công khai SEO/GEO | ~ | AD-13/AD-14 bọc tốt, **nhưng chưa có FR** — spine đã tự nêu ở Câu hỏi mở 1 |

### 5.2 Các khoảng trống phủ cần nêu riêng

#### [HIGH-14] FR-37 — thiếu thực thể công ty/ngành, thiếu bảng đồng xuất hiện

FR-37 có 5 loại thẻ. Hai trong số đó không có chỗ nào trong sơ đồ thực thể cốt lõi:

- **"Bộ kỹ năng hay đi cùng nhau"** cần một bảng cặp kỹ năng đồng xuất hiện theo ô thống kê. ER có `STAT_SKILL_RATE` và `STAT_PERCENTILE`, **không có `STAT_SKILL_PAIR`**. AD-12 nói đồng xuất hiện "nằm ở bảng tổng hợp" nhưng không đặt tên bảng — nên dev C sẽ tự tạo, có thể với khóa khác (không có `snapshot_id`? vi phạm AD-4) và quy tắc ngưỡng khác.
- **"Ngành và nhà tuyển dụng nổi bật"** cần **thực thể công ty và ngành**. ER **không có cả hai**.

Và thực thể công ty không chỉ FR-37 cần:
- FR-4 ghép trùng giữa các nguồn dựa trên "**tên công ty đã chuẩn hóa**" — tức cần chuẩn hóa tên công ty, một bài toán có thật (biến thể "FPT Software", "FPT Soft", "Công ty TNHH FPT Software");
- FR-46 kiểm "có tên công ty";
- FR-31 D7 kích hoạt khi "tin không nêu tên công ty";
- FR-47 nói phần người dùng thấy gồm "các trường ngắn (chức danh, **công ty**, thành phố, khoảng lương)".

Vậy chuẩn hóa tên công ty là một phép dùng chung bởi **ba tính năng ở ba sprint khác nhau** (dedupe sprint 1–2, Soi tin sprint 4, Insights sprint 6) và nó **không có AD, không có thực thể, không có nơi sống**. Đây là cùng dạng lỗi mà AD-2 chặn cho kỹ năng, nhưng không ai chặn cho công ty. Rất có thể ba bản cài đặt khác nhau, và khi đó FR-4 ghép sai → mọi con số sai.

> **Đề xuất:** thêm `COMPANY` (và `INDUSTRY` nếu đủ thời gian) vào sơ đồ thực thể; thêm `stat_skill_pairs` vào danh sách bảng tổng hợp; thêm "chuẩn hóa tên công ty" vào danh sách hàm thuần trong `domain/` của cây mã nguồn; và đưa nó vào registry của AD-2 (xem §6.2).

#### [MEDIUM-18] FR-16 — bản tải về không có nhà, và nó cũng là điểm kích hoạt của FR-43

FR-16 đòi tải về bản tóm tắt gồm danh sách kỹ năng cần bổ sung vào CV + lộ trình học theo chặng kèm link, và **"ghi rõ vai trò mục tiêu, cỡ mẫu và ngày của dữ liệu"**. NFR §5 còn đòi "bản tóm tắt tải về" phải có lưu ý về độ phủ dữ liệu.

Spine: không AD, không convention, không dòng nào trong cây mã nguồn. Brief gợi ý "in trình duyệt ra PDF là phương án rẻ nhất" nhưng spine không chốt. Hai hệ quả:

1. Yêu cầu "cỡ mẫu + ngày + lưu ý độ phủ" là **đúng tinh thần AD-17** nhưng AD-17 chỉ nói về *response của API*. Bản tải về là một hiện vật thứ hai mang số liệu, và nó không chịu bất biến nào.
2. **FR-43 nói modal cuối phiên "tự bật khi người thử bấm 'Lưu kết quả' (FR-16) hoặc 'Copy link chia sẻ' (FR-15)"** — tức tính năng của dev A (sprint 3) là điểm kích hoạt của tính năng dev C (sprint 6), qua một sự kiện mà không hợp đồng nào mô tả. Nếu dev A làm nút tải về bằng `window.print()` thuần, dev C không có móc nào để chặn vào. Đây là phân kỳ liên-sprint kiểu kinh điển, và nó rơi đúng vào đường đo SM-1/SM-2/SM-3.

#### [MEDIUM-17] FR-25 và FR-31 — có cơ chế sẵn (AD-8) mà không dùng

AD-8 đã chứng minh một khuôn mẫu rất tốt: "văn bản do LLM sinh không được chứa chữ số nào ngoài chữ số trong tên công nghệ; **có kiểm thử tự động chặn**" — biến một yêu cầu về câu chữ thành một bất biến kiểm được.

Hai yêu cầu cùng dạng đang bị bỏ ngoài:
- FR-25: "Không câu chữ nào trên giao diện hay trong lời dẫn chứa lời khuyên bỏ qua một kỹ năng";
- FR-31: "Không câu chữ nào dùng các từ **'lừa đảo', 'tin giả', 'tin ma'**".

Cái thứ hai là một danh sách từ cấm hữu hạn, kiểm được bằng đúng một test grep trên mọi chuỗi hiển thị — rẻ hơn cả test của AD-8. Và nó bảo vệ một cam kết sản phẩm quan trọng (PRD §7: "không kết luận tin thật hay giả"), với rủi ro thật là một dev viết câu chữ cảnh báo quá tay ở sprint 4 rồi không ai rà lại ở sprint 8.

> **Đề xuất:** mở rộng AD-8 (hoặc thêm một dòng convention) thành: mọi chuỗi hiển thị tiếng Việt nằm trong **một bảng/một file** (convention "Chuỗi hiển thị tiếng Việt tra từ bảng" đã nói đúng hướng), và cổng CI chạy một test danh sách từ cấm trên bảng đó.

#### [MEDIUM-19] FR-39 — mẫu câu Insights không nằm trong `domain/`

Capability map đặt Insights ở `haido_core/steps/` ("tính sẵn thành thẻ"). Cây mã nguồn liệt kê 9 phép trong `domain/` và **không có mẫu câu Insights**. Nhưng FR-39 là một phép **tất định có ranh giới khoảng** ("trên 50%", "30–50%", "dưới 10%") với yêu cầu kiểm thử "cho từng ranh giới khoảng" và "cùng snapshot luôn cho cùng câu kết luận" — tức đúng hồ sơ của một hàm thuần thuộc `domain/`, cùng loại với "dấu hiệu D1–D7" và "chất lượng JD" đã được liệt kê.

Nhỏ, nhưng nó là biểu hiện của một vấn đề lớn hơn: `domain/` có một **danh sách liệt kê** chứ không có **tiêu chí thuộc về**, nên bất cứ phép mới cũng có thể bị đặt sai chỗ (xem §6.2).

### 5.3 Kết luận mục 5

**Phủ tốt ở phần lõi, hổng ở phần biên văn bản và phần hiện vật phụ.**

- Nhóm FR được phủ xuất sắc: FR-19 đến FR-24 (Cố vấn), FR-41 đến FR-45 (thử nghiệm), FR-8, FR-9, FR-15.
- **Ba FR hoàn toàn không có AD/convention chạm tới dù lẽ ra phải có: FR-2, FR-5, FR-14.** Cộng FR-16 và FR-46 ở mức gần như không.
- **Một AD (AD-3) tạo ra khoảng trống cho 6 FR cùng lúc** (FR-6 phần năm kinh nghiệm, FR-27, FR-30 phần năm kinh nghiệm, FR-31 D5–D7, FR-46, FR-8 phần trích lương). Sửa một AD đóng được cả sáu — đây là sửa có đòn bẩy cao nhất trong bài rà soát.
- **Một thực thể bị thiếu (công ty/ngành) ảnh hưởng 4 FR** (FR-4, FR-31 D7, FR-37, FR-46).
- Khoảng trống SEO được spine **tự nêu** ở Câu hỏi mở 1 với hành động rõ ("Phải làm trước khi chia epic") — cách xử lý đúng, ghi nhận.

---

## 6. Có AD nào mâu thuẫn với AD khác, hoặc hai AD nói cùng một điều?

### 6.1 Mâu thuẫn

#### [HIGH-15] AD-1 vs phần Triển khai vs AD-14 — `web` có biết Postgres hay không?

Ba chỗ nói ba điều khác nhau:

| Nơi | Nói gì |
|---|---|
| Bảng bốn tầng | "Giao diện · `web/` · Biết hợp đồng HTTP của `haido_api`; **không biết Postgres**" |
| Sơ đồ của AD-1 | `web --> api` và **không có cạnh** `web --> pg` |
| Sơ đồ Triển khai | `web --> api` **và** `web --> pg` |
| Văn bản sau sơ đồ Triển khai | "`web` đọc Postgres **chỉ** lúc sinh trang nội dung công khai (AD-14)" |
| AD-14 | "template trang công khai chỉ được đọc bảng tổng hợp" — tức **có** đọc DB |

Quyết định thực chất (web đọc Postgres chỉ khi build trang ISR, qua bảng `stat_*`) là hợp lý và được giải thích rõ ở phần Triển khai. Vấn đề là **Rule của AD-1 không khớp với nó**, và AD-1 là AD duy nhất tuyên bố "có kiểm thử chặn". Hệ quả thực tế: khi dev web ở sprint 5 cần đọc `stat_*` để sinh trang, hoặc kiểm thử của AD-1 sẽ đỏ (và bị ai đó nới ra, làm AD-1 mất lực toàn bộ), hoặc kiểm thử đó chưa từng phủ `web/` (vì nó là TypeScript, import-linter không thấy) — trong đó khả năng thứ hai có nghĩa AD-1 chỉ phủ Python và spine không nói ra điều đó.

> **Sửa:** thêm cạnh `web --> pg` vào sơ đồ AD-1 với nhãn "chỉ `stat_*`, chỉ lúc build (AD-14)", sửa ô "Được biết gì" của tầng Giao diện cho khớp, và nói rõ kiểm thử của AD-1 phủ Python; phần `web/` được cưỡng chế bằng **quyền DB**: tài khoản Postgres của `web` chỉ có `SELECT` trên `stat_*`. Đó vừa sửa mâu thuẫn, vừa biến AD-14 từ "cưỡng chế được nếu ai đó nghĩ ra cách" thành "cưỡng chế bằng hạ tầng".

#### [HIGH-16] AD-4 (bất biến) vs FR-47 (yêu cầu gỡ)

AD-4: "Hàng thuộc snapshot đã công bố **không bao giờ** bị sửa hay xóa."
FR-47: "Một yêu cầu gỡ hợp lệ được xử lý, và **tin liên quan biến khỏi số liệu công khai từ snapshot kế tiếp**", với cam kết 48 giờ.

Hai câu này **hòa giải được** (gỡ khỏi snapshot *kế tiếp*, không sửa snapshot cũ) nhưng spine chưa hòa giải, và cơ chế thì hoàn toàn thiếu: cần một **danh sách chặn bền** (theo công ty / URL / nguồn) mà bước `ingest` hoặc `aggregate` tham chiếu mỗi đêm, cộng một quyết định về việc trang công khai đã index có còn chứa dữ liệu đó không. Không có nó, người xử lý yêu cầu gỡ ở tuần 6 sẽ làm việc duy nhất rõ ràng với họ — `DELETE` trong Postgres — tức phá đúng bất biến quan trọng nhất của spine, dưới áp lực pháp lý và deadline 48 giờ.

Thêm một lớp: trang công khai là tĩnh (AD-13). Gỡ dữ liệu khỏi snapshot kế tiếp **không** tự gỡ nó khỏi trang đã sinh, nếu lệnh làm mới không chạy hoặc trang không được sinh lại.

> **Sửa:** một dòng vào AD-4: *"Yêu cầu gỡ (FR-47) không bao giờ sửa snapshot cũ. Nó ghi một hàng vào `takedown_blocklist`; bước `ingest` loại mọi tin khớp danh sách đó khỏi snapshot kế tiếp, và bước làm mới trang (AD-13) sinh lại trang công khai."*

#### [CRITICAL-5 đã nêu] AD-17 vs FR-33

Mâu thuẫn trực tiếp về quy tắc n < 30. Đây là mâu thuẫn giữa một AD và PRD, không giữa hai AD, nhưng nó biểu hiện ra đúng như một mâu thuẫn nội bộ vì AD-17 `Binds: FR-34` và FR-33 nằm trong `Binds` của AD-5/AD-17 qua bảng capability.

#### [MEDIUM-20] AD-5 (tiêu đề) vs FR-32 / FR-31 D4

Tiêu đề AD-5: *"Tầng phục vụ **chỉ đọc**; không tính con số thị trường tại chỗ"*. Rule thì hẹp hơn và chính xác hơn (cấm **tổng hợp** trên bảng tin, không cấm **đọc**). Nhưng:

- FR-32 đòi API tìm trong dữ liệu đã thu thập một tin trùng với tin dán — đọc bảng tin/cụm **lúc chạy**;
- FR-31 D4 đòi đọc vòng đời tin ("≥ 2 lần đăng lại hoặc xuất hiện liên tục qua ≥ 30 snapshot") — "xuất hiện liên tục qua ≥ 30 snapshot" là một phép đếm trên lịch sử, rất gần ranh giới "tổng hợp";
- FR-47 nói người dùng thấy "các trường ngắn (chức danh, công ty, thành phố, khoảng lương), kèm link về tin gốc" — tức API trả dữ liệu tin thô.

Không vi phạm chữ của Rule, nhưng một dev đọc tiêu đề sẽ kết luận sai hoặc sẽ dừng lại hỏi. Và "xuất hiện liên tục qua ≥ 30 snapshot" thực sự nên được **tính sẵn** vào vòng đời tin ở bước đêm, không tính lúc chạy — spine nên nói ra, vì đó là một quyết định thật.

> **Sửa:** đổi tiêu đề AD-5 thành *"Tầng phục vụ không tính con số thị trường tại chỗ"* và thêm một dòng cho phép tường minh: *"API được đọc bảng tin và cụm tin cho hai mục đích đã nêu — so khớp tin dán (FR-32) và các trường ngắn hiển thị kèm link gốc (FR-47). Vòng đời tin dùng cho D4 được tính sẵn ở bước đêm và lưu thành cột, không đếm lúc chạy."*

#### [MEDIUM-12 đã nêu] AD-10 / convention "Không có nơi cấu hình thứ ba" vs `haido_core/vocab/`

Ba nơi trong thực tế: biến môi trường, bảng cấu hình có phiên bản, và file dữ liệu có phiên bản trong repo (`vocab/`, `eval_fixtures/`). Convention tuyên bố chỉ có hai.

#### [HIGH-6 đã nêu] Stack (Batch API) vs AD-4 (một transaction cuối lượt chạy)

Không phải mâu thuẫn logic, mà là hai quyết định chưa được hòa giải với nhau — và cả hai đều ở trong spine.

#### [MEDIUM-21] AD-10 (θ là dữ liệu, đổi không cần triển khai lại) vs PRD FR-9 (θ phải **đóng băng** trước Sprint 6)

AD-10 làm việc đổi θ trở nên dễ — đó là mục đích, và đúng với FR-9 ("đổi θ_core thì nhóm kỹ năng thay đổi ngay từ lần tính kế tiếp, không cần triển khai lại"). Nhưng FR-9 còn có một yêu cầu thứ hai mà AD-10 không phủ: *"θ được hiệu chỉnh **một lần** ở Sprint 2, rồi **đóng băng** trước đợt thử nghiệm ở Sprint 6–7. Mọi lần đổi θ sau đó phải được **ghi lại kèm lý do**"* — và PRD nói rõ lý do: để θ không bị dùng như một cách làm đẹp SM-1 (SM-C2).

Tức FR-9 đòi một **thay đổi dễ nhưng để lại dấu**. AD-10 chỉ làm phần "dễ": nó nói mỗi snapshot lưu `config_version`, nhưng không đòi bảng cấu hình lưu **ai đổi, khi nào, và vì sao**. Với một tham số mà PRD nêu tên như một rủi ro liêm chính nghiên cứu, đây là một khoảng trống đáng sửa bằng hai cột.

> **Sửa:** thêm vào AD-10: bảng cấu hình chỉ cộng thêm (append-only), mỗi phiên bản lưu `changed_at`, `changed_by`, `reason` **không rỗng**; không bao giờ `UPDATE` một hàng cấu hình đã được một snapshot đã công bố tham chiếu.

### 6.2 Hai AD nói cùng một điều / nên gộp

#### [HIGH-17] AD-2 + AD-6 + AD-7 là **một** bất biến được viết ba lần — và việc viết ba lần chính là nguyên nhân của nhiều khoảng trống ở mục 5

Ba AD này có cùng hình dạng Rule:

| AD | Phép | Rule |
|---|---|---|
| AD-2 | văn bản → mã kỹ năng → nhóm kỹ năng | "chỉ tồn tại trong `haido_core/domain/`"; API/pipeline/frontend không cài lại |
| AD-6 | chọn ô thống kê + thứ tự quay về | "**một hàm duy nhất** trong `domain`"; "không nơi nào khác được dựng lại" |
| AD-7 | thứ tự lộ trình học (4 tầng) | "chỉ tồn tại ở Python"; frontend không cài lại |

Không nên gộp một cách máy móc — mỗi AD có `Prevents` riêng và cụ thể, và việc nêu tên ba phép nguy hiểm nhất có giá trị dạy học thật. **Nhưng** cách viết hiện tại tạo ra một lỗ hổng có hệ thống: nó liệt kê ba phép, và **ngụ ý rằng những phép không được liệt kê thì không chịu bất biến này**. Chính xác là chuyện đã xảy ra. Những phép dùng chung sau cũng cần đúng bất biến đó và **không** có AD nào:

| Phép dùng chung không được liệt kê | Ai dùng | Sprint |
|---|---|---|
| So khớp tin trùng (FR-4 / FR-32) | bước dedupe; Soi tin | 1–2 và 4 |
| Chuẩn hóa tên công ty (FR-4, FR-31 D7, FR-37, FR-46) | dedupe; Soi tin; Insights | 1–2, 4, 6 |
| Mức khớp có trọng số (FR-28) | Soi tin (và bản tải về FR-16?) | 4 |
| Mẫu câu Insights theo khoảng (FR-39) | bước Insights | 6 |
| Danh sách kiểm chất lượng JD (FR-46) | Soi tin | 4 |
| Chuẩn hóa lương (FR-8) | bước salary; Soi tin (đặt lương tin dán vào mốc) | 1–2 và 4 |
| Xóa PII người đăng tin (FR-5) | crawl/ingest | 1 |
| Phân loại vai trò/cấp bậc (FR-7) | bước classify; Soi tin FR-27 | 2 và 4 |

Cột "Sprint" là phần quan trọng: **mỗi phép trong bảng này được hai đơn vị khác nhau cần, ở hai sprint cách nhau 2–4 tuần.** Đó là định nghĩa của một điểm phân kỳ.

> **Đề xuất (sửa có đòn bẩy cao nhất về mặt cấu trúc):** giữ AD-2, AD-6, AD-7 làm ba ví dụ có `Prevents` riêng, nhưng **thêm một AD bao trùm kèm registry**: *"**AD-25 — Mỗi phép nghiệp vụ dùng chung có đúng một bản cài đặt, trong `haido_core/domain/`.** Một phép thuộc nhóm này khi nó được hai tính năng trở lên cần, hoặc khi hai con số của nó phải khớp nhau. Bảng dưới đây là danh sách đóng; thêm một phép dùng chung mà không thêm dòng vào bảng là lỗi review."* Rồi đặt bảng 8 dòng ở trên (cộng ba phép của AD-2/6/7) vào spine. Như vậy spine chuyển từ **liệt kê** sang **có tiêu chí thuộc về**, và các khoảng trống FR-4/FR-5/FR-7/FR-46 ở mục 5 tự đóng.

#### [MEDIUM-22] AD-13 + AD-14 — chồng lấn nhẹ, nên để riêng nhưng sửa `Binds`

Cả hai nói về trang công khai. `Prevents` khác nhau thật (số lệch đêm vs JD thô bị index), nên **không nên gộp**. Nhưng:
- `Binds` của AD-14 có **FR-47**, trong khi FR-47 là trang chính sách dữ liệu + kênh gỡ — không phải một trang đọc bảng tổng hợp. Liên kết này sai hướng: cái AD-14 thực sự bảo vệ cho FR-47 là **§6.2** (không đăng lại toàn văn JD), và §6.2 đã có trong `Binds`. Nên bỏ FR-47 khỏi AD-14 và cho FR-47 một nơi sống thật (xem HIGH-16 + MEDIUM-18).

#### [MEDIUM-23] AD-8 + AD-9 — mệnh đề "ba chỗ gọi" đặt sai AD

AD-8 (nội dung do LLM sinh) chứa câu *"LLM chỉ được gọi ở ba chỗ lúc chạy…"* — đó là một phát biểu về **nơi gọi**, thuộc địa hạt của AD-9 (cổng trích xuất) và được cưỡng chế bằng cổng của AD-9, không bằng bất kỳ cơ chế nào của AD-8. Hệ quả nhỏ nhưng thật: ai đọc AD-9 để biết "cổng này được gọi từ đâu" sẽ không thấy câu trả lời ở đó; và khi CRITICAL-3 được sửa (mở rộng những gì cổng trả về), người sửa sẽ phải nhớ sửa cả hai AD.

> **Đề xuất:** chuyển mệnh đề "ba chỗ gọi (và một bước offline)" sang AD-9, giữ AD-8 thuần về *nội dung* (không số, không thứ tự, không câu kết luận).

#### [thấp] AD-11 vs convention "Đột biến trạng thái" và "Ghi log"

Convention *"Đột biến trạng thái: chỉ `haido_core/steps/` được ghi vào bảng thị trường. `haido_api` chỉ ghi vào `anon_events` và hai bảng `eval_*`"* là một phát biểu **sắc hơn và dễ kiểm hơn** chính Rule của AD-11. Không phải trùng lặp có hại (convention nhắc lại AD là bình thường), nhưng câu sắc hơn nên nằm trong AD, vì AD là nơi người đọc tìm bất biến. Tương tự, convention `Ghi log` ("không bao giờ ghi body của request, văn bản CV, hay nội dung JD") trùng một phần với AD-11.

### 6.3 Kết luận mục 6

- **6 mâu thuẫn**, trong đó 1 là mâu thuẫn thẳng giữa AD và PRD (AD-17 ↔ FR-33, critical), 1 là mâu thuẫn nội bộ giữa ba chỗ trong cùng spine (AD-1 ↔ Triển khai ↔ AD-14, high), 1 là bất biến vs yêu cầu pháp lý (AD-4 ↔ FR-47, high), và 3 là tiêu đề/phạm vi nói rộng hơn Rule.
- **Không có hai AD nào trùng lặp đến mức nên gộp.** Nhưng AD-2/AD-6/AD-7 là ba lần phát biểu cùng một bất biến, và cách khắc phục đúng **không** phải gộp lại mà là **thêm tiêu chí thuộc về + registry** — vì chính việc liệt kê thay cho tiêu chí đã sinh ra phần lớn khoảng trống ở mục 5.

---

## 7. Danh sách sửa, theo thứ tự ưu tiên

### Chặn — phải sửa trước khi chia epic

| # | Sửa | Vì sao chặn |
|---|---|---|
| 1 | **Sửa AD-3**: cổng trả về "dữ kiện trích nguyên văn hoặc có cấu trúc", không chỉ lượt nhắc kỹ năng; vẫn cấm mã kỹ năng/vai trò/cấp bậc/phán xét | Mở khóa FR-6, FR-8, FR-27, FR-30, FR-31 D5–D7, FR-46. Không sửa thì epic Soi tin (sprint 4) không chia được |
| 2 | **Sửa AD-17**: `meta` toàn cục + `cell` theo từng phần tử; thêm `n_with_salary`/`n_with_experience`/`ci`/`no_prereq_graph`; nêu ngoại lệ n<30 cho FR-33 | AD-17 là hợp đồng mà 4 tính năng và 3 dev tiêu thụ. Sai ở đây là sai 4 chỗ |
| 3 | **Thêm AD-19/AD-20**: hợp đồng `localStorage` (một tiền tố, một danh sách khóa, `schema_version`) + enum đóng cho mã sự kiện ẩn danh, kèm bảng mã → SM | Không có thì FR-14 sai lặng lẽ và FR-45/SM-1/2/3/9/12 — toàn bộ chương Thực nghiệm — không xuất được số |
| 4 | **Thêm AD-21 (cổng kiểm thử là một)** và sửa dòng Deferred về CI | 6 AD đang dựa vào một cổng chưa tồn tại |
| 5 | **Thêm AD-24 (sao lưu)** | Snapshot lịch sử và dữ liệu thử nghiệm không tái tạo được; 1 VPS, 1 volume |
| 6 | **Thêm AD-25 + registry phép dùng chung**, gồm FR-4/FR-32 so khớp, chuẩn hóa tên công ty, FR-5 scrub, FR-7 phân loại, FR-28, FR-39, FR-46 | Đóng một lượt phần lớn khoảng trống của mục 5, và cho spine một tiêu chí thay vì một danh sách |

### Cao — sửa trong cùng lượt chỉnh spine

7. **Thêm AD-22**: một cổng HTTP ra nguồn duy nhất (FR-2), và khoanh mã né phát hiện bot vào module tắt được (R1–R4).
8. **Thêm AD-23**: di trú schema chỉ cộng thêm, một head Alembic, chạy ở entrypoint.
9. **Sửa AD-1**: thêm cạnh `web --> pg` có nhãn; nói rõ phần `web/` cưỡng chế bằng quyền DB; sửa bảng bốn tầng cho khớp.
10. **Sửa AD-4**: chính sách thất bại một phần (FR-1/FR-3), cơ chế gỡ theo danh sách chặn (FR-47), hạn chót chờ Batch API, và cơ chế bất biến bằng quyền DB.
11. **Sửa AD-11**: nêu cơ chế cho "không chạm đĩa" (spool size / Caddy 5 MB) và thêm kiểm thử `/tmp`.
12. **Sửa AD-9**: ngân sách thời gian, không thử lại đường đồng bộ, một mã lỗi dùng chung, giới hạn đồng thời, và lưu `input_tokens`/`output_tokens` cho SM-C5.
13. **Thêm vào conventions**: giới hạn tốc độ + kích thước body ở Caddy cho hai route POST; Dagster UI không route ra Internet.
14. **Thêm `COMPANY`/`INDUSTRY` và `stat_skill_pairs`** vào sơ đồ thực thể (FR-4, FR-31 D7, FR-37, FR-46).
15. **Thêm vào conventions**: lược đồ đường dẫn trang công khai (dành chỗ cho phần hoãn).

### Trung bình — nên có, không chặn

16. AD-6: nói rõ `scope` mang chiều thành phố (hoặc thêm cột).
17. AD-10: bổ sung n=30, 60 ngày, 5 điểm %, B, ngưỡng của FR-30 và FR-1 vào danh sách; bảng cấu hình append-only có `reason`.
18. AD-2: câu cho phép tường minh cho ô tìm kiếm kỹ năng (FR-13/FR-42).
19. AD-13: làm mới có thử lại + xác minh `snapshot_date`.
20. AD-5: sửa tiêu đề; cho phép tường minh đọc tin thô cho FR-32/FR-47; D4 tính sẵn.
21. AD-8: chuyển mệnh đề "ba chỗ gọi" sang AD-9; thêm test danh sách từ cấm cho FR-25/FR-31.
22. AD-14: bỏ FR-47 khỏi `Binds`; cho FR-47 một nơi sống thật.
23. Conventions: khóa sắp xếp toàn phần cho mọi danh sách top-N; vòng quay log Docker; snapshot hạt giống dùng chung cho dev; ngân sách RAM theo service; giờ chạy đêm và quy tắc không triển khai trùng giờ.
24. AD-12: bỏ dấu `[ADOPTED]` còn sót trong tiêu đề.
25. Deferred: viết lại ba dòng (SEO, hàng đợi, CI/CD) cho hẹp hơn, nêu rõ phần **không** hoãn; thêm một dòng cho mảng sao lưu nếu phần nào của nó bị hoãn có ý thức.

---

## 8. Ghi nhận những gì spine làm đúng

Để bài rà soát không bị đọc sai thành "tài liệu này tệ":

- **Paradigm có lý do, và lý do đó là lý do đúng.** "Ba lời hứa trung tâm — tất định, truy vết, chạy trên snapshot cũ khi lỗi — là hệ quả miễn phí của việc tách bên ghi theo lô khỏi bên đọc chỉ-đọc. Làm theo kiểu CRUD thì phải tự dựng lại cả ba." Đây là một lập luận kiến trúc thật, không phải một nhãn.
- **`Prevents` cụ thể tới mức dùng được.** Phần lớn AD nêu một thất bại có thể tưởng tượng ra, kèm hậu quả neo vào một chỉ số SM hay một mục PRD. AD-11 và AD-3 là hai ví dụ tốt nhất.
- **Danh sách "đã loại" kèm lý do có số.** Airflow bị loại vì sàn 4 GB RAM đánh nhau với §6.4; pgvector bị loại sau khi rà 47 FR. Đây là thứ cứu nhóm khỏi tranh luận lại trong sprint 5, và cứu nhóm trước câu hỏi của hội đồng.
- **Bảng Stack có ngày tra cứu.** "Kiểm ngày 03/11/2026 trên PyPI, npm và postgresql.org" — biến bảng phiên bản từ một danh sách thành một khẳng định có thể kiểm lại.
- **Câu hỏi mở đúng kiểu.** Năm câu, mỗi câu có hệ quả, có số (30–50 ms vs 250 ms), có nơi quyết (Sprint 2), và câu số 1 tự thừa nhận lỗ hổng lớn nhất của chính spine với một hành động dứt khoát ("Phải làm trước khi chia epic"). Rất ít spine tự tố mình như vậy.
- **AD-8, AD-15, AD-17 (hình dạng), AD-18 là bốn AD mà Rule gần như hoàn hảo về mặt cưỡng chế** — Rule được viết dưới dạng một điều kiện mà một kiểm thử có thể đọc.

Spine này không cần viết lại. Nó cần **một lượt sửa 6 điểm chặn** — trong đó 2 điểm (AD-3, AD-17) là sửa câu chữ của Rule đã có, 3 điểm là thêm AD mới ngắn, và 1 điểm là tái cấu trúc AD-2/6/7 thành registry. Sau lượt đó, nó đủ vững để chia epic cho 3 dev × 8 tuần.
