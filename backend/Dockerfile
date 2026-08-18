# syntax=docker/dockerfile:1.7
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install --no-install-recommends -y libglib2.0-0 libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml alembic.ini ./
COPY alembic ./alembic
COPY app ./app
COPY docker-entrypoint.sh /usr/local/bin/frame-studio-entrypoint

RUN python -m pip install --upgrade pip \
    && python -m pip install . \
    && chmod +x /usr/local/bin/frame-studio-entrypoint

RUN mkdir -p /data/storage

EXPOSE 8000
VOLUME ["/data"]
ENTRYPOINT ["frame-studio-entrypoint"]
