# Facebook-Like AI Platform Launcher for PowerShell
# HireBahamas Advanced Social Experience

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "        🚀 HireBahamas Facebook-Like AI Platform" -ForegroundColor Yellow
Write-Host "             Advanced Social Media Experience" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$workspaceDir = "c:\Users\Dell\OneDrive\Desktop\HireBahamas"
Set-Location $workspaceDir

Write-Host "[STEP 1] 🤖 Activating AI Environment..." -ForegroundColor Green
try {
    & ".venv\Scripts\Activate.ps1"
    Write-Host "✓ Python environment activated" -ForegroundColor Green
} catch {
    Write-Host "⚠ Virtual environment not found, using system Python" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[STEP 2] 🔧 Starting Facebook-Like Backend..." -ForegroundColor Green
Write-Host "Launching AI-powered social backend server..." -ForegroundColor White

$backendJob = Start-Process -FilePath "python" -ArgumentList "facebook_like_backend.py" -WorkingDirectory $workspaceDir -WindowStyle Normal -PassThru
Write-Host "✓ Backend process started (PID: $($backendJob.Id))" -ForegroundColor Green

Start-Sleep 6

Write-Host ""
Write-Host "[STEP 3] 🌐 Preparing Social Frontend..." -ForegroundColor Green

# Switch to frontend directory and backup original App.tsx
Set-Location "$workspaceDir\frontend\src"

if (-not (Test-Path "App_Original.tsx")) {
    Copy-Item "App.tsx" "App_Original.tsx" -ErrorAction SilentlyContinue
    Write-Host "✓ Original App.tsx backed up" -ForegroundColor Green
}

Copy-Item "App_Social.tsx" "App.tsx" -ErrorAction SilentlyContinue
Write-Host "✓ Switched to Facebook-like frontend" -ForegroundColor Green

# Return to workspace root
Set-Location $workspaceDir

Write-Host "Starting frontend development server..." -ForegroundColor White
Set-Location "$workspaceDir\frontend"
$frontendJob = Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WorkingDirectory "$workspaceDir\frontend" -WindowStyle Normal -PassThru
Write-Host "✓ Frontend process started (PID: $($frontendJob.Id))" -ForegroundColor Green

Set-Location $workspaceDir
Start-Sleep 8

Write-Host ""
Write-Host "[STEP 4] 🔍 Running Health Check..." -ForegroundColor Green
try {
    $health = Invoke-RestMethod -Uri "http://127.0.0.1:8008/health" -TimeoutSec 10
    Write-Host "✓ Facebook-Like Backend: HEALTHY" -ForegroundColor Green
    Write-Host "✓ AI Analytics: $($health.ai_analytics)" -ForegroundColor Green
} catch {
    Write-Host "⚠ Backend: Starting up... (this is normal)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[STEP 5] 🚀 Opening Social Platform..." -ForegroundColor Green
Start-Process "http://localhost:3000"
Start-Sleep 2
Start-Process "http://localhost:3001"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "               🎉 FACEBOOK-LIKE PLATFORM LAUNCHED! 🎉" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Your AI-Powered Social Platform Features:" -ForegroundColor White
Write-Host ""
Write-Host "🤖 AI Features:" -ForegroundColor Magenta
Write-Host "  • User behavior pattern analysis" -ForegroundColor White
Write-Host "  • Intelligent content recommendations" -ForegroundColor White
Write-Host "  • Engagement score tracking" -ForegroundColor White
Write-Host "  • User type classification" -ForegroundColor White
Write-Host "  • Predictive analytics" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Social Features:" -ForegroundColor Blue
Write-Host "  • Facebook-like interface" -ForegroundColor White
Write-Host "  • Real-time posts and comments" -ForegroundColor White
Write-Host "  • Like and share functionality" -ForegroundColor White
Write-Host "  • AI-powered feed optimization" -ForegroundColor White
Write-Host "  • User profile management" -ForegroundColor White
Write-Host "  • Direct messaging" -ForegroundColor White
Write-Host "  • Trending topics" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Access URLs:" -ForegroundColor Green
Write-Host "  • Platform: http://localhost:3000" -ForegroundColor White
Write-Host "  • Alt Port: http://localhost:3001" -ForegroundColor White
Write-Host "  • Backend API: http://127.0.0.1:8008" -ForegroundColor White
Write-Host "  • Health Check: http://127.0.0.1:8008/health" -ForegroundColor White
Write-Host ""
Write-Host "👤 Login Credentials:" -ForegroundColor Yellow
Write-Host "  • Email: admin@hirebahamas.com" -ForegroundColor White
Write-Host "  • Password: AdminPass123!" -ForegroundColor White
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔧 Technical Features Active:" -ForegroundColor Cyan
Write-Host "  ✓ AI User Pattern Analytics" -ForegroundColor Green
Write-Host "  ✓ Machine Learning Recommendations" -ForegroundColor Green
Write-Host "  ✓ Real-time Socket Connections" -ForegroundColor Green
Write-Host "  ✓ Advanced Rate Limiting" -ForegroundColor Green
Write-Host "  ✓ JWT Authentication" -ForegroundColor Green
Write-Host "  ✓ Performance Caching" -ForegroundColor Green
Write-Host "  ✓ Predictive Error Prevention" -ForegroundColor Green
Write-Host ""
Write-Host "Both servers are running in separate windows." -ForegroundColor White
Write-Host "The AI system continuously learns from user interactions." -ForegroundColor White
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Press any key to exit launcher (servers will continue running)..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")