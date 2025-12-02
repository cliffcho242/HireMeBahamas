# Master Network Fix - Troubleshooting and Updates

## Overview

The Master Network Fix (`master_network_fix.py`) is a cross-platform utility script that ensures the HireMeBahamas backend server starts reliably and network connectivity is optimal.

## Recent Updates (December 2025)

### Issue: Master Fix App Dying

**Problem:** The master_network_fix.py script was failing to start due to:
1. Missing database dependencies (psycopg2)
2. Windows-only commands on Linux systems
3. Incomplete package installation list

**Solution:** 
- ✅ Added `psycopg2-binary` to required packages
- ✅ Made the script cross-platform compatible (Windows, Linux, macOS)
- ✅ Platform-aware networking configuration
- ✅ Platform-aware port management

### Changes Made

#### 1. Added Database Dependencies

```python
packages = [
    # ... existing packages ...
    "psycopg2-binary",  # Database adapter for PostgreSQL
]
```

#### 2. Cross-Platform Port Management

The `check_port_availability()` function now detects the operating system and uses:
- **Windows**: PowerShell commands with `Get-NetTCPConnection`
- **Linux/Unix**: `lsof` and `kill` commands

#### 3. Cross-Platform Networking Configuration

The `configure_system_networking()` function (formerly `configure_windows_networking()`) now:
- Detects the operating system
- Runs platform-appropriate network configuration commands
- Gracefully handles missing utilities

## Usage

### Windows

```powershell
# Run the PowerShell launcher
.\START_MASTER_FIX.ps1

# Or run directly with Python
python master_network_fix.py
```

### Linux/macOS

```bash
# Run directly
python3 master_network_fix.py

# Or make executable and run
chmod +x master_network_fix.py
./master_network_fix.py
```

## System Requirements

### All Platforms
- Python 3.8 or higher
- pip (Python package installer)

### Windows
- PowerShell (for network configuration)
- Administrator rights (recommended for network stack reset)

### Linux
- `lsof` utility (for port management)
- `systemd-resolved` (optional, for DNS flushing)

## Features

### 1. Automatic Package Installation
Installs all required Python packages:
- Flask and extensions (CORS, Limiter, Caching)
- WSGI servers (Waitress, Gunicorn)
- Async libraries (gevent, eventlet)
- Security (PyJWT, bcrypt)
- Database (psycopg2-binary)
- Utilities (python-dotenv, requests)

### 2. Port Management
- Checks if port 9999 (or 8080) is available
- Automatically kills blocking processes
- Falls back to alternative port if needed

### 3. Network Configuration
- Resets network stack (Windows)
- Flushes DNS cache
- Configures optimal TCP/IP settings

### 4. Server Startup
- Imports and validates the Flask app
- Starts with Waitress server (most reliable)
- Falls back to Flask development server if needed
- Verifies server is accepting connections

### 5. Health Testing
Creates a network test script (`test_admin_network.py`) to verify admin login functionality.

## Troubleshooting

### Script Won't Start

**Error: `ModuleNotFoundError: No module named 'psycopg2'`**

Solution: The script now automatically installs psycopg2-binary. If it still fails:
```bash
pip install psycopg2-binary
```

**Error: `ModuleNotFoundError: No module named 'final_backend'`**

Solution: Ensure you're running the script from the repository root directory:
```bash
cd /path/to/HireMeBahamas
python3 master_network_fix.py
```

### Port Already in Use

The script automatically attempts to kill processes using ports 9999 and 8080.

**On Linux**, ensure you have `lsof` installed:
```bash
sudo apt-get install lsof  # Ubuntu/Debian
sudo yum install lsof       # RHEL/CentOS
```

### Network Configuration Fails

**Windows**: Run PowerShell as Administrator for full network stack reset capabilities.

**Linux**: The script will skip advanced networking configuration if run without sudo. This is usually fine for local development.

### Server Won't Accept Connections

If the server starts but doesn't accept connections:

1. Check firewall settings
2. Verify no other process is using the port
3. Check the logs in `network_master_fix.log`
4. Try running on an alternative port (8080)

## Logs

The script creates a log file: `network_master_fix.log`

Check this file for detailed information about:
- Package installations
- Port availability checks
- Network configuration commands
- Server startup process
- Any errors encountered

## Cross-Platform Compatibility

### Tested Platforms
- ✅ Windows 10/11
- ✅ Ubuntu 20.04/22.04
- ✅ macOS 12+
- ✅ GitHub Actions runners (Ubuntu)

### Platform-Specific Notes

**Windows**:
- Full networking reset requires Administrator privileges
- PowerShell commands work on Windows 10+

**Linux**:
- DNS flushing requires systemd-resolved
- Port killing requires lsof utility
- Some operations may require sudo

**macOS**:
- Similar to Linux behavior
- May need to allow Python network access in Security preferences

## Related Scripts

- `START_MASTER_FIX.ps1` - PowerShell launcher for Windows
- `START_MASTER_FIX.bat` - Batch file launcher for Windows
- `test_admin_network.py` - Auto-generated network test script
- `final_backend.py` - The Flask backend being started

## Support

If you encounter issues not covered here:

1. Check `network_master_fix.log` for detailed error messages
2. Ensure all system requirements are met
3. Try running with elevated privileges (admin/sudo)
4. Verify `final_backend.py` is present and valid
5. Check that required environment variables are set (DATABASE_URL, etc.)

## Future Improvements

Potential enhancements:
- Docker containerization option
- Automatic environment variable setup
- Integration with systemd/Windows Service
- Health monitoring and auto-restart
- Multi-backend support
