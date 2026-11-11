# Research: Hình response của màn người mới và dữ liệu giả

## Quyết định

- Dữ liệu giả do chính API phục vụ (nguồn `fake` chọn bằng biến môi trường), như `city-shares` và `skill-rates` đã làm. Web dùng fixture chép từ response của API giả, có test so hai bên.
- Số đếm nằm ở `meta.cells`, tỷ lệ là `Stat` loại `level_share`.

## Cách các repo công khai làm

- [stoplightio/prism, `packages/http/src/mocker/negotiator/NegotiatorHelpers.ts`](https://github.com/stoplightio/prism/blob/e5d2bed63a15853a275b09fe1702fc20610c7b3e/packages/http/src/mocker/negotiator/NegotiatorHelpers.ts): mock server sinh response từ `example` trong OpenAPI, hoặc sinh ngẫu nhiên từ schema khi bật `dynamic`. Lấy ý "hợp đồng trước, dữ liệu giả theo đúng hợp đồng". Không lấy công cụ: example tĩnh trong OpenAPI không chạy validator của Envelope (`display` khớp `suppression_for`, mọi `cell_id` có mục), còn sinh ngẫu nhiên thì không cho được các ca biên mà #110 cần (dưới 30 tin, 0 tin entry-level).
- [mswjs/msw, `src/core/handlers`](https://github.com/mswjs/msw/tree/ec5e8777d6c81f3953d3454d755552a67159eb86/src/core/handlers): chặn `fetch` phía trình duyệt và trả dữ liệu giả từ handler. Không lấy: thêm một gói và một nguồn giả thứ hai nằm trong web, có thể lệch với API. Repo đã có cách rẻ hơn: `web/tests/helpers/fetch.ts` stub `fetch` bằng fixture, và `tests/api/test_ad17_web_fixtures.py` bắt fixture lệch API.

## Vì sao số đếm nằm ở `meta.cells`

Hợp đồng AD-17 (`docs/api/envelope-meta.md`) đặt cỡ mẫu của mọi con số ở `meta.cells[cell_id].n` và cấm số đứng riêng trong `data`. Số tin entry-level của một vai trò chính là cỡ của ô "vai trò × Intern/Fresher/Junior trên toàn quốc", nên khai nó là một ô (`vn.<role>.entry`) thì không cần loại `Stat` mới cho số đếm, và Envelope tự kiểm ô đó có mục. Ô `vn.backend.entry` đã có trong bản giả với đúng nghĩa này (n = 52 = 13 + 7 + 32).

## Vì sao thêm `level_share`

`composition_share` dưới ngưỡng là `low_sample_shown` (hiện mờ) — đúng cho tỷ trọng thành phố (FR-33). #110 lại đòi vai trò dưới 30 tin ghi "not enough data (X/30)" thay cho tỷ lệ. Dùng `skill_rate` thì sai nghĩa. Loại mới `level_share` là tỷ lệ 0–1, dưới ngưỡng ra `null_data`, và vẫn đi qua `suppression_for` như mọi loại khác.
