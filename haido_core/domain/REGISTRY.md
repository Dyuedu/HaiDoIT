# Registry đóng — tám phép dùng chung (AD-2)

Mỗi phép có một chữ ký trong `registry.py`. Chữ ký gọi được cho một đối tượng và cho một lô (`list` hoặc `tuple`). Không có biến thể chỉ-theo-lô. Thân hàm chưa có. Thêm phép thứ chín thì sửa file này trong cùng thay đổi.

| # | Phép | Hàm | Chữ ký | Cài sau |
|---|---|---|---|---|
| 1 | mapping lượt nhắc → mã kỹ năng | `map_mentions` | `(mentions: OneOrMany[Mention]) -> OneOrMany[MappedMention]` | `haido_core/domain/mapping.py` |
| 2 | chọn ô thống kê + thứ tự quay về | `select_cell` | `(queries: OneOrMany[CellQuery]) -> OneOrMany[CellChoice]` | `haido_core/domain/cells.py` |
| 3 | dân số của ô (cửa sổ 60 ngày, đếm theo cụm) | `population` | `(requests: OneOrMany[PopulationRequest]) -> OneOrMany[int]` | `haido_core/domain/population.py` |
| 4 | nhóm kỹ năng theo θ | `group_skills` | `(requests: OneOrMany[SkillGroupRequest]) -> OneOrMany[tuple[SkillGroup, ...]]` | `haido_core/domain/skill_groups.py` |
| 5 | phân vị, mốc, khoảng tin cậy | `percentiles` | `(requests: OneOrMany[PercentileRequest]) -> OneOrMany[PercentileResult]` | `haido_core/domain/percentiles.py` |
| 6 | phân loại vai trò / nhánh / cấp bậc / thành phố | `classify` | `(postings: OneOrMany[PostingFacts]) -> OneOrMany[Classification]` | `haido_core/domain/classify.py` |
| 7 | so khớp tin (trong nguồn và chéo nguồn) | `match_postings` | `(pairs: OneOrMany[PostingPair]) -> OneOrMany[MatchDecision]` | `haido_core/domain/matching.py` |
| 8 | xếp thứ tự lộ trình, quy tắc 4 tầng | `order_path` | `(requests: OneOrMany[PathRequest]) -> OneOrMany[tuple[str, ...]]` | `haido_core/domain/path_order.py` |

`OneOrMany[T]` là `T | list[T] | tuple[T, ...]`. Một đối tượng trả một kết quả. Một lô trả `tuple` cùng độ dài.

Quy tắc không nằm trong thân hàm, nhưng chữ ký không được phép phá:

- chọn ô trả ô, `n` và nhãn cùng lúc. Quay về chỉ trong cùng phạm vi. Ô thành phố không quay về ô toàn quốc.
- dân số đếm cụm. `window_days` là tham số.
- nhóm kỹ năng nhận `theta_core` và `theta_common` từng lần gọi.
- phân vị nhận `seed` từ người gọi.
- phân loại được nhận văn bản JD đầy đủ (chức danh, mô tả, dòng địa chỉ) nhưng không gọi mô hình: cùng đầu vào và cùng cấu hình thì cùng nhãn. Văn bản JD chỉ đi qua bộ nhớ, không ghi vào bảng, log hay file tạm (DoD dòng 9); kết quả chỉ là nhãn và mã. Nhánh có thể trống cho tới Story 1.9.
- so khớp không xóa tin.
