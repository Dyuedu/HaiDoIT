# Feature Specification: Bật deploy lên VPS

**Feature Branch**: `gh-262-bat-deploy`

**Created**: 2026-11-10

**Status**: Đường deploy đã ở `main` (#268, #269), `DEPLOY_ENABLED` đã bật. Đợt 3 (2026-11-10) chuyển script chạy trên VPS ra `deploy/vps-deploy.sh` sau khi run 42851541091 lỗi cú pháp bash. Đợt 4 (2026-11-11, #273): workflow build thêm image kho, script deploy kéo nó và ghi `.warehouse-tag`.

**Input**: GitHub issue [#262](https://github.com/Dyuedu/HaiDoIT/issues/262) — Merges to `main` reach the VPS: the deploy workflow is switched on, the production compose file is on the VPS, and migrations run as a deploy step.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Merge vào main cập nhật API và web (Priority: P1)

Người merge vào `main` thấy API và web trên VPS đổi theo commit đó. Cổng sức khỏe của API và web trả lời được.

**Why this priority**: Tiêu chí cuối của issue. Không có nhịp này thì bản đồ production không nhận code mới.

**Independent Test**: Workflow khai `vars.DEPLOY_ENABLED == 'true'`. Script trên VPS kéo image `sha-<commit>` rồi kiểm `http://127.0.0.1:8000/openapi.json` và `http://127.0.0.1:3000`.

**Acceptance Scenarios**:

1. **Given** `DEPLOY_ENABLED` là `true` và secret SSH đã có, **When** một commit chạm API hoặc web được đẩy lên `main`, **Then** workflow build image, kéo lên VPS và hai cổng localhost trả lời.
2. **Given** `DEPLOY_ENABLED` khác `true`, **When** có push lên `main`, **Then** workflow bỏ qua, không đỏ.

---

### User Story 2 - File compose production nằm trên VPS và không dọn scraper (Priority: P1)

`compose.prod.yml` của đúng commit được chép tới `VPS_PATH` trước khi `up`. `docker compose up -d --remove-orphans` chỉ đụng project `haido-prod`.

**Why this priority**: Tiêu chí thứ hai. Cùng project với scraper thì `--remove-orphans` xóa container scraper và kho.

**Independent Test**: Workflow có bước `scp` file compose. `compose.prod.yml` đặt `name: haido-prod`. `compose.scraper.yml` không dùng tên đó và không bị file prod khai báo service `scraper` hay `warehouse`.

**Acceptance Scenarios**:

1. **Given** thư mục VPS đang có `compose.scraper.yml`, **When** deploy chạy, **Then** `compose.prod.yml` được ghi đè bằng bản của commit, còn file scraper giữ nguyên.
2. **Given** container scraper thuộc project khác `haido-prod`, **When** `up -d --remove-orphans` chạy với `compose.prod.yml`, **Then** container scraper không nằm trong tập bị dọn.

---

### User Story 3 - Migration chạy trước khi API mới khởi động (Priority: P1)

`alembic upgrade head` chạy trong image API vừa kéo, với `HAIDO_ALLOW_REMOTE_MIGRATION=1`, và lệnh đó đứng trước `up -d`. Lỗi migration thì không `up`.

**Why this priority**: Tiêu chí thứ ba. API mới khởi động trên schema cũ sẽ đọc bảng chưa có.

**Independent Test**: Trong script deploy, vị trí chữ `alembic upgrade head` đứng trước `up -d --remove-orphans`. Dòng migrate có `--no-deps`, cờ remote đúng `1`, và `< /dev/null`.

**Acceptance Scenarios**:

1. **Given** image API của commit đã được `pull`, **When** deploy tiếp tục, **Then** một container một lần chạy `alembic upgrade head` rồi mới `up` api và web.
2. **Given** Alembic trả mã khác 0, **When** script có `set -euo pipefail`, **Then** `up` không chạy.

---

### User Story 4 - Đổi khóa phụ thuộc thì build lại (Priority: P2)

Sửa `pyproject.toml`, `uv.lock`, `alembic.ini` hoặc `.dockerignore` cũng kích hoạt workflow, dù không đụng thư mục ứng dụng.

**Why this priority**: Tiêu chí thứ tư. Image cài gói và copy các file này lúc build. Không có đường dẫn này thì merge chỉ đổi khóa mà VPS vẫn chạy image cũ.

**Independent Test**: `on.push.paths` của `.github/workflows/deploy.yml` chứa bốn đường dẫn đó.

**Acceptance Scenarios**:

1. **Given** một commit chỉ sửa `uv.lock`, **When** đẩy lên `main` và deploy đang bật, **Then** workflow được chạy.

---

### User Story 5 - Deploy không cắt web khỏi proxy công khai (Priority: P1)

`haidoit.io.vn` đi qua Nginx Proxy Manager ở project Compose riêng `haido-proxy`. Proxy tới web qua mạng ngoài `haido-edge`. Mỗi lần deploy, web vẫn ở trong mạng đó.

**Why this priority**: Trên VPS, web đang nằm trong `haido-edge` và tên miền trả 200. Nếu `compose.prod.yml` của `main` không khai mạng này, lần deploy đầu sẽ tạo lại web ngoài mạng và tên miền sập. Không bật được `DEPLOY_ENABLED` trước khi sửa.

**Independent Test**: `compose.prod.yml` cho `web` vào `default` và `edge`, còn `api` không vào `edge`. `edge` là mạng ngoài tên `haido-edge`. Script deploy tạo mạng khi chưa có, trước `up -d --remove-orphans`. `compose.proxy.yml` có `name: haido-proxy` và cổng quản trị 81 chỉ trên `127.0.0.1`.

**Acceptance Scenarios**:

1. **Given** proxy đang chạy trong project `haido-proxy`, **When** deploy chạy `up -d --remove-orphans` với `compose.prod.yml`, **Then** container proxy không bị dọn và web vẫn trong `haido-edge`.
2. **Given** VPS mới chưa có mạng `haido-edge`, **When** deploy chạy, **Then** mạng được tạo trước `up` và `up` không lỗi vì thiếu mạng ngoài.
3. **Given** cổng 81 của proxy, **When** nhìn từ Internet, **Then** không mở được. Chỉ vào được qua `ssh -L 81:127.0.0.1:81`.

---

### Edge Cases

- Script chạy trên VPS không nhúng heredoc trong workflow. Heredoc không nháy làm `\\\"` thành `\\"` và mở một chuỗi không đóng (run 42851541091, `unexpected EOF`). Script nằm ở `deploy/vps-deploy.sh`, biến đi trước qua stdin bằng `printf %q`, và `main` chạy ở dòng cuối nên bash đọc hết script trước khi lệnh docker nào chạy.
- `.env` có thể có CRLF và nháy đơn hoặc kép quanh URL. Script bỏ cả hai trước khi dùng.
- `docker compose run` đọc stdin. Script đi qua `bash -s` phải gắn `< /dev/null` vào lệnh migrate, nếu không phần còn lại của script bị nuốt.
- `HAIDO_ALLOW_REMOTE_MIGRATION` chỉ nhận đúng `1`. Giá trị `true` bị Alembic từ chối.
- Không có `GHCR_PULL_TOKEN` thì dùng `GITHUB_TOKEN` của chính job (workflow đã có `packages: write`). Cả hai đều trống thì dừng trước `pull`, không in token.
- `HEALTHCHECK_URL` vẫn tùy chọn. Cổng bắt buộc là hai địa chỉ localhost trên VPS.
- Không đặt `name` mới cho `compose.scraper.yml`. Project scraper hiện lấy theo tên thư mục. Đổi tên sẽ tách volume dữ liệu crawl.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Workflow chỉ chạy job khi `vars.DEPLOY_ENABLED` bằng `true`.
- **FR-002**: Job deploy checkout đúng SHA rồi `scp deploy/compose.prod.yml` tới `$VPS_PATH/compose.prod.yml`.
- **FR-003**: `compose.prod.yml` giữ `name: haido-prod` và không khai service scraper hay warehouse.
- **FR-004**: Sau `pull`, chạy `alembic upgrade head` bằng service `api`, `--no-deps`, cờ `HAIDO_ALLOW_REMOTE_MIGRATION=1`, rồi mới `up -d --remove-orphans`.
- **FR-005**: `on.push.paths` gồm `pyproject.toml`, `uv.lock`, `alembic.ini`, `.dockerignore`, cùng các đường dẫn ứng dụng đã có.
- **FR-006**: Sau `up`, kiểm `http://127.0.0.1:8000/openapi.json` và `http://127.0.0.1:3000` trên VPS. Hết số lần thử thì job đỏ.
- **FR-007**: Không in URL cơ sở dữ liệu hay token ra log.
- **FR-009**: Script chạy trên VPS là file `deploy/vps-deploy.sh`, qua được `bash -n`, và workflow gửi nó qua stdin của `ssh ... bash -se`. Token kéo image đi qua stdin, không nằm trên dòng lệnh.
- **FR-010**: Từ #273, workflow còn build image kho, chép `compose.scraper.yml` và `daily.sh` (`scp -p`), và chạy cả khi đổi `config/**`. `vps-deploy.sh` kéo image kho cùng tag trước `docker logout` và chỉ ghi `.warehouse-tag` sau khi cổng sức khỏe qua. Chi tiết ở `specs/273-image-kho-trong-deploy/`.
- **FR-008**: `web` ở trong mạng ngoài `haido-edge`, `api` thì không. Script deploy tạo `haido-edge` khi chưa có, trước `up`. Proxy nằm ở project `haido-proxy`, cổng 81 chỉ trên localhost.

### Key Entities

- **Compose project**: Tên `haido-prod` cho API và web. Scraper đứng ở project khác.
- **Mạng `haido-edge`**: Mạng Docker ngoài, chung giữa `haido-proxy` và web của `haido-prod`.
- **Image tag**: `sha-<commit>` như workflow đang gắn vào `IMAGE_TAG`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `uv run pytest tests/deploy/test_gh262_bat_deploy.py tests/deploy/test_proxy_npm.py tests/deploy/test_gh262_vps_script.py` xanh.
- **SC-002**: `compose.prod.yml` có mặt tại `VPS_PATH` và `name` trong file đó là `haido-prod`.
- **SC-003**: Secret SSH mà workflow đọc (`VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`, `VPS_KNOWN_HOSTS`, `VPS_PATH`) đã tồn tại. Token kéo image dùng `GHCR_PULL_TOKEN` nếu có, không thì `GITHUB_TOKEN`.
- **SC-004**: Một lần chạy workflow trên `main` làm API và web trả lời ở hai cổng localhost. Biến `DEPLOY_ENABLED` chỉ được bật khi commit này đã ở `main`, để lần push trước đó không deploy bằng workflow cũ.

## Assumptions

- Image `deploy/api.Dockerfile` đã có `alembic`, `alembic.ini` và `haido_core/db/migrations`. Không thêm Dockerfile mới.
- File môi trường trên VPS có `DATABASE_URL` của scraper. Script deploy suy ra `HAIDO_DATABASE_URL` (thêm driver `postgresql+psycopg` khi thiếu) rồi để Compose nội suy. Script không in URL và không ghi thêm dòng vào file môi trường.
- `VPS_PATH` là thư mục đang chứa `compose.scraper.yml`. File scraper không bị workflow ghi đè.
