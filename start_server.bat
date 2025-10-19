@echo off
echo Starting HireMeBahamas Backend Server...
echo.

:loop
echo [%date% %time%] Starting server...
C:\Users\Dell\OneDrive\Desktop\HireBahamas\.venv\Scripts\python.exe final_backend.py

echo [%date% %time%] Server crashed or was stopped. Restarting in 3 seconds...
timeout /t 3 /nobreak > nul
goto loop