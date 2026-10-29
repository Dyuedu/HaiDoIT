#!/usr/bin/env bash
# Hải Đồ IT - cào tin IT định kỳ (ITviec, TopDev, API ATS, Cốc Cốc) vào data/scraped/*.jsonl
# Mỗi lần chạy chỉ tải tin chưa cào (state lưu cạnh JSONL), nên chạy hằng ngày để tích luỹ dần.
# Lên lịch hằng ngày lúc 02:00 (crontab -e):
#   0 2 * * * cd /path/to/HaiDoIT && scraper/run_scrapers.sh
set -uo pipefail

LIMIT="${1:-1000}"
cd "$(dirname "$0")/.."
PY=python3
[ -x .venv/bin/python ] && PY=.venv/bin/python

mkdir -p data/scraped
LOG="data/scraped/run-$(date +%Y%m%d-%H%M).log"
ARGS=(-m scraper.jobboards --source all --limit "$LIMIT")
[ -n "${SCRAPER_CONTACT:-}" ] && ARGS+=(--contact "$SCRAPER_CONTACT")

echo "Cào mọi nguồn (tối đa $LIMIT trang/nguồn) -> $LOG"
"$PY" "${ARGS[@]}" >"$LOG" 2>&1
CODE=$?
grep -E "^(===|  [a-z_]+ +:|DỪNG|LỖI)" "$LOG"
case $CODE in
  0) echo "Xong." ;;
  3) echo "Có nguồn chặn bot - đã dừng nguồn đó, không vượt chặn." ;;
  *) echo "Lỗi (mã $CODE), xem $LOG" ;;
esac
exit $CODE
