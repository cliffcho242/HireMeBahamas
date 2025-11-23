# Multi-stage Dockerfile for HireMeBahamas Flask Backend with PostgreSQL
# This ensures all PostgreSQL dependencies are properly installed

FROM python:3.12-slim AS base

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
FROM base AS dependencies

# Update package lists and install ALL required dependencies
# This ensures the database can properly store user information
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build tools (required for compiling Python packages)
    build-essential \
    gcc \
    g++ \
    make \
    pkg-config \
    cmake \
    autoconf \
    automake \
    libtool \
    # PostgreSQL client and development libraries (REQUIRED for production)
    postgresql \
    postgresql-client \
    postgresql-client-common \
    postgresql-common \
    postgresql-contrib \
    libpq-dev \
    libpq5 \
    # SQLite libraries (for development/testing)
    sqlite3 \
    libsqlite3-dev \
    libsqlite3-0 \
    # Python development headers
    python3-dev \
    python3-setuptools \
    python3-wheel \
    # SSL/TLS libraries (for secure connections and cryptography)
    libssl-dev \
    libffi-dev \
    ca-certificates \
    openssl \
    # Image processing libraries (for avatar and media uploads)
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    zlib1g-dev \
    # Event notification (for gevent and async operations)
    libevent-dev \
    # XML processing
    libxml2-dev \
    libxslt1-dev \
    # Additional libraries for Python packages
    libreadline-dev \
    libbz2-dev \
    libncurses5-dev \
    libncursesw5-dev \
    tk-dev \
    xz-utils \
    llvm \
    # Utilities
    curl \
    wget \
    git \
    vim \
    net-tools \
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
FROM python:3.12-slim AS production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.local/bin:$PATH" \
    ENVIRONMENT=production

WORKDIR /app

# Install runtime libraries (needed for database and app to run)
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    postgresql-client-common \
    libpq5 \
    sqlite3 \
    libsqlite3-0 \
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

# Health check - use PORT environment variable with fallback
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD sh -c 'curl -f http://localhost:${PORT:-8080}/health || exit 1'

# Start command - use exec form with shell to allow environment variable expansion
CMD ["sh", "-c", "gunicorn final_backend_postgresql:application --bind 0.0.0.0:${PORT:-8080} --workers 4 --timeout 120 --access-logfile - --error-logfile - --log-level info"]
