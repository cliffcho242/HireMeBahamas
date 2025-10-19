@echo off
REM HireBahamas Force Health Check - Now uses Python for reliability
REM This script delegates to the Python version to avoid freezing issues

echo 🤖 HireBahamas Force Health Check (Batch Wrapper)
echo ==================================================
echo Using Python backend for maximum reliability...
echo.

REM Run the Python version
python force_health_check.py

echo.
echo Batch wrapper complete.
pause

goto :END

:RETRY_START
REM Retry starting backend
start "HireBahamas Backend" /MIN cmd /c "cd /d %~dp0 && python ULTIMATE_BACKEND_FIXED.py"
timeout /t 7 /nobreak >nul
goto :RUN_HEALTH_CHECK

:END
echo.
echo 🤖 AI System: Health check automation complete
echo Press any key to exit...
pause >nul