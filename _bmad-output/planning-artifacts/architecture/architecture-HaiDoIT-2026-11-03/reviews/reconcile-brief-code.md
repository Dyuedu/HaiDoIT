---
title: "Đối chiếu: brief addendum + code scraper thật ↔ ARCHITECTURE-SPINE"
type: reconcile-review
created: 2026-11-03
inputs:
  - "A — _bmad-output/planning-artifacts/briefs/brief-HaiDoIT-2026-11-02/addendum.md (mục 1, 2, 3, 5)"
  - "B — scraper/ (README.md, Makefile, requirements.txt, crawlers/*.py, step-02..step-07)"
  - "Dẫn xuất — _bmad-output/planning-artifacts/architecture/architecture-HaiDoIT-2026-11-03/ARCHITECTURE-SPINE.md"
  - "Tham chiếu — prds/prd-HaiDoIT-2026-11-02/prd.md (FR-1..FR-9, FR-22, FR-47, §6.1, §6.4)"
---

# Đối chiếu brief ↔ code ↔ spine

## 0. Kết luận một dòng

Spine tôn trọng **gần hết** các quyết định kiến trúc đã chốt ở brief (Neo4j, hai loại cạnh, Postgres một nguồn sự thật, không tài khoản, Dagster) và chốt đúng chỗ brief yêu cầu chốt — **nhưng nó không RATIFY code thật**: AD-16 mô tả sai giao diện của cả 9 crawler, câu cuối của AD-16 vô tình xóa toàn bộ 3.469 tin nền khỏi số liệu công khai (trái brief §2 và §5), dòng dữ liệu thiếu hẳn bước đắt nhất của pipeline hiện tại (step-03 lấy mô tả đầy đủ), và hai FR có trọng lượng pháp lý nhất (FR-2 thu thập lịch sự, FR-5 xóa thông tin cá nhân) không được AD nào bind dù `polite.py` đã cài sẵn một nửa.

Mức độ: **3 critical, 5 high, 5 medium.** Không phải viết lại spine — là thêm 3 AD, sửa 1 AD, và sửa thứ tự Sprint 1–2.

---

## 1. Quyết định đã chốt ở brief §2 có được tôn trọng không?

| # | Gạch đầu dòng ở brief §2 | Trạng thái | Ở đâu trong spine |
|---|---|---|---|
| 2.1 | Không dùng Neo4j độc lập; chỉ một bài toán đồ thị thật là duyệt DAG 100–300 nút; "chuyển ngành" = hiệu tập hợp + topo; "kỹ năng bản lề" = `GROUP BY` | **đã vào spine** | Stack §"Đã loại": Neo4j + GraphRAG; Deferred: Apache AGE/Cypher; NetworkX 3.7 trong Stack |
| 2.2 | PostgreSQL là nguồn sự thật duy nhất (`skills`, `skill_edges`); đồ thị nạp vào bộ nhớ khi tính lộ trình; AGE là phương án dự phòng cho hội đồng | **đã vào spine** | ERD (`SKILL`, `SKILL_EDGE`), AD-16 *Prevents* ("hai nguồn sự thật"), Deferred Apache AGE với điều kiện quay lại đúng như brief |
| 2.3 | Hai loại cạnh tách biệt: `PREREQUISITE` soạn tay quyết thứ tự; tần suất/đồng xuất hiện quyết ưu tiên; không trộn trong một phép tìm đường có trọng số | **đã vào spine** (mạnh hơn brief) | AD-12 `[ADOPTED]` — nói thẳng "chỉ dùng cho tầng 2–3 của quy tắc 4 tầng" |
| 2.4 | Thuật toán lộ trình 5 bước; kết quả là khung JSON cố định; LLM chỉ viết lời dẫn; link chỉ từ danh mục; bỏ "GraphRAG" | **đã vào spine, một phần rơi** | AD-7 (thứ tự chỉ ở Python), AD-8 (LLM không sinh số/thứ tự/kết luận; lời dẫn soạn offline), ERD `RESOURCE`/`BLURB`. **Rơi:** "kết quả là một khung JSON cố định" không thành rule ở đâu — AD-17 chỉ quy định envelope `{data, meta}` cho response có số, không quy định khung lộ trình là schema đóng. Xem M4. |
| 2.5 | Pipeline: brief chỉ ghi ở mức năng lực; **Airflow hay Dagster quyết ở bước kiến trúc**; Airflow nặng ~4 GB và không chạy trực tiếp trên Windows; Dagster nhẹ hơn, asset vẽ được dòng dữ liệu | **đã vào spine** (đã chốt đúng chỗ) | Stack: Dagster 1.13.28; §"Đã loại": Airflow với đúng lý do 4 GB + trần §6.4; AD-15 giữ trình điều phối là vỏ mỏng (phòng đúng rủi ro khóa-vào-Dagster). **Nhưng** xem H4: lý do "Windows" bị bỏ dở — chính Dagster-trong-Docker lại là chỗ code Playwright hiện tại không chạy được. |
| 2.6 | Không có tài khoản: `localStorage`; link chia sẻ chỉ chứa mã kỹ năng; tải kết quả về máy (in trình duyệt ra PDF là phương án rẻ nhất); server không lưu CV/hồ sơ, chỉ sự kiện ẩn danh theo mã phiên + dữ liệu chế độ thử nghiệm | **đã vào spine, một phần rơi** | AD-11, AD-18, Conventions "Xác thực" + "Link chia sẻ" (đúng từng ký tự: `?role=&level=&have=`). **Rơi:** "in trình duyệt ra PDF" (FR-16) không có ở đâu. Đây không phải chi tiết trang trí: nếu ai đó cài FR-16 bằng cách render PDF ở server thì **chạm AD-11** ("endpoint nhận CV không có lệnh ghi nào… file xử lý trong bộ nhớ"). Spine nên nói rõ bản tải về sinh **phía client**. |
| 2.7 | Công tắc theo từng nguồn, **kèm kết quả rà soát điều khoản sử dụng**; bản công khai chỉ bật nguồn hợp lệ; **ngoại lệ đã chấp nhận là R1–R4**, gồm TopCV, ITviec và dữ liệu LinkedIn lịch sử **vẫn nằm trong số liệu công khai** | **BỊ MÂU THUẪN** | AD-10 có công tắc nguồn trong bảng cấu hình có phiên bản — tốt. Nhưng: (a) "kèm kết quả rà soát điều khoản sử dụng" rơi — bảng cấu hình của AD-10 không có trường nào cho kết luận ToS/ngày rà/người rà; (b) **R1–R4 không xuất hiện một lần nào trong spine** (`grep -i "R1\|điều khoản"` → 0 kết quả), nên kiến trúc không biết rằng nó phải chứa một crawler né phát hiện bot chạy trên bản công khai (R1, TopCV, 38% dữ liệu) và một khối dữ liệu lịch sử không tái thu được (R3 LinkedIn 625 tin); (c) câu cuối AD-16 **xóa thẳng** phần "vẫn nằm trong số liệu công khai" → xem **C1**. |

