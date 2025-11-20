# 🚀 HireMeBahamas - One-Click Installation

## Quick Start (Choose Your Platform)

### 🐧 Linux / 🍎 macOS
```bash
./scripts/install_all_dependencies.sh
```

### 🪟 Windows
```cmd
scripts\install_all_dependencies.bat
```

### 🐳 Docker (All Platforms)
```bash
./scripts/docker_install_all.sh
```

---

## What Happens?

✅ **System Dependencies Installed**
- Python 3.12
- Node.js 20+
- PostgreSQL 15
- Redis
- Build tools

✅ **Python Packages Installed**
- Flask, Django, FastAPI frameworks
- PostgreSQL adapter (psycopg2)
- Redis client
- All packages from requirements.txt

✅ **Node.js Packages Installed**
- React, TypeScript, Vite
- All packages from frontend/package.json

✅ **Services Configured**
- PostgreSQL database: `hiremebahamas`
- Redis server started
- Environment files created

✅ **Installation Verified**
- All dependencies checked
- Services tested
- Report generated

---

## After Installation

### 1. Start Backend
```bash
cd backend
python app.py
```

### 2. Start Frontend
```bash
cd frontend
npm run dev
```

### 3. Access App
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## Common Issues?

### Run Verification
```bash
python scripts/verify_installation.py
```

### Check Logs
```bash
cat installation.log
```

### Re-install with Force
```bash
./scripts/install_all_dependencies.sh --force
```

---

## Need More Options?

### Dry Run (Preview)
```bash
./scripts/install_all_dependencies.sh --dry-run
```

### Skip System Packages
```bash
./scripts/install_all_dependencies.sh --skip-system
```

### Skip Services
```bash
./scripts/install_all_dependencies.sh --skip-services
```

### See All Options
```bash
./scripts/install_all_dependencies.sh --help
```

---

## Full Documentation

📖 **[INSTALLATION_COMPLETE.md](INSTALLATION_COMPLETE.md)** - Complete installation guide  
📖 **[scripts/README.md](scripts/README.md)** - Scripts documentation  
📖 **[README.md](README.md)** - Project overview  

---

## Support

🐛 **Issues**: https://github.com/cliffcho242/HireMeBahamas/issues  
💬 **Discussions**: https://github.com/cliffcho242/HireMeBahamas/discussions

---

**🎉 That's it! Your HireMeBahamas platform is ready to use!**

Built with ❤️ for the Bahamas 🇧🇸
