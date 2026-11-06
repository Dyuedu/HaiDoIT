---
title: 'GH-1 [1.1] Mở khung Hải Đồ IT trên máy dev'
type: 'feature'
created: '2026-11-05'
status: 'done'
route: 'dispatch'
baseline_commit: '622d061bb65059261021347f07563cd8c3684a06'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/_bmad-output/planning-artifacts/DOD.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Chưa có web, Compose local hay Alembic, nên nhóm chưa có chỗ để hiện số, và CI chưa chặn được web nối Postgres hay import ngược chiều. #46, #9, #11 đang chờ nền này.

**Approach:** Hoàn thiện cây package, thêm `web/` Next.js với khung tối, `compose.local`, `compose.prod`, Alembic một head, rồi siết cổng CI. Dùng lại khung Python và `haido_api` của #2, không dựng bản thứ hai.

## Boundaries & Constraints

**Always:**
- Phiên bản theo bảng Stack của spine: Python 3.13, PostgreSQL 18.6, SQLAlchemy 2.1.6 kèm `greenlet`, Alembic 1.20.1, `psycopg[binary]==3.3.7`, Next.js 16.4.4, React 19.3.1, Tailwind 4.3.4, Node 24.
- Màu và chữ lấy từ `DESIGN.md`: nền `#070B10`, header `#0A1017`, Be Vietnam Pro. Nav tên "Điều hướng chính", đúng bốn mục: Bản đồ, Insights, Cố vấn, Soi tin; đúng một mục có `aria-current="page"`.
- Code Python đọc `HAIDO_DATABASE_URL`, luôn dạng `postgresql+psycopg://`. `DATABASE_URL` là của `scraper/`, giữ nguyên.
- `compose.local` chỉ nối Postgres trong Compose: chuỗi kết nối viết tại chỗ với host `postgres`, không `env_file`, không nhận biến kết nối từ môi trường. Compose tự đọc `deploy/.env` đang chứa chuỗi Supabase thật.
- Alembic từ chối host ngoài `localhost`, `127.0.0.1`, `postgres`, trừ khi đặt `HAIDO_ALLOW_REMOTE_MIGRATION=1`.
- Postgres local chỉ bind `127.0.0.1`. `compose.local` và `compose.prod` có `name:` riêng, không trùng project của `compose.scraper`.
- Trình duyệt gọi API cùng origin qua `/api/*`, bằng route handler chỉ nhận `GET`, đọc `API_BASE_URL` lúc chạy. Không bật CORS.
- Image đi theo `deploy.yml`: build trên Actions, tên `ghcr.io/dyuedu/haidoit-{api,web}:${IMAGE_TAG}`.

