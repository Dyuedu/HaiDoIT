---
title: 'Digest cho PRD: nghiên cứu thị trường Hải Đồ IT'
type: 'prd-extract'
source: '_bmad-output/planning-artifacts/research/market-hai-do-it-nen-tang-nghe-nghiep-it-viet-n-2026-10-22/research.md'
source_status: complete
source_created: '2026-10-22'
extracted: '2026-10-22'
product: 'Hải Đồ IT — web hướng nghiệp IT Việt Nam cho junior, fresher, người chuyển hướng'
note: 'Rút từ research.md. Không sửa nguồn. Không bổ sung số liệu ngoài báo cáo. Nhãn Khuyến nghị và Suy luận là của chính báo cáo.'
---

# Digest cho PRD — nghiên cứu thị trường Hải Đồ IT (2026-10-22)

Nguồn duy nhất: `research.md` cùng thư mục nghiên cứu thị trường ngày 2026-10-22. Báo cáo phục vụ câu hỏi *có nên thương mại hóa, và màn nào trong 11 màn prototype là điểm vào*. Phương pháp: web fan-out, 13 trợ lý, 3 vòng, có 1 vòng red team. Sổ nhận định: 29 ref, **21 đã xác minh, 7 chưa xác minh, 1 bị lật**. Độ tin cậy tổng thể báo cáo: **TB**. Mọi nguồn trong báo cáo được truy cập 2026-10-22. Số `[n]` là số nguồn trong phụ lục của báo cáo.

Ba nhãn dùng xuyên suốt digest:

- **Dữ kiện** — báo cáo nêu số và nguồn.
- **Suy luận** — báo cáo tự gắn là không phải dữ kiện.
- **Khuyến nghị** — việc nên làm; không phải bằng chứng nhu cầu hay sẵn lòng trả.

---

## 1. Người dùng: ai, nỗi đau, việc cần làm

Báo cáo khoanh thị trường là ứng viên IT Việt Nam: junior/mid, người chuyển hướng, sinh viên sắp ra trường. Ba phân khúc được rút từ bằng chứng:

| Phân khúc | Quy mô / tín hiệu | Thu nhập báo cáo nêu | Việc họ đang làm |
|---|---|---|---|
| Sinh viên / fresher (&lt;1 năm) | Khoảng 50–60 nghìn người tốt nghiệp hoặc nhập học mỗi năm. Nhân Dân: khoảng 50 nghìn tốt nghiệp/năm, chỉ khoảng 30% đáp ứng yêu cầu việc làm [1], độ tin cậy TB. TopDev: 55–60 nghìn sinh viên nhập học/năm [3], TB. Tuyển người dưới 1 năm kinh nghiệm giảm 13%; nhóm này chiếm 45% số ca bị cắt giảm (JobOKO, Tuổi Trẻ, 2025-12) [13], TB–cao | Trung vị khoảng 10–14 triệu/tháng: back-end 12,4 triệu, full-stack 10,1 triệu. ITviec 2025-26, n=1.839 [8], TB. Đây là hai mức trung vị, không phải dải của mọi vai trò | Tìm thực tập qua Facebook 47,5%, người quen 37,5%, chương trình nhà trường 30% (ITviec) [6] |
| Junior/mid muốn chuyển hướng (ví dụ báo cáo dùng: PHP → Data/AI) | 26,3% muốn nghỉ để đổi hướng nghề (ITviec) [6]. Lượt tìm "AI" trên ITviec tăng 89% (Q1/2025) [9] | 1–2 năm: back-end trung vị 25,35 triệu; Data Engineer trung vị 41,3 triệu [8]. Mức Data Engineer không phải lương fresher | Muốn môi trường cởi mở, sáng tạo và lộ trình rõ ràng: hơn 70% muốn, khoảng 1/3 thấy công ty hiện tại đáp ứng. JobsGO, **một nguồn, chưa xác minh**; câu này gộp môi trường với lộ trình [7] |
| Mid/senior đổi việc hoặc nhắm Nhật/remote | Khoảng 41–55% có ý định đổi việc, xem hai khảo sát bên dưới [6][7] | Báo cáo chỉ ghi "lương cao hơn", không nêu số riêng | Khi chọn việc, 70% coi trọng review của nhân viên, 57% coi trọng phúc lợi (ITviec) [6] |

### Ý định đổi việc — đã có hai nguồn, không được gộp

- ITviec 2024-25, n=2.324: **40,9%** dân IT dự định nghỉ việc trong 12 tháng. Blog chính thức làm tròn thành "40%". Lý do: lương 34,2%, muốn đổi hướng 26,3%, thiếu cơ hội phát triển 22,3% [6]. Độ tin cậy TB–cao. Nguồn là sàn việc làm nên có thể thiên lệch. PDF đầy đủ bị khóa.
- JobsGO, PLO/Tuổi Trẻ, 2025-02: **54,5%** dân IT đang chủ động tìm việc năm 2025, so với 48,4% mọi ngành [7]. TB–cao.

Hai câu hỏi khác nhau. Báo cáo cho phép dùng **khoảng 41–55%**, không cộng thành một tỷ lệ. **Suy luận của báo cáo:** áp vào 500–560 nghìn người thì nhóm cân nhắc đổi việc mỗi năm khoảng 200–300 nghìn, chưa kể người mới ra trường. Đây không phải dữ kiện.

### Nỗi đau, xếp theo độ mạnh bằng chứng

Báo cáo nói rõ: nỗi đau mạnh chỉ chứng minh vấn đề có thật, **không** chứng minh người dùng trả tiền cho cố vấn AI.

