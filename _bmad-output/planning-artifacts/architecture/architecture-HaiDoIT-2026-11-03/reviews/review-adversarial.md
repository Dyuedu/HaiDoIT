---
title: 'Rà soát đối kháng — ARCHITECTURE-SPINE Hải Đồ IT'
type: adversarial-review
target: '_bmad-output/planning-artifacts/architecture/architecture-HaiDoIT-2026-11-03/ARCHITECTURE-SPINE.md'
sources:
  - '_bmad-output/planning-artifacts/prds/prd-HaiDoIT-2026-11-02/prd.md'
  - '_bmad-output/planning-artifacts/prds/prd-HaiDoIT-2026-11-02/addendum.md'
  - '_bmad-output/planning-artifacts/briefs/brief-HaiDoIT-2026-11-02/addendum.md'
reviewer-stance: adversary
created: '2026-11-03'
---

# Rà soát đối kháng — Architecture Spine Hải Đồ IT

## 0. Cách đọc tài liệu này

Tôi không đi tìm lỗi chính tả, cũng không tranh luận về stack. Tôi đóng vai **kẻ phá hoại thiện chí**: giả định 3 dev đọc spine này, mỗi người nhận một story khác nhau, **không ai nói chuyện với ai**, và mỗi người **tuân thủ từng chữ của mọi AD**. Rồi tôi tìm những cặp story mà kết quả ghép lại **không khớp nhau**.

Mỗi lỗ hổng dưới đây có dạng:

- **Cặp đơn vị** — hai story (hoặc hai dev) cụ thể, có mốc sprint theo kế hoạch 8 sprint đã chốt;
- **Cả hai đều hợp lệ theo** — AD nào cho phép, và tại sao chữ của AD đó không loại được bên nào;
- **Lệch nhau cụ thể** — hiện tượng người dùng hoặc hội đồng nhìn thấy;
- **Vì sao kiểm thử hiện có không bắt được** — đây là phần quan trọng nhất: một lỗ hổng chỉ đáng bịt khi nó **im lặng**;
- **Đề xuất** — một câu Rule cưỡng chế được (có thể viết thành kiểm thử, ràng buộc DB, hoặc cổng CI).

Tổng: **18 lỗ hổng** — 5 critical, 8 high, 5 medium.

Một ghi chú về mức độ: spine này đã **tốt hơn trung bình rất nhiều**. AD-2, AD-5, AD-6 và AD-7 đã bịt đúng bốn chỗ mà một đồ án SEP490 thường vỡ. Những lỗ hổng dưới đây nằm ở **tầng dưới** của chính các AD đó: AD nói "chỉ có một hàm", nhưng không nói **hàm đó nhận đối số gì**; AD nói "phải có `meta`", nhưng không nói **`meta` có hình dạng gì**. Đó chính là nơi ba người xây ba thứ khác nhau mà vẫn đúng luật.

---

## 1. Bảng tổng hợp lỗ hổng

| # | Lỗ hổng | Hướng tấn công | Mức | AD bị xuyên |
|---|---|---|---|---|
| G-01 | Hình dạng của `meta` không được định nghĩa, chỉ có danh sách khóa | hình dạng dữ liệu dùng chung | high | AD-17 |
| G-02 | Không ai sở hữu định nghĩa "dân số của ô thống kê" (60 ngày, đếm cụm) | hai chủ sở hữu | high | AD-5, AD-6, AD-16 |
| G-03 | `stat_percentile` không bắt buộc có `n_with_value`; FR-30 có ba n khác nhau | hình dạng dữ liệu | **critical** | AD-5, AD-17 |
| G-04 | Ai sinh `snapshot_id`; một nguồn lỗi thì có snapshot không | thứ tự / tất định | **critical** | AD-4, AD-15 |
| G-05 | FR-4 và FR-32 là hai bản cài đặt của cùng một vị ngữ so khớp | hai đường đột biến | high | (không AD nào phủ) |
| G-06 | FR-29 đòi ghi danh sách chờ từ tin dán, AD-11 cấm mọi lệnh ghi | hai chủ sở hữu + riêng tư | **critical** | AD-11, Quy ước đột biến |
| G-07 | AD-17 (`n<30` ⇒ `data = null`) mâu thuẫn trực tiếp với FR-33 (cột Đà Nẵng luôn vẽ) | ngưỡng n=30 | **critical** | AD-17, AD-5 |
| G-08 | Hàm chọn ô của AD-6 có tham số `scope`, nên gọi được cho ô thành phố — mà chuỗi quay về không có bậc thành phố | thứ tự quay về | high | AD-6 |
| G-09 | "Lộ trình đã xếp thứ tự" không có hình dạng; `web/` phải tự dựng chặng để vẽ đồ thị | biên FE/BE | high | AD-7 |
| G-10 | Không AD nào nói `skills` là danh sách đóng; mã kỹ năng lạ sinh nút mồ côi | hình dạng mã kỹ năng | medium | AD-2, Quy ước mã kỹ năng |
| G-11 | Bảng `stat_*` không bắt buộc là con của `stat_cells`; hai dev hai head Alembic | di trú schema | high | AD-5, AD-6 |
| G-12 | AD-10 không phủ `n=30`, `60 ngày`, `5 điểm phần trăm`, `≥30 tin` của FR-7 | ngưỡng n=30 | high | AD-10 |
| G-13 | Quy ước route (chỉ 3 POST) **buộc** frontend tự tính mức khớp | biên FE/BE | **critical** | AD-7, Quy ước route |
| G-14 | Câu kết luận Insights: không nói ai lắp mẫu câu, nên ranh giới khoảng chạy sang TypeScript | thứ tự / tất định | high | AD-8, AD-5 |
| G-15 | `revalidate` nằm trong hay ngoài transaction công bố; danh sách path lấy từ đâu | thứ tự / tất định | medium | AD-4, AD-13 |
| G-16 | `is_eval` do ai đặt, và không AD nào buộc báo cáo phải lọc nó | hai chủ sở hữu | medium | AD-18 |
| G-17 | Nhãn nhóm kỹ năng không mang theo ô đã sinh ra nó | hình dạng dữ liệu | high | AD-2, AD-6 |
| G-18 | `anon_events` có hai đường ghi khả dĩ ⇒ đếm đôi hoặc đếm không | hai đường đột biến | medium | AD-11, FR-17 |

---

## 2. Các lỗ hổng, chi tiết

### G-01 — Hình dạng của `meta` không được định nghĩa, chỉ có danh sách khóa `[high]`

**Cặp đơn vị.**
- Story A (Sprint 4, dev B): "Soi tin — `GET /api/v1/jd-insight` trả phân vị, mức khớp, dấu hiệu".
- Story B (Sprint 5, dev C): "Bản đồ nhu cầu — `GET /api/v1/city-detail` trả cơ cấu vai trò và kỹ năng hàng đầu".

**Cả hai đều hợp lệ theo.** AD-17 nói `meta` phải "gồm `snapshot_date`, `stat_cell`, `n`, `fallback_label` (hoặc `null`), `sources[]`, `thresholds`". Đó là một **danh sách tên khóa**, không phải một schema. Không chữ nào trong spine nói:

- `stat_cell` là chuỗi (`"backend|java-backend|junior|national"`) hay đối tượng (`{role, branch, seniority, scope}`);
- `thresholds` là `{theta_core, theta_common}`, hay `{n_min: 30}`, hay mảng ngưỡng D1–D7;
- `sources[]` là mã nguồn (`["topcv", "careerlink"]`) hay tên hiển thị (`["TopCV", "CareerLink"]`);
- `snapshot_date` là ngày hiển thị hay chính `snapshot_id` (quy ước nói `snapshot_id` **là** ngày `YYYY-MM-DD`, nên hai khóa này trùng nghĩa mà vẫn khác tên — tự nó đã là một mời gọi lệch).

Dev B chọn `stat_cell` là chuỗi để in trực tiếp lên nhãn; dev C chọn đối tượng để lọc theo `role`. Cả hai qua AD-17.

**Lệch nhau cụ thể.** §5 NFR đòi **mọi** màn hình có số liệu phải in cỡ mẫu, nguồn, ngày, cộng lưu ý độ phủ. Đó là một component dùng chung hiển nhiên (`<DataProvenance meta={...} />`). Với hai hình dạng `meta`, component đó **không viết chung được**; nhóm sẽ có hai component, rồi FR-36 ("danh sách nguồn đang bật") in `"TopCV, CareerLink"` ở Bản đồ và `"topcv, careerlink"` ở Soi tin. Trên cùng một sản phẩm, hội đồng demo sẽ thấy hai cách gọi tên nguồn.

**Vì sao kiểm thử hiện có không bắt được.** AD-17 nói "Thiếu `meta` là lỗi schema, có kiểm thử hợp đồng chặn". Một kiểm thử *sự có mặt của khóa* xanh trên cả hai hình dạng. Kiểm thử hợp đồng duy nhất được spine yêu cầu chính là kiểm thử không phân biệt được hai thế giới này.

**Đề xuất — siết AD-17.**
> **Rule:** `meta` là **đúng một** model Pydantic `Meta` khai báo một lần tại `haido_api/schemas/meta.py`, với `stat_cell: StatCellRef{role, branch|null, seniority|null, scope}`, `thresholds: Thresholds{theta_core, theta_common, n_min}`, `sources: list[SourceCode]` (mã enum, không phải tên hiển thị), `snapshot_date: date`; mọi endpoint trả số **phải** trả đúng model đó, và một kiểm thử hợp đồng so **JSON Schema của `meta` giữa tất cả các endpoint có số và khẳng định chúng giống nhau từng byte**.

---

### G-02 — Không ai sở hữu định nghĩa "dân số của ô thống kê" `[high]`

