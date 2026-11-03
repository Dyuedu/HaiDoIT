---
title: "Rà soát toàn vẹn dữ liệu và đúng đắn thống kê — ARCHITECTURE-SPINE Hải Đồ IT"
lens: data-integrity
target: _bmad-output/planning-artifacts/architecture/architecture-HaiDoIT-2026-11-03/ARCHITECTURE-SPINE.md
baseline:
  - _bmad-output/planning-artifacts/prds/prd-HaiDoIT-2026-11-02/prd.md
  - _bmad-output/planning-artifacts/prds/prd-HaiDoIT-2026-11-02/addendum.md
created: 2026-11-03
---

# Rà soát toàn vẹn dữ liệu và đúng đắn thống kê

## 0. Verdict

**Spine chưa đủ để bảo đảm con số đúng: tuân thủ đầy đủ cả 18 AD vẫn cho ra số sai hoặc số không nhất quán ở ít nhất bốn đường độc lập nhau.**

Câu hỏi của lăng kính này không phải "kiến trúc có đẹp không" mà: *nếu ba người lập trình làm đúng từng chữ trong 18 AD, con số hiện lên màn hình có đúng không.* Trả lời: không.

Nguyên nhân gốc không phải một AD nào sai, mà là **danh sách invariant dừng quá sớm**. AD-2, AD-3, AD-6, AD-7, AD-12 khóa rất tốt *bộ máy kỹ năng* và *bộ máy lộ trình học* — đúng hai chỗ mà "hai bản cài đặt cho hai con số" dễ xảy ra nhất. Nhưng sản phẩm này có **năm** bộ máy sinh số, không phải hai. Ba bộ còn lại — **ghép trùng**, **phân loại vai trò/cấp bậc**, **phân vị** — không có AD nào gác, và cả ba đều được gọi ở *hai* nơi (bước pipeline hằng đêm và đường Soi tin lúc chạy). Đó là nơi phần lớn phát hiện dưới đây nằm.

Bốn lỗ hổng mà reviewer đối kháng đã tìm ra và coordinator đã nhận (`n_with_value`, AD-17 vs FR-33, chủ sở hữu định nghĩa dân số ô, snapshot-theo-ngày vs vòng đời-theo-lượt-chạy) **không được lặp lại ở đây**. Tài liệu này chỉ nhận xét chỗ nào trong *cách bịt đã đề xuất* còn hở (§1), rồi tập trung vào phần còn lại (§2 trở đi).

Điểm quan trọng nhất cần nói ngay: **cách bịt cho lỗ thứ tư — "thêm trạng thái partial + `meta.sources_failed`" — không giải quyết xung đột giữa snapshot bất biến và vòng đời tin.** Nó giải quyết một vấn đề khác (minh bạch về đêm lỗi, NFR khả dụng). Xung đột bất biến vẫn còn nguyên và vẫn là mức critical. Chi tiết ở §2.

---

## 1. Nhận xét về bốn cách bịt đã nhận

Không lặp lại chẩn đoán. Chỉ nêu chỗ cách bịt còn sai hoặc còn hở.

### 1.1 `n_with_value NOT NULL` + `meta.n_by_measure` — đúng hướng, còn hở ba chỗ

- **Chưa nói `n` nào gác dải CI của FR-9.** FR-9 tính bootstrap cho `30 ≤ n < 100`. Thêm `n_with_value` vào bảng mà không sửa phát biểu này thì người cài vẫn đọc `stat_cell.n`. Hệ quả cụ thể và rất thường gặp vì §6.3 nói chỉ ~24% tin có lương: ô `n = 320`, `n_salary = 95` → xét theo `n` thì 320 ≥ 100 ⇒ **không tính CI**, trong khi mẫu thật là 95, đúng dải cần CI nhất. Người dùng thấy một phân vị lương mẫu 95 **không kèm khoảng tin cậy** — mất đúng thứ mà §6.5 bài toán khó số 3 lấy làm thành tựu. Cần viết rõ: *dải CI xét trên `n_with_value` của chính thước đo*, và `meta.n` của một con số luôn là mẫu số **của con số đó**, không bao giờ là `n` của ô.
- **Khóa đọc trong phát biểu AD-5 vẫn sai.** AD-5 viết "đọc từ bảng tổng hợp theo khóa `(snapshot_id, stat_cell_id)`". Khóa đó thiếu `measure` và `p`. FR-30 có ba thước đo, D1/D3 cần P25/P75/P90, cộng phân vị của chính tin → một ô có hàng chục hàng `stat_percentile`. Thêm cột `n_with_value` không sửa được một **phát biểu Rule sai**, và Rule là thứ sẽ được copy vào code. Khóa đúng: `(snapshot_id, stat_cell_id, measure, p)`.
- **Thiếu các cột làm con số tự khai báo.** Cùng lần migration đó nên thêm `ci_low`, `ci_high`, `ci_level`, `b`, `method`, `seed`. Lý do `method` và `seed` là bắt buộc chứ không phải "nice to have": xem §4 và §5.

### 1.2 Thay AD-17 bằng `meta.suppression` do một hàm `domain` quyết — đúng hướng, còn hở bốn chỗ

Đặt quyết định vào một hàm `domain` là đúng (nó song song với AD-6: thứ tự quay về cũng là một hàm duy nhất). Nhưng `suppression` dạng một trường cho cả response sẽ tái tạo đúng vấn đề của AD-17:

- **Phải theo từng thước đo, không theo response.** UJ-2 bước 4 mô tả cảnh bắt buộc phải diễn đạt được: *"mục lương ghi 'chưa đủ dữ liệu (X/30 tin có lương)'. Mục số kỹ năng yêu cầu thì vẫn hiển thị phân vị bình thường."* Một `meta.suppression` cho cả response không biểu diễn được "lương: ẩn; số kỹ năng: hiện".
- **Trạng thái "ẩn" vẫn phải trả về `n_used`.** FR-30 buộc in ra `X` trong "chưa đủ dữ liệu (X/30 tin có lương)", và `X < 30`. Nếu `suppression` làm rỗng luôn mẫu số thì không in được câu đó.
- **Cần ít nhất ba trạng thái, không phải hai.** FR-33 không cần "ẩn" cũng không cần "hiện bình thường": nó cần **hiện giá trị thật kèm dấu bất định** (cột mờ + nhãn). Nên: `ok` | `low_confidence` (có `value` thật, `n_used < 30`) | `insufficient` (`value = null`, vẫn có `n_used`) | `not_applicable` (tin không có trường đó). Và `low_confidence` phải đi kèm **một danh sách đóng các bề mặt được phép dùng nó** — hiện chỉ có chiều cao cột của FR-33. Nếu để mở, "mờ + nhãn" sẽ lan sang Soi tin và Insights, rồi §5 mất nghĩa.
- **Quyết định phải xảy ra *sau* khi quay về hết bốn bước của AD-6.** Nếu hàm `domain` nhận `n` của ô người dùng yêu cầu, nó sẽ ẩn đúng những ca mà AD-6 vừa giải quyết xong bằng thứ tự quay về, làm AD-6 thành vô dụng. Chữ "sau khi quay về" phải nằm trong Rule.
- Một ghi chú về lập luận: *một tỷ trọng tính trên n = 25 không phải "con số đoán".* §5 cấm hiển thị con số đoán, không cấm hiển thị con số thật kèm cảnh báo. Với cột bản đồ, **ẩn mới là nói sai**: người đọc thấy hai cột rồi kết luận "Đà Nẵng không có thị trường IT", trong khi sự thật là "Đà Nẵng có 64 tin". Addendum §3 đã loại phương án buộc phải "ẩn cột Đà Nẵng" — nên bản viết lại cần ghi rõ đây là **ngoại lệ có chủ ý** của §5, kèm lý do, để không bị một reviewer sau lật lại.

### 1.3 AD mới cho định nghĩa dân số ô (cửa sổ 60 ngày + đếm theo cụm) — đúng, nhưng sẽ vẫn sai nếu thiếu một câu

AD mới này là bắt buộc, và nó phải chứa **câu sau**, nếu không nó sẽ trông đúng mà vẫn cho số sai khi tính lại:

> Cửa sổ 60 ngày được xét trên **trạng thái vòng đời thuộc chính snapshot đang dùng**, không bao giờ trên `last_seen` hiện thời.

Lý do: `last_seen` là trạng thái sống (xem §2). Tính lại ô thống kê "như ở snapshot 26/10" bằng `last_seen` của hôm nay cho hai lỗi đối xứng:
- tin còn sống ở 26/10 nhưng chết ngày 01/11 → bị **loại oan** khỏi ô của 26/10;
- tin thấy lần cuối 20/10 rồi được đăng lại 10/11 → `last_seen` thành 10/11, **lọt vào** ô của 26/10 dù lúc đó đã quá cửa sổ.

Nói cách khác: lỗ hổng số 3 và lỗ hổng số 4 **là một gói, không sửa được riêng lẻ**. AD mới về dân số ô chỉ đứng được nếu mô hình vòng đời được sửa theo §2.

