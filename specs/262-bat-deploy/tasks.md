# Tasks: Bật deploy lên VPS

**Input**: Design documents from `specs/262-bat-deploy/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Tests**: Viết trước theo `tdd.md`. Test mới phải đỏ trước khi sửa workflow.

## Phase 1: User Story 4 - Đường dẫn build (Priority: P2)

- [x] T001 [US4] Test `on.push.paths` chứa `pyproject.toml`, `uv.lock`, `alembic.ini`, `.dockerignore` trong `tests/deploy/test_gh262_bat_deploy.py`

## Phase 2: User Story 2 - Compose trên VPS (Priority: P1)

- [x] T002 [US2] Test job deploy checkout và `scp deploy/compose.prod.yml`
- [x] T003 [US2] Test `name: haido-prod` khác project scraper và file prod không có service scraper

## Phase 3: User Story 3 - Migration trước API (Priority: P1)

- [x] T004 [US3] Test `alembic upgrade head` đứng trước `up -d --remove-orphans`, có `--no-deps`, cờ `1`, và `< /dev/null`

## Phase 4: User Story 1 - Cập nhật và sức khỏe (Priority: P1)

- [x] T005 [US1] Test kiểm `127.0.0.1:8000/openapi.json` và `127.0.0.1:3000` sau `up`
- [x] T006 [US1] Test vẫn khóa bằng `DEPLOY_ENABLED` và token kéo image có lối `GITHUB_TOKEN`

## Phase 5: Implementation

- [x] T007 Sửa `.github/workflows/deploy.yml` cho các test trên xanh
- [x] T008 Ghi chú `name: haido-prod` trong `deploy/compose.prod.yml`
- [x] T009 Chép `compose.prod.yml` lên `VPS_PATH` và đối chiếu secret SSH đã có

## Phase 6: User Story 5 - Web trong mạng proxy (Priority: P1, đợt 2026-11-10)

- [x] T010 [US5] Test `compose.proxy.yml` là project `haido-proxy`, cổng 81 chỉ localhost, mạng ngoài `haido-edge` trong `tests/deploy/test_proxy_npm.py`
- [x] T011 [US5] Test `web` vào `default` và `edge`, `api` không vào `edge`
- [x] T012 [US5] Test script deploy tạo `haido-edge` trước `up -d --remove-orphans`
- [x] T013 Thêm `deploy/compose.proxy.yml`, sửa `deploy/compose.prod.yml` và `.github/workflows/deploy.yml` cho các test trên xanh
- [ ] T014 Bật `DEPLOY_ENABLED`, merge, xem run deploy xanh, kiểm `haidoit.io.vn` và hai cổng localhost
