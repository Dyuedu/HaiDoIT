# Feature Specification: TopDev thử lại khi rớt kết nối

**Feature Branch**: `gh-296-298-crawler-ben`

**Created**: 2026-11-15

**Status**: Code xong, test xanh.

**Input**: GitHub issue [#298](https://github.com/Dyuedu/HaiDoIT/issues/298) — Retry a TopDev listing page after a dropped connection.

## Bối cảnh

TopDev đi khoảng 336 trang listing mỗi đêm (26–29 phút). Ngày 13/11, ở khoảng trang 125, một `ConnectionResetError(104, 'Connection reset by peer')` làm `walk_listing` dừng; TopDev bị ghi là chưa xong và snapshot `2026-11-13` chốt `partial` ("nguồn lỗi: topdev"). `fetch_results_page` đã thử lại khi site trả "0 kết quả", nhưng chưa thử lại khi mất kết nối.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Rớt kết nối một lần không làm mất cả lượt (Priority: P1)

**Why this priority**: AC thứ nhất và thứ năm. Đây là lỗi ngày 13/11.

**Independent Test**: `tests/test_observations.py`, client giả ném `ConnectionError` ở trang 2 vài lần rồi trả bình thường.

**Acceptance Scenarios**:

1. **Given** trang 2 rớt kết nối 2 lần rồi trả trang, **When** crawler chạy, **Then** lượt đủ, có tin của trang 2, và hai lần chờ là `CONNECT_WAIT` rồi `2 × CONNECT_WAIT`.
2. **Given** trang 2 timeout một lần, **When** crawler chạy, **Then** lượt đủ.

---

### User Story 2 - Hết lượt thử thì ghi chưa xong như cũ (Priority: P1)

**Why this priority**: AC thứ hai và thứ năm.

**Acceptance Scenarios**:

1. **Given** trang 2 rớt kết nối mãi, **When** crawler chạy, **Then** trang 2 được gọi đúng `CONNECT_TRIES` lần, lượt chưa xong, `error` có "Connection reset".

---

### User Story 3 - Bị từ chối thì không thử lại (Priority: P1)

**Why this priority**: AC thứ ba, luật lịch sự.

**Acceptance Scenarios**:

1. **Given** trang 2 gây `BlockedError`, **When** crawler chạy, **Then** trang 2 chỉ được gọi một lần và không có lần chờ nào.

---

### User Story 4 - Mỗi lần thử lại có log (Priority: P2)

**Why this priority**: AC thứ tư.

**Acceptance Scenarios**:

1. **Given** trang 2 rớt kết nối, **When** thử lại, **Then** log có URL trang và `attempt N/CONNECT_TRIES`.

### Edge Cases

- Chờ tối đa 30 + 60 + 120 = 210 giây cho một trang trước khi bỏ cuộc; lượt đêm vẫn kết thúc trước 03:30 trong trường hợp xấu nhất có một trang như vậy.
- Lỗi HTTP 5xx (`HTTPError`) không thuộc phạm vi issue, vẫn dừng lượt như cũ.
- Vòng tải chi tiết đã có cơ chế bỏ qua lỗi riêng, không đổi.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `get_listing_page()` gọi `client.get` tối đa `CONNECT_TRIES` (4) lần khi gặp `requests.ConnectionError`, `requests.Timeout`, `ChunkedEncodingError`.
- **FR-002**: Lần chờ thứ n là `CONNECT_WAIT × 2^(n−1)` giây (`CONNECT_WAIT` = 30).
- **FR-003**: Hết lượt thử thì ném lại lỗi cuối; `main` ghi lượt chưa xong như cũ.
- **FR-004**: `BlockedError` không bị bắt trong `get_listing_page()`.
- **FR-005**: `fetch_results_page()` dùng `get_listing_page()`; cơ chế thử lại "0 kết quả" giữ nguyên.

## Success Criteria *(mandatory)*

- **SC-001**: `python -m pytest tests -q` trong `scraper/` xanh.
- **SC-002**: Đêm nào có rớt kết nối, log có dòng `attempt 1/4 failed, retrying` và TopDev vẫn `complete=True`.
