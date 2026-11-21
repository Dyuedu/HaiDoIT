# Feature Specification: Nhận định trên trang Insights

**Feature Branch**: `gh-338-nhan-dinh-insights`

**Created**: 2026-11-21

**Status**: Draft

**Input**: GitHub issue [#338](https://github.com/Dyuedu/HaiDoIT/issues/338) — Add interpretive commentary to the Insights page.

## Bối cảnh

Trang Insights hiện có biểu đồ và bốn câu tóm tắt sự kiện (`takeaways` trong `market-overview-view.ts`). Người dùng (sinh viên khám phá IT) thấy số nhưng chưa biết số đó có nghĩa gì cho mình. Cần thêm nhận định hướng dẫn hành động, sinh từ data có sẵn, không cần API mới.

## User Scenarios & Testing

### User Story 1 - Nhận định hành động ở phần Toàn cảnh (Priority: P1)

Sinh viên mở Insights, đọc các câu takeaway và thấy không chỉ "vai trò nào có nhiều tin nhất" mà còn "nếu chưa chọn hướng thì nên nhắm vào đâu" và "kinh nghiệm không phải rào cản lớn" hoặc "cần cân nhắc vì phần lớn tin yêu cầu kinh nghiệm".

**Why this priority**: Phần toàn cảnh là thứ đầu tiên sinh viên đọc; thêm nhận định ở đây có tác động lớn nhất.

**Independent Test**: Unit test `buildMarketOverviewView` với fixture data, kiểm tra `takeaways` chứa câu mới.

**Acceptance Scenarios**:

1. **Given** data có `roles_by_entry_share` ≥ 2 vai trò, **When** buildMarketOverviewView chạy, **Then** `takeaways` có câu gợi ý vai trò phù hợp cho người chưa chọn hướng.
2. **Given** data có nhóm năm kinh nghiệm "0" và "none" chiếm tỷ trọng lớn (≥ 40% tổng), **When** buildMarketOverviewView chạy, **Then** `takeaways` có câu khuyến khích rằng kinh nghiệm không phải rào cản.
3. **Given** data có nhóm năm kinh nghiệm "0" và "none" chiếm tỷ trọng nhỏ (< 40% tổng), **When** buildMarketOverviewView chạy, **Then** `takeaways` có câu lưu ý rằng phần lớn tin yêu cầu kinh nghiệm.
4. **Given** Hà Nội và TP.HCM chênh lệch, **When** buildMarketOverviewView chạy, **Then** `takeaways` có câu gợi ý cho sinh viên theo vùng miền (ví dụ: "Sinh viên miền Bắc nên lưu ý [role] — Hà Nội có lợi thế").

---

### User Story 2 - Nhận định ở phần Người mới (Priority: P2)

Sinh viên cuộn tới "Cửa vào cho người mới" và thấy 1–2 câu tổng kết: hai vai trò nào chiếm phần lớn cơ hội, vai trò nào đáng chú ý dù tổng tin nhỏ.

**Why this priority**: Mục này sinh viên đọc ngay sau toàn cảnh.

**Independent Test**: Unit test `buildNewcomerView` kiểm tra field `takeaways` mới.

**Acceptance Scenarios**:

1. **Given** ≥ 3 vai trò có `shareShown`, **When** buildNewcomerView chạy, **Then** view có `takeaways` ≥ 1 câu nêu tên hai vai trò dẫn đầu.
2. **Given** có vai trò tỷ lệ entry cao nhưng tổng tin nhỏ (ví dụ ngoài top 3 theo tổng tin mà nằm trong top 3 theo entry share), **When** buildNewcomerView chạy, **Then** `takeaways` có câu gọi đó là "đáng chú ý" hoặc "cửa vào bất ngờ".

---

### User Story 3 - Nhận định ở phần Kỹ năng theo vai trò (Priority: P2)

Sinh viên chọn một kỹ năng (ví dụ Python) và đọc một câu ngắn: kỹ năng này là "nền tảng" (nhiều vai trò nhắc) hay "chuyên biệt" (chỉ 1–2 vai trò nhắc).

**Why this priority**: Giúp sinh viên hiểu giá trị kỹ năng mình đang học.

**Independent Test**: Unit test `buildSkillRolesView` kiểm tra field `insight` mới.

**Acceptance Scenarios**:

1. **Given** ≥ 3 vai trò có `shareShown` và ≥ 60% vai trò có `share.value > 0.2`, **When** buildSkillRolesView chạy, **Then** view có `insight` chứa từ "nền tảng" hoặc "nhiều vai trò".
2. **Given** chỉ 1–2 vai trò có `share.value > 0.2`, **When** buildSkillRolesView chạy, **Then** view có `insight` chứa từ "chuyên biệt" hoặc tên vai trò cụ thể.
3. **Given** kỹ năng không được vai trò nào nhắc tới (`mentioned = false`), **When** buildSkillRolesView chạy, **Then** `insight` là `null`.

---

### Edge Cases

- Data ẩn số (`null_data`, `low_sample_shown`): câu nhận định chỉ dùng vai trò/cấp có `display === "shown"`. Nếu không đủ dữ liệu để sinh câu, bỏ qua câu đó.
- Mọi câu tuân thủ DEC-6 (#132): không chứa số, chỉ gọi tên.

## Requirements

### Functional Requirements

- **FR-001**: Nhận định phải sinh từ data đã có trong `MarketOverviewEnvelope`, `NewcomerRolesEnvelope`, `SkillRolesEnvelope` — không gọi thêm API.
- **FR-002**: Mỗi câu nhận định phải tuân thủ DEC-6: không chứa con số.
- **FR-003**: Nhận định phải có guard condition — chỉ hiện khi đủ dữ liệu để khẳng định.
- **FR-004**: Nhận định hiển thị đúng trên 360 px phone.

## Success Criteria

- **SC-001**: Mỗi phần (toàn cảnh, người mới, kỹ năng) có ít nhất 1 câu nhận định hướng dẫn hành động khi data đủ.
- **SC-002**: Unit tests cover tất cả scenario ở trên.

## Assumptions

- Data hiện tại đủ phong phú để sinh câu nhận định (≥ 3 vai trò, ≥ 2 cấp).
- DEC-6 vẫn áp dụng: câu trên trang không chứa số.
