# Research: tỷ lệ kỹ năng theo nhóm

Ngày 16/11/2026.

## lukebarousse/Python_Data_Analytics_Course

- Link: https://github.com/lukebarousse/Python_Data_Analytics_Course/blob/efeea590e6eb00b57690d3320ddbc3e354117870/3_Project/2_Skill_Demand.ipynb
- Cách làm: `explode('job_skills')`, đếm theo (chức danh, kỹ năng), chia cho tổng số tin của chức danh (`skill_percent = skill_count / jobs_total * 100`).
- Lấy: mẫu số là số tin của nhóm, không phải số lượt nhắc; tử số đếm tin, nên lượt nhắc lặp không tăng số.
- Không lấy: bảng thưa, chỉ có kỹ năng xuất hiện (AD-5 cấm: kỹ năng thiếu hàng rơi khỏi mẫu số); xử lý bằng pandas trong notebook, còn đây là tập hợp trong bộ nhớ ở bước `aggregate`; chia theo chức danh nguyên văn, còn đây theo ô đã phân loại.

## usail-hkust/Skill-Demand-Supply-Joint-Prediction

- Link: https://github.com/usail-hkust/Skill-Demand-Supply-Joint-Prediction/tree/80558582e892dac6b0aa6d9cc84ecdf7129bcd4f
- Cách làm: dự báo cầu, cung kỹ năng bằng mạng đồ thị (bài arXiv 2401.17838).
- Lấy: không lấy gì cho bảng này.
- Không lấy: mô hình dự báo; issue chỉ cần tần suất đếm được, không dự báo.

## Quyết định rút ra

Bảng dày theo (ô × từ vựng), tử số đếm cụm, mẫu số là `n` của `stat_cells`; nhóm theo θ tính lúc đọc (`>=`, theo PRD FR-9, khởi tạo 30% và 10%).