| Nỗi đau | Bằng chứng và nguồn | Độ mạnh trong báo cáo | Việc người dùng cần (đọc từ bằng chứng) |
|---|---|---|---|
| Junior/fresher mất phương hướng trước AI | Tuyển &lt;1 năm giảm 13%, nhóm này = 45% ca cắt giảm [13]. Tỷ lệ doanh nghiệp coi năng suất AI là lý do không tuyển thêm: 5,9% (2024) → 20,2% (2025) → **dự báo** 34,3% (2026). Doanh nghiệp không tăng hoặc giảm biên chế: 4,9% (2021) → 31% (2026). Doanh nhân / Báo Pháp luật VN [11], TB–cao. Một bạn trẻ phỏng vấn 10 lần trong 6 tháng, được trả lời cắt tuyển junior vì AI giúp senior làm nhanh hơn; xu hướng 2023–2026. VnExpress International [14], cao | **Mạnh** (≥2 nguồn độc lập) | Chọn hướng học và việc khi cửa fresher hẹp lại |
| Muốn đổi việc hoặc đổi hướng nhưng thiếu lộ trình | 40,9% và 54,5% là ý định đổi việc, mạnh [6][7]. Phần "thiếu lộ trình" nằm trong câu JobsGO gộp với môi trường làm việc, **chưa xác minh** [7] | **Mạnh về ý định; chưa xác minh về thiếu lộ trình** | Đổi việc hoặc đổi hướng. Nhu cầu "một lộ trình" chưa được tách riêng |
| Đóng BHXH thấp hơn thu nhập thực | 43,1% đóng theo mức lương cố định, thấp hơn thu nhập thực; 10,7% đóng theo lương tối thiểu vùng; 38,3% đóng trên toàn bộ lương gross. Navigos Talent Guide 2026, hơn 250 doanh nghiệp, hơn 1.600 người lao động, VCCI đăng lại [18]. **Không có số riêng cho IT.** Nghị định 274/2025 phạt chậm đóng 0,03%/ngày [20] | **TB**, một nguồn | Khi cầm offer, kiểm tra mức đóng BHXH so với lương thực |
| Bị nhà tuyển dụng ghost | 58% ứng viên Việt Nam từng bị ghost sau phỏng vấn. CareerLink, không nêu phương pháp [21], thấp–TB, **chưa xác minh tại Việt Nam**. Greenhouse (quốc tế): 61%, tăng 9 điểm phần trăm từ 2021 [22] | **TB–yếu** | Biết nhà tuyển dụng có phản hồi hay không — bằng chứng Việt Nam mỏng |
| Lương không minh bạch | Khoảng 54% tin tuyển HR ghi "thương lượng". Mẫu 50 tin, **không phải IT**. CareerLink [25] | **Yếu** | Thấy mức lương trước khi ứng tuyển — mẫu không đại diện cho IT |
| Tin tuyển dụng lừa đảo | Tỷ lệ nạn nhân lừa đảo trực tuyến 0,45% (2024) → 0,18% (2025). Lừa đảo việc làm không nằm trong top 5. Nạn nhân chủ yếu là lao động phổ thông. Tạp chí Luật sư VN [23], cao. Có một vụ qua TopCV; TopCV có 5 lớp xác minh nhà tuyển dụng [24], TB | **Yếu hơn báo cáo từng kỳ vọng** | Tránh tin lừa — vấn đề có thật nhưng không phải nỗi đau đặc trưng của dân IT trong dữ liệu này |
| Điều khoản hợp đồng bất lợi | Thỏa thuận không cạnh tranh không bị cấm; tòa xử không thống nhất (2010 công nhận, 2019 bác) [26], cao. Báo cáo không thấy nhiều phàn nàn từ dân IT | **Yếu** | Soát hợp đồng — nhu cầu IT chưa được chứng minh |

### Hành vi liên quan tới sản phẩm hướng nghiệp

- Chọn việc (JobsGO): cơ hội phát triển 72,7%, văn hóa công ty 69,7%, lương thưởng 67,7% [7].
- Kênh tìm việc (ITviec 2023-24, chính sàn công bố): trang tuyển dụng 55,9%, LinkedIn 16,4%, người quen 10,3% [6].
- LinkedIn Việt Nam khoảng 10 triệu tài khoản (12/2025, NapoleonCat, đếm theo tập quảng cáo, không phải người dùng hoạt động) [68], TB.
- 81% người Việt được khảo sát tương tác với công cụ AI hằng ngày. e-Conomy SEA 2025, Vietstock [29], cao.
- 93,49% dân IT-phần mềm dùng AI trong công việc. TopCV tự công bố, không nêu phương pháp, **độ tin cậy thấp** [16].
- 86% lập trình viên Việt Nam luôn hoặc thường xuyên kiểm tra lại kết quả AI. Agoda, Viet Nam News [66], TB.

**Khuyến nghị R1 của báo cáo** (độ tin cậy TB, không phải bằng chứng): điểm vào thị trường là cố vấn lộ trình 90 ngày có nút "Vì sao?" trích nguồn, cộng mô phỏng Nếu–thì, cộng xu hướng kỹ năng, cho junior/fresher và người chuyển hướng. Báo cáo gắn khuyến nghị này với nỗi đau AI [11][13][14] và với khoảng trống trải nghiệm, đồng thời ghi rủi ro bị sao chép và bị ChatGPT thay thế.

---

## 2. Cạnh tranh và khoảng trống báo cáo nêu

Đối thủ trong nước thu tiền chủ yếu từ nhà tuyển dụng và đã có công cụ phía ứng viên. Bài học quốc tế trong báo cáo là bài học mô hình kinh doanh, không phải đối thủ đang bán tại Việt Nam.

### Trong nước — ai đang đứng ở đâu

