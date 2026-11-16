# Data model: Tìm kỹ năng song ngữ

Không đổi bảng, cột, revision Alembic hay hình API. Đọc `GET /api/v1/skills` (hình của #205: `{data: {vocab_version, skills: [{code, name_en, name_vi, aliases}]}}`).

Không lưu chuỗi tìm. Kỹ năng tick từ ô tìm lưu vào `haido:profile.skills` theo #206.
