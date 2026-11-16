# Data model: Chức danh thành vai trò

Không đổi bảng, cột hay revision Alembic. Không lưu chức danh ở đâu cả (không bảng, không log, không `localStorage`).

API mới `GET /api/v1/role-for-title?title=<chuỗi, 1–120 ký tự sau khi bỏ khoảng trắng hai đầu>`:

```json
{ "data": { "status": "matched", "role": "backend" } }
```

| `status` | Khi nào | `role` |
|---|---|---|
| `matched` | phép 6 ra một vai trò cụ thể | mã của `config/rules.toml` |
| `generic` | phép 6 ra `Other` (chức danh IT chung chung) | `null` |
| `not_it` | phép 6 ra `không thuộc IT` | `null` |

Response không có số nên không dùng Envelope (như `GET /api/v1/skills`).
