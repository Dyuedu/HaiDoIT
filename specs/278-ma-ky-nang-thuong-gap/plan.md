# Implementation Plan: Mã kỹ năng cho mọi kỹ năng tin hay nhắc tới

**Branch**: `gh-278-ma-ky-nang-thuong-gap` | **Date**: 2026-11-23 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/278-ma-ky-nang-thuong-gap/spec.md`

## Summary

Mở rộng bản mồi `skills_seed.json` theo quyết định đã duyệt (`quyet-dinh-2026-11-20.json`): 40 mã mới, bí danh cho mã có sẵn, 6 thẻ ghép, `scan_skip` mở rộng, phiên bản `seed-2026-11-23`. Thêm `skills_excluded.json` (158 thẻ loại trừ có lý do) và bộ nạp/kiểm trong `skills.py`. Thêm `--after` vào `tools/vocab/skill_gaps.py` để đo lại "sau" ngoại tuyến. Không đổi lược đồ DB, không đổi API.

## Technical Context

**Language/Version**: Python 3.13

**Primary Dependencies**: thư viện chuẩn (`json`, `importlib.resources`, `argparse`), SQLAlchemy cho script. Không thêm gói.

**Storage**: file JSON trong `haido_core/vocab/`; không đổi PostgreSQL.

**Testing**: `uv run pytest <file> -q` (Postgres: `HAIDO_TEST_DATABASE_URL` trỏ `haido_test` cổng 5433).

**Constraints**: ánh xạ không gọi mạng hay mô hình (AD-9, #97); mã giữ định dạng `snake_case` ≤ 40 ký tự; 225 mã cũ không mất (hồ sơ người dùng đã lưu); một khóa đã bỏ dấu chỉ thuộc một mã. Không sửa `scraper/`, `_bmad-output/`.

**Scale/Scope**: 265 mã, 1.021 từ được quét (sau khi trừ `scan_skip`), 158 dòng loại trừ.

## Constitution Check

- AD-2: không thêm phép; phép 1 (`map_mentions`) không đổi thân hàm.
- AD-9: không gọi LLM; thêm mã là sửa dữ liệu có người duyệt.
- AD-10: từ vựng là dữ liệu có phiên bản; phiên bản đổi thì `ingest` quét lại (#283).
- AD-25: không có migration.
- Bộ từ vựng v1 (#96) sẽ thay `skills_seed.json`; thay đổi này không tuyên bố giảng viên đã duyệt.

## Project Structure

### Documentation (this feature)

```text
specs/278-ma-ky-nang-thuong-gap/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── tasks.md
├── tdd.md
├── de-xuat-tu-vung.md            (bản đề xuất, giữ làm hồ sơ duyệt)
├── gaps-2026-11-20.json          (kết quả skill_gaps.py trên prod)
└── quyet-dinh-2026-11-20.json    (quyết định đã duyệt)
```

### Source Code (repository root)

```text
haido_core/vocab/skills_seed.json       # 40 mã mới, bí danh, thẻ ghép, scan_skip, version seed-2026-11-23
haido_core/vocab/skills_excluded.json   # MỚI: 158 thẻ loại trừ
haido_core/vocab/skills.py              # ExcludedSkill, ExclusionList, parse_exclusions, load_exclusions; load_vocabulary kiểm phần của mã ghép (review 2026-11-23)
tools/vocab/skill_gaps.py               # MỚI vào repo; có remap() và --after
docs/data/vocabulary.md                 # MỚI: cách từ vựng lớn lên, danh sách loại trừ, scan_skip, chạy script
web/tests/fixtures/skills.json          # fixture của GET /api/v1/skills theo từ vựng mới

tests/domain/test_gh278_vocab.py                # AC1, AC2, scan_skip, version, 225 mã cũ, chặn mạng
tests/tools/test_gh278_skill_gaps.py            # summarize, remap, --after
tests/steps/test_gh278_skill_gaps_db.py         # counted_postings, raw_skills, collect, chỉ-đọc (Postgres)
tests/core/test_fr13_skill_seed.py              # (review 2026-11-23) tên vai trò làm bí danh phải ở scan_skip
tests/domain/test_gh283_posting_text.py         # (review 2026-11-23) khôi phục câu gốc, kỳ vọng thêm `api`
```

Test cũ đổi vì từ vựng lớn lên: ghi từng file trong [tdd.md](tdd.md).

## Spec của issue cũ cập nhật cùng commit

`haido_core/vocab/skills.py`, `skills_seed.json` và `web/tests/fixtures/skills.json` đã được các issue sau đụng tới (theo `git log` và `specs/*/plan.md`): #205, #283, #166, #207, #149/#150 (fixture). Mỗi issue có `specs/` được thêm một đợt vào `tdd.md` (có ngày), và `plan.md`/`tasks.md`/`spec.md` khi file hoặc hành vi liên quan đổi. Không AC nào của các issue đó đổi nghĩa (xem tdd.md). Issue cũ chưa có `specs/` mà code liên quan: không có (mọi issue đã commit vào các file này đều có thư mục `specs/`).

## Rủi ro và quyết định

- Ba khóa trùng giữa mã cũ và mã mới: mã mới giữ khóa (data-model.md). Mã cũ không mất mã nào.
- Thêm từ vào `scan_terms` đổi kết quả quét mọi tin (nhiều tin có thêm mã mới). Đó là mục đích; `ingest` kế tiếp quét lại tin trong cửa sổ khi `vocab_version` đổi.
- Số "sau" theo vai trò chỉ đo được trên prod: hướng dẫn ở `docs/data/vocabulary.md`.

## Đợt review 2026-11-23

- `tools/vocab/skill_gaps.py`: `remap` đọc `code`/`roles` của chính script (rơi về `code_before`/`roles_before`), thêm `--min-postings` (mặc định 20); `_strings` tách chuỗi không phải JSON theo dấu phẩy.
- `haido_core/vocab/skills_seed.json`: phần của `ai/ml` là `ai`, `ml`; `scan_skip` thêm 11 từ (47 → 58).
- `haido_core/vocab/skills.py`: `load_vocabulary` kiểm mỗi phần của mã ghép nằm trong cụm.
- Test: `tests/tools/test_gh278_skill_gaps.py`, `tests/domain/test_gh278_vocab.py`, `tests/core/test_fr13_skill_seed.py`, `tests/domain/test_gh283_posting_text.py`. Docs: `docs/data/vocabulary.md`, `data-model.md`, `spec.md` (giới hạn đã biết, AC2, AC3).
