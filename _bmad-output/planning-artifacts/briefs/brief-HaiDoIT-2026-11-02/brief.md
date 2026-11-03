---
title: "Product Brief: Hải Đồ IT"
status: final
created: 2026-11-02
updated: 2026-11-03
---

# Product Brief: Hải Đồ IT

## Tóm tắt

Hải Đồ IT là ứng dụng web giúp sinh viên IT năm cuối và fresher ở Việt Nam đọc thị trường tuyển dụng bằng số liệu thay vì lời đồn. Hệ thống thu thập tin tuyển dụng IT hằng ngày từ nhiều nguồn, loại tin trùng lặp và chuẩn hóa kỹ năng. Nhờ đó, nó trả lời được câu hỏi mà chưa công cụ nào trả lời: *"Kỹ năng này xuất hiện trong bao nhiêu phần trăm tin tuyển dụng cùng vai trò ở Việt Nam?"*

Sản phẩm có bốn chức năng:
- **Cố vấn:** lộ trình học dựng từ dữ liệu thị trường, cá nhân hóa theo CV;
- **Soi tin:** đặt một tin tuyển dụng cạnh hồ sơ người dùng và cạnh mặt bằng thị trường;
- **Bản đồ nhu cầu:** bản đồ 3D theo thành phố và vai trò;
- **Insights:** nhận định do code tính, chỉ hiện khi đủ mẫu.

Đây là đồ án SEP490 của nhóm 3 người, làm trong 8 tuần (2/11–27/12/2026) nhưng thiết kế theo chuẩn một sản phẩm thật. Thành công được đo bằng độ chính xác của hệ thống và bằng thử nghiệm trước–sau với 30–50 người dùng.

## Vấn đề

Mỗi tuần, sinh viên IT năm cuối và fresher đọc hàng chục JD (bản mô tả công việc trong tin tuyển dụng) mà không có thước đo nào. Mỗi công ty mô tả cùng một vai trò theo một kiểu, nên người đọc không phân biệt được kỹ năng nào là **cốt lõi của thị trường**, kỹ năng nào chỉ là **yêu cầu riêng của một công ty**. Kết quả là họ học theo lời đồn, rải một bản CV cho mọi nơi, hỏi nhóm Facebook, và nhờ ChatGPT sửa câu chữ trong CV mà không có dữ liệu để đối chiếu.

Sai lầm này ngày càng đắt vì thị trường đang phân hóa. Năm 2025, tin tuyển người dưới 1 năm kinh nghiệm giảm 13% (JobOKO), còn tin AI/ML tăng 41% (ITviec).

Các nguồn hiện có không lấp được khoảng trống:
- báo cáo thị trường hằng năm phải điền form mới tải được và chỉ có số liệu tổng quát;
- dữ liệu tin tuyển dụng nằm riêng ở từng sàn;
- AI của các sàn phục vụ nhà tuyển dụng;
- chatbot đa dụng không thống kê được trên tin tuyển dụng Việt Nam.

**Giả thuyết cần kiểm chứng: "thiếu kỹ năng cốt lõi".** Một bạn học Java Backend vững nộp 20 CV mà không được gọi phỏng vấn. Nhóm cho rằng việc thiếu kỹ năng cốt lõi mà JD yêu cầu, hoặc có kỹ năng nhưng CV không thể hiện, là **một** nguyên nhân đáng kể khiến CV của fresher bị loại. Các nguyên nhân khác cũng có thật: thị trường fresher co hẹp, dự án cá nhân còn yếu. Đợt thử nghiệm người dùng được thiết kế để kiểm chứng giả thuyết này.

## Người dùng

Người dùng chính:
- sinh viên IT năm 3 và năm cuối đang chuẩn bị thực tập (OJT) hoặc tốt nghiệp;
- fresher/junior có 0–2 năm kinh nghiệm, kể cả người muốn chuyển nhánh (ví dụ từ Backend sang Data).

v1 chỉ phục vụ người tìm việc.