**Tổng kết mục 1:** 5/7 gạch đầu dòng đã vào spine trọn vẹn; 1 rơi một phần (2.4 + 2.6); 1 bị mâu thuẫn nặng (2.7). Không gạch nào bị spine **đảo ngược** về mặt chủ ý — vấn đề nằm ở các hệ quả mà spine không tính.

---

## 2. Spine có RATIFY code hiện có? — AD-16 nói sai giao diện thật

### 2.1 Giao diện THẬT của các crawler

AD-16 viết: *"mỗi crawler giữ nguyên giao diện hiện tại — **trả về danh sách bản ghi thô**, không biết gì về Postgres."*

Đọc code: **không có crawler nào trả về danh sách bản ghi.** Giao diện công khai duy nhất của mỗi module là `main()` — không tham số, không trả về gì, tự parse `sys.argv` bằng `argparse`, tự quyết đường ra, tự xóa/ghi file, tự in tiến độ ra stdout. Cụ thể:

| Crawler | Entry thật | Trả về | Ghi file ở đâu | Phụ thuộc ngoài bản ghi |
|---|---|---|---|---|
| `itviec.py` | `main()` → `fetch_page(page, n) -> list[dict]` | `main()` trả `None`; `fetch_page` cần một `page` của Playwright | `write_jsonl(out, rows)` mỗi trang; `out.unlink()` đầu lượt | Chrome thật (`channel="chrome"`), vá chống phát hiện bot |
| `topdev.py` | `main()` → `fetch_page(page, n) -> list[dict]` | như trên | như trên | như trên |
| `vietnamworks.py` | `main()` → `fetch_page(ctx, n) -> list[dict]` | như trên | như trên | `p.request.new_context` + UA giả Chrome |
| `topcv.py` | `main()` → **`interactive_scrape(page, parse_cards, out, label=...)`** | **vòng lặp `while True` cho tới `KeyboardInterrupt`** | tự `open("w")` ghi lại **toàn bộ** file mỗi 2 giây | **cần người thật** bấm sang trang trong cửa sổ Chrome hiện hữu |
| `linkedin.py` | `main()` → `interactive_scrape(...)` | như trên | như trên | **cần người đăng nhập tay**, profile WebKit lưu cookie |
| `careerlink.py` | `main()` | `None` | `write_jsonl(out, [parse_job(...)])` từng tin | đọc **chính file output** để dựng tập `done`; đọc/ghi `data/state/careerlink.json` (`queue`, `pages`, `listing_done`, `skipped`, `last_run`); tự từ chối chạy nếu cách lượt trước < 1 giờ |
| `itnavi.py` | `main()` | `None` | như trên | đọc file output để dựng `done` theo `job_id` |
| `zalo.py` | `main()` | `None` | `write_jsonl` theo từng team; `out.unlink()` đầu lượt | — |
| `momo.py` | `main()` | `None` | như trên | `list_job_paths()` tự mở Playwright riêng, trả về **đường dẫn**, không phải bản ghi |

Các hàm *có* trả về danh sách nằm thấp hơn một tầng và **không có chữ ký chung**: `parse_card(card) -> dict | None` (itviec, theo từng thẻ), `parse_cards(soup) -> list[dict]` (topdev, topcv), `parse_jobs(soup) -> list[dict]` (linkedin), `parse_job(url, posting)` (careerlink), `parse_job(d)` (itnavi), `parse_job(j, team)` (zalo), `parse_job(url, d)` (momo), `parse_job(j)` (vietnamworks). Hai trong số đó nhận `BeautifulSoup`, bốn nhận `dict` JSON, và tầng trên chúng (`fetch_page`) lại nhận một `page`/`ctx` của Playwright. Không có generator, không có `crawl() -> Iterable[dict]`.

### 2.2 Vì sao câu AD-16 sai lại nguy hiểm, chứ không chỉ là sai từ ngữ

1. **"Giữ nguyên giao diện hiện tại" nếu hiểu đúng chữ nghĩa = giữ nguyên việc ghi JSONL** — tức là giữ đúng cái mà AD-16 lấy làm *Prevents* ("hai nguồn sự thật sống song song, file JSONL và Postgres"). AD-16 tự đánh nhau với chính nó trong hai câu liền kề.
2. **Lập trình viên đọc AD-16 sẽ tưởng công việc là "viết một bước `ingest` gọi 9 hàm trả về list"** — trong khi công việc thật là *refactor cả 9 crawler*: tách `main()` thành một hàm thu thập trả về/`yield` bản ghi, bóc `argparse` ra khỏi logic, bóc `write_jsonl` ra khỏi vòng lặp thu thập, và **chuyển trạng thái resume ra khỏi file** (xem M5). Đó là một story vài ngày, không phải một dòng ghi chú ranh giới.
3. **2/9 crawler không thể tự động hóa**: `topcv.py` và `linkedin.py` là vòng lặp người-trong-vòng. LinkedIn không sao (R3: v1 không thu mới). TopCV thì **chí tử**: 1.323/3.469 tin = 38,1% dữ liệu nền, và R1 nói rõ TopCV *"chạy cả trên bản công khai"*. Spine vẽ `crawl["thu thập — 9 crawler, công tắc theo nguồn"]` như một asset Dagster chạy hằng đêm. Với TopCV hôm nay điều đó là bất khả thi — phải viết lại thành crawler phân trang không tương tác (và khi đó phải đối mặt Cloudflare/captcha của TopCV, chính thứ `interactive_scrape` đang lách bằng cách để người thật điều hướng).

### 2.3 Câu Rule đề xuất thay AD-16

> ### AD-16 — Ranh giới của scraper kế thừa
>
> - **Binds:** FR-1, FR-2, FR-3, FR-4, `scraper/`
> - **Prevents:** hai nguồn sự thật sống song song (file JSONL và Postgres); và cùng lúc đó: nhập nhầm rằng crawler kế thừa đã có giao diện gọi được từ pipeline
> - **Rule:**
>   1. **Giao diện đích** (chưa tồn tại, phải refactor trong Sprint 1): mỗi nguồn cho đúng **một** hàm `crawl(cfg: SourceConfig) -> Iterator[RawJob]`, thuần phần thu thập, **không `argparse`, không ghi file, không `print` tiến độ, không biết gì về Postgres hay Dagster**. `main()`/`argparse` hiện tại trở thành lớp vỏ CLI mỏng gọi đúng hàm đó.
>   2. **Logic phân tích giữ nguyên.** Các hàm `parse_*` hiện có là tài sản đã kiểm chứng trên 3.469 tin: không viết lại selector, không "dọn dẹp" chúng. Chỉ bóc chúng ra khỏi `main()`.
>   3. **Trạng thái thu thập ra khỏi file.** Hàng đợi, tập đã thu, số trang đã quét, mốc `last_run` và trần request của từng nguồn (hiện ở `data/state/careerlink.json` và ở chính file output) chuyển sang bảng `source_crawl_state` trong Postgres. Không bước nào được đọc file trong `scraper/data/` để quyết định thu thập tiếp cái gì.
>   4. **Một bước `ingest` duy nhất** ghi `RawJob` vào `job_raw` kèm `snapshot_id` và `source`.
>   5. **Hai crawler người-trong-vòng** (`topcv.py`, `linkedin.py`) **không đạt giao diện này**. `linkedin` bị tắt vĩnh viễn ở v1 (R3). `topcv` phải được viết lại thành crawler phân trang không tương tác trước khi snapshot hằng ngày được coi là đạt FR-1; cho tới lúc đó công tắc TopCV ở chế độ `manual` và lượt chạy hằng đêm ghi nhận nguồn này là "không thu thập" thay vì báo lỗi.
>   6. **Dữ liệu nền là một snapshot nhập một lần**, không phải "tiện ích lúc dev": xem AD-19 (C1).