**Cặp đơn vị.**
- Story A (Sprint 2, dev A): "bước `aggregate` tính `stat_cells`, tỷ lệ xuất hiện, nhóm kỹ năng".
- Story B (Sprint 5, dev C): "`stat_city_role` cho Bản đồ nhu cầu và Insights".

**Cả hai đều hợp lệ theo.** §3 có hai dòng tách rời nhau:
- *"Chỉ tính những tin có ngày thấy lần cuối trong vòng 60 ngày tính tới snapshot đang dùng."*
- FR-4: *"Mọi con số thống kê tính mỗi cụm đúng một lần."*

Spine **không nhắc cả hai**. AD-6 nói `stat_cells` lưu `n`, nhưng không nói `n` đếm gì. AD-16 chỉ nói `ingest` ghi vào `job_raw`. Vậy:
- `n` là số hàng `job_raw`, số hàng `jobs` (đại diện cụm), hay số `job_cluster`? AD-16 và ERD cho phép cả ba.
- Cửa sổ 60 ngày: dòng ấy nằm **dưới** gạch đầu dòng "Trong Cố vấn và Soi tin", **trên** gạch đầu dòng "Trong Bản đồ nhu cầu và Insights". Đọc là "áp cho mọi ô" hay "chỉ áp cho ô Cố vấn/Soi tin" đều đứng được về mặt văn bản.

Dev A đếm cụm có `last_seen_at` trong 60 ngày. Dev C đếm mọi tin từ đầu lịch sử (tự nhiên hơn cho câu "tỷ trọng của thành phố trong tổng số tin của vai trò").

**Lệch nhau cụ thể.** Insights "Cửa vào cho người mới" (tỷ lệ tin Junior theo vai trò) và Bản đồ "tỷ trọng Hà Nội trong vai trò Backend" chạy trên hai dân số khác nhau. Sau 3 tháng chạy pipeline, chênh lệch giữa "mọi thời" và "60 ngày" sẽ khoảng 2–3 lần. Hội đồng mở Bản đồ thấy *Backend toàn quốc 4.100 tin*, mở Cố vấn thấy *Backend × Junior toàn quốc n = 180*, và không ai trong nhóm giải thích được tại sao — vì chính nhóm không biết hai con số đếm hai thứ.

Phiên bản ác hơn: FR-33 có kết quả kiểm chứng *"tổng tỷ trọng của các cột cộng phần Khác bằng 100%"*. Kiểm thử đó **xanh** trên cả hai dân số, vì nó chỉ kiểm tính cộng trong nội bộ một bảng.

**Đề xuất — AD mới (AD-19).**
> **Rule:** Mọi `stat_cells.n` và mọi phép tổng hợp đếm **cụm tin** (`job_cluster`), đúng một lần mỗi cụm, và chỉ những cụm mà `last_seen_at` nằm trong `THRESHOLDS.recency_days` tính từ `snapshot_id`. Vị ngữ này tồn tại **đúng một lần**, trong hàm thuần `domain.population.is_in_cell_population(cluster, snapshot_id)`; không bước nào, không endpoint nào, không câu SQL nào được viết lại điều kiện ngày hay điều kiện cụm. `stat_cells.n` **luôn** là số cụm; số hàng `job_raw` không bao giờ là `n`, ở bất kỳ ô nào, kể cả ô thành phố × vai trò.

---

### G-03 — `stat_percentile` không bắt buộc có `n_with_value`; FR-30 có **ba** n khác nhau `[critical]`

**Cặp đơn vị.**
- Story A (Sprint 2, dev A): "bước `aggregate` — mốc phân vị + bootstrap CI (FR-9)".
- Story B (Sprint 4, dev B): "Soi tin — FR-30 phân vị so với thị trường, và D1/D3 (FR-31)".

**Cả hai đều hợp lệ theo.** AD-5 cho phép tầng phục vụ **một** phép lúc chạy: "đặt một giá trị của tin người dùng dán vào các mốc phân vị đã tính sẵn", và đọc theo khóa `(snapshot_id, stat_cell_id)`. AD-17 cho `meta` **một** trường `n`. ERD có `STAT_CELL ||--o{ STAT_PERCENTILE`, không nói `STAT_PERCENTILE` có cột `n` riêng.

Nhưng FR-30 đòi **ba** cỡ mẫu độc lập:
- `n` của ô (cho phân vị *số kỹ năng yêu cầu*, luôn hiển thị);
- *"ô thống kê có từ 30 tin **có số năm kinh nghiệm** trở lên"*;
- *"ô thống kê có từ 30 tin **có lương** trở lên"*, với kết quả kiểm chứng tường minh: *"Ngưỡng này đếm số tin **có trường đó**, không đếm toàn bộ tin của ô."*

Dev A hoàn toàn hợp lệ khi lưu `stat_percentiles(snapshot_id, stat_cell_id, measure, p25, p50, p75, p90, ci_low, ci_high)` và để `n` ở `stat_cells` — đúng chữ AD-5 và ERD. Dev B khi đó **không có đường nào** lấy "số tin có lương": đếm nó là một `COUNT(*)` trên bảng tin, mà AD-5 cấm `haido_api` chạy phép tổng hợp trên bảng tin tuyển dụng. Nên dev B làm điều hợp lệ duy nhất còn lại: dùng `meta.n` (n của ô) làm cổng.

**Lệch nhau cụ thể.** Ô `backend × mid × national` có `n = 120`, trong đó chỉ **12** tin có lương dạng số (addendum PRD: khoảng 76% tin không ghi lương — nên 12/120 là con số thực tế, không phải trường hợp bệnh lý). Dev B hiển thị *"lương của tin nằm ở phân vị 65%"* — một phân vị tính trên 12 tin, kèm `meta.n = 120`. Đây là **vi phạm trực tiếp kết quả kiểm chứng của FR-30** (*"Không phân vị lương nào được tính trên ô thống kê có dưới 30 tin có lương"*), và nó xảy ra **mà không bên nào phá một chữ nào của spine**.

Thêm một xung đột nữa, ngược chiều: ô có `n = 120` nhưng `n_salary = 12`. Theo AD-17 (`n < 30` mới cho `data = null`), `data` **không được** null — `n` là 120. Theo FR-30, phân vị lương **phải** là "chưa đủ dữ liệu". Hai luật, hai kết quả, trên cùng một response.

**Vì sao kiểm thử hiện có không bắt được.** Kiểm thử FR-30 sẽ được viết bởi dev B, trên dữ liệu mẫu mà dev B tự dựng — và dev B sẽ dựng một ô mà `n` và `n_salary` bằng nhau, vì trong đầu dev B chúng là một thứ. Lỗi chỉ lộ ra trên dữ liệu thật, ở Sprint 7, giữa đợt thử nghiệm 30–50 người.

**Đề xuất — siết AD-5 và AD-17.**
> **Rule:** `stat_percentiles` có khóa `(snapshot_id, stat_cell_id, measure)` và cột **`n_with_value NOT NULL`**; `meta` của mọi response có phân vị mang `n_by_measure: {measure: n_with_value}`. Cổng hiển thị của **từng** phân vị là `n_with_value >= THRESHOLDS.n_min` của **chính thước đo đó**, không bao giờ là `meta.n`; `haido_api` không được chạy `COUNT` trên bảng tin để suy ra con số này, và `meta.insufficient_data` được thay bằng `meta.insufficient_by_measure: {measure: bool}`.

---

### G-04 — Ai sinh `snapshot_id`, và một nguồn lỗi thì có snapshot không `[critical]`

Lỗ hổng này có hai nửa; nửa sau nặng hơn.

#### G-04a — Chạy lại một bước trên snapshot đã công bố

**Cặp đơn vị.**
- Story A (Sprint 1, dev A): "bước `ingest` ghi `job_raw` kèm `snapshot_id` và `source` (AD-16)".
- Story B (Sprint 1–2, dev A/B): "bước `dedupe` gom cụm (FR-4)".

**Cả hai đều hợp lệ theo.** AD-15 nói rõ mỗi bước "gọi được bằng CLI", và lý do là "chạy lại được một bước riêng lẻ khi debug". AD-4 nói: "Hàng thuộc snapshot đã công bố **không bao giờ bị sửa hay xóa**." Chữ ấy cấm `UPDATE` và `DELETE` — **không cấm `INSERT`**.

Dev A viết `ingest` dạng upsert theo `(source, external_id)`; dev B viết `dedupe` dạng `INSERT` thuần vào `job_clusters` (hợp lý: cụm là dẫn xuất, tính lại thì chèn mới). Chạy lại `dedupe` trên `snapshot_id` đã `published` để debug ⇒ cụm nhân đôi ⇒ mọi `n` của snapshot đó sai gấp đôi, **vĩnh viễn**, vì AD-4 cấm sửa.

**Vì sao kiểm thử hiện có không bắt được.** Không có kiểm thử nào trong spine về tính lũy đẳng của bước. Lỗi xuất hiện đúng lúc người ta đang debug — tức là lúc không ai nhìn vào con số.

**Đề xuất — siết AD-4 và AD-15.**
> **Rule:** Mỗi bước pipeline **lũy đẳng theo khóa `(snapshot_id, source)`**: chạy lại trên cùng khóa phải thay thế đúng phần của chính nó (`DELETE … WHERE snapshot_id = … AND source = …` rồi `INSERT`, trong một transaction), và **mọi lệnh ghi vào một `snapshot_id` đã `published` bị chặn bằng trigger ở tầng cơ sở dữ liệu** — kể cả `INSERT` — chứ không chỉ bị cấm bằng quy ước. Có kiểm thử chạy mỗi bước **hai lần** và khẳng định mọi bảng ra cùng số hàng.

#### G-04b — Một nguồn lỗi: snapshot có được công bố không `[critical]`

