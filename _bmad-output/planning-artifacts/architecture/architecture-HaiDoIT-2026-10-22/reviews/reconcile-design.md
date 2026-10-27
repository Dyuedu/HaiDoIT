---
title: Đối chiếu DESIGN với architecture spine
type: architecture-reconcile
source: _bmad-output/planning-artifacts/ux-designs/ux-HaiDoIT-2026-10-22/DESIGN.md
compared: _bmad-output/planning-artifacts/architecture/architecture-HaiDoIT-2026-10-22/ARCHITECTURE-SPINE.md
language: vi
verdict: gaps
---

# Đối chiếu DESIGN.md với architecture spine

Nguồn là `DESIGN.md` (`status: final`, cập nhật 2026-10-22). Spine là `ARCHITECTURE-SPINE.md` (`status: draft`, cập nhật 2026-10-23). Lần này không sửa hai bản đó.

Lỗ chỉ tính khi một ràng buộc nhìn hoặc thao tác trong DESIGN khiến hai người dựng lệch nhau, và spine bỏ sót hoặc nói ngược. Màu, chữ, bản đồ 3D, giảm chuyển động và mốc 720px thuộc DESIGN. Im lặng của spine ở những chỗ đó không phải lỗ, trừ khi spine nói ngược.

## Findings

### 1. Nhãn dự báo đòi một khoảng, spine chỉ cho câu chưa ghi nhận

- **Severity:** high
- **DESIGN:** Elevation & Depth và Components «Bản đồ 3D» — ở mốc dự báo, nhãn gồm tên thành phố, chữ «Dự báo», và một khoảng; cột có khung nét đứt. Components «Tầm nhìn» giữ bốn mốc NAY, +6T, +12T, +18T. Components «Thẻ thành phố» — tab Dự báo là một khoảng có nhãn «Dự báo», hoặc câu chưa ghi nhận tín hiệu. Do's and Don'ts — vẽ dự báo thành một khoảng có chữ «Dự báo». Cùng mục cấm lấy số minh họa của prototype (3.960 tin, lương 26 triệu) làm dữ liệu đang chạy.
- **Spine:** AD-12 buộc dự báo 18 tháng và tín hiệu sớm, trước tuần 1, dùng câu chưa ghi nhận. Cấm hệ số minh họa của prototype. Deferred lặp lại: chưa có công thức thì chỉ có câu đó.
- **Class:** contradiction

Tab thành phố còn cửa «hoặc câu chưa ghi nhận». Nhãn trên bản đồ và câu «Làm» thì không có cửa đó: mốc dự báo phải kèm một khoảng. Người theo DESIGN vẽ số. Người theo AD-12 để câu chưa ghi nhận và không có số. Hai mặt đó không cùng một payload.

### 2. Hướng kỹ năng và các số «tăng» không có quy tắc

- **Severity:** high
- **DESIGN:** Components «Khối xu hướng tám quý» — trên Bản đồ nhu cầu, cột tăng, giảm và đi ngang, có chú giải chữ. Components «Chip kỹ năng» và «Danh nên học tiếp» — kỹ năng đang giảm có tem chữ. Mỗi dòng danh nên học tiếp có số tin tăng, số tuần, và số tin trên mỗi tuần.
- **Spine:** AD-10 chỉ giữ danh kỹ năng và số tuần. AD-2 cấm Next tự tính số tin, lương, dự báo. AD-6 chốt cách gộp lương. AD-12 chỉ buộc dự báo 18 tháng và tín hiệu sớm, và không nói khối tám quý có nằm trong chỗ bị giữ lại hay không. Không có quy tắc tăng, giảm, đi ngang, số tin tăng, hay số tin trên mỗi tuần.
- **Class:** spine-hole

Hai người dựng có thể giấu khối này sau câu chưa ghi nhận, hoặc tự đặt quy tắc quý và tự chia số tin cho số tuần. Cùng một kỹ năng sẽ ra hai hướng.

### 3. Ba thẻ chặng và nhận định bị loại, spine chỉ có ba câu

