# Permanent Data Storage & Token Configuration

## Overview

This document describes the implemented fixes to ensure:
1. **Tokens never expire** (365-day expiration)
2. **Posts are permanently stored** (never automatically deleted)
3. **Efficient handling of millions of posts** (pagination support)
4. **All system dependencies installed**

## 1. Token Never Expires

### Implementation
- Token expiration set to **365 days (1 year)**
- Default was 7 days, now extended to prevent frequent re-login
- Users stay logged in for a full year unless they manually log out

### Configuration
```python
# In final_backend_postgresql.py
TOKEN_EXPIRATION_DAYS = int(os.getenv("TOKEN_EXPIRATION_DAYS", "365"))
```

### Environment Variable
```bash
# Optional: Override in .env file
TOKEN_EXPIRATION_DAYS=365
```

### Benefits
- ✅ Users don't need to re-login after inactivity
- ✅ Prevents "can't sign in" issues after periods of inactivity
- ✅ Maintains session across server restarts (as long as database persists)

## 2. Posts Permanently Stored

### Implementation
Posts are **NEVER automatically deleted**. They remain in the database permanently unless:
1. User manually deletes their own post
2. Admin intervention

### Database Guarantees
- ✅ No automatic cleanup based on age
- ✅ No automatic deletion based on number of posts
- ✅ No deletion when posts "get lost in pages"
- ✅ Foreign key constraints ensure data integrity
- ✅ CASCADE delete only for related data (likes, comments when post is manually deleted)

### Deletion Policy
```python
# DELETE /api/posts/:id endpoint
# - Only the post owner can delete
# - No automatic deletion
# - Even with millions of posts, all remain stored
```

## 3. Handling Millions of Posts

### Pagination Support
The GET /api/posts endpoint now supports pagination to efficiently handle large datasets:

```bash
# Get first page (20 posts)
GET /api/posts

# Get specific page
GET /api/posts?page=2&per_page=50

# Parameters:
# - page: Page number (default: 1)
# - per_page: Posts per page (default: 20, max: 100)
```

### Response Format
```json
{
  "success": true,
  "posts": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_posts": 1000000,
    "total_pages": 50000,
    "has_next": true,
    "has_prev": false
  }
}
```

### Performance
- ✅ Uses LIMIT/OFFSET for efficient queries
- ✅ Supports up to millions of posts
- ✅ Client-side pagination support
- ✅ Index on created_at column for fast sorting

## 4. System Dependencies

### Core Dependencies (apt-get install)

```bash
# All required system dependencies
sudo apt-get update && sudo apt-get install -y \
    build-essential \
    gcc \
    g++ \
    make \
    pkg-config \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    postgresql \
    postgresql-client \
    libpq-dev \
    redis-server \
    redis-tools \
    libssl-dev \
    libffi-dev \
    libjpeg-dev \
    libpng-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    libwebp-dev \
    libevent-dev \
    libxml2-dev \
    libxslt1-dev \
    nginx \
    curl \
    wget \
    git \
    sqlite3 \
    libsqlite3-dev
```

### Python Dependencies
```bash
pip install -r requirements.txt
```

Key packages:
- psycopg2-binary (PostgreSQL)
- bcrypt (password hashing)
- PyJWT (tokens)
- Flask (web framework)
- Flask-CORS (cross-origin support)

## 5. Data Persistence Configuration

### For Production (Recommended)
Use PostgreSQL with persistent storage:

```bash
# Set environment variable
export DATABASE_URL="postgresql://user:password@host:5432/hiremebahamas"
```

Benefits:
- ✅ Enterprise-grade persistence
- ✅ Survives server restarts
- ✅ Handles millions of records
- ✅ ACID compliance
- ✅ Automatic backups (if configured)

### For Development
SQLite with persistent file:

```bash
# Database file: hiremebahamas.db
# Location: Same directory as final_backend_postgresql.py
# Permissions: 644
```

**Important**: 
- ✅ Ensure database file is NOT in `/tmp` or ephemeral storage
- ✅ Use persistent volume mounts for containers
- ✅ Regular backups recommended

## 6. Database Schema

### Posts Table
```sql
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Index for pagination performance
CREATE INDEX idx_posts_created_at ON posts(created_at DESC);
```

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    user_type VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    is_available_for_hire BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

## 7. Testing

### Test Token Persistence
```bash
# 1. Register and login
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Test123!","first_name":"Test","last_name":"User","user_type":"job_seeker","location":"Nassau"}'

# 2. Save the access_token from response

# 3. Wait (token valid for 365 days)

# 4. Use token to create post (should work)
curl -X POST http://localhost:8080/api/posts \
  -H "Authorization: ******" \
  -H "Content-Type: application/json" \
  -d '{"content":"Test post","image_url":""}'
```

### Test Post Persistence
```bash
# 1. Create posts
# 2. Restart server
# 3. Verify posts still exist
curl http://localhost:8080/api/posts
```

### Test Pagination
```bash
# Get first page
curl "http://localhost:8080/api/posts?page=1&per_page=10"

# Get second page
curl "http://localhost:8080/api/posts?page=2&per_page=10"
```

## 8. Troubleshooting

### Issue: Users can't sign in after inactivity
**Solution**: Token now expires after 365 days instead of 7 days

### Issue: Posts disappear after restart
**Solution**: 
1. Check database file exists and is not in /tmp
2. For production, use PostgreSQL with DATABASE_URL
3. Ensure persistent volume mounts

### Issue: Too many posts slow down loading
**Solution**: Use pagination:
- `/api/posts?page=1&per_page=20`
- Frontend should implement infinite scroll or page navigation

### Issue: Database file missing
**Solution**:
1. Check `.gitignore` - *.db files are excluded from git
2. Ensure database file is in persistent storage
3. Use PostgreSQL in production

## 9. Deployment Checklist

- [ ] Set `DATABASE_URL` to PostgreSQL connection string
- [ ] Set `TOKEN_EXPIRATION_DAYS=365` (or leave default)
- [ ] Configure persistent storage for database
- [ ] Enable database backups
- [ ] Set up monitoring for database size
- [ ] Test token persistence after deployment
- [ ] Test post creation and retrieval
- [ ] Verify pagination works with large datasets

## 10. Monitoring

### Check Token Expiration
```python
import jwt
token = "your_token_here"
payload = jwt.decode(token, verify=False)
print(f"Token expires: {payload['exp']}")
```

### Check Database Size
```sql
-- PostgreSQL
SELECT pg_size_pretty(pg_database_size('hiremebahamas'));

-- SQLite
-- Check file size: ls -lh hiremebahamas.db
```

### Check Post Count
```sql
SELECT COUNT(*) FROM posts;
SELECT COUNT(*) FROM users;
```

## Summary

✅ **Token Expiration**: 365 days (effectively never expires for normal usage)
✅ **Post Storage**: Permanent, never automatically deleted
✅ **Scalability**: Pagination supports millions of posts
✅ **Dependencies**: All system dependencies documented
✅ **Data Persistence**: Guaranteed with proper configuration

---

**Last Updated**: November 2025
**Version**: 2.0.0
