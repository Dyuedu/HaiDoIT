# Rà soát độc lập — tính thực tế của các lựa chọn công nghệ trong ARCHITECTURE-SPINE

- **Tài liệu được rà:** `_bmad-output/planning-artifacts/architecture/architecture-HaiDoIT-2026-11-03/ARCHITECTURE-SPINE.md`
- **Ngày rà:** 2026-11-03
- **Người rà:** reviewer độc lập (không tham gia buổi làm kiến trúc)
- **Phạm vi:** chỉ phần **Stack**, các khẳng định kỹ thuật đi kèm (Dagster, Next.js ISR, Batch API, ngân sách RAM). Không rà AD-1..AD-18 về mặt thiết kế.
- **Phương pháp:** tra cứu trực tiếp trên registry và tài liệu chính thức — PyPI JSON API, npm registry API, Docker Hub tags API, endoflife.date API, `nodejs.org/dist/index.json`, `platform.claude.com/docs`, `nextjs.org/docs`, `dagster.io/docs`, `postgresql.org/docs`, `airflow.apache.org/docs`, `docs.sqlalchemy.org`. Không có kết luận nào trong bài này dựa vào ký ức mô hình; mỗi con số đều có nguồn kèm theo.

---

## 1. Verdict

**Bảng Stack chính xác đến mức đáng ngạc nhiên — 17/17 phiên bản được kiểm đều đúng là phiên bản hiện hành ngày 03/11/2026, và cả hai model Claude đều tồn tại. Nhưng ba *khẳng định* đi kèm thì yếu: Dagster không phải "daemon + UI" mà là ba service thường trú cộng một process cho mỗi lượt chạy; `revalidatePath` không sinh lại trang mà chỉ đánh dấu hết hạn; và ngân sách 4 GB RAM không đứng được vào đúng lúc pipeline hằng đêm chạy. Không cần đổi công nghệ nào, nhưng cần sửa sơ đồ triển khai, sửa AD-13 và chốt lại cỡ VPS.**

Phân loại:

| Mức | Số phát hiện |
|---|---|
| Chặn (phải sửa trước khi chia epic) | 3 |
| Nặng (sửa trong Sprint 1) | 4 |
| Vừa (ghi nhận, xử lý khi gặp) | 5 |
| Xác nhận đúng (không phải sửa) | 21 |

---

## 2. Bảng Stack — kiểm từng dòng

Cột "Thực tế 03/11/2026" lấy trực tiếp từ registry. Lệnh dùng: `GET https://pypi.org/pypi/<pkg>/json` → `info.version`; `GET https://registry.npmjs.org/<pkg>` → `dist-tags.latest`.

### 2.1 Phía Python (PyPI)

| Dòng trong spine | Ghi trong spine | Thực tế trên PyPI | Ngày phát hành bản đó | `requires_python` | Kết luận |
|---|---|---|---|---|---|
| Python | 3.13 | 3.13 là bản ổn định đang dùng rộng rãi; 3.14 đã ra | — | — | ✅ Hợp lý (xem §2.5) |
| Dagster | 1.13.28 | **1.13.28** | 2026-10-30 | `>=3.10,<3.15` | ✅ Đúng, mới 4 ngày |
| FastAPI | 0.162.0 | **0.162.0** | 2026-10-23 | `>=3.10` | ✅ Đúng |
| SQLAlchemy | 2.1.6 | **2.1.6** | 2026-10-21 | `>=3.11` | ✅ Đúng (xem §4.1) |
| Alembic | 1.20.1 | **1.20.1** | 2026-10-22 | `>=3.10` | ✅ Đúng |
| Pydantic | 2.14.2 | **2.14.2** | 2026-10-29 | `>=3.10` | ✅ Đúng |
| Uvicorn | 0.54.0 | **0.54.0** | 2026-09-25 | `>=3.10` | ✅ Đúng |
| psycopg | 3.3.7 | **3.3.7** | 2026-11-03 | `>=3.10` | ✅ Đúng, phát hành *cùng ngày* rà soát |
| NetworkX | 3.7 | **3.7** | 2026-09-21 | `!=3.14.1,>=3.12` | ✅ Đúng |
| SciPy | 1.18.1 | **1.18.1** | 2026-08-21 | `>=3.12` | ✅ Đúng |
| anthropic (SDK Python) | 2.4.0 | **2.4.0** | 2026-11-02 | `>=3.10` | ✅ Đúng, mới 1 ngày |

**11/11 đúng.** Không dòng nào cũ, không dòng nào bị đổi tên, không dòng nào deprecated. Câu "Kiểm ngày 03/11/2026 trên PyPI" trong spine là một khẳng định kiểm chứng được và nó **đúng**.

Lưu ý nhỏ: `psycopg 3.3.7` ra đúng ngày 2026-11-03 — nghĩa là lúc buổi làm kiến trúc diễn ra, bản mới nhất có thể còn là 3.3.6. Không ảnh hưởng gì, chỉ cho thấy việc ghim phiên bản patch vào tài liệu kiến trúc sẽ hết hạn rất nhanh (xem khuyến nghị §9.3).

