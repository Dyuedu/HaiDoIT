#!/usr/bin/env bash
# Chay tay TopCV tren may nguoi that, roi dua ket qua len VPS. Chay bang Git Bash:
#     bash deploy/topcv-manual.sh                 # crawl + day len + ghi DB
#     bash deploy/topcv-manual.sh --skip-crawl    # bo crawl, day ket qua da co
#     bash deploy/topcv-manual.sh --extract       # them trich xuat ngay (ton tien API)
#
# Khong co --extract thi lan chay nhip hai ke tiep (cron) se trich xuat cac tin nay.
#
# Khong dua file nay vao cron: TopCV ne Cloudflare (rui ro R1 cua PRD), nen no chi
# chay khi co nguoi chu dong bam. Ctrl+C luc crawl van xuat va day phan da tai.
set -uo pipefail

SKIP_CRAWL=0
EXTRACT=0
for arg in "$@"; do
  case "$arg" in
    --skip-crawl) SKIP_CRAWL=1 ;;
    --extract) EXTRACT=1 ;;
    *) echo "tham so khong hop le: $arg"; exit 2 ;;
  esac
done

cd "$(dirname "$0")/../scraper" || exit 1
PY=".venv/Scripts/python"
[ -x "$PY" ] || PY=".venv/bin/python"
export TOPCV_DB="../topcv_jobs.db"
COMPOSE="cd /opt/haidoit/deploy && docker compose -f compose.scraper.yml run --rm scraper"

die() { echo; echo "DUNG LAI: $*"; exit 1; }

# Kiem tra VPS truoc: crawl co the mat hang gio, dung de cuoi cung moi biet khong ket noi duoc.
ssh -o BatchMode=yes -o ConnectTimeout=15 haidoit true || die "khong ket noi duoc VPS (ssh haidoit)"

if [ "$SKIP_CRAWL" -eq 0 ]; then
  echo "=== 1/4 Crawl TopCV, co the mat nhieu gio. Ctrl+C de dung va day phan da tai."
  trap 'echo; echo "Da nhan Ctrl+C, xuat phan da tai..."' INT
  "$PY" -X utf8 -m crawlers.topcv
  trap - INT
  "$PY" -X utf8 -c "from crawlers.topcv import export_jsonl; export_jsonl()" || die "khong xuat duoc data/raw/topcv.jsonl"
fi

[ -s data/raw/topcv.jsonl ] || die "khong co data/raw/topcv.jsonl"
SEEN="$(ls -1 data/seen/*/topcv.json 2>/dev/null | sort | tail -1)"
[ -n "$SEEN" ] || die "khong co file data/seen/<ngay>/topcv.json"
SNAPSHOT="$(basename "$(dirname "$SEEN")")"

read -r COUNT COMPLETE <<< "$("$PY" -X utf8 -c "
import json, sys
d = json.load(open(sys.argv[1], encoding='utf-8'))
print(len(d['job_urls']), d['listing_complete'])" "$SEEN")"
echo "Ngay $SNAPSHOT: listing thay $COUNT tin, quet het: $COMPLETE"
[ "${COUNT:-0}" -gt 0 ] || die "listing 0 tin, nhieu kha nang bi Cloudflare chan. Khong co gi de gui."
[ "$COMPLETE" = "True" ] || echo "CANH BAO: listing chua quet het. Tin vang mat hom nay khong co nghia la da go."

RUNNING="$(ssh -o BatchMode=yes haidoit "docker ps -q --filter name=deploy-scraper | wc -l")"
[ "${RUNNING:-1}" -eq 0 ] || die "VPS dang chay pipeline (co the la cron). Doi xong roi chay: bash deploy/topcv-manual.sh --skip-crawl"

echo "=== 2/4 Chep file len VPS"
scp -q data/raw/topcv.jsonl haidoit:/tmp/topcv.jsonl || die "scp topcv.jsonl loi"
scp -q "$SEEN" haidoit:/tmp/topcv-seen.json || die "scp file seen loi"
ssh haidoit "docker run --rm -v deploy_scraper_data:/d -v /tmp:/t:ro alpine sh -c 'mkdir -p /d/seen/$SNAPSHOT && cp /t/topcv.jsonl /d/raw/topcv.jsonl && cp /t/topcv-seen.json /d/seen/$SNAPSHOT/topcv.json && chown -R 10001:10001 /d/raw/topcv.jsonl /d/seen/$SNAPSHOT' && rm -f /tmp/topcv.jsonl /tmp/topcv-seen.json" \
  || die "khong chep duoc vao volume"

echo "=== 3/4 Xoa lien he va ghi vao DB"
ssh haidoit "$COMPOSE pipeline.py redact && $COMPOSE ingest.py --sources topcv --snapshot $SNAPSHOT" \
  || die "redact hoac ingest loi"

if [ "$EXTRACT" -eq 1 ]; then
  echo "=== 4/4 Trich xuat bang Claude (ton tien API)"
  ssh haidoit "$COMPOSE pipeline.py dedupe && $COMPOSE pipeline.py process" || die "trich xuat loi; lan cron sau se thu lai"
else
  echo "=== 4/4 Chua trich xuat: lan cron ke tiep se lam, hoac chay lai voi --skip-crawl --extract"
fi

echo
echo "Xong: TopCV ngay $SNAPSHOT, $COUNT tin trong listing."
