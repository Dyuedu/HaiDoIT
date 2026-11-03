# Rà soát delta FR-48 — PRD: Hải Đồ IT

_Rà soát delta trên PRD đã final (`prd.md`, `status: final`, `updated: 2026-11-03`) theo `.claude/skills/bmad-prd/assets/prd-validation-checklist.md`. Phạm vi chỉ gồm phần delta thêm: câu trang công khai ở §1, §4.8 FR-48, bullet trang công khai ở §8.1, bullet cuối §8.2, câu hỏi mở 7, ghi chú FR-48 và hai dòng "Trang công khai" trong `addendum.md`. Không rà lại 47 FR còn lại. Không lặp finding của `review-rubric.md` mà delta này không đổi._

## Overall verdict

Delta chốt được một việc mà spine kiến trúc đang thiếu trên PRD: trang công khai theo vai trò là FR-48, có tiêu chí, có phần loại trừ (không lấy JSON-LD hay file hướng dẫn mô hình làm điều kiện xong; không có trang theo thành phố, kỹ năng, câu hỏi trong v1), và không kéo Next.js, ISR, `revalidatePath` hay GET mồi trang vào PRD. Phần đứng vững là các ràng buộc cấm: không toàn văn JD, không bảng R1–R4, không tài khoản, số của snapshot mới phải có trước lượt mở đầu tiên.

Chỗ rủi ro là người chia story không kiểm được "câu trả lời" trên trang. Ô thống kê và quy tắc "chưa đủ dữ liệu" không khớp câu §1 hay các màn trong ứng dụng; đoạn đầu trang chưa khóa nội dung bắt buộc, kể cả việc máy thu thập đọc được câu đó trong HTML. §8.1 đưa trang vào lúc phát hành, câu hỏi mở 7 vẫn để FR-48 trong hàng cắt P1/P2.

## 1. Decision-readiness — adequate

Các lựa chọn của delta được viết thành quyết định. FR-48: một URL cho mỗi vai trò mục tiêu, câu trả lời ở đầu trang, chỉ số tổng hợp, ràng buộc trung thực của FR-47 "áp dụng nguyên", trang không tự tính số lúc có người mở. Hai dòng addendum §3 ghi rõ thứ đã bỏ và cái giá: dữ liệu có cấu trúc không làm tăng việc được công cụ AI dẫn (bằng chứng ngày 03/11); thêm loại trang là thêm một dòng sinh trang, nên v1 dừng ở trang vai trò tới khi đo được việc được dẫn. Câu hỏi mở 7 vẫn là câu hỏi mở thật, không phải câu đã trả lời ở câu kế.

Một cửa thì còn hai giọng, riêng với FR này.

### Findings

- **[medium]** Cửa phát hành của FR-48 bị nói hai mức (§8.1, §10 câu 7) — §8.1 xếp trang vào "Có trong v1": "Trang nội dung công khai lúc phát hành" và "Review giữa kỳ không phụ thuộc FR-48". Câu 7 viết "PRD chưa có lằn ranh cắt giảm. Cần gắn mức ưu tiên cho từng FR, gồm FR-48", với P1 là "bắt buộc trước khi công khai" và P2 là "làm nếu kịp". Vế không chặn review giữa kỳ đã chốt. Vế còn lại thì "lúc phát hành" đọc như cam kết, còn "gồm FR-48" đọc như vẫn cắt được khi chia epic — đúng chỗ delta này được thêm để epic khỏi bỏ sót. *Fix:* một dòng ở §8.1: FR-48 là P1 hoặc là P2. Nếu P1, xóa "gồm FR-48" khỏi câu 7. Nếu P2, sửa bullet §8.1 để trang không đứng trong danh sách đã cam kết lúc phát hành.

## 2. Substance over theater — strong

Câu tầm nhìn mới không phải câu lắp vào PRD nào cũng được: "cùng snapshot, cùng cỡ mẫu và cùng quy tắc 'chưa đủ dữ liệu'". FR-48 có việc người đọc làm được (đọc mặt bằng kỹ năng của một vai trò) và việc cố ý không làm. Lý do loại JSON-LD và file hướng dẫn nằm ở addendum, kèm mốc ngày, không phải một đoạn khác biệt cho có. Không thêm persona.

### Findings

- **[low]** Câu mô tả §4.8 nhận một kết quả nhóm không kiểm soát (§4.8 "Mô tả") — "Người tìm trên công cụ tìm kiếm hoặc công cụ AI gặp được câu trả lời có số, có nguồn và có ngày." "Gặp được" phụ thuộc công cụ bên ngoài. Phần FR-48 kiểm được là trang cho đọc và câu trả lời đứng ở đầu trang. *Fix:* đổi thành "trang để trình thu thập của công cụ tìm kiếm và công cụ AI đọc được câu trả lời có số, có nguồn và có ngày trong nội dung trả về."

