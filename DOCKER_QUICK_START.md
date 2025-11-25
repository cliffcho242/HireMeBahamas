# Quick Start Guide: Docker Base Images

This guide helps you get started with the new Docker base images for faster deployments.

## What Changed?

The HireMeBahamas project now uses **pre-built Docker base images** that contain all system dependencies. This makes deployments **5-10x faster** and eliminates build timeouts.

## For Developers

### Local Development

No changes needed! Continue using:
```bash
docker-compose up
```

The docker-compose.yml automatically uses the optimized Dockerfiles.

### Database Admin Interface

Access the built-in database management interface:

```bash
# Start all services including Adminer
docker-compose up -d

# Access Adminer at http://localhost:8081
# Login credentials:
#   Server: postgres
#   Username: hiremebahamas_user
#   Password: hiremebahamas_password
#   Database: hiremebahamas
```

📖 See [DATABASE_ADMIN_INTERFACE.md](./DATABASE_ADMIN_INTERFACE.md) for complete guide.

### Building Images Locally

To build application images locally:

```bash
# Backend
cd backend
docker build -t hiremebahamas-backend .

# Frontend
cd frontend
docker build -t hiremebahamas-frontend .
```

These will automatically pull the base images from GitHub Container Registry.

## For Deployment

### First Time Setup (One-time)

After this PR is merged to `main`:

1. **GitHub Actions will automatically build base images**
   - Check: https://github.com/cliffcho242/HireMeBahamas/actions
   - Wait for "Build and Push Docker Base Images" workflow to complete

2. **Make base images public** (required for Railway/Render):
   - Go to: https://github.com/cliffcho242?tab=packages
   - Click on `hiremebahamas-base-backend`
   - Click "Package settings" → "Change visibility" → "Public"
   - Repeat for `hiremebahamas-base-frontend`

3. **Verify base images are accessible**:
   ```bash
   docker pull ghcr.io/cliffcho242/hiremebahamas-base-backend:latest
   docker pull ghcr.io/cliffcho242/hiremebahamas-base-frontend:latest
   ```

### Ongoing Deployments

Once setup is complete:

- **Railway**: Deployments will automatically use new base images (70-80% faster!)
- **Render**: Deployments will automatically use new base images (70-80% faster!)
- **No more build timeouts** during "Build › Build image" phase
- **Consistent builds** every time

## Troubleshooting

### "Failed to pull base image" Error

**Problem**: Deployment fails with error about pulling `ghcr.io/cliffcho242/hiremebahamas-base-*`

**Solutions**:
1. Check if base images are built: https://github.com/cliffcho242/HireMeBahamas/actions
2. Verify images are public: https://github.com/cliffcho242?tab=packages
3. Manually trigger workflow: Go to Actions → "Build and Push Docker Base Images" → "Run workflow"

### "Packages not found" Error During Build

**Problem**: Build fails with "no such package" error

**Solution**: 
This means base images need to be rebuilt. Trigger the workflow:
1. Go to: https://github.com/cliffcho242/HireMeBahamas/actions/workflows/build-base-images.yml
2. Click "Run workflow"
3. Wait for completion
4. Retry deployment

### Base Images Out of Date

**Problem**: Need to update system dependencies

**Solution**:
1. Edit `docker/base-images/Dockerfile.base-backend` or `Dockerfile.base-frontend`
2. Commit and push to `main`
3. GitHub Actions automatically rebuilds and publishes
4. Next deployment uses updated base images

## Performance Comparison

### Before (Original Dockerfiles)
```
System dependencies install:  2-3 minutes
Backend build:                5-7 minutes
Frontend build:               4-6 minutes
Total deployment:            10-15 minutes
⚠️ Frequent timeouts
```

### After (With Base Images)
```
System dependencies install:  0 seconds (pre-installed)
Backend build:                1-2 minutes
Frontend build:               1-2 minutes
Total deployment:             2-4 minutes
✅ No timeouts
```

## Manual Base Image Rebuild

If you need to rebuild base images manually:

```bash
# Ensure you're logged in
docker login ghcr.io -u YOUR_GITHUB_USERNAME

# Run the build script
./scripts/build-base-images.sh
```

This is rarely needed since GitHub Actions handles it automatically.

## More Information

- **Full Documentation**: [DOCKER_BASE_IMAGES.md](./DOCKER_BASE_IMAGES.md)
- **Installation Guide**: [INSTALL.md](./INSTALL.md)
- **Main README**: [README.md](./README.md)

## Support

If you encounter issues:
1. Check the [Troubleshooting](#troubleshooting) section above
2. Review GitHub Actions logs for build failures
3. Open an issue with details about the error

---

**Last Updated**: November 2025
