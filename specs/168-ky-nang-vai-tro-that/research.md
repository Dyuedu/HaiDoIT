# Research: tỷ lệ kỹ năng theo vai trò, số thật (#168)

Ngày 17/11/2026.

## lukebarousse/Python_Data_Analytics_Course

- Link: https://github.com/lukebarousse/Python_Data_Analytics_Course/blob/efeea590e6eb00b57690d3320ddbc3e354117870/3_Project/2_Skill_Demand.ipynb
- Lấy: tỷ lệ kỹ năng theo nhóm tin (số tin nhắc chia số tin của nhóm), xếp giảm dần để xếp hạng. Ở đây số chia đã do `aggregate` ghi (#101), chỉ đọc.
- Không lấy: tính tỷ lệ bằng `groupby` lúc đọc (AD-7 cấm); không cắt mẫu nhỏ (notebook xếp cả nhóm vài tin, còn ta ẩn dưới 30).

## pandas-dev/pandas

- Link: https://github.com/pandas-dev/pandas/blob/3f78c15dd01c22bea029ef4e56de3cabd29e4d31/pandas/core/methods/selectn.py
- Lấy: `nlargest` giữ thứ tự ổn định khi hòa giá trị; xác nhận cách làm khóa sắp xếp đủ để hòa tỷ lệ thì phân định bằng khóa phụ (mã vai trò), không phụ thuộc thứ tự hàng của DB.
- Không lấy: thuật toán chọn top-n; cần xếp đủ cả 17 vai trò.

## Trong repo

- `FakeMarket.skill_roles` (#166): khóa sắp xếp (`null_data` sau; tỷ lệ giảm dần; cỡ mẫu giảm dần; mã). Bản thật dùng đúng khóa đó.
- `StatMarket.newcomer_roles` (#146): `_national_cells` cho `n` và `seniority_mix` ô entry; lỗi `RuntimeError` khi số liệu hỏng.
- `StatMarket.skill_rates` (#151): chọn snapshot (`_latest_with_skill_rates`), dựng `Meta`.

## Quyết định rút ra

- Cỡ mẫu theo vai trò là `n_scanned` của hàng entry của kỹ năng đang xem, không đọc thêm bảng khác (`aggregate` ghi cùng giá trị ở mọi hàng của ô).
- Một truy vấn theo `(snapshot_id, skill)` dùng chỉ mục `ix_stat_skill_rates_snapshot_skill`, lấy cả hàng `entry` và hàng `all` để có `mentioned`.
