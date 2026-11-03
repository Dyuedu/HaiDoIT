---
title: "Đối chiếu brief → PRD: Hải Đồ IT"
created: 2026-11-03
input: "_bmad-output/planning-artifacts/briefs/brief-HaiDoIT-2026-11-02/ (brief.md, addendum.md, .memlog.md)"
target: "prd.md + addendum.md (thư mục này); đã đọc .memlog.md của PRD để nhận diện thay đổi có chủ đích"
---

# Đối chiếu brief → PRD: Hải Đồ IT

**Cách đọc**
- **Trạng thái:** `thiếu` (brief cam kết, PRD không có) · `mâu thuẫn` (PRD nói ngược) · `yếu đi` (PRD có nhưng lỏng hơn) · `đã thay đổi có chủ đích` (có quyết định trong `.memlog.md`) · `brief lỗi thời` (PRD đã đổi, brief chưa cập nhật).
- **Ưu tiên:** Cao / Trung bình / Thấp.
- "Brief dòng N" là số dòng trong `brief.md`; "BA §N" là `addendum.md` của brief; "BM dòng N" là `.memlog.md` của brief; "PM dòng N" là `.memlog.md` của PRD.

---

## A. PRD thiếu, mâu thuẫn hoặc yếu đi so với brief

### Ưu tiên cao

**A1. "Chất lượng JD" trong phần so với thị trường của Soi tin**
- **Brief:** §Giải pháp, Soi tin, "So với thị trường" (dòng 80); BA §1 Sprint 4 "(phân vị, chất lượng JD, dấu hiệu cần kiểm tra)"; BM dòng 8.
- **Trạng thái:** thiếu.
- **Chi tiết:** PRD FR-30 (phân vị) và FR-31 (D1–D4) không có FR, thuật ngữ hay tiêu chí nào tên "chất lượng JD". PM không ghi quyết định bỏ hay gộp mục này. D1/D2 có thể được hiểu là thay thế, nhưng không chỗ nào nói vậy.
- **Đề xuất sửa:** chọn một trong hai:
  - thêm FR "Chất lượng JD" (ví dụ: có lương, có số năm kinh nghiệm, có mô tả trách nhiệm, số kỹ năng trong khoảng P10–P90 của ô thống kê) kèm tiêu chí kiểm chứng; **hoặc**
  - ghi quyết định vào PM và bảng phương án bị loại (addendum PRD §3): "chất lượng JD được thể hiện qua D1–D3 và dòng lương trung tính", rồi sửa brief dòng 80 và BA §1 Sprint 4.

**A2. Bộ từ vựng kỹ năng song ngữ Việt–Anh**
- **Brief:** §Điểm khác biệt, "Lợi thế nằm ở đâu" (dòng 114); §Ràng buộc, "Yêu cầu học thuật" (dòng 179: "chuẩn hóa kỹ năng song ngữ").
- **Trạng thái:** thiếu.
- **Chi tiết:** PRD không có chữ "song ngữ". FR-6 chỉ kiểm chứng biến thể tiếng Anh ("SpringBoot", "Spring Boot"). §5 Ngôn ngữ chỉ nói tên kỹ năng hiển thị bằng tiếng Anh. Đây vừa là "lợi thế" duy nhất mang tính dữ liệu, vừa là một trong bốn bài toán khó dùng để bảo vệ độ phức tạp học thuật, nhưng PRD không đo nó.
- **Đề xuất sửa:** FR-6 thêm: bộ từ vựng chứa cách viết tiếng Việt (ví dụ "học máy" → `machine-learning`, "kiểm thử tự động" → `test-automation`); tiêu chí kiểm chứng: báo cáo precision/recall riêng cho các kỹ năng được viết bằng tiếng Việt trong bộ 200 JD. SM-6 thêm dòng tách số liệu này.

**A3. "Giới hạn đã biết" của đợt thử nghiệm người dùng**
- **Brief:** §Tiêu chí thành công (dòng 138–140); BM dòng 33 ("ghi selection bias là giới hạn đã biết").
- **Trạng thái:** thiếu.
- **Chi tiết:** §9 không có mục giới hạn. Hai giới hạn brief cam kết nêu rõ (người thử phần lớn cùng trường và quen nhóm; 2 tuần chỉ đo nhận thức và ý định, chưa đo kết quả xin việc) đều mất. Đây là phần cụ thể của nguyên tắc trung thực "thiếu dữ liệu thì nói thiếu" áp lên chính số liệu của nhóm.
- **Đề xuất sửa:** thêm vào cuối §9 mục "Giới hạn đã biết" gồm hai giới hạn của brief, cộng một giới hạn mới phát sinh trong PRD: so sánh mù (SM-3) chỉ dùng một tình huống mẫu cố định cho mỗi vai trò và một câu trả lời ChatGPT soạn sẵn.

