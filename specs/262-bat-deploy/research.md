# Research: Deploy lên VPS

## Quyết định

Migration chạy xong rồi mới `up` API và web. File `compose.prod.yml` được chép mỗi lần deploy. Project Compose của production là `haido-prod`, khác project của scraper, nên `--remove-orphans` không xóa container scraper.

## Cách các repo công khai làm

- [entire-vc/evc-team-relay, deploy.yml](https://github.com/entire-vc/evc-team-relay/blob/3cacea7a341498795fb9bcfc386d56cb4d33be6b/.github/workflows/deploy.yml): cổng migration đóng khi lỗi. `alembic upgrade head` xong và trả mã 0 rồi mới `docker compose up`. Migration hỏng thì container đang chạy giữ nguyên.
- [valerian-drmt/fx-volatility-trading-system, deploy.yml](https://github.com/valerian-drmt/fx-volatility-trading-system/blob/65470d95022e81cc47df686d5a9ce571026a5750/.github/workflows/deploy.yml): `scp` file compose lên máy, `docker login` GHCR, `pull`, rồi `up`. Alembic của repo đó chạy sau `up`. Hải Đồ không lấy thứ tự này: API mới sẽ khởi động trên schema cũ.
- [Tài liệu Compose: project name](https://docs.docker.com/compose/how-tos/project-name/) và [`up --remove-orphans`](https://docs.docker.com/reference/cli/docker/compose/up/): cờ chỉ xóa container của service không còn trong file Compose của cùng một project. Hai file hai `name` là hai project.

## Vì sao không đổi tên project scraper

Scraper không khai `name`, nên project là tên thư mục trên VPS. Volume dữ liệu crawl đang gắn project đó. Đặt `name` mới sẽ tạo volume trống và cron đêm mất file `seen`.

## Vì sao không nhét Alembic vào lệnh khởi động của API

Image API khởi động bằng uvicorn. Gắn `alembic upgrade head && uvicorn` làm hai process cùng tạo bảng phiên bản khi scale, và một migration hỏng vẫn có thể để container ở trạng thái khởi động lại mãi. Một lệnh `compose run --rm --no-deps` tách biệt, lỗi thì `set -e` dừng trước `up`.
