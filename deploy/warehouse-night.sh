#!/bin/sh
# Một ngày snapshot: tạo schema haido nếu chưa có, rồi ingest, lifecycle,
# aggregate và publish. Ngày đã chốt thì published hoặc partial.
# URL lấy từ DATABASE_URL của scraper khi hai biến kho chưa được đặt.
# Không in URL.
set -eu

if [ -z "${HAIDO_DATABASE_URL:-}" ]; then
    base="${DATABASE_URL:-}"
    case "$base" in
        postgresql+psycopg://*)
            HAIDO_DATABASE_URL="$base"
            ;;
        postgresql://*)
            HAIDO_DATABASE_URL="postgresql+psycopg://${base#postgresql://}"
            ;;
        postgres://*)
            HAIDO_DATABASE_URL="postgresql+psycopg://${base#postgres://}"
            ;;
        *)
            echo "Lỗi: chưa có HAIDO_DATABASE_URL và DATABASE_URL không phải Postgres." >&2
            exit 1
            ;;
    esac
    export HAIDO_DATABASE_URL
fi

if [ -z "${HAIDO_SCRAPER_DATABASE_URL:-}" ]; then
    if [ -z "${DATABASE_URL:-}" ]; then
        echo "Lỗi: chưa có HAIDO_SCRAPER_DATABASE_URL." >&2
        exit 1
    fi
    export HAIDO_SCRAPER_DATABASE_URL="$DATABASE_URL"
fi

day="${1:-}"
if [ -z "$day" ]; then
    echo "Lỗi: thiếu ngày snapshot YYYY-MM-DD." >&2
    exit 1
fi

alembic upgrade head
python -m haido_core.cli ingest --snapshot "$day"
python -m haido_core.cli lifecycle --snapshot "$day"
python -m haido_core.cli aggregate --snapshot "$day"
python -m haido_core.cli publish --snapshot "$day"
