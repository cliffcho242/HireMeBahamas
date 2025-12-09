# Docker Compose Configuration

## 📋 File Naming Convention

This project uses `docker-compose.local.yml` instead of the standard `docker-compose.yml` filename.

### Why the `.local.yml` suffix?

**To prevent accidental deployment to cloud platforms like Railway.**

When Railway detects a file named `docker-compose.yml`, it may attempt to deploy it as a multi-container application. This causes deployment failures because:

1. **PostgreSQL refuses to run as root** - Railway's container runtime has security constraints
2. **Data loss risk** - Containerized databases lose data on redeployment
3. **Inefficiency** - Managed databases are faster and more reliable
4. **Cost** - Running database containers wastes resources

### ✅ Correct Usage

#### For Local Development:
```bash
# Start all services
docker-compose -f docker-compose.local.yml up -d

# Stop all services
docker-compose -f docker-compose.local.yml down

# View logs
docker-compose -f docker-compose.local.yml logs -f

# Start specific services
docker-compose -f docker-compose.local.yml up postgres adminer -d
```

#### For Production (Cloud Deployment):

**DO NOT use docker-compose files for production deployment!**

Instead, use platform-managed services:

- **Railway**: Use managed PostgreSQL database service ([Setup Guide](./RAILWAY_POSTGRESQL_SETUP.md))
- **Render**: Use managed PostgreSQL database service
- **Vercel**: Use Vercel Postgres

### 🔒 Security Notes

The `docker-compose.local.yml` file is excluded from cloud deployments via:

1. **`.railwayignore`** - Prevents Railway from using it
2. **`.nixpacksignore`** - Prevents Nixpacks from detecting it
3. **`railway.json`** - Explicitly disables Docker Compose detection
4. **File naming** - The `.local.yml` suffix makes intent clear

### 📖 Documentation

- **Railway Setup**: [RAILWAY_SETUP_REQUIRED.md](./RAILWAY_SETUP_REQUIRED.md)
- **Development Guide**: [DEVELOPMENT.md](./DEVELOPMENT.md)
- **Docker Quick Start**: [DOCKER_QUICK_START.md](./DOCKER_QUICK_START.md)

### 🆘 Getting "root execution not permitted" Error?

This means you're trying to deploy PostgreSQL as a container on Railway. This is **incorrect**.

➡️ **Read: [RAILWAY_SETUP_REQUIRED.md](./RAILWAY_SETUP_REQUIRED.md)** for the correct setup.

---

**Last Updated**: December 2025
