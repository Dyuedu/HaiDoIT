# Implementation Plan: Hình response của một kỹ năng qua các vai trò và dữ liệu giả

**Branch**: `gh-166-hinh-ky-nang-theo-vai-tro` | **Date**: 2026-11-17 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification từ `specs/166-hinh-ky-nang-theo-vai-tro/spec.md`

## Summary

Thêm phép thứ năm vào nguồn số liệu thị trường: `skill_roles`, route `GET /api/v1/skill-roles?skill=`. Schema `SkillLabel`, `SkillRoleRow`, `SkillRolesData` ở `haido_api/schemas/market.py` (validator thứ tự, `mentioned`, `level`, `cell_id`, và `check_against_meta` cho thứ tự dòng `null_data`). Bản giả đọc mục `skill_roles` của `fake_market.json` (`entry[vai trò]` và `mentions_all_levels` theo kỹ năng; số tin của ô và `skill_count` lấy từ ô `vn.<role>.entry` đã có). `StatMarket` giữ chỗ đến #168. Web có kiểu, hàm gọi API và năm fixture để #169 dựng màn.

Đợt 2 (2026-11-17, theo review): cỡ mẫu của `skill_rate` là `n_by_measure.skill_count` (hàm chung `sample_n` ở `haido_core/domain/envelope.py`, dùng ở `Envelope`, bản giả và schema); `Envelope` gọi `data.check_against_meta(meta)` nếu `data` có; `mentioned` theo `mentions_all_levels`; `data.level`; compose prod đặt `stat`; bộ chốt chống lệch fixture và config.

## Technical Context

**Language/Version**: Python 3.13, FastAPI, Pydantic 2; TypeScript, Next.js, Vitest

**Primary Dependencies**: Không thêm gói.

**Storage**: Không đổi cơ sở dữ liệu.

**Testing**: `HAIDO_TEST_DATABASE_URL=... uv run pytest -q`; `cd web && npx vitest run tests/fr09-skill-roles-fixture.test.ts`

**Constraints**: AD-17 (số là `Stat`, `meta.cells`), AD-22 (web không sắp xếp, không suy `mentioned`), AD-5 (route không tính), DEC-6 (không chữ số trong câu).

## Constitution Check

- AD-17: tỷ lệ là `Stat`; n ở `meta.cells`; không số nào đứng riêng.
- AD-22: thứ tự và `mentioned` ở API.
- Không viết spec vào `_bmad-output/`.

## Project Structure

### Documentation (this feature)

```text
specs/166-hinh-ky-nang-theo-vai-tro/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── tasks.md
└── tdd.md
```

### Source Code (repository root)

```text
haido_api/schemas/market.py           (SkillLabel, SkillRoleRow, SkillRolesData)
haido_api/market_source.py            (UnknownSkill, MarketReadModel.skill_roles)
haido_api/errors.py                   (handler 404 unknown_skill)
haido_api/routes/market.py            (SOURCE_ENV skill_roles, route /skill-roles, kiểm bộ từ vựng)
haido_api/fake_market.py              (FakeMarket.skill_roles)
haido_api/fixtures/fake_market.json   (mục skill_roles: python, figma, abap, sap, machine_learning; đợt 2: vn.game.entry skill_count 12)
haido_api/stat_market.py              (StatMarket.skill_roles: unknown_cell đến #168; từ #168 đọc số thật)
haido_core/domain/envelope.py         (đợt 2: SKILL_COUNT, sample_n, hook check_against_meta)
deploy/compose.prod.yml               (đợt 2: HAIDO_MARKET_SOURCE_SKILL_ROLES: stat)
haido_core/vocab/skills.py            (find_seed_skill)
docs/api/openapi.json, docs/api/envelope-meta.md
web/lib/skill-roles.ts                (mới; đợt 2: rowN theo skill_count, level, invalid_query không thử lại)
web/tests/fixtures/skill-roles-{python,figma,abap,sap,machine_learning}.json (mới), newcomer-roles.json (đợt 2: ô game đổi skill_count)
web/tests/fr09-skill-roles-fixture.test.ts (mới)
tests/api/test_fr09_skill_roles.py    (mới)
tests/api/test_ad17_routes.py, test_ad17_web_fixtures.py   (route mới, fixture web; đợt 2: n của skill_rate theo skill_count)
tests/domain/test_ad17_envelope.py    (đợt 2: cỡ mẫu skill_rate, hook check_against_meta)
tests/deploy/test_gh166_ky_nang_vai_tro_doc_snapshot_that.py (đợt 2, mới: prod stat, local fake)
tests/api/test_dat20_stat_market.py, test_fr33_city_shares_level.py, test_fr33_city_shares_years.py,
tests/api/test_fr37_newcomer_roles_stat.py, tests/steps/test_dat20_api_end_to_end.py,
tests/steps/test_gh284_aggregate_vai_tro_moi.py            (create_app đòi thêm nguồn skill_roles)
```

**Structure Decision**: Cùng khuôn với `newcomer_roles` (#144) và `learning_path` (#212): một phép trong `MarketReadModel`, một mục `SOURCE_ENV`, một route, một mục fixture; không cơ chế song song.
