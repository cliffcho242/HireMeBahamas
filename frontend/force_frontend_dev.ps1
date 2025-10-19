<#!
.SYNOPSIS
  Force-kill any stuck frontend dev server processes (Node/Vite), optionally clear cache, and relaunch Vite with fallback ports.

.DESCRIPTION
  This script is useful when `npm run dev` appears to hang or the browser never loads.
  It will:
    1. Validate the frontend directory
    2. Kill processes bound to the target ports (default 3000 + fallbacks)
    3. Optionally clean Vite cache folders
    4. Attempt to start Vite on the primary port, then fallback ports if the server does not become reachable
    5. Detect readiness by polling the HTTP endpoint

.PARAMETER PrimaryPort
  Primary port to attempt first (default 3000)

.PARAMETER FallbackPorts
  Additional ports to try if the primary doesn’t start serving (default 3001,3002)

.PARAMETER CleanCache
  If supplied, removes .vite and other build caches inside node_modules

.PARAMETER HardKill
  Also kill ALL node.exe processes owned by the current user (more aggressive)

.PARAMETER TimeoutSeconds
  Max seconds to wait for a port to respond before switching to the next one (default 35)

.PARAMETER VerboseLog
  Stream extra diagnostic info

.EXAMPLE
  ./force_frontend_dev.ps1 -CleanCache -VerboseLog

.EXAMPLE
  ./force_frontend_dev.ps1 -PrimaryPort 3000 -FallbackPorts 3005,3010

.NOTES
  Safe to re-run. Does not delete node_modules unless you manually remove it.
#>

param(
  [int]$PrimaryPort = 3000,
  [int[]]$FallbackPorts = @(3001,3002),
  [switch]$CleanCache,
  [switch]$HardKill,
  [int]$TimeoutSeconds = 35,
  [switch]$VerboseLog
)

$ErrorActionPreference = 'Stop'

function Write-Info($msg){ Write-Host "[INFO ] $msg" -ForegroundColor Cyan }
function Write-Warn($msg){ Write-Host "[WARN ] $msg" -ForegroundColor Yellow }
function Write-Err($msg){ Write-Host "[ERROR] $msg" -ForegroundColor Red }
function Write-Success($msg){ Write-Host "[ OK  ] $msg" -ForegroundColor Green }

# Resolve frontend path
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$FrontendDir = $ScriptRoot  # script placed inside frontend folder
if(-not (Test-Path (Join-Path $FrontendDir 'package.json'))){
  Write-Err "package.json not found in $FrontendDir. Place this script in frontend folder or adjust path."
  exit 1
}

Write-Info "Frontend directory: $FrontendDir"

if($env:PORT){
  Write-Warn "Environment variable PORT=$env:PORT is set. Vite config already defines port 3000; CLI --port overrides both."
}

# Helper: Get PIDs listening on a port
function Get-PortPids([int]$Port){
  netstat -ano | Select-String ":$Port" | ForEach-Object {
    ($_.ToString() -split '\s+')[-1]
  } | Sort-Object -Unique | Where-Object { $_ -match '^[0-9]+$' }
}

# Kill processes on a port
function Free-Port([int]$Port){
  $pids = Get-PortPids -Port $Port
  if($pids){
    Write-Warn "Port $Port in use by PIDs: $($pids -join ', ') -> terminating"
    foreach($procPid in $pids){
      try { 
        Stop-Process -Id $procPid -Force -ErrorAction Stop
        Write-Info "Killed PID $procPid on port $Port"
      } catch {
        Write-Warn ("Could not kill PID {0} - {1}" -f $procPid, $_.Exception.Message)
      }
    }
  } else {
    Write-Info "Port $Port is free"
  }
}

# Optional broad kill
if($HardKill){
  Write-Warn "HardKill enabled: terminating ALL node.exe processes for current user"
  Get-Process node -ErrorAction SilentlyContinue | ForEach-Object {
    try { Stop-Process -Id $_.Id -Force; Write-Info "Hard-killed node PID $($_.Id)" } catch { Write-Warn "Failed to kill node PID $($_.Id)" }
  }
}