## 3. Strategic coherence — adequate

Trang này là cùng một luận điểm của §1 — "Kỹ năng này xuất hiện trong bao nhiêu phần trăm tin tuyển dụng cùng vai trò" — đưa ra chỗ người chưa mở ứng dụng. Nó không thành một sản phẩm thứ hai. §8.2 và mục "Ngoài phạm vi" của FR-48 cùng cắt các kiểu trang khác, đúng hướng ưu tiên theo luận điểm (trang vai trò trước), không theo số trang dễ sinh. §9 không có nhịp nào cho lời hứa mới, nên điều kiện "được dẫn tới" ở §8.2 chưa gắn vào bộ đo.

Mâu thuẫn "cùng quy tắc với ứng dụng" nằm ở mục 4: nếu trang và ứng dụng ra hai số khác nhau cho cùng một vai trò, luận điểm một mặt bằng có nguồn bị gãy trên đúng bề mặt để máy khác trích dẫn.

### Findings

- **[medium]** Lời hứa người chưa mở ứng dụng không có cách kiểm (§1, §8.2, §9, addendum §3) — §1: "Người chưa mở ứng dụng vẫn đọc được mặt bằng kỹ năng". §8.2 chỉ xét thêm trang "sau khi các trang vai trò (FR-48) đã được công cụ tìm kiếm hoặc công cụ AI dẫn tới". Addendum nói "cho tới khi đo được FR-48 có được dẫn hay không". §9 không có chỉ số cho việc được đọc hay được dẫn, và cũng không ghi v1 cố ý không đo. "Được dẫn tới" không có người quan sát, thời điểm, hay mức nào tính là đạt, nên cửa mở rộng không có cách đóng. *Fix:* một câu ở §9: v1 không đặt mục tiêu lượt dẫn. Khi xét bullet §8.2, "được dẫn tới" nghĩa là một trang vai trò xuất hiện trong kết quả tìm hoặc trong câu trả lời của công cụ AI, do nhóm kiểm tại thời điểm xét. Không thêm SM có ngưỡng nếu nhóm không muốn tối ưu việc được dẫn.

## 4. Done-ness clarity — thin

Khung cấm của FR-48 kiểm được: một URL không cần tài khoản, không mô tả tin hay toàn văn JD, không bảng R1–R4, không câu khẳng định tuân thủ trái §6.1, ô dưới ngưỡng hiện chữ "chưa đủ dữ liệu". Câu "Trang không tự tính số vào lúc có người mở" và "trước khi người đọc hoặc trình thu thập đầu tiên mở trang" là điều phải đúng với người đọc, đúng tầng PRD. Phần dương — câu trả lời gồm những số nào, trên ô nào — chưa thành bài kiểm.

### Findings

- **[high]** Ô của trang vai trò không được chọn, và "chưa đủ dữ liệu" không còn là một quy tắc (§1, §3 "Ô thống kê", FR-18, FR-19, FR-33, FR-34, FR-48) — §1 buộc trang "dùng cùng snapshot, cùng cỡ mẫu và cùng quy tắc 'chưa đủ dữ liệu' với ứng dụng". FR-48 viết "giống các màn trong ứng dụng", rồi "Tỷ lệ kỹ năng và phân vị không hiện khi ô dưới ngưỡng". Tiêu chí: "Ô dưới ngưỡng hiện 'chưa đủ dữ liệu', không hiện một tỷ lệ." Các màn không cùng một quy tắc. FR-19: ô vai trò mục tiêu × cấp bậc có n < 30 thì quay về ô rộng hơn và vẫn hiện tỷ lệ, kèm nhãn. FR-34: n < 30 thì không hiện tỷ lệ. FR-33: vẫn vẽ cột, kèm "Cỡ mẫu nhỏ". §3 đặt ô Cố vấn là vai trò mục tiêu × cấp bậc; FR-18 đặt cấp mặc định Intern/Fresher/Junior; cửa sổ là 60 ngày; có thứ tự quay về. FR-48 không chọn ô, không chọn cấp bậc, không nói có quay về hay không. Tiêu chí "số khớp bảng tổng hợp của snapshot đó" không chốt được một số: FR-9 có một tỷ lệ cho mỗi ô. "Snapshot đã công bố" không có trong §3. Snapshot ở §3 là "Mỗi lần pipeline chạy thành công". Tiêu chí không nói một lượt đã công bố có tính là xong khi trang vẫn còn số cũ hay không. *Fix:* chốt một ô cho mọi trang vai trò, viết trong FR-48. Ví dụ vai trò × mọi cấp bậc, toàn quốc, đúng cửa sổ 60 ngày của §3, không quay về. Một quy tắc hết: dưới ngưỡng thì câu đầu trang là "chưa đủ dữ liệu" và không có tỷ lệ; nếu chọn quay về như FR-19 thì in đúng nhãn n và cơ cấu cấp bậc, và sửa câu §1 cho khớp quy tắc đó. "Snapshot đã công bố" là snapshot mà FR-9 đã tính xong và mọi URL vai trò đã hiện số của nó. Trang giữ snapshot trước nếu lượt mới chưa hiện lên hết, và ngày in trên trang là ngày snapshot đang hiện. Thêm một tiêu chí với số giả: tỷ lệ trên trang bằng đúng ô đã chốt.