---

## 3. Quy ước đã có trong code mà spine bỏ sót

Spine có mục *Consistency Conventions* dài 15 dòng, nhưng **không một dòng nào** đến từ code thật. `grep -i "robots\|user-agent\|captcha\|403\|429"` trên spine → 0 kết quả. Dưới đây là những quy ước code đã có, đáng nâng lên spine.

### 3.1 `polite.py` — quy ước đáng nâng lên AD, hiện đang rơi hoàn toàn (**H1**)

`crawlers/polite.py` đã cài sẵn gần đủ FR-2:

- `USER_AGENT = "HaiDoIT-research-bot/0.1 (non-commercial student research)"` — UA trung thực, không giả trình duyệt;
- `allowed(url)` kiểm `robots.txt` **trước mọi request**, cache theo origin, `can_fetch(USER_AGENT, url)`;
- giãn cách cố định tính bằng `time.monotonic()` (không phải `sleep` mù), mặc định 3 s, CareerLink đặt 15 s;
- `max_requests` → `BudgetExhausted`: trần request theo từng lượt;
- 403/429 → `BlockedError`; HTML chứa `hcaptcha`/`g-recaptcha`/`cf-challenge` → `BlockedError`;
- **ngữ nghĩa quan trọng nhất**: `BlockedError` nghĩa là **dừng, không tìm cách lách** — docstring viết thẳng *"Stop, do not retry around it"*, và `careerlink.py`/`itnavi.py`/`momo.py` bắt nó ở ngoài vòng lặp rồi kết thúc lượt, không retry.

Spine không có AD nào bind **FR-2**. `grep "FR-2\b"` trên spine → 0 kết quả. Hệ quả thực tế: một người làm bước `ingest` mới hoàn toàn có thể dùng `requests.get` trần, hoặc bọc `BlockedError` trong `try/except: continue` để "lượt chạy không bị đứt" — và review sẽ không có invariant nào để chặn. Đây là FR có rủi ro pháp lý cao nhất của dự án (§6.2, Điều 289 nêu ở R1).

**Đề xuất AD mới:**

> ### AD-20 — Mọi request ra ngoài đi qua một cổng lịch sự duy nhất
>
> - **Binds:** FR-1, FR-2, FR-47, §6.1, §6.2
> - **Prevents:** một bước mới gọi `requests.get` trần, hoặc bọc `BlockedError` để "lượt chạy không bị đứt" — phá cam kết FR-2 mà lượt chạy vẫn xanh
> - **Rule:** mọi request HTTP tới nguồn tin đi qua `PoliteClient` (nâng từ `scraper/crawlers/polite.py`): UA trung thực **có địa chỉ liên hệ trỏ về kênh yêu cầu gỡ của FR-47**, kiểm `robots.txt` trước mọi request, giãn cách cố định theo từng nguồn, trần request theo từng lượt. `BlockedError` (robots/403/429/captcha) **chấm dứt nguồn đó trong lượt chạy**, ghi lý do dừng vào `pipeline_run`, và nguồn không được thử lại cho tới lượt sau. Không bước nào được bắt `BlockedError` rồi tiếp tục. Ngoại lệ duy nhất là các crawler trong bảng R1–R4, mỗi ngoại lệ phải được bảng cấu hình nguồn ghi rõ (`politeness_exception`, kèm ngày rà soát điều khoản sử dụng, theo brief §2).

Kèm một việc sửa code một dòng: UA hiện tại **chưa có địa chỉ liên hệ**, trong khi Sprint 1 và FR-47 đều đòi *"User-Agent có thông tin liên hệ"*. `browser.py` thì ngược lại — UA giả Chrome/Safari + `--disable-blink-features=AutomationControlled` + vá `navigator.webdriver`: đó chính là R1/R2, và spine không nhắc.

### 3.2 FR-5 (xóa thông tin cá nhân của người đăng tin) — rơi ở cả spine lẫn code (**H1**)

`grep "FR-5\b"` trên spine → 0 kết quả. Dòng dữ liệu của spine đi `crawl → ingest vào job_raw → dedupe → mentions`: **không có bước xóa PII**, trong khi FR-5 nói rõ *"ngay khi đọc tin và **trước khi lưu**"*. Code hiện tại cũng không có: cả 9 crawler và step-03 đều đưa `description` nguyên khối vào bản ghi, và `data/step-07-jev-extracted.jsonl` chứa 3.469 mô tả đầy đủ chưa qua bộ lọc nào. AD-11 chỉ bảo vệ **nội dung người dùng dán**, AD-14 chỉ chặn **render** `description` ra trang công khai — không chỗ nào chặn việc *lưu* email/số điện thoại nhà tuyển dụng vào `job_raw`.

**Đề xuất:** thêm một bước `redact` giữa `crawl` và `ingest` trong Structural Seed, và một rule: *"`job_raw.description` được ghi sau khi đã qua hàm xóa PII thuần trong `domain`; kiểm thử xác nhận không hàng nào trong `job_raw` khớp mẫu email hoặc số điện thoại Việt Nam (FR-5). Nhật ký chỉ ghi loại thông tin đã xóa, không ghi giá trị."*

### 3.3 `base.py` — `write_jsonl`/`read_jsonl` và quy ước checkpoint (**M5**)

`write_jsonl` là **append**, `read_jsonl` trả `[]` khi thiếu file. Trên đó, cả pipeline dựng một quy ước duy nhất và rất nhất quán: **file output vừa là kết quả vừa là checkpoint**, khóa theo `job_url` (hoặc `job_id`), và mọi bước đều `resumable`:

- step-03: `results` nạp từ `out` nếu có, `flush()` mỗi `BATCH_SIZE = 200`, `description_complete()` quyết định tin nào cần lấy lại (biết cả hai lỗi lịch sử: VietnamWorks cắt bằng `...`, TopDev cắt cứng ở đúng 6000 ký tự);
- step-04/05/06/07: mỗi bước một `*-cache.jsonl` append-only, chạy lại thì bỏ qua cái đã có; step-07 còn **chỉ nạp cache những hàng đã qua validation** (`classification.get(field) in allowed`).

