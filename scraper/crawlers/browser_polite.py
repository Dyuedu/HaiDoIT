"""Playwright browser helper — honest identification, no anti-bot evasion.

Uses the same User-Agent as polite.py so sites see a consistent identity.
No webdriver-flag hiding, no AutomationControlled disabling.
"""

from contextlib import contextmanager

from crawlers.polite import USER_AGENT

DEFAULT_DELAY = 3.0


# A long-lived tab on these sites grows until Chromium kills it, and a crashed tab
# fails every later goto. Recycle tabs often, and always after a failure.
PAGE_RECYCLE_EVERY = 25
MAX_CONSECUTIVE_FAILURES = 10


def fresh_page(ctx, page=None):
    """Close `page` if it can still be closed and open a new tab."""
    if page is not None:
        try:
            page.close()
        except Exception:  # noqa: BLE001 - a crashed tab may refuse even this
            pass
    return ctx.new_page()


@contextmanager
def browser_polite(headless=True):
    """Launch headless Chromium with honest UA. Yields a BrowserContext."""
    from playwright.sync_api import sync_playwright  # only the browser image has it

    with sync_playwright() as p:
        b = p.chromium.launch(headless=headless)
        ctx = b.new_context(user_agent=USER_AGENT)
        try:
            yield ctx
        finally:
            ctx.close()
            b.close()