**Minh, 22 tuổi, sinh viên Kỹ thuật Phần mềm năm cuối, hướng Java Backend.**
- *Hiện tại:* Minh đã có Java, Spring Boot và MySQL. Đọc 15 JD xong, Minh thấy ngợp vì không biết Docker, Kafka hay AWS là bắt buộc hay chỉ là điểm cộng.
- *Minh cần biết:*
  - những kỹ năng cốt lõi nào còn thiếu, kèm tỷ lệ xuất hiện thật trên thị trường;
  - nên học theo thứ tự nào, với tài liệu miễn phí nào;
  - với một JD cụ thể, mình khớp đến đâu.
- *Thành công với Minh:* rời Hải Đồ IT với một lộ trình học theo chặng dựa trên dữ liệu, và đủ dữ kiện để tự quyết JD nào đáng nộp. Hệ thống không gợi ý số tuần học, cũng không khuyên nộp hay không nộp.

## Giải pháp

Hệ thống có hai lớp nền:
- **pipeline thu thập hằng ngày:** loại tin trùng lặp, chuẩn hóa kỹ năng và lương, lưu vòng đời của từng tin;
- **mô-đun trích xuất kỹ năng dùng chung:** đọc một JD hoặc một CV và trả về danh sách kỹ năng đã chuẩn hóa.

Bốn chức năng được xây trên hai lớp nền đó.

**1. Cố vấn.**
- **Giao diện:** lộ trình học dạng đồ thị nút, tham khảo roadmap.sh.
- **Hồ sơ kỹ năng:** tập kỹ năng người dùng đã có, tạo từ CV **hoặc** tự chọn trên đồ thị, lưu trong trình duyệt. Cố vấn và Soi tin dùng chung hồ sơ này.
- **Hồ sơ trống:** người dùng nhận lộ trình học chung cho vai trò mục tiêu. Mỗi nút ghi tỷ lệ tin có kỹ năng đó.
- **Hồ sơ có dữ liệu:** hệ thống đánh dấu kỹ năng đã có và sắp xếp phần còn thiếu. Mỗi khoảng trống có ba lựa chọn: "Tôi chưa biết", "Tôi đã biết, chỉ là CV chưa ghi", và "CV của tôi có ghi rồi (hệ thống đọc sót)".
- **Kỹ năng nền tảng:** kỹ năng dưới ngưỡng vẫn vào lộ trình nếu là điều kiện tiên quyết của một khoảng trống (ví dụ Linux cần cho Docker), và được gắn nhãn riêng.
- **Tài liệu:** mỗi nút kèm tài liệu và khóa học miễn phí, lấy từ danh mục đã kiểm duyệt.
- **Cách dựng:** khung lộ trình học do thuật toán dựng:
  - đồ thị "học trước – học sau" quyết định **thứ tự học**;
  - tần suất trên thị trường quyết định **mức ưu tiên**.

  LLM chỉ viết lời dẫn cho khung đã dựng.

**2. Soi tin.** Người dùng dán một JD và nhận hai góc nhìn. Hệ thống tự nhận diện vai trò và cấp bậc của tin; người dùng đổi lại được.
- **So với hồ sơ:** hiển thị **mức khớp** có trọng số (cốt lõi 3, thường gặp 2, riêng của công ty 1), kèm một dòng đếm thô theo nhóm. Mỗi kỹ năng còn thiếu được xếp vào một trong ba nhóm:
  - **cốt lõi:** có trong từ 30% số tin cùng vai trò và cấp bậc trở lên;
  - **thường gặp:** 10–30%;
  - **riêng của công ty này:** dưới 10%, chỉ cần học nếu nhắm đúng công ty đó.

  Kỹ năng không có trong bộ từ vựng được hiển thị riêng là **kỹ năng chưa nhận diện** và không tính vào mức khớp.

  Các ngưỡng này là tham số. Sprint 2 sẽ hiệu chỉnh trên dữ liệu thật để mỗi vai trò mục tiêu có ít nhất 3 kỹ năng cốt lõi (mục tiêu 3–5), rồi đóng băng trước đợt thử nghiệm. Lý do: với ngưỡng 50%, nhóm cốt lõi gần như rỗng. Vai trò được chia theo nhánh công nghệ khi đủ từ 30 tin trở lên (ví dụ Java Backend).
