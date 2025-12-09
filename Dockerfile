# ============================================================================
# MASTERMIND FIX 2025 — ZERO-COMPILE DOCKERFILE
# ============================================================================
# Uses ONLY binary wheels, NO compilation, NO build tools
# Build time: <30 seconds | Image size: ~200MB smaller
# ============================================================================

FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# ============================================================================
# Stage 1: Install Python dependencies (binary wheels only)
# ============================================================================
FROM base AS dependencies

# Install ONLY runtime dependencies, NO build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq5 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# MASTERMIND FIX 2025 — NUCLEAR BINARY-ONLY INSTALL
RUN pip install --upgrade pip --root-user-action=ignore && \
    pip install --only-binary=:all: --root-user-action=ignore -r requirements.txt

# Verify installation
RUN python -c "import asyncpg; print(f'✅ asyncpg version: {asyncpg.__version__}')"

# ============================================================================
# Stage 2: Production image (minimal)
# ============================================================================
FROM python:3.12-slim AS production

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.local/bin:$PATH" \
    ENVIRONMENT=production

WORKDIR /app

# Install runtime libraries only
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq5 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from dependencies stage
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads/avatars uploads/portfolio uploads/documents uploads/stories

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD sh -c 'curl -f http://localhost:${PORT:-8000}/health || exit 1'

CMD ["sh", "-c", "uvicorn api.backend_app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --timeout-keep-alive 5 --limit-concurrency 100"]
