# Research: Tìm kỹ năng song ngữ

## Quyết định

- Bỏ dấu bằng `normalize("NFD")` rồi bỏ dấu kết hợp, thêm `đ` → `d`, chữ thường, gộp khoảng trắng: đúng luật `fold` của `haido_core/domain/posting_text.py`, để "hoc may" ở web khớp cùng cách API khớp lượt nhắc trong tin.
- So khớp chuỗi con trên tên Anh, tên Việt, bí danh. Khớp đầu tên xếp trước khớp giữa tên; hòa thì theo thứ tự danh sách (thứ tự mã).
- Tối đa 8 kết quả; không có kết quả thì nói thành chữ.

## Cách các repo công khai làm

- [krisk/Fuse @ edf2fb6, `src/helpers/diacritics.ts`](https://github.com/krisk/Fuse/blob/edf2fb608eca0461508d1d71317e6e58309ffada/src/helpers/diacritics.ts): Fuse.js bỏ dấu bằng `normalize('NFD')` rồi xóa các dải dấu kết hợp, và có bảng riêng cho ký tự không tách được bằng NFD, trong đó có `đ` → `d`. Đây đúng là chỗ dễ sót với tiếng Việt: chỉ NFD thì "đ" vẫn còn. Hải Đồ lấy cả hai bước, chỉ giữ dải `\p{M}` và ánh xạ `đ`.
- [alphagov/accessible-autocomplete @ 86537ef, `src/autocomplete.js`](https://github.com/alphagov/accessible-autocomplete/blob/86537ef85f8fabb4082d0036ad621f75646c254f/src/autocomplete.js), [`src/status.js`](https://github.com/alphagov/accessible-autocomplete/blob/86537ef85f8fabb4082d0036ad621f75646c254f/src/status.js): hiện "No results found" thành dòng chữ và đọc số kết quả qua `aria-live`. Hải Đồ lấy câu "Không có kỹ năng nào khớp" trong `role="status"`.

## Không lấy

- Không dùng Fuse.js (tìm mờ theo khoảng cách): danh sách ~225 mục, chuỗi con sau khi bỏ dấu là đủ, và tìm mờ dễ ra kết quả lạ như "java" khớp "javascript" ở thứ hạng khó đoán. Không thêm gói.
- Không làm combobox ARIA của accessible-autocomplete: kết quả là checkbox để tick ngay, không phải chọn một giá trị cho ô nhập.
