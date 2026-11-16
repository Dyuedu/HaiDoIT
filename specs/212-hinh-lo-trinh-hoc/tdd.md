# TDD: Hình response của lộ trình học và dữ liệu giả

Theo `docs/templates/test-driven-tdd/test-driven-development.md`.

Mỗi test một hành vi. Test Python không mạng, chạy API qua `TestClient` với nguồn giả. Test web đọc fixture JSON và stub `fetch`.

Lệnh:

```text
HAIDO_TEST_DATABASE_URL=postgresql+psycopg://haido:haido_local@127.0.0.1:5433/haido_test uv run pytest -q
PYTHONHASHSEED=0 uv run pytest -q -m determinism   (và PYTHONHASHSEED=1)
cd web && npx vitest run tests/fr22-learning-path-fixture.test.ts
```

## Các hành vi

1. Hình response: đủ trường, chặng đánh số 1..k, 3 chặng trở lên, 12–16 kỹ năng, `rate` thuộc `data.cell_id`, link `https://`.
2. Thứ tự trong chặng theo FR-22; một chặng có cả cốt lõi và thường gặp; không kỹ năng nào đứng trước tổ tiên.
3. Kỹ năng nền tảng (FR-20); nhóm khớp θ của `thresholds`.
4. Tỷ lệ và nhóm của lộ trình bằng `skill-rates` cùng vai trò, cấp, ô (backend, data_engineer).
5. `have`: cờ, `have_on_path`, `path_size`, không đổi thứ tự, `current_stage`, `have_ignored`, mã trùng, `have` rỗng, trần 200 mã (201 là 422), mã sai định dạng và phần tử rỗng là 422, mặc định `level = entry`.
6. `not_ready` (qa, ai_ml ở cấp senior), quay về ô có `entry_cell_id` (data_engineer), backend không quay về, cấp khác là 404, vai trò lạ là 404, tham số sai là 422.
7. Tất định: cùng yêu cầu hai lần cho cùng body (`determinism`).
8. Dữ liệu giả: tập vai trò khớp config; mọi mã `skill-rates` và `learning-path` giả là snake_case và thuộc `skills_seed.json`; lời dẫn không số ngoài tên công nghệ, không `%`, không khuyên bỏ kỹ năng.
9. Nguồn: `FakeMarket` ném `UnknownCell` kèm ngày; `StatMarket` ném `UnknownCell`, không mở kết nối.
10. Validator `LearningPathData` từ chối 30 ca sai (rate khác ô, chặng không liền, sai thứ tự, mã lặp, tham chiếu lạ, kỹ năng ở chặng không sau, riêng công ty không nền tảng, đếm sai, `current_stage` sai, `not_ready` có chặng, trường lạ...).
11. Route có trong `SAMPLE_QUERY` và danh sách kiểm `display` của AD-17; `create_app` cần nguồn `learning_path`.
12. Fixture web giống hệt response (bốn fixture); web: kiểu, `learningPathUrl` (cắt ở 200 mã), `fetchLearningPath` (ok, lỗi, unreadable).

## RED (2026-11-12)

- `uv run pytest -q tests/api/test_fr22_learning_path.py` → 1 error lúc thu thập: `ModuleNotFoundError: No module named 'haido_api.schemas.learning_path'`.
- `uv run pytest -q tests --ignore=tests/api/test_fr22_learning_path.py` → 8 failed, 714 passed: `test_ad17_moi_route_tra_envelope` (route chưa có), ba ca `test_ad17_display_chi_do_suppression_for_quyet[/api/v1/learning-path]` (404) và bốn ca `test_ad17_fixture_web_khop_response_learning_path` (404 và thiếu fixture).
- `npx vitest run tests/fr22-learning-path-fixture.test.ts` → 1 file failed: không import được `@/lib/learning-path` và fixture.

## GREEN

Lần sửa đầu (schema, nguồn giả, route) còn hai lỗi do chính thiết kế, sửa rồi chạy lại:

- `Envelope` từ chối `stage`, `current_stage`, `have_on_path`, `path_size` vì AD-17 cấm số đứng riêng ngoài `Stat` (500 `invalid_response`, 12 error + 12 failed). Thêm dấu `Ordinal` ở `haido_core/domain/envelope.py` cho số thứ tự và số đếm của response; số liệu thị trường vẫn là `Stat`.
- Test trần 200 mã dùng danh sách mồi chỉ có 100 mã, và một regex hoa thường; sửa test.

