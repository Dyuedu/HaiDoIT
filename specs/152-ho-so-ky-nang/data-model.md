# Data model: Hồ sơ kỹ năng

Không đổi bảng, cột hay revision Alembic. Hình API `skill-rates` đổi ở #149 (xem `specs/149-skill-rate-gia-vai-tro-cap/data-model.md`).

Trình duyệt: đọc và ghi `haido:profile` qua `web/lib/haido-keys.ts` (#205, #206). Không thêm khóa.

| Chữ trên màn | Lấy từ |
|---|---|
| Tên kỹ năng | `name_vi` của `GET /api/v1/skills`; chưa tải được thì mã |
| Tỷ lệ | `row.rate.value` khi `display = shown` |
| Nhóm | `row.group` → "Cốt lõi", "Thường gặp", "Riêng của công ty" |
| "chưa đủ dữ liệu" | `row.rate.display = null_data` |
| Tick | mã có trong `profile.skills` |
| "3/6 kỹ năng cốt lõi bạn đã có" | `data.have_core`, `data.core_size` (API đếm) |
| Câu quay về, n | `meta.cells[data.cell_id].fallback_label`, `.n` |
| Ngày, nguồn, lưu ý | `meta.snapshot_date`, `meta.sources`, `meta.sources_failed`, `meta.coverage_notes` |
