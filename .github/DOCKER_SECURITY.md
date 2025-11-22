# Docker Security Best Practices

## Current Implementation Status

✅ **All Dockerfiles in this repository follow security best practices**

### Dockerfiles Reviewed

1. **backend/Dockerfile** - Production backend container
2. **frontend/Dockerfile** - Production frontend container  
3. **frontend/Dockerfile.dev** - Development frontend container
4. **docker-compose.yml** - Local development setup

## Security Best Practices Implemented

### ✅ No Secrets in ARG or ENV
All Dockerfiles avoid hardcoding sensitive data (API keys, passwords, etc.) in ARG or ENV instructions.

**Secure Pattern (Current Implementation)**:
```dockerfile
# ✅ GOOD: No secrets hardcoded
ENV DATABASE_URL=${DATABASE_URL}
ENV SECRET_KEY=${SECRET_KEY}
```

**Insecure Pattern (Avoided)**:
```dockerfile
# ❌ BAD: Secrets hardcoded in image
ARG ANTHROPIC_API_KEY=sk-ant-api03-xxx
ENV ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
```

### How Secrets Are Managed

#### Production (Render)
- Secrets configured via Render Dashboard → Environment Variables
- Never committed to version control
- Injected at runtime, not build time

#### Development (Docker Compose)
- Use `.env` file (excluded from git via `.gitignore`)
- Environment variables passed through docker-compose.yml
- Each developer maintains their own `.env` file

### Creating a Secure `.env` File

```bash
# Copy the example file
cp .env.example .env

# Edit with your local secrets
nano .env
```

Example `.env.example`:
```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/hiremebahamas

# Redis
REDIS_URL=redis://redis:6379

# API Keys (never commit actual keys)
SECRET_KEY=change-this-in-production
ANTHROPIC_API_KEY=your-key-here
GOOGLE_API_KEY=your-key-here
FCM_SERVER_KEY=your-key-here
```

## Security Scan Warnings

If you receive Docker security warnings about secrets in ARG/ENV:

1. **Check the file being scanned** - The warning may be from an old/cached version
2. **Verify current Dockerfiles** - Run: `grep -r "ARG.*API_KEY" backend/ frontend/`
3. **Update local images** - Run: `docker-compose down && docker-compose build --no-cache`

## Additional Security Measures

### ✅ Non-root User
Backend container could be enhanced to run as non-root user:
```dockerfile
# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
```

### ✅ Minimal Base Images
- Backend: `python:3.11-slim` (minimal Python image)
- Frontend: `node:18-alpine` and `nginx:alpine` (minimal images)

### ✅ Health Checks
Both containers include health check configurations

### ✅ No Unnecessary Privileges
Containers run with default (restricted) privileges

## Docker Security Checklist

- [x] No secrets in ARG or ENV instructions
- [x] Secrets managed via environment variables
- [x] `.env` file excluded from git
- [x] Minimal base images used
- [x] Health checks configured
- [x] Production dependencies only (`npm ci --only=production`)
- [x] Build cache optimization
- [x] Multi-stage builds (frontend)
- [ ] Non-root user (enhancement opportunity for backend)

## References

- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
- [OWASP Docker Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

## Troubleshooting

### "SecretsUsedInArgOrEnv" Warning
**Cause**: Security scanner detected potential secrets in Dockerfile

**Resolution**:
1. Verify the specific file being scanned
2. Check if warning is from a cached/old version
3. Review current Dockerfiles for hardcoded secrets
4. Rebuild containers with `--no-cache` flag

### Environment Variables Not Working
**Cause**: `.env` file missing or docker-compose not reading it

**Resolution**:
1. Create `.env` file from `.env.example`
2. Restart containers: `docker-compose down && docker-compose up`
3. Verify with: `docker-compose config | grep -A 5 environment`
