# Data Model: Cố vấn lộ trình roadmap.sh từ CV, Level, Vị trí & dữ liệu JD

**Date**: 2026-11-27  
**Branch**: `gh-216-lo-trinh-that`

## Database / Alembic

**Không thay đổi schema Postgres / không thêm revision Alembic.**

- Tuân thủ `AD-11` và `NFR-4`: file CV và văn bản trích từ CV chỉ sống trong RAM trong thời gian xử lý request và bị hủy ngay sau khi trả response; không ghi vào Postgres hay log.
- Dữ liệu yêu cầu JD theo `(role, level)` đọc từ `MarketReadModel.skill_rates` (`stat_skill_rates` + `stat_cells` khi bật `stat`, hoặc `FakeMarket` khi ở chế độ `fake`), giữ nguyên `AD-7` và `AD-25`.

## API Response Contracts (`Envelope[AdvisorRoadmapData]`)

- `AdvisorGenerationMode`: `"llm"` | `"market_fallback"`
- `AdvisorRoadmapData`:
  - `path: LearningPathData` — cấu trúc lộ trình `roadmap.sh` chuẩn gồm `role`, `level`, `status`, `cell_id`, `entry_cell_id`, `stages[]`, `current_stage`, `have_on_path`, `path_size`, `have_ignored`.
  - `cv_skills: list[SkillCode]` — các mã kỹ năng nhận diện từ CV (thuộc `skills_seed.json`, tối đa 200 mã).
  - `missing_core_skills: list[SkillCode]` — kỹ năng `core` từ JD của `(role, level)` chưa có trong CV/hồ sơ.
  - `missing_common_skills: list[SkillCode]` — kỹ năng `common` từ JD của `(role, level)` chưa có trong CV/hồ sơ.
  - `advisor_summary: str` — nhận xét cá nhân hóa về độ khớp hiện tại của CV với `(role, level)` và định hướng học.
  - `generation_mode: AdvisorGenerationMode` — `"llm"` khi gọi model thành công, `"market_fallback"` khi dùng bộ dựng lộ trình từ dữ liệu thị trường (offline/chưa có key).

*Lưu ý `Ordinal` allowlist (`tests/api/test_ad17_ordinal_allowlist.py`):* Không thêm trường `Ordinal` mới vào `AdvisorRoadmapData` (chỉ tái sử dụng `LearningPathData` đã nằm trong allowlist) và cập nhật `docs/api/envelope-meta.md` + `docs/api/openapi.json` cùng `SAMPLE_QUERY` cho route `POST` trong `tests/api/test_ad17_routes.py`.