Spine ratify **một nửa**: AD-15 nói mỗi bước là một hàm + một CLI, chạy lại được từng bước khi debug. Nhưng không có convention nào nói **mỗi bước idempotent theo khóa tin và chạy lại được giữa lượt**. Với AD-4 (publish nguyên khối trong một transaction), đây không phải chi tiết nhỏ: một lượt đêm đi qua 3.469 tin × một lệnh gọi LLM, nếu lượt chạy đứt ở giữa mà không có checkpoint thì hoặc mất tiền gọi lại từ đầu, hoặc snapshot không bao giờ publish được.

**Đề xuất convention:** *"Mỗi bước trong `haido_core/steps/` idempotent theo `(snapshot_id, job_id)`: chạy lại một bước trên cùng snapshot không tạo hàng trùng và không gọi lại LLM cho tin đã có kết quả. Kết quả trung gian nằm trong Postgres, không trong file — nhưng tính 'chạy lại được giữa lượt' của pipeline kế thừa phải được giữ."*

### 3.4 Cách step-03 lấy mô tả đầy đủ — spine bỏ hẳn một bước của pipeline (**H2**)

`step-03-fetch-details.py` là **508 dòng, chiếm 19% toàn bộ code scraper**, và là bước đắt + dễ vỡ nhất:

- bốn extractor riêng theo nguồn (`EXTRACTORS = {itviec, vietnamworks, topdev, topcv}`), mỗi cái vì một lý do cụ thể đã học được: ITviec dùng JSON-LD; VietnamWorks phải scrape `h2` "Mô tả công việc"/"Yêu cầu công việc" vì *JSON-LD thiếu phần Yêu cầu*, phải bấm nút "Xem đầy đủ", và phải bỏ teaser "Mức độ phù hợp"; TopDev phải chọn thẻ JD dài nhất có marker và loại "More jobs for you"; TopCV phải loại 4 chuỗi boilerplate ("Tiếp lợi thế", "Hệ sinh thái HR Tech"…);
- `is_cloudflare()` nhận diện trang chặn bằng title + hook DOM + 6 marker văn bản, **có chú thích vì sao không dùng từ "challenge" rộng** (dương tính giả trên JD thật);
- `CloudflareDetected` → **đóng và mở lại trình duyệt** rồi thử lại, tối đa `RETRIES = 5`;
- LinkedIn đi đường khác hoàn toàn: Voyager API + `csrf-token` lấy từ cookie `JSESSIONID`.

Dòng dữ liệu của spine: `crawl → ingest → dedupe → mentions → mapping → …`. **Không có bước "lấy mô tả đầy đủ".** Nhưng 4/5 nguồn kế thừa (itviec, topdev, topcv, linkedin) chỉ cho **listing không có `description`** — kiểm được ngay trong code: `itviec.py` docstring viết *"Phase 1: listing only… Full description is fetched in Phase 2"*, và bản ghi của `parse_card` không có khóa `description`. Không có step-03 thì không có văn bản để AD-3 trích lượt nhắc.

Đáng chú ý: 4 crawler **mới** (careerlink, itnavi, zalo, momo) **đã có `description` ngay trong bản ghi** — đó là một tiến hóa thật của code và là lý do kiến trúc nên tách rõ hai lớp nguồn. Spine coi "9 crawler" là một khối đồng nhất nên không thấy sự phân đôi này.

**Đề xuất:** thêm vào Structural Seed một bước `fetch_details` giữa `dedupe` và `mentions` (đúng thứ tự code hiện tại: dedupe trước, để không tốn request lấy mô tả của tin trùng), và một convention: *"Nguồn được phân hai loại: `detail_included` (bản ghi đã có `description`) và `listing_only` (phải qua bước `fetch_details`). Bước `fetch_details` chỉ chạy trên tin chưa có mô tả đầy đủ, theo một vị từ `description_complete` riêng cho từng nguồn."*

### 3.5 Cách step-04/step-07 gọi Jev — một quy ước tốt, spine bỏ mất khi bỏ Jev (**M1**)

Hai bước này có hai quy ước đáng giữ, độc lập với việc dùng Jev hay Claude:

1. **Quy tắc loại bỏ bảo thủ** (step-04): `DROP_CONFIDENCE = 0.7`, và *"drop only when Jev says `non_tech` with confidence >= 0.7. Everything else is kept and flagged."* Tức là nghi ngờ thì **giữ lại**. Đây đúng là tinh thần FR-7 ("tin không thuộc IT được gắn nhãn và loại khỏi mọi bảng tổng hợp" — gắn nhãn, không xóa) và là lý do `is_tech`/`tech_confidence` còn nằm trong mỗi bản ghi của bộ 3.469.
2. **Validation enum trước khi ghi cache** (step-07): `parse_classification()` kiểm **từng** trường phải nằm trong `CATEGORIES[field]`, sai thì `raise` và **không ghi gì**; lúc nạp cache lại kiểm lần nữa. Không có "giá trị lạ lọt vào bảng thống kê".

Spine có AD-3 (LLM chỉ trả lượt nhắc nguyên văn) và AD-8 (văn bản LLM không chứa chữ số) — nhưng **không có rule nào bắt mọi giá trị phân loại do LLM trả về phải được validate theo enum của `domain` trước khi ghi**, và không có rule nào về "nghi ngờ thì giữ, kèm nhãn". Với AD-10 (θ và ngưỡng là dữ liệu) thì ngưỡng loại bỏ của FR-7 cũng nên vào bảng cấu hình.

**Đề xuất convention:** *"Mọi giá trị phân loại do LLM trả về được validate theo hằng enum trong `domain` trước khi ghi; giá trị ngoài enum là lỗi của bản ghi đó, không phải lỗi lượt chạy, và tin đó đi vào danh sách chờ. Tin không phân loại được **được giữ và gắn nhãn**, không bị xóa; ngưỡng loại bỏ nằm ở bảng cấu hình (AD-10)."*

---

## 4. AD-9 "bỏ Jev/TypeSafe khỏi v1" làm mất gì?

### 4.1 Mất gì về mặt năng lực

