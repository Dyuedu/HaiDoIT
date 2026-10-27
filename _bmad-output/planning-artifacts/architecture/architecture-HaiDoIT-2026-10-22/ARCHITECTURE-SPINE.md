---
name: Hải Đồ IT
type: architecture-spine
purpose: build-substrate
altitude: initiative
paradigm: modular monolith
scope: Web v1 Hải Đồ IT
status: final
created: 2026-10-22
updated: 2026-10-27
binds: []
sources:
  - _bmad-output/planning-artifacts/prds/prd-HaiDoIT-2026-10-22/prd.md
  - _bmad-output/planning-artifacts/prds/prd-HaiDoIT-2026-10-22/addendum.md
  - _bmad-output/planning-artifacts/ux-designs/ux-HaiDoIT-2026-10-22/DESIGN.md
  - _bmad-output/planning-artifacts/ux-designs/ux-HaiDoIT-2026-10-22/EXPERIENCE.md
companions: []
---

# Architecture Spine — Hải Đồ IT

## Design Paradigm

Modular monolith. Một tiến trình Python giữ luật và dữ liệu. Web là client riêng, chỉ vẽ những gì tiến trình đó trả.

`backend/` là monolith: tính số, nạp tin, gửi thư, chạy đồ thị agent. `frontend/` là Next.js. `scraper/` ghi object lên Silo, không mở Postgres và không mở Neo4j. Lệnh nạp trong `backend/` đọc object đó.

## Capability → Architecture Map

| Capability / Area | Lives in | Governed by |
| --- | --- | --- |
| Bản đồ nhu cầu | Agent Bản đồ gọi tool, Next vẽ | AD-2, AD-6, AD-12, AD-14, AD-16, AD-18, AD-22 |
| Học gì tiếp? | Agent Học gì tiếp | AD-6, AD-10, AD-15, AD-16, AD-18, AD-22 |
| Lộ trình 90 ngày | Agent Lộ trình gọi `roadmap_frame` rồi viết câu | AD-7, AD-8, AD-18, AD-22 |
| So sánh offer (hoãn v1.1) | Trình duyệt, bộ số từ FastAPI | AD-9 |
| Soi tin | Agent Soi tin gọi `lookup_posting` | AD-4, AD-6, AD-9, AD-18, AD-21, AD-22 |
| GraphRAG | neo4j-graphrag truy xuất, agent viết | AD-19, AD-22 |
| Danh kỹ năng | Supabase, chiếu sang Neo4j | AD-10, AD-19 |
| Cào và nạp tin | scraper/, Silo, Redis, lệnh nạp | AD-4, AD-5, AD-20, AD-21 |
| Thư mở lại | FastAPI trên máy chạy web | AD-8, AD-11 |
| Xu hướng kỹ năng | Một lớp trong Supabase | AD-16 |

## Invariants & Rules

```mermaid
flowchart LR
  scraper[scraper] --> lake[Silo]
  lake --> loader[lệnh nạp]
  loader --> db[(Supabase)]
  loader --> graph[(Neo4j)]
  scraper --> queue[Redis]
  queue --> loader
  api[FastAPI] --> db
  api --> graph
  api --> cache[Redis]
  api --> agents[LangGraph]
  agents --> model[Ollama]
  api --> mail[hộp thư nhóm]
  web[Next.js] --> api
```

### AD-1 — Hai phần trong một repo [ADOPTED]

- **Binds:** all
- **Prevents:** gộp thành một app Next.js, hoặc tách hai repo
- **Rule:** `frontend/` là Next.js 16.4.2. `backend/` là FastAPI 0.159.1 trên Python 3.12. Cùng một repo.

### AD-2 — Web không giữ luật số [ADOPTED]

- **Binds:** frontend
- **Prevents:** Next.js tự tính số tin, lương, dự báo, hoặc tự nối database
- **Rule:** Next.js chỉ gọi HTTP của FastAPI và vẽ payload. Chuỗi nối Supabase chỉ nằm trong `backend/`, qua SQLModel 0.0.48. Phép tính duy nhất trên trình duyệt là So sánh offer, theo AD-9.

### AD-3 — Một Supabase dùng chung [ADOPTED]

- **Binds:** all
- **Prevents:** mỗi máy code một Postgres, hoặc trình duyệt gọi API tự sinh của Supabase
- **Rule:** Một Postgres trên Supabase, gói trả phí. Máy chạy web và máy code cùng nối vào đó. Chỉ dùng Postgres. Không dùng đăng nhập Supabase. Trình duyệt không nối Supabase.

### AD-4 — Một chỗ ghi tin [ADOPTED]

