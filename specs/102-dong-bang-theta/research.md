# Research: Hiệu chỉnh và đóng băng θ_core, θ_common

Ngày 2026-11-19. Câu hỏi: làm sao một ngưỡng cấu hình có phiên bản, không đổi lặng lẽ, mà đổi có chủ đích vẫn dễ?

## Repo đã xem

### syrupy-project/syrupy (kiểm "giá trị đã ghi không đổi nếu không có hành động rõ")

- Link: https://github.com/syrupy-project/syrupy/blob/098dd11d86376de9154d9cc2ddec5ef37df0dcf6/README.md
- Lấy: ý tưởng test so sánh với bản đã ghi và chỉ cập nhật bằng một thao tác chủ động (`pytest --snapshot-update`), nên mọi thay đổi hiện trong diff. Áp vào đây thành test ghim `PINNED`: sửa giá trị phiên bản cũ thì test đỏ, muốn thêm phiên bản phải sửa `PINNED` cùng commit.
- Không lấy: thư viện, file snapshot `.ambr` và cờ cập nhật tự động. θ chỉ có vài số; một dict literal trong test dễ đọc hơn và không có đường "cập nhật hết cho xanh".

### sqlalchemy/alembic (thêm cột nullable không điền lại)

- Link: https://github.com/sqlalchemy/alembic/blob/1bcba93ea0473c69b48e704f842ca96e9e5348f5/alembic/operations/ops.py (`AddColumnOp`)
- Lấy: `op.add_column` với cột nullable, không chép dữ liệu trong migration; `drop_column` khi hạ cấp. Cùng kiểu với cột `vocab_version` của migration 0009 trong repo.
- Không lấy: điền giá trị mặc định bằng `server_default`. Một `server_default = 'theta-1'` sẽ làm snapshot tính sau này ghi `theta-1` mà không do `aggregate` quyết, che mất lỗi quên ghi. NULL giữ nghĩa "trước đóng băng".

### great-expectations/great_expectations (bộ ngưỡng có phiên bản, lưu cùng kết quả)

- Link: https://github.com/great-expectations/great_expectations/tree/e08d1a800c8b759c84b820e420f5699392c53a98 (chỉ tham khảo ý tưởng: bộ ngưỡng kiểm dữ liệu là một đối tượng có tên, và kết quả kiểm nói rõ bộ nào đã chạy; không đọc sâu mã)
- Lấy: kết quả giữ định danh của bộ ngưỡng đã dùng thay vì suy từ cấu hình hiện hành. Áp vào đây: mỗi snapshot lưu `theta_version`.
- Không lấy: định dạng suite JSON hay kho lưu trữ; ở đây chỉ cần một file TOML chỉ-thêm.

## Quyết định

- Sổ đăng ký là file TOML chỉ-thêm cạnh `rules.toml`, nạp cùng cấu hình; `rules.toml` chỉ chọn phiên bản hiện hành.
- Phiên bản lưu theo từng snapshot, đọc lại bằng chính phiên bản đó.
- Chốt bằng test ghim, không bằng ràng buộc DB, vì sổ đăng ký nằm ở file.
- Tách 'giá trị' khỏi 'phiên bản hiện hành' để thêm `theta-2` sau này không cần chạm snapshot cũ.
