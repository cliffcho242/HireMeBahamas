# Multi-stage Dockerfile for HireMeBahamas Flask Backend with PostgreSQL
# This ensures all PostgreSQL dependencies are properly installed

FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# ============================================
# Stage 1: Install system dependencies
# ============================================
FROM base as dependencies

# Update package lists and install PostgreSQL dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build tools (required for compiling Python packages)
    build-essential \
    gcc \
    g++ \
    make \
    pkg-config \
    # PostgreSQL client and development libraries (REQUIRED)
    postgresql-client \
    postgresql-client-common \
    libpq-dev \
    libpq5 \
    # Python development headers
    python3-dev \
    # SSL/TLS libraries (for secure connections)
    libssl-dev \
    libffi-dev \
    ca-certificates \
    # Image processing libraries
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev \
    libfreetype6-dev \
    liblcms2-dev \
    zlib1g-dev \
    # Event notification (for gevent)
    libevent-dev \
    # XML processing
    libxml2-dev \
    libxslt1-dev \
    # SQLite (for development/testing)
    libsqlite3-dev \
    # Additional libraries
    libreadline-dev \
    libbz2-dev \
    libncurses5-dev \
    # Utilities
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Verify psycopg2-binary installation
RUN python -c "import psycopg2; print(f'✅ psycopg2 version: {psycopg2.__version__}')" && \
    python -c "import aiosqlite; print(f'✅ aiosqlite installed')"

# ============================================
# Stage 2: Production image
# ============================================
FROM python:3.12-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.local/bin:$PATH" \
    ENVIRONMENT=production

WORKDIR /app

# Install only runtime PostgreSQL libraries (smaller image)
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq5 \
    libssl3 \
    ca-certificates \
    curl \
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

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start command
CMD ["gunicorn", "final_backend_postgresql:application", \
     "--bind", "0.0.0.0:8080", \
     "--workers", "4", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info"]