| Thứ bị mất | Hiện ở đâu | Có thay thế trong spine? |
|---|---|---|
| Lọc IT/không-IT thô, **có độ tự tin số** và ngưỡng loại bảo thủ 0,7 | step-04, 205 dòng | Không. AD-3 chỉ nói LLM trích lượt nhắc; không có cổng nào trả về `(nhãn, độ tự tin)`. Claude structured outputs **không cho độ tự tin đã hiệu chỉnh** — "confidence" do model tự khai không tương đương, và ngưỡng 0,7 sẽ mất nghĩa thống kê. |
| Phân loại 4 chiều (`title/seniority/location/work_model`) với validation enum chặt | step-07, 347 dòng | Có chỗ đứng (`classify` trong dòng dữ liệu), chưa có rule (xem M1). |
| Chi phí rất thấp cho quyết định nhỏ lặp lại nhiều lần | step-04 tự in: `~$0.000022`/lệnh gọi → ~0,08 USD cho 3.469 tin, **5 câu hỏi** trong 1–2 lượt gọi | Spine chọn `claude-haiku-5-5` qua Batch API. Hợp lý về kiến trúc nhưng **spine không đưa con số**, trong khi §6.4 có trần 5–10 USD/tháng và brief §3 nói rõ "chỉ chuyển sang mô hình nhỏ **sau** khi đo trên bộ 200 JD". |
| Tính **tái lập** của bộ dữ liệu nền đã công bố | 3.469 tin đều mang `is_tech`, `tech_confidence`, `classification` do Jev sinh | Không. Đổi nhà cung cấp ⇒ thành phần bộ 3.469 (và con số "3.469 tin" trong brief, PRD, báo cáo) không tái lập được bằng pipeline mới. |

### 4.2 Những bước phải viết lại (dù AD-9 chỉ nói "gộp về một cổng")

- **step-04** (Jev) — viết lại: cổng `extract` + enum `domain` + ngưỡng ở bảng cấu hình.
- **step-07** (Jev) — viết lại, **và đổi taxonomy**: FR-7 tách `Data / AI / ML` thành 3 (Data Analyst/BI, Data Engineer, AI/ML Engineer), tách `Embedded` khỏi `Other`, và nhánh chỉ được tạo khi ≥ 30 tin. Enum hiện tại của step-07 không khớp. Thêm việc: **map 3.469 giá trị `classification` cũ sang enum mới** khi nhập dữ liệu nền.
- **step-06** (Claude, nhưng sai đầu ra) — viết lại hoàn toàn theo AD-3. Hiện nó trả `title_cleaned` + `tech_stack[]` + `keywords[]` **đã dịch sang tiếng Anh** ("CRITICAL REQUIREMENT: All extracted text MUST be in English"). AD-3 đòi "lượt nhắc **nguyên văn** trích từ văn bản" rồi mapping tất định. Đây là hai hợp đồng khác nhau về bản chất, không phải một lần đổi prompt.
- **step-05** (Claude) — **phải bỏ**, xem C2.
- **step-02** (dedupe) — phải viết lại: hiện chỉ dedupe **trong cùng nguồn** theo `site||company||title` chuẩn hóa và *cố ý giữ* tin trùng giữa các sàn (docstring: *"The same job on different boards is kept"*). FR-4 đòi dedupe **cả giữa các nguồn** và **gom thành cụm thay vì xóa** (`JOB_CLUSTER` trong ERD). Spine đúng ở ERD, nhưng không nói rằng bước dedupe hiện tại có *chủ ý ngược lại* — người đọc spine sẽ tưởng step-02 là nền để sửa, trong khi nó phải đảo logic.
- **step-03** — là bước duy nhất gần như giữ được nguyên, nhưng lại là bước duy nhất spine không nhắc (H2).

Tức là: trong 6 bước kế thừa, **5 bước phải viết lại** và bước thứ 6 không có trong kiến trúc. Spine mô tả `scraper/` là "code kế thừa: 9 crawler + 6 bước, 2.7k dòng" và đặt nó làm một node trong AD-1 như thể nó là tài sản dùng lại được. Tài sản dùng lại được thật sự chỉ là: 9 bộ `parse_*` + `polite.py` + `is_cloudflare()` + 4 extractor của step-03 ≈ 900–1.000 dòng.

### 4.3 Rủi ro spine chưa nêu

1. **Mất độ tự tin đã hiệu chỉnh** ⇒ quy tắc an toàn "nghi ngờ thì giữ" của FR-7 không có cơ chế tương đương; nếu thay bằng ngưỡng tự khai của Claude thì tỷ lệ loại theo từng nguồn (tiêu chí nghiệm thu FR-7) mất tính so sánh với số đã có.
2. **Chi phí chưa tính lại**: Jev làm 5 quyết định/tin với ~2,2e-5 USD. Với `claude-haiku-5-5` qua Batch cho 3.469 tin/đêm × (trích lượt nhắc + phân loại) — spine không đưa ước tính nào, dù §6.4 đặt trần và dù chính spine viện §6.4 để loại Airflow. Đây là chỗ duy nhất trong spine mà một ràng buộc chi phí được dùng để loại công cụ nhưng không được dùng để kiểm chính lựa chọn của mình.
3. **Mất tính tái lập của con số công bố** (3.469 tin, 604 tin "Other", 24% có lương): mọi số trong brief §5 và README đều là đầu ra của Jev. Sau khi bỏ Jev, báo cáo SEP490 sẽ có hai bộ số không khớp nhau mà không có bước nào trong kế hoạch để hòa giải.
4. **`anthropic` SDK + Batch API là phụ thuộc đơn điểm**: AD-9 nói thẳng "v1 chỉ dùng Claude; không có nhà cung cấp thứ hai". Hợp lý cho 3 người/8 tuần, nhưng *Deferred* không có dòng nào cho tình huống "Batch API chậm/lỗi một đêm" — trong khi AD-4 đòi snapshot publish nguyên khối. Nên có một rule: lượt chạy lỗi ⇒ **không publish**, tầng đọc tiếp tục dùng snapshot cũ (spine đã hứa năng lực này ở Design Paradigm nhưng không có rule nào thực thi).

---

## 5. Kế hoạch 8 sprint ↔ kiến trúc: việc nào không kịp, việc nào phải đổi thứ tự?

### 5.1 Sprint 1 (2–8/11, **còn 5 ngày**) — "bật snapshot hằng ngày" + chọn Dagster

Sprint 1 theo brief phải có: kế hoạch (brief → PRD → kiến trúc) ✔ đang làm, làm sạch dữ liệu, **bật snapshot hằng ngày (FR-3)**, khung repo + Compose + CI, bộ từ vựng kỹ năng v0, 3 email xin phép, trang chính sách dữ liệu + kênh gỡ (FR-47), UA có liên hệ. Demo: *"Pipeline chạy mỗi đêm"*.

Kiến trúc trong spine làm việc này **không kịp**, vì bốn lý do xếp theo mức nặng:

**(a) AD-4 làm "snapshot hằng ngày" không có định nghĩa thỏa được ở Sprint 1 (H3).** AD-4: *"Một snapshot chuyển sang `published` trong đúng một transaction ở cuối lượt chạy, **sau khi mọi bảng tổng hợp của nó đã ghi xong**"*. Bảng tổng hợp cần bộ từ vựng đầy đủ + mapping + θ_core/θ_common — tất cả đều là việc **Sprint 2**. Vậy ở Sprint 1 hoặc snapshot không bao giờ `published` (và demo "pipeline chạy mỗi đêm" không chứng minh được gì), hoặc đội phá AD-4 ngay tuần đầu. Spine phải định nghĩa **trạng thái snapshot phân tầng** — ví dụ `ingested` → `enriched` → `aggregated` → `published` — và nói rõ Sprint 1 nghiệm thu ở `ingested` (FR-3 chỉ đòi vòng đời tin: `first_seen`, `last_seen`, `times_seen`, `times_reposted`, hoàn toàn tính được mà không cần một bảng `stat_*` nào).

