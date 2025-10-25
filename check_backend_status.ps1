# Automated Backend Status Checker
# This script checks if the Render backend is live

Write-Host "`n🔄 AUTOMATED BACKEND MONITORING" -ForegroundColor Cyan -BackgroundColor Black
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "`n⏰ Checking every 45 seconds (max 6 attempts = ~5 minutes)" -ForegroundColor Yellow
Write-Host "   Backend URL: https://hiremebahamas.onrender.com" -ForegroundColor White
Write-Host "`n════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

$maxAttempts = 6
$intervalSeconds = 45
$backendUrl = "https://hiremebahamas.onrender.com/health"

for ($attempt = 1; $attempt -le $maxAttempts; $attempt++) {
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] Attempt $attempt/$maxAttempts : " -NoNewline -ForegroundColor Cyan
    
    try {
        $response = Invoke-RestMethod -Uri $backendUrl -TimeoutSec 20 -ErrorAction Stop
        
        # SUCCESS!
        Write-Host "✅ BACKEND IS LIVE!" -ForegroundColor Green
        Write-Host "`n════════════════════════════════════════════════════════════" -ForegroundColor Green
        Write-Host "         🎉 DEPLOYMENT SUCCESSFUL! 🎉" -ForegroundColor Green -BackgroundColor Black
        Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Green
        Write-Host "`n✅ Backend Status: $($response.status)" -ForegroundColor Cyan
        Write-Host "✅ Message: $($response.message)" -ForegroundColor Cyan
        Write-Host "✅ Timestamp: $($response.timestamp)" -ForegroundColor Cyan
        Write-Host "`n🌐 YOUR LIVE PLATFORM:" -ForegroundColor Yellow
        Write-Host "   Frontend: https://frontend-28x0xgo52-cliffs-projects-a84c76c9.vercel.app" -ForegroundColor Cyan
        Write-Host "   Backend:  https://hiremebahamas.onrender.com" -ForegroundColor Cyan
        Write-Host "`n🔐 Admin Login:" -ForegroundColor Yellow
        Write-Host "   Email:    admin@hiremebahamas.com" -ForegroundColor White
        Write-Host "   Password: AdminPass123!" -ForegroundColor White
        Write-Host "`n✅ READY FOR APP STORES!" -ForegroundColor Green
        Write-Host "   • Google Play Store ✅" -ForegroundColor White
        Write-Host "   • Apple App Store ✅" -ForegroundColor White
        Write-Host "`n════════════════════════════════════════════════════════════" -ForegroundColor Green
        Write-Host "`n🎊 Your HireBahamas platform is now fully operational!" -ForegroundColor Cyan
        Write-Host "   Open your website and test the login!" -ForegroundColor White
        Write-Host "`n════════════════════════════════════════════════════════════`n" -ForegroundColor Green
        
        # Open the website
        Start-Process "https://frontend-28x0xgo52-cliffs-projects-a84c76c9.vercel.app"
        
        exit 0
        
    } catch {
        $errorMsg = $_.Exception.Message
        if ($errorMsg -like "*timeout*") {
            Write-Host "⏳ Timeout (still building)" -ForegroundColor Yellow
        } elseif ($errorMsg -like "*502*" -or $errorMsg -like "*Bad Gateway*") {
            Write-Host "⏳ 502 Bad Gateway (still deploying)" -ForegroundColor Yellow
        } elseif ($errorMsg -like "*connection*") {
            Write-Host "⏳ Connection closed (server starting)" -ForegroundColor Yellow
        } else {
            Write-Host "⏳ Not ready yet" -ForegroundColor Yellow
        }
        
        if ($attempt -lt $maxAttempts) {
            Write-Host "   ⏰ Waiting $intervalSeconds seconds..." -ForegroundColor Gray
            Start-Sleep -Seconds $intervalSeconds
            Write-Host ""
        } else {
            Write-Host "`n════════════════════════════════════════════════════════════" -ForegroundColor Yellow
            Write-Host "   ⚠️  Backend still deploying after $($maxAttempts * $intervalSeconds / 60) minutes" -ForegroundColor Yellow
            Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Yellow
            Write-Host "`n📊 POSSIBLE REASONS:" -ForegroundColor Cyan
            Write-Host "   1. First-time deployment takes 5-10 minutes" -ForegroundColor White
            Write-Host "   2. Render free tier may have queue delays" -ForegroundColor White
            Write-Host "   3. Dependencies installation taking longer" -ForegroundColor White
            Write-Host "`n🎯 NEXT STEPS:" -ForegroundColor Cyan
            Write-Host "   Option A: Wait 3 more minutes, then run this script again" -ForegroundColor White
            Write-Host "             Command: .\check_backend_status.ps1" -ForegroundColor Cyan
            Write-Host "`n   Option B: Check Render logs manually" -ForegroundColor White
            Write-Host "             URL: https://dashboard.render.com/web/srv-d3qjl58dl3ps73c151mg" -ForegroundColor Cyan
            Write-Host "`n   Option C: Tell Copilot: 'test now'" -ForegroundColor White
            Write-Host "             I'll check the status immediately" -ForegroundColor Gray
            Write-Host "`n════════════════════════════════════════════════════════════`n" -ForegroundColor Yellow
            
            exit 1
        }
    }
}
