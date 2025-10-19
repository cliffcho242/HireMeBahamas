@echo off
title HireMeBahamas - Public Backend Launcher
color 0B

echo.
echo ========================================
echo    HIREMEBAHAMAS PUBLIC BACKEND
echo ========================================
echo.
echo This will:
echo   1. Start your Flask backend on port 9999
echo   2. Create a public URL using ngrok
echo   3. Update frontend configuration
echo   4. Open test page
echo.
echo Press any key to start...
pause > nul

cd /d "%~dp0"

:: Activate virtual environment
echo.
echo [1/4] Activating Python environment...
call .venv\Scripts\activate.bat

:: Start backend in new window
echo [2/4] Starting Flask backend on port 9999...
start "HireMeBahamas Backend" /MIN cmd /c ".venv\Scripts\python.exe final_backend.py"

:: Wait for backend to start
timeout /t 5 /nobreak > nul

:: Start ngrok in new window and capture URL
echo [3/4] Creating public URL with ngrok...
start "Ngrok Tunnel" cmd /k "ngrok http 9999"

:: Wait for ngrok to start
timeout /t 3 /nobreak > nul

echo [4/4] Getting public URL...
powershell -Command "$maxRetries=10; $retryCount=0; $ngrokUrl=$null; while ($retryCount -lt $maxRetries -and -not $ngrokUrl) { try { $response = Invoke-RestMethod -Uri 'http://127.0.0.1:4040/api/tunnels' -TimeoutSec 5; $ngrokUrl = $response.tunnels[0].public_url; if ($ngrokUrl) { Write-Host \"`n`n===========================================\" -ForegroundColor Green; Write-Host \"   YOUR PUBLIC BACKEND URL:\" -ForegroundColor Cyan -BackgroundColor Black; Write-Host \"   $ngrokUrl\" -ForegroundColor Yellow; Write-Host \"===========================================`n\" -ForegroundColor Green; \"VITE_API_URL=$ngrokUrl\" | Out-File -FilePath 'frontend/.env.production' -Encoding UTF8; Write-Host \"Frontend configured to use: $ngrokUrl`n\" -ForegroundColor Green; Write-Host \"DEPLOYMENT INFO:\" -ForegroundColor Cyan; Write-Host \"  Backend: $ngrokUrl\" -ForegroundColor White; Write-Host \"  Admin: admin@hiremebahamas.com / AdminPass123!`n\" -ForegroundColor White; \"Backend URL: $ngrokUrl`nAdmin: admin@hiremebahamas.com`nPassword: AdminPass123!`nStarted: $(Get-Date)\" | Out-File -FilePath 'PUBLIC_BACKEND_URL.txt' -Encoding UTF8; Write-Host \"URL saved to PUBLIC_BACKEND_URL.txt`n\" -ForegroundColor Gray; Write-Host \"NEXT STEPS:\" -ForegroundColor Yellow; Write-Host \"  1. Keep this window open (backend is running)\" -ForegroundColor White; Write-Host \"  2. Deploy frontend: cd frontend; vercel --prod\" -ForegroundColor White; Write-Host \"  3. Test at: $ngrokUrl/health`n\" -ForegroundColor White; break } } catch { $retryCount++; Start-Sleep -Seconds 2 } } if (-not $ngrokUrl) { Write-Host \"Could not get ngrok URL. Check ngrok window.\" -ForegroundColor Red }"

echo.
echo ========================================
echo    BACKEND IS NOW PUBLIC!
echo ========================================
echo.
echo Check the output above for your public URL
echo Keep this window open to keep backend running
echo.
pause
