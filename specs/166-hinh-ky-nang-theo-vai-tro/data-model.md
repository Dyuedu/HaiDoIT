# Data model: Hình response của một kỹ năng qua các vai trò và dữ liệu giả

Không thêm bảng, không thêm cột, không thêm revision Alembic (đợt 1 và đợt 2 đều không đổi). Bản thật (#168) đọc `stat_skill_rates` (migration 0009, #101) theo khóa `(snapshot, role, branch=all, seniority=entry, years=any, scope=vn, skill)`, chỉ mục `ix_stat_skill_rates_snapshot_skill`; thêm hàng ô mọi vai trò, mọi cấp (`role=all`, `seniority=all`, `years=any`, `scope=vn`) để tính `mentioned`.

## Response `GET /api/v1/skill-roles?skill=python`

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
  "meta": { "cells": {
    "vn.ai_ml.entry": { "n": 501, "n_by_measure": { "skill_count": 501, "…": "…" }, "…": "…" },
    "vn.game.entry": { "n": 43, "n_by_measure": { "skill_count": 12, "…": "…" }, "…": "…" } }, "…": "…" }
}
```

| Con số | Đọc ở |
|---|---|
| Tỷ lệ | `share.value` (null khi `display = null_data`) |
| Cỡ mẫu của tỷ lệ | `meta.cells[share.cell_id].n_by_measure.skill_count` |
| Số tin của ô entry (cùng số với `newcomer-roles`) | `meta.cells[share.cell_id].n` |
| Ngưỡng | `meta.thresholds.min_sample` |

Ánh xạ sang dữ liệu thật (#168): `share.value = n_with / n_scanned` của hàng `stat_skill_rates`; `n_by_measure.skill_count = n_scanned` (nhỏ hơn hoặc bằng `n`); `n` giữ là số tin của ô; `mentioned = n_with > 0` của hàng ô `vn.all` (xem `spec.md`, quyết định 2).

## Fixture `haido_api/fixtures/fake_market.json`

Đợt 2 đổi hình mục `skill_roles` thành `skill_roles[mã kỹ năng] = { "entry": { vai trò: số tin entry-level nhắc kỹ năng }, "mentions_all_levels": số tin ở mọi cấp nhắc kỹ năng }`. Số nhắc là số nguyên, không vượt `skill_count` của ô `vn.<role>.entry`; `mentions_all_levels` không nhỏ hơn tổng số nhắc entry-level. Không thêm ô mới; đổi một số trong ô cũ: `cells["vn.game.entry"].n_by_measure.skill_count` từ 43 xuống 12 (n giữ 43), để có ca đủ tin mà ít tin được quét kỹ năng. Ô này cũng đổi `skill-rates` và `newcomer-roles` giả như sau: `skill-rates` của `game` / `entry` thành `null_data` (cỡ mẫu 12); `newcomer-roles` chỉ đổi số `skill_count` trong `meta.cells` (`web/tests/fixtures/newcomer-roles.json`), `share` theo `n` nên không đổi.

| Kỹ năng | Trường hợp |
|---|---|
| `python` | `ai_ml` 389/501 dẫn đầu; `mobile` 0/30 (đủ mẫu, bằng 0); `embedded`, `data_scientist`, `data_engineer`, `devops`, `ui_ux`, `other` dưới 30 (`null_data`); `game` n = 43 nhưng quét 12 (`null_data`, số nhắc 5 bị ẩn) |
| `figma` | `frontend` 33/140 dẫn đầu; `ui_ux` 19/21 là tỷ lệ cao nhất nhưng bị ẩn; nhiều vai trò đủ mẫu bằng 0 (hòa xếp theo mã) |
| `abap` | mọi vai trò 0, `mentions_all_levels` = 0: `mentioned = false` |
| `sap` | mọi vai trò 0 ở entry-level, `mentions_all_levels` = 87: `mentioned = true`, mọi dòng 0 hoặc ẩn |
| `machine_learning` | `ai_ml` dẫn đầu; tên tiếng Việt khác tiếng Anh (`Học máy`) để kiểm nhãn song ngữ |
