---
title: Sprint Change Proposal — Hải Đồ IT
date: 2026-10-27
status: approved
approved_by: Duy
trigger: Review khách quan bộ tài liệu BMad và đo dữ liệu 832 tin
---

# Sprint Change Proposal — 2026-10-27

## 1. Vì sao có đề xuất này

Review ngày 2026-10-27 tìm thấy ba vấn đề lớn:

1. **Lỗi logic ở Học gì tiếp?** Luật "tin phải có đủ mọi kỹ năng của tập đang xét" làm số sau luôn nhỏ hơn hoặc bằng số trước. Thêm một kỹ năng giả định không bao giờ làm tăng số tin.
2. **Dữ liệu mỏng** hơn mức các tài liệu đang ngầm giả định.
3. **Tài liệu lệch nhau** sau nhiều lần đổi quyết định: brief, PRD, kiến trúc, SPEC và epics nói khác nhau về agent, dự báo, lưu mô tả và So sánh offer.

## 2. Số đo

Đo trên ảnh 832 tin của SkillNexus (`D:\FR_KS_FU_Java_03\SkillNexus\data\scraped\*.jsonl`, cào ngày 2026-10-21). Script: `measurements/measure-2026-10-27.py`. Chạy bằng `python -I -X utf8 measure-2026-10-27.py <thư mục scraped>`.

Vai trò của tin được gán bằng heuristic theo tiêu đề, vì bảng `skill.role` chưa được điền. Khi nhóm điền bảng đó, các số theo vai trò sẽ thay đổi.

| Đo | Kết quả |
|---|---|
| Nguồn | ITviec 652, TopDev 99, Greenhouse 40, Lever 32, Workable 6, Cốc Cốc 3 |
| Thành phố | TP. HCM 444, Hà Nội 355, Đà Nẵng 21, Hải Phòng 2, Cần Thơ, Quy Nhơn, Nha Trang 0, khác 10 |
| Cấp | Middle 349, Fresher 245, Senior 91, Unknown 74, Junior 44, Intern 29 |
| Có lương VND | 24 tin, toàn bộ từ TopDev |
| Chỉ có lương USD | 140 tin, chủ yếu từ ITviec |
| Ô (vai trò × TP) đạt ≥ 30 tin có lương VND | 0/42, ở mọi cách gộp cấp |
| Có tính USD, Fresher và Junior, ba TP | Ô cao nhất là Hà Nội Backend với 11 tin; toàn quốc Backend 14, Data/AI 10 |
| Có tính USD, mọi cấp, toàn quốc | Data/AI 39, Backend 37; các vai còn lại dưới 15 |

Thử các luật đủ điều kiện trên pool 392 tin cấp Intern, Fresher, Junior và Unknown:

| Hồ sơ | Luật AND cũ | Mức khớp ≥ 50% |
|---|---|---|
| Python, SQL + Docker | 14 → 0 | 12 → 12 |
| Python, SQL + Machine Learning | 14 → 2 | 12 → 14 |
| Java, Spring Boot, SQL + Docker | 5 → 0 | 14 → 15 |

## 3. Quyết định (Duy, 2026-10-27)

| # | Quyết định | Lý do |
|---|---|---|
| D1 | **Tin đủ điều kiện** = mức khớp tin ≥ 50%, tức là số kỹ năng của tin nằm trong tập đang xét chia cho số kỹ năng của tin. Tin không có kỹ năng thì không tính. Ngưỡng 50% là tham số `MATCH_MIN`. | Thêm kỹ năng chỉ làm số tin tăng hoặc giữ nguyên, nên "học X mở thêm Y việc" mới có nghĩa. |
| D2 | **Lương:** tập lương của một ô là tin có lương với `last_seen` trong 180 ngày, đang mở hay đã đóng. USD đổi sang VND theo `USD_VND_RATE` cố định kèm ngày áp dụng, và màn ghi tỷ giá khi số đang hiện có dùng tin USD. Giữ ngưỡng 30. | Chỉ có 24 tin lương VND. Không hạ ngưỡng 30 (SM-C1). |
| D3 | **Ba thành phố:** Hà Nội, TP. Hồ Chí Minh, Đà Nẵng. Toàn quốc là gộp ba thành phố. | Bốn thành phố còn lại có 0–2 tin. |
| D4 | **Giữ bronze như AD-21.** JSON-LD gốc được lưu trên Silo, không hiện trên màn và không trả qua API. PRD NFR-2 sửa theo. | Agent Soi tin cần `read_bronze`. Duy chấp nhận rủi ro điều khoản ITviec và TopDev; câu hỏi pháp lý đã thêm vào PRD mục 12. |
| D5 | **Bốn agent là yêu cầu bắt buộc.** | Duy chốt. Ghi vào PRD, SPEC, AD-18 và epics. |
| D6 | **So sánh offer hoãn v1.1** (quyết định 2026-10-25, giờ đồng bộ vào tài liệu). Điều hướng còn bốn mục. | Dồn lực cho bốn agent. |

