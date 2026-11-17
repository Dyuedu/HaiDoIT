# Research: tỷ lệ kỹ năng thật (#151)

Ngày 17/11/2026. Phần quay về dùng chung với `specs/106-chon-o-quay-ve/research.md`.

## kaptinlin/go-i18n

- Link: https://github.com/kaptinlin/go-i18n/blob/1612a824823f49c91f71d7c9e8d8eca6f7328e1b/localizer.go
- Lấy: kết quả tra cứu mang theo nguồn đã cấp giá trị (`TranslationSourceFallback`), nên người gọi nói được "đã dùng tập nào". Ở đây thành `fallback_label`, `data.cell_id` và `meta.cells[cell_id].n`.
- Không lấy: xem `106-chon-o-quay-ve/research.md`.

## lukebarousse/Python_Data_Analytics_Course

- Link: https://github.com/lukebarousse/Python_Data_Analytics_Course/blob/efeea590e6eb00b57690d3320ddbc3e354117870/3_Project/2_Skill_Demand.ipynb
- Lấy (đã dùng ở #101): tỷ lệ kỹ năng chia cho số tin của nhóm. Ở lớp đọc này chỉ đọc số đã ghi.
- Không lấy: tính tỷ lệ trong lúc đọc. AD-7 cấm; số do `aggregate` ghi.

## Trong repo

- `StatMarket.city_shares` và `newcomer_roles` (#93, #146): khuôn chọn snapshot đọc được, `meta` từ `rules.toml`, `UnknownCell` có và không có ngày. Dùng lại.
- `FakeMarket.skill_rates` (#149): thứ tự dòng (tỷ lệ giảm dần rồi mã; `null_data` theo mã) và cách đếm `core_size`, `have_core`. Bản thật theo cùng quy tắc.

## Quyết định rút ra

- Cỡ mẫu quyết định ô là `n_scanned`, không phải `n` của ô (AD-17 `n_by_measure.skill_count`); nếu dùng `n`, ô được chọn vẫn bị `suppression_for` ẩn ngay sau đó.
- Khi không tập nào đủ, trả ô `all` với dòng `null_data` thay vì lỗi, để web hiện nhãn và "chưa đủ dữ liệu" (AC 3).
