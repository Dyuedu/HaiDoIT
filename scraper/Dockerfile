# Anh chay nhip mot tren VPS: crawl 4 nguon HTTP, dedupe, consolidate, sync.
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    PIP_NO_CACHE_DIR=1 \
    TZ=Asia/Ho_Chi_Minh

WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates tzdata curl \
 && rm -rf /var/lib/apt/lists/*

COPY requirements-vps.txt .
RUN pip install --no-cache-dir -r requirements-vps.txt

COPY . .

# Chay bang user thuong, khong phai root
RUN useradd -m -u 10001 runner && mkdir -p /app/data && chown -R runner:runner /app
USER runner

ENTRYPOINT ["python"]
CMD ["pipeline.py", "--help"]