## 4. Tài liệu đã sửa

| Tài liệu | Thay đổi |
|---|---|
| `prds/.../prd.md` | Thêm khối cập nhật ở đầu. Thêm thuật ngữ "Mức khớp tin", định nghĩa lại "Tin đủ điều kiện", sửa "Ô mẫu", "Lương công khai", "Toàn quốc". FR-1 và FR-2 theo ba thành phố và AD-12. FR-7 có số đo. FR-8 thêm hệ quả "số sau ≥ số trước". §5.3 nói về agent. §5.5 đánh dấu hoãn v1.1. Cập nhật §6, §7, §8, §9, §10, NFR-2, §12. UJ-1 đặt ở Đà Nẵng, UJ-3 ở Hà Nội, UJ-4 đánh dấu hoãn. |
| `prds/.../addendum.md` | Trích kỹ năng bằng taxonomy, không dùng LLM. Bronze theo AD-21. |
| `architecture/.../ARCHITECTURE-SPINE.md` | AD-5: thêm cột USD, lọc ba thành phố. AD-4: thêm cột USD. AD-6: cửa sổ lương 180 ngày, đổi USD. AD-14: ba thành phố. AD-15: mức khớp tin và `MATCH_MIN`. AD-18: agent bắt buộc. AD-21: ghi lời chốt của Duy. Bảng capability: offer hoãn. |
| `specs/spec-HaiDoIT/SPEC.md` | CAP-1 và CAP-2 theo D1–D3. CAP-4 đánh dấu hoãn v1.1. Constraints: bốn mục điều hướng, ba thành phố, lương, bronze, agent bắt buộc, số đo. Non-goals thêm So sánh offer. |
| `epics.md` | Sửa phần mở đầu (bốn epic, đã có story). FR1, FR3, FR7, FR8, NFR1, NFR2, Additional Requirements, UX-DR4, UX-DR9. Tiêu đề Epic 1. Story 1.2: lọc thành phố, cột USD. Story 1.3: ba thành phố, tập lương 180 ngày, tỷ giá. Story 1.5: ba thành phố. **Story 2.1: thay "strict AND" bằng mức khớp, kèm property test và regression test.** Story 2.2: tập lương và toàn quốc. |
| `ux-designs/.../EXPERIENCE.md` | Bảng IA, thanh điều hướng bốn mục, tầm nhìn và thẻ thành phố không có số dự báo, dòng tỷ giá, định nghĩa tin đủ điều kiện, đoạn nới, UJ-1 ở Đà Nẵng, UJ-3 ở Hà Nội, UJ-4 hoãn. |
| `ux-designs/.../DESIGN.md` | Điều hướng bốn mục, bản đồ ba cột, trạng thái dự báo chưa có số, lương ẩn là trạng thái chính, dòng tỷ giá. |
| `briefs/.../brief.md`, `addendum.md` | Giữ nguyên nội dung gốc để truy vết. Thêm khối "superseded in part" ở brief và mục F ở addendum. |

`sprint-status.yaml` không cần đổi: tên story vẫn đúng, và vẫn không có epic offer.

## 5. Việc còn lại

- **Điền `skill.role`** (AD-10), rồi chạy lại script để có số theo vai trò chính xác thay cho heuristic theo tiêu đề.
- **Chốt `USD_VND_RATE` và ngày áp dụng** trước Story 1.3.
- **Đo lại ô lương sau 4–6 tuần cào hằng ngày.** Ước tính cửa sổ 180 ngày nhân mẫu lên 5–6 lần (`[GIẢ ĐỊNH]`). Nếu đúng, chỉ vài ô Backend và Data/AI ở Hà Nội và HCM mới đạt 30.
- **Xem lại `MATCH_MIN`** khi kho tin lớn hơn. Với 832 tin, số tin mở thêm khi học một kỹ năng thường chỉ 0–2. Đây là giới hạn của dữ liệu, không phải của luật mới.
- **Ghi chú review:** review trước ghi "tiêu đề Epic 1 bị lặp". Nhận xét đó sai, do hai đoạn trích in ra chồng lên nhau.
