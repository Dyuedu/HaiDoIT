# PRD Quality Review — PRD: Hải Đồ IT (prd-HaiDoIT-2026-11-02)

_Rà soát ngày 03/11/2026 theo `.claude/skills/bmad-prd/assets/prd-validation-checklist.md`. Bối cảnh: đồ án SEP490 trước hội đồng, đồng thời là MVP công khai cho sinh viên IT. PRD đứng đầu chuỗi UX → kiến trúc → epic/story. Đầu vào: `prd.md`, `addendum.md`, đối chiếu thêm với brief và `.memlog.md`._

_Một số nhận định được kiểm chứng trực tiếp trên `scraper/data/step-07-jev-extracted.jsonl` (3.469 dòng). Phép đếm dùng các trường `site`, `classification.title_category`, `classification.seniority_category`, `classification.location_category`, và `extracted_info.tech_stack` + `keywords` (so khớp chữ thường). Cách đếm này tái lập đúng mọi con số PRD trích: Backend 378, Java Backend 204, Spring Boot 51%, Microservices 68%, PostgreSQL 45%, CI/CD 40%, Docker 34%, Hà Nội 160 tin Backend, Data/AI chiếm 18% ở Hà Nội và 19,5% ở TP.HCM, Hà Nội giữ 47% và TP.HCM 38% số tin Data/AI. Vì vậy các con số bổ sung dưới đây cùng cơ sở với PRD._

## Overall verdict

Phần cơ chế của PRD chắc tay. FR nào cũng có mục "Kết quả kiểm chứng được". Bảng thuật ngữ có kỷ luật. Các quyết định khó (θ là tham số, mức khớp có trọng số, D2 không tính kỹ năng chưa nhận diện, "không ghi lương" không phải dấu hiệu) đều được ghi kèm phương án bị loại. Bộ chỉ số đối trọng tốt hơn hẳn mức thường gặp.

Rủi ro nằm ở nền dữ liệu và ở cách đo:
- các con số trong hành trình đến từ bộ 3.469 tin, trong đó 34% thuộc những nguồn chính PRD loại khỏi v1;
- ô mặc định Intern/Fresher/Junior của người dùng chính nằm dưới ngưỡng mẫu, nên lộ trình cho fresher thực chất được tính trên một tập gồm 83% tin Mid trở lên;
- SM-1 và SM-3, hai chỉ số hội đồng sẽ soi kỹ nhất, có lỗi cách đo làm kết quả đẹp lên.

Không lỗi nào buộc phải đổi cấu trúc FR. Phần lớn sửa được bằng định nghĩa, một bảng nguồn và vài quyết định ghi rõ.

## 1. Decision-readiness — adequate

Các quyết định được viết thành quyết định, không phải "cân nhắc". Ví dụ: "Một chiều cao chỉ mang một nghĩa" (FR-33), "Tin không ghi lương **không** là một dấu hiệu" (FR-31), "Quyết định của nhóm" (§6.1). Addendum §3 là bảng phương án bị loại kèm lý do: đúng thứ người phản biện cần, và hiếm PRD nào có. Các câu hỏi mở ở §10 là câu hỏi mở thật (z-test, tỷ giá, ai kiểm duyệt danh mục tài liệu); không câu nào đã có sẵn câu trả lời ngay sau.

Yếu điểm là hai căng thẳng lớn nhất bị lách thay vì được quyết:
- **TopCV.** §6.1 tự thừa nhận "Nhóm cần chuẩn bị câu trả lời nếu hội đồng hỏi", tức là chưa có câu trả lời.
- **Nguồn dữ liệu của bản công khai.** PRD không có bảng nguồn nào, trong khi mọi con số minh họa đến từ một bộ dữ liệu trộn cả những nguồn bị loại.

Toàn tài liệu không có callout `[NOTE FOR PM]` nào, kể cả ở hai chỗ này.

### Findings
- **[high]** Số liệu của mọi hành trình dựa vào nguồn mà v1 tự loại (§0 "Nguồn của các con số", UJ-1, UJ-3, FR-33, §6.2, §8.2) — Bộ 3.469 tin gồm TopCV 1.323 (38%), LinkedIn 625 (18%), VietnamWorks 591 (17%), ITviec 555 (16%), TopDev 375 (11%). §8.2 loại "Dữ liệu LinkedIn"; §6.2 cho ITviec "chỉ dùng làm bộ kiểm tra nội bộ, công tắc tắt trên bản công khai". Nếu bỏ hai nguồn này:
  - Backend giảm từ 378 xuống 184 tin, Java Backend từ 204 xuống 105, Backend ở Hà Nội từ 160 xuống 117;
  - nhóm "Other" ở TP.HCM (23,4%) vượt Data/AI (19,5%), nên câu "Data/AI là vai trò chiếm tỷ trọng tin cao nhất ở cả hai thành phố" ở UJ-3 phải tính lại (dù FR-7 sẽ tách Embedded khỏi Other);
  - tỷ trọng của Hà Nội trong tin Data/AI tăng từ 47% lên 60%.

  Câu mồi trên Facebook ở UJ-1 ("3.469 tin… 378 tin Backend") vì thế sẽ công bố số liệu rút từ ITviec và LinkedIn. VietnamWorks và TopDev, cộng lại 28% dữ liệu, không được nhắc tới ở §6.2. Các crawler mới (CareerLink, ITNavi, Zalo Careers, MoMo) mà bảng thuật ngữ lấy làm ví dụ cho "Nguồn" lại không có trong bộ 3.469 tin. Ngoài ra, "snapshot ngày 26/10/2026" không phải một snapshot theo định nghĩa ở §3: 1.660/3.469 dòng không có `date_posted`, phần còn lại rải trong tháng 9–10/2026. *Fix:* thêm vào §6.2 bảng nguồn của v1, mỗi dòng gồm nguồn, tình trạng pháp lý, công tắc trên bản công khai và tỷ trọng dữ liệu. Ghi thành quyết định vai trò của bộ 3.469 tin: lớp dữ liệu nền nội bộ, hay được phép công bố số tổng hợp. Tính lại các con số ở UJ và FR-33 trên tập nguồn công khai, hoặc gắn nhãn "số minh họa từ bộ dữ liệu nội bộ".
