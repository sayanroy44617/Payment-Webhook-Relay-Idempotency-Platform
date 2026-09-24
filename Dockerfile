# ==========================================
# Stage 1: Build & Dependency Installation
# ==========================================
FROM python:3.13-slim-bookworm AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install uv binary directly from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency configuration files first for Docker layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies into /app/.venv using uv
RUN uv sync --frozen --no-install-project --no-dev


# ==========================================
# Stage 2: Final Runtime Image
# ==========================================
FROM python:3.13-slim-bookworm AS runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app/src" \
    PATH="/app/.venv/bin:$PATH"

# Install minimal runtime library dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security best practices
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Copy installed virtual environment from builder stage
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy application source code and Alembic configurations
COPY --chown=appuser:appuser . .

EXPOSE 8000

# Default command (overridden in compose for migration sidecar)
CMD ["uvicorn", "payment_webhook_relay_idempotency_platform.main:app", "--host", "0.0.0.0", "--port", "8000"]