Hai chi tiết nhỏ nên gộp vào cùng AD:
- `window_days` và ngưỡng mẫu `30` vào **bảng cấu hình có phiên bản** của AD-10, và `stat_cells` lưu kèm `window_days`, `window_end` đã dùng. Hiện AD-10 liệt kê θ, tỷ giá, công tắc nguồn, ngưỡng D1–D7 — **không có** 60 ngày, không có 30, dù cả hai đúng tiêu chí "tham số hiệu chỉnh được" mà chính AD-10 đặt ra.
- **Bỏ `NULL` khỏi khóa ô thống kê.** Khóa của AD-6 là `(snapshot_id, role, branch, seniority, scope)`, và thứ tự quay về cần "mọi nhánh"/"mọi cấp bậc" — cách viết tự nhiên nhất là `NULL`. Trong PostgreSQL, `UNIQUE` **không chống trùng** khi có `NULL` (`NULL <> NULL`), nên `aggregate` chạy lại một phần sẽ sinh hàng thứ hai thay vì ghi đè → `n` đếm đôi; và `WHERE branch = $1` với `$1 = NULL` trả **rỗng**, nên tầng đọc nhận 0 hàng rồi hoặc báo "chưa đủ dữ liệu" sai, hoặc nhảy sang bước quay về tiếp theo và in nhãn cỡ mẫu sai. Dùng sentinel `'_all'`, thêm `cell_shape ∈ {advisor, map}` với `CHECK` buộc mỗi hình dạng chỉ dùng chiều của nó (§3 định nghĩa **hai** hình dạng ô khác nhau: vai trò × cấp bậc toàn quốc, và thành phố × vai trò không có cấp bậc). Thêm một dòng vào Consistency Conventions: *khóa bảng tổng hợp không bao giờ chứa `NULL`*.

### 1.4 Trạng thái `partial` + `meta.sources_failed` — **không bịt lỗ hổng mà nó được gán cho**

Đây là chỗ cần nói mạnh nhất trong §1.

`partial` + `sources_failed` giải quyết **minh bạch về đêm lỗi**: người đọc biết snapshot này thiếu nguồn nào. Đó là một bổ sung tốt cho NFR khả dụng và cho FR-36. Nhưng nó **không chạm tới** xung đột "snapshot bất biến vs vòng đời xuyên snapshot":

- Sau khi thêm `partial`, vòng đời tin **vẫn** nằm ở `job_raw` và **vẫn** bị `UPDATE` mỗi đêm. Nên D4 ("tin đã đăng lại X lần") **vẫn** không truy ngược được về snapshot nào, và **vẫn** không tất định: cùng một tin dán lại, cùng `meta.snapshot_date`, hai thời điểm cho hai con số. Vi phạm §5 ở cả hai gạch đầu dòng ("dấu hiệu cần kiểm tra là tất định" và "mọi con số truy ngược được về snapshot đã tạo ra nó").
- Cửa sổ 60 ngày **vẫn** không tính lại được cho snapshot cũ (§1.3).
- FR-3 **vẫn** không có mô hình dữ liệu để cài: "vắng mặt ở ít nhất 3 lần chạy thành công liên tiếp **của chính nguồn đó**" cần nối **từng quan sát tin** với **từng lượt chạy**. `meta.sources_failed` là metadata ở tầng đọc, không phải một quan hệ trong kho dữ liệu. ERD có `SOURCE ||--o{ PIPELINE_RUN` (tốt) nhưng `JOB_RAW` chỉ treo vào `SOURCE`, **không** vào `PIPELINE_RUN` — nên phép "vắng mặt 3 lượt chạy thành công liên tiếp" không viết được thành câu truy vấn.

Kết luận: giữ `partial` + `sources_failed` (nó đáng giá cho FR-36 và NFR khả dụng), nhưng **đừng tính nó là cách bịt cho lỗ hổng vòng đời tin**. Cách bịt thật ở §2.

---

## 2. Câu 2 — xung đột giữa snapshot bất biến và vòng đời tin xuyên snapshot

### 2.1 Xung đột là xung đột cấu trúc, không phải chi tiết cài đặt

Bốn phát biểu sau của spine và PRD **không thể cùng đúng**:

1. **AD-16:** "một bước `ingest` duy nhất ghi chúng vào `job_raw` kèm `snapshot_id` và `source`" ⇒ `job_raw` là **bảng quan sát theo snapshot**: một hàng cho mỗi (tin, đêm thấy nó).
2. **Structural Seed:** `ingest vào job_raw + vòng đời tin` ⇒ vòng đời nằm cùng chỗ đó.
3. **§3 Bảng thuật ngữ:** vòng đời tin là "bốn thông tin của một tin **qua các snapshot**" ⇒ thuộc tính của **danh tính tin**, không của một lần quan sát.
4. **AD-4:** "hàng thuộc snapshot đã công bố không bao giờ bị sửa hay xóa".

Ép bốn phát biểu lại thì chỉ còn hai cách cài, và cả hai đều sai:

**Cách A — cột vòng đời nằm trên hàng quan sát, cập nhật mỗi đêm cho khớp.** Để bốn con số của một tin nhất quán giữa các hàng, bước `ingest` phải ghi lại các hàng của những đêm trước ⇒ **sửa hàng thuộc snapshot đã công bố ⇒ vi phạm AD-4 trực tiếp**. Có thể cãi rằng `job_raw` "không phải bảng tổng hợp" nên AD-4 không áp — nhưng AD-4 nói "hàng thuộc snapshot đã công bố", và `job_raw` theo AD-16 mang `snapshot_id`. Nếu định nghĩa hẹp lại thành "chỉ bảng `stat_*` mới bất biến" thì phải nói ra, và khi đó mất luôn khả năng tính lại một snapshot cũ từ dữ liệu nền — tức là mất tính truy vết ở mức sâu hơn.

**Cách B — `job_raw` là một hàng cho mỗi tin, cột vòng đời bị `UPDATE` mỗi đêm.** Khi đó `snapshot_id` trên `job_raw` mất nghĩa (snapshot nào? lần đầu thấy?), `job_raw` trở thành bảng trạng thái hiện thời, và **mọi phép cần "trạng thái vòng đời *tại* snapshot S" là không thể** vì `last_seen` đã bị ghi đè. Hệ quả: cửa sổ 60 ngày không tính lại được (§1.3), D4 không tất định, và kết quả kiểm chứng của FR-3 *"một tin xuất hiện trong 3 snapshot liên tiếp có số lần thấy bằng 3"* không kiểm lại được sau khi đã qua snapshot thứ tư — nó chỉ kiểm được **đúng lúc** nó vừa xảy ra.

### 2.2 Một đòi hỏi của FR-3 mà cả hai cách đều không đáp được

FR-3 có hai kết quả kiểm chứng được mà mô hình hiện tại **không có đường cài**, độc lập với việc chọn cách A hay B:

> - Một tin chỉ được coi là đã biến mất khi vắng mặt ở **ít nhất 3 lần chạy thành công liên tiếp của chính nguồn đó**. Khi xuất hiện lại sau đó, tin được tính thêm một lần đăng lại.
> - Một đêm nguồn bị lỗi hoặc bị dừng (FR-2) **không bao giờ** làm tăng số lần đăng lại.

Phép này phải phân biệt ba trạng thái, không phải hai: **"đêm đó thấy tin"**, **"đêm đó không thấy tin"**, **"đêm đó nguồn hỏng nên không biết"**. Muốn vậy cần nối từng quan sát với **lượt chạy** và trạng thái thành công của lượt chạy đó. ERD không có thực thể nào làm việc này. Và như §1.4 đã nói, `meta.sources_failed` ở tầng đọc không thay thế được một quan hệ trong kho.

Điều này cũng là lý do `partial` không đủ: một nguồn có thể **thành công một phần** (crawl được 3 trang rồi gặp 429 và dừng theo FR-2). Lúc đó những tin ở các trang chưa crawl "vắng mặt" mà không phải vì đã bị hạ. Nếu `repost_count` tăng vì chuyện đó, D4 sẽ kích hoạt sai trên hàng loạt tin — đụng trực tiếp SM-C3 ("một dấu hiệu kích hoạt trên quá nhiều tin sẽ mất tác dụng cảnh báo"). Vậy trạng thái lượt chạy cần ít nhất `success | partial | failed`, và **chỉ `success` được tính vào chuỗi "3 lần vắng mặt"**.

### 2.3 Cách giải đề xuất — tách ba thực thể

```
JOB_POSTING          -- danh tính tin ở một nguồn: (source_id, external_key) UNIQUE
                     -- KHÔNG có snapshot_id. Bảng chiều, sống mãi.
                     -- -> company_id (xem §6.3)

JOB_OBSERVATION      -- sự thật bất biến, CHỈ GHI THÊM, không bao giờ UPDATE:
                     -- (posting_id, snapshot_id, pipeline_run_id, text_hash, ...)
                     -- một hàng cho mỗi đêm tin đó ĐƯỢC THẤY.

PIPELINE_RUN         -- đã có trong ERD; thêm status ∈ {success, partial, failed}
                     -- và phạm vi đã quét (để phân biệt "không thấy" với "chưa quét")

STAT_JOB_LIFECYCLE   -- vật hóa THEO SNAPSHOT, bất biến, công bố trong cùng
                     -- transaction của AD-4:
                     -- (snapshot_id, posting_id, first_seen, last_seen,
                     --  times_seen, repost_count, is_active_60d)
                     -- Tính từ JOB_OBSERVATION ⨝ PIPELINE_RUN(status='success').
```

Bốn hệ quả, mỗi cái sửa đúng một chỗ:

1. **D4 đọc `STAT_JOB_LIFECYCLE` theo `(snapshot_id, posting_id)`** ⇒ tất định và truy vết được. "Tin đã đăng lại 2 lần" trở thành một con số **thuộc** snapshot, đúng như §5 đòi.
2. **Cửa sổ 60 ngày thành cột `is_active_60d` thuộc snapshot** ⇒ tính lại được cho snapshot cũ, và AD mới về dân số ô (§1.3) đứng được.
3. **FR-3 có đường cài:** "vắng mặt 3 lượt chạy thành công liên tiếp" là một phép window trên `JOB_OBSERVATION ⨝ PIPELINE_RUN WHERE status='success'`. "Đêm nguồn lỗi không làm tăng số lần đăng lại" thành **tính chất của câu truy vấn**, kiểm được bằng một kiểm thử có tên `test_fr3_dem_loi_khong_tang_dang_lai`, thay vì một lời hứa suông.
4. **AD-4 không phải nhượng bộ gì.** `JOB_OBSERVATION` chỉ ghi thêm (append-only) nên bất biến tự nhiên; `STAT_JOB_LIFECYCLE` là một bảng `stat_*` như mọi bảng khác, công bố nguyên khối cùng snapshot.

