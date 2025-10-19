# HireBahamas Auto-Fix PowerShell Launcher
param(
    [switch]$SkipDiagnostics = $false
)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "HireBahamas Platform Auto-Fix Launcher" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

if (-not $SkipDiagnostics) {
    Write-Host "Running automated diagnostics and fixes..." -ForegroundColor Yellow
    Write-Host "This will automatically resolve any connection issues." -ForegroundColor Yellow
    Write-Host ""
    
    # Set location
    Set-Location "c:\Users\Dell\OneDrive\Desktop\HireBahamas"
    
    # Run the automated diagnostics
    try {
        & "C:\Users\Dell\OneDrive\Desktop\HireBahamas\.venv\Scripts\python.exe" automated_platform_diagnostics.py
    } catch {
        Write-Host "Error running diagnostics: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Falling back to manual launch..." -ForegroundColor Yellow
        
        # Fallback manual launch
        Write-Host "Starting backend manually..." -ForegroundColor Yellow
        Start-Process powershell -ArgumentList "-Command", "cd 'c:\Users\Dell\OneDrive\Desktop\HireBahamas'; C:\Users\Dell\OneDrive\Desktop\HireBahamas\.venv\Scripts\python.exe final_backend.py; pause"
        
        Start-Sleep -Seconds 3
        
        Write-Host "Starting frontend manually..." -ForegroundColor Yellow
        Start-Process powershell -ArgumentList "-Command", "cd 'c:\Users\Dell\OneDrive\Desktop\HireBahamas\frontend'; npm run dev; pause"
        
        Start-Sleep -Seconds 5
        
        Write-Host "Opening browser..." -ForegroundColor Cyan
        Start-Process "http://localhost:3001"
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Platform launch complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor White
Write-Host "Frontend: http://localhost:3001" -ForegroundColor Yellow
Write-Host "Backend:  http://127.0.0.1:8008" -ForegroundColor Yellow
Write-Host "Admin Login: admin@hirebahamas.com / AdminPass123!" -ForegroundColor Yellow
Write-Host ""

# Quick health check
Write-Host "Performing quick health check..." -ForegroundColor Cyan
try {
    $backendHealth = Invoke-RestMethod -Uri "http://127.0.0.1:8008/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✓ Backend: Online ($($backendHealth.status))" -ForegroundColor Green
} catch {
    Write-Host "✗ Backend: Offline or starting up" -ForegroundColor Red
}

try {
    $frontendHealth = Invoke-WebRequest -Uri "http://localhost:3001" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✓ Frontend: Online (Status: $($frontendHealth.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "✗ Frontend: Offline or starting up" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to exit or close this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")