# Implementation Plan: Build image kho trong workflow deploy

**Branch**: `gh-273-image-kho` | **Date**: 2026-11-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification từ `specs/273-image-kho-trong-deploy/spec.md`

## Summary

Thêm `warehouse` vào matrix build của `deploy.yml`. Script deploy kéo image kho cùng tag và, khi bản deploy khỏe, ghi tag vào `.warehouse-tag`. `compose.scraper.yml` bỏ `build` của kho, dùng image GHCR với tag từ biến. `daily.sh` đọc tag trước khi chạy kho. Workflow chép `compose.scraper.yml` và `daily.sh` lên VPS; `daily.sh` có mode `100755`.

## Technical Context

**Language/Version**: GitHub Actions, Bash, Docker Compose v2

**Primary Dependencies**: Không thêm action mới. Dùng lại `docker/metadata-action` và `docker/build-push-action` đang có.

**Storage**: Không đổi DB. Thêm một file trạng thái `.warehouse-tag` trên VPS.

**Testing**: `uv run pytest tests/deploy -q`

**Target Platform**: VPS, project scraper (`deploy`) và `haido-prod`.

**Constraints**: Nhịp một không được phụ thuộc image kho. Cron không có token GHCR. Không đổi `name` của project scraper.

**Scale/Scope**: Một image mới, ba file deploy, một script.

## Constitution Check

- AD-15: không build gì trên máy chủ prod. Kho trước đây build trên VPS; giờ build trên Actions như API và web.
- Spine "nhịp một không phụ thuộc": thiếu tag chỉ làm hỏng bước kho.
- Không viết spec vào `_bmad-output/`.

## Project Structure

### Documentation (this feature)

```text
specs/273-image-kho-trong-deploy/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── tasks.md
└── tdd.md
```

### Source Code (repository root)

```text
.github/workflows/deploy.yml
deploy/vps-deploy.sh
deploy/compose.scraper.yml
deploy/daily.sh            (mode 100755)
tests/deploy/test_gh273_image_kho.py
tests/deploy/test_daily_warehouse.py
```

**Structure Decision**: Tag đi qua một file trên VPS chứ không qua `.env`, vì `.env` chứa secret và do người quản trị viết tay; script deploy không ghi vào đó. Image kho không vào `compose.prod.yml`, vì `up -d` sẽ chạy nó như service.

## Complexity Tracking

- `tests/deploy/test_daily_warehouse.py` là test của #90 (chưa có `specs/`): đổi chuỗi `haidoit-warehouse:local` sang image GHCR.
- `deploy/vps-deploy.sh` và `.github/workflows/deploy.yml` thuộc #262: cập nhật `specs/262-bat-deploy/` cùng commit.
