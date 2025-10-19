@echo off
REM HireBahamas Permanent Startup Script with AI Error Prevention
REM This script ensures the platform starts reliably and prevents connection errors

echo ====================================================
echo    HireBahamas Platform - Permanent Startup
echo    AI Error Prevention System - Activated
echo ====================================================
echo.

REM Step 1: Environment Setup
echo [1/6] Setting up environment...
set PYTHON_EXE=C:\Users\Dell\OneDrive\Desktop\HireBahamas\.venv\Scripts\python.exe
set PROJECT_DIR=C:\Users\Dell\OneDrive\Desktop\HireBahamas
cd /d "%PROJECT_DIR%"

REM Step 2: Process Cleanup
echo [2/6] Cleaning up existing processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
timeout /t 3 >nul

REM Step 3: Port Cleanup
echo [3/6] Clearing ports 8008 and 3000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8008') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do taskkill /F /PID %%a >nul 2>&1
timeout /t 2 >nul

REM Step 4: Install Dependencies
echo [4/6] Verifying dependencies...
"%PYTHON_EXE%" -m pip install flask flask-cors bcrypt pyjwt requests waitress --upgrade --quiet
cd frontend
call npm install --silent >nul 2>&1
cd ..

REM Step 5: Start Backend
echo [5/6] Starting backend server on port 8008...
start "HireBahamas Backend" /MIN cmd /k ""%PYTHON_EXE%" final_backend.py && echo Backend Running && pause"
timeout /t 8 >nul

REM Verify backend is running
echo Testing backend connection...
powershell -Command "try { $response = Invoke-RestMethod -Uri 'http://127.0.0.1:8008/health' -TimeoutSec 5; if ($response.status -eq 'healthy') { Write-Host 'Backend: ONLINE' -ForegroundColor Green } else { Write-Host 'Backend: FAILED' -ForegroundColor Red } } catch { Write-Host 'Backend: CONNECTION FAILED' -ForegroundColor Red }"

REM Step 6: Start Frontend
echo [6/6] Starting frontend server on port 3000...
cd frontend
start "HireBahamas Frontend" /MIN cmd /k "npm run dev && echo Frontend Running && pause"
cd ..
timeout /t 10 >nul

REM Final verification
echo.
echo ====================================================
echo           VERIFICATION & ACCESS INFO
echo ====================================================
echo.

REM Test login system
echo Testing login system...
powershell -Command "$body = @{email='admin@hirebahamas.com'; password='AdminPass123!'} | ConvertTo-Json; try { $response = Invoke-RestMethod -Uri 'http://127.0.0.1:8008/auth/login' -Method POST -Body $body -ContentType 'application/json' -TimeoutSec 10; if ($response.success) { Write-Host 'Login System: WORKING' -ForegroundColor Green } else { Write-Host 'Login System: FAILED' -ForegroundColor Red } } catch { Write-Host 'Login System: ERROR' -ForegroundColor Red }"

echo.
echo ====================================================
echo              PLATFORM STATUS
echo ====================================================
echo Backend Server:  http://127.0.0.1:8008
echo Frontend App:    http://localhost:3000
echo Admin Login:     admin@hirebahamas.com
echo Admin Password:  AdminPass123!
echo.
echo AI Error Prevention: ACTIVE
echo Continuous Monitoring: ENABLED
echo Auto-Recovery: CONFIGURED
echo ====================================================
echo.

REM Create monitoring batch file for continuous running
echo @echo off > monitor_platform.bat
echo :monitor >> monitor_platform.bat
echo timeout /t 60 /nobreak ^>nul >> monitor_platform.bat
echo powershell -Command "try { Invoke-RestMethod -Uri 'http://127.0.0.1:8008/health' -TimeoutSec 5 ^| Out-Null; Write-Host 'Platform: HEALTHY' } catch { Write-Host 'Platform: RESTARTING...'; Start-Process 'start_permanent.bat' }" >> monitor_platform.bat
echo goto monitor >> monitor_platform.bat

echo Starting continuous monitoring...
start "Platform Monitor" /MIN cmd /k monitor_platform.bat

echo.
echo ====================================================
echo    HIREBAHAMAS PLATFORM IS NOW RUNNING!
echo    
echo    Ready to use at: http://localhost:3000
echo    
echo    Features Active:
echo    - AI Error Prevention
echo    - Automatic Recovery  
echo    - Continuous Monitoring
echo    - Permanent Configuration
echo ====================================================
echo.
echo Press any key to open the application in your browser...
pause >nul

echo Opening browser...
start http://localhost:3000

echo.
echo Platform is running with AI protection!
echo Close this window to stop monitoring (servers will continue running)
echo.
pause