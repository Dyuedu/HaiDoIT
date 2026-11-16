# Research: Test hồ sơ kỹ năng

## Quyết định

- Test theo hành vi người dùng thấy (vai trò, nhãn, chữ trên màn) bằng Testing Library, không theo state nội bộ.
- Mỗi AC một test có mã FR trong tên, như quy ước `fr37-…`, `test_fr22_…` của repo.

## Cách các repo công khai làm

- [alphagov/accessible-autocomplete @ 86537ef, thư mục `test/`](https://github.com/alphagov/accessible-autocomplete/tree/86537ef85f8fabb4082d0036ad621f75646c254f/test): test chức năng đặt tên theo hành vi người dùng ("shows no results"…), kiểm vùng trạng thái đọc cho trình đọc màn hình. Hải Đồ lấy cách đặt tên theo hành vi và kiểm `role="status"`.
- Trong repo: `specs/148-test-nguoi-moi/` (task test của story #110) đã làm một file test cho các AC của story. #154 theo mẫu đó.

## Không lấy

- Không chạy trình duyệt thật (Playwright) cho test AC: repo chưa có hạ tầng e2e trong CI; kiểm tay Chrome headless ghi ở `specs/152-ho-so-ky-nang/tdd.md`.
