"""Cache response trong tiến trình cho `GET /api/v1/*`, xóa theo snapshot (#343).

Số của API chỉ đổi khi một snapshot được chốt. Mỗi request vẫn hỏi nguồn `version()` (với `StatMarket` là một query
nhỏ trên bảng `snapshots`); version khác lần trước thì bỏ toàn bộ cache. Vì vậy snapshot mới được phục vụ ngay ở
request kế tiếp, và quy tắc "snapshot đọc được mới nhất" của các route không đổi.

Request trúng cache trả nguyên bytes đã gửi lần đầu: không đọc bảng `stat_*`, không dựng model Pydantic, không
serialize lại. Chỉ response 200 được giữ. Request mang dữ liệu người dùng gõ (`title`, `have`) không bao giờ vào
cache, để máy chủ không giữ bản sao chức danh hay hồ sơ kỹ năng (#150, #205).

Middleware ASGI thuần, không dùng `BaseHTTPMiddleware`, để request trúng cache tốn ít CPU nhất.
"""

import logging
from collections import OrderedDict
from collections.abc import Callable, Iterator
from operator import itemgetter
from urllib.parse import parse_qsl

import anyio.to_thread
from starlette.types import ASGIApp, Message, Receive, Scope, Send

CACHE_ENV = "HAIDO_RESPONSE_CACHE"
"""Đặt `on` để bật. Mặc định tắt, như nguồn `fake` của `SOURCE_ENV`; `compose.prod.yml` bật."""
CACHE_HEADER = "x-cache"
"""`HIT` hoặc `MISS` trên response đi qua cache. Request không được cache thì không có header này."""
PREFIX = "/api/v1/"
PRIVATE_PARAMS = frozenset({"title", "have"})
DEFAULT_MAX_ENTRIES = 1024

log = logging.getLogger(__name__)

Key = tuple[str, tuple[tuple[str, str], ...]]
Entry = tuple[int, list[tuple[bytes, bytes]], bytes]


class ResponseStore:
    """LRU có trần số mục, gắn với một version. Version đổi thì rỗng."""

    def __init__(self, max_entries: int = DEFAULT_MAX_ENTRIES) -> None:
        if max_entries < 1:
            raise ValueError("max_entries phải từ 1 trở lên.")
        self.max_entries = max_entries
        self.version: str | None = None
        self._entries: OrderedDict[Key, Entry] = OrderedDict()

    def use(self, version: str) -> None:
        if version != self.version:
            self._entries.clear()
            self.version = version

    def get(self, key: Key) -> Entry | None:
        entry = self._entries.get(key)
        if entry is not None:
            self._entries.move_to_end(key)
        return entry

    def put(self, version: str, key: Key, entry: Entry) -> None:
        if version != self.version:  # snapshot đã đổi trong lúc route chạy: response này có thể là số cũ
            return
        self._entries[key] = entry
        self._entries.move_to_end(key)
        while len(self._entries) > self.max_entries:
            self._entries.popitem(last=False)

    def __iter__(self) -> Iterator[Key]:
        return iter(list(self._entries))

    def __len__(self) -> int:
        return len(self._entries)


class ResponseCache:
    """Middleware ASGI. `version` chạy trong threadpool vì nó có thể chạm DB."""

    def __init__(self, app: ASGIApp, *, store: ResponseStore, version: Callable[[], str]) -> None:
        self.app = app
        self.store = store
        self.version = version

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        key = _key(scope)
        if key is None:
            await self.app(scope, receive, send)
            return
        try:
            version = await anyio.to_thread.run_sync(self.version)
        except Exception:
            log.warning("Không đọc được version của nguồn; bỏ qua cache cho request này.", exc_info=True)
            await self.app(scope, receive, send)
            return

        self.store.use(version)
        hit = self.store.get(key)
        if hit is not None:
            status, headers, body = hit
            await send({"type": "http.response.start", "status": status, "headers": [*headers, _flag(b"HIT")]})
            await send({"type": "http.response.body", "body": body})
            return

        start: Message | None = None
        chunks: list[bytes] = []

        async def capture(message: Message) -> None:
            nonlocal start
            if message["type"] == "http.response.start":
                start = message
                message = {**message, "headers": [*message.get("headers", []), _flag(b"MISS")]}
            elif message["type"] == "http.response.body" and start is not None and start["status"] == 200:
                chunks.append(message.get("body", b""))
                if not message.get("more_body", False):
                    headers = [(k, v) for k, v in start.get("headers", []) if k.lower() != CACHE_HEADER.encode()]
                    self.store.put(version, key, (200, headers, b"".join(chunks)))
            await send(message)

        await self.app(scope, receive, capture)


def _key(scope: Scope) -> Key | None:
    """Khóa cache của request, hoặc None nếu request không được cache."""
    if scope["type"] != "http" or scope["method"] != "GET":
        return None
    path: str = scope["path"]
    if not path.startswith(PREFIX):
        return None
    query = parse_qsl(scope.get("query_string", b"").decode("latin-1"), keep_blank_values=True)
    if any(name in PRIVATE_PARAMS for name, _ in query):
        return None
    # Sắp theo tên, giữ thứ tự giữa các giá trị cùng tên: route lấy giá trị cuối khi một tham số lặp lại.
    return path, tuple(sorted(query, key=itemgetter(0)))


def _flag(value: bytes) -> tuple[bytes, bytes]:
    return CACHE_HEADER.encode(), value
