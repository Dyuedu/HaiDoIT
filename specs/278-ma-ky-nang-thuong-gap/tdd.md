# TDD: Mã kỹ năng cho mọi kỹ năng tin hay nhắc tới (#278)

## Lệnh test

```bash
export HAIDO_TEST_DATABASE_URL=postgresql+psycopg://<user>:<mật khẩu>@127.0.0.1:5433/haido_test
uv run pytest tests/domain/test_gh278_vocab.py tests/tools/test_gh278_skill_gaps.py \
  tests/steps/test_gh278_skill_gaps_db.py -q
```

Đủ bộ: `uv run pytest -q`, `uv run ruff check .`, `uv run python tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24`; ở `web/`: `npx vitest run`, `npx tsc --noEmit`, `npx eslint .`.

## Danh sách hành vi

1. AC1: mỗi trong 673 khóa từ 20 tin của `gaps-2026-11-20.json` có trong `lookup` hoặc `composites`, hoặc có trong danh sách loại trừ với lý do không rỗng; mỗi dòng loại trừ có số tin bằng chứng khớp `gaps`; khóa loại trừ không là khóa từ vựng; bộ kiểm từ chối khóa trùng, thiếu lý do, khóa chưa bỏ dấu, số tin sai, khóa thuộc từ vựng, danh sách rỗng.
2. AC2: 19 cặp Anh/Việt ("Cơ sở dữ liệu"/"database", "Xử lý sự cố"/"troubleshooting", "Quản trị hệ thống"/"system administration"…) về một mã; mỗi dòng `new`/`alias`/`composite`/`exclude` của quyết định đã duyệt ra đúng mã đã duyệt; tên Anh, tên Việt và khóa thẻ của mỗi mã mới ra một mã; không khóa nào thuộc hai mã; bốn khóa chuyển khỏi mã cũ và `solid` hết dấu phẩy; mã ghép tách thành hai lượt nhắc.
3. `scan_skip`: 31 từ của quyết định không nằm trong `scan_terms` nhưng còn trong `lookup`; văn bản chỉ có các từ đó không ra lượt nhắc; "troubleshooting, debugging, code review" vẫn được quét.
4. AC4: `version` khác `seed-2026-11-13` và bằng `load_vocabulary().version`; 225 mã cũ còn; 40 mã mới có tên Anh, tên Việt, `source` `gh-278`; khi `socket.socket`, `create_connection`, `getaddrinfo` ném lỗi thì nạp từ vựng, `map_mentions` trên mọi khóa và `find_mentions` vẫn chạy. Quét lại tin khi đổi phiên bản đã có ở #283, `tests/steps/test_gh283_ingest_classify.py::test_dat29_d3_doi_tu_vung_thi_ingest_ke_tiep_quet_lai_tin_trong_cua_so`; không nhân đôi.
5. AC3 (hàm thuần): `summarize` gộp dạng bỏ dấu thành một khóa, mỗi tin một lần cho mỗi khóa, thẻ ghép tính là có mã, tỷ lệ theo vai trò (kể cả vai trò không có lượt nhắc), thứ tự số tin giảm dần; `remap` tính lại ở mức khóa; `--after` in báo cáo; số liệu snapshot 2026-11-20 (369 → 515 khóa, 26.750 → 32.802 lượt nhắc, 0 khóa bỏ sót).
6. AC3 (Postgres, kho `haido` + `public.jobs`): `counted_postings` chỉ lấy tin IT của nguồn không bị loại trong cửa sổ; `raw_skills` ghép `skills` và `skills_raw`, bỏ trùng, tin không có thẻ ra rỗng; `collect` ra bảng kỹ năng và tỷ lệ theo vai trò; chỉ-đọc (mọi SQL chụp được là SELECT, DELETE vào kho bị từ chối, bảng kho không đổi, engine ghi không bị dùng).

## RED (2026-11-23)

Chạy thật trên Postgres local (`haido_test`, cổng 5433). Viết test trước khi sửa dữ liệu thì không thể chạy đỏ riêng từng test trên code chưa có, nên RED được dựng lại bằng cách đưa các file về trạng thái trước thay đổi (`git checkout` `skills.py` và `skills_seed.json`, file mới chưa có `load_exclusions`) rồi chạy bộ test mới:

