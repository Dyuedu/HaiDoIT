---
title: "PRD: Hải Đồ IT"
status: final
created: 2026-11-02
updated: 2026-11-05
---

# PRD: Hải Đồ IT

## 0. Mục đích tài liệu

**Đối tượng đọc:** PRD này dành cho nhóm phát triển (3 người), giảng viên hướng dẫn, và các bước tiếp theo trong quy trình: thiết kế UX, kiến trúc, chia epic và story.

**Nội dung:** tài liệu đặc tả *cái gì* cần xây và *vì sao*, không mô tả *xây bằng gì*. Lựa chọn công nghệ và kế hoạch sprint nằm ở `addendum.md` và ở addendum của product brief.

**Đầu vào:** product brief (`_bmad-output/planning-artifacts/briefs/brief-HaiDoIT-2026-11-02/`), báo cáo nghiên cứu "Hải Đồ IT khoảng trống", prototype, và bộ dữ liệu 3.469 tin.

**Quy ước:**
- mọi thuật ngữ dùng đúng như §3 Bảng thuật ngữ;
- yêu cầu chức năng được đánh số FR-N liên tục trên toàn tài liệu;
- hành trình người dùng được đánh số UJ-N;
- những chỗ suy đoán được gắn nhãn `[GIẢ ĐỊNH]` và gom lại ở §11.

**Nguồn của các con số:** mọi con số trong hành trình là **số minh họa**:
- lấy từ dữ liệu thô của snapshot ngày 26/10/2026 (3.469 tin, gồm cả 625 tin LinkedIn và 555 tin ITviec, xem §6.1);
- tính với ngưỡng khởi tạo cốt lõi ≥ 30% và thường gặp 10–30%;
- chưa qua bước chuẩn hóa kỹ năng, nên vẫn còn những cách viết trùng nhau như "REST API" và "RESTful API".

Các con số sẽ được thay bằng số thật sau khi hiệu chỉnh ngưỡng ở Sprint 2.

## 1. Tầm nhìn

Hải Đồ IT là ứng dụng web giúp sinh viên IT năm cuối và fresher ở Việt Nam đọc thị trường tuyển dụng bằng số liệu thay vì lời đồn. Hệ thống thu thập tin tuyển dụng IT hằng ngày từ nhiều nguồn, loại tin trùng lặp và chuẩn hóa kỹ năng. Nhờ đó, nó trả lời được câu hỏi mà chưa công cụ nào trả lời: *"Kỹ năng này xuất hiện trong bao nhiêu phần trăm tin tuyển dụng cùng vai trò ở Việt Nam?"*

Trên nền dữ liệu đó có bốn chức năng:
- **Bản đồ nhu cầu:** cho thấy thị trường cần gì, ở đâu;
- **Insights:** chỉ ra những điều đáng chú ý trong dữ liệu;
- **Cố vấn:** dựng lộ trình học theo vai trò mục tiêu, cá nhân hóa theo hồ sơ kỹ năng;
- **Soi tin:** đặt một JD cụ thể cạnh hồ sơ của người dùng và cạnh mặt bằng thị trường.

Người chưa mở ứng dụng vẫn đọc được mặt bằng kỹ năng của từng vai trò mục tiêu trên một trang công khai. Trang đó dùng snapshot mà ứng dụng đang hiển thị, trên một ô duy nhất: vai trò đó, mọi cấp bậc, toàn quốc (FR-48).

Hải Đồ IT khác chatbot và các sàn tuyển dụng ở ba điểm:
- mọi con số đi kèm cỡ mẫu, nguồn và ngày của snapshot;
- lộ trình học được dựng tất định trên đồ thị học trước – học sau đã kiểm duyệt; LLM chỉ viết lời dẫn;
- thiếu dữ liệu thì nói thiếu, không đoán.

Đây là đồ án tốt nghiệp SEP490, làm trong 8 tuần (2/11–27/12/2026), nhưng được thiết kế để công khai cho sinh viên dùng thật.

**Sau v1.** Sản phẩm được duy trì như một tiện ích cộng đồng chi phí thấp (trần chi phí ở §6.4). Khoảng tháng 03/2027, khi chuỗi snapshot đủ 3–6 tháng, nhóm mở khóa xu hướng kỹ năng theo thời gian và tín hiệu tin bất thường, hai thứ v1 cố ý gác lại. Nếu số người dùng tăng tự nhiên thì mở tiếp báo cáo theo quý cho bộ phận OJT của các trường, extension Soi tin, và kênh gửi lương ẩn danh.

## 2. Người dùng mục tiêu

### 2.0 Người dùng chính

- Sinh viên IT năm 3 và năm cuối đang chuẩn bị thực tập (OJT) hoặc tốt nghiệp.
- Fresher/junior có 0–2 năm kinh nghiệm, **kể cả người muốn chuyển nhánh** (ví dụ từ Backend sang Data). FR-24 phục vụ riêng nhóm này.

Nhóm 2–5 năm kinh nghiệm dùng được nhưng không phải đối tượng tối ưu: dữ liệu và ví dụ của v1 đều nhắm vào cấp 0–2 năm.

### 2.1 Việc người dùng cần làm

- **Biết thị trường cần gì:** kỹ năng nào là cốt lõi, kỹ năng nào chỉ là yêu cầu riêng của một công ty, cho đúng vai trò và cấp bậc của mình.
- **Biết mình thiếu gì:** đặt hồ sơ kỹ năng của mình (từ CV hoặc tự chọn) cạnh vai trò mục tiêu để thấy khoảng trống kỹ năng.
- **Biết học gì trước:** có lộ trình học theo chặng, kèm tài liệu miễn phí, thay vì học theo lời đồn.
- **Không tự làm yếu CV của mình:** phát hiện những kỹ năng đã có nhưng CV chưa ghi.
- **Quyết định có nộp vào một tin hay không:** biết mình khớp đến đâu, và tin đó có yêu cầu bất thường so với mặt bằng hay không.
- **Chọn hướng đi khi chưa có kinh nghiệm:** so sánh các vai trò bằng dữ liệu, thấy kỹ năng nào dùng được cho cả hai hướng.
- **Về mặt cảm xúc:** bớt hoang mang. Ra quyết định dựa trên con số có nguồn gốc, thay vì dựa trên lời khuyên trái chiều trong các nhóm Facebook.

### 2.2 Ai không phải người dùng của v1

- **Nhà tuyển dụng:** không có tính năng đăng tin, lọc ứng viên, hay mua điểm đánh giá.
- **Nhà trường và trung tâm đào tạo:** báo cáo đối chiếu chương trình học được để dành cho hướng mở rộng sau v1.
- **Người tìm việc ngoài ngành IT.**
- **Người có từ khoảng 5 năm kinh nghiệm trở lên:** họ vẫn dùng được, nhưng sản phẩm không tối ưu cho họ.

### 2.3 Các hành trình chính

- **UJ-1. Minh tìm ra khoảng trống kỹ năng thật của mình và nhận lộ trình học.**
  - **Persona và bối cảnh:** Minh, 22 tuổi, sinh viên Kỹ thuật Phần mềm năm cuối, hướng Java Backend. Đã nộp hơn chục CV trên ITviec và TopCV mà không có phản hồi.
  - **Trạng thái ban đầu:** tối Chủ nhật, dùng laptop. Minh bấm vào link trong bài đăng trên nhóm Facebook "Thực tập sinh & Fresher IT Việt Nam": *"Mình vừa thống kê 3.469 tin tuyển dụng IT tại Việt Nam, trong đó có 378 tin Backend…"*. Minh chưa từng vào Hải Đồ IT và không cần tài khoản.
  - **Diễn biến:**
    1. Trang chủ mở Bản đồ nhu cầu 3D, kèm thanh điều hướng 4 mục: Bản đồ, Insights, Cố vấn, Soi tin.
    2. Minh bấm vào cột Hà Nội. Bảng chi tiết thành phố hiện ra: tỷ trọng các vai trò (Backend có 160 tin ở Hà Nội) và các kỹ năng hàng đầu. Mỗi con số đều ghi cỡ mẫu và ngày cập nhật.
    3. Minh bấm "Xem lộ trình học và đối chiếu CV cho vai trò này" và chuyển sang Cố vấn. Vai trò Backend được chọn sẵn, cấp bậc mặc định là Intern/Fresher/Junior. Minh đổi sang nhánh **Java Backend**.
    4. Ô Java Backend × Intern/Fresher/Junior chỉ có 26 tin, dưới ngưỡng. Cố vấn giữ cấp bậc và quay về **Backend × Intern/Fresher/Junior (n = 52)**, kèm nhãn: "Nhánh Java Backend ở cấp Fresher/Junior hiện có 26 tin (dưới 30), nên tỷ lệ được tính trên 52 tin Backend cùng cấp bậc (32 Junior, 13 Intern, 7 Fresher)."
    5. Minh xem lộ trình học chung dạng đồ thị nút; mỗi nút ghi tỷ lệ tin có kỹ năng đó. Minh đọc ô đồng ý, trong đó nêu rõ văn bản CV được gửi tới một dịch vụ AI bên ngoài để trích kỹ năng và không được lưu lại. Minh tích đồng ý, rồi kéo thả `CV_Minh_JavaBackend.pdf` vào.
    6. Trong khoảng 8–10 giây xử lý, giao diện hiện lần lượt từng bước đang chạy.
  - **Cao trào** (số minh họa):
    - **Có làm nhưng CV không ghi.**
      - **Đã có trong CV:** Java (50%, cốt lõi) và MySQL (25%) được tô xanh.
      - **Khoảng trống thuộc nhóm thường gặp:** PostgreSQL (27%), Microservices (19%), Docker (17%).
      - **Phát hiện của Minh:** trong đồ án kỳ trước, Minh đã tách service, cấu hình Docker và dùng PostgreSQL. Vậy mà CV chỉ ghi đúng một dòng: "Xây dựng backend bằng Java Spring Boot".
      - **Hành động:** Minh bấm **"Tôi đã biết, chỉ là CV chưa ghi"** cho cả ba. Ba kỹ năng chuyển sang "đã có" và vào danh sách "cần bổ sung vào CV".
    - **Thứ thật sự chưa biết.**
      - **Cốt lõi:** hệ thống còn báo SQL (35%) là khoảng trống cốt lõi. Thực ra SQL là thứ Minh dùng hằng ngày, chỉ là CV không ghi chữ "SQL". Minh bấm "Tôi đã biết, chỉ là CV chưa ghi".
      - **Thường gặp:** Minh bấm **"Tôi chưa biết"** cho CI/CD (13%) và Redis (12%).
      - **Kết quả:** lộ trình học được tính lại và xếp phần còn thiếu theo chặng, kèm nhắc rằng nhóm thường gặp nên học sau khi đã nắm các kỹ năng cốt lõi.
    - **Có tài liệu cho từng bước.** Bấm vào một nút, Minh thấy giải thích ngắn vì sao thị trường cần kỹ năng đó, kèm tài liệu miễn phí đã kiểm duyệt.
  - **Kết thúc:** hồ sơ kỹ năng được tự động lưu trong trình duyệt. Minh bấm "Lưu kết quả" để tải về một bản tóm tắt gồm hai phần:
    - các kỹ năng đã có nhưng cần ghi vào CV;
    - lộ trình học theo chặng, kèm link tài liệu.

    Tối đó, Minh sửa lại CV.
  - **Tình huống lỗi:** CV là file PDF dạng ảnh scan nên chỉ trích được dưới 30 ký tự có nghĩa. Trong vòng 1 giây, hệ thống báo lý do và gợi ý ba cách: tải bản PDF xuất trực tiếp từ Word/Canva/Overleaf, tải file DOCX, hoặc tự chọn kỹ năng ngay trên màn hình.

- **UJ-2. Minh soi hai tin tuyển dụng trước khi nộp.**
  - **Persona và bối cảnh:** vẫn là Minh, sáng hôm sau UJ-1. CV đã được sửa.
  - **Trạng thái ban đầu:** Minh thấy 2 tin tuyển Java Backend Fresher trên ITviec và TopCV. Mở lại tab Hải Đồ IT, hồ sơ kỹ năng từ hôm qua vẫn còn.
  - **Diễn biến:**
    1. Minh mở Soi tin, dán nội dung tin của công ty A và bấm "Soi tin".
    2. Hệ thống tự nhận diện vai trò và cấp bậc, hiển thị ở đầu kết quả: "Đang đối chiếu với: [Java Backend ▾] · [Fresher/Junior ▾]". Nếu không đủ 30 tin cho ô này, hệ thống ghi rõ nó đang tính trên tập nào. Minh có thể đổi vai trò hoặc cấp bậc; kết quả được tính lại mà không phải dán lại tin.
    3. **So với hồ sơ:** "Mức khớp: 89% (theo trọng số thị trường)". Dòng phụ ghi: "Bạn đáp ứng 6/8 kỹ năng trong tin này: 4/4 cốt lõi, 2/2 thường gặp, 0/2 riêng của công ty". Hai kỹ năng còn thiếu đều thuộc nhóm "riêng của công ty này".
    4. **So với thị trường:** mục lương ghi "chưa đủ dữ liệu (X/30 tin có lương)". Mục số kỹ năng yêu cầu thì vẫn hiển thị phân vị bình thường.
    5. Minh dán tiếp tin của công ty B. Hệ thống nêu hai dấu hiệu cần kiểm tra:
       - **D1:** số kỹ năng yêu cầu cao hơn 90% số tin cùng vai trò và cấp bậc;
       - **D2:** hơn một nửa công nghệ trong tin thuộc nhóm riêng của công ty.

       Phần lương hiển thị dòng thông tin trung tính "Tin không công bố khoảng lương", đây không phải dấu hiệu.
  - **Cao trào:** Minh nộp đơn vào công ty A và bỏ qua công ty B. Đây là quyết định của Minh; hệ thống không khuyên nộp hay không nộp.
  - **Kết thúc:** Minh dành thời gian cho những tin đáng nộp.

