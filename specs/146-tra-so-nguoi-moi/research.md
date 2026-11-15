# Research: Trả số người mới kèm cỡ mẫu và ẩn mẫu nhỏ

## Quyết định

- Mọi vai trò của config đều có dòng, kể cả khi snapshot không có hàng của nó; vai trò đó là 0 tin, n = 0, không có tỷ lệ.
- Tỷ lệ dưới ngưỡng không trả giá trị (`null_data`), số đếm vẫn trả.

## Cách repo công khai làm

- [plausible/analytics, `lib/plausible/stats/table_decider.ex`](https://github.com/plausible/analytics/blob/03a4f7293350b017b19a310c054b9ef8bcc1e9ec/lib/plausible/stats/table_decider.ex): số trả về đọc từ bảng đã gom sẵn có đủ chiều cần, không đếm lại khi đọc (xem `specs/145-doc-so-tin-entry/research.md`). Lấy cho #146: API chỉ ghép dòng, tính một phép chia và sắp thứ tự; mọi số đếm đến từ `stat_cells`.

## Vì sao điền 0 cho vai trò vắng thay vì bỏ dòng

AC 1 của #146 đòi mọi vai trò có mặt, và AC 3 của #110 đòi vai trò 0 tin entry-level vẫn ở trong danh sách. Bỏ dòng thì người dùng không phân biệt được "không có tin" với "hệ thống thiếu vai trò này". Snapshot công bố trước #284 không có bảy vai trò mới; chúng hiện 0 tin và "chưa đủ dữ liệu" cho tới lượt chạy đêm sau, đúng với dữ liệu của snapshot đó.

## Vì sao không lấy cách bản giả tính `share`

Bản giả lưu sẵn `share` thô trong JSON. Bản thật tính entry / n từ hai ô, để tỷ lệ luôn khớp hai số đếm trong `meta.cells` mà màn hình hiện bên cạnh.
