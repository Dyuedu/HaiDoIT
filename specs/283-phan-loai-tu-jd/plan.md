# Implementation Plan: Phân loại tin ở bước ingest từ chức danh và nội dung JD

**Branch**: `gh-283-phan-loai-tu-jd` | **Date**: 2026-11-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/283-phan-loai-tu-jd/spec.md`

## Summary

`ingest` đọc thêm mô tả JD của scraper, cắt lấy các mục yêu cầu và nhiệm vụ, tìm lượt nhắc kỹ năng bằng từ vựng song ngữ (regex xen kẽ, cụm dài trước), ánh xạ sang mã qua phép 1 `map_mentions`, giải số năm, rồi gọi phép 6 `classify` với chức danh, chữ cấp, văn bản, mã kỹ năng và số năm. Kho chỉ lưu nhãn vai trò, chức danh con, cấp, mã kỹ năng có số lượt, số năm và `classify_version` (migration 0007). Tin trong cửa sổ có nhãn của luật cũ được làm mới ở lượt ingest kế tiếp. `aggregate` dùng nhãn đã lưu. Luật nằm ở `config/classify.toml`.

## Technical Context

**Language/Version**: Python 3.13

**Primary Dependencies**: SQLAlchemy, Alembic; `re`, `unicodedata`, `tomllib` của thư viện chuẩn. Không thêm gói.

**Storage**: PostgreSQL schema `haido`. Migration `0007_haido_classify_at_ingest`.

**Testing**: `uv run pytest <file> -q` (Postgres: `HAIDO_TEST_DATABASE_URL=postgresql+psycopg://haido:haido_local@127.0.0.1:5433/haido_test`).

**Constraints**: Phân loại không gọi mô hình; cùng đầu vào và cấu hình thì cùng nhãn. Văn bản JD không xuống bảng, log, file tạm (DoD dòng 9). Chữ ký tám phép trong `REGISTRY.md` không đổi; chỉ đổi luật phép 6 và thêm thân hàm phép 1. `CellKey` không đổi. API và web không đổi ở issue này (#284, #285, #286). Không sửa `scraper/`, `_bmad-output/`.

**Scale/Scope**: Khoảng 2700 quan sát mỗi ngày, mô tả trung bình 2150 ký tự; lượt làm mới đầu tiên sau deploy phân loại lại khoảng 9000 tin trong cửa sổ. Bản nháp chạy 6255 tin trong 28 giây.

## Constitution Check

- AD-2: không thêm phép; phép 1 có thân hàm trong `domain/mapping.py`, phép 6 vẫn một class trong `domain/classify.py`. Luật phép 6 đổi trong `REGISTRY.md` cùng PR. `find_mentions` và `requirement_text` là hàm trợ giúp, không phải phép dùng chung.
- AD-4: dữ kiện chỉ thêm phiên bản, không sửa hàng cũ; tin quan sát sau S không nhận phiên bản tại S.
- AD-9: không gọi LLM; số năm của bước trích được đọc như trường đã lưu.
- AD-10: luật và từ vựng là dữ liệu có phiên bản.
- AD-25: một head Alembic, có `downgrade`.
- DoD dòng 9: test chuỗi đánh dấu trên mọi cột text/jsonb của schema `haido`.

## Project Structure

### Documentation (this feature)

```text
specs/283-phan-loai-tu-jd/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── tasks.md
└── tdd.md
```

### Source Code (repository root)

```text
config/classify.toml                                  (mới)
config/rules.toml                                     (config_version, labels.role)
haido_core/config.py                                  (đọc classify.toml)
haido_core/domain/REGISTRY.md                         (luật phép 6)
haido_core/domain/registry.py                         (PostingFacts.text/skills/years_min)
haido_core/domain/classify.py                         (luật v2, ClassifyConfig từ config)
haido_core/domain/mapping.py                          (mới: phép 1 VocabularyMapper)
haido_core/domain/posting_text.py                     (mới: fold, requirement_text, find_mentions, years)
haido_core/vocab/skills.py, skills_seed.json          (từ vựng mới)
haido_core/db/scraper_source.py                       (mô tả, số năm; đọc tin theo URL)
haido_core/db/tables.py
haido_core/db/migrations/versions/0007_haido_classify_at_ingest.py
haido_core/db/snapshot_store.py                       (FactVersion; tin trong cửa sổ cần làm mới)
haido_core/steps/ingest.py
haido_core/steps/aggregate.py
tools/classify_eval/                                  (mới: classify_v1.py đóng băng, sample.py, evaluate.py, labels.csv, labels_holdout.csv; không có văn bản JD)

tests/domain/test_gh283_posting_text.py               (mới)
tests/domain/test_gh283_mapping.py                    (mới)
tests/domain/test_gh283_classify_roles.py             (mới)
tests/domain/test_gh283_classify_levels.py            (mới)
tests/core/test_gh283_classify_config.py              (mới)
tests/steps/test_gh283_ingest_classify.py             (mới, Postgres)
tests/db/test_gh283_facts_labels.py                   (mới, Postgres)
tests/domain/test_classify*.py, tests/steps/test_ad4_ingest.py, tests/steps/test_dat20_aggregate_step.py,
tests/db/test_ad4_snapshot_schema.py, tests/core/test_skills_seed*.py   (sửa theo kỳ vọng mới)
```

## Spec của issue cũ bị đụng

Tìm bằng `git log -- <file>` và `specs/*/plan.md`:

- `classify.py`: #100 (cụm), #163 (cấp lọc) — thêm đợt TDD có ngày.
- `ingest.py`, `scraper_source.py`, `snapshot_store.py`, `tables.py`: #280 — thêm đợt TDD; `data-model.md` của #280 ghi `years_min` đổi nghĩa.
- `aggregate.py` (bước): #100, #163, #263, #280 — thêm đợt TDD.
- `skills_seed.json`, `skills.py`: #205 — thêm đợt TDD, dòng Status.
- Issue không có thư mục `specs/` mà test của chúng đổi: #3 (`test_ad2_registry.py`), #6 (`test_ad10_rules_config.py`, `test_ad4_ingest.py`, `test_ad4_snapshot_schema.py`), #93 (`test_dat20_aggregate_step.py`, `test_dat20_stat_tables.py`), #263 (`aggregate.py`) — ghi tên trong mô tả PR.
