# Vercel Postgres Migration - Post-Migration Checklist

## Overview

This checklist helps you verify a successful migration from Railway/Render to Vercel Postgres. Use it to ensure all data and functionality work correctly before decommissioning the old database.

---

## ✅ Immediate Post-Migration (Day 0)

### Database Connection
- [ ] Health endpoint responds: `curl https://your-app.vercel.app/health`
- [ ] Ready endpoint shows database connected: `curl https://your-app.vercel.app/ready`
- [ ] No database connection errors in Vercel deployment logs
- [ ] Connection pool metrics are healthy (check `/api/health` detailed response)

### Data Integrity
- [ ] Row counts match between source and target databases
  ```bash
  python scripts/verify_vercel_postgres_migration.py
  ```
- [ ] All tables exist in Vercel Postgres
- [ ] All indexes are present
- [ ] All foreign key constraints are intact
- [ ] Sample queries return expected results

### User Authentication
- [ ] Existing users can log in successfully
- [ ] New user registration works
- [ ] Password reset functionality works
- [ ] Session persistence across page reloads
- [ ] JWT token generation and validation works

### Core Features
- [ ] User profiles load correctly
- [ ] Posts are visible in feed
- [ ] Job listings display properly
- [ ] Messages can be sent and received
- [ ] Notifications are generated and delivered
- [ ] Search functionality works
- [ ] Follow/unfollow system works

### Performance
- [ ] API response times are acceptable (<500ms)
- [ ] Database queries complete quickly (<100ms for simple queries)
- [ ] No timeout errors under normal load
- [ ] Connection pool has no exhaustion issues

---

## 📊 Monitoring (Days 1-7)

### Daily Checks

#### Day 1
- [ ] Monitor error rate in Vercel logs
- [ ] Check for database connection errors
- [ ] Verify SSL/TLS connection stability
- [ ] Review response time metrics
- [ ] Test all critical user flows

#### Day 2-3
- [ ] Compare traffic patterns to pre-migration baseline
- [ ] Check database storage usage in Vercel dashboard
- [ ] Monitor compute hours (for Hobby plan)
- [ ] Verify backup/snapshot creation (if configured)
- [ ] Test data write operations (create, update, delete)

#### Day 4-5
- [ ] Review database performance metrics
- [ ] Check for any connection pool issues
- [ ] Verify data consistency across all tables
- [ ] Test edge cases (large uploads, bulk operations)
- [ ] Monitor memory usage

#### Day 6-7
- [ ] Final verification of all features
- [ ] Review overall stability
- [ ] Check for any reported user issues
- [ ] Verify cost projections match expectations
- [ ] Prepare for old database decommission

### Metrics to Track

Create a spreadsheet or monitoring dashboard with these metrics:

| Metric | Pre-Migration | Day 1 | Day 3 | Day 7 | Status |
|--------|---------------|-------|-------|-------|--------|
| API Response Time (avg) | | | | | |
| Database Query Time (avg) | | | | | |
| Error Rate (%) | | | | | |
| Active Users | | | | | |
| Database Size (MB) | | | | | |
| Connection Pool Usage (%) | | | | | |
| Compute Hours (if Hobby) | | | | | |

---

## 🔍 Detailed Verification Tests

### Test 1: User Registration Flow
```bash
# Test new user registration
curl -X POST https://your-app.vercel.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123",
    "full_name": "Test User"
  }'

# Expected: 201 Created with user object
```

### Test 2: User Login Flow
```bash
# Test user login
curl -X POST https://your-app.vercel.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123"
  }'

# Expected: 200 OK with JWT token
```

### Test 3: Create Post
```bash
# Get auth token from login, then:
curl -X POST https://your-app.vercel.app/api/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "content": "Test post from Vercel Postgres!"
  }'

# Expected: 201 Created with post object
```

### Test 4: Data Retrieval
```bash
# Fetch user posts
curl -X GET https://your-app.vercel.app/api/posts \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Expected: 200 OK with array of posts
```

### Test 5: Database Performance
```bash
# Run performance verification
python scripts/verify_vercel_postgres_migration.py

# Should show all checks passing with response times
```

---

## 🔐 Security Verification

### SSL/TLS Configuration
- [ ] All connections use SSL (`sslmode=require` in DATABASE_URL)
- [ ] TLS 1.3 is enforced (check `DB_FORCE_TLS_1_3=true`)
- [ ] No SSL EOF errors in logs
- [ ] Certificate validation works correctly

