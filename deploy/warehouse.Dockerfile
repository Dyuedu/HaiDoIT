# Sau nhịp thu của scraper: alembic, ingest, lifecycle, aggregate, publish.
# Context là gốc repo. .dockerignore bỏ scraper/, tests/ và .env.
FROM ghcr.io/astral-sh/uv:0.6.14-python3.13-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    TZ=Asia/Ho_Chi_Minh

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY haido_core ./haido_core
COPY config ./config
COPY alembic.ini ./
COPY deploy/warehouse-night.sh /app/warehouse-night.sh

RUN uv sync --frozen --no-dev \
 && chmod 755 /app/warehouse-night.sh \
 && groupadd -r haido && useradd -r -g haido -d /app -s /sbin/nologin haido \
 && chown -R haido:haido /app

USER haido

ENTRYPOINT ["/app/warehouse-night.sh"]
