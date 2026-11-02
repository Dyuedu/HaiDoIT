---
title: "Addendum: Product Brief Hải Đồ IT"
created: 2026-11-02
updated: 2026-11-02
---

# Addendum: chi tiết dành cho PRD, kiến trúc và lập kế hoạch sprint

## 1. Kế hoạch 8 sprint (đã chốt)

| Sprint | Tuần | Mục tiêu | Có gì để demo |
|---|---|---|---|
| 1 | 2–8/11 | Kế hoạch (brief → PRD → kiến trúc). Làm sạch dữ liệu, **bật snapshot hằng ngày**. Khung repo, Compose, CI. Bộ từ vựng kỹ năng v0. Gửi email xin phép ITviec, TopCV và tác giả repo gốc | Pipeline chạy mỗi đêm |
| 2 | 9–15/11 | Bộ máy kỹ năng: JD/CV → kỹ năng chuẩn hóa; 200 JD gán nhãn tay (kappa trên 50 JD). Bảng cốt lõi / thường gặp / riêng lẻ theo vai trò. Đồ thị "học trước" và danh mục khóa học cho Backend và Data/AI; giảng viên hướng dẫn rà soát đồ thị | Số đo precision/recall |
| 3 | 16–22/11 | **Vertical slice Cố vấn:** tải CV → khoảng trống kỹ năng → lộ trình học cho 2 vai trò, giao diện đồ thị cơ bản | Luồng demo chính, dùng cho Review giữa kỳ (22–28/11) |
| 4 | 23–29/11 | Soi tin: phần so với hồ sơ (dùng lại bộ máy kỹ năng) + phần so với thị trường (phân vị, chất lượng JD, dấu hiệu cần kiểm tra) | Soi tin hoàn chỉnh |
| 5 | 30/11–6/12 | Bản đồ 3D theo tỷ trọng; thêm 2–3 vai trò cho lộ trình học; **công khai** | Bản đồ + link dùng thử |
| 6 | 7–13/12 | Insights cắt ngang; lộ trình học chung khi không có CV; bắt đầu thử nghiệm người dùng | Insights |
| 7 | 14–20/12 | Thử nghiệm 30–50 người (60% trong trường / 40% ngoài trường), đo, sửa lỗi; thực nghiệm độ nhất quán của chatbot | Số liệu kiểm chứng |
| 8 | 21–27/12 | Code freeze, hoàn thiện báo cáo, slide, tập dượt demo, dự phòng | — |

Báo cáo SEP490 được viết cuốn chiếu theo từng sprint. Nộp báo cáo và pre-defense khoảng 20–25/12; bảo vệ cuối tháng 12/2026 hoặc đầu tháng 01/2027.

## 2. Quyết định kiến trúc đã chốt trong buổi làm brief

- **Không dùng Neo4j độc lập.** Phép thử "3 câu hỏi đòi duyệt nhiều tầng" chỉ ra đúng một bài toán đồ thị thật: duyệt DAG "học trước – học sau" (khoảng 100–300 nút). Câu hỏi "chuyển ngành" thực chất là hiệu tập hợp rồi sắp xếp topo. Câu hỏi "kỹ năng bản lề" là bài toán đếm trên quan hệ tin–kỹ năng (`GROUP BY`).
- **PostgreSQL là nguồn sự thật duy nhất** (các bảng `skills`, `skill_edges`). Đồ thị được nạp vào bộ nhớ (ví dụ NetworkX) khi tính lộ trình học. Apache AGE là phương án dự phòng nếu cần trình bày truy vấn Cypher cho hội đồng.
- **Hai loại cạnh tách biệt:**
  - `PREREQUISITE`: soạn tay, quyết định thứ tự học;
  - tần suất xuất hiện và đồng xuất hiện từ JD: quyết định mức ưu tiên.

  Không trộn hai loại trong cùng một phép tìm đường có trọng số.
- **Thuật toán lộ trình học:**
  1. lấy tập kỹ năng của vai trò mục tiêu, lọc theo ngưỡng tần suất;
  2. trừ đi các kỹ năng người dùng đã có;
  3. thêm các kỹ năng tổ tiên còn thiếu trên DAG;
  4. sắp xếp topo;
  5. gắn nhãn mức ưu tiên.

  Kết quả là một khung JSON cố định. LLM chỉ viết lời dẫn cho khung này. Link tài liệu chỉ lấy từ danh mục đã kiểm duyệt. Bỏ khái niệm "GraphRAG".
- **Pipeline:** brief chỉ ghi ở mức năng lực (tự động hằng ngày, có giám sát dòng dữ liệu và lịch sử chạy). **Airflow hay Dagster** sẽ quyết ở bước kiến trúc.
  - Airflow: hội đồng nhận ra tên ngay, nhưng nặng (khoảng 4 GB RAM) và không chạy trực tiếp trên Windows.
  - Dagster: nhẹ hơn, mô hình asset vẽ được sơ đồ dòng dữ liệu.
- **Không có tài khoản:**
  - lưu kết quả trong `localStorage`;
  - link chia sẻ có URL chỉ chứa mã kỹ năng;
  - tải kết quả về máy (in trình duyệt ra PDF là phương án rẻ nhất);
  - server không lưu CV gốc hay hồ sơ.
- **Công tắc theo từng nguồn:** pipeline của bản công khai chỉ bật những nguồn hợp lệ. Dữ liệu của nguồn chưa được phép chỉ được dùng làm bộ kiểm tra nội bộ.

## 3. Stack: các phương án đã cân nhắc (chưa chốt, quyết ở bước kiến trúc)