### Environment Variables
- [ ] DATABASE_URL is set correctly in Vercel Dashboard
- [ ] No database credentials in source code
- [ ] All sensitive variables are in Vercel Secrets
- [ ] Environment variables are set for all environments (Production, Preview, Development)

### Access Control
- [ ] Only authorized services can access database
- [ ] Connection pooling limits are appropriate
- [ ] No exposed admin interfaces
- [ ] Backups are secured

---

## 📈 Performance Benchmarks

### Before Migration (Railway/Render Baseline)
Record these metrics for comparison:
- Average API response time: _________ ms
- Average database query time: _________ ms
- 95th percentile response time: _________ ms
- Daily active users: _________
- Peak concurrent connections: _________

### After Migration (Vercel Postgres)
Compare against baseline:
- Average API response time: _________ ms (Target: <200ms)
- Average database query time: _________ ms (Target: <100ms)
- 95th percentile response time: _________ ms (Target: <500ms)
- Daily active users: _________
- Peak concurrent connections: _________

### Performance Goals
- [ ] Response times improved or maintained
- [ ] No increase in error rate
- [ ] Database queries are faster
- [ ] Connection pool usage is stable
- [ ] No cold start delays

---

## 💰 Cost Verification

### Vercel Postgres Costs (Monitor)
- [ ] Check storage usage in Vercel Dashboard
  - Current: _________ MB / 512 MB (Hobby) or _________ GB
  - Projected monthly growth: _________ MB
- [ ] Monitor compute hours (Hobby plan only)
  - Current usage: _________ hours / 60 hours per month
  - Estimated monthly usage: _________ hours
- [ ] Verify no unexpected charges
- [ ] Compare to Railway/Render costs

### Cost Comparison
| Item | Railway/Render | Vercel Postgres | Savings |
|------|----------------|-----------------|---------|
| Database | $____/mo | $____/mo | $____/mo |
| Keep-alive Service | $____/mo | $0/mo | $____/mo |
| Total | $____/mo | $____/mo | $____/mo |

---

## 🚨 Rollback Procedure (If Needed)

If you encounter critical issues during the 7-day grace period:

### Quick Rollback Steps
1. **Update DATABASE_URL in Vercel**
   ```bash
   # In Vercel Dashboard: Settings → Environment Variables
   # Change DATABASE_URL back to Railway/Render URL
   DATABASE_URL=postgresql://user:pass@railway-or-render-host:5432/db
   ```

2. **Remove read-only from old database**
   ```bash
   DB_NAME=$(echo "$OLD_DATABASE_URL" | sed -E 's|.*://[^/]+/([^?]+).*|\1|')
   psql "$OLD_DATABASE_URL" -c "ALTER DATABASE \"$DB_NAME\" SET default_transaction_read_only = off;"
   ```

3. **Redeploy application**
   ```bash
   # Trigger redeploy in Vercel Dashboard or:
   git commit --allow-empty -m "Rollback to Railway/Render database"
   git push origin main
   ```

4. **Verify rollback**
   ```bash
   curl https://your-app.vercel.app/health
   # Should show healthy status
   ```

### When to Rollback
- [ ] Critical data loss detected
- [ ] Unacceptable performance degradation (>2x slower)
- [ ] Persistent connection errors (>5% error rate)
- [ ] Data corruption or integrity issues
- [ ] Security vulnerabilities discovered

### Rollback Decision Matrix
| Issue Severity | Response Time | Action |
|----------------|---------------|--------|
| **Critical** (data loss, security) | Immediate | Rollback immediately |
| **High** (50%+ feature broken) | 1-2 hours | Investigate, rollback if no quick fix |
| **Medium** (partial feature issues) | 4-8 hours | Investigate, fix or rollback |
| **Low** (minor issues) | 24 hours | Fix in place, no rollback |

---

## ✨ Final Decommission (After Day 7)

### Prerequisites
All items in this checklist must be ✅ before decommissioning:
- [ ] 7 days of stable operation on Vercel Postgres
- [ ] All monitoring metrics are within acceptable ranges
- [ ] No critical or high-severity issues reported
- [ ] Cost projections are as expected
- [ ] Backup/restore procedures tested and documented

### Decommission Old Database

