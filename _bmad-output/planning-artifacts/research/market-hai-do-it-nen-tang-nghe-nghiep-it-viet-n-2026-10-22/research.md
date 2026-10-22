---
title: 'Nghiên cứu thị trường: Hải Đồ IT — nền tảng định hướng nghề nghiệp & tuyển dụng IT Việt Nam'
type: 'market'
topic: 'Hải Đồ IT — nền tảng định hướng nghề nghiệp & tuyển dụng IT Việt Nam'
decision: 'Có nên theo đuổi Hải Đồ IT thành sản phẩm thương mại, và tính năng lõi nào làm điểm vào thị trường'
source: 'native run (web fan-out, 13 trợ lý nghiên cứu, 3 vòng)'
status: complete
claims_verified: 21
claims_unverified: 7
claims_overturned: 1
preset: 'deep'
validation: 'high'
created: '2026-10-22'
updated: '2026-10-22'
---

# Nghiên cứu thị trường: Hải Đồ IT

**Quyết định mà nghiên cứu phục vụ:** Có nên theo đuổi Hải Đồ IT thành sản phẩm thương mại không, và tính năng lõi nào trong 11 màn prototype nên làm điểm vào thị trường.

**Phạm vi:** Thị trường ứng viên IT Việt Nam (junior/mid, người chuyển hướng, sinh viên sắp ra trường) · Đối thủ trong nước và quốc tế · Mức sẵn lòng chi trả · Pháp lý 2026. Mọi số liệu đều có nguồn `[n]` ở Phụ lục nguồn. Độ tin cậy ghi theo từng nhận định: **cao** (đã đối chiếu nguồn độc lập), **TB** (trung bình: một nguồn đáng tin), **thấp** (cũ, nguồn yếu hoặc có tranh chấp). Nhận định *chưa xác minh* được ghi rõ.

**Số liệu kiểm chứng:** 29 nhận định chính trong sổ (đếm theo số ref), trong đó 21 đã xác minh, 7 chưa xác minh, 1 bị lật lại (số liệu BHXH vòng 1). Dùng 13 trợ lý nghiên cứu qua 3 vòng, trong đó có 1 vòng red team.

## Tóm tắt điều hành

**Kết luận: NÊN theo đuổi Hải Đồ IT, nhưng KHÔNG làm cả 11 màn.** Nên thu hẹp thành *"định hướng và học kỹ năng IT trong thời AI, có dữ liệu chứng minh"*. Tính năng lõi là **cố vấn lộ trình 90 ngày có trích nguồn + mô phỏng Nếu–thì**, dành cho junior/fresher và người chuyển hướng. Nên thu tiền gắn với *kết quả* (qua trường, bootcamp, gói review dự án), không bán thuê bao "lời khuyên". Độ tin cậy tổng thể: **TB**.

**Ba phát hiện quyết định:**

1. **Nỗi đau có thật và đã được xác minh.**
   - 40,9% dân IT định nghỉ việc trong 12 tháng [6]; 54,5% đang chủ động tìm việc [7].
   - Tuyển người dưới 1 năm kinh nghiệm giảm 13%, nhóm này chiếm 45% số ca bị cắt giảm [13].
   - Tỷ lệ doanh nghiệp coi năng suất AI là lý do không tuyển thêm tăng từ 5,9% lên 20,2%, dự báo 34,3% năm 2026 [11].
   - **Nhưng nhóm đau nhất lại có thu nhập thấp nhất** (10–14 triệu/tháng [8]), và thị trường mới chỉ chứng minh được ứng viên trả các khoản nhỏ (TopCV: 10.000–500.000đ [27]).
2. **Khoảng trống phía ứng viên hẹp hơn dự kiến.**
   - TopCV đã có AI chấm mức độ phù hợp, máy tính lương và BHXH, tra cứu lương [27]. HRCV và X-Interview đã vào thị trường trong năm 2026 [38][39].
   - Phần còn trống là *trải nghiệm*: cố vấn có trích nguồn, mô phỏng Nếu–thì, tra lương theo phân vị. *Dữ liệu* thì đang nằm trong tay các nền tảng lớn.
   - Hướng né đối thủ bằng "hộ chiếu kỹ năng" (hồ sơ kỹ năng đã xác minh) cũng chưa có tiền lệ thành công: ở quốc tế, các mô hình này thất bại hoặc đang lỗ: Triplebyte dừng hoạt động [46], Findy vẫn lỗ khoảng 995 triệu yên [49].
3. **Pháp lý 2026 quyết định phạm vi MVP.**
   - Luật Việc làm 2025 coi cả *"cung cấp thông tin thị trường lao động"* và *"tư vấn, giới thiệu việc làm"* là dịch vụ việc làm cần giấy phép (ký quỹ 300 triệu) [56][75]. ITviec đã có giấy phép này [76].
   - Đánh giá công ty ẩn danh đã có tiền lệ bị chặn [41].
   - **Ghép việc, Chỉ số phản hồi nhà tuyển dụng và agent pháp lý thu phí phải hoãn lại.**

**Rủi ro lớn nhất:**
- Chưa có bằng chứng nào cho thấy dân IT Việt Nam trả phí *định kỳ* cho công cụ nghề nghiệp.
- Chưa có số liệu chi phí thu hút một người dùng (CAC).
- Chưa rõ việc cung cấp thông tin miễn phí có cần giấy phép hay không.

→ **Bước tiếp theo:** phỏng vấn khách hàng, thử giá bằng fake door (trang giới thiệu tính năng chưa có), và xin ý kiến luật sư (R8) **trước khi viết PRD**.

## 1. Quy mô và tăng trưởng thị trường

**Thị trường tiếp cận được nhỏ hơn nhiều so với con số "1,2–1,5 triệu lao động IT" hay được trích dẫn.** Có bốn con số đo bốn nhóm khác nhau:
- **Toàn ngành ICT:** 1,2 triệu [1] đến 1,5 triệu [2], gồm cả sản xuất phần cứng và điện tử.
- **Người làm phần mềm/IT có việc:** khoảng **480 nghìn (2022) đến 560 nghìn (2024)** [3]. Chỉ có một nguồn là TopDev, nên *chưa xác minh*. Các trang khác chỉ đăng lại số này [4], và con số ~500 nghìn của VCCI [17] có thể cũng lấy từ TopDev.
- **Tài khoản GitHub:** 1,5 triệu (Octoverse 2023) [5]. Đây là số tài khoản, không phải số người đang đi làm.
- **Người tốt nghiệp mới:** khoảng **50–60 nghìn người/năm** (Nhân Dân: 50 nghìn [1]; TopDev: 55–60 nghìn sinh viên nhập học [3]; độ tin cậy TB). Chỉ khoảng 30% đáp ứng được yêu cầu công việc [1].

**Quy mô nền kinh tế số:** khoảng 39 tỷ USD GMV năm 2025 (e-Conomy SEA, độ tin cậy cao) [29].

**Nhu cầu đổi việc rất cao, và điểm này đã được xác minh bằng hai nguồn độc lập.**
- ITviec 2024-25 (n=2.324): **40,9%** dân IT dự định nghỉ việc trong 12 tháng tới. Con số này đọc từ file PDF đầy đủ; blog chính thức của ITviec ghi tròn là "40%". Độ tin cậy TB–cao. Lý do chính là lương (34,2%), muốn đổi hướng nghề nghiệp (26,3%) và thiếu cơ hội phát triển (22,3%) [6].
- JobsGO: **54,5%** dân IT đang chủ động tìm việc trong năm 2025, so với 48,4% ở mọi ngành [7].

Hai khảo sát hỏi hai câu khác nhau, nên chỉ có thể dùng **khoảng 41–55%**, không gộp thành một con số. *Suy luận (không phải dữ kiện):* nếu áp tỷ lệ này cho 500–560 nghìn người, nhóm đang cân nhắc đổi việc mỗi năm khoảng 200–300 nghìn người, chưa kể người mới ra trường.

**Chiều hướng nhu cầu tuyển dụng: không sụp đổ mà dịch chuyển.**
- Trên riêng nền tảng ITviec, tin IT tăng 12% so với cùng kỳ (Q1/2025), tin AI/ML tăng 41%, lượt tìm "AI" tăng 89%, tin IT Q2/2025 tăng 7% [9][10]. Đây chỉ là dữ liệu của một nền tảng.
- JobOKO (581.660 tin, 10 tháng đầu 2025): toàn thị trường chỉ tăng 2,05% [12]. Con số "tin IT −16,92%" hay được trích lại *không có trên trang công bố gốc*, nên *chưa xác minh*.
- **Thị trường đang phân cực:** doanh nghiệp coi năng suất AI là lý do chính để không tăng nhân sự. Tỷ lệ này là 5,9% (2024), 20,2% (2025) và dự báo 34,3% (2026) [11]. Tỷ lệ doanh nghiệp không tăng hoặc giảm biên chế tăng từ 4,9% (2021) lên 31% (2026) [11].