- **Severity:** high
- **DESIGN:** Components «Thẻ chặng» — ba thẻ Ngày 1–30, 31–60, 61–90. Mỗi thẻ có kỹ năng của chặng, tên một dự án thực hành, và một câu người học làm ra cái gì. Components «Nút Vì sao?» — mỗi nhận định một nút. Do's and Don'ts — Vì sao? trên từng nhận định của lộ trình, kể cả nhận định bị loại. Components «Ngăn Vì sao?» — có câu nguồn.
- **Spine:** AD-7 — FastAPI tính số trước, model viết ba câu từ các số đó, Vì sao? trỏ về số, một lần gọi, không có mạng năm agent. Không nói ai chọn kỹ năng và tên dự án cho từng chặng. Không có nhận định bị loại.
- **Class:** spine-hole

Người làm API có thể trả đúng ba câu. Người làm màn cần kỹ năng, tên dự án, và các nhận định bị loại kèm Vì sao?. Hai payload không lắp vào nhau. Câu «trỏ về số» không ngược với «câu nguồn»; phần rơi là cấu trúc thẻ và nhận định bị loại.

### 4. Soi tin phải hiện số lần làm mới, dòng tin không giữ số đó

- **Severity:** medium
- **DESIGN:** Components «Kết quả soi tin» — thẻ liệt kê số lần làm mới, ngày thấy đầu, ngày thấy gần nhất. Tin trùng và lương bất thường chỉ đổi mặt hộp khi đã có kết luận. Không có vòng điểm trên 100.
- **Spine:** AD-4 — thấy lại thì cập nhật ngày thấy gần nhất và giữ ngày thấy đầu, khóa `source_id`. Dòng giữ kỹ năng, thành phố, cấp bậc, khoảng lương, ngày đăng, link gốc. Không có số lần thấy lại. AD-9 — Soi tin không ghi server và không qua model. Capability map vẫn để Soi tin ở FastAPI đọc, Next vẽ.
- **Class:** spine-hole

Ngày đầu và ngày gần nhất có chỗ để lấy. Số lần làm mới thì mất khi lần thấy sau ghi đè cùng một dòng. Một người thêm bộ đếm, người kia chỉ có hai ngày. Quy tắc «thế nào là tin trùng» và «thế nào là lương bất thường» không có trong DESIGN, nên im lặng của spine ở hai quy tắc đó không tính là lỗ của lần đối chiếu này. Vòng điểm trên 100 là chi tiết mặt nhìn, ghi ở mục 8.

### 5. Chip vai trò không có chỗ trên dòng tin

- **Severity:** medium
- **DESIGN:** Components «Chip vai trò» — bảy nhãn, có trạng thái đang bật: Tất cả, Backend, Frontend, Data/AI, DevOps/Cloud, Mobile, Bảo mật. Components «Viên hồ sơ phiên» — chữ trên viên là thành phố, cấp bậc và vai trò. Components «Nút phụ» — có «Bỏ lọc».
- **Spine:** AD-4 giữ cấp bậc trên dòng tin, không giữ vai trò, không có quy tắc xếp một tin vào Backend, Frontend, Data/AI, DevOps/Cloud, Mobile hay Bảo mật. AD-2 để số tin ở FastAPI.
- **Class:** spine-hole

Bật chip và bỏ lọc là thao tác lọc. Không có vai trò trên tin thì hai người sẽ lọc bằng hai cách phân loại, và số tin theo vai trò lệch nhau. Cấp bậc trong spine không đứng thay cho vai trò: DESIGN kể thành phố, cấp bậc và vai trò là ba mục.

### 6. Học gì tiếp? có ba số trước và sau, spine không gọi tên ba số

- **Severity:** medium
- **DESIGN:** Layout & Spacing — trên máy bàn, Học gì tiếp? chia hai: kịch bản bên trái, ba số trước và sau bên phải.
- **Spine:** Capability map đưa Học gì tiếp? vào FastAPI đọc Supabase, Next vẽ, theo AD-2, AD-4, AD-6, AD-12. Không nói ba số đó là số nào.
- **Class:** spine-hole

Hai người có thể trả hai bộ ba khác nhau (tin, lương, tuần, hay một bộ khác) cho cùng cột «trước và sau».

### 7. Không avatar, không tên người

- **Severity:** low
- **DESIGN:** Components «Viên hồ sơ phiên» — chữ là thành phố, cấp bậc, vai trò; không tên người; không avatar chữ «M». Components «Lớp chào» — không gọi tên người. Do's and Don'ts — không điền sẵn hồ sơ tên Minh.
- **Spine:** AD-8 giữ hồ sơ trên trình duyệt đến lúc lưu, và chặn tài khoản mật khẩu. Spine không mô tả avatar, chữ «M», hay tên người trên màn.
- **Class:** story-detail

