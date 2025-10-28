@echo off
echo.
echo ========================================
echo   HIREBAHAMAS ADMIN CONTROL PANEL
echo ========================================
echo.
echo Starting Admin Backend...
start "Admin Backend API" cmd /k "python admin_backend.py"

timeout /t 3 /nobreak >nul

echo Starting Admin Frontend...
start "Admin Frontend" cmd /k "cd admin-panel && npm run dev"

echo.
echo ========================================
echo   ADMIN PANEL STARTED
echo ========================================
echo.
echo Backend API: http://localhost:8000
echo Frontend UI: http://localhost:3001
echo.
echo Admin Login:
echo   Email: admin@hiremebahamas.com
echo   Password: Admin123456!
echo.
echo Main App (Users):
echo   Frontend: https://hiremebahamas.com
echo   Backend: https://hiremebahamas.onrender.com
echo.
echo ========================================
echo   Press any key to close this window
echo ========================================
pause >nul
