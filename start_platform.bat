@echo off
echo Starting HireBahamas Platform...
echo.

REM Kill any existing processes
echo Cleaning up existing processes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul

REM Start Backend Server (Flask with Waitress)
echo Starting Backend Server on port 8008...
cd /d %~dp0
start "Backend Server" cmd /k "C:\Users\Dell\OneDrive\Desktop\HireBahamas\.venv\Scripts\python.exe final_backend.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start Frontend Server
echo Starting Frontend Server on port 3000...
cd frontend
start "Frontend Server" npm run dev
cd..

echo.
echo ===================================
echo HireBahamas Platform Started!
echo ===================================
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8005
echo API Docs: http://localhost:8005/docs (if available)
echo ===================================
echo.
echo Press any key to stop all servers...
pause

REM Clean up on exit
echo Stopping servers...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM node.exe 2>nul
echo Servers stopped.