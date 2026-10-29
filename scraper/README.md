# scraper/ — cào tin tuyển dụng IT

Chuyển từ `D:\FR_KS_FU_Java_03\SkillNexus\pipeline` (bản ngày 2026-10-21, bản đã cào ảnh 832 tin) sang đây
theo ARCHITECTURE-SPINE (`scraper/`, `scraper/taxonomy.json`). Hành vi giữ nguyên; chỉ đổi:

- Không còn phụ thuộc `backend/` của SkillNexus: bộ chuẩn hóa kỹ năng (`normalizer.py`) đọc
  `scraper/taxonomy.json` thay cho bảng Postgres `skills_taxonomy`. File này là đúng trạng thái bảng lúc cào
  (seed + migration 001: 31 kỹ năng, 92 khóa tra cứu).
- Lệnh chạy: `python -m scraper.jobboards` (từ thư mục gốc repo).
- Bỏ bộ nạp dataset VietJobs (`vietjobs_loader.py`): tin cũ, không có ngày đăng. Model tin và luật level
  chuyển vào `jobboards.py`.

**Chưa làm theo spine (việc của story cào/nạp trong `epics.md`):** ghi `open-jobs/open-jobs.jsonl` và
`bronze/` lên Silo, đẩy Redis (AD-5, AD-20, AD-21), dòng ảnh theo trường AD-5, bỏ tin ngoài 3 thành phố.
Hiện bộ cào vẫn ghi nối thêm vào `data/scraped/<source>.jsonl` và giữ tiêu đề + tên công ty.

## Cài đặt và test

```bash
pip install -r scraper/requirements.txt
python -m pytest scraper          # offline, httpx.MockTransport
```

## Bộ cào tin tuyển dụng IT Việt Nam (`jobboards.py`, `ats.py`)

Lấy tin tuyển dụng IT đang mở từ **ITviec**, **TopDev**, **API công khai của ATS** (Greenhouse, Lever,
Workable — 13 công ty có văn phòng ở Việt Nam) và **trang tuyển dụng công ty** (Cốc Cốc). Kết quả là JSONL, mỗi dòng một `ScrapedJob` (gồm `source_url`, lương VND/USD,
`valid_through`).
Bộ cào **không** ghi DB.

### Cách lấy dữ liệu

```
robots.txt ──Sitemap:──▶ sitemap index ──▶ sitemap job ──▶ trang chi tiết ──▶ <script type="application/ld+json">
                                                                               @type: JobPosting
```

Mọi trang được hỗ trợ đều nhúng khối schema.org `JobPosting` (dữ liệu có cấu trúc mà trang tự công bố
cho máy tìm kiếm). Đọc khối này thay vì bóc DOM nên không cần Selenium/Playwright và ít vỡ khi trang
đổi giao diện.

| Trường JSON-LD | Trường đầu ra |
| --- | --- |
| `title` | `title`, `standardized_title` |
| `hiringOrganization.name` | `company_name` |
| `skills` (chuỗi phân tách bằng dấu phẩy) | `skills` — qua `normalizer.normalize_batch` (AD-6) |
| `baseSalary` (`currency`, `minValue`/`maxValue`, `unitText`) | `min/max_salary_vnd` hoặc `min/max_salary_usd`; `YEAR` quy về tháng; `HOUR`/`"Negotiable"`/thiếu → `is_salary_negotiable = true` |
| `jobLocation[].address.addressRegion` | `location` (chỉ tỉnh/thành) |
| `experienceRequirements.monthsOfExperience` | `months_of_experience`, `level` (< 12 tháng Fresher, < 36 Junior, < 60 Middle, còn lại Senior; tiêu đề có thực tập/intern → Intern; thiếu số tháng → suy từ tiêu đề) |
| `datePosted`, `validThrough` | `published_date`, `valid_through` |

**Không bao giờ giữ** (AD-7 / AR-6): `description`, `jobBenefits`, `streetAddress`, logo, mọi văn bản JD.
Không lương được quy đổi tiền tệ (không bịa tỷ giá): USD vào cột USD, VND vào cột VND.