Kết quả:

- `uv run pytest -q tests/api/test_fr22_learning_path.py` → 75 passed.
- `uv run pytest -q` (có Postgres) → 797 passed, không skip.
- `-m determinism` với `PYTHONHASHSEED=0` và `1` → 7 passed mỗi lượt.
- `uv run ruff check .` sạch; `check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11` → 8 pass, 2 skip, 0 fail.
- Web: `npx vitest run` → 159 passed (file mới 10 passed); `npm run lint` sạch; `npm run build` thành công.

## Đợt 2 — 2026-11-12 — sửa theo review

Lý do: review của #212 tìm 15 điểm (F1–F15). Đợt 1 giữ nguyên ở trên. Quy trình: viết test trước, chạy đỏ, sửa code, chạy xanh.

Lệnh (thêm so với đợt 1):

```text
HAIDO_TEST_DATABASE_URL=postgresql+psycopg://haido:haido_local@127.0.0.1:5433/haido_test uv run pytest -q --continue-on-collection-errors
cd web && npx vitest run tests/fr22-learning-path-fixture.test.ts
```

### Các hành vi thêm

1. F1: quét mọi vai trò của `config/rules.toml` × mọi `LevelCode`, có và không có `have`: chỉ 200 hoặc 404, mọi 200 giữ các điều kiện; `data_engineer` ở `senior` là 404 (trước là 500, `KeyError: 'git'`); bản giả chỉ ném `UnknownCell`.
2. F2: `cell_id` luôn thuộc vai trò đã chọn (FR-19); `data_engineer` entry: mọi `rate` `null_data`, `group = null`, `cell_id = vn.data_engineer`, nhãn nói 4, 22 và 30; `backend` intern quay về `vn.backend`, nhãn ghi số tin Mid trở lên và tỷ lệ tính từ `seniority_mix`; `skill-rates` cùng (vai trò, cấp) khớp lộ trình.
3. F3: `Ordinal` int được nhận, âm bị từ chối, `bool`, `float` bị chặn, kiểu ghép (`tuple[Ordinal, float]`, `list[Stat] | Ordinal`) không được miễn; danh sách trường `Ordinal` của mọi route bằng đúng 4 trường.
4. F4: mọi kỹ năng `core`/`common` của ô tỷ lệ có trên lộ trình; kỹ năng nhóm khác có `foundation_for` không rỗng.
5. F5: `foundation_for` bắc cầu (chuỗi hai bước A → B → C cho `foundation_for` của A chứa C) ở hàm thuần và ở validator; validator từ chối mã không đi tới được qua `prerequisite_for`, hoặc không thuộc `core`/`common`.
6. F6: `ai_ml` entry `not_ready` mà `skill-rates` trả 200; `qa` `not_ready` mà `skill-rates` trả 404; fixture web cho cả hai.
7. F7: một hàm kiểm lời dẫn ở `haido_core/vocab/prepared_text.py` (che tên công nghệ nguyên từ, mọi chữ số khác và `%` bị bắt), quét `blurb` và `resource.title` của mọi kỹ năng; lời dẫn không nói tần suất; tài nguyên không dùng host đã bỏ.
8. F8: `learningPathUrl` bỏ trùng giữ thứ tự gặp đầu, bỏ mã sai định dạng, rồi cắt 200; `fetchLearningPath` không thử lại với 422 `invalid_query`.
9. F9: 150 mã khác nhau cộng 51 mã lặp (201 mã thô) là 422; `have` lặp chỉ đọc cái cuối; mô tả OpenAPI nói điều đó và nói URL khoảng 8 KB.
10. F10: ví dụ FR-24 (Backend → Data Engineer, hồ sơ {java, sql, git}): `have_on_path = 2` trên 11, `java` ở `have_ignored`; fixture web `learning-path-data_engineer-have.json`.
11. F11: mọi `requires` của fixture là nút có thật và đồ thị không chu trình; `stage_numbers` ném `PathGraphError` (mã không có nút, chu trình, tự trỏ), đồ thị 3000 nút không vỡ stack.

### RED (2026-11-12)