- **[high]** TopCV: mốc bỏ kỹ thuật né bot không khớp với sự kiện công khai (§6.1, FR-2, §8.1, SM-C1, §10 câu 5) — §6.1 viết "bỏ kỹ thuật này trước khi thương mại hóa", nhưng v1 công khai (addendum của brief đặt mốc này ở Sprint 5, 30/11–6/12) và không có sự kiện thương mại hóa nào trong phạm vi. Mốc gỡ vì thế không bao giờ đến, và bản công khai chạy crawler mà chính báo cáo nghiên cứu xếp "rủi ro rất cao… Điều 289 Bộ luật Hình sự". SM-C1 cấm "bật thêm nguồn vi phạm FR-2", trong khi TopCV vi phạm FR-2 và vẫn bật. §8.1 ("Chỉ các nguồn đang bật công tắc trên bản công khai") và câu hỏi mở số 5 đều không trả lời được câu "TopCV có bật trên bản công khai không". *Fix:* ghi một quyết định riêng cho bản công khai. Phương án (a): công tắc TopCV tắt từ ngày công khai, dữ liệu TopCV chỉ làm bộ kiểm tra nội bộ như ITviec. Phương án (b): vẫn bật nhưng bỏ kỹ thuật né bot từ ngày công khai và tuân thủ FR-2. Viết sẵn câu trả lời cho hội đồng vào §6.1, gắn `[NOTE FOR PM]`, và sửa SM-C1 thành "…vi phạm FR-2, ngoài ngoại lệ đã ghi ở §6.1".

## 2. Substance over theater — strong

PRD có hai persona, và mỗi người đều kéo theo quyết định:
- **Minh** dẫn tới FR-10–12, FR-21, phần "Có làm nhưng CV không ghi", và Soi tin;
- **Lan** dẫn tới FR-13, FR-24, và nhánh dùng không cần CV.

Tầm nhìn xoay quanh một câu hỏi cụ thể ("Kỹ năng này xuất hiện trong bao nhiêu phần trăm tin tuyển dụng cùng vai trò ở Việt Nam?"), không đem thay sang PRD khác được. Các điểm khác biệt đều có cơ chế đi kèm và kiểm thử được: FR-22 tất định, FR-23 có kiểm thử regex bảo đảm lời dẫn không chứa số, FR-39 không dùng LLM cho Insights. NFR có ngưỡng cụ thể (15 giây, 1 giây, n ≥ 30, 5 MB), không phải tính từ.

### Findings
- **[low]** Tuyên bố tuyệt đối trong Tầm nhìn (§1) — "trả lời được câu hỏi mà chưa công cụ nào trả lời". Hội đồng chỉ cần đưa ra một báo cáo "top skills" của ITviec hay TopDev là câu này lung lay, dù khác biệt thật nằm ở *theo vai trò, có cỡ mẫu, cập nhật hằng ngày*. *Fix:* viết lại đúng phạm vi đó, ví dụ: "chưa công cụ công khai nào trả lời theo từng vai trò, kèm cỡ mẫu, và cập nhật hằng ngày".

## 3. Strategic coherence — thin

Mạch chiến lược rõ: dữ liệu → bộ máy kỹ năng → Cố vấn và Soi tin, với Bản đồ và Insights làm cửa vào. Thứ tự sprint trong addendum của brief đi theo đúng luận đề. Các chỉ số đối trọng SM-C1–C5 nêu cả cách *không được* tối ưu; đây là phần tốt nhất của §9.

Tuy vậy, hai chỗ chịu lực của luận đề chưa đứng được:
- §2.1 hứa giúp người dùng biết thị trường cần gì "cho đúng vai trò và cấp bậc của mình", nhưng dữ liệu không đỡ được chiều cấp bậc cho đúng người dùng chính;
- các chỉ số chính SM-1 và SM-3 có lỗi cách đo, và lỗi đều nghiêng về phía làm kết quả đẹp lên.

Thêm vào đó, giả thuyết trung tâm ("thiếu kỹ năng cốt lõi") chỉ được phát biểu trong brief, không có trong PRD.

