@echo off
echo ========================================
echo FORCED BACKEND STARTUP
echo ========================================

:loop
echo [%date% %time%] Starting backend...

REM Kill any existing Python processes
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM python3.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Clear port 8008
for /f "tokens=5" %%a in ('netstat -ano ^| find ":8008"') do (
    echo Killing process %%a using port 8008
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul

REM Start backend
echo Starting ULTIMATE_BACKEND_FIXED.py...
start /B python ULTIMATE_BACKEND_FIXED.py

REM Wait for startup
echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Test health endpoint
echo Testing health endpoint...
curl -s -o nul -w "%%{http_code}" http://127.0.0.1:8008/health > temp_health.txt 2>nul
set /p status=<temp_health.txt
del temp_health.txt 2>nul

if "%status%"=="200" (
    echo ✅ Backend is running successfully!
    echo Health endpoint responding: http://127.0.0.1:8008/health
    goto monitor
) else (
    echo ❌ Backend failed to start (Status: %status%)
    echo Retrying in 3 seconds...
    timeout /t 3 /nobreak >nul
    goto loop
)

:monitor
echo ========================================
echo BACKEND MONITORING ACTIVE
echo Press Ctrl+C to stop
echo ========================================

:monitor_loop
REM Test health every 10 seconds
curl -s -o nul -w "%%{http_code}" http://127.0.0.1:8008/health > temp_health.txt 2>nul
set /p status=<temp_health.txt
del temp_health.txt 2>nul

if "%status%"=="200" (
    echo [%date% %time%] ✅ Backend healthy
) else (
    echo [%date% %time%] ❌ Backend not responding, restarting...
    goto loop
)

timeout /t 10 /nobreak >nul
goto monitor_loop