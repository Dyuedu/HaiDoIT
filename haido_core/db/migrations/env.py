"""Môi trường chạy di trú Alembic cho Hải Đồ IT."""

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import make_url

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = getattr(context, "config", None)

# Interpret the config file for Python logging.
if config is not None and config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = None

ALLOWED_LOCAL_HOSTS = {"localhost", "127.0.0.1", "postgres"}


def validate_migration_target(url: str, allow_remote: bool = False) -> str:
    """Kiểm tra URL kết nối của Alembic.

    Từ chối host ngoài localhost, 127.0.0.1, postgres trừ khi allow_remote=True
    (chỉ khi HAIDO_ALLOW_REMOTE_MIGRATION=1).
    Báo lỗi bằng tiếng Việt và tuyệt đối không in mật khẩu.
    Kiểm tra cả authority host lẫn query parameters (host, hostaddr).
    """
    if not url:
        raise ValueError("HAIDO_DATABASE_URL chưa được thiết lập.")

    try:
        url_obj = make_url(url)
    except Exception as exc:
        raise ValueError("HAIDO_DATABASE_URL không hợp lệ.") from exc

    if url_obj.drivername != "postgresql+psycopg":
        raise ValueError(
            f"HAIDO_DATABASE_URL phải dùng driver postgresql+psycopg:// (nhận được: {url_obj.drivername}://)."
        )

    hosts_to_check: set[str] = set()
    if url_obj.host:
        hosts_to_check.add(url_obj.host)

    query = url_obj.query or {}
    for param in ("host", "hostaddr"):
        if param in query:
            val = query[param]
            if isinstance(val, (list, tuple)):
                hosts_to_check.update(val)
            elif isinstance(val, str):
                hosts_to_check.add(val)

    if not hosts_to_check:
        raise ValueError("Không thể xác định host từ HAIDO_DATABASE_URL.")

    foreign_hosts = sorted(hosts_to_check - ALLOWED_LOCAL_HOSTS)
    if foreign_hosts and not allow_remote:
        raise ValueError(
            "Alembic từ chối kết nối tới host ngoài danh sách an toàn "
            "(localhost, 127.0.0.1, postgres) khi chưa đặt cờ HAIDO_ALLOW_REMOTE_MIGRATION=1."
        )

    return url


def get_url() -> str:
    url = os.getenv("HAIDO_DATABASE_URL", "")
    # Cờ chỉ nhận chính xác "1" (spec không cho phép "true")
    allow_remote = os.getenv("HAIDO_ALLOW_REMOTE_MIGRATION", "").strip() == "1"
    return validate_migration_target(url, allow_remote=allow_remote)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    url = get_url()
    configuration = config.get_section(config.config_ini_section, {}) if config else {}
    configuration["sqlalchemy.url"] = url
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if config is not None:
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()