**Chi phí.** Khoảng 3.500 tin đang hoạt động × 25–90 snapshot của v1 ≈ 90.000–315.000 hàng cho mỗi bảng. Trên PostgreSQL 18 ở VPS 4 GB là không đáng kể. Muốn tiết kiệm hơn: chỉ vật hóa `STAT_JOB_LIFECYCLE` cho tin `is_active_60d = true`, giữ `JOB_OBSERVATION` làm nguồn sự thật để tính lại.

**Nếu nhóm quyết không tách bảng** (sprint chật), thì phải **hạ lời hứa cho khớp**, bằng một dòng trong AD-4: *"vòng đời tin là trạng thái hiện thời, không thuộc snapshot nào; D4 vì vậy không mang nhãn snapshot và nằm ngoài phạm vi NFR tất định; cửa sổ 60 ngày chỉ đúng cho snapshot mới nhất."* Lựa chọn này tệ hơn nhưng **trung thực**. Giữ nguyên spine như hiện tại là lựa chọn vừa sai vừa không nhìn thấy — và nó sẽ hiện ra đúng lúc hội đồng hỏi "con số này tính lại được không".

### 2.4 Hai thứ xuyên snapshot khác, cùng loại bệnh

Để AD-4 phủ hết, cần cho **ba** loại dữ liệu xuyên snapshot một chỗ ở hợp pháp, không chỉ một:

- **Vòng đời tin** — §2 này.
- **Thành viên cụm tin** — §3.
- **Danh sách chờ lượt nhắc chưa khớp** (`UNKNOWN_MENTION`). Addendum FR-29/FR-6 nói bảng này lưu *"từ khóa, tần suất, lần thấy gần nhất"* — tức là cũng là trạng thái tích lũy xuyên snapshot. Mức độ nhẹ hơn vì nó chỉ dùng nội bộ (nhóm rà hằng tuần), không hiển thị cho người dùng. Nhưng nếu muốn báo cáo "độ phủ bộ từ vựng theo thời gian" trong chương Thực nghiệm thì cùng bệnh, cùng cách chữa: tần suất theo snapshot, không tích lũy tại chỗ.

---

## 3. Cụm tin trùng — ba vấn đề chưa ai nhận (FR-4, AD-4)

Câu hỏi "mô hình JOB_CLUSTER/JOB có bảo đảm đếm một lần không" chưa nằm trong bốn lỗ hổng đã nhận. Trả lời: **về cấu trúc thì gần đủ; về invariant thì không; về thời gian thì sai.**

### 3.1 (high) Không có invariant nào buộc đếm theo cụm

`JOB_RAW }o--|| JOB_CLUSTER` + `JOB_CLUSTER ||--|| JOB` *cho phép* đếm một lần — **nếu** bước `aggregate` đếm `JOB`. Nhưng không AD nào nói phải vậy. AD-5 chỉ cấm `haido_api` tổng hợp; AD-6 nói `stat_cells` lưu `n` mà không nói `n` đếm gì. Bước `aggregate` nằm trong `steps/`, được phép đọc mọi thứ, và `JOB_RAW` là bảng tự nhiên nhất để `GROUP BY` vì nó mang sẵn `snapshot_id` và `source`.

Một người viết `COUNT(DISTINCT job_raw.id)` thay vì `COUNT(DISTINCT job.id)` sẽ **đếm tin TopCV và tin ITviec của cùng một vị trí thành hai**. Với TopCV chiếm ~38% dữ liệu nền (§6.1), độ phình này không nhỏ: nó đẩy ô qua ngưỡng 30 một cách giả tạo, làm thứ tự quay về của AD-6 chọn sai ô, và làm tỷ lệ xuất hiện lệch về phía nguồn có nhiều bản sao.

Lời hứa quan trọng nhất của FR-4 — *"mọi con số thống kê tính mỗi cụm đúng một lần"* — hiện chỉ là một câu trong PRD, **không phải một invariant kiến trúc**.

**Đề xuất: AD mới — "Cụm tin là đơn vị đếm duy nhất".** Mọi phép đếm, mọi tỷ lệ, mọi phân vị trong `aggregate` đi qua cụm, không bao giờ qua tin thô. Kiểm thử: tổng `n` của các ô bằng số **cụm** hoạt động, không bằng số tin thô. Cấm `COUNT` trên `job_raw`/`job_posting` ngoài bảng vận hành của FR-1.

### 3.2 (high) Thành viên cụm đổi qua các đêm, cụm không gắn snapshot

`JOB_CLUSTER` và `JOB` không treo vào `SNAPSHOT`. Mỗi đêm `dedupe` chạy lại và có thể **gộp** hai cụm (tìm được cặp trùng đêm trước chưa ra), **tách** một cụm (sửa một lần gộp sai), hoặc **đổi tin đại diện**.

Vì `stat_*` bất biến theo AD-4, con số đã công bố không đổi — nhưng điều đó chỉ làm vấn đề **khó thấy hơn**: snapshot 26/10 nói `n = 52`; tính lại hôm nay cho cùng snapshot 26/10 ra `n = 49`; và **không có cách nào biết số nào đúng**, vì mô hình cụm không có phiên bản. Kéo theo:

- D4 đọc vòng đời của cụm; cụm gộp thì "số lần đăng lại" **nhảy lên hồi tố**;
- FR-32 (*"dán lại nguyên văn một tin đã có trong dữ liệu thì tìm được đúng tin đó"*) có thể trả về một đại diện khác lần trước;
- SM-7 (precision/recall ghép trùng) đo trên một mô hình cụm không có phiên bản thì không tái lập được — bài toán khó số 1 của §6.5 mất chỗ dựa.

### 3.3 (high) Không có quy tắc chọn tin đại diện — đây là chỗ sinh **số sai**, không chỉ số không nhất quán

Khi một cụm có 2 tin từ 2 nguồn, chúng thường khác nhau ở **đúng những trường mà thống kê dùng**:

| Trường | Ví dụ lệch | Con số bị ảnh hưởng |
|---|---|---|
| lương | TopCV "15–20 triệu" vs ITviec "thỏa thuận" | tin này có vào mẫu số phân vị lương không, và với giá trị nào — FR-30, D3, `n_salary` |
| cấp bậc | "Fresher" vs "Junior/Mid" | **tin thuộc ô thống kê nào** — AD-6, FR-7, FR-19 |
| thành phố | "Hà Nội" vs "Hà Nội, TP.HCM" | FR-33, FR-34, tổng tỷ trọng 100% |
| tập kỹ năng | hai bản mô tả khác độ dài | D1 (số kỹ năng so P90), D2, FR-28 |

Spine **im lặng hoàn toàn**. Im lặng ở đây nghĩa là **thứ tự trả về của cơ sở dữ liệu quyết định con số** — đúng loại lỗi mà addendum FR-22 đã cẩn thận chặn cho lộ trình học (*"không bao giờ phụ thuộc vào thứ tự trả về của cơ sở dữ liệu"*) nhưng không ai chặn cho cụm tin. Hai lần chạy `aggregate` trên cùng dữ liệu có thể cho hai `n_salary` khác nhau.

### 3.4 (critical) Dòng dữ liệu một đêm xếp sai thứ tự so với FR-4

Structural Seed vẽ: `ingest → dedupe → mentions → mapping → classify → salary → aggregate`.

FR-4 tầng hai: *"**giữa các nguồn:** dựa trên tên công ty đã chuẩn hóa, kết hợp với **độ tương đồng về kỹ năng**"*. Và `.memlog.md` ghi rõ cách cài đã chốt: *"FR-4 ghép trùng dùng **Jaccard trên tập mã kỹ năng**"*.

**Tập mã kỹ năng là đầu ra của `mapping`, nằm sau `dedupe` hai bước.** Bước `dedupe` như vẽ **không có đầu vào** để thực hiện tầng hai của FR-4. Mọi cách sắp lại đều trả giá:

- **Giữ nguyên thứ tự, tầng hai dùng thứ khác** (tương đồng văn bản thô): khác đặc tả FR-4 và khác memlog; SM-7 đo một thuật toán khác thuật toán đã thiết kế; và tương đồng văn bản thô giữa hai sàn thường thấp (mỗi sàn viết lại mô tả) nên recall tệ — bài toán khó số 1 của §6.5 bị làm hỏng.
- **Đổi thành `ingest → mentions → mapping → dedupe → ...`**: đúng về dữ liệu, nhưng LLM chạy trên **mọi tin thô kể cả bản sao**. Nếu tỷ lệ trùng chéo nguồn là 20–30%, chi phí trích xuất hằng đêm tăng tương ứng — đụng trần 5–10 USD/tháng của §6.4, chính là thứ spine dùng làm lý do loại Airflow.
- **Hai pha (đúng nhất):** `dedupe-trong-nguồn` (mã tin, URL, hash nội dung — tầng một, rẻ, không cần kỹ năng) đặt **trước** `mentions`; `cluster-chéo-nguồn` (tên công ty chuẩn hóa + Jaccard mã kỹ năng — tầng hai) đặt **sau** `mapping` và **trước** `aggregate`. Tầng một đã loại phần lớn bản sao nên chi phí LLM gần như không tăng; tầng hai có đúng dữ liệu nó cần.

### 3.5 Ràng buộc kéo theo: lượt nhắc kỹ năng phải treo vào tin thô, không vào cụm

