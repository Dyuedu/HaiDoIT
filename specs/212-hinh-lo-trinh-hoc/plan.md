# Implementation Plan: Hình response của lộ trình học và dữ liệu giả

**Branch**: `gh-212-hinh-lo-trinh-hoc` | **Date**: 2026-11-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification từ `specs/212-hinh-lo-trinh-hoc/spec.md`

## Summary

Thêm phép thứ tư vào nguồn số liệu thị trường: `learning_path`, route `GET /api/v1/learning-path`. Schema mới ở `haido_api/schemas/learning_path.py` (validator thứ tự FR-22, đếm, tham chiếu). Hàm thuần `haido_api/learning_path.py` áp `have` lên lộ trình (đếm, chặng hiện tại, mã bị bỏ qua) để bản giả và bản thật (#216) dùng chung. Bản giả đọc `haido_api/fixtures/fake_learning_path.json` (đồ thị, lời dẫn, tài nguyên) và lấy tỷ lệ từ `skill_rates` của `fake_market.json`, nên số luôn bằng `/skill-rates`. Web có kiểu TypeScript, hàm dựng query và fixture.

## Technical Context

**Language/Version**: Python 3.13, FastAPI 0.162, Pydantic 2.14; TypeScript, Next.js 16, Vitest

**Primary Dependencies**: Không thêm gói.

**Storage**: Không đổi cơ sở dữ liệu.

**Testing**: `HAIDO_TEST_DATABASE_URL=... uv run pytest -q`; `cd web && npx vitest run tests/fr22-learning-path-fixture.test.ts`

**Constraints**: AD-7 (web không sắp xếp), AD-22 (web không đếm; `have` tối đa 200 mã), AD-17 (số là `Stat`, `meta.cells`), AD-5 (route không tính).

## Constitution Check

- AD-17: tỷ lệ là `Stat`; số tin entry-level ở `meta.cells[entry_cell_id].n`; không số nào đứng riêng.
- AD-7, AD-22: thứ tự và mọi phép đếm ở API.
- Không viết spec vào `_bmad-output/`.

## Project Structure

### Documentation (this feature)

```text
specs/212-hinh-lo-trinh-hoc/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── tasks.md
└── tdd.md
```

### Source Code (repository root)

```text
haido_api/schemas/learning_path.py         (mới; đợt 2: validator foundation_for bắc cầu)
haido_api/learning_path.py                 (mới; đợt 2: PathGraphError, stage_numbers, foundation_targets)
haido_core/vocab/prepared_text.py          (đợt 2, mới: kiểm lời dẫn FR-23 cho #138 dùng lại)
haido_api/fixtures/fake_learning_path.json (mới)
haido_api/market_source.py
haido_api/fake_market.py                   (đợt 2: UnknownCell thay KeyError, quay về trong vai trò, foundation_for bắc cầu)
haido_api/stat_market.py
haido_api/routes/market.py                 (đợt 2: mô tả `have`)
haido_api/fixtures/fake_market.json        (đổi mã sang snake_case, thêm hàng skill_rates)
haido_api/schemas/market.py                (chỉ docstring SkillRateRow.skill)
haido_core/domain/envelope.py             (thêm dấu Ordinal; đợt 2: chỉ miễn khi kiểu đúng là Ordinal / Ordinal | None và giá trị int không âm)
docs/api/openapi.json
docs/api/envelope-meta.md
tests/api/test_fr22_learning_path.py       (mới; đợt 2 sửa test FR-19)
tests/api/test_fr22_learning_path_review.py (đợt 2, mới: quét vai trò × cấp, nhóm, FR-24, trần 200, đồ thị)
tests/api/test_fr22_learning_path_graph.py (đợt 2, mới: chặng, foundation_for bắc cầu, validator)
tests/api/test_fr23_blurbs.py              (đợt 2, mới)
tests/api/test_ad17_ordinal_allowlist.py   (đợt 2, mới)
tests/core/test_fr23_prepared_text.py      (đợt 2, mới)
tests/domain/test_ad17_ordinal.py          (đợt 2, mới)
tests/api/test_ad17_routes.py
tests/api/test_ad17_web_fixtures.py
tests/api/test_dat20_stat_market.py
tests/api/test_fr33_city_shares_level.py
tests/steps/test_dat20_api_end_to_end.py
web/lib/learning-path.ts                   (mới)
web/tests/fixtures/learning-path-*.json    (mới; đợt 2: thêm backend.intern, data_engineer-have, ai_ml)
web/tests/fr22-learning-path-fixture.test.ts (mới)
```

**Structure Decision**: Schema ở module riêng vì `schemas/market.py` đã dài và lộ trình có nhiều validator. Chặng là thuộc tính của nút: lọc `have` không đổi thứ tự. Tỷ lệ của lộ trình đọc từ `skill_rates` của bản giả (không chép số) để hai route không thể lệch.

## Complexity Tracking

- `create_app` đòi nguồn cho mọi phép: các test của #2, #93, #163 truyền thêm `learning_path`. Issue cũ chưa có `specs/` mà branch này đụng tới file của chúng (ghi trong mô tả PR): #2, #93, #162, #259, #263 (`stat_market.py`, `envelope.py`, `market_source.py`, `fake_market.json`, test), #140 (`docs/api/envelope-meta.md`), #46 (`tests/api/test_ad17_web_fixtures.py`).
- Cập nhật `specs/144-...`, `specs/163-...`, `specs/205-...` (mục "Thay đổi sau merge" và đợt TDD mới). `main.py` không đổi.
- Đợt 2: `haido_core/domain/envelope.py` còn thuộc #144 (đã có `specs/`): hành vi `Stat` và `MeasureKind` của #144 không đổi.