- Trạng thái 1, code cũ hoàn toàn: `uv run pytest -q tests/domain/test_gh278_vocab.py tests/tools/test_gh278_skill_gaps.py tests/steps/test_gh278_skill_gaps_db.py` → **3 lỗi collection**: `ImportError: cannot import name 'load_exclusions' from 'haido_core.vocab.skills'` (và `ExclusionList`, `parse_exclusions`).
- Trạng thái 2, có bộ nạp (`skills.py` mới) nhưng `skills_seed.json` còn `seed-2026-11-13` (dữ liệu chưa đổi): → **33 failed, 13 passed** trong 46 test. Fail vì: khóa chưa có mã (AC1), 19 cặp Anh/Việt không ra mã mới (`KeyError`), quyết định đã duyệt không tra được, `scan_skip` còn đang quét, phiên bản chưa đổi, `can_bus` v.v. chưa có, và các test dùng `remap`/`collect` với số liệu mới. 13 test xanh sẵn là hàng rào cho hành vi cũ (225 mã cũ còn, bộ kiểm chặn khóa trùng, `counted_postings`/`raw_skills` đọc đúng dữ liệu).

Lỗi của chính test mới, sửa trong lúc GREEN (không đổi hành vi):

- `test_gh278_ac2_moi_the_da_duyet_tra_ve_dung_ma_da_duyet`: ở dòng `composite`, đích là tên phần (`artificial intelligence+machine learning`), còn `composites` trả mã; đổi so sánh sang `lookup[fold(phần)]`.
- `test_gh278_summarize_gop_cach_viet_cung_dang_bo_dau_thanh_mot_khoa`: `most_common` trả tuple, test viết list.
- `test_gh278_collect_chi_doc_khong_ghi_gi`: `env.counts()` cuối test tự chạy SELECT trên engine ghi nên làm hỏng khẳng định "engine ghi không bị dùng"; đổi thứ tự hai khẳng định.
- Ruff: gộp `with` lồng nhau ở test chỉ-đọc.

## GREEN (2026-11-23)

Thứ tự sửa: `skills_seed.json` (40 mã mới, bí danh, thẻ ghép, `scan_skip`, `solid`, `version`) → `skills_excluded.json` → `skills.py` (`parse_exclusions`, `load_exclusions`) → `skill_gaps.py` (`remap`, `--after`) → fixture web.

Va chạm khóa khi dựng từ vựng (`load_vocabulary` ném `ValueError`): `can bus` (`can_bus` và `protocols_hw`), `infrastructure as code` (`infrastructure_as_code` và `terraform`), `tu duy phan tich` (`analytical_thinking` và `problem_solving`). Cả ba chuyển về mã mới; thêm `tu duy logic` đi theo để "logical thinking" và "tư duy logic" không thành hai mã (AC2). Chi tiết ở [data-model.md](data-model.md).

- `tests/domain/test_gh278_vocab.py`, `tests/tools/test_gh278_skill_gaps.py`, `tests/steps/test_gh278_skill_gaps_db.py`: **46 passed**.
- Số liệu `python tools/vocab/skill_gaps.py --after specs/278-ma-ky-nang-thuong-gap/gaps-2026-11-20.json`: 673 khóa; có mã 369 → 515; loại trừ 158; chưa có mã và chưa loại trừ 0; lượt nhắc thẻ có mã 26.750 → 32.802 trên 47.444 (56,4% → 69,1%).

### Test cũ đổi kỳ vọng vì từ vựng lớn lên

Chạy `uv run pytest -q` đầu tiên sau khi sửa dữ liệu (1739 passed, 3 failed):

