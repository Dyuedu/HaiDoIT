# TDD: Hiệu chỉnh và đóng băng θ_core, θ_common (#102)

**Spec**: `specs/102-dong-bang-theta/spec.md`. **Nhánh**: `gh-102-dong-bang-theta`.

## Lệnh test

```bash
export PYTHONUTF8=1; unset VIRTUAL_ENV
export HAIDO_TEST_DATABASE_URL="postgresql+psycopg://<user>:<pass>@127.0.0.1:5433/haido_test"
uv run pytest -q tests/core/test_gh102_theta_dong_bang.py tests/api/test_gh102_stat_market_theta.py \
  tests/api/test_gh102_theta_version_fake.py tests/db/test_gh102_snapshot_theta_version.py \
  tests/steps/test_gh102_aggregate_theta_version.py tests/tools/test_gh102_calibrate_theta.py
uv run pytest -q                  # toàn bộ
cd web && npx vitest run && npx tsc --noEmit && npx eslint .
```

## Hành vi cần chứng minh

1. Sổ đăng ký `config/theta.toml` được nạp; `rules.theta_version`, `rules.theta(version)` đúng (US1.1).
2. Test ghim `PINNED`: sửa, xóa phiên bản đã ghim, hay thêm phiên bản không ghim thì đỏ (US1.2).
3. Sổ đăng ký sai là `ConfigError` (US1.3).
4. `aggregate` ghi `snapshots.theta_version`; phiên bản hiện hành lạ là `StepError` (US1.4).
5. `StatMarket` nhóm và ghi `meta.thresholds` bằng θ của snapshot, không phải θ hiện hành (US1.5).
6. NULL đọc là `theta-1` (US1.6). Phiên bản lạ là `RuntimeError`, 500 (US1.7).
7. `meta.thresholds.theta_version` ở mọi route, giả và thật (US1.8).
8. Migration 0010: cột text nullable (US1, FR-003).
9. Script `tools/theta/calibrate_theta.py` in bảng `core,common`, chỉ SELECT trên `snapshots`, `stat_skill_rates` và `stat_sources` (US2.2; đợt review 2026-11-19).

## RED (2026-11-19)

Chạy 6 file test mới trên code gốc: worktree tạm từ `origin/main` (d1a48f5), chỉ chép 6 file test sang, không có code của #102.

- Cả 6 file: `4 errors during collection`. `test_gh102_theta_dong_bang.py`, `test_gh102_stat_market_theta.py`,
  `test_gh102_aggregate_theta_version.py` lỗi `ImportError` (chưa có `DEFAULT_THETA_PATH`, `ThetaVersion`);
  `test_gh102_calibrate_theta.py` lỗi `ModuleNotFoundError: tools.theta`.
- Hai file nạp được (`test_gh102_theta_version_fake.py`, `test_gh102_snapshot_theta_version.py`): **11 failed, 2 passed**.
  Fail vì `meta.thresholds` chưa có `theta_version` (5 route giả, fixture), `Thresholds` chưa nhận và chưa bắt buộc
  `theta_version`, bảng `snapshots` chưa có cột `theta_version` (cả DB lẫn `tables.py`). Hai test xanh sẵn là ca `Thresholds`
  từ chối `theta_version` rỗng/sai kiểu, vì `extra="forbid"` đã từ chối khóa lạ từ trước.

## GREEN (2026-11-19)

- 6 file test mới cùng `tests/api/test_fr09_skill_roles_stat.py`: xanh.
- Lượt toàn bộ đầu tiên: 8 failed. 7 là test cũ ghim head migration (0004–0009 "là head duy nhất" mong `0009`, `test_ad4` mong
  cột của `snapshots` không có `theta_version`): sửa sang `0010_haido_snapshot_theta` theo cùng mẫu #101 đã dùng khi nối 0009.
  1 (`test_fr09_dung_nguong_mau_...`) fail vì lượt đó chạy song song với `check_gates.py` trên cùng `haido_test`; chạy riêng 3 lần
  đều xanh.
- Chạy lại toàn bộ, không chạy gì song song: `uv run pytest -q` → **1692 passed**.
- `ruff check .` sạch. `tools/gates/check_gates.py` → 10 pass. `alembic heads` → một head `0010_haido_snapshot_theta`.
- Web: `npx vitest run` → 27 files, 347 passed; `tsc --noEmit` và `eslint .` sạch.

## Đột biến (2026-11-19)

Mỗi đột biến áp tạm vào một file, chạy 6 file test #102, khôi phục và kiểm `git status` không đổi.