- **UJ-3. Lan chọn hướng đi giữa Backend và Data khi chưa có CV.**
  - **Persona và bối cảnh:** Lan, 20 tuổi, sinh viên CNTT đầu năm 3. Lan đã học Cấu trúc dữ liệu, Cơ sở dữ liệu, lập trình hướng đối tượng với Java và một chút Python. Sắp phải chọn chuyên ngành hẹp trước kỳ OJT. Chưa từng đi làm nên chưa có CV.
  - **Trạng thái ban đầu:** một bạn cùng lớp gửi link qua Zalo: "Vào đây xem số liệu thật trước khi chọn chuyên ngành". Lan mở trên laptop.
  - **Diễn biến:**
    1. Lan mở lần lượt Hà Nội rồi TP.HCM trên Bản đồ nhu cầu. Lan bất ngờ: Data/AI là vai trò chiếm tỷ trọng tin cao nhất ở cả hai thành phố (Hà Nội 18%, TP.HCM 20%), trên cả Backend.
    2. Lan sang Insights:
       - thẻ "Cửa vào cho người mới" cho thấy tỷ lệ tin nhận Intern/Fresher/Junior của từng vai trò;
       - thẻ "Bộ kỹ năng hay đi cùng nhau" cho thấy SQL, Docker và Git xuất hiện nhiều ở cả hai hướng.

       Thẻ nào chưa đủ 30 mẫu thì được ghi chú rõ.
    3. Lan sang Cố vấn, bỏ qua bước tải CV, chọn vai trò Backend. Lan tự bấm vào các nút Java, SQL, Git để đánh dấu "đã có"; đồ thị làm nổi bật các chặng tiếp theo.
    4. Lan đổi sang nhánh Data Engineer. Đồ thị mới tự tô sáng những kỹ năng trùng với hồ sơ kỹ năng của Lan, kèm một dòng tóm tắt: "Có N kỹ năng trong lộ trình này trùng với hồ sơ của bạn."
  - **Cao trào:** thay cho những lời khuyên cảm tính như "Data giờ khó xin việc" hay "Backend bão hòa rồi", Lan thấy bằng số liệu: theo hướng Data cần học thêm bao nhiêu kỹ năng cốt lõi, và những kỹ năng nào học một lần dùng được cho cả hai hướng.
  - **Kết thúc:** Lan bấm "Copy link lộ trình" để lưu lại, rồi lấy tài liệu miễn phí của các kỹ năng chung. Lan quyết định học chắc những kỹ năng đó trong học kỳ này, rồi quay lại sau 2 tuần để chọn nhánh OJT.

## 3. Bảng thuật ngữ

_Mọi phần của PRD và các tài liệu sau (UX, kiến trúc, epic) dùng đúng các thuật ngữ này. Không dùng từ đồng nghĩa thay thế._

**Dữ liệu thị trường**
- **Tin tuyển dụng.** Một tin đăng tuyển thu thập từ một nguồn. Phần mô tả công việc trong tin gọi là **JD**. Mỗi tin thuộc đúng một vai trò, một nhánh (nếu có), một cấp bậc và một thành phố.
- **Nguồn.** Trang mà tin tuyển dụng được thu thập về, ví dụ TopCV, CareerLink, Zalo Careers. Mỗi nguồn có một công tắc bật/tắt riêng.
- **Snapshot.** Ảnh chụp trạng thái của toàn bộ tin tuyển dụng tại một ngày. Mỗi lần pipeline chạy thành công tạo ra một snapshot.
- **Vòng đời tin.** Bốn thông tin của một tin qua các snapshot: ngày thấy lần đầu, ngày thấy lần cuối, số lần thấy, số lần đăng lại.
- **Kỹ năng.** Một mục trong **bộ từ vựng kỹ năng**. Mỗi kỹ năng có một mã định danh duy nhất và danh sách các cách viết khác nhau trỏ về nó (ví dụ "SpringBoot", "Spring Boot" → `spring-boot`). Kỹ năng gồm cả công nghệ (Docker) lẫn khái niệm (Microservices, CI/CD).
- **Vai trò.** Nhóm công việc, ví dụ Backend, Data/AI, QA.
- **Nhánh.** Phân nhánh của một vai trò theo công nghệ chính, ví dụ Java Backend, Data Engineer. Một nhánh chỉ tồn tại khi có từ 30 tin tuyển dụng trở lên.
- **Vai trò mục tiêu.** Vai trò hoặc nhánh mà người dùng đang chọn để so sánh.
- **Cấp bậc.** Mức kinh nghiệm của tin tuyển dụng. Ba nhóm dùng cho so sánh: Intern/Fresher/Junior (0–2 năm kinh nghiệm), Mid, Senior trở lên.
- **Ô thống kê.** Tập tin tuyển dụng dùng để tính một con số.
  - Trong Cố vấn và Soi tin: vai trò mục tiêu × cấp bậc, trên phạm vi toàn quốc. Nếu n dưới ngưỡng mẫu, hệ thống quay về theo thứ tự **giữ cấp bậc trước, giữ nhánh sau**:
    1. nhánh × cấp bậc;
    2. vai trò × cấp bậc;
    3. nhánh × mọi cấp bậc;
    4. vai trò × mọi cấp bậc.

    Tập được dùng luôn kèm nhãn ghi n và cơ cấu cấp bậc của nó.
  - Chỉ tính những tin có ngày thấy lần cuối trong vòng 60 ngày tính tới snapshot đang dùng.
  - Trong Bản đồ nhu cầu và Insights: thành phố × vai trò.
- **Cỡ mẫu (n).** Số tin tuyển dụng trong ô thống kê. **Ngưỡng mẫu** là 30: ô có n dưới ngưỡng thì không hiển thị con số, hoặc quay về ô rộng hơn kèm nhãn ghi rõ.
- **Tỷ lệ xuất hiện.** Phần trăm số tin trong ô thống kê có nhắc tới một kỹ năng.
- **Nhóm kỹ năng.** Phân loại một kỹ năng theo tỷ lệ xuất hiện của nó trong vai trò mục tiêu:
  - **Cốt lõi:** tỷ lệ ≥ θ_core;
  - **Thường gặp:** từ θ_common đến dưới θ_core;
  - **Riêng của công ty:** dưới θ_common.

  θ_core và θ_common là tham số, khởi tạo ở 30% và 10%.
- **Phân vị.** Vị trí của một giá trị (lương, số kỹ năng yêu cầu, số năm kinh nghiệm) so với các tin trong ô thống kê.

**Người dùng**
- **Hồ sơ kỹ năng.** Tập kỹ năng mà người dùng **đã có**. Hồ sơ được lưu trong trình duyệt, không lưu trên server. Hồ sơ hình thành từ CV, từ việc người dùng tự chọn, hoặc từ cả hai. v1 chỉ có trạng thái "đã có".
- **Khoảng trống kỹ năng.** Kỹ năng thuộc nhóm cốt lõi hoặc thường gặp của vai trò mục tiêu mà hồ sơ kỹ năng chưa có. Kỹ năng thuộc nhóm riêng của công ty không bao giờ là khoảng trống kỹ năng; chúng chỉ xuất hiện trong Soi tin.
- **Kỹ năng cần bổ sung vào CV.** Kỹ năng mà người dùng xác nhận "Tôi đã biết, chỉ là CV chưa ghi".
- **Mã phiên ẩn danh.** Mã ngẫu nhiên sinh ra trong trình duyệt, không gắn với danh tính, dùng để gom các sự kiện ẩn danh của cùng một người.
- **Sự kiện ẩn danh.** Bản ghi một thao tác của người dùng (ví dụ chọn "Tôi chưa biết" cho một kỹ năng) kèm mã phiên ẩn danh. Không chứa nội dung CV.

**Lộ trình học**
- **Đồ thị học trước – học sau.** Đồ thị có hướng, không chu trình, do nhóm soạn và giảng viên hướng dẫn rà soát. Cạnh A → B nghĩa là nên học A trước B.
- **Lộ trình học.** Danh sách có thứ tự các kỹ năng người dùng nên học cho vai trò mục tiêu. Lộ trình học gồm các khoảng trống kỹ năng và các kỹ năng nền tảng của chúng. Lộ trình học được dựng tất định (cùng đầu vào luôn cho cùng kết quả) theo quy tắc 4 tầng ở FR-22.
- **Kỹ năng nền tảng.** Một kỹ năng có tỷ lệ xuất hiện dưới θ_common, nhưng là tổ tiên trên đồ thị học trước – học sau của một khoảng trống kỹ năng. Ví dụ: Linux cần cho Docker. Đây là ngoại lệ duy nhất cho phép một kỹ năng dưới θ_common vào lộ trình học. Trên giao diện, nó được gắn nhãn "Kỹ năng nền tảng (cần cho X)" thay cho nhãn nhóm kỹ năng.
- **Chặng.** Độ sâu của một kỹ năng trên đồ thị học trước – học sau, sau khi đã trừ các kỹ năng có trong hồ sơ.
- **Danh mục tài liệu.** Danh sách tài liệu và khóa học miễn phí đã kiểm duyệt, gắn với từng kỹ năng. Mọi link hiển thị đều lấy từ danh mục này.

**Soi tin**
- **Mức khớp.** Tỷ lệ phần trăm có trọng số giữa hồ sơ kỹ năng và các kỹ năng đã nhận diện của một JD. Trọng số: cốt lõi 3, thường gặp 2, riêng của công ty 1. Mức khớp = tổng trọng số của các kỹ năng trong JD mà người dùng có, chia cho tổng trọng số mọi kỹ năng đã nhận diện trong JD. Kỹ năng chưa nhận diện không được tính.
- **Kỹ năng chưa nhận diện.** Từ khóa công nghệ trong một JD không khớp với mục nào trong bộ từ vựng kỹ năng. Được hiển thị riêng và không tính vào mức khớp. Được ghi vào danh sách chờ (kèm tần suất) để nhóm rà soát hằng tuần và bổ sung vào bộ từ vựng.
- **Dấu hiệu cần kiểm tra.** Một quy tắc minh bạch được kích hoạt trên một JD, ví dụ "số kỹ năng yêu cầu cao hơn 90% số tin cùng ô thống kê" hay "chỉ cho liên hệ qua Zalo". Đây là gợi ý để người dùng tự xác minh, không phải kết luận tin thật hay giả. Danh sách đầy đủ ở FR-31. Việc tin không ghi lương **không** phải một dấu hiệu.

**Giao diện**
- **Bảng chi tiết thành phố.** Bảng hiện ra khi bấm vào một thành phố trên Bản đồ nhu cầu.
- **Thẻ Insights.** Một nhận định do code tính, chỉ hiển thị khi đủ ngưỡng mẫu.

## 4. Tính năng

### 4.1 Thu thập và chuẩn hóa dữ liệu

**Mô tả.** Mỗi đêm, pipeline thu thập tin tuyển dụng từ các nguồn đang bật, tạo một snapshot, cập nhật vòng đời tin, loại tin trùng lặp, chuẩn hóa kỹ năng và lương, phân loại tin, rồi tính lại các bảng tổng hợp mà các tính năng 4.3–4.6 dùng. Người dùng không thao tác trực tiếp với tính năng này. Đây là nền cho mọi hành trình.

#### FR-1: Thu thập hằng ngày theo từng nguồn
Hệ thống tự động thu thập tin tuyển dụng mỗi ngày một lần từ các nguồn đang bật. Mỗi nguồn có một công tắc bật/tắt riêng, nhóm vận hành thay đổi được mà không phải sửa code.

**Kết quả kiểm chứng được:**
- Mỗi lần chạy ghi lại thời điểm bắt đầu, thời điểm kết thúc, trạng thái và số tin thu được của từng nguồn.
- Nguồn đang tắt không nhận request nào trong lần chạy đó.
- Một nguồn bị lỗi không làm dừng các nguồn khác.
- Nhóm vận hành nhận thông báo khi một lượt chạy lỗi, hoặc khi số tin của một nguồn giảm quá 50% so với trung bình 7 ngày `[GIẢ ĐỊNH: ngưỡng 50%]`. Không có báo động thì khó đạt SM-5.

#### FR-2: Thu thập theo quy tắc lịch sự
Khi thu thập, hệ thống tuân thủ bốn quy tắc:
- kiểm tra `robots.txt` và tôn trọng điều khoản sử dụng của nguồn;
- gửi User-Agent trung thực, có thông tin liên hệ của dự án;
- giãn cách cố định giữa các request tới cùng một nguồn;
- không đăng nhập;
- dừng thu thập nguồn đó ngay khi nhận HTTP 403/429 hoặc trang captcha.

Các ngoại lệ được liệt kê đầy đủ ở §6.1 *Rủi ro đã chấp nhận*: crawler TopCV kế thừa, cùng các crawler và bước pipeline kế thừa khác có dùng kỹ thuật né phát hiện bot.

**Kết quả kiểm chứng được:**
- URL bị `robots.txt` cấm thì không bao giờ được request.
- Khi gặp captcha, nhật ký ghi lý do dừng, và nguồn đó không được thử lại cho tới lần chạy sau.

#### FR-3: Snapshot và vòng đời tin
Mỗi lần pipeline chạy thành công tạo một snapshot. Mỗi tin tuyển dụng lưu vòng đời tin: ngày thấy lần đầu, ngày thấy lần cuối, số lần thấy, số lần đăng lại.

