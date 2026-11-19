# TDD: Phân loại tin ở bước ingest từ chức danh và nội dung JD (#283)

## Lệnh test

```bash
export HAIDO_TEST_DATABASE_URL=postgresql+psycopg://haido:haido_local@127.0.0.1:5433/haido_test
uv run pytest tests/domain/test_gh283_posting_text.py tests/domain/test_gh283_mapping.py \
  tests/domain/test_gh283_classify_roles.py tests/domain/test_gh283_classify_levels.py \
  tests/core/test_gh283_classify_config.py tests/steps/test_gh283_ingest_classify.py \
  tests/db/test_gh283_facts_labels.py -q
```

## Danh sách hành vi

1. `requirement_text` giữ mục yêu cầu và nhiệm vụ, bỏ mục quyền lợi, giới thiệu công ty, địa điểm; không có tiêu đề thì giữ hết; che "khoa học máy tính"; cắt `max_text_chars`.
2. `find_mentions` tìm cụm dài trước, không chồng lấn, đếm mọi lượt; `map_mentions` đưa bí danh Anh/Việt về một mã, chuỗi lạ `None`; "C/C++" ra `c` và `cpp`.
3. Từ vựng giữ 100 mã cũ; không có bí danh mơ hồ (`sap`, `lan`, `san`, `pic`, `soc`, `solid`, `less`, `word`).
4. Số năm: số tháng có cấu trúc của nguồn > giá trị bước trích > luật đọc mục yêu cầu (yêu cầu chính, khoảng lấy đầu dưới); "không yêu cầu kinh nghiệm" → 0; số năm ngoài ngữ cảnh kinh nghiệm bị bỏ.
5. Vai trò: cụm vai trò cụ thể trong chức danh thắng cụm chung; chức danh chung dùng bằng chứng kỹ năng; không có cụm nào cần ≥ 4 kỹ năng kỹ thuật để là IT; cụm không thuộc IT thắng trừ khi vai trò cụ thể đứng trước; nghệ sĩ/đồ họa không thuộc IT; QA của phòng thử nghiệm không có kỹ năng kiểm thử phần mềm không thuộc IT.
6. Các lỗi đã thấy ở research.md đều có test: Ba Vì, khoa học máy tính, chăm sóc, cybersecurity, an ninh thông tin, e-commerce, mạng di động 4G/5G, CNC, game artist, Product Manager, Experienced (non-manager).
7. Chức danh con theo vai trò; không khớp thì `None`.
8. Cấp: chữ cấp của nguồn → chức danh → số năm (bảng #134) → "không xác định"; không ra Intern/Lead từ số năm; "Product Manager" không phải cấp Lead.
9. Luật đọc từ `config/classify.toml`, sai thì `ConfigError` nêu khóa; mọi nhãn vai trò có mã trong `[labels.role]`.
10. Ingest lưu nhãn, mã kỹ năng có số lượt, số năm, `classify_version`; làm mới tin trong cửa sổ có phiên bản luật cũ; không thêm phiên bản khi đã đúng.
11. Aggregate dùng nhãn đã lưu; hàng không có nhãn của luật hiện tại thì phân loại từ trường đóng.
12. Migration 0007 là head, có hạ cấp; không cột text/jsonb nào của schema `haido` chứa chuỗi đánh dấu của mô tả.
13. Cùng đầu vào và cấu hình thì cùng nhãn, không phụ thuộc thứ tự lô.

## RED (2026-11-13)

Chạy thật trên Postgres local (`haido_test`, cổng 5433), code chưa đổi.

- `uv run pytest <6 file domain/core/steps> -q` → **6 lỗi collection**: `ImportError: cannot import name 'load_classify_config'` (posting_text, classify_roles, classify_levels, ingest_classify), `ImportError: cannot import name 'DEFAULT_CLASSIFY_PATH'` (classify_config), `ModuleNotFoundError: No module named 'haido_core.domain.mapping'` (mapping).
- `uv run pytest tests/db/test_gh283_facts_labels.py -q` → **3 failed, 1 passed**: head vẫn là 0006, chưa có cột `role`…`classify_version`, chưa có 0007 để hạ cấp. Test chuỗi đánh dấu xanh sẵn vì ingest cũ chưa đọc mô tả; nó đứng làm hàng rào cho code mới.

## GREEN (2026-11-13)

Thứ tự sửa: từ vựng → `posting_text`, `mapping` → `classify.toml`, bộ đọc config, `classify.py`, `registry.py`, `REGISTRY.md` → bảng, migration 0007, `snapshot_store` → `scraper_source`, `ingest` → bước `aggregate`.

Sửa test trong lúc GREEN (lỗi của test, không đổi hành vi):

- `test_gh283_thieu_khoa_thi_configerror_neu_khoa`: `replace("classify_version", …, 1)` thay vào dòng chú thích đầu file; đổi thành thay `classify_version = "`.
- `FULLSTACK_JD` của `test_gh283_classify_roles.py`: JD mẫu ban đầu chỉ cho Frontend 4 điểm (dưới ngưỡng 6 đã hiệu chỉnh trên dữ liệu thật), nghiêng hẳn Backend; thêm Redux, HTML, CSS cho đúng một JD fullstack.
- `test_gh283_ingest_classify.py`: `job_postings` có khóa `id`, không phải `posting_id`.

Test cũ đổi vì hành vi đổi theo spec (không AC nào của issue cũ hỏng):

| Test | Issue | Vì sao |
|---|---|---|
| `tests/domain/test_ad2_registry.py::test_ad2_khong_nhan_van_ban_day_du_va_khong_import_framework` | #3 (không có `specs/`) | `PostingFacts` có thêm `text`, `skills`, `years_min`; test nay kiểm `REGISTRY.md` nói "được nhận văn bản JD đầy đủ" và "không gọi mô hình" |
| `tests/core/test_ad10_rules_config.py::test_ad10_bang_nhan_khop_voi_luat_cua_bo_phan_loai` | #6 | So nhãn vai trò sau `report_as` |
| `tests/core/test_fr13_skill_seed.py::test_fr13_danh_sach_moi_du_va_ma_hop_le` | #205 | Trần 150 mã → 400 (225 mã) |
| `tests/steps/test_ad4_ingest.py::test_ad4_doc_nguon_khong_cham_cot_van_ban_va_khong_ghi_vao_bang_scraper` | #6 | Bỏ dòng "nguồn không chứa chữ description"; phần "mô tả không xuống bảng, bảng scraper không đổi" giữ nguyên. `FakeReader` có thêm `read_facts` |
| `tests/db/test_ad4_snapshot_schema.py::test_ad4_cot_dung_thiet_ke_va_khong_co_cot_van_ban_jd` | #6 | Thêm năm cột nhãn vào danh sách cột |
| `tests/steps/test_dat20_aggregate_step.py::test_dat20_nguon_chi_it_…` | #93 | "Nhân viên kinh doanh" nay là không thuộc IT (cụm "kinh doanh"); ví dụ đổi sang "Chuyên viên sản phẩm" (không mang cụm nào) để giữ ý "nguồn chỉ-IT, chức danh không rõ vai trò là Other" |
| `test_dat20_stat_tables.py`, `test_fr33_stat_city_shares_level.py`, `test_fr33_stat_years.py` (kiểm head) | #93, #163, #280 | Head là 0007 |

Kết quả: `uv run pytest -q` → **875 passed**; hai lượt `-m determinism` 6 passed mỗi lượt.

## Đo trên mẫu tự gán nhãn — đợt 1 (2026-11-13)

`tools/classify_eval/`: 180 tin của bản sao local (snapshot 12/11): 120 ngẫu nhiên, 30 chức danh nhắc AI, 30 chức danh có cụm AI/ML chặt (đợt AI đầu chỉ ra 16 tin AI/ML hoặc khoa học dữ liệu thật theo nhãn tay, nên lấy thêm). Tổng 43 tin AI/ML hoặc khoa học dữ liệu. Nhãn tay ở `labels.csv` (mã băm URL, vai trò, số năm), không có văn bản JD.

| Bộ | Đúng vai trò | Đúng mã trên bản đồ | IT precision* | IT recall* |
|---|---|---|---|---|
| Luật cũ | 49% | 54% | 69% | 55% |
| Luật mới (`classify-2026-11-13.1`) | 81% | 84% | **82%** | 93% |
| Bước trích (Haiku) | 85% | 93% | 99% | 97% |

\* trên 120 tin ngẫu nhiên. AI/ML gộp Data Scientist: luật cũ P 97% / R 65%, luật mới 98% / 98%, bước trích 100% / 95%. Số năm (109 tin đọc được): luật mới khớp 94%, bước trích 92%.

IT precision 82% chưa đạt SC-001 (≥ 90%). Tin lệch tập trung: TopDev bị coi là nguồn chỉ-IT (10 tin ngân hàng, xây dựng, điện thành Other), "quality control" trong cụm không thuộc IT, cụm "network" quá rộng, thiếu "systems administrator", "máy chủ", "(qa)", "applied ai scientist", " ui ", và chức danh lãnh đạo IT (CTO, Solution Architect) bị coi là không thuộc IT khi mô tả ít kỹ năng.

## RED đợt 2 (2026-11-13)

Thêm `test_gh283_loi_tu_mau_tu_gan_nhan` (12 trường hợp lấy từ tin lệch ở trên). Chạy trên `classify.toml` trước khi sửa (sinh lại từ script sinh ban đầu, cộng hai chỉnh tay đã có): **12 failed, 53 passed**.

## GREEN đợt 2 (2026-11-13)

`classify.toml` → `classify-2026-11-13.2`: bỏ `topdev` khỏi `it_only_sources`; bỏ "quality control" khỏi `non_it_phrases`, thêm "khách hàng doanh nghiệp/cá nhân", "quan hệ khách hàng"; Hạ tầng bỏ "network" đứng riêng, thêm "network engineer/administrator", "quản trị viên máy chủ", "máy chủ", "systems administrator/engineer"; QA thêm "(qa)"; AI/ML thêm "ai scientist", "applied ai"; UI/UX thêm " ui "; BA thêm "lead - product"; `art_phrases` thêm "video editor"; khóa mới `generic_it_titles` (CTO, Solution Architect…: luôn là Other). Code: `ClassifyConfig.generic_it_titles` và một nhánh trong `_role`.

`tests/domain`, `tests/core` → 358 passed. Đo lại trên cùng mẫu:

| Bộ | Đúng vai trò | Đúng mã trên bản đồ | IT precision | IT recall |
|---|---|---|---|---|
| Luật mới (`classify-2026-11-13.2`) | 94% | 97% | 97% | 100% |

Số này lạc quan vì luật được sửa theo chính mẫu này. Để kiểm, gán nhãn thêm **40 tin ngẫu nhiên ngoài mẫu** (seed 2830, `labels_holdout.csv`) **sau khi** luật đã chốt, không sửa luật theo chúng:

| Bộ (mẫu giữ riêng, 40 tin) | Đúng vai trò | Đúng mã trên bản đồ | IT precision | IT recall |
|---|---|---|---|---|
| Luật cũ | 38% | 48% | 65% | 42% |
| Luật mới | **85%** | 85% | **95%** | **81%** |
| Bước trích | 86% | 92% | 96% | 92% |

Số năm trên mẫu giữ riêng (23 tin đọc được): luật mới 22/23, bước trích 19/23. IT recall 81% dưới SC-001 (≥ 85%) trên mẫu giữ riêng: 5 tin bị coi là không thuộc IT đều là việc quản lý dự án/quản trị ("Technical Program Manager", "Giám đốc dự án phát triển sản phẩm số", kiểm toán CNTT, LiveOps game, quản trị LMS). Mẫu chỉ có 26 tin IT nên sai số lớn; không sửa luật theo mẫu này để nó còn là phép thử.

## Trước/sau trên snapshot 12/11/2026 của bản sao local

Gỡ snapshot 12/11 khỏi bản sao `haido_preview`, chạy lại `ingest → lifecycle → aggregate → publish` bằng code mới (`classify-2026-11-13.2`). Số đếm theo cụm, phạm vi toàn quốc, `years = any`.

| Vai trò (mã bản đồ) | Trước: mọi cấp / mới vào nghề / % không rõ cấp | Sau |
|---|---|---|
| Tất cả | 2233 / 136 / 68,4% | 3748 / 711 / 13,3% |
| AI/ML | 107 / 11 / 59,8% | 208 / 41 / 14,9% |
| Backend | 386 / 7 / 57,3% | 470 / 56 / 13,8% |
| QA | 282 / 31 / 65,2% | 292 / 77 / 9,9% |
| DevOps | 138 / 8 / 67,4% | 214 / 23 / 11,7% |
| Data Engineer | 86 / 3 / 58,1% | 134 / 18 / 14,9% |
| Data Analyst | 109 / 6 / 73,4% | 140 / 22 / 15,0% |
| Mobile | 65 / 0 / 67,7% | 91 / 15 / 9,9% |
| Frontend | 72 / 3 / 59,7% | 73 / 10 / 8,2% |
| Embedded | 52 / 7 / 80,8% | 82 / 17 / 28,0% |
| Other | 936 / 60 / 75,4% | 2044 / 432 / 13,2% |

Other lớn vì BA/PO/PM, Hạ tầng, Security, Fullstack, UI/UX, Game báo cáo như Other tới #284 (`report_as`); trong kho các nhãn này tách riêng.

Thời gian và bộ nhớ: `ingest` 14,1 giây cho 2716 quan sát cộng phần làm mới (6255 dữ kiện mới; lần đầu sau deploy mọi tin trong cửa sổ đều được phân loại lại); đỉnh heap Python 32 MB (`tracemalloc`). `lifecycle` 1,8 giây, `aggregate` 3,2 giây, `publish` 1,1 giây.

## Kết quả cuối

| Lệnh | Kết quả |
|---|---|
| `uv run pytest <7 file của #283> -q` | xanh |
| `uv run pytest -q` (Postgres local) | **887 passed** |
| `PYTHONHASHSEED=0 uv run pytest -q -m determinism` | 6 passed |
| `PYTHONHASHSEED=1 uv run pytest -q -m determinism` | 6 passed |
| `uv run ruff check .` | All checks passed |
| `uv run python tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7` | 8 pass, 2 skip (có hạn), 0 fail |
| `uv run alembic heads` | `0007_haido_classify_at_ingest (head)` |

## REFACTOR

`plan_ingest` và phần làm mới dùng chung `FactLabeler` (một chỗ tạo từ vựng, bộ ánh xạ, bộ phân loại). Bản sao luật v1 ở `tools/classify_eval/classify_v1.py` đổi tên method thành `label_v1` để registry vẫn đóng (cổng AD-2).

## Đợt 2026-11-13 — #284 bảy nhãn mới có mã riêng

Lý do: #284 làm rỗng `[report_as]` của `config/classify.toml` và thêm bảy mã vào `config/rules.toml`. Nhãn lưu ở `job_posting_facts` không đổi, `classify_version` không đổi.

- RED: `test_gh283_moi_nhan_vai_tro_co_ma_trong_rules_sau_report_as` (đòi Data Scientist → `ai_ml` qua `report_as`) và `test_gh283_aggregate_dung_nhan_da_luu` (đòi Data Scientist trong ô `ai_ml`) đỏ.
- GREEN: đổi kỳ vọng sang mã riêng (`data_scientist`, `fullstack`); `uv run pytest -q` → 908 passed.

## Đợt 2026-11-13 — #285 34 tỉnh, Remote, Nước ngoài

Lý do: #285 đổi mã nơi (`classify.toml` thay ba thành phố bằng 34 tỉnh, thêm Remote, Nước ngoài, dòng địa chỉ; `classify_version` `classify-2026-11-13.3`; nơi lưu ở `job_posting_facts.city`). Không AC nào của issue này đổi.

- RED: `test_gh283_migration_0007_noi_tiep_0006_va_la_head_duy_nhat` đỏ vì head là 0008.
- GREEN: sửa kỳ vọng theo mã nơi mới; `uv run pytest -q` → 947 passed; `npx vitest run` → 166 passed.

## Đợt 2026-11-16 (theo #101)

Lý do: #101 sửa `haido_core/steps/ingest.py` và `haido_core/db/snapshot_store.py` (xem đợt 2 bên dưới: `vocab_version` và quét lại khi từ vựng đổi), `haido_core/steps/aggregate.py`, `haido_core/db/tables.py`. `tests/db/test_gh283_facts_labels.py` đổi kỳ vọng head Alembic từ 0008 sang 0009; `tests/steps/test_gh283_ingest_classify.py` thêm hai test quét lại khi từ vựng đổi. Không thêm hành vi mới nào của issue này, không AC nào đổi. Hành vi mới (quét lại khi từ vựng đổi) có đợt riêng bên dưới.

Chạy lại thật sau thay đổi (đợt 2 của #101): `uv run pytest tests/steps/test_gh283_ingest_classify.py tests/db/test_gh283_facts_labels.py tests/steps/test_gh284_aggregate_vai_tro_moi.py -q` → **15 passed**. Toàn bộ `uv run pytest -q` → **1194 passed**.

## Đợt 2026-11-16 — #101 D3: quét lại khi từ vựng đổi

Lý do: người dùng quyết định (D3) rằng `ingest` quét lại kỹ năng của tin trong cửa sổ khi phiên bản từ vựng đổi, giống lệch `classify_version`. Dữ kiện có thêm cột `vocab_version`; không AC nào của #283 đổi.

- Lệnh: `HAIDO_TEST_DATABASE_URL=... uv run pytest tests/steps/test_gh283_ingest_classify.py tests/db/test_gh283_facts_labels.py tests/steps/test_gh284_aggregate_vai_tro_moi.py -q`.
- Hành vi: (a) từ vựng đổi phiên bản thì dữ kiện trong cửa sổ có phiên bản mới mang `vocab_version` mới; (b) dữ kiện cũ NULL cũng được quét lại; (c) chạy lại cùng từ vựng không thêm phiên bản.
- RED: hai test (a) và (b) đã viết cùng đợt với code ở đợt làm trước; không chạy RED trên cây chưa sửa. Bằng chứng thay thế là đột biến: bỏ hai điều kiện `vocab_version` khỏi `stale_in_window` thì **2 test fail** (đúng hai test trên), khôi phục thì xanh.
- GREEN: ba file trên → **15 passed** (chạy lại thật). Toàn bộ `uv run pytest -q` → **1194 passed**, không skip.

## Đợt 2026-11-17 (#166): file dùng chung đổi, hành vi của issue này không đổi

Lý do: #166 (hình response `skill-roles`) sửa file mà issue này từng đụng: `haido_core/vocab/skills.py` (thêm `find_seed_skill`; `load_vocabulary`, quét JD không đổi). Thay đổi: từ vựng quét JD không đổi.

- RED: không có, vì không có hành vi nào của issue này đổi; không test nào của issue này đổi kỳ vọng. RED của #166 nằm ở `specs/166-hinh-ky-nang-theo-vai-tro/tdd.md`.
- GREEN (chạy thật, 2026-11-17): `uv run pytest -q` (Postgres thật, DB `t166_test`) → 1510 passed, không skip; `cd web && npx vitest run` → 22 files, 293 passed; `tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` → 10 pass, 0 skip, 0 fail.

## Chạy lại (2026-11-17, #302)

#302 sửa `config/rules.toml` (`[sources].auto` thêm `topcv`, `config_version` lên `2026-11-17.1`), `tests/core/test_ad10_rules_config.py` và `tests/steps/test_ad4_ingest.py` (ví dụ nguồn chạy tay đổi từ `topcv` sang `linkedin`). Không đổi scenario của issue này.

- `uv run pytest -q` → 1018 passed, 217 skipped.

## Đợt 2026-11-17 (#151, #106, #103): file dùng chung đổi, AC của issue này không đổi

Lý do: tỷ lệ kỹ năng thật (#151), phép 2 `select_cell` (#106) và ràng buộc lớp đọc (#103) sửa file mà issue này từng đụng:

  - `haido_core/domain/REGISTRY.md` (ghi thân hàm phép 2);
  - `haido_core/domain/registry.py` (`CellChoice.label` nới thành `str | None`, thêm `CellChoice.order` có mặc định);

Hành vi và AC của issue này không đổi: thay đổi chỉ thêm (phương thức `skill_rates` thật, trường `order` có mặc định, một biến môi trường ở prod, một đoạn tài liệu); `city_shares`, `newcomer_roles`, `learning_path`, `skill_roles` của `StatMarket` giữ nguyên. Chi tiết: `specs/151-ty-le-ky-nang-that/plan.md`.

- RED: không có, vì không có hành vi nào của issue này đổi; không test nào của issue này đổi kỳ vọng. RED của #151, #106, #103 nằm ở `specs/151-ty-le-ky-nang-that/tdd.md`, `specs/106-chon-o-quay-ve/tdd.md`, `specs/103-api-doc-ty-le-that/tdd.md`.
- GREEN (chạy thật, 2026-11-17): `uv run pytest -q` (Postgres thật, DB `fx151_test`, không skip) → 1580 passed; `cd web && npx vitest run` → 298 passed; `tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` → 10 pass, 0 skip, 0 fail.

Cập nhật sau review (đợt 2, 2026-11-17): trong `StatMarket` chỉ `skill_rates` đổi thêm (404 khi ô không có hàng tỷ lệ, `n_scanned` nhất quán, chữ nhãn); hành vi và AC của issue này vẫn không đổi. RED và GREEN: `specs/151-ty-le-ky-nang-that/tdd.md` đợt 2.

## Đợt #102 (2026-11-19): θ có phiên bản, AC của issue này không đổi

Lý do: #102 đóng băng θ (`config/theta.toml`, `theta-1` = 0,3/0,1), thêm `snapshots.theta_version` (migration 0010) và `meta.thresholds.theta_version`, sửa file mà issue này từng đụng: `config/rules.toml`, `haido_core/config.py`, `haido_core/db/snapshot_store.py`, `haido_core/db/tables.py`, `haido_core/steps/aggregate.py`, `tests/core/test_ad10_rules_config.py`, `tests/db/test_ad4_snapshot_schema.py`, `tests/db/test_dat20_stat_tables.py`, `tests/db/test_fr33_stat_city_shares_level.py`, `tests/db/test_fr33_stat_years.py`, `tests/db/test_gh283_facts_labels.py`.
Giá trị θ không đổi nên số, nhóm và hành vi của issue này không đổi; test chỉ thêm `theta_version` vào ngưỡng hoặc đổi head migration mong đợi sang 0010. Riêng `tests/core/test_ad10_rules_config.py`: `rules.toml` không còn `theta_core`/`theta_common` nên `BASE` dùng `theta_version`, và các ca kiểm θ cũ (thiếu khóa, giá trị ngoài [0, 1], `theta_common > theta_core`) đã chuyển sang `tests/core/test_gh102_theta_dong_bang.py`, nay kiểm trên `config/theta.toml`. RED, GREEN và đột biến: `specs/102-dong-bang-theta/tdd.md`.
