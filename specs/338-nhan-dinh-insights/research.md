# Research: Cách dashboard thị trường việc làm thêm nhận định

## Repo tham khảo

### 1. blessen5/job-analysis — Evidence Engine (template-based)

- **Link**: https://github.com/Blessen-P-Shaju/job-analysis (commit trên `main`)
- **Cách làm**: Mỗi insight là một object có `title`, `statement` (câu dạng template: "X appeared in Y% of postings for Z role, compared with W% overall"), `evidence_strength` (Strong/Moderate/Descriptive), `sample_size`. Frontend lọc theo tier.
- **Lấy gì**: Cấu trúc insight object (statement + evidence tier), cách xếp hạng insight theo độ tin cậy.
- **Không lấy**: Phần kiểm định thống kê (Mann-Whitney, Chi-Square) — dữ liệu Hải Đồ chưa cần mức này.

### 2. bhaavi1207-cyber/job-market-insights — KPI cards

- **Link**: https://github.com/bhaavi1207-cyber/job-market-insights
- **Cách làm**: Python pipeline tạo `insights.json`, React frontend hiển thị stat cards. Text hardcoded trong JSX, không có câu narrative tự động.
- **Lấy gì**: Không — cách hiện tại của Hải Đồ đã tốt hơn (câu sinh từ data).
- **Không lấy**: Text cứng không cập nhật theo data.

### 3. AmirhosseinHonardoust/AI-Report-Factory — LLM-generated

- **Link**: https://github.com/AmirhosseinHonardoust/AI-Report-Factory
- **Cách làm**: Dùng LLM sinh báo cáo Markdown/HTML, mỗi biểu đồ kèm đoạn phân tích.
- **Không lấy**: Phụ thuộc API key, latency cao, không phù hợp cho trang tải nhanh. Hải Đồ có thể tính sẵn nhận định ở phía client.

## Kết luận

Áp dụng mô hình **template-based** — mở rộng hàm `takeaways()` hiện tại:

1. Thêm câu **hướng dẫn hành động** dựa trên so sánh data (entry_share, years, butterfly).
2. Thêm nhận định **theo ngữ cảnh** cho mục "Người mới" và "Kỹ năng theo vai trò".
3. Dữ liệu đã có sẵn trong API response — không cần LLM, không cần API mới.
4. Tuân thủ DEC-6: câu không chứa số; số đứng riêng ở từng dòng.
