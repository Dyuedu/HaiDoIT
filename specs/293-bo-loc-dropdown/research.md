# Research: bộ lọc bằng `<select>` gốc trong repo public

Ngày 13/11/2026. Xem hai design system công khai có `<select>` gốc dùng được bằng bàn phím và trình đọc màn hình.

## alphagov/govuk-frontend (GOV.UK Design System, component Select)

- Link: https://github.com/alphagov/govuk-frontend/blob/a11bd3316363ab4702fcef81d6ce06a947c464ef/packages/govuk-frontend/src/govuk/components/select/template.njk
- Cách làm: `<label for=id>` hiện luôn đứng trên `<select id>`; ghi chú (hint) có id riêng nối vào `aria-describedby` của `<select>`. Không dùng nhãn chỉ-placeholder, không dùng `aria-label` thay nhãn hiện.
- Lấy: nhãn hiện nối bằng `for`/`id`; ghi chú nối bằng `aria-describedby` (đúng cách `LevelChips` và `YearsChips` đang nối ghi chú).
- Không lấy: macro Nunjucks, `govuk-form-group` và lớp lỗi: màn này không có form gửi đi.

## uswds/uswds (U.S. Web Design System, usa-select)

- Link: https://github.com/uswds/uswds/blob/029d6d792241b3b4107a630590a27ee951a152b5/packages/usa-select/src/styles/_usa-select.scss
- Cách làm: `appearance: none` cộng mũi tên nền SVG dời bên phải với `padding-right` chừa chỗ; `option { overflow: hidden; text-overflow: ellipsis }`; `@media (forced-colors: active)` trả `appearance: listbox` và bỏ mũi tên.
- Lấy: `appearance: none` kèm chevron vẫn giữ picker và bàn phím gốc; chừa `padding-right` cho chevron để nhãn dài không đè lên.
- Không lấy: SCSS và token của USWDS; xử lý autofill (không có form); `[multiple]` (không dùng); forced-colors riêng (chevron là nền CSS, người dùng forced-colors vẫn có `<select>` gốc; xem lại nếu DoD đòi).