- **So với thị trường:**
  - phân vị của số kỹ năng yêu cầu, số năm kinh nghiệm và mức lương. Hai cái sau chỉ hiển thị khi ô thống kê có từ 30 tin có trường đó trở lên;
  - **chất lượng JD:** danh sách kiểm tra đạt/không đạt (có lương, có tên công ty, có mô tả trách nhiệm, có phúc lợi, chức danh nhất quán với cấp bậc và kỹ năng);
  - các **dấu hiệu cần kiểm tra** (7 dấu hiệu): yêu cầu dàn trải, tỷ lệ kỹ năng riêng cao, yêu cầu cao nhưng lương thấp, tin đăng lại nhiều lần, kênh liên hệ bất thường, đòi tiền trước, không rõ công ty. Đây là gợi ý để người dùng tự xác minh, không phải phán quyết tin thật hay giả, và giao diện ghi rõ đa số tin bị gắn dấu hiệu vẫn là tin thật. Việc tin không ghi lương **không** phải một dấu hiệu, vì khoảng 76% tin không ghi lương.

**Cấp bậc.** Mọi so sánh đều tính trên **ô thống kê = vai trò mục tiêu × cấp bậc** (Intern/Fresher/Junior 0–2 năm, Mid, Senior trở lên). Nếu ô đó dưới 30 tin, hệ thống quay về tập rộng hơn theo thứ tự **giữ cấp bậc trước, giữ nhánh sau**, và luôn ghi rõ cỡ mẫu cùng cơ cấu cấp bậc của tập đang dùng. Chiều thành phố chỉ dùng cho Bản đồ và Insights.

**3. Bản đồ nhu cầu.** Bản đồ 3D của Việt Nam. Chiều cao cột thể hiện **tỷ trọng và thứ hạng**, không phải số tin tuyệt đối. Bấm vào một thành phố để xem bảng chi tiết.

**4. Insights.**
- **Nội dung:** nhận định cắt ngang do code tính:
  - cửa vào cho người mới;
  - bộ kỹ năng hay đi cùng nhau;
  - kỹ năng tăng dần từ Junior lên Senior;
  - khác biệt giữa các thành phố;
  - ngành nổi bật.
- **Ngưỡng hiển thị:** chỉ hiện khi đủ 30 mẫu trở lên.
- **Câu kết luận:** dùng mẫu câu cố định, điền số liệu đã tính; không dùng LLM.

**Nguyên tắc chung:** mọi con số đi kèm cỡ mẫu, nguồn và ngày. Thiếu dữ liệu thì nói thiếu, không đoán.

## Điểm khác biệt

Hội đồng sẽ hỏi: *"Sao không dán CV và JD vào ChatGPT cho xong?"*

**1. So với toàn bộ tin cùng vai trò, không phán đoán trên một văn bản đơn lẻ.**
- **Chatbot:** chỉ so đúng một JD với một CV. Gặp JD đòi 15 công nghệ cho vị trí fresher, nó sẽ khuyên học cả 15.
- **Hải Đồ IT:** đặt JD đó cạnh hàng trăm tin cùng vai trò và trả lời bằng tỷ lệ.
- **Bằng chứng:** một nghiên cứu tại AIES 2026 (165.000 câu trả lời của 11 mô hình) cho thấy gợi ý nghề của chatbot bám theo nội dung blog hơn là theo cấu trúc thị trường thật.

**2. Lộ trình học tất định (cùng đầu vào luôn cho cùng kết quả).**
- **Chatbot:** mỗi lần hỏi lại sinh ra một lộ trình khác.
- **Hải Đồ IT:** sắp xếp topo trên đồ thị "học trước – học sau", nên LLM không thể bịa ra thứ tự học.
- **Kiểm duyệt đồ thị:** đồ thị được soạn từ tài liệu chính thức, rồi giảng viên hướng dẫn rà soát.

