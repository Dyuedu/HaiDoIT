#!/usr/bin/env bash
# Hai nhip cua spine. Nhip mot khong duoc phu thuoc API key hay ket qua nhip hai:
# job_observations phai co hang moi moi ngay. Nhip hai hong thi mai chay lai.
set -uo pipefail

cd "$(dirname "$0")"
# Mui gio tuong minh: VPS dang o Europe/London, nhung AD-15 dinh nghia
# snapshot_id la YYYY-MM-DD theo Asia/Ho_Chi_Minh.
SNAPSHOT="$(TZ=Asia/Ho_Chi_Minh date +%F)"
LOG_DIR="${LOG_DIR:-/opt/haidoit/logs}"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/daily-$SNAPSHOT.log"

exec 9>"$LOG_DIR/daily.lock"
flock -n 9 || { echo "$(date -Is) luot truoc chua xong, bo qua" >> "$LOG"; exit 0; }

# Giu 30 ngay log, dia chi co 33 GB
find "$LOG_DIR" -name 'daily-*.log' -mtime +30 -delete

run() { docker compose -f compose.scraper.yml run --rm -e HAIDO_SNAPSHOT="$SNAPSHOT" scraper "$@"; }
run_browser() { docker compose -f compose.scraper.yml run --rm -e HAIDO_SNAPSHOT="$SNAPSHOT" scraper-browser "$@"; }
# Image kho do workflow deploy build va keo ve; vps-deploy.sh ghi tag cua ban da deploy
# vao .warehouse-tag (#273). Thieu file thi chi buoc kho hong, nhip mot van chay.
run_warehouse() {
  local tag
  tag="$(tr -d '[:space:]' < .warehouse-tag 2>/dev/null || true)"
  if [ -z "$tag" ]; then
    echo "chua co .warehouse-tag: chua deploy image kho nao"
    return 1
  fi
  echo "image kho: $tag"
  HAIDO_WAREHOUSE_TAG="$tag" docker compose -f compose.scraper.yml run --rm warehouse "$SNAPSHOT"
}

BEAT_ONE=0
{
  echo "=== $(date -Is) snapshot=$SNAPSHOT nhip mot"
  run pipeline.py crawl --sources zalo,itnavi,careerlink,vietnamworks,topdev
  run_browser pipeline.py crawl --sources momo,itviec
  run pipeline.py redact && run pipeline.py ingest
  BEAT_ONE=$?
  if [ "$BEAT_ONE" -eq 0 ]; then
    echo "=== $(date -Is) kho ingest+lifecycle+aggregate+publish snapshot=$SNAPSHOT"
    run_warehouse || {
      echo "KHO HONG: snapshot $SNAPSHOT"
      BEAT_ONE=1
    }
  else
    echo "NHIP MOT HONG, exit $BEAT_ONE: ngay nay co the mat quan sat"
  fi

  echo "=== $(date -Is) nhip hai"
  run pipeline.py dedupe && run pipeline.py process || echo "nhip hai hong, mai chay lai"
  echo "=== $(date -Is) xong"
} >> "$LOG" 2>&1
exit "$BEAT_ONE"
