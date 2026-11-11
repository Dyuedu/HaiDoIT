# Data model: Hình response của lộ trình học và dữ liệu giả

Không thêm bảng, cột hay revision Alembic (không đổi ở cả hai đợt). Bản thật (#216) đọc `stat_*` và đồ thị đã rà soát (#213) sau.

## Response `GET /api/v1/learning-path`

```json
{
  "data": {
    "role": "backend", "level": "entry", "status": "ready",
    "cell_id": "vn.backend.entry", "entry_cell_id": "vn.backend.entry",
    "stages": [
      { "stage": 1, "skills": [
        { "skill": "java",
          "rate": { "value": 0.6538, "kind": "skill_rate", "display": "shown", "cell_id": "vn.backend.entry" },
          "group": "core", "foundation_for": [], "prerequisite_for": ["spring_boot"],
          "have": false, "blurb": "…", "resource": { "title": "…", "url": "https://…" } } ] }
    ],
    "current_stage": 1, "have_on_path": 0, "path_size": 13, "have_ignored": []
  },
  "meta": { "cells": { "vn.backend.entry": { "n": 52, "…": "…" } }, "…": "…" }
}
```

| Con số | Đọc ở |
|---|---|
| Tỷ lệ của kỹ năng | `rate.value` |
| Số tin entry-level của vai trò | `meta.cells[entry_cell_id].n` |
| Tỷ lệ Mid trở lên khi quay về vai trò × mọi cấp | chữ trong `meta.cells[cell_id].fallback_label`, tính từ `seniority_mix` của ô |
| "N of M skills on this path" | `have_on_path`, `path_size` |
| Chặng cần học tiếp | `current_stage` |

## Fixture

- `haido_api/fixtures/fake_learning_path.json` (mới): `roles.<vai trò>` có `skills[]` với `skill`, `requires`, `foundation`, `blurb`, `resource`. Chặng suy ra từ `requires` (1 + chặng cao nhất của kỹ năng cần); `prerequisite_for` và `foundation_for` suy ra từ `requires`.
- Ngoại lệ AD-17 (đợt 2): `stage`, `current_stage`, `have_on_path`, `path_size` là `Ordinal` (vị trí và số đếm trên mã kỹ năng của người dùng, AD-22), không phải số liệu thị trường nên không bọc `Stat`. Khóa bằng `tests/api/test_ad17_ordinal_allowlist.py`.
- `foundation_for` (đợt 2): các kỹ năng `core`/`common` trên lộ trình có nút này là tổ tiên bắc cầu qua `prerequisite_for` (dữ liệu suy ra; `prerequisite_for` chỉ cạnh trực tiếp); rỗng khi nhóm bị ẩn. Validator: mỗi mã đi tới được qua `prerequisite_for` và thuộc `core` hoặc `common`.
- `haido_api/fixtures/fake_market.json` (đợt 2): `data_engineer/entry` đổi sang `cell_id = vn.data_engineer`, mọi hàng `rate = null`, `group = null`, có `fallback_label`; thêm `backend/intern` (`cell_id = vn.backend`, 15 hàng, số giả theo 157 tin, `fallback_label` ghi 105 trên 157 tin (67%) là Mid trở lên). Không thêm ô: `vn.backend` và `vn.data_engineer` đã có.
- `haido_api/fixtures/fake_learning_path.json` (đợt 2): viết lại lời dẫn có nói tần suất; đổi link tài nguyên (JUnit, Linux, REST, ETL, kho dữ liệu, AWS, Node.js, Spring) sang link đã kiểm trả 200 ở đích cuối, trung lập hơn.
- `haido_api/fixtures/fake_market.json` (đợt 1): mã `skill_rates` đổi sang snake_case; thêm hàng `backend/entry` (`linux`, `postgresql`, `mysql`, `unit_testing`, `ci_cd`, `redis`); thêm `data_engineer/entry` (ô `vn.all.entry`, có `fallback_label`); `data_engineer/senior` thay `airflow`, `spark`; `ai_ml/entry` thay `pandas`, `spark`.
