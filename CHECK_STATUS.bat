@echo off
::============================================================================
::  HireBahamas - Check Server Status
::============================================================================

title HireBahamas - Server Status

echo.
echo ================================================
echo   HireBahamas Server Status Check
echo ================================================
echo.

powershell -Command "$backend = try { (Invoke-WebRequest -Uri 'http://127.0.0.1:8008/health' -UseBasicParsing -TimeoutSec 3).StatusCode -eq 200 } catch { $false }; $frontend = try { (Invoke-WebRequest -Uri 'http://localhost:3000' -UseBasicParsing -TimeoutSec 3).StatusCode -eq 200 } catch { $false }; Write-Host 'Backend (Port 8008): ' -NoNewline; if ($backend) { Write-Host 'RUNNING' -ForegroundColor Green } else { Write-Host 'NOT RUNNING' -ForegroundColor Red }; Write-Host 'Frontend (Port 3000): ' -NoNewline; if ($frontend) { Write-Host 'RUNNING' -ForegroundColor Green } else { Write-Host 'NOT RUNNING' -ForegroundColor Red }"

echo.
pause
