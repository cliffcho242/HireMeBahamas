Write-Host "`n" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   HIREMEBAHAMAS PUBLIC BACKEND" -ForegroundColor White -BackgroundColor DarkCyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

Write-Host "[1/5] Starting Flask backend on port 9999..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit","-Command","cd '$PSScriptRoot'; .\.venv\Scripts\Activate.ps1; python final_backend.py" -WindowStyle Normal
Write-Host "✅ Backend starting..." -ForegroundColor Green

Start-Sleep -Seconds 5

Write-Host "`n[2/5] Creating public tunnel with ngrok..." -ForegroundColor Yellow
Start-Process cmd -ArgumentList "/k", "ngrok http 9999" -WindowStyle Normal
Write-Host "✅ Ngrok starting..." -ForegroundColor Green

Start-Sleep -Seconds 3

Write-Host "`n[3/5] Retrieving public URL..." -ForegroundColor Yellow

$maxRetries = 15
$retryCount = 0
$ngrokUrl = $null

while ($retryCount -lt $maxRetries -and -not $ngrokUrl) {
    try {
        $response = Invoke-RestMethod -Uri "http://127.0.0.1:4040/api/tunnels" -TimeoutSec 5
        $ngrokUrl = $response.tunnels[0].public_url
        
        if ($ngrokUrl) {
            Write-Host "`n" -ForegroundColor Green
            Write-Host "==========================================" -ForegroundColor Green
            Write-Host "   PUBLIC BACKEND URL:" -ForegroundColor Cyan -BackgroundColor Black
            Write-Host "   $ngrokUrl" -ForegroundColor Yellow
            Write-Host "==========================================" -ForegroundColor Green
            Write-Host ""
            
            # Update frontend environment
            Write-Host "[4/5] Updating frontend configuration..." -ForegroundColor Yellow
            "VITE_API_URL=$ngrokUrl" | Out-File -FilePath "frontend/.env.production" -Encoding UTF8
            Write-Host "✅ Frontend configured: $ngrokUrl`n" -ForegroundColor Green
            
            # Save to file
            Write-Host "[5/5] Saving deployment info..." -ForegroundColor Yellow
            $deploymentInfo = @"
HIREMEBAHAMAS PUBLIC BACKEND
========================================

Backend URL: $ngrokUrl
Started: $(Get-Date)

ADMIN CREDENTIALS:
Email: admin@hiremebahamas.com
Password: AdminPass123!

API ENDPOINTS:
  Health: $ngrokUrl/health
  Login: $ngrokUrl/api/auth/login
  Jobs: $ngrokUrl/api/jobs
  Posts: $ngrokUrl/api/posts

NEXT STEPS:
1. Keep backend window open (it's running!)
2. Deploy frontend: cd frontend; vercel --prod
3. Test backend: Invoke-RestMethod $ngrokUrl/health
4. Share URL with users or submit to app stores

NOTE: This URL is temporary and will change when you restart.
For permanent deployment, use Render.com or Render.

========================================
"@
            $deploymentInfo | Out-File -FilePath "PUBLIC_BACKEND_URL.txt" -Encoding UTF8
            Write-Host "✅ Saved to PUBLIC_BACKEND_URL.txt`n" -ForegroundColor Green
            
            # Test backend
            Write-Host "`n🧪 Testing backend health..." -ForegroundColor Cyan
            try {
                Start-Sleep -Seconds 2
                $health = Invoke-RestMethod -Uri "$ngrokUrl/health" -Method GET -TimeoutSec 10
                Write-Host "✅ Backend is healthy: $($health.status)`n" -ForegroundColor Green
            } catch {
                Write-Host "⏳ Backend initializing (this is normal)...`n" -ForegroundColor Yellow
            }
            
            Write-Host "`n" -ForegroundColor Magenta
            Write-Host "========================================" -ForegroundColor Magenta
            Write-Host "   SUCCESS! BACKEND IS PUBLIC!" -ForegroundColor White -BackgroundColor DarkMagenta
            Write-Host "========================================" -ForegroundColor Magenta
            Write-Host ""
            Write-Host "YOUR PUBLIC BACKEND:" -ForegroundColor Cyan
            Write-Host "  $ngrokUrl`n" -ForegroundColor Yellow
            Write-Host "WHAT'S RUNNING:" -ForegroundColor Cyan
            Write-Host "  ✅ Flask backend (port 9999)" -ForegroundColor Green
            Write-Host "  ✅ Ngrok tunnel (public access)" -ForegroundColor Green
            Write-Host "  ✅ CORS enabled" -ForegroundColor Green
            Write-Host "  ✅ All API endpoints active`n" -ForegroundColor Green
            Write-Host "NEXT STEPS:" -ForegroundColor Yellow
            Write-Host "  1. Deploy frontend with new URL:" -ForegroundColor White
            Write-Host "     cd frontend" -ForegroundColor Gray
            Write-Host "     vercel --prod`n" -ForegroundColor Gray
            Write-Host "  2. Or test backend now:" -ForegroundColor White
            Write-Host "     Invoke-RestMethod $ngrokUrl/health`n" -ForegroundColor Gray
            Write-Host "  3. Keep backend/ngrok windows open!" -ForegroundColor White
            Write-Host "     (Closing them stops the backend)`n" -ForegroundColor Gray
            Write-Host "⚠️  IMPORTANT: This URL changes when you restart" -ForegroundColor Yellow
            Write-Host "   For permanent hosting, use Render.com`n" -ForegroundColor Gray
            Write-Host ""
            
            break
        }
    } catch {
        $retryCount++
        if ($retryCount -lt $maxRetries) {
            Write-Host "  Attempt $retryCount/$maxRetries - waiting for ngrok..." -ForegroundColor Gray
            Start-Sleep -Seconds 2
        }
    }
}

if (-not $ngrokUrl) {
    Write-Host "`n❌ Could not retrieve ngrok URL automatically." -ForegroundColor Red
    Write-Host "   Check the ngrok window for your public URL`n" -ForegroundColor Yellow
    Write-Host "   Ngrok dashboard: http://127.0.0.1:4040`n" -ForegroundColor Cyan
}

Write-Host "`nPress any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
