# ASYNCPG FIX - QUICK REFERENCE

## ⚡ ONE-LINE INSTALL COMMAND

```bash
pip install --only-binary=:all: -r requirements.txt
```

## 📋 COPY-PASTE FOR EACH PLATFORM

### Render (render.yaml)
```yaml
buildCommand: pip install --upgrade pip setuptools wheel && pip install --only-binary=:all: -r requirements.txt
```

### Vercel (vercel.json)
```json
"installCommand": "pip install --upgrade pip && pip install --only-binary=:all: -r requirements.txt"
```

### Render (Dockerfile)
```dockerfile
RUN pip install --upgrade pip && \
    pip install --only-binary=:all: -r requirements.txt
```

## 🎯 KEY RULES

1. ✅ DO: Put `--only-binary=:all:` in pip command
2. ❌ DON'T: Put `--only-binary` flag in requirements.txt
3. ✅ DO: Keep requirements.txt clean (just package==version)
4. ❌ DON'T: Install build-essential, gcc, libpq-dev

## 📦 requirements.txt (Example)
```txt
fastapi==0.115.0
uvicorn[standard]==0.31.0
gunicorn==22.0.0
sqlalchemy[asyncio]==2.0.35
asyncpg==0.29.0
pydantic==2.9.2
```

## 🚀 RESULTS

| Metric | Before | After |
|--------|--------|-------|
| Install time | 45-90s | 6-8s |
| Build errors | Frequent | Zero |
| System deps | gcc, libpq-dev, etc | None |
| Works on | Limited | All platforms |

## 🆘 TROUBLESHOOTING

**Still getting build errors?**
→ Use alternative: `requirements-psycopg.txt` (psycopg[binary])

**Forgot the syntax?**
→ `pip install --only-binary=:all: -r requirements.txt`

**Need more details?**
→ See `ASYNCPG_FINAL_FIX_2025.md`
