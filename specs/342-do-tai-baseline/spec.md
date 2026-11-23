# Feature Specification: Đo sức chịu tải baseline của API bằng k6

**Feature Branch**: `gh-342-do-tai-baseline`

**Created**: 2026-11-23

**Status**: Xong (chờ review)

**Input**: GitHub issue [#342](https://github.com/Dyuedu/HaiDoIT/issues/342) — Measure the API's baseline throughput with a k6 load test.

## Bối cảnh

Nhóm đang học thiết kế hệ thống cho mốc 10k người dùng đồng thời và 5k RPS. Trước khi thêm cache, nhiều worker, PgBouncer, CDN hay Kubernetes, cần một con số gốc: cấu hình hiện tại (một container `uvicorn` một worker, mỗi request đọc Postgres, không cache) chịu được bao nhiêu RPS trước khi chậm hoặc lỗi, và nút thắt đầu tiên nằm ở đâu. Mỗi bước tối ưu sau sẽ đo lại bằng cùng kịch bản này.

Đây là task (`type:chore`), không có người dùng cuối. "Người dùng" trong các scenario là thành viên nhóm chạy bài đo.

## User Scenarios & Testing

### Kịch bản 1 - Dựng dữ liệu đo (Priority: P1)

Thành viên nhóm chạy một lệnh để có DB local chứa một snapshot đã công bố, cỡ gần bằng production, sinh qua các bước thật của kho.

**Independent Test**: `tests/tools/test_gh342_loadtest_seed.py` seed vào DB `_test` rồi gọi API ở chế độ `stat`.

**Acceptance Scenarios** (AC 1):

1. **Given** một DB Postgres local tên kết thúc bằng `_test`, **When** chạy `tools/loadtest_seed.py --facts N`, **Then** DB có đúng một snapshot `published`, sinh bởi `lifecycle`, `aggregate`, `publish` thật.
2. **Given** DB vừa seed, **When** API đọc nguồn `stat` gọi mọi endpoint trong kịch bản k6, **Then** mọi endpoint trả 200.
3. **Given** URL trỏ tới host ngoài danh sách local hoặc DB tên không kết thúc bằng `_test`, **When** chạy seed, **Then** tool từ chối và không đụng vào DB.

### Kịch bản 2 - Chạy API giống production (Priority: P1)

**Independent Test**: `tests/deploy/test_gh342_do_tai_baseline.py` so `deploy/compose.loadtest.yml` với `deploy/compose.prod.yml`.

**Acceptance Scenarios** (AC 2, AC 4):

1. **Given** `compose.loadtest.yml`, **When** đọc service `api`, **Then** nó build từ `deploy/api.Dockerfile`, không ghi đè `command` hay `entrypoint`, nên chạy cùng lệnh `uvicorn` với production.
2. **Given** mọi khóa trong `SOURCE_ENV`, **When** đọc môi trường của `api`, **Then** khóa nào cũng là `stat`.
3. **Given** service `api`, **When** đọc giới hạn tài nguyên, **Then** CPU là 2 như VPS.
4. **Given** mọi service, **When** đọc `ports`, **Then** cổng nào cũng chỉ mở trên `127.0.0.1`.
5. **Given** healthcheck của `api`, **When** so với production, **Then** hai lệnh giống nhau.

### Kịch bản 3 - Kịch bản k6 (Priority: P1)

**Independent Test**: cùng file test của kịch bản 2, đọc `loadtest/k6/baseline.js` và `loadtest/k6/params.json`.

**Acceptance Scenarios** (AC 3, AC 4):

1. **Given** `baseline.js`, **When** lấy mọi đường dẫn `/api/v1/...` trong script, **Then** đường dẫn nào cũng có trong OpenAPI của app.
2. **Given** `params.json`, **When** đọc vai trò, cấp bậc, kỹ năng, **Then** mỗi mã đều có trong `config/rules.toml` hoặc bộ từ vựng kỹ năng.
3. **Given** `baseline.js`, **When** đọc `options`, **Then** có kịch bản `smoke` và kịch bản `breakpoint` dùng `ramping-arrival-rate`, và ngưỡng p95 cùng tỷ lệ lỗi có `abortOnFail`.

### Kịch bản 4 - Ghi baseline (Priority: P1)

**Acceptance Scenarios** (AC 5):

1. **Given** API chạy bằng `compose.loadtest.yml` trên DB đã seed, **When** chạy kịch bản `breakpoint`, **Then** `ket-qua-do.md` ghi RPS cao nhất còn giữ p95 < 200 ms và lỗi < 0,1%, cùng nút thắt đầu tiên thấy được (CPU của API, kết nối DB, hay CPU của Postgres).

### Edge Cases

- k6 chạy cùng máy với API: k6 tranh CPU. API bị giới hạn 2 CPU; máy đo có 12 luồng, nên k6 không làm nghẽn API. Kết quả ghi rõ điều kiện này.
- Ở chế độ `stat`, `/api/v1/learning-path` luôn trả 404 `unknown_cell` (chờ #216). Kịch bản không gọi endpoint này, nếu không nó sẽ bị tính là lỗi.
- Không bắn tải vào production hay qua Nginx Proxy Manager của VPS.

## Requirements

- **FR-1**: Seed chỉ chạy trên host local và DB tên kết thúc bằng `_test` (dùng lại `validate_migration_target`).
- **FR-2**: Mỗi iteration của k6 là đúng một request, nên tốc độ iteration bằng RPS.
- **FR-3**: Mỗi request gắn tag `name` theo endpoint để xem độ trễ từng endpoint.
- **FR-4**: Ngưỡng của kịch bản `breakpoint`: `http_req_duration p(95)<200`, `http_req_failed rate<0.001`, cả hai `abortOnFail` với `delayAbortEval` 30 giây.

## Success Criteria

- **SC-1**: Một người mới chạy lại được bài đo từ README trong `loadtest/` mà không cần hỏi.
- **SC-2**: `ket-qua-do.md` có con số baseline và nút thắt, đủ để so với các bước tối ưu sau.
