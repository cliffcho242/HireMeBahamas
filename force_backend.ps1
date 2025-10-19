<#!
.SYNOPSIS
  Force restart the HireBahamas backend (Flask clean_backend.py) on the specified port with logging & health polling.

.DESCRIPTION
  Kills any process bound to the target port, optionally deletes the SQLite DB, and launches clean_backend.py.
  Polls /health until ready or timeout, writing combined stdout/stderr to a timestamped log file.

.PARAMETER Port
  Backend port (default 8008).

.PARAMETER PythonPath
  Path to python executable (auto-detected if omitted).

.PARAMETER CleanDB
  Deletes the existing SQLite database file before start.

.PARAMETER TimeoutSeconds
  Time to wait for health endpoint (default 40 seconds).

.PARAMETER VerboseLog
  Streams backend log tail to console after start confirmation.

.EXAMPLE
  ./force_backend.ps1 -VerboseLog

.EXAMPLE
  ./force_backend.ps1 -CleanDB -PythonPath C:\Python311\python.exe
#>
param(
  [int]$Port = 8008,
  [string]$PythonPath,
  [switch]$CleanDB,
  [switch]$ForceAll,
  [int]$TimeoutSeconds = 40,
  [switch]$VerboseLog
)
$ErrorActionPreference = 'Stop'
function Info($m){ Write-Host "[INFO ] $m" -ForegroundColor Cyan }
function Warn($m){ Write-Host "[WARN ] $m" -ForegroundColor Yellow }
function Err ($m){ Write-Host "[ERROR] $m" -ForegroundColor Red }
function Ok  ($m){ Write-Host "[ OK  ] $m" -ForegroundColor Green }

$Root = $PSScriptRoot
$BackendScript = Join-Path $Root 'clean_backend.py'
if(-not (Test-Path $BackendScript)){ Err "clean_backend.py not found at $BackendScript"; exit 1 }
$DbFile = Join-Path $Root 'hirebahamas.db'

if($ForceAll){
  Warn "ForceAll enabled: will kill existing python processes and rebuild DB"
  $CleanDB = $true
  Get-Process python -ErrorAction SilentlyContinue | ForEach-Object {
    try { Stop-Process -Id $_.Id -Force -ErrorAction Stop; Info ("Killed python PID {0}" -f $_.Id) } catch { Warn ("Failed to kill python PID {0}: {1}" -f $_.Id, $_.Exception.Message) }
  }
}

# Determine python
if(-not $PythonPath){
  $py = Get-Command python -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty Source
  if(-not $py){ Err 'python executable not found in PATH. Supply -PythonPath.'; exit 1 }
  $PythonPath = $py
}
Info "Using Python: $PythonPath"

# Helper: get PIDs using port
function Get-PortPids([int]$p){ netstat -ano | Select-String ":$p" | ForEach-Object { ($_.ToString() -split '\s+')[-1] } | Sort-Object -Unique | Where-Object { $_ -match '^[0-9]+$' } }
function FreePort([int]$p){
  $pids = Get-PortPids $p
  if($pids){
    Warn ("Port {0} in use by PIDs: {1} -> killing" -f $p, ($pids -join ', '))
    foreach($procPid in $pids){
      try {
        Stop-Process -Id $procPid -Force -ErrorAction Stop
        Info ("Killed PID {0}" -f $procPid)
      } catch {
        Warn ("Failed to kill {0}: {1}" -f $procPid, $_.Exception.Message)
      }
    }
  } else {
    Info ("Port {0} free" -f $p)
  }
}

FreePort -p $Port

if($CleanDB){ if(Test-Path $DbFile){ Warn "Deleting existing DB $DbFile"; Remove-Item $DbFile -Force } else { Info 'No DB file to delete.' } }

$Timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$LogFile = Join-Path $Root "backend-$Timestamp.log"
Info "Log file: $LogFile"

# Start backend
Info "Starting backend..."
$startArgs = @($BackendScript)
try {
  # Use cmd.exe to merge stdout+stderr into one log via redirection
  $cmd = "$PythonPath `"$BackendScript`" 1>>`"$LogFile`" 2>>&1"
  $proc = Start-Process -FilePath $env:ComSpec -ArgumentList '/c', $cmd -WorkingDirectory $Root -PassThru -WindowStyle Hidden
} catch {
  Err "Failed to start backend: $($_.Exception.Message)"; exit 1
}

# Poll health
$HealthUrl = "http://127.0.0.1:$Port/health"
$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
$ready = $false
while((Get-Date) -lt $deadline){
  Start-Sleep -Seconds 1
  if($proc.HasExited){ Err "Backend process exited early with code $($proc.ExitCode)"; Get-Content $LogFile -Tail 40; exit 2 }
  try {
    $resp = Invoke-WebRequest -Uri $HealthUrl -UseBasicParsing -TimeoutSec 2
    if($resp.StatusCode -eq 200){ $ready = $true; break }
  } catch {}
}
if(-not $ready){ Warn "Timeout waiting for backend health at $HealthUrl"; Get-Content $LogFile -Tail 60; exit 3 }
Ok "Backend healthy: $HealthUrl"

if($VerboseLog){ Info 'Tailing log (Ctrl+C to stop tail)...'; Get-Content $LogFile -Wait }
else { Info "Tail recent log lines:"; Get-Content $LogFile -Tail 25 }

exit 0
