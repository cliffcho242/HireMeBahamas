@echo off
echo ========================================
echo  HireMeBahamas Simple API Server
echo ========================================
echo Server will be available at: http://127.0.0.1:5000
echo Press Ctrl+C to stop the server completely.
echo.

:restart
echo [%date% %time%] Starting API server...
C:\Users\Dell\OneDrive\Desktop\HireBahamas\.venv\Scripts\python.exe simple_api_server.py

echo [%date% %time%] Server stopped. Restarting in 3 seconds...
timeout /t 3 /nobreak > nul
goto restart

echo.
echo Server stopped.
pause