**Cặp đơn vị.**
- Story A (Sprint 1, dev A): "FR-1/FR-2 — thu thập theo từng nguồn, `pipeline_run` theo từng nguồn, thông báo khi lỗi".
- Story B (Sprint 1, dev A/B): "FR-3 — vòng đời tin và công bố snapshot".

**Cả hai đều hợp lệ theo.** FR-3 định nghĩa vòng đời tin theo **lần chạy thành công của chính nguồn đó**: *"vắng mặt ở ít nhất 3 lần chạy thành công liên tiếp của chính nguồn đó"*, *"một đêm nguồn bị lỗi … không bao giờ làm tăng số lần đăng lại"*. AD-4 và AD-15 định nghĩa snapshot theo **ngày**: "một snapshot = một daily partition", "chuyển sang `published` … ở cuối lượt chạy". Hai hệ đếm, không có AD nào nối chúng.

Nên dev A có thể quyết: TopCV lỗi thì vẫn công bố snapshot với 8/9 nguồn, `pipeline_run` ghi TopCV `failed` (đúng FR-1, đúng AD-4, và đúng NFR khả dụng). Dev B có thể quyết: nguồn lỗi thì không sinh snapshot, tầng đọc dùng snapshot hôm qua (cũng đúng NFR khả dụng: *"Nếu pipeline của một đêm bị lỗi, giao diện vẫn chạy trên snapshot gần nhất"*).

**Lệch nhau cụ thể.** Nếu công bố snapshot thiếu nguồn:
- `stat_cells.n` tụt khoảng 15% trong một đêm; Insights "Bậc thang Junior → Senior" đổi thẻ; Bản đồ đổi tỷ trọng. Không có dấu hiệu nào trên giao diện nói rằng đêm đó thiếu một nguồn — `meta.sources[]` có liệt kê "nguồn đang bật", mà TopCV **vẫn đang bật**, nó chỉ *lỗi*.
- D4 của FR-31 dùng *"xuất hiện liên tục qua ≥ 30 snapshot"*. Mọi tin TopCV mất chuỗi liên tục ngay đêm đó. Đến Sprint 4 khi dev B làm D4, con số "liên tục qua N snapshot" đã bị băm nát bởi quyết định của dev A ở Sprint 1, và không ai nối hai việc ấy lại.

**Đề xuất — AD mới (AD-20).**
> **Rule:** `snapshots` chỉ được tạo bởi bước `open_snapshot` (một bước, một hàng, khóa là ngày theo `Asia/Ho_Chi_Minh`), và chỉ chuyển `published` khi **mọi nguồn đang bật đều có một `pipeline_run` trạng thái `success` trong lượt chạy đó**; nếu có nguồn thất bại, lượt chạy kết thúc ở `partial`, **không** công bố, và tầng đọc giữ snapshot `published` trước đó. Vòng đời tin (FR-3) đếm theo `pipeline_run` thành công **của chính nguồn đó**, không theo `snapshot_id`; phép đếm ấy là một hàm duy nhất trong `domain`, và `meta` mang thêm `sources_failed_last_run[]` để chỗ thiếu nguồn luôn nhìn thấy được.

---

### G-05 — FR-4 và FR-32 là hai bản cài đặt của cùng một vị ngữ so khớp `[high]`

**Cặp đơn vị.**
- Story A (Sprint 1–2, dev A): "FR-4 — ghép trùng hai tầng, gom thành cụm".
- Story B (Sprint 4, dev B): "FR-32 — khớp tin được dán với tin đã thu thập, phục vụ D4".

**Cả hai đều hợp lệ theo.** FR-32 nói *"dùng **cùng cách so khớp** như FR-4"* — nhưng spine **không có AD nào** biến câu đó thành ràng buộc. AD-2 chỉ phủ phép "văn bản → mã kỹ năng → nhóm kỹ năng". AD-5 chỉ cấm **phép tổng hợp** (`GROUP BY`, phân vị, trung bình); một truy vấn tương đồng (`pg_trgm`, Jaccard trên tập kỹ năng) **không phải** phép tổng hợp, nên dev B được phép chạy nó ở API. AD-1 cho `steps` biết Postgres, nên dev A được phép viết dedupe bằng SQL.

Kết quả: dev A viết dedupe trong `steps/dedupe.py` bằng SQL với ngưỡng trigram 0,85 trên tên công ty chuẩn hóa + Jaccard ≥ 0,6 trên tập kỹ năng (hợp lý, chạy theo lô, cần tốc độ). Dev B viết matcher trong `haido_api` bằng Python với ngưỡng 0,7 / 0,4 (hợp lý, chỉ so 1 tin với tập ứng viên, cần recall để FR-32 "dán lại nguyên văn thì tìm được"). Hai ngưỡng, hai bản cài đặt, **không AD nào bị phá**.

**Lệch nhau cụ thể.** Một tin được TopCV và CareerLink đăng với tên công ty viết khác nhau. Dev A (ngưỡng chặt) tách thành **hai cụm**, mỗi cụm `số lần đăng lại = 0`. Dev B (ngưỡng lỏng) khi người dùng dán tin đó tìm thấy **cụm thứ nhất** — tùy `ORDER BY` không xác định, có thể là cụm nào. D4 báo *"không đăng lại"*; link "về tin gốc" trỏ về nguồn ngẫu nhiên trong hai nguồn. Đồng thời D1 so *"số kỹ năng của tin ≥ P90 của ô"*, mà P90 được tính trên dân số đã gom cụm theo ngưỡng chặt của dev A ⇒ hai bên của phép so sánh đến từ hai định nghĩa "một tin".

**Vì sao kiểm thử hiện có không bắt được.** Kết quả kiểm chứng duy nhất của FR-32 là *"Dán lại nguyên văn một tin đã có trong dữ liệu thì tìm được đúng tin đó"* — xanh trên **mọi** ngưỡng lỏng hơn dev A. Và SM-7 đo precision/recall của FR-4 trên 100 cặp gán nhãn tay, hoàn toàn độc lập với matcher của dev B.

**Đề xuất — AD mới (AD-21).**
> **Rule:** Vị ngữ so khớp trùng là **hai hàm thuần duy nhất** trong `domain/dedupe.py`: `fingerprint(posting) -> PostingFingerprint` và `same_posting(a, b) -> bool`; cả bước `dedupe` hằng đêm **lẫn** FR-32 lúc chạy đều gọi đúng hai hàm đó trên cùng kiểu `PostingFingerprint`, với ngưỡng đọc từ bảng cấu hình (AD-10). **Không được cài logic so khớp bằng SQL**; SQL chỉ được dùng để *thu hẹp tập ứng viên* và kết quả thu hẹp luôn phải chạy qua `same_posting` trước khi được coi là trùng. FR-32 trả về **tất cả** cụm khớp, không phải cụm đầu tiên, và hiển thị theo thứ tự tất định `(source, external_id)`.

---

### G-06 — FR-29 đòi ghi danh sách chờ từ tin dán; AD-11 cấm mọi lệnh ghi `[critical]`

Đây là lỗ hổng tôi coi là nặng nhất, vì nó không phải "hai cách đọc" — nó là **một mâu thuẫn**, và cả ba cách thoát khỏi mâu thuẫn đều tệ, trong đó một cách **phá chính cam kết riêng tư** mà AD-11 được viết ra để giữ.

**Cặp đơn vị.**
- Story A (Sprint 2, dev A): "FR-6 — danh sách chờ kỹ năng chưa nhận diện từ JD hằng đêm".
- Story B (Sprint 4, dev B): "FR-29 — phân nhóm kỹ năng của tin dán; kỹ năng chưa nhận diện".

**Mâu thuẫn, chính xác.**
- FR-29 (bắt buộc): *"Kỹ năng chưa nhận diện được hiển thị ở một dòng riêng … và **được đưa vào danh sách chờ (FR-6)**."* §3 nói lại: *"Được ghi vào danh sách chờ (kèm tần suất) để nhóm rà soát hằng tuần."*
- AD-11 (bắt buộc): *"endpoint nhận CV hoặc JD **không có lệnh ghi nào** vào cơ sở dữ liệu hay đĩa, **trừ** một hàng trong bảng sự kiện ẩn danh với **đúng các trường FR-17 liệt kê**."*
- Quy ước đột biến trạng thái: *"`haido_api` **chỉ** ghi vào `anon_events` và hai bảng `eval_*`."*

Vậy dev B có ba đường, **cả ba đều là hệ quả hợp lý của spine**:

1. **Không ghi gì.** Dev B hiển thị dòng "không tính vào mức khớp" và bỏ qua nửa sau của FR-29. Kết quả kiểm chứng của FR-29 là *"Mỗi kỹ năng thiếu thuộc nhóm riêng của công ty có ghi chú…"* — **không kiểm việc ghi danh sách chờ**. Nên FR-29 xanh, mà vòng phản hồi làm giàu bộ từ vựng từ tin người dùng dán — vòng phản hồi đáng giá nhất của sản phẩm — **im lặng biến mất**, và không ai phát hiện cho tới khi hội đồng hỏi "danh sách chờ của các bạn có bao nhiêu từ khóa từ người dùng thật?".
2. **Ghi vào `unknown_mentions`.** Phá quy ước đột biến và phá chữ của AD-11. Đây là vi phạm thấy được, nên nó sẽ bị review bắt — không phải lỗ hổng.
3. **Nhồi từ khóa vào `anon_events`.** FR-17 cho phép sự kiện ẩn danh chứa *"mã kỹ năng"*. Một từ khóa chưa nhận diện **chính là một mã kỹ năng ứng viên**. Nên dev B ghi `anon_events(session, "jd_unknown_mention", skill_code="k8s cluster federation")` — **đúng chữ AD-11** ("một hàng … với đúng các trường FR-17 liệt kê"), **đúng chữ quy ước** (chỉ ghi `anon_events`). Và kiểm thử của AD-11 (*"không bảng nào nhận văn bản CV hay JD"*) **xanh**, vì một token không phải "văn bản".