| Đột biến | Kết quả |
|---|---|
| M1: sửa `theta-1` thành θ_core 0,35 trong `config/theta.toml` | 14 failed |
| M2: `_thresholds` dùng phiên bản hiện hành thay vì phiên bản của snapshot (đổi cả nhóm kỹ năng lẫn `meta.thresholds`, chỉ một chỗ trong `_thresholds`) | 13 failed |
| M2b: chỉ lời gọi `SkillGrouper` trong `skill_rates` dùng `rules.theta_core`/`rules.theta_common` (`meta` vẫn đúng) | 3 failed (chạy bản đầu của 6 file test; đo lại ở đợt review: 3) |
| M3: `replace_stats` không ghi `snapshots.theta_version` | 4 failed |
| M4: NULL đọc là phiên bản hiện hành thay vì `theta-1` | 1 failed |

## Ghi chú

- Subagent cài đặt dừng giữa chừng vì lỗi tài khoản (HTTP 403) trước khi viết file này. RED ở trên được chạy lại sau đó trên
  code gốc, không chép từ lượt chạy của subagent; lượt chạy toàn bộ dở dang của nó (7 fail ở 85%) không được tính.
- Danh sách issue cũ cần thêm đợt lấy từ dòng tiêu đề commit (`git log --format=%s -- <file>`) và đường dẫn file trong
  `specs/*/plan.md`, `specs/*/tasks.md`. Có `specs/`: #100, #101, #103, #106, #144, #145, #146, #147, #148, #149, #150, #151, #163,
  #166, #168, #205, #212, #280, #283, #284, #285, #296, #302, #309. Không có `specs/`: #2, #6, #46, #93, #113, #140, #162, #259, #263.

## Đợt review (2026-11-19)

Lý do: review chỉ ra các chỗ hở của bản đầu: `replace_stats` ghi `theta_version` vào bất kỳ snapshot nào; script hiệu chỉnh chọn snapshot lỏng hơn API; `rules.toml` còn khóa θ cũ thì bị bỏ qua; NULL đọc là `theta_versions[0]` (phụ thuộc vị trí); bộ đọc `theta.toml` còn lỏng; các test chưa đủ chặt. AC của #102 không đổi.

### Hành vi cần chứng minh thêm

1. `replace_stats` chỉ cập nhật `snapshot_id = S AND status = 'open'`; rowcount khác 1 là `ValueError` ("không có hoặc không còn open") và không đổi `theta_version`; luồng `aggregate` vẫn chạy.
2. Script hiệu chỉnh bỏ snapshot có tỷ lệ nhưng không có `stat_sources` (như `_latest_with_skill_rates`); vai trò có `n_scanned == min_sample` được tính; mọi câu SQL là SELECT và chỉ đụng `snapshots`, `stat_skill_rates`, `stat_sources`.
3. `rules.toml` còn `theta_core`/`theta_common` là `ConfigError` nói θ nay ở `config/theta.toml` và chọn bằng `theta_version`.
4. `PRE_FREEZE_THETA_VERSION = "theta-1"` là hằng của NULL; `load_theta_versions` và `load_rules` từ chối sổ đăng ký không có `theta-1` hoặc có nhưng không đứng đầu; `StatMarket._thresholds` dùng hằng.
5. `_theta_entry`: `id` có khoảng trắng hai đầu bị từ chối (không cắt); `calibrated_on` phải là ngày ISO `YYYY-MM-DD`; khóa lạ trong mục và ở cấp cao nhất bị từ chối; cận dưới của θ (`0.3/-0.1`, `0/-0.0001`) báo thông điệp "từ 0 đến 1"; số nguyên và `core == common` được chấp nhận.
6. NULL đọc là `theta-1` ở cả bốn route số liệu khi hiện hành là `theta-test`; 500 vì phiên bản lạ không có `data`/`meta` và không lộ tên phiên bản.
7. Test tài liệu (AC2): mọi id đã ghim có trong `docs/data/theta.md`; bảng "Phiên bản hiện hành" đánh dấu đúng `rules.theta_version`. Test ghim tách hai: "phiên bản đầu là `PRE_FREEZE_THETA_VERSION`" và "phiên bản hiện hành nằm trong `PINNED`".

### RED

Test viết trước, chạy trên code của bản đầu (chưa sửa code). `tests/core/test_gh102_theta_dong_bang.py` import `PRE_FREEZE_THETA_VERSION` nên lúc đầu chỉ có lỗi thu thập (`ImportError`, 1 error); để thấy từng test, thêm RIÊNG hằng `PRE_FREEZE_THETA_VERSION = "theta-1"` vào `haido_core/config.py` (chưa có kiểm tra nào) rồi chạy lại.

