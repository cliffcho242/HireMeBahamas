@echo off
REM Simple wrapper to run the Python force health check
REM This avoids batch file complexities and freezing issues

echo 🤖 HireBahamas Force Health Check
echo ==================================
echo Running automated backend management...
echo.

REM Run the Python script
python force_health_check.py

echo.
echo Press any key to exit...
pause >nul