**Phân bố địa lý rất lệch.** Trong số nhà tuyển dụng trả lời khảo sát ITviec, TP.HCM chiếm 76,7%, Hà Nội 21,4% và Đà Nẵng 1,9% (H1/2024) [6]. Chỉ có một nguồn, và nguồn này là sàn việc làm nên có thể thiên lệch. Các thành phố nhỏ có rất ít dữ liệu.

**Quy mô doanh thu thị trường tuyển dụng trực tuyến: không tìm được số liệu 2023–2026.** Con số duy nhất là khoảng 7.100 tỷ đồng phí dịch vụ giới thiệu việc làm, tính cả headhunt offline (Vietdata, khoảng 2020, độ tin cậy thấp) [69]. Không tìm được doanh thu của TopCV, ITviec hay Navigos. Với Navigos, chỉ biết doanh thu thuần 2024 giảm 2,68% (nguồn bị khoá, *chưa xác minh*) [70].

**Thị trường Nhật:** khoảng 6.000 kỹ sư Việt làm trực tiếp tại Nhật, hơn 300 doanh nghiệp Việt phục vụ thị trường Nhật [17]. Nguồn này không nêu phương pháp, độ tin cậy TB. TopCV xếp kỹ sư cầu nối (BrSE) là vị trí khó tuyển thứ 2 (9,92%) [14].

## 2. Phân khúc khách hàng và hành vi

**Ba phân khúc rút ra từ bằng chứng:**

| Phân khúc | Quy mô / tín hiệu | Thu nhập (khả năng chi trả) | Ghi chú |
|---|---|---|---|
| **Sinh viên / fresher (<1 năm)** | ~50–60 nghìn người/năm [1][3]. Tuyển người dưới 1 năm kinh nghiệm giảm 13%; nhóm này chiếm 45% số ca bị cắt giảm [13] | Lương trung vị ~10–14 triệu/tháng (back-end 12,4; full-stack 10,1) [8] | Tìm thực tập qua Facebook 47,5%, người quen 37,5%, chương trình của trường 30% [6] |
| **Junior/mid muốn chuyển hướng** (ví dụ PHP → Data/AI) | 26,3% muốn nghỉ để đổi hướng [6]. Tìm kiếm "AI" +89% [9] | 1–2 năm: back-end 25,35 triệu; Data Engineer trung vị 41,3 triệu [8] | Hơn 70% muốn có môi trường cởi mở, sáng tạo và lộ trình rõ ràng, nhưng chỉ khoảng 1/3 thấy công ty hiện tại đáp ứng được [7] (*chưa xác minh*, một nguồn) |
| **Mid/senior đổi việc hoặc nhắm Nhật/remote** | ~41–55% có ý định đổi việc [6][7] | Lương cao hơn | Coi trọng review của nhân viên (70%) và phúc lợi (57%) khi chọn việc [6] |

**Kênh tìm việc:** trang tuyển dụng chiếm 55,9%, LinkedIn 16,4%, người quen giới thiệu 10,3% (ITviec 2023-24). Đây là dữ liệu do chính một sàn việc làm công bố [6]. LinkedIn ở Việt Nam có khoảng 10 triệu tài khoản (12/2025, đếm theo tập quảng cáo, không phải số người dùng hoạt động) [68].

**Yếu tố khi chọn việc (JobsGO):** cơ hội phát triển 72,7%, văn hoá công ty 69,7%, lương thưởng 67,7% [7].

**Hành vi dùng AI:** 81% người Việt được khảo sát tương tác với công cụ AI hằng ngày [29]. 93,49% dân IT-phần mềm dùng AI trong công việc. TopCV tự công bố con số này và không nêu phương pháp, độ tin cậy thấp [16]. Lập trình viên Việt Nam thận trọng với AI: 86% luôn hoặc thường xuyên kiểm tra lại kết quả AI đưa ra (nghiên cứu Agoda, độ tin cậy TB) [66].

## 3. Nỗi đau và nhu cầu chưa được đáp ứng

Xếp hạng theo độ mạnh của bằng chứng, đối chiếu với các màn hình trong prototype:

| Nỗi đau | Bằng chứng | Độ mạnh | Màn prototype tương ứng |
|---|---|---|---|
| **Junior/fresher mất phương hướng trước AI** | Tuyển người dưới 1 năm kinh nghiệm giảm 13%, nhóm này chiếm 45% số ca bị cắt giảm [13]. 34,3% doanh nghiệp dự kiến dùng AI thay vì tuyển thêm [11]. Câu chuyện thật: một bạn trẻ phỏng vấn 10 lần trong 6 tháng và được trả lời "cắt tuyển junior vì AI giúp senior làm nhanh hơn" [14]. Xu hướng kéo dài từ 2023 đến 2026 [14]. | **Mạnh** (≥2 nguồn độc lập) | Cố vấn đa agent, Mô phỏng Nếu–thì, Hạn dùng kỹ năng |
| **Muốn đổi việc/đổi hướng nhưng thiếu lộ trình** | 40,9% và 54,5% [6][7]. Hơn 70% muốn có lộ trình rõ ràng (gộp chung với môi trường làm việc), chỉ ~1/3 thấy công ty đáp ứng [7] | **Mạnh** về ý định; *chưa xác minh* về "thiếu lộ trình" | Lộ trình 90 ngày, Lộ trình thật |
| **Đóng BHXH theo mức lương thấp hơn thu nhập thực** | 43,1% người lao động được đóng BHXH theo mức lương cố định, thấp hơn thu nhập thực; 10,7% đóng theo lương tối thiểu vùng; 38,3% đóng trên toàn bộ lương gross (Navigos Talent Guide 2026, 250+ doanh nghiệp, 1.600+ người lao động) [18]. Vấn đề có thật và đã có chế tài: Nghị định 274/2025 phạt chậm đóng 0,03%/ngày [20] | **TB**: chỉ có một nguồn (Navigos, thuộc nhóm VietnamWorks), không có số liệu riêng cho IT | So sánh offer (kiểm tra mức đóng BHXH) |
| **Bị nhà tuyển dụng "ghost"** | 58% ứng viên Việt Nam từng bị ghost sau phỏng vấn (CareerLink, không nêu phương pháp) [21]. Ở quốc tế, Greenhouse ghi nhận 61% và con số này tăng 9 điểm phần trăm kể từ 2021 [22] | **TB–yếu** (*chưa xác minh* tại Việt Nam) | Chỉ số phản hồi nhà tuyển dụng |
| **Lương không minh bạch** | ~54% tin tuyển HR ghi "thương lượng" (mẫu nhỏ 50 tin, không phải IT) [25] | **Yếu** | Lương thời gian thực |
| **Tin tuyển dụng lừa đảo** | Tỷ lệ nạn nhân lừa đảo trực tuyến giảm từ 0,45% xuống 0,18% (2024 → 2025). Lừa đảo việc làm *không* nằm trong top 5 loại lừa đảo [23]. Nạn nhân chủ yếu là lao động phổ thông. Có một vụ lừa đảo diễn ra qua TopCV, và TopCV đã có 5 lớp xác minh nhà tuyển dụng [24] | **Yếu hơn dự kiến** | Soi tin tuyển dụng |
| **Điều khoản hợp đồng bất lợi** | Thoả thuận không cạnh tranh không bị cấm, nhưng toà xử không thống nhất (2010 công nhận, 2019 bác) [26]. Không tìm thấy nhiều phàn nàn từ dân IT | **Yếu** | Bộ công cụ nhảy việc (agent pháp lý) |

**Lưu ý về cách đọc:** "Nỗi đau mạnh" chỉ cho thấy vấn đề có thật. Điều này *không* chứng minh người dùng sẵn sàng trả tiền cho một cố vấn AI (xem mục 5 và 7). Con số hay được trích "60% lao động IT bị sa thải chưa có việc sau 1 năm" không được dùng, vì không nêu phương pháp và thuộc nhóm bị sa thải năm 2023 [15].

## 4. Bức tranh cạnh tranh

Đối thủ trong nước nắm dữ liệu và đã bắt đầu làm tính năng cho ứng viên; bài học quốc tế cho thấy tiền nằm ở dịch vụ gắn với kết quả, không nằm ở dữ liệu hay hồ sơ.

### 4a. Trong nước: các nền tảng lớn thu tiền từ nhà tuyển dụng, nhưng đã bắt đầu lấn sang phía ứng viên

- **TopCV**: khoảng 9–10 triệu hồ sơ. Đây là số tự công bố và không thống nhất: bản tiếng Anh ghi 10 triệu+, bản tiếng Việt ghi 9,5 triệu+ [16].
  - App iOS **đã có**: AI đánh giá mức độ phù hợp và khả năng cạnh tranh của ứng viên với từng việc, máy tính lương gross/net, thuế TNCN và BHXH, trắc nghiệm MBTI/MI, CV builder [27].
  - Có **thu tiền ứng viên**: Pro 50.000đ, Premium 500.000đ, các dịch vụ lẻ 10.000đ (xem số người đã ứng tuyển, tải CV không logo) [27]. Độ tin cậy cao. Ứng dụng có 36 nghìn lượt đánh giá, điểm 4,8.
  - Có trang tra cứu lương theo vị trí. Nguồn chỉ là đoạn trích tìm kiếm, độ tin cậy thấp [27].
  - Không tìm thấy doanh thu.