### Findings
- **[critical]** Ô mặc định của fresher dưới ngưỡng mẫu, và tập quay về nghiêng hẳn về Mid/Senior (§2.1, FR-18, FR-19, UJ-1, §6.3) — FR-18 đặt cấp bậc mặc định là Intern/Fresher/Junior. Với Java Backend, ô này chỉ có 26/204 tin, dưới 30, nên theo FR-19 lộ trình được tính trên cả 204 tin. Trong 204 tin đó có 68 Mid, 59 Lead/Principal, 38 Senior, 4 Manager/Director, tức 83% là Mid trở lên. Trên tập nguồn công khai (bỏ LinkedIn và ITviec), ô này còn 12 tin, và ngay cả Backend × Intern/Fresher/Junior cũng chỉ có 28.

  Trong 26 tin junior, tỷ lệ xuất hiện là Microservices 19%, PostgreSQL 19%, Docker 12%, CI/CD 8%: đều dưới θ_core. Với n = 26, đây chỉ là chỉ báo về hướng, không phải ước lượng tin cậy. Dù vậy, UJ-1 báo cho một fresher các "khoảng trống cốt lõi: Microservices (68%)…" mà phần lớn đến từ yêu cầu của tin cấp cao. Hậu quả:
  - lời hứa "đúng cấp bậc" không giữ được cho chính persona chính;
  - SM-1 bị thổi phồng, vì kỹ năng của tin cấp cao bị gắn nhãn cốt lõi. SM-C2 chỉ chặn việc hạ θ_core, không chặn được nguồn lệch này.

  §6.3 chỉ ghi chung chung "nhiều ô thống kê sẽ quay về toàn bộ vai trò", không nêu con số, cũng không nêu chiều lệch. *Fix:* ghi vào §6.3 cỡ mẫu Intern/Fresher/Junior của mọi vai trò mục tiêu dự kiến công khai. Quyết định một trong các hướng sau và gắn `[NOTE FOR PM]`:
  - (a) mở rộng ô mặc định thành "≤ 3 năm" (Intern/Fresher/Junior + Mid) nếu cỡ mẫu cho phép;
  - (b) nhãn quay về phải nêu cơ cấu cấp bậc của tập quay về, ví dụ "83% tin trong tập này là Mid trở lên";
  - (c) tích lũy snapshot để tăng n của ô junior trước khi công khai;
  - (d) đánh dấu những kỹ năng có tỷ lệ trong tin junior thấp hơn hẳn tỷ lệ chung.

  Sau đó viết lại bước 3–4 của UJ-1 cho trung thực: hiển thị nhãn quay về như FR-19 yêu cầu.
- **[high]** SM-1 bị thổi phồng ngay từ cách đo (§9 SM-1, FR-42, FR-21, FR-9) — Có ba vấn đề:
  1. **Giới hạn 3 kỹ năng.** Modal đầu phiên chỉ cho chọn "tối đa 3 kỹ năng người thử nghĩ mình cần học nhất", trong khi FR-9 hiệu chỉnh θ sao cho mỗi vai trò có ít nhất 3 kỹ năng cốt lõi. Người thử thiếu từ 4 kỹ năng cốt lõi trở lên, chỉ cần bấm "Tôi chưa biết", là gần như chắc chắn được tính vào SM-1. Hơn nữa "cần học nhất" không có nghĩa là "biết mình còn thiếu".
  2. **Tử số phụ thuộc vào một cú bấm không có tác dụng.** Tử số cần cú bấm "Tôi chưa biết", mà FR-21 định nghĩa là "kỹ năng ở lại trong lộ trình học", tức không có hiệu ứng nhìn thấy được. SM-1 vì thế đo hành vi bấm nút nhiều hơn là phát hiện điểm mù.
  3. **Mẫu số chưa định nghĩa.** Không rõ mẫu số gồm mọi phiên, hay chỉ những phiên đã hoàn tất modal cuối.

  *Fix:* ở modal đầu phiên, hỏi "chọn mọi kỹ năng bạn biết mình còn thiếu cho vai trò này", không giới hạn số lượng, tìm trên toàn bộ từ vựng, và không hiển thị danh sách cốt lõi. Định nghĩa điểm mù là kỹ năng cốt lõi được bấm "chưa biết" mà không có trong danh sách đó. Báo cáo kèm phân phối số khoảng trống cốt lõi của mỗi người thử. Mẫu số chỉ gồm phiên đã hoàn tất cả hai modal. Cho nút "Tôi chưa biết" một hiệu ứng nhìn thấy được, ví dụ ghim kỹ năng vào mục "sẽ học".
- **[high]** So sánh mù ở SM-3 khó còn mù, và phương án ChatGPT có thể bị chọn lệch (FR-44, SM-3, addendum §2) — Người thử vừa dùng Hải Đồ IT khoảng 15 phút. Phong cách đầu ra của nó (tỷ lệ %, cỡ mẫu n, nhãn cốt lõi/thường gặp, chặng) nhận ra ngay khi đặt cạnh văn xuôi của ChatGPT. Addendum đã loại một phương án vì lý do "người thử nhận ra ngay", nhưng cùng kiểu lộ nguồn đó vẫn tồn tại qua phong cách. "Câu trả lời ChatGPT soạn sẵn" chưa ghi prompt, model, ngày tạo, hay cách chọn câu trả lời, nên nhóm có thể vô tình chọn một câu yếu. Tiêu chí "được chọn nhiều hơn" với n = 30–50 không có ngưỡng thống kê: 26/50 cũng tính là đạt. Đây lại là câu hội đồng chắc chắn hỏi (brief: "Sao không dán CV và JD vào ChatGPT cho xong?"). *Fix:*
  - đưa cả hai phương án về cùng một khuôn văn bản (cùng cấu trúc, cùng giới hạn độ dài; hoặc bỏ số ở cả hai, hoặc đưa cùng bảng số cho ChatGPT);
  - cố định và công bố prompt, model, ngày tạo; sinh k câu trả lời rồi chọn ngẫu nhiên một câu;
  - thêm câu hỏi "Bạn đoán phương án nào là Hải Đồ IT?" để đo mức độ mù;
  - báo cáo khoảng tin cậy hoặc kiểm định dấu (sign test) cho tỷ lệ chọn.
