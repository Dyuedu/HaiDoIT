# TDD: tỷ lệ kỹ năng theo vai trò, số thật (#168)

Theo `docs/templates/test-driven-tdd/test-driven-development.md`. Test API cần Postgres thật (`HAIDO_TEST_DATABASE_URL` trỏ DB `*_test`, host `127.0.0.1`). Mỗi test dựng schema `haido` bằng `alembic upgrade head`, nạp hàng `stat_*` bằng SQL (`_snapshot`, `_cell` của `test_fr19_skill_rates_stat.py`), gọi route qua `TestClient` với `StatMarket` làm nguồn `skill_roles`.

Lệnh:

```text
uv run pytest tests/api/test_fr09_skill_roles_stat.py tests/api/test_ad17_meta_nguon_stat.py tests/api/test_fr09_skill_roles.py tests/deploy/test_gh166_ky_nang_vai_tro_doc_snapshot_that.py -q
uv run pytest -q
uv run ruff check .
python tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24
```

## Các hành vi (`tests/api/test_fr09_skill_roles_stat.py`)

1. AC 1: dòng `shown` theo tỷ lệ giảm dần rồi mã; `null_data` sau; kind, nhãn kỹ năng, `level`, `levels`.
2. AC 2: dưới 30 là `null_data`; X là `skill_count` ở meta và dòng theo X giảm dần rồi mã.
3. AC 2: `n` đủ mà `n_scanned` dưới 30 là `null_data`, X = `n_scanned`.
4. Vai trò không có ô entry: dòng `null_data`, `n = 0`, `skill_count = 0`.
5. Đủ mẫu, 0 tin nhắc: `value = 0`, `shown`.
6. Meta ô entry: `n`, `seniority_mix`, nguồn, ngưỡng, lưu ý độ phủ, đủ 17 ô.
7. Chỉ dùng hàng của kỹ năng đã chọn (python và java ở cùng ô cho tỷ lệ khác nhau).
8. `mentioned`: true khi chỉ cấp khác entry nhắc; false khi `n_with = 0` ở ô mọi vai trò, mọi cấp.
9. 404 `unknown_cell` kèm ngày khi snapshot không có hàng kỹ năng; 404 không ngày khi chưa có snapshot; 404 `unknown_skill`; 422 sai định dạng.
10. Chọn snapshot: bỏ `open` và cũ, lấy mới nhất; `partial` đọc được.
11. `n_scanned > n`: 500 và `RuntimeError` nêu snapshot và vai trò.
12. AD-7: SQL không `job_*`, không `count(`, `sum(`, `avg(`, `group by`.
13. Cùng tham số cùng kết quả; response qua `Envelope[SkillRolesData]`.
14. `test_ad17_meta_nguon_stat.py`: `/api/v1/skill-roles` ở REAL trả `{data, meta}`.
15. `test_fr09_skill_roles.py`: `StatMarket` không mở kết nối lúc dựng (thay test "stat luôn 404").

Deploy: không thêm `test_gh168_*`. `test_gh309_*` sinh từ `SOURCE_ENV` kiểm prod `stat`, `StatMarket` dựng được và local `fake` cho mọi nguồn, `test_gh166_*` kiểm riêng biến này; thêm một file sẽ chỉ lặp lại.

## RED

Chạy 2026-11-17, sau khi viết test, trước khi viết code, `StatMarket.skill_roles` còn `raise UnknownCell`:

- Bốn file test của lệnh đầu → 17 failed, 73 passed. 16 đỏ ở `test_fr09_skill_roles_stat.py` và 1 ở `test_ad17_meta_nguon_stat.py::test_ad17_103_moi_route_co_so_nguon_stat_tra_data_va_meta`, cùng lý do: 404 `unknown_cell` "chưa có số liệu thật". 2 test mới xanh sẵn: chưa có snapshot (404 không ngày) và `unknown_skill`/422, vì route đã trả đúng mã lỗi.

## GREEN

