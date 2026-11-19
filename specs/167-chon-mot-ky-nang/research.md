# Research: Chọn một kỹ năng

## Quyết định

- Dùng lại hàm tìm của #207 (bỏ dấu theo `fold` của API, khớp tên Anh, tên Việt, bí danh).
- Kết quả là nút chọn một có `aria-pressed`, không phải ô tick: #113 hỏi về đúng một kỹ năng.
- Tên kỹ năng đã dùng hiện theo `data.skill` của API, để người dùng thấy máy chủ đã hiểu kỹ năng nào, không phải chuỗi họ gõ.

## Cách các repo công khai làm

- [alphagov/accessible-autocomplete @ 86537ef, `src/autocomplete.js`](https://github.com/alphagov/accessible-autocomplete/blob/86537ef85f8fabb4082d0036ad621f75646c254f/src/autocomplete.js): sau khi chọn, ô nhập hiện đúng giá trị đã chọn, và khi không có kết quả thì hiện dòng "No results found". Lấy ý "hiện rõ giá trị đã chọn" (dòng "Kỹ năng: …") và câu không có kết quả.
- [krisk/Fuse @ edf2fb6, `src/helpers/diacritics.ts`](https://github.com/krisk/Fuse/blob/edf2fb608eca0461508d1d71317e6e58309ffada/src/helpers/diacritics.ts): cách bỏ dấu (NFD + `đ`) mà #207 đã lấy; #167 dùng lại hàm của #207, không viết lại.

## Không lấy

- Không làm combobox ARIA đầy đủ (mũi tên lên xuống trong danh sách): tối đa tám nút, Tab qua từng nút là đủ, và giữ cùng cách với ô tìm của hồ sơ.