- **[medium]** Giả thuyết trung tâm không có trong PRD, và "Giới hạn đã biết" của brief bị rơi mất (§1, §9 SM-9) — SM-9 viết "Báo cáo để kiểm chứng giả thuyết 'thiếu kỹ năng cốt lõi'", nhưng giả thuyết này chỉ được định nghĩa trong brief. Mục "Giới hạn đã biết" của brief ("người thử phần lớn là sinh viên cùng một trường và quen nhóm phát triển; 2 tuần chỉ đo được nhận thức và ý định") cũng không có ở §9. Thiếu mục này, SM-2 (chỉ một câu Có/Không về ý định) dễ bị đọc như bằng chứng hành vi. *Fix:* thêm vào §1 hoặc §9 một đoạn "Giả thuyết" lấy từ brief, nối từng chỉ số SM-1/2/3/9 với vế giả thuyết mà nó kiểm chứng, và chép mục "Giới hạn đã biết" vào §9.
- **[medium]** Phân cấp thị giác ở FR-21 làm lệch SM-9 và SM-10 (FR-21, addendum §1 mục FR-21, SM-9, SM-10) — "CV của tôi có ghi rồi (hệ thống đọc sót)" chỉ là "link chữ hoặc biểu tượng nhỏ", trong khi "Tôi đã biết, chỉ là CV chưa ghi" là nút chính. Những kỹ năng bộ đọc CV bỏ sót vì thế dễ bị ghi nhận thành "CV chưa ghi". Kết quả là SM-9, bằng chứng cho giả thuyết, đẹp lên, và SM-10 (recall) cũng đẹp lên vì ít ai báo đọc sót. *Fix:* trong chế độ thử nghiệm, tách thành hai câu hỏi ngang hàng: "Bạn đã biết kỹ năng này chưa?" và "CV của bạn có ghi kỹ năng này không?". Hoặc giữ phân cấp thị giác nhưng ghi rõ chiều lệch này cạnh định nghĩa SM-9 và SM-10.

## 4. Done-ness clarity — adequate

Mục "Kết quả kiểm chứng được" có mặt ở cả 45 FR; đây là điểm mạnh lớn nhất cho bước viết story. Nhiều FR có ví dụ kiểm được ngay:
- FR-3: xuất hiện trong 3 snapshot thì số lần thấy bằng 3;
- FR-19: nhãn quay về có số cụ thể;
- FR-28: 16/18 = 89%;
- FR-31: bảng điều kiện D1–D4;
- FR-33: tổng tỷ trọng bằng 100%.

Lỗ hổng tập trung ở vài định nghĩa nền mà mọi con số dựa vào, ở cách đếm "đăng lại", và ở bộ đọc CV (đầu vào của luồng chính nhưng không có ngưỡng chất lượng).

### Findings
- **[high]** "Ô thống kê" không có cửa sổ thời gian (§3 "Ô thống kê", "Snapshot", FR-9, §4.6) — Không rõ ô thống kê gồm những tin còn sống trong snapshot mới nhất, mọi tin từng thấy, hay các tin trong N ngày gần nhất. "Ảnh chụp trạng thái của toàn bộ tin tuyển dụng tại một ngày" đọc theo cả hai cách đều được. §4.6 viết "tính trên snapshot mới nhất". Mọi n, tỷ lệ và phân vị đều phụ thuộc vào định nghĩa này. Các con số ở UJ (n = 204) đến từ dữ liệu cộng dồn tháng 9–10; tập tin còn sống trong một ngày sẽ nhỏ hơn nhiều, và nhiều ô sẽ rơi xuống dưới ngưỡng. *Fix:* định nghĩa trong §3, ví dụ: "Ô thống kê gồm các cụm tin có ngày thấy lần cuối trong N ngày gần nhất (N = …), mỗi cụm tính một lần". Nêu rõ bộ dữ liệu ban đầu được nạp vào chuỗi snapshot thế nào.
- **[high]** "Đăng lại" bị đếm sai khi một nguồn lỗi trong một đêm (FR-3, FR-1, FR-31 D4) — FR-3 viết "Một tin biến mất rồi xuất hiện lại được tính thêm một lần đăng lại", còn FR-1 cho phép một nguồn lỗi trong khi các nguồn khác vẫn chạy. Chỉ cần một đêm TopCV trả 403 hay captcha, mọi tin của TopCV "biến mất" rồi xuất hiện lại, và đều bị cộng một lần đăng lại. Sau hai sự cố như vậy, D4 kích hoạt hàng loạt và hiển thị "Tin đã đăng lại X lần": một khẳng định sự thật về nhà tuyển dụng, nhưng sai. Trường hợp phổ biến hơn, đăng lại với mã tin mới, lại không được xử lý; cũng không rõ vòng đời tính theo tin hay theo cụm (FR-4). *Fix:* chỉ tính "biến mất" khi lượt chạy của nguồn đó thành công và đã quét tới trang chứa tin. Tính vòng đời theo cụm. Đăng lại được định nghĩa là xuất hiện một mã tin mới trong cùng cụm sau khoảng nghỉ ≥ K ngày. Thêm kết quả kiểm chứng: "nguồn lỗi một đêm không làm tăng số lần đăng lại".
- **[high]** Bộ đọc CV không có ngưỡng chất lượng, và yêu cầu tất định chưa có cơ chế (FR-12, SM-6, §6.4, SM-C2) — Kết quả kiểm chứng của FR-12 chỉ gồm tất định và thời gian. SM-6 ghi "Kiểm chứng FR-6, FR-12", nhưng bộ chuẩn chỉ gồm 200 JD. CV khác JD: có mô tả dự án, trộn Việt–Anh, có bảng trong DOCX. Phần "Có làm nhưng CV không ghi" của UJ-1 phụ thuộc trực tiếp vào bộ đọc này, và chính SM-C2 thừa nhận đọc sót sẽ làm SM-1 đẹp lên. Ngoài ra, "Cùng một CV luôn cho cùng một tập kỹ năng" với bước trích bằng LLM (§6.4) không tự đúng: temperature 0 không bảo đảm điều đó. *Fix:* thêm bộ chuẩn CV (≥ 30 CV có đồng ý, gán nhãn tay) với ngưỡng precision và recall, và sửa phần truy vết của SM-6. Viết lại yêu cầu tất định thành "cùng nội dung văn bản cho cùng kết quả, nhờ cache theo hash nội dung (chỉ lưu hash và mã kỹ năng)", hoặc nới thành "trùng ≥ X% qua N lần chạy".
- **[medium]** FR-7 không có ngưỡng nghiệm thu; cấp bậc và thành phố không được kiểm (FR-7, §3 "Tin tuyển dụng", FR-33) — FR-7 chỉ yêu cầu "Báo cáo độ chính xác phân loại vai trò", không có ngưỡng đạt. Cấp bậc quyết định ô mặc định (xem finding critical ở mục 3) nhưng không có kiểm chứng nào. Về thành phố, §3 viết "Mỗi tin thuộc đúng… một thành phố", trong khi FR-33 có "phần không xác định thành phố"; tin nhiều thành phố và tin remote chưa được định nghĩa. Việc tách Data/AI được viết vô điều kiện, trái với quy tắc "Nhánh chỉ tồn tại khi có từ 30 tin". *Fix:* đặt ngưỡng trên bộ 200 JD, ví dụ vai trò ≥ 85%, cấp bậc ≥ 80%. Định nghĩa cách xử lý tin nhiều thành phố, remote và không rõ thành phố. Cho việc tách Data/AI tuân theo quy tắc 30 tin.
- **[medium]** FR-30 và FR-32 thiếu định nghĩa để kiểm thử (FR-30, FR-31, FR-32) — Ở FR-30:
  - phân vị lương tính theo mức sàn, mức trần hay điểm giữa? (D3 dùng "lương trần");
  - phân vị số năm kinh nghiệm không có quy tắc n ≥ 30 như lương, trái với §5 ("Ô thống kê dưới ngưỡng mẫu thì nói 'chưa đủ dữ liệu'");
  - câu "Nếu không, ghi 'chưa đủ dữ liệu (X/30 tin có lương)'" cũng kích hoạt khi chính tin được dán không ghi lương, chồng lên dòng thông tin trung tính của FR-31.

  Ở FR-32, "dùng cùng cách so khớp như FR-4" không khả thi, vì FR-4 dựa vào "tên công ty đã chuẩn hóa" mà người dùng thường chỉ dán phần mô tả, không có tên công ty. Kiểm thử duy nhất lại là dán nguyên văn. *Fix:* định nghĩa cụ thể từng điểm trên, và thêm kiểm thử dán một phần (chỉ dán mục yêu cầu) với ngưỡng tìm đúng.