**(b) TopCV không tự động hóa được (C3).** Nguồn 38% dữ liệu là crawler người-trong-vòng. "Pipeline chạy mỗi đêm" trong 5 ngày sẽ chạy với 4 nguồn mới (careerlink/itnavi/zalo/momo ≈ 1.164 tin) + vietnamworks + itviec/topdev — và một ô trống to ở chỗ TopCV.

**(c) Dagster + Playwright trong Docker không chạy như spine vẽ (H4).** Sơ đồ triển khai của spine: `dag --> sites`, tức container Dagster tự đi thu thập. Nhưng `browser.py` dùng `channel="chrome"` (**Google Chrome đã cài trên máy**, không phải chromium của Playwright) và `headless=False` là mặc định; `step-03` cũng vậy. Trong container Linux `channel="chrome"` sẽ lỗi khởi tạo, và headful cần X. Mặt khác brief chọn Dagster một phần vì *"Airflow không chạy trực tiếp trên Windows"* — nhưng đội dev trên Windows (Makefile có `PY=.venv/Scripts/python`), nên lợi thế đó chỉ còn nếu crawler chạy **ngoài** container. Spine cần một quyết định rõ: crawler chạy trong container (⇒ đổi sang chromium + headless + chấp nhận bị chặn nhiều hơn), hay chạy trên host qua một sensor/CLI của Dagster. Đây là quyết định kiến trúc, không phải chi tiết triển khai, và nó phải có trước khi lập Sprint 1.

**(d) Khối lượng khung repo mà spine đòi.** Cây mã nguồn của spine là 9 package/thư mục mới (`haido_core/{domain,db,steps,extract,vocab}`, `haido_pipeline`, `haido_api`, `web`, `eval_fixtures`, `deploy`), ~16 thực thể trong ERD cần migration Alembic, bảng cấu hình có phiên bản (AD-10), route revalidate + secret (AD-13), kiểm thử chặn import ngược chiều (AD-1). Cộng với refactor 9 crawler (AD-16 bản sửa) và trang chính sách dữ liệu. Trong 5 ngày còn lại, với 3 người đang đồng thời viết PRD/kiến trúc — không kịp.

**Đề xuất đổi thứ tự Sprint 1:** chỉ dựng `haido_core/{db,steps}` + refactor `scraper` + `crawl/redact/ingest` + `pipeline_run` + `source_crawl_state` + trang FR-47 + UA có liên hệ. Hoãn sang Sprint 2: `haido_api`, `web`, `eval_fixtures`, bảng `stat_*`, route revalidate. Và **Dagster hoãn tới Sprint 2**: AD-15 đã làm trình điều phối thành vỏ mỏng, nên Sprint 1 chạy bằng Task Scheduler/cron gọi CLI là đủ để demo "pipeline chạy mỗi đêm", rồi bọc Dagster sau. Dùng đúng cái AD-15 được viết ra để cho phép.

### 5.2 Sprint 2 (9–15/11) — bị dồn thêm việc từ Sprint 1 và từ C2

Sprint 2 đã rất nặng: bộ máy kỹ năng song ngữ, **200 JD gán nhãn tay**, Cohen's kappa, phân loại cấp bậc, tách Data/AI thành 3, tách Embedded, hiệu chỉnh θ rồi đóng băng, bảng nhóm kỹ năng, đồ thị học trước + danh mục tài liệu cho 2 vai trò, **giảng viên rà soát có biên bản**. Kiến trúc thêm vào: nếu Sprint 1 trượt theo 5.1 thì toàn bộ `stat_*` + `haido_api` dồn về đây; và theo **C2**, việc lấy 200 JD *văn bản gốc* đòi chạy lại step-03 trên hàng nghìn trang (hoặc crawl lại), vốn chưa có trong ô Sprint 2 nào.

### 5.3 Sprint 3 (16–22/11) — vertical slice Cố vấn cho Review giữa kỳ 22–28/11

Đây là chỗ kiến trúc trong spine **chặn đường tắt thường dùng**, và đó vừa là ưu điểm vừa là rủi ro lịch:

- AD-5 + AD-6: API **không được** `GROUP BY` trên bảng tin; mọi tỷ lệ phải đọc từ `stat_cells`/`stat_skill_rate` theo `(snapshot_id, stat_cell_id)`. ⇒ demo Cố vấn không thể "tính nhanh tại chỗ".
- AD-17: mọi response có số phải mang `meta` đủ (`snapshot_date`, `stat_cell`, `n`, `fallback_label`, `sources[]`, `thresholds`), và `n < 30` ⇒ `data = null`. ⇒ demo không thể bỏ qua cỡ mẫu.
- AD-16 (bản hiện tại): dữ liệu nền **không bao giờ** là đầu vào bảng tổng hợp. ⇒ demo không thể chạy trên `step-07-jev-extracted.jsonl`.
- FR-22 (PRD): *"Vai trò chỉ được bật trong Cố vấn sau khi có biên bản rà soát"* ⇒ phụ thuộc cứng vào buổi rà soát của giảng viên ở Sprint 2.

Cộng lại: **để có vertical slice Cố vấn ngày 22/11, gần như toàn bộ bên ghi (crawl → ingest → dedupe → fetch_details → mentions → mapping → classify → salary → aggregate → publish) phải xong trước 16/11**, tức trong Sprint 2 — cùng tuần đang làm 200 JD gán nhãn và hiệu chỉnh θ. Đây là rủi ro lịch nặng nhất của cả kế hoạch, và spine không nêu nó ở đâu (mục *Deferred* và *Câu hỏi mở* đều không có dòng nào về thứ tự sprint).

**Hai đường thoát, phải chọn một và ghi vào spine:**
1. **Nhập dữ liệu nền làm snapshot gốc** (AD-19 đề xuất ở C1): bên ghi chỉ cần chạy từ `mentions` trở đi trên 3.469 tin đã có, không phụ thuộc crawl hằng đêm. Đây là đường duy nhất khả thi cho 22/11 — và nó đòi **sửa AD-16**.
2. Hoặc đổi thứ tự: đẩy phần "so với thị trường" của Cố vấn sang Sprint 4, Review giữa kỳ demo slice chỉ-hồ-sơ (CV → khoảng trống → lộ trình theo đồ thị `PREREQUISITE` soạn tay, chưa có tỷ lệ xuất hiện). Khi đó AD-5/AD-6/AD-17 không bị chạm, nhưng demo mất đúng phần "dựa trên dữ liệu thật" — là luận điểm trung tâm của đồ án.

### 5.4 Trang nội dung công khai (SEO/GEO): workstream mới, không có ô nào trong kế hoạch (**H5**)