Đường số 3 là thảm họa im lặng: từ khóa nguyên văn do người dùng dán **được lưu vào cơ sở dữ liệu**, gắn với **mã phiên ẩn danh**, nghĩa là ghép được các token của cùng một người trong cùng một phiên — tức là **khôi phục được một phần nội dung JD họ đã dán**. Đúng loại rủi ro mà §5 và FR-47 cam kết không có ("dữ liệu nào không được lưu: CV, nội dung tin người dùng dán vào"). Và nó đi qua review vì **mỗi AD đều được tôn trọng**.

**Đề xuất — siết AD-11 + AD mới (AD-22).**
> **Rule 1:** Danh sách chờ có **hai bảng tách biệt**: `unknown_mentions` (chỉ bước pipeline ghi, nguồn là JD đã thu thập) và `unknown_mentions_pasted` (đường ghi duy nhất của `haido_api`). Mỗi hàng của `unknown_mentions_pasted` là **một từ khóa đã chuẩn hóa**, có ràng buộc DB: `length <= 64`, khớp `^[a-z0-9][a-z0-9 .+#/-]*$`, **không chứa mã phiên**, **không có cột thời điểm chính xác hơn ngày**; bảng chỉ có `(keyword, freq, last_seen_date)` và ghi bằng `INSERT … ON CONFLICT (keyword) DO UPDATE SET freq = freq + 1`.
>
> **Rule 2:** `anon_events.skill_code` có **khóa ngoại tới `skills.code`**, cưỡng chế ở cơ sở dữ liệu. Do đó `anon_events` **không thể** nhận một chuỗi phát sinh từ văn bản người dùng; mọi sự kiện ẩn danh chỉ mang mã kỹ năng đã tồn tại trong bộ từ vựng. Kiểm thử của AD-11 được đổi từ "không bảng nào nhận văn bản CV hay JD" thành "**mọi** cột kiểu text mà `haido_api` ghi được đều có khóa ngoại tới một bảng từ vựng, hoặc có `CHECK` giới hạn độ dài và ký tự".

---

### G-07 — AD-17 (`n<30` ⇒ `data = null`) mâu thuẫn trực tiếp với FR-33 `[critical]`

**Cặp đơn vị.**
- Story A (Sprint 5, dev C): "FR-33 — Bản đồ 3D theo tỷ trọng, cột Đà Nẵng".
- Story B (Sprint 5, dev C hoặc dev B): "FR-34 — bảng chi tiết thành phố".

**Mâu thuẫn, chính xác.**
- AD-17: *"Khi `n < 30`: `data` phải là `null` và `meta.insufficient_data = true` — **không bao giờ** là một con số đoán."*
- FR-33: *"Cột có `n < 30`: cột **không bị ẩn**, mà **vẫn vẽ theo tỷ trọng thật**, ở trạng thái mờ, kèm nhãn 'Cỡ mẫu nhỏ (n = X < 30): số liệu chỉ để tham khảo'."* Kết quả kiểm chứng: *"**Cột Đà Nẵng luôn được vẽ.**"*
- Thêm vào: addendum PRD ghi *"hiện Đà Nẵng chỉ có 64 tin"*, nên khi lọc theo một vai trò, ô Đà Nẵng × vai trò **gần như luôn** có `n < 30`. Đây là trường hợp thường, không phải biên.

FR-34 lại đứng về phía AD-17: *"Ô thống kê có `n < 30` thì không hiển thị tỷ lệ, chỉ ghi 'chưa đủ dữ liệu'."*

Vậy **cùng một ô** (`đà-nẵng × backend`, n = 18) phải vừa trả về một con số (FR-33) vừa không được trả về con số (AD-17 + FR-34). Dev C có hai đường thoát, cả hai hợp lệ:

1. **Tuân AD-17, tính tỷ trọng ở frontend.** API trả `data = null`; dev C lấy số tin thô từ một endpoint khác (một endpoint trả `counts` không phải "tỷ lệ, phân vị hay mốc phân vị" — nên **không** bị AD-5 cấm) rồi chia ở TypeScript. AD-7 chỉ cấm frontend sắp xếp topo và so sánh 4 tầng; AD-5 chỉ ràng buộc `haido_api`. **Không AD nào cấm `web/` làm một phép chia.** Và đây là đúng loại "tiện tay tự tính rồi lệch số" mà đề bài hỏi.
2. **Khai ô thống kê của bản đồ là ô toàn quốc.** `meta.stat_cell = {role: backend, scope: national}`, `meta.n = 4100`; tỷ trọng từng thành phố nằm **trong** `data` như một trường hiển thị. AD-17 xanh (n = 4100 ≥ 30), FR-33 xanh (cột Đà Nẵng có số). Nhưng giờ `meta.n` **không còn mô tả** con số mà người dùng đang nhìn — đúng điều AD-17 ra đời để chặn.

**Lệch nhau cụ thể.** Người dùng bấm cột Đà Nẵng (có chiều cao, có tỷ trọng 4%) và bảng chi tiết mở ra ghi *"chưa đủ dữ liệu"* cho cùng một vai trò. Hai phán quyết về cùng một ô, **cách nhau một cú bấm chuột**. Nếu đi đường 1, tỷ trọng ở frontend còn tính trên dân số khác với `stat_city_role` (xem G-02) ⇒ tổng các cột không còn bằng 100%, và kết quả kiểm chứng của FR-33 về tổng 100% sẽ đỏ **ở Sprint 5** mà nguyên nhân nằm ở một AD viết từ Sprint 1.

**Đề xuất — siết AD-17 + AD mới.**
> **Rule:** AD-17 không còn áp quy tắc `data = null` một cách vô điều kiện. Mỗi response khai báo `meta.suppression: "null_data" | "low_sample_shown"`, và việc chọn chế độ nào là **một hàm duy nhất** `domain.display_policy.suppression_for(measure_kind, n)`: tỷ lệ xuất hiện, nhóm kỹ năng, phân vị, mốc phân vị và thẻ Insights ⇒ `null_data`; **duy nhất** tỷ trọng thành phố của FR-33 ⇒ `low_sample_shown` kèm `n` và nhãn cỡ mẫu nhỏ. `web/` **không bao giờ** tự tính tỷ trọng, kể cả khi `data = null`; nếu một màn hình cần một con số mà API không trả, đó là lỗi của API, không phải việc của frontend. Có kiểm thử khẳng định `web/` không chứa phép chia nào trên dữ liệu đến từ `/api/v1/`.

---

### G-08 — Hàm chọn ô của AD-6 gọi được cho ô thành phố, mà chuỗi quay về không có bậc thành phố `[high]`

**Cặp đơn vị.**
- Story A (Sprint 3, dev B): "FR-19 — lộ trình học chung, nhãn quay về".
- Story B (Sprint 6, dev C): "FR-37/FR-38 — thẻ 'Khác biệt giữa các thành phố'".

**Cả hai đều hợp lệ theo.** AD-6 khóa `stat_cells` là `(snapshot_id, role, branch, seniority, scope)` và nói việc chọn ô là "**một hàm duy nhất** trong `domain`", "không nơi nào khác được dựng lại chuỗi quay về". Trường `scope` tồn tại chính là để chứa phạm vi — và với Bản đồ/Insights, phạm vi **là thành phố**.

Nhưng §3 chỉ định nghĩa chuỗi quay về cho ô **Cố vấn và Soi tin** (vai trò × cấp bậc, **toàn quốc**). Với ô thành phố × vai trò, §3 không có chuỗi nào, và FR-38 nói ngược lại: thẻ chỉ hiển thị khi `n >= 30`, không quay về gì cả.

Dev C, làm thẻ "Khác biệt giữa Hà Nội và TP.HCM", gọi `select_cell(role=backend, scope=hanoi)` — **đúng chữ AD-6**, vì AD-6 nói hàm này là đường duy nhất để chọn ô. Hàm của dev B nhận `scope` nhưng chuỗi quay về của nó không có bậc nào đổi `scope`; nên nó làm điều tự nhiên nhất: quay về **bậc 4 (vai trò × mọi cấp bậc)** và trả về ô **toàn quốc** kèm `fallback_label`.

**Lệch nhau cụ thể.** Một thẻ Insights tiêu đề *"Khác biệt giữa Hà Nội và TP.HCM"* được tính trên **dữ liệu toàn quốc cho cả hai phía**, nên chênh lệch bằng 0 ⇒ thẻ không bao giờ hiện (FR-38 đòi chênh ≥ 5 điểm). Nhóm sẽ kết luận "dữ liệu Đà Nẵng/HCM chưa đủ" và bỏ thẻ, trong khi thật ra hàm chọn ô đã âm thầm thay hai thành phố bằng toàn quốc. Hoặc tệ hơn: nếu `fallback_label` chỉ in ra "tính trên 4.100 tin Backend", người đọc hiểu là 4.100 tin **Hà Nội**.

**Thêm một lỗi tất định trong chính chuỗi quay về.** §3 ghi bậc khởi đầu là *"vai trò mục tiêu × cấp bậc"*, trong đó **vai trò mục tiêu có thể chính là một nhánh** (§3: "Vai trò mục tiêu. Vai trò hoặc nhánh mà người dùng đang chọn"). Rồi bậc 1 là *"nhánh × cấp bậc"* — **trùng y nguyên bậc khởi đầu** khi người dùng chọn một nhánh. Hai dev sẽ chuẩn hóa khác nhau: một người bỏ bậc trùng (3 bậc), một người giữ (4 bậc) và sinh thêm một `fallback_label` vô nghĩa ("đã quay về nhánh Java Backend" khi chưa quay về đâu cả). Cả hai "tuân AD-6", vì AD-6 không liệt kê các bậc.