- **Binds:** tin tuyển dụng
- **Prevents:** scraper và web cùng ghi bảng tin, hoặc hai màn đếm hai tập đang mở
- **Rule:**
  - **Người ghi:** Lệnh nạp là chỗ duy nhất ghi bảng `job_posting`. Không đọc bảng `job_postings` của SkillNexus. VietJobs không vào tập đang mở.
  - **source_id:** Lệnh nạp tự tính SHA-256 hex thường của `source`, một ký tự U+001F, rồi `source_url` đã cắt khoảng trắng, theo `jobboards.compute_source_id`. Không dùng hàm cùng tên trong `vietjobs_loader`. `source_id` có sẵn trong dòng file thì bỏ qua.
  - **Thấy lại:** Thấy lại trong một lần nạp thành công thì tăng `seen_count` thêm một, cập nhật `last_seen`, giữ `first_seen`. Cùng nội dung byte thì không tăng lần thứ hai.
  - **Đang mở:** Có trong file của lần nạp thành công gần nhất. Tin vắng mặt được giữ, `is_open` là sai, không đếm trên bản đồ, không xóa.
  - **Mốc:** Lần nạp thành công ghi `ingest_run.succeeded_at` chỉ sau khi Neo4j đã cập nhật, theo thứ tự bên dưới. Chân trang đọc mốc mới nhất thành ngày lịch Asia/Ho_Chi_Minh. Không suy mốc từ `last_seen` hay `posted_on`.
  - **Thứ tự nạp:** Mở transaction Postgres và ghi các dòng `job_posting` cùng seed bảng `skill`, chưa commit. Cập nhật Neo4j từ các dòng `skill` của transaction đó. Neo4j lỗi thì rollback Postgres, xóa cache số gộp trên Redis, ghi log, và không ghi `ingest_run.succeeded_at`. Neo4j xong thì commit Postgres và ghi `ingest_run.succeeded_at`.
  - **Soi tin:** Tra bằng `source_url` đã lưu, khớp sau khi cắt khoảng trắng, không tra bằng `source_id`. Tin trùng là tin đang mở khác, khác link, cùng tập kỹ năng, thành phố, cấp bậc và khoảng lương. Trước tuần 1 không gắn nhãn tin treo.
  - **Cột:** `source_id`, `source`, `skills`, `city`, `role`, `level`, `salary_min_vnd`, `salary_max_vnd`, `salary_min_usd`, `salary_max_usd`, `posted_on`, `source_url`, `seen_count`, `first_seen`, `last_seen`, `is_open`. `skills` là mảng chữ. Không giữ mô tả, tiêu đề, tên công ty, tên người tuyển, liên hệ người tuyển.

### AD-5 — Cào và nạp trao nhau bằng file [ADOPTED]

- **Binds:** scraper, lệnh nạp
- **Prevents:** `backend/` gọi thẳng code SkillNexus, hoặc một bên bỏ kênh ATS
- **Rule:**
  - **Chỗ code:** Code cào nằm trong repo này. SkillNexus chỉ là chỗ đang có code để chuyển sang. Cào và lệnh nạp không gọi nhau.
  - **Ảnh:** Mỗi lần đủ kênh thì ghi đè `open-jobs/open-jobs.jsonl` trên Silo. Kênh lỗi thì không ghi đè. Mô tả thô ghi vào `bronze/` theo AD-21. Xong thì đẩy Redis theo AD-20.
  - **Dòng ảnh:** `source`, `skills`, `city`, `level`, `salary_min_vnd`, `salary_max_vnd`, `salary_min_usd`, `salary_max_usd`, `posted_on`, `source_url`. `source` chỉ là `itviec`, `topdev`, `coccoc`, `greenhouse`, `lever`, `workable`. `skills` là mảng tên có trong `scraper/taxonomy.json`. Lương VND là số nguyên đồng hoặc null. Lương USD là số như nguồn ghi hoặc null. Cào không đổi USD; việc đổi nằm ở AD-6. `posted_on` là ngày ISO hoặc null. Không có mô tả, tiêu đề, tên công ty, tên người tuyển.
  - **Lọc:** `city` phải là một trong ba tên ở AD-14, không thì bỏ dòng. `level` là Intern, Fresher, Junior, Middle, Senior, hoặc Unknown.
  - **Kênh:** HTML của ITviec, TopDev, Cốc Cốc, và JSON công khai của Greenhouse, Lever, Workable. Trích kỹ năng bằng taxonomy trong bộ nhớ. Không gọi Ollama và không gọi API mô hình bên ngoài. Trích xong thì bỏ mô tả khỏi dòng ảnh.
  - **Phép lịch sự:** Giữ robots.txt, danh xưng trung thực, dừng khi trang chặn bot. Cào không mở Supabase và không mở Neo4j. Cào được mở Silo và Redis.

### AD-6 — Lương công khai là trung vị [ADOPTED]

