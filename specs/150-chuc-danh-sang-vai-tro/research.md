# Research: Chức danh thành vai trò

## Quyết định

- Không viết luật so khớp mới. Dùng phép 6 (`RuleClassifier`) mà `aggregate` đã dùng để đếm tin, để vai trò của màn trùng vai trò của số liệu.
- Ba trạng thái `matched`, `generic`, `not_it`. Màn dùng hai câu khác nhau cho `generic` và `not_it`, cùng một danh sách vai trò.
- Không khớp thì hiện danh sách vai trò ngay dưới câu báo, không để người dùng tự đoán bước tiếp.

## Cách các repo công khai làm

- [alphagov/accessible-autocomplete @ 86537ef, `src/autocomplete.js`](https://github.com/alphagov/accessible-autocomplete/blob/86537ef85f8fabb4082d0036ad621f75646c254f/src/autocomplete.js): khi không có kết quả, hiện một dòng "No results found" (`tNoResults`, `showNoOptionsFound`) ngay trong danh sách, không im lặng. [`src/status.js`](https://github.com/alphagov/accessible-autocomplete/blob/86537ef85f8fabb4082d0036ad621f75646c254f/src/status.js) đọc số kết quả và câu "No search results" qua vùng `aria-live="polite"`. Hải Đồ lấy hai ý: câu báo không khớp phải hiện thành chữ và được đọc bằng `role="status"`.
- Thư viện đó gợi ý trong lúc gõ. Hải Đồ không lấy cách này cho chức danh: phép 6 cần cả chức danh mới phân loại được, và gọi API mỗi phím gõ là thừa. Ô chức danh là một form có nút "Tìm vai trò".

## Không lấy

- Không trả "độ tin cậy" hay nhiều vai trò ứng viên: phép 6 tất định và trả đúng một nhãn. Muốn vai trò khác thì người dùng chọn trong ô Vai trò (AC 2).
