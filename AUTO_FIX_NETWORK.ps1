# AUTO FIX NETWORK - One-Click Solution
# This script automatically fixes all network errors with force mode

$ErrorActionPreference = "Continue"

Write-Host @"

================================================
   HIREBAHAMAS AUTO NETWORK FIX
   One-Click Automated Solution
================================================

"@ -ForegroundColor Cyan

Write-Host "Starting automated fix in 3 seconds..." -ForegroundColor Yellow
Write-Host "(Press Ctrl+C to cancel)" -ForegroundColor Gray
Start-Sleep -Seconds 3

Write-Host "`n[1/3] Checking system..." -ForegroundColor Cyan
$scriptPath = Join-Path $PSScriptRoot "NETWORK_FIX.ps1"

if (-not (Test-Path $scriptPath)) {
    Write-Host "[ERROR] NETWORK_FIX.ps1 not found!" -ForegroundColor Red
    Write-Host "Expected location: $scriptPath" -ForegroundColor Gray
    exit 1
}

Write-Host "[OK] Network fix script found" -ForegroundColor Green

Write-Host "`n[2/3] Executing force install..." -ForegroundColor Cyan
Write-Host "This will:" -ForegroundColor Yellow
Write-Host "  - Kill all backend processes" -ForegroundColor White
Write-Host "  - Clear network connections" -ForegroundColor White
Write-Host "  - Install missing Python packages" -ForegroundColor White
Write-Host "  - Restart backend server" -ForegroundColor White
Write-Host "  - Verify everything is working" -ForegroundColor White
Write-Host ""

# Execute the fix
& $scriptPath -Install -Force

Write-Host "`n[3/3] Complete!" -ForegroundColor Cyan

Write-Host @"

================================================
   FIX APPLIED
================================================

Next steps:
1. Check the status above
2. If backend is RUNNING, open: http://localhost:3000
3. If issues persist, check the logs

Commands:
  Check status: .\NETWORK_FIX.ps1 -Status
  Fix issues:   .\NETWORK_FIX.ps1 -Fix
  Re-run this:  .\AUTO_FIX_NETWORK.ps1

================================================

"@ -ForegroundColor Green

# Auto-open browser if backend is healthy
Start-Sleep -Seconds 2
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8008/health" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "Backend is healthy! Opening browser..." -ForegroundColor Green
        Start-Sleep -Seconds 2
        Start-Process "http://localhost:3000"
    }
} catch {
    Write-Host "Backend not responding. Check the output above for errors." -ForegroundColor Yellow
}
