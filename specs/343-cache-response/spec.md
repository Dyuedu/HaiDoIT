# Feature Specification: Cache response của API thị trường, xóa theo snapshot

**Feature Branch**: `gh-343-cache-response`

**Created**: 2026-11-23

**Status**: Xong (chờ review)

**Input**: GitHub issue [#343](https://github.com/Dyuedu/HaiDoIT/issues/343) — Cache market API responses in process, invalidated by snapshot.

## Bối cảnh

Baseline của #342: API giữ được 40 RPS với p95 < 200 ms, trần khoảng 50–58 RPS. Nút thắt là CPU của tiến trình Python duy nhất: mỗi request đọc bảng `stat_*` rồi dựng và serialize model Pydantic, dù câu trả lời chỉ đổi khi có snapshot mới được chốt (mỗi đêm một lần).

Issue này giữ response 200 trong RAM của tiến trình. Người dùng chọn cách kiểm tra snapshot **ở mỗi request** (một query nhỏ trên bảng `snapshots`) thay vì kiểm tra định kỳ. Nhờ vậy, mọi AC "snapshot đọc được mới nhất" của #145, #146, #151, #163, #168, #280, #328 vẫn đúng nguyên văn: snapshot mới được phục vụ ngay ở request kế tiếp.

Đây là task (`type:chore`). "Người dùng" trong các scenario là người gọi API.

## User Scenarios & Testing

### Kịch bản 1 - Trả lời lặp lại từ cache (Priority: P1)

**Acceptance Scenarios** (AC 1):

1. **Given** cache bật, **When** gọi cùng một `GET /api/v1/...` hai lần, **Then** lần đầu có `x-cache: MISS`, lần hai `x-cache: HIT`, cùng bytes và `content-type`, nguồn chỉ bị gọi một lần.
2. **Given** hai URL chỉ khác thứ tự tham số, **When** gọi lần lượt, **Then** lần hai là `HIT`.
3. **Given** hai URL khác giá trị tham số, **When** gọi lần lượt, **Then** cả hai là `MISS`.

### Kịch bản 2 - Snapshot mới lên ngay (Priority: P1)

**Acceptance Scenarios** (AC 2):

1. **Given** cache bật, **When** gọi 3 request, **Then** `version()` của nguồn được hỏi 3 lần.
2. **Given** `version()` đổi giữa hai request, **When** gọi lại, **Then** request kế tiếp là `MISS` và nguồn được gọi lại.
3. **Given** DB có snapshot D-1 đã công bố và response đã nằm trong cache, **When** chốt snapshot D rồi gọi lại, **Then** request kế tiếp là `MISS` và `meta.snapshot_date` là D. (Postgres)
4. **Given** mở một snapshot mới (`open`), **When** hỏi `StatMarket.version()`, **Then** dấu không đổi. Chốt một snapshot thì dấu đổi. (Postgres)

### Kịch bản 3 - Không giữ dữ liệu người dùng gõ (Priority: P1)

**Acceptance Scenarios** (AC 3):

1. **Given** request có `have` (`skill-rates`, `learning-path`) hoặc `title` (`role-for-title`), **When** gọi hai lần, **Then** không response nào có `x-cache`.
2. **Given** đã gọi `role-for-title?title=Secret Title` và `skill-rates?...&have=python`, **When** xem các khóa trong cache, **Then** không khóa nào chứa chức danh hay `have`.

### Kịch bản 4 - Lỗi không vào cache (Priority: P1)

**Acceptance Scenarios** (AC 4):

1. **Given** request trả 404 `unknown_cell`, 404 `unknown_skill` hoặc 422, **When** gọi ba lần, **Then** không lần nào là `HIT`.
2. **Given** `version()` ném lỗi (DB không trả lời), **When** gọi, **Then** request đi thẳng vào route như khi không có cache, không có header `x-cache`.
3. **Given** đường dẫn ngoài `/api/v1/` (`/openapi.json`) hoặc method khác `GET`, **When** gọi, **Then** không đi qua cache.

### Kịch bản 5 - Bật bằng biến môi trường, có trần (Priority: P1)

**Acceptance Scenarios** (AC 5):

1. **Given** không đặt `HAIDO_RESPONSE_CACHE`, **When** dựng app, **Then** cache tắt.
2. **Given** `HAIDO_RESPONSE_CACHE=on`, **When** dựng app, **Then** cache bật.
3. **Given** `compose.prod.yml`, **Then** `HAIDO_RESPONSE_CACHE` là `on`. `compose.local.yml` (smoke của CI) không đặt. `compose.loadtest.yml` mặc định `on` và tắt được qua biến.
4. **Given** trần 2 mục, **When** lưu 3 URL, **Then** URL dùng lâu nhất bị bỏ, cache không quá 2 mục.

### Kịch bản 6 - Đo lại (Priority: P1)

**Acceptance Scenarios** (AC 6):

1. **Given** API chạy bằng `compose.loadtest.yml` với cache bật, **When** chạy lại kịch bản của #342, **Then** `ket-qua-do.md` ghi RPS cao nhất còn giữ p95 < 200 ms, so với baseline 40 RPS.

### Edge Cases

- Snapshot đổi trong lúc route đang chạy: response tính xong có thể là số cũ, nên không được lưu (`put` so version).
- Nhiều request cùng `MISS` một khóa ngay sau khi snapshot đổi: mỗi request tự tính (chưa có single-flight). Chấp nhận ở bước này vì chỉ xảy ra một lần mỗi đêm.
- Mỗi worker có cache riêng. Khi chạy nhiều worker (bước sau), mỗi worker `MISS` một lần cho mỗi khóa.

## Requirements

- **FR-1**: Khóa cache là (đường dẫn, tham số đã sắp theo tên). Giữ thứ tự giữa các giá trị cùng tên.
- **FR-2**: Dấu version của `StatMarket` lấy từ mọi snapshot khác `open`: số dòng cùng md5 của ngày, trạng thái và lúc chốt.
- **FR-3**: Request trúng cache gửi nguyên status, header, body đã lưu, cộng `x-cache: HIT`.
- **FR-4**: Trần mặc định 1024 mục, bỏ theo LRU.

## Success Criteria

- **SC-1**: RPS giữ p95 < 200 ms cao hơn baseline 40 RPS của #342, số ghi trong `ket-qua-do.md`.
- **SC-2**: Không test cũ nào phải sửa.
