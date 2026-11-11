# Research: Bộ lọc cấp bậc và tổng hợp theo chiều

## Quyết định

Bộ chọn cấp bậc là một nhóm `<button aria-pressed>` như chip vai trò hiện có. Tổng hợp lưu sẵn mỗi cấp một bộ số trong bảng dẫn xuất, khóa có thêm cột cấp, API đọc theo khóa. Không tính lại lúc đọc.

## Cách các repo công khai làm

### Điều khiển chọn một trong nhiều, có bàn phím

- [radix-ui/primitives, `toggle`](https://github.com/radix-ui/primitives/blob/eb3a2b709129/packages/react/toggle/src/toggle.tsx): nút bật tắt dùng `aria-pressed`, trạng thái ra thêm `data-state`.
- [radix-ui/primitives, `toggle-group`](https://github.com/radix-ui/primitives/blob/eb3a2b709129/packages/react/toggle-group/src/toggle-group.tsx): nhóm chọn một dùng `role="radiogroup"` và roving focus (một điểm Tab cho cả nhóm, mũi tên đổi nút).
- **Lấy**: `aria-pressed` trên từng `<button>` và một nhóm có tên (`role="group"`, `aria-label`). Đúng cách `RoleChips` đang làm và đúng yêu cầu của issue.
- **Không lấy**: roving focus và `radiogroup`. Màn Bản đồ đã có chip vai trò với mỗi chip một điểm Tab (test bàn phím của #46 khóa điều đó); hai nhóm chọn một mà hành xử khác nhau sẽ làm người dùng bàn phím bối rối. Cũng không thêm thư viện.

### Lưu số tổng hợp theo chiều

- [cube-js/cube, pre-aggregations](https://github.com/cube-js/cube/blob/a1426171d36e/docs-mintlify/docs/pre-aggregations/using-pre-aggregations.mdx): một rollup khai báo danh sách `dimensions`, truy vấn nào dùng tập con các chiều đó thì đọc thẳng rollup thay vì tính lại từ bảng gốc.
- [plausible/analytics, `lib/plausible/stats/filters`](https://github.com/plausible/analytics/tree/0c3903a9411d/lib/plausible/stats/filters): bộ lọc được áp lúc truy vấn lên bảng sự kiện, tính lại mỗi lần.
- **Lấy** từ Cube: chiều lọc là một phần của khóa rollup; đọc theo khóa; mỗi tổ hợp chiều là một hàng đã tính.
- **Không lấy**: đối sánh rollup động và tính lúc đọc kiểu Plausible. AD-5 và cổng AD-7 cấm API cộng lại từ bảng tin, và snapshot đã chốt phải đọc ra đúng số đã công bố.

## Vì sao ghi sẵn một hàng `all` thay vì để trống chiều

Cột `seniority` của `stat_cells` đã dùng sentinel `all` từ #93. `stat_city_shares` theo cùng quy ước (`all`), nên hàng cũ chỉ cần nhận `all` và API không có nhánh `NULL`.

## Vì sao nhóm `entry` cộng từ các cấp thay vì đếm riêng

Một cụm chỉ có một cấp, các cấp rời nhau, nên n của nhóm là tổng n của thành viên và không đếm cụm hai lần. Nhóm nằm trong `config/rules.toml` (#134) nên đổi nhóm không cần đổi code.
