#!/usr/bin/env bash
# Nhip mot hang ngay: crawl 4 nguon HTTP -> dedupe -> sync vao Postgres.
# Ranh gioi khong duoc vuot: job_observations phai co hang moi moi ngay.
set -euo pipefail

cd "$(dirname "$0")"
SNAPSHOT="$(date +%F)"
LOG_DIR="${LOG_DIR:-/opt/haidoit/logs}"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/daily-$SNAPSHOT.log"

dc() { docker compose -f compose.scraper.yml "$@"; }

{
  echo "=== $(date -Is) snapshot=$SNAPSHOT"
  dc run --rm scraper pipeline.py crawl --sources zalo,itnavi,careerlink,vietnamworks || echo "crawl: co nguon loi, di tiep"
  dc run --rm scraper pipeline.py dedupe
  dc run --rm scraper sync_pg.py --snapshot "$SNAPSHOT"
  echo "=== $(date -Is) xong"
} >> "$LOG" 2>&1

# Giu 30 ngay log, dia chi co 33 GB
find "$LOG_DIR" -name 'daily-*.log' -mtime +30 -delete
