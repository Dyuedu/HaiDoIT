# Feature Specification: ITviec nodriver path + queue/export fixes

**Feature Branch**: `gh-336-itviec-nodriver`

**Created**: 2026-11-20

**Status**: Done

**Input**: Issue #336 — ITviec crawler: add nodriver path, fix queue and export bugs

## User Scenarios & Testing

### Scenario 1 — Pipeline chạy đường nodriver mặc định (P1)

Lượt cron đêm gọi `pipeline.py crawl --sources itviec`. Trên Linux không có
DISPLAY thì pipeline bọc lệnh trong `xvfb-run`.

**Given** pipeline.py có `type: "nodriver"` cho itviec,
**When** `run_crawler("itviec", ...)` chạy trên Linux không có DISPLAY,
**Then** lệnh bắt đầu bằng `xvfb-run` và kết thúc bằng `-m crawlers.itviec`.

### Scenario 2 — Fallback Playwright qua `--playwright` (P1)

**Given** `crawlers/itviec.py` có cả `main()` (Playwright) lẫn `_nodriver_main()`,
**When** người dùng chạy `python -m crawlers.itviec --playwright`,
**Then** `main()` được gọi, test observation cũ vẫn pass.

### Scenario 3 — Tin đã có mô tả không bị cào lại (P2)

**Given** `data/raw/itviec.jsonl` có 500 tin có mô tả,
**When** lượt nodriver chạy listing và xếp 500 URL đó vào queue,
**Then** cả 500 được đánh dấu `COMPLETED` và `process_job_queue` không gửi request nào cho chúng.

### Scenario 4 — Mô tả rỗng → FAILED, không phải COMPLETED (P2)

**Given** một tin trong queue ở trạng thái PENDING,
**When** trang chi tiết trả về HTML không chứa JSON-LD hay mô tả,
**Then** tin được chuyển sang FAILED với `retry_count + 1`, không ghi vào `job_details`.

### Scenario 5 — FAILED được thử lại (P2)

**Given** một tin FAILED có `retry_count < MAX_RETRIES`,
**When** `queue_batch` được gọi,
**Then** tin đó nằm trong danh sách trả về, sau các tin PENDING.

**Given** một tin FAILED có `retry_count >= MAX_RETRIES` và `updated_at` cách đây > 7 ngày,
**When** `queue_batch` được gọi,
**Then** tin đó được lấy ra để thử lại.

### Scenario 6 — Export không ghi trùng (P2)

**Given** `itviec.jsonl` có dòng URL "a" chưa có mô tả và dòng URL "b" có mô tả,
**When** SQLite có chi tiết cho "a" (có mô tả) và "c" (có mô tả),
**Then** dòng "a" được thay tại chỗ, "b" giữ nguyên, "c" ghi nối. File có đúng 3 dòng.

### Scenario 7 — CI pass không cần nodriver (P1)

**Given** môi trường CI cài `requirements-vps.txt` (không có nodriver),
**When** pytest thu thập `test_observations.py`,
**Then** import thành công vì `nodriver` chỉ được import bên trong `_nodriver_main()`.

## Edge Cases

- Export khi SQLite rỗng (lượt đầu tiên): không xóa dòng cũ, ghi nối 0 dòng.
- Trình duyệt không khởi động được: `write_seen` vẫn ghi file rỗng để ingest không dùng dữ liệu hôm qua.
- `json.loads(qsk)` nhận `None` hoặc rỗng: trả `[]`.

## Requirements

- **FR-001**: `import nodriver` chỉ xảy ra bên trong `_nodriver_main()`.
- **FR-002**: `queue_batch` và `export_jsonl` ở cấp module, test được không cần nodriver.
- **FR-003**: `export_jsonl` ghi qua file `.tmp` + `os.replace` khi cần thay dòng, để crash không để file dở.
- **FR-004**: `pipeline.py` đặt itviec `type: "nodriver"`.

## Success Criteria

- CI scraper job: 0 fail.
- Lượt đêm trên VPS: itviec không partial vì lỗi code (Cloudflare vẫn có thể chặn, nhưng không phải lỗi của code).
