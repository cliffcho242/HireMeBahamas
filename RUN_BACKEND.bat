@echo off
TITLE HireMeBahamas Backend Server
cd /d "%~dp0"
call .venv\Scripts\activate.bat
echo Starting backend server...
python run_backend.py
pause