- **[medium]** FR-22: "chặng" chưa định nghĩa rõ, và kiểm tra phủ đồ thị không theo kịp dữ liệu hằng đêm (§3 "Chặng", FR-22, FR-9) — "Độ sâu" trên một DAG có hai nghĩa: đường ngắn nhất hay đường dài nhất. Nếu là đường ngắn nhất, sắp xếp "Tầng 1: chặng tăng dần" có thể đặt một kỹ năng trước tổ tiên của nó, trái với chính kiểm thử của FR-22. Thuật toán Kahn trong addendum tránh được lỗi này, nhưng quy tắc trong PRD thì không. Kiểm tra phủ đồ thị chạy "trước khi triển khai", trong khi nhóm kỹ năng được tính lại mỗi đêm (FR-9). Một kỹ năng vượt θ_common qua đêm sẽ không có nút trên đồ thị, và hành vi lúc chạy chưa được định nghĩa. *Fix:* định nghĩa "chặng = độ dài đường dài nhất từ một nút gốc". Chạy kiểm tra phủ sau mỗi lần FR-9 tính lại. Định nghĩa phương án dự phòng khi thiếu nút (hiển thị trong mục "chưa xếp chặng" kèm nhãn) và gửi cảnh báo cho nhóm.
- **[medium]** Danh sách trường của FR-17 là danh sách đóng, nhưng các FR khác cần thêm trường (FR-17, §5 "Quyền riêng tư", FR-21, FR-41, SM-1, SM-9) — §5 viết "Sự kiện ẩn danh chỉ chứa những trường đã liệt kê ở FR-17", tức chỉ có mã phiên, loại thao tác, mã kỹ năng và vai trò mục tiêu. Trong khi đó:
  - FR-21 ("lựa chọn sau cùng là lựa chọn có hiệu lực") cần thời điểm hoặc số thứ tự;
  - FR-41 cần cờ đánh dấu thử nghiệm;
  - SM-9 ("những phiên có tải CV") cần biết hồ sơ đến từ đâu;
  - §5 ("Mọi con số truy ngược được về snapshot") cần mã snapshot.

  *Fix:* bổ sung vào FR-17 các trường thời điểm, cờ thử nghiệm, nguồn hồ sơ (CV/tự chọn), cấp bậc và mã snapshot, và cập nhật §5 cho khớp.
- **[medium]** FR-21 chưa tính tới người không có CV (FR-21, FR-13, UJ-3, FR-16) — Lan (UJ-3) không có CV vẫn thấy nút "Tôi đã biết, chỉ là CV chưa ghi", và kỹ năng được đẩy vào "danh sách kỹ năng cần bổ sung vào CV". Danh sách này vô nghĩa với Lan nhưng lại là phần đầu của bản tóm tắt FR-16. *Fix:* khi hồ sơ không đến từ CV, chỉ hiện hai lựa chọn "Tôi đã biết" (thêm vào hồ sơ, không vào danh sách CV) và "Tôi chưa biết". Ghi rõ cách SM-1 tính cho nhánh này.
- **[medium]** NFR thiếu giới hạn cho bản công khai (§5, §6.4, SM-C5, FR-26) — Sản phẩm công khai, không cần đăng nhập, và mỗi lần dán tin (tối đa 20.000 ký tự) hay tải CV đều gọi một LLM trả phí. PRD không có giới hạn theo phiên hay IP, không có trần ngân sách theo ngày, và không có mục tiêu tải đồng thời cho đợt tăng truy cập sau bài đăng Facebook. SM-C5 chỉ theo dõi chi phí, không có trần. *Fix:* thêm vào §5:
  - giới hạn lượt dùng, ví dụ ≤ N lần soi tin mỗi giờ cho một phiên;
  - trần chi phí LLM theo ngày, khi chạm trần thì xuống cấp nhẹ nhàng ("tạm hết lượt, bạn có thể tự chọn kỹ năng");
  - mục tiêu tải, ví dụ 50 người dùng đồng thời với p95 < 15 giây;
  - mục tiêu sẵn sàng trong tuần thử nghiệm.
