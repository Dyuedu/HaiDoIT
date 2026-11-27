# TDD: tỷ lệ kỹ năng thật theo vai trò và cấp (#151)

Theo `docs/templates/test-driven-tdd/test-driven-development.md`. Test API cần Postgres thật (`HAIDO_TEST_DATABASE_URL` trỏ DB `*_test`; trên Windows dùng `127.0.0.1`, không dùng `localhost` vì IPv6 treo kết nối tới Docker). Mỗi test dựng schema `haido` mới bằng `alembic upgrade head`, nạp hàng `stat_*` bằng SQL, gọi route qua `TestClient` với `StatMarket` làm nguồn `skill_rates`.

Lệnh:

```text
uv run pytest tests/api/test_fr19_skill_rates_stat.py tests/deploy/test_gh151_ty_le_ky_nang_doc_snapshot_that.py -q
uv run pytest -q
uv run ruff check
python tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24
```

## Các hành vi (`tests/api/test_fr19_skill_rates_stat.py`, mã FR-19, AD-17, AD-7)

1. Ô đủ mẫu: dòng `core` và `common` (θ 0.3 và 0.1, `>=`), kỹ năng `rare` không có dòng; tỷ lệ giảm dần rồi mã; `display = shown`; `core_size`, `have_core`.
2. Hòa tỷ lệ thì theo mã.
3. AD-17: `meta.cells[cell].n` là `n` của `stat_cells`, `n_by_measure.skill_count` là `n_scanned`, `insufficient_by_measure` khớp; ngày, nguồn, ngưỡng, lưu ý độ phủ.
4. Mã ô: `vn.<vai trò>` ở `all`, `vn.<vai trò>.<cấp>` ở cấp khác.
5. AC 2: cấp thô thiếu mẫu quay về nhóm `entry`; nhãn gọi tên (Backend, Fresher, Entry) và n (26, 52).
6. AC 2 / FR-19: quay về `all` ghi tỷ lệ Mid trở lên của ô `all` (60%), `seniority_mix` của ô trong meta.
7. AD-17: `n` đủ mà `n_scanned < 30` thì ô không được chọn.
8. AC 3: không tập nào đủ: `null_data`, `group = null`, `core_size`/`have_core` `null`, `have` vẫn đúng, nhãn nói chưa đủ 30; dòng là kỹ năng có nhắc theo mã. Ô cuối không kỹ năng nào được nhắc: mọi mã của ô theo mã.
9. `have`: tick dòng, đếm core.
10. 404: vai trò ngoài config; vai trò không có tin (kèm ngày snapshot); chưa có snapshot (không ngày). 422: `level` lạ.
11. Snapshot `open` hoặc thiếu nguồn bị bỏ, lùi về snapshot cũ; `partial` đọc được và ghi trạng thái.
12. AD-7: chỉ đọc `stat_skill_rates` và `stat_cells`, không tổng hợp.
13. Cùng tham số cùng kết quả.

Deploy (`tests/deploy/test_gh151_ty_le_ky_nang_doc_snapshot_that.py`): prod `stat`, local `fake`. (AC 4)

## RED

Chạy 2026-11-17, sau khi viết test, trước khi viết code:

- `uv run pytest tests/api/test_fr19_skill_rates_stat.py -q` → 14 failed, 3 passed. Cả 14 đỏ cùng lý do: 404 `unknown_cell` "Tỷ lệ kỹ năng chưa có số liệu thật." vì `StatMarket.skill_rates` còn `raise UnknownCell`. 3 test xanh sẵn là các ô chỉ cần 404/422 (vai trò ngoài config, chưa có snapshot, `level` lạ): `StatMarket` cũ đã cho đúng mã lỗi.
- `uv run pytest tests/deploy/test_gh151_ty_le_ky_nang_doc_snapshot_that.py -q` → 1 failed, 1 passed (prod chưa đặt `stat`; local đã giữ `fake`).
- Ô cuối không kỹ năng nào được nhắc (phát hiện khi đối chiếu với web, `rows` rỗng làm `isSkillRatesEnvelope` từ chối): test viết thêm sau, chạy trước khi sửa → 1 failed: `assert [] == ['git', 'python']`.

## GREEN