Không phải contradiction. Không phải lỗ: mặt viên hồ sơ đã nằm trong DESIGN, spine không đòi một avatar.

### 8. Bản đồ 3D, giảm chuyển động, mốc 720px, màu và chữ

- **Severity:** low
- **DESIGN:** Elevation & Depth và Components «Bản đồ 3D», «Nút thế bản đồ» — dùng khối 3D của prototype; không thay bằng biểu đồ cột phẳng; nút 2D là một thế phẳng trong cụm 3D, xoay, đặt lại. `prefers-reduced-motion` tắt animation và transition, nút 3D vẫn còn. Layout & Spacing — dưới 720px, khối hai cột xếp một cột. Colors, Typography, Do's and Don'ts giữ nền đêm, chữ, nút chanh, nhấn lạnh.
- **Spine:** Không nói bản đồ phẳng, không nói màn hẹp hay giảm chuyển động phải bỏ 3D, không nói màu hay họ chữ.
- **Class:** story-detail

Không phải contradiction. Không phải lỗ.

### 9. Các mặt còn lại DESIGN đã khóa

- **Severity:** low
- **DESIGN:** Shapes — lương ẩn là hộp nét đứt, không vẽ trục P25–P75. Do's and Don'ts — không dùng đỏ để chấm tin đáng tin hay rủi ro cao; không khóa bảng lương sau form số điện thoại; không đưa mạng năm agent, trục phân vị, vòng điểm, chỉ số AI lên màn v1. Components «Toast», «Khối trạng thái», nút cao ít nhất 44px, lớp chào một lần trên mỗi máy.
- **Spine:** Không thêm các mặt đó, cũng không cấm từng món bằng một AD riêng. AD-7 đã cấm mạng năm agent trên màn. AD-6 giữ một kiểu gộp lương.
- **Class:** story-detail

## Đã khớp

Những chỗ sau không phải lỗ và không phải contradiction.

- Nút báo nguồn. DESIGN, Components «Ngăn Vì sao?» và Do's and Don'ts: không có nút «Báo nguồn sai hoặc đã cũ». Spine AD-13: không nút, không thư báo nguồn, không bảng báo nguồn. Ngăn vẫn có câu nguồn; AD-7 để Vì sao? trỏ về số. Hai câu đó đứng cùng nhau được.
- Lương công khai. DESIGN hiện một số khi ô mẫu đủ 30 tin, và câu chưa đủ mẫu khi đã chọn thành phố mà thiếu mẫu; ô đầu trang và tab lương của thành phố đang chọn là cùng một số. Spine AD-6: trung vị điểm giữa, từ 30 tin, dưới ngưỡng thì câu chưa đủ mẫu, không đổi USD sang VND. DESIGN không nói cách gộp; spine điền trung vị, không đổi «một số».
- Offer. DESIGN vẽ thanh thực nhận và hộp hụt, có ô tên công ty trên form. Spine AD-9: trình duyệt tự tính, FastAPI chỉ trả bộ số thuế và BHXH, không có API nhận nội dung offer. Tên công ty trên form không đụng AD-4, vì AD-4 cấm tên công ty trên dòng tin.
- Lộ trình và email. DESIGN đặt ô email dưới ba chặng đã hiện, và có câu «Chưa có lộ trình cho email này.» Spine AD-7 chỉ ghi lộ trình khi email lưu được. AD-8: biết email không trả lộ trình trên màn.
- Số mẫu prototype không thành dữ liệu đang chạy. DESIGN cấm các mức minh họa. AD-12 cấm hệ số minh họa. Xung đột nằm ở mục 1, chỗ DESIGN vẫn đòi một khoảng.

## Kết

Verdict: gaps. Lỗ nặng là khoảng dự báo ngược AD-12, quy tắc hướng kỹ năng bị bỏ, và payload lộ trình chỉ còn ba câu. Số lần làm mới, vai trò trên tin, và tên ba số trước/sau là lỗ vừa. Avatar, nút báo nguồn, và bản đồ 3D so với mặt phẳng không phải lỗ: hai mục đầu đã khớp, mục sau là chi tiết DESIGN giữ.
