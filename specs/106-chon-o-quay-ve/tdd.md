# TDD: phép 2, chọn ô và thứ tự quay về (#106)

Theo `docs/templates/test-driven-tdd/test-driven-development.md`. Test không mạng, không database; bảng ô là một class giả ghi lại mọi ô đã tra.

Lệnh:

```text
uv run pytest tests/domain/test_ad2_select_cell.py tests/domain/test_ad2_registry.py -q
python tools/gates/check_gates.py --require AD-2
```

## Các hành vi (`tests/domain/test_ad2_select_cell.py`, mã AD-2, AD-6, AD-17, FR-19)

1. Khớp chữ ký Protocol `SelectCell` của registry.
2. Ô được yêu cầu đủ mẫu: trả chính nó, `label = None`, chỉ tra một ô.
3. Ngưỡng: `n = min_sample` đủ, `n = min_sample - 1` thì quay về.
4. Cấp thô thuộc nhóm: quay về nhóm; nhãn gọi tên cả hai ô và n của cả hai.
5. Nhóm cũng thiếu: quay về `all`; nhãn có n của ô yêu cầu và ô `all`.
6. FR-19: bước `all` với cấp mới vào nghề ghi tỷ lệ Mid trở lên của ô `all` (60% từ `seniority_mix`); cấp `mid` không có câu này; không có cơ cấu cấp thì không có câu này.
7. Không tập nào đủ: ô cuối kèm nhãn "chưa ... 30"; ô thiếu coi như n = 0.
8. Cấp `all`: một ứng viên.
9. Thứ tự (`order`) của `fresher`, `entry`, `mid`, `unknown`.
10. AD-6: phạm vi, vai trò, snapshot không đổi (ô `hanoi` không quay về `vn`); nhánh thử trước, nhánh `all` sau, trong từng bước cấp.
11. AD-17: quyết định theo `sample_n`, không theo `n`.
12. AD-2: cùng truy vấn cùng kết quả (nhiều lần, hai selector); một đối tượng và một lô (list, tuple, rỗng, đảo thứ tự); `min_sample < 1` và phần tử không phải `CellQuery` là `ValueError`.

## RED

Chạy 2026-11-17 sau khi viết test, trước khi viết code:

- `uv run pytest tests/domain/test_ad2_select_cell.py -q` → 1 error lúc thu thập: `ModuleNotFoundError: No module named 'haido_core.domain.cells'`. Không test nào chạy được, nên không có số "failed" theo từng hành vi; chúng chạy lần đầu ở GREEN.

## GREEN

- Sau khi viết `haido_core/domain/cells.py` và sửa `CellChoice`: `uv run pytest tests/domain/test_ad2_select_cell.py tests/domain/test_ad2_registry.py -q` → 33 passed, 1 failed. Test đỏ là lỗi của test: `isinstance(x, SelectCell)` không dùng được với Protocol không `runtime_checkable`. Sửa test thành gán kiểu tĩnh `sel: SelectCell = ...`, không sửa code.
- `uv run pytest tests/domain/test_ad2_select_cell.py -q` → 20 passed.
- `ruff` báo `TRY004` cho `ValueError` khi sai kiểu; đổi sang `CellSelectionError(ValueError)` (cùng kiểu `PathOrderError`), test vẫn xanh.
- `python tools/gates/check_gates.py --require AD-2` → PASS (một Protocol, một thân hàm).

## Đợt 2 (2026-11-17): sửa theo review

Lý do: nhãn phải nói con số là gì (với tỷ lệ kỹ năng là `n_scanned`, không phải `n` của ô); tỷ lệ Mid trở lên phải làm tròn nửa lên, mẫu số là mọi tin kể cả `unknown`; test nhãn phải đúng từng chữ. AC không đổi.

- Hành vi thêm: `sample_noun` ("tin" mặc định; "tin đọc được kỹ năng" cho `skill_rates`) vào nhãn quay về và nhãn không tập nào đủ; làm tròn nửa lên bằng số nguyên `(200*mid + total) // (2*total)`; test mẫu số có `unknown`, `lead`, `mid`, `senior`, cấp entry (50%, không phải 60%) và các ca .5 (1/8 thành 13%, 7/8 thành 88%, 1/3 thành 33%, 0%); mọi test nhãn so cả chuỗi.
- RED: xem `specs/151-ty-le-ky-nang-that/tdd.md` đợt 2: `test_ad2_select_cell.py` 22 failed (`TypeError` do `sample_noun` chưa có), sau khi thêm tham số rỗng 2 failed, 20 passed (chữ nhãn, và 12% khác 13%).
- GREEN (chạy thật): `uv run pytest tests/domain/test_ad2_select_cell.py -q` → 22 passed.

## Đợt #168 (2026-11-17): file dùng chung đổi, AC của issue này không đổi

Lý do: #168 cài `StatMarket.skill_roles` đọc `stat_skill_rates` (số thật cho `skill-roles`), sửa file mà issue này từng đụng: `deploy/compose.prod.yml`, `docs/api/envelope-meta.md`, `haido_api/stat_market.py`, `tests/api/test_ad17_meta_nguon_stat.py`.
Hành vi và AC của issue này không đổi; thay đổi chỉ thêm phương thức `skill_roles` thật và chữ mô tả. RED, GREEN và mutation: `specs/168-ky-nang-vai-tro-that/tdd.md`.

## Đợt #324 (2026-11-19): câu chữ trên màn viết lại

Lý do: #324 viết lại chữ hiển thị bằng tiếng Việt dễ hiểu (bỏ nhãn `n = `, "snapshot", "entry-level"; câu thiếu mẫu "Mới có X tin, cần ít nhất 30"; khung nguồn "Đang xem", "Cập nhật", tên nguồn). File của issue này bị đụng: `web/lib/skill-profile-view.ts`. Số, thứ tự và ẩn số theo ngưỡng không đổi. Hành vi và AC của issue này không đổi.

- RED và GREEN: `specs/324-cau-chu-de-hieu/tdd.md` (RED 42 failed / 299 passed; GREEN 357 passed, chạy `npx vitest run` từ PowerShell).