**Đề xuất — siết AD-6.**
> **Rule:** `domain.stat_cell.select(req: CellRequest) -> CellChoice` nhận `CellRequest(role, branch|null, seniority|null, scope)` và **chỉ hỗ trợ `scope = national`**; nó **raise `UnsupportedScope`** khi `scope` là một thành phố. Ô `thành phố × vai trò` của Bản đồ và Insights **không có thứ tự quay về**: thiếu mẫu thì không hiển thị (FR-38) hoặc hiển thị kèm nhãn cỡ mẫu nhỏ (FR-33), và `select` không bao giờ được gọi cho chúng. Chuỗi quay về được viết thành **một danh sách hằng 5 bậc tường minh** trong `domain` (bậc 0 = đúng yêu cầu gốc, đã chuẩn hóa để bậc 0 và bậc 1 không bao giờ trùng), mỗi bậc gắn **một** chuỗi nhãn; có kiểm thử liệt kê đúng 5 bậc và đúng 5 nhãn, và một kiểm thử bảng chân lý khẳng định `select` cho cùng kết quả khi vai trò mục tiêu là nhánh và khi nhánh được truyền riêng.

---

### G-09 — "Lộ trình đã xếp thứ tự" không có hình dạng `[high]`

**Cặp đơn vị.**
- Story A (Sprint 3, dev B): "FR-22 — endpoint lộ trình học tất định".
- Story B (Sprint 3/5, dev C): "FR-19/FR-20/FR-24 — đồ thị nút kiểu roadmap.sh bằng `@xyflow/react`"; cộng Story C (Sprint 3, dev C): "FR-16 — tải kết quả, **lộ trình học theo chặng**".

**Cả hai đều hợp lệ theo.** AD-7 nói API "trả về lộ trình **đã xếp thứ tự**" và frontend chỉ được làm hai phép: giao tập để tô sáng (FR-24) và **"lọc hiển thị"**. Không chữ nào nói hình dạng:

- mảng phẳng đã xếp thứ tự, mỗi phần tử có `stage`?
- cấu trúc lồng, nhóm theo chặng?
- `{nodes, edges}` cho `@xyflow`?

Dev B trả mảng phẳng (sát nghĩa "đã xếp thứ tự" nhất, và sát thuật toán Kahn trong addendum). Dev C cần **cạnh** để vẽ đồ thị — AD-7 cấm sắp xếp topo ở frontend, **không cấm** lấy cạnh và tự xếp hàng (layout). Nên dev C gọi thêm một endpoint `skill-edges` và nhóm nút thành hàng theo độ sâu **mà dev C tự tính từ cạnh**.

Và "lọc hiển thị" là một cụm từ rất rộng: một dev đọc nó là quyền **ẩn nút có tỷ lệ dưới θ_common** cho gọn — việc này **xóa sạch kỹ năng nền tảng**, mà FR-20 bắt buộc phải có kèm nhãn "Kỹ năng nền tảng (cần cho X)".

**Lệch nhau cụ thể.** Hai khái niệm "chặng" tồn tại song song: `stage` do `domain` tính (độ sâu **sau khi trừ hồ sơ** — §3) và hàng layout do dev C tính từ cạnh (độ sâu **trên đồ thị đầy đủ**). Với hồ sơ {Java, SQL, Git}, Docker ở `stage = 1` theo server nhưng ở hàng 3 theo layout. Bản tải về của FR-16 ("lộ trình học **theo chặng**") in theo `stage`; màn hình vẽ theo hàng layout. Người dùng tải PDF về và thấy thứ tự khác màn hình họ vừa xem.

**Vì sao kiểm thử hiện có không bắt được.** Kết quả kiểm chứng của FR-22 (*"cùng hồ sơ, cùng vai trò, cùng snapshot luôn cho cùng một lộ trình học"*, *"không kỹ năng nào đứng trước tổ tiên của nó"*) sẽ được viết trên **API** — và nó xanh. SM-8 cũng đo trên API. Không kiểm thử nào so màn hình với bản tải về.

**Đề xuất — siết AD-7.**
> **Rule:** Endpoint lộ trình trả về **một cấu trúc duy nhất** `{nodes: [{skill_code, order, stage, group, ratio, badge, in_profile}], edges: [{from, to}], meta}`, trong đó `order` là số nguyên liên tục từ 1 và `stage` do `domain` tính sau khi trừ hồ sơ. `web/` **chỉ được** đọc `order`, `stage`, `edges` đúng như đã cho: không nhóm lại, không suy ra chặng từ cạnh, không ẩn nút theo `ratio` hay `group`. "Lọc hiển thị" trong AD-7 được định nghĩa hẹp lại thành **duy nhất**: ẩn/hiện theo lựa chọn tường minh của người dùng trên giao diện, và một nút `badge = "foundation"` **không bao giờ** được ẩn. Bản tải về của FR-16 sinh từ **đúng response đó**, không từ một truy vấn thứ hai.

---

### G-10 — `skills` không được khai là danh sách đóng `[medium]`

**Cặp đơn vị.**
- Story A (Sprint 1, dev A): "bộ từ vựng kỹ năng v0 + bảng bí danh".
- Story B (Sprint 2, dev B): "đồ thị học trước cho Java Backend và Data Engineer, có biên bản rà soát (FR-22)"; cộng Story C (Sprint 2–3, dev C): "danh mục tài liệu + lời dẫn soạn offline (FR-23)".

**Cả hai đều hợp lệ theo.** Quy ước nói mã kỹ năng là "kebab-case, chỉ ASCII, không dấu … Là khóa chính, **không bao giờ đổi**". Cây mã nguồn có chú thích `vocab/ # bộ từ vựng song ngữ, đồ thị học trước, danh mục tài liệu (dữ liệu có phiên bản)` — nhưng đó là **một dòng chú thích trong sơ đồ cây**, không phải một AD; và AD-10 (dữ liệu có phiên bản) liệt kê **chỉ** θ, tỷ giá, công tắc nguồn và ngưỡng dấu hiệu. Nên:

- không AD nào nói `skills` được nạp từ file có phiên bản bởi **một** bước;
- không AD nào nói ai được `INSERT` vào `skills`;
- không AD nào nói `skill_edges.from/to` phải tồn tại trong `skills`.

Dev B soạn file cạnh và viết `nodejs` làm nút tiên quyết. Dev A có `node-js` trong bộ từ vựng. **Cả hai đều kebab-case ASCII.** Dev C viết danh mục tài liệu cho `node.js`.

**Lệch nhau cụ thể.** Ba mã cho một kỹ năng. Bước kiểm tra tự động của FR-22 (*"mọi kỹ năng cốt lõi hoặc thường gặp đều phải có nút trong đồ thị"*) **xanh**, vì `nodejs` chỉ là một nút mồ côi thêm vào, còn `node-js` tình cờ chưa vượt θ_common. Đến Sprint 6, khi dữ liệu dày lên và `node-js` thành "thường gặp", bước kiểm tra **đỏ** — hai tuần trước code freeze — và cách sửa đúng là đổi mã kỹ năng, điều mà quy ước nói "không bao giờ đổi".

**Đề xuất — AD mới (AD-23).**
> **Rule:** `skills` là một **danh sách đóng**, nạp từ `haido_core/vocab/skills.yaml` bởi **đúng một** bước `seed_vocab`, có `vocab_version`. `skill_aliases`, `skill_edges`, `resources` và `blurbs` đều có **khóa ngoại tới `skills.code` cưỡng chế ở cơ sở dữ liệu**; một mã lạ làm `seed_vocab` **thất bại**, không bao giờ tạo nút ngầm. Không tiến trình nào ngoài `seed_vocab` được `INSERT` vào `skills`, và CI chạy một kiểm thử khẳng định mọi mã xuất hiện trong mọi file của `vocab/` đều có mặt trong `skills.yaml`.

---

### G-11 — Bảng `stat_*` không bắt buộc là con của `stat_cells`; hai dev hai head Alembic `[high]`

**Cặp đơn vị.**
- Story A (Sprint 2, dev A): "`stat_cells`, `stat_skill_rates`, `stat_percentiles` + bootstrap CI".
- Story B (Sprint 5, dev C): "`stat_city_role` cho Bản đồ"; cộng Story C (Sprint 6, dev C): "`eval_pre_session`, `eval_post_session`".

**Cả hai đều hợp lệ theo.** AD-6 nói `stat_cells` là bảng thật với khóa `(snapshot_id, role, branch, seniority, scope)`. AD-5 nói con số đọc "theo khóa `(snapshot_id, stat_cell_id)`" — chú ý: AD-6 nói khóa tự nhiên, AD-5 nói `stat_cell_id`, **spine không nối hai thứ đó**, nên `stat_cell_id` là khóa thay thế hay là tuple thì tùy dev. Quy ước chỉ nói "Bảng tổng hợp mang tiền tố `stat_`".

Dev A tạo `stat_cells.id` serial và các bảng con trỏ bằng `stat_cell_id`. Dev C, làm bản đồ, thấy ô của mình là `thành phố × vai trò` — mà §3 gọi đó là một loại ô thống kê khác — nên tạo `stat_city_role(snapshot_id, city, role, share, n)` **không** trỏ về `stat_cells`. Tiền tố `stat_` có, AD-5 "đọc từ bảng tổng hợp" có, AD-6 nói về `stat_cells` nhưng dev C lập luận được rằng ô thành phố không phải cùng loại ô.

**Lệch nhau cụ thể.** Hệ quả không phải một con số sai, mà là **AD-6 bị vô hiệu hóa cho một nửa sản phẩm**: Bản đồ và Insights có ô thống kê **không** đi qua hàm chọn ô, **không** có `fallback_label`, và `meta.stat_cell` của chúng không tham chiếu được về `stat_cells`. Mọi lỗ hổng G-02, G-07, G-08 trở nên không thể phát hiện bằng một truy vấn kiểm tra chéo, vì không có bảng nào nối hai thế giới.

