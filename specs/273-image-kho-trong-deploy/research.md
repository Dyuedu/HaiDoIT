# Research: Build image kho trong workflow deploy

## Quyết định

- Build image kho trên GitHub Actions trong cùng matrix với API và web, đẩy lên GHCR với tag `sha-<commit>`.
- Máy chủ kéo image lúc deploy, khi còn token. Cron chỉ chạy image đã có trên máy (`pull_policy: never`).
- Tag của bản đã deploy nằm trong file `.warehouse-tag`. Chỉ ghi file này khi bản deploy đã khỏe.

## Cách làm tham khảo

- [docker/build-push-action, README](https://github.com/docker/build-push-action/blob/562e51947939164e4fe808a6eab5101977e509e0/README.md): action build một Dockerfile mỗi lần gọi. Nhiều image thì gọi nhiều lần hoặc dùng matrix. Workflow của Hải Đồ đã dùng matrix `app`/`dockerfile` cho API và web, nên chỉ thêm một dòng. Lấy thêm từ tài liệu cache gha của action: mỗi image một `scope`, nếu không thì ba job song song ghi đè cache của nhau.
- [compose-spec, `05-services.md`](https://github.com/compose-spec/compose-spec/blob/3a4a6995e4a971f6173dff9130cb3e38e6738651/05-services.md) và [tài liệu Docker về `pull_policy`](https://docs.docker.com/reference/compose-file/services/#pull_policy): `never` thì Compose không bao giờ kéo image, thiếu image thì lỗi. Hải Đồ dùng `never` vì cron không có token GHCR, và thà bước kho báo lỗi rõ còn hơn lặng lẽ build hay kéo một bản khác.
- [Tài liệu Docker về nội suy biến](https://docs.docker.com/reference/compose-file/interpolation/): `${VAR:?}` làm lỗi cả file khi thiếu biến, kể cả khi chạy service khác. Hải Đồ dùng `${HAIDO_WAREHOUSE_TAG:-none}` để lệnh chạy `scraper` không phụ thuộc biến của kho.

## Không lấy

- **Tag `main` hoặc `latest` cho cron.** Workflow đã gắn tag `main`, nhưng cron kéo `main` thì cần token trên VPS, và có thể chạy image của một commit mà bản deploy (API, web) đã thất bại. File tag chỉ đổi khi deploy khỏe.
- **Ghi tag vào `.env`.** `.env` chứa secret, do người quản trị viết, script deploy không sửa nó.
- **Đưa kho vào `compose.prod.yml` với `profiles`.** Kho phải chạy trong project scraper vì dùng chung `.env` và lịch đêm; đưa sang project khác phải đổi `daily.sh` nhiều hơn mà không được gì thêm.