Nguồn: [PyPI JSON API](https://warehouse.pypa.io/api-reference/json.html) cho từng package, ví dụ [pypi.org/pypi/dagster/json](https://pypi.org/pypi/dagster/json), [pypi.org/pypi/sqlalchemy/json](https://pypi.org/pypi/sqlalchemy/json).

### 2.2 Phía Node/npm

| Dòng trong spine | Ghi trong spine | `dist-tags.latest` thực tế | Ngày phát hành | Kết luận |
|---|---|---|---|---|
| Next.js | 16.4.4 | **16.4.4** | 2026-11-02 | ✅ Đúng, mới 1 ngày |
| React | 19.3.1 | **19.3.1** | 2026-10-14 | ✅ Đúng |
| deck.gl | 9.4.1 | **9.4.1** | 2026-10-28 | ✅ Đúng |
| @xyflow/react | 12.12.1 | **12.12.1** | 2026-11-02 | ✅ Đúng, mới 1 ngày |
| Tailwind CSS | 4.3.4 | **4.3.4** | 2026-11-02 | ✅ Đúng, mới 1 ngày |

**5/5 đúng.** Không gói nào có cờ `deprecated`. Các dist-tag khác cho thấy ngữ cảnh:

- `next`: `latest: 16.4.4`, `canary: 16.5.0-canary.37`, `beta: 16.0.0-beta.0` → 16.4.4 là bản stable mới nhất của dòng 16, chưa có 17.
- `react`: `latest: 19.3.1`, không có dist-tag 20.x → React 19 vẫn là dòng hiện hành.
- `deck.gl`: `latest: 9.4.1`, còn giữ `v9.3-latest: 9.3.12` và `v8-latest: 8.9.36` → 9.4 là dòng hiện hành.
- `@xyflow/react`: `latest: 12.12.1`, `next: 13.0.0-next.0` → **dòng 13 đang trong giai đoạn next**. Không phải vấn đề hôm nay, nhưng nếu dự án sống qua Q1/2027 thì sẽ có một đợt nâng major. Ghi nhận ở §6.
- `tailwindcss`: `latest: 4.3.4`, còn giữ `v3-lts: 3.4.19` → v4 là dòng hiện hành.

Nguồn: [npm registry API](https://github.com/npm/registry/blob/main/docs/REGISTRY-API.md), ví dụ [registry.npmjs.org/next](https://registry.npmjs.org/next), [registry.npmjs.org/deck.gl](https://registry.npmjs.org/deck.gl).

### 2.3 PostgreSQL 18.6

✅ **Đúng.**

- endoflife.date: dòng 18 có `latest: 18.6`, `latestReleaseDate: 2026-08-11`, `releaseDate: 2025-09-25`, `eol: 2030-11-14`.
- Docker Hub `library/postgres`: tag `18.6` và `18.6-trixie` cập nhật 2026-10-31, và tag **`latest` trỏ về cùng thời điểm với `18.6`** → 18 là dòng stable hiện hành.
- Docker Hub cũng có tag **`19rc1`** (cập nhật 2026-11-01) → **PostgreSQL 19 mới ở mức Release Candidate**, chưa GA. Chọn 18 cho v1 là đúng, không phải chọn bản cũ.
- Dòng 18 được hỗ trợ đến **2030-11-14**, dài hơn mọi mốc trong kế hoạch 2 tháng của dự án.

Một lưu ý về lịch: PostgreSQL phát hành minor theo quý; đợt kế tiếp dự kiến giữa tháng 11/2026, nên con số "18.6" trong tài liệu sẽ cũ trong khoảng hơn một tuần. Không phải lỗi, nhưng củng cố khuyến nghị §9.3.

Nguồn: [endoflife.date/api/postgresql.json](https://endoflife.date/api/postgresql.json), [hub.docker.com/_/postgres](https://hub.docker.com/_/postgres).

### 2.4 Node.js "22 LTS" — ❌ PHÁT HIỆN CHẶN

**Đây là dòng duy nhất trong bảng Stack chọn sai dòng phiên bản.**

Dữ liệu từ `endoflife.date/api/nodejs.json` và `nodejs.org/dist/index.json`:

| Dòng | Codename | Vào LTS | Hết **Active** support | **EOL** | Bản mới nhất |
|---|---|---|---|---|---|
| **22** | Jod | 2024-10-29 | **2025-10-21** | **2027-04-30** | 22.23.4 (2026-10-20) |
| 24 | Krypton | 2025-10-28 | **2026-10-20** | 2028-04-30 | 24.22.2 (2026-10-27) |
| **26** | Lithium | **2026-10-28** | 2027-10-27 | **2029-04-30** | 26.13.0 (2026-10-28) |

Vấn đề:

1. Node 22 đã **ra khỏi Active LTS từ 2025-10-21**, tức là đã ở Maintenance LTS hơn một năm. Maintenance nghĩa là chỉ còn bản vá lỗi nghiêm trọng và bảo mật, không còn tính năng, không còn backport thường.
2. Node 22 **EOL 2027-04-30**. Dự án khởi động 11/2026, kế hoạch 2 tháng → ra mắt khoảng đầu 01/2027. Nền tảng runtime sẽ **hết hạn hỗ trợ khoảng 4 tháng sau khi ra mắt**. Đó là một đợt nâng cấp bắt buộc rơi đúng vào lúc sản phẩm vừa có người dùng thật.
3. Node 24 cũng đã vừa ra khỏi Active LTS (2026-10-20). **Node 26 "Lithium" mới là Active LTS hiện hành**, vào LTS ngày 2026-10-28 — tức là *6 ngày trước* buổi làm kiến trúc.
4. Next.js 16.4.4 khai báo `engines.node: ">=20.9.0"`, nên cả 22, 24 và 26 đều chạy được. Không có lý do kỹ thuật nào buộc phải ở 22.

**Khuyến nghị:** đổi sang **Node 24 LTS (EOL 2028-04-30)** nếu muốn an toàn với toolchain đã chín, hoặc **Node 26 LTS (EOL 2029-04-30)** nếu muốn vòng đời dài nhất. Không giữ 22.

Nguồn: [endoflife.date/api/nodejs.json](https://endoflife.date/api/nodejs.json), [nodejs.org/dist/index.json](https://nodejs.org/dist/index.json), [nodejs/Release](https://github.com/nodejs/Release), [registry.npmjs.org/next](https://registry.npmjs.org/next) (trường `engines`).

### 2.5 Python 3.13 — ⚠️ cần kiểm tra lại, không sai

Python 3.13 chạy được với toàn bộ stack: Dagster `>=3.10,<3.15`, SQLAlchemy `>=3.11`, SciPy `>=3.12`, NetworkX `!=3.14.1,>=3.12`. Tài liệu cài đặt Dagster còn nói rõ **"Python 3.13 recommended"**.

Nhưng Python 3.14 đã phát hành (10/2025), và `NetworkX 3.7` có pin lạ `!=3.14.1` — cho thấy hệ sinh thái đã bước sang 3.14. Chọn 3.13 là chọn bản *n-1*, hoàn toàn hợp lý cho một dự án 2 tháng (wheel đầy đủ, ít rủi ro build). **Giữ 3.13, nhưng ghi rõ trong tài liệu rằng đây là lựa chọn n-1 có chủ ý**, kẻo sprint sau có người "nâng cho mới" rồi vỡ wheel của SciPy.

Nguồn: [dagster.io/docs/getting-started/installation](https://dagster.io/docs/getting-started/installation).

### 2.6 Caddy 2

✅ Ghi ở mức major (`2`) nên không thể sai. Caddy 2 vẫn là dòng hiện hành. Không có gì để sửa.

---

## 3. Model Claude và Batch API

### 3.1 `claude-haiku-5-5` và `claude-sonnet-5-5` có tồn tại không?

✅ **Cả hai đều tồn tại, đều là model hiện hành của dòng mình, và đều được Batch API hỗ trợ.**

Trang tài liệu Batch processing của Anthropic liệt kê `supportedModels` gồm — nguyên văn — `claude-haiku-5-5` và `claude-sonnet-5-5` (cùng với `claude-opus-5-5`, `claude-sonnet-5`, `claude-opus-5`, `claude-fable-5-1`, v.v.).

Giá công bố:

| Model | Input $/MTok | Output $/MTok | Giá trong Batch (−50%) |
|---|---|---|---|
| Claude Haiku 5.5 (prompt ≤ 100.000 token) | 0,10 | 0,50 | **0,05 / 0,25** |
| Claude Haiku 5.5 (prompt > 100.000 token) | 0,50 | 2,50 | 0,25 / 1,25 |
| Claude Sonnet 5.5 | 2,00 | 10,00 | 1,00 / 5,00 |

### 3.2 Có phải lựa chọn hợp lý cho trích xuất có cấu trúc + Batch API?

✅ **Về nguyên tắc: rất hợp lý.** Phân vai Haiku-cho-lô-hằng-đêm / Sonnet-cho-tương-tác là đúng hình dạng bài toán: JD ngắn, khối lượng lớn, không cần phản hồi tức thì → Haiku 5.5 qua Batch ở 0,05 $/MTok input là mức rẻ nhất có thể đạt. Việc đặt cả hai sau một interface duy nhất (AD-9) khớp với khuyến nghị migration của Anthropic.

❌ **Nhưng có hai cạm bẫy kỹ thuật cụ thể mà spine chưa biết, và cả hai đều đánh thẳng vào chữ "trích xuất có cấu trúc":**

**(a) `tool_choice` cưỡng bức bị từ chối trên Sonnet 5.5.** Cách phổ biến nhất để buộc LLM trả JSON có schema là `tool_choice: {type: "tool", name: "..."}` hoặc `{type: "any"}`. Trên `claude-sonnet-5-5` (và `claude-opus-5-5`, `claude-fable-5-1`), hai dạng này **trả về lỗi 400** — và lỗi này áp dụng *cả trong Batch API và cả trong `count_tokens`*. Cách đúng là:
- `output_config: {format: {...}}` (structured outputs), hoặc
- `tool_choice: {type: "auto"}` + `strict: true` trên tool + chỉ dẫn gọi tên tool trong prompt.

Nếu `haido_core/extract/` được viết theo khuôn cũ (forced tool use), nó sẽ **chạy được với Haiku nhưng 400 với Sonnet** — tức là đường CV/JD dán vào (FR-12, FR-26) vỡ, còn đường hằng đêm thì chạy. Đây là loại lỗi lọt qua test đơn vị nếu test chỉ mock một model.

**(b) Không tắt được thinking trên Sonnet 5.5 — rủi ro cho NFR "trong vòng 15 giây".** Trên `claude-sonnet-5-5`, `thinking: {type: "disabled"}` **trả về 400**. Muốn tắt phải gửi `thinking: {type: "between_tools"}`, và dạng này chỉ được nhận ở `effort` ≤ `high`, không nhận kèm `display`/`budget_tokens`/`block_binding`, và không cho đổi effort giữa hội thoại. Mặc định `effort` của Sonnet 5.5 là `high`. Với FR-12 và FR-26 có ngân sách 15 giây (và Câu hỏi mở số 2 của spine đã lo về 30–50 ms độ trễ mạng), **thinking bật mặc định ở effort `high` là nguồn tốn thời gian lớn hơn nhiều so với vị trí đặt VPS**. Cần đo và hạ `effort` xuống `low`/`medium`, hoặc dùng `between_tools`, trong Sprint 2.

Trên `claude-haiku-5-5`: `disabled` chỉ được nhận ở effort ≤ `high`, mặc định effort là `medium`. Nhẹ hơn nhưng vẫn phải đặt tường minh.

### 3.3 Batch API hiện có giới hạn gì đáng kể?

Lấy nguyên văn từ trang tài liệu chính thức:

| Hạng mục | Giá trị | Nguyên văn |
|---|---|---|
| **Kích thước lô** | 100.000 request **hoặc** 256 MB, cái nào tới trước | "A Message Batch is limited to either 100,000 Message requests or 256 MB in size, whichever is reached first." |
| **Thời gian hoàn thành** | Phần lớn < 1 giờ | "most batches completing within 1 hour" |
| **Cửa sổ xử lý / hết hạn** | **24 giờ — hết hạn thì mất** | "You can access batch results when all messages have completed or after 24 hours, whichever comes first. **Batches expire if processing does not complete within 24 hours.**" |
| **Giảm giá** | **50%** trên mọi loại token | "All usage is charged at 50 percent of the standard API prices." — áp dụng cho input, output và special token |
| **Lưu kết quả** | 29 ngày kể từ `created_at` | "Batch results are available for 29 days after creation." |
| **Tham số KHÔNG dùng được** | `stream: true`, `speed`, `fallbacks`, `max_tokens: 0` | "Including any of these returns a validation error." |
| **Thứ tự kết quả** | Bất kỳ — phải khóa theo `custom_id` | — |
| **Vượt spend limit** | Có thể vượt nhẹ | "batches may go slightly over the spend limit configured in the Claude Console" |
| **Rate limit** | Riêng, không ảnh hưởng Messages API | "Usage of the Batches API does not affect rate limits in the Messages API" |
| **Zero Data Retention** | ❌ **Không đủ điều kiện ZDR** | `zdr.eligibility: not-eligible`, `note: "29-day retention; async storage required."` |

**Bốn hệ quả cụ thể cho Hải Đồ IT:**

1. ⚠️ **Lô hết hạn sau 24 giờ, và pipeline là một daily partition.** Nếu một đêm Anthropic quá tải và lô không xong trong 24 giờ, các request chưa gửi đi sẽ về trạng thái `expired` (không bị tính tiền, nhưng cũng không có kết quả). Lúc đó snapshot đêm đó **không đủ dữ liệu để công bố**. AD-4 nói snapshot chuyển `published` trong đúng một transaction ở cuối lượt chạy — vậy xử lý ra sao khi 3% lượt nhắc `expired`? **Spine chưa có quy tắc nào cho việc này.** Lời hứa "vẫn chạy trên snapshot cũ khi pipeline lỗi" cứu được tình huống *hỏng toàn bộ*, nhưng không cứu được tình huống *thiếu một phần*, vốn là tình huống hay gặp hơn. Cần một quy tắc tường minh: ngưỡng tỷ lệ `expired` tối đa để vẫn công bố, hoặc bắt buộc chạy lại.
2. ⚠️ **Batch không đủ điều kiện ZDR và lưu dữ liệu 29 ngày.** Toàn văn JD rời khỏi VPS và nằm trong lưu trữ async của Anthropic 29 ngày. AD-11 chỉ phủ nội dung *người dùng* (CV/JD dán vào) nên **không bị vi phạm** — đường đó là đường synchronous, không qua Batch. Nhưng §6.2 của PRD đang lo rủi ro pháp lý với toàn văn JD, và AD-14 cấm render `description` ra trang công khai. Việc cùng toàn văn đó được lưu 29 ngày ở bên thứ ba là một mặt của rủi ro ấy mà spine chưa nêu. Nên ghi nhận tường minh (một dòng trong §6.2 hoặc trong AD-9), chứ không phải vì nó sai mà vì nó chưa được quyết.
3. ✅ **Giới hạn 100.000 request / 256 MB không phải vấn đề.** Quy mô 9 nguồn tin tuyển dụng Việt Nam mỗi đêm còn rất xa trần này.
4. 💡 **Nên dùng prompt caching 1 giờ.** Tài liệu khuyên: "Because batches can take longer than 5 minutes to process, consider using the 1-hour cache duration with prompt caching for better cache hit rates when processing batches with shared context." Prompt trích lượt nhắc + bộ từ vựng là phần dùng chung cho mọi JD trong đêm → đây là khoản tiết kiệm miễn phí cộng dồn với −50% của Batch. Chưa thấy trong spine.

Nguồn: [platform.claude.com/docs/en/build-with-claude/batch-processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing), [Rate limits](https://platform.claude.com/docs/en/api/rate-limits#message-batches-api), [Pricing](https://platform.claude.com/docs/en/about-claude/pricing), [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching).

---

## 4. Deprecated / đổi tên / cảnh báo tương thích

### 4.1 SQLAlchemy 2.1 + psycopg 3.3 — ✅ đúng hướng, nhưng có 2 bẫy

Tin tốt: **SQLAlchemy 2.1 đổi driver PostgreSQL mặc định từ psycopg2 sang psycopg (3)**. URL trần `postgresql://` giờ nạp dialect `psycopg` chứ không phải `psycopg2`, và extra `sqlalchemy[postgresql]` kéo theo psycopg 3. Cặp SQLAlchemy 2.1.6 + psycopg 3.3.7 trong spine vì vậy là cặp *được khuyến nghị*, không phải cặp lạ. 2.1 là "Current Release Series", không phải beta.

Hai bẫy cho dự án greenfield này:

1. ⚠️ **`greenlet` không còn được cài mặc định.** Nguyên văn migration guide: asyncio không còn kéo `greenlet`; người dùng asyncio phải cài extra `[asyncio]`. Nếu `haido_api` dùng `AsyncSession` / `create_async_engine` (rất tự nhiên với FastAPI), thì **phải khai `sqlalchemy[asyncio]`**, nếu không sẽ lỗi lúc chạy chứ không phải lúc cài. Dòng "SQLAlchemy 2.1.6" trong bảng Stack không nói gì về extra này.
2. ⚠️ **Autoflush giờ chạy trên *mọi* lần execute, kể cả `text()` thuần.** Trước 2.1 chỉ ORM query mới autoflush. Với AD-5 ("API không được chạy phép tổng hợp") và AD-19 về đột biến trạng thái, việc một câu `text()` chỉ-đọc bất ngờ flush session là loại hành vi gây khó hiểu khi debug. Nên đặt `autoflush=False` tường minh cho session chỉ-đọc của `haido_api`.

Khác đáng ghi nhận trong 2.1: `Select.filter_by()` nay raise `AmbiguousColumnError` khi tên cột tồn tại ở nhiều FROM entity; typing đổi từ `Select[Tuple[int, str]]` sang `Select[int, str]` (cần mypy ≥ 1.7); composite của object pending trả về object có field `None` thay vì `None`; mặc định backslash escape đổi thành `False`; và `Computed.persisted` khi không khai nay theo mặc định **VIRTUAL của PostgreSQL 18**. Điểm cuối cùng đáng để ý vì stack này đúng là PG 18 — nếu có cột tính toán nào trong `stat_*`, hành vi mặc định đã khác so với PG 17.

Nguồn: [What's New in SQLAlchemy 2.1](https://docs.sqlalchemy.org/en/21/changelog/migration_21.html), [PostgreSQL dialect](https://docs.sqlalchemy.org/en/21/dialects/postgresql.html).

### 4.2 Pydantic 2.14 + FastAPI 0.162 — ✅ không có vấn đề

Kiểm trực tiếp metadata PyPI:

- FastAPI 0.162.0 khai `pydantic>=2.9.0` — **không có chặn trên**. Pydantic 2.14.2 thỏa.
- FastAPI 0.162.0 khai `starlette>=0.46.0` — không chặn trên.
- Pydantic 2.14.2 khai `pydantic-core==2.50.2` (pin cứng, bình thường) và `typing-extensions>=4.16.0`.

Không có xung đột. Không có cảnh báo deprecation nào liên quan cặp này.

### 4.3 Next.js 16 + React 19 — ✅ không có vấn đề

`next@16.4.4` khai `peerDependencies.react: "^18.2.0 || 19.0.0-rc-... || ^19.0.0"` và `react-dom` tương tự. React 19.3.1 thỏa `^19.0.0`. `react-dom@19.3.1` khai `peerDependencies.react: "^19.3.1"` — khớp chính xác.

Các gói frontend khác cũng khớp:
- `deck.gl@9.4.1`: peer `react: ">=16.3.0"`, `react-dom: ">=16.3.0"` → OK.
- `@xyflow/react@12.12.1`: peer `react: ">=17"`, `react-dom: ">=17"`, `@types/react: ">=17"` → OK.
- `tailwindcss@4.3.4`: không có peerDependencies → OK.

### 4.4 Xung đột phụ thuộc trong cùng một môi trường Python — ✅ giải được sạch

Đây là rủi ro lớn nhất mà bảng Stack *không* nhìn thấy, vì AD-15 đặt Dagster và `haido_core` (SQLAlchemy + Pydantic) **trong cùng một môi trường**. Kiểm metadata:

| Gói | Pin liên quan | Phiên bản trong spine | Kết luận |
|---|---|---|---|
| `dagster 1.13.28` | `sqlalchemy<3,>=1.0` | SQLAlchemy 2.1.6 | ✅ |
| `dagster 1.13.28` | `alembic!=1.11.0,!=1.6.3,!=1.7.0,>=1.2.1` | Alembic 1.20.1 | ✅ |
| `dagster-shared 1.13.28` | `pydantic<3.0.0,>=2` | Pydantic 2.14.2 | ✅ |
| `dagster-shared 1.13.28` | `typing-extensions<5,>=4.11.0` | — | ✅ (Pydantic đòi `>=4.16.0`, nằm trong khoảng) |
| `alembic 1.20.1` | `SQLAlchemy>=2.0` | SQLAlchemy 2.1.6 | ✅ |
| `fastapi 0.162.0` | `pydantic>=2.9.0` | Pydantic 2.14.2 | ✅ |

**Không có xung đột.** Dagster không ghim SQLAlchemy hay Pydantic xuống dòng cũ — đây là rủi ro đã từng tồn tại ở các thế hệ Dagster trước và nay không còn. Kết luận này đáng ghi vào spine vì nó là điều kiện sống của AD-15.

Nguồn: `requires_dist` từ [pypi.org/pypi/dagster/json](https://pypi.org/pypi/dagster/json), [pypi.org/pypi/dagster-shared/json](https://pypi.org/pypi/dagster-shared/json), [pypi.org/pypi/alembic/json](https://pypi.org/pypi/alembic/json), [pypi.org/pypi/fastapi/json](https://pypi.org/pypi/fastapi/json).

### 4.5 Lý do loại Airflow — ✅ khẳng định đúng nguyên văn

Spine viết: *"Airflow (tài liệu khuyến nghị sàn 4 GB RAM chỉ cho riêng nó...)"*.

Tài liệu Airflow chính thức, phần Docker Compose, nói nguyên văn: Docker phải được cấu hình dùng **"at least 4.00 GB of memory for the Airflow containers to run properly"**, và một tip bổ sung: **"You should allocate at least 4GB memory for the Docker Engine (ideally 8GB)."**

✅ Khẳng định của spine đúng, có nguồn, và lý do loại Airflow đứng vững. Đây là một trong những quyết định được biện minh tốt nhất trong tài liệu.

Nguồn: [airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html).

### 4.6 Thiếu trong bảng Stack — basemap cho deck.gl

⚠️ `deck.gl@9.4.1` khai `peerDependencies` gồm `maplibre-gl: "^4.5.1 || ^5.0.0 || ^6.0.0"`. Tính năng 4.5 "Bản đồ nhu cầu" (FR-33..FR-36) được xếp vào `web/` với deck.gl, nhưng bảng Stack **không có dòng nào cho basemap, cho nguồn tile, hay cho GeoJSON ranh giới tỉnh/thành Việt Nam**. Ba thứ này không miễn phí về mặt quyết định:
- basemap raster/vector cần một nhà cung cấp tile (có hạn mức, có điều khoản sử dụng, có thể phát sinh chi phí — liên quan trần chi phí §6.4);
- GeoJSON ranh giới hành chính Việt Nam cần một nguồn và một giấy phép;
- deck.gl không SSR được, nên trong Next.js App Router phải nạp động client-only — nếu không `next build` sẽ vỡ.

Không phải lỗi phiên bản, nhưng là một lỗ trong bảng Stack đủ lớn để làm lệch ước lượng một story.

---

## 5. Các khẳng định về Dagster

### 5.1 "Dagster có daily partition" — ✅ ĐÚNG

Tài liệu Dagster (bản "Latest (1.13.28)" — trùng khớp phiên bản trong spine) có mục "Time-based partitions" với ví dụ nguyên văn:

```python
daily_partitions = dg.DailyPartitionsDefinition(start_date="2024-01-01")
```

`DailyPartitionsDefinition` là API hiện hành, không deprecated, không đổi tên. AD-15 ("Một snapshot = một daily partition") và Consistency Convention (`snapshot_id` dạng `YYYY-MM-DD`) đều khả thi trực tiếp.

Một lưu ý cho AD-15: `snapshot_id` được định nghĩa theo `Asia/Ho_Chi_Minh`. `DailyPartitionsDefinition` nhận tham số timezone, và nếu để mặc định (UTC) thì nhãn partition sẽ lệch 7 giờ so với `snapshot_id` — nghĩa là partition `2026-11-03` của Dagster và snapshot `2026-11-03` của Hải Đồ có thể là hai ngày khác nhau. Phải đặt timezone tường minh. Chưa thấy trong spine.

Nguồn: [dagster.io/docs/guides/build/partitions-and-backfills/partitioning-assets](https://dagster.io/docs/guides/build/partitions-and-backfills/partitioning-assets).

### 5.2 "Dagster chạy được trên Windows cho dev" — ✅ ĐÚNG, có bằng chứng cứng

Ba chứng cứ độc lập:

1. **Metadata package:** `dagster 1.13.28` khai hai phụ thuộc có điều kiện riêng cho Windows — `psutil>=1.0; platform_system == "Windows"` và `pywin32!=226; platform_system == "Windows"`. Một project không hỗ trợ Windows sẽ không ship dependency Windows-conditional.
2. **Tài liệu triển khai:** trang "Deploying Dagster as a service" có tab riêng **"Windows (PowerShell)"** bên cạnh "Linux/macOS (Bash)" cho việc đặt `DAGSTER_HOME`.
3. **Tài liệu cài đặt:** chỉ yêu cầu "Python 3.10 or higher" (khuyến nghị 3.13), **không nêu hạn chế hệ điều hành nào**, và phần kiểm tra cài đặt có tab Windows với lệnh Windows.

Lưu ý: tài liệu *contributing* của Dagster (dành cho người phát triển chính Dagster, không phải người dùng) có nói nếu dùng Windows thì cần WSL. Điều đó không áp dụng cho việc *dùng* Dagster.

⚠️ **Nhưng spine viết câu này mơ hồ và cần làm rõ.** Nguyên văn: *"local (Docker Compose trên Windows, Postgres trong container, Dagster chạy bằng `dagster dev`)"*. Hai cách đọc rất khác nhau:
- (a) `dagster dev` chạy **trên host Windows**, Postgres trong container → Dagster thật sự chạy native Windows. Được, nhưng đây là đường đi ít người đi nhất, nơi gặp các khác biệt về spawn process và đường dẫn file.
- (b) `dagster dev` chạy **trong container Linux** dưới Docker Desktop → câu hỏi "Dagster trên Windows" trở thành vô nghĩa, và đây là đường an toàn.

Với lệnh "local và prod dùng **cùng một** `docker-compose.yml`, khác `.env`", cách đọc (b) mới nhất quán. Nhưng `dagster dev` *không phù hợp cho prod* — tài liệu Dagster nói rõ nó "is not suitable for the demands of most production deployments". Vậy local và prod **không** thể dùng cùng một định nghĩa service cho Dagster. Đây là một mâu thuẫn nội tại trong phần "Triển khai và môi trường", không phải lỗi công nghệ.

Nguồn: [pypi.org/pypi/dagster/json](https://pypi.org/pypi/dagster/json), [Deploying Dagster as a service](https://dagster.io/docs/deployment/oss/deployment-options/deploying-dagster-as-a-service), [Installation](https://dagster.io/docs/getting-started/installation), [Dagster daemon](https://dagster.io/docs/deployment/execution/dagster-daemon).

### 5.3 "Mức RAM thực tế của dagster daemon + UI" — ❌ PHÁT HIỆN CHẶN: spine đếm thiếu service

**Dagster OSS không phải hai process. Tài liệu kiến trúc triển khai của Dagster nói nguyên văn: "Dagster requires three long-running services".**

| Service thường trú | Vai trò | Có trong sơ đồ spine? |
|---|---|---|
| `dagster-webserver` | UI + GraphQL | ✅ (gộp trong `dag`) |
| `dagster-daemon` | schedule, sensor, run queue. **Không hỗ trợ nhiều replica** | ✅ (gộp trong `dag`) |
| **Code location server (gRPC)** | nạp và phục vụ metadata định nghĩa; **cả webserver và daemon đều kết nối tới nó** | ❌ **THIẾU** |
| **Run worker** (mỗi lượt chạy một cái) | không thường trú; run launcher sinh một process/container **cho mỗi lượt chạy** | ❌ **THIẾU** |

Ví dụ Docker Compose *chính thức* của Dagster định nghĩa **bốn service**: `postgresql`, `user_code` (gRPC), `webserver`, `daemon` — và trang đó nói thêm một triển khai Dagster trên Docker "typically executes each run in its own container", với `DAGSTER_CURRENT_IMAGE` được đặt để run launcher dùng lại cùng image, và webserver/daemon đều mount Docker socket.

Nghĩa là sơ đồ `vps` trong spine — với một hộp `dag["dagster: daemon + UI"]` — **thiếu ít nhất một process thường trú và toàn bộ process thực thi**. Và process thực thi chính là nơi `haido_core/steps/` chạy, tức là nơi SciPy bootstrap B = 1.000 (Câu hỏi mở số 3) tiêu RAM. Đây không phải chi tiết vận hành vụn: nó làm ngân sách RAM ở §6 sai một bậc.

**Về con số RAM:** không có con số chính thức nào.
- Dagster **không công bố** yêu cầu RAM tối thiểu/khuyến nghị cho OSS. Trang "Deploying Dagster as a service" không nêu con số RAM hay CPU nào; trang Installation cũng không.
- Giá trị tham chiếu từ Helm chart cộng đồng thường thấy: ~512 Mi cho webserver, ~256 Mi cho daemon (đây là *giá trị mẫu*, không phải sàn chính thức).
- Số đo thực tế công khai thì cao hơn nhiều: trong một PR công khai, daemon idle khoảng **0,95 GB khi có 2 code server**, một gRPC code server độc lập khoảng **422 MB**, và một lượt chạy in-process thêm khoảng **0,8 GB** (một step đạt đỉnh 764 MB). Đó là trên máy 7,7 GB. Đây là một mẫu đơn lẻ, phải coi là anecdote — nhưng là anecdote *đo được*, và nó đi cùng chiều với issue công khai về daemon tăng RAM theo số asset (tới 20 GB với ~1000 asset) và các báo cáo rò rỉ bộ nhớ ở webserver chạy dài.

Kết luận: **không thể nói "mức RAM thực tế của dagster daemon + UI" là một con số, vì (a) Dagster không công bố nó, và (b) câu hỏi sai đối tượng — phải hỏi daemon + UI + code server + run worker.** Phải đo trong Sprint 1, không được giả định.

Nguồn: [Dagster OSS deployment architecture](https://dagster.io/docs/deployment/oss/oss-deployment-architecture), [Deploying Dagster using Docker Compose](https://dagster.io/docs/deployment/oss/deployment-options/docker), [examples/deploy_docker/docker-compose.yml](https://github.com/dagster-io/dagster/blob/master/examples/deploy_docker/docker-compose.yml), [issue #26287 — daemon consumes too much memory](https://github.com/dagster-io/dagster/issues/26287), [issue #21307 — possible memory leak in long-running webserver/daemon](https://github.com/dagster-io/dagster/issues/21307).

---

## 6. Khẳng định về ISR của Next.js

Spine (AD-13 và Capability Map) dựa vào ba khẳng định. Kiểm trên trang tài liệu Next.js hiện hành (`lastUpdated: 2026-10-15`, tức là cho dòng 16.4):

### 6.1 "ISR chỉ chạy trên Node runtime" — ✅ ĐÚNG, nguyên văn

> "ISR is only supported when using the Node.js runtime (default)."

### 6.2 "ISR không hoạt động với `output: export`" — ✅ ĐÚNG, nguyên văn

> "ISR is not supported when creating a [Static Export]."

Và bảng Platform Support xác nhận: Node.js server **Yes**, Docker container **Yes**, Static export **No**.

Hai khẳng định này đứng vững và biện minh cho dòng `web["web: Next.js 16 trên Node"]` trong sơ đồ triển khai.

### 6.3 "`revalidatePath` gọi được từ Route Handler" — ✅ đúng, nhưng ❌ **hệ quả mà AD-13 trông cậy vào thì SAI**

Gọi được: tài liệu nói `revalidateTag`/`revalidatePath` dùng được "in a Server Actions **or Route Handler**". Về mặt cơ học, AD-13 khả thi.

**Nhưng AD-13 phát biểu điều này như một cơ chế *sinh lại trang*, và nó không phải vậy.** Nguyên văn tài liệu:

> "`revalidatePath` invalidates the cache entries but **regeneration happens on the next request**. If you want to eagerly regenerate the cache entry immediately instead of waiting for the next request, you can use the Pages router `res.revalidate` method. **We're working on adding new methods to provide eager regeneration capabilities for the App Router.**"

Hệ quả cụ thể cho Hải Đồ IT:

1. **AD-13 phát biểu sai cơ chế.** Spine viết: *"sau khi một snapshot chuyển `published`, bước cuối của pipeline **gọi route làm mới** của `web/`"* và *"Trang nội dung không bao giờ render động theo request"*. Thực tế: lệnh gọi đó chỉ *đánh dấu hết hạn*. Trang được render lại **khi có request đầu tiên tới** — và request đó render đồng bộ, đọc Postgres. Tức là người đọc (hoặc con bot của Google) đầu tiên sau mỗi đêm **chính là người trả giá cho việc render**. Với mục tiêu SEO/GEO, đó đúng là đối tượng không nên phải chờ.
2. **Lỗ nhất quán mà AD-13 định bịt vẫn hở.** AD-13 nói mục đích là ngăn "trang SEO hiển thị số của đêm nay trong khi API trả số của đêm qua". Nhưng vì sinh lại là lazy, trong khoảng từ lúc publish đến lúc có request đầu tiên tới một trang cụ thể, **trang đó vẫn phục vụ nội dung của đêm trước** trong khi API đã trả số đêm nay. Khoảng lệch không bị xoá, chỉ bị thu ngắn. Nếu muốn bịt thật, phải tự "mồi" (warm) từng URL bằng một lượt `GET` ngay sau khi gọi revalidate — và đây là việc phải thêm vào bước cuối của pipeline, không miễn phí khi danh sách trang SEO mở rộng (xem bảng Deferred).
3. ⚠️ **API `revalidateTag` đã đổi trong Next 16.** Ví dụ hiện hành trong tài liệu là `revalidateTag('posts', 'max')` — **hai tham số**. Nếu code được viết theo khuôn Next 14/15 (`revalidateTag('posts')`) thì đã lệch so với tài liệu hiện hành.
4. ⚠️ **Next 16 có hai chế độ ISR và spine chưa chọn.** Trang này mở đầu bằng: *"This guide covers ISR **without** Cache Components. If you are using `cacheComponents`, see ISR with Cache Components instead."* Next.js 16 giới thiệu Cache Components (`use cache`) với mô hình caching khác hẳn. Đây là một quyết định kiến trúc thật, phải chốt trước khi viết `web/`, chứ không nên để mỗi story tự chọn. Spine nói "Next.js 16: app tương tác (client) + trang nội dung công khai (ISR)" mà không nói ISR nào.
5. ⚠️ **"Proxy won't be executed for on-demand ISR requests"** — tài liệu nói rõ mọi rewrite/logic trong Proxy sẽ không áp dụng cho request ISR on-demand, nên "ensure you are revalidating the exact path". Với Caddy làm reverse proxy phía trước, đường dẫn truyền cho `revalidatePath` phải là đường dẫn *Next.js nhìn thấy*, không phải đường dẫn công khai. Đây là loại lỗi chỉ hiện ra trên prod.
6. ✅ Hai caveat về multi-instance ("default file-system cache is per-instance", "on-demand revalidation only invalidates the instance that receives the call") **không áp dụng**, vì spine chạy một instance (và bảng Deferred đã hoãn multi-instance có chủ ý). Tốt — đây là một chỗ mà quyết định hoãn của spine đúng.

Có thể quan sát hành vi cache qua header `x-nextjs-cache` (`HIT`/`STALE`/`MISS`/`REVALIDATED`) — nên đưa vào tiêu chí nghiệm thu của story trang công khai.

Nguồn: [nextjs.org/docs/app/guides/incremental-static-regeneration](https://nextjs.org/docs/app/guides/incremental-static-regeneration), [ISR with Cache Components](https://nextjs.org/docs/app/guides/incremental-static-regeneration-cache-components), [revalidatePath](https://nextjs.org/docs/app/api-reference/functions/revalidatePath), [Self-hosting: caching and ISR](https://nextjs.org/docs/app/guides/self-hosting).

---

## 7. Bốn service có vừa một VPS 4 GB không?

### 7.1 Sửa lại phép đếm trước khi cộng

Spine nói "bốn service": postgres, FastAPI, Dagster (daemon+UI), Next.js. Thực tế trên `docker-compose.yml` sẽ là:

1. `caddy` — reverse proxy (spine đã có trong sơ đồ nhưng không tính vào "4 service")
2. `postgres` 18
3. `api` — FastAPI + Uvicorn
4. `web` — Next.js trên Node
5. `dagster-webserver`
6. `dagster-daemon`
7. **`dagster-code-location` (gRPC)** — bắt buộc theo kiến trúc Dagster OSS
8. **run worker** — sinh ra theo mỗi lượt chạy, là nơi SciPy/NetworkX/bootstrap thực thi

Tức là **7 container thường trú + 1 process bùng lên hằng đêm**, không phải 4.

### 7.2 Ước lượng RAM có dẫn nguồn

| Thành phần | Ước lượng | Cơ sở |
|---|---|---|
| OS + Docker Engine | 300–400 MB | nền của mọi VPS Linux chạy Docker |
| `caddy` | 20–50 MB | Caddy là binary Go tĩnh, footprint nhỏ |
| `postgres 18` — tuned cho máy nhỏ | **300–500 MB** | `shared_buffers` mặc định **128 MB** (PG docs); `work_mem` mặc định **4 MB** nhưng "total memory used could be many times the value of `work_mem`" vì một query có thể chạy nhiều sort/hash và nhiều session song song; `maintenance_work_mem` mặc định **64 MB**, và "up to `autovacuum_max_workers` times this memory may be allocated" |
| `api` — FastAPI + Uvicorn + SQLAlchemy + import SciPy/NetworkX | 250–400 MB mỗi worker | không có con số chính thức; SciPy nạp BLAS/LAPACK nên chỉ riêng `import scipy` đã là hàng trăm MB. Nếu chạy >1 Uvicorn worker thì nhân lên |
| `web` — Next.js 16 prod server | 200–400 MB lúc idle, **tăng dần** | Next.js docs: "When the Next.js server starts, it preloads each page's JavaScript modules into memory... in exchange for a larger initial memory footprint", và quan trọng hơn: "**Next.js doesn't unload these JavaScript modules**, meaning that even with this optimization disabled, the memory footprint of your Next.js server will eventually be the same if all pages are eventually requested" |
| `dagster-webserver` | 400–600 MB | không có con số chính thức; giá trị mẫu Helm ~512 Mi; có issue công khai về RAM tăng dần ở webserver chạy dài |
| `dagster-daemon` | 250 MB – **0,95 GB** | giá trị mẫu Helm ~256 Mi; số đo công khai: ~0,95 GB khi có 2 code server |
| `dagster-code-location` (gRPC) | ~420 MB | số đo công khai: một gRPC server độc lập ~422 MB |
| **run worker hằng đêm** (SciPy bootstrap B=1.000) | **0,7 – 2 GB+ đỉnh** | số đo công khai: một lượt chạy in-process ~0,8 GB, một step đạt đỉnh 764 MB. Với bootstrap B=1.000 trên "số ô thống kê thật" (Câu hỏi mở số 3 của spine — chính spine cũng chưa biết) con số này là **chưa đo** |

**Tổng:**

- **Steady state (không chạy pipeline):** ≈ 1,7 – 2,8 GB
- **Lúc pipeline hằng đêm chạy:** ≈ **2,4 – 4,8 GB**

### 7.3 Kết luận

❌ **Khẳng định "vừa một VPS 4 GB" không đứng được như đã viết.**

- Ở trạng thái nghỉ thì vừa, còn dư.
- Ở **đúng khoảnh khắc pipeline chạy** — khoảnh khắc duy nhất mà cả hệ thống phải làm việc thật — biên trên của ước lượng **vượt 4 GB**. Và đó là khoảnh khắc không thể tránh: AD-4 bắt mọi bảng tổng hợp phải ghi xong trước khi snapshot chuyển `published` trong một transaction.
- Hậu quả của việc vượt là OOM killer của Linux giết một process. Nếu nó giết run worker, snapshot đêm đó không công bố được. Nếu nó giết `postgres`, mất cả hai.
- Một chi tiết trớ trêu: spine loại Airflow vì *"tài liệu khuyến nghị sàn 4 GB RAM chỉ cho riêng nó"*. Sàn 4 GB của Airflow là cho **4 container** (webserver, scheduler, worker, postgres). Dagster OSS, theo tài liệu chính thức của chính nó, cũng cần **4 container** (webserver, daemon, code location, postgres) cộng run container. Lý do loại Airflow vẫn đúng về số tuyệt đối (Dagster nhẹ hơn), nhưng **lập luận "Dagster nhẹ nên vừa 4 GB" chưa được chứng minh ở đâu cả** — Dagster không công bố con số nào.

**Một vấn đề thứ hai, riêng biệt: `next build`.** Spine nói prod triển khai bằng `docker compose up -d` sau khi test xanh (bảng Deferred: "CI/CD nhiều tầng, blue-green" — hoãn). Nếu image `web` được **build trên VPS**, thì `next build` sẽ chạy cùng lúc với 7 container đang sống. Next.js có cả một trang tài liệu riêng về tối ưu RAM lúc build, với các biện pháp giảm nhẹ: `experimental.webpackMemoryOptimizations: true`, webpack build worker, tắt webpack cache, `typescript.ignoreBuildErrors` (docs cảnh báo "!! WARN !!"), `productionBrowserSourceMaps: false` + `experimental.serverSourceMaps: false` + `enablePrerenderSourceMaps: false`, và cờ `--experimental-debug-memory-usage`. Sự tồn tại của trang đó là bằng chứng rằng OOM lúc build là chuyện thường. Thêm nữa, giai đoạn "Generating static pages" của `next build` chính là lúc các trang ISR được prerender — và với AD-14, các trang đó **đọc Postgres**, nên build không phải là tác vụ thuần CPU.

### 7.4 Phải làm gì

Có bốn đường, không loại trừ nhau:

1. **Nâng VPS lên 8 GB.** Đơn giản nhất, và có lẽ rẻ hơn thời gian đi tối ưu. Spine viết "1 VPS từ 4 GB" trong sơ đồ — chữ "từ" cho thấy 4 GB được hiểu là *sàn*, nhưng dòng tiêu đề §7 của bảng Deferred và Câu hỏi mở số 2 lại coi 4 GB như *cấu hình thật*. Cần chốt.
2. **Build image ngoài VPS** (máy dev hoặc CI), chỉ `docker compose pull && up -d` trên prod. Việc này gỡ bỏ đỉnh RAM lớn nhất và không cần CI/CD nhiều tầng — vẫn nằm trong tinh thần "3 người, 1 VPS".
3. **Không chạy `dagster-webserver` thường trú trên prod.** UI Dagster là công cụ vận hành, không phải service người dùng. Bật khi cần, tắt khi không. Tiết kiệm 400–600 MB và loại bỏ nguy cơ rò rỉ bộ nhớ ở process chạy dài. (Tài liệu Dagster nói một triển khai không có daemon là khả thi — nhưng ở đây cần giữ daemon và bỏ webserver, chứ không phải ngược lại, vì daemon là thứ chạy schedule.)
4. **Cấu hình swap và đặt `mem_limit` cho từng service trong `docker-compose.yml`.** Swap biến OOM-kill thành chậm. `mem_limit` khiến container ăn RAM nhất bị giết trước, thay vì để OOM killer chọn ngẫu nhiên — tuyệt đối không được để nó chọn `postgres`.

Và **đo trong Sprint 1, không giả định**: `docker stats` ở trạng thái nghỉ, và ở đỉnh một lượt chạy pipeline đầy đủ với dữ liệu thật. Câu hỏi mở số 3 của spine đã đặt đúng việc đo bootstrap; cần mở rộng nó thành "đo RAM đỉnh của cả VPS".

Nguồn: [PostgreSQL 18 — Resource Consumption](https://www.postgresql.org/docs/18/runtime-config-resource.html), [Next.js — How to optimize memory usage](https://nextjs.org/docs/app/guides/memory-usage), [Dagster OSS deployment architecture](https://dagster.io/docs/deployment/oss/oss-deployment-architecture), [Dagster Docker Compose deployment](https://dagster.io/docs/deployment/oss/deployment-options/docker), [Airflow Docker Compose requirements](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html).

---

## 8. Tổng hợp phát hiện theo mức độ

### Chặn — sửa trước khi chia epic

| # | Phát hiện | Ở đâu | Phải làm gì |
|---|---|---|---|
| B1 | **Ngân sách 4 GB RAM không đứng được lúc pipeline chạy** (ước lượng đỉnh 2,4–4,8 GB) | §Triển khai, sơ đồ `vps` | Chốt cỡ VPS (khuyến nghị 8 GB), build image ngoài VPS, đặt `mem_limit`, cấu hình swap, đo trong Sprint 1 |
| B2 | **Dagster OSS cần 3 service thường trú + 1 process mỗi lượt chạy**, spine chỉ vẽ "daemon + UI" | Sơ đồ `vps`, AD-15 | Thêm `dagster-code-location` vào sơ đồ và vào `docker-compose.yml`; nêu rõ run worker là nơi `haido_core/steps/` thực thi |
| B3 | **AD-13 phát biểu sai cơ chế `revalidatePath`** — nó chỉ đánh dấu hết hạn, sinh lại xảy ra ở request kế tiếp; App Router chưa có eager regeneration | AD-13 | Sửa Rule của AD-13; thêm bước "mồi" từng URL bằng `GET` sau revalidate nếu muốn giữ lời hứa nhất quán |

### Nặng — sửa trong Sprint 1

| # | Phát hiện | Phải làm gì |
|---|---|---|
| N1 | **Node 22 LTS đã ở Maintenance LTS, EOL 2027-04-30** — khoảng 4 tháng sau ngày ra mắt dự kiến | Đổi sang Node 24 LTS (EOL 2028-04) hoặc Node 26 LTS (EOL 2029-04) |
| N2 | **`tool_choice` cưỡng bức trả 400 trên `claude-sonnet-5-5`** (kể cả trong Batch và `count_tokens`) — đúng cách viết "trích xuất có cấu trúc" hay dùng | Viết `haido_core/extract/` bằng `output_config.format` hoặc `tool_choice: auto` + `strict: true`; test hợp đồng phải chạy với **cả hai** model, không mock |
| N3 | **Không tắt được thinking trên `claude-sonnet-5-5` (`disabled` → 400), mặc định `effort: high`** — rủi ro trực tiếp cho NFR 15 giây của FR-12/FR-26 | Đo độ trễ thật ở Sprint 2; hạ `effort`, hoặc dùng `thinking: {type: "between_tools"}` ở `effort` ≤ `high` |
| N4 | **Lô Batch hết hạn sau 24 giờ** → snapshot có thể thiếu một phần dữ liệu; AD-4 không có quy tắc cho trường hợp thiếu *một phần* | Thêm vào AD-4 ngưỡng tỷ lệ `expired` tối đa để vẫn công bố, và hành vi khi vượt ngưỡng |

### Vừa — ghi nhận

| # | Phát hiện |
|---|---|
| V1 | **Mâu thuẫn local/prod:** spine nói hai môi trường dùng *cùng một* `docker-compose.yml`, nhưng `dagster dev` được tài liệu Dagster nói rõ là "not suitable for... production deployments". Hai môi trường không thể dùng cùng định nghĩa service cho Dagster. |
| V2 | **`DailyPartitionsDefinition` cần timezone tường minh** — nếu để mặc định UTC, partition Dagster lệch 7 giờ so với `snapshot_id` theo `Asia/Ho_Chi_Minh`. |
| V3 | **Next 16 có hai mô hình ISR** (có/không `cacheComponents`) và spine chưa chọn. `revalidateTag` hiện có 2 tham số (`revalidateTag('posts', 'max')`). "Proxy won't be executed for on-demand ISR requests" → đường dẫn truyền cho `revalidatePath` phải là đường Next.js thấy, không phải đường công khai qua Caddy. |
| V4 | **SQLAlchemy 2.1: `greenlet` không còn cài mặc định** (cần extra `[asyncio]` nếu `haido_api` dùng async session) và **autoflush nay chạy trên mọi `execute`, kể cả `text()`** (nên đặt `autoflush=False` cho session chỉ-đọc). |
| V5 | **Bảng Stack thiếu basemap/tile provider và GeoJSON ranh giới tỉnh Việt Nam** cho FR-33..FR-36; `deck.gl` khai peer `maplibre-gl ^4.5.1 \|\| ^5 \|\| ^6`. deck.gl không SSR được → phải nạp client-only trong App Router. Có hệ quả về chi phí (§6.4) và giấy phép dữ liệu. |
| V6 | **Batch API không đủ điều kiện ZDR, lưu dữ liệu 29 ngày.** Không vi phạm AD-11 (chỉ phủ nội dung người dùng), nhưng là một mặt của rủi ro §6.2 chưa được nêu tường minh. |
| V7 | **Chưa dùng prompt caching 1 giờ cho lô hằng đêm** — tài liệu Anthropic khuyên đúng cho trường hợp này; tiết kiệm cộng dồn với −50% của Batch. |
| V8 | **`@xyflow/react` đã có `next: 13.0.0-next.0`** — một đợt nâng major đang tới. Không phải vấn đề hôm nay. |
| V9 | **Python 3.13 là lựa chọn n-1 có chủ ý** (3.14 đã ra) — nên ghi rõ lý do để sprint sau không "nâng cho mới" rồi vỡ wheel SciPy. |

### Xác nhận đúng — không phải sửa

- 11/11 phiên bản Python đúng là bản hiện hành trên PyPI (Dagster 1.13.28, FastAPI 0.162.0, SQLAlchemy 2.1.6, Alembic 1.20.1, Pydantic 2.14.2, Uvicorn 0.54.0, psycopg 3.3.7, NetworkX 3.7, SciPy 1.18.1, anthropic 2.4.0, + Python 3.13 hợp lệ với mọi `requires_python`).
- 5/5 phiên bản npm đúng là `dist-tags.latest` (Next 16.4.4, React 19.3.1, deck.gl 9.4.1, @xyflow/react 12.12.1, Tailwind 4.3.4). Không gói nào `deprecated`.
- PostgreSQL 18.6 là bản stable hiện hành; PG 19 mới ở `19rc1`; dòng 18 được hỗ trợ đến 2030-11-14.
- Không có xung đột phụ thuộc nào trong môi trường Python dùng chung: Dagster `sqlalchemy<3,>=1.0`, `dagster-shared` `pydantic<3.0.0,>=2`, FastAPI `pydantic>=2.9.0` không chặn trên, Alembic `SQLAlchemy>=2.0`.
- Next.js 16 + React 19 tương thích theo `peerDependencies` chính thức; deck.gl và @xyflow/react đều nhận React 19.
- `claude-haiku-5-5` và `claude-sonnet-5-5` đều tồn tại, đều trong danh sách `supportedModels` của Batch API, phân vai đúng hình dạng bài toán.
- Batch API: −50% mọi loại token, 100.000 request / 256 MB, phần lớn < 1 giờ, kết quả giữ 29 ngày, rate limit riêng.
- Dagster có `DailyPartitionsDefinition` — AD-15 khả thi.
- Dagster hỗ trợ Windows (ship `pywin32`/`psutil` conditional, có tab PowerShell trong docs, không nêu hạn chế OS).
- "ISR chỉ chạy trên Node runtime" — đúng nguyên văn.
- "ISR không hoạt động với `output: export`" — đúng nguyên văn; bảng Platform Support xác nhận.
- `revalidatePath`/`revalidateTag` gọi được từ Route Handler — đúng.
- Lý do loại Airflow ("sàn 4 GB RAM") — đúng nguyên văn tài liệu Airflow.
- Quyết định hoãn multi-instance khiến hai caveat về cache per-instance của ISR không áp dụng — đúng.
- SQLAlchemy 2.1 + psycopg 3 là cặp *được khuyến nghị* (2.1 đổi driver mặc định sang psycopg 3), không phải cặp lạ. 2.1.6 là "Current Release Series", không phải beta.

---

## 9. Khuyến nghị về cách viết bảng Stack

**9.1 — Tách "phiên bản" khỏi "dòng phiên bản".** Phần lớn giá trị của bảng Stack nằm ở việc chốt *dòng* (Next 16, React 19, PG 18, Node 24), không phải chốt *patch* (16.4.4, 19.3.1, 18.6). Patch sẽ cũ trong vài ngày — `psycopg` đã ra bản mới ngay trong ngày rà soát này. Đề xuất: ghi dòng phiên bản trong spine, để patch cho lockfile (`uv.lock` / `package-lock.json`), vốn là nơi duy nhất nói sự thật.

**9.2 — Ghi rõ EOL cho các thứ có vòng đời.** Node và PostgreSQL là hai thứ duy nhất trong stack có ngày hết hạn công khai. Thêm một cột `EOL` sẽ bắt được lỗi N1 ngay lúc viết bảng, không cần đến người rà soát.

**9.3 — Thêm cột "đã kiểm ở đâu".** Câu "Kiểm ngày 03/11/2026 trên PyPI, npm và postgresql.org" là đúng và đáng tin — nhưng nó là một khẳng định không kiểm lại được ở mức từng dòng. Nếu mỗi dòng có nguồn riêng, lần rà sau mất vài phút thay vì một buổi.

**9.4 — Bảng Stack nên bao gồm cả thứ *không* phải thư viện.** Ba thiếu sót có hậu quả thật đều thuộc loại này: service thứ ba của Dagster, basemap/tile provider, và nguồn GeoJSON ranh giới hành chính. Không gói npm nào đại diện cho chúng, nên chúng lọt khỏi bảng.

---

## 10. Nguồn

**Registry và vòng đời**
- [PyPI JSON API](https://warehouse.pypa.io/api-reference/json.html) — `pypi.org/pypi/{dagster,fastapi,sqlalchemy,alembic,pydantic,uvicorn,psycopg,networkx,scipy,anthropic,dagster-shared}/json`
- [npm registry API](https://github.com/npm/registry/blob/main/docs/REGISTRY-API.md) — `registry.npmjs.org/{next,react,react-dom,deck.gl,@xyflow/react,tailwindcss}`
- [endoflife.date/api/nodejs.json](https://endoflife.date/api/nodejs.json) · [endoflife.date/api/postgresql.json](https://endoflife.date/api/postgresql.json)
- [nodejs.org/dist/index.json](https://nodejs.org/dist/index.json) · [nodejs/Release](https://github.com/nodejs/Release)
- [Docker Hub — library/postgres](https://hub.docker.com/_/postgres)

**Anthropic**
- [Batch processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing)
- [Pricing](https://platform.claude.com/docs/en/about-claude/pricing) · [Models overview](https://platform.claude.com/docs/en/about-claude/models/overview)
- [Model migration guide](https://platform.claude.com/docs/en/about-claude/models/migration-guide)
- [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) · [Rate limits](https://platform.claude.com/docs/en/api/rate-limits#message-batches-api)

**Dagster**
- [OSS deployment architecture](https://dagster.io/docs/deployment/oss/oss-deployment-architecture)
- [Deploying with Docker Compose](https://dagster.io/docs/deployment/oss/deployment-options/docker) · [examples/deploy_docker/docker-compose.yml](https://github.com/dagster-io/dagster/blob/master/examples/deploy_docker/docker-compose.yml)
- [Deploying Dagster as a service](https://dagster.io/docs/deployment/oss/deployment-options/deploying-dagster-as-a-service) · [Installation](https://dagster.io/docs/getting-started/installation)
- [Partitioning assets](https://dagster.io/docs/guides/build/partitions-and-backfills/partitioning-assets) · [Dagster daemon](https://dagster.io/docs/deployment/execution/dagster-daemon)
- [issue #26287 — daemon memory](https://github.com/dagster-io/dagster/issues/26287) · [issue #21307 — webserver/daemon leak](https://github.com/dagster-io/dagster/issues/21307)

**Next.js**
- [Incremental Static Regeneration](https://nextjs.org/docs/app/guides/incremental-static-regeneration) · [ISR with Cache Components](https://nextjs.org/docs/app/guides/incremental-static-regeneration-cache-components)
- [How to optimize memory usage](https://nextjs.org/docs/app/guides/memory-usage) · [Self-hosting](https://nextjs.org/docs/app/guides/self-hosting) · [revalidatePath](https://nextjs.org/docs/app/api-reference/functions/revalidatePath)

**Khác**
- [PostgreSQL 18 — Resource Consumption](https://www.postgresql.org/docs/18/runtime-config-resource.html)
- [SQLAlchemy — What's New in 2.1](https://docs.sqlalchemy.org/en/21/changelog/migration_21.html) · [PostgreSQL dialect](https://docs.sqlalchemy.org/en/21/dialects/postgresql.html)
- [Airflow — Running in Docker](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html)
