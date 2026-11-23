# Research: Kịch bản đo tải với k6

## Repo tham khảo

### 1. grafana/quickpizza — bộ ví dụ k6 chính thức

- **Link**: https://github.com/grafana/quickpizza/tree/8807687aaa7dd8b90c54f0d200cca72493870ca8/k6/foundations
- **Cách làm**: Chuỗi script từ cơ bản tới nâng cao. `07.scenarios.js` có kịch bản `smoke` (`constant-vus`, 1 VU) và `stress` trong cùng file. `08.arrival-rate.js` dùng `constant-arrival-rate`, không `sleep`, để tốc độ iteration bằng RPS. `09.data.js` đọc dữ liệu bằng `SharedArray` + `open()`. Ngưỡng `http_req_failed`, `http_req_duration p(95)`.
- **Lấy gì**: Mô hình open model (arrival-rate) thay vì closed model (VU + sleep), vì mục tiêu đo bằng RPS. Một iteration một request, không `sleep`. Đọc tham số từ file JSON bằng `SharedArray`. Hàm `setup()` gọi thử trước, hỏng thì dừng.
- **Không lấy**: `handleSummary` import `k6-summary` từ jslib.k6.io (cần mạng lúc chạy). Thay bằng web dashboard có sẵn của k6 (`K6_WEB_DASHBOARD_EXPORT`) để có biểu đồ RPS và độ trễ theo thời gian. `console.log` mỗi request (làm chậm k6 ở RPS cao).

### 2. Tài liệu breakpoint của k6 (Grafana learning path "Find system limits with k6")

- **Link**: https://grafana.com/docs/learning-paths/find-k6-limits/build-breakpoint-script/ và https://grafana.com/docs/k6/latest/testing-guides/test-types/breakpoint-testing/
- **Cách làm**: Breakpoint test tăng tải liên tục kể cả khi hệ thống đã xuống cấp, nên dùng `ramping-arrival-rate`. Hai ngưỡng `abortOnFail` (độ trễ và tỷ lệ lỗi) kèm `delayAbortEval` 30 giây để không dừng vì nhiễu lúc đầu. Khuyên tắt autoscaling và dùng môi trường riêng.
- **Lấy gì**: Cả cấu trúc kịch bản `breakpoint`: `ramping-arrival-rate`, `preAllocatedVUs`/`maxVUs`, `abortOnFail` + `delayAbortEval`. Theo dõi `dropped_iterations`: k6 không đủ VU để giữ tốc độ cũng là dấu hiệu chạm trần (grafana/k6#2837).
- **Không lấy**: Mốc 200 iteration/giây của ví dụ; Hải Đồ đặt trần qua biến `MAX_RPS`.

### 3. luketn/docker-k6-grafana-influxdb — k6 + InfluxDB + Grafana trong compose

- **Link**: https://github.com/luketn/docker-k6-grafana-influxdb/tree/4c8ec1876c28a9fbea9fe3d31a1d263745b82f83
- **Cách làm**: Compose dựng InfluxDB 1.8 và Grafana, k6 chạy trong container và đẩy số qua `K6_OUT=influxdb=...`.
- **Không lấy (lúc này)**: Thêm hai dịch vụ chỉ để xem biểu đồ, trong khi web dashboard có sẵn của k6 đã đủ cho baseline. Bước quan sát (Prometheus + Grafana) để sau, khi có nhiều pod. Chạy k6 trong container trên Docker Desktop thêm một lớp mạng ảo; k6 chạy thẳng trên máy thì số đo ít nhiễu hơn.

## Kết luận

Kịch bản `baseline.js` theo quickpizza (smoke + arrival-rate, một request mỗi iteration, tham số từ JSON) và theo hướng dẫn breakpoint của k6 (`ramping-arrival-rate`, `abortOnFail`). Biểu đồ lấy từ web dashboard có sẵn, chưa dựng InfluxDB/Grafana.
