# Production Dockerfile for frontend
FROM node:18-alpine AS builder

WORKDIR /app

# Install build dependencies for Node.js native modules (if needed)
# Alpine uses apk instead of apt-get
RUN apk add --no-cache \
    # Build tools
    python3 \
    make \
    g++ \
    # Git (for npm packages from git repos)
    git

# Copy package files
COPY package*.json ./

# Install dependencies using BuildKit cache for npm
# Note: --legacy-peer-deps is required due to peer dependency conflicts in the project
RUN --mount=type=cache,target=/root/.npm \
    npm ci --legacy-peer-deps

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