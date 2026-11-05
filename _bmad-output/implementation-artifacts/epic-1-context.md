# Epic 1 Context: Thấy nhu cầu thị trường trên bản đồ

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Sinh viên mở ứng dụng và thấy Hà Nội, TP.HCM, Đà Nẵng chiếm bao nhiêu phần tin của vai trò đang chọn, mỗi số kèm cỡ mẫu, nguồn và ngày snapshot; đêm pipeline lỗi thì bản đồ vẫn mở trên snapshot gần nhất. Epic này dựng khung hệ thống và toàn bộ bên ghi mà các epic sau đọc lại, nên quyết định độ tin cậy của mọi con số. Lát cắt chạy thật đầu tiên là 1.15 trên dữ liệu thật, xong ngày 08/11, chưa cần 3D và LLM.

## Stories

- Story 1.1: Mở khung Hải Đồ IT trên máy dev
- Story 1.2: Chạy một lượt thu thập lịch sự
- Story 1.3: Lưu tin đã xóa liên hệ người đăng
- Story 1.4: Chốt snapshot và vòng đời tin
- Story 1.5: Bỏ bản sao trong cùng nguồn trước khi gọi mô hình
- Story 1.6: Trích dữ kiện JD theo lô
- Story 1.7: Quy lượt nhắc về mã kỹ năng
- Story 1.8: Gom tin trùng giữa các nguồn
- Story 1.9: Gán vai trò, nhánh, cấp bậc và thành phố
- Story 1.10: Quy lương về VND của snapshot
- Story 1.11: Tính tỷ lệ và nhóm kỹ năng cho từng ô
- Story 1.12: Tính phân vị có khoảng tin cậy tất định
- Story 1.13: Đọc số qua API kèm cỡ mẫu
- Story 1.14: Nhập bộ dữ liệu nền một lần
- Story 1.15: Xem tỷ trọng ba thành phố
- Story 1.16: Mở bảng chi tiết một thành phố
- Story 1.17: Xoay bản đồ 3D
- Story 1.18: Báo khi một nguồn gãy hoặc sụt tin
- Story 1.19: Sao lưu snapshot ra ngoài VPS
- Story 1.20: Gán vai trò, cấp bậc và thành phố bằng luật tất định
- Story 1.21: Tính và đọc tỷ trọng thành phố kèm cỡ mẫu

## Requirements & Constraints

- **Thu thập lịch sự:** kiểm `robots.txt`, User-Agent trung thực có liên hệ, giãn cách cố định, không đăng nhập; gặp 403/429/captcha thì dừng nguồn đó tới lượt sau. Một nguồn lỗi không dừng nguồn khác. LinkedIn tắt vĩnh viễn; TopCV chạy tay, không chặn công bố snapshot.
- **PII:** xóa tên, email, điện thoại, Zalo của người đăng trước mọi lệnh ghi; nhật ký chỉ ghi loại đã xóa.
- **Con số:** mọi số hiển thị kèm n, nguồn, ngày snapshot. Dưới ngưỡng thì "chưa đủ dữ liệu"; ngoại lệ duy nhất là tỷ trọng cột bản đồ.
- **Tỷ trọng:** phần của thành phố trong tổng tin toàn quốc của vai trò đang chọn. Ba cột + "Khác" + "không xác định" = 100%; hai phần sau không phải cột và không gộp vào nhau.
- **Không được cắt dù trượt lịch:** nhịp thu hằng ngày, sao lưu, bộ chuẩn 200 JD (chỉ lấy từ văn bản gốc mới thu, không lấy từ dữ liệu nền).
- **Mốc:** P0 phục vụ review giữa kỳ 22–28/11; ngày 20/11 đóng băng snapshot review.

## Technical Decisions