- **Binds:** mọi số lương công khai
- **Prevents:** hai màn ra hai kiểu gộp lương, hoặc gọi lương bất thường khi ô còn mỏng
- **Rule:**
  - **Cửa sổ lương:** Tập lương của một ô là mọi tin của ô đó có lương và có `last_seen` trong 180 ngày tính tới lần nạp thành công gần nhất, đang mở hay đã đóng. Số tin trên bản đồ vẫn chỉ đếm tin đang mở. Tin có lương VND dùng số VND. Tin chỉ có lương USD được đổi sang VND bằng `USD_VND_RATE`, một tỷ giá cố định kèm ngày áp dụng, nhóm giữ trong cấu hình backend. Không lấy tỷ giá trực tiếp. Khi tập lương của số đang hiện có tin USD, màn ghi tỷ giá và ngày áp dụng ngay dưới số.
  - **Ô:** Vai trò × thành phố × cấp bậc. Một vai trò đang lọc thì ô là vai trò đó, thành phố đang chọn, và cấp của hồ sơ phiên. Chưa chọn cấp thì dùng Junior. Bộ lọc Tất cả thì vai trò của ô là vai trò có nhiều tin đang mở nhất tại thành phố đó. Hòa thì lấy vai trò đứng trước trong danh AD-14. Chưa chọn thành phố thì ô lương đầu trang không hiện số.
  - **Trung vị:** Chỉ tin trong tập lương, sau khi đã đổi USD. Điểm giữa của khoảng. Tin một mức lấy mức đó. Từ 30 tin, số hiện là trung vị các điểm giữa. Số điểm chẵn thì trung vị là trung bình hai điểm giữa. Không nguyên thì làm tròn đến đồng gần nhất, đúng một nửa thì lên.
  - **Ngưỡng:** Dưới 30 tin trong tập lương thì câu chưa đủ mẫu trên mọi màn. Không hạ ngưỡng. Không hiện phân vị. Ngưỡng nới của AD-15 đếm đúng tập này.
  - **Đã nới:** Học gì tiếp? đủ 30 tin có khoảng lương ở phạm vi nới thì lương là trung vị của phạm vi đó.
  - **Soi tin:** Chỉ kết luận bất thường khi ô của chính tin đủ 30 tin trong tập lương và trung vị nằm ngoài khoảng của tin. Ô của tin là vai trò × thành phố × cấp của tin. Dưới 30, hoặc tin không có vai trò, thì không kết luận bất thường.

### AD-7 — Lộ trình viết từ số đã tính [ADOPTED]

- **Binds:** Lộ trình 90 ngày
- **Prevents:** model bịa số tin hoặc lương, hoặc hai bên ghi hai hình chặng khác nhau
- **Rule:**
  - **Khung:** `roadmap_frame` trả đúng ba chặng, ngày 1–30, 31–60, 61–90. Mỗi chặng một kỹ năng mục tiêu.
  - **Hơn ba kỹ năng giả định:** Giữ đúng ba kỹ năng hạng cao nhất theo AD-15. Kỹ năng thứ tư trở đi không vào lộ trình. Hòa hạng thì tên đứng trước trong `scraper/taxonomy.json`.
  - **Chia chặng:** Chặng 1 nhận hạng 1. Chặng 2 nhận hạng 2 nếu có. Chặng 3 nhận hạng 3 nếu có. Chặng không có hạng giả định tương ứng thì đào sâu kỹ năng đã có được nhiều tin đang mở trong phạm vi nhắc tới nhất. Hòa thì lấy tên đứng trước trong `scraper/taxonomy.json`.
  - **Câu của agent:** Agent Lộ trình gọi `roadmap_frame` trước khi viết. Agent chỉ viết tên dự án và câu sản phẩm của từng chặng. Không thêm URL khóa học.
  - **Vì sao?:** Không phải một lượt agent mới. Cùng lượt trả `headline`, `why`, và `citations`. FastAPI kiểm tra cả câu và Vì sao? trên kết quả tool của lượt đó. Trình duyệt giữ các trường này và chỉ bật hiện khi người dùng bấm. Nhận định từ tin trỏ tập đã trích hoặc link gốc, không trỏ mô tả. Nhận định từ báo cáo gọi tên một trong bốn: ITviec, TopDev, TopCV, JobOKO. Nhận định thiếu dữ liệu nói thiếu dữ liệu và không nêu một mức lương. Nhận định bị loại vì thiếu dữ liệu vẫn có Vì sao?.
  - **Lưu:** Lộ trình chỉ ghi khi email gửi được. Thiếu liên kết khóa vẫn ghi được. Không lưu liên kết khóa.

### AD-8 — Mở lại bằng token [ADOPTED]