ERD hiện là `JOB ||--o{ JOB_SKILL_MENTION`, tức lượt nhắc treo vào **đại diện cụm**. Khi đại diện đổi, tập lượt nhắc của cụm phải đổi theo ⇒ hoặc **gọi lại LLM** (đốt chi phí trái §6.4), hoặc **giữ lượt nhắc của một văn bản không còn là đại diện** (số sai). Và nó khóa luôn §3.4: không thể trích kỹ năng *trước* khi biết đại diện, mà ghép trùng chéo nguồn lại cần kỹ năng *trước* khi lập cụm.

**Đề xuất gói cho §3:**

```
JOB_CLUSTER                 -- cluster_id ổn định, không snapshot_id
STAT_CLUSTER_MEMBERSHIP     -- (snapshot_id, cluster_id, posting_id, is_representative)
                            -- vật hóa theo snapshot, bất biến, công bố cùng AD-4
JOB_SKILL_MENTION           -- treo vào (posting_id, text_hash), KHÔNG treo vào cụm.
                            -- cache theo text_hash => đổi đại diện không tốn LLM
```
- Quy tắc chọn đại diện **viết rõ và tất định**, đặt trong `domain`: ví dụ "ưu tiên nguồn theo thứ tự trong bảng cấu hình → tin có nhiều trường không rỗng nhất → `last_seen` mới nhất → `external_key` A–Z". Không khóa nào bỏ lửng.
- **Hoặc tốt hơn:** định nghĩa **hợp nhất theo từng trường** (lương: lấy giá trị dạng số nếu có, lệch thì theo ưu tiên nguồn; cấp bậc: lấy cấp thấp nhất; thành phố: hợp tập; kỹ năng: hợp tập mã) thay vì "một tin thắng tất cả". Phép nào cũng được, miễn **viết ra** và nằm **một chỗ** trong `domain`.
- Thêm `cluster_algo_version` vào `SNAPSHOT` (xem §4).

---

## 4. Câu 5 — `vocab_version` / `config_version`: snapshot cũ còn so sánh được với snapshot mới không?

**Spine chưa nói gì về việc đó, và đây là một lỗ hổng thật, mức high.**

### 4.1 Hiện trạng

- `config_version`: **có**, qua `APP_CONFIG ||--o{ SNAPSHOT` và AD-10 ("mỗi snapshot lưu lại `config_version` đã dùng"). Đúng chỗ.
- `vocab_version`: **chỉ** nằm trên bản ghi kết quả trích xuất (AD-9). **Không** trên `SNAPSHOT`, không trên `STAT_CELL`, không trên `STAT_SKILL_RATE`.
- `cluster_algo_version`: **không tồn tại** (§3.2).
- `meta` của AD-17: **không mang cái nào trong ba**.
- Không AD nào nói gì về việc so sánh hai snapshot có phiên bản khác nhau.

### 4.2 Ba hệ quả

**(a) Một con số đã công bố không truy ngược được về bộ từ vựng sinh ra nó.** Tỷ lệ "PostgreSQL 27%" phụ thuộc hoàn toàn vào việc bộ từ vựng có bí danh "Postgres", "PSQL", "Postgre" hay không. Thêm ba bí danh, tỷ lệ nhảy lên 31% và kỹ năng **đổi từ *thường gặp* sang *cốt lõi*** — mà không một con số nào trong hệ thống ghi lại vì sao. NFR truy vết nói *"mọi kết quả trích xuất bằng LLM truy ngược được về phiên bản model và prompt"*, và AD-9 làm đúng việc đó. Nhưng **bảng tổng hợp** thì không — và bảng tổng hợp mới là thứ người dùng thấy. Lời hứa ở §1 của PRD là *"mọi con số đi kèm cỡ mẫu, nguồn và ngày của snapshot"*: **ngày của snapshot không đủ** để xác định nghĩa của con số. Nghĩa của nó là hàm của **(dữ liệu, bộ từ vựng, cấu hình, cửa sổ thời gian, mô hình cụm)**. Hiện `meta` mang một trong năm.

**(b) AD-3 để lửng một câu hỏi quyết định.** AD-3 nói *"Đổi bộ từ vựng ⇒ chạy lại **mapping**, không chạy lại LLM"*. Chạy lại mapping **trên dữ liệu nào**?

- **Chỉ trên snapshot đêm nay:** snapshot N dùng v2, snapshot N−1 dùng v1. Chuỗi snapshot trộn hai hệ quy chiếu. Mọi so sánh dọc thời gian — phần Deferred "xu hướng theo thời gian", và cả việc người dùng mở lại link FR-15 vào ngày khác rồi thấy lộ trình đổi — đang **so táo với lê**, và không ai biết.
- **Chạy lại trên toàn bộ lịch sử** để chuỗi đồng nhất: phải **ghi lại `stat_*` của các snapshot đã công bố ⇒ vi phạm AD-4 trực tiếp**.

Spine không chọn nhánh nào. Và đây không phải chi tiết hoãn được: FR-6 và FR-29 thiết kế **danh sách chờ rà hằng tuần**, nghĩa là bộ từ vựng sẽ đổi **khoảng 8 lần trong 8 tuần**. Đổi bộ từ vựng là **hành vi vận hành thường kỳ của v1**, không phải sự kiện hiếm.

**(c) θ cũng vậy, với một lối thoát một phần.** Hạ θ_core từ 30% xuống 25% làm nhóm kỹ năng đổi ⇒ trọng số 3/2/1 đổi ⇒ **mức khớp của cùng một tin, cùng một hồ sơ đổi, trong khi dữ liệu không đổi**. FR-9 có giảm nhẹ: *"θ được hiệu chỉnh **một lần** ở Sprint 2, rồi **đóng băng** trước đợt thử nghiệm ở Sprint 6–7"*. Nhưng đó là **kỷ luật quy trình, không phải tính chất hệ thống**, và nó chỉ bảo vệ cửa sổ thử nghiệm — không bảo vệ bản công khai sau đó, đúng lúc §1 của PRD nói sản phẩm sẽ được "duy trì như một tiện ích cộng đồng".

### 4.3 Đề xuất

- **AD mới — "Ngữ nghĩa của một snapshot".** Mỗi `SNAPSHOT` lưu **bộ bốn** `(config_version, vocab_version, cluster_algo_version, window_days)`. `STAT_CELL` và `STAT_SKILL_RATE` chép lại bộ bốn (hoặc trỏ tới nó bằng một khóa duy nhất) để **một hàng bảng tổng hợp tự mô tả được**.
- `meta` của AD-17 mang bộ bốn đó, cạnh `snapshot_id` và `window_end`.
- **Quy tắc so sánh:** hai snapshot chỉ được đặt cạnh nhau trong một phép so sánh (xu hướng, delta, "tăng/giảm so với…") khi bộ bốn **trùng khớp**; khác nhau thì hoặc không so, hoặc so kèm nhãn "bộ từ vựng đã thay đổi giữa hai mốc". Có kiểm thử chặn.
- **Chốt nhánh của AD-3:** v1 chọn *"chỉ áp dụng từ snapshot kế tiếp, không chạy lại lịch sử"*; đổi bộ từ vựng **tăng `vocab_version`** và tạo một **ranh giới so sánh** được ghi lại. Lý do chọn: AD-4 bất khả xâm phạm, và v1 đã loại xu hướng theo thời gian khỏi phạm vi (§8.2), nên chi phí của ranh giới so sánh **gần bằng không ngay bây giờ** — nhưng chỉ khi nó được ghi lại, để tháng 03/2027 khi mở khóa xu hướng, nhóm biết chuỗi nào so được với chuỗi nào. Nếu không ghi, tháng 03/2027 sẽ không có cách nào dựng lại.
- Gợi ý vận hành rẻ: in bộ bốn vào chân trang công khai (AD-13 đã buộc in ngày snapshot, cỡ mẫu và danh sách nguồn — thêm hai chuỗi phiên bản là gần như miễn phí và rất có lợi khi bảo vệ đồ án).

---

## 5. Câu 6 — tính tất định của bootstrap (FR-9)

### 5.1 Chẩn đoán: không tất định, và spine không nhận ra

FR-9 là phép **lấy mẫu có hoàn lại, B = 1.000 lần**. Trong spine:

- **AD-10** liệt kê những tham số phải nằm trong bảng cấu hình có phiên bản: θ_core, θ_common, tỷ giá USD, công tắc nguồn, ngưỡng D1–D7. **Không có `B`. Không có seed.**
- **Consistency Conventions** không có dòng nào về số ngẫu nhiên (có dòng cho tỷ lệ, cho tiền, cho ngày, cho log — không cho RNG).
- **Stack** có SciPy 1.18.1. `scipy.stats.bootstrap` mặc định tạo một `Generator` mới mỗi lần gọi.
- **NFR §5** liệt kê những thứ phải tất định: *"Lộ trình học, mức khớp, dấu hiệu cần kiểm tra và câu kết luận của Insights"*. Chú ý: **phân vị và CI không có trong danh sách đó** — nhưng *"Mọi con số truy ngược được về snapshot đã tạo ra nó"* thì có, và **FR-30 hiển thị CI trực tiếp cho người dùng** ("lương của tin nằm ở phân vị 65% (khoảng tin cậy 52–74%)").

Hệ quả: **chạy lại bước `aggregate` cho cùng một snapshot cho ra CI khác.**

### 5.2 Vì sao lỗi này nguy hiểm hơn vẻ ngoài

Trong prod, AD-4 **che mất** chuyện này: snapshot đã công bố thì không ghi lại nữa, nên con số trên màn hình ổn định. Lỗi sẽ **không bao giờ lộ ra khi chạy bình thường** — và sẽ lộ đúng vào ba lúc tệ nhất:

