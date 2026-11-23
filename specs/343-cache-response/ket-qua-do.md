# Kết quả đo lại với cache (#343) — 2026-11-23

## Kết luận

| | Baseline (#342) | Có cache (#343) |
|---|---|---|
| RPS cao nhất còn giữ p95 < 200 ms, 0 lỗi | 40 | **300** (k6 trên Windows) / **330** (k6 trong mạng Docker) |
| Trung vị / p95 ở mức đó | 15 ms / 60 ms | 2,6 ms / 3,7 ms |
| CPU của API ở mức đó | ~115% | ~48% |
| Tỷ lệ cache hit | — | 100% |
| Nút thắt kế tiếp | CPU của tiến trình Python | **Pool kết nối DB mở và đóng kết nối liên tục** |

Cache tăng sức chịu khoảng **7,5 lần**. Còn cách mục tiêu 5k RPS khoảng 15 lần.

## Điều kiện đo

Như [#342](../342-do-tai-baseline/ket-qua-do.md): cùng máy, cùng dữ liệu (5.600 tin, seed 342), cùng kịch bản. API build lại với `HAIDO_RESPONSE_CACHE=on`. Script k6 thêm chỉ số `cache_hit` (tỷ lệ response có `x-cache: HIT`).

`smoke`: 119/119 URL trả 200.

## Tốc độ cố định (60 giây mỗi lượt, k6 trên Windows qua `127.0.0.1:8001`)

| Tải đặt | Lượt | Trung vị | p95 | RPS đạt | Bỏ | Hit |
|---|---|---|---|---|---|---|
| 200 | 2 | 2,7–2,9 ms | 3,7–3,8 ms | 200 | 0 | 100% |
| 300 | 3 | 2,6 ms | 3,7–64 ms | 300 | 0 | 100% |
| 330 | 2 | 0,8–2,7 s | 4,7–5,6 s | 230–245 | 1311–1566 | |
| 350 | 1 | 383 ms | 4,36 s | 264 | 1332 | |
| 360 | 2 | 2,6 ms–1,2 s | 0,83–6 s | 249–338 | 295–1743 | |
| 400 | 2 | 4,2–4,3 s | 9,1–9,6 s | 209 | ~3070 | 100% |
| 500 | 1 | 6,4 s | 11,7 s | 218 | 5987 | 100% |

p95 64 ms ở lượt 300 RPS đầu tiên là lúc cache còn nguội. Hai lượt 300 RPS sau đều 3,7 ms.

## k6 chạy trong mạng Docker (gọi thẳng `api:8000`)

Để loại lớp chuyển cổng của Docker Desktop khỏi phép đo: `docker run --network haido-loadtest_default grafana/k6:2.2.0`, giới hạn 4 CPU cho k6.

| Tải đặt | Lượt | Trung vị | p95 | RPS đạt | Bỏ |
|---|---|---|---|---|---|
| 330 | 2 | 1,9–2,0 ms | 2,6–3,0 ms | 330 | 0 |
| 400 | 2 | 3,5–3,8 s | 8,0–8,1 s | 231–234 | ~2700 |
| 500 | 1 | 5,8 s | 11 s | 227 | 5700 |

Lớp chuyển cổng chỉ làm trần thấp đi khoảng 10%. Cú sụp ở 400 RPS nằm ở API.

## Quá tải thì thông lượng giảm, không chỉ chững lại

Từ khoảng 330–400 RPS, API không giữ được mức ~300 mà tụt xuống ~210–245 RPS, độ trễ vài giây. Đây là **congestion collapse**: quá tải làm mỗi request tốn hơn, nên phục vụ được ít hơn cả lúc chưa quá tải.

## Vì sao: pool kết nối mở và đóng liên tục

| | 300 RPS | 400 RPS |
|---|---|---|
| CPU của API | ~48% | ~195% (hết 2 core) |
| CPU của Postgres | ~14% | 70–98% |
| Phiên Postgres mới / request | **40,4%** (2645 / 6548) | **48,6%** (3039 / 6258) |

Đếm bằng `pg_stat_database.sessions` trước và sau mỗi lượt 45 giây, k6 trong mạng Docker.

`make_read_engine` dùng pool mặc định của SQLAlchemy: 5 kết nối thường trực, cho thêm tối đa 10 kết nối overflow, và **đóng hẳn kết nối overflow khi trả về pool**. Request đến không đều (k6 mở iteration thành cụm), nên số request đồng thời thường xuyên vượt 5. Mỗi lần vượt, pool mở một kết nối mới rồi đóng ngay, tức Postgres fork một backend mới. Tới 400 RPS, chi phí này cộng với hàng đợi tạo vòng xoáy: chậm hơn thì đồng thời nhiều hơn, thì mở nhiều kết nối hơn, thì càng chậm.

Cache làm vấn đề lộ rõ hơn, vì `version()` chạm DB ở mỗi request (đúng lựa chọn giữ AC "snapshot mới nhất" nguyên văn). Nhưng gốc rễ là cấu hình pool, đã có từ trước #343.

## Bước tiếp theo gợi ý (mỗi bước đo lại bằng cùng kịch bản)

1. **Pool kết nối cố định** trong `make_read_engine`: giữ đủ kết nối thường trực cho số luồng có thể chạm DB cùng lúc, không overflow, để không còn mở và đóng kết nối theo từng request. Đo lại số phiên mới / request, kỳ vọng gần 0.
2. **Kiểm tra snapshot không tốn query mỗi request mà AC vẫn đúng nguyên văn**: Postgres `LISTEN/NOTIFY`. Bước `publish` gửi `NOTIFY`, API nghe và xóa cache ngay. Request trúng cache khi đó không chạm DB.
3. **Nhiều worker** (2 worker cho 2 CPU), sau khi pool đã ổn định.
4. **Chống quá tải** (giới hạn số request đồng thời, trả 503 sớm) để quá tải không biến thành congestion collapse.
