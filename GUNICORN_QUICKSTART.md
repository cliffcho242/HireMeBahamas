# Gunicorn Quick Start Guide

## TL;DR

All deployment platforms now use a simplified Gunicorn command that references `gunicorn.conf.py`:

```bash
cd backend && poetry run gunicorn app.main:app --config gunicorn.conf.py
```

## What Changed?

### Before (Inline Arguments):
```bash
gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --workers 1 --timeout 120
```

### After (Config File):
```bash
gunicorn app.main:app --config gunicorn.conf.py
```

All settings are now in `backend/gunicorn.conf.py`.

## Configuration

### Default Settings:
- **Workers**: 1 (optimal for small instances)
- **Worker Class**: uvicorn.workers.UvicornWorker (FastAPI async)
- **Timeout**: 120 seconds
- **Graceful Timeout**: 30 seconds
- **Keepalive**: 5 seconds

### Environment Variables (Optional):
Override defaults with these environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 10000 | Bind port |
| `WEB_CONCURRENCY` | 1 | Number of workers |
| `WEB_THREADS` | 2 | Threads per worker |
| `GUNICORN_TIMEOUT` | 120 | Worker timeout (seconds) |

Example:
```bash
export WEB_CONCURRENCY=2
export GUNICORN_TIMEOUT=180
poetry run gunicorn app.main:app --config gunicorn.conf.py
```

## Local Development

### Run the Server:
```bash
cd backend
poetry run gunicorn app.main:app --config gunicorn.conf.py
```

### With Custom Port:
```bash
PORT=8000 poetry run gunicorn app.main:app --config gunicorn.conf.py
```

### Development Mode (with reload):
```bash
# For development, use uvicorn directly with --reload
poetry run uvicorn app.main:app --reload --port 8000
```

## Deployment

### Render:
Configured in `render.yaml`:
```yaml
startCommand: cd backend && poetry run gunicorn app.main:app --config gunicorn.conf.py
```

### Railway:
Configured in `nixpacks.toml`:
```toml
cmd = "cd backend && poetry run gunicorn app.main:app --config gunicorn.conf.py"
```

### Heroku:
Configured in `Procfile`:
```
web: cd backend && poetry run gunicorn app.main:app --config gunicorn.conf.py
```

### Docker:
Configured in `backend/Dockerfile`:
```dockerfile
CMD ["sh", "-c", "gunicorn app.main:app --config gunicorn.conf.py"]
```

## Health Check

Verify the server is running:
```bash
curl http://localhost:8000/health
# Expected: {"status":"ok"}
```

## Troubleshooting

### Server won't start?
1. Check you're in the `backend` directory: `cd backend`
2. Verify Poetry is installed: `poetry --version`
3. Check the config file exists: `ls gunicorn.conf.py`
4. View startup logs for errors

### Wrong port?
Set the PORT environment variable:
```bash
export PORT=8000
poetry run gunicorn app.main:app --config gunicorn.conf.py
```

### Need more workers?
Set WEB_CONCURRENCY:
```bash
export WEB_CONCURRENCY=4
poetry run gunicorn app.main:app --config gunicorn.conf.py
```

### Timeout errors?
Increase GUNICORN_TIMEOUT:
```bash
export GUNICORN_TIMEOUT=300
poetry run gunicorn app.main:app --config gunicorn.conf.py
```

## Production Best Practices

✅ **DO**:
- Use 1 worker for small instances (< 1GB RAM)
- Use 2-4 workers for larger instances
- Set appropriate timeout (120s minimum)
- Use environment variables for configuration
- Monitor worker logs for SIGTERM/SIGABRT

❌ **DON'T**:
- Use `--reload` in production
- Set `preload_app = True` with databases
- Use `--preload` flag (conflicts with config)
- Set workers > available CPU cores
- Ignore worker timeout warnings

## Advanced Configuration

Edit `backend/gunicorn.conf.py` to customize:
- Worker lifecycle hooks
- Logging configuration
- Memory management
- Security settings
- Process naming

See the config file for detailed comments on each setting.

## References

- Full documentation: `GUNICORN_CONFIG_FIX_SUMMARY.md`
- Gunicorn docs: https://docs.gunicorn.org/
- FastAPI deployment: https://fastapi.tiangolo.com/deployment/
- Uvicorn workers: https://www.uvicorn.org/deployment/

## Summary

✨ **Simple command, powerful configuration**

The new approach:
1. Keeps commands clean and maintainable
2. Centralizes all settings in one file
3. Provides production-grade worker management
4. Supports environment-based configuration
5. Works consistently across all platforms