- **ITviec**: báo cáo lương IT hằng năm (n=1.839, 2025-26), chỉ có trung vị tĩnh; muốn tải file PDF đầy đủ phải để lại thông tin liên hệ. Không có công cụ tra lương phân vị tương tác [8]. AI chủ yếu phục vụ nhà tuyển dụng ("AI Match", "Talent Finder") [33][34]. Có review công ty được kiểm duyệt [34]. Quy chế hoạt động không có dịch vụ trả phí nào cho ứng viên [33].
- **VietnamWorks**: AI cho nhà tuyển dụng (AI Application Screening, Job Post AI ra mắt 4/2026) [35].
- **TopDev**: CV builder, máy tính gross-net, trắc nghiệm tính cách. Không có AI cho ứng viên [36].
- **Công cụ AI chấm CV đã thành hàng miễn phí**: Cake, VietnamWorks, JobsGO đều có [37].
- **Đối thủ mới:**
  - **HRCV** ra mắt 6/2026: AI phân tích CV và ghép việc, máy tính gross-net, tham khảo lương, tính năng luyện phỏng vấn đang phát triển. Khoảng 3.400 người dùng (8/2026). Chỉ một nguồn [38].
  - **X-Interview**: luyện phỏng vấn bằng AI từ JD. Chưa rõ quy mô người dùng [39].
- **Đánh giá công ty ẩn danh**: reviewcongty bị Bộ TT&TT chặn vào 6/2023 sau kiến nghị của hiệp hội ngành, nhưng sau đó vẫn hoạt động trên các tên miền nhân bản [40][41].

**Phần chưa có ai làm** (trong phạm vi đã tìm, chưa chứng minh là không tồn tại):
- tra lương theo phân vị (P25/P75) có ngưỡng mẫu,
- cố vấn hội thoại đa agent có trích nguồn ("Vì sao?"),
- mô phỏng "nếu học thêm kỹ năng X thì sao",
- quét dấu hiệu tin treo hoặc tin ảo,
- soát điều khoản hợp đồng.

**Rủi ro bị bắt chước rất cao**, vì các nền tảng lớn nắm dữ liệu tin tuyển dụng và đã có năng lực AI [27][34].

### 4b. Quốc tế: bài học về mô hình kinh doanh

| Tham chiếu | Ứng với tính năng | Bài học |
|---|---|---|
| **LinkedIn Premium**: doanh thu hơn 2 tỷ USD trong 12 tháng [42] | Cố vấn, gói trả phí cho ứng viên | Ứng viên có trả tiền, nhưng trên nền một hiệu ứng mạng lưới khổng lồ |
| **Levels.fyi**: dữ liệu lương do cộng đồng góp; dịch vụ thương lượng **1.250–5.000 USD**, cam kết tăng lương, không đạt thì hoàn tiền [44]. Thương lượng từng là nguồn thu lớn nhất [45] | Lương, so sánh offer, tập thương lượng | Dữ liệu lương kéo người dùng vào; tiền đến từ **dịch vụ gắn với kết quả** |
| **Findy (Nhật)**: chấm điểm kỹ năng từ GitHub, miễn phí cho ứng viên, nhà tuyển dụng trả tiền. Gọi vốn Series D 2,05 tỷ yên (5/2025) [48]. Nhưng **vẫn lỗ ròng khoảng 995 triệu yên năm tài chính 2025** (khoản lỗ tăng liên tục đến 2024, khoảng 1,06 tỷ yên, rồi thu hẹp lại năm 2025) [49] | Hộ chiếu kỹ năng | Mô hình chưa chứng minh có lãi, kể cả ở Nhật |
| **LAPRAS (Nhật)**: khoảng 40 nghìn người dùng sau khoảng 7 năm [50] | Hộ chiếu kỹ năng | Tăng trưởng chậm |
| **Triplebyte**: dừng hoạt động 31/3/2023; Karat chỉ mua công nghệ đánh giá, không mua kho hồ sơ ứng viên [46] | Hộ chiếu kỹ năng đã xác minh | Nhà tuyển dụng trả tiền cho *bài đánh giá*, không phải cho hồ sơ ứng viên |
| **Hired**: gọi khoảng 130 triệu USD, bị bán khi đang chịu áp lực trả nợ, sau đó sáp nhập vào LHH năm 2024 [47] | Sàn ghép việc | Sàn hai phía rất mong manh khi thị trường tuyển dụng đi xuống |
| **Glassdoor**: bị nhập vào Indeed, cắt giảm nhân sự 3 năm liền [51] | Chỉ số nhà tuyển dụng | Review chỉ là một tính năng, không thành một doanh nghiệp độc lập |
| **Google Career Dreamer**: miễn phí, dùng dữ liệu Lightcast, hiện chỉ có ở Mỹ [52] | Lộ trình nghề, cố vấn | Ông lớn đang biến mảng khám phá lộ trình thành hàng miễn phí |
| **Final Round AI / Teal**: lần lượt gọi vốn 6,9 triệu và 19 triệu USD, giá khoảng 25–29 USD/tháng, không công bố doanh thu định kỳ (ARR) [43] | Luyện phỏng vấn, công cụ AI cho ứng viên | Gọi được vốn nhưng chưa chứng minh được doanh thu |
| **roadmap.sh**: gói Pro 8,33 USD/tháng có gia sư AI [55] | Lộ trình | Freemium giá thấp |
| **Tiện ích phát hiện tin tuyển dụng ảo**: tiện ích GhostJob có 23 người dùng/tháng, doanh thu 0 USD [54] | Soi tin | Không ai trả tiền cho tính năng này. Chỉ nên dùng làm tính năng miễn phí để kéo người dùng |
| **Glints (Đông Nam Á)**: gọi 50 triệu USD rồi cắt giảm 18% nhân sự [53] | Toàn nền tảng | Nền tảng nghề nghiệp gọi vốn mạo hiểm ở khu vực này dễ tổn thương |

**Chưa thấy ai kết hợp "dữ liệu thị trường lao động + cố vấn AI đa agent" trong một sản phẩm** [52][48]. Đây là một khoảng trống, không phải bằng chứng là có nhu cầu.

## 5. Kênh tiếp cận, định giá và mức sẵn lòng chi trả

**Mô hình doanh thu trong nước:** các nền tảng đều bán gói đăng tin, thương hiệu tuyển dụng và truy cập kho CV cho nhà tuyển dụng, giá theo báo giá riêng, không công khai [33].

**Mức giá tham chiếu cho người dùng Việt Nam:**

| Sản phẩm | Giá | Người trả | Nguồn |
|---|---|---|---|
| TopCV Pro / Premium / dịch vụ lẻ | 50.000đ / 500.000đ / 10.000đ (chưa rõ thời hạn) | Ứng viên | [27] |
| ELSA Speak | 145.000đ/tháng; 769.000–1.590.000đ/năm | Người học | [28] (một nguồn) |
| ChatGPT Go / Plus | ~132.000đ / ~522.000đ/tháng | Người dùng | [63] (nguồn mâu thuẫn về cách tính tiền) |
| Levels.fyi (Mỹ) | 1.250–5.000 USD/lần | Ứng viên, có cam kết kết quả | [44] |

**Đối chiếu với thu nhập:** junior dưới 1 năm kinh nghiệm có trung vị khoảng 10–14 triệu/tháng [8]. Thu nhập bình quân của người lao động nói chung là khoảng 8,3 triệu/tháng [64]. *Suy luận:* gói 50.000–150.000đ/tháng tương đương khoảng 0,4–1,5% lương junior, là mức chấp nhận được. Nhưng chưa có bằng chứng ứng viên IT sẽ trả phí *định kỳ* cho công cụ nghề nghiệp.

**Tín hiệu cho thấy người Việt có trả tiền cho mảng "học có kết quả":**
- Edupia có khoảng 400 nghìn học sinh trả phí trên 5 triệu người dùng. Số liệu năm 2022, đã cũ [31].
- Coursera Việt Nam có 1,8 triệu người học (+22%) và 152 nghìn lượt đăng ký khoá GenAI (+400%) (7/2025, hai nguồn) [30].
- Các bootcamp dùng mô hình "học trước, trả sau" và cam kết việc làm (MindX, CodeGym). Thông tin từ nguồn quảng cáo, độ tin cậy thấp [73].