**A4. Báo cáo tách nhóm trong trường / ngoài trường cho mọi chỉ số người dùng**
- **Brief:** BA §6 (dòng 101: "Kết quả báo cáo riêng cho nhóm trong trường và nhóm ngoài trường"); BM dòng 44.
- **Trạng thái:** yếu đi.
- **Chi tiết:** PRD chỉ yêu cầu báo cáo tách cho SM-3. SM-1, SM-2 và SM-9 không tách, dù FR-42 đã thu thông tin nhóm. Việc tách này là cách nhóm giảm nhẹ thiên lệch chọn mẫu (A3).
- **Đề xuất sửa:** ở đầu mục "Chính" của §9, ghi: "SM-1, SM-2, SM-3 và SM-9 được báo cáo tổng và tách theo nhóm trong trường / ngoài trường (FR-42)".

**A5. SM-1 cho phép 0–3 kỹ năng tự đoán, làm chỉ số "Phát hiện điểm mù" có thể bị thổi phồng**
- **Brief:** BA §4 (dòng 75: "người dùng chọn 3 kỹ năng cần học nhất"); brief §Tiêu chí (dòng 134).
- **Trạng thái:** yếu đi.
- **Chi tiết:** FR-42 ghi "tối đa 3 kỹ năng". Người thử chọn 0 hoặc 1 kỹ năng thì gần như mọi kỹ năng cốt lõi họ bấm "Tôi chưa biết" đều được tính là điểm mù, nên SM-1 (≥ 70%) dễ đạt một cách giả tạo.
- **Đề xuất sửa:** FR-42 bắt buộc chọn đúng 3 kỹ năng; **hoặc** SM-1 chỉ tính các phiên chọn đủ 3, và báo cáo số phiên bị loại.

**A6. Nguyên tắc "bản công khai chỉ bật nguồn hợp lệ" và "tôn trọng điều khoản từng sàn"; trạng thái của TopCV trên bản công khai**
- **Brief:** BA §2 "Công tắc theo từng nguồn" (dòng 49: "chỉ bật những nguồn hợp lệ. Dữ liệu của nguồn chưa được phép chỉ được dùng làm bộ kiểm tra nội bộ"); brief §Pháp lý, "Nguyên tắc thu thập" (dòng 188: "tôn trọng `robots.txt` **và điều khoản của từng sàn**").
- **Trạng thái:** yếu đi.
- **Chi tiết:**
  - §8.1 viết "Chỉ các nguồn đang bật công tắc trên bản công khai", tức là lặp lại chính nó và mất tiêu chí "hợp lệ / được phép".
  - FR-2 có bốn quy tắc nhưng không có "tôn trọng điều khoản sử dụng". Chỉ ITviec được xét điều khoản (§6.2).
  - §6.1 không nói TopCV (chưa được phép, có né phát hiện bot, chiếm khoảng 38% dữ liệu) có bật trên bản công khai ở Sprint 5 hay không. §10 câu 5 để ngỏ. Theo quy tắc của BA §2, TopCV phải chỉ dùng nội bộ, nên brief đang tự mâu thuẫn (xem C12), và PRD thừa hưởng điểm mơ hồ đó.
  - SM-C1 cấm "bật thêm nguồn vi phạm FR-2", trong khi TopCV chính là nguồn ngoại lệ của FR-2.
- **Đề xuất sửa:**
  - FR-1 thêm: một nguồn chỉ được bật trên bản công khai khi điều khoản sử dụng đã được rà soát và cho phép (hoặc đã có thư đồng ý); kết quả rà soát được ghi cạnh công tắc.
  - FR-2 thêm quy tắc thứ năm: tôn trọng điều khoản sử dụng của nguồn.
  - §6.1 nói rõ trạng thái công tắc TopCV trên bản công khai (bật / chỉ nội bộ), và nếu bật thì nêu hệ quả đối với số liệu công bố.
  - Sửa BA §2 hoặc brief §Rủi ro cho thống nhất.

> Mục **C1** (kế hoạch sprint của brief không phản ánh phạm vi mới của PRD) cũng thuộc ưu tiên cao; xem phần C.

### Ưu tiên trung bình

**A7. Thực nghiệm phụ: độ nhất quán lộ trình học của chatbot**
- **Brief:** BA §4 "Thực nghiệm phụ" (dòng 78); BA §1 Sprint 7 ("thực nghiệm độ nhất quán của chatbot"); BM dòng 39.
- **Trạng thái:** thiếu.
- **Chi tiết:** PRD §9 không có chỉ số hay thí nghiệm này. Đây là bằng chứng đối chứng cho luận điểm khác biệt số 2 ("lộ trình học tất định"). SM-8 chỉ chứng minh phía Hải Đồ IT.
- **Đề xuất sửa:** thêm SM-11 (phụ, chỉ số mô tả): hỏi cùng một câu về lộ trình học N lần trên 2–3 chatbot, đo độ lệch thứ tự học (ví dụ Kendall tau), và đặt cạnh SM-8.

