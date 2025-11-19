# Clean Database Guide

This guide explains how to remove fake/sample/test data from the HireMeBahamas database and prevent it from being re-inserted.

## Overview

During development, several scripts may have inserted fake/sample/test data into the database for testing purposes. This data should be removed before deploying to production or when you want to work with real user data only.

## Quick Cleanup

To remove all fake/sample/test posts from the database:

```bash
# Preview what will be deleted (recommended first)
python remove_fake_posts.py --dry-run

# Actually delete the fake posts
python remove_fake_posts.py
```

## What Gets Deleted

The cleanup script (`remove_fake_posts.py`) removes:

1. **Posts from test users (IDs 1-5)**
   - These are the initial sample users created by setup scripts

2. **Posts from fake email addresses:**
   - john@hirebahamas.com
   - sarah@hirebahamas.com
   - mike@hirebahamas.com
   - lisa@hirebahamas.com

3. **Posts containing test/sample keywords:**
   - "test", "sample", "demo", "fake"
   - "Welcome to HireBahamas"
   - "Just launched our new job board"

## Scripts That Previously Created Fake Data

The following scripts have been updated to prevent accidental insertion of fake data:

### 1. `add_sample_posts.py`
- **Now requires:** `--dev` flag to run
- **Creates:** 8 sample posts with fake users
- **Usage:** `python add_sample_posts.py --dev` (development only)

### 2. `seed_data.py`
- **Now requires:** `--dev` flag to run
- **Creates:** 8 sample posts and users
- **Usage:** `python seed_data.py --dev` (development only)

### 3. `automated_posts_fix.py`
- **Changed:** No longer creates sample posts automatically
- **Now:** Only checks database structure

### 4. `create_posts_table.py`
- **Changed:** No longer inserts sample data
- **Now:** Only creates table structure

## Production Safety

To prevent fake data from being inserted in production:

### Environment Variables

Set one of these environment variables to enable production mode:

```bash
# Option 1: Set PRODUCTION flag
export PRODUCTION=true

# Option 2: Set FLASK_ENV
export FLASK_ENV=production

# Option 3: Set ENVIRONMENT
export ENVIRONMENT=production

# Option 4: Use remote PostgreSQL (automatically detected)
export DATABASE_URL=postgresql://...
```

### Development Flag

All sample data scripts now require the `--dev` flag:

```bash
# This will FAIL in production even with --dev flag:
python add_sample_posts.py --dev

# This will FAIL without --dev flag:
python add_sample_posts.py  # ❌ Error: --dev flag required
```

## Verification

After cleanup, verify the database state:

```bash
# Check posts count
python -c "
import sqlite3
conn = sqlite3.connect('hiremebahamas.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM posts')
print(f'Total posts: {cursor.fetchone()[0]}')
cursor.execute('SELECT COUNT(DISTINCT user_id) FROM posts')
print(f'Unique users with posts: {cursor.fetchone()[0]}')
conn.close()
"
```

## Best Practices

1. **Run cleanup before production deployment:**
   ```bash
   python remove_fake_posts.py
   ```

2. **Set production environment variables:**
   ```bash
   export PRODUCTION=true
   ```

3. **Never use --dev flag in production scripts**

4. **Regular cleanup during development:**
   ```bash
   # Clean database
   python remove_fake_posts.py
   
   # Add fresh sample data if needed
   python add_sample_posts.py --dev
   ```

5. **Verify environment before operations:**
   ```bash
   python -c "from production_utils import print_environment_info; print_environment_info()"
   ```

## Troubleshooting

### Issue: Script still inserts sample data

**Solution:** 
- Check environment variables: `python -c "from production_utils import print_environment_info; print_environment_info()"`
- Ensure you're not using the `--dev` flag
- Verify `PRODUCTION=true` is set

### Issue: Cannot remove posts

**Solution:**
- Check database permissions
- Verify database file exists: `ls -la hiremebahamas.db`
- Check if using PostgreSQL: Set `DATABASE_URL` environment variable

### Issue: Script says "cannot run in production"

**Solution:**
- This is expected behavior - sample data scripts are blocked in production
- If you really need sample data, unset production environment variables
- Only use sample data in development environments

## Database Migration to Production

When migrating to production:

1. **Clean the database:**
   ```bash
   python remove_fake_posts.py
   ```

2. **Verify cleanup:**
   ```bash
   python remove_fake_posts.py --dry-run
   ```

3. **Set production mode:**
   ```bash
   export PRODUCTION=true
   export DATABASE_URL=postgresql://your-production-db
   ```

4. **Deploy application**

5. **Never run sample data scripts on production**

## Support

For issues or questions:
- Review script output carefully
- Check environment variables
- Ensure you're using the correct database
- Verify you have the latest version of the scripts

## Related Files

- `remove_fake_posts.py` - Main cleanup script
- `production_utils.py` - Production detection utilities
- `add_sample_posts.py` - Sample post creation (dev only)
- `seed_data.py` - Database seeding (dev only)
- `automated_posts_fix.py` - Posts system checker
- `create_posts_table.py` - Table creation
