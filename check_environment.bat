@echo off
REM Check if system is ready for HireMeBahamas Production Mode

echo.
echo 🔍 HireMeBahamas Environment Check
echo ====================================
echo.

set ERRORS=0

REM Check Docker
echo|set /p="Checking Docker installation... "
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Not installed
    echo    ^→ Install Docker Desktop: https://www.docker.com/products/docker-desktop
    set /a ERRORS+=1
) else (
    echo ✅ Installed
)

REM Check docker compose
echo|set /p="Checking docker compose... "
docker compose version >nul 2>&1
if errorlevel 1 (
    echo ❌ Not available
    echo    ^→ Update Docker Desktop or see DOCKER_SETUP.md
    set /a ERRORS+=1
) else (
    echo ✅ Available
)

REM Check Docker daemon
echo|set /p="Checking Docker daemon... "
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Not running
    echo    ^→ Start Docker Desktop
    set /a ERRORS+=1
) else (
    echo ✅ Running
)

REM Check Node.js
echo|set /p="Checking Node.js... "
node --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Not installed ^(required for frontend^)
    echo    ^→ Install from: https://nodejs.org/
    set /a ERRORS+=1
) else (
    echo ✅ Installed
)

REM Check npm
echo|set /p="Checking npm... "
npm --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Not installed ^(included with Node.js^)
    set /a ERRORS+=1
) else (
    echo ✅ Installed
)

REM Check Python
echo|set /p="Checking Python... "
python --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Not installed ^(required for backend^)
    echo    ^→ Install from: https://www.python.org/
    set /a ERRORS+=1
) else (
    echo ✅ Installed
)

REM Check pip
echo|set /p="Checking pip... "
pip --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Not installed ^(included with Python^)
    set /a ERRORS+=1
) else (
    echo ✅ Installed
)

echo.
echo ====================================

if %ERRORS%==0 (
    echo ✅ All checks passed! You're ready to run production mode.
    echo.
    echo Next steps:
    echo   1. start_production.bat
    echo   2. Open http://localhost:3000
    exit /b 0
) else (
    echo ❌ Found %ERRORS% issue^(s^). Please fix them before continuing.
    echo.
    echo For help:
    echo   • Docker: See DOCKER_SETUP.md
    echo   • Full guide: See PRODUCTION_MODE_GUIDE.md
    pause
    exit /b 1
)
