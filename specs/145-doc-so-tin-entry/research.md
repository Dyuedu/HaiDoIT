# Research: Đọc số tin entry-level từ ô đã tổng hợp

## Quyết định

Đọc thẳng ô đã tổng hợp (`stat_cells`, `scope = vn`, `seniority = entry`) thay vì đếm lại ở API.

## Cách repo công khai làm

- [plausible/analytics, `lib/plausible/stats/table_decider.ex`](https://github.com/plausible/analytics/blob/03a4f7293350b017b19a310c054b9ef8bcc1e9ec/lib/plausible/stats/table_decider.ex): khi trả một truy vấn, module quyết đọc bảng nào sao cho ít truy vấn và ít JOIN nhất, và chọn bảng `sessions` (đã gom theo phiên) khi mọi chiều và chỉ số đều có ở đó, thay vì đếm lại trên bảng `events`. Lấy: số trên màn hình đọc từ bảng đã gom sẵn có đúng chiều cần, không đếm lại khi đọc. Không lấy: bộ quyết định động. Ở đây chỉ có một bảng đọc (`stat_cells`) và AD-7 cấm hẳn đường đọc bảng tin, nên không cần chọn bảng.

## Vì sao không cộng `seniority_mix` của ô `all`

Ô `all` có `seniority_mix` đủ để cộng Intern + Fresher + Junior. Nhưng `aggregate` đã ghi ô `entry` với đúng tổng đó và cùng nhóm cấp của `config/rules.toml` (#134). Đọc ô `entry` thì số trên màn người mới trùng số trên bản đồ khi chọn "Mới vào nghề", và đổi nhóm cấp chỉ cần sửa config, không sửa API.