- 5 file còn lại (`tests/api/test_gh102_stat_market_theta.py`, `test_gh102_theta_version_fake.py`, `tests/db/test_gh102_snapshot_theta_version.py`, `tests/steps/test_gh102_aggregate_theta_version.py`, `tests/tools/test_gh102_calibrate_theta.py`): **5 failed, 43 passed**. 3 fail của `replace_stats` (`published`, `partial`, snapshot không tồn tại: "DID NOT RAISE"); 2 fail của script (snapshot mới hơn không có nguồn vẫn bị chọn; câu SQL của script không đụng `stat_sources`).
- `tests/core/test_gh102_theta_dong_bang.py` (sau khi thêm riêng hằng): **18 failed, 37 passed**. 3 id có khoảng trắng, 8 `calibrated_on` sai, 1 khóa lạ trong mục, 1 khóa lạ cấp cao nhất, 1 mục đầu không phải `theta-1`, 1 thiếu `theta-1`, 2 khóa θ cũ trong `rules.toml`, 1 test tài liệu (bảng chưa có cột "Hiện hành").
- Tổng RED có sai số hành vi: **23 failed** (cộng 1 lỗi thu thập ban đầu).

Các test sau đã xanh sẵn trên code cũ, nên RED của chúng được chứng minh bằng đột biến (bảng dưới), không bằng lần chạy này: NULL ở cả bốn route khi hiện hành đổi và 500 chặt hơn (item 6), `n_scanned == min_sample`, cận dưới của θ, các ca chấp nhận (số nguyên, `core == common`), test ghim tách đôi, test tài liệu `PINNED` có trong doc.

### GREEN

- Sau khi sửa code (`snapshot_store.py`, `config.py`, `stat_market.py`, `calibrate_theta.py`) và `docs/data/theta.md`: 6 file test #102 **103 passed**.
- `uv run pytest -q` (một mình): **1730 passed** (550 giây). Lượt trước 1692; 38 test mới.
- `uv run ruff check .`: sạch (`All checks passed!`).
- `tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` (một mình): 10 gate: 10 pass, 0 skipped, 0 failed.
- `uv run alembic heads`: một head `0010_haido_snapshot_theta`
- Web: `npx vitest run`: 27 file, 347 passed; `npx tsc --noEmit`: sạch (exit 0); `npx eslint .`: sạch (exit 0).

### Đột biến của đợt review

Mỗi đột biến áp tạm vào một file, chạy 6 file test #102 (103 test), khôi phục byte-for-byte (so bằng `cmp`).

| Đột biến | Mục | Kết quả |
|---|---|---|
| M5: bỏ `status == "open"` khỏi UPDATE trong `replace_stats` | 1 | 2 failed (`published`, `partial`) |
| M6: bỏ `has_sources` khỏi câu chọn snapshot của script | 2 | 2 failed |
| M7: `n_scanned > min_sample` thay `>=` trong script | 2 | 1 failed |
| M8: bỏ kiểm khóa θ cũ trong `load_rules` | 3 | 2 failed |
| M9: NULL đọc là `rules.theta_version` thay vì `PRE_FREEZE_THETA_VERSION` | 4, 6 | 5 failed (bản đầu chỉ 1) |
| M10: bỏ kiểm "mục đầu phải là theta-1" | 4 | 2 failed |
| M11: bỏ cận dưới `0 <=` của θ trong `_theta_entry` | 5 | 4 failed |
| M2 đo lại: `_thresholds` dùng phiên bản hiện hành | cũ | 17 failed (bản đầu 13; thêm test mới) |
| M12 (M2b): chỉ lời gọi `SkillGrouper` dùng θ hiện hành | cũ | 3 failed |

Cả chín đột biến đều bị giết. Ghi chú: M5 cho 2 fail, không phải 3, vì ca "snapshot không tồn tại" vẫn bị rowcount 0 chặn dù không có bộ lọc `status`.

## Đợt #217 (2026-11-25): lộ trình học thành chủ đề

Lý do: sửa file mà issue này từng đụng (trong số `fake_market.py`, `docs/api/openapi.json`, `docs/api/envelope-meta.md`, `tools/gates/check_gates.py`, `web/lib/learning-path.ts`, test lộ trình): chỉ phần lộ trình học. Hành vi và AC của issue này không đổi.

RED và GREEN: `specs/217-man-lo-trinh/tdd.md` đợt 4.

## Đợt #216 (2026-11-25): lộ trình thật trong StatMarket

Lý do: sửa file mà issue này từng đụng (trong số `stat_market.py`, `check_gates.py`, `envelope-meta.md`, `compose.prod.yml`, test lộ trình): chỉ phần lộ trình học. Hành vi và AC của issue này không đổi.

RED và GREEN: `specs/216-lo-trinh-that/tdd.md`.