AD-13 + AD-14 + dòng cuối bảng Capability đưa vào một hạng mục hoàn toàn mới: template ISR theo vai trò, route revalidate + secret dùng chung, `web` đọc Postgres trực tiếp (ngoại lệ duy nhất của AD-1), mỗi trang in ngày snapshot + cỡ mẫu + nguồn đang bật. Spine tự nhận ở Câu hỏi mở 1 rằng *nó chưa có FR trong PRD* — nhưng không nói rằng **nó cũng không có trong kế hoạch 8 sprint**: không ô nào từ Sprint 1 đến Sprint 8 nhắc tới trang SEO. Sprint 5 có "**công khai**" nhưng đó là công khai app. Đây là scope mới ước lượng 3–5 ngày (template + revalidate + 5–8 trang vai trò + kiểm thử không render `description`), chưa ai cấp thời gian.

### 5.5 Những ô kế hoạch mà kiến trúc **ratify tốt**

Để công bằng, phần lớn kế hoạch được spine đỡ đúng chỗ:

- Sprint 2 "hiệu chỉnh θ rồi đóng băng" ↔ AD-10 (θ là dữ liệu có phiên bản, mỗi snapshot lưu `config_version`) — ratify chính xác tiêu chí nghiệm thu FR-9 "đổi θ không cần triển khai lại".
- Sprint 3 "ba lựa chọn xác nhận" + "tự chọn kỹ năng" ↔ AD-2 (một bộ máy kỹ năng) + AD-7 (frontend chỉ giao tập và lọc).
- Sprint 4 "FR-32 khớp tin được dán" ↔ ERD `JOB_CLUSTER`/`JOB` + AD-11 (tin dán là phù du) — hợp nhau; **lưu ý nhỏ:** FR-32 đòi dùng *"cùng cách so khớp như FR-4"*, nên hàm so khớp phải nằm trong `domain` để cả bước dedupe hằng đêm và endpoint phù du dùng chung. AD-2 chỉ nói về bộ máy kỹ năng, không nói về bộ máy so khớp tin — nên thêm.
- Sprint 5 "chế độ 2D/bảng bắt buộc (FR-36)" ↔ AD-17 (`meta` đủ ở mọi response có số) — chế độ bảng đọc cùng dữ liệu, không cần endpoint riêng. Tốt.
- Sprint 6 "chế độ thử nghiệm phải xong đầu sprint" ↔ AD-18 (bảng `eval_*` riêng, cờ `is_eval`, fixture JSON tĩnh có phiên bản) — ratify rất sạch, và `eval_fixtures/` đã có chỗ trong cây mã nguồn.
- Sprint 7 "thực nghiệm độ nhất quán của chatbot" — đứng ngoài hệ thống, kiến trúc không chạm. Đúng.
- Sprint 8 "code freeze" ↔ Deferred "CI/CD nhiều tầng, blue-green" — hợp với 3 người/1 VPS.

---

## 6. Bảng phát hiện xếp theo mức độ

### Critical

**C1 — Câu cuối AD-16 xóa toàn bộ 3.469 tin nền khỏi số liệu công khai, trái brief §2 và §5.**
AD-16: *"File trong `scraper/data/` chỉ còn là tiện ích lúc dev, **không bao giờ là đầu vào của bảng tổng hợp**."* Nhưng brief §2 chốt ngược lại: *"ngoại lệ đã chấp nhận là R1–R4 …, gồm TopCV, ITviec và **dữ liệu LinkedIn lịch sử vẫn nằm trong số liệu công khai**"*, và PRD §6.1 nói rõ *"Mọi số liệu công khai hiện tính trên 3.469 tin, gồm cả R3 và R4"*. Kiểm trên dữ liệu thật: 3.469 tin = topcv 1.323 + linkedin 625 + vietnamworks 591 + itviec 555 + topdev 375. LinkedIn 625 **không tái thu được** (R3: v1 không crawl mới). Nếu AD-16 đứng, dữ liệu rơi về 2.289 tin (đúng con số PRD), Backend còn 184 và Java Backend còn 105 — sát ngưỡng `n ≥ 100` của bootstrap CI (FR-9) và ngưỡng `n ≥ 30` của AD-17, nghĩa là nhiều ô thống kê sẽ trả `insufficient_data` đúng vào vai trò chủ lực của demo.
*Sửa:* thêm **AD-19 — Nhập dữ liệu nền một lần làm snapshot gốc**: `step-07-jev-extracted.jsonl` được nhập đúng một lần vào `job_raw` với một `snapshot_id` cố định (ảnh chụp 9–10/2026) và cờ `is_backfill = true`; vòng đời tin của khối này **không tính được** nên `times_seen = 1`, `times_reposted = null`, và dấu hiệu D4 (FR-31) phải trả "không đánh giá được" cho nó; mọi `meta.sources[]` phải phân biệt tin nền với tin thu hằng đêm. Sau bước nhập đó, file JSONL mới là "tiện ích lúc dev".

**C2 — Mô tả trong bộ dữ liệu duy nhất đã bị thay bằng bản viết lại tiếng Anh; văn bản gốc không còn trong repo. Bộ chuẩn 200 JD của Sprint 2 và AD-3 không thực hiện được trên dữ liệu đang có.**
`step-05-consolidate.py` ghi `merged = {**row, "description": clean}` — **thay thế**, không thêm trường. Đếm trên `data/step-07-jev-extracted.jsonl`: **3.464/3.469 bản ghi** có `description` bắt đầu bằng `## ` (khung Markdown tiếng Anh do Claude sinh: `## Company / ## Details / ## Responsibilities / …`). step-06 lại nhấn thêm *"All extracted text MUST be in English"*. Văn bản gốc chỉ còn ở `data/step-03-full.jsonl` — **không có trong repo**, bị `.gitignore` chặn, README ghi "hơn 600 MB và đều tái tạo được từ pipeline".
Hệ quả: (i) FR-6 và brief §4 đòi bộ chuẩn 200 JD lấy **từ văn bản gốc** (*"không lấy từ bản mô tả đã được viết lại sang tiếng Anh"*) → không có nguồn để lấy, phải chạy lại step-03 trên hàng nghìn trang hoặc crawl lại, việc này không có trong ô Sprint 2 nào; (ii) nếu dùng AD-19 (C1) nhập dữ liệu nền rồi chạy AD-3 trên đó, LLM sẽ trích "lượt nhắc nguyên văn" **từ bản dịch tiếng Anh**, nên chỉ số precision/recall tách riêng cho **nhóm kỹ năng viết bằng tiếng Việt** (FR-6, một trong bốn bài toán khó §6.5, và là điểm bán của đồ án) sẽ được đo trên văn bản đã mất hết tiếng Việt; (iii) spine không nhắc step-05 một lần nào, không nói nó bị bỏ, và không có rule nào bảo vệ văn bản gốc.
*Sửa:* thêm convention **"Văn bản gốc là bất biến"**: `job_raw.description_original` không bao giờ bị ghi đè; mọi bản viết lại/dịch (nếu còn dùng) nằm ở cột/bảng khác; cổng trích xuất của AD-9 **chỉ** đọc `description_original`. Và thêm vào Sprint 2 một việc có tên: phục hồi văn bản gốc cho ≥ 200 tin (hoặc crawl lại một mẫu đủ 200) trước khi gán nhãn.

