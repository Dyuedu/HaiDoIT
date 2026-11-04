# Phân tích việc làm IT ở Việt Nam — Phiên bản 2026

Thu thập và phân tích tin tuyển dụng IT **gần đây** tại Việt Nam, để làm video
**"Phân tích [N] việc làm IT ở Việt Nam — Phiên bản 2026"** trên kênh
[Học Lập Trình cùng Phát](https://www.youtube.com/@TranSonPhat).

Bản 2026 này so sánh với bộ dữ liệu 3.101 tin cũ
([IT-Job-Posting](https://github.com/SonPhatTranDeveloper/IT-Job-Posting)) để xem
thị trường đã dịch chuyển ra sao, và bổ sung các chiều mới mà video cũ chưa đụng
tới: cấp bậc (junior/mid/senior), mức lương, và mô hình làm việc
(remote/hybrid/onsite).

> Lưu ý: mọi dữ liệu và thí nghiệm ở đây chỉ dành cho mục đích giáo dục. Không
> dùng cho mục đích thương mại hoặc vi phạm điều khoản của các nền tảng.

## Nguồn dữ liệu

| Nguồn | Loại | Ghi chú |
| --- | --- | --- |
| ITviec | IT | public, server-rendered, có working-model |
| TopDev | IT (đã thành Saramin) | cần lọc danh mục IT |
| VietnamWorks | tổng hợp | mục inTECH, có lương |
| TopCV | tổng hợp | cần lọc việc làm IT |
| LinkedIn | IT | Playwright + đăng nhập tài khoản |
| CareerLink | tổng hợp | danh mục CNTT phần mềm + phần cứng/mạng, JSON-LD có lương VND; tối đa 40 request/lượt, cách nhau ≥ 1 giờ |
| ITNavi | IT | HTML danh sách + JSON chi tiết `/ajax/get-job-by-id`; tối đa 150 tin/lượt |
| Zalo Careers | trang công ty | API JSON công khai `/api/v2/jobs`, một request mỗi team |
| MoMo Careers | trang công ty | danh sách đọc từ DOM (trình duyệt headless bấm "Xem thêm"), chi tiết từ `__NEXT_DATA__` |

Bốn crawler mới dùng chung `crawlers/polite.py`: User-Agent trung thực, kiểm tra
`robots.txt`, giãn cách cố định giữa các request, và **dừng hẳn** khi gặp
403/429 hoặc captcha (không tìm cách vượt qua).

## Pipeline

```
crawl                 → data/raw/<nguồn>.jsonl    4 nguồn HTTP trên VPS,
                                                  4 nguồn cần trình duyệt chạy tay
  dedupe.py           → data/dedup.jsonl          gom trùng
  consolidate.py      → data/consolidated.jsonl   dọn HTML và boilerplate, không gọi API
  extract.py          → data/extracted.jsonl      MỘT lần gọi Claude mỗi tin:
                        data/non_it.jsonl         lọc + trích xuất + phân loại
  ingest.py           → Postgres                  bảng jobs và job_observations
```

Chạy cả chuỗi: `python pipeline.py`. Từng chặng: `pipeline.py crawl|dedupe|process|sync`.

Tên file theo từ vựng bước của `ARCHITECTURE-SPINE.md`, không đánh số — thứ tự đã
đổi hai lần và số thứ tự mục theo mỗi lần đổi.

Hai mô hình, hai việc khác nhau:

- **Claude** (`claude-sonnet-4-6`, step-06) làm phần trích xuất mở — đọc mô tả
  việc làm viết tự do và trả về JSON có cấu trúc.
- **Jev** (`jev-latest`, TypeSafe, step-04 và step-07) làm phần quyết định nhỏ
  lặp lại nhiều lần: lọc IT / không phải IT, rồi phân loại bốn chiều
  (`title_category`, `seniority_category`, `location_category`,
  `work_model_category`). Step-04 chỉ bỏ một tin khi Jev trả lời `non_tech` với
  độ tự tin từ 0.7 trở lên, nên tin nào còn mơ hồ thì vẫn được giữ lại.

## Chạy

Cần `uv` (hoặc `pip install -r requirements.txt`):

```bash
# 1. crawl từng nguồn
make crawl-itviec
make crawl-topdev
make crawl-vietnamworks
make crawl-topcv
make crawl-linkedin        # cần đăng nhập LinkedIn bằng Playwright
make crawl-careerlink      # chạy lại mỗi ≥ 1 giờ cho tới khi hết hàng đợi
make crawl-itnavi          # chạy lại tới khi không còn tin mới
make crawl-zalo
make crawl-momo            # cần: playwright install chromium

# Windows: make PY=.venv/Scripts/python crawl-zalo
# hoặc chạy thẳng: .venv/Scripts/python -m crawlers.zalo

# 2. bỏ trùng + lấy mô tả đầy đủ
make dedupe
make details

# 3. lọc IT / không phải IT, rồi gộp (cần TYPESAFE_API_KEY)
export TYPESAFE_API_KEY=...
make classify
make consolidate

# 4. trích xuất bằng Claude (cần ANTHROPIC_API_KEY)
export ANTHROPIC_API_KEY=sk-ant-...
make extract

# 5. phân loại bốn chiều bằng Jev
make jev-classify
```

## Dữ liệu trong repo này

Repo chỉ công bố **`data/step-07-jev-extracted.jsonl`** — 3.469 tin IT đã qua
toàn bộ pipeline. Những thứ sau **không** được đưa lên, và `.gitignore` chặn
sẵn cả thư mục `data/` để một lần chạy lại không vô tình publish thêm gì:

- `data/linkedin-profile-webkit/` — profile Playwright đã đăng nhập LinkedIn
  (cookie, LocalStorage). Tuyệt đối không publish.
- `data/raw/` — dữ liệu thô từng nguồn.
- Các file trung gian và cache (`step-03-full`, `step-04-cache`, …), tổng cộng
  hơn 600 MB và đều tái tạo được từ pipeline.

## Cấu trúc dữ liệu

Mỗi dòng trong `data/step-07-jev-extracted.jsonl` là một tin tuyển dụng.

**Trường lấy trực tiếp từ trang tuyển dụng:**

| Trường | Ghi chú |
| --- | --- |
| `site` | `itviec` / `topdev` / `vietnamworks` / `topcv` / `linkedin` |
| `job_url`, `title`, `company`, `location` | nguyên văn từ nguồn |
| `work_model`, `role_type`, `salary`, `posted_at` | nguyên văn, không chuẩn hoá |
| `description` | mô tả đầy đủ, cắt ở 12.000 ký tự khi gửi cho Jev |
| `date_posted`, `employment_type`, `experience_months` | chỉ một số nguồn có |

**Trường do Claude trích xuất** (`extracted_info`, step-06, đã dịch sang tiếng Anh):

`title_cleaned` · `tech_stack[]` · `keywords[]`

**Trường do Jev phân loại** (step-04 và step-07):

| Trường | Giá trị |
| --- | --- |
| `is_tech`, `tech_confidence` | `tech` / `non_tech` + độ tự tin 0–1 (step-04) |
| `classification.title_category` | Backend · Frontend · Fullstack · Mobile · Data / AI / ML · DevOps / SRE / Cloud · QA / Testing · Product / BA / Agile · Security / Cyber · Infrastructure / IT Support · UI/UX Design · Game Development · Other |
| `classification.seniority_category` | Intern · Fresher / Entry-level · Junior · Mid-level · Senior · Lead / Principal · Manager · Director / Executive · Unknown |
| `classification.location_category` | Ho Chi Minh · Ha Noi · Da Nang · Other |
| `classification.work_model_category` | On-site · Hybrid · Remote · Unknown |

### Đọc số liệu cho đúng

Vài giới hạn nên biết trước khi dùng bộ dữ liệu này:

- **Nguồn không giống bản 3.101 cũ.** Bản này có 5 nguồn thay vì 3, và riêng
  TopCV chiếm khoảng 38%. Một nhóm việc làm tăng hay giảm so với video cũ có
  thể là do thị trường, mà cũng có thể là do đổi nguồn.
- **`Other` trong `title_category` khá lớn** (604 tin) — phần lớn từ các trang
  tổng hợp. `Frontend` và `Mobile` thấp bất thường, rất có thể vì bị xếp sang
  `Fullstack` hoặc `Other`.
- **`salary` phần lớn không có số.** Khoảng 76% ghi "Thoả thuận", "Thương
  lượng" hoặc yêu cầu đăng nhập. Phần có số thì lệch về mức trung bình trở
  xuống.
- **`date_posted` chỉ có ở 1.809 / 3.469 tin.** Trong số đó hơn 90% là tháng
  9–10/2026.
- **`work_model_category` có 22% là `Unknown`.** Tính tỉ lệ remote nên nói rõ
  mẫu số là toàn bộ tin hay chỉ tin có ghi mô hình.