- Sau khi viết `skill_roles`: 89 passed, 1 failed. Test đỏ là lỗi của test: regex đặt vai trò trước ngày trong khi thông báo ghi ngày snapshot trước; sửa regex.
- Sau đó `test_fr09_skill_roles_stat.py` 18 passed; cùng bốn file: 90 passed.
- Toàn bộ (Postgres thật `haido_test`, không skip): `uv run pytest -q` → 1615 passed (495 s). `uv run ruff check .` → All checks passed. Cổng → 10 pass, 0 skip, 0 fail.

## Mutation (tạm sửa `haido_api/stat_market.py`, chạy `test_fr09_skill_roles_stat.py` + `test_ad17_meta_nguon_stat.py`, khôi phục, `diff` với bản sao giống hệt)

- M1, bỏ khóa cỡ mẫu của dòng `null_data` (thay bằng 0): 8 failed, 12 passed (500 vì `Envelope` từ chối thứ tự; test thứ tự và SQL đỏ).
- M2, `mentioned` tính từ các dòng entry thay vì hàng `all`: 1 failed (`mentioned_true_khi_chi_cap_khac_entry_nhac`).
- M3, `display` theo `n` của ô thay vì `n_scanned`: 9 failed (kể cả `test_ad17_103_*`).
- M4 và M5, bỏ lọc kỹ năng khỏi truy vấn: 2 failed mỗi lần (`chi_dung_hang_cua_ky_nang_da_chon`, `ky_nang_khong_co_hang_..._404`).

## Đợt 2026-11-17: file dùng chung đổi

`haido_api/stat_market.py`, `deploy/compose.prod.yml`, `docs/api/envelope-meta.md`, `tests/api/test_ad17_meta_nguon_stat.py`, `tests/api/test_fr09_skill_roles.py` và `tests/deploy/test_gh166_*` thuộc các issue có `specs/`: #103, #106, #144, #145, #146, #148, #149, #150, #151, #163, #166, #205, #212, #262, #273, #280, #309. Mỗi `tdd.md` thêm một đợt ngắn. Đổi chữ thật ở hai chỗ, không AC nào của issue sai đi:

- `specs/166-*/spec.md` (US3 kịch bản 1) và `plan.md`, `tasks.md` (T015): "stat luôn 404" là trạng thái chuyển tiếp ghi rõ "đến #168".
- `specs/103-*/spec.md` (US1 kịch bản 1, 2): `skill-roles` chuyển từ nhóm "chưa có số thật" sang nhóm có `{data, meta}`; AC 1 của #103 (mọi response có số đều có meta) vẫn đúng.

Issue cũ chưa có `specs/` mà từng đụng các file này, cần ghi trong mô tả PR: #1, #2, #93, #140, #162, #259, #263.

## Đợt review 2026-11-17

Lý do: review chỉ ra các mutation còn sống và vài chỗ test rỗng. Danh sách issue liên quan ở đợt trên suy ra từ dòng tiêu đề commit (`git log --format='%h %s'`, số `#N`) và tìm đường dẫn file trong `specs/*/plan.md`, `tasks.md`; không đọc thân commit.

Lệnh: `uv run pytest tests/api/test_fr09_skill_roles_stat.py tests/api/test_fr09_skill_roles.py -q` (Postgres thật `haido_test`).

### Hành vi

1. Hòa tỷ lệ giữa các dòng `shown` thì chỉ mã vai trò quyết (fixture: `frontend` hòa `backend` ở 0.5 nhưng `n_scanned` 80 so với 60).
2. `mentioned` chỉ lấy từ hàng `role = all`, `seniority = all`; hàng `all × entry` (n_with = 0) không ảnh hưởng, cả khi `mentioned` đúng lẫn sai.
3. `StatMarket(engine_factory=...)`: factory đếm lần gọi, 0 lần sau khi dựng, đúng 1 lần ở `skill_roles(skill="python")`.
4. `skill_roles` mã ngoài bộ từ vựng: `UnknownSkill` trước khi mở kết nối (factory không được gọi).
5. Guard: vai trò có `n_with > 0` ở entry mà `all × all` có `n_with = 0`: `RuntimeError` nêu snapshot, kỹ năng, vai trò.
6. Biên: `n_scanned = min_sample` là `shown` có giá trị; `min_sample - 1` là `null_data`.
7. Số dòng `null_data` suy từ `len(ROLES) - 4`; đuôi 0 mẫu theo mã.
8. Snapshot mới không có `stat_sources` bị bỏ; `sources_failed` của snapshot `partial` đi qua `meta`.
9. Khóa sắp xếp dùng `display is NULL_DATA` nhất quán (sửa dọn, hành vi không đổi).

