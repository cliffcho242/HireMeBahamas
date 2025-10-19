@echo off
echo ========================================
echo  HireMeBahamas Backend Server Launcher
echo ========================================
echo.
echo This will start the backend server and keep it running.
echo The server will be available at: http://127.0.0.1:5000
echo.
echo Press Ctrl+C to stop the server completely.
echo.

:restart
echo [%date% %time%] Starting server...
C:\Users\Dell\OneDrive\Desktop\HireBahamas\.venv\Scripts\python.exe final_backend.py

echo [%date% %time%] Server stopped. Restarting in 3 seconds...
timeout /t 3 /nobreak > nul
goto restart

echo.
echo Server stopped.
pause