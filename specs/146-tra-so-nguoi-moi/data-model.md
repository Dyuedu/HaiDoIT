# Data model: Trả số người mới

Không đổi bảng, không đổi cột, không thêm revision Alembic (head vẫn `0008_haido_fact_city`). Hình response giữ nguyên như `specs/144-hinh-nguoi-moi/data-model.md`; `docs/api/openapi.json` không đổi.

| Con số | Nguồn |
|---|---|
| Số tin entry-level | `stat_cells.n`, `scope = vn`, `seniority = entry` (#145) → `meta.cells["vn.<role>.entry"].n` |
| n của vai trò | `stat_cells.n`, `scope = vn`, `seniority = all` → `meta.cells["vn.<role>"].n` |
| Tỷ lệ | entry / n, `null` khi `null_data` → `rows[].share` |
| Ngày, trạng thái | `snapshots` |
| Nguồn | `stat_sources` |

Cấu hình triển khai: `deploy/compose.prod.yml` thêm `HAIDO_MARKET_SOURCE_NEWCOMER_ROLES: stat`.
