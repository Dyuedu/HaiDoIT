# Feature Specification: Trang listing TopCV rỗng thì thử lại sau, không dừng phân trang

**Feature Branch**: `gh-318-topcv-thu-lai-trang-trong`

**Created**: 2026-11-18

**Status**: Code xong, test xanh trên máy dev. Chưa merge, chưa deploy tay lên VPS.

**Input**: GitHub issue [#318](https://github.com/Dyuedu/HaiDoIT/issues/318) — Fetch an empty TopCV listing page again later instead of ending the walk.

## Bối cảnh

`daily-2026-11-18.log` trên VPS: từ trang 18 TopCV trả trang không có thẻ tin ngày càng dày (11 lần phải tải lại). Trang 41–44 mỗi trang cần 1–2 lần tải lại mới có tin; trang 45 rỗng cả 3 lần nên crawler (bản #302) coi là hết listing. Lượt dừng ở 2.169/2.502 tin, `complete=False`, snapshot 2026-11-18 chốt `partial; nguồn lỗi: topcv`. Đêm đó #296 phải đếm lại ba đêm ổn định.

Trang rỗng ở giữa listing không phải hết tin. Nguyên nhân nhiều khả năng là crawler đọc trang chậm quá sớm:

- Trang 24 đêm 18/11 chỉ có 22/50 thẻ, dấu hiệu đọc HTML khi danh sách mới tải được một phần.
- `fetch()` chờ thẻ đầu tiên tối đa 6 giây, hết thì ngủ 1,5 giây rồi đọc HTML. Thẻ đầu vừa hiện là đọc ngay, không chờ đủ thẻ.
- Tải lại ngay thường có tin (lần 2 hoặc 3), và listing đêm đó không gặp trang Cloudflare nào. Đêm 17/11 listing có 2 lần Cloudflare, qua được, không trang nào rỗng.

Chưa loại được khả năng TopCV trả trang "nhẹ" không có danh sách mà `is_challenge()` không nhận ra. Vì vậy issue gồm ba phần: thử lại trang rỗng sau (User Story 1–3), chờ trang tải xong và tải lại trang thiếu thẻ (User Story 5–6), lưu chẩn đoán (User Story 7).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Trang rỗng giữa listing được để lại và thử lại sau (Priority: P1)

**Why this priority**: AC 1 và 2. Đây là lỗi làm đêm 18/11 chốt `partial`.

**Independent Test**: `test_topcv_empty_page_in_the_middle_is_fetched_again_later`, `test_topcv_empty_tail_short_of_the_total_is_fetched_again_later`.

**Acceptance Scenarios**:

1. **Given** tiêu đề ghi 4 tin, mỗi trang 1 tin, trang 2 rỗng 3 lần đầu rồi có tin, **When** crawler chạy, **Then** trang 3 được quét trước lần tải thứ tư của trang 2, lượt thấy 4 tin và `complete`.
2. **Given** tiêu đề ghi 4 tin, trang 1–2 có tin, trang 3–4 rỗng 3 lần đầu rồi có tin (giống đêm 18/11: đuôi listing rỗng, thiếu so với tổng), **When** crawler chạy, **Then** trang 3–4 được tải lại sau khi nghỉ, lượt thấy 4 tin và `complete`.

---

### User Story 2 - Trang vẫn rỗng sau mọi vòng thì lượt chưa đủ (Priority: P1)

**Why this priority**: AC 3. Thiếu một trang giữa listing thì vòng đời sẽ coi tin của trang đó là đã gỡ.

**Independent Test**: `test_topcv_page_empty_in_every_round_makes_the_run_incomplete`, `test_topcv_page_empty_in_every_round_is_fetched_again_each_round`.

**Acceptance Scenarios**:

1. **Given** tiêu đề ghi 3 tin, trang 1 và 3 có tin, trang 2 rỗng mãi, **When** `main()` chạy, **Then** file seen có `listing_complete = false` và `error` có "pages still empty: 2".
2. **Given** như trên, **Then** trang 2 được tải `EMPTY_PAGE_TRIES × (1 + DEFERRED_ROUNDS)` lần.

---

### User Story 3 - Tiêu đề không có tổng (Priority: P2)

**Why this priority**: AC 4. Không có tổng thì không biết trang cuối.

**Independent Test**: `test_topcv_without_a_total_ends_after_empty_pages_in_a_row`.

**Acceptance Scenarios**:

1. **Given** không có tổng trên tiêu đề, trang 1 và 3 có tin, trang 2 rỗng 3 lần đầu rồi có tin, các trang sau rỗng, **When** crawler chạy, **Then** lượt đi qua trang 2, dừng sau `EMPTY_PAGES_IN_A_ROW` trang rỗng liền (trang cao nhất được tải là 6), thấy 3 tin và `complete`.

---

### User Story 4 - Các hành vi của #302 giữ nguyên (Priority: P1)

**Why this priority**: AC 5.

**Acceptance Scenarios** (test cũ, xanh trước và sau):

1. Trang bị chặn (Cloudflare hoặc tải lỗi) → lượt dừng, `complete = false` (`test_topcv_block_is_not_the_end_of_the_listing`).
2. Trang 1 rỗng → `([], False)` (`test_topcv_empty_first_page_is_not_a_complete_run`).
3. Hết listing với ít hơn 90% tổng → "met N of M" (`test_topcv_listing_short_of_the_listed_total_is_incomplete`).
4. Trang cuối bị lặp → dừng, `complete` (`test_topcv_repeated_last_page_ends_the_walk`).

---

### User Story 5 - Chỉ đọc trang khi thẻ tin đã đứng yên (Priority: P1)

**Why this priority**: AC 6. Sửa gốc của trang rỗng và trang thiếu thẻ.

**Independent Test**: `test_topcv_waits_until_the_cards_stop_growing`, `test_topcv_wait_for_cards_gives_up_after_the_timeout`.

**Acceptance Scenarios**:

1. **Given** số thẻ đếm được lần lượt 0, 10, 30, 50, 50, 50 và `readyState` từ `loading` sang `complete`, **When** `wait_for_cards` chạy, **Then** nó trả `(50, "complete")`, không trả ở lần đếm có thẻ đầu tiên.
2. **Given** trang không bao giờ có thẻ, **When** `wait_for_cards` chạy, **Then** nó trả số thẻ 0 sau `LISTING_WAIT` giây (cộng tối đa một nhịp `CARD_POLL`).

---

### User Story 6 - Trang thiếu thẻ được tải lại (Priority: P1)

**Why this priority**: AC 7. Trang 24 ngày 18/11 mất 28 tin mà lượt không biết.

**Independent Test**: `test_topcv_short_page_is_fetched_again`, `test_topcv_short_last_page_is_not_fetched_again`, `test_topcv_short_page_keeps_its_cards_when_it_stays_short`.

**Acceptance Scenarios**:

1. **Given** tổng 6, trang 1 có 2 thẻ, trang 2 lần đầu 1 thẻ rồi 2 thẻ, **When** crawler chạy, **Then** trang 2 được tải 2 lần, lượt thấy 6 tin và `complete`.
2. **Given** tổng 3, trang 1 có 2 thẻ, trang cuối (trang 2) có 1 thẻ, **Then** trang 2 chỉ tải 1 lần.
3. **Given** trang 2 thiếu thẻ mãi, **Then** thẻ của nó vẫn vào `seen`, và trang 2 được tải `EMPTY_PAGE_TRIES × (1 + DEFERRED_ROUNDS)` lần.

---

### User Story 7 - Lưu chẩn đoán trang rỗng hoặc thiếu thẻ (Priority: P2)

**Why this priority**: AC 8. Để biết chắc là trang chậm hay trang chặn.

**Independent Test**: `test_topcv_odd_page_is_saved_for_diagnosis`.

**Acceptance Scenarios**:

1. **Given** trang 2 rỗng lần đầu, **When** crawler chạy, **Then** `DEBUG_DIR/<ngày>/page-2-try-1.html` có đúng HTML lần tải đó, và log có dòng "Trang 2 lần 1: 0 thẻ" kèm thời gian tải, `readyState`, độ dài HTML, tiêu đề.

### Edge Cases

- Đêm bình thường (đi hết listing, thấy ≥ 90% tổng, không có trang rỗng kẹp giữa) không có vòng thử lại nào, không tốn thêm thời gian nghỉ.
- Trang làm lượt dừng (trang rỗng vượt trang cuối) có tin ở vòng thử lại: lượt đi tiếp từ trang sau nó.
- Đuôi listing vẫn rỗng sau các vòng thử lại: coi là hết listing; kiểm 90% tổng quyết định đủ hay chưa.
- Trang bị chặn khi đang thử lại: trang đó vẫn nằm trong danh sách rỗng, không dừng cả lượt.
- Trang bị chặn trong lượt đi: không có vòng thử lại.
- Trang cuối (theo tổng trên tiêu đề) ít thẻ là bình thường, không tải lại. Không có tổng thì không xét thiếu thẻ.
- Trang thiếu thẻ sau mọi vòng không làm lượt chưa đủ; kiểm 90% tổng quyết định.
- `wait_for_cards` chờ đủ `LISTING_WAIT` với trang hết listing thật (không có thẻ): thêm khoảng 20 giây mỗi trang rỗng thật ở cuối.
- Lưu HTML tối đa `DEBUG_MAX_FILES` (40) file mỗi lượt; thư mục ngày cũ hơn `DEBUG_KEEP_DAYS` (7) bị xoá đầu lượt. Lỗi ghi file chỉ in cảnh báo.

## Requirements *(mandatory)*

- **FR-001**: Trang vẫn rỗng sau `EMPTY_PAGE_TRIES` lần tải được ghi vào danh sách trang rỗng; lượt đi tiếp tới khi vượt `ceil(tổng / số tin trang đầu)`.
- **FR-002**: Không có tổng thì `EMPTY_PAGES_IN_A_ROW` (3) trang rỗng liền là hết listing.
- **FR-003**: Có trang rỗng kẹp giữa trang có tin, hoặc thấy dưới `MIN_COVERAGE` tổng, thì tải lại các trang rỗng sau khi nghỉ `DEFERRED_PAUSE` (120–240 giây), tối đa `DEFERRED_ROUNDS` (2) vòng.
- **FR-004**: Còn trang rỗng kẹp giữa sau vòng cuối thì lượt chưa đủ, `problems` có "pages still empty: …".
- **FR-005**: Trang bị chặn trong lượt đi vẫn dừng ngay với `complete = false`; kiểm 90% tổng của #302 giữ nguyên.
- **FR-006**: `fetch()` của trang listing gọi `wait_for_cards`: đếm thẻ mỗi `CARD_POLL` (0,5 giây), đọc khi số thẻ > 0, giống nhau `CARD_STABLE_POLLS` (3) lần liền và `readyState` là `interactive` hoặc `complete`; tối đa `LISTING_WAIT` (20 giây). Trang chi tiết giữ cách chờ cũ.
- **FR-007**: Trang trước trang cuối có ít thẻ hơn trang đầu được tải lại tới `EMPTY_PAGE_TRIES` lần, giữ lần nhiều thẻ nhất; vẫn thiếu thì giữ thẻ và đưa vào vòng thử lại.
- **FR-008**: Mỗi lần tải rỗng hoặc thiếu thẻ in giờ, số thẻ, thời gian tải, `readyState`, độ dài HTML, tiêu đề, và lưu HTML vào `TOPCV_DEBUG_DIR` (mặc định `data/state/topcv_debug/<ngày>/`). Dòng "Đang quét trang" có giờ.

## Success Criteria *(mandatory)*

- **SC-001**: `cd scraper && python -m pytest tests -q` xanh.
- **SC-002**: Đêm đầu sau khi deploy tay, nếu TopCV lại trả trang rỗng thì `daily-*.log` có dòng "Vòng thử lại", và `topcv listed=… complete=True` khi các trang đó có tin lại.
- **SC-003**: Đêm có trang rỗng hoặc thiếu thẻ, `data/state/topcv_debug/<ngày>/` có HTML để xác định trang chậm hay trang chặn; kết luận ghi vào `tdd.md`.
