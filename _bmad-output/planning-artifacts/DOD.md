---
title: "Definition of Done — Hải Đồ IT"
created: 2026-11-04
---

# Definition of Done

DoD là checklist **chung cho mọi backlog item**, khác với AC vốn riêng cho từng item. Một item xong nghĩa là: **AC của nó đạt** *và* **mọi dòng DoD dưới đây đạt**. Thiếu một trong hai thì chưa xong, dù code đã chạy.

Nhóm thống nhất bộ này một lần. Đổi DoD là đổi cho tất cả item, kể cả item đã làm xong trước đó — nên đổi thì phải cả ba đồng ý và ghi ngày.

Mỗi sprint có thêm **cổng ra sprint** riêng, ghi trong file sprint tương ứng. Cổng đó không thay DoD, nó cộng thêm.

## DoD chung — 14 dòng

### Nghiệp vụ

1. **AC đạt.** Đọc từng dòng `Given/When/Then` của item và chỉ ra được chỗ nào trong code hoặc test thỏa dòng đó.
2. **Mọi số hiển thị kèm ngữ cảnh:** cỡ mẫu `n`, ngày snapshot, nguồn. Số nằm trong ô số, tách khỏi lời dẫn — không trộn số vào câu văn.
3. **Mẫu nhỏ bị chặn đúng chỗ.** Ngưỡng kiểm qua `domain.display_policy.suppression_for(measure_kind, n)`, không tự so sánh `n < 30` rải rác. Chỉ tỷ trọng cấu phần (FR-33) được `low_sample_shown`; tỷ lệ kỹ năng và phân vị luôn `null_data` khi dưới ngưỡng.
4. **Không hardcode ngưỡng.** Mọi ngưỡng, θ, tỷ giá, trần, danh sách nguồn đọc từ bảng cấu hình có phiên bản.

### Kiến trúc

5. **Phép dùng lại có đúng một chữ ký** trong `haido_core/domain/REGISTRY.md`. Không có bản thứ hai của cùng một phép ở nơi khác.
6. **Alembic đúng một head** sau khi merge. Hai head là lỗi chặn merge, không phải việc dọn sau.
7. **Hướng phụ thuộc không đảo.** `web/` không nói chuyện với Postgres; `haido_core/steps/` không import Dagster; `haido_api/` không tổng hợp trên bảng `job_*`.
8. **Thao tác người dùng không gọi mô hình**, trừ đúng hai đường đã cho phép: lô đêm qua Batch API, và đường người dùng dán. Bấm một nút trên lộ trình thì đọc bản đã lưu.

### Riêng tư

9. **Không có nội dung CV hay JD** trong bảng, trong log, trong sự kiện ẩn danh, trong file tạm. CV 5 MB không để lại file tạm trên đĩa.
10. **Không có bản ghi nào khớp email hoặc số điện thoại Việt Nam** trong dữ liệu đã `redact`.

### Chất lượng

11. **Có kiểm thử cho AC chính**, và tên kiểm thử chứa mã FR hoặc AD liên quan. Kiểm thử tất định: cùng đầu vào cho cùng đầu ra, seed dẫn xuất theo khóa chứ không theo thời gian.
12. **Cổng CI của AD liên quan còn xanh.** Cổng mới mà item này sinh ra đã được thêm vào job chặn merge.
13. **Một người khác rà soát.** Không tự rà soát rồi merge. Người rà soát đọc được AC mà không cần hỏi lại tác giả.
14. **Trạng thái đã cập nhật** trong `_bmad-output/implementation-artifacts/sprint-status.yaml`, và lệnh CLI mới (nếu có) đã ghi vào `README` hoặc `docs/`.

## Definition of Ready — khi nào một item được chọn vào sprint

Không bắt buộc, nhưng dùng nó ở đầu mỗi sprint thì tránh được việc nhận một item rồi tắc giữa tuần:

- Item có AC viết xong, đọc hiểu được mà không cần tác giả giải thích.
- Phụ thuộc của nó đã `xong`, hoặc sẽ xong trước khi tới lượt.
- Quyết định nó dựa vào đã được ghi ở đâu đó — PRD, spine, `DESIGN.md`, `EXPERIENCE.md` — không phải "để làm rồi tính".
- Chia được thành task ≤ 1 ngày.
- Một người nhận được trọn item, không cần hai người sửa cùng file.

## Những dòng DoD này từ đâu ra

Mỗi dòng là một ràng buộc đang lặp lại trong `epics.md`, đếm trên bản ngày 04/11: "cỡ mẫu" 28 lần, "ngày snapshot" 22 lần, "chạy đủ trên điện thoại" 20 lần, "ngưỡng 30 tin" 17 lần, "đọc từ cấu hình" 16 lần, `aria-*` 10 lần, "bấm không gọi mô hình" 10 lần.

Lặp trong AC có hai cái hại: viết thừa, và **story nào quên viết thì mặc nhiên được miễn kiểm**. `aria-*` chỉ xuất hiện ở 10 story trong 56 — không ai muốn 46 story kia được phép bỏ a11y. Chuyển lên DoD thì không item nào trốn được.