| Sản phẩm | Vị trí báo cáo mô tả | Bằng chứng |
|---|---|---|
| **TopCV** | Nền tảng lớn, có hồ sơ ứng viên và đã thu tiền phía ứng viên | Khoảng 9–10 triệu hồ sơ, tự công bố, không thống nhất: bản tiếng Anh 10 triệu+, bản tiếng Việt 9,5 triệu+ [16], TB. App iOS đã có AI đánh giá mức độ phù hợp và khả năng cạnh tranh theo từng việc, máy tính lương gross/net, thuế TNCN và BHXH, trắc nghiệm MBTI/MI, CV builder. Có trang tra cứu lương theo vị trí nhưng nguồn chỉ là đoạn trích tìm kiếm, độ tin cậy thấp. 36 nghìn lượt đánh giá, điểm 4,8. App Store VN, 2026-10 [27], cao cho giá và tính năng app. Không tìm thấy doanh thu |
| **ITviec** | Sàn IT, AI chủ yếu cho nhà tuyển dụng, lương là báo cáo tĩnh | Báo cáo lương hằng năm, n=1.839 (2025-26), chỉ trung vị; PDF đầy đủ đổi lấy thông tin liên hệ. Không có công cụ tra lương phân vị tương tác [8]. "AI Match", "Talent Finder" phục vụ nhà tuyển dụng [33][34]. Có review công ty được kiểm duyệt [34]. Quy chế hoạt động không có dịch vụ trả phí cho ứng viên [33], cao. Đã có giấy phép dịch vụ việc làm số 19710/2023/39/SLĐTBXH-VLATLĐ [76], cao |
| **VietnamWorks** | AI cho nhà tuyển dụng | AI Application Screening; Job Post AI ra mắt 4/2026 [35], TB. Chân trang chỉ thấy đăng ký kinh doanh; báo cáo không xác nhận giấy phép dịch vụ việc làm [76] |
| **TopDev** | Công cụ ứng viên cơ bản, không có AI cho ứng viên | CV builder, máy tính gross-net, trắc nghiệm tính cách [36], cao. Cũng là nguồn duy nhất của số 480–560 nghìn người làm IT [3] |
| **Cake, VietnamWorks, JobsGO** | AI chấm CV đã thành hàng miễn phí | [37], TB |
| **HRCV** | Đối thủ mới, 2026, ghép CV với việc | Ra mắt 6/2026. AI phân tích CV và ghép việc, máy tính gross-net, tham khảo lương; luyện phỏng vấn đang phát triển. Khoảng 3.400 người dùng (8/2026). Tuổi Trẻ, **một nguồn** [38], TB |
| **X-Interview** | Luyện phỏng vấn bằng AI từ JD | Chưa rõ quy mô người dùng [39], TB |
| **reviewcongty** | Đánh giá công ty ẩn danh | Bộ TT&TT chặn ngày 19/6/2023 sau kiến nghị hiệp hội ngành [40][41], cao. Sau đó vẫn hoạt động trên tên miền nhân bản |

Mô hình thu tiền trong nước: bán gói đăng tin, thương hiệu tuyển dụng và quyền xem kho CV cho nhà tuyển dụng. Giá theo báo giá, không công khai [33].

### Quốc tế — bài học mô hình, đúng tên sản phẩm trong báo cáo

| Tên | Việc báo cáo dùng họ để chỉ | Kết luận của báo cáo |
|---|---|---|
| LinkedIn Premium | Ứng viên trả tiền trên một mạng lưới lớn | Doanh thu hơn 2 tỷ USD trong 12 tháng [42], cao |
| Levels.fyi | Lương cộng đồng kéo người vào; tiền nằm ở dịch vụ có cam kết kết quả | Thương lượng 1.250–5.000 USD/lần, không đạt thì hoàn tiền [44], cao. Thương lượng từng là nguồn thu lớn nhất [45], TB |
| Findy (Nhật) | Hộ chiếu kỹ năng: ứng viên miễn phí, nhà tuyển dụng trả | Series D 2,05 tỷ yên (5/2025); phụ lục nguồn còn ghi khoảng 200 nghìn thành viên [48]. Vẫn lỗ ròng khoảng 995 triệu yên năm tài chính 2025; lỗ khoảng 1,06 tỷ yên năm 2024 rồi thu hẹp [49], TB–cao |
| LAPRAS (Nhật) | Hộ chiếu kỹ năng | Khoảng 40 nghìn người dùng sau khoảng 7 năm [50], TB |
| Triplebyte | Hồ sơ kỹ năng đã xác minh | Dừng hoạt động 31/3/2023. Karat mua công nghệ đánh giá, không mua kho hồ sơ [46], cao |
| Hired | Sàn ghép việc hai phía | Gọi khoảng 130 triệu USD, bị bán khi chịu áp lực trả nợ, sáp nhập vào LHH năm 2024 [47], cao |
| Glassdoor | Review nhà tuyển dụng như một doanh nghiệp | Bị nhập vào Indeed; Indeed và Glassdoor cắt khoảng 1.300 nhân sự [51], cao |
| Google Career Dreamer | Khám phá lộ trình thành hàng miễn phí của ông lớn | Miễn phí, dữ liệu Lightcast, hiện chỉ có ở Mỹ [52], cao |
| Final Round AI / Teal | Công cụ AI cho ứng viên và luyện phỏng vấn | Lần lượt gọi vốn 6,9 triệu và 19 triệu USD; giá khoảng 25–29 USD/tháng; không công bố doanh thu định kỳ [43]. Phụ lục chỉ chi tiết Final Round AI: Pro từ 25 USD/tháng, seed 6,88 triệu USD |
| roadmap.sh | Lộ trình freemium | Pro 8,33 USD/tháng, có gia sư AI [55], TB |
| Tiện ích GhostJob | Phát hiện tin tuyển dụng ảo | 23 người dùng/tháng, doanh thu 0 USD [54], TB |
| Glints (Đông Nam Á) | Nền tảng nghề nghiệp gọi vốn khu vực | Gọi 50 triệu USD rồi cắt 18% nhân sự [53], cao |