**Kết quả kiểm chứng được:**
- Một tin xuất hiện trong 3 snapshot liên tiếp có số lần thấy bằng 3.
- Một tin chỉ được coi là đã biến mất khi vắng mặt ở **ít nhất 3 lần chạy thành công liên tiếp của chính nguồn đó**. Khi xuất hiện lại sau đó, tin được tính thêm một lần đăng lại.
- Một đêm nguồn bị lỗi hoặc bị dừng (FR-2) không bao giờ làm tăng số lần đăng lại.

#### FR-4: Loại tin trùng lặp
Hệ thống loại tin trùng lặp ở hai tầng:
- **trong cùng nguồn:** dựa trên mã tin, URL và nội dung;
- **giữa các nguồn:** dựa trên tên công ty đã chuẩn hóa, kết hợp với độ tương đồng về kỹ năng.

Các tin trùng nhau được gom thành một cụm thay vì bị xóa. Mọi con số thống kê tính mỗi cụm đúng một lần.

**Kết quả kiểm chứng được:**
- Báo cáo precision/recall trên khoảng 100 cặp tin có độ giống nhau cao đã gán nhãn tay.
- Tỷ lệ trùng còn sót trên 100 tin ngẫu nhiên dưới 5%.

#### FR-5: Loại thông tin cá nhân của người đăng tin
Ngay khi đọc tin và trước khi lưu, hệ thống xóa tên, email, số điện thoại và Zalo của người tuyển dụng có trong tin.

**Kết quả kiểm chứng được:**
- Không bản ghi nào trong kho dữ liệu khớp mẫu email hoặc số điện thoại Việt Nam.
- Mỗi lần xóa được ghi nhật ký: chỉ ghi loại thông tin, không ghi giá trị.

#### FR-6: Chuẩn hóa kỹ năng
Hệ thống trích các kỹ năng được nhắc tới trong JD và quy chúng về mã trong bộ từ vựng kỹ năng. Từ khóa không khớp mục nào được ghi vào danh sách kỹ năng chưa nhận diện, kèm tần suất. Trong cùng lượt xử lý đó, hệ thống trích luôn **số năm kinh nghiệm yêu cầu** (tối thiểu, tối đa) nếu tin có nêu. Mỗi kết quả trích xuất lưu kèm phiên bản model và phiên bản prompt đã dùng.

**Kết quả kiểm chứng được:**
- Tin ghi "2–3 năm kinh nghiệm" được lưu thành tối thiểu 2, tối đa 3. Tin không nêu thì để trống; hệ thống không đoán.
- Precision ≥ 85% và Recall ≥ 80% trên bộ chuẩn 200 JD gán nhãn tay. Báo cáo Cohen's kappa của 2 người gán nhãn trên 50 JD chung.
- Bộ chuẩn được lấy từ **văn bản gốc của tin**, phần lớn là tiếng Việt hoặc trộn Việt–Anh, không lấy từ bản mô tả đã được viết lại sang tiếng Anh trong dữ liệu nền. Lý do: người dùng sẽ dán JD gốc. Bộ chuẩn phải có cả tin ghi kỹ năng bằng tiếng Việt, ví dụ "kiểm thử tự động" hay "cơ sở dữ liệu".
- Các cách viết khác nhau ("SpringBoot", "Spring Boot", "Java Spring Boot") quy về cùng một mã.
- **Bộ từ vựng là song ngữ Việt–Anh:** mỗi kỹ năng có cả các cách viết tiếng Việt, ví dụ "học máy" → `machine-learning`, "kiểm thử tự động" → `test-automation`, "cơ sở dữ liệu" → `sql`. Báo cáo precision/recall **tách riêng** cho nhóm kỹ năng được viết bằng tiếng Việt trong bộ chuẩn. Đây là một trong bốn bài toán khó ở §6.5.

#### FR-7: Phân loại vai trò, nhánh, cấp bậc, thành phố
Mỗi tin tuyển dụng được gán một vai trò, một nhánh (nếu có), một cấp bậc và một thành phố.
- **Nhánh:** chỉ được tạo khi có từ 30 tin trở lên.
- **Data/AI:** tách thành Data Analyst/BI, Data Engineer và AI/ML Engineer.
- **Embedded:** tách khỏi nhóm "Other".

**Kết quả kiểm chứng được:**
- Báo cáo độ chính xác phân loại vai trò trên bộ chuẩn 200 JD.
- Tỷ lệ tin rơi vào nhóm "Other" được báo cáo trước và sau khi tách.
- Tin không thuộc lĩnh vực IT (ví dụ tin từ các team không phải công nghệ của Zalo Careers hay MoMo Careers) được gắn nhãn và **loại khỏi mọi bảng tổng hợp**. Tỷ lệ tin bị loại được báo cáo theo từng nguồn.

#### FR-8: Chuẩn hóa lương
Lương dạng số được quy về cùng một đơn vị: VND/tháng, gross. USD được đổi theo một tỷ giá cố định, có thể cấu hình. Tin chỉ ghi "thỏa thuận" hoặc không ghi lương được đánh dấu là không có lương dạng số.

**Kết quả kiểm chứng được:**
- Một khoảng lương "1.000–1.500 USD" được lưu thành khoảng VND tương ứng theo tỷ giá cấu hình.
- Tỷ lệ tin có lương dạng số được báo cáo riêng cho từng nguồn.

#### FR-9: Bảng tổng hợp và ngưỡng tham số
Sau mỗi snapshot, hệ thống tính lại:
- tỷ lệ xuất hiện của từng kỹ năng trong từng ô thống kê;
- nhóm kỹ năng của từng kỹ năng, theo các tham số θ_core và θ_common.

Hai tham số được cấu hình, không viết cứng trong code.

**Kết quả kiểm chứng được:**
- Đổi θ_core thì nhóm kỹ năng thay đổi ngay từ lần tính kế tiếp, không cần triển khai lại.
- Ở cấu hình nghiệm thu Sprint 2, mỗi vai trò mục tiêu có ít nhất 3 kỹ năng cốt lõi (mục tiêu 3–5).
- θ được hiệu chỉnh **một lần** ở Sprint 2, rồi **đóng băng trước đợt thử nghiệm ở Sprint 6–7**. Mọi lần đổi θ sau đó phải được ghi lại kèm lý do. Quy tắc này để θ không bị dùng như một cách làm đẹp SM-1 (xem SM-C2).
- Với mỗi phân vị được tính trên ô thống kê có 30 ≤ n < 100, bước tính hằng đêm chạy **bootstrap không tham số** (lấy mẫu có hoàn lại, B = 1.000 lần) để ước lượng khoảng tin cậy 95% của phân vị. Khoảng này được lưu cùng giá trị phân vị. Lý do: phân phối lương và số kỹ năng trong tin tuyển dụng lệch phải và nhạy với ngoại lai, nên một phân vị thô ở cỡ mẫu nhỏ có thể dao động mạnh.

#### FR-47: Chính sách dữ liệu và yêu cầu gỡ
Hải Đồ IT có một trang **chính sách dữ liệu** công khai, gồm:
- mục đích: nghiên cứu học thuật, phi thương mại;
- những nguồn đang dùng;
- dữ liệu nào được thu thập, và được công bố ở mức tổng hợp;
- dữ liệu nào không được lưu (CV, nội dung tin người dùng dán vào);
- cam kết xử lý mọi yêu cầu gỡ trong 48 giờ.

Trang này có một **kênh yêu cầu gỡ** (email) dành cho nhà tuyển dụng hoặc nguồn muốn gỡ tin hay dữ liệu của mình. User-Agent của crawler ghi địa chỉ liên hệ trỏ về kênh này.

**Phân biệt nội bộ với công khai.** Bảng rủi ro đã chấp nhận R1–R4 (§6.1) là tài liệu **nội bộ**, phục vụ bảo vệ đồ án và báo cáo SEP490. Trang công khai **không** đăng chi tiết các kỹ thuật thu thập hay bảng R1–R4.

**Ràng buộc trung thực.** Vì hệ thống đang mang các rủi ro R1–R4, trang công khai **không được khẳng định những điều trái với thực tế đó**, ví dụ không viết "tuân thủ đầy đủ điều khoản của mọi nguồn" hay "mọi dữ liệu đều đã được cấp phép". Trang nêu mục đích và kênh gỡ, không đưa ra cam kết tuân thủ mà hệ thống chưa đạt. Đây là ranh giới giữa "không phô bày rủi ro nội bộ" và "nói sai sự thật"; PRD chỉ chấp nhận vế đầu.

**Kết quả kiểm chứng được:**
- Trang chính sách dữ liệu truy cập được từ chân trang của mọi màn hình.
- Trang không chứa chi tiết kỹ thuật thu thập hay nội dung bảng R1–R4.
- Trang không chứa câu khẳng định tuân thủ nào mâu thuẫn với R1–R4.
- Một yêu cầu gỡ hợp lệ được xử lý, và tin liên quan biến khỏi số liệu công khai từ snapshot kế tiếp.

**Ngoài phạm vi:**
- Không công bố toàn văn JD. Phía người dùng chỉ thấy số liệu tổng hợp và các trường ngắn (chức danh, công ty, thành phố, khoảng lương), kèm link về tin gốc.

### 4.2 Hồ sơ kỹ năng

**Mô tả.** Hồ sơ kỹ năng là tập kỹ năng người dùng **đã có**. Hồ sơ được tạo từ CV, từ việc người dùng tự chọn, hoặc từ cả hai, và chỉ nằm trong trình duyệt của người dùng. Cố vấn và Soi tin đều đọc chung một hồ sơ. Tính năng này thực hiện UJ-1 và UJ-3.

#### FR-10: Tải CV có đồng ý
Người dùng tải lên một CV dạng PDF hoặc DOCX, dung lượng tối đa 5 MB, sau khi tích vào ô đồng ý. Ô đồng ý nêu rõ ba điều:
- hệ thống xử lý văn bản CV để trích kỹ năng, và **văn bản CV được gửi tới một nhà cung cấp dịch vụ AI bên ngoài** (ghi rõ tên nhà cung cấp) để thực hiện việc này;
- hệ thống không lưu file gốc hay thông tin định danh;
- hệ thống ghi thống kê ẩn danh, theo mã phiên ẩn danh, về các thao tác chọn kỹ năng.

Thực hiện UJ-1.

**Kết quả kiểm chứng được:**
- Chưa tích ô đồng ý thì không tải lên được.
- Sau khi xử lý xong, file CV và văn bản trích từ CV không còn trên server.
- Trong lúc xử lý, giao diện hiển thị lần lượt các bước đang chạy.

#### FR-11: Nhận biết CV dạng ảnh scan
Nếu văn bản trích được từ CV có dưới 30 ký tự có nghĩa, hệ thống báo lỗi và gợi ý ba cách khắc phục:
- tải bản PDF xuất trực tiếp từ Word, Canva hoặc Overleaf;
- tải file DOCX;
- tự chọn kỹ năng.

**Kết quả kiểm chứng được:**
- Thông báo lỗi xuất hiện trong vòng 1 giây kể từ lúc tải lên.
- v1 không chạy OCR.

#### FR-12: Trích kỹ năng từ CV
Hệ thống trích kỹ năng từ văn bản CV theo cùng bộ từ vựng kỹ năng ở FR-6, rồi thêm vào hồ sơ kỹ năng.

**Kết quả kiểm chứng được:**
- Cùng một CV luôn cho cùng một tập kỹ năng.
- Thời gian từ lúc tải CV đến lúc có hồ sơ kỹ năng nằm trong ngân sách 15 giây của toàn luồng.

#### FR-13: Tự chọn kỹ năng
Người dùng tự thêm hoặc bỏ kỹ năng trong hồ sơ, không cần CV, bằng một trong hai cách:
- bấm trực tiếp lên nút kỹ năng trên đồ thị lộ trình học;
- tìm và chọn từ danh sách kỹ năng.

Thực hiện UJ-3.

**Kết quả kiểm chứng được:**
- Hồ sơ tạo bằng cách tự chọn và hồ sơ tạo từ CV được Cố vấn và Soi tin xử lý giống hệt nhau.

#### FR-14: Lưu hồ sơ trong trình duyệt và xóa hồ sơ
Hồ sơ kỹ năng và vai trò mục tiêu được lưu trong trình duyệt, nên tải lại trang hoặc mở lại vào hôm sau vẫn còn. Người dùng có nút "Xóa hồ sơ" để xóa toàn bộ dữ liệu này. Thực hiện UJ-2.

**Kết quả kiểm chứng được:**
- Đóng rồi mở lại trình duyệt trên cùng máy, hồ sơ vẫn còn.
- Sau khi bấm "Xóa hồ sơ", không còn dữ liệu nào của Hải Đồ IT trong bộ nhớ trình duyệt.

#### FR-15: Link chia sẻ
Người dùng copy được một link chứa vai trò mục tiêu và danh sách mã kỹ năng trong hồ sơ. Mở link đó sẽ khôi phục đúng màn hình lộ trình học. Thực hiện UJ-3.

**Kết quả kiểm chứng được:**
- URL không chứa tên, email hay bất kỳ nội dung nào của CV.
- Mở link trên một máy khác, trên cùng một snapshot, hiển thị đúng lộ trình học như trên máy gốc.
- Link không gắn với một snapshot cố định, nên nếu mở vào một ngày khác, lộ trình học được tính lại trên snapshot mới. Màn hình luôn ghi ngày của snapshot đang dùng, nên người đọc thấy được điều này.