- **[low]** Thẻ "Ngành" của Insights không có nguồn dữ liệu (FR-37) — Thẻ "Ngành và nhà tuyển dụng nổi bật" cần phân loại ngành của công ty (Fintech, Banking), nhưng không FR nào ở §4.1 trích hay phân loại ngành. *Fix:* bổ sung phân loại ngành vào FR-7, hoặc rút thẻ về "nhà tuyển dụng nổi bật".
- **[low]** Một vài tiêu chí còn chưa đo được (FR-2, FR-11, FR-15, FR-16, FR-26) — Cụ thể:
  - FR-2: "giãn cách cố định" nhưng không ghi bao nhiêu giây;
  - FR-11: "30 ký tự có nghĩa" chưa định nghĩa, và "trong vòng 1 giây kể từ lúc tải lên" chưa rõ tính từ lúc bắt đầu hay lúc tải xong;
  - FR-15: "hiển thị đúng lộ trình học như trên máy gốc" chỉ đúng khi cùng snapshot, mà Lan quay lại sau 2 tuần; cũng chưa rõ mở link có ghi đè hồ sơ đang có của người nhận không;
  - FR-16: định dạng tải về chưa nêu;
  - FR-26: tiêu chí nhận biết "không thuộc lĩnh vực IT" chưa có.

  *Fix:* bổ sung giá trị hoặc định nghĩa cho từng chỗ. Với FR-15, đưa mã snapshot vào link hoặc ghi rõ kết quả có thể khác.

## 5. Scope honesty — adequate

§7 "Không làm gì" và §8.2 làm việc thật: không tài khoản, không chatbot, không dự báo, không OCR, không LinkedIn, không có trạng thái "đang học". Mỗi mục đều chặn một giả định dễ bị suy ra ngầm.

Mật độ mục mở gồm 6 câu hỏi mở, 1 `[GIẢ ĐỊNH]` và 0 `[NOTE FOR PM]`. Mức thấp này một phần xứng đáng, vì memlog cho thấy nhiều giả định đã được nhóm chốt trong phiên (các dòng ghi "gỡ GIẢ ĐỊNH"). Nhưng với một bản công khai, chỗ còn thiếu lại rơi đúng vào những nơi có rủi ro: pháp lý của bước xử lý CV, đường cắt giảm phạm vi, và khâu vận hành.

### Findings
- **[high]** 45 FR trong 8 tuần mà không có đường cắt giảm (§8.1, §6.5) — §8.1 ghi "Bảy tính năng với FR-1 đến FR-45" và không phân hạng gì. Khối lượng thủ công lại lớn:
  - đồ thị học trước – học sau cho 4–5 vai trò, chờ giảng viên rà soát;
  - danh mục tài liệu;
  - lời dẫn cho từng cặp kỹ năng × vai trò, có rà soát;
  - 200 JD gán nhãn bởi 2 người, khoảng 100 cặp tin trùng, 100 tin ngẫu nhiên;
  - bản đồ 3D cộng chế độ 2D bắt buộc;
  - chế độ thử nghiệm.

  Chế độ thử nghiệm (FR-41–45), công cụ duy nhất đo được các chỉ số chính, lại xếp sau Bản đồ và Insights (Sprint 5–6 trong addendum của brief). Nếu trễ, SM-1–3 sẽ mất đầu tiên. *Fix:* thêm §8.3 "Thứ tự cắt giảm khi trễ" theo luận đề:
  - giữ: pipeline, bộ máy kỹ năng, Cố vấn, chế độ thử nghiệm, phần "so với hồ sơ" của Soi tin;
  - cắt trước: 3D (giữ 2D), thẻ Insights 3–5, D3/D4, FR-15.

  Gắn nhãn phải có / nên có cho từng FR.
- **[high]** Nội dung CV được gửi tới LLM bên ngoài mà ô đồng ý không nói (FR-10, §5 "Quyền riêng tư", §6.2, §6.4) — §6.4 xác nhận có gọi LLM để trích kỹ năng từ CV. Phương án stack ở addendum của brief (§3) còn ghi "đọc CV PDF trực tiếp", tức gửi cả tên, số điện thoại và email. Ô đồng ý ở FR-10 nêu ba điều nhưng không nói CV được chuyển cho một bên xử lý bên ngoài, có thể ở nước ngoài. Câu "không lưu… thông tin định danh" chỉ đúng với server của nhóm. PRD tự lấy Luật 91/2025 làm khung (§6.2); theo khung đó, việc chuyển dữ liệu cho bên xử lý và chuyển ra nước ngoài nhiều khả năng phải được thông báo (nhóm cần đối chiếu điều khoản cụ thể). Thứ tự giữa bước xóa PII ở FR-5 và bước gửi JD cho LLM cũng chưa nêu. *Fix:*
  - ô đồng ý ở FR-10 nêu tên bên xử lý, mục đích và thời hạn lưu của họ;
  - thêm một FR: loại thông tin định danh khỏi văn bản CV *trước khi* gửi LLM (dùng lại mẫu của FR-5), với kiểm thử "payload gửi LLM không khớp mẫu email hoặc số điện thoại";
  - cấu hình nhà cung cấp không lưu dữ liệu, và ghi điều này vào §6.2.
