# Read Replica Setup - Neon Database (Zero Downtime Scaling)

## Overview

HireMeBahamas implements read replica support for horizontal database scaling. This allows the application to handle increased read traffic by distributing SELECT queries across multiple database instances while maintaining data consistency.

## Architecture

```
                    API Requests
                         |
                         |
                    FastAPI App
                    /          \
                   /            \
              WRITE           READ
           (INSERT,         (SELECT,
            UPDATE,          COUNT)
            DELETE)
                |              |
                |              |
                v              v
         ┌─────────────┐  ┌─────────────┐
         │   Primary   │  │ Read Replica│
         │  Database   │──│  Database   │
         │  (Neon)     │  │   (Neon)    │
         └─────────────┘  └─────────────┘
         DATABASE_URL     DATABASE_URL_READ
```

### Key Benefits

- **Zero Downtime Scaling**: Add read replicas without code changes
- **Automatic Failover**: Falls back to primary if replica unavailable
- **Improved Performance**: Distribute read load across multiple databases
- **Cost Effective**: Neon read replicas are cheaper than scaling primary
- **Simple Integration**: Just set environment variable and use appropriate dependency

## Neon Read Replica Setup

### 1. Create Read Replica in Neon

1. Log in to [Neon Console](https://console.neon.tech)
2. Select your project
3. Go to **Branches** → **Create Read Replica**
4. Configure:
   - **Region**: Same as primary for low latency
   - **Compute size**: Based on read load (can be smaller than primary)
5. Copy the connection string

### 2. Set Environment Variables

Add both database URLs to your environment:

```bash
# Primary database (for writes)
DATABASE_URL=postgresql://user:password@ep-primary-xxx.us-east-2.aws.neon.tech:5432/mydb?sslmode=require

# Read replica (for reads)
DATABASE_URL_READ=postgresql://user:password@ep-replica-xxx.us-east-2.aws.neon.tech:5432/mydb?sslmode=require
```

**Important**: 
- Both URLs must point to the same database
- Read replica URL will have a different hostname
- Use the same credentials
- Include `?sslmode=require` for security

### 3. Configure Pool Settings (Optional)

Read replicas can handle more connections:

```bash
# Read replica pool configuration
DB_READ_POOL_SIZE=10          # Higher than primary
DB_READ_MAX_OVERFLOW=10       # Higher than primary
DB_READ_POOL_RECYCLE=300      # 5 minutes
DB_READ_CONNECT_TIMEOUT=5     # 5 seconds
```

## Usage in Code

### FastAPI Dependencies

Use `get_db_read()` for read operations and `get_db_write()` for write operations:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend_app.core.read_replica import get_db_read, get_db_write

router = APIRouter()

# ✅ Read operation - uses read replica
@router.get("/users")
async def list_users(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db_read)  # Use read replica
):
    """List users - read-only operation"""
    result = await db.execute(
        select(User).offset(skip).limit(limit)
    )
    return result.scalars().all()


# ✅ Read operation - uses read replica
@router.get("/posts/{post_id}")
async def get_post(
    post_id: int,
    db: AsyncSession = Depends(get_db_read)  # Use read replica
):
    """Get single post - read-only operation"""
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


# ✅ Write operation - uses primary database
@router.post("/posts")
async def create_post(
    post: PostCreate,
    db: AsyncSession = Depends(get_db_write),  # Use primary
    current_user: User = Depends(get_current_user)
):
    """Create post - write operation"""
    db_post = Post(**post.dict(), author_id=current_user.id)
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    return db_post


# ✅ Write operation - uses primary database
@router.put("/posts/{post_id}")
async def update_post(
    post_id: int,
    post_update: PostUpdate,
    db: AsyncSession = Depends(get_db_write),  # Use primary
    current_user: User = Depends(get_current_user)
):
    """Update post - write operation"""
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404)
    
    for key, value in post_update.dict(exclude_unset=True).items():
        setattr(post, key, value)
    
    await db.commit()
    return post


# ✅ Write operation - uses primary database
@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db_write),  # Use primary
    current_user: User = Depends(get_current_user)
):
    """Delete post - write operation"""
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404)
    
    await db.delete(post)
    await db.commit()
    return {"success": True}
```

### Query Type Guidelines

| Operation | Database | Dependency |
|-----------|----------|------------|
| SELECT | Read Replica | `get_db_read()` |
| COUNT | Read Replica | `get_db_read()` |
| JOIN (read-only) | Read Replica | `get_db_read()` |
| INSERT | Primary | `get_db_write()` |
| UPDATE | Primary | `get_db_write()` |
| DELETE | Primary | `get_db_write()` |
| Transaction | Primary | `get_db_write()` |

### Handling Replication Lag

For operations that require immediate consistency (read-after-write):

```python
@router.post("/posts")
async def create_post(
    post: PostCreate,
    db_write: AsyncSession = Depends(get_db_write)
):
    # Create post
    db_post = Post(**post.dict())
    db_write.add(db_post)
    await db_write.commit()
    await db_write.refresh(db_post)
    
    # ✅ Read from primary to get immediate consistency
    # (use same session used for write)
    result = await db_write.execute(
        select(Post).where(Post.id == db_post.id)
    )
    created_post = result.scalar_one()
    
    return created_post


@router.get("/posts/{post_id}")
async def get_post(
    post_id: int,
    force_primary: bool = False,  # Optional parameter
    db_read: AsyncSession = Depends(get_db_read),
    db_write: AsyncSession = Depends(get_db_write)
):
    # Use primary if requested (for critical reads)
    db = db_write if force_primary else db_read
    
    post = await db.get(Post, post_id)
    return post
