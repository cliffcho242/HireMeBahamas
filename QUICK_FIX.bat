@echo off
REM Quick Fix for HireBahamas Freezing Issues
REM Kills stuck processes and restarts services

echo ========================================
echo 🔧 HIREBAHAMAS QUICK FIX
echo ========================================
echo.

echo [1/4] Stopping stuck processes...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
taskkill /f /im npm.cmd >nul 2>&1
timeout /t 2 /nobreak > nul
echo ✅ Processes stopped

echo.
echo [2/4] Cleaning up ports...
REM Kill any processes using our ports
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8008') do taskkill /f /pid %%a >nul 2>&1
timeout /t 2 /nobreak > nul
echo ✅ Ports cleaned

echo.
echo [3/4] Restarting services...
echo Starting backend...
start "HireBahamas Backend" cmd /c "python ULTIMATE_BACKEND_FIXED.py"
timeout /t 3 /nobreak > nul

echo Starting frontend...
cd frontend
start "HireBahamas Frontend" cmd /c "npm run dev"
cd ..
timeout /t 5 /nobreak > nul

echo.
echo [4/4] Verifying services...
python check_services.py

echo.
echo ========================================
echo ✅ QUICK FIX COMPLETE!
echo ========================================
echo.
echo 🌐 Frontend: http://localhost:3000
echo 🔧 Backend:  http://127.0.0.1:8008
echo.
echo If issues persist, run: ULTIMATE_HIREME_AUTOMATION.bat
echo.
pause