- **[medium]** Khâu vận hành nội bộ không có FR, cũng không được ghi là non-goal (FR-1 "nhóm vận hành", FR-6/FR-29 "danh sách chờ… rà soát hằng tuần", FR-9, FR-23, §3 "Đồ thị học trước – học sau", "Danh mục tài liệu") — Ai bật/tắt nguồn, ai đổi θ, ai duyệt danh sách chờ để thêm vào bộ từ vựng, ai sửa đồ thị, ai rà soát lời dẫn LLM: PRD đều không nói, và cũng không nói làm qua giao diện hay qua script. Câu hỏi mở số 6 chỉ hỏi về danh mục tài liệu. *Fix:* thêm một mục non-goal "v1 không có trang quản trị; vận hành qua file cấu hình, script và SQL". Ghi người phụ trách cho từng tài sản (bộ từ vựng, đồ thị, danh mục, lời dẫn) cùng nhịp rà soát.
- **[medium]** Một số mục của brief bị bỏ âm thầm (§4.4, §9, so với brief) — Phần Soi tin "so với thị trường" trong brief có "chất lượng JD"; PRD không còn mục này và không nói đã gộp vào D1/D2 hay bỏ hẳn. "Thực nghiệm phụ" của brief (hỏi chatbot nhiều lần để đo độ lệch thứ tự học, addendum brief §4), vốn là bằng chứng cho điểm khác biệt "lộ trình tất định" ở §1, không xuất hiện ở §9. *Fix:* với từng mục, hoặc liệt kê vào §8.2, hoặc đưa thành một chỉ số phụ, hoặc ghi rõ đã gộp vào đâu.
- **[medium]** Giả định chưa gắn nhãn và không có `[NOTE FOR PM]` nào (toàn tài liệu, §11) — Chỉ có một `[GIẢ ĐỊNH]` (SM-5). Những giả định sau chưa được gắn nhãn:
  - tuyển đủ 30–50 người thử, 40% ngoài trường, trong Sprint 6–7;
  - giảng viên kịp rà soát đồ thị của 4–5 vai trò;
  - ITviec, TopCV và tác giả repo trả lời kịp trước khi công khai;
  - độ trễ của LLM nằm vừa trong 15 giây;
  - có người đảm nhận vai trò "nhóm vận hành".

  *Fix:* gắn `[GIẢ ĐỊNH]` cho các mục trên và đưa vào §11. Thêm `[NOTE FOR PM]` ở §6.1, §6.3 và §8.1.

## 6. Downstream usability — adequate

PRD đứng đầu chuỗi nên chiều này nặng ký. §3 tự tuyên bố ràng buộc ("Không dùng từ đồng nghĩa thay thế") và phần lớn được dùng nhất quán. ID FR-1..45, UJ-1..3, SM-1..10 và SM-C1..C5 đều liên tục, không trùng. Mỗi FR ghi "Thực hiện UJ-N", nên luồng truy vết UJ → FR chạy được. Vấn đề là ở vài chỗ, UJ hoặc chính bảng thuật ngữ mâu thuẫn với FR, trong khi bảng thuật ngữ là nguồn mà UX và epic được yêu cầu bám theo.

### Findings
- **[medium]** UJ-2 và Bảng thuật ngữ mâu thuẫn FR-31 về "không ghi lương" (UJ-2 bước 5, §3 "Dấu hiệu cần kiểm tra", FR-31) — UJ-2 viết "Hệ thống nêu hai dấu hiệu cần kiểm tra: … tin không ghi lương". §3 lấy "không ghi lương" làm ví dụ cho dấu hiệu. Còn FR-31 viết "Tin không ghi lương **không** là một dấu hiệu", và addendum §3 nêu lý do: dấu hiệu này kích hoạt trên khoảng 76% số tin. Phần cao trào của UJ-2 (bỏ qua công ty B) vì thế dựa một phần vào một dấu hiệu đã bị loại. *Fix:* sửa bước 5 của UJ-2 thành chỉ có D1, cộng dòng thông tin lương trung tính. Thay ví dụ trong §3 bằng D2 hoặc D4.
- **[medium]** UJ-1 xếp Redis và Kafka sai nhóm theo chính dữ liệu và ngưỡng của PRD (UJ-1 phần Cao trào, §0) — Trên Java Backend (n = 204), Redis có tỷ lệ 63/204 = 30,9% và Kafka 62/204 = 30,4%, đều ≥ θ_core = 30%, nên là kỹ năng *cốt lõi*. UJ-1 lại xếp cả hai vào "nhóm thường gặp" và chỉ liệt kê bốn khoảng trống cốt lõi. Như vậy là trái với quyết định ghi trong memlog: "Mọi con số trong PRD… phải khớp dữ liệu thật". Hai kỹ năng này chỉ cao hơn ngưỡng 0,4–0,9 điểm phần trăm, nên sẽ đổi nhóm qua lại giữa các snapshot và làm lộ trình của cùng một người xáo trộn từ ngày này sang ngày khác. *Fix:* sửa UJ-1 cho đúng (sáu khoảng trống cốt lõi, hoặc điều chỉnh những gì Minh đã biết). Thêm vào §10 câu hỏi về vùng đệm cho ranh giới nhóm, ví dụ chỉ đổi nhóm khi vượt ngưỡng ±2 điểm hoặc vượt liên tục 2 snapshot.
- **[medium]** UJ-3 dùng thẻ Insights khác với định nghĩa ở FR-37/FR-38; ô thống kê của Insights định nghĩa sai (UJ-3 bước 2, FR-37, FR-38, §3 "Ô thống kê") — Có ba chỗ lệch:
  - UJ-3 dùng thẻ "Bộ kỹ năng hay đi cùng nhau" để cho thấy "SQL, Docker và Git xuất hiện nhiều ở cả hai hướng", tức giao giữa hai vai trò; FR-37 lại định nghĩa thẻ này là các cặp kỹ năng đi cùng nhau *trong từng vai trò*;
  - UJ-3 viết "Thẻ nào chưa đủ 30 mẫu thì được ghi chú rõ", nhưng FR-38 ẩn hẳn các thẻ đó;
  - §3 định nghĩa ô thống kê của Insights là "thành phố × vai trò", trong khi 4/5 loại thẻ tính theo vai trò hoặc vai trò × cấp bậc trên toàn quốc.

  *Fix:* thống nhất UJ-3 với FR-37 và FR-38 (hoặc thêm một loại thẻ "kỹ năng chung giữa hai vai trò"), và sửa định nghĩa ô thống kê của Insights theo từng loại thẻ.

