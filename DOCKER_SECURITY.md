# Docker Security Best Practices

## Overview

This document explains how secrets and sensitive data are managed in this project to comply with Docker security best practices.

## Issues Fixed

### 1. Secrets in Docker Images

**Problem:** Using `ARG` or `ENV` instructions in Dockerfiles to pass sensitive data embeds those secrets in the Docker image layers, making them accessible to anyone with access to the image.

**Solution:** 
- Secrets are now loaded from environment variables at runtime
- Use `.env` files locally (never commit to git)
- Use platform secret management for production (Render, Render, etc.)

### 2. Environment Variable Management

#### Local Development (docker-compose.yml)
```yaml
backend:
  env_file:
    - .env  # Loads secrets from .env file (gitignored)
  environment:
    # Only non-sensitive configuration here
    ENVIRONMENT: development
```

#### Production (Render, Render, etc.)
- Configure secrets via platform dashboard
- Nixpacks/buildpacks automatically inject them at runtime
- Never use `ARG` or `ENV` for: SECRET_KEY, API keys, passwords, tokens

### 3. Secrets That Should NEVER Be in Dockerfiles

- `SECRET_KEY` - Flask/Django secret key
- `JWT_SECRET_KEY` - JWT signing key
- `DATABASE_URL` - Database connection string with credentials
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` - AI service keys
- `SMTP_PASSWORD` - Email service password
- `SSL_KEY_PATH` - SSL certificate keys
- `WANDB_API_KEY` - Weights & Biases API key
- `FCM_SERVER_KEY` - Firebase Cloud Messaging key
- `GOOGLE_API_KEY` - Google services API key
- `LINKEDIN_CLIENT_SECRET` - LinkedIn OAuth secret

## How to Use

### Local Development

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Update `.env` with your local secrets:
   ```bash
   SECRET_KEY=<generate-random-key>
   JWT_SECRET_KEY=<generate-random-key>
   DATABASE_URL=<your-local-db-url>
   ```

3. Start services:
   ```bash
   docker-compose up
   ```

### Production Deployment

1. **Render:**
   - Go to project settings → Variables
   - Add each secret as an environment variable
   - Render automatically injects them at runtime

2. **Render:**
   - Go to service settings → Environment
   - Add secrets as environment variables
   - Render injects them at runtime

3. **Other platforms:**
   - Use platform-specific secret management
   - Ensure secrets are injected at runtime, not build time

## File Structure

```
.
├── .env.example          # Template (safe to commit)
├── .env                  # Your secrets (NEVER commit)
├── .dockerignore         # Prevents .env from being copied
├── docker-compose.yml    # Uses env_file for secrets
├── nixpacks.toml         # No secrets in build config
└── Dockerfile            # No ARG/ENV for secrets
```

## Verification

To verify secrets aren't in your Docker image:

```bash
# Build image
docker build -t test-image .

# Check for secrets (should return nothing)
docker history test-image --no-trunc | grep -i "secret\|password\|key"
```

## References

- [Docker Secrets Best Practices](https://docs.docker.com/go/dockerfile/rule/secrets-used-in-arg-or-env/)
- [The Twelve-Factor App - Config](https://12factor.net/config)
- [OWASP: Secrets Management](https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_password)
