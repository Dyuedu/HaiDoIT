# Kết quả đo baseline (#342) — 2026-11-23

## Kết luận

| | Số đo |
|---|---|
| RPS cao nhất còn giữ p95 < 200 ms và lỗi < 0,1% | **40 RPS** (p95 ≈ 60 ms, 0 lỗi) |
| Trần thông lượng (đặt tải cao hơn cũng không phục vụ thêm) | **≈ 50–58 RPS** |
| Nút thắt đầu tiên | **CPU của tiến trình Python của API** (một worker `uvicorn`); Postgres còn rảnh |
| Khoảng cách tới mục tiêu 5k RPS | **≈ 125 lần** |

Lỗi HTTP luôn là 0%. Quá trần thì API không trả lỗi mà xếp hàng: độ trễ lên vài giây, và k6 phải bỏ iteration (`dropped_iterations`) vì hết VU chờ.

## Điều kiện đo

- **Máy đo**: Windows 11, 12 luồng CPU, Docker Desktop 29.6.1, k6 2.2.0 chạy thẳng trên máy (không trong container).
- **API**: `deploy/compose.loadtest.yml`, cùng `deploy/api.Dockerfile` và lệnh với prod (`uvicorn`, 1 worker), mọi nguồn `stat`, giới hạn 2 CPU / 1 GB.
- **Postgres** 18.6 cùng compose, giới hạn 2 CPU / 1 GB. Trên prod, DB nằm ngoài VPS, nên prod có thêm độ trễ mạng tới DB mà bài đo này không có.
- **Dữ liệu**: `uv run python -m tools.loadtest_seed --facts 5600 --seed 342`, một snapshot `published`.
- **Kịch bản**: `loadtest/k6/baseline.js`, mỗi iteration một request, endpoint chọn theo trọng số (toàn cảnh 25, người mới 20, thành phố 20, tỷ lệ kỹ năng 15, kỹ năng qua vai trò 15, từ vựng 5).

## Smoke

`SCENARIO=smoke`: 120 request (119 URL của kịch bản + 1 của `setup`), 100% trả 200. Một người dùng: trung vị 11,9 ms, p95 17 ms.

## Thời gian từng endpoint khi chỉ một request một lúc

30 lần mỗi endpoint, tuần tự, sau một lần làm nóng.

| Endpoint | Trung vị | p90 | Cỡ response |
|---|---|---|---|
| `market-overview` | 45,8 ms | 56,8 ms | 40,4 KB |
| `newcomer-roles` | 14,4 ms | 16,5 ms | 9,4 KB |
| `city-shares` | 14,8 ms | 17,1 ms | 12,1 KB |
| `skill-rates` | 15,8 ms | 16,9 ms | 2,6 KB |
| `skill-roles` | 14,6 ms | 16,6 ms | 5,8 KB |
| `skills` (không đọc DB) | 5,1 ms | 6,4 ms | 30,3 KB |

Tính theo trọng số của kịch bản: trung bình ≈ 22 ms một request. Một tiến trình Python (GIL) phục vụ được tối đa ≈ 1000 / 22 ≈ 45 RPS. Con số này khớp với trần đo được.

## Breakpoint (ramp)

`SCENARIO=breakpoint MAX_RPS=1000 DURATION=5m`: dừng sau 32 giây vì `p(95)<200` vượt ngưỡng. Lúc dừng, tải đặt khoảng 115 RPS, nhưng API chỉ phục vụ trung bình 30 RPS, p95 8,58 s, 468 iteration bị bỏ.

Ramp tăng 3,3 RPS mỗi giây, nhanh hơn tốc độ p95 cộng dồn phản ứng, nên lần ramp này chỉ cho thấy trần nằm dưới 115 RPS. Con số chính xác lấy từ các lượt tốc độ cố định bên dưới.

## Tốc độ cố định (60 giây mỗi lượt)

Đặt `START_RPS = MAX_RPS`. Các mức được chạy theo thứ tự xáo trộn, nghỉ 10–15 giây giữa hai lượt.

| Tải đặt | Lượt | Trung vị | p95 | RPS đạt | Bỏ |
|---|---|---|---|---|---|
| 20 | 2 | 15–16 ms | 51–57 ms | 20,0 | 0 |
| 25 | 2 | 15 ms | 57 ms | 25,0 | 0 |
| 30 | 2 | 14–15 ms | 56–57 ms | 30,0 | 0 |
| 35 | 1 | 16 ms | 60 ms | 34,9 | 0 |
| 40 | 1 | 16 ms | 61 ms | 40,0 | 0 |
| 50 | 2 | 31–270 ms | 0,37–1,02 s | 49,9 | 0 |
| 60 | 2 | 0,32–2,6 s | 0,83–4,65 s | 47,4–57,8 | 0–152 |
| 70 | 2 | 2,9–3,8 s | 4,6–6,1 s | 49,7–54,0 | 203–274 |
| 80 | 1 | 4,3 s | 7,7 s | 50,1 | 425 |

Có hai lượt bị loại vì nhiễu của máy, ghi lại để minh bạch. Cả hai nằm trong loạt đầu (20 → 30 → 40) chạy ngay sau lần ramp:

- một lượt 30 RPS sụp: p95 4,77 s, chỉ đạt 24,5 RPS, bỏ 38 iteration;
- một lượt 40 RPS có p95 386 ms.

Bảng trên dùng lượt 20 RPS của loạt đó cùng các lượt lặp sau. Các lượt lặp ở 20–40 RPS đều ổn định quanh p95 ≈ 60 ms.

## Tài nguyên trong lúc quá tải

Lấy mẫu mỗi 2 giây bằng `docker stats` và `pg_stat_activity` trong lần ramp:

- **API**: CPU 113–155% trên giới hạn 200%. Một tiến trình Python chỉ chạy mã Python trên một core một lúc (GIL); phần trên 100% là I/O của psycopg và luồng của threadpool.
- **Postgres**: CPU 10–33%.
- **Kết nối DB**: lên 15–16, đúng trần pool mặc định của SQLAlchemy (5 + 10 overflow). Request chờ kết nối từ pool là một nguồn xếp hàng thứ hai, sau CPU.

## Bước tiếp theo gợi ý (mỗi bước đo lại bằng cùng kịch bản)

1. **Cache response theo `snapshot_id`** trong tiến trình (bytes JSON đã serialize). Request cache hit không đọc DB và không dựng model Pydantic. Kỳ vọng tăng nhiều nhất vì `market-overview`, endpoint nặng nhất, trả cùng một kết quả cả ngày.
2. **Nhiều worker** (`gunicorn -k uvicorn.workers.UvicornWorker -w 2` trên 2 CPU) để thoát giới hạn một core của GIL.
3. **Pool kết nối và PgBouncer**: chỉnh khi có nhiều worker, để tổng số kết nối không vượt sức chịu của Postgres.
4. **Header `Cache-Control`/`ETag`**, rồi đo lại qua CDN.
