# Data model: Hiệu chỉnh và đóng băng θ_core, θ_common

## Bảng và cột

| Bảng | Thay đổi |
|---|---|
| `haido.snapshots` | Thêm cột `theta_version text NULL`. NULL ở snapshot tính trước đóng băng; đọc là `PRE_FREEZE_THETA_VERSION` (`theta-1`, luôn là mục đầu của sổ đăng ký). `replace_stats` chỉ ghi cột này khi `status = 'open'`. |

Không bảng nào khác đổi. Nhóm core, common, rare vẫn không lưu: tính lúc đọc từ tỷ lệ và θ của phiên bản trong snapshot.

## Alembic

- Revision mới: `0010_haido_snapshot_theta` (sau `0009_haido_skill_rates`). `upgrade` thêm cột; `downgrade` bỏ cột.
- Không điền lại hàng cũ, nên migration không đọc file cấu hình.

## Cấu hình (không phải DB)

`config/theta.toml`, chỉ-thêm:

```toml
[[versions]]
id = "theta-1"
theta_core = 0.3
theta_common = 0.1
calibrated_on = "2026-11-19"
note = "..."
```

`config/rules.toml`: `theta_core` và `theta_common` bị bỏ (còn khóa nào là `ConfigError`), thay bằng `theta_version = "theta-1"`; `config_version` từ `2026-11-17.1` lên `2026-11-19.1`.

## Hợp đồng API

`meta.thresholds` thêm `theta_version` (chuỗi không rỗng). Xem `docs/api/envelope-meta.md` và `docs/api/openapi.json`.
