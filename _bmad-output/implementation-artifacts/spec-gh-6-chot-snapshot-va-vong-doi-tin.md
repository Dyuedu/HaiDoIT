---
title: 'GH-6 [1.4] Chốt snapshot và vòng đời tin'
type: 'feature'
created: '2026-11-06'
status: 'done'
baseline_commit: 'be07e0c54eb1773def53f2afaf2cc49034d243e7'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/_bmad-output/planning-artifacts/DOD.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** #69 (tỷ trọng thành phố, cổng ra Sprint 1) cần đọc tin của đúng ngày S và đánh dấu S đã công bố, nhưng kho của Hải Đồ chưa có bảng nào: migration `0001` rỗng, còn `job_lifecycle` của #74 chỉ là hàm thuần. Dữ liệu thật hiện chỉ nằm ở bảng của scraper (cầu nối C-11), nơi `jobs` bị ghi đè bằng bản mới nhất.

**Approach:** Thêm migration tạo bảng snapshot, lượt chạy, tin, dữ kiện tin theo ngày, quan sát và vòng đời. Thêm hai bước CLI: `haido ingest --snapshot S` mở snapshot S rồi chép lượt chạy, quan sát và dữ kiện tin của S từ bảng scraper (chỉ thêm); `haido lifecycle --snapshot S` gọi `job_lifecycle` rồi ghi `stat_job_lifecycle`. Scraper và nhịp một hằng ngày giữ nguyên.

## Boundaries & Constraints

**Always:**
- `snapshot_id` là `YYYY-MM-DD` theo `Asia/Ho_Chi_Minh`.
- Snapshot chỉ do `open_snapshot` (gọi trong `ingest`) tạo, trạng thái đầu là `open`. `published` và `partial` do bước `publish` của #69 đặt. `ingest` và `lifecycle` cho S đã `published` hoặc `partial` thì từ chối và không ghi gì.
- Quan sát và dữ kiện tin chỉ thêm: code không `UPDATE`/`DELETE`, và DB chặn bằng trigger. Chạy lại `ingest` cho S đang `open` không sinh hàng trùng.
- Mỗi quan sát treo vào một lượt chạy (`pipeline_run`) của đúng nguồn và đúng S. Lượt thành công khi `listing_complete` của scraper là true. Nguồn ngoài danh sách tự động trong config ghi `mode = manual`.
- Dữ kiện tin (chức danh, công ty, địa điểm, chữ cấp bậc) lưu theo phiên bản: chỉ thêm phiên bản khi khác phiên bản mới nhất có `snapshot_id ≤ S`. "Dữ kiện của tin tại S" là phiên bản mới nhất có `snapshot_id ≤ S`.
- Không lưu mô tả JD, liên hệ người đăng hay cột nào ngoài dữ kiện trên.
- Số lần thấy, ngày thấy đầu và cuối, số lần đăng lại, `absent`, `in_window` chỉ nằm trong `stat_job_lifecycle` theo từng snapshot, tính bằng `domain.lifecycle.job_lifecycle`. Không có cột vòng đời bị `UPDATE` trên bảng tin.
- `window_days` và danh sách nguồn tự động đọc từ `config/rules.toml` có `config_version`; `stat_job_lifecycle` lưu `config_version` đã dùng.
- Hàng của một bước cho S ghi trong một transaction. Lỗi giữa chừng thì không còn hàng nào của lần chạy đó.
- Cùng dữ liệu nguồn, cùng config thì chạy lại cho kết quả giống hệt.
- Bước ở `haido_core/steps/`, truy cập DB ở `haido_core/db/`, logic thuần ở `domain`. Không import Dagster. Thông báo lỗi tiếng Việt, không in mật khẩu.
- Code theo TDD như #46: test đỏ đúng lý do trước, ghi vào Implementation Notes, rồi mới code cho xanh.
- Kết nối nguồn (bảng scraper) đặt chế độ chỉ-đọc ở phía DB. Kết nối đích có host ngoài `localhost`/`127.0.0.1`/`postgres` thì từ chối, trừ khi đặt `HAIDO_ALLOW_REMOTE_WRITE=1`.