- **[high]** Đoạn đầu trang và điều kiện để máy đọc chưa thành tiêu chí (§4.8, FR-48, §5 "Trung thực của con số", FR-36, §6.2) — §4.8 hứa câu trả lời "có số, có nguồn và có ngày". Thân FR-48: "kỹ năng nào xuất hiện nhiều", kèm cỡ mẫu và ngày; khi có snapshot mới thì kèm "ngày snapshot, cỡ mẫu và danh sách nguồn đang bật". Tiêu chí đoạn đầu chỉ đòi "nhóm hoặc tỷ lệ kỹ năng, cỡ mẫu n, và ngày snapshot". Chữ "hoặc" cho một trang không có phần trăm vẫn đạt. Danh sách nguồn không có trong tiêu chí. Không nói những kỹ năng nào được nêu (cốt lõi, thường gặp, hay một top N). Câu "phân vị không hiện khi ô dưới ngưỡng" mặc nhận trang có phân vị, nhưng không nói phân vị lương, số kỹ năng, hay số năm. "Chỉ dùng số liệu tổng hợp" và "không chứa mô tả tin hay toàn văn JD" vẫn để lọt chức danh, công ty, khoảng lương và link tin gốc — các trường ngắn mà §6.2 cho công bố. "Trình thu thập phổ biến … không bị chặn" không chỉ họ trình nào, và không đòi câu trả lời có trong HTML trả về khi không chạy script. Trang vẽ số bằng script sau khi tải vẫn qua hết tiêu chí hiện có. §5 bắt lưu ý độ phủ trên danh sách đóng "Bản đồ nhu cầu, Insights, Cố vấn, Soi tin" và bản tóm tắt. Trang vai trò không có trong danh sách, dù đây là chỗ số bị trích ra ngoài sản phẩm. Ba lưu ý chuẩn của FR-36 không được gọi. FR-47 đòi trang chính sách "từ chân trang của mọi màn hình"; FR-48 không nhắc liên kết đó, nên kênh gỡ có thể vắng trên đúng trang bị lập chỉ mục. *Fix:* thay tiêu chí đoạn đầu bằng một danh sách đóng: kỹ năng cốt lõi và thường gặp, mỗi kỹ năng có tỷ lệ xuất hiện; cỡ mẫu n; ngày snapshot; danh sách nguồn đang bật; lưu ý độ phủ (tin IT trên N nguồn, cộng ba lưu ý FR-36 — hoặc ghi rõ trang không hiện lương thì bỏ ý lương). Nói phân vị có trên trang hay không; nếu có, chỉ rõ phân vị nào và câu "chưa đủ dữ liệu" kèm mẫu số như các màn lương. Cấm các trường của từng tin. Thêm tiêu chí: HTML trả về, không chạy script, chứa câu trả lời đó. Thay "phổ biến" bằng các họ trình thu thập của công cụ tìm kiếm và của công cụ AI phải được phép đọc. Sửa §5 để câu lưu ý độ phủ gồm trang vai trò. Chân mỗi trang vai trò mở được FR-47.

## 5. Scope honesty — adequate

Phần để ngoài v1 được viết thành mục, không để người đọc tự suy. FR-48 "Ngoài phạm vi", bullet cuối §8.2, và hai dòng addendum §3 cùng một ranh: không trang theo thành phố, kỹ năng, hay câu hỏi; dữ liệu có cấu trúc và file hướng dẫn mô hình không phải tiêu chí hoàn thành; không tài khoản trên các trang này. Số trang bám "vai trò mục tiêu" của §8.1, không sinh thêm một con số trang mới. Tập trang nằm trong v1 thì chưa đếm được.

### Findings

