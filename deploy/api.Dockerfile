FROM ghcr.io/astral-sh/uv:0.6.14-python3.13-bookworm-slim AS runner

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Copy dependency files first
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev --no-install-project

# Copy application source explicitly
COPY haido_core ./haido_core
COPY haido_api ./haido_api
COPY alembic.ini ./

# Sync project
RUN uv sync --frozen --no-dev

# Create system user and switch to it
RUN groupadd -r haido && useradd -r -g haido -d /app -s /sbin/nologin haido && chown -R haido:haido /app

USER haido

EXPOSE 8000

CMD ["/app/.venv/bin/uvicorn", "haido_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