**Kênh tiếp cận:**
- Sinh viên tiếp cận được qua Facebook và chương trình của trường (xem bảng ở mục 2) [6].
- Kênh YouTube F8 có khoảng 143 nghìn người đăng ký. Đây là ước tính của bên thứ ba [71].
- **Không tìm được số liệu chi phí thu hút một người dùng (CAC) hay chi phí mỗi lượt cài app (CPI) cho Việt Nam.** AppsFlyer chỉ ghi nhận thị trường đã chuyển từ chạy theo lượt cài sang chú trọng chất lượng người dùng [72].

## 6. Pháp lý: ràng buộc thiết kế (luật có hiệu lực 2026)

Luật Việc làm 2025 là ràng buộc quyết định phạm vi sản phẩm; các luật còn lại chủ yếu định hình kiến trúc dữ liệu.

### 6.1 Luật Việc làm 2025: điểm nghẽn lớn nhất

**Điều 27(1) Luật Việc làm 74/2025/QH15** (hiệu lực 01/01/2026) định nghĩa dịch vụ việc làm như sau: *"Dịch vụ việc làm bao gồm tư vấn, giới thiệu việc làm; cung ứng và giới thiệu lao động cho người sử dụng lao động; **thu thập, phân tích, lưu trữ, cung cấp thông tin về thị trường lao động**"* [56][74]. Điều 20(1) nêu rõ thông tin thị trường lao động bao gồm cả **tiền lương và thu nhập** [56].

Điều 27(4) quy định: chỉ doanh nghiệp đã có giấy phép mới được cung cấp dịch vụ việc làm theo phương thức thương mại điện tử [56]. Độ tin cậy cao.

**Điều kiện giấy phép** (Nghị định 352/2025, hiệu lực 01/01/2026) [75], độ tin cậy cao:
- ký quỹ **300 triệu đồng**;
- trụ sở còn thời hạn sử dụng ít nhất 24 tháng;
- người đại diện có bằng đại học hoặc 2 năm kinh nghiệm;
- do UBND cấp tỉnh cấp, thời hạn tối đa 60 tháng;
- doanh nghiệp cung cấp dịch vụ qua thương mại điện tử phải đồng bộ dữ liệu với Sàn giao dịch việc làm quốc gia.

**Đối thủ:** ITviec có Giấy phép hoạt động dịch vụ việc làm số 19710/2023/39/SLĐTBXH-VLATLĐ [76]. Chân trang của VietnamWorks chỉ có đăng ký kinh doanh [76]. Chưa kiểm tra được TopCV.

**Chế tài theo chế độ cũ:** Nghị định 12/2022 phạt **45–60 triệu đồng** nếu hoạt động dịch vụ việc làm không phép, *không phụ thuộc vào việc có thu phí hay không* [77]. Chưa tìm được nghị định xử phạt mới thay thế, nên mục này *chưa xác minh*.

**Hệ quả:** không tìm thấy điều khoản nào miễn giấy phép cho dịch vụ "miễn phí" hoặc "chỉ cung cấp thông tin". Theo câu chữ của luật, ngay cả bản đồ nhu cầu tuyển dụng và tra lương cũng nằm trong định nghĩa dịch vụ việc làm. Mức độ rủi ro trên thực tế chưa rõ. Đây là **câu hỏi cần xin ý kiến luật sư hoặc Sở Nội vụ trước khi ra mắt**.

### 6.2 Dữ liệu cá nhân, AI, mạng xã hội, tư vấn pháp lý

- **Luật Bảo vệ dữ liệu cá nhân 91/2025 và Nghị định 356/2025** (hiệu lực 01/01/2026) [57][58]:
  - Danh mục dữ liệu nhạy cảm *không* gồm lương, thu nhập hay lịch sử việc làm. Danh mục *có* gồm ảnh CCCD, dữ liệu thẻ và giao dịch ngân hàng, và **dữ liệu theo dõi hành vi trên mạng xã hội hoặc dịch vụ trực tuyến** [58]. Độ tin cậy cao.
  - **Điều 38:** trong 5 năm, doanh nghiệp nhỏ và doanh nghiệp khởi nghiệp được tự chọn có lập hồ sơ đánh giá tác động và hồ sơ chuyển dữ liệu ra nước ngoài hay không. Ưu đãi này **mất** nếu doanh nghiệp xử lý dữ liệu nhạy cảm hoặc dữ liệu của "số lượng lớn" chủ thể [57]. Chưa tìm được ngưỡng "số lượng lớn" là bao nhiêu.
  - **Mức phạt:** mua bán dữ liệu cá nhân bị phạt gấp 10 lần khoản thu trái phép hoặc 3 tỷ đồng, tùy mức nào cao hơn; vi phạm về chuyển dữ liệu xuyên biên giới bị phạt tới 5% doanh thu [59]. Nguồn là bài phân tích của một hãng luật, độ tin cậy TB–cao.
  - **Gửi CV hoặc hợp đồng cho API LLM ở nước ngoài** là chuyển dữ liệu xuyên biên giới [59].
- **Luật AI 134/2025** (hiệu lực 01/3/2026) [61]. Theo **Quyết định 33/2026/QĐ-TTg**, danh mục AI rủi ro cao gồm 6 lĩnh vực: giáo dục, dân tộc–tôn giáo, y tế, ngân hàng, tố tụng, giao thông. Danh mục **không có tuyển dụng hay nhân sự** [60]. Độ tin cậy cao. Tuy vậy, AI dùng cho mục đích *giáo dục* thuộc nhóm rủi ro cao, nên cần lưu ý nếu định vị sản phẩm là "lộ trình học".
- **Mạng xã hội / đánh giá ẩn danh:**
  - Nghị định 147/2024 yêu cầu xác thực tài khoản bằng số điện thoại Việt Nam và gỡ nội dung vi phạm trong 24 giờ kể từ khi cơ quan chức năng yêu cầu [62]. Mới có tổng hợp từ báo chí, chưa đọc điều khoản gốc, độ tin cậy TB.
  - reviewcongty đã bị chặn vào năm 2023 [40][41].
- **Tư vấn pháp luật:** Luật Luật sư (Điều 32) chỉ cho phép hành nghề luật sư qua văn phòng hoặc công ty luật [67]. Độ tin cậy thấp–TB. Nghị định 77/2008 về tư vấn pháp luật vẫn còn hiệu lực một phần [78]. Không tìm thấy quy định nào riêng cho AI.

### 6.3 Mức rủi ro theo từng màn prototype

| Màn / hoạt động | Mức rủi ro | Cách giảm rủi ro |
|---|---|---|
| Ghép việc ("Ghép việc lại" trong Hộ chiếu kỹ năng), tin "vừa mở khoá", gợi ý tin tuyển | **Cao**: dịch vụ việc làm, cần giấy phép [56][75] | Hoãn lại; hoặc chỉ dẫn link sang sàn gốc; hoặc hợp tác với doanh nghiệp đã có phép; hoặc xin phép (ký quỹ 300 triệu) |
| Bản đồ nhu cầu, Lương thời gian thực | **TB–cao**: thuộc nhóm "thông tin thị trường lao động" theo câu chữ của luật [56] | Trình bày như báo cáo hoặc nghiên cứu tổng hợp; xin ý kiến pháp lý |
| Chỉ số phản hồi nhà tuyển dụng (đóng góp ẩn danh) | **Cao** [40][41][62] | Chỉ công bố số liệu tổng hợp; xác thực bằng số điện thoại; kiểm duyệt; gỡ trong 24 giờ; không nêu tên cá nhân |
| Agent pháp lý đọc hợp đồng | **Cao** nếu thu phí và gọi là "tư vấn" [67][78] | Định vị là "thông tin pháp lý / danh sách kiểm tra"; che ảnh CCCD và số tài khoản ngân hàng; giới thiệu sang luật sư |
| Hộ chiếu kỹ năng (review repo), lưu CV | **TB** [57][58] | Xin đồng ý rõ ràng; thu tối thiểu dữ liệu; ẩn danh trước khi gọi LLM |
| Lộ trình thật (hồ sơ ẩn danh) | **TB**: dễ bị nhận diện lại ở công ty nhỏ (suy luận) | Ngưỡng k-ẩn danh (prototype đang đặt n ≥ 20) |
| So sánh offer, máy tính net, tập thương lượng | **Thấp** [60] | Kèm miễn trừ trách nhiệm; không khai thuế thay người dùng |

## 7. Kết luận rút ra khi ghép các mảng lại

1. **Nỗi đau mạnh nằm ở đúng chỗ khó thu tiền.**
   - Nỗi đau mạnh nhất là junior và người chuyển hướng mất phương hướng trước AI [11][13][14]. Nhóm này lại có thu nhập thấp nhất (10–14 triệu) [8], và thị trường chỉ chứng minh được các khoản thu nhỏ từ ứng viên [27].
   - Ngược lại, thứ người dùng đã chứng minh sẵn lòng trả là **kết quả**:
     - Levels.fyi bán dịch vụ thương lượng có cam kết tăng lương [44].
     - Edupia và ELSA bán sản phẩm học có kết quả [31][28].
     - Bootcamp theo mô hình "học trước, trả sau" [73].
   - **Hệ quả:** sản phẩm nên thu tiền gắn với *kết quả* (lên kỹ năng, lên lương), không bán "lời khuyên".