- **Binds:** lưu lộ trình, hồ sơ phiên
- **Prevents:** tài khoản mật khẩu, hoặc máy khác mở liên kết mà mất dấu kỹ năng đã có
- **Rule:** Hồ sơ phiên là một kho trên trình duyệt, sống qua lần tải lại, gồm thành phố, cấp bậc, vai trò mục tiêu và kỹ năng đã có. Năm bề mặt đọc cùng kho đó cho đến lúc lưu. Liên kết chứa token không đoán được. Server chỉ lưu hash, cạnh đúng một lộ trình của email đó. Bản lưu gồm thành phố, cấp bậc, vai trò mục tiêu, kỹ năng đã có, và ba chặng. Mở đúng liên kết thì response trả các trường đó, không trả email, và trình duyệt ghi chúng vào kho phiên. Biết email không trả lộ trình trên màn. Màn mở lại không hiện email. Email chưa có lộ trình thì không tạo dòng và không gửi thư. Ngày 14 không làm token hết hạn. Mỗi lần mở token hợp lệ ghi một mốc thời gian trên server. Mở trong 14 ngày kể từ lúc lưu thì tính vào phép đo. Mở sau ngày 14 vẫn ra lộ trình và không tính. Lưu lần nữa hoặc gửi lại thư thì token mới, liên kết cũ ngừng mở, và 14 ngày tính lại từ lần lưu đó. Chỉ route lưu lộ trình ghi bảng lộ trình. Route ghi dòng và hash trong một transaction, gửi thư, rồi commit khi hộp thư nhận. Thư lỗi thì rollback, không còn dòng. Bộ gửi thư không ghi bảng.

### AD-9 — Offer tính trên trình duyệt [ADOPTED]

- **Binds:** So sánh offer
- **Prevents:** lương offer nằm trong nhật ký server, hoặc hai trình duyệt dùng hai phép tính
- **Rule:** FastAPI chỉ trả bộ số thuế và BHXH 2026 trong phụ lục PRD. Trình duyệt tự tính và không giữ một bộ số riêng. Net thì dò ngược ra gross. Ngày remote không đổi tiền. Khoản hụt cả năm gồm phần người lao động và phần công ty. Chênh dưới 1% thực nhận cả năm thì hai offer gần ngang. Không có API nhận nội dung offer. Soi tin không ghi server. Câu trên màn Soi tin do agent Soi tin viết theo AD-18. Số lần thấy, hai ngày và kết luận lương là kết quả của tool `lookup_posting`.

### AD-10 — Danh kỹ năng trong database [ADOPTED]

- **Binds:** chip kỹ năng, số tuần học, vai trò của tin
- **Prevents:** màn và pipeline lệch tên kỹ năng, hoặc hai lệnh nạp gán vai trò theo hai bảng
- **Rule:** `scraper/taxonomy.json` là danh tên kỹ năng đã chuẩn hóa duy nhất. Cào chỉ ghi tên có trong file đó. Lệnh nạp seed cột `name` của bảng `skill` từ file đó và bỏ token ngoài file. Bảng có `name`, `weeks`, `role`, `required_backend`, `required_frontend`, `required_data_ai`, `required_devops`, `required_mobile`, `required_security`. Nhóm sửa số tuần, vai trò và các cờ. Nhóm không đổi tên trên Supabase. Vai trò của kỹ năng là một trong sáu tên ở AD-14 hoặc để trống. Next nhận danh từ FastAPI. Lệnh nạp đặt vai trò của tin là vai trò được nhiều kỹ năng của tin gán nhất. Hòa, hoặc không kỹ năng nào đã gán vai trò, thì tin không có vai trò.

### AD-11 — Máy chạy web và lệnh bật [ADOPTED]

- **Binds:** chạy sản phẩm
- **Prevents:** mỗi máy một cách bật, hoặc Postgres nằm trong lệnh bật
- **Rule:** Một máy của nhóm luôn bật, nơi người mở trang được trả về. Docker Compose 5.6.1 trên máy chạy web bật web, FastAPI, Ollama, Neo4j, Redis và Silo. Không bật Postgres. Neo4j, Redis và Silo chỉ có một bản, trên máy đó. Máy code nối tới ba dịch vụ đó và tới Supabase, không dựng bản thứ hai. Thư thật chỉ gửi từ máy chạy web, qua hộp thư của nhóm. Máy code không gửi thư cho người dùng.

### AD-12 — Chưa bịa dự báo [ADOPTED]

- **Binds:** dự báo 18 tháng, tín hiệu sớm
- **Prevents:** dùng hệ số minh họa của prototype, hoặc sau này trả một điểm thay vì một khoảng
- **Rule:** Chưa có công thức đã đo. Trước tuần 1, các mốc +6, +12, +18 và ô dự báo trên thẻ lúc đang xem nay không có số và không có khoảng. Câu của các ô đó là «Chưa ghi nhận dự báo cho mốc này.» Mốc nay vẫn là số tin đang mở. v1 không dự báo lương. Khi có công thức đã đo, payload là một khoảng số tin có nhãn dự báo tại 6, 12 và 18 tháng, và ô trên thẻ lúc đang xem nay lấy khoảng 12 tháng. Không trả một điểm. Tín hiệu sớm là việc khác. Chưa có quy tắc phát hiện thì thẻ dùng câu «Chưa ghi nhận tín hiệu đáng kể cho thành phố này.» Khi có quy tắc, tín hiệu là một câu: thành phố đang có việc mới vì một sự kiện, kèm Vì sao?.

