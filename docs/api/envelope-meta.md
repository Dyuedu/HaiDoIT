# Hợp đồng envelope `{data, meta}` — cho người dựng giao diện

Nguồn yêu cầu: AD-17 (spine), issue #2 (C-1). Schema máy đọc được: [`openapi.json`](openapi.json).
Code: `haido_core/domain/envelope.py` (envelope), `haido_core/domain/display_policy.py` (quy tắc ẩn
số liệu khi mẫu nhỏ), `haido_api/schemas/` (phần `data` của từng route và hình lỗi).

**Ẩn số liệu khi mẫu nhỏ** nghĩa là: con số tính từ quá ít tin (dưới ngưỡng mẫu, hiện là 30) thì
không hiện như số bình thường. Tỷ trọng thành phố vẫn hiện nhưng mờ, kèm nhãn cỡ mẫu nhỏ; tỷ lệ kỹ
năng và phân vị thì ẩn hẳn, giao diện ghi "chưa đủ dữ liệu".

Hợp đồng này không đổi khi dữ liệu thật nối vào (Story 1.21 cho tỷ trọng thành phố, #27 cho tỷ lệ
kỹ năng). Giao diện dựng trên dữ liệu giả hôm nay chạy được trên dữ liệu thật mà không cần sửa.

## Ba quy tắc

