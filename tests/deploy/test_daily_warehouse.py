"""Lịch đêm gọi ingest, lifecycle, aggregate rồi publish sau khi scraper ghi xong ngày đó."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DAILY = ROOT / "deploy" / "daily.sh"
COMPOSE = ROOT / "deploy" / "compose.scraper.yml"


def test_daily_chay_kho_sau_ingest_scraper() -> None:
    text = DAILY.read_text(encoding="utf-8")
    scraper_ingest = text.index("pipeline.py ingest")
    warehouse = text.index("run_warehouse ||")
    assert scraper_ingest < warehouse
    night = (ROOT / "deploy" / "warehouse-night.sh").read_text(encoding="utf-8")
    order = [
        "alembic upgrade head",
        "python -m haido_core.cli ingest",
        "python -m haido_core.cli lifecycle",
        "python -m haido_core.cli aggregate",
        "python -m haido_core.cli publish",
    ]
    positions = [night.index(step) for step in order]
    assert positions == sorted(positions)


def test_compose_co_warehouse_khong_mo_cong() -> None:
    text = COMPOSE.read_text(encoding="utf-8")
    assert "ghcr.io/dyuedu/haidoit-warehouse:" in text
    assert "HAIDO_ALLOW_REMOTE_WRITE" in text
    assert "HAIDO_ALLOW_REMOTE_MIGRATION" in text
    warehouse = text.split("warehouse:", 1)[1].split("scraper-browser:", 1)[0]
    assert "ports:" not in warehouse
