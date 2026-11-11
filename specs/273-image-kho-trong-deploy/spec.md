# Feature Specification: Build image kho trong workflow deploy

**Feature Branch**: `gh-273-image-kho`

**Created**: 2026-11-11

**Status**: Done. Merge qua PR #274; lượt đêm `2026-11-12` chạy kho bằng image GHCR `sha-cd57eb8` và chốt snapshot.

**Input**: GitHub issue [#273](https://github.com/Dyuedu/HaiDoIT/issues/273) — The nightly warehouse image is built from the same commit as the API and web, so the VPS never runs warehouse code that is older than `main`.

## Bối cảnh

Ngày 11/11/2026, bản đồ production báo "Chưa có snapshot nào đã công bố" dù lượt đêm đã công bố các snapshot 9, 10 và 11/11. Nguyên nhân: image `haidoit-warehouse:local` được build tay trên VPS từ một bản copy cũ của `/opt/haidoit`, chưa có commit `5a4d9e9` (#162, #259). Vì vậy `aggregate` không ghi `stat_sources`, và API bỏ qua mọi snapshot. Đã build lại tay từ `main` (`8938ba7`) để chữa tạm. Issue này bỏ bước làm tay.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Image kho build cùng commit với API và web (Priority: P1)

Mỗi lần deploy, workflow build image kho từ `deploy/warehouse.Dockerfile` và đẩy lên GHCR với tag `sha-<commit>`, như API và web.

**Why this priority**: AC thứ nhất. Đây là chỗ gây ra lỗi ngày 11/11.

**Independent Test**: `tests/deploy/test_gh273_image_kho.py` kiểm matrix của job `build` có `warehouse`.

**Acceptance Scenarios**:

1. **Given** một push lên `main` chạm `haido_core/`, **When** workflow deploy chạy, **Then** job build đẩy `ghcr.io/dyuedu/haidoit-warehouse:sha-<commit>`.
2. **Given** một push chỉ sửa `config/rules.toml`, **When** đẩy lên `main`, **Then** workflow cũng chạy, vì cả API lẫn kho đọc file này.

---

### User Story 2 - Lịch đêm chạy image kho của bản đã deploy (Priority: P1)

`daily.sh` chạy image kho có tag của lần deploy gần nhất đã khỏe, không build gì trên VPS.

**Why this priority**: AC thứ hai và thứ ba. Merge một thay đổi `haido_core/` thì đêm sau kho chạy code mới mà không ai phải vào VPS.

**Independent Test**: Test chạy `vps-deploy.sh` với `docker`, `curl`, `sleep` giả: deploy khỏe thì `.warehouse-tag` thành `sha-<commit>`, deploy hỏng thì giữ tag cũ. Test đọc `daily.sh` và `compose.scraper.yml`.

**Acceptance Scenarios**:

1. **Given** deploy kéo image API và web, **When** còn đăng nhập GHCR, **Then** script cũng `docker pull` image kho cùng tag, trước `docker logout`.
2. **Given** cổng sức khỏe qua, **When** script kết thúc, **Then** `$VPS_PATH/.warehouse-tag` chứa `sha-<commit>`, ghi qua file tạm rồi `mv`.
3. **Given** cổng sức khỏe không qua, **When** script thoát lỗi, **Then** `.warehouse-tag` giữ tag cũ, lịch đêm vẫn chạy image cũ.
4. **Given** `.warehouse-tag` có tag, **When** `daily.sh` tới bước kho, **Then** nó chạy `compose.scraper.yml` với `HAIDO_WAREHOUSE_TAG` bằng tag đó.
5. **Given** chưa có `.warehouse-tag`, **When** `daily.sh` tới bước kho, **Then** chỉ bước kho hỏng ("KHO HONG"), nhịp một và nhịp hai vẫn chạy.

---

### User Story 3 - Chép repo lên VPS không làm hỏng cron (Priority: P2)

`deploy/daily.sh` có mode `100755` trong git. Workflow chép `compose.scraper.yml` và `daily.sh` lên VPS bằng `scp -p`.

**Why this priority**: AC thứ tư. Ngày 11/11, chép code từ `main` lên VPS đã làm `daily.sh` mất quyền thực thi, phải `chmod` tay.

**Independent Test**: `git ls-files -s deploy/daily.sh` bắt đầu bằng `100755`. Workflow có dòng `scp -p deploy/compose.scraper.yml deploy/daily.sh`.

**Acceptance Scenarios**:

1. **Given** checkout repo, **When** đọc mode của `deploy/daily.sh`, **Then** là `100755`.
2. **Given** deploy chạy, **When** bước chép file xong, **Then** `compose.scraper.yml` và `daily.sh` trên VPS là bản của commit đó, `daily.sh` vẫn thực thi được.

---

### Edge Cases

- `compose.scraper.yml` dùng `${HAIDO_WAREHOUSE_TAG:-none}`, không dùng `:?`. Compose kiểm nội suy của cả file, nên `:?` sẽ làm hỏng cả lệnh chạy `scraper` khi thiếu tag, trái với nguyên tắc nhịp một không phụ thuộc gì.
- `pull_policy: never`: cron không có token GHCR, và image phải có sẵn từ lúc deploy.
- Rollback bằng `workflow_dispatch` với `sha` cũ: image kho của commit cũ cũng được kéo về, và `.warehouse-tag` trỏ về commit đó.
- `docker image prune -f` chỉ xóa image dangling, nên image kho có tag không bị xóa giữa hai lần deploy.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Matrix của job `build` có `warehouse` với `deploy/warehouse.Dockerfile`. Mỗi image một scope cache gha.
- **FR-002**: `on.push.paths` có `config/**`.
- **FR-003**: Job deploy chạy `scp -p deploy/compose.scraper.yml deploy/daily.sh` tới `$VPS_PATH/`.
- **FR-004**: `vps-deploy.sh` kéo `ghcr.io/dyuedu/haidoit-warehouse:sha-<commit>` trước `docker logout`.
- **FR-005**: `vps-deploy.sh` ghi `.warehouse-tag` chỉ sau khi cổng sức khỏe qua.
- **FR-006**: Service `warehouse` của `compose.scraper.yml` không có `build`, dùng image GHCR với tag lấy từ `HAIDO_WAREHOUSE_TAG`, `pull_policy: never`.
- **FR-007**: `daily.sh` đọc `.warehouse-tag`, thiếu thì báo và trả lỗi cho riêng bước kho.
- **FR-008**: `deploy/daily.sh` có mode `100755` trong git.

### Key Entities

- **`.warehouse-tag`**: một dòng `sha-<commit>` trong `VPS_PATH`. Do `vps-deploy.sh` ghi, `daily.sh` đọc.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `uv run pytest tests/deploy -q` xanh.
- **SC-002**: Sau merge, run deploy xanh; trên VPS có `ghcr.io/dyuedu/haidoit-warehouse:sha-<commit>` và `.warehouse-tag` trỏ tới nó.
- **SC-003**: Chạy bước kho qua đúng đường của `daily.sh` trên VPS dùng image GHCR, kết nối được DB.
- **SC-004**: Lượt đêm `2026-11-12` công bố snapshot có hàng trong `stat_sources`, và `/api/v1/city-shares` trả số.

## Assumptions

- `VPS_PATH` là `/opt/haidoit/deploy`, thư mục có `compose.scraper.yml`, `daily.sh` và `.env`.
- Package GHCR mới do `GITHUB_TOKEN` của workflow tạo gắn với repo, nên token của job deploy kéo được, giống image API và web.
