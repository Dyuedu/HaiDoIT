# Research: Test danh sách người mới

Ghi chú ngắn, theo "Cách làm việc" trong `CLAUDE.md`. Chỉ xem tên file và vài dòng đầu của từng file; không đọc hết.

## Repo tham khảo

1. **testing-library/dom-testing-library**, [`src/__tests__/role.js`](https://github.com/testing-library/dom-testing-library/blob/6049cc0bc7cf2201625c476c95fa6299d0e2fa8b/src/__tests__/role.js) (commit `6049cc0`).
   - Lấy: truy vấn theo role (`heading`, `listitem`) và tên, không dùng class hay `data-testid`. Đó là lý do test DEC-6 duyệt `h1..h6` thay vì dựa vào thẻ gắn tay.
   - Không lấy: cấu trúc test của chính thư viện (kiểm engine, không kiểm màn).
2. **alphagov/govuk-frontend**, [`summary-list/template.test.js`](https://github.com/alphagov/govuk-frontend/blob/a11bd3316363ab4702fcef81d6ce06a947c464ef/packages/govuk-frontend/src/govuk/components/summary-list/template.test.js) (commit `a11bd33`).
   - Lấy: test dựng từ ví dụ cố định rồi kiểm chữ trong từng phần tử; cùng ý với fixture JSON của #144.
   - Không lấy: render Nunjucks (repo này dùng React).
3. **stryker-mutator/stryker-js**, [README](https://github.com/stryker-mutator/stryker-js/blob/8f24ef0be3a2119fc44ac48bfce58930ab2c9032/README.md) (commit `8f24ef0`).
   - Lấy: ý tưởng chứng minh test cắn bằng đột biến.
   - Không lấy: công cụ. Đột biến làm tay một dòng, chạy, ghi vào `tdd.md`, hoàn lại.

## Quyết định

- Test DEC-6 duyệt phần tử thay vì dựa vào `data-testid`, vì thẻ gắn tay bỏ sót tiêu đề.
- Không cắt tỷ lệ về 1: cắt thì che dữ liệu hỏng. Thay vào đó lỗi nêu tên vai trò và hai số.