**A8. Phân vị số năm kinh nghiệm không có điều kiện đủ mẫu**
- **Brief:** §Giải pháp, Soi tin (dòng 79: "phân vị của mức lương **và số năm kinh nghiệm yêu cầu**, chỉ hiển thị khi đủ mẫu").
- **Trạng thái:** yếu đi.
- **Chi tiết:** FR-30 chỉ yêu cầu số năm kinh nghiệm "trích được từ tin". Không có điều kiện về số tin trong ô thống kê có số năm kinh nghiệm, trong khi lương có điều kiện "≥ 30 tin có lương". Ngưỡng n ≥ 30 của ô thống kê đếm mọi tin, không đếm tin có trường này.
- **Đề xuất sửa:** FR-30 thêm: "và ô thống kê có ≥ 30 tin có số năm kinh nghiệm; nếu không, ghi 'chưa đủ dữ liệu (X/30 tin có số năm kinh nghiệm)'", kèm tiêu chí kiểm chứng tương tự lương.

**A9. "Mọi con số đi kèm cỡ mẫu, nguồn và ngày" bị rơi ở mức FR**
- **Brief:** §Giải pháp, "Nguyên tắc chung" (dòng 95).
- **Trạng thái:** yếu đi.
- **Chi tiết:** §5 có đủ ba yếu tố. Tuy vậy:
  - §1 chỉ nêu "mọi con số đi kèm cỡ mẫu";
  - FR-16 (bản tóm tắt tải về) thiếu nguồn;
  - FR-27 (Soi tin) chỉ ghi cỡ mẫu, thiếu nguồn và ngày;
  - FR-34 (bảng chi tiết thành phố) và FR-37 (Insights) thiếu nguồn.

  Nhóm UX và người viết story thường đọc tiêu chí của từng FR, không đọc §5.
- **Đề xuất sửa:** §1 sửa thành "cỡ mẫu, nguồn và ngày". Thêm một tiêu chí kiểm chứng chung, ví dụ: "mọi khối số liệu có dải 'n · nguồn · ngày snapshot'", hoặc bổ sung trực tiếp vào FR-16, FR-27, FR-34, FR-37.

**A10. Giả thuyết "thiếu kỹ năng cốt lõi" không được phát biểu trong PRD**
- **Brief:** §Vấn đề (dòng 34).
- **Trạng thái:** yếu đi.
- **Chi tiết:** SM-9 nhắc tên giả thuyết nhưng PRD không định nghĩa nó. PRD cũng bỏ câu khiêm tốn của brief: đây là **một** nguyên nhân, còn các nguyên nhân khác (thị trường fresher co hẹp, dự án cá nhân yếu) cũng có thật. UJ-1 kể theo mạch nhân quả (nộp CV không phản hồi → sửa CV), nên càng cần câu giới hạn này.
- **Đề xuất sửa:** thêm vào §1 hoặc đầu §9 đoạn "Giả thuyết cần kiểm chứng": hai nhánh (thiếu kỹ năng; có kỹ năng nhưng CV không thể hiện), câu "một nguyên nhân trong nhiều nguyên nhân", và chỉ số nào kiểm chứng nhánh nào (SM-1 → nhánh 1; SM-9 → nhánh 2).

**A11. Đơn vị đo của chỉ số "đã có nhưng quên ghi vào CV"**
- **Brief:** BA §6 (dòng 100: "tỷ lệ **người dùng** phát hiện kỹ năng đã có nhưng quên ghi vào CV").
- **Trạng thái:** mâu thuẫn (nhẹ). PM dòng 27 đổi tên chỉ số nhưng không ghi việc đổi đơn vị.
- **Chi tiết:** SM-9 tính trên **khoảng trống kỹ năng** (tỷ lệ khoảng trống được bấm "đã biết"), không tính trên **người dùng**. Brief gọi tỷ lệ người dùng là "bằng chứng trực tiếp" cho nhánh 2 của giả thuyết.
- **Đề xuất sửa:** SM-9 báo cáo cả hai: (a) % phiên có tải CV có ≥ 1 kỹ năng "Tôi đã biết, chỉ là CV chưa ghi"; (b) % khoảng trống như hiện tại.

**A12. Người dùng chính và nhóm "chuyển nhánh"**
- **Brief:** §Người dùng (dòng 38–40).
- **Trạng thái:** yếu đi.
- **Chi tiết:**
  - PRD §2 không có danh sách người dùng chính, chỉ có "việc cần làm" và "ai không phải người dùng".
  - Nhóm "fresher/junior 0–2 năm muốn chuyển nhánh (Backend → Data)" không có hành trình. UJ-3 là sinh viên năm 3 chưa có CV.
  - Brief giới hạn ở 0–2 năm, còn PRD §2.2 chỉ loại nhóm từ 5 năm trở lên, nên nhóm 2–5 năm không được nói tới.
