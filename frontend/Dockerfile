# Production Dockerfile for frontend
# Use pre-built base image with all system dependencies for builder stage
# This image has all apk packages pre-installed, significantly speeding up builds
# Base image: docker/base-images/Dockerfile.base-frontend
FROM ghcr.io/cliffcho242/hiremebahamas-base-frontend:latest AS builder

# Working directory is already set to /app in base image

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Production stage with nginx
FROM nginx:alpine

# Install nginx utilities and security updates
RUN apk add --no-cache \
    # Curl for health checks
    curl \
    # SSL/TLS support
    ca-certificates \
    # Security updates
    && apk upgrade --no-cache

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]