### Khoảng trống báo cáo khẳng định

Trong phạm vi đã tìm, báo cáo nói **chưa chứng minh là không tồn tại**:

- tra lương theo phân vị (P25/P75) có ngưỡng mẫu;
- cố vấn hội thoại đa agent có trích nguồn ("Vì sao?");
- mô phỏng "nếu học thêm kỹ năng X thì sao";
- quét dấu hiệu tin treo hoặc tin ảo;
- soát điều khoản hợp đồng.

Câu chữ của báo cáo: chưa thấy ai kết hợp "dữ liệu thị trường lao động + cố vấn AI đa agent" trong một sản phẩm [52][48]. **Đây là khoảng trống, không phải bằng chứng có nhu cầu.**

Phần dữ liệu không trống: TopCV, ITviec, VietnamWorks, TopDev đang nắm tin và hồ sơ. Rủi ro bị bắt chước được báo cáo ghi là **rất cao** [27][34].

Hộ chiếu kỹ năng (hồ sơ đã xác minh, nhà tuyển dụng trả tiền) không phải lối né còn trống: Triplebyte đã dừng, Findy vẫn lỗ, LAPRAS tăng chậm, Hired suy khi thị trường tuyển dụng đi xuống.

Red team làm yếu thêm câu "phía ứng viên còn trống": ITviec và TopDev đã ra báo cáo lương nhiều năm [8].

---

## 3. Sẵn lòng chi trả

### Bằng chứng báo cáo thực sự có

| Việc người ta đã trả | Mức | Ai trả | Giới hạn của bằng chứng |
|---|---|---|---|
| TopCV Pro / Premium / dịch vụ lẻ | 50.000đ / 500.000đ / 10.000đ. Dịch vụ lẻ gồm xem số người đã ứng tuyển và tải CV không logo | Ứng viên | **Chưa rõ thời hạn** của Pro/Premium và gói gồm những gì [27], cao. Đây là khoản nhỏ, không phải bằng chứng thuê bao định kỳ cho công cụ hướng nghiệp |
| ELSA Speak | 145.000đ/tháng; 769.000–1.590.000đ/năm | Người học tiếng Anh | Một nguồn [28], TB. Không phải dân IT trả cho công cụ nghề |
| ChatGPT Go / Plus | khoảng 132.000đ / khoảng 522.000đ mỗi tháng | Người dùng ChatGPT | FPT Shop [63], TB, nguồn mâu thuẫn về cách tính tiền |
| Levels.fyi | 1.250–5.000 USD mỗi lần thương lượng, có cam kết tăng lương | Ứng viên tại Mỹ | [44], cao. Không phải giá Việt Nam |
| Edupia | Khoảng 400 nghìn học sinh trả phí trên 5 triệu người dùng | Phụ huynh / học sinh phổ thông | TechCrunch, 2022-09 [31], cao nhưng **đã cũ**. Không phải IT đi làm |
| Coursera Việt Nam | 1,8 triệu người học (+22%); 152 nghìn lượt đăng ký khóa GenAI (+400%), 7/2025 | Người học | VTV [30], cao. Báo cáo nói "người học" và "lượt đăng ký", **không nói đây là người trả phí** |
| Bootcamp "học trước, trả sau", cam kết việc làm (MindX, CodeGym) | Không nêu học phí | Học viên | Nguồn quảng cáo, độ tin cậy thấp [73]. Phụ lục chỉ chi tiết MindX: gọi vốn 3,3 triệu USD, TechCrunch 2021-11, đã cũ |

Thu nhập để đối chiếu, không phải bằng chứng đã trả:

- Fresher IT: trung vị khoảng 10–14 triệu/tháng [8].
- Thu nhập bình quân người lao động nói chung: khoảng 8,3 triệu/tháng. Tổng cục Thống kê, Tuổi Trẻ [64], TB–cao.

**Suy luận của báo cáo, không phải dữ kiện:** gói 50.000–150.000đ/tháng tương đương khoảng 0,4–1,5% lương junior, "là mức chấp nhận được". Ngay sau câu này báo cáo viết: chưa có bằng chứng ứng viên IT sẽ trả phí định kỳ cho công cụ nghề nghiệp.

Việc báo cáo **không** tìm được:

- Bất kỳ bằng chứng nào về phí **định kỳ** của dân IT Việt Nam cho công cụ nghề nghiệp.
- CAC hoặc CPI cho ứng dụng giáo dục và nghề nghiệp tại Việt Nam. AppsFlyer chỉ được báo cáo dẫn là thị trường đã chuyển từ chạy theo lượt cài sang chất lượng người dùng [72]. Phụ lục nguồn còn ghi AppsFlyer VN 2025: 1,37 tỷ lượt cài trả phí và 397 triệu USD chi cho thu hút người dùng — đây là số toàn thị trường app, **không phải CAC của Hải Đồ IT**. Câu hỏi mở nói báo cáo AppsFlyer và Adjust bị khóa.
- Doanh thu TopCV, ITviec, Navigos. Với Navigos chỉ có doanh thu thuần 2024 giảm 2,68%, nguồn bị khóa, chưa xác minh [70].
- Doanh thu thị trường tuyển dụng trực tuyến 2023–2026. Số duy nhất: khoảng 7.100 tỷ đồng phí dịch vụ giới thiệu việc làm, gồm cả headhunt offline, Vietdata khoảng 2020, độ tin cậy thấp [69].

