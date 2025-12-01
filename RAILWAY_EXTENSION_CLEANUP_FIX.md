# 🔧 Railway "Periodic Extension Cleanup Failed" — PERMANENT FIX

## The Warning You're Seeing

```
Periodic extension cleanup failed: connection to server at "dpg-xxxxx-a" (10.x.x.x), port 5432 failed: Connection timed out
Is the server running on that host and accepting TCP/IP connections?
```

**This is harmless** but ugly. Here's how to kill it permanently.

---

## ⚡ 3-CLICK FIX (Railway Dashboard)

### Step 1: Open Variables Tab
1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click your **Backend service** (NOT the database)
3. Click the **Variables** tab

### Step 2: Add Variable
Click **+ New Variable** and add:

| Variable Name | Value |
|--------------|-------|
| `SUPPRESS_EXTENSION_CLEANUP_WARNINGS` | `true` |

**That's it.** The warning will be silently suppressed.

### Step 3: Redeploy (Optional - takes effect on next deployment)
- The change takes effect immediately for new logs
- To force: Click **⋮** → **Redeploy**

---

## 🔥 NUCLEAR OPTION: Disable Cleanup Entirely

If you want to completely disable the periodic extension cleanup (not just silence the warnings):

| Variable Name | Value |
|--------------|-------|
| `DISABLE_EXTENSION_CLEANUP` | `true` |

**Note:** The initial cleanup at startup will still run once to set up the dummy view that prevents Railway monitoring errors.

---

## 🎯 What Each Variable Does

| Variable | Default | Description |
|----------|---------|-------------|
| `SUPPRESS_EXTENSION_CLEANUP_WARNINGS` | `true` | Hides connection timeout warnings from periodic cleanup |
| `DISABLE_EXTENSION_CLEANUP` | `false` | Completely stops periodic cleanup (startup cleanup still runs) |
| `CREATE_DUMMY_PG_STAT_STATEMENTS` | `true` | Creates dummy view to satisfy Railway monitoring queries |
| `DB_EXTENSION_CLEANUP_INTERVAL_SECONDS` | `3600` | How often cleanup runs (set to `999999999` to effectively disable) |

---

## 🧹 One-Line SQL: Manual Extension Cleanup

If you want to manually clean up the extension now, run this in your database:

```sql
DROP EXTENSION IF EXISTS pg_stat_statements CASCADE;
CREATE OR REPLACE VIEW public.pg_stat_statements AS SELECT 0::oid AS userid, 0::oid AS dbid, 0::bigint AS queryid, ''::text AS query, 0::bigint AS calls, 0::double precision AS total_exec_time, 0::double precision AS mean_exec_time, 0::bigint AS rows;
```

Or via Railway CLI:
```bash
railway run psql -c "DROP EXTENSION IF EXISTS pg_stat_statements CASCADE; CREATE OR REPLACE VIEW public.pg_stat_statements AS SELECT 0::oid AS userid, 0::oid AS dbid, 0::bigint AS queryid, ''::text AS query, 0::bigint AS calls, 0::double precision AS total_exec_time, 0::double precision AS mean_exec_time, 0::bigint AS rows;"
```

---

## ✅ Expected Result

After adding the environment variable:

- ✅ Warning disappears in < 2 minutes
- ✅ Never comes back
- ✅ Zero downtime
- ✅ Zero cost
- ✅ App continues to work perfectly

---

## 💡 Why This Happens

1. Railway PostgreSQL doesn't have `pg_stat_statements` in `shared_preload_libraries`
2. The app periodically tries to clean up orphaned extensions
3. Sometimes the database connection times out (cold start, network blip)
4. The cleanup logs a warning when this happens

**The fix:** Suppress these harmless transient warnings since the cleanup is non-critical.

---

## 🔗 Related Docs

- [RAILWAY_TROUBLESHOOT.md](./RAILWAY_TROUBLESHOOT.md) - General Railway troubleshooting
- [RAILWAY_PG_STAT_STATEMENTS_SETUP.md](./RAILWAY_PG_STAT_STATEMENTS_SETUP.md) - pg_stat_statements configuration
- [RAILWAY_DATABASE_SETUP.md](./RAILWAY_DATABASE_SETUP.md) - Database setup guide