**C3 — AD-16 mô tả sai giao diện thật của cả 9 crawler; 2/9 là crawler người-trong-vòng nên "snapshot hằng ngày" của Sprint 1 không thực hiện được như spine giả định.**
Chi tiết ở §2. Điểm nặng nhất: `topcv.py` (38,1% dữ liệu, R1 chạy cả bản công khai) chạy bằng `interactive_scrape` — `while True` + người thật bấm sang trang + `Ctrl+C` để kết thúc. Không có cronjob nào gọi được nó.
*Sửa:* câu Rule đề xuất ở §2.3.

### High

**H1 — FR-2 và FR-5 không được AD nào bind; `polite.py` không được ratify; không có bước xóa PII trong dòng dữ liệu.** Hai FR có trọng lượng pháp lý cao nhất của dự án là hai FR duy nhất trong 4.1 không có invariant. Đề xuất AD-20 ở §3.1 và bước `redact` ở §3.2.

**H2 — Dòng dữ liệu của spine thiếu hẳn bước "lấy mô tả đầy đủ" (step-03).** 508 dòng, bước đắt và dễ vỡ nhất (Playwright, Cloudflare, 4 extractor theo nguồn, retry + checkpoint 200 tin), và là bước duy nhất cấp văn bản cho 4/5 nguồn kế thừa. Chi tiết §3.4.

**H3 — AD-4 (publish nguyên khối sau khi mọi bảng tổng hợp đã ghi) khiến Sprint 1 "bật snapshot hằng ngày" không có định nghĩa thỏa được.** Cần trạng thái snapshot phân tầng. Chi tiết §5.1(a).

**H4 — Dagster-trong-Docker + Playwright `channel="chrome"` headful: sơ đồ triển khai `dag --> sites` không chạy được với code hiện tại.** Cần quyết định rõ crawler chạy trong container (đổi sang chromium headless) hay trên host. Chi tiết §5.1(c).

**H5 — Trang nội dung công khai (AD-13, AD-14) là workstream mới, không có FR trong PRD *và* không có ô nào trong kế hoạch 8 sprint.** Spine chỉ nhận nửa đầu ở Câu hỏi mở 1. Chi tiết §5.4.

### Medium

**M1 — Bỏ Jev làm mất ngưỡng độ tự tin 0,7 + quy tắc "nghi ngờ thì giữ" (FR-7) và validation enum chặt của step-07; chi phí chưa tính lại; taxonomy cũ phải map sang enum mới của FR-7.** Chi tiết §3.5 và §4.

**M2 — Bảng Stack thiếu các phụ thuộc load-bearing của FR-1.** `scraper/` là một node trong AD-1 nhưng `playwright`, `requests`, `beautifulsoup4`, `lxml`, `tqdm` không có trong Stack, dù chúng quyết định được/không được của FR-1 (và `playwright` là lý do H4 tồn tại). Ngược lại `pandas` có trong `requirements.txt` nhưng biến mất khỏi cả hai nơi — nên nói rõ nó bị loại hay giữ.

**M3 — "Kèm kết quả rà soát điều khoản sử dụng" (brief §2) rơi, và R1–R4 không xuất hiện trong spine.** Bảng cấu hình của AD-10 cần trường ToS (kết luận, ngày rà, người rà, `politeness_exception`), và spine cần một dòng thừa nhận nó phải chứa crawler né phát hiện bot trên bản công khai — vì điều đó ảnh hưởng tới lựa chọn ở H4.

**M4 — "Khung JSON cố định" cho lộ trình (brief §2) và "in trình duyệt ra PDF" (FR-16) đều rơi.** Cái thứ hai có rủi ro thật: FR-16 làm ở server sẽ chạm AD-11. Spine nên nói rõ bản tải về sinh phía client, và lộ trình trả về theo một schema đóng mà LLM không được chèn trường.

**M5 — AD-16 hạ file JSONL xuống "tiện ích lúc dev" sẽ phá cơ chế resume và trần request của careerlink/itnavi.** `careerlink.py` dùng chính file output để dựng tập `done` và `data/state/careerlink.json` để giữ `queue`/`pages`/`last_run`/khoảng cách ≥ 1 giờ; `itnavi.py` dùng file output để dựng `done` theo `job_id`. Mất chúng là mất trần 40 request/lượt — đúng thứ đang giữ CareerLink không bị hCaptcha. Cần bảng `source_crawl_state` (điểm 3 trong Rule đề xuất §2.3).

---

## 7. Việc cần làm, gọn lại

| # | Việc | Khi |
|---|---|---|
| 1 | Sửa AD-16 theo §2.3 (6 điểm) | trước khi chia epic |
| 2 | Thêm AD-19 *Nhập dữ liệu nền làm snapshot gốc* (C1) | trước khi chia epic |
| 3 | Thêm AD-20 *Cổng lịch sự duy nhất* (FR-2) và bước `redact` + rule PII (FR-5) | trước khi chia epic |
| 4 | Thêm convention *Văn bản gốc là bất biến*; ghi rõ step-05 bị bỏ (C2) | trước khi chia epic |
| 5 | Thêm bước `fetch_details` vào Structural Seed + convention `detail_included` / `listing_only` (H2) | trước khi chia epic |
| 6 | Định nghĩa trạng thái snapshot phân tầng, nghiệm thu Sprint 1 ở mức `ingested` (H3) | ngay, ảnh hưởng Sprint 1 |
| 7 | Quyết: crawler chạy trong container hay trên host (H4) | ngay, ảnh hưởng Sprint 1 |
| 8 | Hoãn Dagster sang Sprint 2 (AD-15 cho phép), Sprint 1 chạy bằng cron/Task Scheduler gọi CLI | ngay |
| 9 | Thêm vào Sprint 2 việc "phục hồi văn bản gốc cho ≥ 200 tin" (C2) | ngay |
| 10 | Chọn đường thoát cho Review giữa kỳ (§5.3: nhập dữ liệu nền, hay demo slice chỉ-hồ-sơ) | trước 9/11 |
| 11 | Cấp thời gian cho trang nội dung công khai, hoặc hoãn nó khỏi v1 (H5) | khi cập nhật PRD |
| 12 | Ước tính lại chi phí LLM sau khi bỏ Jev, đối chiếu trần §6.4 (M1) | Sprint 2 |
| 13 | Thêm `playwright`/`requests`/`beautifulsoup4`/`lxml` vào Stack; chốt `pandas` (M2) | nhỏ |
| 14 | Thêm địa chỉ liên hệ vào `polite.USER_AGENT` (FR-47, Sprint 1) | nhỏ, sửa 1 dòng |