2. **Lợi thế cạnh tranh thật nằm ở dữ liệu, và Hải Đồ IT chưa có dữ liệu.**
   - Mọi màn hình trong prototype đều phụ thuộc "[NGUỒN DỮ LIỆU TUYỂN DỤNG]".
   - Đối thủ lớn đang nắm dữ liệu: TopCV có khoảng 9–10 triệu hồ sơ [16], ITviec có khảo sát lương hằng năm [8].
   - Ngay cả ITviec cũng chỉ thu được khoảng 1,8–2,3 nghìn phản hồi khảo sát lương mỗi năm [8][6]. Con số này quá mỏng để chia phân vị theo vai trò × cấp bậc × thành phố, nhất là ở các thành phố nhỏ khi TP.HCM chiếm 76,7% nhu cầu tuyển IT theo khảo sát nhà tuyển dụng [6].
   - Crawl dữ liệu từ sàn khác có rủi ro về quyền tác giả đối với cơ sở dữ liệu và vi phạm điều khoản sử dụng. Dữ liệu do cộng đồng đóng góp thì vướng tiền lệ reviewcongty và Nghị định 147.
3. **Pháp lý đẩy sản phẩm về phía "giáo dục kỹ năng".**
   - Ghép việc và cung cấp thông tin thị trường lao động thuộc diện cần giấy phép [56][75].
   - Tuyển dụng không bị xếp vào AI rủi ro cao, nhưng giáo dục thì có [60].
   - Đánh giá ẩn danh có tiền lệ bị chặn [41].
   - Một sản phẩm định vị là **"định hướng và học kỹ năng IT"** sẽ né được rủi ro dịch vụ việc làm, đổi lại phải chịu nghĩa vụ của AI rủi ro cao trong giáo dục từ 9/2027 [60]. Còn định vị là "tuyển dụng" thì cần giấy phép. Đây là một lựa chọn chiến lược thực sự, không có phương án tối ưu sẵn.
4. **Khoảng trống còn lại là trải nghiệm** (cố vấn có trích nguồn, mô phỏng Nếu–thì, tra lương theo phân vị), **không phải dữ liệu, nên dễ bị sao chép** [27][38][39].

## 8. Bằng chứng ngược (red team)

Một trợ lý red team đã tìm bằng chứng phản bác cho 5 kết luận lớn. Không kết luận nào bị lật hoàn toàn, nhưng cả 5 đều **yếu đi**:

- **"Phía ứng viên còn trống" → yếu đi.** Ngoài bằng chứng ở mục 4a, ITviec và TopDev đã ra báo cáo lương nhiều năm trước [8].
- **"Ứng viên không trả tiền" → yếu đi một phần.**
  - Người Việt có trả tiền cho mảng học: Edupia có khoảng 400 nghìn học sinh trả phí [31], TopCV thu được các khoản nhỏ [27].
  - Cách nói đứng vững hơn: *ứng viên trả khoản nhỏ cho thứ gắn với kết quả gần; doanh thu thuê bao định kỳ chưa được chứng minh*.
- **"Cố vấn AI giải quyết nỗi đau junior" → yếu đi.**
  - ChatGPT và Gemini miễn phí đã là phương án thay thế. 47% Gen Z (khảo sát ở Mỹ) cho rằng ChatGPT tư vấn nghề tốt hơn sếp của họ (đoạn trích, độ tin cậy thấp) [79].
  - Lập trình viên Việt Nam hay tự kiểm tra lại kết quả AI [66].
  - Ứng dụng tự hướng dẫn trong lĩnh vực lân cận chỉ giữ chân người dùng trung vị 2,5–3,5 tuần [65].
  - Thị trường tuyển dụng vẫn tăng [9], nên nỗi đau có thể là "chọn hướng nào", không phải "không có việc".
- **"Hộ chiếu kỹ năng do nhà tuyển dụng trả" → yếu đi.** Triplebyte đã thất bại [46]. Findy vẫn lỗ khoảng 1 tỷ yên mỗi năm [49]. LAPRAS tăng trưởng chậm [50].
- **"Dữ liệu cộng đồng sẽ đủ dày" → yếu đi, và gần như bị lật đối với đánh giá nhà tuyển dụng.** Đã có tiền lệ bị chặn [41]. Mẫu khảo sát của đơn vị dẫn đầu chỉ khoảng 2 nghìn phản hồi mỗi năm [8].

**Có một điểm phải sửa trong quá trình nghiên cứu:** vòng 1 ghi "chỉ 0,12% được đóng BHXH trên toàn bộ thu nhập". Con số này là **đọc nhầm**. Nguồn Navigos (VCCI đăng lại) ghi **38,3% đóng trên toàn bộ lương gross** [18]. Báo cáo dùng số đã sửa.

## 9. Khuyến nghị

**Quyết định: NÊN theo đuổi, nhưng phải thu hẹp mạnh. Không làm cả 11 màn.** Độ tin cậy TB. Hải Đồ IT nên định vị là *"định hướng và học kỹ năng IT trong thời AI, có dữ liệu chứng minh"*, không phải một nền tảng tuyển dụng.

| # | Khuyến nghị | Màn prototype | Căn cứ | Độ tin cậy | Dùng cho |
|---|---|---|---|---|---|
| R1 | **Tính năng lõi để vào thị trường:** Cố vấn lộ trình 90 ngày (có "Vì sao?" trích nguồn) + Mô phỏng Nếu–thì + xu hướng kỹ năng. Đối tượng là junior/fresher và người chuyển hướng (ví dụ PHP → Data/AI) | Cố vấn đa agent, Mô phỏng Nếu–thì, Hạn dùng kỹ năng | Nỗi đau mạnh [11][13][14]; khoảng trống trải nghiệm [27][34]; nhu cầu học AI tăng mạnh [30][9] | TB. Dễ bị sao chép, và còn bị ChatGPT thay thế [79] | Brief: vấn đề, người dùng. PRD: persona chính |
| R2 | **Thu tiền gắn với kết quả, không bán thuê bao "lời khuyên"**: hợp tác với trường và bootcamp (B2B2C), hoa hồng giới thiệu khoá học, gói "lộ trình + review dự án" theo đợt. Thử giá ở mức 50.000–150.000đ | Hộ chiếu kỹ năng (phần review dự án) | Giá tham chiếu [27][28]; Edupia [31]; Levels.fyi [44]; Coursera VN [30]; sinh viên tìm việc qua trường [6] | Thấp–TB: *chưa có bằng chứng về mức sẵn lòng trả của dân IT* | Định giá / chiến lược ra thị trường |
| R3 | **Tính năng miễn phí để kéo người dùng:** So sánh offer theo thực nhận, có kiểm tra mức đóng BHXH, và Soi tin (cảnh báo tin treo) | So sánh offer; Soi tin tuyển dụng | 43,1% đóng BHXH thấp hơn thu nhập thực [18]; không ai trả tiền cho tính năng phát hiện tin ảo [54]; máy tính gross-net đã phổ biến [27] | TB | PRD: tính năng thu hút người dùng |
| R4 | **Hoãn lại** cho đến khi có giấy phép hoặc ý kiến pháp lý: ghép việc, tin "vừa mở khoá", Chỉ số phản hồi nhà tuyển dụng, agent pháp lý thu phí | Ghép việc lại; Chỉ số phản hồi; Bộ công cụ nhảy việc (phần hợp đồng) | [56][75][41][62][67] | Cao | PRD: ngoài phạm vi; ràng buộc kiến trúc |
| R5 | **Giải bài toán dữ liệu trước khi viết code**: chọn một trong ba hướng: đối tác dữ liệu (sàn tuyển dụng, trường), dữ liệu công khai đã tổng hợp, hoặc đóng góp theo kiểu "góp lương để xem lương". Bản đồ thành phố chỉ hiển thị nơi có đủ mẫu | Bản đồ nhu cầu; Lương thời gian thực; Lộ trình thật | Phân bố lệch về TP.HCM [6]; mẫu mỏng [8]; dữ liệu bị đối thủ nắm [16][27]; crawl dữ liệu chưa có án lệ | Cao | Kiến trúc: nguồn dữ liệu |
| R6 | **Thiết kế tuân thủ ngay từ đầu:** ẩn danh trước khi gọi LLM, che CCCD và số tài khoản trong hợp đồng, không theo dõi hành vi người dùng, để giữ ưu đãi 5 năm theo Điều 38 | Tất cả | [57][58][59] | Cao | Ràng buộc kiến trúc |
| R7 | **Ưu tiên thấp:** Remote/Nhật + BrSE (chỉ làm dạng nội dung), Lộ trình thật (cần lượng dữ liệu lớn), Hộ chiếu kỹ năng thu phí nhà tuyển dụng | Remote & Nhật; Lộ trình thật; Hộ chiếu | Khoảng 6.000 kỹ sư Việt ở Nhật [17]; Findy và Triplebyte [49][46] | TB | Lộ trình sản phẩm (roadmap) |
| R8 | **Kiểm chứng trước khi làm PRD:** phỏng vấn 15–20 junior/fresher và 3–5 trường hoặc bootcamp; thử "fake door" (trang giới thiệu tính năng chưa có) ở mức giá 50.000 và 150.000đ; xin ý kiến luật sư về Điều 27 | — | Các khoảng trống ở mục 10 | Cao (về sự cần thiết) | Bước tiếp theo |

