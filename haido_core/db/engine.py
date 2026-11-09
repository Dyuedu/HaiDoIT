"""Engine kết nối Postgres cho các bước CLI (Story 1.4).

- Engine đích (`HAIDO_DATABASE_URL`) từ chối host ngoài danh sách local trừ khi đặt
  `HAIDO_ALLOW_REMOTE_WRITE=1`.
- Engine nguồn (`HAIDO_SCRAPER_DATABASE_URL`, bảng của scraper) luôn chỉ-đọc ở phía DB:
  mỗi transaction mở bằng `BEGIN READ ONLY`, nên cả pooler Supabase cũng không ghi được.
- Engine đọc của API (`make_read_engine`) cùng URL đích nhưng chỉ-đọc ở phía DB.
- Thông báo lỗi không bao giờ chứa URL, host hay mật khẩu.
"""

import os

from sqlalchemy import Engine, create_engine
from sqlalchemy.engine import URL, make_url

from haido_core.db.migrations.env import ALLOWED_LOCAL_HOSTS

TARGET_ENV = "HAIDO_DATABASE_URL"
SOURCE_ENV = "HAIDO_SCRAPER_DATABASE_URL"
ALLOW_REMOTE_ENV = "HAIDO_ALLOW_REMOTE_WRITE"
DRIVER = "postgresql+psycopg"
CONNECT_TIMEOUT = 10  # giây; host không tới được thì báo lỗi thay vì treo


class DatabaseConfigError(ValueError):
    """Cấu hình kết nối sai. Thông báo bằng tiếng Việt, không in URL."""


def _parse(url_text: str, env_name: str) -> URL:
    try:
        return make_url(url_text)
    except Exception as exc:
        raise DatabaseConfigError(f"{env_name} không hợp lệ.") from exc


def _hosts(url: URL) -> set[str]:
    hosts = {url.host} if url.host else set()
    for param in ("host", "hostaddr"):
        value = (url.query or {}).get(param)
        if isinstance(value, str):
            hosts.add(value)
        elif value:
            hosts.update(value)
    return hosts


def normalize_source_url(url: str) -> str:
    """URL kiểu scraper (`postgresql://`, `postgres://`) đổi sang driver psycopg của SQLAlchemy."""
    for prefix in ("postgresql://", "postgres://"):
        if url.startswith(prefix):
            url = DRIVER + "://" + url[len(prefix) :]
            break
    if _parse(url, SOURCE_ENV).drivername != DRIVER:
        raise DatabaseConfigError(f"{SOURCE_ENV} phải là URL Postgres (postgresql://...).")
    return url


def make_write_engine(url: str | None = None) -> Engine:
    """Engine ghi vào kho của Hải Đồ. Không kết nối ngay."""
    url = url if url is not None else os.getenv(TARGET_ENV, "")
    if not url:
        raise DatabaseConfigError(f"{TARGET_ENV} chưa được thiết lập.")
    parsed = _parse(url, TARGET_ENV)
    if parsed.drivername != DRIVER:
        raise DatabaseConfigError(f"{TARGET_ENV} phải dùng driver postgresql+psycopg://.")
    hosts = _hosts(parsed)
    if not hosts:
        raise DatabaseConfigError(f"Không thể xác định host từ {TARGET_ENV}.")
    allow_remote = os.getenv(ALLOW_REMOTE_ENV, "").strip() == "1"
    if hosts - ALLOWED_LOCAL_HOSTS and not allow_remote:
        raise DatabaseConfigError(
            "Từ chối ghi vào host ngoài danh sách an toàn (localhost, 127.0.0.1, postgres) "
            f"khi chưa đặt cờ {ALLOW_REMOTE_ENV}=1."
        )
    return create_engine(url, connect_args={"prepare_threshold": None, "connect_timeout": CONNECT_TIMEOUT})


def make_source_engine(url: str | None = None) -> Engine:
    """Engine đọc bảng của scraper. Chỉ-đọc ở phía DB, snapshot nhất quán trong một transaction."""
    url = url if url is not None else os.getenv(SOURCE_ENV, "")
    if not url:
        raise DatabaseConfigError(f"{SOURCE_ENV} chưa được thiết lập.")
    return create_engine(
        normalize_source_url(url),
        connect_args={"prepare_threshold": None, "connect_timeout": CONNECT_TIMEOUT},
        execution_options={"postgresql_readonly": True, "isolation_level": "REPEATABLE READ"},
    )


def make_read_engine(url: str | None = None) -> Engine:
    """Engine đọc kho của Hải Đồ cho API (`HAIDO_DATABASE_URL`). Không kết nối ngay.

    Chỉ-đọc ở phía DB nên không áp danh sách host của engine ghi: đọc từ host ngoài không đổi dữ liệu.
    """
    url = url if url is not None else os.getenv(TARGET_ENV, "")
    if not url:
        raise DatabaseConfigError(f"{TARGET_ENV} chưa được thiết lập.")
    if _parse(url, TARGET_ENV).drivername != DRIVER:
        raise DatabaseConfigError(f"{TARGET_ENV} phải dùng driver postgresql+psycopg://.")
    return create_engine(
        url,
        connect_args={"prepare_threshold": None, "connect_timeout": CONNECT_TIMEOUT},
        execution_options={"postgresql_readonly": True},
        pool_pre_ping=True,
    )
