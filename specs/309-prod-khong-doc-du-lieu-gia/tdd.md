# TDD: Production không bao giờ phục vụ fixture giả của thị trường

Theo `docs/templates/test-driven-tdd/test-driven-development.md`.

Lệnh:

```text
uv run pytest -q -p no:cacheprovider tests/deploy/test_gh309_prod_khong_doc_du_lieu_gia.py
```

## Các hành vi

1. Mỗi khóa của `SOURCE_ENV` có giá trị `stat` trong `deploy/compose.prod.yml` (tham số hóa theo `SOURCE_ENV`, nên phép mới tự vào danh sách).
2. `load_sources` với môi trường của prod chỉ dựng `StatMarket`.
3. compose.local giữ `fake` cho mọi phép.

## Đợt 1 (2026-11-17)

### RED

`3 failed, 8 passed`. Đỏ đúng lý do: `test_gh309_compose_prod_dat_stat_cho_moi_nguon[learning_path]` và `[skill_rates]` (biến chưa có trong compose.prod), `test_gh309_moi_nguon_cua_prod_dung_ban_that` báo "prod vẫn dựng nguồn giả cho: learning_path, skill_rates". Ba phép đã đặt `stat` và năm test compose.local xanh ngay từ đầu.

### GREEN

Thêm hai dòng `stat` vào `deploy/compose.prod.yml`: `tests/deploy` 75 passed.

## Đợt #151 (2026-11-17): skill-rates có số thật

Lý do: #151 cài `StatMarket.skill_rates`, nên `skill-rates` trên prod không còn trả 404 mà trả số thật của `stat_skill_rates`. Lúc gộp main, dòng `HAIDO_MARKET_SOURCE_SKILL_RATES` của #309 và của #151 bị lặp trong `deploy/compose.prod.yml`; giữ một dòng (ghi chú của #151), ghi chú của #309 giờ chỉ nói về `learning-path`. AC của #309 vẫn đúng: mọi khóa của `SOURCE_ENV` là `stat`.

- Không có test mới; `tests/deploy/test_gh309_prod_khong_doc_du_lieu_gia.py` vẫn xanh sau khi gộp (xem GREEN của #151).

## Đợt #168 (2026-11-17): file dùng chung đổi, AC của issue này không đổi

Lý do: #168 cài `StatMarket.skill_roles` đọc `stat_skill_rates` (số thật cho `skill-roles`), sửa file mà issue này từng đụng: `deploy/compose.prod.yml`, `docs/api/envelope-meta.md`.
Hành vi và AC của issue này không đổi; thay đổi chỉ thêm phương thức `skill_roles` thật và chữ mô tả. RED, GREEN và mutation: `specs/168-ky-nang-vai-tro-that/tdd.md`.