1. **Mọi con số trong `data` là một `Stat`.** Không có số nào đứng riêng ngoài `Stat`. `Stat` mang
   luôn trạng thái hiển thị, nên giao diện chỉ cần một component cho mọi con số. Ngoại lệ duy nhất là dấu `Ordinal`
   (AD-22, #212): vị trí và số đếm trên chính các mã kỹ năng của người dùng ("N of M skills on this path", số chặng),
   không bao giờ là số tin, tỷ lệ, tỷ trọng hay n. Envelope chỉ miễn một trường khi kiểu của nó đúng là `Ordinal` hoặc
   `Ordinal | None` và giá trị là số nguyên không âm (không phải `bool`); kiểu ghép như `tuple[Ordinal, float]` hay
   `list[Stat] | Ordinal` vẫn bị kiểm. Tập trường dùng `Ordinal` bị khóa bằng test
   (`tests/api/test_ad17_ordinal_allowlist.py`): hiện chỉ `PathStage.stage`, `LearningPathData.current_stage`,
   `have_on_path`, `path_size`, và `SkillRatesData.core_size`, `have_core` (#149).
2. **Máy chủ quyết số liệu nào được hiện** (`suppression_for`), giao diện chỉ đọc `display`. Không so `n` với 30 ở
   giao diện, không tự tính tỷ trọng hay tỷ lệ. Envelope tự kiểm: `display` của tỷ trọng và tỷ lệ
   kỹ năng, cùng `insufficient_by_measure`, phải đúng bằng kết quả `suppression_for`.
3. **Mọi `cell_id` trong `data` có mục trong `meta.cells`.** Cỡ mẫu, cơ cấu cấp bậc và nhãn quay về
   của một con số luôn tra được ở `meta.cells[stat.cell_id]`.

## `Stat`

```json
{ "value": 0.02394526795895097, "kind": "composition_share", "display": "low_sample_shown", "cell_id": "da_nang.ai_ml" }
```

| Trường | Kiểu | Ý nghĩa |
|---|---|---|
| `value` | số thực hoặc `null` | Chưa làm tròn. Tỷ lệ, tỷ trọng là 0–1; giao diện tự làm tròn khi hiển thị, đúng một lần |
| `kind` | `composition_share` · `skill_rate` · `percentile` · `level_share` | Loại thước đo |
| `display` | `shown` · `low_sample_shown` · `null_data` | Cách hiển thị, xem bảng dưới |
| `cell_id` | chuỗi | Mã ô, opaque. Chỉ dùng để tra `meta.cells` |

| `display` | `value` | Giao diện làm gì |
|---|---|---|
| `shown` | có | Hiện bình thường |
| `low_sample_shown` | có | Hiện mờ, kèm nhãn cỡ mẫu nhỏ với `n` của ô (FR-33). Chỉ xảy ra với `composition_share` |
| `null_data` | `null` | Ghi "chưa đủ dữ liệu". Tỷ lệ kỹ năng, tỷ lệ cấp bậc và phân vị dưới ngưỡng luôn ở trạng thái này |

## `meta`

| Trường | Kiểu | Ý nghĩa |
|---|---|---|
| `snapshot_date` | `YYYY-MM-DD` | Ngày snapshot, giờ Việt Nam |
| `snapshot_status` | `published` · `partial` | `partial` khi có nguồn lỗi; vẫn đọc được |
| `sources` | chuỗi[] | Nguồn có ít nhất một tin được đếm trong cửa sổ 60 ngày của snapshot, A–Z (#259); `linkedin` không bao giờ có mặt (#263) |
| `sources_failed` | chuỗi[] | Nguồn lỗi; rỗng khi `published` |
| `thresholds` | `{min_sample, theta_core, theta_common}` | Ngưỡng đã dùng cho response này |
| `coverage_notes` | `{code, text}[]` | Lưu ý độ phủ, ít nhất một; hiện `text` trên mọi màn hình có số |
| `cells` | `{cell_id: CellMeta}` | Một mục cho mỗi ô mà response dùng |

`CellMeta`:

| Trường | Ý nghĩa |
|---|---|
| `n` | Số tin của ô |
| `fallback_label` | Câu giải thích khi số lấy từ ô rộng hơn ô người dùng chọn; `null` nếu không quay về |
| `seniority_mix` | Số tin theo cấp bậc chi tiết, ví dụ `{"intern": 13, "fresher": 7, "junior": 32}` |
| `n_by_measure` | Số tin có giá trị của từng thước đo: `skill_count`, `experience_years`, `salary`. `skill_count` (số tin đã quét kỹ năng, `n_scanned` của #101) là cỡ mẫu của mọi `Stat` `kind = skill_rate`: `display` của chúng khớp `suppression_for` trên `skill_count`, thiếu khóa thì trên `n`. Loại khác xét `n` |
| `insufficient_by_measure` | `true` khi thước đo đó dưới ngưỡng. Phân vị lương xét `n_by_measure.salary`, không xét `n` |

Mã vai trò, cấp bậc, thành phố, nhóm kỹ năng hiện là chuỗi tạm (`ai_ml`, `entry`, `ha_noi`, `core`…);
#16 chốt mã thật. Chuỗi hiển thị tiếng Việt sẽ đến từ bảng tra, không suy từ mã.

## `GET /api/v1/city-shares?role=<mã>&level=<mã>&years=<mã>`

Tỷ trọng từng thành phố trong số tin của vai trò, ở cấp bậc đã chọn, trên toàn quốc (FR-33). `role=all` là mọi vai
trò. `level` là tham số tùy chọn (#163):

| `level` | Nghĩa |
|---|---|
| `all` (mặc định khi bỏ trống) | Mọi cấp bậc; số và mã ô như trước khi có tham số này |
| `entry` | Nhóm mới vào nghề: Intern, Fresher, Junior gộp một (#134). Không gồm `unknown` |
| `intern`, `fresher`, `junior`, `mid`, `senior`, `lead` | Từng cấp |
| `unknown` | Tin chưa ghi cấp bậc ("Level not stated") |

Danh sách lấy từ `level_options` trong `config/rules.toml`. Giá trị ngoài danh sách là 422 `invalid_query`. Giao diện
luôn gửi `level` rõ ràng (mặc định `entry`). Nguồn giả chỉ có `all` và `entry`; cấp khác trả 404 `unknown_cell`.
Vai trò không có tin nào ở cấp đã chọn cũng là 404 `unknown_cell`, kèm ngày snapshot.

`years` là tham số tùy chọn (#280), mốc số năm kinh nghiệm tối thiểu mà tin yêu cầu:

| `years` | Nghĩa |
|---|---|
| `any` (mặc định khi bỏ trống) | Mọi tin, kể cả tin không ghi số năm; số và mã ô như trước khi có tham số này |
| `0`, `1`, `2`, `3`, `5` | Chỉ tin yêu cầu tối thiểu không quá N năm (`0` = không cần kinh nghiệm). Tin không ghi số năm bị bỏ |

Danh sách lấy từ `years_options` trong `config/rules.toml`; giá trị ngoài danh sách là 422 `invalid_query`. Giao diện
luôn gửi `years` (mặc định `any`). Nguồn giả chỉ có `any` cho mọi (vai trò, cấp), cộng `years=1` cho `role=all&level=entry`.

```json
{
  "data": {
    "role": "ai_ml",
    "level": "all",
    "total_cell_id": "vn.ai_ml",
    "rows": [
      { "city": "da_nang",
        "share": { "value": 0.02394526795895097, "kind": "composition_share",
                   "display": "low_sample_shown", "cell_id": "da_nang.ai_ml" } }
    ]
  },
  "meta": { "…": "…",
    "cells": {
      "vn.ai_ml": { "n": 877, "fallback_label": null, "…": "…" },
      "da_nang.ai_ml": { "n": 21, "fallback_label": null,
        "seniority_mix": { "intern": 2, "junior": 9, "mid": 7, "senior": 3 },
        "n_by_measure": { "skill_count": 21, "experience_years": 14, "salary": 5 },
        "insufficient_by_measure": { "skill_count": true, "experience_years": true, "salary": true } } } }
}
```

- `rows` có một dòng cho mỗi thành phố, cộng dòng `other` (thành phố khác, hiện ở chú thích) và
  `unknown` (không xác định thành phố). Không rỗng, không trùng `city`, mọi `share.value` có giá trị,
  và tổng bằng 1.
- `total_cell_id` là ô toàn quốc của vai trò ở cấp đã chọn, mẫu số của mọi tỷ trọng.
- `data.level` là cấp đã dùng (`all` khi không gửi `level`); giao diện đối chiếu nó với cấp đã yêu cầu.
- `data.years` là mốc số năm đã dùng (`any` khi không gửi `years`); giao diện cũng đối chiếu nó.
- `data.years_unstated_cell_id` (#280): `null` khi `years = any`; ở một mốc, là ô `vn.<vai trò>[.<cấp>].ynone` của
  `meta.cells`, có `n` là số tin của vai trò ở cấp đó không ghi số năm nên không được tính. Số này nằm ở `meta.cells`
  chứ không đứng trần trong `data` (luật 1 ở trên).
- Mã ô: `<phạm vi>.<vai trò>` ở `level=all` (ví dụ `ha_noi.ai_ml`), `<phạm vi>.<vai trò>.<cấp>` ở cấp khác (ví dụ
  `ha_noi.ai_ml.entry`, `vn.ai_ml.entry`). Cỡ mẫu và `seniority_mix` của ô theo cấp chỉ tính các cấp thuộc nó. Ở mốc
  số năm `N`, mã ô có thêm đuôi `.y<N>` (ví dụ `vn.ai_ml.entry.y1`, `ha_noi.ai_ml.y2`).
- Thành phố dưới ngưỡng vẫn có `value`, kèm `low_sample_shown`: vẽ cột mờ, không ẩn cột. Ngưỡng xét theo `n` của ô
  thành phố ở cấp và mốc số năm đã chọn, không theo `n` của mọi cấp.

## `GET /api/v1/skill-rates?role=<mã>&level=<mã>&have=<mã,mã,...>`

Tỷ lệ xuất hiện của từng kỹ năng trong ô vai trò × cấp bậc. `role` và `level` bắt buộc; `level` là `all` hoặc một mã
của `level_options` (#149). `have` tùy chọn, cùng luật với `learning-path` (AD-22).

```json
{
  "data": {
    "role": "java_backend", "level": "entry", "cell_id": "vn.backend.entry",
    "rows": [
      { "skill": "java",
        "rate": { "value": 0.6538461538461539, "kind": "skill_rate", "display": "shown", "cell_id": "vn.backend.entry" },
        "group": "core", "have": true }
    ],
    "core_size": 7, "have_core": 1
  },
  "meta": { "…": "…",
    "cells": {
      "vn.backend.entry": { "n": 52,
        "fallback_label": "Backend · Fresher chỉ có 26 tin đọc được kỹ năng (dưới 30), chưa đủ để tính riêng, nên số dưới đây lấy từ Backend · Entry (52 tin đọc được kỹ năng).",
        "seniority_mix": { "intern": 13, "fresher": 7, "junior": 32 },
        "n_by_measure": { "skill_count": 52, "experience_years": 37, "salary": 13 },
        "insufficient_by_measure": { "skill_count": false, "experience_years": false, "salary": true } } } }
}
```

- `data.cell_id` là ô **đã dùng**. Khi khác ô người dùng chọn, `meta.cells[data.cell_id].fallback_label`
  giải thích vì sao; hiện câu đó nguyên văn.
- `group` là nhóm kỹ năng theo θ: `core`, `common`, `company_specific`. Khi `rate.display = null_data`
  thì `group = null`: không hiện tên nhóm, không hiện phần trăm. Khi ô bị ẩn số liệu, thứ tự dòng
  không mang nghĩa xếp hạng (bản giả xếp theo mã kỹ năng).
- Dòng đã theo thứ tự hiển thị (#149): có tỷ lệ trước, tỷ lệ giảm dần, rồi mã kỹ năng. Giao diện không sắp lại.
- `have` của dòng: mã kỹ năng có trong `have=`. `core_size` là số dòng `core`, `have_core` là số dòng `core` có
  `have`; cả hai `null` khi mọi `rate` là `null_data`. Hai số này là `Ordinal` (quy tắc 1), như `path_size` và
  `have_on_path` của `learning-path`: số đếm trên mã kỹ năng của ô và của người dùng, không phải số tin.
- Bản thật (`HAIDO_MARKET_SOURCE_SKILL_RATES=stat`, #151) đọc `stat_skill_rates` của snapshot đọc được mới nhất, chỉ ô
  toàn quốc. Ô do phép 2 (`select_cell`, #106) chọn theo thứ tự `(vai trò, cấp)` → `(vai trò, nhóm cấp)` → `(vai trò,
  all)`, không đổi phạm vi và vai trò; đủ mẫu là `n_scanned >= min_sample`. `meta.cells[data.cell_id].n` là `n` của ô,
  `n_by_measure.skill_count` là `n_scanned`, `fallback_label` là nhãn của phép 2: `null` khi ô đã chọn đủ mẫu; còn lại
  gọi tên ô được chọn và n của nó, tên ô đã dùng và n của nó (n là số tin đọc được kỹ năng, tức `n_scanned`, nên có thể
  nhỏ hơn `meta.cells[...].n`), và ở bước `all` với cấp mới vào nghề thì thêm tỷ lệ tin Mid trở lên của ô đó (FR-19;
  làm tròn nửa lên, mẫu số là mọi tin của ô kể cả `unknown`). Dòng chỉ gồm `core` và `common` (nhóm theo θ của `meta.thresholds`). Khi không tập nào
  đủ `min_sample`, `data.cell_id` là ô `all`, dòng là kỹ năng có nhắc ít nhất một lần, xếp theo mã, mọi `rate` là
  `null_data`, `group = null`, `core_size` và `have_core` là `null`. Vai trò ngoài `config/rules.toml` hoặc không có tin
  nào ở snapshot là 404 `unknown_cell`, cũng như ô có trong `stat_cells` mà không có hàng tỷ lệ nào. Ô đủ mẫu mà mọi
  kỹ năng dưới θ_common cho `rows = []`, `core_size = 0`, `have_core = 0` (hợp lệ; web hiện câu giải thích).

## `GET /api/v1/role-for-title?title=<chức danh>`

Chức danh người dùng gõ thành một vai trò qua phép 6 (#150). Response không có số nên không dùng Envelope (như
`GET /api/v1/skills`).

```json
{ "data": { "status": "matched", "role": "backend" } }
```

- `status`: `matched` (có `role`), `generic` (chức danh IT chung chung như `Developer`, `role = null`), `not_it`
  (`role = null`). Hai trường hợp sau: giao diện nói không khớp và hiện danh sách vai trò, không hiện số.
- `title` 1–120 ký tự sau khi bỏ khoảng trắng hai đầu; sai là 422 `invalid_query`. Chức danh không được lưu, ghi log hay
  lặp lại trong response.

## `GET /api/v1/newcomer-roles`

Màn người mới (#110): mỗi vai trò một dòng, có số tin entry-level (Intern, Fresher, Junior), tỷ lệ
trong số tin của vai trò, và n. Không có tham số.

```json
{
  "data": {
    "levels": ["intern", "fresher", "junior"],
    "rows": [
      { "role": "ai_ml", "total_cell_id": "vn.ai_ml", "entry_cell_id": "vn.ai_ml.entry",
        "share": { "value": 0.5712656784492588, "kind": "level_share", "display": "shown", "cell_id": "vn.ai_ml" } },
      { "role": "embedded", "total_cell_id": "vn.embedded", "entry_cell_id": "vn.embedded.entry",
        "share": { "value": null, "kind": "level_share", "display": "null_data", "cell_id": "vn.embedded" } }
    ]
  },
  "meta": { "…": "…",
    "cells": {
      "vn.ai_ml": { "n": 877, "…": "…" }, "vn.ai_ml.entry": { "n": 501, "…": "…" },
      "vn.embedded": { "n": 12, "…": "…" }, "vn.embedded.entry": { "n": 6, "…": "…" } } }
}
```

| Con số | Đọc ở |
|---|---|
| Số tin entry-level | `meta.cells[entry_cell_id].n` |
| Tỷ lệ | `share.value`, chỉ khi `share.display = shown` |
| n của vai trò | `meta.cells[total_cell_id].n` |

- `share.kind = level_share`, `share.cell_id = total_cell_id`. Vai trò có n dưới `min_sample` thì
  `share.display = null_data`: ghi "not enough data (n/min_sample)", vẫn hiện số tin entry-level.
- Vai trò đủ mẫu mà không có tin entry-level có `share.value = 0`: hiện 0 và giữ trong danh sách.
- Mọi vai trò của `config/rules.toml` có mặt, kể cả vai trò không có tin nào (n = 0).
- `rows` đã theo thứ tự hiển thị: dòng có tỷ lệ trước, rồi dòng `null_data`; trong mỗi nhóm, số tin
  entry-level giảm dần rồi theo mã vai trò. Web không sắp xếp lại.
- Kiểu TypeScript và hàm tra số: `web/lib/newcomer-roles.ts`. Fixture cho test web:
  `web/tests/fixtures/newcomer-roles.json`.

## `GET /api/v1/market-overview`

Toàn cảnh thị trường trên Insights (#326, #327, #328): cấp bậc, vai trò, nơi làm việc, số năm kinh nghiệm của snapshot
mới nhất, trong một envelope. Không có tham số. Mọi tỷ trọng đã tính và đã qua `suppression_for` ở máy chủ
(`haido_api/market_overview.py`); web chỉ in, không cộng, không chia, không sắp xếp (AD-22). Đọc cùng nguồn với
`newcomer-roles` (biến `HAIDO_MARKET_SOURCE_NEWCOMER_ROLES`), vì hai phép cùng đọc ô toàn quốc của `stat_cells`.

```json
{
  "data": {
    "total_cell_id": "vn.all", "entry_cell_id": "vn.all.entry",
    "levels": ["intern", "fresher", "junior", "mid", "senior", "lead", "unknown"],
    "entry_levels": ["intern", "fresher", "junior"],
    "level_mix": [{ "code": "mid", "share": { "value": 0.2894, "kind": "level_share", "display": "shown", "cell_id": "vn.all" } }],
    "entry_share": { "value": 0.5678, "kind": "level_share", "display": "shown", "cell_id": "vn.all" },
    "big_cities_share": { "value": 0.86, "kind": "composition_share", "display": "shown", "cell_id": "big_cities.all" },
    "roles": [{ "role": "ai_ml", "cell_id": "vn.ai_ml", "entry_cell_id": "vn.ai_ml.entry",
                "share": { "…": "composition_share, ô vn.ai_ml" }, "entry_share": { "…": "level_share, ô vn.ai_ml" },
                "level_mix": ["…"], "places": [{ "code": "ha_noi", "share": { "…": "ô ha_noi.ai_ml" } }] }],
    "places": [{ "code": "other_provinces", "share": { "…": "ô other_provinces.all" } }],
    "years": [{ "code": "4-5", "share": { "…": "ô vn.all.years_4-5" } }]
  },
  "meta": { "…": "…", "cells": { "vn.all": { "n": 3586, "seniority_mix": { "…": "…" } }, "big_cities.all": { "n": 3083 } } }
}
```

| Con số | Đọc ở |
|---|---|
| Số tin IT đang mở, số tin theo cấp | `meta.cells[total_cell_id].n`, `.seniority_mix` |
| Tỷ lệ một cấp, tỷ lệ người mới (toàn thị trường hay của một vai trò) | `level_mix[].share`, `entry_share` |
| Tỷ trọng một vai trò, một nơi, một mốc số năm | `share.value`; số tin của phần đó ở `meta.cells[share.cell_id].n` |

- Tỷ trọng cấu phần (`composition_share`) trỏ tới ô của chính phần đó (tử số): dưới `min_sample` thì
  `low_sample_shown`, vẫn có giá trị. Tỷ lệ cấp bậc (`level_share`) trỏ tới ô của cả nhóm (mẫu số): dưới ngưỡng là
  `null_data`.
- `roles`: mọi vai trò của `config/rules.toml`; nhiều tin trước, cùng số tin thì theo mã; `other` luôn ở cuối.
  `places` của mỗi vai trò chỉ có Hà Nội và TP.HCM.
- `places`: Hà Nội, TP.HCM, Đà Nẵng, `other_provinces` (các tỉnh còn lại gộp), `remote`, `abroad`, `unknown`.
- `years`: mốc của `years_options` (`0`, `1`, `2`, `3`, `4-5`), `over_5`, `none` (tin không ghi). Các phần cộng
  lại bằng `n` toàn quốc.
- Ô `big_cities.all`, `other_provinces.all`, `vn.all.years_<mã>` là ô gộp của phép này, không có hàng riêng trong
  `stat_cells`.
- Fixture cho test web: `web/tests/fixtures/market-overview.json` (`tests/api/test_ad22_market_overview.py` kiểm khớp).

## `GET /api/v1/skill-roles?skill=<mã>`

Màn "kỹ năng này dùng ở vai trò nào" (#113, #166): mỗi vai trò một dòng, tỷ lệ tin entry-level (Intern, Fresher,
Junior) của vai trò có nhắc kỹ năng. Cấp bậc cố định là nhóm `entry`, không có tham số cấp. `skill` là mã trong
`GET /api/v1/skills` (snake_case, tối đa 40 ký tự).

```json
{
  "data": {
    "skill": { "code": "python", "name_en": "Python", "name_vi": "Python" },
    "level": "entry",
    "levels": ["intern", "fresher", "junior"],
    "mentioned": true,
    "rows": [
      { "role": "ai_ml",
        "share": { "value": 0.7764471057884231, "kind": "skill_rate", "display": "shown", "cell_id": "vn.ai_ml.entry" } },
      { "role": "game",
        "share": { "value": null, "kind": "skill_rate", "display": "null_data", "cell_id": "vn.game.entry" } }
    ]
  },
  "meta": { "…": "…",
    "cells": {
      "vn.ai_ml.entry": { "n": 501, "n_by_measure": { "skill_count": 501, "…": "…" }, "…": "…" },
      "vn.game.entry": { "n": 43, "n_by_measure": { "skill_count": 12, "…": "…" }, "…": "…" } } }
}
```

| Con số | Đọc ở |
|---|---|
| Tỷ lệ tin entry-level của vai trò có nhắc kỹ năng | `share.value`, chỉ khi `share.display = shown` |
| Cỡ mẫu của tỷ lệ (X trong "not enough data (X/30)") | `meta.cells[share.cell_id].n_by_measure.skill_count` |
| Số tin của ô entry-level (cùng số với `newcomer-roles`) | `meta.cells[share.cell_id].n` |
| Ngưỡng | `meta.thresholds.min_sample` |

- `share.kind = skill_rate`, `share.cell_id = vn.<role>.entry`. Vai trò có `skill_count` dưới `min_sample` thì
  `share.display = null_data`: ghi "not enough data (skill_count/min_sample)", kể cả khi `n` của ô từ `min_sample` trở lên
  (ví dụ `game`: n = 43, `skill_count` = 12). Số tin của ô và số tin đã quét kỹ năng là hai số khác nhau; một ô chỉ có một `n`.
- Vai trò đủ mẫu mà không tin nào nhắc kỹ năng có `share.value = 0`: hiện 0 và giữ trong danh sách.
- Mọi vai trò của `config/rules.toml` có mặt, kể cả vai trò không có tin nào (n = 0, `null_data`).
- `rows` đã theo thứ tự hiển thị: dòng có tỷ lệ trước, tỷ lệ giảm dần rồi theo mã vai trò; sau đó dòng `null_data`,
  `skill_count` giảm dần rồi theo mã vai trò (`Envelope` kiểm, nguồn thật cũng phải khớp). Web không sắp xếp lại.
- `data.level = entry` là mã nhóm cấp: dùng làm `level` khi mở `/ho-so-ky-nang?role=&level=` hay gọi `skill-rates`.
- `data.mentioned = false` khi không tin tuyển dụng hiện tại nào, ở cấp bậc nào, nhắc kỹ năng (AC 4 của #113), không
  chỉ entry-level: màn ghi rằng chưa tin nào nhắc kỹ năng này. Web không suy cờ này từ các dòng. `mentioned = true` mà
  mọi dòng hiện đều 0 là hợp lệ khi tin nhắc nằm ở cấp khác hoặc ở ô entry-level bị ẩn.
- `data.skill` gồm mã và tên song ngữ để màn ghi kỹ năng đã dùng. Tên công nghệ được có chữ số (DEC-6, AD-8 miễn tên
  công nghệ); mọi chuỗi khác của `data` không có chữ số nào: số chỉ nằm trong `Stat` và `meta`.
- Lỗi: mã đúng định dạng nhưng không có trong bộ từ vựng là 404 `unknown_skill`; thiếu `skill` hoặc sai định dạng là 422
  `invalid_query`; nguồn chưa có số cho một kỹ năng hợp lệ là 404 `unknown_cell`: nguồn `stat` trả 404 không có ngày khi
  chưa có snapshot đọc được, và 404 kèm ngày snapshot khi snapshot không có hàng nào của kỹ năng đó. Production đặt
  `HAIDO_MARKET_SOURCE_SKILL_ROLES=stat` (số thật từ #168, không bao giờ số giả).
- Kiểu TypeScript, hàm gọi API và hàm tra cỡ mẫu `rowN`: `web/lib/skill-roles.ts`. Fixture cho test web:
  `web/tests/fixtures/skill-roles-{python,figma,abap,sap,machine_learning}.json`.
- Số thật (#168), nguồn `stat`: snapshot là `published` hoặc `partial` mới nhất có nguồn và có hàng `stat_skill_rates`.
  `share.value` là `rate` của hàng entry (`= n_with / n_scanned`); `n_scanned` thành `n_by_measure.skill_count` của
  `meta.cells[vn.<role>.entry]` (`n` giữ là số tin của ô, cũng là `n` mà `newcomer-roles` ghi) để `Envelope` kiểm được
  `display`. `mentioned = n_with > 0` của hàng ô mọi vai trò, mọi cấp của `stat_skill_rates` (`role = all`, `seniority = all`,
  `years = any`, `scope = vn`; `cell_id` `vn.all`), không cộng các ô entry.

## `GET /api/v1/learning-path?role=<mã>&level=<cấp>&have=<mã,mã,...>`

Lộ trình học đã xếp theo chặng (#121, #122). `level` như `city-shares`, mặc định `entry`. `have` tùy chọn: mã kỹ năng
người dùng đã có, ngăn bằng dấu phẩy, tối đa 200 mã (AD-22), mỗi mã snake_case tối đa 40 ký tự; mã trùng chỉ tính một
lần; mã sai định dạng, phần tử rỗng hoặc quá 200 mã là 422 `invalid_query`; `have=` rỗng như không gửi. Trần 200 đếm
trên số mã gửi lên, trước khi loại trùng (150 mã khác nhau cộng 51 mã lặp là 201 mã, 422). Chỉ đọc một tham số `have`
(lặp lại `have` thì lấy cái cuối). Hồ sơ 200 mã dài có thể làm URL khoảng 8 KB.

```json
{
  "data": {
    "role": "backend", "level": "entry", "status": "ready",
    "cell_id": "vn.backend.entry", "entry_cell_id": "vn.backend.entry",
    "stages": [
      { "stage": 1, "skills": [
        { "skill": "java",
          "rate": { "value": 0.6538461538461539, "kind": "skill_rate", "display": "shown", "cell_id": "vn.backend.entry" },
          "group": "core", "foundation_for": [], "prerequisite_for": ["rest_api", "spring_boot", "unit_testing"],
          "have": false, "blurb": "…", "resource": { "title": "Học Java (dev.java)", "url": "https://dev.java/learn/" } } ] }
    ],
    "current_stage": 1, "have_on_path": 0, "path_size": 14, "have_ignored": []
  },
  "meta": { "…": "…", "cells": { "vn.backend.entry": { "n": 52, "…": "…" } } }
}
```

- Lộ trình đã xếp sẵn (AD-7). **Chặng là thuộc tính của từng kỹ năng**: `have` không đổi chặng hay thứ tự, chỉ đổi cờ
  `have`, `have_on_path`, `current_stage`, `have_ignored`. Web không sắp xếp, không đếm (AD-22).
- Thứ tự trong một chặng (FR-22): nhóm (`core` trước `common`, rồi `company_specific`, rồi bị ẩn), tỷ lệ giảm dần, mã A–Z.
  Không kỹ năng nào ở chặng trước hoặc cùng chặng với kỹ năng nó cần (`prerequisite_for` luôn ở chặng sau).
- Lộ trình **giữ kỹ năng đã có** (`have = true`) và tính vào `path_size` (khác chữ "không nằm trong lộ trình" của
  FR-20/FR-22): để hiện "N of M" (#121 AC3, #220, FR-24); web tô kỹ năng đã có chứ không ẩn.
- `rate`: `skill_rate`, `cell_id = data.cell_id`, bằng đúng số của `skill-rates` cùng vai trò, cấp, ô. Khi `cell_id` quay
  về ô rộng hơn, `meta.cells[cell_id].fallback_label` giải thích (FR-19). Quay về chỉ đi trong vai trò (vai trò × cấp,
  rồi vai trò × mọi cấp); `cell_id` không bao giờ là ô của vai trò khác. Không ô nào đạt 30 tin thì mọi `rate` là
  `null_data`, `group = null`, lộ trình vẫn `ready` (đã rà soát), và `cell_id` là ô cuối đã thử trong vai trò.
  Ở bước cuối (vai trò × mọi cấp) khi người chọn cấp entry, nhãn ghi tỷ lệ tin Mid trở lên (FR-19).
- `entry_cell_id`: ô entry-level của vai trò; `meta.cells[entry_cell_id].n` là số tin entry-level (#221), có cả khi `cell_id` quay về.
- `foundation_for` không rỗng là kỹ năng nền tảng (FR-20): ghi "Kỹ năng nền tảng (cần cho X)". Gồm các kỹ năng `core`
  hoặc `common` trên lộ trình có kỹ năng này là tổ tiên, **bắc cầu** (cháu cũng tính), xếp A–Z; `prerequisite_for` thì
  chỉ cạnh trực tiếp. Chỉ kỹ năng nền tảng mới được `company_specific`. Khi nhóm bị ẩn (`null_data`), `foundation_for`
  rỗng vì chưa biết nhóm của ai.
- `blurb`: lời dẫn viết sẵn, không có chữ số ngoài tên công nghệ, không `%` (FR-23), không nói bao nhiêu tin đòi kỹ
  năng. Quy tắc kiểm nằm ở `haido_core/vocab/prepared_text.py` (cổng #138 dùng lại). `resource`: một link `https://` miễn phí.
- `have_on_path`/`path_size` là "N of M skills on this path". `current_stage` là chặng đầu còn kỹ năng `have = false`,
  `null` nếu đã có hết hoặc `not_ready`. `have_ignored`: mã hợp lệ không có trên lộ trình, A–Z.
- `status = not_ready` (200, không phải lỗi): không có chặng, `cell_id = null`, `current_stage = null`, hai số đếm bằng 0;
  `meta.cells` vẫn có `entry_cell_id`. Giao diện gợi ý hồ sơ kỹ năng (`skill-rates`).
- `stage`, `current_stage`, `have_on_path`, `path_size` là số thứ tự và số đếm trên chính mã kỹ năng của người dùng,
  đánh dấu `Ordinal` trong `haido_core/domain/envelope.py` (xem quy tắc 1): không phải số liệu thị trường nên không
  bọc `Stat`. Số tin, tỷ lệ, tỷ trọng và n vẫn là `Stat` hoặc ở `meta.cells`.
- Kiểu TypeScript: `web/lib/learning-path.ts`. Fixture: `web/tests/fixtures/learning-path-*.json`.
- Mọi mã kỹ năng giả (cả ở `skill-rates`) là snake_case và có trong `haido_core/vocab/skills_seed.json`.

## Hình lỗi

Mọi lỗi, kể cả lỗi tham số, có cùng một hình. Không bao giờ có `data` trong response lỗi.

```json
{ "error": { "code": "invalid_query", "message": "Truy vấn không hợp lệ: thiếu tham số level.", "snapshot_date": null } }
```

| HTTP | `code` | Khi nào |
|---|---|---|
| 404 | `unknown_cell` | Không có ô cho tham số đã chọn. `snapshot_date` là snapshot đã tìm |
| 404 | `unknown_skill` | `skill-roles`: mã kỹ năng đúng định dạng nhưng không có trong bộ từ vựng. `snapshot_date` luôn `null` |
| 422 | `invalid_query` | Thiếu tham số, hoặc mã sai định dạng (chỉ `a-z`, `0-9`, `_`, tối đa 64 ký tự) |
| 404 | `not_found` | Sai đường dẫn |
| 405 | `method_not_allowed` | Sai phương thức; các route số liệu chỉ nhận `GET` |
| khác 4xx/5xx | `http_error` | Lỗi HTTP khác của tầng định tuyến; mã HTTP giữ nguyên |
| 411 | `length_required` | Tải CV thiếu `Content-Length`, nên chưa biết cỡ tệp trước khi đọc |
| 413 | `cv_too_large` | Tệp CV lớn hơn `cv_max_bytes`, hoặc `Content-Length` vượt mức cho phép |
| 415 | `cv_unsupported_type` | Yêu cầu không phải `multipart/form-data` có boundary, hoặc loại tệp CV không được nhận, hoặc byte đầu không khớp định dạng đã khai |
| 400 | `cv_invalid_upload` | Tải CV sai cấu trúc: chưa chọn tệp, thiếu hoặc thừa tệp `cv`, thân bị cắt, `Content-Length` không hợp lệ. Mọi lỗi tải CV kèm `Connection: close` |
| 500 | `invalid_response` | Máy chủ tạo ra dữ liệu sai hợp đồng này, ở response hoặc trong lúc dựng nó |
| 500 | `internal_error` | Lỗi khác của máy chủ |

`message` là tiếng Việt, hiện được cho người dùng, và không lặp lại giá trị người dùng gửi lên.
Rẽ nhánh theo `code`, không theo `message`.

`snapshot_date` chỉ có giá trị ở `unknown_cell`. Mọi mã còn lại (`unknown_skill`, `invalid_query`, `not_found`,
`method_not_allowed`, `length_required`, `cv_too_large`, `cv_unsupported_type`, `cv_invalid_upload`, `http_error`, `invalid_response`, `internal_error`) luôn trả `snapshot_date = null`.

## Dữ liệu giả hiện có

Fixture: `haido_api/fixtures/fake_market.json`, snapshot `2026-11-03`, ngưỡng `min_sample = 30`.

| Truy vấn | Trường hợp |
|---|---|
| `city-shares?role=ai_ml` | Hà Nội n = 412 `shown`; Đà Nẵng n = 21 `low_sample_shown`; có `other`, `unknown` |
| `city-shares?role=backend` | Mọi thành phố dưới ngưỡng trừ Hà Nội và TP.HCM |
| `city-shares?role=all` | Mọi vai trò; Đà Nẵng n = 64 |
| `skill-rates?role=ai_ml&level=entry` | Ô đủ mẫu, có cả ba nhóm kỹ năng |
| `skill-rates?role=java_backend&level=entry` | Quay về ô Backend · Entry (n = 52), có `fallback_label` |
| `skill-rates?role=backend&level=entry` | Cùng ô trên, chọn thẳng nên `fallback_label = null` |
| `skill-rates?role=backend&level=intern` | Quay về `vn.backend` (n = 157), có `fallback_label` ghi tỷ lệ Mid trở lên |
| `skill-rates?role=data_engineer&level=entry` | `vn.data_engineer` (n = 22, dưới 30): mọi `rate` là `null_data`, `group = null`, có `fallback_label` |
| `skill-rates?role=data_engineer&level=senior` | n = 18: mọi `rate` là `null_data`, `group = null` |
| `city-shares?role=khong_ton_tai` | 404 `unknown_cell` |
| `skill-rates?role=data_engineer` | 422 `invalid_query` |
| `learning-path?role=backend&level=entry` | Sẵn sàng: 3 chặng, 14 kỹ năng, có kỹ năng nền tảng (`linux`), ô n = 52 |
| `learning-path?role=backend&level=intern` | Sẵn sàng qua `vn.backend` (vai trò × mọi cấp, n = 157; ô Intern n = 13), mọi `rate` có số; `fallback_label` ghi 105 trên 157 tin (67%) là Mid trở lên |
| `learning-path?role=data_engineer&level=entry` | Sẵn sàng nhưng mọi `rate` là `null_data`, `group = null`: ô entry n = 4 và `vn.data_engineer` n = 22 đều dưới 30; `cell_id = vn.data_engineer`, `fallback_label` giải thích |
| `learning-path?role=qa` | 200 `not_ready` (mọi vai trò khác của config); `ai_ml&level=entry` cũng `not_ready` nhưng có `skill-rates` để mở hồ sơ |
| `learning-path?role=backend&level=senior` | 404 `unknown_cell` (bản giả chỉ có ô `entry` và `intern` của backend, như `skill-rates`); `data_engineer&level=senior` cũng 404 vì ô đó không phủ hết kỹ năng của lộ trình |
| `skill-roles?skill=python` | 17 vai trò: 11 đủ mẫu, trong đó `mobile` đủ mẫu (n = 30) và 0 tin nhắc; `embedded`, `data_scientist`, `data_engineer`, `devops`, `ui_ux`, `other` dưới 30 (`null_data`); `ai_ml` dẫn đầu |
| `skill-roles?skill=figma` | Xếp hạng khác `python` (`frontend` dẫn đầu); `ui_ux` có tỷ lệ thật cao nhất nhưng n = 21 nên `null_data`; nhiều vai trò đủ mẫu bằng 0 (xếp theo mã) |
| `skill-roles?skill=abap` | Mã hợp lệ mà không tin nào nhắc: `mentioned = false`, mọi dòng đủ mẫu bằng 0 |
| `skill-roles?skill=java` | 404 `unknown_cell` (mã trong bộ từ vựng nhưng bản giả chưa có số); `skill=khong_co_ky_nang` là 404 `unknown_skill` |
| `newcomer-roles` | 17 vai trò: 12 đủ mẫu; `devops` đủ mẫu, 0 tin entry-level; `embedded`, `data_scientist`, `data_engineer` dưới 30; `other` không có tin |
| `market-overview` | Cùng ô `vn.<role>` với `newcomer-roles`; Hà Nội/TP.HCM của tám vai trò chưa có ô thành phố và các mốc số năm lấy từ mục `market_overview` của fixture |

## Chạy và chọn nguồn

```bash
uv sync
uv run uvicorn haido_api.main:app        # http://localhost:8000/docs
```

Mỗi phép chọn nguồn riêng qua biến môi trường, mặc định `fake`. Production không bao giờ phục vụ bản giả: mọi biến dưới đây phải là `stat` trong `deploy/compose.prod.yml`, và `tests/deploy/test_gh309_prod_khong_doc_du_lieu_gia.py` đỏ khi thiếu một biến (#309). `compose.local.yml` giữ `fake`.

| Biến | Route | Bản thật |
|---|---|---|
| `HAIDO_MARKET_SOURCE_CITY_SHARES` | `/api/v1/city-shares` | `stat` (#93); `deploy/compose.prod.yml` đặt `stat`, `compose.local.yml` giữ `fake` |
| `HAIDO_MARKET_SOURCE_SKILL_RATES` | `/api/v1/skill-rates` | `stat` (#151): `stat_skill_rates` của snapshot đọc được mới nhất, quay về qua phép 2 (#106); `deploy/compose.prod.yml` đặt `stat` |
| `HAIDO_MARKET_SOURCE_NEWCOMER_ROLES` | `/api/v1/newcomer-roles`, `/api/v1/market-overview` (#327) | `stat` (#145, #146): ô `vn.<role>.entry` và `vn.<role>` của snapshot đã công bố mới nhất có hàng cấp `entry`; `deploy/compose.prod.yml` đặt `stat`, `compose.local.yml` giữ `fake` |
| `HAIDO_MARKET_SOURCE_LEARNING_PATH` | `/api/v1/learning-path` | #216; `stat` hiện trả 404 `unknown_cell`. `deploy/compose.prod.yml` đặt `stat` (#309) |
| `HAIDO_MARKET_SOURCE_SKILL_ROLES` | `/api/v1/skill-roles` | `stat` (#168): `stat_skill_rates` hàng entry của kỹ năng và `stat_cells` ô `vn.<role>.entry` của snapshot đọc được mới nhất; `deploy/compose.prod.yml` đặt `stat` (#166) |

Tên nguồn không có trong `IMPLEMENTATIONS` (`haido_api/routes/market.py`) thì app không khởi động.
Thêm bản thật: cài `MarketReadModel` (`haido_api/market_source.py`), thêm một mục vào `IMPLEMENTATIONS`,
rồi đặt biến môi trường. Route và schema không đổi.

## Sinh lại `openapi.json`

`tests/api/test_ad17_routes.py` so file đã commit với `app.openapi()` và đỏ khi hai bên lệch. Sau khi
đổi schema, sinh lại rồi commit:

```bash
HAIDO_UPDATE_OPENAPI=1 uv run pytest tests/api -q              # bash
```

```powershell
$env:HAIDO_UPDATE_OPENAPI = "1"; uv run pytest tests/api -q; Remove-Item Env:HAIDO_UPDATE_OPENAPI   # PowerShell
```
