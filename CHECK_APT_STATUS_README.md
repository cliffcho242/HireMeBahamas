# APT-GET Status Checker

A comprehensive script to check the installation status and progress of all required system dependencies for the HireMeBahamas application.

## Features

- ✅ Checks installation status of all required apt packages
- ✅ Displays version information for installed packages
- ✅ Shows service status (PostgreSQL, Redis)
- ✅ Visual progress bar showing installation completion
- ✅ Lists missing packages with installation commands
- ✅ Checks APT cache status and last update time
- ✅ Color-coded output for easy reading

## Usage

```bash
# Make the script executable
chmod +x check_apt_status.sh

# Run the status checker
./check_apt_status.sh
```

## Sample Output

```
================================================================
  HireMeBahamas - APT-GET Dependency Status Check
================================================================

━━━ 1. Build Tools ━━━

✓ Build Essential (build-essential) - v12.10ubuntu1
✓ GCC Compiler (gcc) - v4:13.2.0-7ubuntu1
✓ G++ Compiler (g++) - v4:13.2.0-7ubuntu1
✓ Make Build Tool (make) - v4.3-4.1build2
✓ Package Config (pkg-config) - v1.8.1-2build1

━━━ 2. Python Dependencies ━━━

✓ Python 3 (python3) - v3.12.3-0ubuntu2
✓ Python pip (python3-pip) - v24.0+dfsg-1ubuntu1.3
✓ Python Dev Headers (python3-dev) - v3.12.3-0ubuntu2
✓ Python Virtual Env (python3-venv) - v3.12.3-0ubuntu2

...

━━━ 10. Runtime Commands ━━━

✓ Python 3: Python 3.12.3
✓ pip Package Manager: pip 24.0
✓ Node.js: v20.19.5
✓ npm Package Manager: 10.8.2
✓ PostgreSQL Client: psql (PostgreSQL) 16.10
✓ Redis CLI: redis-cli 7.0.15

━━━ 11. Services Status ━━━

✓ PostgreSQL Service: RUNNING
✓ Redis Service: RUNNING

━━━ 12. APT Cache Information ━━━

APT Cache Size: 52K
✓ Package lists are up to date (last updated 2 days ago)

================================================================
                    SUMMARY
================================================================

Total Packages Checked:    25
Installed Packages:        25
Missing Packages:          0
Installation Progress:     100%
[██████████████████████████████████████████████████] 100%

✓ All required packages are installed!

Next steps:
  1. Install Python packages: pip install -r requirements.txt
  2. Install frontend packages: cd frontend && npm install
  3. Run tests: python test_app_operational.py
```

## What It Checks

### 1. Build Tools
- build-essential
- gcc, g++, make
- pkg-config

### 2. Python Dependencies
- python3, python3-pip
- python3-dev, python3-venv

### 3. Database Dependencies
- postgresql, postgresql-client
- libpq-dev

### 4. Redis Cache
- redis-server, redis-tools

### 5. SSL/Crypto Libraries
- libssl-dev, libffi-dev

### 6. Image Processing Libraries
- libjpeg-dev, libpng-dev

### 7. Additional Libraries
- libevent-dev, libxml2-dev, libxslt1-dev

### 8. Web Server
- nginx

### 9. Essential Utilities
- curl, wget, git

### 10. Runtime Commands
- Verifies python3, pip, node, npm, psql, redis-cli are in PATH

### 11. Services
- Checks if PostgreSQL and Redis services are running

### 12. APT Cache
- Shows cache size and last update time

## Exit Codes

- **0**: All packages are installed
- **1**: Some packages are missing

## Integration

This script complements the other dependency management scripts:

- **install_dependencies.sh**: Installs all required dependencies
- **test_app_operational.py**: Tests application functionality
- **check_apt_status.sh**: Checks apt-get package status (this script)

## Recommended Workflow

```bash
# 1. Check current status
./check_apt_status.sh

# 2. If packages are missing, install them
./install_dependencies.sh

# 3. Verify status again
./check_apt_status.sh

# 4. Test application functionality
python test_app_operational.py
```

## Troubleshooting

If packages show as missing but you believe they're installed:

1. Check with dpkg directly:
   ```bash
   dpkg -l | grep package-name
   ```

2. Update package lists:
   ```bash
   sudo apt-get update
   ```

3. Verify package availability:
   ```bash
   apt-cache policy package-name
   ```

## Notes

- The script requires read access to dpkg and systemctl
- Some checks may require sudo privileges for full functionality
- Package names may vary slightly between Ubuntu versions
- The script is designed for Ubuntu/Debian-based systems

## See Also

- [DEPENDENCY_INSTALLATION_REPORT.md](DEPENDENCY_INSTALLATION_REPORT.md) - Complete technical report
- [QUICK_START_DEPENDENCIES.md](QUICK_START_DEPENDENCIES.md) - Quick start guide
- [install_dependencies.sh](install_dependencies.sh) - Installation script
- [test_app_operational.py](test_app_operational.py) - Operational tests
