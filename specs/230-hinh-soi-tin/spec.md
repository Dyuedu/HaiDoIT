# Feature Specification: Hình response của tin dán ("Soi tin") và dữ liệu giả

**Feature Branch**: `gh-230-hinh-soi-tin`

**Created**: 2026-11-27

**Status**: Implemented, chờ merge. Đã qua hai đợt rà lại (2026-11-27; đợt hai: D2 not_evaluable, trần 200 kỹ năng, `market.note`, checklist `present` null, 422 không nêu khóa lạ, D7 tương thích tiến): hợp đồng nay mang đủ #231–#247 chỉ bằng cách thêm giá trị, không đổi hình. Test và kiểm tra đều xanh (xem `tdd.md`).

**Input**: GitHub issue [#230](https://github.com/Dyuedu/HaiDoIT/issues/230) — Agree the pasted-posting response shape and add fake data. Phục vụ story #124 (US-D1) và để chừa chỗ cho #125 (US-D2: so với thị trường) và #126 (US-D3: dấu hiệu cần kiểm). Đọc sau này bởi #231 (trần tốc độ, câu chữ), #232 (đọc bằng model), #234 (đánh dấu có/thiếu bằng số thật), #235, #236, #237 (màn hình), #240–#243 (so thị trường), #244–#247 (kiểm cảnh báo). Yêu cầu gốc: FR-26 đến FR-32 (D1 đến D7) ở `_bmad-output/planning-artifacts/epics.md`, AD-9, AD-10, AD-11, AD-17, AD-22, AD-26.

## Quyết định thiết kế (hai bước)

1. `POST /api/v1/posting-reads` nhận `{"text": "..."}`, đọc chữ dán qua cổng model đúng một lần và **không lưu gì**. Trả `{data}` gồm các sự kiện đóng đã trích, kể cả tin thu thập khớp (bước này thấy chữ nên tra luôn, FR-32).
2. `GET /api/v1/posting-check?role=&level=&have=&skills=&...` chỉ nhận **mã và số** (không bao giờ có chữ của tin), trả `Envelope{data, meta}` với ba mục: `match` (đã có số, từ #230), `market` (hình `ready` đã chốt cho #125, chưa tính) và `warnings` (hình `ready` đã chốt cho #126, chưa tính).

Lý do tách hai bước: đổi vai trò hoặc cấp bậc thì chỉ gọi lại bước 2 (AC 1 của #124: "tính lại mà không dán lại"), nên chữ dán chỉ đi lên máy chủ một lần (AD-11) và phép tính mức khớp nằm duy nhất ở API (AD-22). Hệ quả cho hợp đồng: mọi thứ màn cần hiện mà là chữ nguyên văn (cụm chưa nhận diện, trích dẫn phí, trích dẫn liên hệ, link tin khớp) nằm ở bước 1 và chỉ hiện trên màn; bước 2 chỉ nhận mã và số rút từ bước 1 (`QUERY_FIELDS` và `SCREEN_ONLY_FIELDS` của `tests/api/posting_samples.py` phân loại từng trường của bước 1 vào đúng một trong hai, test giữ điều đó).

## Hình bước 1 — `POST /api/v1/posting-reads`

Thân `{"text": "..."}`: `text` tối đa 20.000 ký tự (FR-26, `Field(max_length=20000)`). **Trần cỡ thân (AD-9)**: thân bị chặn **trước khi phân tích**, như `haido_api/uploads.py` làm với CV: `Content-Length` vượt `posting_read.max_body_bytes` của `config/rules.toml` bị từ chối ngay; thân không khai độ dài hoặc khai gian bị dừng lúc đọc khi vượt trần; chữ dài hơn 20.000 ký tự trong thân nhỏ hơn trần byte cũng vậy. Cả ba: 413 `text_too_long`, câu nêu giới hạn ("tối đa 20.000 ký tự"), nguồn đọc không được gọi. Trần byte là 131.072 (128 KiB): phủ 20.000 ký tự ở tệ nhất 4 byte UTF-8 mỗi ký tự (80.000) cộng phần phụ trội của JSON, và không mở cửa cho thân lớn vào bộ nhớ (config từ chối quá 1 MiB).

**#231 chồng lên đây (AC 1, trần cỡ)**: vòng review này đã cài trần cỡ vì route đã sống ở prod. #231 vẫn giữ trần tốc độ theo IP (`rate_limited`, 429) và câu chữ trên màn cho `text_too_long`. Không sửa gì trên GitHub; ghi ở đây để người làm #231 không làm lại.

`data` (`PostingReadData`):

- `is_posting: bool`; `reason: "not_posting" | "too_short" | "not_it" | null` (null khi là tin). Không phải tin thì mọi trường còn lại rỗng, null hoặc false. `not_it` (FR-26, UX-DR44: "Tin này có vẻ không thuộc lĩnh vực IT") là tin tuyển dụng mà không thuộc IT; `not_posting` là chữ không phải tin tuyển dụng; `too_short` là dưới 200 ký tự.
- `role`, `level`: mã trong `config/rules.toml` (`roles`, `labels.level`); `null` khi không phải tin. Tin không ghi cấp thì `level = "unknown"`. `branch` (FR-27): mã nhánh của vai trò hoặc `null`; mã là snake_case của nhãn trong `[[branches]]` của `config/classify.toml` (`cloud`, `llm_agent`, `product_owner`...) và phải thuộc đúng `role`.
- `skills`: `[{code, mentions}]`, mã trong bộ từ vựng, `mentions >= 1`, không trùng mã, **tối đa 200 (`MAX_PROFILE_SKILLS`, bằng trần `skills=` của bước 2)**: cổng đọc cắt phần dư ở cuối trước khi dựng model, nên tin nhắc nhiều kỹ năng không làm bước 2 trả 422.
- `unrecognised`: các cụm chữ chưa nhận diện, nguyên văn, **chỉ hiện trên màn**, tối đa 50 cụm, mỗi cụm tối đa 60 ký tự. Không bao giờ vào query của bước 2.
- `years_min: int | null` (0 đến 60); `salary: {min, max, currency: vnd|usd, period: month|year} | null` (số, tối đa `MAX_SALARY` = 10^10, **cùng trần với tham số `salary_min`, `salary_max` của bước 2** nên tin hợp lệ ở bước 1 không bao giờ bị 422 ở bước 2); `salary_non_numeric: bool` (tin nói về lương mà không có số, như "thỏa thuận"; loại trừ với `salary`); `company_named: bool`; `contacts`: tập đóng `company_email | company_site | phone | zalo | telegram | personal_email`.
- **Sự kiện của danh sách chi tiết (#244)**: `duties_described: bool` và `title_level: str | null` (cấp mà chức danh cho biết, mã của `labels.level` trừ `unknown`, hoặc `null` khi chức danh không nêu cấp). Dùng `title_level` đóng thay vì chữ của chức danh để "chức danh khớp cấp bậc" kiểm được mà không đưa chữ của JD lên bước 2.
- **Trích dẫn nguyên văn (#245)**: `fee_mentions` (tối đa 5, mỗi cái 120 ký tự) và `contact_quotes: [{channel, quote}]` (tối đa 5, mỗi `quote` 120 ký tự, `channel` nằm trong `contacts`), cạnh enum `contacts`. Dấu hiệu "phải trích điều đã tìm thấy": màn hiện chúng từ response này; không bao giờ vào query.
- **Tin thu thập khớp (FR-32, #246)**: `collected: {site, first_seen, repost_count, snapshots_seen, url} | null`. `url` bắt buộc khi có (FR-32 đòi link về tin gốc). Bước 1 tra vì chỉ nó thấy chữ; bước 2 chỉ nhận hai số cho D4.
- `model_id`, `prompt_version`, `vocab_version` (truy vết AD-9).

**Có `meta` không?** Không. Response này là `{data}` như `GET /api/v1/skills`: nó không có Stat nào của thị trường, không có ô thống kê để trỏ `cell_id`, không có snapshot. Các số trong đó (`mentions`, `years_min`, `salary`, `repost_count`, `snapshots_seen`) là sự kiện trích từ chữ người dùng dán hoặc từ tin đã thu thập, không phải số liệu thị trường, nên quy tắc "mọi số là Stat" (AD-17) không áp. Test `test_ad17_routes.py` ghi route này vào danh sách response của chữ người dùng, kiểm thân chỉ có `data` và các trường số nằm đúng danh sách cho phép.

**Lỗi đã khai cho đường thật** (mã và HTTP, theo hình lỗi chuẩn): `text_too_long` 413 (cài từ vòng review), `rate_limited` 429 (#231), `read_failed` 502, `read_unavailable` 503, `read_timeout` 504 (#232), `invalid_query` 422 (thân sai hình; khóa lạ trong thân chỉ được báo chung là "có trường không có trong hợp đồng", không lặp lại tên khóa vì tên đó có thể là chữ của tin dán, AD-11). Nguồn "model" của prod chưa cài đặt và trả 503 `read_unavailable`, nên route chưa nhận chữ thật tới khi #232 xong.

**Kết quả quá cỡ và lỗi của nguồn đọc (AD-11)**: kết quả của cổng đọc vượt trần (cụm chưa nhận diện 50×60, trích dẫn phí và liên hệ 5×120, `years_min` quá 60) bị cắt trước khi dựng model (`truncate_read`); số năm quá 60 thành `null` thay vì kẹp về trần, vì kẹp là bịa một sự kiện. Lỗi còn lại của một lần đọc (kể cả `ValidationError`) là 502 `read_failed`, không phải 500. Hợp đồng của nguồn đọc: thông điệp của mọi ngoại lệ có thể mang chữ của tin (`ValidationError` của pydantic chứa giá trị đầu vào), nên **route bắt mọi ngoại lệ của nguồn, chỉ ghi tên kiểu của nó, trả 502 và không ném lại lên máy chủ ASGI**; câu trong response luôn là câu chuẩn của mã lỗi (`POSTING_READ_MESSAGES`), không bao giờ thông điệp của nguồn.

**Nguồn giả chọn kết quả từ chữ dán, tất định** (xét theo thứ tự): (1) sau khi cắt khoảng trắng đầu cuối, ngắn hơn 200 ký tự thì `too_short`; (2) không chứa dấu IT nào của `it_markers` (không phân biệt hoa thường): có dấu tin tuyển dụng của `job_markers` ("tuyển dụng", "ứng tuyển", "mức lương", "quyền lợi", "gửi cv"...) thì `not_it`, không có thì `not_posting`; (3) chứa `đặt cọc` hoặc `deposit` thì tin có phí (Zalo, Telegram, không nêu công ty, cấp `unknown`); (4) chứa `devops`, `kubernetes` hoặc `terraform` thì tin DevOps nhánh `cloud` (cấp `mid`, lương "thỏa thuận", đã có tin thu thập khớp); (5) còn lại là tin Backend Junior.

**Đường ghi sẽ có (AD-11)**: các issue sau sẽ thêm đúng **một** đường ghi, và chỉ những gì AD-11 cho phép: từ khóa, tần suất, lần thấy cuối của cụm chưa nhận diện (FR-29, `unknown_mentions_pasted`) và sự kiện ẩn danh bốn trường mỗi lần soi (FR-26), không bao giờ chữ của tin. Đường đó nằm ở một mô-đun riêng mà route gọi với đúng các trường ấy. Vì vậy test cấm `sqlalchemy`, ghi file và `print` trong `routes/posting.py` và `posting_read.py` **được giữ** (nó cấm chữ của tin chạm đĩa hoặc cơ sở dữ liệu qua hai mô-đun này) và chỉ đổi khi mô-đun ghi đó có mặt; không nới thành "cấm mọi truy cập DB".

## Hình bước 2 — `GET /api/v1/posting-check`

Tham số (chỉ mã và số; tham số lạ bị 422, kể cả `text`):

| Tham số | Ý nghĩa |
|---|---|
| `role`, `level` | Ô đang dùng. Cùng mã với `skill-rates`. Bắt buộc. |
| `branch` | Mã nhánh (FR-27), phải thuộc `role` (đổi vai trò thì bỏ nhánh); được lặp lại ở `data.branch`. |
| `have` | Hồ sơ: mã kỹ năng ngăn bằng dấu phẩy, tối đa 200 (AD-22), cùng bộ đọc `parse_have` với `skill-rates`. **Không kiểm với bộ từ vựng**: chỉ kiểm định dạng, như `skill-rates`; mã lạ không khớp kỹ năng nào của tin nên bị bỏ qua (có test). |
| `skills` | Mã kỹ năng của tin, ngăn bằng dấu phẩy, tối đa 200, **phải có trong bộ từ vựng**: cụm chưa nhận diện dù đúng dạng snake_case vẫn bị 422, nên không thể lọt vào query. |
| `years_min`, `salary_min`, `salary_max`, `salary_currency`, `salary_period`, `salary_non_numeric`, `company_named`, `contacts`, `fees`, `duties_described`, `title_level`, `collected_reposts`, `collected_snapshots` | Sự kiện đóng của bước 1 cho #125 và #126 (`fees` là số trích dẫn phí; `collected_*` là hai số của tin thu thập khớp, đi cặp, vắng mặt là không khớp). #230 chỉ kiểm định dạng; #240–#246 mới đọc. |

Số lần nhắc (`mentions`) không đưa vào query: mức khớp theo FR-28 tính trên kỹ năng khác nhau, không cần số lần.

`data` (`PostingCheckData`): `role`, `branch`, `level`, `cell_id` (ô đã dùng cho `match`, sau khi quay về như `skill-rates`; nhãn quay về ở `meta.cells[cell_id].fallback_label`), `has_profile`, và ba mục:

- `match` (`PostingMatch`, có số):
  - `status`: `ready`, `not_enough_data` (ô đã dùng dưới 30 tin, không chia nhóm được) hoặc `no_skills` (tin không có kỹ năng nhận diện).
  - `skills`: mỗi kỹ năng của tin `{skill{code,name_en,name_vi}, group: core|common|specific|null, rate: Stat(skill_rate), have: bool|null}`. Thứ tự do máy chủ: core, common, specific, rồi tỷ lệ giảm dần, rồi mã. `specific` là kỹ năng tin nêu mà hiếm ở ô (nhóm `company_specific` của θ, hoặc không có dòng nào trong ô, tính là tỷ lệ 0). `have = null` khi không có hồ sơ.
  - `groups`: ba dòng `core, common, specific`, mỗi dòng `{group, total, had|null}` (chỉ khi `ready`; rỗng nếu không).
  - `level`: `{points, max_points, percent}` hoặc `null`. Trọng số core 3, common 2, specific 1 (`config/rules.toml`, `[posting_match]`), chỉ tính kỹ năng đã nhận diện; `percent` làm tròn nửa lên. Ví dụ FR-28: 4/4 core + 2/2 common + 0/2 specific = 12 + 4 + 0 = 16 trên 18 = 89%.
  - `cv_first`: mã kỹ năng vừa có trong hồ sơ vừa có trong tin, theo thứ tự của `skills` (#235).
  - `config_version`: phiên bản cấu hình đã cho trọng số (AD-10).
  - Không có hồ sơ (`has_profile = false`): `have` là `null`, `level = null`, `groups[].had = null`, `cv_first = []`; nhóm và tỷ lệ vẫn có (AC 4 của #124).
- `market` (#125, FR-30). Chưa tính: `{status: "not_ready", cell_id: null, years: null, skill_count: null, salary: null, note: null}`. Hình `ready` đã chốt đầy đủ:
  - `note`: `"comparisons_not_verdict"` khi `ready` (bắt buộc), `null` khi `not_ready`: mã câu "đây là so sánh với thị trường, không phải phán quyết về tin" (AC 5 của #125, #242); chữ do web dựng từ mã.
  - `cell_id`: ô của ba so sánh, **có thể khác `data.cell_id` của `match`** (mỗi mục quay về theo thước đo của mình). Cỡ mẫu "chưa đủ dữ liệu (X/30 ...)" lấy ở `meta.cells[market.cell_id].n_by_measure` theo thước của chính trường (FR-30: ngưỡng đếm số tin có đúng trường đó, không đếm cả ô): `years` là `experience_years`, `skill_count` là `skill_count`, `salary` là `salary`. (Bản trước của spec này trỏ nhầm vào ô của `match` và vào `n_by_measure` chung chung; đã sửa.)
  - `years`, `skill_count`: `{state: compared|not_enough_data|not_stated, percentile: Stat(percentile, 0 đến 100)|null, ci_low: Stat|null, ci_high: Stat|null}`. `ci_low`, `ci_high` là khoảng tin cậy 95% (AD-26), đi cặp, bao `percentile`, chỉ có khi `compared` và 30 ≤ n < 100 (`[posting_market] ci_below_n = 100` của `config/rules.toml`); `Envelope` kiểm điều này với `meta`. `not_stated` (tin không ghi) chỉ dành cho `years`.
  - `salary`: `{state: compared|not_enough_data|not_stated|not_numeric, position: below|within|above|null, low: Stat|null, high: Stat|null, converted: {min_vnd_month, max_vnd_month, fx: {rate, unit: "vnd_per_usd", fx_version}|null}|null, note: "salary_not_stated"|null}`. **Lương được quy đổi trước khi so** (AD-10: tiền là VND một tháng gross; USD theo tỷ giá cố định của snapshot kèm `fx_version`, lương theo năm chia 12), nên trạng thái cũ "không so được vì không phải VND một tháng" đã bỏ. `not_stated` là sự thật trung tính có mã câu `salary_not_stated`, không phải cảnh báo (AC 4 của #125). `not_numeric`: tin nói về lương mà không có số. `low` và `high` là P25 và P75 (khoảng giữa, DEC-10).
- `warnings` (#126, FR-31). Chưa tính: `{status: "not_ready", checklist: [], signs: [], collected_match: null, salary_note: null, disclaimer: null}`. Hình `ready` đã chốt đầy đủ:
  - `checklist`: đủ bốn mục `company_named | salary_stated | duties_described | title_matches_level`, mỗi mục `{code, present: bool|null}` (#244). `null` là "không biết", khác `false`: `title_matches_level` là `null` khi `title_level` của tin là `null` hoặc cấp là `unknown`.
  - `signs`: **đủ bảy** theo thứ tự D1 đến D7 (`d1_wide_skills`, `d2_specific_heavy`, `d3_high_req_low_pay`, `d4_reposted`, `d5_unusual_contact`, `d6_fee_first`, `d7_no_company`), mỗi cái `{code, status: triggered|not_triggered|not_evaluable, reason, fact, action, source_field}`. `reason` chỉ có khi `not_evaluable`: `not_in_data` (D4: "không đánh giá được: tin chưa có trong dữ liệu"), `not_enough_data` (D1, D2, D3: ô chưa đủ mẫu để có P90, P75, P25 hay nhóm kỹ năng), `no_numeric_salary` (D3). `fact` là đối tượng có kiểu theo dấu hiệu, chỉ có khi `triggered`: D1 `{skill_count, p90: Stat}`; D2 `{recognised_count, specific_count}`; D3 `{skill_count, p75_skill_count: Stat, salary_ceiling_vnd_month, p25_salary: Stat}`; D4 `{reposts, snapshots_seen}`; D5 `{channels}`; D6 `{quote_count}`; D7 `{}`. `action` là mã câu gợi ý (một-một với dấu hiệu). `source_field` là `contacts` (D5), `fee_mentions` (D6) hoặc `null`. D5 trỏ tới trích dẫn bằng kênh (màn lọc `contact_quotes` theo `channels`) và D6 bằng số trích dẫn (màn lấy `fee_mentions[0 : quote_count]`), vì bước 2 không nhận chữ và không nhận thứ tự trích dẫn.
  - `collected_match`: `{repost_count, snapshots_seen}` hoặc `null` (không khớp: D4 là `not_evaluable`). Site, ngày thấy đầu và link ở `collected` của bước 1. Bản trước định nghĩa `{site, first_seen, repost_count, url|null}` ở bước 2, nhưng bước 2 không có chữ nên không thể điền; đã đổi.
  - `salary_note`: `salary_not_stated` khi tin không ghi lương (dòng trung tính của FR-31, không phải dấu hiệu). `disclaimer`: `signs_are_hints`, mã câu cố định FR-31 ("Dấu hiệu là gợi ý để bạn tự kiểm tra. Đa số tin bị gắn dấu hiệu vẫn là tin thật."), có khi và chỉ khi `ready`.

Một mục chưa làm luôn là `not_ready`, không phải số 0 hay danh sách rỗng trông như "không có gì". Ngưỡng của D1 đến D7 (P90, ≥ 4 và > 50%, P75 và P25 với 30 tin có lương, ≥ 2 lần đăng lại hoặc ≥ 30 snapshot) là của #245 và sẽ vào `config/rules.toml` ở đó (AD-10); hình chỉ mang các số đã kích hoạt chúng. Câu chữ của dấu hiệu và gợi ý ở web, không dùng "lừa đảo", "tin giả", "tin ma" (cổng FR-25/31/47 vẫn xanh; mã câu là snake_case tiếng Anh).

**Nguồn**: `GET` đi qua `MarketReadModel.posting_check` với khóa `SOURCE_ENV["posting_check"]` = `HAIDO_MARKET_SOURCE_POSTING_CHECK`. Prod đặt `stat`; `StatMarket.posting_check` ném `CheckUnavailable`: **503 `check_unavailable`** ("chưa sẵn sàng, thử lại sau", khai trong OpenAPI, web coi là thử lại được) cho tới #234, **không phải** 404 `unknown_cell` (kết quả cuối "không có số cho vai trò này"), để màn không nhầm chưa nối số với không có dữ liệu. `POST` đi qua `PostingReader` với biến `HAIDO_POSTING_READER` (`fake` mặc định, `model` ở prod, demo và loadtest, trả 503 `read_unavailable` tới #232). Mặc định `fake` khi không đặt biến, như mọi nguồn khác (#309: đóng cửa ở compose, không ở mã; các test deploy giữ cả ba file compose). Prod, demo và loadtest không bao giờ trả dữ liệu giả.

**Bản giả quay về cho mọi cấp**: tin đọc ở bước 1 luôn qua được bước 2. Cấp không có ô trong fixture (`unknown` của tin không ghi cấp, hay `mid` của `devops`) quay về ô mọi cấp của vai trò, kèm `fallback_label` (phép 2 như `intern`); chỉ vai trò không có ô nào là 404. `skill-rates` giả không đổi (vẫn 404 ở những cấp đó).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ba màn dựng trên một hình (Priority: P1)

Người làm #233–#237 (kết quả khớp), #240–#243 (so thị trường), #244–#247 (cảnh báo) dựng cùng lúc trên dữ liệu giả có đủ hình, và hình `ready` của hai mục sau đã chốt nên không phải đổi khi số thật đến.

**Why this priority**: AC duy nhất của #230. Nếu mỗi bên tự đoán hình thì ba màn chạy trên dữ liệu giả nhưng vỡ khi nối số thật.

**Independent Test**: `tests/api/test_fr28_posting_check.py`, `tests/api/test_fr26_posting_read.py`, `tests/api/test_ad22_posting_check_query.py`, `tests/api/test_ad11_posting_read.py`, `tests/api/test_gh230_posting_read_caps.py`, `tests/api/test_fr30_fr31_posting_ready_shapes.py`, `tests/deploy/test_gh230_posting_nguon_prod.py`, `web/tests/fr28-posting-fixture.test.ts`, `web/tests/fr30-fr31-posting-ready.test.ts`.

**Acceptance Scenarios** (mỗi AC của #230 và các AC của #124–#126 mà hình phải mang được):

1. **Given** nguồn giả, **When** `GET /api/v1/posting-check?role=backend&level=junior&skills=<8 mã>`, **Then** `data.match` có đủ kỹ năng, nhóm, tỷ lệ; `data.market` và `data.warnings` có `status = not_ready` và rỗng (AC của #230).
2. **Given** hồ sơ có đúng 6 kỹ năng (4 core, 2 common) của tin, **When** gọi với `have`, **Then** `match.level` là 16 trên 18 và 89 (ví dụ FR-28), `groups` là 4/4, 2/2, 0/2 (AC 2 của #124).
3. **Given** hồ sơ có kỹ năng trùng với tin, **Then** `cv_first` liệt kê đúng các kỹ năng đó (AC 3 của #124).
4. **Given** `have` rỗng, **Then** `has_profile = false`, `level = null`, mọi `have = null`, nhóm và tỷ lệ vẫn có (AC 4 của #124).
5. **Given** ô vai trò × cấp dưới 30 tin, **Then** `cell_id` là ô rộng hơn và `meta.cells[cell_id].fallback_label` giải thích; nếu không ô nào đủ thì `match.status = not_enough_data`, không có nhóm (AC 1 của #124, FR-27).
6. **Given** chữ không phải tin, quá ngắn hoặc tin tuyển dụng ngoài IT, **When** `POST /api/v1/posting-reads`, **Then** `is_posting = false`, `reason = not_posting`, `too_short` hoặc `not_it`, không có kỹ năng, vai trò hay cấp (AC 5 của #124, FR-26).
7. **Given** lỗi của đường thật, **Then** các mã `text_too_long`, `rate_limited`, `read_unavailable`, `read_timeout`, `read_failed` đã khai trong OpenAPI (AC 6 của #124).
8. **Given** `POST`, **Then** nguồn không giữ trạng thái và route không ghi chữ dán vào log (AC 7 của #124, AD-11).
9. **Given** `GET` có tham số lạ hoặc kỹ năng ngoài bộ từ vựng, **Then** 422 `invalid_query` (AD-22).
10. **Given** `compose.prod.yml`, **Then** mọi khóa của `SOURCE_ENV` (kể cả `posting_check`) là `stat` và `HAIDO_POSTING_READER` là `model` (#309); `compose.demo.yml` và `compose.loadtest.yml` cũng đặt `model` và `posting_check: stat`.
11. **Given** fixture web, **Then** chúng bằng response của API giả (`test_ad17_web_fixtures.py`); hai ví dụ `ready` bằng `tests/api/posting_examples.py`.
12. **Given** tin có `role` có nhánh (DevOps, `cloud`), **When** đọc rồi gọi bước 2 với `branch`, **Then** bước 1 trả `branch = cloud` và bước 2 lặp lại nó; nhánh không thuộc vai trò là 422 (FR-27).
13. **Given** tin đọc thành công ở bước 1 (kể cả tin có phí, cấp `unknown`), **When** dựng query từ kết quả (chỉ mã và số) và gọi bước 2, **Then** 200 (chuỗi hai bước, test cho mọi tin `is_posting` của bản giả).
14. **Given** tin có chữ nguyên văn (cụm chưa nhận diện, trích dẫn phí, trích dẫn liên hệ, link tin khớp), **Then** chúng chỉ ở response bước 1 và không bao giờ trong query của bước 2 (AC của #245, AD-22).
15. **Given** tin khớp một tin đã thu thập, **Then** bước 1 trả `collected` có `url`, và bước 2 nhận `collected_reposts`, `collected_snapshots` (FR-32, D4).
16. **Given** kết quả của cổng đọc vượt trần hoặc sai hình, **Then** quá cỡ thì bị cắt (200), sai hình thì 502 `read_failed`, không bao giờ 500 và không có chữ của tin trong response hay log (AD-11).
17. **Given** thân quá 131.072 byte, hoặc `text` quá 20.000 ký tự, **Then** 413 `text_too_long` nêu giới hạn, nguồn đọc không được gọi (AD-9; chồng với #231 AC 1).
18. **Given** `market` và `warnings` ở hình `ready` (ví dụ viết tay), **Then** hợp lệ với `Envelope[PostingCheckData]` kể cả luật với `meta` (X/30 theo ô của `market`, khoảng tin cậy khi 30 ≤ n < 100), và mọi kiểu sai bị schema từ chối (FR-30, FR-31).
19. **Given** nguồn `stat` chưa có số thật, **Then** 503 `check_unavailable` (không phải 404 `unknown_cell`), web coi là thử lại được.
20. **Given** web nhận `market` hoặc `warnings` ở hình `ready`, **Then** bộ kiểm chấp nhận và màn không trắng; hình sai bị từ chối.
21. **Given** ô khớp chưa đủ mẫu nên không có nhóm kỹ năng, **Then** D2 là `not_evaluable` với `reason = not_enough_data` (đợt rà lại 2026-11-27); lý do khác thì bị từ chối.
22. **Given** tin nhắc quá 200 kỹ năng, **When** đọc rồi gọi bước 2, **Then** `skills` của bước 1 bị cắt còn 200 và bước 2 trả 200, không phải 422.
23. **Given** `market` ở hình `ready`, **Then** có `note = comparisons_not_verdict`; `not_ready` thì `note = null` (AC 5 của #125, #242).
24. **Given** chức danh không cho biết cấp, **Then** `title_matches_level.present` là `null` (không biết), hợp lệ ở API và web.
25. **Given** thân `POST` có khóa lạ mang chữ của tin, **Then** 422 không chứa khóa đó.
26. **Given** web nhận D7 `triggered` có thêm trường lạ trong `fact`, **Then** vẫn chấp nhận (tương thích tiến).

### Edge Cases

- Kỹ năng của tin không có dòng trong ô đã dùng: tỷ lệ 0, nhóm `specific` (quy ước của bản giả; #234 phải theo cùng quy tắc hoặc ghi lại khác biệt).
- Tin có kỹ năng nhưng ô bị ẩn (dưới 30): `status = not_enough_data`, `group = null`, `rate` là `null_data`, `have` vẫn có nếu có hồ sơ.
- `fees` lớn hơn 5, `years_min` âm, `salary_min` lớn hơn `salary_max`, có lương mà thiếu tiền tệ hay kỳ, `salary_non_numeric` cùng `salary_*`, `collected_reposts` mà thiếu `collected_snapshots`: 422.
- `have` có mã không có trong bộ từ vựng: không lỗi, mã đó không khớp kỹ năng nào (như `skill-rates`).
- Tin không ghi lương: dòng trung tính `salary_not_stated`, không phải dấu hiệu (FR-31); tin ghi "thỏa thuận": `salary_non_numeric`, `market.salary.state = not_numeric`.

## Requirements

- **FR-26**: bước 1 trả kỹ năng theo bộ từ vựng, không lưu chữ dán, tối đa 20.000 ký tự (413 `text_too_long` quá đó); tin không thuộc IT báo `not_it` và không tính mức khớp.
- **FR-27**: vai trò, nhánh và cấp nhận diện là mã; đổi hai mã vai trò hoặc cấp gọi lại bước 2, không dán lại.
- **FR-28 và FR-29**: trọng số core 3, common 2, specific 1 từ cấu hình có phiên bản; kỹ năng chưa nhận diện không tính; nhóm `specific` hiếm ở ô.
- **FR-30**: hình `market` mang phân vị kèm khoảng tin cậy 95% khi 30 ≤ n < 100, lương đã quy đổi theo tỷ giá của snapshot, cỡ mẫu theo từng thước ở ô của `market`.
- **FR-31**: hình `warnings` mang đủ D1 đến D7 với trạng thái, dữ kiện có kiểu và gợi ý hành động; câu ghi chú cố định và dòng lương trung tính là mã câu.
- **FR-32**: bước 1 tra tin thu thập khớp và trả link; bước 2 nhận số lần đăng lại và số snapshot cho D4.
- **AD-9**: một cổng đọc; `model_id`, `prompt_version`, `vocab_version` đi theo kết quả; trần cỡ thân ở API, trần tốc độ ở #231.
- **AD-10**: tỷ giá, trọng số, ngưỡng khoảng tin cậy và trần thân nằm trong `config/rules.toml` có phiên bản.
- **AD-11**: không bảng, không log nào chứa chữ của tin; lỗi của nguồn đọc chỉ ghi tên kiểu.
- **AD-17**: mọi số của thị trường là Stat có `meta`; số đếm, tiền và tỷ giá của chính tin là `Ordinal`, thêm vào danh sách khóa của `test_ad17_ordinal_allowlist.py`.
- **AD-22**: hồ sơ lên máy chủ chỉ ở GET `?role=&level=&have=`; phép tính mức khớp chỉ ở API.

## Success Criteria

- AC của #230: kết quả giả có mục khớp kỹ năng và hai mục rỗng cho so thị trường và cảnh báo, và hình `ready` của hai mục đó mang được #231–#247 mà chỉ thêm.
- Mọi scenario trên có test và xanh; `uv run pytest -q`, `ruff`, `check_gates`, `vitest`, `tsc`, `eslint` đều xanh.
