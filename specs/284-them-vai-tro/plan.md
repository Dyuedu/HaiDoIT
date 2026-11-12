# Implementation Plan: Thêm bảy vai trò vào danh sách vai trò

**Branch**: `gh-284-them-vai-tro` (tách từ `gh-283-phan-loai-tu-jd`, PR #287 chưa merge) | **Date**: 2026-11-13 | **Spec**: [spec.md](spec.md)

## Summary

Thêm bảy mã vai trò vào `roles` và `[labels.role]` của `config/rules.toml`, làm rỗng `[report_as]` của `config/classify.toml`, thêm bảy chip vào `ROLE_OPTIONS` của web, thêm số giả cho bảy mã vào `haido_api/fixtures/fake_market.json` (city-shares mức `all`, dòng `newcomer_roles`), sinh lại `web/tests/fixtures/newcomer-roles.json`. Bước `aggregate`, API và màn Bản đồ đọc danh sách vai trò từ config nên không đổi code.

## Technical Context

**Language/Version**: Python 3.13; TypeScript 5, Next.js 16, React 19.

**Primary Dependencies**: không thêm gói.

**Storage**: không đổi bảng. Số hàng `stat_*` mỗi snapshot tăng theo số vai trò: 18 vai trò (kể cả `all`) × 9 cấp × 6 mốc số năm × 6 phạm vi = 5832 ô (trước 3564).

**Testing**: `uv run pytest -q` (Postgres), `npm --prefix web run test`, `lint`, `build`.

**Constraints**: `classify_version` không đổi (nhãn đã lưu không đổi, chỉ cách báo cáo đổi). `config_version` đổi. Luật "mỗi mã một nhãn" của `[labels.role]` giữ nguyên.

## Constitution Check

- AD-10: danh sách vai trò và nhãn là config có phiên bản.
- AD-17: vai trò mới đi qua cùng `suppression_for`.
- AD-5: API không đếm; số do `aggregate` ghi.

## Project Structure

```text
config/rules.toml
config/classify.toml
haido_api/fixtures/fake_market.json
web/lib/labels.ts
web/tests/fixtures/newcomer-roles.json
tests/deploy/test_gh284_vai_tro_moi.py                 (mới)
tests/steps/test_gh284_aggregate_vai_tro_moi.py        (mới, Postgres)
web/tests/fr33-role-chips-new-roles.test.tsx           (mới)
tests/core/test_ad10_rules_config.py, tests/core/test_gh283_classify_config.py,
tests/steps/test_gh283_ingest_classify.py, web/tests/fr33-map-screen.test.tsx (sửa theo kỳ vọng mới)
```

## Spec của issue cũ bị đụng

- `config/rules.toml`, `labels.ts`: #163, #280 (bộ lọc dùng chung danh sách vai trò) — thêm đợt TDD.
- `config/classify.toml`, `test_gh283_*`: #283 — thêm đợt TDD, ghi `report_as` đã rỗng.
- `fake_market.json`, `newcomer-roles.json`: #144 — thêm đợt TDD.
- `test_gh162_ban_do_doc_snapshot_that.py`: #162 (không có `specs/`) — ghi tên trong mô tả PR.
