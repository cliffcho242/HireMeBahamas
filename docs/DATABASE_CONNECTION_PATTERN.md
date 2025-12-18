# Database Connection Pattern

## ✅ CORRECT: Lazy Database Connection Initialization

This project implements **lazy database connection initialization** to prevent connection issues during application startup and serverless cold starts.

### How It Works

All database configuration files use a `LazyEngine` wrapper pattern:

```python
# Global engine instance (initialized lazily on first use)
_engine = None
_engine_lock = threading.Lock()

def get_engine():
    """Get or create database engine (lazy initialization for serverless)."""
    global _engine
    
    if _engine is None:
        with _engine_lock:
            if _engine is None:
                _engine = create_async_engine(
                    DATABASE_URL,
                    pool_size=POOL_SIZE,
                    # ... other configuration
                )
    
    return _engine

# Wrap engine for backward compatibility
class LazyEngine:
    """Wrapper to provide lazy engine initialization."""
    def __getattr__(self, name: str):
        actual_engine = get_engine()  # Engine created here on first access
        return getattr(actual_engine, name)

engine = LazyEngine()
```

### Session Management

Use dependency injection for database sessions:

```python
async def get_db():
    """Get database session with automatic cleanup."""
    async with AsyncSessionLocal() as session:
        yield session
```

Then use it in FastAPI endpoints:

```python
@app.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    # Database connection is created lazily on first request
    result = await db.execute(select(User))
    return result.scalars().all()
```

### ❌ WRONG: Connecting at Import Time

**DO NOT** do this at module level:

```python
# ❌ BAD - Connects immediately when module is imported
engine = create_async_engine(DATABASE_URL)
conn = engine.connect()  # Blocks app startup & requests
```

### Benefits of Lazy Initialization

1. **No startup failures**: App can start even if database is temporarily unavailable
2. **Serverless-friendly**: Connections created only when needed (not during cold start)
3. **Resource efficient**: No idle connections during module import
4. **Render/Vercel compatible**: Works with serverless platforms and managed databases

## Request Timeout Protection

All HTTP requests using the `requests` library should include a `timeout` parameter:

### ✅ CORRECT: With Timeout

```python
import requests

# For health checks (fast response expected)
response = requests.get("http://localhost:8000/health", timeout=5)

# For API calls (reasonable network latency)
response = requests.post(
    "http://api.example.com/endpoint",
    json=data,
    timeout=10
)

# For external services (may be slower)
response = requests.get("https://external-api.com/data", timeout=30)
```

### ❌ WRONG: Without Timeout

```python
# ❌ BAD - Can hang indefinitely if server doesn't respond
response = requests.get("http://api.example.com/endpoint")
```

### Recommended Timeout Values

- **5 seconds**: Local health checks, fast endpoints
- **10 seconds**: Standard API calls, GitHub API
- **30 seconds**: External services, slow operations
- **Custom**: Adjust based on expected response time

### Why Timeouts Matter

1. **Prevent hanging requests**: Requests can hang indefinitely without timeout
2. **Better error handling**: Fail fast instead of blocking
3. **Resource protection**: Don't tie up threads/processes waiting
4. **User experience**: Faster feedback on failures

## Files Using These Patterns

### Database Connection (Lazy Engine)
- `/api/backend_app/database.py` - Backend database configuration
- `/backend/app/database.py` - Main database configuration
- `/api/database.py` - API database configuration

### Request Timeouts
- `/check_deployed.py` - Render deployment checker
- `/start_app_automated.py` - Application launcher
- `/backend_monitor.py` - Backend health monitor
- `/scripts/check_pr_status.py` - GitHub PR status checker
- And many test files...

## Testing These Patterns

### Test Lazy Initialization

```python
# Engine should not connect until first use
from backend.app.database import engine

# No connection yet - just imported the LazyEngine wrapper
print("Engine imported, no connection created yet")

# Connection created on first access
async with engine.begin() as conn:
    await conn.execute(text("SELECT 1"))
print("Connection created successfully")
```

### Test Request Timeouts

```python
import requests
from time import time

start = time()
try:
    # This will timeout after 5 seconds if server is slow
    response = requests.get("http://slow-server.com/api", timeout=5)
except requests.Timeout:
    elapsed = time() - start
    print(f"Request timed out after {elapsed:.2f} seconds (expected ~5s)")
```

## CI/CD Considerations

These patterns are especially important for:
- **GitHub Actions**: Workflows start fresh environments
- **Render/Vercel**: Serverless functions with cold starts  
- **Docker containers**: May start before database is ready
- **Health checks**: Need fast timeouts to detect issues quickly

## References

- [SQLAlchemy Async Engine](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Requests Timeouts](https://requests.readthedocs.io/en/latest/user/advanced/#timeouts)
- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
