@echo off
echo.
echo ========================================
echo HireMeBahamas - Quick Test
echo ========================================
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0test_job_posting.ps1"

echo.
pause