#### FR-16: Tải kết quả
Người dùng tải về một bản tóm tắt gồm hai phần:
- danh sách kỹ năng cần bổ sung vào CV;
- lộ trình học theo chặng, kèm link từ danh mục tài liệu.

Thực hiện UJ-1.

**Kết quả kiểm chứng được:**
- Bản tóm tắt ghi rõ vai trò mục tiêu, cỡ mẫu và ngày của dữ liệu.

#### FR-17: Sự kiện ẩn danh
Hệ thống sinh một mã phiên ẩn danh trong trình duyệt và ghi sự kiện ẩn danh cho các thao tác sau:
- chọn một trong ba lựa chọn của FR-21 cho một khoảng trống kỹ năng;
- tải CV thành công hoặc thất bại;
- soi một tin;
- lưu kết quả.

**Kết quả kiểm chứng được:**
- Sự kiện chỉ chứa mã phiên ẩn danh, loại thao tác, mã kỹ năng và vai trò mục tiêu.
- Sự kiện không bao giờ chứa nội dung CV, nội dung JD hay thông tin định danh.
- Xóa hồ sơ (FR-14) cũng xóa mã phiên ẩn danh khỏi trình duyệt.

### 4.3 Cố vấn

**Mô tả.** Cố vấn dựng lộ trình học cho vai trò mục tiêu dưới dạng đồ thị nút, giao diện tham khảo roadmap.sh.
- **Chưa có hồ sơ kỹ năng:** người dùng thấy lộ trình học chung của thị trường.
- **Đã có hồ sơ kỹ năng:** lộ trình học trừ đi những gì người dùng đã có, và khoảng trống kỹ năng được làm nổi bật.

Thứ tự học do thuật toán quyết định; LLM chỉ viết lời dẫn. Tính năng này thực hiện UJ-1 và UJ-3.

#### FR-18: Chọn vai trò mục tiêu và cấp bậc
Người dùng chọn vai trò, nhánh (nếu có) và cấp bậc. Cấp bậc mặc định là Intern/Fresher/Junior (0–2 năm kinh nghiệm). Khi người dùng đến từ bảng chi tiết thành phố của Bản đồ nhu cầu, vai trò được chọn sẵn. Thực hiện UJ-1.

**Kết quả kiểm chứng được:**
- **Vai trò mục tiêu chưa có đồ thị học trước – học sau:**
  - Cố vấn không vẽ đồ thị. Thay vào đó, nó hiển thị danh sách kỹ năng theo nhóm (cốt lõi, thường gặp), kèm tỷ lệ xuất hiện. Người dùng vẫn đối chiếu được với hồ sơ kỹ năng.
  - Có dòng thông báo: "Lộ trình học có thứ tự cho vai trò này đang được biên soạn".
  - Nút chuyển từ bảng chi tiết thành phố sang Cố vấn hiển thị cùng thông báo đó.
- Đổi vai trò hoặc cấp bậc thì lộ trình học được tính lại mà người dùng không phải tải lại trang.

#### FR-19: Lộ trình học chung
Khi hồ sơ kỹ năng trống, Cố vấn hiển thị toàn bộ kỹ năng thuộc nhóm cốt lõi và nhóm thường gặp của ô thống kê. Mỗi nút ghi tỷ lệ xuất hiện và nhóm kỹ năng. Thực hiện UJ-3.

**Kết quả kiểm chứng được:**
- Màn hình ghi rõ cỡ mẫu, nguồn và ngày của snapshot.
- Nếu ô thống kê vai trò mục tiêu × cấp bậc có n < 30, hệ thống quay về theo thứ tự đã định nghĩa ở §3 (giữ cấp bậc trước, giữ nhánh sau), kèm nhãn ghi n và cơ cấu cấp bậc của tập được dùng. Ví dụ: "Nhánh Java Backend ở cấp Fresher/Junior hiện có 26 tin (dưới 30), nên tỷ lệ được tính trên 52 tin Backend cùng cấp bậc."
- Một người dùng chọn cấp Intern/Fresher/Junior không bao giờ nhận một tập mà cấp Mid trở lên chiếm đa số, trừ khi ở bước cuối cùng của thứ tự quay về. Khi đó nhãn phải ghi rõ tỷ lệ tin Mid trở lên.

#### FR-20: Lộ trình học cá nhân hóa
Khi hồ sơ kỹ năng có dữ liệu:
- kỹ năng đã có được tô xanh và không nằm trong lộ trình học;
- mỗi khoảng trống kỹ năng được làm nổi bật kèm nhóm kỹ năng của nó.

Thực hiện UJ-1.

**Kết quả kiểm chứng được:**
- Kỹ năng thuộc nhóm riêng của công ty không xuất hiện trong lộ trình học, trừ khi là kỹ năng nền tảng. Kỹ năng nền tảng luôn mang nhãn "Kỹ năng nền tảng (cần cho X)".
- Cập nhật hồ sơ kỹ năng (tải CV, tự chọn, hoặc dùng FR-21) làm lộ trình học được tính lại trong vòng 1 giây.

#### FR-21: Xác nhận khoảng trống kỹ năng
Trên mỗi khoảng trống kỹ năng có ba lựa chọn.

**Hai nút chính:**
- **"Tôi chưa biết":** kỹ năng ở lại trong lộ trình học.
- **"Tôi đã biết, chỉ là CV chưa ghi":** kỹ năng được thêm vào hồ sơ kỹ năng, chuyển sang danh sách kỹ năng cần bổ sung vào CV, và lộ trình học được tính lại.

**Một lựa chọn phụ**, hiển thị nhỏ hơn hai nút chính, chỉ có khi hồ sơ kỹ năng được tạo từ CV:
- **"CV của tôi có ghi rồi (hệ thống đọc sót)":** kỹ năng được thêm vào hồ sơ kỹ năng và lộ trình học được tính lại. Kỹ năng **không** vào danh sách kỹ năng cần bổ sung vào CV.

Mỗi lựa chọn ghi một sự kiện ẩn danh (FR-17). Thực hiện UJ-1.

**Kết quả kiểm chứng được:**
- Chọn "Tôi đã biết, chỉ là CV chưa ghi" cho Docker: Docker biến khỏi lộ trình học và xuất hiện trong danh sách kỹ năng cần bổ sung vào CV.
- Chọn "CV của tôi có ghi rồi (hệ thống đọc sót)" cho Docker: Docker biến khỏi lộ trình học và không xuất hiện trong danh sách đó.
- Người dùng đổi được lựa chọn của mình; lựa chọn sau cùng là lựa chọn có hiệu lực.

#### FR-22: Dựng lộ trình học tất định
Lộ trình học được dựng theo các bước:
1. lấy tập khoảng trống kỹ năng;
2. thêm các kỹ năng tổ tiên còn thiếu trên đồ thị học trước – học sau;
3. xếp thứ tự theo quy tắc 4 tầng:
   - **Tầng 1:** chặng tăng dần;
   - **Tầng 2:** trong cùng chặng, nhóm cốt lõi đứng trước nhóm thường gặp;
   - **Tầng 3:** cùng nhóm thì xếp theo tỷ lệ xuất hiện giảm dần;
   - **Tầng 4:** bằng nhau thì xếp theo mã kỹ năng A–Z.

**Kết quả kiểm chứng được:**
- Cùng hồ sơ kỹ năng, cùng vai trò mục tiêu và cùng snapshot luôn cho cùng một lộ trình học. Có kiểm thử tự động chạy lặp lại để xác nhận.
- Không kỹ năng nào đứng trước một kỹ năng tổ tiên của nó.
- Có một bước kiểm tra tự động: mọi kỹ năng thuộc nhóm cốt lõi hoặc thường gặp của vai trò mục tiêu đều phải có nút trong đồ thị học trước – học sau. Nếu thiếu, bước kiểm tra báo lỗi trước khi triển khai.
- **Nguồn và kiểm duyệt đồ thị:** mỗi cạnh lưu nguồn tài liệu đã dùng để soạn (tài liệu chính thức của công nghệ, hoặc giáo trình công khai). Mỗi vai trò mục tiêu có một biên bản rà soát ghi người rà soát, ngày, và số cạnh đã rà. Vai trò chỉ được bật trong Cố vấn sau khi có biên bản này.

#### FR-23: Chi tiết một kỹ năng
Bấm vào một nút sẽ mở bảng chi tiết, gồm:
- tỷ lệ xuất hiện và nhóm kỹ năng;
- lời dẫn ngắn giải thích vì sao thị trường cần kỹ năng này;
- tài liệu và khóa học miễn phí lấy từ danh mục tài liệu.

Lời dẫn do LLM viết sẵn một lần cho mỗi cặp kỹ năng × vai trò mục tiêu, được rà soát và lưu lại. Lời dẫn chỉ giải thích bằng lời, **không chứa con số**. Mọi con số (tỷ lệ xuất hiện, cỡ mẫu, ngày cập nhật) được lấy trực tiếp từ bảng tổng hợp (FR-9) và hiển thị ở ô riêng. Thực hiện UJ-1 và UJ-3.

**Kết quả kiểm chứng được:**
- Mọi link hiển thị đều có trong danh mục tài liệu.
- Kiểm thử tự động xác nhận không lời dẫn nào chứa ký hiệu phần trăm hay số lượng tin. Số nằm trong tên công nghệ (Java 17, S3, OAuth2, HTML5, Vue 3…) không bị tính.
- Bấm vào nút không gọi LLM. Lời dẫn được trả về từ dữ liệu đã lưu.

#### FR-24: Tô sáng kỹ năng trùng khi đổi vai trò
Khi người dùng đổi vai trò mục tiêu, những nút trùng với hồ sơ kỹ năng được tô sáng. Một dòng tóm tắt cho biết có bao nhiêu kỹ năng trong lộ trình học mới trùng với hồ sơ. Thực hiện UJ-3.

**Kết quả kiểm chứng được:**
- Đổi từ Backend sang Data Engineer với hồ sơ {Java, SQL, Git}, hệ thống tô sáng đúng những kỹ năng thuộc cả hồ sơ lẫn lộ trình học của Data Engineer.
- Câu chữ dùng cách nói "vai trò có kỹ năng gần", không dùng "lộ trình chuyển việc". Lý do: hệ thống chỉ có dữ liệu tin tuyển dụng, không có dữ liệu về những người đã chuyển việc thật.

#### FR-25: Diễn đạt khách quan theo nhóm kỹ năng
Giao diện mô tả nhóm thường gặp là "nên học sau khi đã nắm các kỹ năng cốt lõi". Hệ thống không bao giờ khuyên "đừng học" một kỹ năng nào.

**Kết quả kiểm chứng được:**
- Không câu chữ nào trên giao diện hay trong lời dẫn chứa lời khuyên bỏ qua một kỹ năng.

**Yêu cầu phi chức năng riêng của tính năng này:**
- Từ lúc tải CV tới lúc lộ trình học cá nhân hóa hiển thị: dưới 15 giây.
- Trên điện thoại: thay đồ thị nút bằng danh sách khoảng trống kỹ năng dạng thẻ, kèm gợi ý mở trên máy tính.

### 4.4 Soi tin

**Mô tả.** Người dùng dán nội dung một tin tuyển dụng và nhận hai góc nhìn:
- **so với hồ sơ:** mức khớp, và kỹ năng còn thiếu theo nhóm;
- **so với thị trường:** phân vị, và các dấu hiệu cần kiểm tra.

Soi tin chỉ nêu dữ kiện và gợi ý để người dùng tự xác minh. Nó không bao giờ khuyên nộp hay không nộp, và không bao giờ kết luận tin thật hay giả. Tính năng này thực hiện UJ-2.

#### FR-26: Dán tin và trích kỹ năng
Người dùng dán nội dung tin tuyển dụng dạng văn bản, dài từ 200 đến 20.000 ký tự. Hệ thống trích kỹ năng theo bộ từ vựng kỹ năng (FR-6). Thực hiện UJ-2.

**Kết quả kiểm chứng được:**
- Nội dung tin được dán vào không được lưu trên server sau khi xử lý xong.
- Nếu tin không thuộc lĩnh vực IT, hệ thống báo "Tin này có vẻ không thuộc lĩnh vực IT" và không tính mức khớp.
- Mỗi lần soi tin ghi một sự kiện ẩn danh (FR-17), không kèm nội dung tin.

#### FR-27: Nhận diện vai trò mục tiêu và cấp bậc của tin
Hệ thống tự nhận diện vai trò (và nhánh, nếu có) cùng cấp bậc của tin, rồi hiển thị ở đầu kết quả dưới dạng ô chọn. Người dùng đổi được vai trò hoặc cấp bậc, và kết quả được tính lại mà không phải dán lại tin. Thực hiện UJ-2.

**Kết quả kiểm chứng được:**
- Đầu kết quả ghi cỡ mẫu của ô thống kê đang dùng.
- Khi n < 30, kết quả quay về theo thứ tự ở §3 và có nhãn ghi n và cơ cấu cấp bậc của tập được dùng (giống FR-19).

#### FR-28: Mức khớp
Khi hồ sơ kỹ năng có dữ liệu, hệ thống hiển thị:
- mức khớp (theo trọng số thị trường);
- ngay dưới đó, một dòng đếm thô theo nhóm. Ví dụ: "Bạn đáp ứng 6/8 kỹ năng trong tin này: 4/4 cốt lõi, 2/2 thường gặp, 0/2 riêng của công ty."

Khi hồ sơ trống, hệ thống mời người dùng tải CV hoặc tự chọn kỹ năng; phần so với thị trường vẫn hiển thị bình thường. Thực hiện UJ-2.

