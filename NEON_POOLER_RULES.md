# 🔒 NEON POOLER COMPATIBILITY RULES

## ⚠️  ABSOLUTE RULES FOR NEON POOLED CONNECTIONS

This document explains why certain database configuration patterns are **FORBIDDEN** when using Neon pooled connections (PgBouncer).

---

## 1. ❌ sslmode is FORBIDDEN

### Why?
Neon uses **PgBouncer** as a connection pooler. PgBouncer does NOT support the `sslmode` parameter in connection strings or startup options.

### What happens if you add sslmode?
- **Connection crashes** on startup
- **Boot loops** in Render/Railway
- **Warmup failures** that mask until production
- **Silent failures** that break health checks

### The Fix
```bash
# ❌ WRONG - Will crash with Neon pooler
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require

# ✅ CORRECT - Neon pooler compatible
DATABASE_URL=postgresql://user:pass@host:5432/db
```

### How SSL Actually Works with Neon
- SSL is **handled automatically** by the Neon proxy layer
- The proxy sits between your app and PgBouncer
- Your connection to the proxy IS encrypted
- You don't need to configure SSL manually
- Adding sslmode breaks the proxy layer

---

## 2. ❌ NO Startup DB Options

### Forbidden in connect_args:
```python
# ❌ WRONG
connect_args={
    "options": "-c statement_timeout=30s",  # NOT SUPPORTED
    "sslmode": "require",                   # NOT SUPPORTED
    "server_settings": {                     # NOT SUPPORTED
        "statement_timeout": "30000"
    }
}

# ✅ CORRECT - Only timeouts allowed
connect_args={
    "timeout": 5,              # Connection timeout (asyncpg)
    "command_timeout": 30,     # Query timeout (asyncpg)
    "connect_timeout": 5,      # Connection timeout (psycopg2)
}
```

### Why?
PgBouncer operates in **transaction pooling mode**. It does NOT preserve:
- Session-level settings
- Temporary tables
- Prepared statements
- Connection-specific parameters

---

## 3. ❌ NO Index Creation on Startup

### Why?
- **DDL operations** (CREATE INDEX, ALTER TABLE) can take seconds/minutes
- Neon pooler connections have **strict timeouts**
- Startup DDL causes **boot loops** and **health check failures**
- Multiple workers can cause **race conditions**

### The Fix
```bash
# ✅ Run indexes via migration (one-time)
alembic upgrade head

# ✅ Or via manual script (controlled execution)
python backend/create_database_indexes.py

# ❌ NEVER do this on app startup
create_indexes(engine)  # FORBIDDEN IN STARTUP CODE
```

---

## 4. ✅ App Must Boot Without Database

### Requirements
```python
# ✅ Health endpoint must respond WITHOUT database
@app.get("/health")
def health():
    return {"status": "ok"}  # NO database access

# ✅ Database warmup must be NON-FATAL
def warmup_db():
    try:
        test_connection()
    except Exception:
        logger.warning("DB warmup failed (non-critical)")
        return False  # Don't crash the app
```

---

## 5. 🔍 How to Detect Violations

### Check for sslmode leaks:
```bash
# Find all sslmode references
grep -r "sslmode" app/ api/ --include="*.py"

# Check database.py for ensure_sslmode calls
grep "ensure_sslmode" app/database.py api/database.py

# Check for startup DB options
grep -r "options.*-c\|server_settings" app/ api/ --include="*.py"
```

### Verification Tests
```bash
# Test database module loads without DB
python -c "from app.database import engine; print('OK')"

# Test app starts without DATABASE_URL
unset DATABASE_URL && python app/main.py
```

---

## 6. 🛡️ Guards Against Future Violations

### Code Review Checklist
- [ ] No `sslmode` in URL or connect_args
- [ ] No `ensure_sslmode()` calls
- [ ] No startup DB options (`-c`, `server_settings`)
- [ ] No DDL operations on startup
- [ ] Health endpoint doesn't touch DB
- [ ] DB warmup is non-fatal
- [ ] App boots without DATABASE_URL

### CI/CD Checks
```yaml
# Add to GitHub Actions
- name: Check for sslmode violations
  run: |
    if grep -r "sslmode=require" app/ api/ --include="*.py"; then
      echo "❌ Found sslmode violations"
      exit 1
    fi
```

---

## 7. 📚 Reference Documentation

### Neon Pooler Documentation
- [Neon Connection Pooling](https://neon.tech/docs/connect/connection-pooling)
- [PgBouncer Compatibility](https://www.pgbouncer.org/config.html)

### Why This Kept Coming Back
1. **Old guides** - Most tutorials are NOT Neon-safe
2. **Postgres muscle memory** - `sslmode=require` is common pattern
3. **Render retries** - Keeps triggering bad startup code
4. **Silent failures** - Masked until warmup or health checks

---

## 8. ✅ Final Guarantee

After implementing these rules:

❌ No sslmode crashes  
❌ No DB warmup failures  
❌ No index creation failures  
❌ No boot loops  
❌ No Neon incompatibilities  

Your app is now **immune to Neon pooler issues**.

---

## 9. 🔧 Emergency Fix Commands

If you deployed with sslmode and are experiencing crashes:

```bash
# 1. Remove sslmode from DATABASE_URL
# In Render/Railway dashboard, edit environment variable:
DATABASE_URL=postgresql://user:pass@host:5432/db  # Remove ?sslmode=require

# 2. Restart the service
# Render: Manual deploy
# Railway: git push

# 3. Verify health endpoint responds
curl https://your-app.com/health

# 4. Check logs for sslmode errors
# Should see: "✅ Database engine initialized (Neon pooled)"
# Should NOT see: "sslmode" errors or connection crashes
```

---

## 10. 📞 Support

If you encounter issues after applying these rules:

1. Check logs for specific error messages
2. Verify DATABASE_URL format (no sslmode)
3. Confirm health endpoint responds WITHOUT database
4. Check that startup code has no DDL operations
5. Verify warmup is non-fatal (logs warning, doesn't crash)

For Neon-specific issues, check [Neon Status](https://neon.tech/status).