**3. Trung lập.** Các sàn sống bằng tiền của nhà tuyển dụng, nên khó gắn nhãn "yêu cầu cao bất thường" lên tin của chính khách hàng đang trả tiền.

**Lợi thế nằm ở đâu.** Lợi thế không nằm ở mô hình AI hay crawler: scraper thương mại cho các sàn Việt Nam đã có sẵn trên thị trường. Thứ người khác không có sẵn là:
- bộ từ vựng kỹ năng song ngữ Việt–Anh có độ chính xác được đo;
- đồ thị "học trước – học sau" đã được kiểm duyệt;
- chuỗi snapshot lịch sử tích lũy theo từng ngày, tức lịch sử dữ liệu không mua được.

## Tiêu chí thành công

**Hệ thống** (phương pháp đo chi tiết ở addendum §4):

| Tiêu chí | Ngưỡng |
|---|---|
| Pipeline | ≥ 95% lượt chạy hằng đêm thành công trong ≥ 4 tuần; ≥ 25 snapshot; ≥ 1.500 tin mới `[GIẢ ĐỊNH]` |
| Loại tin trùng lặp | Báo cáo precision/recall trên khoảng 100 cặp tin có độ giống nhau cao; tỷ lệ trùng còn sót < 5% |
| Trích xuất kỹ năng | Precision ≥ 85%, Recall ≥ 80% trên 200 JD gán nhãn tay; báo cáo Cohen's kappa giữa 2 người gán nhãn |
| Lộ trình học | Kiểm thử tự động xác nhận 100% lộ trình đúng thứ tự topo; rà soát một mẫu lời dẫn do LLM viết |
| Hiệu năng | Từ lúc tải CV đến lúc có lộ trình học: < 15 giây |

**Người dùng.** Mẫu thử gồm 30–50 người: khoảng 60% là sinh viên trong trường, khoảng 40% là người ngoài trường. Mỗi người dùng thử trong một phiên khoảng 15 phút. Phần khảo sát nằm **ngay trong ứng dụng**, ở chế độ thử nghiệm bật bằng link riêng, và **ẩn danh tuyệt đối**: không thu thông tin liên hệ, không hỏi lại sau phiên. Mọi chỉ số dưới đây được báo cáo cả ở dạng tổng và dạng tách theo nhóm trong trường / ngoài trường.

| Chỉ số | Ngưỡng |
|---|---|
| Phát hiện điểm mù: tìm ra ít nhất 1 kỹ năng cốt lõi **hoặc thường gặp** không nằm trong 3 kỹ năng người thử tự đoán trước phiên, và người thử xác nhận "Tôi chưa biết" | ≥ 70% |
| Có ý định sửa CV hoặc đổi thứ tự học | ≥ 60% |
| Khi so sánh mù trên một tình huống mẫu cố định, đặt cạnh câu trả lời ChatGPT soạn sẵn: điểm trung bình, và tỷ lệ chọn Hải Đồ IT | ≥ 4,0/5 và được chọn nhiều hơn (kiểm định nhị thức, p < 0,05) |
| Tỷ lệ bỏ sót kỹ năng đã có khi viết CV | chỉ số mô tả, không đặt ngưỡng |
| Độ rõ ràng về kỹ năng cần học: một câu tự đánh giá 1–5, hỏi giống nhau ở đầu và cuối phiên | điểm sau cao hơn điểm trước, kiểm định Wilcoxon, p < 0,05 |

**Thực nghiệm đối chứng.** Hỏi cùng một câu về lộ trình học nhiều lần trên 2–3 chatbot phổ biến, đo độ lệch thứ tự học. Kết quả đặt cạnh số đo tất định của Hải Đồ IT.

**Giới hạn đã biết:**
- người thử phần lớn là sinh viên cùng một trường và quen nhóm phát triển;
- 2 tuần chỉ đo được nhận thức và ý định, chưa đo được kết quả xin việc thật;
- phần so sánh mù chỉ dùng một tình huống mẫu cho mỗi vai trò và một câu trả lời ChatGPT soạn sẵn.