**Nửa thứ hai: migration.** Spine chỉ nói "`db/` # model SQLAlchemy + migration Alembic". Alembic có **một** chuỗi `down_revision` tuyến tính. Dev A (Sprint 2) và dev C (Sprint 5, Sprint 6) đều nhánh từ cùng một head trong các branch git riêng ⇒ sau merge có **hai head** ⇒ `alembic upgrade head` **thất bại trên prod** đúng ngày demo, hoặc có người tạo merge revision tay và thứ tự `CREATE TABLE` làm khóa ngoại đổ. Không AD nào, không quy ước nào nói một chữ về chuyện này, dù spine biết rõ là có 3 dev.

**Đề xuất — siết AD-6 + AD mới (AD-24).**
> **Rule 1:** Mọi bảng `stat_*` là **bảng con của `stat_cells`**: một con số tổng hợp chỉ tồn tại khi có một hàng `stat_cells` tương ứng, qua khóa ngoại `stat_cell_id NOT NULL`. Ô của Bản đồ và Insights **là** hàng `stat_cells` với `scope = <city>` và `seniority = 'any'`. Không có bảng tổng hợp nào có khóa riêng chứa `role` hay `city`.
>
> **Rule 2:** Mỗi story tạo hoặc đổi bảng phải khai bảng của mình trong `haido_core/db/OWNERS.md` (bảng → story → dev) **trước** khi viết migration; CI thất bại nếu `alembic heads` trả về nhiều hơn một dòng, hoặc nếu một migration chạm một bảng không thuộc sở hữu của story đó, hoặc nếu `alembic upgrade head` rồi `downgrade base` rồi `upgrade head` trên DB rỗng không cho cùng schema.

---

### G-12 — AD-10 không phủ `n = 30`, `60 ngày`, `5 điểm phần trăm`, và `≥ 30 tin` của FR-7 `[high]`

**Cặp đơn vị.**
- Story A (Sprint 2, dev A): "FR-7 — tạo nhánh khi có ≥ 30 tin".
- Story B (Sprint 3–4, dev B): "FR-19/FR-27 — ngưỡng mẫu 30 và chuỗi quay về"; cộng Story C (Sprint 6, dev C): "FR-38 — ngưỡng 5 điểm phần trăm, thẻ chỉ hiện khi n ≥ 30".

**Cả hai đều hợp lệ theo.** AD-10 liệt kê **chính xác**: θ_core, θ_common, tỷ giá USD, công tắc từng nguồn, ngưỡng của từng dấu hiệu. Rồi nói "Không hằng số nào **trong nhóm này** xuất hiện trong code". Nghĩa là mọi ngưỡng **ngoài** nhóm đó được phép viết cứng, ở bao nhiêu chỗ cũng được:

`n_min = 30`, biên CI `100`, cửa sổ `60 ngày`, `5 điểm phần trăm` (FR-38), `30 tin` để tạo nhánh (FR-7), `3 lần chạy vắng mặt` (FR-3), `30 ký tự` (FR-11), `200–20.000 ký tự` (FR-26), `5 MB` (FR-10).

Riêng con số 30 sẽ nằm ở ít nhất **sáu** chỗ: `domain.stat_cell` (quay về), `haido_api` (AD-17), `web/` (nhãn mờ của FR-33 và "chưa đủ dữ liệu" của FR-34), `steps` (cổng thẻ FR-38), `steps` (tạo nhánh FR-7), `domain` (cổng phân vị FR-30).

**Lệch nhau cụ thể — và đây là phiên bản im lặng.** FR-7 nói *"Nhánh: chỉ được tạo khi có từ 30 tin trở lên"*. Dev A đếm **mọi tin đã thu được từ đầu** tại thời điểm phân loại (tự nhiên: phân loại chạy trước `aggregate`). §3 nói ngưỡng mẫu 30 áp cho **ô thống kê**, mà ô thống kê chỉ đếm cụm trong 60 ngày (G-02). Nên: nhánh `embedded-firmware` tồn tại (35 tin mọi thời) nhưng ô `embedded-firmware × junior` luôn có n = 22 ⇒ **mọi** người dùng chọn nhánh đó **luôn luôn** nhận nhãn quay về, mãi mãi. Thêm nữa, FR-19 có kết quả kiểm chứng *"một người dùng chọn cấp Intern/Fresher/Junior không bao giờ nhận một tập mà cấp Mid trở lên chiếm đa số, trừ khi ở bước cuối"* — và chính nhánh ấy sẽ rơi xuống bước cuối thường xuyên, làm kết quả kiểm chứng đó đỏ vì một lý do nằm cách đó bốn sprint.

Thêm vấn đề biên cho `web/`: `web/` không `import` được Python, nên con số 30 **buộc** phải tồn tại lần thứ hai ở TypeScript — trừ khi nó đến từ `meta.thresholds`, mà G-01 cho thấy `thresholds` chưa có hình dạng.

**Đề xuất — siết AD-10.**
> **Rule:** Mọi ngưỡng mà PRD nêu bằng con số là thuộc tính của **một đối tượng hằng duy nhất** `domain.thresholds.THRESHOLDS`: `n_min = 30`, `ci_upper = 100`, `recency_days = 60`, `insight_delta_pp = 5`, `branch_min_clusters = 30`, `absence_runs = 3`, `cv_min_chars = 30`, `jd_len = (200, 20000)`, `upload_max_mb = 5`. `branch_min_clusters` **phải đếm cùng dân số với `n_min`** (`domain.population`, xem G-02). Một chữ số của các ngưỡng này xuất hiện ở bất kỳ file nào khác — kể cả trong `web/` — là lỗi: `web/` chỉ được lấy chúng từ `meta.thresholds`; có kiểm thử quét mã nguồn cả Python và TypeScript.

---

### G-13 — Quy ước route **buộc** frontend tự tính mức khớp `[critical]`

Lỗ hổng này không phải "spine quên cấm" — mà là **spine chủ động chặn** đường làm đúng.

**Cặp đơn vị.**
- Story A (Sprint 4, dev B): "FR-28 — mức khớp và dòng đếm thô theo nhóm".
- Story B (Sprint 3, dev C): "FR-13/FR-21 — cập nhật hồ sơ kỹ năng, kết quả mới trong vòng 1 giây"; cộng FR-24 (dev C).

**Vì sao cả hai hợp lệ, và vì sao dev C **phải** tính ở frontend.**

1. AD-2 cấm cài lại phép "văn bản → mã kỹ năng → nhóm kỹ năng". **Mức khớp không phải phép đó** — nó là một phép cộng có trọng số trên hai tập mã kỹ năng đã có nhóm. AD-2 không phủ.
2. AD-7 cấm frontend sắp xếp topo, so sánh 4 tầng, dùng θ — và **cho phép tường minh** "giao tập để tô sáng kỹ năng trùng (FR-24)". FR-24 lại đòi *"một dòng tóm tắt cho biết **có bao nhiêu** kỹ năng trong lộ trình học mới trùng với hồ sơ"*. Vậy AD-7 **cho phép** frontend **đếm** kết quả giao.
3. AD-5 chỉ ràng buộc `haido_api`, không ràng buộc `web/`.
4. Quyết định: Quy ước route nói *"Chỉ `GET` cho dữ liệu thị trường; `POST` **chỉ** cho hai endpoint trích xuất phù du và cho sự kiện ẩn danh."* Hồ sơ kỹ năng nằm ở `localStorage` (FR-14), nên để server tính mức khớp, `web/` phải **gửi hồ sơ lên**. Một `POST /api/v1/match` là **endpoint POST thứ ba** ⇒ **bị quy ước cấm**. Còn `GET ?have=…` thì chưa được quy ước nào cho phép ngoài link chia sẻ (FR-15), và với hồ sơ 40–60 kỹ năng, chẳng ai chắc nó nằm trong giới hạn URL.

Nên dev C làm điều hợp lệ nhất: tính `Σw(có) / Σw(tất cả)` bằng TypeScript. NFR "trong vòng 1 giây" khi FR-21 đổi hồ sơ càng đẩy về hướng đó. Đồng thời dev B cũng trả `match_percent` trong response Soi tin, vì FR-28 là story của dev B.

**Lệch nhau cụ thể, ba cách.**
- **Kỹ năng chưa nhận diện.** FR-28 và D2 nhấn mạnh phải loại chúng. Bản TypeScript của dev C rất dễ gộp chúng với trọng số 1 (chúng nằm cùng một mảng trên màn hình). Kết quả kiểm chứng *"Kỹ năng chưa nhận diện không làm thay đổi mức khớp"* là một kiểm thử **backend**, nên nó xanh trong khi màn hình sai.
- **Làm tròn hai lần.** FR-28/addendum định nghĩa `round(Σ/Σ × 100)` — **làm tròn nằm trong định nghĩa**. Quy ước lại nói "Tỷ lệ lưu dạng số thực 0–1. Làm tròn **chỉ** ở tầng hiển thị, không bao giờ làm tròn hai lần". Hai câu này **đã** mâu thuẫn. Dev B trả `0.8333`, dev C in `83%`; nhưng nếu dev C tự tính, dev C tính `round(15/18*100) = 83` — trùng nhau ở ví dụ của addendum, lệch 1 điểm ở những tỷ số khác. Hội đồng thấy mức khớp đổi 1 điểm khi reload trang.
- **Hai phép đếm cùng nghĩa, hai nơi.** FR-24 "có bao nhiêu kỹ năng trùng" (frontend, trên lộ trình của vai trò người dùng chọn) và FR-28 "Bạn đáp ứng 6/8 kỹ năng" (backend, trên ô của tin). Khi hai số này xuất hiện trong cùng một phiên, chúng **phải** khác nhau (ô khác nhau — xem G-17) nhưng **không màn hình nào nói vì sao**.

