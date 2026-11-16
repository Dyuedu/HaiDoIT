# Research: Endpoint tỷ lệ kỹ năng giả

## Quyết định

- Đếm kỹ năng core đã có ở API, qua `have=`, như `learning-path` đã làm (`have_on_path`, `path_size`).
- Bản giả sắp dòng; web hiện đúng thứ tự nhận được.

## Tham khảo

- Trong repo: `GET /api/v1/learning-path` (#212, hàm `parse_have` của `haido_api/routes/market.py`) đã chốt cách gửi hồ sơ lên bằng `have=` cho AD-22. Dùng lại nguyên hàm, không viết luật mới.
- [kamranahmedse/developer-roadmap (nay là `nilbuild/developer-roadmap`) @ 2b53446](https://github.com/nilbuild/developer-roadmap/tree/2b534461da5629c57d8a0a4a7efcb26adc7f179e): roadmap.sh hiện "X of Y done" theo tiến độ người dùng. Ở commit này repo chỉ còn nội dung roadmap, không còn mã ứng dụng, nên không đọc được cách nó đếm. Hải Đồ giữ cách đã có trong repo.

## Không lấy

- Không trả `requested_cell_id`: `fallback_label` khác `null` đã cho biết có quay về, và `meta.cells[cell_id].n` là n của ô đã dùng.
