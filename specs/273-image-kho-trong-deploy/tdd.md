# TDD: Build image kho trong workflow deploy

Theo `docs/templates/test-driven-tdd/test-driven-development.md`.

Lệnh:

```text
uv run pytest tests/deploy -q
```

Test đọc workflow, file compose, `daily.sh` và mode trong git. Riêng `vps-deploy.sh` được chạy thật trong thư mục tạm, với `docker`, `curl`, `sleep` giả đặt trước trong `PATH` để ghi lại lệnh.

## Các hành vi

1. Matrix của job `build` có `warehouse` → `deploy/warehouse.Dockerfile`, cùng `api` và `web`.
2. `on.push.paths` có `config/**`.
3. Job deploy có `scp -p deploy/compose.scraper.yml deploy/daily.sh "$USER@$HOST:$VPS_PATH/"`.
4. Service `warehouse` dùng `ghcr.io/dyuedu/haidoit-warehouse:${HAIDO_WAREHOUSE_TAG:-none}`, không có `build`, `pull_policy: never`, không mở cổng; `scraper` và `scraper-browser` vẫn có `build`.
5. `daily.sh` đọc `.warehouse-tag`, đặt `HAIDO_WAREHOUSE_TAG=`, rồi mới `run --rm warehouse`.
6. `git ls-files -s deploy/daily.sh` bắt đầu bằng `100755`.
7. Deploy khỏe: có `docker pull ghcr.io/dyuedu/haidoit-warehouse:sha-abc123` trước `docker logout ghcr.io`, và `.warehouse-tag` thành `sha-abc123`.
8. Deploy hỏng ở cổng sức khỏe: script thoát khác 0 và `.warehouse-tag` vẫn là `sha-old`.

## RED

`uv run pytest tests/deploy/test_gh273_image_kho.py -q` → 7 failed, 1 passed.

- Hành vi 8 xanh sẵn: script cũ chưa đụng tới `.warehouse-tag`, nên tag cũ đương nhiên còn. Test này giữ lại để chặn việc ghi tag trước cổng sức khỏe.
- Hành vi 7 đỏ vì `ValueError: substring not found`: log lệnh không có `docker pull` image kho.
- Các hành vi còn lại đỏ vì workflow, compose, `daily.sh` và mode git chưa đổi.

## GREEN