| Test | Issue | Vì sao |
|---|---|---|
| `tests/api/test_ad17_web_fixtures.py::test_ad17_fixture_web_khop_response_skills` | #207 (fixture của #149/#150) | `web/tests/fixtures/skills.json` là response của `GET /api/v1/skills`; sinh lại từ chính response (`vocab_version` `seed-2026-11-23`, 265 mã). Hình dạng không đổi. `npx vitest run` xanh |
| `tests/core/test_fr13_skill_seed.py::test_fr13_khong_co_ten_vai_tro_trong_danh_sach` | #205 | Bỏ `it support` khỏi tên vai trò bị cấm (sửa ở đợt review 2026-11-23: lý do đúng là `it support` chỉ để tra thẻ của `helpdesk` và nằm trong `scan_skip`; người dùng chỉ duyệt thẻ "IT Support" (41 tin) là bí danh của `helpdesk`). Bốn tên còn lại vẫn bị cấm |
| `tests/domain/test_gh283_posting_text.py::test_gh283_giu_muc_yeu_cau_va_nhiem_vu_bo_quyen_loi_va_gioi_thieu` | #283 | Câu mẫu "Phát triển API bằng Docker" nay ra thêm mã `api` (tên Việt của mã mới là "Phát triển API"); đổi câu mẫu sang "Phát triển dịch vụ bằng Docker" để test vẫn kiểm việc cắt mục |

Các test đếm mã (`test_gh283_tu_vung_lon_hon_va_co_phien_ban_moi`: ≥ 200 mã; `test_fr13_danh_sach_moi_du_va_ma_hop_le`: trần 400) không phải sửa.

### Kết quả cuối

Chạy thật 2026-11-23, Postgres local:

- `uv run pytest -q` → **1788 passed** (lượt đầu sau khi sửa dữ liệu: 1739 passed, 3 failed, đã sửa như bảng trên).
- `uv run ruff check .` → All checks passed.
- `uv run python tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` → 10 pass, 0 skip, 0 fail.
- `web/`: `npx vitest run` → 33 files, **385 passed**; `npx tsc --noEmit` → không lỗi; `npx eslint .` → không lỗi (`tsconfig.tsbuildinfo` đã hoàn nguyên).

## Kiểm đột biến (2026-11-23)

Mỗi đột biến áp lên file thật, chạy `uv run pytest -q tests/domain/test_gh278_vocab.py tests/tools/test_gh278_skill_gaps.py`, rồi khôi phục đúng nguyên văn từ bản sao (so bằng `cmp`; `git status` không có file lạ).

| Đột biến | Kết quả |
|---|---|
| Bỏ bí danh đã duyệt `RDBMS` khỏi `databases` | **4 failed** (AC1 khóa `rdbms` bỏ sót, AC2 quyết định đã duyệt, hai test số liệu snapshot) |
| Xóa lý do của dòng đầu trong `skills_excluded.json` | **5 failed** (bộ nạp ném `thiếu lý do loại trừ`) |
| Bỏ `cloud` khỏi `scan_skip` | **1 failed** (`test_gh278_scan_skip_khong_nam_trong_tu_duoc_quet_nhung_van_tra_duoc`) |
| Giữ phiên bản cũ `seed-2026-11-13` | **2 failed** (`test_gh278_ac4_them_ma_thi_phien_ban_tu_vung_doi`, số liệu "sau" của `skill_gaps`) |
| `VocabularyMapper._one` gọi `socket.create_connection` | **3 failed** (`test_gh278_ac4_anh_xa_chay_khi_chan_mang`, `test_gh278_ac2_ma_ghep_tach_thanh_hai_ky_nang` và một test nữa chạm `_one`; ở các test không chặn mạng lỗi là `ConnectionRefusedError`) |

## Không đo được trong PR này

- AC3 cột "sau" theo vai trò: cần chạy `tools/vocab/skill_gaps.py` trên prod sau deploy (task T020). Số "sau" ở mức khóa đã có ở trên.
- #96 (từ vựng v1 có giảng viên duyệt) chưa làm; thay đổi này không thay phần duyệt của giảng viên.

## Đợt review (2026-11-23)

Lý do: review của thay đổi chưa commit tìm ra sáu lỗi. (1) `--after` đọc `code_before`/`roles_before` trong khi chính script ghi `code`/`roles`, nên báo "trước" bằng 0 khi đưa đầu ra thô vào. (2) Mã ghép `ai/ml` có phần `artificial intelligence`, `machine learning` không nằm trong "ai/ml", nên `find_mentions` trả lượt nhắc có vị trí -1. (3) Một số chữ chung của JD (`wifi`, `phân quyền`, `it support`, `khoa học dữ liệu` trong danh sách chuyên ngành…) khớp ở văn bản thật. (4) Test của #283 đã né hành vi mới bằng cách đổi câu mẫu. (5) Comment trong test của #205 nói người dùng đã duyệt việc bỏ `it support` khỏi danh sách cấm; điều đó không đúng. (8) `_strings` trả `[]` cho chuỗi không phải JSON.