**Đề xuất — siết AD-7 + siết quy ước route.**
> **Rule 1:** `mức khớp`, `dòng đếm thô theo nhóm` (FR-28), `danh sách khoảng trống kỹ năng` (FR-20) và `số kỹ năng trùng` (FR-24) **chỉ** do `haido_api` trả về, tính bằng hàm `domain.match`. `web/` **không được** chứa phép cộng, chia, trọng số hay đếm nào trên mã kỹ năng; ngoại lệ "giao tập" của AD-7 được thu hẹp thành **duy nhất việc đặt cờ tô màu cho một nút đã có trong response**, không bao gồm đếm.
>
> **Rule 2:** Quy ước route được bổ sung một dạng được phép thứ tư: `GET /api/v1/<danh-từ>?have=<mã,mã,…>` — **cùng cách mã hóa với link chia sẻ của FR-15** — là đường duy nhất để gửi hồ sơ kỹ năng lên server; `have` giới hạn 200 mã, và `web/` gọi lại endpoint này mỗi khi hồ sơ đổi. Không có `POST` nào mang hồ sơ kỹ năng.

---

### G-14 — Câu kết luận Insights: không nói ai lắp mẫu câu `[high]`

**Cặp đơn vị.**
- Story A (Sprint 6, dev A): "bước `aggregate` — tính thẻ Insights (FR-37, FR-38)".
- Story B (Sprint 6, dev C): "trang Insights — thẻ, câu kết luận, lọc theo vai trò (FR-39, FR-40)".

**Cả hai đều hợp lệ theo.** AD-8 nói "Insights không gọi LLM" — xong, không nói ai lắp mẫu câu. Bảng Capability ghi Insights sống ở **cả** `haido_core/steps/` ("tính sẵn thành thẻ") **và** `web/`. AD-5 chỉ cấm `haido_api` tổng hợp. Quy ước nói "Chuỗi hiển thị tiếng Việt **tra từ bảng**, không viết trong code" — và "bảng" có thể là bảng DB hay một file hằng TypeScript.

Dev A lưu `insight_cards(snapshot_id, kind, role, values_json)` và để câu chữ cho frontend (hợp lý: i18n, và dev A không muốn tiếng Việt trong Python). Dev C lắp câu trong React: chọn biến thể theo khoảng (`> 50%`, `30–50%`, `< 10%`) và nội suy số.

**Lệch nhau cụ thể.** Ranh giới khoảng chạy sang TypeScript. FR-39 có kết quả kiểm chứng *"Biến thể mẫu câu được chọn đúng theo khoảng giá trị; **có kiểm thử cho từng ranh giới khoảng**"* — giờ kiểm thử đó nằm ở Jest, trên một hàm TS, trong khi con số dưới câu đến từ backend. Một tỷ lệ đúng `0.500` cho câu *"Áp đảo: **hơn một nửa** số tin…"* đứng trên con số in ra **50,0%** — mâu thuẫn hiển thị kinh điển ở biên, và FR-39 có kết quả kiểm chứng *"Mọi con số trong câu khớp với số liệu hiển thị bên dưới"* mà vẫn xanh (số khớp; chỉ **chữ** sai).

Nặng hơn: NFR tất định nói "câu kết luận của Insights là tất định: cùng đầu vào và cùng snapshot luôn cho cùng kết quả". Khi câu được lắp ở frontend, tính tất định bị chẻ qua hai ngôn ngữ và một lần làm tròn ở giữa — và `0.4999` làm tròn thành `50%` để hiển thị rồi đi vào nhánh "> 50%" là một lỗi tôi cho là **sẽ** xảy ra.

**Đề xuất — siết AD-8 + AD-5.**
> **Rule:** Câu kết luận của thẻ Insights được **sinh đầy đủ trong `domain`** và lưu vào `insight_cards.headline`, cùng `template_id` và `values_json`; `web/` **chỉ in `headline` ra**, không chọn biến thể, không nội suy, không so sánh khoảng. Ranh giới khoảng của mỗi mẫu câu là dữ liệu trong `haido_core/vocab/insight_templates.yaml`, viết bằng khoảng nửa mở tường minh (`[lo, hi)`) trên **giá trị chưa làm tròn**, và việc chọn biến thể phải dùng **cùng giá trị** đã sinh ra con số in trên thẻ. Có kiểm thử ranh giới trong Python cho từng mẫu câu, gồm điểm `lo` và điểm `hi`.

---

### G-15 — `revalidate`: trong hay ngoài transaction, và path lấy từ đâu `[medium]`

**Cặp đơn vị.**
- Story A (Sprint 1/5, dev A): "bước `publish` — công bố snapshot trong một transaction (AD-4)".
- Story B (Sprint 5, dev C): "trang nội dung công khai, ISR, một template theo vai trò (AD-13)".

**Cả hai đều hợp lệ theo.** AD-4: chuyển `published` trong **đúng một** transaction. AD-13: "sau khi một snapshot chuyển `published`, **bước cuối của pipeline** gọi route làm mới". Hai câu này không nói `revalidate` ở trong hay ngoài transaction, cũng không nói thất bại thì sao.

- Dev A đặt lệnh gọi HTTP **trong** transaction (đọc "bước cuối" là "cuối cùng của bước publish") ⇒ một request mạng giữ transaction mở; `web` khởi động lại ⇒ transaction rollback ⇒ **mất một snapshot hoàn toàn tốt**, hoặc lỗi bị `except: pass` và không ai biết.
- Dev A đặt **ngoài** ⇒ thất bại im lặng ⇒ trang công khai phục vụ số của hôm qua **vô hạn** trong khi API trả số hôm nay. Đúng điều AD-13 ra đời để chặn, và không kiểm thử nào bắt.

Thêm: **danh sách path**. AD-13 không nói lấy ở đâu. Dev A viết cứng `["/", "/vai-tro/backend", …]` (AD-10 không phủ, nên hợp lệ). Câu hỏi mở số 5 của spine thừa nhận **danh sách vai trò chưa chốt**. Thêm vai trò ở Sprint 5 ⇒ trang của nó không bao giờ được làm mới, hoặc 404.

Và Câu hỏi mở số 1 của spine đã nói: **trang công khai chưa có FR nào**, nên **không có kết quả kiểm chứng nào** để bắt bất kỳ lỗi nào trong nhóm này.

**Đề xuất — siết AD-13.**
> **Rule:** `revalidate` là một bước pipeline **riêng, chạy sau khi transaction công bố đã commit**, lũy đẳng, và nhận danh sách đường dẫn từ **một truy vấn trên `stat_cells` của snapshot vừa công bố** (không viết cứng). Thất bại của nó **không** rollback snapshot, nhưng đặt `snapshots.public_pages_stale = true` và gửi thông báo theo FR-1. Mọi trang công khai in `snapshot_date` mà **chính nó** render được, và có một kiểm thử sau triển khai so `snapshot_date` trên trang công khai với `snapshot_date` của `GET /api/v1/health`; lệch là đỏ.

---

### G-16 — `is_eval` do ai đặt, và không AD nào buộc báo cáo phải lọc nó `[medium]`

**Cặp đơn vị.**
- Story A (Sprint 6, dev C): "FR-41 — bật chế độ thử nghiệm; modal đầu/cuối phiên".
- Story B (Sprint 7, dev A): "bảng số liệu SM-1..SM-3 và thống kê sử dụng cho báo cáo SEP490".

**Cả hai đều hợp lệ theo.** AD-18 nói "`eval_pre_session` và `eval_post_session` là bảng riêng; **mọi sự kiện ẩn danh có cờ `is_eval`**". Đó là tất cả. Không nói: ai đặt cờ (trình duyệt hay API), cờ có `NOT NULL` không, và — quan trọng nhất — **không nói truy vấn phân tích phải lọc nó**. AD-18 chỉ hứa ngăn "dữ liệu của người thử lẫn vào thống kê sử dụng thường", nhưng cơ chế duy nhất nó dựng là *tách bảng* cho `eval_*`, còn `anon_events` **vẫn dùng chung**.

**Lệch nhau cụ thể.**
- `anon_events` ship ở **Sprint 3**; chế độ thử nghiệm ship ở **Sprint 6**. Cột `is_eval` thêm vào Sprint 6 ⇒ mọi sự kiện Sprint 3–5 có `is_eval = NULL`. Dev A viết `WHERE is_eval = false` ⇒ **âm thầm bỏ toàn bộ dữ liệu ba sprint đầu** (SQL ba trạng thái). Dev C viết `WHERE is_eval IS NOT TRUE` ⇒ giữ. Hai mẫu số cho cùng một chỉ số, trong cùng một báo cáo bảo vệ đồ án.
- Cờ do trình duyệt gửi trong thân request ⇒ một người thử reload trang mất cờ ⇒ nửa phiên vào "normal", nửa vào "eval"; mã phiên ẩn danh thì nối cả hai nửa, nên câu `JOIN` của Sprint 7 (addendum: "chỉ cần một câu truy vấn JOIN là ra bảng số liệu") ra số không giải thích được.

**Đề xuất — siết AD-18.**
> **Rule:** `anon_events.is_eval` là `BOOLEAN NOT NULL DEFAULT false` (migration điền `false` cho hàng cũ), do `haido_api` đặt từ header `X-Haido-Mode` chỉ nhận `normal|eval` — **không** từ thân request, và **không** đổi được giữa phiên: một `session_id` đã ghi sự kiện với một mode thì mọi sự kiện sau của nó mang mode đó (cưỡng chế bằng ràng buộc). Mọi truy vấn phân tích và mọi số liệu vào báo cáo đi qua **đúng hai view** `v_events_normal` và `v_events_eval`; không báo cáo nào truy vấn trực tiếp `anon_events`.