- `uv run pytest tests/deploy -q` → lần đầu 37 passed, 1 failed: `test_daily_warehouse.py::test_compose_co_warehouse_khong_mo_cong` (#90) còn đòi `haidoit-warehouse:local`. Đổi sang image GHCR → 38 passed.
- `bash -n deploy/daily.sh deploy/vps-deploy.sh` sạch.
- `docker compose -f compose.scraper.yml config` (với `.env` giả): thiếu tag ra `ghcr.io/dyuedu/haidoit-warehouse:none`, có `HAIDO_WAREHOUSE_TAG=sha-abc` ra đúng tag; image của scraper không đổi.

## Kiểm sau merge (2026-11-12)

Lượt cron 02:00 trên VPS, snapshot `2026-11-12`, là lượt đêm đầu tiên chạy kho bằng image GHCR.

- Log `daily-2026-11-12.log`: dòng `image kho: sha-cd57eb8f132d8e46b17393201a0eace587f05947`. Tag không còn là `sha-28a7cd6` của lần deploy PR #274 vì #275 và #276 đã deploy lại, mỗi lần tự build và chuyển tag. Bước kho chạy 02:44:58–02:45:20: ingest 2716 tin, vòng đời 6466 tin, tổng hợp 594 ô và 495 tỷ trọng thành phố, chốt `published`. Không có `KHO HONG`.
- `haido.stat_sources` có 8 hàng cho `2026-11-12` (careerlink, itnavi, itviec, momo, topcv, topdev, vietnamworks, zalo). Truy vấn trong transaction READ ONLY.
- `GET /api/v1/city-shares?role=ai_ml|backend|frontend` → 200, `snapshot_date: 2026-11-12`, `sources_failed: []`.
- Sau khi kiểm, đã xoá image `haidoit-warehouse:local` và hai image GHCR cũ (`sha-28a7cd6`, `sha-ca51d8e`) trên VPS; giữ image đang ghi trong `.warehouse-tag`.

## Chạy lại (2026-11-16, #302)

#302 sửa `deploy/daily.sh` (thêm `topcv` vào bước trình duyệt) và `deploy/compose.scraper.yml` (`shm_size` của `scraper-browser` lên `1g`). Không đụng image kho hay `.warehouse-tag`, không đổi scenario của #273.

- `uv run pytest tests/deploy -q` → 62 passed.

## Đợt 2026-11-17 (#166, đợt 2 theo review): file dùng chung đổi lần nữa, AC của issue này không đổi

Lý do: #166 đợt 2 (cỡ mẫu `skill_count` của `skill_rate`, `mentioned` theo mọi cấp, `data.level`, prod chọn nguồn `stat`) sửa thêm `deploy/compose.prod.yml` (thêm `HAIDO_MARKET_SOURCE_SKILL_ROLES: stat`). Image kho không vào `compose.prod.yml`, `.warehouse-tag` và `vps-deploy.sh` không đổi.

- RED: không có, vì không có hành vi nào của issue này đổi. RED của #166 đợt 2 nằm ở `specs/166-hinh-ky-nang-theo-vai-tro/tdd.md`.
- GREEN (chạy thật, 2026-11-17): `uv run pytest -q` (Postgres thật, DB `fx166_test`, không skip) → 1538 passed; `cd web && npx vitest run` → 22 files, 298 passed; `tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` → 10 pass, 0 skip, 0 fail.

## Đợt #309 (2026-11-17): compose.prod đặt `stat` cho mọi nguồn

Lý do: `deploy/compose.prod.yml` thiếu `HAIDO_MARKET_SOURCE_SKILL_RATES` và `HAIDO_MARKET_SOURCE_LEARNING_PATH`, nên prod phục vụ số giả của hai phép này. #309 thêm hai dòng `stat` và test `tests/deploy/test_gh309_prod_khong_doc_du_lieu_gia.py` sinh từ `SOURCE_ENV`. Hành vi và AC của issue này không đổi; test cũ của nó vẫn xanh.

- RED: test mới của #309, `3 failed, 8 passed` (thiếu `skill_rates`, `learning_path`).
- GREEN: `tests/deploy` 75 passed.

## Đợt 2026-11-17 (#151, #106, #103): file dùng chung đổi, AC của issue này không đổi

Lý do: tỷ lệ kỹ năng thật (#151), phép 2 `select_cell` (#106) và ràng buộc lớp đọc (#103) sửa file mà issue này từng đụng:

  - `deploy/compose.prod.yml` (thêm `HAIDO_MARKET_SOURCE_SKILL_RATES: stat`);

Hành vi và AC của issue này không đổi: thay đổi chỉ thêm (phương thức `skill_rates` thật, trường `order` có mặc định, một biến môi trường ở prod, một đoạn tài liệu); `city_shares`, `newcomer_roles`, `learning_path`, `skill_roles` của `StatMarket` giữ nguyên. Chi tiết: `specs/151-ty-le-ky-nang-that/plan.md`.

- RED: không có, vì không có hành vi nào của issue này đổi; không test nào của issue này đổi kỳ vọng. RED của #151, #106, #103 nằm ở `specs/151-ty-le-ky-nang-that/tdd.md`, `specs/106-chon-o-quay-ve/tdd.md`, `specs/103-api-doc-ty-le-that/tdd.md`.
- GREEN (chạy thật, 2026-11-17): `uv run pytest -q` (Postgres thật, DB `fx151_test`, không skip) → 1580 passed; `cd web && npx vitest run` → 298 passed; `tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` → 10 pass, 0 skip, 0 fail.

Cập nhật sau review (đợt 2, 2026-11-17): trong `StatMarket` chỉ `skill_rates` đổi thêm (404 khi ô không có hàng tỷ lệ, `n_scanned` nhất quán, chữ nhãn); hành vi và AC của issue này vẫn không đổi. RED và GREEN: `specs/151-ty-le-ky-nang-that/tdd.md` đợt 2.

## Đợt #168 (2026-11-17): file dùng chung đổi, AC của issue này không đổi

Lý do: #168 cài `StatMarket.skill_roles` đọc `stat_skill_rates` (số thật cho `skill-roles`), sửa file mà issue này từng đụng: `deploy/compose.prod.yml`.
Hành vi và AC của issue này không đổi; thay đổi chỉ thêm phương thức `skill_roles` thật và chữ mô tả. RED, GREEN và mutation: `specs/168-ky-nang-vai-tro-that/tdd.md`.

## Đợt #216 (2026-11-25): lộ trình thật trong StatMarket

Lý do: sửa file mà issue này từng đụng (trong số `stat_market.py`, `check_gates.py`, `envelope-meta.md`, `compose.prod.yml`, test lộ trình): chỉ phần lộ trình học. Hành vi và AC của issue này không đổi.

RED và GREEN: `specs/216-lo-trinh-that/tdd.md`.

## Đợt sửa 2026-11-27 (#230, hình tin dán "Soi tin")

**Vì sao sửa**: #230 thêm nguồn `posting_check` vào `SOURCE_ENV`, bảng `[posting_match]` vào `config/rules.toml`, ô `vn.backend.junior` vào
`fake_market.json`, route `posting-reads` và `posting-check`. Các file của issue này bị chạm: `deploy/compose.prod.yml`.

**Hành vi của issue này**: không đổi; không AC nào của #273 đúng khác đi. Mọi thay đổi chỉ cộng thêm (khóa nguồn mới, mục cấu hình mới, ô và hàng
fixture mới, hàng tài liệu mới, nguồn `posting_check` trong các lời gọi `create_app` của test).

**RED/GREEN**: RED (chạy thật): trả 13 file test cũ dựng create_app với năm nguồn về bản ở HEAD rồi chạy với code mới thì 109 failed, 54 lỗi, 32 passed (thiếu nguồn posting_check). GREEN: sau khi thêm nguồn và sửa các file, uv run pytest -q toàn bộ được 2029 passed (không còn test nào đỏ của issue này). Chi tiết ở specs/230-hinh-soi-tin/tdd.md.