### AD-13 — Không báo nguồn [ADOPTED]

- **Binds:** Lộ trình 90 ngày
- **Prevents:** một người gửi thư báo nguồn, người kia ghi bảng
- **Rule:** v1 không có nút «Báo nguồn sai hoặc đã cũ». Không gửi thư báo nguồn. Không ghi bảng báo nguồn.

### AD-14 — Ba thành phố và sáu vai trò [ADOPTED]

- **Binds:** bản đồ, bộ lọc
- **Prevents:** thêm thành phố, hoặc viết hai cách tên cùng một nơi
- **Rule:** Thành phố chỉ có ba tên, theo thứ tự: Hà Nội, TP. Hồ Chí Minh, Đà Nẵng. Duy thu từ bảy xuống ba ngày 2026-10-27 sau khi đo: trên 832 tin, Hà Nội 355, TP. Hồ Chí Minh 444, Đà Nẵng 21, Hải Phòng 2, Cần Thơ, Quy Nhơn và Nha Trang 0. Thêm thành phố là quyết định của Duy sau một lần đo mới, không tự thêm. Payload bản đồ luôn đủ ba dòng, kể cả dòng không tin. Toàn quốc là gộp ba thành phố, không phải thành phố thứ tư. Remote và Nhật không phải thị trường. Vai trò lọc là Tất cả, Backend, Frontend, Data/AI, DevOps/Cloud, Mobile, Bảo mật. Tất cả là bộ lọc, không phải vai trò lưu trên tin. Số tin trên bản đồ là mọi tin đang mở của thành phố theo bộ lọc vai trò, mọi cấp. Cấp hồ sơ chỉ chọn ô lương và kịch bản Học gì tiếp?. Học gì tiếp? chỉ dựng kịch bản cho Fresher và Junior. Cơ cấu vai trò của một thành phố cộng đủ 100%, có một nhóm còn lại. Tin không có vai trò nằm trong Tất cả và trong nhóm còn lại, không nằm trong một chip vai trò.

### AD-15 — Tin đủ điều kiện và thứ tự nới [ADOPTED]

- **Binds:** Học gì tiếp?
- **Prevents:** hai đầu đếm tin đủ điều kiện theo hai luật khác nhau, hoặc một luật làm số tin giảm khi người dùng thêm kỹ năng
- **Rule:**
  - **Mức khớp tin:** Với một tin và một tập kỹ năng, mức khớp là số kỹ năng của tin nằm trong tập, chia cho số kỹ năng của tin. Kỹ năng của tin là mảng `skills` đã chuẩn hóa theo `scraper/taxonomy.json`.
  - **Tin đủ điều kiện:** Tin đang mở, trong phạm vi đang tính, đúng vai trò mục tiêu, đúng cấp, có ít nhất một kỹ năng, và có mức khớp với tập đang xét từ `MATCH_MIN` trở lên. `MATCH_MIN` là 0,5, một tham số nhóm giữ trong cấu hình backend, đổi được sau khi đo, không đổi riêng cho từng màn. Tin không có kỹ năng nào thì không bao giờ đủ điều kiện. Tập trước chỉ có kỹ năng đã có. Tập sau thêm các kỹ năng giả định đang chọn. Số trước đếm tập trước. Số sau đếm tập sau. Vì tập sau chứa tập trước, số sau không bao giờ nhỏ hơn số trước. Tin mở thêm bằng sau trừ trước. Chưa chọn kỹ năng giả định thì không có chênh lệch. Không dùng luật «tin phải nhắc đủ mọi kỹ năng của người dùng»: luật đó làm số sau giảm khi thêm kỹ năng (đo 2026-10-27: Python + SQL thêm Docker cho 14 → 0 tin).
  - **Hạng:** Số tin mở thêm trên mỗi tuần học. Kỹ năng đã có hoặc đang chọn không nằm trong danh. Mỗi dòng trả số tin tăng, số tuần, và số tin trên mỗi tuần.
  - **Lương:** Lương trước là trung vị AD-6 của tập trước. Lương sau là trung vị AD-6 của tập sau. Tập lương dùng cùng luật mức khớp, nhưng trên cửa sổ lương 180 ngày của AD-6 thay vì chỉ tin đang mở. Dưới 30 tin có lương trong tập thì ẩn lương của tập đó. Không có kiểu gộp lương thứ hai.
  - **Độ phủ:** Số kỹ năng yêu cầu của vai trò đang nằm trong kỹ năng đã có, chia cho số kỹ năng yêu cầu của vai trò đó. Danh kỹ năng yêu cầu là các cờ ở AD-10.
  - **Điều kiện:** Chưa đủ thành phố, cấp và vai trò mục tiêu thì không có số trước và sau. Số tin trên bản đồ không phải tập này.
  - **Nới:** Ô vai trò × thành phố × cấp dưới 30 tin có lương trong cửa sổ lương AD-6 thì nới toàn quốc cùng vai trò và cùng cấp trước. Toàn quốc là gộp ba thành phố ở AD-14. Vẫn dưới 30 thì nới nhóm vai gần: Data/AI đứng riêng, Backend với Frontend, DevOps/Cloud với Bảo mật, Mobile đứng riêng. Vì sao? nói ô gốc dưới 30 và nói đang ở bước toàn quốc hay bước nhóm vai gần. Đo 2026-10-27 trên 832 tin: không ô Fresher hoặc Junior nào đạt 30 tin có lương, kể cả toàn quốc. Lúc ra mắt, lương thường ẩn cho đến khi cửa sổ 180 ngày tích lũy đủ.

