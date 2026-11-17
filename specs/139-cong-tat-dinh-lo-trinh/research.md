# Research: Cổng tất định cho thứ tự lộ trình

Ngày xem: 2026-11-16. Link ghim theo commit của nhánh chính lúc xem.

## Quyết định

- Thân hàm phép 8 là sắp xếp topo theo Kahn với hàng đợi ưu tiên `heapq`, khóa `(chặng, hạng nhóm, -tỷ lệ, mã)`. Mã kỹ năng là duy nhất nên khóa là thứ tự toàn phần, không cần khóa phụ theo thứ tự chèn.
- Cổng chạy phép đó trong tiến trình con với `PYTHONHASHSEED=0` và `1`, xáo đầu vào, rồi so với thứ tự cứng.

## Cách các repo công khai làm

- [networkx/networkx @ ada19dd](https://github.com/networkx/networkx/blob/ada19dd8000ec550fd45cf72841c416319dc568d/networkx/algorithms/dag.py) — `lexicographical_topological_sort(G, key)`. Lấy: Kahn với `heapq` trên các nút có bậc vào bằng 0, `key` do người gọi đưa vào; hết hàng đợi mà còn nút thì báo vòng (`NetworkXUnfeasible`). Không lấy: nó thêm `nodeid_map` (thứ tự chèn nút vào đồ thị) làm khóa phụ để so được các nút có khóa trùng, nên với khóa trùng kết quả phụ thuộc thứ tự dựng đồ thị. Phép 8 cấm điều đó (FR-22: không phụ thuộc thứ tự do cơ sở dữ liệu trả về), nên khóa kết bằng mã kỹ năng duy nhất. Cũng không lấy: thư viện là phụ thuộc lớn, và `haido_core/domain` chỉ được import thư viện chuẩn (AD-1).
- [python/cpython @ 91ab655](https://github.com/python/cpython/blob/91ab655eb519d7c48e78934e00295e3c755b04a9/Lib/graphlib.py) — `graphlib.TopologicalSorter`. Lấy: ý báo vòng bằng lỗi riêng (`CycleError`) và đếm số tiên quyết còn lại của từng nút (`npredecessors`). Không lấy: `static_order()` trả thứ tự theo thứ tự thêm nút và cạnh (từ điển giữ thứ tự chèn), không có khóa ưu tiên, và phục vụ chạy song song bằng `prepare`/`get_ready`/`done`. Không có chỗ cắm luật bốn tầng nên không dùng.
- Tìm "deterministic topological sort priority queue" trên GitHub không thấy kho nào kéo sẵn tổ tiên của một tập khoảng trống rồi xếp theo luật chặng, nhóm, tỷ lệ; phần kéo tổ tiên (truy vết ngược theo cạnh `before` -> `after`) là tự viết, đơn giản (ngăn xếp và tập đã thăm).

## Kiểm tính tất định

- `PYTHONHASHSEED` đổi thứ tự duyệt `set` và `dict` khóa chuỗi giữa các tiến trình, nên cổng chạy hai tiến trình và so kết quả. Cách này cùng kiểu với bước `determinism` đã có ở CI (`-m determinism`, hai lượt `PYTHONHASHSEED`), nhưng nằm ngay trong cổng AD-24 để chặn merge, không cần cài gói.
- Xáo `gaps`, `edges`, `skills` bằng `random.Random(seed)` cố định (20 hạt giống và một lần đảo ngược) để cổng chạy nhanh và lặp lại được.
