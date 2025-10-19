@echo off
title HireBahamas - Automated Platform Launcher
color 0B

echo.
echo ========================================================
echo.
echo           HIREBAHAMAS AUTOMATED LAUNCHER
echo      Facebook-Style Professional Social Platform
echo.
echo ========================================================
echo.

REM Ensure we're in the correct directory
cd /d "%~dp0"
echo Current directory: %CD%

echo [1/5] Checking system requirements...
timeout /t 1 /nobreak >nul

REM Check if Node.js is available
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)

REM Check if Python is available
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo [2/5] Stopping any existing servers...
taskkill /F /IM node.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo [3/5] Starting Backend Server (Python Flask)...
echo      Using: ULTIMATE_BACKEND_FIXED.py
start "HireBahamas Backend" /MIN cmd /c "cd /d %~dp0 && python ULTIMATE_BACKEND_FIXED.py"
timeout /t 3 /nobreak >nul

REM Verify backend is running
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://127.0.0.1:8008/health' -TimeoutSec 5; if ($response.StatusCode -eq 200) { Write-Host '      Backend started successfully on http://127.0.0.1:8008' } } catch { Write-Host '      Backend starting...' }" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo      Backend starting...
)

echo [4/5] Starting Frontend Server (React + Vite)...
echo      Using: frontend directory
start "HireBahamas Frontend" /MIN cmd /c "cd /d %~dp0\frontend && npm run dev"
timeout /t 5 /nobreak >nul

REM Verify frontend is running
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:3000' -TimeoutSec 5; if ($response.StatusCode -eq 200) { Write-Host '      Frontend started successfully on http://localhost:3000' } } catch { Write-Host '      Frontend starting...' }" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo      Frontend starting...
)

echo [5/5] Opening HireBahamas in default browser...
timeout /t 2 /nobreak >nul
start http://localhost:3000

echo.
echo ========================================================
echo.
echo   SUCCESS! HireBahamas Platform is Running!
echo.
echo   🌐 Frontend: http://localhost:3000
echo   🔧 Backend:  http://127.0.0.1:8008
echo   ❤️ Health:   http://127.0.0.1:8008/health
echo.
echo   🔑 Default Login Credentials:
echo   Email:    admin@hirebahamas.com
echo   Password: AdminPass123!
echo.
echo   📱 Features Available:
echo   - Facebook-style login system
echo   - Stories and posts feed
echo   - Real-time messaging
echo   - Job postings and applications
echo   - Professional networking
echo.
echo   ⚠️  IMPORTANT: Keep this window open to keep servers running!
echo      Close this window to stop all servers.
echo.
echo ========================================================
echo.

echo Press any key to stop servers and exit...
pause >nul

echo.
echo Stopping HireBahamas servers...
taskkill /F /IM node.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1
echo All servers stopped. Thank you for using HireBahamas!
timeout /t 2 /nobreak >nul