- **Đề xuất sửa:** thêm §2.0 "Người dùng chính" chép từ brief. Ghi rõ FR-24 phục vụ nhóm chuyển nhánh. Nói rõ nhóm 2–5 năm thuộc diện "dùng được nhưng không tối ưu" hay không.

**A13. Điện thoại: kênh vào của người ngoài trường và chế độ thử nghiệm**
- **Brief:** BA §6 (dòng 98: phần lớn người ngoài trường bấm link từ Facebook trên điện thoại); brief §Phạm vi (dòng 146).
- **Trạng thái:** yếu đi.
- **Chi tiết:**
  - Không hành trình nào diễn ra trên điện thoại. UJ-1 vào qua Facebook nhưng dùng laptop.
  - FR-21 (ba lựa chọn xác nhận) và FR-41–FR-44 (modal, so sánh mù trái/phải) không nêu hành vi trên điện thoại, trong khi khoảng 40% mẫu thử có thể dùng điện thoại và SM-1, SM-3 phụ thuộc trực tiếp vào các FR này.
  - Insights trên điện thoại không được nhắc tới.
- **Đề xuất sửa:**
  - Thêm tiêu chí kiểm chứng trên điện thoại cho FR-21 và FR-42–FR-44: so sánh mù xếp trên/dưới thay cho trái/phải, vẫn đảo ngẫu nhiên và vẫn lưu vị trí.
  - FR-42 ghi loại thiết bị để phân tích.
  - Nói rõ Insights hiển thị thế nào trên điện thoại.

**A14. Yêu cầu học thuật: danh sách bốn bài toán khó**
- **Brief:** §Ràng buộc, "Yêu cầu học thuật" (dòng 177–183).
- **Trạng thái:** yếu đi.
- **Chi tiết:** §6.5 giữ nguyên tắc ("bài toán khó, giải đúng, đo được") nhưng bỏ danh sách bốn bài toán.
  - Loại tin trùng lặp → FR-4, SM-7: đủ.
  - Lộ trình học tất định → FR-22, SM-8: đủ.
  - Song ngữ → thiếu (A2).
  - "Tính phân vị khi mẫu thưa" → PRD chỉ dùng ngưỡng n ≥ 30 và quay về ô rộng hơn. Cách này né mẫu thưa thay vì giải nó, và không có số đo.
- **Đề xuất sửa:** §6.5 liệt kê bốn bài toán, mỗi bài trỏ tới FR và SM chứng minh. Với phân vị mẫu thưa, chọn một trong hai:
  - định nghĩa phương pháp và số đo (ví dụ khoảng tin cậy bootstrap, độ ổn định phân vị qua các snapshot);
  - ghi rõ lời giải là "ngưỡng + quay về", kèm cách chứng minh nó đúng.

**A15. Tầm nhìn sau bảo vệ và ràng buộc chi phí vận hành**
- **Brief:** §Tầm nhìn (dòng 199–206); BA §6 (dòng 102).
- **Trạng thái:** thiếu.
- **Chi tiết:** PRD §1 không có hướng đi sau v1. §5 và §6.4 không có trần chi phí vận hành (< 5–10 USD/tháng, một VPS nhỏ), trong khi con số này chi phối quyết định kiến trúc (Airflow cần khoảng 4 GB RAM) và giải thích vì sao trích xuất phải chuyển sang mô hình nhỏ.
- **Đề xuất sửa:**
  - §6.4 thêm: "Chi phí vận hành mục tiêu sau bảo vệ: < 5–10 USD/tháng trên một VPS nhỏ `[GIẢ ĐỊNH]`", và đưa vào §11.
  - §1 thêm 2–3 câu: khoảng 03/2027 mở xu hướng và tín hiệu tin bất thường; khi có lực kéo thì mở báo cáo cho trường, extension Soi tin, kênh gửi lương ẩn danh.

### Ưu tiên thấp

**A16. Giám sát pipeline**
- **Brief:** BA §2 "Pipeline" (dòng 41: "có giám sát dòng dữ liệu và lịch sử chạy").
- **Trạng thái:** yếu đi (nhẹ).
- **Chi tiết:** FR-1 có lịch sử chạy, và §5 có truy vết. Tuy vậy, không có yêu cầu báo động khi một lượt chạy lỗi hoặc khi số tin của một nguồn tụt bất thường. Thiếu báo động thì khó đạt SM-5 (≥ 95% lượt chạy thành công).
- **Đề xuất sửa:** FR-1 thêm tiêu chí: lượt chạy lỗi, hoặc số tin của một nguồn giảm quá X% so với trung bình 7 ngày, thì nhóm vận hành nhận thông báo.

**A17. Loại tin không thuộc IT trong pipeline**
- **Brief:** BA §5 (dòng 87: Zalo Careers "gồm cả tin không phải IT").
- **Trạng thái:** thiếu (nhẹ).
- **Chi tiết:** FR-26 chỉ lọc tin không thuộc IT khi người dùng dán vào. FR-7 không có nhãn "không phải IT" cho tin thu thập.
- **Đề xuất sửa:** FR-7 thêm: tin không thuộc IT bị loại khỏi bảng tổng hợp; tỷ lệ tin bị loại được báo cáo theo từng nguồn.