# Clean caches if requested
if($CleanCache){
  Write-Info "Cleaning Vite/TypeScript caches"
  $cacheTargets = @(
    (Join-Path $FrontendDir 'node_modules/.vite'),
    (Join-Path $FrontendDir 'node_modules/.cache'),
    (Join-Path $FrontendDir 'node_modules/.tsbuildinfo'),
    (Join-Path $FrontendDir '.turbo')
  )
  foreach($target in $cacheTargets){
    if(Test-Path $target){
      try { Remove-Item -Recurse -Force $target; Write-Info "Removed $target" } catch { Write-Warn "Failed to remove $target : $_" }
    }
  }
}

# Ensure dependencies
if(-not (Test-Path (Join-Path $FrontendDir 'node_modules'))){
  Write-Info "node_modules missing -> running npm install"
  pushd $FrontendDir
  npm install
  popd
}

$allPorts = @($PrimaryPort) + $FallbackPorts

# Poll URL for readiness
function Test-ServerReady($Port){
  try {
    $resp = Invoke-WebRequest -Uri "http://localhost:$Port" -UseBasicParsing -TimeoutSec 2
    if($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 500){ return $true }
  } catch {}
  return $false
}

function Start-ViteOnPort([int]$Port){
  Write-Info "Attempting start on port $Port"
  Free-Port -Port $Port

  $global:LogFile = Join-Path $FrontendDir "vite-$Port-$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
  Write-Info "Logging output to $LogFile"

  $psi = New-Object System.Diagnostics.ProcessStartInfo
  # Resolve npm executable (handles cases where PATH not propagated in subshell)
  $npmExe = Get-Command npm -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty Source
  if(-not $npmExe){
    Write-Warn "npm not found in PATH, attempting to invoke npx vite directly via cmd.exe"
    $npxCmd = Get-Command npx -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty Source
    if($npxCmd){
      $psi.FileName = "$env:ComSpec"  # cmd.exe
      $psi.Arguments = "/c npx vite --port $Port"
    } else {
      Write-Err "Neither npm nor npx were found. Ensure Node.js is installed and PATH is set."
      return $false
    }
  } else {
    # Use cmd.exe to execute npm script reliably
    $psi.FileName = "$env:ComSpec"
    $psi.Arguments = "/c npm run dev -- --port $Port"
  }
  $psi.WorkingDirectory = $FrontendDir
  $psi.RedirectStandardOutput = $true
  $psi.RedirectStandardError  = $true
  $psi.UseShellExecute = $false
  $psi.CreateNoWindow = $true

  $proc = New-Object System.Diagnostics.Process
  $proc.StartInfo = $psi
  $null = $proc.Start()

  # Async log capture
  $stdOutHandler = [System.Diagnostics.DataReceivedEventHandler]{ param($sender,$e) if($e.Data){ Add-Content -Path $global:LogFile -Value $e.Data; if($VerboseLog){ Write-Host $e.Data } } }
  $stdErrHandler = [System.Diagnostics.DataReceivedEventHandler]{ param($sender,$e) if($e.Data){ Add-Content -Path $global:LogFile -Value $e.Data; if($VerboseLog){ Write-Host $e.Data -ForegroundColor DarkRed } } }
  $proc.BeginOutputReadLine(); $proc.BeginErrorReadLine()

  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  while((Get-Date) -lt $deadline){
    Start-Sleep -Seconds 1
    if($proc.HasExited){
      Write-Warn "Vite process exited early with code $($proc.ExitCode)"
      return $false
    }
    if(Test-ServerReady -Port $Port){
      Write-Success "Frontend ready: http://localhost:$Port"
      Write-Info "(Streaming stopped: see log file for full output)"
      return $true
    }
  }
  Write-Warn "Timeout waiting for port $Port to respond"
  try { if(-not $proc.HasExited){ $proc.Kill() } } catch {}
  return $false
}

$started = $false
foreach($p in $allPorts){
  if(Start-ViteOnPort -Port $p){ $started = $true; $SelectedPort = $p; break }
}

if(-not $started){
  Write-Err "Failed to start dev server on any port: $($allPorts -join ', ')"
  Write-Info "Check the most recent log file in $FrontendDir for clues (vite-*.log)."
  exit 2
}

Write-Info "Opening browser..."
try { Start-Process "http://localhost:$SelectedPort" } catch { Write-Warn "Could not open browser automatically." }

Write-Info "Tail the log with: Get-Content -Path $LogFile -Wait"
Write-Info "Press Ctrl+C to exit this script; dev server keeps running until its process ends."