### AD-16 — Lớp xu hướng dùng chung [ADOPTED]

- **Binds:** Học gì tiếp?, lộ trình, khối tám quý
- **Prevents:** mỗi màn tự vẽ một chuỗi quý từ tin đang mở
- **Rule:** Xu hướng và hạn dùng kỹ năng là một lớp trong Supabase, không phải màn và không có mục điều hướng. Bản đồ, Học gì tiếp? và lộ trình đọc cùng lớp. Chưa có chuỗi đã đo thì khối tám quý hiện «Chưa đủ mẫu.» và không có kỹ năng nào bị đánh dấu đang giảm. Không dựng chuỗi quý từ ngày đăng của tin đang mở. Không làm màn hạn dùng của prototype. Khi một kỹ năng bị đánh dấu đang giảm, kỹ năng đó không đứng hạng nhất, và Vì sao? nói mức giảm.

### AD-17 — Đọc công khai không phải sàn việc [ADOPTED]

- **Binds:** API công khai
- **Prevents:** một người làm danh tin để ứng tuyển, người kia chỉ trả số gộp
- **Rule:** API công khai trả số gộp và một lần tra đúng link người dùng dán. Không trả danh tin để ứng tuyển, không ghép hồ sơ với tin, không điểm nhà tuyển dụng, không đọc hợp đồng. Không trả object `bronze/`. Trên site không có giá, không có URL khóa học, không có bộ đếm lượt mở khóa.

### AD-18 — Bốn agent [ADOPTED]

- **Binds:** câu do model viết
- **Prevents:** một nút chỉ viết câu từ payload code gắn sẵn, hoặc model tự bịa số tin và lương
- **Rule:**
  - **Bắt buộc:** Bốn agent là yêu cầu bắt buộc của v1, Duy chốt ngày 2026-10-27. Không thay bằng câu mẫu code gắn sẵn để tiết kiệm công. Câu mẫu chỉ là đường dừng khi chạm trần bên dưới.
  - **Bốn phần:** LLM, lập kế hoạch, bộ nhớ, và tool. LLM là Ollama 0.40.8 chạy Qwen3 8B. LangChain 1.4.7 là chỗ model sinh lời gọi tool. LangGraph 1.2.16 chạy tool và đưa kết quả lại.
  - **Bốn agent:** Bản đồ, Học gì tiếp, Lộ trình, Soi tin. So sánh offer không có agent. Một thao tác mở một lượt của đúng agent đó.
  - **Ma trận tool:** Bản đồ chỉ thấy `market_snapshot` và `graph_retrieve`. Học gì tiếp chỉ thấy `skill_delta` và `graph_retrieve`. Lộ trình chỉ thấy `roadmap_frame`, `read_saved_roadmap`, và `graph_retrieve`. Soi tin chỉ thấy `lookup_posting`, `graph_retrieve`, và `read_bronze`. Schema của từng agent không đăng ký tool ngoài danh sách đó.
  - **Hợp đồng tool:** `market_snapshot` trả số tin, cơ cấu, lương hoặc câu chưa đủ mẫu, trạng thái dự báo và tín hiệu sớm. `skill_delta` trả số trước, số sau, tuần, hạng và lương hoặc trạng thái ẩn. `roadmap_frame` trả ba chặng theo AD-7. `lookup_posting` trả `seen_count`, `first_seen`, `last_seen`, tin trùng, kết luận lương, `source_id`, và `skills`. Không thấy tin thì `source_id` là null, `skills` là mảng rỗng, và lượt kết thúc với câu «Chưa soi được tin này.» `graph_retrieve` trả đồ thị con theo AD-22. `read_bronze` trả đoạn trích đã lọc theo AD-21, không trả JSON-LD. `read_saved_roadmap` trả thành phố, cấp, vai trò, kỹ năng đã có và ba chặng của một token, không trả email.
  - **Điều kiện dừng:** Trần là 6 bước sinh của model, kể cả bước gọi tool và bước viết câu. Trần thứ hai là 2 lần từ chối câu liên tiếp. Chạm một trần mà chưa có câu đạt thì lượt kết thúc và điền câu mẫu từ kết quả tool đã có. Chưa có kết quả tool thì dùng câu lỗi trong EXPERIENCE.md. Model lỗi thì cùng cách dừng đó.
  - **Kiểm tra:** FastAPI đối chiếu mọi số tin, mức lương, số tuần và cỡ mẫu trong câu và trong Vì sao? với kết quả tool của lượt. Số lạ thì trả câu lại cho model. Câu trùng một chuỗi nguyên văn của mô tả thô, hoặc chứa tên công ty, email, số điện thoại, tên người tuyển, thì bị từ chối. Prompt và kết quả tool không có email.
  - **Payload:** Cùng lượt trả `headline`, `why`, và `citations`. Màn ghi tên agent. Màn không hiện kế hoạch và không hiện lời gọi tool. Trình duyệt giữ Vì sao? và chỉ bật hiện khi người dùng bấm.
  - **Bộ nhớ:** Ngắn hạn là trạng thái của lượt và mất khi lượt kết thúc. Dài hạn là lộ trình trên Postgres, đồ thị kỹ năng trên Neo4j, và `bronze/` trên Silo. Không có vector DB và không có embedding.
  - **Cấm:** Không có agent đọc hợp đồng, ghép việc, chấm nhà tuyển dụng, hay đọc CV.

