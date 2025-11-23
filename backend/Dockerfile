# Use pre-built base image with all system dependencies
# This image has all apt-get packages pre-installed, significantly speeding up builds
# Base image: docker/base-images/Dockerfile.base-backend
FROM ghcr.io/cliffcho242/hiremebahamas-base-backend:latest

# Working directory is already set to /app in base image

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies using BuildKit cache for pip
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

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