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
   luôn trạng thái hiển thị, nên giao diện chỉ cần một component cho mọi con số.
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
| `kind` | `composition_share` · `skill_rate` · `percentile` | Loại thước đo |
| `display` | `shown` · `low_sample_shown` · `null_data` | Cách hiển thị, xem bảng dưới |
| `cell_id` | chuỗi | Mã ô, opaque. Chỉ dùng để tra `meta.cells` |

| `display` | `value` | Giao diện làm gì |
|---|---|---|
| `shown` | có | Hiện bình thường |
| `low_sample_shown` | có | Hiện mờ, kèm nhãn cỡ mẫu nhỏ với `n` của ô (FR-33). Chỉ xảy ra với `composition_share` |
| `null_data` | `null` | Ghi "chưa đủ dữ liệu". Tỷ lệ kỹ năng và phân vị dưới ngưỡng luôn ở trạng thái này |

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
| `n_by_measure` | Số tin có giá trị của từng thước đo: `skill_count`, `experience_years`, `salary` |
| `insufficient_by_measure` | `true` khi thước đo đó dưới ngưỡng. Phân vị lương xét `n_by_measure.salary`, không xét `n` |

Mã vai trò, cấp bậc, thành phố, nhóm kỹ năng hiện là chuỗi tạm (`ai_ml`, `entry`, `ha_noi`, `core`…);
#16 chốt mã thật. Chuỗi hiển thị tiếng Việt sẽ đến từ bảng tra, không suy từ mã.

## `GET /api/v1/city-shares?role=<mã>`

Tỷ trọng từng thành phố trong số tin của vai trò trên toàn quốc (FR-33). `role=all` là mọi vai trò.

```json
{
  "data": {
    "role": "ai_ml",
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
- `total_cell_id` là ô toàn quốc của vai trò, mẫu số của mọi tỷ trọng.
- Thành phố dưới ngưỡng vẫn có `value`, kèm `low_sample_shown`: vẽ cột mờ, không ẩn cột.

## `GET /api/v1/skill-rates?role=<mã>&level=<mã>`

Tỷ lệ xuất hiện của từng kỹ năng trong ô vai trò × cấp bậc. Cả hai tham số bắt buộc.

```json
{
  "data": {
    "role": "java_backend", "level": "entry", "cell_id": "vn.backend.entry",
    "rows": [
      { "skill": "java",
        "rate": { "value": 0.6538461538461539, "kind": "skill_rate", "display": "shown", "cell_id": "vn.backend.entry" },
        "group": "core" }
    ]
  },
  "meta": { "…": "…",
    "cells": {
      "vn.backend.entry": { "n": 52,
        "fallback_label": "Java Backend · Entry chỉ có 26 tin, chưa đủ để tính riêng, nên số dưới đây lấy từ ô rộng hơn Backend · Entry.",
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

## Hình lỗi

Mọi lỗi, kể cả lỗi tham số, có cùng một hình. Không bao giờ có `data` trong response lỗi.

```json
{ "error": { "code": "invalid_query", "message": "Truy vấn không hợp lệ: thiếu tham số level.", "snapshot_date": null } }
```

| HTTP | `code` | Khi nào |
|---|---|---|
| 404 | `unknown_cell` | Không có ô cho tham số đã chọn. `snapshot_date` là snapshot đã tìm |
| 422 | `invalid_query` | Thiếu tham số, hoặc mã sai định dạng (chỉ `a-z`, `0-9`, `_`, tối đa 64 ký tự) |
| 404 | `not_found` | Sai đường dẫn |
| 405 | `method_not_allowed` | Sai phương thức; hai route này chỉ nhận `GET` |
| khác 4xx/5xx | `http_error` | Lỗi HTTP khác của tầng định tuyến; mã HTTP giữ nguyên |
| 500 | `invalid_response` | Máy chủ tạo ra dữ liệu sai hợp đồng này, ở response hoặc trong lúc dựng nó |
| 500 | `internal_error` | Lỗi khác của máy chủ |

`message` là tiếng Việt, hiện được cho người dùng, và không lặp lại giá trị người dùng gửi lên.
Rẽ nhánh theo `code`, không theo `message`.

`snapshot_date` chỉ có giá trị ở `unknown_cell`. Mọi mã còn lại (`invalid_query`, `not_found`,
`method_not_allowed`, `http_error`, `invalid_response`, `internal_error`) luôn trả `snapshot_date = null`.

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
| `skill-rates?role=data_engineer&level=senior` | n = 18: mọi `rate` là `null_data`, `group = null` |
| `city-shares?role=khong_ton_tai` | 404 `unknown_cell` |
| `skill-rates?role=data_engineer` | 422 `invalid_query` |

## Chạy và chọn nguồn

```bash
uv sync
uv run uvicorn haido_api.main:app        # http://localhost:8000/docs
```

Mỗi phép chọn nguồn riêng qua biến môi trường, mặc định `fake`:

| Biến | Route | Bản thật |
|---|---|---|
| `HAIDO_MARKET_SOURCE_CITY_SHARES` | `/api/v1/city-shares` | `stat` (#93); `deploy/compose.prod.yml` đặt `stat`, `compose.local.yml` giữ `fake` |
| `HAIDO_MARKET_SOURCE_SKILL_RATES` | `/api/v1/skill-rates` | #27 |

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