1. **Kiểm thử của FR-37:** *"mỗi loại thẻ có kiểm thử so khớp con số hiển thị với một câu truy vấn kiểm tra độc lập **trên cùng snapshot**"*. Câu truy vấn độc lập sẽ ra CI khác. Kiểm thử đỏ ngẫu nhiên — và cách xử lý tự nhiên nhất của một nhóm 3 người đang chạy deadline là **nới biên độ cho tới khi nó xanh**, lúc đó kiểm thử không còn kiểm gì.
2. **SM-13** (thí nghiệm làm thưa mẫu xuống n = 100/50/30/15): toàn bộ biểu đồ sai số theo cỡ mẫu — thứ dùng để **trả lời hội đồng** câu *"vì sao chọn ngưỡng 30 mà không phải 20 hay 50"* — không tái lập được. §6.5 đặt đây là một trong **bốn bài toán khó** của đồ án, và SM-13 là thước đo duy nhất của nó.
3. **Backfill hoặc chạy lại một partition Dagster** sau khi sửa lỗi: snapshot mới công bố mang CI khác snapshot cũ cho cùng dữ liệu, không ai giải thích được.

### 5.3 Đề xuất

- **Seed dẫn xuất tất định theo khóa, không phải một seed toàn cục:**

  `seed = u64(blake2b(f"{snapshot_id}|{stat_cell_id}|{measure}|{p}"))`

  **Vì sao không dùng một seed toàn cục:** Dagster có thể tính lại một ô lẻ, tính song song, hoặc đổi thứ tự ô. Với một `Generator` chung, kết quả phụ thuộc **thứ tự tính** — tức là vẫn không tất định, chỉ khó phát hiện hơn. Seed theo khóa làm mỗi ô độc lập và tái lập được dù tính lẻ, tính lại, hay tính song song.
- **Lưu `seed`, `b`, `method`, `ci_level` trên từng hàng `stat_percentile`** để con số **tự khai báo** cách nó được tính. Đây là điều kiện để FR-37 có kiểm thử thật và SM-13 có số tái lập được.
- **Đưa vào AD-10:** `B`, công thức dẫn xuất seed, và — cùng dịp — những tham số khác hiện đang nằm ngoài AD-10 dù đúng tiêu chí của chính nó: ngưỡng mẫu 30, `window_days` 60, trọng số 3/2/1 của FR-28, ngưỡng 0,05 của FR-38, estimator phân vị, thứ tự ưu tiên nguồn khi hợp nhất cụm (§3.5).
- **Làm rõ Câu hỏi mở số 3 của spine.** Spine viết: *"Nếu chậm, AD-5 vẫn đứng: giảm B, hoặc chỉ tính CI cho những ô thật sự được xem."* Nhánh thứ hai **phải** hiểu là *"một danh sách ô được chọn trước, tính trong lượt chạy hằng đêm"*. Nếu hiểu là *"tính khi có người xem"* thì **trái AD-5** (API chạy phép tổng hợp), **trái AD-4** (CI không thuộc snapshot nào, không truy vết được), và phá luôn ngân sách 15 giây của FR-26 (bootstrap B=1.000 trên một ô, trong một request, cộng với một lượt gọi LLM). Câu này cần viết rõ, vì nó đang là một lối thoát trông hợp lệ dẫn thẳng vào vi phạm hai AD.
- **Giảm `B` là cách tối ưu an toàn; "tính lúc chạy" thì không.** Nếu Sprint 2 đo thấy chậm: B = 200 vẫn cho CI dùng được ở mức hiển thị (biên sai số của chính biên sai số đủ nhỏ ở độ phân giải "52–74%"), và nó giữ nguyên mọi invariant. Nên ghi nhánh này là nhánh ưu tiên.

### 5.4 (high) Một thứ liên quan chưa ai nhận: định nghĩa phân vị và giá trị trùng

Cùng chủ đề "phân vị tính thế nào", có một lỗ hổng nữa, và nó sinh số sai ngay trong v1 chứ không phải lúc tính lại.

**Chưa ai chốt estimator phân vị, và chưa ai chốt luật xử lý giá trị trùng.** `numpy.percentile` có 9 phương pháp nội suy; `linear`, `nearest`, `lower` cho mốc khác nhau ở n nhỏ — mà toàn bộ bài toán của sản phẩm này là n nhỏ. Spine đặt "phân vị" trong `domain/` ở cây mã nguồn (tốt) nhưng **không AD nào chốt phép tính**, trong khi đã bỏ công chốt những thứ ít rủi ro hơn nhiều (thứ tự 4 tầng của FR-22, thứ tự quay về của AD-6).

Thêm nữa, **AD-5 gộp hai phép khác nhau thành một**: "đặt một giá trị vào mốc phân vị đã tính sẵn" có thể là
- **so với mốc**: `skills_count >= p90_value` — đúng như D1 và D3 viết; cần **một mốc**;
- **tính thứ hạng của giá trị**: "tin này nằm ở phân vị 65%" — đúng như FR-30 hiển thị; cần **phân phối tích lũy**, không chỉ một mốc.

Hai phép cần hai thứ khác nhau trong bảng, và spine không phân biệt. Nếu `stat_percentile` chỉ lưu vài mốc rời rạc thì FR-30 không tính được thứ hạng; nếu nội suy thứ hạng từ vài mốc thì con số "65%" là một phép nội suy không ai đặc tả.

**Và chỗ sinh số sai rõ nhất: "số kỹ năng yêu cầu" là một số nguyên nhỏ, phân phối rất nhiều giá trị trùng.** Trên một ô n = 30 với số kỹ năng tập trung ở 5–9, hoàn toàn có thể **P75 = P90 = 9**. Khi đó:
- **D1 ("≥ P90") và D3 ("≥ P75") kích hoạt cùng lúc hoặc không bao giờ** — phá ý nghĩa thiết kế của hai dấu hiệu khác nhau, và làm kết quả kiểm chứng của FR-31 ("mỗi quy tắc có một tin mẫu kích hoạt và một tin mẫu không kích hoạt") trở thành may rủi theo dữ liệu đêm đó;
- `>=` trên một mốc trùng giá trị khiến **mọi tin có 9 kỹ năng** bị gắn D1 — có thể là 20–30% số tin cùng ô, đụng trực tiếp **SM-C3**.

**Đề xuất:** một AD (hoặc mở rộng AD-6) chốt: estimator duy nhất (ví dụ `method='linear'`), luật `>=` trên mốc, và trả kèm `ties_at_marker` để giao diện nói được "cùng mức với X% số tin cùng ô" thay vì ngụ ý "cao hơn 90%". Lưu `method` trên mỗi hàng `stat_percentile`. Và cân nhắc một nhận xét sản phẩm: với thước đo nguyên như "số kỹ năng", gợi ý hiển thị của D1 (*"cao hơn 90% số tin cùng vai trò và cấp bậc"*) **nói quá** khi có nhiều giá trị trùng — câu đúng là "nằm trong nhóm X% tin liệt kê nhiều kỹ năng nhất".

---

## 6. Câu 7 — D1/D2/D3 và mức khớp FR-28: ngoại lệ của AD-5 có đủ không?

Ngoại lệ của AD-5, nguyên văn: *"Ngoại lệ duy nhất được phép tính lúc chạy: đặt một giá trị của tin người dùng dán vào các mốc phân vị **đã tính sẵn**."*

### 6.1 Rà từng dấu hiệu

| Dấu hiệu | Cần gì lúc chạy | Ngoại lệ AD-5 phủ? |
|---|---|---|
| **D1** — số kỹ năng ≥ P90 | đếm kỹ năng của tin dán, so với **một** mốc đã tính sẵn | **Có** — đúng hình dạng của ngoại lệ (nhưng xem §5.4 về giá trị trùng) |
| **D2** — > 50% kỹ năng thuộc nhóm riêng của công ty | **tra nhóm kỹ năng cho từng kỹ năng** trong `stat_skill_rate`, rồi đếm tỷ lệ trên tập kỹ năng của tin | **Không** — đây là N phép tra cứu + một phép đếm, không phải "đặt một giá trị vào mốc phân vị" |
| **D3** — số kỹ năng ≥ P75 **và** lương trần ≤ P25 | hai phép đặt giá trị vào hai mốc (phủ) **+** cổng `n` có lương ≥ 30 **+** quy đổi USD→VND cho tin dán | **Không đủ** — xem §6.3 |
| **D4** — tin đăng lại ≥ 2 lần | vòng đời tin của cụm khớp (FR-32) | **Không**, và vốn không truy vết được (§2) |
| **D5/D6/D7** | chỉ văn bản tin dán | không cần dữ liệu thị trường, ngoài phạm vi AD-5 |
| **FR-28** — mức khớp | **tra nhóm kỹ năng cho từng kỹ năng** của JD để lấy trọng số 3/2/1, rồi tính tỷ số | **Không** — cùng dạng như D2 |
| **FR-46** — chất lượng JD | văn bản tin dán **+ phân loại vai trò/cấp bậc** để kiểm tính nhất quán | **Không** — cần bộ máy phân loại lúc chạy, §6.4 |

**Dấu hiệu vi phạm phát biểu AD-5: D2, D3, D4, FR-28, FR-46.** Nhưng phải phân biệt hai loại vi phạm khác nhau về bản chất.

### 6.2 Loại 1 — AD-5 phát biểu quá hẹp (lỗi của AD, không phải của FR)

D2 và FR-28 không làm gì nguy hiểm: chúng **tra cứu** những giá trị đã tính sẵn (`rate`, `skill_group`) **theo khóa**, rồi làm số học **trên các phần tử của chính tin người dùng dán**. Đó chính là tinh thần của AD-5 ("không tính con số thị trường tại chỗ"). Nhưng chữ trong Rule chỉ cho phép **một** hình dạng.