## Phạm vi

**Có trong v1:** bảy nhóm tính năng, gồm 4 chức năng người dùng thấy, cộng ba lớp nền: thu thập và chuẩn hóa dữ liệu, hồ sơ kỹ năng, và chế độ thử nghiệm trong ứng dụng.
- Giao diện tiếng Việt.
- Web ưu tiên máy tính. Trên điện thoại: Soi tin đầy đủ, Cố vấn dạng thẻ, Bản đồ dạng danh sách thành phố, Insights xếp dọc, chế độ thử nghiệm chạy đầy đủ. Bắt buộc có chế độ 2D hoặc dạng bảng thay cho bản đồ 3D.
- 4–5 vai trò khi công khai; bản đồ gồm Hà Nội, TP.HCM, Đà Nẵng và "Khác".
- CV dạng PDF hoặc DOCX, chỉ xử lý khi người dùng đồng ý, không lưu file gốc. Hồ sơ kỹ năng cũng tạo được bằng cách tự chọn, không cần CV.
- Không cần tài khoản: kết quả lưu ở trình duyệt, có link chia sẻ và có thể tải về. Server chỉ ghi sự kiện ẩn danh theo mã phiên, không chứa nội dung CV hay JD, và điều này được nêu trong ô đồng ý.
- Dữ liệu từ các nguồn công khai, thu thập không đăng nhập (ngoại lệ: xem *Rủi ro đã chấp nhận*).

**Không có trong v1:**
- xu hướng theo thời gian và dự báo;
- kết luận về tin bất thường;
- viết lại câu chữ CV;
- kênh để người dùng gửi mức lương;
- extension trình duyệt;
- tài khoản người dùng, và trạng thái "đang học" trong hồ sơ kỹ năng;
- ước lượng số tuần học cho từng kỹ năng;
- so sánh song song hai thành phố trên bản đồ;
- OCR cho CV dạng ảnh scan;
- hỏi lại người thử sau phiên thử nghiệm;
- thu thập mới từ LinkedIn (dữ liệu LinkedIn lịch sử vẫn dùng, xem *Rủi ro đã chấp nhận*);
- tính năng cho nhà trường hoặc nhà tuyển dụng;
- ứng dụng di động.

## Ràng buộc và rủi ro

**Rủi ro đã chấp nhận.** Nhóm đã cân nhắc và chấp nhận có chủ đích bốn rủi ro dưới đây. Chúng là ngoại lệ đối với nguyên tắc thu thập ở mục Pháp lý. Chi tiết và hệ quả ở PRD §6.1; nhóm cần chuẩn bị câu trả lời cho từng mục nếu hội đồng hỏi.

| # | Rủi ro | Phạm vi | Mức rủi ro |
|---|---|---|---|
| R1 | Crawler TopCV kế thừa dùng kỹ thuật né phát hiện bot. TopCV chiếm khoảng 38% dữ liệu nền | Chạy cả trên bản công khai. Nhóm xin phép TopCV, và bỏ kỹ thuật này khi thương mại hóa | **Rất cao**, có thể rơi vào Điều 289 Bộ luật Hình sự |
| R2 | Các crawler và bước pipeline kế thừa khác dùng cùng kỹ thuật: ITviec, TopDev, và bước lấy mô tả đầy đủ | Như R1 | **Rất cao** |
| R3 | 625 tin LinkedIn trong dữ liệu nền được thu bằng tài khoản đăng nhập | Vẫn tính vào số liệu công khai. v1 không thu thập mới từ LinkedIn | **Rất cao** |
| R4 | 555 tin ITviec trong dữ liệu nền, trong khi điều khoản ITviec cấm thu thập khi chưa có đồng ý bằng văn bản | Vẫn tính vào số liệu công khai trong lúc chờ xin phép | **Trung bình–cao** |

