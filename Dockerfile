FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONPATH=/app \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3-dev \
    gcc \
    g++ \
    build-essential \
    libpq-dev \
    default-mysql-client \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

RUN mkdir -p /app/RAG-Layer

EXPOSE 8000 8080 5000

CMD ["python", "main.py"]
