"""#302 — TopCV chạy trong lượt đêm, trong image scraper-browser."""

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DAILY = ROOT / "deploy" / "daily.sh"
SCRAPER_COMPOSE = ROOT / "deploy" / "compose.scraper.yml"
BROWSER_DOCKERFILE = ROOT / "scraper" / "Dockerfile.browser"
MANUAL = ROOT / "deploy" / "topcv-manual.sh"


def test_gh302_daily_crawls_topcv_in_browser_step() -> None:
    text = DAILY.read_text(encoding="utf-8")
    assert "run_browser pipeline.py crawl --sources momo,itviec,topcv" in text


def test_gh302_browser_image_has_chrome_xvfb_and_pinned_nodriver() -> None:
    text = BROWSER_DOCKERFILE.read_text(encoding="utf-8")
    assert "playwright==1.64.1" in text
    assert re.search(r"\bnodriver==\d+\.\d+", text)
    assert "google-chrome-stable" in text
    assert re.search(r"\bxvfb\b", text)
    assert "CHROME_PATH=/usr/bin/google-chrome-stable" in text


def test_gh302_browser_service_has_one_gigabyte_shm() -> None:
    services = yaml.safe_load(SCRAPER_COMPOSE.read_text(encoding="utf-8"))["services"]
    assert services["scraper-browser"]["shm_size"] == "1g"


def test_gh302_manual_script_uses_the_default_queue() -> None:
    assert "TOPCV_DB=" not in MANUAL.read_text(encoding="utf-8")
