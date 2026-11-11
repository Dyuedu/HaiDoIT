#!/usr/bin/env bash
# Chạy trên VPS. deploy.yml gửi qua stdin của `ssh ... bash -se`: vài dòng gán biến
# (VPS_PATH, SHA, ACTOR, PULL_TOKEN), rồi nguyên nội dung file này.
# Để file riêng, không nhúng heredoc trong workflow: escape nháy qua heredoc từng làm
# bash trên VPS lỗi cú pháp (run 42851541091).
set -euo pipefail

WAREHOUSE_IMAGE=ghcr.io/dyuedu/haidoit-warehouse
# daily.sh đọc tag image kho đã deploy từ file này, cùng thư mục VPS_PATH.
WAREHOUSE_TAG_FILE=.warehouse-tag

# Giá trị khóa $1 trong .env: bỏ CR cuối dòng và một cặp nháy bao ngoài.
env_value() {
  local line value
  line=$(grep -m1 "^$1=" .env || true)
  value=${line#*=}
  value=${value%$'\r'}
  case "$value" in
    \"*\") value=${value#\"}; value=${value%\"} ;;
    \'*\') value=${value#\'}; value=${value%\'} ;;
  esac
  printf '%s' "$value"
}

# URL kho: HAIDO_DATABASE_URL, không có thì suy từ DATABASE_URL của scraper. Không in ra log.
resolve_db_url() {
  local url base
  url=$(env_value HAIDO_DATABASE_URL)
  if [ -n "$url" ]; then
    printf '%s' "$url"
    return 0
  fi
  base=$(env_value DATABASE_URL)
  case "$base" in
    postgresql+psycopg://*) printf '%s' "$base" ;;
    postgresql://*) printf '%s' "postgresql+psycopg://${base#postgresql://}" ;;
    postgres://*) printf '%s' "postgresql+psycopg://${base#postgres://}" ;;
    *) echo "Không suy ra được URL kho" >&2; return 1 ;;
  esac
}

main() {
  : "${VPS_PATH:?}" "${SHA:?}" "${ACTOR:?}"
  cd "$VPS_PATH"

  HAIDO_DATABASE_URL=$(resolve_db_url)
  export HAIDO_DATABASE_URL

  if [ -z "${PULL_TOKEN:-}" ]; then
    echo "Thiếu token kéo image"
    exit 1
  fi
  printf '%s\n' "$PULL_TOKEN" | docker login ghcr.io -u "$ACTOR" --password-stdin
  unset PULL_TOKEN

  export IMAGE_TAG="sha-$SHA"
  docker compose -f compose.prod.yml pull
  # Image kho không phải service của compose.prod.yml: kéo riêng khi còn đăng nhập GHCR,
  # để cron đêm (không có token) chạy được bằng image có sẵn trên máy (#273).
  docker pull "$WAREHOUSE_IMAGE:$IMAGE_TAG"
  docker logout ghcr.io
  docker compose -f compose.prod.yml run --rm --no-deps -T -e HAIDO_ALLOW_REMOTE_MIGRATION=1 api alembic upgrade head < /dev/null
  docker network inspect haido-edge >/dev/null 2>&1 || docker network create haido-edge
  docker compose -f compose.prod.yml up -d --remove-orphans
  docker compose -f compose.prod.yml ps
  # 35 GB đĩa: không dọn thì image cũ ăn hết trong vài tuần
  docker image prune -f --filter "until=168h"

  local i
  for i in $(seq 1 20); do
    if curl -fsS --max-time 10 http://127.0.0.1:8000/openapi.json >/dev/null \
      && curl -fsS --max-time 10 -o /dev/null http://127.0.0.1:3000; then
      echo "sống sau $i lần thử"
      # Chỉ trỏ lịch đêm sang image kho mới khi bản deploy này đã khỏe. Ghi qua file tạm
      # rồi mv, để daily.sh không bao giờ đọc phải file ghi dở.
      printf '%s\n' "$IMAGE_TAG" > "$WAREHOUSE_TAG_FILE.tmp"
      mv "$WAREHOUSE_TAG_FILE.tmp" "$WAREHOUSE_TAG_FILE"
      echo "lịch đêm dùng $WAREHOUSE_IMAGE:$IMAGE_TAG"
      return 0
    fi
    sleep 6
  done
  echo "không phản hồi sau 2 phút"
  exit 1
}

# Test nạp file với HAIDO_DEPLOY_LIB_ONLY=1 để gọi riêng từng hàm.
# main chạy ở dòng cuối, nên bash đã đọc hết script khỏi stdin trước khi lệnh docker nào chạy.
if [ "${HAIDO_DEPLOY_LIB_ONLY:-}" != 1 ]; then
  main
fi