### Khuyến nghị — tách khỏi bằng chứng

Độ tin cậy của cả khối giá bên dưới là **thấp–TB**. Báo cáo tự ghi: *chưa có bằng chứng về mức sẵn lòng trả của dân IT.*

- **R2.** Thu tiền gắn với kết quả, không bán thuê bao "lời khuyên": hợp tác trường và bootcamp (B2B2C), hoa hồng giới thiệu khóa học, gói "lộ trình + review dự án" theo đợt. Thử giá 50.000đ và 150.000đ. Căn cứ báo cáo nêu là giá TopCV và ELSA, Edupia, Levels.fyi, Coursera VN, và việc sinh viên tìm việc qua trường [6].
- **R3.** Miễn phí để kéo người vào: so sánh offer theo thực nhận, có kiểm tra mức đóng BHXH, và soi tin (cảnh báo tin treo). Căn cứ: 43,1% đóng BHXH thấp hơn thu nhập thực [18]; GhostJob doanh thu 0 [54]; máy tính gross-net đã phổ biến [27]. Độ tin cậy TB.
- **R8.** Trước khi làm PRD: phỏng vấn 15–20 junior/fresher và 3–5 trường hoặc bootcamp; trang giới thiệu tính năng chưa có ở hai mức 50.000đ và 150.000đ; xin ý kiến luật sư về Điều 27. Báo cáo ghi độ tin cậy **cao về sự cần thiết của bước kiểm chứng**, không phải cao về mức giá.

Cách nói còn đứng sau red team: ứng viên trả khoản nhỏ cho thứ gắn với kết quả gần; doanh thu thuê bao định kỳ chưa được chứng minh. Edupia và TopCV làm yếu câu "ứng viên không trả tiền", không biến câu đó thành "dân IT sẽ thuê bao".

---

## 4. Ràng buộc pháp lý, dữ liệu, cào và niềm tin

### 4.1 Luật Việc làm 2025 — báo cáo gọi là điểm nghẽn lớn nhất

Luật Việc làm 74/2025/QH15, hiệu lực 01/01/2026 [56][74], độ tin cậy cao với câu chữ điều luật:

- Điều 27(1): dịch vụ việc làm gồm tư vấn, giới thiệu việc làm; cung ứng và giới thiệu lao động; **thu thập, phân tích, lưu trữ, cung cấp thông tin về thị trường lao động**.
- Điều 20(1): thông tin thị trường lao động gồm cả **tiền lương và thu nhập**.
- Điều 27(4): chỉ doanh nghiệp đã có giấy phép được cung cấp dịch vụ việc làm theo thương mại điện tử.

Nghị định 352/2025, hiệu lực 01/01/2026 [75], cao:

- ký quỹ **300 triệu đồng**;
- trụ sở còn thời hạn sử dụng ít nhất 24 tháng;
- người đại diện có bằng đại học hoặc 2 năm kinh nghiệm;
- UBND cấp tỉnh cấp, thời hạn tối đa 60 tháng;
- doanh nghiệp cung cấp qua thương mại điện tử phải đồng bộ dữ liệu với Sàn giao dịch việc làm quốc gia.

Không tìm thấy điều khoản miễn giấy phép cho dịch vụ miễn phí hoặc "chỉ cung cấp thông tin". Theo câu chữ, bản đồ nhu cầu tuyển dụng và tra lương nằm trong định nghĩa dịch vụ việc làm. **Mức rủi ro trên thực tế chưa rõ.** Báo cáo xếp đây là câu hỏi cho luật sư hoặc Sở Nội vụ trước khi ra mắt.

Chế tài cũ: Nghị định 12/2022 phạt 45–60 triệu đồng nếu hoạt động dịch vụ việc làm không phép, không phụ thuộc vào việc có thu phí hay không [77], TB. Nghị định xử phạt mới **chưa tìm được**, nên mức phạt này chưa xác minh là còn áp dụng.

Giấy phép đã thấy: ITviec có [76]. VietnamWorks: chân trang chỉ có đăng ký kinh doanh [76]. TopCV: chưa kiểm tra.

### 4.2 Dữ liệu cá nhân và AI

Luật Bảo vệ dữ liệu cá nhân 91/2025 và Nghị định 356/2025, hiệu lực 01/01/2026 [57][58]:

- Danh mục dữ liệu nhạy cảm **không** gồm lương, thu nhập, lịch sử việc làm. Danh mục **có** ảnh CCCD, dữ liệu thẻ, giao dịch ngân hàng, và dữ liệu theo dõi hành vi trên mạng xã hội hoặc dịch vụ trực tuyến. Cao.
- Điều 38: trong 5 năm, doanh nghiệp nhỏ và doanh nghiệp khởi nghiệp được tự chọn có lập hồ sơ đánh giá tác động và hồ sơ chuyển dữ liệu ra nước ngoài hay không. Ưu đãi mất nếu xử lý dữ liệu nhạy cảm hoặc dữ liệu của "số lượng lớn" chủ thể. **Chưa tìm được ngưỡng "số lượng lớn".**
- Mua bán dữ liệu cá nhân: phạt gấp 10 lần khoản thu trái phép hoặc 3 tỷ đồng, tùy mức nào cao hơn. Vi phạm chuyển dữ liệu xuyên biên giới: tới 5% doanh thu. Bài của một hãng luật [59], TB–cao.
- Gửi CV hoặc hợp đồng cho API LLM ở nước ngoài là chuyển dữ liệu xuyên biên giới [59].
- Phụ lục ghi nguồn [59] còn đụng Điều 25 về tuyển dụng. Phần tường thuật **không nêu nội dung Điều 25**. Digest không suy ra nghĩa của điều đó.