- `uv run pytest -q --continue-on-collection-errors` → **23 failed, 803 passed, 3 errors lúc thu thập**:
  - 3 lỗi thu thập: `test_fr22_learning_path_graph.py` (`ImportError: cannot import name 'PathGraphError'`), `test_fr23_blurbs.py` và `test_fr23_prepared_text.py` (`ModuleNotFoundError: haido_core.vocab.prepared_text`).
  - `tests/domain/test_ad17_ordinal.py`: 5 failed (tuple có float, union với `Ordinal` mang `Stat` sai ô, `bool`, âm và float qua `_walk` đều lọt vì `_walk` bỏ cả trường hễ thấy `OrdinalRef`). Ba ca còn lại của file (int được nhận, âm bị từ chối ở schema, `cell_id` vẫn bị kiểm) xanh ngay: chống lùi.
  - `tests/api/test_fr22_learning_path_review.py`: 10 failed. Sáu ca do cùng một lỗi 500 `KeyError: 'git'` ở `data_engineer`/`senior` khi các test duyệt mọi cấp: hai lượt quét, `data_engineer` senior, `FakeMarket` ném `KeyError` thay vì `UnknownCell`, `cell_id` thuộc vai trò, và hai test nhóm-và-lộ-trình (F4) duyệt mọi ô. Ba ca khác: `skill_rates` của `data_engineer` entry trỏ `vn.all.entry` (sai vai trò), `linux` không bắc cầu (`foundation_for` chỉ có `docker`), mô tả `have` thiếu "cái cuối" và "8 KB".
  - `tests/api/test_fr22_learning_path.py`: 3 failed (`backend` intern 404; `data_engineer` entry vẫn `vn.all.entry` có số; ô `intern` chưa có).
  - `tests/api/test_ad17_routes.py`: 1 failed (`learning-path` intern 404). `tests/api/test_ad17_web_fixtures.py`: 3 failed (thiếu `learning-path-backend.intern.json`, `-data_engineer-have.json`, `-ai_ml.json`).
  - Test chặn danh sách trường `Ordinal` đầu tiên đỏ vì lỗi của chính test (`app.routes` của FastAPI mới chỉ có `_IncludedRouter`, không thấy `response_model`): sửa test để duyệt `market.router` và `skills.router`. Sau đó nó xanh ngay trên mã cũ vì tập trường hiện tại đúng bằng 4: đây là test khóa chống lùi, không phải RED.
  - Các test thêm khác xanh ngay trên mã cũ (chống lùi, không phải RED): F9 trần 201 mã thô và `have` lặp, F10 ví dụ FR-24, F11 fixture sạch, F6 `ai_ml`/`qa`. Test `test_fr23_*` chưa chạy được vì thiếu module.
- `npx vitest run tests/fr22-learning-path-fixture.test.ts` trên `web/lib/learning-path.ts` cũ → **2 failed, 13 passed** (bỏ trùng và mã sai định dạng; `retryable` của 422). Khi ba fixture mới chưa có: file lỗi ngay lúc import (`Failed to resolve import "./fixtures/learning-path-backend.intern.json"`), không chạy test nào.

### GREEN