- Sau khi viết `StatMarket.skill_rates`: 16 passed, 1 failed. Test đỏ là lỗi của test: trạng thái snapshot `draft` vi phạm `ck_snapshots_status` (chỉ `open`, `published`, `partial`); đổi sang `open`.
- Sau khi sửa dòng khi không kỹ năng nào được nhắc: `uv run pytest tests/api/test_fr19_skill_rates_stat.py tests/api/test_ad17_meta_nguon_stat.py tests/domain -q` → 415 passed.
- Toàn bộ: xem dòng cuối dưới đây.

## Web

Web không đổi. Response thật khớp `isSkillRatesEnvelope` (`web/lib/skill-rates.ts`): `data.cell_id` có trong `meta.cells` với `n` và `fallback_label` kiểu chuỗi hoặc `null`; mọi `rate.cell_id` bằng `data.cell_id`; `display = shown` đi với `group` là `core` hoặc `common`, `null_data` đi với `value = null` và `group = null`; `rows` không rỗng (nên dòng `null_data` luôn có ít nhất một dòng). Điều kiện chưa kiểm được ở dữ liệu thật: ô đủ mẫu mà mọi kỹ năng là `rare` cho `rows` rỗng.

## GREEN toàn bộ (2026-11-17)

- `uv run pytest -q` (Postgres thật, DB `fx151_test`, không skip) → 1580 passed.
- `uv run ruff check` → All checks passed.
- `python tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` → 10 pass, 0 skip, 0 fail.
- Web (không đổi mã): `cd web && npx vitest run` → 298 passed; `npx tsc --noEmit` và `npm run lint` sạch. Kiểm thêm bằng một test tạm (đã xóa): hai response thật (ô quay về nhóm có `have`, và ô `null_data`) qua `fetchSkillRates` đều ra `kind: "ok"`.

## Đợt 2 (2026-11-17): sửa theo review

Lý do: review chỉ ra (1) ô có trong `stat_cells` mà không có hàng tỷ lệ trả "có 0 tin" và dòng rỗng; ô đủ mẫu mà mọi kỹ năng hiếm cho `rows = []` làm web báo hỏng; (2) `_skill_cell_stats` chọn ngầm một `n_scanned` khi các hàng khác nhau; (3) nhãn không nói con số là số tin đọc được kỹ năng; (4) tỷ lệ Mid trở lên dùng `round` của Python (nửa về chẵn); (5) test nhãn chỉ kiểm chuỗi con; (6) route chưa có số thật chấp nhận cả 500; (7) kiểm SQL của AD-7 chỉ phủ đường đủ mẫu. AC không đổi; thêm scenario 9, 10, 11 ở `spec.md`.

Lệnh:

```text
uv run pytest tests/domain/test_ad2_select_cell.py tests/api/test_fr19_skill_rates_stat.py tests/api/test_ad17_meta_nguon_stat.py -q
cd web && npx vitest run tests/fr19-skill-profile.test.tsx
```

Hành vi thêm hoặc siết: nhãn đúng từng chữ (quay về nhóm, quay về `all` kèm Mid trở lên, không tập nào đủ); ô không hàng tỷ lệ là 404 kèm ngày; ô đủ mẫu mọi kỹ năng hiếm là `rows = []`, `core_size = 0`; `n_scanned` khác nhau là `RuntimeError`; AD-7 chạy qua đường đủ mẫu, quay về, không tập nào đủ và hai đường 404, cấm thêm `max(`, `min(`, `having`; web đọc được `rows` rỗng khi `core_size = 0` và hiện câu giải thích, vẫn coi rỗng với `core_size = null` hoặc khác 0 là hỏng.

RED (chạy thật, 2026-11-17, Postgres thật `fx151b_test`):

