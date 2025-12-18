# BACKEND_URL Environment Variable Usage Guide

This guide explains how to use the `BACKEND_URL` environment variable in HireMeBahamas Python scripts.

## Overview

The `BACKEND_URL` environment variable is used to configure the backend API URL for health checks, testing, and external service integrations.

## Quick Start

### Setting BACKEND_URL

```bash
# For development (local backend)
export BACKEND_URL=http://localhost:8000

# For Render deployment
export BACKEND_URL=https://hiremebahamas-backend.render.app

# For Vercel deployment
export BACKEND_URL=https://hiremebahamas.vercel.app

# For Render deployment
export BACKEND_URL=https://hiremebahamas.onrender.com
```

### Basic Usage Pattern

The recommended pattern for using `BACKEND_URL` is:

```python
import os
import requests

# Get backend URL from environment variable
BASE_URL = os.environ["BACKEND_URL"]

# Use it with health check endpoint
response = requests.get(f"{BASE_URL}/health")
```

## Usage Patterns

### Pattern 1: Strict (Production Scripts)

For production deployment scripts that **must** have `BACKEND_URL` set:

```python
import os
import sys
import requests

try:
    BASE_URL = os.environ["BACKEND_URL"]
except KeyError:
    print("ERROR: BACKEND_URL environment variable is not set")
    sys.exit(1)

# Validate URL format
if not BASE_URL.startswith(("http://", "https://")):
    print(f"ERROR: BACKEND_URL must start with http:// or https://")
    sys.exit(1)

# Use the URL
response = requests.get(f"{BASE_URL}/health")
```

**Examples:**
- `keep_alive.py` - Background worker for keeping services alive
- `example_backend_health_check.py` - Health check demonstration

### Pattern 2: Flexible (Development/Testing Scripts)

For development and testing scripts with fallback defaults:

```python
import os
import requests

# Get backend URL with fallback for convenience
BASE_URL = os.getenv("BACKEND_URL", "https://hiremebahamas.vercel.app")

# Maintain backward compatibility if needed
BACKEND_URL = BASE_URL

# Use the URL
response = requests.get(f"{BASE_URL}/health")
```

**Examples:**
- `comprehensive_api_test.py` - API integration tests
- `test_hireme.py` - HireMe feature tests
- `init_admin_render.py` - Admin initialization

## Files Using BACKEND_URL

### Updated Files

| File | Pattern | Description |
|------|---------|-------------|
| `keep_alive.py` | Strict | Background worker for service keepalive |
| `comprehensive_api_test.py` | Flexible | Comprehensive API endpoint testing |
| `test_hireme.py` | Flexible | HireMe functionality testing |
| `init_admin_render.py` | Flexible | Admin user initialization |
| `example_backend_health_check.py` | Strict | Example health check script |

### Test Files

| File | Purpose |
|------|---------|
| `tests/test_backend_url_pattern.py` | Validates BACKEND_URL usage patterns |
| `tests/test_keep_alive.py` | Tests keep_alive.py functionality |

## Environment Configuration

### .env File

Add `BACKEND_URL` to your `.env` file:

```bash
# Backend URL Configuration
# Set this to your backend API URL for external services and health checks
BACKEND_URL=http://localhost:8000
```

See `.env.example` for complete configuration options.

### Deployment Platforms

#### Render
```bash
# Set in Render Dashboard → Your Service → Variables
BACKEND_URL=https://your-app.up.render.app
```

#### Vercel
```bash
# Set in Vercel Dashboard → Your Project → Settings → Environment Variables
BACKEND_URL=https://your-app.vercel.app
```

#### Render
```bash
# Set in Render Dashboard → Your Service → Environment
BACKEND_URL=https://your-app.onrender.com
```

#### GitHub Actions
```yaml
# Set in workflow file or repository secrets
env:
  BACKEND_URL: https://your-app.up.render.app
```

## Common Use Cases

### Health Check

```python
import os
import requests

BASE_URL = os.environ["BACKEND_URL"]

response = requests.get(f"{BASE_URL}/health", timeout=10)
if response.status_code == 200:
    data = response.json()
    print(f"Status: {data['status']}")
```

### API Testing

```python
import os
import requests

BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Test authentication
response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"email": "test@example.com", "password": "test123"}
)
```

### Keep-Alive Worker

```python
import os
import time
import requests

BASE_URL = os.environ["BACKEND_URL"]
HEALTH_URL = f"{BASE_URL}/health"

while True:
    try:
        response = requests.get(HEALTH_URL, timeout=30)
        print(f"Ping successful: {response.status_code}")
    except Exception as e:
        print(f"Ping failed: {e}")
    
    time.sleep(45)  # Wait 45 seconds between pings
```

## Testing

Run the test suite to verify BACKEND_URL usage:

```bash
# Run BACKEND_URL pattern tests
python -m unittest tests.test_backend_url_pattern -v

# Run all tests
python -m unittest discover tests -v
```

## Troubleshooting

### Error: BACKEND_URL not set

```
KeyError: 'BACKEND_URL'
```

**Solution:** Set the environment variable before running the script:
```bash
export BACKEND_URL=https://your-backend-url.com
python your_script.py
```

### Error: Invalid URL format

```
ERROR: BACKEND_URL must start with http:// or https://
```

**Solution:** Ensure your URL includes the protocol:
```bash
export BACKEND_URL=https://your-app.com  # Correct
# Not: export BACKEND_URL=your-app.com   # Wrong
```

### Connection Failed

```
❌ Connection failed
```

**Possible causes:**
1. Backend is not running
2. Wrong URL or port
3. Network/firewall issues
4. Backend is sleeping (free tier services)

**Solution:** Verify the backend is accessible:
```bash
curl $BACKEND_URL/health
```

## Best Practices

1. **Always set BACKEND_URL** in production deployments
2. **Use strict pattern** for production scripts
3. **Use flexible pattern** for development/testing
4. **Validate URL format** before using
5. **Include timeout** in requests (e.g., `timeout=10`)
6. **Handle errors gracefully** with try-except blocks
7. **Document** which scripts require BACKEND_URL

## Security Considerations

1. **Never commit** `.env` files with production URLs
2. **Use environment variables** instead of hardcoding URLs
3. **Validate** URL format to prevent injection
4. **Use HTTPS** in production for encrypted connections
5. **Rotate** credentials if exposed in environment variables

## Related Documentation

- [.env.example](.env.example) - Environment variable configuration
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Deployment instructions
- [README.md](README.md) - Project overview

## Examples

See these files for implementation examples:
- [`example_backend_health_check.py`](example_backend_health_check.py) - Complete health check example
- [`keep_alive.py`](keep_alive.py) - Production keep-alive worker
- [`comprehensive_api_test.py`](comprehensive_api_test.py) - API testing suite
