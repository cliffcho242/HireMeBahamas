# Docker & Docker Compose Setup Guide

This guide will help you install Docker and Docker Compose, which are required to run HireMeBahamas in production mode.

## 📋 Why Docker?

HireMeBahamas uses Docker to run:
- **PostgreSQL** - Production-ready database
- **Redis** - Caching and session storage
- **Adminer** - Database management interface

These services run in isolated containers, making setup consistent across all platforms.

## 🔧 Installation

### Windows

#### Option 1: Docker Desktop (Recommended)
1. Download **Docker Desktop** from: https://www.docker.com/products/docker-desktop
2. Run the installer
3. Restart your computer
4. Open Docker Desktop and wait for it to start
5. Verify installation:
   ```cmd
   docker --version
   docker compose version
   ```

#### Option 2: WSL2 with Docker
1. Install WSL2: https://docs.microsoft.com/en-us/windows/wsl/install
2. Install Docker Desktop with WSL2 backend
3. Follow steps above

### macOS

#### Option 1: Docker Desktop (Recommended)
1. Download **Docker Desktop** from: https://www.docker.com/products/docker-desktop
2. Drag Docker to Applications folder
3. Open Docker Desktop from Applications
4. Wait for Docker to start (whale icon in menu bar)
5. Verify installation:
   ```bash
   docker --version
   docker compose version
   ```

#### Option 2: Homebrew
```bash
brew install --cask docker
# Open Docker Desktop from Applications
```

### Linux (Ubuntu/Debian)

#### Install Docker Engine
```bash
# Update package index
sudo apt-get update

# Install dependencies
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
sudo mkdir -m 0755 -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add your user to docker group (to run without sudo)
sudo usermod -aG docker $USER

# Log out and log back in for group changes to take effect
```

#### Verify Installation
```bash
docker --version
docker compose version
```

### Linux (Fedora/RHEL/CentOS)

```bash
# Install Docker
sudo dnf -y install dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group
sudo usermod -aG docker $USER

# Log out and log back in
```

### Linux (Arch)

```bash
# Install Docker
sudo pacman -S docker docker-compose

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group
sudo usermod -aG docker $USER

# Log out and log back in
```

## ✅ Verify Installation

After installation, verify Docker and Docker Compose are working:

```bash
# Check Docker version
docker --version
# Expected: Docker version 24.0.0 or higher

# Check Docker Compose version
docker compose version
# Expected: Docker Compose version v2.20.0 or higher

# Test Docker
docker run hello-world
# Expected: "Hello from Docker!" message

# Check if Docker daemon is running
docker ps
# Expected: Empty list (no errors)
```

## 🚀 Quick Start with HireMeBahamas

Once Docker is installed, you can start the services:

```bash
# Start PostgreSQL and Redis
docker compose up -d postgres redis

# Check services are running
docker compose ps

# View logs
docker compose logs postgres redis

# Stop services
docker compose down
```

## 🐛 Troubleshooting

### Docker Desktop won't start (Windows/macOS)
**Solution:**
1. Close Docker Desktop completely
2. Restart your computer
3. Open Docker Desktop again
4. Wait 2-3 minutes for initialization

### Permission denied (Linux)
```bash
# Error: permission denied while trying to connect to Docker daemon
# Solution: Add user to docker group and log out/in
sudo usermod -aG docker $USER
# Then log out and log back in
```

### Docker Compose not found
```bash
# Old docker-compose (with hyphen) not found
# Use new docker compose (with space) instead
docker compose version  # ✅ Correct
docker-compose version  # ❌ Old (deprecated)
```

### Port already in use
```bash
# Error: port 5432 is already allocated
# Solution: Stop existing PostgreSQL service
sudo systemctl stop postgresql  # Linux
brew services stop postgresql   # macOS
```

### WSL2 integration issues (Windows)
**Solution:**
1. Open Docker Desktop
2. Settings → Resources → WSL Integration
3. Enable integration for your WSL2 distro
4. Click "Apply & Restart"

## 📚 Additional Resources

### Official Documentation
- Docker: https://docs.docker.com/get-docker/
- Docker Compose: https://docs.docker.com/compose/install/

### Docker Basics
```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# View container logs
docker logs <container-id>

# Stop all containers
docker stop $(docker ps -q)

# Remove all stopped containers
docker container prune

# View Docker images
docker images

# Remove unused images
docker image prune
```

### Docker Compose Basics
```bash
# Start services in background
docker compose up -d

# Start specific services
docker compose up -d postgres redis

# Stop services
docker compose down

# Stop and remove volumes (⚠️ deletes data)
docker compose down -v

# View logs
docker compose logs

# Follow logs in real-time
docker compose logs -f

# Restart a service
docker compose restart postgres

# Rebuild and start
docker compose up -d --build
```

## 🎯 Next Steps

After installing Docker:
1. Return to [PRODUCTION_MODE_GUIDE.md](./PRODUCTION_MODE_GUIDE.md)
2. Run `./start_production.sh` (Linux/macOS) or `start_production.bat` (Windows)
3. Access the application at http://localhost:3000

## 💡 Tips

- **Keep Docker Desktop running** while developing
- **Docker uses system resources** - allocate enough RAM (4GB minimum, 8GB recommended)
- **Update regularly** - Docker releases important updates frequently
- **Check Docker Dashboard** - Visual interface to manage containers (Desktop versions)
- **Use docker compose** - Modern replacement for docker-compose

---

**Need help?** Check the [official Docker documentation](https://docs.docker.com/) or ask in the project issues.
