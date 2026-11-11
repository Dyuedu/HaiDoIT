# Data model: Build image kho trong workflow deploy

Không thêm bảng, không thêm cột, không thêm revision Alembic.

Thêm một file trạng thái trên VPS:

| File | Nội dung | Ai ghi | Ai đọc |
|---|---|---|---|
| `$VPS_PATH/.warehouse-tag` | một dòng `sha-<commit 40 ký tự>` | `vps-deploy.sh`, sau khi cổng sức khỏe qua | `daily.sh`, trước bước kho |

Image mới trên GHCR: `ghcr.io/dyuedu/haidoit-warehouse`, tag `sha-<commit>` và `main`.
