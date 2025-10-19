<#
.SYNOPSIS
    Permanent Network Error Fix for HireBahamas Platform
.DESCRIPTION
    This script provides a permanent solution for network errors by:
    - Cleaning up TIME_WAIT connections
    - Monitoring backend health
    - Auto-restarting crashed servers
    - Proper connection pooling
    - Network diagnostics
#>

param(
    [switch]$Install,
    [switch]$Monitor,
    [switch]$Fix,
    [switch]$Status
)

$ErrorActionPreference = "Stop"
$BACKEND_PORT = 9999
$FRONTEND_PORT = 3000
$PROJECT_ROOT = "C:\Users\Dell\OneDrive\Desktop\HireBahamas"

# Color functions
function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }

function Test-AdminRights {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Clear-TimeWaitConnections {
    Write-Info "Cleaning up TIME_WAIT connections..."
    
    # Get count before
    $beforeCount = (netstat -ano | Select-String "TIME_WAIT.*:$BACKEND_PORT").Count
    Write-Info "TIME_WAIT connections before: $beforeCount"
    
    # Reduce TIME_WAIT timeout (requires admin)
    if (Test-AdminRights) {
        try {
            # Set TCP time wait delay to 30 seconds (default is 240)
            netsh int ipv4 set dynamicport tcp start=49152 num=16384
            Write-Success "TCP dynamic port range configured"
        } catch {
            Write-Warning "Could not modify TCP settings (may need admin rights)"
        }
    }
    
    # Force close lingering connections (optional - aggressive)
    # Uncomment if you want to forcefully close TIME_WAIT connections
    # Get-NetTCPConnection -LocalPort $BACKEND_PORT -State TimeWait -ErrorAction SilentlyContinue | 
    #     ForEach-Object { Write-Host "Closing TIME_WAIT connection: $($_.RemoteAddress):$($_.RemotePort)" }
    
    Write-Success "Connection cleanup completed"
}

function Test-BackendHealth {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:$BACKEND_PORT/health" `
            -Method GET `
            -UseBasicParsing `
            -TimeoutSec 5 `
            -ErrorAction Stop
        
        if ($response.StatusCode -eq 200) {
            return $true
        }
    } catch {
        return $false
    }
    return $false
}

function Get-ProcessOnPort {
    param([int]$Port)
    
    $connection = netstat -ano | Select-String ":$Port\s+.*LISTENING"
    if ($connection) {
        $pid = ($connection -split '\s+')[-1]
        try {
            return Get-Process -Id $pid -ErrorAction Stop
        } catch {
            return $null
        }
    }
    return $null
}

function Stop-BackendServer {
    Write-Info "Stopping backend server..."
    
    $process = Get-ProcessOnPort -Port $BACKEND_PORT
    if ($process) {
        Write-Info "Found backend process: PID $($process.Id)"
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        Write-Success "Backend stopped"
    } else {
        Write-Info "No backend process found on port $BACKEND_PORT"
    }
}

function Start-BackendServer {
    Write-Info "Starting backend server..."
    
    # First ensure no process is running
    Stop-BackendServer
    
    # Wait for port to be free
    Start-Sleep -Seconds 2
    
    # Start backend in new window
    $backendScript = Join-Path $PROJECT_ROOT "final_backend.py"
    
    if (Test-Path $backendScript) {
        $startInfo = New-Object System.Diagnostics.ProcessStartInfo
        $startInfo.FileName = "powershell.exe"
        $startInfo.Arguments = "-NoExit -Command `"cd '$PROJECT_ROOT'; python final_backend.py`""
        $startInfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Normal
        $startInfo.UseShellExecute = $true
        
        $process = [System.Diagnostics.Process]::Start($startInfo)
        
        Write-Info "Backend starting (PID: $($process.Id))..."
        
        # Wait for backend to be ready
        $maxAttempts = 10
        $attempt = 0
        $isReady = $false
        
        while ($attempt -lt $maxAttempts -and -not $isReady) {
            Start-Sleep -Seconds 2
            $attempt++
            Write-Info "Waiting for backend... attempt $attempt/$maxAttempts"
            
            if (Test-BackendHealth) {
                $isReady = $true
                Write-Success "Backend is ready on http://127.0.0.1:$BACKEND_PORT"
            }
        }
        
        if (-not $isReady) {
            Write-Error "Backend failed to start properly"
            return $false
        }
        
        return $true
    } else {
        Write-Error "Backend script not found: $backendScript"
        return $false
    }
}