### AD-19 — Neo4j là đồ thị kỹ năng [ADOPTED]

- **Binds:** quan hệ kỹ năng
- **Prevents:** agent đếm tin bằng Cypher trong khi bản đồ đếm bằng SQL
- **Rule:** Neo4j Community 2026.10.0, driver Python 6.4.1. Lệnh nạp là chỗ duy nhất ghi, theo thứ tự ở AD-4. Nút là `Skill` và `Role`. Cạnh một chiều là `(:Skill)-[:HAS_ROLE]->(:Role)` từ cột `role`, và `(:Skill)-[:REQUIRED_FOR]->(:Role)` từ sáu cờ kỹ năng yêu cầu. Không có cạnh nào khác. Neo4j không giữ tin, không giữ lương, không giữ số đếm. Số tin và lương trung vị chỉ đọc từ Postgres. Agent không chạy Cypher để ra một con số hiện trên màn. GraphRAG đọc đồ thị này theo AD-22. Không thêm nút, không thêm cạnh, không tạo vector index.

### AD-20 — Redis là hàng đợi và cache [ADOPTED]

- **Binds:** báo cào xong, cache số gộp
- **Prevents:** cào gọi thẳng lệnh nạp, hoặc mỗi máy API giữ một cache lệch nhau
- **Rule:** Redis 8.8.3, client Python 8.1.0. List `ingest` chỉ máy chạy web được đẩy và được lấy. Máy code không lấy phần tử của list đó. Máy code thử nạp thì dùng list `ingest:dev`. Phần tử là JSON `{"sha256","object","timestamp"}`, với `object` là `open-jobs/open-jobs.jsonl`. Lệnh nạp tải object, băm SHA-256, và hủy lượt nạp khi hash không khớp. Cùng nội dung byte thì không tăng `seen_count` lần thứ hai, theo AD-4. FastAPI cache payload số gộp. Cache hết hiệu lực khi có `ingest_run` mới, và bị xóa khi Neo4j lỗi theo AD-4. Hồ sơ phiên và token lộ trình không nằm trên Redis.

### AD-21 — Silo giữ ảnh tin và mô tả thô [ADOPTED]

- **Binds:** tay trao giữa cào và nạp, bản mô tả thô
- **Prevents:** mô tả nằm trên Postgres hoặc trong payload công khai, hoặc máy code giữ một file ảnh riêng
- **Rule:** Duy chốt ngày 2026-10-27 giữ bản JSON-LD gốc trên Silo và chấp nhận rủi ro pháp lý đi kèm. PRD NFR-2 đã sửa theo quy tắc này. Server là `pgsty/silo:RELEASE.2026-10-18T00-00-00Z`. Client Python là `minio` 7.2.20. Bucket `open-jobs`, object `open-jobs.jsonl`, chỉ ghi đè khi mọi kênh thành công. Prefix `bronze/` giữ JSON-LD `JobPosting` đã đọc, một object cho một tin, khóa bằng `source_id` của AD-4. Dòng trên Postgres vẫn không có mô tả, tiêu đề, tên công ty, tên người tuyển. Màn không hiện nguyên văn mô tả. Chữ người dùng dán không được ghi vào Silo. API công khai không trả `bronze/`. `read_bronze` không trả JSON-LD. Backend chỉ trả đoạn trích nói yêu cầu kỹ năng và lý do tuyển, đã bỏ `hiringOrganization`, tên công ty, email, số điện thoại, tiêu đề, và link ứng tuyển. FastAPI đối chiếu câu với JSON-LD gốc và từ chối câu trùng nguyên văn mô tả thô hoặc chứa thông tin định danh nhà tuyển dụng.