Trang không có JSON-LD nhưng dựng bằng Next.js App Router: đọc payload RSC trong `self.__next_f.push([1, "..."])`
(nối các chuỗi, tách dòng `ID:JSON`, cách đọc giống [njsparser](https://pypi.org/p/njsparser)) và lấy object đầu tiên
có `jobTitle`. Lương chỉ lấy khi payload ghi rõ tiền tệ. Hiện chưa nguồn nào trong `SOURCES` cần đường này.

`source_id` = SHA-256(`source` + URL) — ổn định để Story 7.4 `MERGE` idempotent.

Nguồn không có trường `skills` (ATS, trang công ty): kỹ năng được **trích từ mô tả** bằng
[`skills_text.py`](skills_text.py) — quét khóa của `taxonomy.json`, qua `normalize_batch`, rồi bỏ văn bản
(AD-7). Bí danh trùng từ thông dụng được siết: `go`/`rest`/`node`/`spring`/`react`/`vue` chỉ khớp đúng kiểu
viết công nghệ; `Go`, `Spring` còn phải đứng trong danh sách ("Java, Go, C#"), nên "go beyond", "Spring 2026"
không bị tính; `container` không quét.

**Lọc IT** — tiêu đề có vai trò không-IT (`_NON_IT_TITLE_RE`: artist, video editor, creative, marketing,
sales, talent, kế toán...) luôn bị loại. Còn lại:

| Nguồn | Coi là IT khi |
| --- | --- |
| ITviec | luôn (trang chỉ có tin IT) |
| TopDev | slug có từ khoá IT (trước khi tải) **và** (kỹ năng khớp taxonomy **hoặc** tiêu đề IT) |
| ATS | tiêu đề IT **hoặc** phòng ban/nhóm/chức năng kỹ thuật — *không* dựa vào kỹ năng trích từ mô tả, vì đoạn giới thiệu công ty lặp ở mọi tin (AvePoint nhắc Azure cả trong tin Commission Specialist) |
| Trang công ty không có `skills` | slug có từ khoá IT **và** tiêu đề / `occupationalCategory` IT |

### Nguồn — khảo sát ngày 2026-10-21

| Trang | robots.txt | Chống bot | Dữ liệu có cấu trúc | Trạng thái |
| --- | --- | --- | --- | --- |
| ITviec | cho phép (chỉ cấm `/subscriptions/new`) | không | sitemap `twinnings_jobs_desc_vn.xml` (~650 tin) + JSON-LD | **hỗ trợ** |
| TopDev | cho phép `/detail-jobs/` | không | `sitemap-jobs.xml` → 139 trang × 20 tin + JSON-LD | **hỗ trợ**, lọc IT |
| TopCV | cho phép | **Cloudflare challenge** ngay cả với sitemap | — | **không hỗ trợ** |
| Cốc Cốc (`careers.coccoc.com`) | cho phép | không | JSON-LD trên trang tin, **không sitemap** → lấy link từ trang danh sách (chỉ ~4 tin hiện trong HTML) | **hỗ trợ** |
| VietnamWorks | cho phép trang tin, cấm endpoint AJAX | không | không JSON-LD (render phía client), sitemap trả 404, chỉ có API nội bộ không công bố | **không hỗ trợ** |

- **TopDev** gắn `industry: Information Technology` cho mọi tin, kể cả kế toán/xây dựng/phiên dịch
  (chạy thử 12 tin đầu sitemap: chỉ 3 tin IT). Bộ cào giữ tin có ít nhất một kỹ năng khớp
  `taxonomy.json` **hoặc** tiêu đề chứa vai trò IT (`_IT_TITLE_RE` — cần vì taxonomy còn nhỏ:
  "RPA Developer" với kỹ năng ERP/SAP/RPA không khớp kỹ năng nào). Số tin bị loại in ở dòng `non_it`.
  Sitemap TopDev dùng `/viec-lam/…` (tiếng Việt) và `/detail-jobs/…` (tiếng Anh) cho cùng một tin;
  bộ cào chỉ đi sitemap tiếng Việt.
- Nếu 3 sitemap liên tiếp không có URL nào khớp mẫu tin, bộ cào dừng với lỗi "cấu trúc trang có thể đã đổi"
  thay vì âm thầm đi hết cây sitemap.
- **Lọc thô theo slug** (TopDev): trước khi tải trang, slug URL phải chứa từ khoá IT (`it_slug`) — tránh tải
  ~70% số trang không phải IT. Cố ý rộng tay (giữ nhầm QC nhà máy, "sáp waxing"... rồi `is_it_job` loại sau);
  đo trên 60 slug: giữ 19, không sót tin IT nào. Số tin bỏ qua in ở dòng `skipped_slug`.
- **TopCV**: trang thử thách Cloudflare là tín hiệu chủ trang không muốn bot. Bộ cào không có và sẽ không
  có cơ chế vượt (headless giả trình duyệt, xoay proxy, giải challenge). Muốn dùng dữ liệu TopCV thì xin
  phép/API chính thức.
- **VietnamWorks**: endpoint `ms.vietnamworks.com/job-search/...` trả JSON nhưng là API nội bộ không công bố,
  và robots.txt của trang chặn các endpoint AJAX. Chưa dùng; cân nhắc lại nếu có API/thoả thuận chính thức.

### Khảo sát mở rộng — 2026-10-21

Tiêu chí thêm nguồn: robots.txt cho phép, không chặn bot định danh, ToS **không** cấm crawl tường minh,
có JSON-LD `JobPosting` (hoặc dữ liệu có cấu trúc tương đương). Không nguồn nào dưới đây đạt:

| Trang | Kết quả | Lý do loại |
| --- | --- | --- |
| CareerViet | robots cho phép, sitemap + JSON-LD tốt | **ToS cấm** "trình thu thập dữ liệu, người máy" ([Thỏa thuận sử dụng](https://careerviet.vn/vi/employers/use), mục *Những Hạn Chế Sử Dụng Cụ Thể*) |
| Glints (VN) | robots cho phép, 58 sitemap VN + JSON-LD tốt | **ToS cấm** "screen scraping, data mining, robots" khi chưa có đồng ý bằng văn bản ([Terms of Use](https://glints.com/vn/about/terms) §2.3(9)) |
| JobsGO | robots cho phép | 403 với User-Agent bot định danh |
| ViecOi | robots cho phép | Cloudflare challenge |
| Vieclam24h | — | 403 ngay cả với robots.txt |
| timviec365 | robots cho phép, JSON-LD | không có kỹ năng, lương giả (`1–1`), gần như toàn tin ngoài IT — giá trị thấp |
| DevWork | robots cho phép, chuyên IT | không JSON-LD (phải bóc DOM), không sitemap — ứng viên tương lai nếu cần |
| ITNavi, CareerLink, 123job | robots cho phép | không sitemap dùng được, link tin render bằng JS |

Khi ToS cấm tường minh, bộ cào theo ToS dù robots.txt cho phép. Muốn dùng các nguồn này: xin phép bằng
văn bản / API chính thức.

### API công khai của ATS (`ats.py`) — 2026-10-21

Nhiều công ty công nghệ ở Việt Nam đăng tin qua ATS; các ATS này công bố API job board không cần khóa:

| ATS | Endpoint (1 request / công ty) | robots.txt host API | Điều khoản |
| --- | --- | --- | --- |
| Greenhouse | `boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true` | cho phép (chỉ cấm `/embed/`) | ["Job Board data is publicly available, so authentication is not required for any GET endpoints"](https://docs.greenhouse.io/job-board.html) |
| Lever | `api.lever.co/v0/postings/{token}?mode=json` | cho phép, `Crawl-delay: 1` | tin đã đăng là công khai và "may be scraped by third parties" ([`lever/postings-api`](https://github.com/lever/postings-api)) |
| Workable | `apply.workable.com/api/v1/widget/accounts/{token}?details=true` | cho phép | widget API công khai |
| SmartRecruiters | — | **`User-agent: *` → `Disallow: /`** (chỉ LinkedInBot) | **không dùng** (KMS, Endava, Grab... dùng ATS này) |

Bảng tin hiện có (`BOARDS` trong `ats.py`; thêm công ty = thêm một dòng): Greenhouse — NAVER Vietnam, Axon,
WorldQuant, AvePoint, Joblogic, Thoughtworks; Lever — Amanotes, Gradion, Portcast, ShopBack, Ninja Van, Keyloop;
Workable — OptiSigns.
Chạy thử 2026-10-21: 125 tin ở Việt Nam → **78 tin IT**; 60/81 tin (gồm Cốc Cốc) trích được ít nhất một kỹ năng.

Dò thêm ngày 2026-10-29 (chạy chính adapter + bộ lọc của `ats.py`, không ghi file):

| Kết quả | Bảng tin |
| --- | --- |
| **Thêm** | Lever `keyloop` — 15 tin VN, 14 tin IT (TP.HCM); Greenhouse `thoughtworks` — 3 tin VN, 2 tin IT (TP.HCM) |
| Có tài khoản Workable nhưng 0 tin | `momo` (M_Service), `katalon`, `shopee`, `holistics`, `nimble`; `nab`, `sea`, `vng` là tên chung, chưa chắc đúng công ty |
| Có bảng tin nhưng không có tin IT ở VN | Greenhouse `agoda` (312 tin, 2 tin VN, 0 tin IT) |
| 404 trên cả Greenhouse / Lever | MoMo, Shopee/Sea, VNG, Katalon, NAB, Sky Mavis, Parcel Perform, Employment Hero, Trusting Social, TymeX, East Agile, Got It, Zalora, Persefoni |

NAB Innovation Centre, MoMo, Shopee, VNG, Katalon tuyển qua trang riêng hoặc ATS khác, không qua ba API trên.
Dò lại các tài khoản Workable 0 tin theo định kỳ: có thể chúng chỉ đăng khi có đợt tuyển.
Chỉ giữ tin ở Việt Nam (địa điểm / văn phòng / `country`). Lương chỉ khi API trả số (Lever `salaryRange`).

Trang tuyển dụng riêng của công ty Việt Nam đã thử (FPT Software, VNG, MoMo, Tiki, Viettel, Shopee, Grab, Zalo,
VNPT, VinAI, VinBigData, NashTech, Katalon...): đa số render bằng JavaScript và không có JSON-LD, hoặc chặn bot
(FPT Software: Cloudflare; NashTech: 403; VNG: lỗi 500 với bot) — chỉ Cốc Cốc đạt.

### Điều khoản sử dụng (đọc ngày 2026-10-21)

Không trang nào trong ba trang đã đọc có điều khoản cấm crawl/bot một cách tường minh, nhưng cả ba đều
hạn chế **sao chép / phân phối lại nội dung**, nhất là cho mục đích thương mại:

- [ITviec — Thoả thuận sử dụng](https://itviec.com/blog/terms-conditions-vn/) §2.2: nội dung không được
  "lấy, hiển thị, sửa đổi, sao chép, in, bán, tải về, cho thuê" khi chưa có đồng ý bằng văn bản.
- [TopDev — Term of services](https://topdev.vn/term-of-services) và
  [VietnamWorks — Thoả thuận sử dụng](https://www.vietnamworks.com/thoa-thuan-su-dung) (mục *Các Quyền
  Sở Hữu Trí Tuệ*): cấm sao chép/phân phối/công bố và khai thác thương mại nội dung; cho phép bản sao
  để xem và dùng nội bộ.

Vì vậy bộ cào chỉ giữ **dữ kiện** (tiêu đề, công ty, kỹ năng, lương, địa điểm, level, ngày) — không lưu,
không hiển thị lại văn bản JD (AD-7) — và chỉ phục vụ phân tích phi thương mại. Đây không phải tư vấn
pháp lý: trước khi dùng ở quy mô lớn, công khai dữ liệu, hay thương mại hoá, cần xin phép các trang.

### Nguyên tắc lịch sự (`polite_http.py`)

- Đọc robots.txt trước mọi request; URL bị cấm → bỏ qua. robots.txt lỗi 5xx → coi như cấm hết
  (RFC 9309); 404 → không giới hạn. Tôn trọng `Crawl-delay`.
- User-Agent trung thực: `SkillNexusBot/0.1 (+non-commercial research; contact: …)`. Không giả trình duyệt.
- Mặc định ≥ 3 s + jitter 0–2 s giữa hai request cùng host, tuần tự (không chạy song song).
- 429/5xx: chờ `Retry-After` (trần 300 s) hoặc backoff lũy thừa, tối đa 3 lần thử lại.
- Trang thử thách chống bot hoặc 401/403 → dừng nguồn ngay, thoát mã 3.
- `--limit` mặc định 50 trang chi tiết mỗi lần chạy; URL đã cào lưu ở `<out>.state.json` và được bỏ qua
  ở lần sau (không dựa vào `lastmod` vì hai trang ghi giờ sinh sitemap cho mọi URL).

### Lệnh chạy

Từ thư mục gốc repo (normalizer nạp `scraper/taxonomy.json`):

```bash
python -m scraper.jobboards --source itviec --limit 20 --contact you@example.com
python -m scraper.jobboards --source topdev --limit 100
python -m scraper.jobboards --source ats                 # API ATS (không cần --limit)
python -m scraper.jobboards --source coccoc
python -m scraper.jobboards --source all --limit 1000     # mọi nguồn, tuần tự

# tuỳ chọn: --out path.jsonl (chỉ khi một nguồn)   --min-delay 5   --refresh (tải lại cả URL đã cào)
```

Đầu ra mặc định `data/scraped/<source>.jsonl` (ghi nối thêm) và `data/scraped/<source>.state.json`;
`data/` đã nằm trong `.gitignore`. Mã thoát: `0` ok, `1` lỗi mạng/sitemap, `2` tham số sai, `3` bị chặn
(nhiều nguồn: mã lớn nhất; một nguồn lỗi không làm dừng nguồn khác).

Ước lượng thời gian lần đầu với mặc định: ITviec ~650 tin ≈ 45 phút; TopDev 139 sitemap + ~30% của
~2.800 tin (sau lọc slug) ≈ 1 giờ. Các lần sau chỉ tải tin mới.

### Chạy định kỳ — tích luỹ dữ liệu

Tin trên hai trang chỉ sống ~1 tháng (`valid_through`), nên độ phủ đến từ việc chạy **hằng ngày** và tích luỹ:
mỗi lần chỉ tải tin chưa có trong state.

```powershell
scraper\run_scrapers.ps1 -Limit 1000          # Windows; log ở data\scraped\run-*.log / *.err.log
```
```bash
scraper/run_scrapers.sh 1000                  # Linux/macOS
```

Lệnh lên lịch (Task Scheduler / cron) ghi ở đầu mỗi script. Đặt biến môi trường `SCRAPER_CONTACT`
để đưa email liên hệ vào User-Agent.

### Test

Chạy offline với `httpx.MockTransport`:
- `scraper/tests/test_jobboard_scraper.py` — robots, Cloudflare, 429/Retry-After, giãn cách, sitemap, lọc slug/IT,
  AD-7, state;
- `scraper/tests/test_ats_scraper.py` — 3 adapter ATS, host ATS bị chặn, trang danh sách (Cốc Cốc), trích kỹ năng
  từ văn bản (từ nhập nhằng), lọc không-IT, chuẩn hoá thành phố.
