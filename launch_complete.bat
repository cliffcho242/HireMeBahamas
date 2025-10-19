@echo off
title HireBahamas Platform Auto-Fix Launcher

echo ============================================
echo HireBahamas Platform Auto-Fix Launcher
echo ============================================
echo.

echo Running automated connection fix system...
echo This will resolve localhost connection issues automatically.
echo.

REM Run the simple auto-fix system
cd /d "c:\Users\Dell\OneDrive\Desktop\HireBahamas"
"C:\Users\Dell\OneDrive\Desktop\HireBahamas\.venv\Scripts\python.exe" simple_autofix.py

echo.
echo ============================================
echo Platform diagnostic and launch complete!
echo ============================================
echo.
echo Access your platform at:
echo Frontend: http://localhost:3001
echo Backend: http://127.0.0.1:8008
echo Admin Login: admin@hirebahamas.com / AdminPass123!
echo.

pause