- **Phụ thuộc một chiều:** `web` → `haido_api` → `haido_core` → `domain`; `haido_pipeline` → `haido_core`. `web` không nối Postgres; `domain` là hàm thuần.
- **Registry đóng tám phép** ở `haido_core/domain/REGISTRY.md`: mỗi phép một chữ ký, gọi được cho một đối tượng và một lô, không cài lại nơi khác.
- **Thứ tự một đêm là bất biến:** crawl → redact → ingest → dedupe trong nguồn → fetch_details → extract → mapping → cluster chéo nguồn → classify → normalize_salary → stat_job_lifecycle → aggregate → publish. Mỗi bước là hàm trong `haido_core/steps/`, gọi được bằng CLI, không import Dagster.
- **Hai nhịp:** thu quan sát chạy tự động hằng ngày, không phụ thuộc từ vựng hay `stat_*`. Tính tổng hợp chạy bằng CLI; tầng đọc không phân biệt snapshot chạy tay với chạy Dagster.
- **Cầu nối C-11:** trong lúc chuyển, pipeline ở `scraper/` ghi JSONL rồi `redact` và `ingest`; hết hạn khi 1.2 và 1.3 đưa các bước vào `haido_core/`. Đích của mỗi nguồn là `crawl(cfg) -> Iterator[RawJob]`, giữ nguyên `parse_*`, mọi request qua cổng `polite`, kể cả crawler trình duyệt.
- **Snapshot:** `snapshot_id` là `YYYY-MM-DD` theo `Asia/Ho_Chi_Minh`; kết thúc `published` hoặc `partial`, cả hai đều đọc được. Hàng đã công bố không sửa, không xóa; tính lại là sinh snapshot mới. `job_observations` chỉ thêm.
- **Trích xuất:** LLM chỉ trả lượt nhắc nguyên văn và trường có kiểu kèm đoạn nguồn; không trả mã kỹ năng, nhãn hay số tự tính. Quy chuẩn là hàm tất định trong `domain`.
- **Tổng hợp:** `aggregate` đếm `job_clusters`, không đếm bản ghi thô. `stat_cells` khóa theo snapshot, vai trò, nhánh, cấp bậc, phạm vi; quay về chỉ đi trong cùng phạm vi.
- **Tầng đọc:** `haido_api` không tổng hợp trên `job_*`; chỉ `haido_core/steps/` ghi bảng thị trường. Response có số là `{data, meta}`, mỗi số là `Stat {value, kind, display, cell_id}` với `cell_id` có trong `meta.cells`. Che số do `domain.display_policy.suppression_for` quyết; chỉ tỷ trọng cấu phần được `low_sample_shown`. Lỗi là `{error: {code, message, snapshot_date}}`, `message` tiếng Việt.
- **Quy ước:** route `/api/v1/<danh-từ-kebab>`. Tỷ lệ là số thực 0–1, chỉ làm tròn ở hiển thị. Vai trò, nhánh, cấp bậc, thành phố là enum snake_case trong `domain`. θ, n = 30, cửa sổ 60 ngày, tỷ giá, công tắc nguồn nằm trong cấu hình có phiên bản.
- **Nợ tạm Sprint 1:** mỗi tin là một cụm (đếm trùng chéo nguồn tới khi có 1.5 và 1.8); luật gán vai trò chưa đo độ chính xác (đo ở 1.9).
- **Chưa chốt, đừng tự quyết:**
  - Kho đang là Postgres trên Supabase, khác Postgres 18 tự chạy trong thiết kế.
  - Bước trích xuất hiện tại trả nhãn phân loại, trái quy tắc trên.
  - Bảng `jobs` hiện ghi đè bản mới nhất, chưa có snapshot bất biến.
  - Cổng CI tìm model `Envelope` trong `haido_core/domain/`, còn thiết kế C-1 đặt ở `haido_api/schemas/`; C-1 tạm dừng tới khi chốt.
  - Danh sách vai trò/nhánh cuối, θ sau Sprint 2, tỷ giá USD.

## UX & Interaction Patterns

- Mở ứng dụng vào Bản đồ, vai trò "Tất cả". Ba lối trên cùng số liệu: 3D, Biểu đồ 2D, Bảng. Khi 1.17 chưa xong: mở lối 2D, nút 3D tắt, chú thích "Bản đồ 3D sắp có". Không có WebGL thì tự chuyển 2D hoặc bảng, không hiện màn hình lỗi.
- Đà Nẵng luôn có mặt. Cột n < 30 vẫn vẽ đúng tỷ trọng, mờ, nhãn đứng "Cỡ mẫu nhỏ (n = X < 30): số liệu chỉ để tham khảo"; phần trăm chỉ hiện khi trỏ, chạm hoặc focus. "Khác" nằm ở chú thích.
- Luôn nhìn thấy, kể cả trên điện thoại: nguồn đang bật, ngày snapshot và ba lưu ý: tin tuyển dụng không đồng nghĩa vị trí đang cần người; dữ liệu nghiêng về thành phố lớn và công ty lớn; con số lương chỉ phản ánh tin có công bố lương. Không dùng ba câu khác trên artboard.
- Điện thoại: danh sách thành phố và thanh tỷ trọng, kèm gợi ý mở trên máy tính.
- Bảng: ô n < 30 chỉ ghi "chưa đủ dữ liệu". Cột số canh phải, JetBrains Mono.
- Token ở `DESIGN.md`. Vùng bấm tối thiểu 44px, kể cả cụm 3D / 2D / bảng mà artboard vẽ 38px. Ngưỡng nhóm trên giao diện là 30% và 10%, không theo 60/30 của artboard.

## Cross-Story Dependencies

- **Đường găng Sprint 1:** 1.1 → C-11 → 1.20 → 1.21 → 1.15. 1.15 dựng trước trên endpoint giả của C-1 rồi nối vào 1.21, route và schema giữ nguyên. `skill_rates` vẫn là bản giả tới 1.13.
- **Số story không phải thứ tự làm.** Sprint 1: 1.1, 1.4, 1.20, 1.21, 1.15. Sprint 2: 1.2, 1.3, 1.5, 1.6, 1.7, 1.9, 1.11, 1.14, 1.19. Sprint 3: 1.8, 1.13. Sprint 4: 1.10, 1.12, 1.18. Sprint 5: 1.16, 1.17.
- **Chuỗi bên ghi:** 1.8 cần tập kỹ năng của 1.7. 1.9 mở rộng phép phân loại của 1.20. 1.16 cần tỷ lệ kỹ năng. 1.17 mở bảng của 1.16. Bộ chuẩn 200 JD chỉ có sau khi nhịp thu đã chạy.
- **Với epic khác:** lộ trình của Epic 2 đọc bảng tỷ lệ của 1.11. Soi tin dùng lại phép phân loại, mapping và so khớp tin.
</content>