- **Phương án ban đầu của nhóm:** Airflow + LLM + PostgreSQL + Neo4j + GraphRAG. Neo4j và GraphRAG đã bị loại, xem mục 2.
- **Phương án Claude đề xuất trước buổi làm brief, tối ưu cho 3 người × 8 tuần:**
  - Python package `haido_core` dùng chung cho pipeline và API;
  - FastAPI + SQLAlchemy 2 + Alembic;
  - PostgreSQL 16 + pgvector, embedding bge-m3 chạy local;
  - Next.js + deck.gl (bản đồ 3D) + React Flow (lộ trình học);
  - Claude API (Batch API + structured outputs; đọc CV PDF trực tiếp);
  - một VPS, Docker Compose + Caddy.
- **Mô hình cho bước trích xuất:** sau khi vận hành ổn định, sẽ chuyển sang mô hình nhỏ, rẻ, nhưng chỉ sau khi đã đo chất lượng trên bộ 200 JD.

## 4. Phương pháp đo (chi tiết cho chương Thực nghiệm)

- **Loại tin trùng lặp:**
  - gán nhãn khoảng 100 cặp tin có độ giống nhau cao, báo cáo precision/recall của bước dedup;
  - tìm thủ công bản trùng của 100 tin ngẫu nhiên trong bảng phân tích để ước lượng tỷ lệ trùng còn sót.
- **Trích xuất kỹ năng:** bộ chuẩn 200 JD. Mỗi JD có 2 người gán nhãn, tính Cohen's kappa trên 50 JD chung. Mục tiêu P ≥ 85%, R ≥ 80%.
- **Ảo giác của LLM:**
  - thứ tự lộ trình học được đảm bảo bằng kiểm thử tự động;
  - lời dẫn được kiểm bằng cách rà soát một mẫu;
  - link tài liệu không thể bị bịa vì chỉ lấy từ danh mục.
- **Thử nghiệm người dùng:**
  - phiên khoảng 15 phút, form ẩn danh;
  - trước phiên, người dùng tự liệt kê 3 kỹ năng cần học nhất;
  - với mỗi kỹ năng hệ thống báo thiếu, người dùng xác nhận đó là thật (câu xác nhận này cũng đo độ chính xác đọc CV ngoài thực tế);
  - so sánh mù kết quả của Hải Đồ IT với câu trả lời ChatGPT chuẩn bị sẵn;
  - nếu kịp, hỏi lại sau 7 ngày.
- **Thực nghiệm phụ:** hỏi cùng một câu về lộ trình học nhiều lần trên 2–3 chatbot, đo mức độ lệch của thứ tự học.

## 5. Dữ liệu đầu vào hiện có (2026-11-02)

- `scraper/data/step-07-jev-extracted.jsonl`: 3.469 tin IT, ảnh chụp chủ yếu tháng 9–10/2026, từ 5 nguồn (TopCV khoảng 38%).
- **Crawler mới:**
  - CareerLink: khoảng 459 tin;
  - ITNavi: khoảng 486 tin;
  - Zalo Careers: 117 tin, gồm cả tin không phải IT;
  - MoMo Careers: 102 tin, mặc định lấy 40 tin của Khối Công nghệ và Khối Sản phẩm.

  Các crawler mới không đăng nhập, tôn trọng `robots.txt`, giãn cách request và dừng khi gặp captcha.
- **Giới hạn của dữ liệu:**
  - chỉ khoảng 24% tin có lương dạng số;
  - Đà Nẵng chỉ có 64 tin;
  - Frontend 46 tin, Mobile 57 tin;
  - nhóm "Other" có 604 tin, cần tách riêng nhóm Embedded.

## 6. Chi tiết chuyển từ brief khi rút gọn (2026-11-02)

- **Lý do ưu tiên Soi tin và danh sách khoảng trống kỹ năng trên điện thoại:** phần lớn người dùng ngoài trường sẽ bấm link từ Facebook trên điện thoại. Đồ thị lộ trình học và bản đồ 3D được thu gọn, kèm gợi ý mở trên máy tính.
- **Link chia sẻ:** URL chỉ chứa mã kỹ năng, không chứa thông tin cá nhân.
- **Chỉ số phụ cho giả thuyết "thiếu kỹ năng cốt lõi":** ghi riêng tỷ lệ người dùng phát hiện **kỹ năng đã có nhưng quên ghi vào CV**. Đây là bằng chứng trực tiếp cho nhánh "có kỹ năng nhưng CV không thể hiện".
- **Mẫu thử ngoài trường:** tiếp cận qua các bài phân tích dữ liệu đăng lên cộng đồng sinh viên IT và fresher, kèm link dùng thử không cần đăng ký. Kết quả báo cáo riêng cho nhóm trong trường và nhóm ngoài trường.
- **Vì sao chi phí vận hành sau bảo vệ thấp:** chỉ có một cơ sở dữ liệu (không dùng Neo4j), và bước trích xuất hằng ngày chuyển sang mô hình nhỏ sau khi đã được kiểm chứng trên bộ 200 JD.
- **Các mục cụ thể của Insights:** cửa vào cho người mới (tỷ lệ tin nhận fresher/junior theo vai trò), bộ kỹ năng hay đi cùng nhau, kỹ năng tăng dần từ Junior lên Senior, khác biệt giữa các thành phố, ngành và nhà tuyển dụng nổi bật.
- **Nguồn số liệu ở phần Vấn đề** (lấy từ báo cáo "Hải Đồ IT khoảng trống"):
  - JobOKO: khoảng 580.000 tin, tháng 1–10/2025;
  - ITviec Vietnam IT Market Insight, quý 1/2025;
  - AIES 2026: 165.000 câu trả lời của 11 mô hình;
  - ITviec AI Match: tính năng phục vụ nhà tuyển dụng.
