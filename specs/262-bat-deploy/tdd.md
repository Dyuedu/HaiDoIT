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
