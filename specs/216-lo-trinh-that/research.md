# Research: API trả lộ trình đã xếp kèm tỷ lệ của từng kỹ năng

- [exercism/docs @ bf02685, `building/tracks/config-json.md`](https://github.com/exercism/docs/blob/bf02685d047a436ed5d8d0b67fbb6761cbd8cfec/building/tracks/config-json.md): mỗi bài có `status` (`wip`, `beta`, `active`, `deprecated`) ngay trong file nội dung; bài `wip` không hiện cho người học. **Lấy ý**: trạng thái nằm cạnh nội dung, nguồn thật ẩn phần chưa duyệt, `beta` hiện kèm nhãn (như lưu ý bản nháp của app demo). **Không lấy**: mặc định `active` khi thiếu trạng thái; ở đây thiếu dấu là lỗi, vì #96 đòi có biên bản trước khi bật.
- Trong repo: `DraftPathMarket` của #217 đã ghép tỷ lệ thật; chuyển vào `StatMarket` thay vì viết lại.
