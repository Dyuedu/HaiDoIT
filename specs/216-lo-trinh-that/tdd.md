# TDD: API trả lộ trình đã xếp kèm tỷ lệ của từng kỹ năng

Theo `docs/templates/test-driven-tdd/test-driven-development.md`. Lệnh (Postgres thật):

```text
HAIDO_TEST_DATABASE_URL=... uv run pytest -q tests/api/test_fr22_learning_path_stat.py tests/api/test_fr22_learning_path_draft.py
```

## Các hành vi

1. Chưa rà soát, không có nội dung, hay không có tin: 200 `not_ready` ở mọi cấp, đủ `meta`.
2. Vai trò lạ 404 kèm ngày; chưa có snapshot 404 không ngày.
3. Đã rà soát: `ready`, tỷ lệ, nhóm, ô, ngày bằng `skill-rates`; cốt lõi trước thường gặp; không lưu ý nháp; chỉ đọc `stat_*`.
4. Dấu rà soát sai là lỗi lúc nạp; đã rà soát thì phải có biên bản trong `docs/`; đồ thị hỏng là lỗi lúc nạp.
5. Cổng FR-24 quét `haido_api/content/learning_path.json`.

## RED (2026-11-25)

Bốn file test → 1 failed, 144 passed, 2 errors (`haido_api.stat_path` chưa có; cổng FR-24 chưa quét đường dẫn mới).

## GREEN (2026-11-25)

- Bảy nhóm test liên quan → 314 passed.
- Lượt toàn bộ đầu: 1 failed, 1899 passed. Test đỏ là test của #103 ghi "`learning-path` nguồn `stat` trả 404"; AC của #103 vẫn đúng, test và spec của #103 được cập nhật.
- Lượt toàn bộ cuối: 1901 passed; `ruff check .` sạch; `check_gates.py` 10 pass; `npx vitest run` 442 passed (web không đổi).
- Image thật, snapshot 2026-11-25: `main:app` mọi nguồn `stat` trả `not_ready` cho backend, data_engineer, frontend, 404 cho mã lạ; app demo trả Backend 50 kỹ năng, 16 chặng, có lưu ý `draft_path`.