**A18. Đồ thị học trước – học sau: nguồn soạn và bằng chứng kiểm duyệt**
- **Brief:** §Điểm khác biệt mục 2 (dòng 109: "soạn từ tài liệu chính thức, rồi giảng viên hướng dẫn rà soát"); "Lợi thế" (dòng 115).
- **Trạng thái:** yếu đi (nhẹ).
- **Chi tiết:** §3 chỉ ghi "do nhóm soạn và giảng viên hướng dẫn rà soát". Cụm "tài liệu chính thức" bị bỏ, và không có tiêu chí kiểm chứng cho việc rà soát, dù đây là một "lợi thế" được tuyên bố.
- **Đề xuất sửa:** FR-22 thêm: mỗi cạnh lưu nguồn tài liệu; mỗi vai trò có biên bản rà soát (người rà soát, ngày, số cạnh) trước khi được bật trong Cố vấn.

**A19. Thẻ "Khác biệt giữa các thành phố" chỉ còn Hà Nội và TP.HCM**
- **Brief:** §Giải pháp, Insights (dòng 90).
- **Trạng thái:** yếu đi (nhẹ). Hợp lý theo dữ liệu (Đà Nẵng chỉ có 64 tin) nhưng PM không ghi lại.
- **Đề xuất sửa:** FR-37 ghi "Đà Nẵng được đưa vào khi ô thống kê đủ n ≥ 30", hoặc ghi lý do vào addendum PRD §3.

**A20. Mục tiêu hiệu chỉnh ở Sprint 2: "ít nhất 3–5" thành "ít nhất 3"**
- **Brief:** §Giải pháp, Soi tin (dòng 77); PM dòng 24 vẫn ghi "≥ 3–5".
- **Trạng thái:** yếu đi (nhẹ).
- **Chi tiết:** FR-9 chỉ giữ cận dưới (3).
- **Đề xuất sửa:** thống nhất một cách viết ở cả brief và PRD, ví dụ "≥ 3, mục tiêu 3–5". Ghi thêm rằng θ được đóng băng trước Sprint 6–7 (xem E2).

**A21. "Why now" và lý do các nguồn hiện có không đủ**
- **Brief:** §Vấn đề (dòng 26–32).
- **Trạng thái:** thiếu (thấp). PRD không bắt buộc phải có.
- **Chi tiết:** PRD §1 không có số liệu phân hóa thị trường (tin dưới 1 năm kinh nghiệm giảm 13%, tin AI/ML tăng 41%), cũng không nêu khoảng trống của các nguồn hiện có.
- **Đề xuất sửa:** thêm 1–2 câu vào §1, hoặc dẫn chiếu brief §Vấn đề.

**A22. Ba điểm khác biệt bị lệch thông điệp**
- **Brief:** §Điểm khác biệt (dòng 101–111): so với toàn bộ tin cùng vai trò, tất định, trung lập.
- **Trạng thái:** yếu đi (nhẹ).
- **Chi tiết:** PRD §1 liệt kê ba điểm khác: cỡ mẫu, tất định, nói thiếu. "Trung lập" chỉ còn ngầm trong §7 ("Không bán điểm đánh giá"). Luận điểm "mẫu số thị trường, không phán đoán trên một văn bản" (trả lời câu "sao không dùng ChatGPT") không được nói thẳng.
- **Đề xuất sửa:** §1 dùng lại ba điểm của brief, tách "cỡ mẫu" và "thiếu thì nói thiếu" thành nguyên tắc riêng, và trỏ tới §7 cho tính trung lập.

**A23. "Đo trước và sau phiên" và mục tiêu "bớt hoang mang"**
- **Brief:** §Tóm tắt (dòng 20: "thử nghiệm trước–sau"); §Tiêu chí (dòng 130: "có đo trước và sau phiên"); BM dòng 23 ("độ tự tin").
- **Trạng thái:** yếu đi (nhẹ).
- **Chi tiết:** PRD có modal đầu phiên và cuối phiên nhưng không đo cùng một biến ở hai thời điểm. Việc cần làm "về mặt cảm xúc: bớt hoang mang" ở §2.1 không có chỉ số nào.
- **Đề xuất sửa:** thêm một câu tự đánh giá 1–5 (ví dụ "Tôi biết rõ mình cần học gì tiếp theo") vào cả FR-42 và FR-43, rồi báo cáo chênh lệch như chỉ số mô tả. Nếu không làm, sửa brief: "trước–sau" nghĩa là "tự đoán trước phiên, đối chiếu với phát hiện trong phiên".