Chỗ nguy hiểm không phải việc vi phạm — mà là **cách người ta thoát ra khỏi sự bối rối**: một người đọc AD-5 nghiêm túc, thấy FR-28 không khớp ngoại lệ, sẽ viết `SELECT skill_id, COUNT(*) ... GROUP BY skill_id` trong `haido_api` và tự thuyết phục rằng đó là "tra cứu". Lúc đó Soi tin và Insights **thật sự** có hai bộ số cho cùng một thứ — đúng điều AD-5 ra đời để chặn.

**Đề xuất viết lại ngoại lệ, mở ra đúng mức và khóa lại đúng mức:**

> Ngoại lệ được phép tính lúc chạy, và chỉ ba phép này:
> 1. đặt một giá trị của tin dán vào một mốc phân vị đã tính sẵn, đọc theo khóa `(snapshot_id, stat_cell_id, measure, p)`;
> 2. tra `rate` và `skill_group` của **từng** mã kỹ năng theo khóa `(snapshot_id, stat_cell_id, skill_id)` — đọc theo khóa chính, **không `GROUP BY`**, không `ORDER BY … LIMIT` trên bảng tin;
> 3. số học trên **các phần tử của chính tin người dùng dán** (đếm, giao tập, tổng trọng số).
>
> Cả ba phép nằm trong `haido_core/domain/` dưới dạng hàm thuần nhận dữ liệu **đã đọc**; `haido_api` chỉ đọc theo khóa rồi gọi hàm. Trong `haido_api` không có `GROUP BY`, không `percentile_cont`, không `AVG` trên bảng tin.

### 6.3 Loại 2 — vi phạm thật, cần thêm dữ liệu hoặc thêm invariant

**(a) (high) Hàng thiếu trong `stat_skill_rate` — một đường ra số sai, rất dễ xảy ra.**

Một kỹ năng trong JD có mã trong bộ từ vựng nhưng **chưa từng xuất hiện** trong ô thống kê đang dùng (công nghệ niche, hoặc ô đã quay về nhưng vẫn mỏng). `stat_skill_rate` gần như chắc chắn sẽ được cài **thưa** — lưu đầy đủ là |ô| × |bộ từ vựng| hàng. Khi đó phép tra cứu trả về **không có hàng**, và người lập trình có hai lựa chọn tự nhiên:

- **bỏ kỹ năng đó khỏi mẫu số** ⇒ **mức khớp bị thổi phồng**. §3 nói rõ mẫu số là "tổng trọng số **mọi** kỹ năng đã nhận diện trong JD". Một tin 8 kỹ năng, 2 trong số đó không có hàng ⇒ tính 16/16 = **100%** thay vì 16/18 = 89%. Kiểm thử của FR-28 dùng đúng ví dụ 16/18 nên sẽ bắt được *trường hợp đó*, **không** bắt được trường hợp hàng thiếu — nên lỗi này sống qua CI.
- **coi là `rate = 0` ⇒ nhóm "riêng của công ty" ⇒ trọng số 1** ⇒ đúng theo §3.

Spine không nói cái nào. **Cần một dòng trong AD-5 hoặc Consistency Conventions:** *"không có hàng trong `stat_skill_rate` nghĩa là `rate = 0`, nhóm *riêng của công ty*, trọng số 1 — không bao giờ nghĩa là bỏ qua."*

Cùng quy tắc đó sửa luôn **kỹ năng nền tảng** (§3 Bảng thuật ngữ): kỹ năng nền tảng có tỷ lệ dưới θ_common, **kể cả 0** (Linux có thể 0% trong ô Java Backend Fresher), nhưng FR-19 và FR-23 vẫn phải hiển thị tỷ lệ của nó. Nếu hàng thiếu nghĩa là "không có dữ liệu", nút Linux trên đồ thị lộ trình sẽ không có tỷ lệ để in.

**(b) (high) Quy đổi lương của tin dán trong D3 — hai hệ quy chiếu tiền tệ.**

D3 so "lương trần" của tin dán với P25 của ô. Tin dán có thể ghi USD. FR-8 nói USD đổi theo một tỷ giá cố định, cấu hình được; AD-10 đặt tỷ giá vào bảng cấu hình có phiên bản và nói "mỗi snapshot lưu lại `config_version` đã dùng". Nhưng **không AD nào nói đường tính lúc chạy phải dùng `config_version` của snapshot đang đọc** thay vì bản cấu hình hiện hành.

Nếu tỷ giá được cập nhật — và câu hỏi mở số 4 của PRD hỏi đúng *"bao lâu cập nhật một lần"*, nên việc cập nhật là dự kiến chứ không phải giả thuyết — thì lương của tin dán quy đổi bằng tỷ giá **hôm nay**, trong khi P25/P75 của ô quy đổi bằng tỷ giá **của đêm snapshot**. **So hai số ở hai hệ quy chiếu tiền tệ khác nhau.** Tỷ giá USD/VND biến động vài phần trăm là đủ để lật một so sánh sát ngưỡng, và D3 sẽ kích hoạt lệch **một phía** (có hệ thống, không phải nhiễu) — đụng SM-C3.

**Đề xuất quy tắc:** *mọi phép tính lúc chạy đọc tham số từ `config_version` của snapshot đang dùng, không bao giờ từ bản cấu hình hiện hành.* Áp cho tỷ giá USD (D3, FR-8), θ (FR-28, D2), ngưỡng D1–D7, và `window_days`. Đây là một dòng trong AD-10, và nó cũng là lý do nữa để có "ghim snapshot theo request" (§7.1).

**(c) D3 còn bị chặn bởi cổng `n` theo thước đo** — cùng gốc với lỗ hổng số 1 đã nhận, nhận xét ở §1.1.

### 6.4 (high) FR-27 và FR-46 cần bộ máy phân loại lúc chạy — thiếu một AD song song với AD-2

AD-2 làm **rất đúng** cho kỹ năng: phép *"văn bản → mã kỹ năng → nhóm kỹ năng theo ô thống kê"* chỉ tồn tại trong `domain`. Nhưng Soi tin cần **hai bộ máy nữa** lúc chạy, và cả hai hiện chỉ sống ở `steps/`:

- **Phân loại vai trò/nhánh/cấp bậc.** FR-27: *"hệ thống tự nhận diện vai trò (và nhánh, nếu có) cùng cấp bậc của tin"*. FR-46: kiểm tính nhất quán chức danh / kỹ năng / cấp bậc (*"tin tuyển 'Fresher' nhưng đòi từ 5 năm kinh nghiệm"*). Trong spine, `classify` là một **bước pipeline**. Bước pipeline thường viết theo lô: nhận DataFrame, đọc DB, trả về cột mới — hình dạng đó **không gọi lại được cho một tin đơn trong một request**, nên đường Soi tin sẽ cài một bản riêng. Hậu quả: **ô thống kê mà Soi tin chọn lệch với ô mà chính tin đó được xếp vào trong dữ liệu đêm.** Tin được bộ phân loại đêm xếp "Mid" nhưng bộ phân loại lúc chạy xếp "Fresher" ⇒ mức khớp, phân vị, D1, D3 **đều tính trên một ô mà tin đó không thuộc về**. Người dùng dán lại một tin đã có trong dữ liệu và nhận hai câu trả lời khác nhau cho cùng một tin, cùng một snapshot — vi phạm NFR tất định mà không một kiểm thử nào trong danh sách hiện tại bắt được.
- **Ghép trùng.** FR-32 nói rõ: *"dùng **cùng cách so khớp** như FR-4"*. `dedupe` cũng là một bước pipeline. Hai bản cài đặt ⇒ FR-4 và FR-32 không khớp ⇒ **D4 kích hoạt bất nhất**, và kết quả kiểm chứng của FR-32 (*"dán lại nguyên văn một tin đã có trong dữ liệu thì tìm được đúng tin đó"*) chỉ đúng cho trường hợp nguyên văn, không đúng cho trường hợp thật.

**Đề xuất: mở rộng AD-2 từ "một bộ máy kỹ năng duy nhất" thành "một bộ máy miền duy nhất cho bốn phép":**

1. văn bản → mã kỹ năng → nhóm kỹ năng theo ô;
2. văn bản → vai trò / nhánh / cấp bậc / thành phố;
3. hai tin → có trùng không (khóa so khớp + ngưỡng tương đồng);
4. giá trị → phân vị / nhóm phân vị (kèm estimator của §5.4).

Cả bốn là **hàm thuần trong `domain`**, nhận dữ liệu **đã đọc**, không I/O. `steps/` gọi chúng theo lô; `haido_api` gọi chúng cho một tin. AD-15 đã chuẩn bị sẵn nền cho việc này (*"mỗi bước pipeline là một hàm trong `haido_core/steps/`"*) — chỉ cần **đẩy phần quyết định của mỗi bước xuống `domain`** và để `steps/` còn lại I/O + vòng lặp. Chi phí gần bằng không nếu làm từ đầu; rất đắt nếu làm sau Sprint 4.

---

## 7. Phát hiện còn lại

### 7.1 (medium) Không có quy tắc ghim snapshot theo request

AD-4 nói *"Tầng đọc luôn chọn snapshot `published` mới nhất"* — đó là một quy tắc **theo từng câu truy vấn**, không phải **ghim theo request**. Với ngân sách 15 giây của FR-12/FR-26 và việc công bố diễn ra hằng đêm, một request có thể trích kỹ năng ở snapshot N rồi tra nhóm kỹ năng và mốc phân vị ở snapshot N+1 ⇒ một mức khớp **không thuộc snapshot nào**. FR-27 làm chuyện này thường xuyên hơn: *"đổi vai trò hoặc cấp bậc, kết quả được tính lại mà không phải dán lại tin"* — một màn hình sống nhiều phút, mỗi lần tính lại là một lần chọn lại "snapshot mới nhất".