### RED

Test đợt này viết cùng lúc với sửa code, nên phần lớn xanh ngay trên code mới. Bằng chứng đỏ là chạy test với mutant (tạm sửa `haido_api/stat_market.py`, chạy hai file test, khôi phục, `cmp` với bản sao):

- A, khóa `null_data` theo `n_scanned` áp cho cả dòng `shown`: 8 failed, 83 passed (gồm `ac1_xep_theo_ty_le...`, nay đỏ nhờ fixture hòa tỷ lệ).
- B1, `mentioned` lấy từ mọi hàng `role = all`: 1 failed (`mentioned_chi_lay_tu_hang_all_x_all...`), 90 passed. B2, `mentioned` lấy từ hàng `all × entry`: 18 failed (mutant làm hỏng cả nguồn của mọi test `mentioned`). Mutant trước review (cùng loại B1) còn sống ở bộ test cũ.
- C, bỏ guard `n_with`: 1 failed (`vai_tro_co_n_with_o_entry...`), 90 passed.
- D, `display` tính trên `n_scanned - 1` (lệch biên): 18 failed, trong đó có test biên mới.
- E, `sources_failed = []`: 1 failed (`snapshot_partial...`), 90 passed.
- F, kiểm `UnknownSkill` đặt sau khi mở kết nối: 1 failed (`stat_ma_ngoai_bo_tu_vung...truoc_khi_mo_ket_noi`), 90 passed.
- G, bỏ điều kiện `has_sources` khỏi `_latest_with_skill_rates`: 1 failed (`bo_snapshot_moi_khong_co_stat_sources`), 90 passed.

Chưa chạy mutant cho hành vi 3 (factory gọi trong `__init__`) và 7; hành vi 3 thay test cũ chỉ dựng nguồn mà không gọi, nay có hai khẳng định số lần gọi. Mutant A của đợt trước (bỏ thứ tự theo cỡ mẫu) vẫn đỏ ở test thứ tự.

### GREEN

- Hai file test: 91 passed.
- Toàn bộ `uv run pytest -q`: 1620 passed (534 s), tăng 5 so với 1615 (5 test mới: biên, `mentioned` không lấy `all × entry`, snapshot không có nguồn, guard `n_with`, `UnknownSkill` trước kết nối). `uv run ruff check .` sạch. Cổng: 10 pass, 0 skip, 0 fail.

## Đợt sửa câu chữ AC (2026-11-19)

Lý do: AC 2 của #168 và AC 3 của #113 ghi "under 30 entry-level postings", còn code (theo #166) dùng số tin đọc được kỹ năng (`n_scanned`, `skill_count`). Người dùng chọn sửa câu chữ AC theo code. Code và test không đổi, nên không có RED mới; GREEN chạy lại sau khi merge `origin/main` (ghi bên dưới).

- GREEN sau merge `origin/main` (66c8087): `uv run pytest -q` → 1627 passed; `ruff check .` sạch; `tools/gates/check_gates.py` → 10 pass. PR này không đổi file web.

## Đợt #327, #328 (2026-11-19): thêm route toàn cảnh thị trường, AC của issue này không đổi

Lý do: #327 và #328 thêm `GET /api/v1/market-overview` và sửa file mà issue này từng đụng (`haido_api/schemas/market.py`, `fake_market.py`, `market_source.py`, `routes/market.py`, `stat_market.py`, `fixtures/fake_market.json`, `docs/api/envelope-meta.md`, `tests/api/test_ad17_routes.py`). Thay đổi chỉ thêm: schema, phương thức, route, một mục fixture, một dòng `SAMPLE_QUERY`; route cũ và số của chúng không đổi.

- RED và GREEN: `specs/327-tong-quan-thi-truong-api/tdd.md`. `uv run pytest -q` → 1336 passed, 304 skipped.
