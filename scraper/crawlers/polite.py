"""Polite HTTP client shared by the CareerLink / ITNavi / Zalo / MoMo crawlers.

- Honest User-Agent, no browser impersonation.
- Checks robots.txt before every request.
- Fixed delay between requests and an optional per-run request budget.
- Stops (BlockedError) on 403/429 or a captcha page instead of working around it.
"""

import time
import urllib.robotparser
from urllib.parse import urlparse

import requests

USER_AGENT = "HaiDoIT-research-bot/0.1 (non-commercial student research)"
CAPTCHA_MARKERS = ("hcaptcha", "g-recaptcha", "cf-challenge")


class BlockedError(RuntimeError):
    """The site refused us (robots.txt, 403/429, captcha). Stop, do not retry around it."""


class BudgetExhausted(RuntimeError):
    """The per-run request budget is used up."""


class PoliteClient:
    def __init__(self, delay: float = 3.0, max_requests: int = 0):
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT
        self.delay = delay
        self.max_requests = max_requests
        self.count = 0
        self._robots = {}
        self._last = 0.0

    def allowed(self, url: str) -> bool:
        parts = urlparse(url)
        base = f"{parts.scheme}://{parts.netloc}"
        rp = self._robots.get(base)
        if rp is None:
            rp = urllib.robotparser.RobotFileParser()
            lines = []
            try:
                resp = self.session.get(base + "/robots.txt", timeout=30)
                if resp.status_code == 200 and "text/plain" in resp.headers.get(
                    "Content-Type", ""
                ):
                    lines = resp.text.splitlines()
            except requests.RequestException:
                pass
            rp.parse(lines)
            self._robots[base] = rp
        return rp.can_fetch(USER_AGENT, url)

    def get(self, url: str, **kwargs) -> requests.Response:
        if self.max_requests and self.count >= self.max_requests:
            raise BudgetExhausted(f"used {self.count} requests")
        if not self.allowed(url):
            raise BlockedError(f"robots.txt disallows {url}")

        wait = self.delay - (time.monotonic() - self._last)
        if wait > 0:
            time.sleep(wait)
        resp = self.session.get(url, timeout=30, **kwargs)
        self._last = time.monotonic()
        self.count += 1

        if resp.status_code in (403, 429):
            raise BlockedError(f"HTTP {resp.status_code} on {url}")
        if "html" in resp.headers.get("Content-Type", ""):
            head = resp.text[:200_000].lower()
            if any(m in head for m in CAPTCHA_MARKERS):
                raise BlockedError(f"captcha page on {url}")
        resp.raise_for_status()
        return resp