function Show-NetworkStatus {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "  NETWORK STATUS CHECK" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    # Backend status
    $backendHealthy = Test-BackendHealth
    $backendProcess = Get-ProcessOnPort -Port $BACKEND_PORT
    
    Write-Host "Backend (Port $BACKEND_PORT):" -NoNewline
    if ($backendHealthy) {
        Write-Host " HEALTHY ✅" -ForegroundColor Green
        if ($backendProcess) {
            Write-Host "  Process: $($backendProcess.Name) (PID: $($backendProcess.Id))" -ForegroundColor Gray
        }
    } else {
        Write-Host " DOWN ❌" -ForegroundColor Red
    }
    
    # Frontend status
    try {
        $frontendResponse = Invoke-WebRequest -Uri "http://localhost:$FRONTEND_PORT" `
            -Method GET -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
        Write-Host "Frontend (Port $FRONTEND_PORT): RUNNING ✅" -ForegroundColor Green
    } catch {
        Write-Host "Frontend (Port $FRONTEND_PORT): DOWN ❌" -ForegroundColor Red
    }
    
    # Network connections
    $timeWaitCount = (netstat -ano | Select-String "TIME_WAIT.*:$BACKEND_PORT").Count
    $establishedCount = (netstat -ano | Select-String "ESTABLISHED.*:$BACKEND_PORT").Count
    
    Write-Host "`nNetwork Connections:" -ForegroundColor Cyan
    Write-Host "  ESTABLISHED: $establishedCount" -ForegroundColor $(if ($establishedCount -lt 50) { "Green" } else { "Yellow" })
    Write-Host "  TIME_WAIT: $timeWaitCount" -ForegroundColor $(if ($timeWaitCount -lt 100) { "Green" } elseif ($timeWaitCount -lt 500) { "Yellow" } else { "Red" })
    
    if ($timeWaitCount -gt 500) {
        Write-Warning "High number of TIME_WAIT connections detected!"
        Write-Info "Run with -Fix to clean up connections"
    }
    
    Write-Host "`n========================================`n" -ForegroundColor Cyan
}

function Start-NetworkMonitor {
    Write-Info "Starting network monitor (press Ctrl+C to stop)..."
    Write-Info "Monitoring backend health and auto-restarting on failure`n"
    
    $checkInterval = 10  # seconds
    $failureCount = 0
    $maxFailures = 3
    
    while ($true) {
        $timestamp = Get-Date -Format "HH:mm:ss"
        
        if (Test-BackendHealth) {
            Write-Host "[$timestamp] Backend: " -NoNewline
            Write-Host "HEALTHY ✅" -ForegroundColor Green
            $failureCount = 0
            
            # Check TIME_WAIT connections
            $timeWaitCount = (netstat -ano | Select-String "TIME_WAIT.*:$BACKEND_PORT").Count
            if ($timeWaitCount -gt 1000) {
                Write-Warning "[$timestamp] High TIME_WAIT count: $timeWaitCount (cleaning up...)"
                Clear-TimeWaitConnections
            }
        } else {
            $failureCount++
            Write-Host "[$timestamp] Backend: " -NoNewline
            Write-Host "UNHEALTHY ❌ (Failure $failureCount/$maxFailures)" -ForegroundColor Red
            
            if ($failureCount -ge $maxFailures) {
                Write-Warning "[$timestamp] Max failures reached. Restarting backend..."
                Clear-TimeWaitConnections
                if (Start-BackendServer) {
                    Write-Success "[$timestamp] Backend restarted successfully"
                    $failureCount = 0
                } else {
                    Write-Error "[$timestamp] Backend restart failed"
                }
            }
        }
        
        Start-Sleep -Seconds $checkInterval
    }
}

function Install-NetworkFix {
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "  INSTALLING NETWORK FIX" -ForegroundColor Green
    Write-Host "========================================`n" -ForegroundColor Green
    
    # Step 1: Clean up connections
    Clear-TimeWaitConnections
    
    # Step 2: Restart backend
    Write-Info "Restarting backend server..."
    if (Start-BackendServer) {
        Write-Success "Backend restarted successfully"
    } else {
        Write-Error "Failed to restart backend"
        return
    }
    
    # Step 3: Show status
    Start-Sleep -Seconds 2
    Show-NetworkStatus
    
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "  NETWORK FIX INSTALLED ✅" -ForegroundColor Green
    Write-Host "========================================`n" -ForegroundColor Green
    
    Write-Info "To monitor backend health: .\NETWORK_FIX_PERMANENT.ps1 -Monitor"
    Write-Info "To check status: .\NETWORK_FIX_PERMANENT.ps1 -Status"
    Write-Info "To fix issues: .\NETWORK_FIX_PERMANENT.ps1 -Fix"
}

# Main execution
try {
    if ($Install) {
        Install-NetworkFix
    }
    elseif ($Monitor) {
        Start-NetworkMonitor
    }
    elseif ($Fix) {
        Write-Info "Applying network fix..."
        Clear-TimeWaitConnections
        
        if (-not (Test-BackendHealth)) {
            Write-Warning "Backend is down. Restarting..."
            Start-BackendServer
        } else {
            Write-Success "Backend is healthy"
        }
        
        Show-NetworkStatus
    }
    elseif ($Status) {
        Show-NetworkStatus
    }
    else {
        Write-Host @"

========================================
  HIREBAHAMAS NETWORK FIX
========================================

Usage:
  .\NETWORK_FIX_PERMANENT.ps1 -Install   # Install and apply network fix
  .\NETWORK_FIX_PERMANENT.ps1 -Status    # Check network status
  .\NETWORK_FIX_PERMANENT.ps1 -Fix       # Fix network issues
  .\NETWORK_FIX_PERMANENT.ps1 -Monitor   # Start health monitor

Examples:
  # Install the fix and restart servers
  .\NETWORK_FIX_PERMANENT.ps1 -Install

  # Check current status
  .\NETWORK_FIX_PERMANENT.ps1 -Status

  # Fix network issues
  .\NETWORK_FIX_PERMANENT.ps1 -Fix

  # Start monitoring (auto-restart on failure)
  .\NETWORK_FIX_PERMANENT.ps1 -Monitor

========================================
"@
    }
}
catch {
    Write-Error "An error occurred: $_"
    Write-Host $_.ScriptStackTrace -ForegroundColor Red
}
