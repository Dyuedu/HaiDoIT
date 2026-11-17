# Research: Vai trò nào dùng một kỹ năng

## Quyết định

- Danh sách liên kết theo mẫu summary list của GOV.UK Frontend: trên điện thoại tên và ô số xếp chồng, từ `sm` thành hai cột. Màn người mới (#147) đã dùng mẫu này, nên hai mục của Insights trông như một.
- Câu tỷ lệ là một dòng chữ thường ("77,6% tin AI/ML mới vào nghề nhắc tới Python"), số đứng ở `span` riêng để giữ DEC-6.
- Kỹ năng đã chọn nằm trong URL để chia sẻ được, đọc bằng `useSyncExternalStore` với snapshot server rỗng (cùng cách hồ sơ trình duyệt của #206).

## Cách các repo công khai làm

- [alphagov/govuk-frontend @ 3862ef3, `packages/govuk-frontend/src/govuk/components/summary-list/_mixin.scss`](https://github.com/alphagov/govuk-frontend/blob/3862ef30df6a5da3e03974214cd28ffbfa769867/packages/govuk-frontend/src/govuk/components/summary-list/_mixin.scss): summary list để khóa và giá trị xếp chồng dưới cỡ tablet, từ tablet thành `display: table` / `table-row` / `table-cell`. Lấy cách xếp này cho dòng vai trò (cùng commit #147 đã tham khảo).
- [alphagov/accessible-autocomplete @ 86537ef, `src/status.js`](https://github.com/alphagov/accessible-autocomplete/blob/86537ef85f8fabb4082d0036ad621f75646c254f/src/status.js): kết quả và "không có kết quả" đọc qua vùng `aria-live`. Lấy cho câu "chưa tin nào nhắc" và trạng thái tải.

## Không lấy

- Không vẽ thanh tỷ lệ: con số kèm n đủ cho AC, và thanh dễ đọc như xếp hạng khi nhiều dòng bị ẩn.
