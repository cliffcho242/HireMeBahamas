# HireBahamas Smart Launcher - Fixes Directory Navigation Issues
# Automatically handles frontend directory navigation

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "    🎯 HireBahamas Smart Launcher - Directory Fix Edition" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$basePath = "c:\Users\Dell\OneDrive\Desktop\HireBahamas"
$frontendPath = Join-Path $basePath "frontend"

Write-Host "🔧 DIRECTORY NAVIGATION FIX APPLIED" -ForegroundColor Yellow
Write-Host ""
Write-Host "Base Path: $basePath" -ForegroundColor Gray
Write-Host "Frontend Path: $frontendPath" -ForegroundColor Gray
Write-Host ""

# Verify directories exist
if (Test-Path $basePath) {
    Write-Host "✓ Base directory found" -ForegroundColor Green
} else {
    Write-Host "❌ Base directory missing" -ForegroundColor Red
    exit 1
}

if (Test-Path $frontendPath) {
    Write-Host "✓ Frontend directory found" -ForegroundColor Green
} else {
    Write-Host "❌ Frontend directory missing" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[STEP 1] Starting Backend Server..." -ForegroundColor Yellow
Set-Location $basePath

# Start backend
$backendCommand = "cd '$basePath'; & '.\.venv\Scripts\python.exe' final_backend.py; Write-Host 'Backend window can be closed safely'; pause"
Start-Process powershell -ArgumentList "-Command", $backendCommand -WindowStyle Normal

Start-Sleep -Seconds 4

Write-Host ""
Write-Host "[STEP 2] Starting Frontend Server..." -ForegroundColor Yellow

# Check and install dependencies if needed
$nodeModulesPath = Join-Path $frontendPath "node_modules"
if (-not (Test-Path $nodeModulesPath)) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    Set-Location $frontendPath
    npm install
    Write-Host "Dependencies installed!" -ForegroundColor Green
}

# Start frontend with correct directory
$frontendCommand = "cd '$frontendPath'; npm run dev; Write-Host 'Frontend window can be closed safely'; pause"
Start-Process powershell -ArgumentList "-Command", $frontendCommand -WindowStyle Normal

Start-Sleep -Seconds 6

Write-Host ""
Write-Host "[STEP 3] Opening Browser..." -ForegroundColor Yellow

# Open browser
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "                 🎉 LAUNCH COMPLETE! 🎉" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your platform is now running:" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor Yellow
Write-Host "🔧 Backend:  http://127.0.0.1:8008" -ForegroundColor Yellow
Write-Host "👤 Login:    admin@hirebahamas.com / AdminPass123!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Directory navigation issue FIXED! ✓" -ForegroundColor Green
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")