#### Railway
1. [ ] Go to [Railway Dashboard](https://railway.app/dashboard)
2. [ ] Select your PostgreSQL service
3. [ ] Click **Settings**
4. [ ] Scroll to bottom and click **Delete Service**
5. [ ] Type service name to confirm deletion
6. [ ] Screenshot confirmation for records

#### Render
1. [ ] Go to [Render Dashboard](https://dashboard.render.com)
2. [ ] Select your PostgreSQL instance
3. [ ] Click **Settings**
4. [ ] Scroll to bottom and click **Delete Service**
5. [ ] Type "delete" to confirm deletion
6. [ ] Screenshot confirmation for records

### Clean Up
- [ ] Remove old DATABASE_URL references from documentation
- [ ] Update team documentation with new database information
- [ ] Archive old database connection strings securely
- [ ] Remove Railway/Render keep-alive services (if any)
- [ ] Cancel billing for old database services
- [ ] Update monitoring dashboards with new database source

### Documentation Updates
- [ ] Update README.md to reflect Vercel Postgres as primary
- [ ] Remove Railway/Render-specific instructions
- [ ] Update environment variable documentation
- [ ] Update deployment guides
- [ ] Archive old backup files

---

## 📝 Post-Migration Report

After completing the migration and decommissioning old database, document the results:

### Migration Summary
- **Migration Date**: _________________
- **Source Database**: Railway / Render (circle one)
- **Target Database**: Vercel Postgres
- **Database Size**: _________ MB/GB
- **Total Rows Migrated**: _________
- **Migration Duration**: _________ minutes
- **Downtime**: _________ minutes (if any)

### Performance Results
- **Response Time**: Improved / Same / Degraded (circle one)
  - Before: _________ ms
  - After: _________ ms
- **Error Rate**: Improved / Same / Increased (circle one)
  - Before: _________%
  - After: _________%

### Cost Savings
- **Previous Monthly Cost**: $_________
- **New Monthly Cost**: $_________
- **Monthly Savings**: $_________
- **Annual Savings**: $_________

### Issues Encountered
1. _________________________________________________
2. _________________________________________________
3. _________________________________________________

### Lessons Learned
1. _________________________________________________
2. _________________________________________________
3. _________________________________________________

### Recommendations for Future Migrations
1. _________________________________________________
2. _________________________________________________
3. _________________________________________________

---

## 🎉 Success Criteria

Your migration is successful when:

✅ All checklist items above are complete  
✅ 7+ days of stable operation  
✅ No data loss or corruption  
✅ Performance meets or exceeds baseline  
✅ Cost savings achieved  
✅ Old database successfully decommissioned  
✅ Team trained on new database setup  
✅ Documentation updated  

---

## 📞 Support Resources

If you encounter issues:

1. **Check logs**: Vercel Dashboard → Your Project → Logs
2. **Database metrics**: Vercel Dashboard → Storage → Your Database → Insights
3. **Run verification**: `python scripts/verify_vercel_postgres_migration.py`
4. **Consult docs**:
   - [VERCEL_POSTGRES_MIGRATION_GUIDE.md](./VERCEL_POSTGRES_MIGRATION_GUIDE.md)
   - [VERCEL_POSTGRES_QUICK_REFERENCE.md](./VERCEL_POSTGRES_QUICK_REFERENCE.md)
   - [Vercel Postgres Docs](https://vercel.com/docs/storage/vercel-postgres)
5. **Open GitHub issue** with:
   - Error messages
   - Steps to reproduce
   - Database metrics
   - Vercel logs

---

*Checklist Version: 1.0*  
*Last Updated: December 2025*

## Appendix: Quick Commands

```bash
# Test health
curl https://your-app.vercel.app/health

# Test database connection
psql "$DATABASE_URL" -c "SELECT 1"

# Check row counts
psql "$DATABASE_URL" -c "
  SELECT table_name, 
         (xpath('/row/c/text()', 
          query_to_xml(format('select count(*) as c from %I', table_name), false, true, '')))[1]::text::int AS count
  FROM information_schema.tables
  WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
  ORDER BY table_name;
"

# Run full verification
python scripts/verify_vercel_postgres_migration.py

# Monitor logs (real-time)
vercel logs --follow

# Check database size
psql "$DATABASE_URL" -c "
  SELECT pg_size_pretty(pg_database_size('verceldb'));
"
```
