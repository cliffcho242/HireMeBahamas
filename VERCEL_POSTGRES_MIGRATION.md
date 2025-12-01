# ZERO-DOWNTIME MIGRATION: Railway Postgres → Vercel Postgres

## THE 7 COMMANDS

### COMMAND 1: Export from Railway
```bash
pg_dump "$RAILWAY_DATABASE_URL" \
  --no-owner \
  --no-acl \
  --format=custom \
  --compress=0 \
  --jobs=8 \
  --file=railway_backup_$(date +%Y%m%d_%H%M%S).dump
```

### COMMAND 2: Import to Vercel Postgres (Neon)
```bash
pg_restore \
  --no-owner \
  --no-acl \
  --jobs=8 \
  --dbname="$VERCEL_POSTGRES_URL" \
  railway_backup_*.dump
```

### COMMAND 3: Verify Row Counts
```bash
psql "$VERCEL_POSTGRES_URL" -c "
SELECT 'users' as table_name, COUNT(*) as row_count FROM users
UNION ALL SELECT 'posts', COUNT(*) FROM posts
UNION ALL SELECT 'jobs', COUNT(*) FROM jobs
UNION ALL SELECT 'messages', COUNT(*) FROM messages
UNION ALL SELECT 'notifications', COUNT(*) FROM notifications;
"
```

### COMMAND 4: Switch DATABASE_URL (Zero Downtime)
```bash
# In Vercel Dashboard: Settings → Environment Variables
# Update DATABASE_URL to Vercel Postgres connection string
# App auto-restarts with new database connection
```

### COMMAND 5: Set Railway to Read-Only (7-day backup)
```bash
# Extract database name from your RAILWAY_DATABASE_URL
# Example: postgresql://user:pass@host:5432/mydb → database name is "mydb"
DB_NAME=$(echo "$RAILWAY_DATABASE_URL" | sed -E 's|.*://[^/]+/([^?]+).*|\1|')
psql "$RAILWAY_DATABASE_URL" -c "ALTER DATABASE \"$DB_NAME\" SET default_transaction_read_only = on;"

# Or use the automated script:
./scripts/migrate_railway_to_vercel.sh --set-readonly
```

### COMMAND 6: Rollback (if needed)
```bash
# Revert DATABASE_URL in Vercel Dashboard to Railway URL
# Then remove read-only from Railway:
DB_NAME=$(echo "$RAILWAY_DATABASE_URL" | sed -E 's|.*://[^/]+/([^?]+).*|\1|')
psql "$RAILWAY_DATABASE_URL" -c "ALTER DATABASE \"$DB_NAME\" SET default_transaction_read_only = off;"
```

### COMMAND 7: Cleanup (after 7 days)
```bash
# Delete Railway Postgres service from Railway Dashboard
# Remove old RAILWAY_DATABASE_URL from all environments
```

---

## 8-STEP CHECKLIST

- [ ] **Step 1:** Create Vercel Postgres database (Vercel Dashboard → Storage → Postgres)
- [ ] **Step 2:** Copy VERCEL_POSTGRES_URL from Vercel Dashboard
- [ ] **Step 3:** Run Command 1 (Export from Railway)
- [ ] **Step 4:** Run Command 2 (Import to Vercel Postgres)
- [ ] **Step 5:** Run Command 3 (Verify row counts match)
- [ ] **Step 6:** Run Command 4 (Switch DATABASE_URL in Vercel)
- [ ] **Step 7:** Test app: login, create post, send message
- [ ] **Step 8:** Run Command 5 (Set Railway read-only for 7-day backup)

---

## FULL MIGRATION SCRIPT

Run `./scripts/migrate_railway_to_vercel.sh` for automated migration.

## VERIFICATION QUERIES

After migration, verify data integrity:

```sql
-- Check all tables exist
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

-- Check indexes
SELECT indexname FROM pg_indexes WHERE schemaname = 'public';

-- Check constraints
SELECT conname FROM pg_constraint;
```

## ENVIRONMENT VARIABLES

```bash
# Before migration (Railway)
DATABASE_URL=postgresql://user:pass@railway-host:5432/railway

# After migration (Vercel/Neon)
DATABASE_URL=postgresql://user:pass@ep-xyz.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require
```

## ESTIMATED TIME

| Rows | Time |
|------|------|
| 10k | < 1 min |
| 100k | 2-3 min |
| 500k | 10-15 min |
| 1M+ | 20-30 min |

## NOTES

- Zero downtime achieved via parallel `--jobs=8`
- Uses custom format for fastest restore
- Compression disabled for speed
- Railway kept read-only for 7 days as backup
- Rollback is instant (just change env var)
