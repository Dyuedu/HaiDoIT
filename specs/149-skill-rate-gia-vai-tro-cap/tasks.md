# Tasks: Endpoint tỷ lệ kỹ năng giả theo vai trò và cấp

**Input**: `specs/149-skill-rate-gia-vai-tro-cap/`

**Tests**: Viết trước theo `tdd.md`.

## Phase 1: Test

- [x] T001 Test mọi vai trò × `entry`/`all` trả 200; `level` lạ 422, trong `tests/api/test_fr19_skill_rates_vai_tro_cap.py`
- [x] T002 Test ô quay về gọi tên ô rộng hơn và n ≥ 30; không ô nào đủ thì `null_data`
- [x] T003 Test thứ tự dòng và nhóm theo θ
- [x] T004 Test `have`, `core_size`, `have_core`; `have` sai 422

## Phase 2: Implementation

- [x] T005 Schema, route, protocol, `StatMarket`
- [x] T006 `FakeMarket.skill_rates`: sắp dòng, `have`, đếm core
- [x] T007 Fixture: `entry` + `all` cho mọi vai trò
- [x] T008 Sinh lại `docs/api/openapi.json` và fixture web `skill-rates-*.json`