Luật AI 134/2025, hiệu lực 01/3/2026 [61], cao. Quyết định 33/2026/QĐ-TTg: AI rủi ro cao gồm giáo dục, dân tộc–tôn giáo, y tế, ngân hàng, tố tụng, giao thông. **Không có tuyển dụng hay nhân sự** [60], cao. AI dùng cho giáo dục thuộc nhóm rủi ro cao. Mục 7 của báo cáo nói định vị "định hướng và học kỹ năng IT" phải chịu nghĩa vụ AI rủi ro cao trong giáo dục **từ 9/2027** [60], đổi lại né giấy phép dịch vụ việc làm. Định vị "tuyển dụng" thì cần giấy phép. Báo cáo gọi đây là lựa chọn chiến lược, không có phương án tối ưu sẵn.

### 4.3 Niềm tin, đánh giá ẩn danh, tư vấn pháp lý

- Nghị định 147/2024: xác thực tài khoản bằng số điện thoại Việt Nam; gỡ nội dung vi phạm trong 24 giờ kể từ khi cơ quan yêu cầu. Báo cáo mới có tổng hợp báo chí, **chưa đọc điều khoản gốc**, TB [62].
- reviewcongty bị chặn 19/6/2023 [40][41], cao.
- Luật Luật sư, Điều 32: hành nghề luật sư qua văn phòng hoặc công ty luật [67], thấp–TB, tổng hợp, chưa đọc văn bản gốc. Nghị định 77/2008 về tư vấn pháp luật còn hiệu lực một phần [78], TB. Không tìm thấy quy định riêng cho AI.

### 4.4 Dữ liệu và cào — ràng buộc phạm vi

- Mọi màn prototype phụ thuộc một nguồn báo cáo đặt trong ngoặc: "[NGUỒN DỮ LIỆU TUYỂN DỤNG]". Báo cáo kết luận lợi thế cạnh tranh thật nằm ở dữ liệu, và Hải Đồ IT chưa có dữ liệu.
- ITviec chỉ thu khoảng 1,8–2,3 nghìn phản hồi khảo sát lương mỗi năm [8][6]. Báo cáo nói mẫu này quá mỏng để chia phân vị theo vai trò × cấp bậc × thành phố.
- Phân bố nhà tuyển dụng trả lời ITviec, H1/2024: TP.HCM 76,7%, Hà Nội 21,4%, Đà Nẵng 1,9% [6]. Một nguồn, sàn việc làm, có thể thiên lệch. Các thành phố nhỏ có rất ít dữ liệu.
- Crawl dữ liệu từ sàn khác: rủi ro quyền tác giả đối với cơ sở dữ liệu và vi phạm điều khoản sử dụng. **Chưa có án lệ** (khuyến nghị R5). Dữ liệu cộng đồng đóng góp vướng tiền lệ reviewcongty và Nghị định 147.
- **Khuyến nghị R5**, độ tin cậy cao về việc phải giải trước khi viết code: chọn một trong ba — đối tác dữ liệu (sàn, trường), dữ liệu công khai đã tổng hợp, hoặc đóng góp kiểu "góp lương để xem lương". Bản đồ thành phố chỉ hiện nơi đủ mẫu.
- **Khuyến nghị R6**, cao: ẩn danh trước khi gọi LLM, che CCCD và số tài khoản trong hợp đồng, không theo dõi hành vi người dùng, để giữ ưu đãi 5 năm của Điều 38.
- Lộ trình thật (hồ sơ ẩn danh): báo cáo ghi rủi ro nhận diện lại ở công ty nhỏ là **suy luận**. Prototype đang đặt ngưỡng k-ẩn danh n ≥ 20.

### 4.5 Mức rủi ro báo cáo gán cho từng màn

Cột "cách giảm" là **khuyến nghị** của báo cáo, không phải kết luận rằng cách đó đã được luật chấp nhận.

| Màn / hoạt động | Mức rủi ro báo cáo gán | Căn cứ | Cách giảm báo cáo đề xuất |
|---|---|---|---|
| Ghép việc, tin "vừa mở khóa", gợi ý tin tuyển | Cao — dịch vụ việc làm, cần giấy phép | [56][75] | Hoãn; hoặc chỉ dẫn link sang sàn gốc; hoặc hợp tác với doanh nghiệp đã có phép; hoặc xin phép (ký quỹ 300 triệu) |
| Bản đồ nhu cầu, lương thời gian thực | TB–cao — "thông tin thị trường lao động" theo câu chữ luật | [56] | Trình bày như báo cáo hoặc nghiên cứu tổng hợp; xin ý kiến pháp lý |
| Chỉ số phản hồi nhà tuyển dụng (đóng góp ẩn danh) | Cao | [40][41][62] | Chỉ số liệu tổng hợp; xác thực số điện thoại; kiểm duyệt; gỡ trong 24 giờ; không nêu tên cá nhân |
| Agent pháp lý đọc hợp đồng, nếu thu phí và gọi là tư vấn | Cao | [67][78] | Định vị là thông tin pháp lý / danh sách kiểm tra; che ảnh CCCD và số tài khoản; giới thiệu sang luật sư |
| Hộ chiếu kỹ năng (review repo), lưu CV | TB | [57][58] | Xin đồng ý; thu tối thiểu; ẩn danh trước khi gọi LLM |
| Lộ trình thật | TB | Suy luận về nhận diện lại | Ngưỡng k-ẩn danh, prototype đang đặt n ≥ 20 |
| So sánh offer, máy tính net, tập thương lượng | Thấp | [60] | Miễn trừ trách nhiệm; không khai thuế thay người dùng |

