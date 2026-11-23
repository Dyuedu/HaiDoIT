# Đo tải API (#342)

Bài đo chạy trên máy dev. Không bắn tải vào production hay vào VPS.

Cần có: Docker, [k6](https://grafana.com/docs/k6/latest/set-up/install-k6/) (≥ 2.2), `uv`.

## 1. Dựng API và Postgres

```bash
docker compose -f deploy/compose.loadtest.yml up -d --build --wait
```

API chạy ở `http://127.0.0.1:8001`, cùng image và lệnh với prod (`uvicorn` một worker), mọi nguồn `stat`, giới hạn 2 CPU như VPS. Postgres mở cổng `127.0.0.1:5434`, DB `haido_load_test`.

## 2. Nạp một snapshot giả

```bash
HAIDO_TEST_DATABASE_URL=postgresql+psycopg://haido:haido_local@127.0.0.1:5434/haido_load_test \
  uv run python -m tools.loadtest_seed --facts 5600
```

Lệnh **xóa** schema `haido` của DB đó, và chỉ chạy với DB local có tên kết thúc bằng `_test`. Mất khoảng 40 giây.

## 3. Chạy k6

```bash
cd loadtest/k6

# Gọi mỗi URL của kịch bản một lần; mọi URL phải trả 200.
SCENARIO=smoke k6 run baseline.js

# Tăng tải tới khi p95 >= 200 ms hoặc lỗi >= 0,1%, kèm báo cáo HTML.
SCENARIO=breakpoint MAX_RPS=1000 DURATION=5m \
  K6_WEB_DASHBOARD=true K6_WEB_DASHBOARD_EXPORT=breakpoint.html k6 run baseline.js

# Tải cố định 40 RPS trong 60 giây.
SCENARIO=breakpoint START_RPS=40 MAX_RPS=40 DURATION=60s k6 run baseline.js
```

| Biến | Mặc định | Ý nghĩa |
|---|---|---|
| `BASE_URL` | `http://127.0.0.1:8001` | Địa chỉ API |
| `SCENARIO` | `smoke` | `smoke` hoặc `breakpoint` |
| `START_RPS`, `MAX_RPS` | 10, 2000 | RPS đầu và cuối của ramp |
| `DURATION` | `10m` | Thời gian ramp |
| `MAX_VUS` | 2000 | Số VU tối đa k6 được dùng để giữ tốc độ |

Mỗi iteration là đúng một request, nên `iterations/s` chính là RPS. Khi `dropped_iterations` > 0, API đã chậm tới mức k6 hết VU chờ, tức đã quá trần.

## Đọc kết quả cho đúng

- **p95 của k6 là cộng dồn từ đầu bài.** Ramp nhanh thì bài dừng muộn hơn thời điểm API thật sự xuống cấp. Muốn biết chính xác trần, chạy vài mức tốc độ cố định quanh điểm gãy, mỗi mức ít nhất hai lần.
- **Máy dev có nhiễu.** Lượt nào lệch hẳn so với các lượt cùng mức thì chạy lại.
- Theo dõi tài nguyên trong lúc đo: `docker stats haido-loadtest-api-1 haido-loadtest-postgres-1`.

Kết quả baseline: [specs/342-do-tai-baseline/ket-qua-do.md](../specs/342-do-tai-baseline/ket-qua-do.md).

## Dọn

```bash
docker compose -f deploy/compose.loadtest.yml down -v
```
