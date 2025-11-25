@echo off
REM Start HireMeBahamas in Full Production Mode
REM Uses PostgreSQL, production builds, no hot-reload

echo.
echo 🚀 Starting HireMeBahamas in Full Production Mode
echo ==================================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed.
    echo.
    echo Please install Docker Desktop:
    echo https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)

REM Check if Docker daemon is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running.
    echo.
    echo Please start Docker Desktop and try again.
    echo.
    pause
    exit /b 1
)

REM Check if docker compose is available
docker compose version >nul 2>&1
if errorlevel 1 (
    echo ❌ docker compose is not available.
    echo.
    echo Please update Docker Desktop to get docker compose.
    echo.
    pause
    exit /b 1
)

REM Start PostgreSQL and Redis
echo 📦 Starting PostgreSQL and Redis...
docker-compose up -d postgres redis

REM Wait for PostgreSQL to be ready
echo ⏳ Waiting for PostgreSQL to be ready...
timeout /t 5 /nobreak >nul

REM Check if backend .env exists
if not exist backend\.env (
    echo ⚙️  Creating backend\.env from .env.example...
    copy backend\.env.example backend\.env
    echo ✅ backend\.env created. Please update with your configuration if needed.
)

REM Check if frontend .env exists
if not exist frontend\.env (
    echo ⚙️  Creating frontend\.env from .env.example...
    copy frontend\.env.example frontend\.env
    echo ✅ frontend\.env created.
)

REM Build frontend for production
echo 🏗️  Building frontend for production...
cd frontend
call npm install
call npm run build
cd ..

REM Start backend in production mode
echo 🖥️  Starting backend in production mode...

REM Load environment variables from .env file if it exists
if exist backend\.env (
    echo Loading environment variables from backend\.env...
    for /f "usebackq tokens=1,2 delims==" %%a in ("backend\.env") do (
        set "%%a=%%b"
    )
)

start "HireMeBahamas Backend" cmd /k "cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --no-reload --workers 2"

REM Wait for backend to start
echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Start frontend in production mode
echo 🌐 Starting frontend in production mode...
start "HireMeBahamas Frontend" cmd /k "cd frontend && npm run start"

echo.
echo ✅ HireMeBahamas is running in Full Production Mode!
echo ==================================================
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Database Admin: http://localhost:8081
echo.
echo Database: PostgreSQL (localhost:5432)
echo Mode: PRODUCTION
echo.
echo Press any key to view this information again...
pause >nul