```

## Monitoring

### Health Check Endpoint

Add health check for read replica:

```python
from backend_app.core.read_replica import check_read_replica_health, get_read_replica_pool_status

@router.get("/health/database")
async def database_health():
    """Check database health including read replica"""
    from backend_app.database import test_db_connection, get_pool_status
    
    # Check primary database
    primary_ok, primary_error = await test_db_connection()
    primary_pool = await get_pool_status()
    
    # Check read replica
    replica_health = await check_read_replica_health()
    replica_pool = await get_read_replica_pool_status()
    
    return {
        "primary": {
            "status": "healthy" if primary_ok else "unhealthy",
            "error": primary_error,
            "pool": primary_pool
        },
        "replica": {
            "status": replica_health["status"],
            "latency_ms": replica_health.get("latency_ms"),
            "pool": replica_pool
        }
    }
```

### Metrics to Monitor

1. **Replication Lag**
   - Monitor time difference between primary and replica
   - Alert if lag > 5 seconds

2. **Query Distribution**
   - Track read/write ratio
   - Ensure reads are using replica

3. **Connection Pool Usage**
   - Monitor pool exhaustion
   - Scale replicas if needed

4. **Failover Events**
   - Log when replica is unavailable
   - Track fallback to primary

## Deployment

### Vercel

Set environment variables in Vercel dashboard:

```bash
# Project Settings → Environment Variables
DATABASE_URL=postgresql://...primary...
DATABASE_URL_READ=postgresql://...replica...
```

Deploy:
```bash
vercel --prod
```

### Railway

Set environment variables in Railway dashboard:

```bash
# Add to service variables
DATABASE_URL=postgresql://...primary...
DATABASE_URL_READ=postgresql://...replica...
```

### Docker

Update `docker-compose.yml`:

```yaml
services:
  api:
    environment:
      - DATABASE_URL=postgresql://...primary...
      - DATABASE_URL_READ=postgresql://...replica...
```

## Scaling Strategy

### When to Add Read Replicas

1. **Read-Heavy Workload**
   - More than 70% SELECT queries
   - Feed/timeline endpoints with high traffic

2. **Geographic Distribution**
   - Users in multiple regions
   - Reduce latency with regional replicas

3. **High Concurrency**
   - Many simultaneous users
   - Connection pool exhaustion

### Neon Scaling

```
Development:
- Primary: Compute 0.25 (free tier)
- No replica

Production (Small):
- Primary: Compute 1
- Replica 1: Compute 0.5 (same region)

Production (Large):
- Primary: Compute 2
- Replica 1: Compute 1 (us-east)
- Replica 2: Compute 1 (eu-west)
- Replica 3: Compute 1 (ap-south)
```

## Troubleshooting

### Replica Not Being Used

1. Check environment variable:
   ```bash
   echo $DATABASE_URL_READ
   ```

2. Check logs for replica connection:
   ```
   INFO: Read replica configured - routing read queries to replica
   ```

3. Verify endpoints use `get_db_read()`:
   ```python
   db: AsyncSession = Depends(get_db_read)  # Not get_db()
   ```

### Replication Lag Issues

1. Check Neon replication lag:
   - Neon Console → Monitoring → Replication Lag

2. For critical reads, use primary:
   ```python
   db: AsyncSession = Depends(get_db_write)
   ```

3. Increase replica compute size in Neon

### Connection Errors

1. Verify replica URL format:
   ```
   postgresql://user:pass@ep-replica-xxx.region.aws.neon.tech:5432/db?sslmode=require
   ```

2. Check replica is active in Neon Console

3. Test connection manually:
   ```bash
   psql "postgresql://user:pass@replica-host:5432/db?sslmode=require"
   ```

## Best Practices

1. **Use Correct Dependency**
   - ✅ `get_db_read()` for SELECT
   - ✅ `get_db_write()` for INSERT/UPDATE/DELETE
   - ❌ Don't use `get_db()` directly

2. **Handle Replication Lag**
   - Use primary for read-after-write scenarios
   - Add retry logic for critical reads

3. **Monitor Performance**
   - Track query distribution
   - Monitor replication lag
   - Alert on failover events

4. **Graceful Degradation**
   - App continues working if replica fails
   - Automatic fallback to primary
   - Log warnings, don't crash

5. **Connection Pooling**
   - Higher pool size for replicas
   - Monitor pool usage
   - Scale replicas, not pool size

## Cost Optimization

### Neon Pricing

- Primary: $0.102/hour for 1 CU
- Read Replica: ~50% of primary cost
- Data transfer: Free within same region

### Example Costs

```
Small App (100 users):
- Primary: 1 CU × $0.102 × 720h = $73/mo
- Replica: 0.5 CU × $0.051 × 720h = $37/mo
Total: $110/mo

Medium App (1000 users):
- Primary: 2 CU × $0.204 × 720h = $147/mo
- Replica 1: 1 CU × $0.102 × 720h = $73/mo
- Replica 2: 1 CU × $0.102 × 720h = $73/mo
Total: $293/mo
```

## Support

For issues or questions:
- Neon Documentation: https://neon.tech/docs/guides/read-replicas
- GitHub Issues: https://github.com/cliffcho242/HireMeBahamas/issues
- Architecture: See SCALING_STRATEGY.md
