<#!
.SYNOPSIS
  Unified launcher for HireBahamas platform: starts both backend and frontend with force restart options.

.DESCRIPTION
  Launches backend (Flask) and frontend (Vite) simultaneously with health checks.
  Supports force restart options for both components.

.PARAMETER ForceAll
  Force restart both backend and frontend: kill processes, clean caches/DBs, rebuild.

.PARAMETER BackendOnly
  Launch only backend.

.PARAMETER FrontendOnly
  Launch only frontend.

.PARAMETER BackendPort
  Backend port (default 8008).

.PARAMETER FrontendPort
  Frontend port (default 3000).

.PARAMETER VerboseLog
  Enable verbose logging for both services.

.EXAMPLE
  ./launch_hirebahamas.ps1 -ForceAll

.EXAMPLE
  ./launch_hirebahamas.ps1 -BackendOnly -VerboseLog
#>
param(
  [switch]$ForceAll,
  [switch]$BackendOnly,
  [switch]$FrontendOnly,
  [int]$BackendPort = 8008,
  [int]$FrontendPort = 3000,
  [switch]$VerboseLog
)

$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot
$FrontendDir = Join-Path $Root 'frontend'

function Info($m){ Write-Host "[INFO ] $m" -ForegroundColor Cyan }
function Warn($m){ Write-Host "[WARN ] $m" -ForegroundColor Yellow }
function Err ($m){ Write-Host "[ERROR] $m" -ForegroundColor Red }
function Ok  ($m){ Write-Host "[ OK  ] $m" -ForegroundColor Green }

Info "HireBahamas Unified Launcher"
Info "=============================="

# Launch backend if not FrontendOnly
if(-not $FrontendOnly){
  Info "Starting backend..."
  $backendArgs = @('-Port', $BackendPort)
  if($ForceAll){ $backendArgs += '-ForceAll' }
  if($VerboseLog){ $backendArgs += '-VerboseLog' }

  try {
    $backendJob = Start-Job -ScriptBlock {
      param($scriptPath, $jobArgs, $rootDir)
      Set-Location $rootDir
      & powershell -ExecutionPolicy Bypass -File $scriptPath @jobArgs
    } -ArgumentList (Join-Path $Root 'force_backend.ps1'), $backendArgs, $Root
    Info "Backend job started (ID: $($backendJob.Id))"
  } catch {
    Err "Failed to start backend: $($_.Exception.Message)"
    exit 1
  }
}

# Launch frontend if not BackendOnly
if(-not $BackendOnly){
  Info "Starting frontend..."
  $frontendArgs = @('-PrimaryPort', $FrontendPort)
  if($ForceAll){ $frontendArgs += '-HardKill'; $frontendArgs += '-CleanCache' }
  if($VerboseLog){ $frontendArgs += '-VerboseLog' }

  try {
    $frontendJob = Start-Job -ScriptBlock {
      param($scriptPath, $jobArgs, $frontendDir)
      Set-Location $frontendDir
      & powershell -ExecutionPolicy Bypass -File $scriptPath @jobArgs
    } -ArgumentList (Join-Path $FrontendDir 'force_frontend_dev.ps1'), $frontendArgs, $FrontendDir
    Info "Frontend job started (ID: $($frontendJob.Id))"
  } catch {
    Err "Failed to start frontend: $($_.Exception.Message)"
    exit 1
  }
}

# Wait for both to be ready
$backendReady = $false
$frontendReady = $false
$timeout = 60
$startTime = Get-Date

while(((Get-Date) - $startTime).TotalSeconds -lt $timeout){
  if(-not $FrontendOnly -and -not $backendReady){
    try {
      $resp = Invoke-WebRequest -Uri "http://127.0.0.1:$BackendPort/health" -UseBasicParsing -TimeoutSec 2
      if($resp.StatusCode -eq 200){ $backendReady = $true; Ok "Backend ready: http://127.0.0.1:$BackendPort" }
    } catch {}
  }

  if(-not $BackendOnly -and -not $frontendReady){
    try {
      $resp = Invoke-WebRequest -Uri "http://localhost:$FrontendPort" -UseBasicParsing -TimeoutSec 2
      if($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 500){ $frontendReady = $true; Ok "Frontend ready: http://localhost:$FrontendPort" }
    } catch {}
  }

  if(($FrontendOnly -or $backendReady) -and ($BackendOnly -or $frontendReady)){ break }
  Start-Sleep -Seconds 2
}

if(-not $FrontendOnly -and -not $backendReady){ Warn "Backend not ready within $timeout seconds" }
if(-not $BackendOnly -and -not $frontendReady){ Warn "Frontend not ready within $timeout seconds" }

# Open browser if both ready
if($backendReady -and $frontendReady){
  Info "Both services ready! Opening browser..."
  try { Start-Process "http://localhost:$FrontendPort" } catch { Warn "Could not open browser automatically." }
}

Info "Services are running in background jobs."
Info "To stop: Get-Job | Stop-Job; Get-Job | Remove-Job"
Info "To view logs: Get-Job | Receive-Job -Keep"

# Keep script alive to monitor
Info "Press Ctrl+C to exit (services will continue running)"
try {
  while($true){
    Start-Sleep -Seconds 10
    $jobs = Get-Job
    if($jobs | Where-Object { $_.State -eq 'Failed' }){
      Warn "Some jobs failed. Check with: Get-Job | Receive-Job"
    }
  }
} finally {
  Info "Exiting launcher. Services may still be running."
}