**Kết quả kiểm chứng được:**
- Một tin có 4 kỹ năng cốt lõi, 2 thường gặp và 2 riêng của công ty, với người dùng thiếu đúng 2 kỹ năng riêng, cho mức khớp 89% (16/18).
- Kỹ năng chưa nhận diện không làm thay đổi mức khớp.

#### FR-29: Phân nhóm kỹ năng của tin
Mỗi kỹ năng của tin được xếp vào một trong các nhóm: cốt lõi, thường gặp, riêng của công ty, hoặc kỹ năng chưa nhận diện. Kỹ năng chưa nhận diện được hiển thị ở một dòng riêng, ghi rõ "không tính vào mức khớp", và được đưa vào danh sách chờ (FR-6).

**Kết quả kiểm chứng được:**
- Mỗi kỹ năng thiếu thuộc nhóm riêng của công ty có ghi chú "chỉ cần nếu bạn nhắm đúng công ty này".

#### FR-30: Phân vị so với thị trường
Hệ thống đặt tin vào phân vị của ô thống kê theo ba thước đo:
- **số kỹ năng yêu cầu:** luôn hiển thị;
- **số năm kinh nghiệm yêu cầu:** chỉ hiển thị khi trích được từ tin **và** ô thống kê có từ 30 tin có số năm kinh nghiệm trở lên. Nếu không, ghi "chưa đủ dữ liệu (X/30 tin có số năm kinh nghiệm)";
- **lương:** chỉ hiển thị khi tin có lương dạng số và ô thống kê có từ 30 tin có lương trở lên. Nếu không, ghi "chưa đủ dữ liệu (X/30 tin có lương)".

**Kết quả kiểm chứng được:**
- Không phân vị lương nào được tính trên ô thống kê có dưới 30 tin có lương.
- Không phân vị số năm kinh nghiệm nào được tính trên ô thống kê có dưới 30 tin có trường này. Ngưỡng này đếm số tin **có trường đó**, không đếm toàn bộ tin của ô.
- Khi ô thống kê có 30 ≤ n < 100, giao diện hiển thị phân vị kèm **khoảng tin cậy 95%** đã tính sẵn ở FR-9, thay vì chỉ một con số. Ví dụ: "lương của tin nằm ở phân vị 65% (khoảng tin cậy 52–74%)".

#### FR-31: Dấu hiệu cần kiểm tra
Hệ thống đánh giá từng quy tắc dưới đây. Mỗi dấu hiệu được kích hoạt hiển thị dữ kiện đã kích hoạt nó, cùng một gợi ý hành động.

| # | Dấu hiệu | Điều kiện kích hoạt | Gợi ý hiển thị (tóm tắt) |
|---|---|---|---|
| D1 | Yêu cầu kỹ năng dàn trải | Số kỹ năng đã nhận diện ≥ P90 của ô thống kê | Tin liệt kê nhiều kỹ năng hơn 90% số tin cùng vai trò và cấp bậc. Nên hỏi rõ 2–3 công nghệ nhóm thực sự dùng hằng ngày |
| D2 | Tỷ lệ kỹ năng riêng cao | Tin có ≥ 4 kỹ năng đã nhận diện và hơn 50% trong số đó thuộc nhóm riêng của công ty. **Không tính kỹ năng chưa nhận diện** | Hơn một nửa công nghệ trong tin ít phổ biến trên thị trường chung. Cân nhắc khả năng chuyển đổi sang công ty khác |
| D3 | Yêu cầu cao, lương thấp | Tin có lương dạng số; ô thống kê có ≥ 30 tin có lương; số kỹ năng ≥ P75 trong khi lương trần ≤ P25 | Tin yêu cầu nhiều hơn mặt bằng nhưng trả thấp hơn mặt bằng |
| D4 | Tin đăng lại nhiều lần | Tin khớp với một tin đã thu thập (FR-32), và tin đó có số lần đăng lại ≥ 2 hoặc xuất hiện liên tục qua ≥ 30 snapshot | Tin đã đăng lại X lần. Có thể công ty tuyển nhiều đợt, hoặc chưa tìm được người phù hợp |
| D5 | Kênh liên hệ bất thường | Tin chỉ cho liên hệ qua Zalo, Telegram hoặc email cá nhân (Gmail…), không có kênh của công ty | Hãy xác minh công ty qua website hoặc trang tuyển dụng chính thức trước khi gửi thông tin cá nhân |
| D6 | Đòi tiền trước | Tin nhắc tới đặt cọc, phí đào tạo, phí hồ sơ hoặc phí giữ chỗ | Nhà tuyển dụng hợp pháp không thu tiền của ứng viên. Đừng chuyển tiền trước khi xác minh |
| D7 | Không rõ công ty | Tin không nêu tên công ty | Hãy hỏi rõ tên công ty và tự tra cứu trước khi nộp |

Ngay dưới các dấu hiệu luôn có ghi chú: "Dấu hiệu là gợi ý để bạn tự kiểm tra. Đa số tin bị gắn dấu hiệu vẫn là tin thật." Lý do: ngay trên bộ dữ liệu chuẩn, các mô hình phát hiện tin giả chỉ đạt precision khoảng 0,28.

Tin không ghi lương **không** là một dấu hiệu. Thay vào đó, phần lương hiển thị một dòng thông tin trung tính: "Tin không công bố khoảng lương. Bạn có thể tham khảo phân vị lương của vai trò này (nếu đủ mẫu) khi đàm phán."

**Kết quả kiểm chứng được:**
- Mỗi quy tắc có kiểm thử với một tin mẫu kích hoạt nó và một tin mẫu không kích hoạt nó.
- Không câu chữ nào dùng các từ "lừa đảo", "tin giả" hay "tin ma".

#### FR-46: Chất lượng JD
Hệ thống chấm chất lượng của tin được dán theo một danh sách kiểm tra minh bạch, và hiển thị từng mục đạt hoặc không đạt:
- có khoảng lương;
- có tên công ty;
- có mô tả trách nhiệm công việc;
- có phúc lợi;
- chức danh, các kỹ năng yêu cầu và cấp bậc có nhất quán với nhau không. Ví dụ không nhất quán: tin tuyển "Fresher" nhưng đòi từ 5 năm kinh nghiệm.

Thực hiện UJ-2.

**Kết quả kiểm chứng được:**
- Mỗi mục kiểm tra có một quy tắc viết rõ được và có kiểm thử riêng.
- Kết quả chỉ là danh sách đạt/không đạt kèm lý do. Không gộp thành một "điểm chất lượng" duy nhất.

#### FR-32: Khớp tin được dán với tin đã thu thập
Hệ thống tìm trong dữ liệu đã thu thập một tin trùng với tin được dán, dùng cùng cách so khớp như FR-4. Nếu tìm thấy, Soi tin dùng vòng đời tin của tin đó (cho D4) và hiển thị link về tin gốc. Nếu không tìm thấy, D4 được đánh dấu "không đánh giá được: tin chưa có trong dữ liệu".

**Kết quả kiểm chứng được:**
- Dán lại nguyên văn một tin đã có trong dữ liệu thì tìm được đúng tin đó.

**Yêu cầu phi chức năng riêng:**
- Từ lúc bấm "Soi tin" đến lúc có kết quả: dưới 15 giây.
- Trên điện thoại: Soi tin hoạt động đầy đủ.

### 4.5 Bản đồ nhu cầu

**Mô tả.** Trang chủ của Hải Đồ IT là bản đồ 3D của Việt Nam, mỗi thành phố là một cột. Bấm vào một thành phố để mở bảng chi tiết thành phố. Từ đó, người dùng đi tiếp sang Cố vấn. Bản đồ chỉ hiển thị tỷ trọng và thứ hạng, không hiển thị số tin tuyệt đối như thể đó là mức nhu cầu. Tính năng này thực hiện UJ-1 và UJ-3.

#### FR-33: Bản đồ 3D theo tỷ trọng
Bản đồ có một cột cho mỗi thành phố: Hà Nội, TP.HCM, Đà Nẵng. Người dùng chọn vai trò để lọc; mặc định là "Tất cả".

**Chiều cao cột** luôn là **tỷ trọng của thành phố đó trong tổng số tin của vai trò đang chọn, trên toàn quốc**:
- **khi chọn "Tất cả":** cho thấy quy mô thị trường chung của từng thành phố;
- **khi chọn một vai trò:** cho thấy vai trò đó tập trung ở đâu. Ví dụ, trong snapshot ngày 26/10/2026, Hà Nội chiếm 47% và TP.HCM 38% số tin Data/AI.

Một chiều cao chỉ mang một nghĩa. Câu hỏi "vai trò này chiếm bao nhiêu phần trong một thành phố" do bảng chi tiết thành phố trả lời (FR-34).

**Cột có n < 30:** cột không bị ẩn, mà vẫn vẽ theo tỷ trọng thật, ở trạng thái mờ, kèm nhãn "Cỡ mẫu nhỏ (n = X < 30): số liệu chỉ để tham khảo".

**Thành phố khác:** tin ở các thành phố khác được gom thành "Khác" và hiển thị ở phần chú thích, không vẽ cột.

**Thao tác:** người dùng xoay và nghiêng được bản đồ.

**Kết quả kiểm chứng được:**
- Mỗi cột hiển thị tỷ trọng kèm cỡ mẫu khi người dùng trỏ hoặc chạm vào.
- Khi chọn một vai trò, tổng tỷ trọng của các cột cộng với phần "Khác" và phần không xác định thành phố bằng 100%.
- Cột Đà Nẵng luôn được vẽ. Khi n < 30, cột ở trạng thái mờ và có nhãn cỡ mẫu nhỏ.

#### FR-34: Bảng chi tiết thành phố
Bấm vào một cột sẽ mở bảng chi tiết thành phố, gồm:
- cơ cấu vai trò, với tỷ trọng và cỡ mẫu của từng vai trò;
- các kỹ năng có tỷ lệ xuất hiện cao nhất, cho vai trò đang chọn hoặc cho tất cả;
- ngày của snapshot.

Thực hiện UJ-1 và UJ-3.

**Kết quả kiểm chứng được:**
- Mọi con số trong bảng có ghi cỡ mẫu.
- Ô thống kê có n < 30 thì không hiển thị tỷ lệ, chỉ ghi "chưa đủ dữ liệu".

#### FR-35: Đi tiếp sang Cố vấn
Bảng chi tiết thành phố có nút "Xem lộ trình học và đối chiếu CV cho vai trò này". Nút mở Cố vấn với vai trò đã được chọn sẵn. Nếu vai trò chưa có đồ thị học trước – học sau, nút hiển thị thông báo như ở FR-18. Thực hiện UJ-1.

**Kết quả kiểm chứng được:**
- Bấm nút từ bảng chi tiết Hà Nội, vai trò Backend, sẽ mở Cố vấn với vai trò mục tiêu là Backend.

#### FR-36: Chú thích về nguồn và giới hạn dữ liệu
Bản đồ luôn có phần chú thích gồm:
- danh sách nguồn đang bật;
- ngày của snapshot;
- ba lưu ý chuẩn:
  - tin tuyển dụng không đồng nghĩa với vị trí đang thực sự cần người;
  - dữ liệu nghiêng về thành phố lớn và công ty lớn;
  - con số lương chỉ phản ánh những tin có công bố lương.

**Kết quả kiểm chứng được:**
- Phần chú thích hiển thị trên mọi trạng thái của bản đồ, kể cả trên điện thoại.

**Yêu cầu phi chức năng riêng:**
- Trên điện thoại, bản đồ 3D được thay bằng danh sách thành phố với thanh tỷ trọng, kèm gợi ý mở trên máy tính.
- **Bắt buộc** có chế độ xem 2D hoặc dạng bảng, với cùng số liệu như bản đồ 3D. Người dùng chuyển qua lại được. Nếu trình duyệt không chạy được WebGL, hệ thống tự chuyển sang chế độ này, không hiện màn hình lỗi. Đây cũng là phương án dự phòng khi máy demo yếu.

### 4.6 Insights

**Mô tả.** Insights là trang gồm các thẻ, mỗi thẻ là một nhận định cắt ngang do code tính trên snapshot mới nhất. v1 không có nhận định về xu hướng theo thời gian. Mỗi thẻ có:
- một câu kết luận;
- các con số làm căn cứ, kèm cỡ mẫu và ngày;
- một nút hành động, sang Cố vấn hoặc Bản đồ nhu cầu.

Tính năng này thực hiện UJ-3.

#### FR-37: Năm loại thẻ Insights
v1 có năm loại thẻ:

| Loại thẻ | Cách tính |
|---|---|
| **Cửa vào cho người mới** | Tỷ lệ tin Intern/Fresher/Junior trong từng vai trò |
| **Bộ kỹ năng hay đi cùng nhau** | Các cặp kỹ năng cùng xuất hiện trong nhiều tin nhất, theo từng vai trò |
| **Bậc thang Junior → Senior** | Các kỹ năng có tỷ lệ xuất hiện tăng nhiều nhất từ tin Intern/Fresher/Junior lên tin Senior trở lên, trong cùng vai trò |
| **Khác biệt giữa các thành phố** | Các kỹ năng có tỷ lệ xuất hiện chênh lệch nhiều nhất giữa Hà Nội và TP.HCM. Đà Nẵng được đưa vào khi ô thống kê của nó đạt n ≥ 30; hiện Đà Nẵng chỉ có 64 tin nên phần lớn ô chưa đủ |
| **Ngành và nhà tuyển dụng nổi bật** | Các ngành (ví dụ Fintech, Banking) và các công ty có nhiều tin nhất |

Thực hiện UJ-3.

**Kết quả kiểm chứng được:**
- Mỗi loại thẻ có kiểm thử so khớp con số hiển thị với một câu truy vấn kiểm tra độc lập trên cùng snapshot.

