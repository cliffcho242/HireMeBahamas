# Database Scaling Strategy for 100K+ Users

## Overview

This document outlines the database architecture and optimization strategies for scaling HireMeBahamas to 100K+ concurrent users.

## Current Implementation (Phase 1)

### Connection Pooling
- **Implementation**: psycopg2 connection pool in `final_backend_postgresql.py`
- **Configuration**: 
  - Min connections: 2
  - Max connections: 10 per worker
  - With 4 gunicorn workers: Up to 40 total connections
  
### Database Indexes

All critical indexes are implemented in `backend/create_database_indexes.py` and include:

#### User Table Indexes
- `idx_users_email_lower` - Case-insensitive email lookup for login (< 5ms)
- `idx_users_phone` - Phone number authentication
- `idx_users_active_role` - Filter active users by role
- `idx_users_available_for_hire` - HireMe page query optimization
- `idx_users_oauth` - OAuth login lookup

#### Posts Table Indexes
- `idx_posts_user_created` - User's posts listing (profile page)
- `idx_posts_feed` - Global feed chronological ordering
- `idx_posts_type_created` - Filter posts by type

#### Jobs Table Indexes
- `idx_jobs_employer_created` - User's posted jobs
- `idx_jobs_category_status` - Category filtering for active jobs
- `idx_jobs_location_remote` - Location and remote job filtering
- `idx_jobs_salary_range` - Salary range filtering
- `idx_jobs_active_created` - Latest active jobs listing
- `idx_jobs_title_trgm` - Full-text search (requires pg_trgm extension)

#### Social Features Indexes
- `idx_follows_follower_followed` - Unique follow relationship
- `idx_follows_followed` - User's followers list
- `idx_follows_follower` - User's following list
- `idx_post_likes_post_user` - Like tracking and uniqueness
- `idx_post_comments_post_created` - Comments for posts

#### Messaging Indexes
- `idx_messages_conversation_created` - Messages in conversation
- `idx_messages_receiver_unread` - Unread messages count (< 10ms)
- `idx_conversations_participants` - Unique conversation constraint

#### Notifications Indexes
- `idx_notifications_user_unread` - Unread notifications count
- `idx_notifications_user_created` - User's all notifications

### Query Performance Targets

Based on Meta's TAO/MySQL patterns:
- **Login queries**: < 5ms (email index)
- **Posts feed**: < 10ms (user_id + created_at composite)
- **Messages**: < 10ms (receiver_id + is_read)
- **Jobs search**: < 15ms (category, location, is_remote combined)

### Running Index Migration

To apply indexes:
```bash
python backend/create_database_indexes.py
```

Or add to Railway/Render build command:
```bash
python backend/create_database_indexes.py && gunicorn ...
```

## Future Implementation (Phase 2: Beyond 100K Users)

### Read Replica Strategy

When scaling beyond 100K concurrent users, implement read replicas:

#### Write Operations (Primary Database)
All write operations go to the primary database:
- User registration
- Post creation
- Job posting
- Profile updates
- Message sending
- Like/follow actions

#### Read Operations (Replica Databases)
Read-heavy operations can be distributed to replicas:
- Feed generation
- User profile viewing
- Job listings
- Search operations
- Message history

### Implementation Plan

#### 1. Connection Management

Update `final_backend_postgresql.py` to support multiple database connections:

```python
# Primary database (writes)
PRIMARY_DB_URL = os.getenv("DATABASE_URL")

# Read replicas (reads) - load balance across replicas
REPLICA_DB_URLS = os.getenv("DATABASE_REPLICA_URLS", "").split(",")

# Connection pools
_primary_pool = None
_replica_pools = []

def get_write_connection():
    """Get connection to primary database for write operations."""
    return _primary_pool.getconn()

def get_read_connection():
    """Get connection to a read replica for read operations (load balanced)."""
    if not _replica_pools:
        # Fallback to primary if no replicas configured
        return get_write_connection()
    
    # Round-robin load balancing across replicas
    pool = random.choice(_replica_pools)
    return pool.getconn()
```

#### 2. Query Routing

Route queries based on operation type:

```python
# Write operation - use primary
@app.route('/api/posts', methods=['POST'])
def create_post():
    conn = get_write_connection()
    # ... create post
    return_connection(conn, is_primary=True)

# Read operation - use replica
@app.route('/api/posts', methods=['GET'])
def get_posts():
    conn = get_read_connection()
    # ... fetch posts
    return_connection(conn, is_primary=False)
```

#### 3. Replication Lag Handling

Handle replication lag for consistency:

```python
def read_your_writes(user_id, operation, max_wait=5):
    """
    Ensure user sees their own writes immediately.
    
    After a write, temporarily read from primary for that user
    until replication catches up.
    """
    # After write: store timestamp in cache
    cache_key = f"last_write:{user_id}:{operation}"
    cache.set(cache_key, time.time(), timeout=max_wait)
    
    # On read: check if recent write exists
    last_write = cache.get(cache_key)
    if last_write and (time.time() - last_write) < max_wait:
        # Use primary for consistency
        return get_write_connection()
    else:
        # Use replica for performance
        return get_read_connection()
```

