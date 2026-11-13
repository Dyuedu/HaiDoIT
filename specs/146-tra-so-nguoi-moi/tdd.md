# TDD: Trả số tin entry-level, tỷ lệ và n của mỗi vai trò

Theo `docs/templates/test-driven-tdd/test-driven-development.md`. Test API dùng Postgres thật (`haido_test`), dựng thẳng hàng `stat_*`. Test deploy đọc file compose.

Lệnh:

```text
HAIDO_TEST_DATABASE_URL=postgresql+psycopg://haido:haido_local@127.0.0.1:5433/haido_test uv run pytest tests/api/test_fr37_newcomer_roles_stat.py tests/deploy/test_gh146_nguoi_moi_doc_snapshot_that.py -q
```

## Các hành vi

1. `test_fr37_moi_vai_tro_cua_config_deu_co_dong`: đủ 17 mã của config; `game` vắng là 0/0, `null_data`.
2. `test_fr37_vai_tro_du_mau_khong_co_tin_entry_hien_0`: `qa` 0/35, `share = 0`, `shown`.
3. `test_fr37_vai_tro_duoi_30_tin_khong_co_ty_le_nhung_van_co_so`: `ui_ux` 3/12, `null_data`, value `null`, `level_share` của `vn.ui_ux`.
4. `test_fr37_nguong_mau_lay_tu_config`: `min_sample = 10` đổi `ui_ux` sang `shown`.
5. `test_fr37_thu_tu_dong_co_ty_le_truoc_roi_so_entry_giam_dan`: `qa`, `backend`, `devops`, `mobile`, rồi `ui_ux`, rồi phần còn lại theo mã.
6. `test_fr37_envelope_co_ngay_snapshot_nguon_va_nguon_loi`: ngày, `partial`, nguồn A–Z, nguồn lỗi.
7. `test_fr37_chua_co_snapshot_doc_duoc_la_404`: 404 `unknown_cell`.
8. `test_gh146_compose_prod_chon_nguon_stat_cho_newcomer_roles`.
9. `test_gh146_compose_local_giu_nguon_gia_cho_newcomer_roles`.

## RED (2026-11-12)

- `uv run pytest tests/api/test_fr37_newcomer_roles_stat.py -q` → 9 failed, 1 passed. Sáu test 1–6 của issue này (cùng ba test của #145) đỏ vì `StatMarket.newcomer_roles` còn là bản giữ chỗ, luôn ném `UnknownCell` → 404 (`assert 404 == 200`). Test 7 xanh ngay vì bản giữ chỗ cũng trả 404; giữ lại để khóa hành vi khi chưa có snapshot.
- `uv run pytest tests/deploy/test_gh146_nguoi_moi_doc_snapshot_that.py -q` → 1 failed, 1 passed: `compose.prod.yml` chưa có biến (`assert None == 'stat'`). Test 9 xanh ngay (local vốn không đặt biến).

## GREEN (2026-11-12)

- Hai file test trên → 12 passed.
- `uv run pytest -q` (Postgres) → 959 passed.
- `uv run ruff check .` sạch; `tools/gates/check_gates.py` → 8 pass, 2 skip, 0 fail.
- Trên DB local `haido` (bản sao prod, snapshot 12/11): 17 dòng; 16 vai trò có tỷ lệ, đứng đầu là `it_infra` 132/485 (27,2%), `ba_po_pm` 128/791, `qa` 77/292; `data_scientist` 5/28 là `null_data` và đứng cuối.

## Đợt 2026-11-13 (#148): ô hỏng entry > n

Lý do sửa: review PR #291 chỉ ra phép chia `entry_n / total_n` không có bảo vệ. Một ô hỏng làm cả danh sách 17 dòng không đọc được ở web.

- RED: `uv run pytest tests/api/test_fr37_newcomer_roles_stat.py -q` → 3 failed, 12 passed. Hai test đỏ vì `ValidationError` của `Stat` thay vì `RuntimeError` và code `invalid_response` thay vì `internal_error`; một test `DID NOT RAISE` (vai trò dưới ngưỡng, entry 20 > n 12).
- GREEN: cùng lệnh → 15 passed. `uv run pytest tests/api/test_fr37_newcomer_roles_stat.py tests/deploy/test_gh146_nguoi_moi_doc_snapshot_that.py -q` → 17 passed. `uv run pytest -q` → 964 passed.
- Chi tiết và đột biến: `specs/148-test-nguoi-moi/tdd.md`.
