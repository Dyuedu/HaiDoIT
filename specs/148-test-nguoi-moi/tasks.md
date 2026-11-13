# Tasks: Test danh sách người mới

**Input**: `specs/148-test-nguoi-moi/`

**Tests**: Viết trước theo `tdd.md`. Test mới khóa hành vi đã có thì không có RED; chứng minh bằng đột biến.

## Phase 1: Test

- [x] T001 Test G1 web: dòng `null_data` sau mọi dòng `shown` theo thứ tự DOM, trong `web/tests/fr37-newcomer-list.test.tsx`
- [x] T002 Test G2 web: dòng `shown` theo thứ tự máy chủ, số entry giảm nghiêm ngặt
- [x] T003 Test G3: DEC-6 đọc mọi tiêu đề, đoạn văn, liên kết của `/insights` và trang giữ chỗ
- [x] T004 Test G4: `role=all` ở trang giữ chỗ
- [x] T005 Test G1, G2 API: thứ tự bất biến trong `tests/api/test_fr37_newcomer_roles_stat.py`
- [x] T006 Test G5: entry > n, viết trước, chạy thấy đỏ (3 failed)

## Phase 2: Implementation

- [x] T007 Bảo vệ entry > n trong `StatMarket.newcomer_roles` (`haido_api/stat_market.py`)
- [x] T008 Đột biến web: web sắp lại dòng, chữ số trong h2 và h1, `role=all` hợp lệ; ghi vào `tdd.md`, hoàn lại
- [x] T009 Đột biến API: bỏ khóa `null_data`, đảo dấu số entry, bỏ khóa mã; ghi vào `tdd.md`, hoàn lại
- [x] T010 Ghi chú ngày và đợt TDD mới ở `specs/144`, `145`, `146`, `147`, `163`, `280`

## Phase 3: Kiểm

- [x] T011 pytest đầy đủ, determinism hai seed, ruff, cổng, lint, vitest, build

## Đợt 2 — 2026-11-13 — sửa theo review

- [x] T012 F1: test web duyệt MỌI dòng (số tin entry, n, tỷ lệ, nhãn "số tin của vai trò"); đột biến, hoàn lại
- [x] T013 F2: test API nhiều vai trò, tỷ lệ = entry / n riêng; gộp test thứ tự đợt 1 vào đó; đột biến mẫu số, hoàn lại
- [x] T014 F3: `narrative()` duyệt mọi nút chữ và thuộc tính, loại region thật, năm trạng thái `/insights`, trang giữ chỗ, đổi tên `ad8`; sửa "8 nguồn" và scenario 5; đột biến, hoàn lại
- [x] T015 F4: biên n = 30 `shown`, n = 29 `null_data`; đột biến `min_sample + 1`, hoàn lại
- [x] T016 F5: `_set_entry_n` kiểm `rowcount == 1`
- [x] T017 F6: sửa `plan.md` (issue cũ #93, #162, #259, #263), ghi điểm mở ngoài phạm vi
- [x] T018 Kiểm: pytest đầy đủ trên DB riêng, determinism hai seed, ruff, cổng, lint, vitest, build