- `tests/domain/test_ad2_select_cell.py`: lần đầu 22 failed vì `CellSelector` chưa nhận `sample_noun` (`TypeError`, lỗi chỗ gọi, che hành vi). Thêm tham số rỗng rồi chạy lại: 2 failed, 20 passed. Hai đỏ đúng lý do: nhãn thiếu "đọc được kỹ năng", và `12% != 13%` (`round(12.5)` là 12). 20 test xanh gồm các test nhãn viết lại đúng từng chữ, khớp chữ cũ.
- `tests/api/test_fr19_skill_rates_stat.py` + `test_ad17_meta_nguon_stat.py`: 5 failed, 19 passed. Ba đỏ vì chữ nhãn (cùng lý do trên); `assert 200 == 404` ở ô không hàng tỷ lệ; `DID NOT RAISE RuntimeError` ở `n_scanned` khác nhau. Xanh sẵn: ô đủ mẫu mọi kỹ năng hiếm (code đã đúng, test khóa lại), AD-7 mở rộng, và route chưa có số thật đã trả 404 `unknown_cell` (chỉ siết điều kiện, không có RED riêng).
- `web/tests/fr19-skill-profile.test.tsx`: 2 failed, 23 passed: `isSkillRatesEnvelope` từ chối `rows` rỗng; màn hiện lỗi thay cho câu giải thích. Hai test "vẫn hỏng khi `core_size` là `null` hoặc 2" xanh sẵn.

Mutation cho AD-7 và AD-17 (tạm sửa `haido_api/stat_market.py`, chạy `test_fr19_skill_rates_stat.py` + `test_ad17_meta_nguon_stat.py`, rồi khôi phục; `git diff haido_api/stat_market.py | sha256sum` trước và sau đều `d2e27ad8924f3ba373d5ede7f9a4eb66036fa19ee39bc59f9e1c90783029bf08`, `cmp` với bản sao gốc giống hệt):

- A, `sample_n=None` trong `_skill_cell_stats` (quyết định theo `n` thay vì `n_scanned`): 6 failed, 18 passed. Đỏ ở `n_by_measure.skill_count` (80 thay 60, 80 thay 52), nhãn ghi 100 thay 90, `cell_id` `vn.backend.entry` thay `vn.backend`, và ô `null_data` thành `shown`.
- B, thêm `SELECT count(*) FROM haido.job_postings` vào `_skill_cell_stats`: 2 failed, 22 passed. Hai test AD-7 đỏ ở `assert 'job_' not in sql`.

GREEN (sau khi sửa code và web):

- `uv run pytest tests/domain tests/api/test_fr19_skill_rates_stat.py tests/api/test_ad17_meta_nguon_stat.py -q` → 421 passed.
- Web: `npx vitest run` → 22 files, 302 passed; `npx tsc --noEmit` và `npm run lint` sạch.
- Toàn bộ: `uv run pytest -q` (Postgres thật, DB `fx151b_test`, không skip) → 1586 passed; `uv run ruff check` → All checks passed; `check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` → 10 pass, 0 skip, 0 fail.

## Đợt #168 (2026-11-17): file dùng chung đổi, AC của issue này không đổi

Lý do: #168 cài `StatMarket.skill_roles` đọc `stat_skill_rates` (số thật cho `skill-roles`), sửa file mà issue này từng đụng: `deploy/compose.prod.yml`, `docs/api/envelope-meta.md`, `haido_api/stat_market.py`, `tests/api/test_ad17_meta_nguon_stat.py`.
Hành vi và AC của issue này không đổi; thay đổi chỉ thêm phương thức `skill_roles` thật và chữ mô tả. RED, GREEN và mutation: `specs/168-ky-nang-vai-tro-that/tdd.md`.

## Đợt #324 (2026-11-19): câu chữ trên màn viết lại

Lý do: #324 viết lại chữ hiển thị bằng tiếng Việt dễ hiểu (bỏ nhãn `n = `, "snapshot", "entry-level"; câu thiếu mẫu "Mới có X tin, cần ít nhất 30"; khung nguồn "Đang xem", "Cập nhật", tên nguồn). File của issue này bị đụng: `web/lib/skill-profile-view.ts`. Số, thứ tự và ẩn số theo ngưỡng không đổi. Hành vi và AC của issue này không đổi.

- RED và GREEN: `specs/324-cau-chu-de-hieu/tdd.md` (RED 42 failed / 299 passed; GREEN 357 passed, chạy `npx vitest run` từ PowerShell).

## Đợt #102 (2026-11-19): θ có phiên bản, AC của issue này không đổi

