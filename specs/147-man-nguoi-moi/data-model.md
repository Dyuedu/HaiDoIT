# Data model: Màn người mới

Không đổi bảng, cột hay revision Alembic (head vẫn `0008_haido_fact_city`). Không đổi API: màn đọc `GET /api/v1/newcomer-roles` theo hình của #144.

Trình duyệt không lưu gì (không `localStorage`).

| Chữ trên màn | Lấy từ |
|---|---|
| Tên vai trò | `roleLabel(row.role)` (`web/lib/labels.ts`) |
| "N tin cho người mới" | `meta.cells[row.entry_cell_id].n` |
| Tỷ lệ | `row.share.value` khi `display = shown` |
| "chưa đủ dữ liệu (n/ngưỡng)" | `meta.cells[row.total_cell_id].n`, `meta.thresholds.min_sample` |
| "n = …" | `meta.cells[row.total_cell_id].n` |
| Ngày, nguồn, lưu ý | `meta.snapshot_date`, `meta.sources`, `meta.sources_failed`, `meta.coverage_notes` |
