# 🚀 Quick Deploy Backend to Railway

Write-Host "`n🚂 RAILWAY BACKEND DEPLOYMENT GUIDE`n" -ForegroundColor Cyan -BackgroundColor Black

Write-Host "═══════════════════════════════════════════════════════════════`n" -ForegroundColor Green

Write-Host "📋 Step 1: Open Railway" -ForegroundColor Yellow
Write-Host "   Opening Railway in browser..." -ForegroundColor White
Start-Process "https://railway.app/new"
Start-Sleep -Seconds 3

Write-Host "`n📋 Step 2: Authentication" -ForegroundColor Yellow
Write-Host "   ✓ Log in with GitHub (if not logged in)" -ForegroundColor White
Write-Host "   ✓ Authorize Railway to access your repositories`n" -ForegroundColor White

Write-Host "📋 Step 3: Deploy from GitHub" -ForegroundColor Yellow
Write-Host "   ✓ Click 'Deploy from GitHub repo'" -ForegroundColor White
Write-Host "   ✓ Search for 'HireMeBahamas'" -ForegroundColor White
Write-Host "   ✓ Select the repository`n" -ForegroundColor White

Write-Host "📋 Step 4: Configure (Auto-Detected)" -ForegroundColor Yellow
Write-Host "   Railway will automatically detect:" -ForegroundColor White
Write-Host "   ✓ Python (from requirements.txt)" -ForegroundColor Green
Write-Host "   ✓ Flask (from final_backend.py)" -ForegroundColor Green
Write-Host "   ✓ Start command (from Procfile)" -ForegroundColor Green
Write-Host "   ✓ Port and environment`n" -ForegroundColor Green

Write-Host "📋 Step 5: Environment Variables" -ForegroundColor Yellow
Write-Host "   Add these in Railway dashboard (Settings → Variables):" -ForegroundColor White
Write-Host "   - SECRET_KEY: hiremebahamas_production_secret_2024_secure_key_v1" -ForegroundColor Cyan
Write-Host "   - FLASK_ENV: production" -ForegroundColor Cyan
Write-Host "   - DATABASE_URL: (Railway provides automatically)`n" -ForegroundColor Cyan

Write-Host "📋 Step 6: Deploy!" -ForegroundColor Yellow
Write-Host "   ✓ Click 'Deploy'" -ForegroundColor White
Write-Host "   ✓ Wait 2-3 minutes for deployment" -ForegroundColor White
Write-Host "   ✓ Railway will show deployment logs`n" -ForegroundColor White

Write-Host "📋 Step 7: Get Your Backend URL" -ForegroundColor Yellow
Write-Host "   ✓ Click on your deployment" -ForegroundColor White
Write-Host "   ✓ Go to 'Settings' → 'Domains'" -ForegroundColor White
Write-Host "   ✓ Railway provides a URL like: https://hiremebahamas-production.up.railway.app" -ForegroundColor White
Write-Host "   ✓ Copy this URL!`n" -ForegroundColor White

Write-Host "═══════════════════════════════════════════════════════════════`n" -ForegroundColor Green

Write-Host "⏱️ Estimated Time: 10 minutes`n" -ForegroundColor Yellow

Write-Host "📝 After deployment, run: " -NoNewline -ForegroundColor White
Write-Host ".\CONNECT_FRONTEND_TO_BACKEND.ps1" -ForegroundColor Cyan

Write-Host "`n═══════════════════════════════════════════════════════════════`n" -ForegroundColor Green

# Keep window open
$null = Read-Host "`nPress Enter to close this window"