- **[medium]** Không đếm được số trang, và "vai trò mục tiêu" không chỉ một cấp (§3, §8.1, §10 câu 3, FR-22, FR-48) — §4.8: "đúng một trang cho mỗi vai trò mục tiêu đang nằm trong §8.1". Tiêu chí: "Với mỗi vai trò mục tiêu trong §8.1 có đúng một URL". §8.1: "mỗi vai trò mục tiêu đang bật", rồi "khi công khai: 4–5 vai trò mục tiêu". Câu 3 còn hỏi "4–5 vai trò mục tiêu nào". Ba cách gọi không cùng một tập. §3: vai trò mục tiêu là "Vai trò hoặc nhánh mà người dùng đang chọn để so sánh". §8.1 viết "Backend (nhánh Java Backend)", vừa vai trò vừa nhánh. FR-48 không chọn trang theo vai trò hay theo nhánh. "Đang bật" ở FR-22 nghĩa là có biên bản đồ thị học trước – học sau thì mới bật trong Cố vấn. Trang này chỉ cần mặt bằng kỹ năng. PRD không nói vai trò chưa có đồ thị có một URL hay không. *Fix:* chốt trang theo vai trò (Backend, Data/AI, …) hoặc theo nhánh, và dùng đúng chữ của §3. Tập URL bằng danh sách vai trò lúc công khai, mỗi mục một URL, không cần biên bản đồ thị. Chừng nào câu 3 còn mở, tiêu chí áp lên đúng danh sách của bản phát hành đang kiểm. Thêm một mục bảng thuật ngữ cho trang này nếu "vai trò mục tiêu" giữ nghĩa "thứ người dùng đang chọn".

## 6. Downstream usability — adequate

FR-48 tách được khỏi các FR khác: một mục, một ID, các cấm tham chiếu FR-47 và §6.1 đều có chỗ đến. §1, §8.1, §8.2 và câu 7 đều trỏ FR-48. Không có UJ treo. Chỗ gãy khi UX và story rút mục này ra là thuật ngữ "vai trò mục tiêu" / "đang bật" (mục 5) và một câu addendum dán nhầm tầng.

PRD không lọt cách làm. Không có Next.js, ISR, `revalidatePath`, hay GET mồi trang. "Trang không tự tính số vào lúc có người mở" ở đúng tầng năng lực.

### Findings

- **[medium]** Addendum gọi tiêu chí năng lực là cách làm (addendum §1, FR-48) — Addendum: tiêu chí "số của snapshot mới phải có trước người đọc đầu tiên", "và việc trang chỉ đọc số tổng hợp qua API, nằm ở AD-13 và AD-14 của spine ngày 03/11. Không đưa vào PRD vì đó là cách làm." Vế đầu đã nằm trong PRD: "trước khi người đọc hoặc trình thu thập đầu tiên mở trang". Đó là điều phải đúng với người đọc. Vế API đúng là cách làm và đúng khi đứng ngoài PRD. Câu này gộp hai vế, gọi cả hai là cách làm, và trỏ AD-13/AD-14 mà không có đường dẫn file. Người sửa PRD theo câu đó sẽ cắt tiêu chí nghiệm thu vì tưởng là lọt cách làm. *Fix:* addendum chỉ giữ cách làm: trang đọc số tổng hợp qua API (AD-14), và cơ chế sinh lại trang trước lượt mở đầu tiên (AD-13), kèm đường dẫn tới `ARCHITECTURE-SPINE.md` của spine `architecture-HaiDoIT-2026-11-03`. Xóa câu "không đưa vào PRD" đối với tiêu chí số mới có trước người đọc đầu tiên.

## 7. Shape fit — adequate

Không đổi bởi delta này. Trang đọc là đặc tả năng lực, cùng kiểu §4.1, không cần thêm UJ.

## Mechanical notes

- FR-48 là ID kế tiếp, không trùng. FR-47 vẫn nằm ở §4.1; FR-48 ở §4.8. Thứ tự mục không đi theo số ID — kiểu này đã có từ trước với FR-47.
- Tham chiếu trong delta đều tới chỗ có thật: §1 → FR-48, §8.1 → FR-48 và FR-47, §8.2 → FR-48, câu 7 → FR-48, FR-48 → FR-47 và §6.1 và §8.1.
- Không thêm `[GIẢ ĐỊNH]`. §11 không đổi. Không có UJ mới.
- Ba cụm cho cùng một tập trang: "đang nằm trong §8.1", "đang bật", "4–5 vai trò mục tiêu". Xem finding ở mục 5.
- "URL ổn định" không nói ổn định qua sự kiện nào: đổi snapshot, đổi mã vai trò, hay rút vai trò khỏi danh sách công khai.
- "Snapshot đã công bố" không có trong §3. Xem finding ô thống kê ở mục 4.
- §8.1 bullet đầu vẫn là "Bảy tính năng tương tác, FR-1 đến FR-47", bullet mới nhắc lại FR-47 như trang chính sách. FR-47 đứng ở cả hai bullet.
- Hai dòng "Trang công khai" ở addendum §3 khớp §8.2 và mục "Ngoài phạm vi" của FR-48. Tên JSON-LD nằm ở addendum, không nằm trong PRD. Đúng tầng.