**A24. Thời lượng phiên khoảng 15 phút**
- **Brief:** §Tiêu chí (dòng 130); BA §4.
- **Trạng thái:** thiếu (nhẹ).
- **Đề xuất sửa:** §4.7 hoặc §9 ghi phiên khoảng 15 phút. FR-45 xuất thêm thời lượng phiên, tính từ các sự kiện ẩn danh.

**A25. Nút "Vì sao?" đã bị bỏ, so với lời dẫn "vì sao thị trường cần kỹ năng này" ở FR-23**
- **Brief:** BM dòng 9 ("bỏ nút 'Vì sao?'").
- **Trạng thái:** cần xác nhận. Có thể không mâu thuẫn, vì FR-23 dùng lời dẫn viết sẵn trong bảng chi tiết, không phải nút gọi LLM, nhưng PM không ghi lại.
- **Đề xuất sửa:** thêm một dòng vào addendum PRD §3: "Nút 'Vì sao?' gọi LLM theo yêu cầu vẫn bị loại; thay bằng lời dẫn viết sẵn (FR-23)".

**A26. Công bố "trường ngắn" của từng tin**
- **Brief:** §Pháp lý, "Công bố" (dòng 189: "chỉ công bố số liệu tổng hợp, kèm link về tin gốc").
- **Trạng thái:** mâu thuẫn (nhẹ). PRD mở rộng mà PM không ghi nhận.
- **Chi tiết:** FR-9 (Ngoài phạm vi) và §6.2 cho phép thêm "các trường ngắn (chức danh, công ty, thành phố, khoảng lương)". FR-37 hiển thị tên các công ty có nhiều tin nhất. Tuy vậy, ngoài link ở FR-32, không FR nào nói màn hình nào hiển thị trường ngắn của từng tin.
- **Đề xuất sửa:** ghi quyết định và căn cứ pháp lý vào PM hoặc addendum PRD §3; cập nhật brief §Pháp lý; chỉ rõ FR nào hiển thị các trường này.

---

## B. Đã thay đổi có chủ đích (có quyết định trong `.memlog.md`)

| # | Mục trong brief | Thay đổi trong PRD | Căn cứ | Brief đã cập nhật chưa? |
|---|---|---|---|---|
| B1 | Ngưỡng nhóm kỹ năng 50% / 10% | Tham số θ, khởi tạo 30% / 10%; chia nhánh khi n ≥ 30 | PM dòng 22–24 | Đã (BM dòng 60). Còn lệch "3–5" và "3" (A20) |
| B2 | Câu kết luận Insights: "LLM chỉ diễn đạt" | Mẫu câu cố định, không dùng LLM (FR-39) | PM dòng 71 | Đã (BM dòng 62, brief dòng 93) |
| B3 | Thử nghiệm: Google Form, hỏi lại sau 7 ngày | Chế độ thử nghiệm trong app, ẩn danh tuyệt đối (FR-41–FR-45) | PM dòng 49, 53 | BA §4 đã đồng bộ; brief dòng 130 vẫn ghi "form ẩn danh" (C10) |
| B4 | So sánh mù trên kết quả cá nhân hóa | Tình huống mẫu cố định theo vai trò (FR-44) | PM dòng 52 | Đã (BA §4) |
| B5 | "Kế hoạch học cho vài tuần tới" (brief dòng 50) | Không ước lượng số tuần; lộ trình chia theo chặng | PM dòng 16 | Chưa (C8) |
| B6 | "Không ghi lương" là một dấu hiệu (ngầm trong ý tưởng ban đầu) | Dòng thông tin trung tính, không phải dấu hiệu (FR-31) | PM dòng 64 | Brief không liệt kê dấu hiệu nên không lỗi thời. PRD vẫn còn dấu vết cũ (E1) |
| B7 | "Thiếu dữ liệu thì nói thiếu" (brief dòng 95) | Bản đồ: cột n < 30 vẫn vẽ, ở trạng thái mờ, kèm nhãn "cỡ mẫu nhỏ" (FR-33) | PM dòng 69 | Không cần sửa brief. Nên ghi ngoại lệ này vào §5 "Trung thực của con số" |
| B8 | "Server không lưu CV gốc hay hồ sơ" (BA §2) | Server lưu sự kiện ẩn danh (mã phiên, mã kỹ năng, vai trò, lựa chọn) và dữ liệu thử nghiệm (FR-17, FR-45) | PM dòng 26, 38 | Chưa (C6) |
| B9 | Cố vấn: không CV → lộ trình chung; có CV → cá nhân hóa | Hồ sơ kỹ năng từ CV **hoặc** tự chọn (FR-13); 3 lựa chọn xác nhận (FR-21); kỹ năng nền tảng | PM dòng 28, 58, 75 | Chưa (C3) |
| B10 | Thống kê theo vai trò | Thêm cấp bậc (Intern/Fresher/Junior, Mid, Senior+); ô thống kê vai trò × cấp bậc | PM dòng 41–42 | Chưa (C4) |
| B11 | Review giữa kỳ: "Backend và Data/AI" | Java Backend và Data Engineer; Data/AI tách 3 nhánh | PM dòng 22–23 | Tương thích, không bắt buộc sửa |
| B12 | Bản đồ gồm "Khác" | "Khác" chỉ ở chú thích, không vẽ cột (FR-33) | PM dòng 68 | Tương thích |
| B13 | Persona Minh: có Java, Spring Boot, MySQL | UJ-1: Minh thật ra đã biết Microservices, Docker, PostgreSQL nhưng CV không ghi | PM dòng 25, 34 | Tương thích (persona của brief mô tả những gì CV ghi) |

