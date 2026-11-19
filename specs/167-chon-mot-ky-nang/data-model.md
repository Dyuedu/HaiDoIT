# Data model: Chọn một kỹ năng

Không đổi bảng, cột, revision Alembic hay hình API. Đọc `GET /api/v1/skills` (#205) và `data.skill`, `data.mentioned` của `GET /api/v1/skill-roles` (#166).

Trình duyệt: chỉ đọc `haido:profile.skills` để gợi ý (#206); không ghi. URL: `/insights?skill=<mã>`; mã phải đúng định dạng của `isSkillCode`.