Lệnh test: `uv run pytest -q tests/domain/test_gh278_vocab.py tests/tools/test_gh278_skill_gaps.py tests/core/test_fr13_skill_seed.py tests/domain/test_gh283_posting_text.py` (Postgres local `haido_test`, cổng 5433).

### Hành vi

1. `remap` nhận đầu ra của `summarize`/`collect` (`code`, `roles`) và vẫn nhận file đã lọc (`code_before`, `roles_before`); `--min-postings N` (mặc định 20) lọc khóa; `--after` nhận `--min-postings`. Số "trước" khác 0 khi đưa đầu ra thực vào.
2. "ai/ml" ra hai lượt nhắc `ai` (5-7) và `ml` (8-10), không có vị trí -1; mỗi phần của mọi mã ghép nằm trong cụm; `load_vocabulary` ném `ValueError` khi một phần không nằm trong cụm.
3. 11 khóa mới trong `scan_skip` (`bao mat`, `lap ke hoach`, `phan quyen`, `wifi`, `wi-fi`, `it infrastructure`, `it operations`, `it support`, `presentation`, `khoa hoc du lieu`, `tri tue nhan tao`): vẫn tra thẻ ra mã, không quét trong JD. Tên (không chỉ bí danh) cũng skip được, vì `scan_terms = lookup - scan_skip`.
4. `test_gh283_giu_muc_...` dùng lại câu "Phát triển API bằng Docker" và khẳng định `{"api": 1, "docker": 1, "python": 2}`.
5. `it support` là bí danh chỉ-tra-thẻ nằm trong `scan_skip`; các tên vai trò còn lại vẫn bị cấm; tên vai trò còn là bí danh phải nằm trong `scan_skip`.
8. `_strings("Python, Java ,, Go")` → `["Python", "Java", "Go"]`.

### RED (chạy thật trước khi sửa code)

Viết test trước rồi chạy: **10 failed, 64 passed** (74 test của bốn file). 11 test mới, 10 đỏ:

| Test | Vì sao đỏ |
|---|---|
| `test_gh278_ma_ghep_ai_ml_neo_tung_phan_trong_cum` | lượt nhắc đầu là `('artificial intelligence', -1, 22)`, mong `('ai', 5, 7)` |
| `test_gh278_moi_phan_cua_ma_ghep_nam_trong_cum_da_bo_dau` | `'artificial intelligence' in 'ai/ml'` sai |
| `test_gh278_tai_tu_vung_tu_choi_ma_ghep_co_phan_khong_nam_trong_cum` | `DID NOT RAISE ValueError` |
| `test_gh278_chuyen_nganh_khong_sinh_ma_data_science_hay_ai` | ra `data_science` và `artificial_intelligence` |
| `test_gh278_cum_chung_chung_trong_jd_khong_sinh_ma_moi` | mượn lượt nhắc `lap ke hoach`, `wifi` |
| `test_gh278_remap_nhan_dau_ra_cua_summarize_khong_can_doi_ten_khoa` | `TypeError: remap() got an unexpected keyword argument 'min_postings'` |
| `test_gh278_remap_loc_khoa_duoi_min_postings_mac_dinh_20` | `assert 2 == 1` (không lọc) |
| `test_gh278_cli_after_nhan_tuy_chon_min_postings` | `assert 1 == 0` (không lọc theo ngưỡng mặc định) |
| `test_gh278_strings_chuoi_khong_phai_json_tach_theo_dau_phay` | `[] == ['Python', 'Java', 'Go']` |
| `test_fr13_ten_vai_tro_duoc_giu_lam_bi_danh_phai_nam_trong_scan_skip` | `it support` còn trong `scan_terms` |

Test đã xanh sẵn: `test_gh278_remap_van_nhan_khoa_code_before_va_roles_before_cua_file_da_loc` (hành vi cũ giữ nguyên). RED bằng đột biến: `remap` chỉ đọc `code`/`roles` → 3 failed (test này, `test_gh278_remap_tinh_lai_o_muc_khoa_voi_tu_vung_moi`, `test_gh278_ac3_so_lieu_sau_...`), khôi phục bằng `cmp`.

