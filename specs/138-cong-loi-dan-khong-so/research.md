# Research: cổng CI kiểm câu chữ theo mẫu cấm

Ngày 2026-11-16.

## errata-ai/vale

- Link: https://github.com/errata-ai/vale/blob/4ce91ef208b37f9ac2894766e8cd7b33ffe3baed/internal/check/existence.go
- Cách làm: kiểm "existence" là danh sách mẫu (regex) mà văn bản không được chứa; mỗi lần khớp là một cảnh báo kèm vị trí tệp và dòng; mẫu nằm ở một chỗ (file style), công cụ chỉ chạy chúng.
- Lấy: một nguồn quy tắc duy nhất cho mọi nơi kiểm, và báo `tệp:dòng` cho mỗi vi phạm. Ở đây nguồn là `prepared_text.py`.
- Không lấy: engine và file style YAML. Quy tắc chỉ có ba ý và đã có hàm Python kèm test; thêm Vale là thêm một công cụ phải cài trong CI, trong khi `check_gates.py` chạy bằng stdlib.

## get-alex/alex

- Link: https://github.com/get-alex/alex/blob/9a57595d1050d8fff99dc073670ee2bb41c925f6/cli.js và https://github.com/get-alex/alex/blob/9a57595d1050d8fff99dc073670ee2bb41c925f6/test/cli.js
- Cách làm: CLI quét văn bản, thoát khác 0 khi gặp cụm bị cấm; test chạy CLI trên file mẫu bẩn và sạch rồi so mã thoát.
- Lấy: cặp test "mẫu sạch PASS, mẫu bẩn FAIL" cho từng quy tắc, và quét từng dòng của văn bản đã chuẩn bị sẵn.
- Không lấy: danh sách từ và allowlist theo cấu hình (ở đây ngoại lệ là `TECH_NAMES` trong code, kèm test).

## Kết luận

Cả hai tách quy tắc khỏi chỗ chạy. Repo này đang có hai bản quy tắc lệch nhau (regex cũ của cổng cho qua "Hơn 30 tin cần Python", hàm của FR-23 thì bắt); sửa bằng cách cổng gọi hàm của FR-23.
