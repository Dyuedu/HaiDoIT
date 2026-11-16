# Research: TopCV chạy trong lượt đêm trên VPS

## Quyết định

- Chrome có giao diện (`headless=False`) dưới Xvfb, bọc bằng `xvfb-run` trong `pipeline.py`, chỉ khi Linux không có `DISPLAY`.
- Cờ Chrome cho container: `--no-sandbox`, `--disable-setuid-sandbox`, `--disable-dev-shm-usage`; `shm_size` 1 GB.
- Ghim `nodriver==0.50.99`. Chrome Stable không ghim được, phiên bản in ra trong log build.

## Cách làm tham khảo

- [ultrafunkamsterdam/nodriver, `nodriver/core/config.py` @0233da5](https://github.com/ultrafunkamsterdam/nodriver/blob/0233da5bfbe98dc58341f0863526b6315a97e646/nodriver/core/config.py#L99-L108): nodriver chỉ tự tắt sandbox khi chạy bằng root. Lấy: image chạy bằng user `runner` (uid 10001) nên phải truyền `--no-sandbox` tường minh. Không lấy: chạy container bằng root cho đỡ cờ, vì image cố ý dùng `runner`.
- [puppeteer/puppeteer, `docs/troubleshooting.md` @12348e4](https://github.com/puppeteer/puppeteer/blob/12348e4e06f4b0d5e216be768226afc9903d2be2/docs/troubleshooting.md#L347-L358): chạy Chrome có giao diện trên CI bằng Xvfb; `--no-sandbox` khi không dựng được sandbox. Lấy: Xvfb thay cho headless. Không lấy: dịch vụ Xvfb chạy nền riêng, vì `xvfb-run --auto-servernum` gắn vòng đời màn hình ảo với một lần chạy crawler.
- [SeleniumHQ/docker-selenium, `docker-compose-v3.yml` @17c1247](https://github.com/SeleniumHQ/docker-selenium/blob/17c124730af5f9e705855502fc17c23d396ae4d6/docker-compose-v3.yml#L8): node Chrome đặt `shm_size: 2gb`. Lấy: nâng `/dev/shm` cho Chrome chạy lâu. Không lấy: 2 GB, vì container giới hạn 1500M trên VPS 3,8 GB RAM; đã có `--disable-dev-shm-usage` nên 1 GB đủ.

## Không lấy

- **Proxy WARP để đổi IP của VPS, nạp sẵn cookie `cf_clearance` từ máy khác**: có trong hướng dẫn người dùng dán trước đó, không nằm trong #302. Nếu chép profile từ máy local lên volume thì đó là việc tay của người dùng, không có trong code.
- **Fallback nạp URL cũ từ `job_queue` vào file seen**: bỏ, vì làm `job_observations` ghi tin cũ là còn đăng.
