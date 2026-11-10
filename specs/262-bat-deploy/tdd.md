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
