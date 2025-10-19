<#
 .SYNOPSIS
  Force-kill anything on the dev port, optionally reinstall deps, then start Vite with fallback ports until it works.

 .PARAMETER Port
  Preferred starting port (default 3000).

 .PARAMETER MaxAttempts
  How many successive ports to try if one fails (default 3).

 .PARAMETER Reinstall
  If supplied, performs a clean reinstall (removes node_modules + package-lock.json then runs npm install).

 .PARAMETER ClearCache
  If supplied, removes Vite/Turbo cache directories (.vite, dist) before starting.

 .PARAMETER NoTypeCheck
  Add --no-type-check when launching dev (can speed startup if TS diagnostics are hanging).

 .PARAMETER Force
  Skip confirmation prompts.

 USAGE EXAMPLES
  ./force-dev.ps1
  ./force-dev.ps1 -Port 3001 -Reinstall -ClearCache
  ./force-dev.ps1 -NoTypeCheck -Force
  ./force-dev.ps1 -MaxAttempts 5
#>

param(
    [int]$Port = 3000,
    [int]$MaxAttempts = 3,
    [switch]$Reinstall,
    [switch]$ClearCache,
    [switch]$NoTypeCheck,
    [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$script:npmPath = $null

function Write-Section($Title) {
    Write-Host "`n=== $Title ===" -ForegroundColor Cyan
}

function Kill-PortProcesses([int]$TargetPort) {
    Write-Host "Checking for processes on port $TargetPort..." -ForegroundColor Yellow
    $pids = @()
    try {
        $conns = Get-NetTCPConnection -LocalPort $TargetPort -ErrorAction SilentlyContinue | Where-Object { $_.State -eq 'Listen' }
        if ($conns) { $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique }
    } catch {}
    if (-not $pids -or $pids.Count -eq 0) {
        # Fallback to netstat parsing
        $net = netstat -ano | Select-String ":$TargetPort" | ForEach-Object { ($_ -split '\s+')[-1] } | Select-Object -Unique
        if ($net) { $pids = $net }
    }
    if ($pids -and $pids.Count -gt 0) {
        foreach ($pid in $pids) {
            if ($pid -and $pid -match '^[0-9]+$') {
                try {
                    $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
                    if ($proc) {
                        Write-Host "Killing PID $pid ($($proc.ProcessName)) on port $TargetPort" -ForegroundColor Red
                        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                    }
                } catch {}
            }
        }
        Start-Sleep -Milliseconds 400
    } else {
        Write-Host "No listeners on port $TargetPort." -ForegroundColor DarkGray
    }
}

function Ensure-FrontendDir {
    if (-not (Test-Path -LiteralPath "$PSScriptRoot")) {
        throw "Script root not found."
    }
    Set-Location $PSScriptRoot
}

function Reinstall-Deps {
    if ($Reinstall) {
        Write-Section "Reinstalling dependencies"
        if (Test-Path node_modules) { Write-Host "Removing node_modules" -ForegroundColor Yellow; Remove-Item node_modules -Recurse -Force }
        if (Test-Path package-lock.json) { Write-Host "Removing package-lock.json" -ForegroundColor Yellow; Remove-Item package-lock.json -Force }
        npm install
        if ($LASTEXITCODE -ne 0) { throw "npm install failed" }
        Write-Host "Reinstall complete" -ForegroundColor Green
    }
}

function Clear-CacheDirs {
    if ($ClearCache) {
        Write-Section "Clearing local build caches"
        foreach ($d in @('.vite','dist')) { if (Test-Path $d) { Write-Host "Removing $d" -ForegroundColor Yellow; Remove-Item $d -Recurse -Force -ErrorAction SilentlyContinue } }
    }
}

function Test-DevReady([int]$TestPort) {
    try {
        $resp = Invoke-WebRequest -Uri "http://localhost:$TestPort" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        if ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 500) { return $true }
    } catch { return $false }
    return $false
}

function Start-Dev([int]$BasePort) {
    $attempt = 0
    while ($attempt -lt $MaxAttempts) {
        $currentPort = $BasePort + $attempt
        Write-Section "Attempt $(($attempt+1)) starting dev on port $currentPort"
        Kill-PortProcesses -TargetPort $currentPort
        $extra = @()
        if ($NoTypeCheck) { $extra += '--no-type-check' }
        $env:PORT = $currentPort
            # Prefer npm.cmd; fallback to direct vite
            if (-not $script:npmPath) {
                try { $script:npmPath = (Get-Command npm.cmd -ErrorAction Stop).Source } catch { $script:npmPath = $null }
            }
            if ($script:npmPath) {
                $cmd = '"' + $script:npmPath + '" run dev -- --port ' + $currentPort + ' ' + ($extra -join ' ')
            } else {
                $viteLocal = Join-Path $PWD 'node_modules/.bin/vite.cmd'
                if (Test-Path $viteLocal) {
                    $cmd = '"' + $viteLocal + '" --port ' + $currentPort + ' ' + ($extra -join ' ')
                } else {
                    $cmd = 'npx vite --port ' + $currentPort + ' ' + ($extra -join ' ')
                }
            }
        Write-Host "Launching: $cmd" -ForegroundColor Magenta
        # Start in a child process so we can monitor readiness
    $proc = Start-Process powershell -ArgumentList "-NoProfile","-Command","cd `"$PWD`"; $cmd" -PassThru
        Write-Host "PID: $($proc.Id)" -ForegroundColor DarkCyan
        Write-Host "Waiting for readiness..." -ForegroundColor Yellow
        $ready = $false
        for ($i=0; $i -lt 40; $i++) { # ~40s max
            Start-Sleep -Seconds 1
            if (Test-DevReady -TestPort $currentPort) { $ready = $true; break }
            Write-Host -NoNewline '.'
        }
        Write-Host ''
        if ($ready) {
            Write-Host "✅ Dev server ready: http://localhost:$currentPort" -ForegroundColor Green
            return @{ Port = $currentPort; PID = $proc.Id }
        } else {
            Write-Host "Server did not become ready on port $currentPort. Killing and retrying..." -ForegroundColor Yellow
            try { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue } catch {}
        }
        $attempt++
    }
    throw "Failed to start dev server after $MaxAttempts attempts."
}

Write-Section "Force Dev Startup"
Ensure-FrontendDir

if (-not $Force) {
    $answer = Read-Host "Proceed with force restart actions? (y/n)"
    if ($answer -notin @('y','Y','yes','YES')) { Write-Host 'Aborted by user.'; exit 1 }
}

Reinstall-Deps
Clear-CacheDirs

Write-Section "Environment Info"
    try { $nodeVersion = node -v } catch { $nodeVersion = 'unknown' }
    Write-Host "Node version: $nodeVersion" -ForegroundColor Gray
    try {
        $npmCmd = (Get-Command npm.cmd -ErrorAction Stop).Source
        $npmVersion = & $npmCmd -v 2>$null
    } catch { $npmCmd = $null; $npmVersion = 'unavailable' }
    Write-Host "NPM version : $npmVersion" -ForegroundColor Gray
    if (-not $npmCmd) { Write-Host "Warning: npm.cmd not resolved; will attempt direct vite execution" -ForegroundColor Yellow }

$result = Start-Dev -BasePort $Port

Write-Section "Summary"
Write-Host ("Active Port : {0}" -f $result.Port) -ForegroundColor Cyan
Write-Host ("Process PID: {0}" -f $result.PID) -ForegroundColor Cyan
Write-Host "Open in browser: http://localhost:$($result.Port)" -ForegroundColor Green
Write-Host "To terminate: Stop-Process -Id $($result.PID) -Force" -ForegroundColor Yellow

exit 0
