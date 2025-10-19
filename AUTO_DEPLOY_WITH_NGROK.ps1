# Automated Ngrok URL Fetcher and Deployment Automator
Write-Host "`n🤖 AUTOMATED DEPLOYMENT IN PROGRESS..." -ForegroundColor Cyan -BackgroundColor Black
Write-Host ""

# Step 1: Fetch ngrok URL
Write-Host "[1/5] Fetching ngrok URL..." -ForegroundColor Yellow
$maxRetries = 20
$retryCount = 0
$ngrokUrl = $null

while ($retryCount -lt $maxRetries -and -not $ngrokUrl) {
    try {
        $response = Invoke-RestMethod -Uri "http://127.0.0.1:4040/api/tunnels" -TimeoutSec 5 -ErrorAction Stop
        if ($response.tunnels -and $response.tunnels.Count -gt 0) {
            $ngrokUrl = $response.tunnels[0].public_url
            if ($ngrokUrl) {
                Write-Host "✅ Found ngrok URL: $ngrokUrl`n" -ForegroundColor Green
                break
            }
        }
    } catch {
        $retryCount++
        if ($retryCount -eq 1) {
            Write-Host "⏳ Waiting for ngrok to start..." -ForegroundColor Gray
        } elseif ($retryCount % 5 -eq 0) {
            Write-Host "  Still waiting... ($retryCount/$maxRetries)" -ForegroundColor Gray
        }
        Start-Sleep -Seconds 2
    }
}

if (-not $ngrokUrl) {
    Write-Host "`n❌ Could not auto-detect ngrok URL" -ForegroundColor Red
    Write-Host "Please check ngrok window or visit: http://127.0.0.1:4040" -ForegroundColor Yellow
    Write-Host "`nManually paste your ngrok URL here to continue.`n" -ForegroundColor Cyan
    exit 1
}

# Step 2: Test backend
Write-Host "[2/5] Testing backend connection..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$ngrokUrl/health" -Method GET -TimeoutSec 10
    Write-Host "✅ Backend is healthy: $($health.status)`n" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Backend responding slowly (this is normal)`n" -ForegroundColor Yellow
}

# Step 3: Update frontend configuration
Write-Host "[3/5] Updating frontend configuration..." -ForegroundColor Yellow
"VITE_API_URL=$ngrokUrl" | Out-File -FilePath "frontend/.env.production" -Encoding UTF8
Write-Host "✅ Frontend configured with: $ngrokUrl`n" -ForegroundColor Green

# Step 4: Save deployment info
Write-Host "[4/5] Saving deployment info..." -ForegroundColor Yellow
$deploymentInfo = @"
HIREMEBAHAMAS - DEPLOYMENT COMPLETE
========================================

Backend URL: $ngrokUrl
Frontend: Deploying to Vercel next...
Started: $(Get-Date)

ADMIN CREDENTIALS:
Email: admin@hiremebahamas.com
Password: AdminPass123!

API ENDPOINTS:
  Health: $ngrokUrl/health
  Login: $ngrokUrl/api/auth/login
  Register: $ngrokUrl/api/auth/register
  Jobs: $ngrokUrl/api/jobs
  Posts: $ngrokUrl/api/posts

IMPORTANT:
- Keep backend and ngrok windows open
- URL changes when you restart ngrok
- For permanent hosting, use Render.com

========================================
"@
$deploymentInfo | Out-File -FilePath "PUBLIC_BACKEND_URL.txt" -Encoding UTF8
Write-Host "✅ Saved to PUBLIC_BACKEND_URL.txt`n" -ForegroundColor Green

# Step 5: Deploy frontend
Write-Host "[5/5] Deploying frontend to Vercel..." -ForegroundColor Yellow
Write-Host ""

Set-Location frontend

try {
    $deployOutput = vercel --prod --yes 2>&1
    $frontendUrl = $deployOutput | Select-String -Pattern "https://.*\.vercel\.app" | Select-Object -Last 1 | ForEach-Object { $_.Matches.Value }
    
    if ($frontendUrl) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "   🎉 DEPLOYMENT COMPLETE!" -ForegroundColor White -BackgroundColor DarkGreen
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "YOUR LIVE URLS:" -ForegroundColor Cyan -BackgroundColor Black
        Write-Host ""
        Write-Host "  Frontend: $frontendUrl" -ForegroundColor Green
        Write-Host "  Backend:  $ngrokUrl" -ForegroundColor Green
        Write-Host ""
        Write-Host "ADMIN LOGIN:" -ForegroundColor Yellow
        Write-Host "  Email: admin@hiremebahamas.com" -ForegroundColor White
        Write-Host "  Password: AdminPass123!" -ForegroundColor White
        Write-Host ""
        Write-Host "TESTING:" -ForegroundColor Yellow
        Write-Host "  1. Open: $frontendUrl" -ForegroundColor Cyan
        Write-Host "  2. Try to sign in with admin credentials" -ForegroundColor White
        Write-Host "  3. Create jobs, posts, etc." -ForegroundColor White
        Write-Host ""
        Write-Host "APP STORE SUBMISSION:" -ForegroundColor Magenta
        Write-Host "  ✅ Website URL: $frontendUrl" -ForegroundColor Green
        Write-Host "  ✅ Privacy Policy: $frontendUrl/privacy-policy.html" -ForegroundColor Green
        Write-Host "  ✅ Terms of Service: $frontendUrl/terms-of-service.html" -ForegroundColor Green
        Write-Host ""
        Write-Host "⚠️  IMPORTANT:" -ForegroundColor Yellow
        Write-Host "  Keep backend and ngrok windows open!" -ForegroundColor White
        Write-Host "  Backend URL changes when you restart ngrok" -ForegroundColor White
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        
        # Update deployment info with frontend URL
        $finalInfo = @"
HIREMEBAHAMAS - DEPLOYMENT COMPLETE
========================================

✅ LIVE URLS:
Frontend: $frontendUrl
Backend:  $ngrokUrl

ADMIN CREDENTIALS:
Email: admin@hiremebahamas.com
Password: AdminPass123!

APP STORE READY:
- Website URL: $frontendUrl
- Privacy Policy: $frontendUrl/privacy-policy.html
- Terms of Service: $frontendUrl/terms-of-service.html

API ENDPOINTS:
  Health: $ngrokUrl/health
  Login: $ngrokUrl/api/auth/login
  Register: $ngrokUrl/api/auth/register
  Jobs: $ngrokUrl/api/jobs
  Posts: $ngrokUrl/api/posts

DEPLOYMENT DATE: $(Get-Date)

IMPORTANT NOTES:
- Keep backend and ngrok windows open
- Ngrok URL changes on restart (free tier)
- For permanent hosting, deploy backend to Render.com

========================================
"@
        Set-Location ..
        $finalInfo | Out-File -FilePath "DEPLOYMENT_COMPLETE.txt" -Encoding UTF8
        
        Write-Host "📄 Full details saved to: DEPLOYMENT_COMPLETE.txt" -ForegroundColor Gray
        Write-Host ""
        Write-Host "🚀 Opening your live website..." -ForegroundColor Cyan
        Start-Sleep -Seconds 2
        Start-Process $frontendUrl
        Write-Host ""
        
    } else {
        Write-Host "⚠️  Frontend deployed but couldn't extract URL" -ForegroundColor Yellow
        Write-Host "Check output above for deployment URL`n" -ForegroundColor Gray
        Set-Location ..
    }
} catch {
    Write-Host "❌ Error deploying frontend: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`nYou can manually deploy with: cd frontend; vercel --prod`n" -ForegroundColor Yellow
    Set-Location ..
}

Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
