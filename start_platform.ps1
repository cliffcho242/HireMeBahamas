<#!
.SYNOPSIS
  HireBahamas Platform Launcher with AI Guardian - Start platform with intelligent monitoring

.DESCRIPTION
  Launches the HireBahamas platform and starts the AI Guardian for continuous monitoring
  and automatic healing. Ensures the platform stays running smoothly.

.PARAMETER Mode
  Launch mode: Normal (start platform), Guardian (start with AI monitoring), or Quick (fast start)

.EXAMPLE
  .\start_platform.ps1 -Mode Guardian

.EXAMPLE
  .\start_platform.ps1 -Mode Quick
#>
param(
  [ValidateSet("Normal", "Guardian", "Quick")]
  [string]$Mode = "Guardian"
)

$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot

function Write-Header($msg) {
  Write-Host "🌴 $msg 🌴" -ForegroundColor Cyan
  Write-Host ("=" * ($msg.Length + 4)) -ForegroundColor Yellow
}

function Write-Step($msg) {
  Write-Host "➤ $msg" -ForegroundColor Green
}

function Write-Success($msg) {
  Write-Host "✅ $msg" -ForegroundColor Green
}

function Write-Error($msg) {
  Write-Host "❌ $msg" -ForegroundColor Red
}

Write-Header "HIREBAHAMAS PLATFORM LAUNCHER"

if ($Mode -eq "Quick") {
  Write-Step "Quick launch mode - starting services..."
  Write-Step "Launching unified platform..."
  $launchJob = Start-Job -ScriptBlock {
    param($root)
    Set-Location $root
    & powershell -ExecutionPolicy Bypass -File ".\launch_hirebahamas.ps1" -ForceAll
  } -ArgumentList $Root

  Write-Success "Platform starting in background (Job ID: $($launchJob.Id))"
  Write-Host "Monitor with: Get-Job | Receive-Job -Keep" -ForegroundColor Cyan
  exit 0
}

if ($Mode -eq "Normal") {
  Write-Step "Normal launch mode - starting platform..."
  & powershell -ExecutionPolicy Bypass -File ".\launch_hirebahamas.ps1" -ForceAll
  exit 0
}

if ($Mode -eq "Guardian") {
  Write-Step "Guardian mode - starting platform with AI monitoring..."

  # Start the platform
  Write-Step "Initializing HireBahamas platform..."
  $platformJob = Start-Job -ScriptBlock {
    param($root)
    Set-Location $root
    & powershell -ExecutionPolicy Bypass -File ".\launch_hirebahamas.ps1" -ForceAll
  } -ArgumentList $Root

  Write-Success "Platform initialization started (Job ID: $($platformJob.Id))"

  # Wait a moment for platform to start
  Write-Step "Waiting for platform initialization..."
  Start-Sleep -Seconds 10

  # Start AI Guardian
  Write-Step "Activating AI Guardian monitoring system..."
  $guardianJob = Start-Job -ScriptBlock {
    param($root)
    Set-Location $root
    & powershell -ExecutionPolicy Bypass -File ".\ai_guardian.ps1" -Mode Full -IntervalSeconds 30 -Verbose
  } -ArgumentList $Root

  Write-Success "AI Guardian activated (Job ID: $($guardianJob.Id))"

  Write-Host ""
  Write-Header "PLATFORM STATUS"
  Write-Host "Platform Job ID: $($platformJob.Id)" -ForegroundColor White
  Write-Host "Guardian Job ID: $($guardianJob.Id)" -ForegroundColor White
  Write-Host ""
  Write-Host "🤖 AI GUARDIAN FEATURES:" -ForegroundColor Cyan
  Write-Host "  - Continuous health monitoring (30s intervals)" -ForegroundColor White
  Write-Host "  - Automatic service restart on failures" -ForegroundColor White
  Write-Host "  - Intelligent diagnostics and healing" -ForegroundColor White
  Write-Host "  - Real-time status display" -ForegroundColor White
  Write-Host "  - Predictive maintenance alerts" -ForegroundColor White
  Write-Host ""
  Write-Host "📊 MONITORING COMMANDS:" -ForegroundColor Yellow
  Write-Host "  View Guardian: Get-Job -Id $($guardianJob.Id) | Receive-Job -Keep" -ForegroundColor White
  Write-Host "  View Platform: Get-Job -Id $($platformJob.Id) | Receive-Job -Keep" -ForegroundColor White
  Write-Host "  Stop All: Get-Job | Stop-Job; Get-Job | Remove-Job" -ForegroundColor White
  Write-Host ""
  Write-Host "🌐 ACCESS YOUR PLATFORM:" -ForegroundColor Green
  Write-Host "  Frontend: http://localhost:3000" -ForegroundColor White
  Write-Host "  Backend: http://127.0.0.1:8008" -ForegroundColor White
  Write-Host ""
  Write-Host "The AI Guardian will now keep your platform running smoothly!" -ForegroundColor Cyan
  Write-Host "Press Ctrl+C to exit this launcher (services continue running)" -ForegroundColor Yellow

  # Keep launcher alive to show status
  try {
    while ($true) {
      Start-Sleep -Seconds 30

      # Check if jobs are still running
      $platformStatus = Get-Job -Id $platformJob.Id -ErrorAction SilentlyContinue
      $guardianStatus = Get-Job -Id $guardianJob.Id -ErrorAction SilentlyContinue

      if ($platformStatus.State -ne "Running") {
        Write-Error "Platform job stopped: $($platformStatus.State)"
      }
      if ($guardianStatus.State -ne "Running") {
        Write-Error "Guardian job stopped: $($guardianStatus.State)"
      }
    }
  } finally {
    Write-Host "Launcher exiting. Platform and Guardian continue running in background." -ForegroundColor Yellow
  }
}