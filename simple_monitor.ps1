<#!
.SYNOPSIS
  Simple HireBahamas Service Monitor and Auto-Restarter

.DESCRIPTION
  Monitors frontend and backend services, automatically restarts them if they fail.
  Simple and reliable alternative to the complex AI Guardian.

.PARAMETER IntervalSeconds
  Monitoring interval in seconds (default 30)

.EXAMPLE
  .\simple_monitor.ps1
#>
param(
  [int]$IntervalSeconds = 30
)

$ErrorActionPreference = 'Continue'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$FrontendPath = Join-Path $Root "frontend"

function Log($message, $level = "INFO") {
  $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
  $logEntry = "[$timestamp] [$level] $message"
  Write-Host $logEntry -ForegroundColor $(switch ($level) {
    "ERROR" { "Red" }
    "WARN" { "Yellow" }
    "SUCCESS" { "Green" }
    default { "White" }
  })
  Add-Content -Path (Join-Path $Root "monitor.log") -Value $logEntry -ErrorAction SilentlyContinue
}

function Test-Service($url, $timeout = 5) {
  try {
    $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec $timeout
    return $response.StatusCode -ge 200 -and $response.StatusCode -lt 400
  } catch {
    return $false
  }
}

function Restart-Frontend {
  Log "Restarting frontend..." "WARN"
  try {
    # Kill existing node processes
    Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2

    # Start frontend
    $startInfo = New-Object System.Diagnostics.ProcessStartInfo
    $startInfo.FileName = "powershell.exe"
    $startInfo.Arguments = "-ExecutionPolicy Bypass -File `"$(Join-Path $FrontendPath 'force_frontend_dev.ps1')`""
    $startInfo.WorkingDirectory = $FrontendPath
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $startInfo
    $null = $process.Start()

    Log "Frontend restart initiated" "SUCCESS"
    return $true
  } catch {
    Log "Frontend restart failed: $($_.Exception.Message)" "ERROR"
    return $false
  }
}

function Restart-Backend {
  Log "Restarting backend..." "WARN"
  try {
    # Kill existing python processes
    Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2

    # Start backend
    $startInfo = New-Object System.Diagnostics.ProcessStartInfo
    $startInfo.FileName = "powershell.exe"
    $startInfo.Arguments = "-ExecutionPolicy Bypass -File `"$(Join-Path $Root 'force_backend.ps1')`" -ForceAll"
    $startInfo.WorkingDirectory = $Root
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $startInfo
    $null = $process.Start()

    Log "Backend restart initiated" "SUCCESS"
    return $true
  } catch {
    Log "Backend restart failed: $($_.Exception.Message)" "ERROR"
    return $false
  }
}

Log "HireBahamas Simple Monitor starting..." "SUCCESS"
Log "Monitoring interval: ${IntervalSeconds}s" "INFO"

$frontendDownCount = 0
$backendDownCount = 0

while ($true) {
  $frontendHealthy = Test-Service "http://localhost:3000"
  $backendHealthy = Test-Service "http://127.0.0.1:8008/health"

  if (-not $frontendHealthy) {
    $frontendDownCount++
    Log "Frontend DOWN (count: $frontendDownCount)" "ERROR"
    if ($frontendDownCount -ge 2) {
      Restart-Frontend
      $frontendDownCount = 0
      Start-Sleep -Seconds 10  # Wait for restart
    }
  } else {
    if ($frontendDownCount -gt 0) {
      Log "Frontend recovered" "SUCCESS"
      $frontendDownCount = 0
    }
  }

  if (-not $backendHealthy) {
    $backendDownCount++
    Log "Backend DOWN (count: $backendDownCount)" "ERROR"
    if ($backendDownCount -ge 2) {
      Restart-Backend
      $backendDownCount = 0
      Start-Sleep -Seconds 10  # Wait for restart
    }
  } else {
    if ($backendDownCount -gt 0) {
      Log "Backend recovered" "SUCCESS"
      $backendDownCount = 0
    }
  }

  # Status update every 10 cycles
  if ((Get-Date).Second % ($IntervalSeconds * 10) -lt $IntervalSeconds) {
    $status = "Status: Frontend=$(if ($frontendHealthy) {'OK'} else {'DOWN'}), Backend=$(if ($backendHealthy) {'OK'} else {'DOWN'})"
    Log $status "INFO"
  }

  Start-Sleep -Seconds $IntervalSeconds
}