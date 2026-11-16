# Research: Hồ sơ kỹ năng

## Quyết định

- Mỗi dòng có một ô tick riêng (checkbox gốc, nhãn là tên kỹ năng) và một liên kết riêng tới lộ trình (#153). Không gộp "chạm cả dòng để tick" với "chạm để mở lộ trình".
- Giữ số của lần tải trước trên màn trong lúc tải lại sau khi tick, để danh sách không nhảy.
- Thứ tự, cờ `have` và số đếm core lấy từ API (AD-22). Ô tick phản hồi ngay theo hồ sơ trong trình duyệt (hiện và lọc, không đếm).

## Cách các repo công khai làm

- [alphagov/accessible-autocomplete @ 86537ef, `src/status.js`](https://github.com/alphagov/accessible-autocomplete/blob/86537ef85f8fabb4082d0036ad621f75646c254f/src/status.js): trạng thái tải và kết quả đọc qua vùng `aria-live="polite"`. Màn hồ sơ kỹ năng dùng `role="status"` cho "Đang tải số liệu…" như màn người mới (#147).
- Trong repo: màn người mới (#147, `web/app/components/insights/newcomer-screen.tsx`) đã chốt cách gọi API phía trình duyệt, xử lý `unknown_cell` không có "Thử lại" và mạng hỏng có "Thử lại". Màn hồ sơ kỹ năng theo đúng cách đó.
- [kamranahmedse/developer-roadmap (nay `nilbuild/developer-roadmap`) @ 2b53446](https://github.com/nilbuild/developer-roadmap/tree/2b534461da5629c57d8a0a4a7efcb26adc7f179e): roadmap.sh đánh dấu từng mục "done" và hiện "X of Y". Ở commit này repo chỉ còn nội dung, không còn mã ứng dụng để đọc; chỉ lấy ý trình bày "X/Y" cho dòng đếm core.

## Không lấy

- Không vẽ thanh tỷ lệ: con số và nhóm đủ cho AC, và thanh dễ bị đọc như xếp hạng khi ô bị ẩn số.
