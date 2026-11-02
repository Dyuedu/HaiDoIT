"""Playwright browser helpers — drives the installed Google Chrome (visible)."""

from contextlib import contextmanager

from playwright.sync_api import sync_playwright

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


@contextmanager
def browser(headless=False):
    """Launch the system Google Chrome (anti-automation) and yield a context."""
    with sync_playwright() as p:
        b = p.chromium.launch(
            channel="chrome",
            headless=headless,
            args=["--disable-blink-features=AutomationControlled"],
        )
        ctx = b.new_context(user_agent=USER_AGENT)
        ctx.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        try:
            yield ctx
        finally:
            ctx.close()
            b.close()


SAFARI_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15"
)


@contextmanager
def webkit_context(user_data_dir, headless=False):
    """Launch a persistent WebKit (Safari engine) profile for LinkedIn."""
    with sync_playwright() as p:
        ctx = p.webkit.launch_persistent_context(
            user_data_dir,
            headless=headless,
            user_agent=SAFARI_UA,
        )
        try:
            yield ctx
        finally:
            ctx.close()


@contextmanager
def persistent_context(user_data_dir, headless=False):
    """Launch a persistent Chrome profile (LinkedIn keeps a login session here)."""
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir,
            channel="chrome",
            headless=headless,
            user_agent=USER_AGENT,
            args=["--disable-blink-features=AutomationControlled"],
        )
        ctx.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        try:
            yield ctx
        finally:
            ctx.close()