**Never:**
- Không tạo bảng tin, snapshot hay thống kê; migration đầu tiên rỗng.
- Không sửa `scraper/`, `compose.scraper.yml`, `daily.sh`, `deploy.yml`, `deploy/.env`; không kết nối Supabase, không in nội dung `deploy/.env`.
- Không làm màn Bản đồ thật (#46), chân trang chính sách (#11), `REGISTRY.md` (#3).
- Không thêm Dagster, Caddy; không bật `DEPLOY_ENABLED`, không deploy.

**Quyết định (05/11/2026):**
- #1 làm trên nhánh `dyuedu`, đã rebase lên `main` sau khi #2 merge (PR #71).
- `compose.prod` không có service Postgres; API đọc `HAIDO_DATABASE_URL`, vì nhóm chưa chốt giữa Supabase và Postgres tự chạy.
- Giữ spec trong một file dù dài hơn khuyến nghị, vì các AC thuộc một story và phụ thuộc nhau.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Web có chuỗi Postgres | File trong `web/` chứa `postgres://`, `postgresql://` hoặc `postgresql+psycopg://` | Cổng AD-1 FAIL, nêu file | Bỏ qua `node_modules`, `.next` |
| Web có driver | `web/package.json` có gói `pg` hoặc `postgres` | Cổng AD-1 FAIL | N/A |
| Import ngược | `haido_core` → `haido_api`, `haido_pipeline`; `haido_pipeline` → `haido_api`; `domain` → `haido_core.db`, `haido_core.steps` | Cổng AD-1 FAIL | N/A |
| Hai head | Hai migration cùng `down_revision` | Kiểm thử AD-25 đỏ | N/A |
| Migration nhầm kho | `HAIDO_DATABASE_URL` trỏ host khác, chưa đặt cờ | Alembic dừng trước khi kết nối, không in mật khẩu | Thông báo tiếng Việt |
| Prod tự build | `compose.prod` có `build:`, `next build` hoặc service Postgres | Kiểm thử AD-15 đỏ | N/A |
| Web nối DB | Service web có biến kết nối hoặc `depends_on: postgres` | Kiểm thử AD-1 đỏ | N/A |
| Rò Supabase | `compose.local` có `env_file`, `${DATABASE_URL}`, `${HAIDO_DATABASE_URL}`, hoặc khai biến kết nối không có giá trị | Kiểm thử đỏ | N/A |
| API không chạy | Gọi `/api/v1/...` qua web khi API tắt | 502, `{error: {code: "api_unavailable", message, snapshot_date: null}}` | Hình lỗi chuẩn |

</frozen-after-approval>

## Code Map

- `pyproject.toml`, `uv.lock` -- của #2: thêm SQLAlchemy, greenlet, Alembic, psycopg; dev thêm PyYAML. `testpaths` đã đúng. `extend-exclude` chưa có migrations, nên thêm `per-file-ignores` cho `haido_core/db/migrations/`
- `haido_api/main.py` -- của #2: `haido_api.main:app`, không sửa; healthcheck API dùng `/openapi.json`, không thêm route
- `haido_api/schemas/error.py` -- hình lỗi mà proxy web phải khớp; `snapshot_date` nhận `null`
- `tools/gates/check_gates.py` -- `gate_ad1_huong_phu_thuoc` chưa quét `web/`, `haido_core`, `haido_pipeline`; `gate_ad25_mot_head_alembic` đã nhận `haido_core/db/migrations/versions`
- `.github/workflows/ci.yml:49` -- `--require AD-1 AD-17`; `:129` job `alembic` đặt `DATABASE_URL`, phải đổi tên; job bật khi có `alembic.ini` ở gốc; job `web` cần `web/package-lock.json`, `npm run lint`, `npm run build`, và không có `API_BASE_URL`
- `.github/workflows/deploy.yml` -- cần `deploy/api.Dockerfile`, `deploy/web.Dockerfile`, context `.`, `IMAGE_TAG=sha-<SHA>`, `--remove-orphans`; đang skip vì `DEPLOY_ENABLED` tắt
- `_bmad-output/planning-artifacts/ux-designs/ux-HaiDoIT-2026-11-03/DESIGN.md` -- nguồn màu và chữ
- `deploy/.env.example` -- mẫu của VPS, chỉ thêm mục mới, không sửa dòng cũ
- `_bmad-output/implementation-artifacts/deferred-work.md` -- mục của #2 về cách web gọi API do spec này giải quyết

## Tasks & Acceptance

**Execution:**
- [x] `tests/tools/test_ad1_gate.py` -- viết trước, thấy đỏ: ba dòng đầu của Matrix, dùng thư mục tạm -- TDD
- [x] `tools/gates/check_gates.py` -- mở rộng AD-1 theo Matrix; cho `ROOT` đổi được khi test -- AC CI
- [x] `tests/db/test_ad25_alembic.py` -- viết trước, thấy đỏ: đúng một head; hai head thì đỏ; chặn host lạ và cờ cho phép; lỗi không chứa mật khẩu -- TDD
- [x] `alembic.ini`, `haido_core/db/migrations/` -- khởi tạo, `env.py` đọc `HAIDO_DATABASE_URL` và áp chặn host, sửa `script.py.mako` cho qua ruff, một migration rỗng -- AC một head
- [x] `haido_core/{db,crawl,extract,steps,vocab}/__init__.py`, `haido_pipeline/__init__.py` -- tạo phần cây còn thiếu -- AC cây package
- [x] `tests/deploy/test_compose_ad1_ad15.py` -- viết trước, thấy đỏ: ba dòng Compose của Matrix, đọc YAML thật và YAML mẫu vi phạm -- TDD
- [x] `deploy/api.Dockerfile`, `deploy/web.Dockerfile`, `.dockerignore` -- chỉ `COPY` đường dẫn cụ thể; web chạy `standalone`; loại `deploy/.env`, `*.db`, `chrome_topcv_profile/` -- khớp `deploy.yml`, không rò bí mật
- [x] `deploy/compose.local.yml`, `deploy/.env.example` -- Postgres 18.6, API, web, cả ba có healthcheck; mật khẩu local qua `HAIDO_LOCAL_DB_PASSWORD` có mặc định; cổng `127.0.0.1:${HAIDO_LOCAL_DB_PORT:-5433}` -- AC cùng lên
- [x] `deploy/compose.prod.yml` -- api và web dùng `image:` với `${IMAGE_TAG:?}`; API nhận `${HAIDO_DATABASE_URL:?}` -- AC không `next build`
- [x] `web/` -- Next.js, `app/layout.tsx`, `app-header`, trang `/` (Bản đồ) và trang giữ chỗ `/insights`, `/co-van`, `/soi-tin`; proxy `app/api/[...path]/route.ts` -- AC khung tối
- [x] `.github/workflows/ci.yml`, `.gitignore` -- `--require` thêm AD-25; job `alembic` đổi sang `HAIDO_DATABASE_URL`; bỏ qua `node_modules/`, `.next/` -- giữ cổng không quay lại SKIP
- [x] `_bmad-output/planning-artifacts/architecture/architecture-HaiDoIT-2026-11-03/ARCHITECTURE-SPINE.md` -- sửa dòng "image `web` build ở máy dev" thành build trên Actions -- khớp quyết định
- [x] `README.md`, `_bmad-output/implementation-artifacts/deferred-work.md` -- ghi lệnh chạy local; đánh dấu mục CORS đã xử lý -- DoD dòng 14

**Acceptance Criteria:**
- Given Docker trên máy dev, when chạy Compose local, then Postgres, API và web cùng healthy; web mở nền `#070B10`, wordmark "HẢI ĐỒ IT", chữ Be Vietnam Pro.
- Given Postgres local trống và URL trỏ `localhost`, when `alembic upgrade head` rồi `downgrade base`, then cả hai thành công và không có bảng nghiệp vụ nào.
- Given trang `/`, when đọc HTML, then nav có bốn mục và chỉ thẻ `<a>` Bản đồ mang `aria-current="page"`; given `/soi-tin`, then chỉ thẻ `<a>` Soi tin mang thuộc tính đó.
- Given API đang chạy, when gọi `/api/v1/city-shares?role=data_ai` qua cổng web, then nhận envelope của #2, không cần CORS; `API_BASE_URL` đổi lúc chạy không cần build lại.

## Implementation Notes

Giới hạn lệnh shell khi implement (lệnh ngoài danh sách sẽ làm dừng cả lượt chạy):

- Đọc và tìm file bằng công cụ đọc file theo đường dẫn trong Code Map. Không dùng lệnh shell để đọc nội dung file.
- Mỗi lần chỉ chạy một lệnh đơn, tham số không có ngoặc kép, dùng `/` trong đường dẫn. Không dùng pipe, `;`, `&&`, chuyển hướng (`2>&1`, `>`), `$`, hay biến môi trường đặt ngay trong lệnh.
- Chỉ được chạy: `uv run pytest` (tối đa 3 tham số), `uv run ruff check`, `uv run ruff format`, `uv sync`, `uv lock`, `uv run alembic heads`, `uv run alembic history`, `python tools/gates/check_gates.py`, `npm --prefix web ci`, `npm --prefix web install`, `npm --prefix web run <script>`, `Get-ChildItem`, `Test-Path`, `mkdir`.
- Viết tay khung Next.js và thư mục Alembic bằng công cụ ghi file; không chạy lệnh sinh mã. Không chạy `docker`, `git`, `alembic upgrade`: Claude tự chạy các lệnh Verification sau khi đọc diff.

## Spec Change Log

- 05/11/2026, trước lúc viết code: worker bị chặn vì spec ghi tên trần `deferred-work.md` nên phải dùng lệnh tìm file. Đã ghi đường dẫn đầy đủ trong Code Map và Tasks, thêm giới hạn lệnh vào Implementation Notes. Không đổi khối frozen, không có code cần giữ lại.

## Review Triage Log

| Phát hiện | Verdict | Route | Bằng chứng |
|---|---|---|---|
| .dockerignore mẫu chỉ khớp gốc context | medium | patch | Đúng ngữ nghĩa Docker; `web/.env.local` sẽ vào `COPY web`. Đã đổi sang `**/`. |
| Proxy thoát khỏi `/api` bằng `..%2f` | high | patch | Tái hiện: `/api/..%2f..%2fopenapi.json` trả 200. Đã từ chối segment xấu và mã hóa; nay 404. |
| `%3F` trong segment thành query upstream | medium | patch | Tái hiện: trả 200 với dữ liệu. Nay 404. |
| Proxy không có timeout upstream | medium | patch | API treo thì không có `api_unavailable`. Đã thêm `AbortSignal.timeout(10000)`. |
| Proxy không ghi log nguyên nhân lỗi | low | reject | Khó gặp lúc này, cần thêm logging; lỗi vẫn hiện rõ qua 502. |
| Non-GET và `/api` trần không có hình lỗi chuẩn | low | reject | POST nhận 405 đúng "chỉ nhận GET"; giao diện không gọi non-GET. |
| 204/205/304 làm constructor ném lỗi | low | reject | API hiện không có route trả các mã này; cần thêm nhánh. |
| Proxy bỏ header upstream ngoài content-type | low | reject | Chưa có client nào dùng; allowlist là phức tạp thêm. |
| Không có test tự động cho proxy, 502, aria-current | medium | patch | Đã thêm job CI `smoke`; script chạy được trên máy dev, chưa chạy trên Actions. |
| Docker image và Compose không được dựng trong CI | medium | patch | Cùng job `smoke`. |
| `deploy.yml` paths thiếu pyproject, uv.lock, alembic.ini | medium | defer | Spec cấm sửa `deploy.yml`. |
| Chưa có đường chạy migration trên prod, chưa chép compose.prod lên VPS | medium | defer | Thuộc lúc bật `DEPLOY_ENABLED`, chưa bật. |
| `.env.example` thiếu `HAIDO_ALLOW_REMOTE_MIGRATION`, thừa `API_BASE_URL` | low | patch | Sửa trực tiếp. |
| `${IMAGE_TAG:?}` không có thông điệp | false | reject | Spec ghi đúng dạng này. |
| `depends_on` prod không chờ healthy | low | reject | Proxy đã trả 502 chuẩn khi API chưa lên. |
| Validator prod bỏ sót command dạng list, entrypoint, name, image | medium | patch | Tái hiện bằng YAML mẫu; đã siết và thêm mẫu xấu. |
| Validator web bỏ sót `env_file` và service web vắng mặt | medium | patch | Đã siết và thêm mẫu xấu. |
| Validator local chấp nhận `$VAR` và host Supabase literal | medium | patch | Đã siết và thêm mẫu xấu, gồm `env_file` trong service. |
| Cổng AD-1 không đọc peer/optional, regex chỉ khớp `..`, domain thiếu psycopg/alembic | low | patch | Sửa trực tiếp. |
| Cổng AD-1 không biết driver khác (prisma, neon...) | low | reject | Matrix chỉ nêu `pg`, `postgres`; web không có lý do thêm các gói này. |
| Regex import nhiều dòng cần parse ast | low | reject | Khó gặp, phải viết lại cổng. |
| Cổng AD-1 in nội dung dòng chứa credential | medium | patch | Nay chỉ in file và số dòng. |
| `except: pass` khi quét web làm cổng PASS sai | low | patch | Nay ghi file không đọc được vào hits. |
| Test AD-1 thiếu biến thể Matrix, assert yếu, thiếu trường hợp sạch | medium | patch | Đã tham số hóa từng biến thể, thêm PASS trên cây sạch. |
| Cổng AD-25 PASS với 0 revision | medium | patch | Tái hiện: PASS. Nay FAIL. |
| Cổng AD-25 không hiểu `down_revision` tuple | medium | defer | Có từ trước story này; chỉ gặp ở migration merge đầu tiên. |
| Test AD-25 không chạy trên `0001_initial.py` thật | false | reject | Cổng chạy trên repo thật qua `--require AD-25` trong CI. |
| Chú thích `ci.yml` cũ về Alembic | low | patch | Sửa trực tiếp. |
| Mật khẩu chứa `@` lộ một phần trong lỗi | high | patch | Tái hiện: in `ssw0rd@db.supabase.co`. Lỗi nay không in host. |
| Driver `postgresql://` lọt kiểm tra | medium | patch | Tái hiện. Nay từ chối bằng tiếng Việt. |
| `::1` không có trong danh sách host | false | reject | Spec liệt kê đúng ba host. |
| Thiếu URL thì âm thầm dùng URL mặc định | medium | patch | Đã xóa fallback; báo "chưa được thiết lập". |
| Chặn host chưa được kiểm qua CLI Alembic | medium | patch | Đã thêm test subprocess có canary mật khẩu. |
| Nhánh không xác định được host chưa có test | low | patch | Đã thêm `test_ad25_rejects_url_without_host`. |
| `import re` thừa trong `script.py.mako` | low | patch | Xóa. |
| Container chạy root | medium | patch | Nay user `haido` và `node`; kiểm bằng `docker inspect`. |
| `node:24-alpine` không ghim, image chứa `uv` | low | reject | Spec chốt Node 24; không có hại cụ thể. |
| `compose.prod` không giới hạn bộ nhớ, không xoay log | medium | defer | Cần trước khi bật deploy; chưa có số đo. |
| Healthcheck API không phản ánh DB | false | reject | Spec chọn `/openapi.json`. |
| Mật khẩu local có `@ / :` làm hỏng URL | low | reject | Mặc định không có ký tự này; chỉ ở máy dev. |
| `pg_isready` qua socket báo healthy sớm trên volume mới | medium | patch | Đã dùng `-h 127.0.0.1`; dựng lại từ volume mới vẫn healthy. |
| Header tràn trên màn hẹp | medium | patch | `DESIGN.md` yêu cầu flex-wrap và nav cuộn ngang. Đã sửa. |
| Màu hard-code, thiếu `:focus-visible`, `color-scheme` | low | reject | Không ảnh hưởng AC của khung; xử lý cùng màn thật #46. |
| `aria-current` mất ở route con | low | reject | Chưa có route con. |
| `next-env.d.ts` là file sinh ra | low | patch | Thêm vào `.gitignore`. |
| README thiếu bước cài, lệnh không chạy trên PowerShell | medium | patch | Sửa trực tiếp. |
| Wordmark có dấu chấm, khác chuỗi trong AC | false | reject | `DESIGN.md`: "HẢI ĐỒ" + dấu + "IT". |

## Design Notes

PostgreSQL 18 đổi đường dẫn dữ liệu trong image: volume gắn vào `/var/lib/postgresql`, không gắn `/var/lib/postgresql/data`.

`rewrites` của Next.js chốt đích lúc build và lỗi khi thiếu biến, nên dùng route handler. Compose local build web bằng chính `deploy/web.Dockerfile`, để kiểm luôn image prod; `npm run dev` dành cho làm giao diện hằng ngày.

Khung Next.js và cấu hình được miễn test trước, kiểm bằng lệnh ở Verification. `compose.prod` tham chiếu image chưa có, nên chỉ kiểm bằng `config -q`. Trước khi bật `DEPLOY_ENABLED`, nhóm phải kiểm `VPS_PATH` vì `--remove-orphans`.

## Verification

**Commands:**
- `uv run pytest -q` -- expected: mọi kiểm thử xanh
- `uv run ruff check .` -- expected: không lỗi
- `python tools/gates/check_gates.py --require AD-1 AD-17 AD-25` -- expected: không FAIL
- `docker compose -f deploy/compose.local.yml up -d --wait` -- expected: cả ba service healthy
- `HAIDO_DATABASE_URL=postgresql+psycopg://haido:haido_local@localhost:5433/haido uv run alembic upgrade head`, rồi `downgrade base` -- expected: mã 0
- `IMAGE_TAG=x HAIDO_DATABASE_URL=postgresql+psycopg://u:p@h/d docker compose -f deploy/compose.prod.yml config -q` -- expected: mã 0; thiếu `IMAGE_TAG` thì khác 0. Không bỏ `-q`, vì sẽ in giá trị từ `deploy/.env`
- `npm --prefix web run lint` và `npm --prefix web run build` -- expected: thành công, không cần `API_BASE_URL`
- `curl -s localhost:3000/ | grep -oE '<a [^>]*aria-current="page"[^>]*>'` -- expected: một thẻ, trỏ `/`; làm lại với `/soi-tin`
- `curl -s "localhost:3000/api/v1/city-shares?role=data_ai"` -- expected: có `data` và `meta`; tắt API thì 502 `api_unavailable`
- Mở `localhost:3000` -- expected: wordmark, nền `#070B10`, font Be Vietnam Pro (kiểm trong DevTools)
