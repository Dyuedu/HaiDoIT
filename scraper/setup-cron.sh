#!/bin/bash
# Setup daily cron job for HaiDoIT scraper pipeline on EC2
# Usage: bash setup-cron.sh

SCRAPER_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="/var/log"
CRON_CMD="0 2 * * * cd $SCRAPER_DIR && /usr/bin/python3 pipeline.py all >> $LOG_DIR/haidoit-pipeline.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "haidoit"; then
    echo "Cron job already exists:"
    crontab -l | grep "haidoit"
    echo "Remove it first with: crontab -e"
    exit 0
fi

# Add cron job
(crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -

echo "Cron job installed:"
echo "  $CRON_CMD"
echo ""
echo "Pipeline runs daily at 02:00 AM server time."
echo "Logs: $LOG_DIR/haidoit-pipeline.log"
echo ""
echo "Required env vars (add to ~/.bashrc or /etc/environment):"
echo "  ANTHROPIC_API_KEY=sk-ant-..."
echo "  TYPESAFE_API_KEY=..."
echo "  SUPABASE_URL=https://xxx.supabase.co"
echo "  SUPABASE_SERVICE_KEY=eyJ..."
