# Feature Specification: ITnavi đi hết listing

**Feature Branch**: `gh-296-298-crawler-ben`

**Created**: 2026-11-15

**Status**: Code xong, test xanh. Đêm 16/11 đủ; đêm 17/11 trang rỗng tạm thời làm lượt chưa đủ, đã thêm tải lại (User Story 5). Còn chờ ba đêm liền trên VPS (AC cuối).

**Input**: GitHub issue [#296](https://github.com/Dyuedu/HaiDoIT/issues/296) — Keep walking the ITnavi listing past a page with no new id.

## Bối cảnh

Kiểm log lượt đêm 10–15/11 trên VPS: crawler ITnavi dừng ở trang 41, 28, 49, 49, 49, 39, số tin listed dao động 254–472, nhưng đêm nào cũng ghi `listing_complete=True`. Ingest vì thế coi các tin chưa tới là đã gỡ: 197 tin ngày 11/11, 120 tin ngày 15/11, phần lớn hôm sau "xuất hiện lại".

Nguyên nhân ở `crawlers/itnavi.py`: trang đầu tiên không có id mới là `break` và đặt `complete = True`. Quét thử ngày 15/11 cho thấy thứ tự listing xô lệch giữa các request (trang 9, 14, 17 chỉ có 9/10 id mới), và sau trang cuối site trả trang trống. Log không cho biết đêm nào dừng vì trang trống tạm thời, đêm nào vì trang trùng hết, nên spec chặn cả hai: chịu được vài trang trùng liên tiếp, và đối chiếu với tổng số tin site in trên trang ("485 Việc làm").

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Trang trùng giữa listing không kết thúc lượt quét (Priority: P1)

**Why this priority**: AC thứ ba. Đây là đường gây "gone" giả khi thứ tự listing xô lệch.

**Independent Test**: `tests/test_observations.py`, fake client có một trang toàn id cũ ở giữa.

**Acceptance Scenarios**:

1. **Given** trang 2 chỉ chứa id đã thấy ở trang 1 và trang 3 có id mới, **When** crawler chạy, **Then** id của trang 3 có trong file seen và `listing_complete` là `True`.
2. **Given** site lặp trang cuối mãi, **When** gặp `STALE_PAGES` trang liên tiếp không có id mới, **Then** lượt quét kết thúc và `listing_complete` là `True`.

---

### User Story 2 - Trang trống kết thúc listing, nhưng chỉ "đủ" khi gặp gần hết tổng số (Priority: P1)

**Why this priority**: AC thứ nhất và thứ hai. Chặn trường hợp trang trống tạm thời giữa listing.

**Independent Test**: fake client có `div.js-tab__show h1` ghi tổng số.

**Acceptance Scenarios**:

1. **Given** trang 3 trống và site ghi tổng 2 tin, đã gặp 2 tin, **When** crawler chạy, **Then** `listing_complete` là `True`.
2. **Given** site ghi tổng 100 tin và listing trống từ trang 2 khi mới gặp 2 tin, **When** crawler chạy, **Then** `listing_complete` là `False`, `error` ghi "met 2 of 100".
3. **Given** trang không ghi tổng số, **When** listing hết bằng trang trống, **Then** `listing_complete` là `True` và log ghi không thấy tổng.

---

### User Story 3 - Chạm trần số trang vẫn là lượt chưa xong (Priority: P2)

**Why this priority**: AC thứ tư, giữ hành vi cũ.

**Acceptance Scenarios**:

1. **Given** `--pages 2` và trang 3 còn tin, **When** crawler chạy, **Then** `listing_complete` là `False`, `error` ghi "hit --pages 2".

---

### User Story 4 - Ba đêm ổn định trên VPS (Priority: P2)

**Why this priority**: AC cuối, kiểm sau merge.

**Acceptance Scenarios**:

1. **Given** bản sửa đã deploy, **When** ba lượt đêm liền nhau chạy, **Then** số listed của ITnavi lệch nhau không quá 10% và "gone since last complete run" dưới 10% số listed. Số liệu ghi vào `tdd.md`.

### User Story 5 - Trang rỗng tạm thời được tải lại (Priority: P1)

**Why this priority**: đêm 17/11 trang 42 trả về không có tin khi mới gặp 380/485 tin; lượt ghi `listing_complete=False` và snapshot chốt `partial`. Sáng 17/11 quét lại thấy 49 trang đủ, 483/485 tin. Thuộc AC thứ nhất: chỉ coi là hết listing khi trang thực sự trống.

**Acceptance Scenarios**:

1. **Given** trang 2 trống ở lần tải đầu rồi có tin, **When** crawler chạy, **Then** trang 2 được tải 2 lần, tin của trang 2 và 3 có trong file seen, `listing_complete` là `True`.
2. **Given** trang 3 trống mãi, **When** crawler chạy, **Then** trang 3 được tải đúng `EMPTY_PAGE_TRIES` lần rồi mới kết thúc listing.

### Edge Cases

- Trang trùng làm tốn thêm tối đa `STALE_PAGES - 1` request mỗi đêm (3 giây/request), chấp nhận được.
- Tổng số trên trang có thể đổi giữa các trang trong một lượt; lấy giá trị lớn nhất gặp được.
- Bị chặn (`BlockedError`) giữa chừng vẫn là lượt chưa xong như cũ.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Trang không có thẻ `div.jsl-item[data-id]` được tải lại tới `EMPTY_PAGE_TRIES` (3) lần; vẫn trống thì kết thúc listing.
- **FR-002**: Trang có thẻ nhưng không có id mới chỉ tăng bộ đếm; `STALE_PAGES` (hằng số đầu module, mặc định 3) trang liên tiếp như vậy thì kết thúc listing. Trang có id mới đặt lại bộ đếm.
- **FR-003**: Khi listing kết thúc, đọc tổng từ `div.js-tab__show h1`; `complete` khi số id gặp ≥ `MIN_COVERAGE` (0,9) × tổng, ngược lại `error = "met X of Y listed jobs"`.
- **FR-004**: Không đọc được tổng thì `complete` và in cảnh báo.
- **FR-005**: Log ghi lý do kết thúc (trang trống hay N trang không có id mới).

## Success Criteria *(mandatory)*

- **SC-001**: `python -m pytest tests -q` trong `scraper/` xanh.
- **SC-002**: Ba đêm liền trên VPS đạt US4.

## Assumptions

- Thẻ tổng số "485 Việc làm" ở `div.js-tab__show h1` của mọi trang listing (kiểm ngày 15/11, trang 1 và 30).
- #88 sẽ chép crawler sang `haido_core/crawl` và mang bản sửa theo.
