# TDD: Màn người mới và lối sang hồ sơ kỹ năng

Theo `docs/templates/test-driven-tdd/test-driven-development.md`. Test web thay `fetch` bằng fixture `web/tests/fixtures/newcomer-roles.json` (response của API giả, #144), không gọi mạng.

Lệnh:

```text
cd web && npx vitest run tests/fr37-newcomer-list.test.tsx
```

## Các hành vi

1. Mỗi vai trò một dòng, nhãn tiếng Việt, đúng thứ tự API.
2. API gửi thứ tự đảo thì web hiện đúng thứ tự đảo (không sắp xếp lại).
3. Dòng đủ mẫu: "501 tin cho người mới", "57,1%", "n = 877".
4. Dòng dưới ngưỡng: "chưa đủ dữ liệu (12/30)", không có "%".
5. Dòng 0 tin entry-level (`devops`) và không có tin nào (`other`) vẫn ở lại, ghi "0 tin cho người mới".
6. Ngưỡng trong ghi chú lấy từ `meta.thresholds.min_sample` ("12/50").
7. Liên kết của dòng là `/ho-so-ky-nang?role=ai_ml&level=entry`, tên liên kết bắt đầu bằng tên vai trò.
8. Khung "Nguồn và lưu ý" có ngày, nguồn, mọi lưu ý.
9. `unknown_cell`: thông báo, ngày, không "Thử lại", không danh sách.
10. Mạng hỏng: "Không đọc được số liệu", "Thử lại" tải lại được.
11. Tám kiểu envelope sai hợp đồng → `unreadable`; envelope đúng → `ok`.
12. Trang giữ chỗ: tiêu đề có tên vai trò, cấp "Mới vào nghề", "sprint sau", nút quay lại `/insights`.
13. Mã vai trò lạ: không in mã, ghi "Không có vai trò này".
14. Câu giới thiệu và câu trang giữ chỗ không có chữ số (DEC-6).

## RED (2026-11-12)

`npx vitest run tests/fr37-newcomer-list.test.tsx` → 1 file failed, không test nào chạy: `Failed to resolve import "@/app/ho-so-ky-nang/page"` (trang giữ chỗ chưa có; `fetchNewcomerRoles` cũng chưa có). Trước đó một lượt hỏng vì test dùng matcher của `jest-dom` mà repo không cài; đã đổi sang assertion thuần của Vitest như các test web khác, đó không phải RED của hành vi.

## GREEN (2026-11-12)

- Lượt đầu sau khi viết code: 20 passed, 2 failed. Hai test hỏng do chính test (`.textContent` gắn vào promise của `findByRole` khi đổi matcher); sửa test, không sửa code. Test `unknown_cell` thêm ngày snapshot vào body lỗi để kiểm đúng điều tên test nói.
- `npx vitest run tests/fr37-newcomer-list.test.tsx` → 22 passed.
- `npx vitest run` → 13 files, 189 passed.
- `npx tsc --noEmit`, `npm run lint` sạch; `npm run build` xong, `/insights` tĩnh, `/ho-so-ky-nang` động.
- `tools/gates/check_gates.py` → 8 pass (có FR-25/31/47 từ ngữ cấm), 2 skip, 0 fail.
- Chrome headless trên `next start` với API local (nguồn giả):
  - 360px: 17 dòng, không cuộn ngang (360/360), dòng thấp nhất 96px.
  - 1280px: không cuộn ngang, dòng thấp nhất 49px.
  - Bấm dòng đầu: `/ho-so-ky-nang?role=ai_ml&level=entry`, tiêu đề "Hồ sơ kỹ năng: AI/ML".

## Đợt 2026-11-13 (#148): khóa thêm thứ tự, `role=all`, DEC-6

Lý do: review PR #291 thấy test chưa kiểm thứ tự DOM `null_data` sau `shown`, thứ tự giảm dần, `role=all`, và test DEC-6 chỉ đọc phần tử có `data-testid`. Test DEC-6 cũ được thay bằng hai test duyệt `h1..h6`, `p`, `a`.

- RED: không có, mã sản phẩm của #147 đã đúng. Bằng chứng test cắn là các đột biến ở `specs/148-test-nguoi-moi/tdd.md` (đột biến thứ tự làm đỏ 4–5 test; chữ số trong tiêu đề và `role=all` mỗi cái làm đỏ 1 test).
- GREEN: `npx vitest run tests/fr37-newcomer-list.test.tsx` → 26 passed; `npm run test` → 13 files, 193 passed; `npm run lint` sạch; `npm run build` xong.

## Đợt 2026-11-16 (#111, #152): trang giữ chỗ được thay

Lý do: #152 thay `web/app/ho-so-ky-nang/page.tsx` bằng hồ sơ kỹ năng thật, như FR-005 của spec này đã báo trước. Liên kết của dòng (`skillProfileHref`) không đổi.

- Test của khối "trang giữ chỗ hồ sơ kỹ năng" trong `web/tests/fr37-newcomer-list.test.tsx` viết lại thành "trang đích của một dòng": mở đúng vai trò ở cấp mới vào nghề, mã lạ và `role=all` không in như tên. Bỏ kiểm câu "sprint sau" và nút quay lại `/insights` (không còn trên trang). Test DEC-6 của trang đó kiểm khung trang trước khi có số, với `fetch` giả treo.
- RED: sau khi thay trang, `npx vitest run` → 1 failed ("gọi tên vai trò, cấp mới vào nghề, và nói hồ sơ kỹ năng có ở sprint sau"), đúng chỗ đã đổi chủ ý.
- GREEN: `npx vitest run` → 21 files, 281 passed.

## Đợt 2026-11-17 (#113, #169): `/insights` có thêm mục kỹ năng

Lý do: #169 thêm mục "Kỹ năng của bạn dùng ở vai trò nào" dưới "Cửa vào cho người mới" trên `web/app/insights/page.tsx`. Mục mới gọi thêm `/api/v1/skills` và có vùng `role="status"` riêng. Hành vi của danh sách người mới không đổi; không AC nào của #147 đổi.

- RED: `npx vitest run` → 2 failed trong `web/tests/fr37-newcomer-list.test.tsx`: "mạng hỏng thì báo không đọc được và thử lại được" (`fetch` được gọi 3 lần thay vì 2, lần thêm là `/api/v1/skills`) và test DEC-6 "lúc đang tải…" (`Found multiple elements with the role "status"`).
- Sửa test: đếm lần gọi của `/api/v1/newcomer-roles`, và đọc vùng `status` trong region "Cửa vào cho người mới".
- GREEN: `npx vitest run` → 25 files, 328 passed.

## Đợt #324 (2026-11-19): câu chữ trên màn viết lại

Lý do: #324 viết lại chữ hiển thị bằng tiếng Việt dễ hiểu (bỏ nhãn `n = `, "snapshot", "entry-level"; câu thiếu mẫu "Mới có X tin, cần ít nhất 30"; khung nguồn "Đang xem", "Cập nhật", tên nguồn). File của issue này bị đụng: `web/lib/newcomer-roles-view.ts`, `web/app/components/insights/newcomer-list.tsx`. Số, thứ tự và ẩn số theo ngưỡng không đổi. Câu trong scenario của `spec.md` đã sửa theo câu mới; ý của AC giữ nguyên (người dùng đồng ý 2026-11-19).

- RED và GREEN: `specs/324-cau-chu-de-hieu/tdd.md` (RED 42 failed / 299 passed; GREEN 357 passed, chạy `npx vitest run` từ PowerShell).

## Đợt #102 (2026-11-19): θ có phiên bản, AC của issue này không đổi

Lý do: #102 đóng băng θ (`config/theta.toml`, `theta-1` = 0,3/0,1), thêm `snapshots.theta_version` (migration 0010) và `meta.thresholds.theta_version`, sửa file mà issue này từng đụng: `web/lib/city-shares.ts`.
Giá trị θ không đổi nên số, nhóm và hành vi của issue này không đổi; test chỉ thêm `theta_version` vào ngưỡng hoặc đổi head migration mong đợi sang 0010. RED, GREEN và đột biến: `specs/102-dong-bang-theta/tdd.md`.

## Đợt #329 (2026-11-19): /insights thêm toàn cảnh ở đầu trang, AC của issue này không đổi

Lý do: #329 thêm mục toàn cảnh thị trường lên đầu `/insights` (`web/app/insights/page.tsx`). Mock `fetch` trong test của mục này (`web/tests/fr37-newcomer-list.test.tsx`, `web/tests/helpers/skill-roles.ts`) trả "đang tải" mãi cho `/api/v1/market-overview`, để test vẫn chỉ kiểm mục của issue này. Hành vi và AC không đổi.

- RED và GREEN: `specs/329-man-tong-quan/tdd.md` (`npx vitest run` → 366 passed).

## Đợt #330 (2026-11-19): danh sách thành biểu đồ, AC của issue này không đổi

Lý do: #330 thêm thanh vào danh sách người mới, lollipop vào danh sách kỹ năng theo vai trò, bảng số cho cả hai và biểu đồ cơ cấu cấp bậc (`web/lib/newcomer-roles-view.ts`, `skill-roles-view.ts`, `market-overview-view.ts`, các component trong `web/app/components/insights/`). Chữ, số, thứ tự và luật ẩn số không đổi. Bộ quét DEC-6 trong `web/tests/fr37-newcomer-list.test.tsx` miễn thêm `table` (bảng số là ô số theo thiết kế).

- RED và GREEN: `specs/330-bieu-do-nguoi-moi-ky-nang/tdd.md` (`npx vitest run` → 373 passed).
