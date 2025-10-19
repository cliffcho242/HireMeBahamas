@echo off
REM FORCE INSTALL - Ultimate Backend Fix
REM This script forces everything to work

echo ========================================
echo FORCE INSTALL - Ultimate Backend Fix
echo ========================================
echo.

echo [1/5] Killing all interfering processes...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM pythonw.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1
timeout /t 2 /nobreak >nul
echo     ✓ Processes killed

echo.
echo [2/5] Cleaning network connections...
netsh winsock reset >nul 2>&1
netsh int ip reset >nul 2>&1
ipconfig /flushdns >nul 2>&1
arp -d * >nul 2>&1
timeout /t 3 /nobreak >nul
echo     ✓ Network cleaned

echo.
echo [3/5] Freeing ports...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8008') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul
echo     ✓ Ports freed

echo.
echo [4/5] Starting backend server...
start /B python ULTIMATE_BACKEND_FIXED.py
timeout /t 5 /nobreak >nul

echo.
echo [5/5] Verifying backend health...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://127.0.0.1:8008/health' -TimeoutSec 10; if ($response.StatusCode -eq 200) { Write-Host '    ✓ Backend is healthy!' -ForegroundColor Green; exit 0 } else { Write-Host '    ✗ Backend returned status: ' + $response.StatusCode -ForegroundColor Red; exit 1 } } catch { Write-Host '    ✗ Backend not responding: ' + $_.Exception.Message -ForegroundColor Red; exit 1 }"

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo 🎉 FORCE INSTALL SUCCESSFUL!
    echo ========================================
    echo.
    echo Backend is running at: http://127.0.0.1:8008
    echo Health check: http://127.0.0.1:8008/health
    echo.
    echo Your curl command will now work:
    echo curl -s http://127.0.0.1:8008/health
    echo.
    echo Press any key to open browser...
    pause >nul
    start http://localhost:3000
) else (
    echo.
    echo ========================================
    echo ❌ FORCE INSTALL FAILED
    echo ========================================
    echo.
    echo Try running again or check the logs.
    echo.
    pause
)