#### FR-38: Ngưỡng hiển thị thẻ
Một thẻ chỉ hiển thị khi mọi con số trong thẻ được tính trên ô thống kê có n ≥ 30. Thẻ so sánh (bậc thang, khác biệt thành phố) chỉ hiển thị khi chênh lệch đạt ít nhất 5 điểm phần trăm. Đây là ngưỡng lọc nhiễu thực tế, không phải kiểm định ý nghĩa thống kê (xem §10).

**Kết quả kiểm chứng được:**
- Không thẻ nào dựa trên ô thống kê có dưới 30 tin.
- Nếu một vai trò không có thẻ nào đủ điều kiện, trang ghi "chưa đủ dữ liệu cho vai trò này".

#### FR-39: Câu kết luận của thẻ
Câu kết luận được tạo từ **mẫu câu cố định**, các chỗ trống được điền bằng số liệu đã tính. Mỗi loại thẻ có 2–3 biến thể, được chọn theo khoảng giá trị của số liệu. Ví dụ:
- trên 50%: "Áp đảo: hơn một nửa số tin…";
- từ 30% đến 50%: "Khá phổ biến: khoảng một phần ba số tin…";
- dưới 10%: "Rất hiếm: chỉ…".

v1 không dùng LLM để sinh câu kết luận của Insights, vì câu kết luận luôn chứa con số và con số thay đổi mỗi ngày.

**Kết quả kiểm chứng được:**
- Biến thể mẫu câu được chọn đúng theo khoảng giá trị; có kiểm thử cho từng ranh giới khoảng.
- Cùng một snapshot luôn cho cùng một câu kết luận.
- Mọi con số trong câu khớp với số liệu hiển thị bên dưới.

#### FR-40: Lọc thẻ theo vai trò
Người dùng lọc thẻ theo vai trò. Nếu trình duyệt đã lưu vai trò mục tiêu (FR-14), bộ lọc được chọn sẵn vai trò đó.

**Kết quả kiểm chứng được:**
- Đổi bộ lọc vai trò thì chỉ các thẻ của vai trò đó hiển thị, cộng các thẻ áp dụng cho mọi vai trò.

### 4.7 Chế độ thử nghiệm

**Mô tả.** Chế độ thử nghiệm phục vụ đợt thử nghiệm 30–50 người dùng cho chương Thực nghiệm. Chế độ này chỉ bật khi người dùng vào bằng link thử nghiệm. Mọi dữ liệu của một người thử được nối với nhau qua mã phiên ẩn danh. Chế độ thử nghiệm **ẩn danh tuyệt đối**: không thu thông tin liên hệ, không hỏi lại sau phiên.

#### FR-41: Bật chế độ thử nghiệm
Khi vào bằng link thử nghiệm (ví dụ `?mode=eval`), giao diện luôn hiển thị nhãn "Chế độ thử nghiệm", và mọi sự kiện ẩn danh trong phiên được đánh dấu là thuộc thử nghiệm.

**Kết quả kiểm chứng được:**
- Người vào bằng link thường không bao giờ thấy modal thử nghiệm.
- Dữ liệu thử nghiệm tách được khỏi dữ liệu sử dụng thường.

#### FR-42: Modal đầu phiên
Ngay khi vào bằng link thử nghiệm, một modal che toàn bộ nền **trước khi** người thử thấy bất kỳ con số nào. Modal hỏi ba thứ:
- nhóm người dùng: trong trường hoặc ngoài trường;
- vai trò mục tiêu;
- **đúng 3** kỹ năng người thử nghĩ mình cần học nhất, chọn từ bộ từ vựng kỹ năng bằng ô tìm kiếm có gợi ý (dùng lại thành phần của FR-13);
- **một câu tự đánh giá thang 1–5:** "Ở thời điểm hiện tại, mức độ rõ ràng của bạn về những kỹ năng cần ưu tiên học tiếp theo cho vị trí mục tiêu là bao nhiêu?" (1 = hoàn toàn mông lung, chưa biết bắt đầu từ đâu; 5 = hoàn toàn rõ ràng về danh sách kỹ năng và thứ tự học). Câu này được hỏi lại **nguyên văn** ở modal cuối phiên (FR-43) để tạo cặp biến trước–sau.

**Kết quả kiểm chứng được:**
- Chưa trả lời xong thì không đóng được modal.
- Ba kỹ năng được lưu dưới dạng mã kỹ năng, không phải văn bản tự do.

#### FR-43: Modal cuối phiên
Modal cuối phiên tự bật khi người thử bấm "Lưu kết quả" (FR-16) hoặc "Copy link chia sẻ" (FR-15). Trong suốt phiên, luôn có nút "Hoàn tất thử nghiệm & Đánh giá (1 phút)". Modal hỏi hai thứ:
- **câu tự đánh giá thang 1–5:** đúng nguyên văn câu đã hỏi ở FR-42, không đổi một chữ nào;
- **ý định hành động:** "Sau phiên này, bạn có dự định sửa CV hoặc đổi thứ tự học trong 4 tuần tới không?" (Có / Không);
- **so sánh mù:** xem FR-44.

**Kết quả kiểm chứng được:**
- Mỗi mã phiên ẩn danh chỉ gửi được modal cuối phiên một lần.

#### FR-44: So sánh mù trên tình huống mẫu cố định
Modal cuối phiên hiển thị một tình huống mẫu cố định theo vai trò mục tiêu của người thử, gồm một hồ sơ kỹ năng mẫu và một JD mẫu, cùng hai phương án tư vấn:
- một phương án do Hải Đồ IT tạo ra trên đúng đầu vào mẫu đó;
- một phương án là câu trả lời ChatGPT soạn sẵn cho cùng đầu vào.

Hai phương án không ghi nguồn, và thứ tự trái/phải được đảo ngẫu nhiên 50/50. Người thử chấm từng phương án từ 1 đến 5, rồi chọn phương án mình thấy hữu ích hơn.

So sánh mù đặt ở **modal cuối phiên**, không đặt ở đầu phiên: người thử vào từ link Facebook để dùng công cụ, chặn họ bằng một bài so sánh ngay đầu sẽ làm phần lớn bỏ cuộc trước khi gom đủ 30–50 mẫu. Để chống thiên lệch do quen văn phong Hải Đồ IT, cả hai phương án được chuẩn hóa về **cùng một định dạng**: cùng dùng markdown trung tính, cùng cấu trúc gạch đầu dòng, độ dài tương đương.

**Kết quả kiểm chứng được:**
- Hai phương án không phân biệt được bằng định dạng, chỉ khác ở nội dung.
- **Trên điện thoại:** hai phương án xếp trên và dưới thay cho trái và phải, vẫn đảo ngẫu nhiên 50/50, và hệ thống vẫn lưu vị trí đã hiển thị. Khoảng 40% người thử có thể dùng điện thoại, nên FR-21 và FR-42 đến FR-44 phải chạy đầy đủ trên điện thoại.
- FR-42 ghi lại loại thiết bị (máy tính hay điện thoại) để phân tích.

**Kết quả kiểm chứng được:**
- Tình huống mẫu và cả hai phương án được chuẩn bị sẵn dưới dạng dữ liệu tĩnh. Lúc thử nghiệm không gọi API nào.
- Hệ thống lưu vị trí trái/phải đã hiển thị, để phân tích được thiên lệch theo vị trí.

#### FR-45: Ẩn danh tuyệt đối và xuất dữ liệu
Chế độ thử nghiệm không có ô nhập email, Zalo hay bất kỳ thông tin liên hệ nào. Dữ liệu của modal đầu phiên, các sự kiện ẩn danh và modal cuối phiên được nối với nhau chỉ bằng mã phiên ẩn danh.

**Kết quả kiểm chứng được:**
- Một câu truy vấn duy nhất xuất được bảng kết quả theo từng phiên, gồm: nhóm người dùng, 3 kỹ năng tự đoán, các lựa chọn "đã biết / chưa biết", ý định hành động, điểm và lựa chọn của phần so sánh mù.

### 4.8 Trang nội dung công khai

**Mô tả.** Ngoài ứng dụng mà người dùng mở để làm các hành trình ở §2.3, Hải Đồ IT có các trang đọc được không cần tài khoản. Trang để trình thu thập của công cụ tìm kiếm và công cụ AI đọc được câu trả lời có số, có nguồn và có ngày trong nội dung trả về. v1 có đúng một trang cho mỗi vai trò mục tiêu trong danh sách lúc công khai ở §8.1, tức 4–5 vai trò, tất cả dùng chung một khuôn. Trang theo vai trò, không theo nhánh. Vai trò chưa có đồ thị học trước vẫn có trang. Cộng một trang chính sách dữ liệu (FR-47). Không có khoảng 5–8 trang.

#### FR-48: Trang thị trường theo vai trò mục tiêu
Mỗi vai trò mục tiêu trong danh sách lúc công khai có đúng một trang. URL của vai trò đó không đổi khi sang snapshot mới.

Ô duy nhất của trang là vai trò mục tiêu × mọi cấp bậc, toàn quốc, chỉ tin có ngày thấy lần cuối trong 60 ngày. n ghi trên trang là n của ô đó. Trang không dùng thứ tự quay về của §3. Trang không vẽ tỷ trọng thành phố và không sửa FR-33.

Khi n của ô ≥ 30, đoạn đầu nêu ít nhất ba kỹ năng, mỗi kỹ năng có tỷ lệ xuất hiện. Khi n < 30, đoạn đầu chỉ được câu "chưa đủ dữ liệu (n = X)": không có tên nhóm kỹ năng, không có phần trăm.

Phân vị số kỹ năng chỉ hiện khi n của ô ≥ 30. Phân vị lương và phân vị số năm kinh nghiệm chỉ hiện khi có ≥ 30 tin có đúng trường đó, cùng cửa với FR-30. Dưới cửa của đúng thước đo thì câu "chưa đủ dữ liệu", không hiện con số của thước đo đó. Tỷ lệ xuất hiện và phân vị trên trang dùng cùng quyết định che số với Soi tin. Tỷ trọng cấu phần không thuộc trang này.

Mỗi con số kèm n của đúng thước đo, danh sách nguồn đang bật, và ngày snapshot. Trang có đủ hai ý độ phủ của §5, trong đó có ba lưu ý chuẩn của FR-36.

Trang chỉ dùng số liệu tổng hợp. Không liệt kê tin. Không chức danh, công ty, thành phố hay lương của từng tin. Không link về tin gốc. Không toàn văn JD, không mô tả tin. Trần trường ngắn của §6.2 không áp vào trang này.

Ràng buộc trung thực của FR-47 áp dụng nguyên: không đăng bảng R1–R4 (§6.1). Trang không có câu nào khẳng định đã có phép, đã tuân thủ điều khoản của nguồn, hoặc mọi dữ liệu đã được cấp phép. Hai câu bị cấm, lấy nguyên từ FR-47: "tuân thủ đầy đủ điều khoản của mọi nguồn" và "mọi dữ liệu đều đã được cấp phép".

Sau khi ứng dụng đã chuyển sang một snapshot, kể cả snapshot thiếu nguồn, nội dung trang khớp snapshot đó. Nguồn thiếu hiện trong danh sách nguồn. Trang không giữ snapshot cũ hơn snapshot ứng dụng đang hiển thị.

Mỗi URL có liên kết nhìn thấy tới trang chính sách dữ liệu.

**Kết quả kiểm chứng được:**
- Với mỗi vai trò trong danh sách lúc công khai của §8.1 có đúng một URL. URL không đổi khi sang snapshot mới. Mở được không cần tài khoản.
- Request không cookie tới URL đó nhận đủ đoạn đầu trong nội dung trả về, không chuyển hướng tới đăng nhập, và URL không nằm trong chỉ dẫn chặn thu thập.
- Khi n của ô ≥ 30, đoạn đầu có ít nhất ba kỹ năng, mỗi kỹ năng một tỷ lệ, kèm n, danh sách nguồn đang bật và ngày snapshot.
- Khi n của ô < 30, đoạn đầu chỉ là "chưa đủ dữ liệu (n = X)", không có tên nhóm và không có phần trăm.
- Phân vị lương không hiện khi số tin có lương dưới 30, kể cả khi n của ô ≥ 30.
- Trang không chứa mô tả tin, toàn văn JD, chức danh, công ty, thành phố, lương của từng tin, hay link về tin gốc.
- Trang không chứa bảng R1–R4, không chứa hai câu cấm ở trên, và không chứa câu nào cùng nghĩa.
- Sau khi ứng dụng chuyển snapshot, kể cả snapshot thiếu nguồn, mở URL thấy ngày của snapshot đó và số khớp bảng tổng hợp của ô đã nêu. Nguồn thiếu có trong danh sách nguồn.
- Trang có hai ý độ phủ của §5 và liên kết tới trang chính sách dữ liệu.

**Ngoài phạm vi:**
- Không có trang theo thành phố, theo kỹ năng, hay theo câu hỏi trong v1.
- Không có tài khoản trên các trang này.
- Không lấy việc thêm dữ liệu có cấu trúc cho công cụ tìm kiếm, hay một file hướng dẫn riêng cho mô hình ngôn ngữ, làm tiêu chí hoàn thành.

## 5. Yêu cầu phi chức năng chung

**Hiệu năng.**
- Từ lúc tải CV đến lúc có lộ trình học cá nhân hóa: dưới 15 giây.
- Từ lúc bấm "Soi tin" đến lúc có kết quả: dưới 15 giây.
- Đổi vai trò mục tiêu, cấp bậc, hoặc cập nhật hồ sơ kỹ năng: kết quả mới hiển thị trong vòng 1 giây.