### AD-22 — GraphRAG trên đồ thị kỹ năng [ADOPTED]

- **Binds:** câu nhắc quan hệ kỹ năng
- **Prevents:** tìm đoạn mô tả theo độ giống, hoặc model tự viết Cypher
- **Rule:** Thư viện là `neo4j-graphrag` 1.22.0, chỉ làm bước truy xuất. Bước viết câu vẫn trong lượt agent của AD-18. Không dùng retriever vector. Không dùng Text2Cypher. Truy vấn Cypher cố định, đi theo hai cạnh một chiều ở AD-19, sâu tối đa 2. Tool tên `graph_retrieve`. Hạt giống của Bản đồ, Học gì tiếp và Lộ trình là kỹ năng trong yêu cầu của lượt và vai mục tiêu nếu đã có. Hạt giống của Soi tin là mảng `skills` mà `lookup_posting` vừa trả. Kết quả tối đa 40 nút. Đủ hơn thì giữ hạt giống, rồi vai mục tiêu, rồi kỹ năng `REQUIRED_FOR` của vai đó, rồi vai `HAS_ROLE` của các kỹ năng đó. Trong cùng một tầng, nút Skill theo thứ tự từ trên xuống trong `scraper/taxonomy.json`. Nút Role theo thứ tự vai ở AD-14: Backend, Frontend, Data/AI, DevOps/Cloud, Mobile, Bảo mật. Kết quả chỉ có tên nút và loại cạnh. Không có số đếm và không có lương. Câu nhắc một quan hệ kỹ năng phải gọi tool này trước khi viết. Tên kỹ năng trong câu phải có trong kết quả tool của lượt.

## Consistency Conventions

| Concern | Convention |
| --- | --- |
| Naming | Thư mục `frontend/`, `backend/`, `scraper/`. Bảng và cột tiếng Anh, chữ trên màn tiếng Việt. |
| Data & formats | Ngày theo ISO. Lương VND là số nguyên đồng. `source_id` là chuỗi hash của pipeline. Lỗi API là một câu tiếng Việt đã có trong EXPERIENCE.md, không trả stack trace. |
| State & cross-cutting | Ghi tin Postgres và ghi Neo4j chỉ qua lệnh nạp. Ghi lộ trình chỉ khi thư gửi được, và thư thất bại thì không còn dòng. Máy code không gửi thư cho người dùng. Hồ sơ phiên là một kho trên trình duyệt cho đến lúc lưu. |

## Stack

| Name | Version |
| --- | --- |
| Python | 3.12 |
| FastAPI | 0.159.1 |
| SQLModel | 0.0.48 |
| Next.js | 16.4.2 |
| Ollama | 0.40.8 |
| Qwen3 | 8B |
| Docker Compose | 5.6.1 |
| Supabase Postgres | Pro, bản Postgres do Supabase quản lý |
| LangGraph | 1.2.16 |
| LangChain | 1.4.7 |
| Neo4j | 2026.10.0-community |
| neo4j (driver) | 6.4.1 |
| neo4j-graphrag | 1.22.0 |
| Redis | 8.8.3 |
| redis (client) | 8.1.0 |
| Silo | pgsty/silo:RELEASE.2026-10-18T00-00-00Z |
| minio (client) | 7.2.20 |

## Structural Seed

```mermaid
flowchart TB
  subgraph maychayweb [Máy chạy web]
    web[Next.js]
    api[FastAPI]
    agents[LangGraph]
    model[Ollama]
    graph[(Neo4j)]
    queue[Redis]
    lake[Silo]
    loader[Lệnh nạp]
  end
  phone[Trình duyệt] --> web
  web --> api
  api --> agents
  agents --> model
  api --> db[(Supabase)]
  loader --> db
  loader --> graph
  loader --> queue
  dev[FastAPI trên máy code] --> db
  dev --> graph
```

```text
backend/     # FastAPI, lệnh nạp, thư, đồ thị LangGraph
frontend/    # Next.js
scraper/     # cào tin, ghi Silo, đẩy Redis
# Máy code nối Supabase và Neo4j. Máy code không lấy list ingest.
```

## Deferred

- Công thức dự báo 18 tháng: hình đầu ra đã khóa ở AD-12. Công thức chờ tuần 1 đo. Trước đó không có số.
- Cách phát hiện tín hiệu sớm: chờ tuần 1. Trước đó là câu chưa ghi nhận.
- Ngưỡng nhãn tin treo: chờ tuần 1. Trước đó chỉ có số lần thấy và hai ngày.
- Quy tắc tăng, giảm, đi ngang của tám quý: chờ chuỗi đã đo. Trước đó khối nói chưa đủ mẫu.
- Tên miền và vùng Supabase: chọn lúc đưa máy chạy web lên.
- Nội dung cột vai trò trên từng kỹ năng: nhóm điền trong bảng AD-10. Công thức gộp đã khóa, danh gán thì chưa điền.
