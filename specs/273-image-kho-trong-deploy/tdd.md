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
