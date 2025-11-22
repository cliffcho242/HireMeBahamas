# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for production deployment
RUN apt-get update && apt-get install -y \
    # Build tools (required for compiling Python packages)
    build-essential \
    gcc \
    g++ \
    make \
    # PostgreSQL client and development libraries (for psycopg2)
    postgresql-client \
    libpq-dev \
    # SSL/TLS libraries (for cryptography package)
    libssl-dev \
    libffi-dev \
    # Image processing libraries (for Pillow)
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev \
    libopenjp2-7-dev \
    zlib1g-dev \
    # Event notification library (for gevent)
    libevent-dev \
    # XML processing libraries (for various packages)
    libxml2-dev \
    libxslt1-dev \
    # Redis tools (for Redis connectivity testing)
    redis-tools \
    # Utilities
    curl \
    wget \
    git \
    # Clean up apt cache to reduce image size
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads/avatars uploads/portfolio uploads/documents

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]