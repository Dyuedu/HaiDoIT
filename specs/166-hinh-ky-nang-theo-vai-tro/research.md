# Research: Hình response của một kỹ năng qua các vai trò và dữ liệu giả

## Quyết định

- Tái dùng khuôn của `newcomer-roles` (#144): mỗi vai trò một dòng, tỷ lệ là `Stat`, n ở `meta.cells`, thứ tự do máy chủ quyết, `null_data` dưới 30 vẫn giữ n. Loại thước đo là `skill_rate` đã có, không thêm `MeasureKind`.
- Kỹ năng không có tin nào nhắc là 200 với `mentioned = false`, không phải lỗi.
- Kỹ năng ngoài bộ từ vựng là lỗi 404 riêng, `unknown_skill`.

## Cách các repo công khai làm

- [onetcenter/web-services-v2-samples@0c414d6, `nodejs/keyword_search.js`](https://github.com/onetcenter/web-services-v2-samples/blob/0c414d6407675e31a4f0e442aed05da91fe0725b/nodejs/keyword_search.js): tra "từ khóa sang nghề" qua `online/search`; khi không có nghề nào thì kết quả là danh sách rỗng và chương trình in "No relevant occupations were found."; lỗi thật nằm ở trường `error` riêng. Lấy ý: "không có gì khớp" là một kết quả hợp lệ (ở ta là 200, `mentioned = false`), tách khỏi lỗi tham số. Không lấy: API của O*NET đi từ từ khóa tới danh sách nghề khớp; ta đi từ một kỹ năng đã biết mã tới tỷ lệ ở đủ mọi vai trò, có cỡ mẫu và ngưỡng, nên hình khác. Cũng không lấy việc dùng khóa API cá nhân.
- [repurpose/emsi-skills-api@2727df4, `lib/api/skills.js` và `test/skills.spec.js`](https://github.com/repurpose/emsi-skills-api/blob/2727df46bf7de59a8ceea07446944077dc5edde4/lib/api/skills.js): kỹ năng có mã ổn định (`id`) tách khỏi tên hiển thị (`name`), tra theo mã qua `skillById`; test khóa tập trường của response (`to.have.all.keys`). Lấy ý: trả cả mã và tên để màn ghi kỹ năng đã khớp (`data.skill`), và khóa tập trường bằng test (như `set(row) == {...}` ở đây). Không lấy: mã `KS...` của Lightcast và đường tra theo `id` qua HTTP; mã ta là `snake_case` của #205, tên lấy từ `skills_seed.json`. Gói là bản không chính thức, không dùng làm phụ thuộc.

## Vì sao `mentioned` do máy chủ tính

Màn cần câu "chưa tin nào nhắc kỹ năng này" (AC 4 của #113). Nếu web suy từ các dòng thì sai ở hai chỗ: ô dưới ngưỡng bị ẩn (`null_data`) có thể có tin nhắc, và mọi dòng hiện đều 0 chưa chứng minh không ai nhắc. Cờ ở API tránh việc web đếm (AD-22) và cho #170 một điều kiện kiểm được.

## Vì sao ô là `vn.<role>.entry` và cỡ mẫu là `skill_count`

AD-17 đặt cỡ mẫu của mọi con số ở `meta.cells[cell_id]`. Ô entry của vai trò đã có từ #144 và đã là mẫu số của `newcomer-roles`; dùng lại thì hai màn thấy cùng một `n` của ô, nên `n` không đổi nghĩa. Thực tế #101 ghi `n_scanned` làm mẫu của phép đo kỹ năng (nhỏ hơn hoặc bằng `n` của ô), đúng nghĩa của khóa `n_by_measure.skill_count` đã có (số tin có giá trị về kỹ năng). Nên cỡ mẫu của tỷ lệ là `skill_count`, và `Envelope` kiểm `display` của `skill_rate` theo đó (đợt 2, 2026-11-17). Không chép từ repo công khai nào: cả hai repo ở trên không có khái niệm hai cỡ mẫu trên một ô.

## Vì sao `mentioned` theo mọi cấp (đợt 2)

AC 4 của #113 nói "một kỹ năng mà không tin hiện tại nào nhắc". Chỉ tin entry-level thì sai: một kỹ năng có tin ở cấp Senior nhưng không có tin entry-level vẫn được nhắc, và màn không được ghi "chưa tin nào nhắc" (người dùng sẽ hiểu kỹ năng đó không ai tuyển). Vì vậy cờ tính từ số tin nhắc kỹ năng ở mọi cấp.