---

## C. Brief lỗi thời (PRD đã đổi, brief chưa cập nhật)

**C1. Kế hoạch 8 sprint không phản ánh phạm vi PRD** · Ưu tiên **cao**
- **Brief:** BA §1.
- **Chi tiết:** PRD §0 giao kế hoạch sprint cho addendum của brief, nhưng kế hoạch đó chưa có:
  - §4.7 Chế độ thử nghiệm (FR-41–FR-45), phải xong trước Sprint 6;
  - FR-13 tự chọn kỹ năng; FR-17 sự kiện ẩn danh; FR-21 ba lựa chọn xác nhận;
  - FR-32 khớp tin được dán với tin đã thu thập (cần cho D4);
  - FR-36 chế độ 2D/bảng bắt buộc;
  - FR-7 phân loại cấp bậc, tách Data/AI và Embedded (dữ liệu nền của Sprint 2).
- **Đề xuất sửa:** cập nhật BA §1 (Sprint 2: cấp bậc và tách nhánh; Sprint 4: FR-32; Sprint 5: chế độ 2D; Sprint 5–6: chế độ thử nghiệm), **hoặc** chuyển kế hoạch sprint sang addendum PRD.

**C2. "Có trong v1: 4 chức năng"** (brief dòng 145)
- **Chi tiết:** PRD có bảy nhóm tính năng: thêm Thu thập và chuẩn hóa, Hồ sơ kỹ năng, Chế độ thử nghiệm.
- **Đề xuất sửa:** thêm "chế độ thử nghiệm trong app" và "hồ sơ kỹ năng (từ CV hoặc tự chọn)" vào mục Phạm vi của brief.

**C3. Cố vấn hai trạng thái CV / không CV** (brief dòng 62–63)
- **Đề xuất sửa:** viết lại theo PRD: hồ sơ kỹ năng từ CV hoặc tự chọn; xác nhận từng khoảng trống ("Tôi chưa biết" / "Tôi đã biết, chỉ là CV chưa ghi"); kỹ năng nền tảng.

**C4. Không có khái niệm cấp bậc** (brief §Giải pháp; BA §1 Sprint 2 "theo vai trò")
- **Đề xuất sửa:** thêm cấp bậc và ô thống kê vai trò × cấp bậc (quay về toàn bộ vai trò khi n < 30).

**C5. Soi tin thiếu các khái niệm PRD đã chốt** (brief dòng 71–81)
- **Chi tiết:** brief chưa có mức khớp có trọng số (3/2/1), kỹ năng chưa nhận diện, phân vị "số kỹ năng yêu cầu", D1–D4, và dòng lương trung tính.
- **Đề xuất sửa:** thêm 2–3 dòng tóm tắt các khái niệm này vào brief, hoặc trỏ tới FR-28–FR-31.

**C6. "Server không lưu CV gốc hay hồ sơ"** (BA §2; brief dòng 150)
- **Đề xuất sửa:** thêm vế "server chỉ ghi sự kiện ẩn danh theo mã phiên (không chứa nội dung CV/JD), được nêu trong ô đồng ý".

**C7. "Không có trong v1" thiếu các mục PRD đã thêm** (brief dòng 153–162)
- **Chi tiết:** thiếu trạng thái "đang học", ước lượng số tuần học, so sánh song song hai thành phố, OCR cho CV scan, hỏi lại người thử sau phiên.
- **Đề xuất sửa:** bổ sung các mục này.

**C8. Thành công với Minh** (brief dòng 50)
- **Chi tiết:** "kế hoạch học cho vài tuần tới" và "biết JD nào đáng nộp ngay" lệch với PRD: lộ trình theo chặng, không số tuần; Soi tin không khuyên nộp hay không nộp.
- **Đề xuất sửa:** "rời Hải Đồ IT với lộ trình học theo chặng dựa trên dữ liệu, và đủ dữ kiện để tự quyết JD nào đáng nộp".

**C9. Điện thoại: "chỉ có Soi tin và danh sách khoảng trống kỹ năng"** (brief dòng 146)
- **Chi tiết:** PRD còn có bản đồ dạng danh sách thành phố trên điện thoại, và chế độ 2D/bảng bắt buộc (FR-36).
- **Đề xuất sửa:** cập nhật câu này.

