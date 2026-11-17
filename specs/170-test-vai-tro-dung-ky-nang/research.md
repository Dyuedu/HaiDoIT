# Research: Test "vai trò nào dùng kỹ năng"

## Quyết định

- Test theo hành vi người dùng thấy (vai trò, nhãn, chữ trên màn) bằng Testing Library; mỗi AC một test có mã FR trong tên.

## Cách các repo công khai làm

- [alphagov/accessible-autocomplete @ 86537ef, thư mục `test/`](https://github.com/alphagov/accessible-autocomplete/tree/86537ef85f8fabb4082d0036ad621f75646c254f/test): test chức năng đặt tên theo hành vi người dùng và kiểm vùng trạng thái cho trình đọc màn hình.
- Trong repo: `specs/154-test-ho-so-ky-nang/` (test theo AC của #111). #170 theo đúng mẫu đó.

## Không lấy

- Không chạy e2e bằng trình duyệt thật trong CI: repo chưa có hạ tầng; kiểm tay Chrome headless ghi ở `specs/169-vai-tro-dung-ky-nang/tdd.md`.