**Never:**
- Không sửa `scraper/` và `deploy/daily.sh`. Bảng scraper chỉ đọc bằng `SELECT`, không đọc cột `description`.
- Không chạy migration hay ghi gì lên Supabase trong story này.
- Không làm `publish`, `aggregate`, phân loại, gom tin trùng (#69, 1.5, 1.8), không làm `haido_pipeline`.
- `haido_api` không đọc bảng mới (AD-5).

**Quyết định (06/11/2026):**
- Bảng mới nằm trong schema Postgres riêng `haido`. `ingest` đọc bảng scraper qua `HAIDO_SCRAPER_DATABASE_URL` và ghi vào `HAIDO_DATABASE_URL`. Hai URL trỏ cùng một DB (prod, Supabase) hoặc khác nhau (máy dev nạp từ Supabase vào Postgres local).
- Lịch chạy hằng ngày và kiểm tay ba ngày để sau; story này chạy tay bằng CLI.
- Giữ một spec dù dài hơn mức khuyến nghị.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Ba lượt liền | Tin X có mặt ở S1, S2, S3, cả ba lượt thành công | `lifecycle` S3: thấy 3 lần, đầu S1, cuối S3 | N/A |
| Đêm lỗi | S2 nguồn có `listing_complete = false` | Lượt S2 không thành công; không tính vắng, không tăng đăng lại | N/A |
| Mất rồi đăng lại | X vắng 3 lượt thành công, có lại ở S5 | S4: `absent`, đăng lại 0; S5: đăng lại 1 | N/A |
| Dữ kiện đổi | Chức danh X đổi ở S3 | Dữ kiện tại S2 là bản cũ, tại S3 là bản mới; hàng cũ giữ nguyên | N/A |
| Chạy lại | `ingest` S hai lần khi S `open` | Số hàng như sau lần đầu | N/A |
| S đã chốt | S có trạng thái `published` | Từ chối, mã thoát khác 0, không ghi | Thông báo tiếng Việt |
| Sửa quan sát | `UPDATE` hoặc `DELETE` trên quan sát | DB từ chối | Lỗi của DB |
| Nguồn thủ công | `topcv` có lượt ở S | Lượt `mode = manual` | N/A |
| Chưa có dữ liệu S | Scraper không có lượt nào ngày S | Không mở snapshot | Báo lỗi, mã thoát khác 0 |
| Sai ngày | `--snapshot 2026-13-01` | Không ghi | Báo lỗi, mã thoát khác 0 |
| Tin chưa có trong `jobs` | Quan sát của S trỏ tới URL không có hàng `jobs` | Vẫn có tin và quan sát; không có phiên bản dữ kiện | N/A |
| Đích là host lạ | `HAIDO_DATABASE_URL` trỏ Supabase, chưa đặt cờ | Không ghi | Báo lỗi, không in mật khẩu |

</frozen-after-approval>

## Code Map

- `haido_core/db/migrations/env.py` -- `get_url()` đọc `HAIDO_DATABASE_URL`, chặn host ngoài `localhost`/`127.0.0.1`/`postgres` trừ khi `HAIDO_ALLOW_REMOTE_MIGRATION=1`; `target_metadata = None`. Không nới cổng an toàn. Dùng lại `validate_migration_target` cho URL test.
- `haido_core/db/migrations/versions/0001_initial.py` -- head hiện tại, rỗng. Migration mới đặt `down_revision = "0001_initial"` (AD-25).
- `haido_core/domain/lifecycle.py` -- `SourceRun(source, snapshot_id, success)`, `Observation(job_id, source, snapshot_id)`, `job_lifecycle(runs, observations, snapshot_id, *, window_days)`. Dùng lại, không sửa. `in_window` là `0 ≤ S − last_seen ≤ window_days`.
- `haido_core/domain/registry.py:131` -- `PostingFacts(title, source, source_category, seniority_text, location_text)`: #69 dựng đầu vào phép 6 từ dữ kiện tin, nên cột dữ kiện phải đủ cho nó (`source_category` hiện không có ở scraper, để trống).
- `haido_core/steps/__init__.py` -- trống; đặt `ingest.py`, `lifecycle.py` ở đây.
- `scraper/schema.sql` -- nguồn: `jobs(job_url PK, site, title, company, location, experience_level, job_level, …)` bị UPSERT; `job_observations(job_url, snapshot_date, site)`; `source_runs(source, snapshot_date, listing_complete, seen_count, error)`.
- `scraper/ingest.py:37` -- `AUTO_SOURCES` bảy nguồn; nguồn thiếu file seen được ghi là lượt chưa đủ. Không sửa.
- `scraper/tests/test_observations.py:492` -- mẫu test Postgres: URL từ biến môi trường, `skipif` khi không có.
- `tests/db/test_ad25_alembic.py` -- test an toàn URL và một head; không được phá.
- `pyproject.toml` -- chưa có `[project.scripts]`; thêm `haido`. Thêm marker `postgres`.
- `.github/workflows/ci.yml` -- job `python` không có Postgres, job `alembic` có `postgres:18.6`. Test DB phải chạy thật trong CI.
- `tools/gates/check_gates.py:338` -- cổng riêng tư cấm tên cột như `jd_text`, `raw_jd`, `job_text`; cổng AD-7 cấm `haido_api` nhắc `job_*`.
- `_bmad-output/implementation-artifacts/spec-gh-69-tinh-va-doc-ty-trong-thanh-pho.md` -- bên dùng: cần cột trạng thái snapshot, lượt chạy theo nguồn cho `sources_failed`, dữ kiện tin tại S, vòng đời trong cửa sổ.

## Tasks & Acceptance

**Cách làm: TDD** theo `docs/templates/test-driven-tdd/test-driven-development.md`. Mỗi cặp: viết test, chạy đúng file test đó và thấy đỏ vì chưa có hành vi (không phải lỗi cú pháp hay import), ghi một dòng vào Implementation Notes, rồi code vừa đủ cho xanh. Tên test chứa `ad4` hoặc `ad10` (DoD dòng 11).

**Chạy test:** trong vòng đỏ-xanh chỉ chạy file test đang làm (`uv run pytest -q <file>`); chạy toàn bộ `uv run pytest -q` một lần ở cuối. Không chạy server hay tiến trình nền. Postgres local đã chạy sẵn (`deploy/compose.local.yml`, service `postgres`); dùng `HAIDO_TEST_DATABASE_URL=postgresql+psycopg://haido:haido_local@localhost:5433/haido_test`. DB `haido_test` đã tạo sẵn; không đụng DB `haido`.

**Execution:**
- [x] `pyproject.toml`, `tests/conftest.py` -- `[project.scripts] haido = "haido_core.cli:main"`; marker `postgres`; fixture DB đọc `HAIDO_TEST_DATABASE_URL` (chỉ host local, kiểm bằng `validate_migration_target`), mỗi test dựng lại schema `haido` bằng `alembic upgrade head` và bảng scraper từ `scraper/schema.sql`, skip khi không có URL -- hạ tầng TDD
- [x] Test đỏ `tests/core/test_ad10_rules_config.py` rồi code xanh `config/rules.toml`, `haido_core/config.py` -- `config_version`, `window_days = 60`, `sources.auto` (bảy nguồn của `scraper/ingest.py:37`); thiếu khóa thì lỗi tiếng Việt
- [x] Test đỏ `tests/db/test_ad4_snapshot_schema.py` rồi code xanh `haido_core/db/migrations/versions/0002_haido_snapshot.py`, `haido_core/db/tables.py`, `haido_core/db/engine.py` -- schema `haido`, sáu bảng ở Design Notes, trigger chặn `UPDATE`/`DELETE` trên quan sát và dữ kiện tin, `CHECK` trạng thái; downgrade xóa sạch schema; engine kiểm host đích và đặt nguồn chỉ-đọc
- [x] Test đỏ `tests/steps/test_ad4_ingest.py` rồi code xanh `haido_core/steps/ingest.py` -- các dòng Matrix về ingest; `open_snapshot`; đọc nguồn qua một interface nhỏ để test thuần không cần DB
- [x] Test đỏ `tests/steps/test_ad4_lifecycle_step.py` rồi code xanh `haido_core/steps/lifecycle.py` -- ba lượt liền, đêm lỗi, mất rồi đăng lại, S đã chốt, lưu `config_version`; một test `determinism` chạy hai lần ra cùng hàng
- [x] Test đỏ `tests/test_ad4_cli.py` rồi code xanh `haido_core/cli.py` -- `haido ingest|lifecycle --snapshot S`, mặc định S là hôm nay theo `Asia/Ho_Chi_Minh`, mã thoát, lỗi khi thiếu URL không in mật khẩu
- [x] `.github/workflows/ci.yml` -- job `python` thêm service `postgres:18.6` và `HAIDO_TEST_DATABASE_URL`; giữ tên job -- để test `postgres` chạy thật
- [x] `README.md`, `deploy/.env.example` -- lệnh CLI, `HAIDO_SCRAPER_DATABASE_URL`, `HAIDO_ALLOW_REMOTE_WRITE`, cách nạp từ Supabase chỉ-đọc vào Postgres local -- DoD dòng 14

**Acceptance Criteria:**
- Given Postgres trống, when `alembic upgrade head` rồi `alembic downgrade base`, then cả hai thành công, có đúng một head, và schema `haido` không còn sau downgrade.
- Given bảng scraper có lượt chạy và quan sát của ngày S, when chạy `haido ingest --snapshot S` rồi `haido lifecycle --snapshot S`, then S ở trạng thái `open`, mọi quan sát có `pipeline_run_id`, và mỗi tin đã thấy có một hàng `stat_job_lifecycle` kèm `config_version`.
- Given code của story, when CI chạy, then test `postgres` chạy thật (không skip) trong job `python`, và cổng kiến trúc xanh.

## Implementation Notes

Vòng đỏ-xanh (mỗi vòng chạy đúng file test, đỏ vì chưa có hành vi: stub `NotImplementedError` hoặc bảng chưa tồn tại, không phải lỗi import):

- `tests/core/test_ad10_rules_config.py`: 7 đỏ (`load_rules` chưa cài) -> xanh sau `config/rules.toml` + `haido_core/config.py`.
- `tests/db/test_ad4_snapshot_schema.py` + `tests/db/test_ad4_engine.py`: 15 đỏ (migration 0002 rỗng nên không có bảng; engine chưa cài) -> 27 xanh cùng `test_ad25_alembic.py` sau migration, `tables.py`, `engine.py`.
- `tests/steps/test_ad4_ingest.py`: 22 đỏ (`plan_ingest`, reader, store chưa cài) -> 22 xanh.
- `tests/steps/test_ad4_lifecycle_step.py`: 12 đỏ (`lifecycle_snapshot` chưa cài) -> 12 xanh.
- `tests/test_ad4_cli.py`: 10 đỏ (`main` chưa cài) -> 10 xanh.

Điểm cần biết:

- User Postgres trùng tên schema `haido` thì `search_path` mặc định (`"$user"`) tìm schema `haido` trước `public`; `scraper_source.py` và fixture test ghi rõ `public.` cho bảng của scraper.
- `job_posting_facts` có PK `(posting_id, snapshot_id)` nên mỗi S tối đa một phiên bản: chạy lại `ingest` cho S đang `open` khi scraper đã đổi dữ kiện thì giữ bản đầu của S (`ON CONFLICT DO NOTHING`), bản mới vào ở S sau.
- `ingest` chạy lại không xóa `stat_job_lifecycle` đã tính của S; cần chạy lại `lifecycle` sau khi `ingest` lại.
- Lệnh `haido` chưa cài được: dự án không có `[build-system]` (Dockerfile API chỉ copy `haido_core`, `haido_api`), nên dùng `python -m haido_core.cli`.
- Windows: `localhost` cho Postgres local mất cỡ 8 giây mỗi kết nối vì thử IPv6 trước; test chạy với `127.0.0.1`.

- Sửa theo rà soát lượt 1 (E1–E13 ở Review Triage Log), bằng một subagent mới chỉ nhận danh sách lỗi:
  - E1: `insert_facts` trả số hàng thật sự thêm; `facts_added` dùng số đó.
  - E2: không thêm phiên bản dữ kiện tại S cho tin đã có quan sát ở snapshot sau S (`observed_after`).
  - E3: DB test phải có tên kết thúc bằng `_test`, kiểm trước mọi lệnh `DROP`.
  - E4–E7, E11: thêm hoặc sửa test (host qua query, `REPEATABLE READ`, `AUTO_SOURCES` của scraper, văn bản JD không vào `haido`, SQLSTATE `25006`).
  - E8–E10, E12, E13: README dùng `python -m haido_core.cli`; dispose engine trong `finally`; bắt `OSError`/`UnicodeDecodeError` khi đọc config; `CI` chỉ nhận `1`/`true`/`yes`; `connect_timeout=10`.
- Kiểm (06/11/2026, sau khi sửa): 230 test xanh với `HAIDO_TEST_DATABASE_URL`, 0 skip; không có URL thì 40 skip; hai lượt `-m determinism` (seed 0 và 1) xanh; `ruff` sạch; cổng `--require AD-1 AD-17 AD-25 AD-2 AD-7` 0 failed; Alembic một head.

## Spec Change Log

## Review Triage Log

Lượt 1 (06/11/2026). Lớp: BH = blind-hunter (Sonnet), EC = edge-case-hunter (Sonnet), VG = verification-gap (Opus). Model của reviewer do người sở hữu spec chọn, khác mặc định "cùng model với phiên chính". Không có `intent_gap` hay `bad_spec`.

| ID | Phát hiện | Verdict | Bằng chứng | Hướng |
|---|---|---|---|---|
| BH-1, EC-1, VG-2, VG-khác-1 | Chạy lại `ingest` cho S đang `open` sau khi scraper đổi dữ kiện cùng ngày: bản mới bị `DO NOTHING` bỏ nhưng `facts_added` vẫn đếm; nhánh xung đột không có test | medium | `facts_at(S)` gồm cả bản của S nên bản khác vào `new_facts`; PK `(posting_id, snapshot_id)` chặn ghi. Đến từ VG: đổi `DO NOTHING` vẫn xanh | patch E1 |
| BH-3, EC-2 | Ingest một S cũ hơn snapshot đã có (nạp bù, lệch thứ tự) ghi dữ kiện hiện tại của `jobs` vào S cũ và làm sai dữ kiện tại các S sau | medium | `jobs` chỉ giữ bản mới nhất; sau đó `facts_at(S sau)` lấy bản vừa ghi ở S cũ | patch E2 |
| BH-7, EC-6 | Fixture test xóa schema `haido`, `alembic_version` và bảng scraper của mọi DB local, kể cả DB `haido` của máy dev | medium | `pg_url` chỉ kiểm host, không kiểm tên DB | patch E3 |
| VG-1 | Chặn host lạ qua `?host=`/`?hostaddr=` của `make_write_engine` không có test | medium | Đến từ VG: bỏ vòng đọc query trong `_hosts` vẫn xanh | patch E4 |
| VG-3 | `REPEATABLE READ` của engine nguồn không có test | low | Đến từ VG: bỏ `isolation_level` vẫn xanh | patch E5 |
| VG-4 | `sources.auto` chỉ được so với bản chép trong test, không với `AUTO_SOURCES` của scraper | low | Đến từ VG: scraper đổi danh sách thì không test nào đỏ | patch E6 |
| BH-8 | Test riêng tư không chứng minh điều tên nó nói: `count(*) == 1` luôn đúng; grep chữ `insert` trong mã nguồn vỡ khi có comment | low | Không có kiểm tra nào cho thấy văn bản mô tả không vào schema `haido` | patch E7 |
| BH-11 | README ghi lệnh `haido ingest` nhưng lệnh không cài được | low | Dự án không có `[build-system]` | patch E8; đóng gói ghi deferred |
| EC-10 | `make_source_engine` lỗi thì engine đích không được dispose | low | Hai engine tạo ngoài `try` | patch E9 |
| EC-7 | `rules.toml` không đọc được (quyền, không phải UTF-8) ra traceback thay vì lỗi tiếng Việt | low | Chỉ bắt `FileNotFoundError` | patch E10 |
| EC-12 | Test chỉ-đọc so chữ tiếng Anh `read-only` | low | Postgres đổi `lc_messages` thì test đỏ dù hành vi đúng; nên so SQLSTATE `25006` | patch E11 |
| EC-13 | `CI=false` vẫn bị coi là CI | low | `os.environ.get("CI")` là chuỗi khác rỗng | patch E12 |
| BH-12a | Không có `connect_timeout`: host không tới được thì lệnh treo lâu | low | VPS đã gặp Supabase chỉ có IPv6; hai engine không đặt timeout | patch E13 |
| BH-2, EC-3 | Chạy lại không xóa được quan sát khi ngày của scraper "co lại" | false | `job_observations` của scraper cũng chỉ thêm (`ON CONFLICT DO NOTHING`), nên mọi URL đã ghi cho S vẫn còn ở nguồn; bản chép khớp nguồn | reject |
| EC-4 | `seen_count` khác số quan sát thì chấp nhận bản chép thiếu | false | Đọc nguồn không có `LIMIT`; chênh lệch chỉ do scraper chạy lại cùng ngày, và được chép đúng như nguồn | reject |
| BH-4, EC-11, VG-khác-2 | Mỗi lần chạy nạp toàn bộ tin, dữ kiện, quan sát của lịch sử | low | Vài nghìn tin mỗi ngày còn nhẹ; `lifecycle` cần cả lịch sử để đếm số lần thấy; sửa là viết lại truy vấn | reject |
| BH-5 | Schema không ép quan sát và lượt chạy cùng S, cùng nguồn; thiếu `CHECK` cho `seen_count`, `closed_at`; `sources_failed` chưa ai ghi | low | Code luôn ghi đúng cặp; chỉ SQL tay mới lệch; `sources_failed` do `publish` của #69 ghi | reject |
| EC-5 | DB không chặn `INSERT` vào snapshot đã chốt | low | Chỉ SQL tay hoặc code sau này chạm tới; hai bước hiện có đều từ chối | reject |
| BH-6 | "Chỉ-đọc phía DB" nói quá; nên dùng role chỉ-đọc | false | Engine luôn mở `BEGIN READ ONLY`, code không có `READ WRITE`; test thấy `INSERT`/`DELETE` bị từ chối | reject |
| BH-9 | Mỗi test dựng lại DB, không chạy song song được | low | Dự án không dùng `pytest-xdist`; 224 test chạy 21 giây | reject |
| BH-10, EC-8 | Đường dẫn `rules.toml` theo cấu trúc repo, không có biến ghi đè; `sources = 3` báo "thiếu khóa" | low | Dự án chưa đóng gói nên luôn chạy từ repo; sửa cần thêm nhánh | reject |
| BH-12b, EC-9 | Lỗi DB không nói phía nguồn hay đích; lỗi ngoài danh sách ra traceback | low | Lỗi ngoài danh sách vẫn thoát mã 1; mọi lỗi DB qua `SQLAlchemyError` nên không lộ URL | reject |
| BH-13 | Phân tích ngày hai lần; S đã chốt mà không có dữ liệu báo "chưa có lượt chạy"; hai lệnh qua nửa đêm lấy hai ngày; docstring `replace_lifecycle` | low | S đã chốt luôn còn dữ liệu ở nguồn (nguồn chỉ thêm); qua nửa đêm thì `lifecycle` báo "chưa mở", lỗi rõ ràng | reject |
| BH-14 | README ghi cổng AD-2, AD-7 mà diff không đổi CI; ảnh `postgres:18.6` chưa chắc khớp local; downgrade xóa dữ liệu | false | `ci.yml` trên `main` đã `--require AD-2 AD-7` từ #74; `compose.local.yml` cũng `postgres:18.6`; downgrade xóa schema là chủ ý | reject |
| EC-14 | Tin chỉ thấy trong lượt lỗi không có hàng vòng đời | false | `job_lifecycle` tính vòng đời trên lượt thành công (AD-4, FR-3); dòng Matrix "Đêm lỗi" đòi đúng vậy | reject, báo #69 |
| EC-15 | `pipeline_runs` bị ghi đè khi chạy lại, trái "chỉ thêm" | false | Frozen chỉ đòi quan sát và dữ kiện chỉ thêm; Design Notes cho phép cập nhật lượt chạy của S đang `open` | reject |

## Design Notes

Sáu bảng trong schema `haido`:

```text
snapshots(snapshot_id DATE PK, status open|published|partial, opened_at, closed_at, sources_failed TEXT[])
pipeline_runs(id PK, snapshot_id FK, source, mode auto|manual, success, seen_count, error; UNIQUE(snapshot_id, source))
job_postings(id PK, source, source_url; UNIQUE(source, source_url))
job_posting_facts(posting_id FK, snapshot_id FK, title, company, location_text, experience_level, job_level; PK(posting_id, snapshot_id))
job_observations(posting_id FK, snapshot_id FK, pipeline_run_id FK; PK(posting_id, snapshot_id))
stat_job_lifecycle(snapshot_id FK, posting_id FK, times_seen, first_seen, last_seen, repost_count, absent, in_window, config_version; PK(snapshot_id, posting_id))
```

- `job_postings` chỉ giữ danh tính tin. Dữ kiện nằm ở `job_posting_facts`. Giữ thô `experience_level` và `job_level`, để #69 tự ghép `seniority_text`.
- `pipeline_runs` của S đang `open` được cập nhật theo `source_runs` mới nhất của scraper (ví dụ chạy lại một nguồn). Sau khi S chốt thì không đổi nữa.
- `id` của `job_postings` (dạng chuỗi) là `job_id` của `Observation` khi gọi `job_lifecycle`.
- Khi Story 1.2 và 1.3 chuyển crawl vào `haido_core`, chỉ phần đọc nguồn của `ingest` đổi. Bảng và bước `lifecycle` giữ nguyên.

## Verification

**Commands:**
- `uv run ruff check .`, `uv run pytest -q` -- expected: xanh, test có marker `postgres` chạy thật khi có `HAIDO_TEST_DATABASE_URL`
- `python tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7` -- expected: `0 failed`
- `uv run alembic upgrade head` rồi `uv run alembic downgrade base` trên Postgres local -- expected: thành công, một head
