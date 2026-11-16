# Research: Mở lộ trình từ kỹ năng

## Quyết định

- Liên kết thường (`<Link>`) chứ không phải nút mở hộp thoại: người dùng mở được ở tab mới và chia sẻ được, đúng tinh thần link chia sẻ FR-15.
- Kỹ năng đã có thì không dẫn sang lộ trình, vì lộ trình cá nhân không chứa kỹ năng đã có (FR-20).

## Cách các repo công khai làm

- [kamranahmedse/developer-roadmap (nay `nilbuild/developer-roadmap`) @ 2b53446, thư mục `roadmaps/`](https://github.com/nilbuild/developer-roadmap/tree/2b534461da5629c57d8a0a4a7efcb26adc7f179e/roadmaps): mỗi mục của roadmap.sh có trang nội dung riêng theo đường dẫn ổn định (roadmap/mục), nên một mục mở được trực tiếp từ nơi khác. Hải Đồ lấy ý "đường dẫn ổn định tới một kỹ năng trong lộ trình": `?skill=` giữ được khi #121 thay trang giữ chỗ.
- Trong repo: trang giữ chỗ `/ho-so-ky-nang` của #147 (gọi tên vai trò, nói "sprint sau", có nút quay lại, mã lạ không in như tên). Trang `/co-van` theo đúng mẫu đó.

## Không lấy

- Không dựng màn lộ trình tối thiểu đọc `GET /api/v1/learning-path`: đó là việc của #213–#219 ở Sprint 4 (người dùng chọn 16/11/2026).
