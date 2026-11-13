# Research: Danh sách xếp hạng có số, đọc được trên điện thoại

## Quyết định

Mỗi vai trò là một khối liên kết: tên vai trò một hàng, ô số (tin cho người mới, tỷ lệ, n) một hàng trên điện thoại; từ `sm` thành hai cột. Không dùng bảng bốn cột.

## Cách repo công khai làm

- [alphagov/govuk-frontend, `packages/govuk-frontend/src/govuk/components/summary-list/_mixin.scss`](https://github.com/alphagov/govuk-frontend/blob/3862ef30df6a5da3e03974214cd28ffbfa769867/packages/govuk-frontend/src/govuk/components/summary-list/_mixin.scss): summary list dưới mốc tablet xếp khóa và giá trị chồng nhau, mỗi dòng có viền dưới và khoảng cách; từ tablet trở lên đổi sang `display: table` với các ô `table-cell`. Lấy: chồng trên điện thoại, cột từ màn rộng, để không có cuộn ngang ở 360px. Không lấy: cột "actions" riêng; ở đây cả dòng là một liên kết nên vùng chạm lớn hơn và trình đọc màn hình đọc tên vai trò trước.

## Vì sao không dùng bảng

Bảng bốn cột (vai trò, tin cho người mới, tỷ lệ, n) ở 360px phải cuộn ngang trong khung, như bảng thành phố của Bản đồ. Ở đây mỗi dòng còn phải bấm được; một hàng bảng không phải phần tử tương tác, nên phải đặt liên kết trong ô đầu và vùng chạm chỉ còn tên vai trò. Danh sách có thứ tự (`ol`) giữ được ngữ nghĩa xếp hạng.

## Vì sao câu giới thiệu không có số

DEC-6 (#132): số đứng ở ô riêng kèm n, ngày, nguồn. Mẫu câu cũ trong EXPERIENCE.md ("[vai trò]: [x]% tin nhận Intern hoặc Fresher (n = [n])") bị quyết định này thay.