**Quyền riêng tư.**
- Server không lưu file CV, văn bản CV hay nội dung JD do người dùng dán vào, sau khi xử lý xong.
- Nhật ký hệ thống không ghi nội dung CV hay JD.
- Dữ liệu cá nhân của người dùng chỉ nằm trong trình duyệt của họ và xóa được bằng một nút (FR-14).
- Sự kiện ẩn danh chỉ chứa những trường đã liệt kê ở FR-17.

**Trung thực của con số.**
- Mọi con số hiển thị cho người dùng đều kèm cỡ mẫu, nguồn và ngày của snapshot.
- Ô thống kê dưới ngưỡng mẫu thì nói "chưa đủ dữ liệu", không bao giờ hiển thị một con số đoán.
- Mọi màn hình có số liệu (Bản đồ nhu cầu, Insights, Cố vấn, Soi tin, trang vai trò FR-48) và bản tóm tắt tải về đều có **lưu ý về độ phủ dữ liệu**, gồm hai ý:
  - dữ liệu chỉ gồm tin tuyển dụng IT đăng online trên N nguồn;
  - ba lưu ý chuẩn ở FR-36.

**Tất định và truy vết.**
- Lộ trình học, mức khớp, dấu hiệu cần kiểm tra và câu kết luận của Insights là tất định: cùng đầu vào và cùng snapshot luôn cho cùng kết quả.
- Mọi con số truy ngược được về snapshot đã tạo ra nó.
- Mọi kết quả trích xuất bằng LLM truy ngược được về phiên bản model và prompt đã dùng.

**Khả dụng.**
- Nếu pipeline của một đêm bị lỗi, giao diện vẫn chạy trên snapshot gần nhất và hiển thị đúng ngày của snapshot đó.

**Thiết bị.**
- Ưu tiên máy tính.
- Trên điện thoại:
  - Soi tin hoạt động đầy đủ;
  - Cố vấn hiển thị dạng thẻ, gồm cả ba lựa chọn xác nhận của FR-21;
  - Bản đồ nhu cầu hiển thị dạng danh sách thành phố kèm thanh tỷ trọng;
  - Insights hiển thị các thẻ xếp dọc, một thẻ một hàng;
  - Chế độ thử nghiệm (FR-41 đến FR-45) chạy đầy đủ.
- Có chế độ 2D hoặc dạng bảng thay cho 3D (FR-36).

**Ngôn ngữ.** Giao diện tiếng Việt. Tên kỹ năng giữ nguyên dạng chuẩn tiếng Anh, ví dụ Docker, Spring Boot.

## 6. Ràng buộc và rủi ro

### 6.1 Rủi ro đã chấp nhận

Nhóm đã cân nhắc và **chấp nhận có chủ đích** các rủi ro dưới đây (quyết định ngày 03/11/2026). Chúng là ngoại lệ đối với FR-2 và §6.2. Nhóm cần chuẩn bị câu trả lời cho từng mục nếu hội đồng hỏi.

| # | Rủi ro | Phạm vi | Mức rủi ro theo báo cáo nghiên cứu |
|---|---|---|---|
| R1 | Crawler TopCV kế thừa dùng kỹ thuật né phát hiện bot | Chạy cả trên **bản công khai**. Nhóm sẽ xin phép TopCV, và bỏ kỹ thuật này khi thương mại hóa. TopCV chiếm khoảng 38% dữ liệu nền | **Rất cao**, có thể rơi vào Điều 289 Bộ luật Hình sự |
| R2 | Dữ liệu nền của ITviec và TopDev, cùng bước lấy mô tả đầy đủ (step-03), từng được thu bằng kỹ thuật né phát hiện bot. Từ 04/11/2026 (commit `1a8e3f6`, `10d4c73`), hai crawler này dùng User-Agent trung thực và step-03 đã bị xóa | Chỉ còn áp cho dữ liệu nền. Lượt thu mới không thuộc R2 | **Rất cao** với dữ liệu nền |
| R3 | 625 tin LinkedIn trong dữ liệu nền được thu bằng tài khoản đăng nhập | Được tính vào số liệu công khai. v1 **không thu thập mới** từ LinkedIn | **Rất cao**: đúng loại hành vi đã thua trong các vụ hiQ, Proxycurl, ProAPIs |
| R4 | 555 tin ITviec trong dữ liệu nền, cùng tin ITviec thu mới từ 05/11/2026, trong khi điều khoản §2.2 của ITviec cấm thu thập khi chưa có đồng ý bằng văn bản | Được tính vào số liệu công khai trong lúc chờ xin phép. Nhóm quyết ngày 04–05/11 cho ITviec chạy tự động trong lúc chờ thư đồng ý | **Trung bình–cao**: rủi ro hợp đồng và sở hữu trí tuệ |

**Hệ quả với PRD:** SM-C1 và FR-2 được hiểu là "trừ R1–R4". Mọi số liệu công khai hiện tính trên 3.469 tin, gồm cả R3 và R4. Nếu loại R3 và R4 ra, số tin còn 2.289, trong đó Backend còn 184 tin và Java Backend còn 105 tin.

### 6.2 Pháp lý và nguồn dữ liệu
- **Dữ liệu cá nhân:** Luật Bảo vệ dữ liệu cá nhân 91/2025 không có căn cứ "dữ liệu công khai". Vì vậy:
  - CV chỉ được xử lý khi người dùng đồng ý (FR-10);
  - thông tin cá nhân của người đăng tin bị xóa ngay lúc thu thập (FR-5).
- **Công bố dữ liệu:** chỉ công bố số liệu tổng hợp và các trường ngắn, kèm link về tin gốc. Không đăng lại toàn văn JD.
- **ITviec:** nhóm gửi email xin phép trong tuần 1. Dữ liệu ITviec đã có được dùng trong số liệu công khai (R4 ở §6.1). Đây là thay đổi so với quyết định trước đó "chỉ dùng làm bộ kiểm tra nội bộ".
- **Repo gốc của bộ scraper:** repo không có LICENSE. Nhóm xin phép tác giả trước khi công khai.

### 6.3 Dữ liệu
- **Lương:** chỉ khoảng 24% tin có lương dạng số, nên phần lớn phân vị lương sẽ hiển thị "chưa đủ dữ liệu".
- **Vai trò mỏng:** một số vai trò và nhánh có ít tin, nên nhiều ô thống kê sẽ quay về toàn bộ vai trò.
- **Thiên lệch:** dữ liệu nghiêng về Hà Nội, TP.HCM và các công ty lớn.

### 6.4 Chi phí
- **Trích xuất hằng ngày:** chạy theo lô.
- **Lời dẫn của Cố vấn:** viết sẵn, không gọi LLM khi người dùng bấm.
- **Insights:** không dùng LLM.
- **Lúc người dùng dùng thật:** chỉ gọi LLM ở hai chỗ, là trích kỹ năng từ CV (FR-12) và từ tin được dán (FR-26).
- **Giảm chi phí về sau:** chuyển bước trích xuất sang mô hình nhỏ, nhưng chỉ sau khi đã đo chất lượng trên bộ chuẩn 200 JD.
- **Trần chi phí vận hành sau bảo vệ:** dưới 5–10 USD/tháng trên một VPS nhỏ `[GIẢ ĐỊNH]`. Con số này là ràng buộc cho bước kiến trúc: nó quyết định chọn trình điều phối pipeline nào, và là lý do bước trích xuất phải chuyển sang mô hình nhỏ.

### 6.5 Thời gian và yêu cầu học thuật
- **Thời gian:** 3 người, 8 sprint 1 tuần (2/11–27/12/2026).
- **Review giữa kỳ (khoảng 22–28/11):** cần luồng CV → lộ trình học chạy thật cho Backend và Data/AI.
- **Nộp báo cáo:** khoảng 20–25/12.
- **Yêu cầu học thuật:** độ phức tạp kỹ thuật được chứng minh bằng những bài toán khó, được giải đúng và đo được, không bằng số lượng công nghệ sử dụng. Bốn bài toán đó là:

| # | Bài toán | Giải ở | Đo bằng |
|---|---|---|---|
| 1 | Loại tin trùng lặp giữa các sàn | FR-4 | SM-7 |
| 2 | Chuẩn hóa kỹ năng song ngữ Việt–Anh | FR-6 | SM-6, kèm số liệu tách riêng cho kỹ năng viết bằng tiếng Việt |
| 3 | Tính phân vị khi mẫu thưa | §3 (thứ tự quay về), FR-9 (bootstrap), FR-19, FR-30 | SM-13 (độ ổn định phân vị khi làm thưa mẫu), cộng khoảng tin cậy bootstrap hiển thị trực tiếp cho người dùng |
| 4 | Dựng lộ trình học tất định | FR-22 | SM-8, đặt cạnh SM-11 |

## 7. Không làm gì

- **Không phải sàn tuyển dụng:** không đăng tin, không ứng tuyển qua Hải Đồ IT, không lọc ứng viên cho nhà tuyển dụng.
- **Không phải chatbot:** không có ô chat tự do. LLM chỉ trích xuất và viết lời dẫn.
- **Không viết CV hộ:** chỉ chỉ ra kỹ năng cần bổ sung vào CV, không sửa câu chữ.
- **Không phán xét tin tuyển dụng:** không kết luận tin thật hay giả, không khuyên nộp hay không nộp.
- **Không dự báo:** không có xu hướng theo thời gian hay dự báo nhu cầu trong v1.
- **Không giữ dữ liệu định danh của người dùng:** không tài khoản, không lưu CV, không lưu lịch sử gắn với danh tính. Server chỉ lưu sự kiện ẩn danh theo mã phiên (FR-17) và dữ liệu chế độ thử nghiệm (FR-45).
- **Không bán điểm đánh giá:** không nhận tiền để thay đổi bất kỳ con số hay dấu hiệu nào.

## 8. Phạm vi MVP

### 8.1 Có trong v1
- Bảy tính năng tương tác, FR-1 đến FR-47.
- Trang nội dung công khai là P1: có trong bản công khai, không có trong review giữa kỳ (FR-48, FR-47). Đúng một trang cho mỗi vai trò mục tiêu trong danh sách lúc công khai (4–5), cộng trang chính sách. Chỉ ra khỏi v1 bằng một dòng phạm vi bị cắt, ghi rõ FR-48.
- Lộ trình học có thứ tự:
  - Review giữa kỳ: 2 vai trò mục tiêu, Backend (nhánh Java Backend) và Data/AI (nhánh Data Engineer);
  - khi công khai: 4–5 vai trò mục tiêu.
- Bản đồ gồm Hà Nội, TP.HCM, Đà Nẵng và "Khác".
- Chỉ các nguồn đang bật công tắc trên bản công khai.

### 8.2 Ngoài phạm vi v1
- Xu hướng theo thời gian và dự báo: cần ít nhất khoảng 3 tháng snapshot liên tục.
- Kết luận về tin bất thường. v1 chỉ nêu dữ kiện vòng đời tin (D4).
- Viết lại câu chữ CV.
- Kênh để người dùng gửi mức lương.
- Extension trình duyệt cho Soi tin.
- Tài khoản người dùng, và trạng thái "đang học" trong hồ sơ kỹ năng.
- Ước lượng số tuần học cho từng kỹ năng.
- So sánh song song hai thành phố trên bản đồ.
- OCR cho CV dạng ảnh scan.
- Hỏi lại người thử sau phiên thử nghiệm.
- Thu thập mới từ LinkedIn. Dữ liệu LinkedIn lịch sử trong bộ nền vẫn được dùng, xem R3 ở §6.1.
- Tính năng cho nhà trường hoặc nhà tuyển dụng.
- Ứng dụng di động.
- Trang công khai theo thành phố, theo kỹ năng, hoặc theo câu hỏi. v1 không đặt mục tiêu lượt được dẫn. Khi xét mục này, "được dẫn tới" nghĩa là một trang vai trò xuất hiện trong kết quả tìm hoặc trong câu trả lời của công cụ AI, do nhóm kiểm tại thời điểm xét.

## 9. Chỉ số thành công

**Giả thuyết cần kiểm chứng: "thiếu kỹ năng cốt lõi".** Nhóm cho rằng việc thiếu kỹ năng cốt lõi mà JD yêu cầu (nhánh 1), hoặc có kỹ năng nhưng CV không thể hiện (nhánh 2), là **một** nguyên nhân đáng kể khiến CV của fresher bị loại. Các nguyên nhân khác cũng có thật: thị trường fresher co hẹp, dự án cá nhân còn yếu. SM-1 kiểm chứng nhánh 1; SM-9 kiểm chứng nhánh 2. Không chỉ số nào trong v1 chứng minh được quan hệ nhân quả tới kết quả xin việc.

**Chính** (đo bằng chế độ thử nghiệm, Sprint 6–7, 30–50 người thử: khoảng 60% trong trường, 40% ngoài trường)