Nếu loại R3 và R4 ra khỏi số liệu công khai thì còn 2.289 tin, trong đó Backend còn 184 tin.

**Thời gian.**
- Nguồn lực: 3 người × 8 tuần.
- Review giữa kỳ khoảng 22–28/11: cần luồng CV → lộ trình học chạy thật cho Backend và Data/AI.
- Nộp báo cáo khoảng 20–25/12.
- Kế hoạch sprint chi tiết: addendum §1.

**Yêu cầu học thuật.** Độ phức tạp kỹ thuật được chứng minh bằng những bài toán khó, được giải đúng và đo được:
- loại tin trùng lặp giữa các sàn (đo bằng precision/recall);
- chuẩn hóa kỹ năng song ngữ Việt–Anh (đo tách riêng cho nhóm kỹ năng viết bằng tiếng Việt);
- tính phân vị khi mẫu thưa (ngưỡng cộng thứ tự quay về giữ cấp bậc, kèm khoảng tin cậy bootstrap; đo bằng thí nghiệm làm thưa mẫu);
- dựng lộ trình học tất định (đo bằng kiểm thử lặp lại, đặt cạnh độ nhất quán của chatbot).

Không chứng minh bằng số lượng công nghệ sử dụng.

**Pháp lý.**
- **CV:** chỉ xử lý khi người dùng đồng ý, theo Luật Bảo vệ dữ liệu cá nhân 91/2025.
- **Thông tin cá nhân của người đăng tin:** loại bỏ ngay lúc thu thập.
- **Nguyên tắc thu thập:** tôn trọng `robots.txt` và điều khoản của từng sàn, gửi User-Agent có thông tin liên hệ, không đăng nhập, không né cơ chế chống bot (ngoại lệ: R1–R4 ở trên).
- **Công bố:** chỉ công bố số liệu tổng hợp và các trường ngắn (chức danh, công ty, thành phố, khoảng lương), kèm link về tin gốc. Không đăng lại toàn văn JD.
- **Chính sách dữ liệu và kênh gỡ:** có trang chính sách dữ liệu công khai và một kênh để nguồn hoặc nhà tuyển dụng yêu cầu gỡ, xử lý trong 48 giờ. Trang này không đăng chi tiết kỹ thuật thu thập hay bảng R1–R4, nhưng cũng không được khẳng định những điều trái với R1–R4.
- **ITviec:** gửi email xin phép trong tuần 1. Dữ liệu ITviec đã có vẫn dùng trong số liệu công khai (R4).
- **Repo gốc của bộ scraper:** repo không có LICENSE. Nhóm xin phép tác giả trước khi công khai sản phẩm.

**Dữ liệu.** Dữ liệu còn mỏng ở ba chỗ: lương (chỉ khoảng 24% tin có số), một số vai trò, và các thành phố ngoài Hà Nội và TP.HCM. Chi tiết ở addendum §5.

**Chi phí LLM.** Vài USD mỗi ngày nếu dùng mô hình mạnh nhất. Có thể giảm khoảng 40 lần nếu đổi sang mô hình nhỏ, sau khi đã đo chất lượng trên bộ 200 JD.

## Tầm nhìn

Sau ngày bảo vệ, Hải Đồ IT được duy trì như một tiện ích cộng đồng chi phí thấp và là sản phẩm minh chứng năng lực của nhóm.

- **Từ 01/2027:** chạy trên một VPS nhỏ, chi phí mục tiêu dưới 5–10 USD/tháng `[GIẢ ĐỊNH]`, phục vụ miễn phí các khóa đàn em chuẩn bị OJT.
- **Khoảng 03/2027:** khi chuỗi snapshot đủ 3–6 tháng, mở khóa xu hướng kỹ năng theo thời gian và tín hiệu tin bất thường.
- **Nếu số người dùng tăng tự nhiên:**
  - báo cáo theo quý cho bộ phận OJT của các trường;
  - extension Soi tin;
  - kênh để người dùng gửi lương ẩn danh. Đây là tài sản dữ liệu do chính Hải Đồ IT sở hữu.
