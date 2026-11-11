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
