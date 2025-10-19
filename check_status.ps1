<#!
.SYNOPSIS
  Quick HireBahamas Platform Status Checker

.DESCRIPTION
  Fast status check for frontend and backend services with AI-powered diagnostics.

.EXAMPLE
  .\check_status.ps1
#>

$ErrorActionPreference = 'SilentlyContinue'

function Test-Service($name, $url, $timeout = 5) {
  $result = @{
    Name = $name
    Status = "UNKNOWN"
    ResponseTime = 0
    Healthy = $false
  }

  $start = Get-Date
  try {
    $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec $timeout
    $result.Status = $response.StatusCode
    $result.ResponseTime = [math]::Round(((Get-Date) - $start).TotalMilliseconds, 0)
    $result.Healthy = $response.StatusCode -ge 200 -and $response.StatusCode -lt 400
  } catch {
    $result.Status = "DOWN"
    $result.ResponseTime = [math]::Round(((Get-Date) - $start).TotalMilliseconds, 0)
    $result.Healthy = $false
  }

  return $result
}

Write-Host "🔍 HIREBAHAMAS PLATFORM STATUS" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Yellow

$frontend = Test-Service "Frontend" "http://localhost:3000"
$backend = Test-Service "Backend" "http://127.0.0.1:8008/health"

# Frontend Status
$frontendIcon = if ($frontend.Healthy) { "OK" } else { "DOWN" }
$frontendColor = if ($frontend.Healthy) { "Green" } else { "Red" }
Write-Host "Frontend (localhost:3000): $frontendIcon | $($frontend.ResponseTime)ms" -ForegroundColor $frontendColor

# Backend Status
$backendIcon = if ($backend.Healthy) { "OK" } else { "DOWN" }
$backendColor = if ($backend.Healthy) { "Green" } else { "Red" }
Write-Host "Backend (127.0.0.1:8008): $backendIcon | $($backend.ResponseTime)ms" -ForegroundColor $backendColor

# Overall Status
$overallHealthy = $frontend.Healthy -and $backend.Healthy
$overallIcon = if ($overallHealthy) { "ALL OK" } else { "ISSUES" }
$overallColor = if ($overallHealthy) { "Green" } else { "Red" }

Write-Host ""
Write-Host "$overallIcon" -ForegroundColor $overallColor

if (-not $overallHealthy) {
  Write-Host ""
  Write-Host "QUICK FIXES:" -ForegroundColor Yellow
  Write-Host "  Start Platform: .\start_platform.ps1 -Mode Guardian" -ForegroundColor White
  Write-Host "  Force Restart: .\ai_guardian.ps1 -Mode Heal" -ForegroundColor White
}

Write-Host ""
$guardianActive = Get-Process -Name powershell -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -match "ai_guardian" }
Write-Host "AI Guardian: $(if ($guardianActive) { "ACTIVE" } else { "INACTIVE" })" -ForegroundColor $(if ($guardianActive) { "Green" } else { "Red" })