**C10. "Trả lời bằng form ẩn danh"** (brief dòng 130)
- **Đề xuất sửa:** "trả lời ngay trong app ở chế độ thử nghiệm, ẩn danh tuyệt đối". BA §4 đã đồng bộ, chỉ còn brief.md.

**C11. Mục tiêu hiệu chỉnh Sprint 2 "3–5"** (brief dòng 77)
- Xem A20; thống nhất với FR-9.

**C12. Brief tự mâu thuẫn về TopCV**
- **Chi tiết:** BA §2 ghi "bản công khai chỉ bật nguồn hợp lệ; nguồn chưa được phép chỉ làm bộ kiểm tra nội bộ", trong khi brief §Rủi ro giữ TopCV (chưa được phép) trong suốt giai đoạn đồ án, bao gồm cả lúc công khai ở Sprint 5.
- **Đề xuất sửa:** sửa cùng lúc với A6.

**C13. Cách gán nhãn bộ chuẩn 200 JD** (BA §4 dòng 68)
- **Chi tiết:** "Mỗi JD có 2 người gán nhãn" mâu thuẫn với "kappa trên 50 JD chung". PRD FR-6 dùng cách hiểu "50 JD chung".
- **Đề xuất sửa:** "200 JD chia cho 2 người gán nhãn; 50 JD được cả hai gán để tính kappa".

---

## D. Đã khớp (không cần sửa)

Các mục sau của brief có mặt đầy đủ trong PRD:
- tóm tắt sản phẩm và câu hỏi cốt lõi;
- bốn chức năng; giao diện tiếng Việt; desktop-first;
- 4–5 vai trò khi công khai; bản đồ ba thành phố cộng "Khác";
- CV PDF/DOCX có đồng ý, không lưu file gốc; không tài khoản, lưu ở trình duyệt, có link chia sẻ và tải về;
- toàn bộ danh sách "Không có trong v1";
- rủi ro TopCV (§6.1, giữ nguyên văn);
- Luật 91/2025; xóa PII của người đăng tin; xin phép ITviec và tác giả repo gốc;
- dữ liệu mỏng (lương 24%, vai trò, thành phố);
- chi phí LLM và việc chuyển sang mô hình nhỏ sau khi đo trên 200 JD;
- mốc Review giữa kỳ và nộp báo cáo;
- tiêu chí hệ thống: pipeline, loại tin trùng lặp, trích xuất P/R/kappa, tất định, < 15 giây;
- ba ngưỡng người dùng (≥ 70%, ≥ 60%, ≥ 4,0/5), mẫu 30–50 người chia 60/40;
- Insights: năm loại thẻ, n ≥ 30, không dùng LLM;
- Soi tin: ba nhóm kỹ năng, ghi chú "chỉ cần nếu nhắm đúng công ty này", dấu hiệu là gợi ý chứ không phải phán quyết;
- lộ trình học: đồ thị quyết định thứ tự, tần suất quyết định ưu tiên, LLM chỉ viết lời dẫn, link chỉ lấy từ danh mục đã kiểm duyệt;
- bản đồ theo tỷ trọng, không theo số tin tuyệt đối;
- link chia sẻ không chứa thông tin cá nhân;
- trung lập (§7).

---

## E. Ghi chú phụ: mâu thuẫn nội bộ PRD phát hiện khi đối chiếu

Các mục này không thuộc phạm vi đối chiếu với brief, nhưng ảnh hưởng tới các nguyên tắc của brief.

- **E1.** UJ-2 bước 5 và định nghĩa "Dấu hiệu cần kiểm tra" ở §3 vẫn dùng "tin không ghi lương" làm dấu hiệu. Điều này trái với FR-31, với addendum PRD §3 và với PM dòng 64. Cần sửa UJ-2 (dấu hiệu thứ hai của tin công ty B nên là D2, D3 hoặc D4) và ví dụ ở §3.
- **E2.** FR-9 cho phép hiệu chỉnh θ ở Sprint 2 để có ≥ 3 kỹ năng cốt lõi, trong khi SM-C2 cấm "hạ θ_core" để làm đẹp SM-1. Nên ghi rõ: θ hiệu chỉnh một lần ở Sprint 2 và đóng băng trước thử nghiệm Sprint 6–7.
- **E3.** §7 viết "không lưu lịch sử trên server", nhưng FR-17 và FR-45 lưu sự kiện ẩn danh trên server. Nên sửa thành "không lưu lịch sử gắn với danh tính".
- **E4.** Link chia sẻ ở FR-15 không mang mã snapshot. Vì vậy tiêu chí "mở trên máy khác hiển thị đúng lộ trình như máy gốc" chỉ đúng khi cùng snapshot. Cần làm rõ cho phù hợp nguyên tắc "kèm ngày".
- **E5.** §10 có 6 câu hỏi mở, trong khi PM dòng 74 ghi 7 câu. Cần kiểm tra xem có câu nào bị rơi.
