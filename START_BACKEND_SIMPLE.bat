@echo off
REM Simple Backend Launcher - No fancy characters
echo ============================================
echo Starting HireMeBahamas Backend Server
echo ============================================
echo.

cd /d "%~dp0"

echo [1/2] Activating Python environment...
call .venv\Scripts\activate.bat

echo [2/2] Starting Waitress server on port 9999...
echo.
echo Backend will be available at: http://127.0.0.1:9999
echo.
echo Press Ctrl+C to stop the server
echo.

python -m waitress --host=127.0.0.1 --port=9999 --threads=6 final_backend:app

pause