## 7. Shape fit — adequate

Đây là sản phẩm cho người dùng cuối, đứng đầu chuỗi, nên dạng PRD đi theo hành trình người dùng, với ba UJ có nhân vật được đặt tên, là đúng. §4.1 (pipeline) được viết dưới dạng đặc tả năng lực, không ép thêm UJ; như vậy cũng hợp lý. Còn thiếu hai hành trình có sức nặng thật: đường vào bằng điện thoại, và hành trình của người thử, tức công cụ đo các chỉ số chính.

### Findings
- **[medium]** Đường vào bằng điện thoại không có UJ nào, và lý do chọn bản đồ làm trang chủ chưa được nêu (§4.5, §5 "Thiết bị", UJ-1, UJ-3) — Cả ba UJ đều diễn ra trên laptop. Addendum của brief (§6) lại cho rằng phần lớn người dùng ngoài trường sẽ bấm link Facebook trên điện thoại; trên đó trang chủ 3D thành danh sách và Cố vấn thành thẻ, nhưng chưa ai mô tả hành trình này. Đây cũng là kênh tuyển 40% người thử. Ngoài ra, không job nào ở §2.1 hỏi về thành phố, vậy mà bản đồ 3D vừa là trang chủ, vừa là rủi ro kỹ thuật lớn nhất. *Fix:* thêm một UJ (hoặc biến thể của UJ-1) cho đường Facebook → điện thoại → Soi tin hoặc danh sách thẻ. Nêu một câu vì sao trang chủ là bản đồ, hoặc cân nhắc đặt ô chọn vai trò/Cố vấn làm trang chủ trên điện thoại.
- **[medium]** Chế độ thử nghiệm không có UJ, và các ca biên chưa được xử lý (FR-41–45) — Hành trình của người thử chính là công cụ đo SM-1–3. Một UJ ngắn sẽ làm lộ ra các ca biên:
  - người thử không bao giờ bấm "Lưu" hay "Copy" và đóng tab (mẫu số, xem SM-1);
  - vai trò mục tiêu chưa có tình huống mẫu cho FR-44;
  - ai có `?mode=eval` cũng làm lại được nhiều phiên chỉ bằng cách xóa bộ nhớ trình duyệt, sinh ra người thử trùng.

  *Fix:* thêm UJ-4 "người thử ngoài trường" ngắn. Bổ sung cho FR-44 cách xử lý vai trò chưa có tình huống mẫu. Ghi cách lọc phiên trùng hoặc phiên chưa hoàn tất khi phân tích.

## Mechanical notes

- **ID continuity:** FR-1..FR-45, UJ-1..UJ-3, SM-1..SM-10, SM-C1..SM-C5 liên tục, không trùng. Các tham chiếu chéo đều trỏ đúng: §6.1 ← FR-2, §10 ← FR-38, FR-22 ← §3, FR-36 ← §5, FR-15/FR-16 ← FR-43.
- **Assumptions Index:** chiều đi – về khớp (1 `[GIẢ ĐỊNH]` ở SM-5 ↔ 1 mục ở §11). Mật độ thấp; xem mục 5.
- **Con trỏ ở §0 lệch:** §0 nói lựa chọn công nghệ và kế hoạch sprint "nằm ở `addendum.md` và ở addendum của product brief", nhưng `addendum.md` của PRD không chứa cả hai mà lại trỏ ngược sang addendum của brief.
- **Thuật ngữ trôi:**
  - tên nút link chia sẻ: "Copy link lộ trình" (UJ-3), "Copy link chia sẻ" (FR-43), "Link chia sẻ" (FR-15);
  - "Lưu kết quả" (UJ-1, FR-43) so với tiêu đề FR-16 "Tải kết quả";
  - "Fresher/Junior" (UJ-2, ví dụ ở FR-19) so với "Intern/Fresher/Junior" (§3);
  - FR-27 dùng "vai trò mục tiêu" cho vai trò của *tin*, trong khi §3 định nghĩa đó là vai trò *người dùng* chọn;
  - "danh sách chờ" và "nhóm vận hành" được dùng nhưng không có trong §3.
- **Ví dụ ở FR-39:** các khoảng mẫu câu trong ví dụ (> 50%, 30–50%, < 10%) bỏ trống khoảng 10–30%. Nên ghi đủ, vì kiểm thử ranh giới bám theo các khoảng này.
- **Một yêu cầu, ba nơi:** ngưỡng 15 giây được nhắc ở ba chỗ (NFR riêng của §4.3, §5, SM-4); nên giữ một nguồn và trỏ về đó.
- **Định dạng:** câu hỏi mở số 6 ở §10 dính liền tiêu đề "## 11", thiếu dòng trống.
- **Lệch so với brief về điện thoại:** brief ghi "trên điện thoại chỉ có Soi tin và danh sách khoảng trống kỹ năng", còn PRD thêm bản đồ dạng danh sách và không nói Insights hiển thị thế nào trên điện thoại.
- **Đủ mục:** có đủ các mục cần cho mức độ nghiêm túc này. Riêng mục "Giả thuyết" và "Giới hạn đã biết" nên được thêm (xem mục 3).
