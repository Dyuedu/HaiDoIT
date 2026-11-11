# Data model: Hình response của màn người mới và dữ liệu giả

Không thêm bảng, không thêm cột, không thêm revision Alembic. Bản thật (#145) đọc `seniority_mix` của ô toàn quốc trong `stat_cells` sẵn có.

## Response `GET /api/v1/newcomer-roles`

```json
{
  "data": {
    "levels": ["intern", "fresher", "junior"],
    "rows": [
      { "role": "ai_ml", "total_cell_id": "vn.ai_ml", "entry_cell_id": "vn.ai_ml.entry",
        "share": { "value": 0.5712656784492588, "kind": "level_share", "display": "shown", "cell_id": "vn.ai_ml" } }
    ]
  },
  "meta": { "cells": { "vn.ai_ml": { "n": 877, "…": "…" }, "vn.ai_ml.entry": { "n": 501, "…": "…" } }, "…": "…" }
}
```

| Con số | Đọc ở |
|---|---|
| Số tin entry-level | `meta.cells[entry_cell_id].n` |
| Tỷ lệ | `share.value` (null khi `display = null_data`) |
| n của vai trò | `meta.cells[total_cell_id].n` |

## `MeasureKind`

Thêm `level_share`: tỷ lệ 0–1; dưới `min_sample` thì `null_data`.

## Fixture `haido_api/fixtures/fake_market.json`

Thêm mục:

```json
"newcomer_roles": {
  "levels": ["intern", "fresher", "junior"],
  "rows": [ { "role": "ai_ml", "total_cell_id": "vn.ai_ml", "entry_cell_id": "vn.ai_ml.entry", "share": 0.57 } ]
}
```

và các ô `vn.<role>`, `vn.<role>.entry` còn thiếu cho đủ 10 vai trò của `config/rules.toml`.

| Vai trò | n | Entry-level | Trường hợp |
|---|---|---|---|
| ai_ml | 877 | 501 | đủ mẫu |
| frontend | 240 | 140 | đủ mẫu |
| qa | 130 | 82 | đủ mẫu |
| data_analyst | 96 | 54 | đủ mẫu |
| backend | 157 | 52 | đủ mẫu |
| mobile | 75 | 30 | đủ mẫu |
| devops | 48 | 0 | đủ mẫu, 0 tin entry-level |
| embedded | 12 | 6 | dưới 30 |
| data_engineer | 22 | 4 | dưới 30 |
| other | 0 | 0 | không có tin |
