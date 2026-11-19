# TDD: Bật deploy

Một hành vi một test. Assert trên nội dung workflow và file compose, không gọi VPS.

Lệnh:

```text
uv run pytest tests/deploy/test_gh262_bat_deploy.py -q
```

RED: 5 failed, 1 passed. Test project name đã xanh vì `compose.prod.yml` vốn có `name: haido-prod`. Bốn test kia đỏ vì workflow chưa có đường dẫn, `scp`, Alembic và cổng localhost.

GREEN: `uv run pytest tests/deploy/test_gh262_bat_deploy.py tests/deploy/test_compose_ad1_ad15.py tests/deploy/test_gh162_ban_do_doc_snapshot_that.py -q` → 16 passed.

## Đợt 2 — 2026-11-10: web trong mạng proxy

Lý do: trên VPS, web đang ở mạng `haido-edge` của Nginx Proxy Manager và `haidoit.io.vn` trả 200. `compose.prod.yml` trên `main` chưa khai mạng này, nên bật `DEPLOY_ENABLED` lúc đó sẽ cắt web khỏi proxy.

Lệnh:

```text
uv run pytest tests/deploy/test_proxy_npm.py -q
```

Các hành vi:

1. Proxy là project `haido-proxy`, cổng 80 và 443 mở, cổng 81 chỉ `127.0.0.1`, mạng ngoài `haido-edge`.
2. `web` vào `default` và `edge`. `api` không vào `edge`.
3. Script deploy tạo `haido-edge` trước `up -d --remove-orphans`.

RED (chạy với `compose.prod.yml` và `deploy.yml` của `main`): 2 failed, 1 passed. Test 1 xanh vì `compose.proxy.yml` là file mới. Test 2 lỗi `KeyError: 'networks'`, test 3 lỗi vì không thấy `docker network create haido-edge`.

GREEN: `uv run pytest tests/deploy -q` → 21 passed.

## Đợt 3 — 2026-11-10: script VPS lỗi cú pháp

Lý do: run 42851541091 (lần deploy thật đầu tiên sau khi bật `DEPLOY_ENABLED`) đỏ ở bước Deploy với `bash: line 52: unexpected EOF while looking for matching "`. Test cũ chỉ so chữ trong `deploy.yml` nên không bắt được. Dựng lại heredoc như Actions bung ra rồi `bash -n` cho đúng lỗi ở dòng 52.

Lệnh:

```text
uv run pytest tests/deploy -q
```

Các hành vi:

1. Bước Deploy không còn `<<EOF`, gửi `deploy/vps-deploy.sh` qua `bash -se`, token lấy `${GHCR_PULL_TOKEN:-$GITHUB_TOKEN}`.
2. `deploy/vps-deploy.sh` qua `bash -n`.
3. `resolve_db_url` trả đúng URL với nháy kép, nháy đơn, CRLF, và khi suy từ `DATABASE_URL` dạng `postgresql://`, `postgres://`, `postgresql+psycopg://`.
4. Thiếu cả hai khóa thì trả mã khác 0, báo "Không suy ra được URL kho", không in gì ra stdout.
5. Các test thứ tự cũ (Alembic trước `up`, tạo `haido-edge` trước `up`, kiểm hai cổng sau `up`) đọc script mới.

RED: 12 failed, 18 passed. Script chưa có nên mọi test đọc nó đều đỏ; test workflow đỏ vì còn heredoc.

GREEN: 30 passed.

Chạy thử bước Deploy trên máy với `ssh`, `docker`, `curl` giả ghi lại lệnh: thứ tự login → pull → logout → alembic → tạo mạng → up → ps → prune → hai cổng. Token có dấu cách và `$` tới `docker login` qua stdin nguyên vẹn. Cho `compose run` trả 3 thì script dừng với mã 3 và không có `up`.

## Đợt 4 — 2026-11-11: image kho trong deploy (#273)

Lý do: bản đồ production trống vì image kho build tay trên VPS từ code cũ, không ghi `stat_sources`. #273 cho workflow build image kho cùng commit. Thay đổi chạm `deploy.yml` và `vps-deploy.sh` của issue này.

Test mới ở `tests/deploy/test_gh273_image_kho.py`; nhật ký RED/GREEN đầy đủ ở `specs/273-image-kho-trong-deploy/tdd.md`. Các test cũ của #262 (`test_gh262_bat_deploy.py`, `test_gh262_vps_script.py`, `test_proxy_npm.py`) không phải sửa và vẫn xanh: thứ tự Alembic → tạo mạng → `up` → kiểm hai cổng giữ nguyên, lệnh `docker pull` image kho chen trước `docker logout`.

GREEN: `uv run pytest tests/deploy -q` → 38 passed.

## Đợt 2026-11-17 (#166, đợt 2 theo review): file dùng chung đổi lần nữa, AC của issue này không đổi

Lý do: #166 đợt 2 (cỡ mẫu `skill_count` của `skill_rate`, `mentioned` theo mọi cấp, `data.level`, prod chọn nguồn `stat`) sửa thêm `deploy/compose.prod.yml` (thêm `HAIDO_MARKET_SOURCE_SKILL_ROLES: stat` vào môi trường dịch vụ `api`). Workflow, `vps-deploy.sh`, mạng, cổng và kiểm sức khỏe không đổi; test `test_gh262_*` không đổi.

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

## Đợt 5 — 2026-11-19: deploy xóa tag image cũ

Lý do: kiểm VPS sáng 2026-11-19 thấy đĩa 33 GB đầy 94% (còn 1,9 GB), 87 image, gần hết là tag `sha-*` cũ của api, web, kho. Dòng `docker image prune -f --filter until=168h` chỉ xóa image dangling nên không gỡ được chúng. Đã dọn tay một lần (còn 13 GB trống); đợt này để deploy tự dọn. Không có issue riêng; người dùng yêu cầu sửa thẳng.

Lệnh:

```text
uv run pytest tests/deploy/test_gh262_don_tag_cu.py -q
```

Các hành vi:

1. Giữ 2 tag `sha-*` mới nhất, in các tag còn lại.
2. Tag đang deploy không bị in dù cũ hơn (rollback).
3. Tag không phải `sha-*` bị bỏ qua và không đếm.
4. Ít hơn hoặc bằng 2 tag thì không in gì.
5. Deploy khỏe: `docker rmi` đúng `sha-old1`, `sha-old2` của cả ba image.
6. Deploy hỏng: không có `docker rmi`.
7. `docker rmi` lỗi: deploy vẫn trả 0.

RED: 6 failed, 1 passed. `stale_tags` chưa có nên bốn test hàm đỏ; script chưa gọi `rmi` nên hai test chạy cả script đỏ. Test "deploy hỏng thì không xóa" xanh sẵn vì script cũ không xóa tag nào.

Lần chạy đầu sau khi sửa: 1 failed (hành vi 2). Trên Windows Python ghi stdin bằng CRLF nên tag thành `sha-b`, không khớp tag cần giữ. Thêm bỏ CR cuối dòng trong `stale_tags`, như `env_value` đã làm.

GREEN: `uv run pytest tests/deploy -q` → 84 passed. `uv run pytest -q --ignore=tests/deploy` → 1240 passed, 280 skipped.

Chạy thử trên VPS: nạp script mới với `HAIDO_DEPLOY_LIB_ONLY=1`, đưa `docker images <repo>` thật qua `stale_tags 2 sha-5e4d9e6…`: mỗi image còn 2 tag nên không in tag nào, và `docker images` liệt kê mới trước như hàm giả định.
