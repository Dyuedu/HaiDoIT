# Implementation Plan: Bật deploy lên VPS

**Branch**: `gh-262-bat-deploy` | **Date**: 2026-11-10 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification từ `specs/262-bat-deploy/spec.md`

## Summary

Sửa `.github/workflows/deploy.yml`: checkout ở job deploy, chép `compose.prod.yml` lên `VPS_PATH`, chạy `alembic upgrade head` trong container API một lần trước `up -d --remove-orphans`, rồi kiểm hai cổng localhost. Thêm bốn đường dẫn phụ thuộc vào `on.push.paths`. Giữ `name: haido-prod` để `--remove-orphans` không đụng project scraper.

## Technical Context

**Language/Version**: GitHub Actions, Bash, Docker Compose v2, Alembic 1.20.1 trong image API

**Primary Dependencies**: Không thêm gói. Image API đã cài Alembic và copy `alembic.ini`.

**Storage**: Không migration mới. Bước deploy chạy các revision đã có trên Supabase.

**Testing**: `uv run pytest tests/deploy/test_gh262_bat_deploy.py`

**Target Platform**: VPS hiện chạy cron scraper. API và web là project Compose riêng.

**Performance Goals**: Một lần deploy. Vòng kiểm sức khỏe tối đa 20 lần, mỗi lần cách 6 giây.

**Constraints**: Không in URL hay token. Cờ remote của Alembic đúng `1`. Không đổi `name` của `compose.scraper.yml`. `set -euo pipefail` nên migration lỗi thì không `up`. `docker compose run` phải `< /dev/null`.

**Scale/Scope**: Hai service `api` và `web`. Không đụng cron `daily.sh`.

## Constitution Check

- `compose.prod` không có `build:` và không chạy `next build` (AD-15). Web không có URL cơ sở dữ liệu (AD-1).
- Migration remote chỉ khi `HAIDO_ALLOW_REMOTE_MIGRATION=1` (đã có trong `haido_core/db/migrations/env.py`).
- Không viết spec vào `_bmad-output/`.

## Project Structure

### Documentation (this feature)

```text
specs/262-bat-deploy/
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
deploy/compose.prod.yml
deploy/compose.proxy.yml
tests/deploy/test_gh262_bat_deploy.py
tests/deploy/test_proxy_npm.py
```

**Structure Decision**: Sửa workflow và một test đọc file. Không thêm service vào `compose.prod.yml`. Đợt 2: proxy đứng file `compose.proxy.yml` với project riêng `haido-proxy`, chạy tay một lần trên VPS, workflow không đụng. Web vào thêm mạng ngoài `haido-edge`.

## Complexity Tracking

Không có vi phạm cần biện minh. Token kéo image dùng `GITHUB_TOKEN` của job khi không có PAT riêng, vì workflow đã khai `packages: write`. Không thêm secret thứ sáu chỉ để lặp lại quyền đó.
