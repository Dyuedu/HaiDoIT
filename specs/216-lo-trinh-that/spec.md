# Feature Specification: API trả lộ trình đã xếp kèm tỷ lệ của từng kỹ năng

**Feature Branch**: `gh-216-lo-trinh-that`

**Created**: 2026-11-25

**Status**: Một phần. AC 2 xong. AC 1: phần API xong và có test với lộ trình được đánh dấu đã rà soát, nhưng chưa vai trò nào có biên bản rà soát (#96) và thứ tự của #213 chưa có. Không đóng issue.

**Input**: GitHub issue [#216](https://github.com/Dyuedu/HaiDoIT/issues/216) — Return an ordered path with each skill's share. Phục vụ story #121.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Vai trò chưa có lộ trình đã rà soát nói rõ là chưa sẵn sàng (Priority: P1)

**Independent Test**: `tests/api/test_fr22_learning_path_stat.py`.

**Acceptance Scenarios**:

1. **Given** nguồn `stat` và vai trò có `review = null` hoặc không có nội dung, **When** gọi ở bất kỳ cấp hợp lệ nào, **Then** 200 `not_ready`, không chặng, `entry_cell_id` có trong `meta.cells`, `have_ignored` xếp A–Z; màn dẫn sang hồ sơ kỹ năng (#217). (AC 2)
2. **Given** vai trò không có trong `config/rules.toml`, **Then** 404 kèm ngày snapshot; chưa có snapshot đọc được thì 404 không ngày.

### User Story 2 - Lộ trình đã rà soát có tỷ lệ thật (Priority: P1)

**Independent Test**: `tests/api/test_fr22_learning_path_stat.py`.

**Acceptance Scenarios**:

1. **Given** vai trò có `review`, **When** gọi, **Then** `ready`; ô, tỷ lệ, nhóm và ngày snapshot bằng `skill-rates` cùng vai trò, cấp; trong mỗi chặng cốt lõi đứng trước thường gặp; không có lưu ý bản nháp. (AC 1)
2. **Given** cùng yêu cầu, **Then** chỉ đọc `stat_*` và `snapshots`, không tổng hợp lại (AD-7).

### User Story 3 - Dấu rà soát không thể có do nhầm (Priority: P1)

1. **Given** `review` thiếu, sai hình, ngày sai hay biên bản rỗng, **When** nạp nội dung, **Then** lỗi nêu vai trò; không bao giờ thành "đã rà soát".
2. **Given** một vai trò có `review`, **When** chạy test, **Then** file biên bản phải có trong `docs/`.
3. **Given** app demo, **When** hiện lộ trình chưa rà soát, **Then** luôn kèm lưu ý `draft_path`; lớp đó không có trong `IMPLEMENTATIONS`.

### Edge Cases

- Vai trò chưa rà soát và không có tin nào ở snapshot: vẫn `not_ready`, ô entry `n = 0`.
- Đã rà soát nhưng không nút nào có số ở ô: 404 kèm ngày.
- Không tập nào đủ mẫu: mọi tỷ lệ `null_data` (#212).

## Requirements *(mandatory)*

- **FR-001**: `StatMarket.learning_path` chỉ hiện lộ trình có `review`.
- **FR-002**: Tỷ lệ lấy từ chính `StatMarket.skill_rates`, không có đường tính riêng (ràng buộc từ #151).
- **FR-003**: Nội dung ở `haido_api/content/learning_path.json`, cổng FR-24 quét.

## Ngoài phạm vi

- Biên bản rà soát (#96), thứ tự bằng phép 8 (#213), bật Backend và Data Engineer (#214, #215). `order_path` trả một dãy còn hợp đồng hiện tại xếp theo chủ đề: cách ghép là việc của #213.
- Phát hiện nội dung bị sửa sau khi rà soát: `_note` yêu cầu rà soát lại, chưa có kiểm tự động.

## Success Criteria *(mandatory)*

- **SC-001**: `uv run pytest -q` xanh với Postgres thật; 10 cổng xanh.
- **SC-002**: Trên snapshot thật, `main:app` trả `not_ready` cho Backend; app demo trả lộ trình kèm lưu ý.