## 10. Câu hỏi còn mở

1. **Ứng viên IT có trả thuê bao định kỳ không, và ở mức nào?** Không tìm được dữ liệu. *Cách trả lời:* thử fake door và phỏng vấn khách hàng (R8).
2. **Điều 27 có áp dụng cho thông tin miễn phí hay không?** Chưa tìm thấy điều khoản miễn trừ. *Cách trả lời:* xin ý kiến luật sư hoặc gửi văn bản hỏi Sở Nội vụ; đọc phần còn lại của Nghị định 352.
3. **CAC/CPI ở Việt Nam** cho ứng dụng giáo dục và nghề nghiệp. Báo cáo AppsFlyer và Adjust bị khoá [72]. *Cách trả lời:* tải các báo cáo đó, hoặc chạy thử quảng cáo nhỏ.
4. **Số lập trình viên đang đi làm ở thời điểm hiện tại**, cần hai nguồn độc lập. Hiện chỉ có TopDev [3]. *Cách trả lời:* đọc báo cáo TopDev 2025 hoặc Sách trắng CNTT-TT.
5. **Doanh thu TopCV, Navigos, ITviec.** *Cách trả lời:* báo cáo tài chính trên masothue/Vietstock; tài liệu nhà đầu tư của en-japan.
6. **Tỷ lệ ghosting và số tin treo tại Việt Nam:** mới có một nguồn từ nhà cung cấp [21].
7. **TopCV đã có giấy phép dịch vụ việc làm chưa; Pro/Premium có thời hạn bao lâu và gồm những gì** [27].
8. **"Hơn 70% muốn có lộ trình, chỉ 1/3 thấy công ty đáp ứng"**: cần nguồn thứ hai, và cần tách riêng câu hỏi về lộ trình [7].

## Phụ lục nguồn

Tất cả nguồn được truy cập ngày 2026-10-22. Độ tin cậy ghi cho phát hiện mà nguồn đó hỗ trợ. Số thứ tự 19 và 32 bị bỏ trống có chủ đích (nguồn đã loại); số thứ tự được giữ cố định để không làm lệch trích dẫn.

