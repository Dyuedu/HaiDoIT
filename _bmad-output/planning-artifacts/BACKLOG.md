---
title: "Backlog — trỏ sang GitHub Issues"
created: 2026-11-04
updated: 2026-11-04
---

# Backlog

**Bản chính nằm trên GitHub.** File này chỉ là chỉ mục. Đừng chép lại nội dung backlog vào đây — hai bản sẽ lệch nhau trong một tuần.

https://github.com/Dyuedu/HaiDoIT/issues

## Ánh xạ khái niệm

| Khái niệm | Trên GitHub |
|---|---|
| Product backlog | Toàn bộ issue đang mở, xếp theo số issue (= thứ tự làm, phụ thuộc đã đúng chiều) |
| Sprint backlog | Một milestone — `Sprint 1` đến `Sprint 8`, có ngày hết hạn |
| Backlog item | Một issue. #1–#69 (#67–#69 thêm theo `sprint-change-proposal-2026-11-05.md`) |
| Task | Checkbox trong mục `## Task` của từng issue |
| Acceptance Criteria | Mục `## Acceptance Criteria` của từng issue |
| Definition of Done | [DOD.md](DOD.md) — 14 dòng, áp cho mọi item |
| Cổng ra sprint | Mô tả của từng milestone |

## Quy ước

- **Một issue, một người.** Chia theo user story: người nhận làm trọn story từ dữ liệu đến màn hình. Năm chore chung (`C-3`, `C-4`, `C-5`, `C-7`, `C-10`) có nhiều người theo đúng yêu cầu của nó.
- **Thứ tự làm = số issue**, trừ #67–#69 được thêm sau ngày 05/11 và làm ngay trong Sprint 1. Phụ thuộc ghi ở dòng `Chặn bởi` trong mỗi issue, trỏ bằng `#số`.
- **Xong = AC đạt *và* DoD đạt.** Thiếu một trong hai thì chưa xong.
- **AC gốc của 58 story** nằm trong [epics.md](epics.md). Issue dẫn link về đúng story. Sửa AC thì sửa cả hai chỗ, hoặc sửa `epics.md` rồi ghi chú trong issue.
- **11 chore item** (`C-1`…`C-11`) không có story trong `epics.md`; issue giữ bản chính AC của chúng.

## Label

| Label | Nghĩa |
|---|---|
| `P0` | Bắt buộc cho review giữa kỳ 22–28/11 |
| `P1` | Bắt buộc trước khi công khai |
| `P2` | Làm nếu kịp — hiện không item nào |
| `loai:story` / `loai:chore` | Viết được theo góc nhìn người dùng, hay không |
| `epic-1`…`epic-6` | Epic của `epics.md` |
| `khong-duoc-cat` | Không cắt dù trượt lịch |

## Thứ tự cắt nếu trượt

Theo `architecture/architecture-HaiDoIT-2026-11-03/WORK-SPLIT.md` §5, từ ít đau nhất:

1. Số vai trò có lộ trình: 4–5 xuống 2.
2. Trang công khai (#51–#53): hoãn sau bảo vệ, phải ghi thành phạm vi bị cắt.
3. Thẻ Insights: năm loại xuống hai loại rẻ nhất (#61, #62).
4. Bọc Dagster (#37): giữ chuỗi lệnh CLI cộng `cron`.

**Không cắt dù trượt:** nhịp một hằng ngày (#67 ở Sprint 1, rồi #4–#6), chín cổng CI (#9), sao lưu (#10), bộ chuẩn 200 JD (#15, và #14 với #16 là hai story dùng nó), chế độ thử nghiệm (#54–#59).