**Khuyến nghị R4**, độ tin cậy cao: hoãn ghép việc, tin "vừa mở khóa", chỉ số phản hồi nhà tuyển dụng, agent pháp lý thu phí cho đến khi có giấy phép hoặc ý kiến pháp lý.

---

## 5. Sự kiện nếu sai thì phạm vi đổi

Chỉ những câu mà phạm vi PRD phải đổi nếu câu đó không đứng. Độ tin cậy là của báo cáo.

| # | Sự kiện | Nếu sai thì phạm vi đổi thế nào | Độ tin cậy |
|---|---|---|---|
| 1 | Cửa fresher đang hẹp vì AI: tuyển &lt;1 năm giảm 13% và chiếm 45% ca cắt giảm [13]; 20,2% doanh nghiệp năm 2025, dự báo 34,3% năm 2026, không tuyển thêm vì năng suất AI [11] | Nếu đây là toàn thị trường nói chung hoặc dự báo không xảy ra, persona lõi "fresher mất hướng trước AI" yếu đi. Red team: tin IT trên ITviec vẫn tăng, nên nỗi đau có thể là "chọn hướng nào" | [13] TB–cao; [11] TB–cao; 34,3% là dự báo |
| 2 | 40,9% định nghỉ trong 12 tháng (ITviec, n=2.324) và 54,5% đang tìm việc (JobsGO). Dùng khoảng 41–55% | Nếu hai khảo sát thiên về người đã ở trên sàn việc làm, tập người dùng web hướng nghiệp nhỏ hơn khoảng báo cáo suy ra (200–300 nghìn là suy luận) | TB–cao cho từng số; suy luận cho quy mô tuyệt đối |
| 3 | Người làm phần mềm/IT có việc khoảng 480 nghìn (2022) đến 560 nghìn (2024), chỉ TopDev [3]. 1,2–1,5 triệu là toàn ngành ICT, gồm phần cứng và điện tử [1][2]. 1,5 triệu GitHub là tài khoản, không phải người đi làm [5] | Dùng nhầm 1,2–1,5 triệu làm tập người dùng sẽ phóng thị trường. Số 480–560 nghìn **chưa xác minh**, một nguồn | [3] TB–thấp, chưa xác minh; [1] TB; [2] thấp |
| 4 | Nhu cầu tuyển IT không sụp: trên ITviec, tin IT Q1/2025 +12%, AI/ML +41%, tìm "AI" +89%, Q2/2025 +7% [9][10]. JobOKO: 581.660 tin, 10 tháng đầu 2025, toàn thị trường +2,05% [12] | Nếu nhu cầu IT thực sự giảm mạnh, sản phẩm dịch từ "chọn hướng" sang "không có việc". Câu "tin IT −16,92%" **không có trên trang gốc**, chưa xác minh — không dùng để thu hẹp hay mở phạm vi | [9] cao cho riêng ITviec, thấp cho toàn quốc; [12] TB |
| 5 | Địa lý lệch: trong nhà tuyển dụng trả lời ITviec, TP.HCM 76,7%, Hà Nội 21,4%, Đà Nẵng 1,9% (H1/2024) [6]. Thành phố nhỏ rất ít dữ liệu. Mẫu lương khoảng 1,8–2,3 nghìn/năm quá mỏng để chia phân vị vai trò × cấp × thành phố | Nếu đứng: bản đồ nhiều thành phố và lương phân vị ở thành phố nhỏ không có mẫu để hiện. Nếu có bộ dữ liệu dày hơn: các màn đó mở lại được. Báo cáo không đo bảy thành phố cụ thể | [6] một nguồn, thiên lệch sàn; kết luận "mẫu mỏng" là của báo cáo, độ tin cậy cao ở khuyến nghị R5 |
| 6 | Điều 27 coi cung cấp thông tin thị trường lao động, kể cả lương, là dịch vụ việc làm cần giấy phép; không thấy miễn trừ cho bản miễn phí | Nếu luật sư kết luận thông tin tổng hợp miễn phí nằm ngoài giấy phép, bản đồ nhu cầu và tra lương hạ từ rủi ro TB–cao. Nếu câu chữ được áp đúng, các màn đó cần phép (ký quỹ 300 triệu) hoặc cách trình bày khác. Rủi ro thực tế báo cáo ghi là chưa rõ | Cao cho câu chữ luật; thực thi chưa rõ |
| 7 | Định vị "học kỹ năng / lộ trình" đụng AI rủi ro cao lĩnh vực giáo dục từ 9/2027; tuyển dụng không nằm trong danh mục rủi ro cao [60] | Nếu mốc hoặc cách đọc này sai, đánh đổi "né giấy phép việc làm / nhận nghĩa vụ AI giáo dục" đổi theo | Danh mục [60] cao; mốc 9/2027 là câu ở mục 7 của báo cáo |
| 8 | 43,1% người lao động đóng BHXH thấp hơn thu nhập thực [18], không có cắt riêng cho IT | Nếu dân IT đóng khác nhóm này, móc miễn phí "so sánh offer + kiểm tra BHXH" yếu đi | TB, một nguồn (Navigos / VietnamWorks) |
| 9 | Chưa có bằng chứng dân IT Việt Nam trả phí định kỳ cho công cụ nghề nghiệp. Khoản đã thấy chỉ là giá lẻ TopCV | Nếu phỏng vấn và thử giá cho thấy có thuê bao, mô hình thu tiền trong PRD đổi. Hiện không được ghi thành giả định đã chứng minh | Không tìm được dữ liệu — xem mục 6 |
| 10 | Ghost, tin ảo, soát hợp đồng: bằng chứng Việt Nam yếu hoặc không đặc thù IT. GhostJob doanh thu 0 | Nếu đo lại thấy ghost và tin treo phổ biến trong IT Việt Nam, các màn đang bị xếp hoãn có căn cứ sản phẩm mạnh hơn. Với dữ liệu hiện tại, báo cáo không lấy chúng làm điểm thu tiền | Ghost VN thấp–TB, chưa xác minh; lừa đảo việc làm cao theo hướng yếu hơn kỳ vọng; hợp đồng cao về pháp lý nhưng nhu cầu IT yếu |
| 11 | Nhật / BrSE: khoảng 6.000 kỹ sư Việt tại Nhật, hơn 300 doanh nghiệp Việt phục vụ thị trường Nhật [17], TB, không nêu phương pháp. TopCV xếp BrSE khó tuyển thứ 2, 9,92% [14] | **Khuyến nghị R7:** chỉ làm dạng nội dung, ưu tiên thấp. Nếu số 6.000 là thiếu nhiều, vẫn chưa đủ để mở thành màn sản phẩm — báo cáo không có nhu cầu ứng viên cho màn này | TB |

