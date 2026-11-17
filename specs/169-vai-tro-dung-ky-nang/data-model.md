# Data model: Vai trò nào dùng một kỹ năng

Không đổi bảng, cột, revision Alembic hay hình API: màn đọc `GET /api/v1/skill-roles?skill=` theo hình của #166.

Trình duyệt: đọc `haido:profile.skills` (qua `web/lib/profile-store.ts`, #206) để gợi ý kỹ năng đã có; không ghi gì. URL: `?skill=<mã>`.

| Chữ trên màn | Lấy từ |
|---|---|
| Tên kỹ năng đã dùng | `data.skill.name_vi`, `data.skill.name_en` |
| Tên vai trò | `roleLabel(row.role)` |
| Tỷ lệ | `row.share.value` khi `display = shown` |
| "n = …" và X của "chưa đủ dữ liệu (X/30)" | `meta.cells[row.share.cell_id].n_by_measure.skill_count` (`rowN`) |
| 30 | `meta.thresholds.min_sample` |
| Liên kết | `/ho-so-ky-nang?role=<row.role>&level=<data.level>` |
| Ngày, nguồn, lưu ý | `meta.snapshot_date`, `meta.sources`, `meta.sources_failed`, `meta.coverage_notes` |