Lý do: #102 đóng băng θ (`config/theta.toml`, `theta-1` = 0,3/0,1), thêm `snapshots.theta_version` (migration 0010) và `meta.thresholds.theta_version`, sửa file mà issue này từng đụng: `docs/api/envelope-meta.md`, `haido_api/stat_market.py`, `tests/api/test_fr19_skill_rates_stat.py`.
Giá trị θ không đổi nên số, nhóm và hành vi của issue này không đổi; test chỉ thêm `theta_version` vào ngưỡng hoặc đổi head migration mong đợi sang 0010. RED, GREEN và đột biến: `specs/102-dong-bang-theta/tdd.md`.

## Đợt #327, #328 (2026-11-19): thêm route toàn cảnh thị trường, AC của issue này không đổi

Lý do: #327 và #328 thêm `GET /api/v1/market-overview` và sửa file mà issue này từng đụng (`haido_api/schemas/market.py`, `fake_market.py`, `market_source.py`, `routes/market.py`, `stat_market.py`, `fixtures/fake_market.json`, `docs/api/envelope-meta.md`, `tests/api/test_ad17_routes.py`). Thay đổi chỉ thêm: schema, phương thức, route, một mục fixture, một dòng `SAMPLE_QUERY`; route cũ và số của chúng không đổi.

- RED và GREEN: `specs/327-tong-quan-thi-truong-api/tdd.md`. `uv run pytest -q` → 1336 passed, 304 skipped.

## Đợt #217 (2026-11-25): `learningPathHref` nhận `skill` tùy chọn

Lý do: màn lộ trình (#217) dựng URL không có kỹ năng. File bị đụng: `web/lib/skill-profile-view.ts` (chỉ `learningPathHref` và chú thích). Hành vi, AC và câu chữ của issue này không đổi.

RED và GREEN: `specs/217-man-lo-trinh/tdd.md` (`npx vitest run` → 432 passed).

## Đợt #217 (2026-11-25): lộ trình học thành chủ đề

Lý do: sửa file mà issue này từng đụng (trong số `fake_market.py`, `docs/api/openapi.json`, `docs/api/envelope-meta.md`, `tools/gates/check_gates.py`, `web/lib/learning-path.ts`, test lộ trình): chỉ phần lộ trình học. Hành vi và AC của issue này không đổi.

RED và GREEN: `specs/217-man-lo-trinh/tdd.md` đợt 4.

## Đợt #216 (2026-11-25): lộ trình thật trong StatMarket

Lý do: sửa file mà issue này từng đụng (trong số `stat_market.py`, `check_gates.py`, `envelope-meta.md`, `compose.prod.yml`, test lộ trình): chỉ phần lộ trình học. Hành vi và AC của issue này không đổi.

RED và GREEN: `specs/216-lo-trinh-that/tdd.md`.

## Đợt sửa 2026-11-27 (#230, hình tin dán "Soi tin")

**Vì sao sửa**: #230 thêm nguồn `posting_check` vào `SOURCE_ENV`, bảng `[posting_match]` vào `config/rules.toml`, ô `vn.backend.junior` vào
`fake_market.json`, route `posting-reads` và `posting-check`. Các file của issue này bị chạm: `deploy/compose.prod.yml`, `docs/api/envelope-meta.md`, `haido_api/routes/market.py`, `haido_api/stat_market.py`, `tests/api/test_ad17_meta_nguon_stat.py`, `tests/api/test_fr19_skill_rates_stat.py`.

**Hành vi của issue này**: không đổi; không AC nào của #151 đúng khác đi. Mọi thay đổi chỉ cộng thêm (khóa nguồn mới, mục cấu hình mới, ô và hàng
fixture mới, hàng tài liệu mới, nguồn `posting_check` trong các lời gọi `create_app` của test).

**RED/GREEN**: RED (chạy thật): trả 13 file test cũ dựng create_app với năm nguồn về bản ở HEAD rồi chạy với code mới thì 109 failed, 54 lỗi, 32 passed (thiếu nguồn posting_check). GREEN: sau khi thêm nguồn và sửa các file, uv run pytest -q toàn bộ được 2029 passed (không còn test nào đỏ của issue này). Chi tiết ở specs/230-hinh-soi-tin/tdd.md.
