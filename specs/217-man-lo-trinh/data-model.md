# Data model: Màn lộ trình học

Không đổi bảng, cột, revision Alembic hay hình API. Không thêm khóa trình duyệt: đọc và ghi `haido:profile` qua `profile-store.ts`.

| Chữ trên màn | Lấy từ |
|---|---|
| Chặng, thứ tự kỹ năng | `data.stages` |
| "Đang học", "Đã xong", khung "Học tiếp" | `data.current_stage`; kỹ năng đã tick trong hồ sơ bị lọc khỏi khung |
| "3/14 kỹ năng trên lộ trình bạn đã có" | `data.have_on_path`, `data.path_size` |
| Tên kỹ năng | `GET /api/v1/skills`; chưa tải được thì mã |
| Tỷ lệ, nhóm | `rate`, `group`, `foundation_for` |
| "Học xong thì học được", "Cần học trước" | `prerequisite_for` và chiều ngược của nó |
| Lời dẫn, tài liệu | `blurb`, `resource` |
| Câu quay về, số tin | `meta.cells[data.cell_id]` |

Đợt 4 (2026-11-25): không đổi bảng; hình response và file lộ trình xem `specs/212-hinh-lo-trinh-hoc/data-model.md`.
