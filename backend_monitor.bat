@echo off
REM HireBahamas Backend Auto-Start and Health Monitor
REM This script automatically starts the backend if needed and monitors health

title HireBahamas Backend Monitor
color 0A

echo.
echo ========================================================
echo.
echo        HIREBAHAMAS BACKEND AUTO-MONITOR
echo      Automated Health Check & Recovery
echo.
echo ========================================================
echo.

REM Get the script directory
set "SCRIPT_DIR=%~dp0"

:CHECK_BACKEND
echo [%DATE% %TIME%] Checking backend status...

REM Test backend health
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://127.0.0.1:8008/health' -TimeoutSec 5; Write-Host 'Backend Status: RUNNING (200)'; exit 0 } catch { Write-Host 'Backend Status: NOT RUNNING'; exit 1 }" >nul 2>&1

if %ERRORLEVEL% EQU 0 (
    echo ✅ Backend is healthy and running
    goto :HEALTH_CHECK_LOOP
) else (
    echo ❌ Backend not running - Starting automatically...
    goto :START_BACKEND
)

:START_BACKEND
echo Starting HireBahamas backend server...

REM Kill any existing Python processes that might be conflicting
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Start the backend
start "HireBahamas Backend" /MIN cmd /c "cd /d %SCRIPT_DIR% && python ULTIMATE_BACKEND_FIXED.py"

echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Verify it started
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://127.0.0.1:8008/health' -TimeoutSec 5; Write-Host '✅ Backend started successfully!'; exit 0 } catch { Write-Host '❌ Backend failed to start'; exit 1 }" >nul 2>&1

if %ERRORLEVEL% EQU 0 (
    echo Backend is now running and healthy!
    goto :HEALTH_CHECK_LOOP
) else (
    echo Failed to start backend. Retrying in 10 seconds...
    timeout /t 10 /nobreak >nul
    goto :START_BACKEND
)

:HEALTH_CHECK_LOOP
echo.
echo ========================================================
echo.
echo   BACKEND MONITORING ACTIVE
echo   Health checks every 30 seconds
echo   Press Ctrl+C to stop monitoring
echo.
echo ========================================================
echo.

:MONITOR_LOOP
echo [%DATE% %TIME%] Running health check...

REM Run the exact command the user requested
python -c "import requests; r=requests.get('http://127.0.0.1:8008/health'); print('Backend:', r.status_code)"

REM Additional status info
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://127.0.0.1:8008/health' -TimeoutSec 5; $data = $response.Content | ConvertFrom-Json; Write-Host ('Service: ' + $data.service); Write-Host ('Status: ' + $data.status) } catch { Write-Host 'Health check failed' }" 2>nul

echo Waiting 30 seconds before next check...
echo Press Ctrl+C to stop monitoring
timeout /t 30 /nobreak >nul
goto :MONITOR_LOOP

echo.
echo Backend monitoring stopped.
pause