SM-1, SM-2, SM-3, SM-9 và SM-12 được báo cáo cả ở dạng tổng và dạng **tách theo nhóm trong trường / ngoài trường** (thông tin nhóm lấy từ FR-42). Việc tách này là cách nhóm giảm nhẹ thiên lệch chọn mẫu nêu ở mục Giới hạn đã biết.
- **SM-1: Phát hiện điểm mù.**
  - **Định nghĩa:**
    - **Mẫu số:** số phiên thử nghiệm hoàn thành cả modal đầu phiên lẫn modal cuối phiên.
    - **Tử số:** số phiên có ít nhất 1 kỹ năng thuộc nhóm cốt lõi **hoặc thường gặp** thỏa mãn đồng thời hai điều kiện: (a) không nằm trong 3 kỹ năng người thử tự đoán ở modal đầu phiên; (b) người thử bấm "Tôi chưa biết" (không tính "Tôi đã biết, chỉ là CV chưa ghi" và "CV của tôi có ghi rồi"). Lý do mở rộng sang nhóm thường gặp: ở cấp Fresher, nhóm cốt lõi hầu như chỉ có Java, SQL, Python mà phần lớn sinh viên đã có; điểm mù thật thường nằm ở nhóm thường gặp (Docker, Redis, CI/CD, Unit Testing).
    - **Báo cáo kèm:** số khoảng trống kỹ năng cốt lõi trung bình mỗi phiên, để người đọc thấy chỉ số này dễ hay khó đạt đến đâu.
  - **Mục tiêu:** ≥ 70%.
  - **Kiểm chứng:** FR-21, FR-42.
- **SM-2: Ý định hành động.**
  - **Định nghĩa:** tỷ lệ người thử trả lời "Có" ở modal cuối phiên.
  - **Mục tiêu:** ≥ 60%.
  - **Kiểm chứng:** FR-43.
- **SM-3: So sánh mù.**
  - **Định nghĩa:** điểm trung bình của phương án Hải Đồ IT, và tỷ lệ người thử chọn phương án này.
  - **Mục tiêu:**
    - điểm ≥ 4,0/5;
    - tỷ lệ chọn Hải Đồ IT cao hơn 50% với kiểm định nhị thức một phía, p < 0,05. Với 30 người thử, điều này cần khoảng 20 người chọn Hải Đồ IT.
  - **Cách chuẩn bị:**
    - câu trả lời ChatGPT được lấy bằng một prompt cố định, ghi rõ model và ngày lấy, và dùng câu trả lời đầu tiên, không chọn lọc;
    - hai phương án được trình bày cùng một định dạng văn bản.
  - **Báo cáo:** tách riêng nhóm trong trường và ngoài trường, kèm phân tích thiên lệch theo vị trí trái/phải.
- **SM-12: Độ rõ ràng trước và sau phiên.**
  - **Định nghĩa:** cặp điểm tự đánh giá thang 1–5 về mức độ rõ ràng của kỹ năng cần ưu tiên học, hỏi cùng một câu ở modal đầu phiên (FR-42) và modal cuối phiên (FR-43), nối với nhau bằng mã phiên ẩn danh.
  - **Mục tiêu:** điểm sau cao hơn điểm trước, có ý nghĩa thống kê với kiểm định Wilcoxon signed-rank, p < 0,05.
  - **Báo cáo kèm:** mức tăng trung vị, và phân bố của từng thời điểm. Nếu một nhóm nhỏ giảm điểm, báo cáo cả nhóm đó thay vì chỉ báo giá trị trung bình.
  - **Giới hạn:** đây là mức tự đánh giá, không phải năng lực thật. Người thử biết mình đang thử sản phẩm của nhóm, nên có thể chấm cao hơn thực tế.
  - **Kiểm chứng:** FR-42, FR-43.
  - **Kiểm chứng:** FR-44.

**Phụ** (đo trong 8 tuần)
- **SM-4: Hiệu năng luồng chính.** Từ lúc tải CV đến lúc có lộ trình học: dưới 15 giây. Kiểm chứng FR-10, FR-12, FR-20.
- **SM-5: Pipeline ổn định.**
  - ≥ 95% lượt chạy hằng đêm thành công trong ≥ 4 tuần liên tiếp;
  - ≥ 25 snapshot;
  - ≥ 1.500 tin mới `[GIẢ ĐỊNH: phụ thuộc số nguồn còn bật]`.

  Kiểm chứng FR-1, FR-3.
- **SM-6: Trích xuất kỹ năng.** Precision ≥ 85%, Recall ≥ 80% trên bộ chuẩn 200 JD; báo cáo Cohen's kappa. Kiểm chứng FR-6, FR-12.
- **SM-7: Loại tin trùng lặp.** Báo cáo precision/recall trên khoảng 100 cặp tin; tỷ lệ trùng còn sót dưới 5%. Kiểm chứng FR-4.
- **SM-8: Tất định.** 100% lộ trình học vượt qua kiểm thử lặp lại và kiểm thử thứ tự tổ tiên. Kiểm chứng FR-22.
- **SM-9: Tỷ lệ bỏ sót kỹ năng đã có khi viết CV.**
  - **Định nghĩa:** báo cáo hai con số, cả hai chỉ tính trên các phiên có tải CV. Các lựa chọn "CV của tôi có ghi rồi (hệ thống đọc sót)" không được tính vào tử số của cả hai.
    - **(a) Theo người dùng:** tỷ lệ phiên có ít nhất 1 kỹ năng được chọn "Tôi đã biết, chỉ là CV chưa ghi". Đây là con số brief gọi là bằng chứng trực tiếp cho nhánh 2 của giả thuyết.
    - **(b) Theo kỹ năng:** tỷ lệ khoảng trống kỹ năng được chọn lựa chọn đó.
  - **Mục tiêu:** chỉ số mô tả, không đặt ngưỡng. Báo cáo để kiểm chứng giả thuyết "thiếu kỹ năng cốt lõi".
  - **Kiểm chứng:** FR-21.

- **SM-10: Recall của bộ đọc CV trên CV thật.**
  - **Định nghĩa:** số kỹ năng hệ thống đọc được từ CV, chia cho tổng của số kỹ năng đó và số kỹ năng người dùng báo "CV của tôi có ghi rồi (hệ thống đọc sót)".
  - **Mục tiêu:** chỉ số mô tả, đặt cạnh Recall đo trên bộ chuẩn (SM-6).
  - **Lưu ý:** đây là **cận trên** của recall thật. Người dùng chỉ báo được những kỹ năng bị đọc sót mà lại nằm trong lộ trình học. Kỹ năng bị đọc sót ở ngoài lộ trình học thì không ai thấy.
  - **Kiểm chứng:** FR-12, FR-21.

**Chỉ số đối trọng (không được tối ưu)**
- **SM-C1: Số tin thu thập.**
  - **Không được tối ưu bằng cách:** bật thêm nguồn vi phạm FR-2 (ngoài các rủi ro đã chấp nhận R1–R4 ở §6.1), hoặc nới bước loại tin trùng lặp.
  - **Cân bằng cho:** SM-5.
  - **Theo dõi kèm:** số lần dừng thu thập vì 403/429/captcha.
- **SM-C2: Số khoảng trống kỹ năng mỗi người dùng.**
  - **Không được tối ưu bằng cách:** hạ θ_core, hoặc để bộ trích xuất đọc sót kỹ năng. Cả hai đều làm SM-1 đẹp lên giả tạo.
  - **Cân bằng cho:** SM-1.
- **SM-C3: Tỷ lệ tin kích hoạt dấu hiệu cần kiểm tra.**
  - **Không được để tăng:** một dấu hiệu kích hoạt trên quá nhiều tin sẽ mất tác dụng cảnh báo.
  - **Theo dõi:** tỷ lệ kích hoạt của từng dấu hiệu trên dữ liệu đã thu thập.
- **SM-C4: Thời gian ở lại trang và số lần quay lại.**
  - **Không phải mục tiêu:** Hải Đồ IT là công cụ ra quyết định, không phải sản phẩm giữ chân người dùng.
- **SM-C5: Chi phí LLM trung bình mỗi phiên.**
  - **Không được tối ưu độ chính xác bằng cách:** viết prompt quá dài, gọi lại nhiều lần, hoặc đổi sang model đắt hơn mà không đo lợi ích trên bộ chuẩn.
  - **Theo dõi:** chi phí của mỗi lần trích CV và mỗi lần soi tin.
  - **Cân bằng cho:** SM-6, SM-10.

**Thực nghiệm đối chứng**
- **SM-11: Độ nhất quán lộ trình học của chatbot.**
  - **Định nghĩa:** hỏi cùng một câu về lộ trình học N lần trên 2–3 chatbot phổ biến, rồi đo độ lệch thứ tự giữa các lần trả lời (ví dụ Kendall tau).
  - **Mục tiêu:** chỉ số mô tả, không đặt ngưỡng. Đặt cạnh SM-8 để luận điểm "lộ trình học tất định" có cả phía đối chứng, không chỉ chứng minh phía Hải Đồ IT.
  - **Kiểm chứng:** luận điểm khác biệt số 2 ở §1.
- **SM-13: Độ ổn định của phân vị khi mẫu thưa.**
  - **Định nghĩa:** thí nghiệm làm thưa mẫu. Lấy một ô thống kê đủ dày (ví dụ Backend, n ≈ 200), rút mẫu con ngẫu nhiên xuống n = 100, 50, 30, 15, rồi đo sai số của phân vị và thứ hạng kỹ năng so với giá trị tính trên toàn bộ ô.
  - **So sánh thêm:** đặt cạnh phương án quay về gộp mọi cấp bậc, để cho thấy thứ tự quay về giữ cấp bậc sai lệch ít hơn.
  - **Mục tiêu:** chỉ số mô tả. Kết quả dùng để trả lời câu hỏi "vì sao chọn ngưỡng 30 mà không phải 20 hay 50", bằng biểu đồ sai số theo cỡ mẫu thay vì bằng lập luận suông.
  - **Kiểm chứng:** FR-9, FR-19, FR-30, và bài toán khó số 3 ở §6.5.

**Giới hạn đã biết**
- Người thử phần lớn là sinh viên cùng một trường, học cùng khung chương trình, và quen nhóm phát triển, nên có thể chấm dễ. Cách giảm nhẹ: chia tầng 60/40, form ẩn danh, và báo cáo tách theo nhóm.
- Hai tuần thử nghiệm chỉ đo được nhận thức và ý định, chưa đo được kết quả xin việc thật.
- SM-3 chỉ dùng **một** tình huống mẫu cố định cho mỗi vai trò và **một** câu trả lời ChatGPT soạn sẵn, nên kết quả không đại diện cho mọi tình huống hay mọi chatbot.
- SM-10 là **cận trên** của recall thật, vì người dùng chỉ báo được những kỹ năng bị đọc sót mà lại nằm trong lộ trình học.

## 10. Câu hỏi mở

1. Thẻ so sánh của Insights có cần thêm kiểm định hai tỷ lệ (z-test), ngoài ngưỡng chênh 5 điểm phần trăm, không? (FR-38)
2. Danh sách cuối cùng các vai trò và nhánh, cùng giá trị θ_core và θ_common, sau khi hiệu chỉnh ở Sprint 2. (FR-7, FR-9)
3. 4–5 vai trò mục tiêu nào có đồ thị học trước – học sau khi công khai? (FR-18)
4. Tỷ giá USD cố định dùng giá trị nào, và bao lâu cập nhật một lần? (FR-8)
5. Kết quả xin phép ITviec, TopCV và tác giả repo gốc. Kết quả sẽ quyết định công tắc của từng nguồn. (§6.1, §6.2)
6. Ai kiểm duyệt danh mục tài liệu, và bao lâu kiểm tra link chết một lần? (FR-23)
7. **Thứ tự ưu tiên của các FR trong 8 tuần.** PRD chưa có lằn ranh cắt giảm cho cả bộ FR. FR-48 đã chốt là P1 ở §8.1, không xếp lại ở bước này. Các FR còn lại cần gắn mức:
   - P0: bắt buộc cho Review giữa kỳ;
   - P1: bắt buộc trước khi công khai;
   - P2: làm nếu kịp.

   Làm ở bước chia epic, hoặc trước đó.
8. **SM-1 nên đếm kỹ năng cốt lõi hay mọi khoảng trống kỹ năng?** Ở cấp Intern/Fresher/Junior, nhóm cốt lõi rất ít: ví dụ Backend chỉ có Java, SQL, Python. Phần lớn sinh viên đã có những kỹ năng này, nên SM-1 có thể khó đạt vì lý do định nghĩa, không phải vì sản phẩm. (SM-1)
9. **Có nên chuyển phần so sánh mù lên ngay sau modal đầu phiên, trước khi người thử dùng sản phẩm?** Sau 15 phút dùng thử, người thử có thể nhận ra văn phong của Hải Đồ IT, nên phép so sánh không còn hoàn toàn mù. (FR-43, FR-44, SM-3)
10. **Có cần một bộ chuẩn nhỏ gồm khoảng 20 CV** (của thành viên nhóm và bạn bè, có đồng ý) để đặt ngưỡng chất lượng cho bộ đọc CV không? Hiện bộ chuẩn 200 bản chỉ có JD, còn SM-10 chỉ là cận trên. (FR-12)
11. **Ngưỡng của D4 có nên nâng lên** (ví dụ ≥ 3 lần đăng lại trong 90 ngày, gần với báo cáo nghiên cứu) không, khi đã có đủ lịch sử snapshot? (FR-31)
12. **Số lần lấy mẫu bootstrap (B = 1.000) có đủ nhanh để chạy trong bước tính hằng đêm không?** Cần đo thời gian chạy ở Sprint 2 trên số ô thống kê thật. Nếu quá chậm, hai hướng: giảm B, hoặc chỉ tính khoảng tin cậy cho các ô mà người dùng thật sự xem. (FR-9)

## 11. Danh sách giả định

- §9 SM-5: mục tiêu ≥ 1.500 tin mới phụ thuộc vào số nguồn còn bật sau khi rà soát pháp lý.
- FR-1: ngưỡng báo động "số tin của một nguồn giảm quá 50% so với trung bình 7 ngày".
- FR-10: giới hạn CV 5 MB `[đã chốt, giữ ở đây để tra cứu]`.
- §6.4: trần chi phí vận hành sau bảo vệ dưới 5–10 USD/tháng.