### Caching Strategy

#### Current Caching (Implemented)

Redis/SimpleCache for:
- User login data (10 minutes)
- Posts feed (30 seconds)
- Jobs listings (1 minute)
- User profiles (1 minute)

#### Advanced Caching (Future)

For 100K+ users:

1. **Query Result Caching**
   - Cache expensive JOIN queries
   - Cache aggregation queries (counts, stats)
   - TTL: 1-5 minutes depending on data freshness requirements

2. **Full-Page Caching**
   - Cache entire API responses for anonymous users
   - Use Vary headers for authenticated users
   - CDN integration (Cloudflare, Fastly)

3. **Database Query Caching**
   - PostgreSQL query plan caching
   - Materialized views for complex queries
   - Refresh materialized views in background jobs

### Monitoring & Optimization

#### Metrics to Track

1. **Database Performance**
   - Query latency (p50, p95, p99)
   - Connection pool utilization
   - Slow query log analysis
   - Index usage statistics

2. **Application Performance**
   - Request duration by endpoint
   - Cache hit rate
   - Background job queue depth
   - Worker utilization

3. **Infrastructure**
   - Database CPU/Memory usage
   - Network I/O
   - Disk IOPS
   - Connection count

#### Tools

- **PostgreSQL**: pg_stat_statements for query analysis
- **Application**: Flask metrics endpoint (`/metrics`)
- **Infrastructure**: Railway/Render built-in monitoring
- **APM**: Consider New Relic, Datadog, or Sentry Performance

### Sharding Strategy (Beyond 1M Users)

If scaling beyond 1M users, consider sharding:

#### Sharding Key Options

1. **User ID-based sharding**
   - Shard by user_id % N
   - Keeps user data together
   - Good for social features

2. **Geographic sharding**
   - Shard by location (Bahamas, Caribbean, International)
   - Reduces latency
   - Simplifies data sovereignty compliance

3. **Functional sharding**
   - Jobs database
   - Social database (posts, follows)
   - Messaging database
   - Allows independent scaling

#### Sharding Implementation

Use Citus extension for PostgreSQL or implement application-level sharding:

```python
def get_shard_connection(user_id):
    """Route to appropriate database shard based on user_id."""
    shard_id = user_id % NUM_SHARDS
    return _shard_pools[shard_id].getconn()
```

## Performance Testing

### Load Testing

Test database under realistic load:

```bash
# Install artillery
npm install -g artillery

# Run load test
artillery run load-test.yml
```

Example `load-test.yml`:
```yaml
config:
  target: 'https://api.hiremebahamas.com'
  phases:
    - duration: 300  # 5 minutes
      arrivalRate: 100  # 100 requests/second
      
scenarios:
  - name: "Browse Jobs"
    flow:
      - get:
          url: "/api/jobs"
      - think: 2
      
  - name: "View Profile"
    flow:
      - get:
          url: "/api/users/{{ $randomInt(1, 10000) }}"
```

### Query Analysis

Analyze slow queries:

```sql
-- Enable query statistics
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Find slow queries
SELECT 
    query,
    calls,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;

-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY idx_tup_read DESC;
```

## Migration Checklist

### Phase 1: Current (0-100K users) ✅
- [x] Connection pooling configured
- [x] Critical indexes created
- [x] Query optimization
- [x] Basic caching (Redis/SimpleCache)
- [x] Gunicorn worker scaling (4 workers)

### Phase 2: Scaling (100K-500K users)
- [ ] Read replicas configured
- [ ] Query routing implemented
- [ ] Replication lag handling
- [ ] Enhanced caching strategy
- [ ] APM integration
- [ ] Load testing completed

### Phase 3: Massive Scale (500K-1M users)
- [ ] Multiple read replicas per region
- [ ] Advanced caching (CDN, materialized views)
- [ ] Auto-scaling worker pools
- [ ] Database connection pooler (PgBouncer)
- [ ] Query result caching layer

### Phase 4: Enterprise Scale (1M+ users)
- [ ] Database sharding
- [ ] Geographic distribution
- [ ] Multi-region deployment
- [ ] Advanced monitoring and alerting
- [ ] Disaster recovery planning

## Resources

- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Scaling PostgreSQL](https://www.postgresql.org/docs/current/high-availability.html)
- [Meta's TAO Architecture](https://www.usenix.org/system/files/conference/atc13/atc13-bronson.pdf)
- [Database Index Optimization](https://use-the-index-luke.com/)

## Support

For questions or issues with database scaling:
1. Check Railway/Render database metrics
2. Review slow query logs
3. Run `python backend/test_database_indexes.py`
4. Consult this document for optimization strategies