- `uv run pytest -q` (có Postgres) → **862 passed**, không skip (mốc đợt 1: 797).
- `PYTHONHASHSEED=0` và `1` với `-m determinism` → 7 passed mỗi lượt.
- `uv run ruff check .` sạch; `ruff format --check` trên 15 file Python đã đổi: sạch.
- `check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11` → 8 pass, 2 skip (FR-22 chờ #139, FR-24 chờ #138), 0 fail. Cổng FR-24 (#138) chưa đổi; #138 nên dùng `haido_core/vocab/prepared_text.py`.
- Web: `npx vitest run` → 164 passed (file lộ trình: 15 passed, đợt 1 là 10); `npm run lint` sạch; `npm run build` thành công.
- Test cũ phải sửa vì khóa hành vi sai: `test_fr19_quay_ve_o_rong_van_giu_entry_cell_id` (đòi n >= 30 và mọi tỷ lệ `shown` cho `data_engineer`), khối `data_engineer` trong `web/tests/fr22-learning-path-fixture.test.ts`, bảng trong `docs/api/envelope-meta.md`, `test_fr20_ky_nang_nen_tang...` (đòi `foundation_for ⊆ prerequisite_for`).
- Link tài nguyên mới kiểm bằng `curl -sIL`: tất cả trả 200 ở đích cuối.

### Ghi chú F15 (lệch RED/GREEN của đợt 1)

Đợt 1 ghi ở RED "ba ca `test_ad17_display_chi_do_suppression_for_quyet[/api/v1/learning-path]`" nhưng bản cuối chỉ còn hai: ca thứ ba là `role=qa` `not_ready`, mà `not_ready` không có `Stat` nào để kiểm `display` nên ca đó bị bỏ khỏi danh sách yêu cầu (trong `_all_fixture_requests`) và `qa` chỉ còn được kiểm ở các test khác. Danh sách này đợt 2 là ba ca đủ mẫu hoặc null_data: `backend` entry, `backend` intern, `data_engineer` entry.

### Quyết định ở đợt 2 cần nhớ

- `foundation_for` rỗng khi nhóm bị ẩn (không biết nhóm của ai nên không ghi nền tảng); nhãn "Kỹ năng nền tảng" của `data_engineer` entry vì thế không hiện.
- `retryable` của lộ trình khác `city-shares`: 422 `invalid_query` cũng không thử lại (theo yêu cầu F8); `city-shares` chỉ loại `unknown_cell`. Không đổi `city-shares`.
- Tên công nghệ chỉ được che khi khớp nguyên từ; "Java 17 năm" vẫn qua vì "Java 17" là đúng một tên công nghệ. Số viết bằng chữ ngoài phạm vi.
- Tỷ lệ của `vn.backend` (157 tin) trong `fake_market.json` là số giả do đợt 2 đặt, nhóm theo θ.

## Đợt 3 — 2026-11-15 — gộp main, đưa spark/airflow/pandas trở lại

Lý do: gộp `origin/main` (64cc4b8, trước đó 30 commit: #280, #283, #284, #285, #145/#146/#147/#148, #290, #293, các sửa crawler) vào nhánh bằng một commit merge, không rebase. Từ #283 `haido_core/vocab/skills_seed.json` có 225 mã, gồm `spark`, `airflow`, `pandas` (đã kiểm), nên bản giả bỏ cách thay tạm của đợt 1.

### Xung đột (9) và cách giải

- `haido_api/stat_market.py`: giữ `newcomer_roles` thật và bảo vệ entry > n của main, giữ `learning_path` ném `UnknownCell` (chờ #216); docstring nêu cả hai.
- `haido_api/fake_market.py`: giữ `CitySharesData` có `years`, `years_unstated_cell_id` của #280; giữ `learning_path`, `_paths`, `_roles` của nhánh.
- `docs/api/envelope-meta.md`: dòng `NEWCOMER_ROLES` lấy bản của main (nguồn `stat`), giữ dòng `LEARNING_PATH`.
- `specs/144/plan.md`, `tdd.md`; `specs/163/plan.md`, `tasks.md`, `tdd.md`; `specs/205/tdd.md`: giữ cả hai bên, xếp lại các mục theo ngày (cùng ngày giữ thứ tự: bên nhánh trước). Không bỏ đợt nào.

### Sửa không có xung đột văn bản

- `create_app` đòi mọi khóa nguồn: thêm `"learning_path"` vào `tests/api/test_fr33_city_shares_years.py` (hai chỗ, #280), `tests/api/test_fr37_newcomer_roles_stat.py` (#145, #146, #148), `tests/steps/test_gh284_aggregate_vai_tro_moi.py` (#284). Tìm bằng `grep "create_app("`, không chạy RED riêng cho ba chỗ này; chỉ đổi dòng dựng app. Test `create_app({"city_shares": ...})` ở `test_ad17_routes.py` cố ý thiếu khóa nên giữ.
- `docs/api/openapi.json` sinh lại bằng `HAIDO_UPDATE_OPENAPI=1 uv run pytest -q tests/api`; `tests/api/test_ad17_web_fixtures.py` đỏ hai ca (`data_engineer` entry, có và không có `have`) sau khi thêm hai nút, nên sinh lại `web/tests/fixtures/learning-path-data_engineer.json` và `-have.json` từ response của `app`. Fixture city-shares và newcomer-roles tự gộp đã khớp, không sinh lại.
- 17 vai trò: bản giả coi mọi vai trò khác `backend` và `data_engineer` là `not_ready`. `test_fr22_vai_tro_cua_du_lieu_gia_khop_config` đã duyệt cả 17 ở `entry`; thêm `test_fr22_moi_vai_tro_cua_config_nhan_moi_cap_cua_config` (17 vai trò x 8 cấp của `level_options`, mọi vai trò ngoài hai vai trò sẵn sàng phải `not_ready`, `stages = []`, `entry_cell_id` đúng).

### Đưa spark, airflow, pandas trở lại

- `fake_market.json` `skill_rates`: `ai_ml/entry` dùng lại `pandas` (0,351, core) và `spark` (0,122, common) thay `data_analysis`, `deep_learning`; `data_engineer/senior` dùng lại `spark` (0,833) và `airflow` (0,5) thay `databricks`, `etl`, xếp lại theo chữ cái như bản gốc; `data_engineer/entry` (null_data) thêm `airflow` và `spark` để lộ trình và `/skill-rates` vẫn bằng nhau.
- `fake_learning_path.json` `data_engineer`: thêm `spark` và `airflow`, mỗi nút `requires` `python`, `sql` (chặng 2), có lời dẫn qua `prepared_text.py` (không số, không `%`, không nói tần suất) và một tài nguyên chính thức miễn phí. Lộ trình từ 11 lên 13 nút.
- Link kiểm bằng `curl -sIL` (HTTP 200 ở đích cuối): `https://spark.apache.org/docs/latest/quick-start.html`; `https://airflow.apache.org/docs/apache-airflow/stable/tutorial/pipeline.html`; `etl` đổi từ hướng dẫn Airflow sang `https://en.wikipedia.org/wiki/Extract,_transform,_load` (trung lập với nhà cung cấp, không thuộc host hay tiền tố đã bỏ).

### Test pin số đếm hoặc mã, sửa theo giá trị thật (không nới)

- RED (chạy thật sau khi sửa fixture, trước khi sửa test): `uv run pytest -q -x -k "not web_fixtures"` → 1 failed, 247 passed: `test_fr24_doi_tu_backend_sang_data_engineer_giao_cua_ho_so_voi_lo_trinh` (`13 == 11`); `HAIDO_UPDATE_OPENAPI=1 uv run pytest -q tests/api` → 2 failed, 338 passed: hai ca `test_ad17_fixture_web_khop_response_learning_path[data_engineer-entry-...]` (fixture web cũ); `npm run test` → 1 failed, 220 passed: `fr22-learning-path-fixture.test.ts` ví dụ FR-24 (`expected 13 to be 11`).
- Sửa: `test_fr24_...` và `web/tests/fr22-learning-path-fixture.test.ts` từ "2 trên 11" thành "2 trên 13" (`have_on_path = 2` không đổi: `sql`, `git`; `java` vẫn ở `have_ignored`); sinh lại hai fixture web.
- GREEN: `uv run pytest -q` (Postgres 5433, không skip) → 1113 passed; `-m determinism` với `PYTHONHASHSEED=0` và `1` → 7 passed mỗi lượt; `uv run ruff check .` sạch; `check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11` → 8 pass, 2 skip (hoãn), 0 fail; web `npm run lint` sạch, `npm run test` → 221 passed (15 file), `npm run build` qua.

## Đợt 4 (2026-11-16, #149): fixture có `skill_rates` cho mọi vai trò

Lý do: #149 thêm `skill_rates[role].entry` và `.all` cho mọi vai trò vào `haido_api/fixtures/fake_market.json` (chỉ thêm, không sửa mục cũ), và `skill-rates` kiểm `level`, nhận `have`. Lộ trình đọc chung `skill_rates`, nên hai chỗ test dựa vào việc fixture *thiếu* ô phải đổi. Hai AC của #212 vẫn đúng.

- RED: `uv run pytest tests/api -q` sau khi thêm fixture → `test_ad17_cap_khac_cua_vai_tro_san_sang_la_404_nhu_skill_rates` (backend · `all` giờ 200) và `test_fr22_ai_ml_entry_not_ready_nhung_co_skill_rates_de_mo_ho_so` (`qa` · `entry` giờ có `skill-rates`) đỏ.
- Sửa test: dùng `lead` thay `all`, và `qa` · `senior` thay `qa` · `entry`, kèm chú thích. Mã lộ trình không đổi; thứ tự và nhóm của `backend`, `data_engineer` không đổi (các fixture `web/tests/fixtures/learning-path-*.json` vẫn khớp).
- GREEN: `uv run pytest tests/api -q` → 379 passed, 74 skipped.
