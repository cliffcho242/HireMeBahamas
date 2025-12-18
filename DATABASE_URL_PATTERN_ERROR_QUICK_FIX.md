# DATABASE_URL Pattern Error - Quick Fix Guide

## Problem
Error: **"Backend connection: The string did not match the expected pattern"**

## Quick Diagnosis

### 1. Check Your DATABASE_URL Format
Your DATABASE_URL should look like this:
```
postgresql://username:password@hostname:5432/database?sslmode=require
```

### 2. Common Issues

#### Missing Hostname
❌ Wrong:
```
postgresql://user:pass@:5432/database
```

✅ Correct:
```
postgresql://user:pass@hostname:5432/database
```

#### Invalid Scheme
❌ Wrong:
```
mysql://user:pass@hostname:5432/database
```

✅ Correct:
```
postgresql://user:pass@hostname:5432/database
```

#### Extra Whitespace
❌ Wrong:
```
  postgresql://user:pass@hostname:5432/database  
```

✅ Correct:
```
postgresql://user:pass@hostname:5432/database
```

## Quick Fix Steps

### Step 1: Check Environment Variable
```bash
# View current DATABASE_URL (masked for security)
echo $DATABASE_URL | sed 's/:.*@/:***@/'
```

### Step 2: Validate Format
Your URL must have:
- ✅ Scheme: `postgres://` or `postgresql://`
- ✅ Username: `username`
- ✅ Password: `password`
- ✅ Hostname: actual hostname or IP (not blank)
- ✅ Port: `5432` (or your custom port)
- ✅ Database: `database_name`

### Step 3: Test Connection
```bash
# Test if format is valid (without connecting)
python3 -c "
from urllib.parse import urlparse
url = 'postgresql://user:pass@host:5432/db'
parsed = urlparse(url)
assert parsed.scheme in ['postgres', 'postgresql']
assert parsed.hostname
print('✅ Format is valid!')
"
```

### Step 4: Update Environment Variable
```bash
# Update DATABASE_URL
export DATABASE_URL="postgresql://username:password@hostname:5432/database?sslmode=require"
```

## Error Messages Explained

### Before This Fix
```
Error: The string did not match the expected pattern
```
**Problem**: Cryptic, doesn't tell you what's wrong

### After This Fix
```
❌ DATABASE_URL configuration error: Invalid DATABASE_URL: missing hostname.
Format should be: postgresql://user:password@hostname:5432/database

Expected format: postgresql://username:password@hostname:5432/database?sslmode=require

Common issues:
  1. Missing hostname (check for patterns like '@:5432' or missing '@')
  2. Invalid characters in username or password
  3. Extra whitespace or newlines in the URL
  4. Missing required parts (username, host, or database name)
```
**Solution**: Clear explanation with troubleshooting steps

## Platform-Specific Examples

### Vercel Postgres (Neon)
```
postgresql+asyncpg://username:password@ep-xxxxx.region.neon.tech:5432/database?sslmode=require
```

### Render PostgreSQL
```
postgresql+asyncpg://postgres:password@containers-us-west-xxx.render.app:5432/render?sslmode=require
```

### Render PostgreSQL
```
postgresql+asyncpg://username:password@dpg-xxxxx.render.com:5432/database?sslmode=require
```

### Local Development
```
postgresql+asyncpg://postgres:password@localhost:5432/hiremebahamas?sslmode=require
```

## Testing Your Fix

### Test 1: Format Validation
```bash
python3 -c "
import re
url = 'YOUR_DATABASE_URL_HERE'
assert re.match(r'^(postgres|postgresql)://', url)
print('✅ Scheme is valid')
"
```

### Test 2: Hostname Check
```bash
python3 -c "
from urllib.parse import urlparse
url = 'YOUR_DATABASE_URL_HERE'
parsed = urlparse(url)
assert parsed.hostname
assert not parsed.netloc.startswith(':')
print(f'✅ Hostname is valid: {parsed.hostname}')
"
```

### Test 3: Full Validation
```bash
python3 /tmp/test_url_validation_standalone.py
```

## Still Getting Errors?

### Check Logs
```bash
# Backend logs
grep "DATABASE_URL" /var/log/app.log

# Check for validation errors
grep "pattern\|format\|invalid" /var/log/app.log
```

### Common Fixes

1. **Remove whitespace**
   ```bash
   export DATABASE_URL=$(echo $DATABASE_URL | xargs)
   ```

2. **Check for invisible characters**
   ```bash
   echo $DATABASE_URL | cat -A
   ```

3. **Verify environment variable is set**
   ```bash
   [ -z "$DATABASE_URL" ] && echo "❌ Not set" || echo "✅ Set"
   ```

4. **Test with a simple URL**
   ```bash
   export DATABASE_URL="postgresql://postgres:password@localhost:5432/test"
   ```

## Need Help?

### Documentation
- 📄 Full implementation: `IMPLEMENTATION_SUMMARY_DATABASE_URL_PATTERN_FIX.md`
- 🔒 Security analysis: `SECURITY_SUMMARY_DATABASE_URL_PATTERN_FIX.md`

### Contact Support
If you're still experiencing issues:
1. Check the backend logs for detailed error messages
2. Verify your DATABASE_URL follows the correct format
3. Ensure your hostname is reachable
4. Contact support with the error message and masked DATABASE_URL

---

**Quick Reference**
- ✅ Format: `postgresql://user:pass@host:5432/db`
- ✅ With SSL: `...?sslmode=require`
- ✅ With asyncpg: `postgresql+asyncpg://...`
- ❌ No whitespace
- ❌ No missing hostname
- ❌ No wrong scheme
