# Feature Specification: MoMo bỏ qua trang chi tiết 404

**Feature Branch**: `gh-296-298-crawler-ben`

**Created**: 2026-11-15

**Status**: Code xong, test xanh.

**Input**: GitHub issue [#297](https://github.com/Dyuedu/HaiDoIT/issues/297) — Skip a MoMo detail page that answers 404 instead of stopping.

## Bối cảnh

Ngày 05/11 và 14/11, listing MoMo thấy 40 tin nhưng một trang chi tiết trả 404 (`STOP -- 404 Client Error ... infrastructure-security-engineer-ii-cloud-devsecops-16804`). Vòng tải chi tiết của `crawlers/momo.py` bắt `requests.RequestException` ở ngoài vòng `for`, nên một lỗi là dừng hết. Crawler xóa `data/raw/momo.jsonl` đầu mỗi lượt, nên file chỉ còn 5 tin và dedupe, extract đêm đó mất 35 tin MoMo. File seen vẫn đủ 40 tin vì được ghi trước vòng chi tiết.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Một trang chi tiết lỗi không làm mất các tin còn lại (Priority: P1)

**Why this priority**: AC thứ nhất và thứ tư. Đây là lỗi đã xảy ra hai đêm.

**Independent Test**: `tests/test_observations.py`, listing được stub, client HTTP giả trả 404 cho một trang.

**Acceptance Scenarios**:

1. **Given** listing có 3 tin và trang thứ hai trả 404, **When** crawler chạy, **Then** `momo.jsonl` có tin thứ nhất và thứ ba, log có URL của trang 404.

---

### User Story 2 - Bị site từ chối thì vẫn dừng (Priority: P1)

**Why this priority**: AC thứ hai, luật lịch sự của dự án.

**Acceptance Scenarios**:

1. **Given** trang thứ hai gây `BlockedError` (403, 429, robots, captcha), **When** crawler chạy, **Then** dừng ngay, không tải trang thứ ba.

---

### User Story 3 - Dòng cuối nói rõ lưu bao nhiêu, bỏ qua bao nhiêu (Priority: P2)

**Why this priority**: AC thứ ba. Người đọc log đêm thấy ngay đêm nào thiếu tin.

**Acceptance Scenarios**:

1. **Given** một trang 404 trong ba trang, **When** crawler xong, **Then** dòng cuối là `saved 2 jobs to ..., skipped 1`.

### Edge Cases

- Mất mạng hẳn: mỗi trang lỗi mất tới 30 giây timeout. Sau `MAX_CONSECUTIVE_FAILURES` (10) trang lỗi liền nhau thì dừng, như `topdev.py` đang làm, để không treo cả lượt đêm.
- Trang không có `__NEXT_DATA__`: vẫn bỏ qua như cũ, giờ được tính vào `skipped`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `requests.RequestException` khi tải một trang chi tiết được bắt trong vòng lặp: in `detail <url>: <lỗi>`, tăng `skipped`, sang trang kế.
- **FR-002**: `BlockedError` dừng vòng tải chi tiết.
- **FR-003**: `MAX_CONSECUTIVE_FAILURES` lỗi liền nhau thì in `STOP -- N details failed in a row` và dừng. Một trang thành công đặt lại bộ đếm.
- **FR-004**: Dòng cuối: `saved {total} jobs to {out}, skipped {skipped}`.

## Success Criteria *(mandatory)*

- **SC-001**: `python -m pytest tests -q` trong `scraper/` xanh.
- **SC-002**: Đêm sau có tin MoMo bị gỡ, log có dòng `detail ...: 404` và số tin lưu bằng số listed trừ số bỏ qua.

## Assumptions

- `PoliteClient._check_response` gọi `raise_for_status()`, nên 404 thành `requests.HTTPError`, là một `RequestException`; còn 403, 429 thành `BlockedError` (lớp con của `RuntimeError`), không bị bắt nhầm.