| # | Phát hiện hỗ trợ | Nhà xuất bản | Ngày đăng | Độ tin cậy |
|---|---|---|---|---|
| 1 | 1,2 triệu lao động ICT; ~50 nghìn tốt nghiệp/năm, 30% đáp ứng yêu cầu | [Nhân Dân (Bộ KH&CN)](https://nhandan.vn/nang-cao-nang-luc-thuc-tien-cho-nguon-nhan-luc-so-post870953.html) | 2025-05 | TB |
| 2 | 1,5 triệu (VINASA); thiếu 150–200 nghìn (tái chế số liệu TopDev) | [VnEconomy](https://vneconomy.vn/viet-nam-nguy-co-thieu-hut-150000-200000-nhan-luc-cong-nghe-ngay-trong-nam-2025.htm) | ~2025 | Thấp |
| 3 | ~480 nghìn (2022) → ~560 nghìn (2024) người làm IT; 55–60 nghìn sinh viên nhập học/năm | [TopDev](https://topdev.vn/vietnam-tech-talents-report-topdev-2024) | 2024-09 | TB–thấp (một nguồn) |
| 4 | Đăng lại số liệu TopDev (không độc lập) | [SecondTalent](https://www.secondtalent.com/resources/software-development-in-vietnam/) | ~2025 | Thấp |
| 5 | Hơn 1,5 triệu tài khoản GitHub Việt Nam (2023) | [GitHub Octoverse 2023](https://github.blog/news-insights/research/the-state-of-open-source-and-AI/) | 2023-11 | TB (đã cũ) |
| 6 | ITviec 2024-25 (n=2.324): 40,9% định nghỉ việc; kênh tìm việc; phân bố theo thành phố; kênh tìm thực tập; yếu tố chọn việc | [ITviec (báo cáo 2024-25)](https://itviec.com/report/vietnam-it-salary-and-recruitment-market-2024-2025) | 2024-12 | TB–cao (PDF bị khoá, blog ghi ~40%; thiên lệch vì là sàn) |
| 7 | 54,5% dân IT chủ động tìm việc; yếu tố chọn việc; >70% muốn có lộ trình | [PLO / Tuổi Trẻ (JobsGO)](https://tuoitre.vn/plo/xu-huong-tim-viec-nganh-it-nam-2025-rao-can-vo-hinh-giua-ung-vien-va-doanh-nghiep-post834396.html) | 2025-02 | TB–cao |
| 8 | ITviec 2025-26 (n=1.839): lương trung vị theo vai trò và số năm kinh nghiệm | [ITviec](https://itviec.com/bao-cao/luong-it-va-thi-truong-tuyen-dung-it-vietnam) | 2025-12 | TB |
| 9 | Q1/2025: tin IT +12%, AI/ML +41%, tìm kiếm "AI" +89% (riêng nền tảng ITviec) | [ITviec blog](https://itviec.com/blog/vietnam-it-recruitment-market-overview-q1-2025-ai-drives-changes/) | 2025-04 | Cao cho nền tảng / thấp cho toàn quốc |
| 10 | Q2/2025: tin IT +7% so với cùng kỳ | [ITviec blog](https://itviec.com/blog/?p=91452) | 2025-07 | TB |
| 11 | Tỷ lệ doanh nghiệp không tuyển thêm vì AI: 5,9% → 20,2% → 34,3%; 31% không tăng biên chế | [Doanh nhân / Báo Pháp luật VN](https://doanhnhan.baophapluat.vn/lan-song-ai-tai-dinh-hinh-nhan-su-nganh-it-doanh-nghiep-uu-tien-cong-nghe-thay-vi-mo-rong-quy-mo.html) | 2026-01 | TB–cao |
| 12 | JobOKO: 581.660 tin, toàn thị trường +2,05% | [JobOKO](https://vn.joboko.com/blog/ra-mat-bao-cao-luong-tuyen-dung-2026-nwi5698) | ~2025-11 | TB |
| 13 | Tuyển người dưới 1 năm kinh nghiệm −13%; nhóm này chiếm 45% số ca bị cắt giảm | [Tuoi Tre News (JobOKO)](https://news.tuoitre.vn/vietnam-job-market-cools-for-graduates-as-firms-favor-experienced-hires-report-103251227143729228.htm) | 2025-12 | TB–cao |
| 14 | Câu chuyện fresher và AI; TopCV: 53% thiếu kỹ năng cao; BrSE khó tuyển thứ 2 | [VnExpress International](https://e.vnexpress.net/news/tech/tech-news/it-industry-suffers-from-lack-of-high-level-talent-surfeit-of-entry-level-coders-5067869.html) | 2026-05 | Cao |
| 15 | "60% lao động IT bị sa thải chưa có việc sau 1 năm" (không nêu phương pháp) | [VnExpress](https://vnexpress.net/vo-mong-doi-doi-nho-nghe-it-5005786.html) | 2026-01 | Thấp |
| 16 | TopCV: 9,5–10 triệu+ hồ sơ (tự công bố, không thống nhất); 93,49% dân IT dùng AI | [TopCV Insights](https://insights.topcv.vn/recruitment-report-2025-2026-eng) | ~2025-12 | TB / thấp |
| 17 | Khoảng 6.000 kỹ sư Việt ở Nhật; hơn 300 doanh nghiệp phục vụ thị trường Nhật | [VCCI](https://www.vcci.com.vn/tin-tuc/doanh-nghiep-viet-nam-da-di-xa-hon-mo-hinh-gia-cong-truyen-thong) | 2025-08 | TB |
| 18 | Navigos Talent Guide 2026: 43,1% đóng BHXH trên mức thấp hơn thu nhập thực / 38,3% đóng trên toàn bộ gross | [VCCI](https://vcci.com.vn/tin-tuc/phan-lon-nguoi-lao-dong-dong-bao-hiem-xa-hoi-thap-hon-thu-nhap-thuc-te) | 2026-01 | TB (một nguồn) |
| 20 | Nghị định 274/2025: phạt chậm đóng hoặc trốn đóng BHXH | [LuatVietnam](https://luatvietnam.vn/bao-hiem/diem-dang-chu-y-tai-nghi-dinh-274-2025-nd-cp-ve-cham-dong-tron-dong-bhxh-bat-buoc-563-104802-article.html) | 2025 | TB |
| 21 | 58% ứng viên bị ghost sau phỏng vấn | [CareerLink](https://www.careerlink.vn/cam-nang-viec-lam/?p=24664) | 2026-06 | Thấp–TB |
| 22 | Greenhouse: 61% bị ghost; 18–22% tin là tin ảo | [Fortune](https://fortune.com/2025/01/16/job-market-rife-fake-listing-ghosting-hiring-managers) | 2025-01 | TB–cao |
| 23 | Tỷ lệ nạn nhân lừa đảo 0,45% → 0,18%; lừa đảo việc làm không nằm trong top 5 | [Tạp chí Luật sư VN](https://lsvn.vn/mao-danh-cong-an-la-hinh-thuc-lua-dao-pho-bien-nhat-nam-2025-a168055.html) | 2026-01 | Cao |
| 24 | Vụ lừa đảo qua TopCV; TopCV có 5 lớp xác minh nhà tuyển dụng | [Báo Lào Cai / VnExpress](https://baolaocai.vn/sap-bay-lua-nha-tuyen-dung-vip-tren-trang-tim-kiem-viec-lam-post381082.html) | 2024-03 | TB |
| 25 | ~54% tin tuyển HR ghi "thương lượng" (mẫu 50 tin) | [CareerLink](https://www.careerlink.vn/cam-nang-viec-lam/tu-van-nghe-nghiep/pay-transparency-cong-khai-luong) | 2026-07 | Thấp–TB |
| 26 | Thoả thuận không cạnh tranh: toà xử không thống nhất | [Tuổi Trẻ / Saigon Times](https://tuoitre.vn/saigontimes/thoa-thuan-khong-canh-tranh-tinh-phap-ly-va-thuc-tien-xet-xu/) | 2023-04 | Cao |
| 27 | TopCV iOS: thu phí Pro 50k / Premium 500k / dịch vụ lẻ 10k; AI chấm mức độ phù hợp; máy tính gross-net/thuế/BHXH; đánh giá trên store | [Apple App Store VN (TopCV)](https://apps.apple.com/vn/app/id1455928592) | 2026-10 | Cao |
| 28 | ELSA Speak 145.000đ/tháng | [Apple App Store VN (ELSA)](https://apps.apple.com/vn/app/elsa-speak-english-learning/id1083804886) | 2026-10 | TB (một nguồn) |
| 29 | Kinh tế số Việt Nam 39 tỷ USD GMV 2025; 81% dùng AI hằng ngày | [Vietstock (e-Conomy SEA 2025)](https://en.vietstock.vn/2025/11/vietnams-digital-economy-to-touch-39-billion-in-2025-38-625181.htm) | 2025-11 | Cao |
| 30 | Coursera VN: 1,8 triệu người học; 152 nghìn lượt đăng ký GenAI | [VTV](https://english.vtv.vn/news/coursera-translates-3000-courses-into-vietnamese-20250714202255079.htm) | 2025-07 | Cao |
| 31 | Edupia khoảng 400 nghìn học sinh trả phí | [TechCrunch](https://techcrunch.com/?p=2390207) | 2022-09 | Cao (đã cũ) |
| 33 | ITviec: không công khai bảng giá; không có dịch vụ trả phí cho ứng viên | [ITviec Quy chế](https://itviec.com/blog/quy-che-hoat-dong-cua-itviec/) | 2025-12 | Cao |
| 34 | ITviec AI Match (AI phục vụ nhà tuyển dụng) | [ITviec blog](https://itviec.com/blog/ai-match-introduction/) | 2025 | TB |
| 35 | VietnamWorks: AI Application Screening, Job Post AI | [VietnamWorks HR Insider](https://www.vietnamworks.com/hrinsider/sang-loc-nhanh-chong-toan-bo-ho-so-ung-tuyen-voi-ai-application-screening.html) | 2024–2026 | TB |
| 36 | Công cụ cho ứng viên của TopDev | [TopDev](https://topdev.vn/) | 2026-10 | Cao |
| 37 | AI chấm CV đã phổ biến và miễn phí | [Cake](https://www.cake.me/resources/resume/cong-cu-ai-cham-diem-cv?locale=vi) | 2026-03 | TB |
| 38 | HRCV: AI ghép CV, gross-net, luyện phỏng vấn; 3.400 người dùng | [Tuổi Trẻ](https://tuoitre.vn/tuoi-tre-startup-award-dung-ai-ghep-cv-voi-viec-lam-ho-tro-ung-vien-luyen-phong-van-100260924154005655.htm) | 2026-09 | TB (một nguồn) |
| 39 | X-Interview: luyện phỏng vấn bằng AI | [X-Interview](https://x-interview.com/en) | 2026 | TB |
| 40 | Cục PTTH&TTĐT xác nhận đã chặn reviewcongty | [Đại biểu Nhân dân](https://daibieunhandan.vn/kien-nghi-xu-ly-cac-trang-review-cong-ty-vi-pham-phap-luat-gay-anh-huong-den-uy-tin-cua-doanh-nghiep-10348852.html) | 2024 | Cao |
| 41 | Bộ TT&TT chặn reviewcongty ngày 19/6/2023 | [VnEconomy](https://vneconomy.vn/kien-nghi-xu-ly-13-mang-xa-hoi-danh-gia-doanh-nghiep.htm) | 2023-06 | Cao |
| 42 | LinkedIn Premium doanh thu hơn 2 tỷ USD trong 12 tháng | [TechCrunch](https://techcrunch.com/2025/01/29/linkedin-passes-2b-in-premium-revenues-in-12-months-with-overall-revenues-up-9-on-the-year) | 2025-01 | Cao |
| 43 | Final Round AI: gói Pro từ 25 USD/tháng; gọi vốn seed 6,88 triệu USD | [Final Round AI](https://www.finalroundai.com/pricing) | 2026-10 | TB |
| 44 | Levels.fyi: dịch vụ thương lượng 1.250–5.000 USD, có cam kết kết quả | [Levels.fyi](https://www.levels.fyi/services/) | 2026 | Cao |
| 45 | Thương lượng từng là nguồn thu lớn nhất của Levels.fyi | [Fast Company](https://www.fastcompany.com/90604436/levels-fyi-leveling-tech-salaries-leveling-negotiation) | ~2021 | TB |
| 46 | Triplebyte dừng hoạt động; Karat chỉ mua công nghệ đánh giá | [Karat](https://connect.karat.com/tb-candidates) | 2023-03 | Cao |
| 47 | Hired được Vettery mua, sau đó sáp nhập vào LHH | [Staffing Industry Analysts](https://www.staffingindustry.com/news/global-daily-news/adecco-incorporating-hired-lhh-business) | 2024-05 | Cao |
| 48 | Findy gọi vốn Series D 2,05 tỷ yên; khoảng 200 nghìn thành viên | [THE BRIDGE](https://thebridge.jp/2025/05/findy-raises-2-05-billion-yen-in-series-d-funding-aiming-to-expand-into-south-korea-taiwan-and-india-with-a-goal-of-serving-1600-companies-across-asia) | 2025-05 | TB–cao |
| 49 | Findy lỗ ròng khoảng 995 triệu yên năm tài chính 2025 (thu hẹp so với khoảng 1,06 tỷ yên năm 2024) | [PR TIMES (công bố tài chính)](https://prtimes.com/finance/8011001098775/settlement) | 2026 | TB–cao |
| 50 | LAPRAS khoảng 40 nghìn người dùng | [THE BRIDGE](https://thebridge.jp/2025/08/lapras-welcomes-spurcle-as-new-investor-strengthens-regional-talent-ecosystem) | 2025-08 | TB |
| 51 | Indeed và Glassdoor cắt khoảng 1.300 nhân sự; Glassdoor nhập vào Indeed | [HR Dive](https://www.hrdive.com/news/layoffs-glassdoor-indeed-ai-headwinds/752876/) | 2025-07 | Cao |
| 52 | Google Career Dreamer miễn phí, dùng dữ liệu Lightcast | [AIN](https://en.ain.ua/2025/02/24/google-launches-career-dreamer) | 2025-02 | Cao |
| 53 | Glints gọi 50 triệu USD rồi cắt giảm 18% nhân sự | [TechCrunch](https://techcrunch.com/2022/08/29/singapore-based-career-development-platform-glints-recruits-50m-in-new-funding) | 2022-08 | Cao |
| 54 | Tiện ích GhostJob: 23 người dùng/tháng, doanh thu 0 USD | [Indie Hackers](https://www.indiehackers.com/post/building-ghostjob-a-chrome-extension-to-detect-ghost-job-postings-day-19-23-mau-0-mrr-b6083b2db2) | 2026-05 | TB |
| 55 | roadmap.sh Pro 8,33 USD/tháng | [roadmap.sh](https://roadmap.sh/premium) | 2026 | TB |
| 56 | Luật Việc làm 74/2025: Điều 20, 27, 28, 54 | [LuatVietnam (toàn văn)](https://luatvietnam.vn/lao-dong/luat-viec-lam-cua-quoc-hoi-so-74-2025-qh15-405176-d1.html) | 2025-06 | Cao |
| 57 | Luật BVDLCN 2025, Điều 38: ưu đãi cho doanh nghiệp khởi nghiệp | [LuatVietnam](https://luatvietnam.vn/dan-su/luat-bao-ve-du-lieu-ca-nhan-2025-co-hieu-luc-khi-nao-568-103652-article.html) | 2025-08 | TB–cao |
| 58 | Nghị định 356/2025, Điều 4: danh mục dữ liệu nhạy cảm | [LuatVietnam](https://luatvietnam.vn/tin-van-ban-moi/thong-tin-ve-suc-khoe-la-du-lieu-ca-nhan-nhay-cam-186-106394-article.html) | 2026-01 | TB–cao |
| 59 | Luật BVDLCN: Điều 25 về tuyển dụng; mức phạt; chuyển dữ liệu xuyên biên giới | [Le & Tran Law](https://letranlaw.com/?p=29633) | 2026-08 | TB–cao |
| 60 | Quyết định 33/2026: danh mục AI rủi ro cao (không có tuyển dụng) | [VOV](https://vov.vn/cong-nghe/ban-hanh-danh-muc-he-thong-ai-rui-ro-cao-trong-6-linh-vuc-post1311806.vov) | 2026-07 | Cao |
| 61 | Luật AI 134/2025 hiệu lực 01/3/2026; 3 mức rủi ro | [Baker McKenzie](https://www.bakermckenzie.com/en/insight/publications/2026/02/vietnam-artificial-intelligence-law-foundation-and-outlook) | 2026-02 | Cao |
| 62 | Nghị định 147/2024: xác thực tài khoản bằng số điện thoại; gỡ nội dung trong 24 giờ (tổng hợp báo chí, chưa đọc điều khoản gốc) | VTC News / VietNamNet / LSVN (đoạn trích tìm kiếm) | 2024-12 | TB |
| 63 | ChatGPT Go ~132.000đ, Plus ~522.000đ | [FPT Shop](https://fptshop.com.vn/tin-tuc/for-gamers/bang-gia-chatgpt-197750) | ~2026-07 | TB (có mâu thuẫn) |
| 64 | Thu nhập bình quân người lao động ~8,3 triệu/tháng (Tổng cục Thống kê) | [Tuoi Tre News](https://news.tuoitre.vn/vietnam-incomes-rise-10-but-16mn-young-people-remain-out-of-work-or-school-103251008130456723.htm) | 2025-10 | TB–cao |
| 65 | Ứng dụng tự hướng dẫn giữ chân người dùng trung vị 2,5–3,5 tuần (lĩnh vực lân cận) | [JMIR / PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9091343/) | 2022 | TB |
| 66 | 86% lập trình viên Việt Nam kiểm tra lại kết quả AI | [Viet Nam News (Agoda)](https://vietnamnews.vn/economy/1800573/ai-delivers-significant-productivity-gains-for-vietnamese-developers-report.html) | 2026 | TB (đoạn trích) |
| 67 | Luật Luật sư, Điều 32: hành nghề qua tổ chức hành nghề luật sư (tổng hợp, chưa đọc văn bản gốc) | luatvietan.vn / LSVN (đoạn trích tìm kiếm) | — | Thấp–TB |
| 68 | LinkedIn Việt Nam khoảng 10 triệu tài khoản (tập quảng cáo) | [NapoleonCat](https://napoleoncat.com/stats/linkedin-users-in-viet_nam/2025/08) | 2025 | TB |
| 69 | Doanh thu phí dịch vụ việc làm ~7.100 tỷ đồng (khoảng 2020) | [Brands Vietnam (Vietdata)](https://www.brandsvietnam.com/congdong/topic/data-station-56-vietdata-thi-truong-tuyen-dung-viet-nam) | ~2020 | Thấp |
| 70 | Navigos: doanh thu thuần 2024 giảm 2,68% | [EMIS](https://www.emis.com/php/company-profile/VN/Navigos_Group_Vietnam_Joint_Stock_Company__C%C3%B4ng_Ty_C%E1%BB%95_Ph%E1%BA%A7n_Navigos_Group_Vi%E1%BB%87t_Nam___C%C3%B4ng_Ty_C%E1%BB%95_Ph%E1%BA%A7n_Navigos_Group_Vi%E1%BB%87t_Nam__Navigos_Group_Vietnam_Joint_Stock_Company___en_7343161.html) | 2024 | Thấp |
| 71 | Kênh YouTube F8 khoảng 143 nghìn người đăng ký (ước tính) | [developereducators.com](https://developereducators.com/channel/f8vnofficial/) | 2026-08 | TB |
| 72 | AppsFlyer VN 2025: 1,37 tỷ lượt cài trả phí; 397 triệu USD chi cho thu hút người dùng | [AppsFlyer](https://www.appsflyer.com/resources/reports/app-marketing-vietnam/) | 2025 | TB |
| 73 | MindX: mô hình "học trước, trả sau"; gọi vốn 3,3 triệu USD | [TechCrunch](https://techcrunch.com/2021/11/15/education-startup-mindx-raises-3-3m-to-prepare-vietnamese-students-for-tech-careers) | 2021-11 | TB (đã cũ) |
| 74 | Điều 27(1),(2) Luật Việc làm 2025 (đoạn trích) | [Thư Viện Pháp Luật](https://thuvienphapluat.vn/lao-dong-tien-luong/luat-viec-lam-2025-dich-vu-viec-lam-bao-gom-hoat-dong-nao-45683.html) | 2025 | TB–cao |
| 75 | Nghị định 352/2025: ký quỹ 300 triệu; UBND tỉnh cấp phép; thời hạn 60 tháng | [Hệ thống pháp luật](https://hethongphapluat.com/decree-no-352-2025-nd-cp-dated-december-30-2025-on-elaborating-certain-articles-of-the-law-on-employment-concerning-employment-services.html) | 2025-12 | Cao |
| 76 | ITviec có giấy phép dịch vụ việc làm 19710/2023 | [ITviec](https://itviec.com/ve-itviec) | 2026 | Cao |
| 77 | Nghị định 12/2022: phạt 45–60 triệu đồng nếu hoạt động không phép | [Đại biểu Nhân dân](https://daibieunhandan.vn/doanh-nghiep-hoat-dong-khi-chua-duoc-cap-giay-phep-se-bi-xu-ly-the-nao-10330253.html) | ~2024 | TB |
| 78 | Nghị định 77/2008 về tư vấn pháp luật vẫn còn hiệu lực một phần | [Luật Minh Khuê](https://luatminhkhue.vn/van-ban/nghi-dinh-77-2008-nd-cp.aspx) | — | TB |
| 79 | 47% Gen Z cho rằng ChatGPT tư vấn nghề tốt hơn sếp (Mỹ) | [BusinessWire (Workplace Intelligence/INTOO)](https://www.businesswire.com/news/home/20230110005699/en/) | 2023-01 | Thấp–TB (đoạn trích) |

## Bản đồ độ mới (staleness map)

**Cần làm ngay:** cập nhật [3] (số lập trình viên) và [9] (số tin ITviec) bằng báo cáo TopDev và ITviec mới; kiểm tra lại [27] (giá và tính năng TopCV) vào **01/2027**.

Thời hạn độ mới theo nhóm: quy mô/tăng trưởng 18 tháng · giá & tính năng 3 tháng · hành vi 24 tháng · quy mô người dùng/doanh thu đối thủ 12 tháng · pháp lý 36 tháng.

| Kiểm tra lại từ | Nhận định | Ghi chú |
|---|---|---|
| **Cần cập nhật ngay** | [3] 500–560 nghìn lập trình viên · [9] ITviec Q1/2025 · [30] Coursera VN · [31] Edupia · [42] LinkedIn Premium | Đã quá hạn độ mới |
| Sự kiện lịch sử | [41] reviewcongty bị chặn · [46] Triplebyte | Không bị lỗi thời |
| 2026-11 | [1] Số lao động ICT và số sinh viên tốt nghiệp | |
| 2026-12 | [6] 40,9% định nghỉ việc | Khi ITviec ra báo cáo 2025-26 bản đầy đủ |
| **2027-01** | [27] Giá và tính năng TopCV · [28] ELSA · [44] Levels.fyi | Giá và tính năng thay đổi nhanh nhất |
| 2027-02 → 2027-12 | [7] JobsGO · [49] Findy · [12] JobOKO · [38] HRCV · [13] JobOKO fresher · [8] Lương ITviec | |
| 2028+ | [11] · [18] · [21] · [23] · [56] · [57] · [58] · [60] | Pháp lý: theo dõi nghị định hướng dẫn Luật AI và nghị định xử phạt mới về việc làm |
