# Research: Khóa hồ sơ trình duyệt và danh sách kỹ năng mồi

## Quyết định

- Một khóa hồ sơ `haido:profile` chứa JSON có trường `v`, cộng `haido:session` và `haido:eval`.
- Mọi lời gọi bộ nhớ bọc try/catch và trả giá trị mặc định khi bị chặn.
- Mã kỹ năng snake_case ASCII.
- Danh sách mồi lấy từ tag kỹ năng của bộ tin nền, một nguồn trong `haido_core`, phát qua API.

## Cách các repo công khai làm

- [pmndrs/zustand, `src/middleware/persist.ts`](https://github.com/pmndrs/zustand/blob/9fed2eb2f3af672da9f7bf694b996df3831fc207/src/middleware/persist.ts): middleware `persist` lưu cả state dưới **một** khóa `name`, kèm `version`. Phiên bản lệch thì không dùng bản lưu, trừ khi có `migrate`. Hải Đồ lấy cách một khóa cộng `v`; chưa có `migrate` vì mới có phiên bản 1, nên sai phiên bản thì đọc ra rỗng.
- [astoilkov/use-local-storage-state, `src/useLocalStorageState.ts`](https://github.com/astoilkov/use-local-storage-state/blob/799291ab6152fbdca80823bf6b12e87257d98638/src/useLocalStorageState.ts): bọc mọi lời gọi `localStorage` trong try/catch vì Safari tắt cookie thì truy cập `localStorage` là ném lỗi, và giữ một `Map` trong bộ nhớ làm chỗ dự phòng. Hải Đồ lấy phần try/catch ngay ở đây. Phần giữ trong bộ nhớ cho phiên hiện tại để cho #210, vì #210 còn phải báo cho người dùng biết.
- Cả hai thư viện để người dùng tự đặt tên khóa. AD-23 cấm việc đó, nên Hải Đồ khai danh sách đóng `HAIDO_KEYS` và xóa theo tiền tố.

## Vì sao không dùng thư viện

Hải Đồ chỉ cần ba khóa và một hàm xóa theo tiền tố. Thêm zustand hay hook để đổi lấy việc đó thì kéo theo một gói và một mô hình state mới cho cả web. Cổng AD-23 cũng chỉ cho tên file `storage` hoặc `haido-keys` gọi `localStorage`, nên một module nhỏ của chính repo là đủ.

## Danh sách kỹ năng mồi

- Nguồn: trường `skills` của 3.469 tin nền (`scraper/data/step-07-jev-extracted.jsonl`, lượt crawl đầu tháng 11/2026). Có 1.582 tag khác nhau sau khi chuẩn hóa chữ thường.
- Chọn khoảng 100 kỹ năng hay gặp nhất mà là kỹ năng thật. Bỏ tag là tên vai trò hoặc quá rộng: `tester`, `it support`, `công nghệ thông tin`, `fullstack`, `data engineer`, `ai`, `cloud`, `api`, `database`.
- Gộp các cách viết của cùng một kỹ năng vào bí danh, ví dụ `reactjs` và `react.js` vào `react`, tag `golang` và tên Go vào mã `golang`, `ci/cd methodologies` vào `ci_cd`, `it security` và `bảo mật thông tin` vào `cybersecurity`.
- Tên tiếng Anh theo cách viết phổ biến của công nghệ, đối chiếu với danh sách công nghệ của Stack Overflow Developer Survey. Tên tiếng Việt dùng thuật ngữ thông dụng ("Học máy", "Kiểm thử tự động"). Tên riêng của công cụ giữ nguyên.
- Trường `source` của mỗi kỹ năng ghi số tin nền có gắn kỹ năng đó (đếm theo tin, gộp mọi bí danh).
- Đây là danh sách mồi, chưa qua giảng viên duyệt. Bộ từ vựng v1 có nguồn cho từng mục và biên bản duyệt là #96.

## Vì sao mã là snake_case

Mã đi thẳng vào `?have=a,b,c` của link chia sẻ (FR-15) và của AD-22. Chữ thường, số và gạch dưới không cần mã hóa URL và không chứa dấu phẩy. Mã vai trò trong `config/rules.toml` cũng là snake_case, nên một quy ước dùng cho cả hai. Ký hiệu như C++, C#, .NET đổi thành `cpp`, `csharp`, `dotnet`; tên hiển thị giữ ký hiệu.
