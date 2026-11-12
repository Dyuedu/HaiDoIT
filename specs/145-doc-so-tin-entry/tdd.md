# TDD: Đọc số tin entry-level từ cơ cấu cấp bậc toàn quốc

Theo `docs/templates/test-driven-tdd/test-driven-development.md`. Test dùng Postgres thật (`haido_test` trên Docker local), dựng thẳng hàng `stat_*`, không có tin nào trong bảng tin.

Lệnh:

```text
HAIDO_TEST_DATABASE_URL=postgresql+psycopg://haido:haido_local@127.0.0.1:5433/haido_test uv run pytest tests/api/test_fr37_newcomer_roles_stat.py -q
```

## Các hành vi

1. `test_fr37_so_tin_entry_level_la_n_cua_o_toan_quoc_nhom_entry`: entry = n của ô `vn` nhóm `entry` (20), n = ô `vn` ở `all` (50), mix giữ nguyên, ô `ha_noi` cấp `entry` (n = 999) không được dùng, `levels` = Intern/Fresher/Junior.
2. `test_fr37_doc_so_nguoi_moi_khong_cham_bang_tin`: không câu SQL nào có `job_`, `public.`, `sum(`, `count(`.
3. `test_fr37_doc_snapshot_cong_bo_moi_nhat_bo_qua_snapshot_dang_mo`: snapshot `open` mới hơn bị bỏ qua.

## RED (2026-11-12)

`uv run pytest tests/api/test_fr37_newcomer_roles_stat.py -q` → 9 failed, 1 passed. Ba test của issue này đỏ vì `StatMarket.newcomer_roles` còn là bản giữ chỗ của #144, luôn ném `UnknownCell` nên route trả 404 (`assert 404 == 200`). Test xanh duy nhất là test 404 khi chưa có snapshot của #146 (bản giữ chỗ cũng trả 404).

## GREEN (2026-11-12)

- `uv run pytest tests/api/test_fr37_newcomer_roles_stat.py -q` → 10 passed.
- `uv run pytest -q` (Postgres) → 959 passed.
- `uv run ruff check .` sạch; `tools/gates/check_gates.py` → 8 pass (có AD-7), 2 skip, 0 fail.
- Số thật: `StatMarket.newcomer_roles` trên DB local `haido` (bản sao prod, snapshot 12/11) cho `it_infra` 132/485, `ba_po_pm` 128/791, `backend` 56/470, `game` 43/99; khớp `n` của ô `vn` mà `GET /api/v1/city-shares?level=entry` của prod trả cùng ngày.
