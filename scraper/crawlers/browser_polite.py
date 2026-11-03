"""Playwright browser helper — honest identification, no anti-bot evasion.

Uses the same User-Agent as polite.py so sites see a consistent identity.
No webdriver-flag hiding, no AutomationControlled disabling.
"""

from contextlib import contextmanager

from playwright.sync_api import sync_playwright

from crawlers.polite import USER_AGENT

DEFAULT_DELAY = 3.0


@contextmanager
def browser_polite(headless=True):
    """Launch headless Chromium with honest UA. Yields a BrowserContext."""
    with sync_playwright() as p:
        b = p.chromium.launch(headless=headless)
        ctx = b.new_context(user_agent=USER_AGENT)
        try:
            yield ctx
        finally:
            ctx.close()
            b.close()