---

### G-17 — Nhãn nhóm kỹ năng không mang theo ô đã sinh ra nó `[high]`

**Cặp đơn vị.**
- Story A (Sprint 4, dev B): "FR-29 — phân nhóm kỹ năng của tin được dán".
- Story B (Sprint 3, dev C): "FR-20 — lộ trình cá nhân hóa, khoảng trống kỹ năng".

**Cả hai đều hợp lệ theo.** §3 định nghĩa nhóm kỹ năng "theo tỷ lệ xuất hiện của nó **trong vai trò mục tiêu**". AD-2 bảo đảm **một** bản cài đặt của phép phân nhóm — nhưng **không bảo đảm một đối số**. Và hai tính năng có hai "vai trò mục tiêu" khác nhau một cách chính đáng:

- Soi tin: vai trò là **của tin**, do hệ thống tự nhận diện (FR-27);
- Cố vấn: vai trò là **người dùng chọn** (FR-18), lưu ở `localStorage` (FR-14).

**Lệch nhau cụ thể.** Người dùng nhắm `data-engineer`, dán một tin Java Backend.
- Dev B (Soi tin) nhóm theo ô `backend × mid`: `spring-boot` = **cốt lõi**, trọng số 3.
- Dev C (Cố vấn) nhóm theo ô `data-engineer × junior`: `spring-boot` = **riêng của công ty** ⇒ theo §3 **không bao giờ** là khoảng trống ⇒ không có trên lộ trình.

Cùng một kỹ năng, cùng một người, cùng một phiên: hai nhãn, hai màu, một bên nói "cốt lõi của thị trường", một bên không thèm hiển thị. Cả hai đúng AD-2 và AD-6.

Phiên bản nguy hiểm hơn: dev B có thể lập luận ngược — mức khớp là phần "so với hồ sơ", nên phải dùng ô của **vai trò mục tiêu người dùng** — rồi ví dụ kiểm tra `16/18 = 89%` của addendum chỉ tái lập được dưới **một** cách đọc. Hai dev viết hai kiểm thử, cả hai xanh, trên hai nghĩa khác nhau của "nhóm kỹ năng".

**Đề xuất — siết AD-2 + AD-6.**
> **Rule:** Nhãn nhóm kỹ năng **luôn đi kèm ô thống kê đã sinh ra nó**: mọi đối tượng kỹ năng trả về từ API có `group` **và** `group_cell` (cùng hình dạng `meta.stat_cell`); một response trả `group` mà thiếu `group_cell` là lỗi schema. Soi tin **bắt buộc** nhóm theo ô của tin (FR-27); Cố vấn **bắt buộc** nhóm theo ô của vai trò mục tiêu người dùng chọn (FR-18); mức khớp của FR-28 dùng **ô của tin**. Khi hai nhãn của cùng một mã kỹ năng xuất hiện trên cùng một màn hình, giao diện in rõ ô của từng nhãn.

---

### G-18 — `anon_events` có hai đường ghi khả dĩ `[medium]`

**Cặp đơn vị.**
- Story A (Sprint 4, dev B): "FR-26 — endpoint trích kỹ năng từ tin dán; mỗi lần soi tin ghi một sự kiện ẩn danh".
- Story B (Sprint 3, dev C): "FR-17 — sinh mã phiên ẩn danh và ghi sự kiện từ trình duyệt".

**Cả hai đều hợp lệ theo.** AD-11 **cho phép** endpoint trích xuất ghi "một hàng trong bảng sự kiện ẩn danh". Quy ước route **cũng** cho phép một endpoint `POST` riêng cho sự kiện ẩn danh. Nên tồn tại **hai** đường ghi hợp lệ cho cùng một sự kiện. FR-26 nói "mỗi lần soi tin ghi một sự kiện ẩn danh" mà không nói ai ghi.

**Lệch nhau cụ thể.** Dev B ghi phòng xa ở server; dev C ghi phòng xa ở client (vì FR-17 là story của dev C và dev C không biết dev B đã ghi). Mỗi lần soi tin ⇒ **hai** sự kiện. SM đo "số lần soi tin" **gấp đôi**, và đó là một con số **đi vào báo cáo SEP490**. Hoặc ngược lại: mỗi người tưởng người kia ghi ⇒ **không** sự kiện nào ⇒ chỉ số bằng 0, phát hiện ở Sprint 7.

Kiểm thử của AD-11 ("không bảng nào nhận văn bản CV hay JD") xanh trong cả bốn thế giới.

**Đề xuất — sửa AD-11.**
> **Rule:** `anon_events` có **đúng một** đường ghi: `POST /api/v1/anon-events`, do `web/` gọi. Endpoint trích xuất phù du (CV, JD) **không ghi gì cả** — câu "trừ một hàng trong bảng sự kiện ẩn danh" bị **xóa khỏi AD-11**, biến AD-11 thành "không có lệnh ghi nào", một luật kiểm được bằng một câu. Mỗi sự kiện mang `event_id` (UUID do trình duyệt sinh) với ràng buộc `UNIQUE`, nên ghi lặp là vô hại và đếm được bằng `COUNT(DISTINCT event_id)`.

---

## 3. Những chỗ spine đã bịt tốt (để không siết trùng)

Để bản rà soát này không bị đọc thành "mọi thứ đều hỏng", xin ghi nhận các chỗ mà tôi **đã thử tấn công và thất bại**:

- **AD-3** (LLM chỉ trả lượt nhắc nguyên văn; mapping tất định) bịt rất chặt. Tôi không dựng được cặp nào trong đó hai dev cho ra hai mã kỹ năng khác nhau cho cùng một lượt nhắc — vì mapping là hàm thuần trong `domain` và AD-2 chặn bản "đơn giản hóa". Chỗ còn hở nằm ở **mã kỹ năng mới** (G-10), không ở phép mapping.
- **AD-12** (hai loại cạnh không trộn) bịt kín. Tôi đã thử dựng cặp "dev A dùng đồng xuất hiện làm trọng số cho tầng 3" vs "dev B dùng tỷ lệ xuất hiện" — AD-12 nói rõ tần suất và đồng xuất hiện "**chỉ** dùng cho tầng 2–3", và FR-22 nói tầng 3 là *tỷ lệ xuất hiện giảm dần*. Hai câu này cộng lại đã loại được đồng xuất hiện khỏi tầng 3.
- **AD-15** (orchestrator là vỏ mỏng, mỗi bước một CLI, không import Dagster) rất tốt và kiểm được bằng một kiểm thử `import`. Lỗ hổng tôi tìm được quanh nó (G-04a) là về **lũy đẳng**, không về ranh giới.
- **AD-16** (ranh giới scraper kế thừa, file JSONL chỉ còn là tiện ích dev) loại được đúng cái bẫy "hai nguồn sự thật" mà một đồ án kế thừa code crawler gần như luôn mắc.
- **AD-14** (trang công khai chỉ đọc bảng tổng hợp, không bao giờ render `description`) là một luật kiểm được bằng grep. Không có chỗ hở.
- **AD-9** (một cổng trích xuất, dán nhãn `model_id`/`prompt_version`/`vocab_version`) đã bịt được chuyện "hai nhà cung cấp hai cách đánh phiên bản".

---

## 4. Thứ tự đề nghị bịt

Nếu chỉ có thời gian cho một buổi sửa spine trước khi chia epic, tôi đề nghị đúng thứ tự này — xếp theo "nếu không bịt bây giờ thì sửa sau tốn bao nhiêu":

| Thứ tự | Bịt | Vì sao trước |
|---|---|---|
| 1 | **G-06** (danh sách chờ + khóa ngoại `anon_events`) | Là cam kết riêng tư, và có một đường thoát "hợp lệ" làm rò nội dung JD. Sửa sau = sửa cả schema lẫn cam kết công khai |
| 2 | **G-07** (AD-17 vs FR-33) | Mâu thuẫn tường minh giữa AD và FR. Nếu không bịt, dev C **sẽ** tính tỷ trọng ở frontend, và chuyện đó lan sang mọi màn hình |
| 3 | **G-13** (quy ước route buộc frontend tính mức khớp) | Cùng loại: spine đang chặn đường đúng. Phải mở `GET ?have=` ngay, vì nó quyết định hình dạng của mọi endpoint phụ thuộc hồ sơ ở Sprint 3 |
| 4 | **G-03** (`n_with_value`) | Là một cột. Thêm ở Sprint 2 gần như miễn phí; thêm ở Sprint 7 nghĩa là tính lại mọi snapshot |
| 5 | **G-02** + **G-12** (dân số của ô + bảng ngưỡng) | Hai cái này là một: định nghĩa "một tin được đếm" và "con số 30". Chúng là nền của mọi con số trong sản phẩm |
| 6 | **G-04b** (nguồn lỗi thì không công bố) | Quyết định ở Sprint 1, hậu quả ở Sprint 4 (D4). Rẻ bây giờ, không sửa được sau |
| 7 | **G-01** + **G-11** (`Meta` một model + `stat_*` là con của `stat_cells`) | Hình dạng và schema. Đặt trước khi có bảng thứ hai |
| 8 | Phần còn lại (G-05, G-08, G-09, G-10, G-14..G-18) | Đều nên bịt, nhưng chi phí sửa sau không tăng theo hàm mũ |

Hai lỗ hổng (G-06 ở nửa FR-29, G-07) **không phải chỗ spine thiếu chữ** — chúng là **mâu thuẫn giữa spine và PRD**. Hai chỗ đó cần một quyết định của PM, không chỉ một AD mới; nếu PM chọn giữ AD-17 nguyên văn thì FR-33 phải sửa, và ngược lại.