**Đề xuất: AD mới.** Tầng đọc giải `snapshot_id` **đúng một lần ở biên request**, rồi truyền xuống mọi phép tra cứu. Mọi hàm `domain` nhận `snapshot_id` là **tham số bắt buộc**; không hàm nào tự đi hỏi "snapshot mới nhất". Kiểm thử hợp đồng: một response không bao giờ chứa hai `snapshot_id`. (Và với FR-27, phiên Soi tin nên giữ nguyên `snapshot_id` của lần dán đầu cho tới khi người dùng tải lại trang — nếu không, đổi cấp bậc lúc 00:05 sẽ đổi luôn cả bộ số nền.)

### 7.2 (medium) Không có đường đọc snapshot cũ — truy vết chỉ là một nhãn

AD-4 nói tầng đọc *luôn* lấy snapshot published mới nhất. Không có route nào, tham số nào, khóa nào cho phép hỏi "con số này ở snapshot 26/10 là bao nhiêu". Nghĩa là tính truy vết hiện chỉ tồn tại ở dạng **nhãn in trên màn hình**, không ở dạng **tính chất kiểm chứng lại được**. Đủ cho §5 (người đọc thấy ngày), **không** đủ cho:
- **kiểm thử FR-37** (*"so khớp con số hiển thị với một câu truy vấn kiểm tra độc lập trên cùng snapshot"*);
- **SM-13** (thí nghiệm làm thưa mẫu cần đọc lại một ô thống kê cũ);
- **§6.5 bài toán khó số 3**.

**Đề xuất:** cho `?snapshot=YYYY-MM-DD` tồn tại ở mức tối thiểu, dùng cho kiểm thử và SM-13, kèm ràng buộc của §7.6 (danh sách chặn). Hoặc, nếu không muốn mở ra API công khai: một lệnh CLI trong `steps/` đọc lại bảng tổng hợp của một snapshot cũ — rẻ hơn, và đủ cho cả ba mục đích trên.

### 7.3 (medium-high) Làm tròn ở đâu

Hai mâu thuẫn nhỏ nhưng **lật được kết quả**:

- Consistency Conventions: *"Tỷ lệ lưu dạng số thực 0–1. Làm tròn **chỉ** ở tầng hiển thị, không bao giờ làm tròn hai lần."* Addendum FR-28: `mức khớp = round(Σw_có ÷ Σw_JD × 100)`. Phép `round` này **là một phần của kết quả kiểm chứng được** (16/18 → 89%; 15/18 → 83%), nên nó thuộc **miền**, không thuộc tầng hiển thị. Hai tài liệu nói khác nhau. Cần nói rõ: mức khớp là **một số nguyên phần trăm do `domain` tính**, trả kèm giá trị thô; `web/` **không làm tròn lại**.
- FR-38: *"Thẻ so sánh chỉ hiển thị khi chênh lệch đạt ít nhất 5 điểm phần trăm."* So trên tỷ lệ thô hay tỷ lệ đã làm tròn? Hai tỷ lệ 0,174 và 0,225 chênh **5,1 điểm** (đạt) nhưng hiển thị 17% và 23% tức **6 điểm**; còn 0,176 và 0,224 chênh **4,8 điểm** (không đạt) mà hiển thị 18% và 22% tức **4 điểm**. Nếu gác bằng số thô và in bằng số làm tròn thì sẽ có thẻ in ra "chênh 4 điểm" (trông như vi phạm chính ngưỡng của nó) và có thẻ không hiện dù số in ra chênh 6 điểm.

**Đề xuất:** gác bằng **giá trị thô** (hiệu tuyệt đối ≥ `0.05` trên thang 0–1), và câu kết luận của FR-39 in **hiệu đã làm tròn từ giá trị thô**, không in hiệu của hai số đã làm tròn. Thêm một dòng vào Consistency Conventions về đơn vị: *"ngưỡng 5 điểm phần trăm = `0.05` trên thang 0–1"* — hiện bảng convention nói tỷ lệ lưu 0–1 trong khi FR-38 nói bằng điểm phần trăm, và không ai nối hai đơn vị lại.

### 7.4 (medium) `ANON_EVENT` không gắn snapshot — SM-1, SM-9, SM-10 trộn mẫu số

SM-1 đếm *"kỹ năng thuộc nhóm cốt lõi **hoặc thường gặp**"* mà người thử bấm "Tôi chưa biết". **Nhóm kỹ năng là hàm của (snapshot, θ, ô thống kê)**, và cả ba đổi trong hai tuần thử nghiệm: snapshot đổi mỗi đêm, ô đổi theo thứ tự quay về khi `n` thay đổi. `ANON_EVENT` theo ERD chỉ nối tới `SKILL`.

Vậy khi phân tích Sprint 7, **không thể biết** một sự kiện "Tôi chưa biết trên `docker`" lúc đó `docker` thuộc nhóm nào, trên ô nào, với `n` bao nhiêu. SM-1, SM-9(b) và SM-10 sẽ phải *giả định* bằng nhóm kỹ năng của snapshot cuối — một phép quy chiếu ngược làm **sai mẫu số của chỉ số chính của đồ án**. FR-9 đóng băng θ trước Sprint 6 (giảm nhẹ) nhưng snapshot vẫn đổi mỗi đêm và ô vẫn đổi theo `n`.

**Đề xuất:** `ANON_EVENT` thêm `snapshot_id`, `config_version`, `cell_key`, `skill_group_at_event`. FR-17 liệt kê **đóng** các trường được phép (*"Sự kiện chỉ chứa mã phiên ẩn danh, loại thao tác, mã kỹ năng và vai trò mục tiêu"*), nên đây là một **yêu cầu đổi PRD** — nhưng là thay đổi **an toàn về quyền riêng tư** (toàn bộ là metadata hệ thống, không có gì của người dùng) và cần thiết để chương Thực nghiệm có số đúng. Nên đưa vào danh sách "phải sửa PRD" cùng với Câu hỏi mở số 1 của spine (trang nội dung công khai chưa có FR).

### 7.5 (medium) Không có thực thể công ty / ngành

FR-4 tầng hai ghép trùng theo *"tên công ty đã chuẩn hóa"*; FR-37 có thẻ *"Ngành và nhà tuyển dụng nổi bật"*; FR-46 và D7 kiểm *"có tên công ty"*. ERD **không có** `COMPANY`, không có `INDUSTRY`.

Hệ quả: khóa ghép trùng không có nơi lưu dạng chuẩn hóa (nên mỗi lần chạy có thể chuẩn hóa khác nếu hàm chuẩn hóa đổi — **một phiên bản nữa không được theo dõi**, cùng loại với §4), và thẻ Insights về nhà tuyển dụng không truy vết được về một danh tính ổn định. Nếu "Techcombank" và "TCB" là hai thực thể ở hai đêm, thẻ "nhà tuyển dụng nổi bật" **nhảy thứ hạng mà không có lý do dữ liệu** — và FR-37 có kết quả kiểm chứng đòi so khớp với một truy vấn độc lập.

**Đề xuất:** `COMPANY (company_id, name_normalized UNIQUE, name_raw_samples, industry_id)` + `INDUSTRY`; chuẩn hóa tên là hàm thuần trong `domain` **có phiên bản** (thêm vào bộ của §4.3 nếu nó ảnh hưởng ghép trùng); `JOB_POSTING` trỏ tới `company_id`.

### 7.6 (medium) SM-C3 không đo được cho D5, D6, D7 — mâu thuẫn FR × SM

FR-5: *"**Ngay khi đọc tin và trước khi lưu**, hệ thống xóa tên, email, số điện thoại và Zalo của người tuyển dụng"*, với kết quả kiểm chứng *"không bản ghi nào trong kho dữ liệu khớp mẫu email hoặc số điện thoại Việt Nam"*.

SM-C3: *"**Theo dõi:** tỷ lệ kích hoạt của từng dấu hiệu **trên dữ liệu đã thu thập**."*

D5 (*"chỉ cho liên hệ qua Zalo, Telegram hoặc email cá nhân"*) là **không thể** đo trên kho dữ liệu: FR-5 đã xóa đúng đầu vào mà D5 cần, trước khi lưu. D6 và D7 nhẹ hơn nhưng cùng loại nếu bước FR-5 cũng cắt các đoạn chứa thông tin liên hệ.

Đây là mâu thuẫn FR × SM mà spine nên nêu, vì nó **quyết định mô hình dữ liệu**: muốn đo được D5 thì phải lưu một **dấu hiệu đã ẩn danh ngay tại lúc xóa** — cờ boolean `contact_channel_class`, `has_personal_email`, `has_zalo_only`, `mentions_upfront_fee`, `has_company_name` — thay vì chỉ ghi nhật ký "loại thông tin" như FR-5 nói. Cờ boolean không phải dữ liệu cá nhân nên không vi phạm §6.2 và không vi phạm Luật 91/2025.

**Đề xuất:** thêm nhóm cờ ẩn danh vào `JOB_POSTING`, sinh tại bước FR-5, và mở rộng AD-11 (hoặc một dòng trong AD mới về ghép trùng) sang phía dữ liệu thu thập: *"bước xóa thông tin cá nhân ghi lại các cờ phân loại ẩn danh cần cho D5–D7 và SM-C3, không bao giờ ghi giá trị"*. Nếu không làm, phải ghi vào Câu hỏi mở: **SM-C3 chỉ đo được cho D1–D4**.

### 7.7 (low) Yêu cầu gỡ tin gặp tính bất biến