Mục 4: test `test_gh283_giu_muc_...` với câu gốc và kỳ vọng cũ `{"docker": 1, "python": 2}` đỏ vì dư `api` (chạy `_skills(...)` ra `{'api': 1, 'docker': 1, 'python': 2}`); với kỳ vọng mới test xanh sẵn vì từ vựng đã đổi từ đợt trước.

### GREEN

Sửa `skill_gaps.py` (`remap`, `--min-postings`, `_strings`), `skills_seed.json` (`ai/ml` → `ai`, `ml`; `scan_skip` thêm 11 khóa), `skills.py` (kiểm phần của mã ghép). Bốn file test trên: **74 passed** (trước đợt này 63). `uv run pytest -q tests/domain tests/tools tests/core/test_fr13_skill_seed.py` → 634 passed.

Số liệu AC3 mức khóa chạy lại `uv run python tools/vocab/skill_gaps.py --after specs/278-ma-ky-nang-thuong-gap/gaps-2026-11-20.json`: không đổi: 673 khóa; có mã 369 → 515; loại trừ 158; chưa có mã chưa loại trừ 0; lượt nhắc thẻ có mã 26.750 → 32.802 trên 47.444.

### Đột biến (mỗi cái khôi phục đúng nguyên văn, so bằng `cmp`)

Chạy `uv run pytest -q tests/domain/test_gh278_vocab.py tests/tools/test_gh278_skill_gaps.py tests/core/test_fr13_skill_seed.py`.

| Mục | Đột biến | Kết quả |
|---|---|---|
| 1 | `remap` bỏ đọc `code`/`roles` | **1 failed** (`..._nhan_dau_ra_cua_summarize...`); với bản chỉ đọc `code`/`roles` (không `code_before`) thì 3 failed |
| 1 | bỏ lọc `min_postings` | **2 failed** |
| 8 | `_strings` trả `[]` cho chuỗi không phải JSON | **1 failed** |
| 2 | phần `ai/ml` về `artificial intelligence`/`machine learning` và tắt kiểm khi nạp | **3 failed** |
| 2 | chỉ tắt kiểm khi nạp | **1 failed** (`..._tu_choi_ma_ghep...`) |
| 3 | bỏ `khoa hoc du lieu` khỏi `scan_skip` | **1 failed** (`..._chuyen_nganh...`) |
| 3 | bỏ `wifi` khỏi `scan_skip` | **1 failed** (`..._cum_chung_chung...`) |
| 5 | bỏ `it support` khỏi `scan_skip` | **2 failed** (`..._cum_chung_chung...`, `test_fr13_ten_vai_tro_duoc_giu...`) |

### Kết quả cuối (chạy thật, từng lệnh riêng)

- `uv run pytest -q` → **1799 passed** (1788 + 11 test mới), 611 giây.
- `uv run ruff check .` → lượt đầu 1 lỗi (duyệt tập hợp trong `for` của test mới; đổi sang tuple), đã sửa; lượt sau All checks passed.
- `uv run python tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` → 10 pass, 0 skip, 0 fail.
- `web/`: `npx vitest run` → 33 files, 385 passed; `npx tsc --noEmit` → không lỗi; `npx eslint .` → không lỗi (`tsconfig.tsbuildinfo` đã hoàn nguyên). `web/tests/fixtures/skills.json` không cần sinh lại (bí danh và mã không đổi, `test_ad17_fixture_web_khop_response_skills` xanh).

## Đợt #217 (2026-11-25): lộ trình học thành chủ đề

Lý do: sửa file mà issue này từng đụng (trong số `fake_market.py`, `docs/api/openapi.json`, `docs/api/envelope-meta.md`, `tools/gates/check_gates.py`, `web/lib/learning-path.ts`, test lộ trình): chỉ phần lộ trình học. Hành vi và AC của issue này không đổi.

RED và GREEN: `specs/217-man-lo-trinh/tdd.md` đợt 4.

## Đợt #216 (2026-11-25): lộ trình thật trong StatMarket

Lý do: sửa file mà issue này từng đụng (trong số `stat_market.py`, `check_gates.py`, `envelope-meta.md`, `compose.prod.yml`, test lộ trình): chỉ phần lộ trình học. Hành vi và AC của issue này không đổi.

RED và GREEN: `specs/216-lo-trinh-that/tdd.md`.
