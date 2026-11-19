# Feature Specification: Hình response của toàn cảnh thị trường và dữ liệu giả

**Feature Branch**: `gh-327-tong-quan-thi-truong`

**Created**: 2026-11-19

**Status**: Implemented, chờ merge.

**Input**: GitHub issue [#327](https://github.com/Dyuedu/HaiDoIT/issues/327) — Agree the market-overview response shape and add fake data. Task phục vụ story #326.

## Bối cảnh

Mockup Insights (2026-11-19) cần tỷ trọng theo cấp bậc, vai trò, nơi làm việc và số năm kinh nghiệm. Mockup tự chia các số đó trên trình duyệt; AD-22 không cho web tính số. Issue này đặt một route trả mọi tỷ trọng đã tính, kèm bản giả cho web dựng màn.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Một envelope cho cả toàn cảnh (Priority: P1)

**Independent Test**: `tests/api/test_ad22_market_overview.py`.

**Acceptance Scenarios**:

1. **Given** số đếm của một snapshot, **When** dựng toàn cảnh, **Then** có tỷ lệ từng cấp (`intern`…`lead`, `unknown`), tỷ lệ người mới, tỷ trọng từng vai trò kèm tỷ lệ cấp và tỷ lệ người mới của nó, Hà Nội/TP.HCM của từng vai trò, bảy nơi làm việc và bảy mốc số năm; mọi số đếm nằm ở `meta.cells`. (AC 1)
2. **Given** vai trò, **When** API trả, **Then** nhiều tin trước, cùng số tin thì theo mã, `other` ở cuối; nơi và mốc số năm theo thứ tự cố định. (AC 2)
3. **Given** vai trò dưới 30 tin, **When** dựng, **Then** tỷ lệ cấp và tỷ lệ người mới là `null_data`, tỷ trọng của vai trò là `low_sample_shown`. (AC 3)
4. **Given** các mốc số năm, **When** dựng, **Then** các phần (`0`, `1`, `2`, `3`, `4-5`, `over_5`, `none`) cộng lại bằng `n` toàn quốc; mốc giảm hay tổng vượt `n` là lỗi. (AC 1)
5. **Given** API chạy bản giả, **When** gọi `GET /api/v1/market-overview`, **Then** 200 với envelope hợp lệ và bằng đúng `web/tests/fixtures/market-overview.json`. (AC 4, AC 5)

### Edge Cases

- Ô gộp `big_cities.all`, `other_provinces.all`, `vn.all.years_<mã>` không có hàng riêng trong `stat_cells`; `n` của chúng là tổng các ô thành phần.
- Bản giả có tổng `n` của các vai trò (3.502) khác `n` toàn quốc (3.586), nên tỷ trọng vai trò của bản giả không cộng đủ 100%. Bản thật thì cộng đủ vì mỗi tin có đúng một vai trò.

## Requirements *(mandatory)*

- **FR-001**: Hàm thuần `build_market_overview` (`haido_api/market_overview.py`) là chỗ duy nhất chia số; nguồn giả và nguồn thật cùng gọi.
- **FR-002**: Mỗi `Stat` trỏ tới ô mà `Envelope` dùng để kiểm hiển thị: tỷ trọng cấu phần trỏ tới ô của phần, tỷ lệ cấp bậc trỏ tới ô của cả nhóm.
- **FR-003**: Route đọc nguồn của `newcomer_roles`, không thêm biến môi trường mới.
- **FR-004** (đợt 2): Thứ hạng cấp, thứ hạng vai trò theo từng cấp và theo tỷ lệ người mới do máy chủ xếp (`levels_by_size`, `roles_by_level`, `roles_by_entry_share`).

## Ngoài phạm vi

- Bản thật: #328. Màn web: #329, #330.

## Success Criteria *(mandatory)*

- **SC-001**: `uv run pytest -q` xanh; `docs/api/openapi.json` sinh lại khớp code.
