# Implementation Plan: Hiệu chỉnh và đóng băng θ_core, θ_common

**Branch**: `gh-102-dong-bang-theta` | **Date**: 2026-11-19 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification từ `specs/102-dong-bang-theta/spec.md`

## Summary

Tách θ khỏi `rules.toml` thành sổ đăng ký chỉ-thêm `config/theta.toml`; `rules.toml` chỉ chọn phiên bản hiện hành. `aggregate` ghi phiên bản đã dùng vào `snapshots.theta_version` (migration 0010). `StatMarket` nhóm kỹ năng và ghi `meta.thresholds` bằng θ của phiên bản trong snapshot được chọn. Một test ghim cứng mọi phiên bản đã đóng băng.

## Technical Context

**Language/Version**: Python 3.13, FastAPI, SQLAlchemy 2, Alembic, Postgres.

**Primary Dependencies**: không thêm.

**Storage**: thêm cột `haido.snapshots.theta_version` (xem `data-model.md`).

**Testing**: `uv run pytest -q`, Postgres thật qua `HAIDO_TEST_DATABASE_URL`; web: `npx vitest run`, `npx tsc --noEmit`.

## Constitution Check

- AD-7: `StatMarket` vẫn chỉ đọc `stat_*` và `snapshots`; script hiệu chỉnh cũng vậy.
- AD-17: `Thresholds` thêm trường bắt buộc; bản giả và fixture web khớp nhau.
- AD-25: một head Alembic (0010 nối sau 0009).
- Không viết spec vào `_bmad-output/`.

## Project Structure

```text
specs/102-dong-bang-theta/                spec, plan, tasks, research, data-model, tdd
config/theta.toml                         MỚI: sổ đăng ký θ
config/rules.toml                         theta_version thay hai số; config_version tăng
haido_core/config.py                      ThetaVersion, PRE_FREEZE_THETA_VERSION, load_theta_versions (mục đầu là theta-1, id không khoảng trắng,
                                          calibrated_on ISO, không khóa lạ), load_rules (từ chối khóa theta cũ), RulesConfig.theta()
haido_core/db/tables.py                   cột snapshots.theta_version
haido_core/db/migrations/versions/0010_haido_snapshot_theta.py   MỚI
haido_core/db/snapshot_store.py           replace_stats(..., theta_version=) cập nhật snapshots chỉ khi status = 'open', rowcount != 1 là ValueError
haido_core/steps/aggregate.py             kiểm phiên bản hiện hành có trong sổ, truyền theta_version
haido_core/domain/envelope.py             Thresholds.theta_version
haido_api/stat_market.py                  _thresholds(latest), nhóm và meta theo θ của snapshot; NULL dùng PRE_FREEZE_THETA_VERSION
haido_api/fixtures/fake_market.json       thresholds.theta_version
web/lib/city-shares.ts                    kiểu Thresholds.theta_version
web/tests/fixtures/*.json, envelopes.ts   chép lại response bản giả, thêm theta_version
docs/api/envelope-meta.md, openapi.json   thêm theta_version
docs/data/theta.md                        MỚI: AC2
tools/theta/calibrate_theta.py            MỚI: in bảng hiệu chỉnh, chỉ đọc; chọn snapshot cần cả stat_sources như API

tests/core/test_gh102_theta_dong_bang.py          MỚI: bộ đọc, test ghim, cận dưới của θ, ca chấp nhận, theta-1 đứng đầu, khóa cũ/lạ, test tài liệu AC2
tests/db/test_gh102_snapshot_theta_version.py     MỚI: migration, replace_stats chỉ ghi snapshot open
tests/steps/test_gh102_aggregate_theta_version.py MỚI: aggregate ghi phiên bản
tests/api/test_gh102_stat_market_theta.py         MỚI: StatMarket theo θ của snapshot; NULL là theta-1 ở cả bốn route khi hiện hành đổi
tests/api/test_gh102_theta_version_fake.py        MỚI: bản giả và Thresholds
tests/tools/test_gh102_calibrate_theta.py         MỚI: script; bỏ snapshot thiếu nguồn, n_scanned == min_sample, bắt SQL (chỉ SELECT, ba bảng)
tests tests/core/test_ad10_rules_config.py (các ca θ cũ đã chuyển sang test_gh102_theta_dong_bang.py), tests/api/test_dat20_stat_market.py, test_fr09_skill_roles_stat.py,
  test_fr19_skill_rates_stat.py, test_fr33_city_shares_level.py, tests/domain/test_ad17_envelope.py,
  test_ad17_ordinal.py, tests/db/test_dat29_stat_skill_rates.py    SỬA: theta_version
```

## Quyết định thiết kế

- Sổ đăng ký nạp luôn từ `config/theta.toml` (tham số `theta_path` để test); không đặt cạnh file `rules.toml` được truyền vào, nên test dùng file rules tạm vẫn chạy với sổ thật.
- `replace_stats` nhận `theta_version` bắt buộc (keyword-only) để không bước nào quên ghi.
- `aggregate` từ chối chạy nếu phiên bản hiện hành không có trong sổ đăng ký, để không tạo snapshot mà API không đọc được.
- Không điền lại `theta_version` cho hàng cũ trong migration: NULL đã có nghĩa rõ (`theta-1`), và migration không phụ thuộc file cấu hình.
- Không thêm ràng buộc DB cho `theta_version`: sổ đăng ký nằm ở file, không ở DB; kiểm ở `aggregate` (ghi) và `StatMarket` (đọc).
- NULL đọc là hằng `PRE_FREEZE_THETA_VERSION = "theta-1"`, không phải `theta_versions[0]`: thứ tự không được quyết định nghĩa của dữ liệu cũ. Để hằng và vị trí không lệch nhau, bộ đọc từ chối sổ đăng ký có mục đầu khác `theta-1`.
- `replace_stats` tự bảo vệ (UPDATE chỉ khớp `status = 'open'`) thay vì tin `aggregate` đã khóa: hàm công khai không được lặng lẽ đổi `theta_version` của snapshot đã chốt.
- `rules.toml` còn `theta_core`/`theta_common` là lỗi, không phải bỏ qua: nếu bỏ qua, người sửa số ở đó sẽ tưởng θ đã đổi.

**Cập nhật 2026-11-27 (#230)**: các file sau của issue này được #230 sửa thêm, hành vi không đổi: `config/rules.toml`, `docs/api/envelope-meta.md`, `docs/api/openapi.json`, `haido_api/fixtures/fake_market.json`, `haido_api/stat_market.py`, `haido_core/config.py`, `tests/api/test_dat20_stat_market.py`, `tests/api/test_fr09_skill_roles_stat.py`, `tests/api/test_fr19_skill_rates_stat.py`, `tests/api/test_fr33_city_shares_level.py`, `tests/api/test_gh102_stat_market_theta.py`, `tests/core/test_ad10_rules_config.py`. Xem `specs/230-hinh-soi-tin/plan.md`.
