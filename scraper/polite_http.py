"""
HTTP client "lịch sự" cho bộ cào job board.

Nguyên tắc (xem `scraper/README.md`):
- Tôn trọng robots.txt (kể cả `Crawl-delay`); URL bị cấm -> `DisallowedError`, không gọi.
- User-Agent trung thực, có thông tin liên hệ; không giả trình duyệt, không xoay proxy.
- Giãn cách tối thiểu giữa hai request cùng host + jitter ngẫu nhiên.
- 429/5xx: chờ theo `Retry-After` (có trần) hoặc backoff lũy thừa, tối đa `max_retries` lần.
- Gặp trang thử thách chống bot (Cloudflare "Just a moment...", header `cf-mitigated`) hoặc 401/403
  -> `BlockedError`: dừng nguồn đó. Không bao giờ cố vượt qua.
"""
import logging
import random
import time
from email.utils import parsedate_to_datetime
from typing import Callable, Dict, Optional
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser

import httpx

logger = logging.getLogger("skillnexus.scraper")

BOT_NAME = "SkillNexusBot"
BOT_VERSION = "0.1"
DEFAULT_MIN_DELAY_S = 3.0
DEFAULT_JITTER_S = 2.0
DEFAULT_MAX_RETRIES = 3
MAX_RETRY_AFTER_S = 300.0
MAX_BODY_BYTES = 20 * 1024 * 1024
RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})
_CHALLENGE_MARKERS = ("<title>Just a moment...</title>", "challenges.cloudflare.com", "cf-browser-verification")


class ScrapeError(RuntimeError):
    """Lỗi chung khi cào."""


class DisallowedError(ScrapeError):
    """robots.txt cấm URL này."""


class BlockedError(ScrapeError):
    """Trang chủ động chặn bot (thử thách chống bot, 401/403). Dừng nguồn, không vượt."""


def build_user_agent(contact: Optional[str] = None) -> str:
    info = "non-commercial research"
    if contact:
        info += f"; contact: {contact}"
    return f"{BOT_NAME}/{BOT_VERSION} (+{info})"


def _is_challenge(resp: httpx.Response) -> bool:
    if resp.headers.get("cf-mitigated", "").lower() == "challenge":
        return True
    if resp.status_code not in (403, 429, 503):
        return False
    head = resp.text[:4000]
    return any(m in head for m in _CHALLENGE_MARKERS)


def _retry_after_seconds(value: Optional[str]) -> Optional[float]:
    if not value:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        pass
    try:
        return max(0.0, parsedate_to_datetime(value).timestamp() - time.time())
    except (TypeError, ValueError, IndexError):
        return None


class PoliteClient:
    """Một client cho mọi host; robots.txt và đồng hồ giãn cách tính riêng từng host."""

    def __init__(
        self,
        user_agent: str,
        min_delay_s: float = DEFAULT_MIN_DELAY_S,
        jitter_s: float = DEFAULT_JITTER_S,
        max_retries: int = DEFAULT_MAX_RETRIES,
        timeout_s: float = 30.0,
        transport: Optional[httpx.BaseTransport] = None,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ):
        self.user_agent = user_agent
        self.min_delay_s = min_delay_s
        self.jitter_s = jitter_s
        self.max_retries = max_retries
        self._sleep = sleep
        self._clock = clock
        self._robots: Dict[str, RobotFileParser] = {}
        self._last_request: Dict[str, float] = {}
        self._client = httpx.Client(
            headers={"User-Agent": user_agent, "Accept-Language": "vi,en;q=0.8"},
            timeout=timeout_s,
            follow_redirects=True,
            transport=transport,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "PoliteClient":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    # ------------------------------------------------------------ robots.txt

    def robots(self, url: str) -> RobotFileParser:
        parts = urlsplit(url)
        origin = f"{parts.scheme}://{parts.netloc}"
        parser = self._robots.get(origin)
        if parser is None:
            parser = RobotFileParser()
            robots_url = origin + "/robots.txt"
            resp = self._send(robots_url)
            if resp.status_code >= 500:
                parser.disallow_all = True  # RFC 9309: server lỗi -> coi như cấm hết
            elif resp.status_code >= 400:
                parser.allow_all = True  # RFC 9309: robots.txt không tồn tại (4xx) -> không giới hạn
            else:
                parser.parse(resp.text.splitlines())
            self._robots[origin] = parser
        return parser

    def can_fetch(self, url: str) -> bool:
        return self.robots(url).can_fetch(self.user_agent, url)

    def sitemaps(self, url: str) -> list:
        return list(self.robots(url).site_maps() or [])

    # ------------------------------------------------------------ fetching

    def get(self, url: str) -> httpx.Response:
        """GET đã qua kiểm robots.txt, giãn cách, retry. Trả response 2xx/3xx/4xx (trừ 401/403)."""
        if not self.can_fetch(url):
            raise DisallowedError(f"robots.txt cấm: {url}")
        return self._send(url)

    def _wait_turn(self, host: str) -> None:
        delay = self.min_delay_s
        crawl_delay = None
        parser = self._robots.get(f"https://{host}") or self._robots.get(f"http://{host}")
        if parser is not None:
            crawl_delay = parser.crawl_delay(self.user_agent)
        if crawl_delay:
            delay = max(delay, float(crawl_delay))
        last = self._last_request.get(host)
        if last is not None:
            remaining = last + delay + random.uniform(0, self.jitter_s) - self._clock()
            if remaining > 0:
                self._sleep(remaining)
        self._last_request[host] = self._clock()

    def _send(self, url: str) -> httpx.Response:
        host = urlsplit(url).netloc
        for attempt in range(self.max_retries + 1):
            self._wait_turn(host)
            try:
                resp = self._client.get(url)
            except httpx.TransportError as e:
                if attempt == self.max_retries:
                    raise ScrapeError(f"Không kết nối được {url}: {e}") from e
                self._sleep(self._backoff(attempt))
                continue
            if _is_challenge(resp):
                raise BlockedError(f"{host} trả trang thử thách chống bot ({resp.status_code}); dừng nguồn")
            if resp.status_code in (401, 403):
                raise BlockedError(f"{host} từ chối truy cập ({resp.status_code}) tại {url}")
            if resp.status_code in RETRYABLE_STATUS and attempt < self.max_retries:
                wait = _retry_after_seconds(resp.headers.get("Retry-After"))
                wait = min(wait if wait is not None else self._backoff(attempt), MAX_RETRY_AFTER_S)
                logger.warning("%s -> %s; chờ %.0fs rồi thử lại", url, resp.status_code, wait)
                self._sleep(wait)
                continue
            if len(resp.content) > MAX_BODY_BYTES:
                raise ScrapeError(f"Response quá lớn ({len(resp.content)} byte): {url}")
            return resp
        raise ScrapeError(f"Hết số lần thử: {url}")  # pragma: no cover - vòng lặp luôn return/raise

    def _backoff(self, attempt: int) -> float:
        return max(self.min_delay_s, 1.0) * (2 ** (attempt + 1))
