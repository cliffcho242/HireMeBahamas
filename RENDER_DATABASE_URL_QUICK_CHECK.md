# ✅ Render DATABASE_URL Quick Check

**30-Second Verification Checklist**

---

## Before You Deploy to Render

Go to **[Render Dashboard](https://dashboard.render.com)** → Your Web Service → **Environment**

Find `DATABASE_URL` and verify these **4 requirements**:

### ✔ 1. No quotes
```bash
# ❌ WRONG
DATABASE_URL="postgresql://..."

# ✅ CORRECT
DATABASE_URL=postgresql://...
```

### ✔ 2. No spaces
```bash
# ❌ WRONG
DATABASE_URL=postgresql://user:pass word@host...

# ✅ CORRECT
DATABASE_URL=postgresql://user:password@host...
```

### ✔ 3. Real domain (NOT "host")
```bash
# ❌ WRONG
DATABASE_URL=postgresql://USER:PASSWORD@host:5432/dbname?sslmode=require

# ✅ CORRECT
DATABASE_URL=postgresql://user:pass@ep-cool-sound-12345.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require
```

### ✔ 4. Ends with `?sslmode=require`
```bash
# ❌ WRONG
DATABASE_URL=postgresql://user:pass@ep-cool.neon.tech:5432/db

# ✅ CORRECT
DATABASE_URL=postgresql://user:pass@ep-cool.neon.tech:5432/db?sslmode=require
```

---

## Automated Verification

Run this command to validate your DATABASE_URL:

```bash
python scripts/verify_render_database_url.py "your-database-url-here"
```

---

## Need More Help?

📖 **Full guide**: [RENDER_DATABASE_URL_VERIFICATION.md](./RENDER_DATABASE_URL_VERIFICATION.md)

**Common issues**:
- Using placeholder "host" → [Fix here](./RENDER_DATABASE_URL_VERIFICATION.md#mistake-1-using-placeholder-values)
- Missing sslmode → [Fix here](./RENDER_DATABASE_URL_VERIFICATION.md#mistake-3-missing-sslmoderequire)
- Has quotes → [Fix here](./RENDER_DATABASE_URL_VERIFICATION.md#mistake-2-quotes-around-url)

---

**Last Updated**: December 2025  
**Priority**: CRITICAL ⚠️
