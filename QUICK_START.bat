@echo off
::============================================================================
::  HireBahamas - Quick Start (No Admin Required)
::  Run this anytime to start your platform
::============================================================================

title HireBahamas - Starting Servers

echo.
echo ================================================
echo   HireBahamas - Quick Start
echo ================================================
echo.

:: Kill any existing servers
echo [1/4] Stopping old processes...
powershell -Command "Get-Process | Where-Object { $_.ProcessName -like '*python*' -or $_.ProcessName -like '*node*' } | Stop-Process -Force" 2>nul
timeout /t 2 /nobreak >nul

:: Start backend
echo [2/4] Starting backend server...
start /min python ULTIMATE_BACKEND_FIXED.py
timeout /t 5 /nobreak >nul

:: Start frontend with force launcher (handles startup issues)
echo [3/4] Starting frontend server (with force launcher)...
cd frontend
start /min powershell -ExecutionPolicy Bypass -File ".\force_frontend_dev.ps1" -PrimaryPort 3000 -CleanCache
cd ..
timeout /t 15 /nobreak >nul

:: Start monitoring
echo [4/4] Starting service monitor...
start /min powershell -ExecutionPolicy Bypass -File ".\service_monitor.ps1"
timeout /t 2 /nobreak >nul

:: Open browser
start http://localhost:3000

echo.
echo ================================================
echo   SUCCESS! HireBahamas is now running
echo ================================================
echo.
echo   Backend:  http://127.0.0.1:8008
echo   Frontend: http://localhost:3000
echo.
echo   Services are running with automatic monitoring
echo   The platform will restart services if they fail
echo   To stop: Close the minimized windows or run STOP_SERVERS.bat
echo.
pause