Số bị loại, không được đưa vào phạm vi: "60% lao động IT bị sa thải chưa có việc sau 1 năm" [15], không nêu phương pháp, nhóm sa thải 2023, độ tin cậy thấp. Số BHXH "0,12% đóng trên toàn bộ thu nhập" là **đọc nhầm vòng 1**; số đúng của Navigos là 38,3% đóng trên toàn bộ lương gross [18].

---

## 6. Không tìm thấy, và cảnh báo red team

### Câu hỏi báo cáo để ngỏ

1. Ứng viên IT có trả thuê bao định kỳ không, và ở mức nào. Không có dữ liệu.
2. Điều 27 có áp dụng cho thông tin miễn phí không. Không thấy điều khoản miễn trừ. Chưa đọc hết Nghị định 352.
3. CAC/CPI Việt Nam cho app giáo dục và nghề nghiệp. Báo cáo AppsFlyer và Adjust bị khóa.
4. Số lập trình viên đang đi làm hiện nay, cần hai nguồn độc lập. Hiện chỉ TopDev [3].
5. Doanh thu TopCV, Navigos, ITviec.
6. Tỷ lệ ghosting và số tin treo tại Việt Nam. Mới một nguồn từ nhà cung cấp [21].
7. TopCV đã có giấy phép dịch vụ việc làm chưa; Pro/Premium thời hạn bao lâu và gồm những gì [27].
8. Câu "hơn 70% muốn có lộ trình, chỉ 1/3 thấy công ty đáp ứng" cần nguồn thứ hai, và cần tách câu hỏi lộ trình khỏi câu hỏi môi trường [7].

### Cảnh báo khác trong báo cáo

- Bảy nhận định chưa xác minh, một nhận định bị lật (BHXH). Độ tin cậy tổng **TB**.
- "Nỗi đau mạnh" không suy ra sẵn lòng trả cho cố vấn AI.
- Khoảng trống "chưa thấy sản phẩm nào kết hợp dữ liệu thị trường + cố vấn đa agent" không suy ra có nhu cầu.
- ChatGPT và Gemini miễn phí đã là phương án thay thế. 47% Gen Z **ở Mỹ** cho rằng ChatGPT tư vấn nghề tốt hơn sếp (đoạn trích, 2023, thấp–TB) [79]. Không phải số Việt Nam.
- Ứng dụng tự hướng dẫn ở lĩnh vực lân cận giữ chân trung vị 2,5–3,5 tuần (JMIR, 2022) [65], TB. Không phải số của sản phẩm hướng nghiệp IT.
- Lập trình viên Việt Nam hay tự kiểm tra kết quả AI (86%) [66], nên cố vấn không trích nguồn yếu về niềm tin.
- Dữ liệu cộng đồng "sẽ đủ dày" bị red team làm yếu, và gần như bị lật với đánh giá nhà tuyển dụng: đã có tiền lệ chặn [41]; đơn vị dẫn đầu cũng chỉ khoảng 2 nghìn phản hồi lương mỗi năm [8].
- Một số mốc đã quá hạn độ mới của chính báo cáo và cần cập nhật trước khi biến thành yêu cầu: số lập trình viên [3], tin ITviec Q1/2025 [9], Coursera VN [30], Edupia [31], LinkedIn Premium [42]. Giá và tính năng TopCV, ELSA, Levels.fyi được báo cáo hẹn kiểm tra lại từ 2027-01. Quy tắc độ mới của báo cáo: quy mô/tăng trưởng 18 tháng, giá và tính năng 3 tháng, hành vi 24 tháng, quy mô người dùng và doanh thu đối thủ 12 tháng, pháp lý 36 tháng.
- Báo cáo kết luận **nên theo đuổi nhưng không làm cả 11 màn**, độ tin cậy TB, và ghi bước kiểm chứng (phỏng vấn, thử giá, luật sư) **trước khi viết PRD**. Digest này không biến kết luận đó thành quyết định phạm vi.

### Việc digest cố ý không kết luận

Báo cáo không đo nhu cầu theo từng thành phố ngoài ba tỷ lệ nhà tuyển dụng của ITviec. Báo cáo không chứng minh một mức giá nào của Hải Đồ IT. Báo cáo không có CAC. Báo cáo không kết luận bản đồ nhu cầu miễn phí có cần giấy phép hay không — chỉ kết luận câu chữ luật bao hàm việc cung cấp thông tin thị trường lao động, kể cả lương, và rủi ro thực tế chưa rõ.
