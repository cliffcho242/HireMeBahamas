@echo off
echo ==========================================
echo   HireBahamas Facebook-Style Platform
echo ==========================================
echo.

echo Starting Backend Server...
start "Backend" cmd /k "cd /d C:\Users\Dell\OneDrive\Desktop\HireBahamas && C:/Users/Dell/OneDrive/Desktop/HireBahamas/.venv/Scripts/python.exe clean_backend.py"

echo Waiting for backend to initialize...
timeout /t 3 /nobreak > nul

echo Starting Frontend (Facebook-style)...
start "Frontend" cmd /k "cd /d C:\Users\Dell\OneDrive\Desktop\HireBahamas\frontend && npm run dev"

echo.
echo ==========================================
echo   Access your platform at:
echo   http://localhost:3000 (or next available port)
echo.
echo   Default Login:
echo   Email: admin@hirebahamas.com
echo   Password: admin123
echo ==========================================
echo.
echo Press any key to exit...
pause > nul