FR-47 cam kết xử lý yêu cầu gỡ trong 48 giờ, kết quả kiểm chứng *"tin liên quan biến khỏi số liệu công khai từ snapshot kế tiếp"*. AD-4 nói hàng của snapshot đã công bố không bao giờ bị sửa hay xóa. Hai cái này tương thích **miễn là** không có đường đọc snapshot cũ — mà hiện đúng là không có (§7.2). Nhưng nếu mở `?snapshot=` như §7.2 đề xuất, tin đã gỡ **sống lại** qua đường đó.

**Đề xuất:** `SUPPRESSION (posting_id | company_id, reason, requested_at)` áp **ở tầng đọc và tầng sinh trang**, không áp bằng cách xóa dữ liệu lịch sử. Quy tắc: mọi đường đọc (API, trang công khai, cả `?snapshot=`) lọc theo danh sách chặn **hiện hành**; dữ liệu lịch sử giữ nguyên cho kiểm toán nội bộ. Một dòng vào AD-4 và AD-13.

### 7.8 (medium) "Khác" và "không xác định thành phố" không có ô thống kê

FR-33 có kết quả kiểm chứng: *"Khi chọn một vai trò, tổng tỷ trọng của các cột cộng với phần 'Khác' và phần không xác định thành phố bằng 100%"*. Khóa ô của AD-6 không có chỗ cho hai mục này, nên tổng sẽ không khép — và nếu một bề mặt nào đó bị ẩn vì ngưỡng mẫu (§1.2) thì càng không khép. Cần ô cho `city = '_other'` và `city = '_unknown'`, cộng một kiểm thử bất biến: tổng tỷ trọng theo vai trò = 1 trong giới hạn sai số số thực.

### 7.9 (nit) Tiêu đề AD-12 còn dính `[ADOPTED]`

`### AD-12 — Hai loại cạnh kỹ năng không bao giờ trộn [ADOPTED]` — chuỗi `[ADOPTED]` sót lại từ memlog. Và `JOB_CLUSTER ||--|| JOB` là quan hệ 1–1 thừa: nên gộp hai thực thể, hoặc nếu giữ `JOB` làm "đại diện" thì nó phải mang `snapshot_id` (§3.2).

---

## 8. Danh sách sửa đề xuất, xếp theo thứ tự làm

**Phải sửa trước khi chia epic** (ảnh hưởng mô hình dữ liệu; sửa sau thì tốn migration):

1. **Tách `JOB_POSTING` / `JOB_OBSERVATION` / `STAT_JOB_LIFECYCLE`**, thêm `status ∈ {success, partial, failed}` cho `PIPELINE_RUN` (§2.3). Đây là điều kiện để lỗ hổng số 3 và số 4 đã nhận thực sự được bịt.
2. **Sửa thứ tự dòng dữ liệu thành hai pha ghép trùng**, và chuyển `JOB_SKILL_MENTION` về treo vào `(posting_id, text_hash)` (§3.4, §3.5).
3. **Vật hóa thành viên cụm theo snapshot** (`STAT_CLUSTER_MEMBERSHIP`) + **quy tắc hợp nhất/chọn đại diện tất định** (§3.2, §3.3).
4. **Bỏ `NULL` khỏi khóa ô thống kê**, thêm `cell_shape` + `CHECK`, thêm ô `_other` / `_unknown` (§1.3, §7.8).
5. **`STAT_PERCENTILE` khóa đầy đủ** `(snapshot_id, stat_cell_id, measure, p)` + `n_with_value`, `ci_*`, `b`, `method`, `seed` (§1.1, §5.3).
6. **Thêm `vocab_version`, `cluster_algo_version`, `window_days` vào `SNAPSHOT`**, chép xuống `STAT_*` (§4.3).
7. **Thêm `snapshot_id`, `config_version`, `cell_key`, `skill_group_at_event` vào `ANON_EVENT`** — kèm đề nghị sửa FR-17 (§7.4).
8. **Thêm `COMPANY` / `INDUSTRY`** và nhóm cờ ẩn danh của FR-5 cho D5–D7 (§7.5, §7.6).
9. **`SUPPRESSION`** cho FR-47 (§7.7).

**Phải sửa trong văn bản spine** (không tốn code, tốn đúng một buổi viết):

10. **AD mới — Cụm tin là đơn vị đếm duy nhất** (§3.1).
11. **AD mới — Ghim snapshot theo request**; mọi hàm `domain` nhận `snapshot_id` bắt buộc (§7.1).
12. **AD mới — Ngữ nghĩa của một snapshot** (bộ bốn phiên bản) + quy tắc "chỉ so sánh khi bộ bốn trùng khớp"; **chốt nhánh của AD-3** (§4.3).
13. **Mở rộng AD-2 thành bốn phép miền** (kỹ năng, phân loại, ghép trùng, phân vị) (§6.4).
14. **Viết lại ngoại lệ của AD-5** thành ba phép được phép; sửa khóa đọc phân vị (§6.2).
15. **Mở rộng AD-10** để phủ: `B`, công thức dẫn xuất seed, ngưỡng mẫu 30, `window_days` 60, trọng số 3/2/1 của FR-28, ngưỡng 0,05 của FR-38, estimator phân vị, thứ tự ưu tiên nguồn khi hợp nhất cụm (§5.3).
16. **Chốt estimator phân vị và luật xử lý giá trị trùng**; phân biệt "so với mốc" (D1, D3) với "thứ hạng của giá trị" (FR-30) (§5.4).
17. **Quy tắc "hàng thiếu trong `stat_skill_rate` nghĩa là rate = 0, nhóm riêng của công ty, trọng số 1"** (§6.3a).
18. **Quy tắc "phép tính lúc chạy đọc tham số theo `config_version` của snapshot đang dùng"** — đặc biệt tỷ giá USD cho D3 (§6.3b).
19. **Chốt làm tròn**: mức khớp là số nguyên do `domain` tính; ngưỡng FR-38 gác trên giá trị thô (§7.3).
20. **Làm rõ Câu hỏi mở số 3 của spine**: "ô thật sự được xem" = danh sách chọn trước, tính trong lượt chạy đêm; **không** phải tính lúc chạy. Ưu tiên nhánh "giảm B" (§5.3).
21. **Đường đọc lại snapshot cũ** (CLI là đủ) cho kiểm thử FR-37 và SM-13 (§7.2).
22. Dọn nit: `[ADOPTED]` ở tiêu đề AD-12; gộp `JOB_CLUSTER`/`JOB` (§7.9).

**Thêm vào Câu hỏi mở của spine:**

- Xác nhận với PM rằng cột `low_confidence` của FR-33 là **ngoại lệ có chủ ý** của §5, kèm **danh sách đóng** các bề mặt được dùng ngoại lệ đó (§1.2).
- SM-C3 có đo cho D5–D7 hay chỉ D1–D4 (§7.6).
- Nếu không tách bảng vòng đời: chấp nhận **hạ lời hứa** D4 và cửa sổ 60 ngày bằng một dòng trong AD-4 (§2.3).

---

## 9. Những chỗ spine làm đúng, nên giữ nguyên

Để bảng trên không bị đọc thành "spine này tệ": phần lớn những gì spine *có* nói là đúng, và đúng ở mức khó.

- **AD-2 + AD-3 + AD-9** giải đúng bài toán khó nhất về nhất quán số: tách LLM (phi tất định) khỏi mapping (tất định), rồi khóa mapping vào một chỗ. Suy luận "đổi bí danh không phải gọi lại LLM" là đúng và tiết kiệm thật. Toàn bộ phê bình ở §4 chỉ là **ghi lại phiên bản**, không phải sửa thiết kế. Và §6.4 chỉ xin **mở rộng** AD-2, không xin đổi nó.
- **AD-6** vật hóa ô thống kê thành bảng thật và buộc thứ tự quay về vào một hàm duy nhất, trả về cả nhãn giải thích. Đây là chỗ dễ sai nhất của sản phẩm này và spine đã nhìn thấy nó.
- **AD-4** đúng về nguyên tắc: snapshot là đơn vị công bố, một transaction, bất biến. Vấn đề không phải AD-4 sai, mà là **ba loại dữ liệu xuyên snapshot** (vòng đời tin, thành viên cụm, danh sách chờ) chưa được cho một chỗ ở hợp pháp bên cạnh nó (§2.4).
- **AD-7 + AD-12** chặn đúng hai cách phá tính tất định của lộ trình học, và lý do nêu ra ("cài lại quy tắc 4 tầng bằng TypeScript để đạt 1 giây") là một dự đoán rất sát thực tế.
- **AD-8** (LLM không sinh số) kèm kiểm thử regex là một invariant hiếm khi được viết ra mà lại **kiểm được bằng máy**.
- **AD-11** chặn rò rỉ CV/JD ở mức *"endpoint không có lệnh ghi nào"* — mạnh hơn "nhớ đừng log", và kiểm được.
- **AD-15** (bước pipeline không import Dagster) là thứ làm cho đề xuất "đẩy phần quyết định xuống `domain`" (§6.4) gần như **miễn phí**.
- **AD-17** sai ở phát biểu ngưỡng, nhưng ý tưởng gốc — *envelope bắt buộc, thiếu `meta` là lỗi schema, có kiểm thử hợp đồng* — là đúng và là nền để sửa; cách bịt đã nhận giữ nguyên toàn bộ ý đó.

Nói gọn: spine có **cấu trúc đúng** và **danh sách invariant chưa đủ**. Chín phát hiện sửa bằng cách thêm bảng; mười ba phát hiện còn lại sửa bằng cách viết thêm chữ. **Không phát hiện nào đòi đổi paradigm, đổi stack, hay đổi ranh giới package.**
