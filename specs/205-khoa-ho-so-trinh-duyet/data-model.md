# Data model: Khóa hồ sơ trình duyệt và danh sách kỹ năng mồi

Không thêm bảng, không thêm cột, không thêm revision Alembic.

## `localStorage` của trình duyệt

| Khóa | Giá trị |
|---|---|
| `haido:profile` | `{"v":1,"role":"backend"\|null,"level":"fresher"\|null,"skills":["python","sql"]}` |
| `haido:session` | mã phiên ẩn danh (UUID ngẫu nhiên) |
| `haido:eval` | `"1"` |

- `skills`: không trùng, giữ thứ tự tick, tối đa 200 mã, mỗi mã khớp `^[a-z0-9]+(_[a-z0-9]+)*$` và dài tối đa 40 ký tự.
- Đổi hình hồ sơ thì tăng `v`. Đọc thấy `v` khác phiên bản hiện tại thì ra hồ sơ rỗng, cho tới khi có bước chuyển đổi.

## File `haido_core/vocab/skills_seed.json`

```json
{
  "version": "seed-2026-11-11",
  "note": "...",
  "skills": [
    {"code": "machine_learning", "name_en": "Machine Learning", "name_vi": "Học máy",
     "aliases": ["ml"], "source": "base-2026-11: tagged on 32 of 3469 postings"}
  ]
}
```

`skills` xếp theo `code`. `source` không được phát qua API.
