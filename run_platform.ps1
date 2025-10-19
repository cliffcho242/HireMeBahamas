<#!
.SYNOPSIS
  Simple HireBahamas Platform Launcher with Monitoring

.DESCRIPTION
  Starts the platform and monitoring system to keep it running.

.EXAMPLE
  .\run_platform.ps1
#>

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "🌴 Starting HireBahamas Platform..." -ForegroundColor Cyan

# Start platform
Write-Host "Starting platform services..." -ForegroundColor Green
$platformJob = Start-Job -ScriptBlock {
  param($root)
  Set-Location $root
  & powershell -ExecutionPolicy Bypass -File ".\launch_hirebahamas.ps1" -ForceAll
} -ArgumentList $Root

Write-Host "Platform job started (ID: $($platformJob.Id))" -ForegroundColor Green

# Wait for services to start
Write-Host "Waiting for services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Start monitor
Write-Host "Starting service monitor..." -ForegroundColor Green
$monitorJob = Start-Job -ScriptBlock {
  param($root)
  Set-Location $root
  & powershell -ExecutionPolicy Bypass -File ".\simple_monitor.ps1" -IntervalSeconds 30
} -ArgumentList $Root

Write-Host "Monitor job started (ID: $($monitorJob.Id))" -ForegroundColor Green

Write-Host ""
Write-Host "✅ Platform and Monitor are running!" -ForegroundColor Green
Write-Host ""
Write-Host "Access your platform:" -ForegroundColor Cyan
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "  Backend: http://127.0.0.1:8008" -ForegroundColor White
Write-Host ""
Write-Host "Monitor logs: monitor.log" -ForegroundColor Yellow
Write-Host "Stop all: Get-Job | Stop-Job; Get-Job | Remove-Job" -ForegroundColor Yellow
Write-Host ""
Write-Host "The monitor will automatically restart services if they fail!" -ForegroundColor Green

# Keep alive
try {
  while ($true) {
    Start-Sleep -Seconds 60
    $jobs = Get-Job
    if ($jobs | Where-Object { $_.State -eq 'Failed' }) {
      Write-Host "Some jobs failed. Check with: Get-Job | Receive-Job" -ForegroundColor Red
    }
  }
} finally {
  Write-Host "Launcher exiting. Services continue running." -ForegroundColor Yellow
}