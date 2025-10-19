@echo off
REM ============================================
REM HIREMEBAHAMAS MASTER NETWORK FIX
REM Complete Solution for Admin Login
REM ============================================

echo.
echo ============================================
echo STARTING HIREMEBAHAMAS COMPLETE SETUP
echo ============================================
echo.

cd /d "%~dp0"

REM Start Backend Server in new window
echo [1/3] Starting Backend Server...
start "HireMeBahamas Backend" cmd /k "cd /d %~dp0 && .venv\Scripts\activate && python -c "from final_backend import app; app.run(host='0.0.0.0', port=9999, debug=True, use_reloader=False)""

echo Waiting for backend to start...
timeout /t 10 /nobreak >nul

REM Test backend
echo [2/3] Testing Backend Connection...
curl -s http://127.0.0.1:9999/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Backend is running on http://127.0.0.1:9999
) else (
    echo [WARNING] Backend may still be starting...
)

REM Test admin login
echo [3/3] Testing Admin Login...
powershell -Command "$response = Invoke-RestMethod -Uri 'http://127.0.0.1:9999/api/auth/login' -Method POST -ContentType 'application/json' -Body '{\"email\":\"admin@hiremebahamas.com\",\"password\":\"AdminPass123!\"}' -ErrorAction SilentlyContinue; if ($response) { Write-Host '[SUCCESS] Admin login works!' -ForegroundColor Green; Write-Host 'Email:' $response.user.email -ForegroundColor Cyan; Write-Host 'Token:' $response.access_token.Substring(0,40)'...' -ForegroundColor Yellow } else { Write-Host '[INFO] Backend still starting, try logging in from the frontend' -ForegroundColor Yellow }"

echo.
echo ============================================
echo SETUP COMPLETE!
echo ============================================
echo.
echo Backend Server: http://127.0.0.1:9999
echo Frontend: http://localhost:3000
echo.
echo Admin Credentials:
echo   Email: admin@hiremebahamas.com
echo   Password: AdminPass123!
echo.
echo The backend server is running in a separate window.
echo Close that window to stop the backend.
echo ============================================
echo.
pause
