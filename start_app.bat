@echo off
echo Starting HireBahamas Application...

REM Kill any existing processes on our ports
echo Cleaning up existing processes...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8005') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do taskkill /f /pid %%a >nul 2>&1

REM Start backend server
echo Starting backend server...
start "Backend Server" /MIN cmd /c "cd /d %~dp0 && .\.venv\Scripts\Activate.ps1 && cd backend && python -m app.main"

REM Wait a moment for backend to start
timeout /t 5 /nobreak >nul

REM Start frontend server  
echo Starting frontend server...
start "Frontend Server" /MIN cmd /c "cd /d %~dp0\frontend && npm run dev"

echo.
echo HireBahamas Application is starting...
echo Backend will be available at: http://localhost:8005
echo Frontend will be available at: http://localhost:3000
echo.
echo Press any key to stop all servers...
pause >nul

REM Kill the servers when done
echo Stopping servers...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8005') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do taskkill /f /pid %%a >nul 2>&1

echo All servers stopped.
pause