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

## Đợt #102 (2026-11-19): θ có phiên bản, AC của issue này không đổi

Lý do: #102 đóng băng θ (`config/theta.toml`, `theta-1` = 0,3/0,1), thêm `snapshots.theta_version` (migration 0010) và `meta.thresholds.theta_version`, sửa file mà issue này từng đụng: `docs/api/envelope-meta.md`.
Giá trị θ không đổi nên số, nhóm và hành vi của issue này không đổi; test chỉ thêm `theta_version` vào ngưỡng hoặc đổi head migration mong đợi sang 0010. RED, GREEN và đột biến: `specs/102-dong-bang-theta/tdd.md`.

## Đợt #327, #328 (2026-11-19): thêm route toàn cảnh thị trường, AC của issue này không đổi

Lý do: #327 và #328 thêm `GET /api/v1/market-overview` và sửa file mà issue này từng đụng (`haido_api/schemas/market.py`, `fake_market.py`, `market_source.py`, `routes/market.py`, `stat_market.py`, `fixtures/fake_market.json`, `docs/api/envelope-meta.md`, `tests/api/test_ad17_routes.py`). Thay đổi chỉ thêm: schema, phương thức, route, một mục fixture, một dòng `SAMPLE_QUERY`; route cũ và số của chúng không đổi.

- RED và GREEN: `specs/327-tong-quan-thi-truong-api/tdd.md`. `uv run pytest -q` → 1336 passed, 304 skipped.

## Đợt #343 (2026-11-23): thêm `HAIDO_RESPONSE_CACHE` vào prod, AC của issue này không đổi

Lý do: #343 thêm biến `HAIDO_RESPONSE_CACHE: "on"` vào `deploy/compose.prod.yml` và phương thức `version()` vào `market_source.py`, `fake_market.py`, `stat_market.py`. Mọi khóa của `SOURCE_ENV` vẫn là `stat` trên prod; `compose.local.yml` vẫn giữ nguồn `fake` và không bật cache. Test của issue này không phải sửa.

- RED và GREEN: `specs/343-cache-response/tdd.md`.

## Đợt #217 (2026-11-25): lộ trình học thành chủ đề

Lý do: sửa file mà issue này từng đụng (trong số `fake_market.py`, `docs/api/openapi.json`, `docs/api/envelope-meta.md`, `tools/gates/check_gates.py`, `web/lib/learning-path.ts`, test lộ trình): chỉ phần lộ trình học. Hành vi và AC của issue này không đổi.

RED và GREEN: `specs/217-man-lo-trinh/tdd.md` đợt 4.

## Đợt #216 (2026-11-25): lộ trình thật trong StatMarket

Lý do: `learning-path` ở prod đổi từ 404 sang 200 `not_ready`; AC vẫn đúng (không số giả).

RED và GREEN: `specs/216-lo-trinh-that/tdd.md`.

## Đợt sửa 2026-11-27 (#230, hình tin dán "Soi tin")

**Vì sao sửa**: #230 thêm nguồn `posting_check` vào `SOURCE_ENV`, bảng `[posting_match]` vào `config/rules.toml`, ô `vn.backend.junior` vào
`fake_market.json`, route `posting-reads` và `posting-check`. Các file của issue này bị chạm: `deploy/compose.prod.yml`, `docs/api/envelope-meta.md`.

**Hành vi của issue này**: không đổi; không AC nào của #309 đúng khác đi. Mọi thay đổi chỉ cộng thêm (khóa nguồn mới, mục cấu hình mới, ô và hàng
fixture mới, hàng tài liệu mới, nguồn `posting_check` trong các lời gọi `create_app` của test).

**RED/GREEN**: RED (chạy thật): trả 13 file test cũ dựng create_app với năm nguồn về bản ở HEAD rồi chạy với code mới thì 109 failed, 54 lỗi, 32 passed (thiếu nguồn posting_check). GREEN: sau khi thêm nguồn và sửa các file, uv run pytest -q toàn bộ được 2029 passed (không còn test nào đỏ của issue này). Chi tiết ở specs/230-hinh-soi-tin/tdd.md.
