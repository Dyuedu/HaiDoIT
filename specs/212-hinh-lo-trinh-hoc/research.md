# Research: Hình response của lộ trình học và dữ liệu giả

## Quyết định

- Một response chứa đủ cho #121 và #122: `entry_cell_id` cho số tin entry-level (#221), `have_on_path` và `path_size` cho "N of M" (#220), `current_stage` cho "đánh dấu đã có thì chặng sau lên" (#121). `have` đi lên chỉ dưới dạng `?have=a,b,c` (AD-22).
- **Hợp đồng cho #213**: chặng là thuộc tính của nút kỹ năng (đồ thị đã rà soát cho `stage`), không tính lại theo `have`. Lọc theo `have` không đổi thứ tự; `current_stage` chỉ là chặng đầu còn kỹ năng chưa có.
- Khóa xếp trong chặng: (nhóm, tỷ lệ giảm dần, mã A–Z) theo FR-22.

## Cách các repo công khai làm

- [kamranahmedse/developer-roadmap @ 01df46b](https://github.com/kamranahmedse/developer-roadmap/tree/01df46b9a27762e8dfafaecaa6ecfb8ed10fa870/roadmaps/backend): roadmap Backend là đồ thị nút và cạnh, nội dung từng nút là một file markdown kèm link tài liệu. Lấy ý "mỗi nút một mô tả ngắn và link miễn phí" và việc chặng là thuộc tính của nút. Không lấy: đồ thị vẽ tay cho người đọc, không có tỷ lệ xuất hiện, không có thứ tự xác định theo khóa, nhiều nút là đề mục chứ không phải mã kỹ năng; kho không có API response.
- [KonstantinosPetrakis/esco-skill-extractor @ cf2877d](https://github.com/KonstantinosPetrakis/esco-skill-extractor/commit/cf2877d462f99a4435df3faf3d6937e1859f6e3f): trích kỹ năng ESCO từ văn bản. ESCO có quan hệ kỹ năng thiết yếu hoặc tùy chọn giữa nghề và kỹ năng. Không lấy: thư viện chỉ trích kỹ năng, không dựng thứ tự học; quan hệ ESCO không có chặng; bộ mã ESCO khác bộ mã snake_case của dự án (#205).
- Tìm "skill prerequisite graph learning path" trên GitHub không thấy kho công khai nào trả một lộ trình đã xếp kèm số; hình response là tự đặt theo AD-17.

## Đợt 2 (sửa theo review)

- Link tài nguyên đã kiểm bằng `curl -sIL`: JUnit chuyển sang `docs.junit.org/current/user-guide/`; Linux Journey chuyển sang trang bán khóa học nên đổi sang hướng dẫn dòng lệnh của Ubuntu; `restfulapi.net` đổi sang MDN (Tổng quan HTTP); ETL dùng hướng dẫn pipeline của Apache Airflow (mã nguồn mở, trung lập); kho dữ liệu dùng bài Wikipedia; AWS dùng trang Bắt đầu với Amazon S3 của tài liệu AWS (miễn phí, chính thức). Link Node.js và Spring ghi theo đích sau chuyển hướng.
- FR-19 (`_bmad-output/planning-artifacts/epics.md`) giữ quay về trong vai trò; bản giả đợt 1 trỏ data_engineer sang ô mọi vai trò là sai và đã bỏ.
- Quy tắc kiểm lời dẫn (FR-23) nay ở một hàm `haido_core/vocab/prepared_text.py`. **#138 nên dùng lại hàm này** cho cổng CI thay vì viết quy tắc riêng. Số viết bằng chữ ngoài phạm vi.

## Dữ liệu giả

- Mã kỹ năng chỉ lấy từ `haido_core/vocab/skills_seed.json`. Bản mồi thiếu `spark`, `airflow`, `pandas`. **#96 (từ vựng v1) nên thêm ba mã này**; bản giả tạm thay `pandas` bằng `data_analysis`, `spark` bằng `deep_learning` (ai_ml) và `databricks` (data_engineer), `airflow` bằng `etl`.
- Mã cũ kiểu `spring-boot` trong `skill_rates` giả đổi sang snake_case theo #205.
